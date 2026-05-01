"""
AI PRD Workspace — 单元测试套件
==================================
不调用 API，毫秒级运行。覆盖三层：

  Layer 1: eval_runner.py 内部函数（断言工具 + 文件工具）
  Layer 2: 命令文件结构完整性
  Layer 3: 规则文件 + CLAUDE.md 完整性

用法:
  pip install pytest
  pytest evals/scripts/test_unit.py -v
  pytest evals/scripts/test_unit.py -v -k "TestCommandFiles"
"""

import re
import sys
from pathlib import Path

# 将 eval_runner 所在目录加入 path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import eval_runner as er

REPO_ROOT    = Path(__file__).resolve().parent.parent.parent
COMMANDS_DIR = REPO_ROOT / ".claude" / "commands"
RULES_DIR    = REPO_ROOT / "rules"

# Commands listed in CLAUDE.md 速查表（/xxx 是占位符，排除）
CLAUDE_MD_COMMANDS = {
    "backlog",
    "design-solution",
    "generate-page-spec",
    "generate-prototype",
    "import-context",
    "ingest-prd",
    "new-prd",
    "prd-qa",
    "prd-summary",
    "requirement-clarifier",
    "update-prd",
    "write-user-story",
}


# ══════════════════════════════════════════════════════════════════════════════
# Layer 1: eval_runner 内部函数
# ══════════════════════════════════════════════════════════════════════════════

