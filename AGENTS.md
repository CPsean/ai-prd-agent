# AGENTS.md — AI PRD 工作空间（OpenAI Codex Agent）

> Codex Agent 自动读取此文件作为项目上下文。本文件是 CLAUDE.md 的 Codex 适配版本，共享所有业务逻辑，仅替换平台专属机制。

---

## 重要：命令执行规则

本工作区的所有操作逻辑定义在 `.claude/commands/` 目录下。

**`$ARGUMENTS` 解释规则**：命令文件中出现的 `$ARGUMENTS` 变量，在 Codex 中等同于「从用户消息中识别到的参数（类型、标题、变更描述等）」。若信息不足，按该命令文件的「解析参数」章节所述规则，主动向用户确认后再继续执行。

**执行方式**：识别用户意图 → 读取对应命令文件 → 按文件步骤执行

---

## 对话开场

用户输入模糊、或说"帮助"/"怎么开始"/"从哪里开始"时，展示以下引导：

```
我可以帮你完成从需求发现到交付物的任意阶段，请描述你的起点：

① 需求还不清晰，先探索真实问题    → 告诉我你的初步想法
② 需求明确，直接写新功能 PRD      → 说"新建功能PRD：[标题]"
③ 小需求 / 单场景                → 说"新建故事卡：[标题]"
④ 大型项目 / 多功能规划           → 说"新建 Epic PRD：[标题]"
⑤ 对已有功能做迭代优化            → 说"迭代优化：[标题]"
⑥ 已有 PRD → 生成页面规格卡      → 说"生成页面规格：[标题]"
⑦ 已有 PRD / 页面规格 → 生成原型  → 说"生成原型：[标题]"
⑧ PRD 更新后核查关联文档一致性    → 说"检查文档一致性：[标题]"

直接描述需求，我来匹配合适的路径。
```

---

## 意图 → 命令文件映射

| 用户意图关键词 | 读取命令文件 |
|-------------|------------|
| 新建PRD / 写需求 / 起草功能 | `.claude/commands/new-prd.md` |
| 更新PRD / 修改需求 / 变更描述 | `.claude/commands/update-prd.md` |
| 需求澄清 / 分析问题 / 不清楚需求 | `.claude/commands/requirement-clarifier.md` |
| 生成页面规格 / 页面规格卡 | `.claude/commands/generate-page-spec.md` |
| 生成原型 / 做原型 / 交互原型 | `.claude/commands/generate-prototype.md` |
| 检查文档一致性 / 同步文档 | `.claude/commands/sync-docs.md` |
| PRD问答 / 需求答疑 / 这个功能怎么... | `.claude/commands/prd-qa.md` |
| PRD摘要 / 评审准备 / 对齐摘要 | `.claude/commands/prd-summary.md` |
| 录入历史PRD / 归档旧需求 | `.claude/commands/ingest-prd.md` |
| 需求分析报告 / 深度分析 | `.claude/commands/analyze-requirement.md` |
| 方案设计 / 架构设计 | `.claude/commands/design-solution.md` |
| 数据模型 / 数据库设计 / 表结构 | `.claude/commands/design-data-model.md` |
| 用户故事 / Gherkin / 开发故事 | `.claude/commands/write-user-story.md` |

意图不明确时，先询问用户确认，再读取命令文件执行。

---

## 首次使用初始化

**执行任何 PRD 操作前，先完成以下检测**（静默检查，有问题才提示）：

1. **作者信息**：检查 `context/workspace-config.md` 是否存在且 `author` 字段已填写（非空、非占位符）。
   - 未填写时，在执行前提示：「请告诉我你的姓名，将自动保存到 workspace-config.md，之后无需再次输入。」
   - 用户回复后写入文件，再继续；回复"跳过"则 author 留空继续。

2. **注册表初始化**：检查 `prds/_registry.md` 是否存在。
   - 不存在时自动创建，内容参考现有格式（如有样本）或使用标准表头。

3. **产品上下文提示**（仅首次，不阻塞）：若 `context/product-background.md` 不存在，在完成当前操作后提示用户参考 README 建立产品背景文件。

---

## 项目简介

**项目名称**：AI PRD 工作空间

**项目目标**：为产品经理打造高效 AI 协作工作空间，支持 PRD 撰写、字段清单整理、原型生成和业务分析等日常工作。AI 作为团队成员，可被产品、研发、测试共同使用。

**产品上下文文件**（涉及业务需求时必须参考）：
- `context/workspace-config.md`：工作区配置（作者姓名等），**不应提交到公共仓库**
- `context/product-background.md`：产品定位、产品线、核心架构和业务术语
- `context/product-strategy.md`：迭代原则、优先级矩阵、边界约束
- `context/user-persona.md`：用户角色、核心目标、痛点和使用场景
- `context/permission-model.md`：权限模型（RBAC/ABAC/PBAC），撰写权限控制章节时读取
- `context/platform-support.md`：支持端清单及各端约束，撰写端差异章节时读取
- `context/iteration-requirement-list.md`：历史迭代需求汇总（可选），不存在时跳过

