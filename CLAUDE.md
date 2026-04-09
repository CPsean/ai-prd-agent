# CLAUDE.md — 全局知识库

> Claude Code 自动读取此文件作为项目上下文。记录项目背景、规范和经验，无需每次手动引用。

---

## 项目简介

**项目名称**：AI PRD 工作空间

**产品类型**：（请填写你的产品类型，例如：To B SaaS / 消费类 App / 平台产品）

**项目目标**：为产品经理打造基于 Claude Code 的高效工作空间，支持 PRD 撰写、字段清单整理、原型生成和业务分析等日常工作。AI 作为团队成员之一，可被产品、研发、测试共同使用。

**产品上下文文件**（涉及业务需求时必须参考，首次使用时通过 README Step 1 建立）：
- `context/product-background.md`：产品定位、产品线、核心架构和业务术语
- `context/product-strategy.md`：迭代原则、优先级矩阵、边界约束
- `context/user-persona.md`：用户角色、核心目标、痛点和使用场景
- `context/permission-model.md`：权限模型类型（RBAC/ABAC/PBAC）及角色定义，撰写 PRD 权限控制章节时读取
- `context/platform-support.md`：产品支持的端清单及各端约束（由用户自行维护，模板中的端列表仅为示例），撰写 PRD 端差异说明章节时读取
- `context/iteration-requirement-list.md`：历史迭代需求汇总表（可选），供 `/ingest-prd` 匹配需求 ID；文件不存在时跳过，不影响其他功能

---

## 斜杠命令速查

### PRD 生命周期命令

| 命令 | 用途 | 典型场景 |
|------|------|----------|
| `/new-prd [story-card\|feature\|epic] [标题]` | 新建 PRD，自动创建文件夹、文件和注册 | 有新需求时第一步 |
| `/ingest-prd` | 录入历史PRD，自动重建结构、更新注册表和需求清单，输出缺口问题 | 历史需求归档 |
| `/update-prd [标题] [变更描述]` | 更新 PRD + 自动归档旧版本 + 写 changelog | 评审后需求变更 |
| `/generate-prototype [标题]` | 从 PRD 生成 HTML 可交互原型 | 需要对齐界面结构时 |
| `/prd-qa [问题]` | 基于 PRD 回答具体问题（产品/研发/测试均可问） | 开发过程中的疑问 |
| `/prd-summary [标题或ID]` | 输出 PRD 的对齐摘要 | 评审前、开发启动前 |

### 需求分析命令

| 命令 | 用途 | 阶段 |
|------|------|------|
| `/requirement-clarifier [需求描述]` | JTBD 框架识别真实问题，生成 RDD 卡片 | 需求发现 |
| `/analyze-requirement [需求描述]` | 深度需求分析，输出分析报告至 `analysis/` | Phase 1 |
| `/design-solution` | 方案架构设计，读取分析报告输出方案文档 | Phase 2 |
| `/write-user-story [需求描述]` | 生成 Gherkin 格式开发可交付用户故事 | PRD 撰写期 |
| `/design-data-model [业务场景]` | DDD 原则生成企业级数据库 Schema | 架构阶段 |

---

## Skill 使用决策地图

> 遇到不确定用哪个 skill / command 时，先看这张图。

```
你处于哪个阶段？
│
├─ 还没有任何需求，在做客户研究
│   └─ → skill: jobs-to-be-done
│       （理解客户的 Functional/Social/Emotional Jobs、Pains、Gains）
│
├─ 有一个功能想法/需求，但不确定问题是否说对
│   └─ → /requirement-clarifier
│       （JTBD 快速诊断 X-Y 问题，输出 RDD 卡片）
│       ⚠️ 输出的用户故事是草稿，不是开发规格
│
├─ 需求已澄清，要写开发可交付的用户故事
│   └─ → /write-user-story
│       （Mike Cohn 格式 + Gherkin Given/When/Then）
│
├─ 要做季度 / 半年产品规划，排优先级、定 Roadmap
│   └─ → skill: roadmap-planning
│       （5阶段：收集输入 → 定 Epic → 优先级 → 排期 → 汇报）
│
└─ 要设计数据库表结构 / ER 图
    └─ → /design-data-model
        （DDD 原则，雪花 ID、软删除、审计字段等企业规范）
```

