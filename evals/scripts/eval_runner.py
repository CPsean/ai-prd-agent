#!/usr/bin/env python3
"""
AI PRD Workspace — 集成测试自动化 Runner
==========================================
自动化覆盖范围：
  ✅ 文件断言（存在性 / 内容 / YAML frontmatter 字段）
  ✅ AI 输出关键词 / 正则模式匹配
  ✅ 多轮对话状态管理（tool_use 循环）
  ✅ 测试前 setup + 测试后 cleanup（自动删除测试文件）
  ⬜ "AI 判断质量"类检查：脚本标记为 [人工]，不影响 pass/fail

用法:
  python eval_runner.py                   # 运行所有已实现用例
  python eval_runner.py --tc TC-INT-01    # 运行单个用例
  python eval_runner.py --list            # 列出所有可用用例
  python eval_runner.py --clean-only      # 只清理测试产生的文件
  python eval_runner.py -v                # 显示 AI 输出和工具调用详情

前置条件:
  pip install -r requirements.txt
  export ANTHROPIC_API_KEY=sk-ant-...     # Windows: set ANTHROPIC_API_KEY=...
"""

import io
import os
import sys
import re
import shutil
import yaml
import argparse
import time
import traceback
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Optional, Union

import anthropic

# ─── 路径常量 ──────────────────────────────────────────────────────────────────
REPO_ROOT   = Path(__file__).resolve().parent.parent.parent
CMDS_DIR    = REPO_ROOT / ".claude" / "commands"
REPORTS_DIR = Path(__file__).resolve().parent / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# 从项目根目录 .env 加载环境变量（若存在）
_dotenv = REPO_ROOT / ".env"
if _dotenv.exists():
    for _line in _dotenv.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

# ─── API 客户端 ────────────────────────────────────────────────────────────────
# 延迟初始化：--list / --clean-only 不需要 API key
CLIENT: "anthropic.Anthropic | None" = None
MODEL  = "claude-sonnet-4-6"


def _get_client() -> "anthropic.Anthropic":
    global CLIENT
    if CLIENT is None:
        if not os.getenv("ANTHROPIC_API_KEY"):
            print("❌  请先设置环境变量 ANTHROPIC_API_KEY")
            sys.exit(1)
        CLIENT = anthropic.Anthropic()
    return CLIENT


# ══════════════════════════════════════════════════════════════════════════════
# 工具实现（Claude Code 核心工具子集，路径均相对于 REPO_ROOT）
# ══════════════════════════════════════════════════════════════════════════════

def _resolve(path: str) -> Path:
    p = Path(path)
    return p if p.is_absolute() else REPO_ROOT / p


def _t_read(file_path: str, offset: int = 0, limit: int = 2000, **_) -> str:
    p = _resolve(file_path)
    if not p.exists():
        return f"Error: {file_path} does not exist"
    lines = p.read_text(encoding="utf-8").splitlines()
    chunk = lines[offset: offset + limit]
    return "\n".join(f"{i + 1 + offset}\t{ln}" for i, ln in enumerate(chunk))