---

## PRD 结构规范

### 三层文档体系

| 层级 | 类型 | ID 前缀 | 适用场景 | 模板 |
|------|------|---------|----------|------|
| Layer 1 | 用户故事卡（Story Card） | SC- | 单场景小需求、子故事 | `templates/story-card.md` |
| Layer 2 | 功能 PRD（Feature PRD） | F- | 一个完整功能模块 | `templates/feature-prd.md` |
| Layer 3 | 史诗 PRD（Epic PRD） | E- | 大型项目，含多个功能 | `templates/epic-prd.md` |

### PRD 目录结构

```
drafts/[标题]/prd.md      ← 草稿（待确认）
prds/_registry.md         ← AI 首先读这里，定位 PRD 路径
prds/[标题]/prd.md        ← 正式版（唯一权威来源）
prds/[标题]/CHANGELOG.md  ← 变更记录
prds/[标题]/archive/      ← 历史快照（禁止修改）
```

### AI 读取规则

1. **优先读 `prds/_registry.md`** → 定位目标 PRD 路径
2. **只读 `prd.md`** → 不读 `archive/` 下历史文件
3. **CHANGELOG.md** → 仅在被问及历史变更时读取

### YAML Frontmatter 标准

```yaml
---
type: story-card | feature-prd | epic-prd
id: SC-001 | F-001 | E-001
title: 中文标题
status: draft | in-review | approved | released
version: "1.0"
created: YYYY-MM-DD
updated: YYYY-MM-DD
author:
feature-area:
has-prototype: false
---
```

---

## 文件夹说明

| 文件夹 | 用途 |
|--------|------|
| `.claude/commands/` | 命令逻辑定义（两平台共用单一源） |
| `analysis/` | 业务分析产物（需求分析报告等） |
| `context/` | 项目上下文（用户画像、产品策略、背景） |
| `drafts/` | 草稿暂存区（PRD 初稿 + 方案设计文档） |
| `prds/` | 正式 PRD（唯一权威来源） |
| `templates/` | 文档模板库 |
| `rules/` | 约束性规则（质量门禁、业务规则、术语规范） |
| `examples/` | 示例库（高质量案例、反面案例） |
| `evals/` | 测试用例集 |

### 关键文件读取时机

| 文件 | 何时读取 |
|------|----------|
| `examples/good-prd/` | 生成或审查 PRD 内容时 |
| `examples/anti-patterns/prd-anti-patterns.md` | 执行质检时 |
| `rules/prd-quality-gates.md` | 执行摘要或更新 PRD 时，输出末尾自动质检 |
| `rules/business-rules.md` | 撰写或审查业务规则章节时 |
| `rules/terminology.md` | 生成任何 PRD 内容时，术语以此为准 |

---

## 工作规范

### 标准工作流

```
新需求（模糊）→ requirement-clarifier → new-prd（读取 RDD，跳过需求讨论）

新需求（明确）→ new-prd → 两轮细节澄清 → 确认移入正式区
  → 涉及页面变更 → generate-page-spec → generate-prototype

评审 & 迭代 → prd-summary → update-prd → sync-docs → 状态改为 released
```

### 版本管理规则

- 小修改：版本号 +0.1；重大重构：升主版本
- 每次变更：自动归档旧版本 → 更新 prd.md → 追加 CHANGELOG.md

### 命令变更四件套

命令逻辑变更时，必须同步更新：

| 文件 | 说明 |
|------|------|
| `.claude/commands/xxx.md` | 两平台共用的单一命令源 |
| `CLAUDE.md` 速查表 | Claude Code 用户认知对齐 |
| `AGENTS.md` 映射表 | Codex 意图映射更新 |
| `evals/commands/TC-xxx.md` | 行为验证基准 |

---

## 评测执行约定

在执行 `evals/` 目录下的测试文档时，遵守以下规则：

- **文件结果验证**：读取文件后直接判断，结论确定，标 ✅ 或 ❌
- **交互行为验证**：若执行为单轮持续模式，允许使用**模拟用户回复**推进交互链（如 author 初始化时自动填写 `Codex测试员`，A/B 询问时自动选择验证价值最高的选项），此类验证项标 ⚠️ 并注明"交互为模拟执行"
- **TC 回填位置**：结果写入与实际验证场景**最匹配的 TC 条目**；若一步覆盖多个用例，在主条目记录状态，备注中说明关联用例编号
- **不改变业务规则**：模拟回复仅用于推进验证流程，不得绕过命令定义中的核心逻辑判断

---

## 最佳实践

1. 模糊需求先过需求澄清，再建 PRD
2. PRD 只有一个权威文件（`prd.md`），不在外部复制维护
3. 研发/测试有疑问时描述问题让 AI 基于 PRD 回答（仅限正式区）
4. 每次需求变更通过更新命令执行，不直接编辑 `prd.md` 而不留记录
5. PRD 草稿完成后及时确认移入正式区，避免草稿积压