### Skill 边界速记

| 容易混淆的组合 | 区分方式 |
|--------------|---------|
| `jobs-to-be-done` vs `/requirement-clarifier` | 有无具体需求待评估：无 → JTBD；有 → clarifier |
| `/requirement-clarifier` vs `/write-user-story` | 草稿确认问题 → clarifier；正式交付开发 → write-user-story |

---

## PRD 结构规范

### 三层文档体系

| 层级 | 类型 | ID 前缀 | 适用场景 | 模板 |
|------|------|---------|----------|------|
| Layer 1 | 用户故事卡（Story Card） | SC- | 单场景小需求、子故事 | `templates/story-card.md` |
| Layer 2 | 功能 PRD（Feature PRD） | F- | 一个完整功能模块 | `templates/feature-prd.md` |
| Layer 3 | 史诗 PRD（Epic PRD） | E- | 大型项目，含多个功能 | `templates/epic-prd.md` |

**用户故事在每层都是必须项。**

### PRD 目录结构

PRD 初稿先在 `drafts/`，用户确认后移入 `prds/`：

```
drafts/                       ← 第一步：/new-prd 在此创建草稿
  [需求中文标题]/
    prd.md                    ← 草稿内容（待确认，不可被 prd-qa/prd-summary 读取）
    CHANGELOG.md
    archive/

        ↓ 用户说「确认 [标题] PRD 移入正式区」

prds/                         ← 第二步：确认后移入，注册生效
  _registry.md                ← AI 首先读这里，找到对应 PRD 路径
  [需求中文标题]/
    prd.md                    ← 当前有效版本（AI 主要消费此文件）
    CHANGELOG.md              ← 变更记录（不作为主要参考）
    fields.md                 ← 字段清单（Feature/Epic 级别）
    prototype/
      index.html              ← 可交互 HTML 原型（按需生成，需已在正式区）
    archive/
      prd-v1.0.md             ← 历史快照（禁止修改）
  archive/                    ← 整体归档（需求废弃或完工）
```

### AI 读取规则

1. **优先读 `prds/_registry.md`** → 定位目标 PRD 路径
2. **只读 `prd.md`** → 当前版本，不读 `archive/` 下的历史文件
3. **CHANGELOG.md** → 仅在被问及历史变更时读取

### 版本管理规则

- `prd.md` 永���是当前有效版本
- 每次变更：自动归档旧版本 → 更新 `prd.md` → 追加 `CHANGELOG.md`
- 小修改：版本号 +0.1（1.0 → 1.1）；重大重构：升主版本（1.x → 2.0）

### YAML Frontmatter 标准

每个 `prd.md` 必须包含以下头部：

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
| `.claude/commands/` | 斜杠命令定义（Claude Code 原生支持） |
| `.claude/skills/` | 技能规格文档（命令的详细定义参考） |
| `analysis/` | 业务分析产物（需求分析报告等） |
| `assets/` | 图片、原型图、流程图等资源文件 |
| `context/` | 项目上下文（用户画像、产品策略、背景） |
| `docs/` | 参考文档库 |
| `drafts/` | 草稿暂存区：PRD 初稿（待用户确认）+ 方案设计文档 |
| `outputs/` | 对外交付物（演示材料、交接文档等，PRD 不在此） |
| `prds/` | 正式 PRD（唯一权威来源，用户确认后从 drafts/ 移入） |
| `prompts/` | 有效提示词沉淀 |
| `evals/` | 测试用例集（命令行为测试、质检规则验证） |
| `examples/` | 示例库（高质量案例、反面案例、skill 输出样本） |
| `rules/` | 约束性规则（质量门禁、业务规则库、术语规范） |
| `templates/` | 文档模板库 |