def _t_write(file_path: str, content: str, **_) -> str:
    p = _resolve(file_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return f"Wrote {len(content)} chars to {file_path}"


def _t_edit(file_path: str, old_string: str, new_string: str,
            replace_all: bool = False, **_) -> str:
    p = _resolve(file_path)
    if not p.exists():
        return f"Error: {file_path} does not exist"
    text = p.read_text(encoding="utf-8")
    if old_string not in text:
        return f"Error: old_string not found in {file_path}"
    updated = text.replace(old_string, new_string) if replace_all \
              else text.replace(old_string, new_string, 1)
    p.write_text(updated, encoding="utf-8")
    return "Edit applied"


def _t_glob(pattern: str, path: str = ".", **_) -> str:
    base = _resolve(path)
    hits = sorted(str(m.relative_to(REPO_ROOT)) for m in base.glob(pattern))
    return "\n".join(hits) if hits else "(no matches)"


def _t_grep(pattern: str, path: str = ".", glob: str = "**/*.md",
            output_mode: str = "files_with_matches", **_) -> str:
    base = _resolve(path)
    results: list[str] = []
    for f in base.glob(glob):
        if not f.is_file():
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
            rel  = str(f.relative_to(REPO_ROOT))
            if output_mode == "files_with_matches":
                if re.search(pattern, text, re.MULTILINE):
                    results.append(rel)
            else:
                for i, line in enumerate(text.splitlines()):
                    if re.search(pattern, line):
                        results.append(f"{rel}:{i+1}: {line}")
        except Exception:
            pass
    return "\n".join(results[:100]) if results else "(no matches)"


_TOOL_FN: dict[str, Callable] = {
    "Read":  _t_read,
    "Write": _t_write,
    "Edit":  _t_edit,
    "Glob":  _t_glob,
    "Grep":  _t_grep,
}

_TOOL_DEFS = [
    {
        "name": "Read",
        "description": "Read a file from the local filesystem",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "offset":    {"type": "integer"},
                "limit":     {"type": "integer"},
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "Write",
        "description": "Write content to a file, creating parent directories as needed",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "content":   {"type": "string"},
            },
            "required": ["file_path", "content"],
        },
    },
    {
        "name": "Edit",
        "description": "Replace a string in a file (exact match required)",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path":   {"type": "string"},
                "old_string":  {"type": "string"},
                "new_string":  {"type": "string"},
                "replace_all": {"type": "boolean"},
            },
            "required": ["file_path", "old_string", "new_string"],
        },
    },
    {
        "name": "Glob",
        "description": "List files matching a glob pattern",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string"},
                "path":    {"type": "string"},
            },
            "required": ["pattern"],
        },
    },
    {
        "name": "Grep",
        "description": "Search file contents using regex",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern":     {"type": "string"},
                "path":        {"type": "string"},
                "glob":        {"type": "string"},
                "output_mode": {"type": "string",
                                "enum": ["files_with_matches", "content", "count"]},
            },
            "required": ["pattern"],
        },
    },
]


# ══════════════════════════════════════════════════════════════════════════════
# Claude 对话管理
# ══════════════════════════════════════════════════════════════════════════════

def _build_system(command_name: str) -> str:
    """拼装 system prompt：CLAUDE.md + 命令文件 + 工作目录声明"""
    parts: list[str] = []

    claude_md = REPO_ROOT / "CLAUDE.md"
    if claude_md.exists():
        parts.append(claude_md.read_text(encoding="utf-8"))

    cmd_file = CMDS_DIR / f"{command_name}.md"
    if cmd_file.exists():
        cmd_content = cmd_file.read_text(encoding="utf-8")
        parts.append(
            f"## 当前激活命令：/{command_name}\n\n"
            f"请严格按照以下命令定义执行，$ARGUMENTS 将由用户消息提供：\n\n"
            f"{cmd_content}"
        )

    parts.append(
        f"## 执行环境\n"
        f"工作目录（所有相对路径的 base）：{REPO_ROOT}\n"
        f"今天日期：{datetime.now().strftime('%Y-%m-%d')}"
    )

    return "\n\n---\n\n".join(parts)


def run_turn(
    messages: list,
    user_input: str,
    command_name: str,
    verbose: bool = False,
) -> tuple[str, list]:
    """
    执行一轮对话，自动处理所有 tool_use 循环直到 end_turn。
    返回 (AI文本输出, 更新后的messages列表)
    """
    messages = messages + [{"role": "user", "content": user_input}]
    system   = _build_system(command_name)

    while True:
        resp = _get_client().messages.create(
            model=MODEL,
            max_tokens=8192,
            system=system,
            tools=_TOOL_DEFS,
            messages=messages,
        )

        text_parts: list[str] = []
        tool_uses: list       = []

        for block in resp.content:
            if hasattr(block, "text"):
                text_parts.append(block.text)
            if block.type == "tool_use":
                tool_uses.append(block)

        messages = messages + [{"role": "assistant", "content": resp.content}]

        if verbose and text_parts:
            print(f"\n    ╔ AI ╗\n    {' '.join(text_parts)[:400]}\n    ╚════╝")

        if resp.stop_reason == "end_turn":
            return "\n".join(text_parts), messages

        if resp.stop_reason == "tool_use" and tool_uses:
            tool_results = []
            for tu in tool_uses:
                fn     = _TOOL_FN.get(tu.name)
                result = fn(**tu.input) if fn else f"unknown tool: {tu.name}"
                if verbose:
                    print(f"    [tool] {tu.name}({list(tu.input.keys())!s:50s}"
                          f"→ {str(result)[:80]}")
                tool_results.append({
                    "type":        "tool_result",
                    "tool_use_id": tu.id,
                    "content":     str(result),
                })
            messages = messages + [{"role": "user", "content": tool_results}]
        else:
            # 未知 stop_reason，直接返回当前文本
            return "\n".join(text_parts), messages


