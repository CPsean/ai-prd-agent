# evals/ — 测试用例集

> **定位**：对 AI PRD 工作空间中的斜杠命令和质量门禁规则进行系统化验证。每条用例均为独立可执行的 prompt，人工运行后对照检查要点判断结果。

---

## 目录结构

```
evals/
  commands/               ← 命令行为测试（验证命令是否按预期执行）
    TC-*.md
  integration/            ← 跨命令端到端集成测试用例
    TC-workflow-chain.md
  quality-gates/          ← 质检规则测试（验证规则能否正确识别问题）
    QG-pass-cases.md
    QG-fail-cases.md
  scripts/                ← 自动化测试脚本
    test_unit.py          ← 单元测试：命令文件结构 + 规则文件完整性（无需 API）
    eval_runner.py        ← 集成测试 Runner（调用 Anthropic API 验证 AI 行为）
    requirements.txt      ← 依赖：anthropic, pyyaml
    reports/              ← eval_runner 生成的报告（gitignored，仅保留 .gitkeep）
```

---

## 执行方式

### 自动化（推荐）

```bash
# 单元测试（无需 API，< 1 秒）
pip install pytest
pytest evals/scripts/test_unit.py -v

# 集成测试（需要 ANTHROPIC_API_KEY，在 .env 中配置）
pip install -r evals/scripts/requirements.txt
python evals/scripts/eval_runner.py --list          # 列出可用用例
python evals/scripts/eval_runner.py --tc TC-INT-01  # 运行单个用例
python evals/scripts/eval_runner.py -v              # 运行全部，显示详情
```

### 手工执行

1. 打开一个**新的 Claude Code 对话**（避免上下文污染）
2. 复制测试用例的"测试输入"部分，粘贴到对话框执行
3. 对照"检查要点"逐条判断输出是否符合预期
4. 在用例的**状态列**记录结果：

| 符号 | 含义 |
|------|------|
| ✅ | 完全通过 |
| ⚠️ | 部分通过，有偏差但可接受 |
| ❌ | 未通过，需修复命令或规则 |
| — | 未执行 |

---

## 用例 ID 规范

| 前缀 | 含义 |
|------|------|
| `TC-NP-` | /new-prd 命令测试 |
| `TC-UP-` | /update-prd 命令测试 |
| `TC-IP-` | /ingest-prd 命令测试 |
| `TC-PS-` | /prd-summary 命令测试 |
| `TC-PQ-` | /prd-qa 命令测试 |
| `TC-GPS-` | /generate-page-spec 命令测试 |
| `TC-GP-` | /generate-prototype 命令测试 |
| `TC-SD-` | /sync-docs 命令测试 |
| `TC-RC-` | /requirement-clarifier 命令测试 |
| `TC-AR-` | /analyze-requirement 命令测试 |
| `TC-DS-` | /design-solution 命��测试 |
| `TC-WS-` | /write-user-story 命令测试 |
| `TC-DM-` | /design-data-model 命令测试 |
| `TC-AP-` | /abandon-prd 命令测试 |
| `TC-BKL-` | /backlog 命令测试 |
| `TC-OA-` | /import-openapi /update-openapi /export-openapi 命令测试 |
| `TC-MIG-` | 存量迁移测试 |
| `QG-P-` | 质检通过用例 |
| `QG-F-` | 质检失败用例（预期触发特定质检项） |

---

## 维护说明

- 命令逻辑变更后，对应 TC 文件需同步更新"预期行为"
- 质检规则新增条目后，在 `QG-fail-cases.md` 补充对应失败用例
- 每次运行结果记录在用例状态列，不需要另建报告文件