### examples/ AI 读取规则

| 文件/目录 | 何时读取 |
|-----------|----------|
| `examples/good-prd/` | 生成或完整审查 PRD 内容时，对齐表达精度和完整度 |
| `examples/anti-patterns/prd-anti-patterns.md` | 执行质检时，识别模糊表达和不完整结构的根因 |
| `examples/skill-outputs/` | 执行对应 skill 时，对齐输出格式和信息密度 |

### rules/ AI 读取规则

| 文件 | 何时读取 |
|------|----------|
| `rules/prd-quality-gates.md` | 执行 `/prd-summary`、`/update-prd` 时，在输出末尾自动进行质检 |
| `rules/business-rules.md` | 撰写或审查 PRD 业务规则章节时，优先检查是否有可复用的全局规则 |
| `rules/terminology.md` | 生成任何 PRD 内容时，术语以此文件为准；用户输入与此不一致时，输出时统一转换 |

---

## 工作规范

### 标准工作流

```
新需求
  → /requirement-clarifier [需求描述]     （澄清真实问题，生成 RDD）
  → /new-prd [type] [标题]               （草稿创建在 drafts/）
  → 填写 prd.md                          （告诉 AI 需求细节 或 手动编辑）
  → 「确认 [标题] PRD 移入正式区」         （移入 prds/，注册）
  → /prd-summary [标题或ID]              （对齐评审）
  → 评审发现问题
  → /update-prd [标题] [变更描述]         （更新 + 自动存档）
  → /generate-prototype [标题]            （按需生成原型，需已在正式区）
  → 用 /update-prd 将 status 改为 approved → released
```

### 字段清单标准

每个字段必须包含：字段名 / 标识符 / 类型 / 长度 / 必填 / 默认值 / 说明 / 业务规则

### 原型生成原则

- 简单需求（单页面/纯逻辑）：文字说明即可，不强制生成原型
- 复杂需求（多页面/需对齐界面）：运行 `/generate-prototype`
- 原型页面与 PRD "页面 & 交互说明"章节一一对应

### 命令变更规范

任何斜杠命令的新增或修改，必须同步更新以下三个文件（"三件套"）：

| 文件 | 作用 | 不更新的后果 |
|------|------|-------------|
| `.claude/commands/xxx.md` | 命令行为定义 | AI 执行逻辑与预期不符 |
| `CLAUDE.md` 速查表 + 目录结构 + 工作流 | AI 和用户的认知对齐 | 参数格式、流程描述与实际行为矛盾 |
| `evals/commands/TC-xxx.md` | 行为验证基准 | 测试通过但验证的是错误行为 |

**三者不一致 = 变更未完成。** AI 在修改命令定义后，应主动检查并同步另外两个文件。

---

## 最佳实践

1. 模糊需求先过 `/requirement-clarifier`，再建 PRD
2. PRD 只有一个权威文件（`prd.md`），不要在外部复制维护
3. 研发/测试有疑问时直接用 `/prd-qa` 问 AI，而非口头询问（仅限正式区 PRD）
4. 每次需求变更用 `/update-prd [标题] [变更描述]`，不要直接编辑 `prd.md` 而不留记录
5. PRD 草稿完成后及时确认移入正式区，避免草稿区积压未发布内容

---

## 经验教训

| 问题 | 解决方案 |
|------|----------|
| 需求理解偏差 | 先用 `/requirement-clarifier` 暴露 X-Y 问题 |
| 版本混乱 | 所有变更通过 `/update-prd`，禁止直接覆盖 |
| 研发对需求有疑问 | 用 `/prd-qa` 基于 PRD 回答，发现缺陷及时补充 |
| 输出不一致 | 使用标准化斜杠命令，不自由发挥提示词 |
| 命令改了但速查表/测试没同步 | 命令变更必须同步三件套（见命令变更规范） |

---

## 项目演进日志

| 日期 | 事件 |
|------|------|
| （首次使用时填写） | 项目初始化 |