# ══════════════════════════════════════════════════════════════════════════════
# 断言工具函数
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class Check:
    name:   str
    passed: bool
    detail: str  = ""
    manual: bool = False   # True = 需人工确认，不计入 pass/fail


# ── 文件断言 ──────────────────────────────────────────────────────────────────

def file_exists(rel_path: str) -> Check:
    ok = _resolve(rel_path).exists()
    return Check(f"file_exists  {rel_path}", ok, "" if ok else "文件不存在")


def file_not_exists(rel_path: str) -> Check:
    ok = not _resolve(rel_path).exists()
    return Check(f"file_absent  {rel_path}", ok, "" if ok else "文件不应存在")


def frontmatter(rel_path: str, key: str, expected) -> Check:
    name = f"frontmatter  {rel_path}  [{key}={expected!r}]"
    p    = _resolve(rel_path)
    if not p.exists():
        return Check(name, False, "文件不存在")
    m = re.match(r"^---\s*\n(.*?)\n---", p.read_text(encoding="utf-8"), re.DOTALL)
    if not m:
        return Check(name, False, "未找到 YAML frontmatter")
    try:
        fm     = yaml.safe_load(m.group(1)) or {}
        actual = fm.get(key)
        ok     = actual == expected
        return Check(name, ok, "" if ok else f"实际值 {actual!r}")
    except Exception as e:
        return Check(name, False, str(e))


def text_in_file(rel_path: str, text: str) -> Check:
    name = f"text_in_file {rel_path!r}  [{text[:30]!r}]"
    p    = _resolve(rel_path)
    if not p.exists():
        return Check(name, False, "文件不存在")
    ok = text in p.read_text(encoding="utf-8")
    return Check(name, ok, "" if ok else "文本未在文件中找到")


# ── 输出断言 ──────────────────────────────────────────────────────────────────

def output_contains(output: str, pattern: str, label: str = "") -> Check:
    ok   = bool(re.search(pattern, output, re.IGNORECASE | re.DOTALL))
    name = label or f"output_match [{pattern[:40]!r}]"
    return Check(name, ok, "" if ok else "模式未在输出中匹配")


def manual(description: str) -> Check:
    """标记为需要人工确认的检查项（不影响自动化 pass/fail 结果）"""
    return Check(f"[人工] {description}", passed=True, manual=True)


# ── 类型别名：output_check 接受 output str；file_check 无参 ──────────────────
OutputCheck = Union[Callable[[str], Check], Check]
FileCheck   = Callable[[], Check]


# ══════════════════════════════════════════════════════════════════════════════
# 测试用例结构
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class Turn:
    user_input:     str
    output_checks:  list[OutputCheck] = field(default_factory=list)
    file_checks:    list[FileCheck]   = field(default_factory=list)


@dataclass
class TestCase:
    id:       str
    name:     str
    command:  str           # 对应 .claude/commands/<command>.md
    setup:    Callable
    teardown: Callable
    turns:    list[Turn]


# ══════════════════════════════════════════════════════════════════════════════
# Setup / Teardown 工具函数
# ══════════════════════════════════════════════════════════════════════════════

def _rmdir(rel: str):
    p = _resolve(rel)
    if p.exists():
        shutil.rmtree(p)

def _rm(rel: str):
    p = _resolve(rel)
    if p.exists():
        p.unlink()

def _write(rel: str, content: str):
    p = _resolve(rel)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")


# ══════════════════════════════════════════════════════════════════════════════
# 测试用例定义
# ══════════════════════════════════════════════════════════════════════════════

# ── TC-INT-01 ─────────────────────────────────────────────────────────────────
# Phase 1 完成后 rdd.md 正确创建

def _setup_int01():
    _rmdir("drafts/报销单批量导出")