class TestFileExistsAssertion:
    def test_true_when_file_present(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        (tmp_path / "a.md").write_text("x")
        assert er.file_exists("a.md").passed

    def test_false_when_file_absent(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        assert not er.file_exists("missing.md").passed

    def test_detail_on_failure(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        r = er.file_exists("missing.md")
        assert r.detail  # detail 不为空


class TestFileNotExistsAssertion:
    def test_true_when_absent(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        assert er.file_not_exists("ghost.md").passed

    def test_false_when_present(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        (tmp_path / "here.md").write_text("x")
        assert not er.file_not_exists("here.md").passed


class TestFrontmatterAssertion:
    def test_string_match(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        (tmp_path / "f.md").write_text("---\nstatus: approved\n---\ncontent")
        assert er.frontmatter("f.md", "status", "approved").passed

    def test_string_mismatch(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        (tmp_path / "f.md").write_text("---\nstatus: draft\n---\n")
        r = er.frontmatter("f.md", "status", "approved")
        assert not r.passed
        assert "draft" in r.detail

    def test_integer_value(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        (tmp_path / "f.md").write_text("---\nphase: 1\n---\n")
        assert er.frontmatter("f.md", "phase", 1).passed

    def test_missing_frontmatter_block(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        (tmp_path / "f.md").write_text("no frontmatter here")
        assert not er.frontmatter("f.md", "status", "x").passed

    def test_file_not_found(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        r = er.frontmatter("nope.md", "status", "x")
        assert not r.passed


class TestTextInFileAssertion:
    def test_found(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        (tmp_path / "f.md").write_text("hello world")
        assert er.text_in_file("f.md", "hello").passed

    def test_not_found(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        (tmp_path / "f.md").write_text("hello world")
        assert not er.text_in_file("f.md", "missing").passed

    def test_file_not_found(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        assert not er.text_in_file("ghost.md", "x").passed


class TestOutputContainsAssertion:
    def test_simple_match(self):
        assert er.output_contains("As a user I want to...", r"As a").passed

    def test_no_match(self):
        assert not er.output_contains("hello world", r"user story").passed

    def test_case_insensitive(self):
        assert er.output_contains("USER STORY created", r"user story").passed

    def test_multiline_match(self):
        assert er.output_contains("line1\nPhase 2 starts\nline3", r"Phase 2").passed

    def test_custom_label_in_name(self):
        r = er.output_contains("foo bar", r"foo", label="my-label")
        assert r.name == "my-label"


class TestManualCheck:
    def test_always_passes(self):
        r = er.manual("human should verify this")
        assert r.passed
        assert r.manual


class TestToolRead:
    def test_basic_read(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        (tmp_path / "a.md").write_text("line1\nline2\nline3")
        out = er._t_read("a.md")
        assert "line1" in out and "line3" in out

    def test_missing_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        out = er._t_read("nope.md")
        assert "does not exist" in out

    def test_offset_and_limit(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        (tmp_path / "a.md").write_text("\n".join(f"L{i}" for i in range(10)))
        out = er._t_read("a.md", offset=3, limit=2)
        assert "L3" in out and "L4" in out
        assert "L5" not in out
        assert "L2" not in out

    def test_line_numbers_in_output(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        (tmp_path / "a.md").write_text("only line")
        out = er._t_read("a.md")
        assert "1\t" in out  # cat -n format


class TestToolWrite:
    def test_creates_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        er._t_write("new.md", "hello")
        assert (tmp_path / "new.md").read_text() == "hello"

    def test_creates_parent_dirs(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        er._t_write("deep/sub/file.md", "content")
        assert (tmp_path / "deep" / "sub" / "file.md").exists()

    def test_overwrites_existing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        (tmp_path / "f.md").write_text("old")
        er._t_write("f.md", "new")
        assert (tmp_path / "f.md").read_text() == "new"


class TestToolEdit:
    def test_basic_replace(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        (tmp_path / "e.md").write_text("hello world")
        er._t_edit("e.md", "hello", "goodbye")
        assert (tmp_path / "e.md").read_text() == "goodbye world"

    def test_replaces_first_occurrence_only(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        (tmp_path / "e.md").write_text("a a a")
        er._t_edit("e.md", "a", "b")
        assert (tmp_path / "e.md").read_text() == "b a a"

    def test_replace_all(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        (tmp_path / "e.md").write_text("a a a")
        er._t_edit("e.md", "a", "b", replace_all=True)
        assert (tmp_path / "e.md").read_text() == "b b b"

    def test_string_not_found(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        (tmp_path / "e.md").write_text("hello")
        out = er._t_edit("e.md", "missing", "x")
        assert "not found" in out

    def test_missing_file(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        out = er._t_edit("nope.md", "a", "b")
        assert "does not exist" in out


class TestToolGlob:
    def test_finds_matching_files(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        (tmp_path / "a.md").write_text("x")
        (tmp_path / "b.md").write_text("x")
        (tmp_path / "c.txt").write_text("x")
        out = er._t_glob("*.md")
        assert "a.md" in out
        assert "b.md" in out
        assert "c.txt" not in out

    def test_no_match(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        out = er._t_glob("*.xyz")
        assert "no matches" in out


class TestToolGrep:
    def test_finds_file_with_match(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        (tmp_path / "x.md").write_text("status: approved\n")
        (tmp_path / "y.md").write_text("status: draft\n")
        out = er._t_grep("approved", path=".")
        assert "x.md" in out
        assert "y.md" not in out

    def test_no_match(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        (tmp_path / "x.md").write_text("nothing here")
        out = er._t_grep("approved", path=".")
        assert "no matches" in out

    def test_content_mode(self, tmp_path, monkeypatch):
        monkeypatch.setattr(er, "REPO_ROOT", tmp_path)
        (tmp_path / "x.md").write_text("line1\napproved here\nline3")
        out = er._t_grep("approved", path=".", output_mode="content")
        assert "approved here" in out


# ══════════════════════════════════════════════════════════════════════════════
# Layer 2: 命令文件结构完整性
# ══════════════════════════════════════════════════════════════════════════════

# ingest-prd.md 是委托型命令（将执行权交给 skill），没有标准标题和 $ARGUMENTS
DELEGATION_COMMANDS = {"ingest-prd.md"}

# 命令文件中显式声明"不存在则静默跳过"的可选 context 文件
OPTIONAL_CONTEXT_FILES = {
    "domain-checklists.md",   # new-prd / requirement-clarifier / update-prd 中已写"不存在则跳过"
    "pending-flywheel.md",    # sync-docs 中已写"不存在则跳过"
}


class TestCommandFiles:
    def test_all_claude_md_commands_have_files(self):
        missing = [
            cmd for cmd in CLAUDE_MD_COMMANDS
            if not (COMMANDS_DIR / f"{cmd}.md").exists()
        ]
        assert missing == [], f"CLAUDE.md 引用的命令缺少对应文件: {missing}"

    def test_all_command_files_have_h1_heading(self):
        bad = [
            f.name for f in COMMANDS_DIR.glob("*.md")
            if f.name not in DELEGATION_COMMANDS
            and not f.read_text(encoding="utf-8").startswith("# ")
        ]
        assert bad == [], f"命令文件缺少 '# ' 一级标题: {bad}"

    def test_all_command_files_have_arguments_placeholder(self):
        bad = [
            f.name for f in COMMANDS_DIR.glob("*.md")
            if f.name not in DELEGATION_COMMANDS
            and "$ARGUMENTS" not in f.read_text(encoding="utf-8")
        ]
        assert bad == [], f"命令文件缺少 $ARGUMENTS 占位符: {bad}"

    def test_all_command_files_nonempty(self):
        short = [
            f.name for f in COMMANDS_DIR.glob("*.md")
            if len(f.read_text(encoding="utf-8").strip()) < 50
        ]
        assert short == [], f"命令文件内容过短（< 50 字符）: {short}"

    def test_no_command_file_references_missing_context_files(self):
        """命令文件中 context/xxx.md 引用的必填文件必须存在（可选文件豁免）"""
        context_dir = REPO_ROOT / "context"
        bad: list[str] = []
        for f in COMMANDS_DIR.glob("*.md"):
            refs = re.findall(r'context/([a-z][a-z\-]+\.md)', f.read_text(encoding="utf-8"))
            for ref in refs:
                if ref in OPTIONAL_CONTEXT_FILES:
                    continue
                if not (context_dir / ref).exists():
                    bad.append(f"{f.name} -> context/{ref}")
        assert bad == [], f"命令文件引用了不存在的 context 文件: {bad}"


# ══════════════════════════════════════════════════════════════════════════════
# Layer 3: 规则文件 + CLAUDE.md 完整性
# ══════════════════════════════════════════════════════════════════════════════

class TestRulesFiles:
    def test_required_rule_files_exist(self):
        required = [
            "prd-quality-gates.md",
            "data-flywheel.md",
            "business-rules.md",
            "terminology.md",
            "routing-signals.md",
        ]
        missing = [f for f in required if not (RULES_DIR / f).exists()]
        assert missing == [], f"缺少规则文件: {missing}"

    def test_prd_quality_gates_has_checklist_section(self):
        content = (RULES_DIR / "prd-quality-gates.md").read_text(encoding="utf-8")
        assert "检查项清单" in content

    def test_data_flywheel_has_required_sections(self):
        content = (RULES_DIR / "data-flywheel.md").read_text(encoding="utf-8")
        for section in ["写出方向", "读入方向", "强制规则"]:
            assert section in content, f"data-flywheel.md 缺少章节: {section}"


class TestClaudeMd:
    def test_required_sections_exist(self):
        content = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        for section in ["斜杠命令速查", "数据飞轮", "工作规范", "经验教训"]:
            assert section in content, f"CLAUDE.md 缺少章节: {section}"

    def test_all_referenced_rule_files_exist(self):
        content = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        refs = re.findall(r'`rules/([^`]+\.md)`', content)
        missing = [r for r in refs if not (RULES_DIR / r).exists()]
        assert missing == [], f"CLAUDE.md 引用了不存在的 rules 文件: {missing}"

    def test_all_referenced_docs_files_exist(self):
        content = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        refs = re.findall(r'\[`?docs/([^`\]]+\.md)`?\]', content)
        docs_dir = REPO_ROOT / "docs"
        missing = [r for r in refs if not (docs_dir / r).exists()]
        assert missing == [], f"CLAUDE.md 引用了不存在的 docs 文件: {missing}"

    def test_skill_decision_map_references_valid_commands(self):
        content = (REPO_ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        # 决策地图中 /command 形式的引用（排除 /new-prd 这类带参数的）
        refs = re.findall(r'→ /([a-z][a-z-]+)', content)
        missing = [r for r in refs if not (COMMANDS_DIR / f"{r}.md").exists()]
        assert missing == [], f"CLAUDE.md 决策地图引用了不存在的命令: {missing}"
