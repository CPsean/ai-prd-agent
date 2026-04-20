# evals/ — 测试用例集

> **定位**：对 AI PRD 工作空间中的斜杠命令和质量门禁规则进行系统化验证。每条用例均为独立可执行的 prompt，人工运行后对照检查要点判断结果。

---

## 目录结构

```
evals/
  commands/               ← 命令行为测试（验证命令是否按预期执行）
    TC-new-prd.md
    TC-update-prd.md
    TC-ingest-prd.md
    TC-prd-summary.md
    TC-prd-qa.md
    TC-generate-page-spec.md
    TC-generate-prototype.md
    TC-sync-docs.md
    TC-requirement-clarifier.md
    TC-analyze-requirement.md
    TC-design-solution.md
    TC-write-user-story.md
    TC-design-data-model.md
  quality-gates/          ← 质检规则测试（验证规则能否正确识别问题）
    QG-pass-cases.md
    QG-fail-cases.md
```

---

## 执行方式

### Claude Code

1. 打开一个**新的 Claude Code 对话**（避免上下文污染）
2. 复制测试用例的"测试输入"部分，粘贴到对话框执行
3. 对照"检查要点"逐条判断输出是否符合预期
4. 在用例状态表的 **`Claude Code 状态`** 行记录结果

### Codex Agent

1. 打开一个**新的 Codex Agent 对话**（确保工作目录为本仓库根目录）
2. 使用各 TC 文件中 **`Codex 等效输入`** 对应的自然语言描述执行
3. 对照相同的"检查要点"逐条判断（文件操作结果与平台无关）
4. 在用例状态表的 **`Codex 状态`** 行记录结果

**状态符号**（两平台通用）：

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
| `QG-P-` | 质检通过用例 |
| `QG-F-` | 质检失败用例（预期触发特定质检项） |

---

## 维护说明

- 命令逻辑变更后，对应 TC 文件需同步更新"预期行为"
- 质检规则新增条目后，在 `QG-fail-cases.md` 补充对应失败用例
- 每次运行结果记录在用例状态列，不需要另建报告文件
- 新增命令时，TC 文件需同时提供"测试输入"（斜杠命令）和"Codex 等效输入"（自然语言）两种格式