def _teardown_int01():
    _rmdir("drafts/报销单批量导出")

TC_INT_01 = TestCase(
    id      = "TC-INT-01",
    name    = "Phase 1 完成后 rdd.md 正确创建",
    command = "requirement-clarifier",
    setup   = _setup_int01,
    teardown= _teardown_int01,
    turns   = [
        Turn(
            user_input = (
                "/requirement-clarifier 财务人员需要每月将费用报销单批量导出为 Excel，"
                "目前只能逐条下载 PDF，非常耗时，导致月末结账时大量等待。"
            ),
            output_checks = [
                lambda o: output_contains(o, r"As a|用户故事|I want to",     "生成了用户故事格式"),
                lambda o: output_contains(o, r"确认|方向是否正确",              "等待用户确认"),
                manual("AI 未自动进入 Phase 2，在用户确认前阻塞"),
            ],
            file_checks = [
                lambda: file_not_exists("drafts/报销单批量导出/rdd.md"),  # 确认前不应创建
            ],
        ),
        Turn(
            user_input = "确认",
            output_checks = [
                lambda o: output_contains(o, r"rdd\.md|已创建|已保存|Phase 2", "文件创建提示"),
            ],
            file_checks = [
                lambda: file_exists(   "drafts/报销单批量导出/rdd.md"),
                lambda: frontmatter(   "drafts/报销单批量导出/rdd.md", "status",        "story-confirmed"),
                lambda: frontmatter(   "drafts/报销单批量导出/rdd.md", "phase",         1),
                lambda: frontmatter(   "drafts/报销单批量导出/rdd.md", "story-version", 1),
                lambda: text_in_file(  "drafts/报销单批量导出/rdd.md", "待 Phase 2 填充"),
            ],
        ),
    ],
)

# ── TC-INT-02 ─────────────────────────────────────────────────────────────────
# 中断续接：status=story-confirmed → 跳过 Phase 1 直接进入 Phase 2

_STORY_CONFIRMED_RDD = """\
---
status: story-confirmed
phase: 1
story-version: 1
created: 2026-04-30
context-loaded:
  - user-persona
  - product-background
---
# RDD：报销单批量导出

> Phase 1 完成于 2026-04-30，待 Phase 2 填充详细分析。

## 用户故事（已确认）

As a 财务专员，I want to 批量导出报销单为 Excel，So that 月末结账更高效。

---

## 节 1：需求摘要

（待 Phase 2 填充）

## 节 2：初步方案

（待 Phase 2 填充）
"""

def _setup_int02():
    _write("drafts/报销单批量导出/rdd.md", _STORY_CONFIRMED_RDD)

def _teardown_int02():
    _rmdir("drafts/报销单批量导出")

TC_INT_02 = TestCase(
    id      = "TC-INT-02",
    name    = "中断续接——story-confirmed 跳过 Phase 1",
    command = "requirement-clarifier",
    setup   = _setup_int02,
    teardown= _teardown_int02,
    turns   = [
        Turn(
            user_input = "/requirement-clarifier 报销单批量导出",
            output_checks = [
                lambda o: output_contains(o, r"已确认|story.confirmed|批量导出", "引用了已确认故事"),
                lambda o: output_contains(o, r"Phase 2|澄清|问题",               "进入 Phase 2 澄清"),
                manual("AI 未重新生成用户故事草稿，未询问「方向是否正确」"),
                manual("AI 未重复执行 X-Y 诊断"),
            ],
        ),
    ],
)

# ── TC-INT-04 ─────────────────────────────────────────────────────────────────
# new-prd 遇到未完成的 rdd.md 给出提示

def _setup_int04():
    _write("drafts/报销单批量导出/rdd.md", _STORY_CONFIRMED_RDD)

def _teardown_int04():
    _rmdir("drafts/报销单批量导出")

TC_INT_04 = TestCase(
    id      = "TC-INT-04",
    name    = "new-prd 遇到 story-confirmed rdd.md 给出选项",
    command = "new-prd",
    setup   = _setup_int04,
    teardown= _teardown_int04,
    turns   = [
        Turn(
            user_input = "/new-prd feature 报销单批量导出",
            output_checks = [
                lambda o: output_contains(o, r"story.confirmed|未完成|Phase 2", "检测到 RDD 未完成"),
                lambda o: output_contains(o, r"[AB选项]|选项|继续|先去完成",      "提供 A/B 选项"),
                lambda o: output_contains(o, r"requirement.clarifier",           "引导用 clarifier 继续"),
                manual("AI 阻塞等待，未直接生成 prd.md"),
            ],
            file_checks = [
                lambda: file_not_exists("drafts/报销单批量导出/prd.md"),
            ],
        ),
    ],
)

# ── TC-INT-09 ─────────────────────────────────────────────────────────────────
# 无规格卡时 generate-prototype 阻断

def _setup_int09():
    _write(
        "prds/_registry.md",
        "# PRD 注册表\n\n| ID | 标题 | 路径 |\n|---|---|---|\n"
        "| F-099 | 消息通知设置 | prds/F-099-消息通知设置/prd.md |\n",
    )
    _write(
        "prds/F-099-消息通知设置/prd.md",
        "---\nid: F-099\nstatus: approved\nhas-prototype: false\n---\n"
        "# PRD: 消息通知设置\n",
    )
    _rm("prds/F-099-消息通知设置/page-spec.md")

def _teardown_int09():
    _rmdir("prds/F-099-消息通知设置")
    # 还原 _registry.md 中测试行（简单处理：直接删回原内容）
    reg = _resolve("prds/_registry.md")
    if reg.exists():
        lines = [l for l in reg.read_text(encoding="utf-8").splitlines()
                 if "F-099" not in l]
        reg.write_text("\n".join(lines), encoding="utf-8")

TC_INT_09 = TestCase(
    id      = "TC-INT-09",
    name    = "无规格卡时 generate-prototype 阻断",
    command = "generate-prototype",
    setup   = _setup_int09,
    teardown= _teardown_int09,
    turns   = [
        Turn(
            user_input = "/generate-prototype 消息通知设置",
            output_checks = [
                lambda o: output_contains(o, r"generate.page.spec|页面规格卡", "提示先运行 generate-page-spec"),
                lambda o: output_contains(o, r"阻断|无法|未找到|不存在|先运行",  "说明阻断原因"),
                manual("明确未回退读取 PRD 直接生成原型"),
            ],
            file_checks = [
                lambda: file_not_exists("outputs/prototypes/F-099-消息通知设置/index.html"),
                lambda: file_not_exists("outputs/prototypes/消息通知设置/index.html"),
            ],
        ),
    ],
)

# ── TC-INT-20 ─────────────────────────────────────────────────────────────────
# 端到端全链路：clarifier → new-prd → 移入正式区 → 草稿清理

def _setup_int20():
    _rmdir("drafts/组合筛选")
    _rmdir("drafts/F-999-组合筛选")   # 清理可能残留
    for p in (REPO_ROOT / "prds").glob("F-999-*"):
        shutil.rmtree(p)

def _teardown_int20():
    _rmdir("drafts/组合筛选")
    _rmdir("drafts/F-999-组合筛选")
    for p in (REPO_ROOT / "prds").glob("F-999-*"):
        shutil.rmtree(p)
    # 从 _registry.md 删测试行
    reg = _resolve("prds/_registry.md")
    if reg.exists():
        lines = [l for l in reg.read_text(encoding="utf-8").splitlines()
                 if "F-999" not in l and "组合筛选" not in l]
        reg.write_text("\n".join(lines), encoding="utf-8")
    reg2 = _resolve("drafts/_draft-registry.md")
    if reg2.exists():
        lines = [l for l in reg2.read_text(encoding="utf-8").splitlines()
                 if "F-999" not in l and "组合筛选" not in l]
        reg2.write_text("\n".join(lines), encoding="utf-8")

TC_INT_20 = TestCase(
    id      = "TC-INT-20",
    name    = "端到端全链路：clarifier → new-prd → 移入正式区",
    command = "requirement-clarifier",
    setup   = _setup_int20,
    teardown= _teardown_int20,
    turns   = [
        # 步骤 1a：Phase 1 生成故事
        Turn(
            user_input = (
                "/requirement-clarifier 组合筛选\n\n"
                "需求描述：用户希望在列表页支持按多个条件组合筛选，目前只能单条件筛选。"
            ),
            output_checks = [
                lambda o: output_contains(o, r"As a|用户故事|I want to", "Phase 1 用户故事"),
                lambda o: output_contains(o, r"确认|方向",               "等待确认"),
            ],
        ),
        # 步骤 1b：确认故事
        Turn(
            user_input = "确认",
            file_checks = [
                lambda: file_exists(    "drafts/组合筛选/rdd.md"),
                lambda: frontmatter(    "drafts/组合筛选/rdd.md", "status", "story-confirmed"),
            ],
        ),
        # 步骤 1c：Phase 2 澄清（简短回答触发收敛）
        Turn(
            user_input = (
                "核心场景：用户在订单列表页，需要同时按状态+日期范围+金额过滤。"
                "业务规则：最多支持 5 个条件组合，条件间默认 AND 关系。"
                "成功指标：查询响应 < 2s，筛选结果准确率 100%。"
            ),
            output_checks = [
                lambda o: output_contains(o, r"rdd|RDD|需求|分析", "RDD 相关输出"),
            ],
        ),
        # 步骤 2：切换到 new-prd（命令变更）
        # 注意：此 turn 之后 command 需要变为 new-prd，通过 _switch 标记实现
        Turn(
            user_input = "/new-prd feature 组合筛选",
            output_checks = [
                lambda o: output_contains(o, r"rdd\.md|需求分析|已读取", "读取了 rdd.md"),
            ],
        ),
        # 步骤 3：确认移入正式区
        Turn(
            user_input = "确认移入正式区",
            output_checks = [
                lambda o: output_contains(o, r"prds/|正式区|已移入|注册", "移入正式区确认"),
                lambda o: output_contains(o, r"草稿|drafts|已清理|删除",  "草稿清理提示"),
            ],
            file_checks = [
                # drafts/ 中旧格式目录不应存在
                lambda: file_not_exists("drafts/组合筛选"),
                manual("prds/ 中存在 F-xxx-组合筛选/prd.md"),
                manual("prds/_registry.md 中有新注册行"),
                manual("drafts/_draft-registry.md 中无残留条目"),
            ],
        ),
    ],
)

# ── 注册所有用例 ──────────────────────────────────────────────────────────────

ALL_TESTS: dict[str, TestCase] = {
    "TC-INT-01": TC_INT_01,
    "TC-INT-02": TC_INT_02,
    "TC-INT-04": TC_INT_04,
    "TC-INT-09": TC_INT_09,
    "TC-INT-20": TC_INT_20,
}


# ══════════════════════════════════════════════════════════════════════════════
# Runner 核心
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class TestResult:
    tc_id:      str
    tc_name:    str
    passed:     bool
    checks:     list[Check]
    error:      Optional[str] = None
    duration_s: float         = 0.0


def _run_checks(checks: list[OutputCheck | FileCheck],
                output: Optional[str] = None) -> tuple[list[Check], bool]:
    """执行一组检查，返回 (结果列表, 是否全部通过)"""
    results: list[Check] = []
    all_ok = True
    for fn in checks:
        if isinstance(fn, Check):
            result = fn                         # manual() 直接是 Check 对象
        elif output is not None:
            result = fn(output)                 # output_check：接受 output
        else:
            result = fn()                       # file_check：无参
        results.append(result)
        icon = "⬜" if result.manual else ("✅" if result.passed else "❌")
        detail = f"  ({result.detail})" if result.detail else ""
        print(f"    {icon} {result.name}{detail}")
        if not result.manual and not result.passed:
            all_ok = False
    return results, all_ok


def run_test(tc: TestCase, verbose: bool = False) -> TestResult:
    print(f"\n{'═'*64}")
    print(f"  {tc.id}  {tc.name}")
    print('═'*64)

    start      = time.time()
    all_checks: list[Check] = []
    passed     = True
    error_msg  = None
    messages: list = []

    # ── Setup ────────────────────────────────────────────────────────────────
    try:
        tc.setup()
        print("  ✅ setup")
    except Exception as e:
        return TestResult(tc.id, tc.name, False, [],
                          f"setup failed: {e}\n{traceback.format_exc()}")

    # ── Turns ────────────────────────────────────────────────────────────────
    try:
        # TC-INT-20 在第 3 轮后需要切换 command，用特殊逻辑处理
        command = tc.command

        for i, turn in enumerate(tc.turns):
            # TC-INT-20 第 4 轮起切换为 new-prd
            if tc.id == "TC-INT-20" and i == 3:
                command = "new-prd"

            print(f"\n  ▶ Turn {i+1}  [{command}]  {turn.user_input[:60]}…")
            output, messages = run_turn(messages, turn.user_input, command, verbose)

            # 输出断言
            chks, ok = _run_checks(turn.output_checks, output=output)
            all_checks.extend(chks)
            if not ok:
                passed = False

            # 文件断言
            chks, ok = _run_checks(turn.file_checks)
            all_checks.extend(chks)
            if not ok:
                passed = False

    except Exception as e:
        error_msg = f"{e}\n{traceback.format_exc()}"
        passed    = False
        print(f"\n  ❌ 运行时错误: {e}")

    # ── Teardown ─────────────────────────────────────────────────────────────
    try:
        tc.teardown()
        print("\n  ✅ teardown（测试文件已清理）")
    except Exception as e:
        print(f"\n  ⚠️  teardown 错误: {e}")

    duration = time.time() - start
    print(f"\n  {'✅ PASSED' if passed else '❌ FAILED'}  ({duration:.1f}s)")
    return TestResult(tc.id, tc.name, passed, all_checks, error_msg, duration)


# ══════════════════════════════════════════════════════════════════════════════
# 报告生成
# ══════════════════════════════════════════════════════════════════════════════

def write_report(results: list[TestResult]) -> Path:
    ts     = datetime.now().strftime("%Y-%m-%d_%H-%M")
    path   = REPORTS_DIR / f"eval-{ts}.md"
    passed = sum(1 for r in results if r.passed)
    total  = len(results)

    lines = [
        f"# Eval Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"**结果**：{passed}/{total} passed",
        "",
        "---",
        "",
    ]

    for r in results:
        icon = "✅" if r.passed else "❌"
        lines += [f"## {icon} {r.id}  _{r.name}_  ({r.duration_s:.1f}s)", ""]

        if r.error:
            lines += [f"> ❌ 错误：`{r.error[:300]}`", ""]

        auto   = [c for c in r.checks if not c.manual]
        manual_ = [c for c in r.checks if c.manual]

        if auto:
            lines.append("**自动检查**")
            for c in auto:
                ci = "✅" if c.passed else "❌"
                lines.append(f"- {ci} {c.name}" + (f" — {c.detail}" if c.detail else ""))

        if manual_:
            lines += ["", "**需人工确认**"]
            for c in manual_:
                lines.append(f"- ⬜ {c.name}")

        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# ══════════════════════════════════════════════════════════════════════════════
# CLI 入口
# ══════════════════════════════════════════════════════════════════════════════

def main():
    # Windows GBK console cannot encode emoji — force UTF-8 when running standalone
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="AI PRD Workspace 集成测试 Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--tc",         help="运行指定用例，如 TC-INT-01")
    parser.add_argument("--list",       action="store_true", help="列出所有可用用例")
    parser.add_argument("--clean-only", action="store_true", help="只清理测试产物")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示 AI 输出和工具调用")
    args = parser.parse_args()

    if args.list:
        print("\n可用测试用例：")
        for tc_id, tc in ALL_TESTS.items():
            print(f"  {tc_id}  {tc.name}")
        return

    if args.clean_only:
        for tc in ALL_TESTS.values():
            try:
                tc.teardown()
            except Exception:
                pass
        print("✅ 清理完成")
        return

    if args.tc:
        if args.tc not in ALL_TESTS:
            print(f"❌ 未找到 {args.tc}，可用：{list(ALL_TESTS.keys())}")
            sys.exit(1)
        tests = [ALL_TESTS[args.tc]]
    else:
        tests = list(ALL_TESTS.values())

    results = [run_test(t, args.verbose) for t in tests]

    passed = sum(1 for r in results if r.passed)
    total  = len(results)
    print(f"\n{'═'*64}")
    print(f"  总计：{passed}/{total} passed")
    print('═'*64)

    report = write_report(results)
    print(f"\n📄 报告：{report}")

    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
