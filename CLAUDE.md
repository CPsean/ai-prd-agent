# CLAUDE.md — 全局知识库

> Claude Code 自动读取此文件作为项目上下文。记录项目背景、规范和经验，无需每次手动引用。

---

## 对话开场

**触发条件**：用户输入模糊（无具体命令）、或输入"帮助"/"从哪里开始"/"我该用哪个命令"/"怎么开始"时，展示以下引导菜单。用户携带具体命令时直接执行，不展示菜单。

```
我可以帮你完成从需求发现到交付物的任意阶段，请选择你的起点：

① 需求还不清晰，先探索真实问题    → /requirement-clarifier [需求描述]
② 需求明确，直接写新功能 PRD      → /new-prd feature [标题]
③ 小需求 / 单场景                → /new-prd story-card [标题]
④ 大型项目 / 多功能规划           → /new-prd epic [标题]
⑤ 对已有功能做迭代优化            → /new-prd feature [标题]（过程中选迭代模板）
⑥ 已有 PRD → 生成页面规格卡      → /generate-page-spec [标题]
⑦ 已有 PRD / 页面规格 → 生成原型  → /generate-prototype [标题]
⑧ PRD 更新后核查关联文档一致性    → /sync-docs [标题]

直接输入编号或描述你的需求，我来匹配合适的路径。
```

**意图匹配规则**：
- 输入编号 → 直接进入对应路径
- 描述新功能需求 → 询问需求是否清晰，清晰走②，模糊走①
- 说"改一下 XX 功能"/"优化 XX" → 走⑤
- 说"画原型"/"做原型" → 判断是否有 PRD，有走⑦，无走①→②→⑦

---

## 项目简介

**项目名称**：AI PRD 工作空间

**产品类型**：（请填写你的产品类型，例如：To B SaaS / 消费类 App / 平台产品）

**项目目标**：为产品经理打造基于 Claude Code 的高效工作空间，支持 PRD 撰写、字段清单整理、原型生成和业务分析等日常工作。AI 作为团队成员之一，可被产品、研发、测试共同使用。

**产品上下文文件**（涉及业务需求时必须参考，首次使用时通过 README Step 1 建立）：
- `context/workspace-config.md`：工作区配置（作者姓名等默认值），首次运行 `/new-prd` 时自动引导创建；**不应提交到公共仓库**
- `context/product-background.md`：产品定位、产品线、核心架构和业务术语
- `context/product-strategy.md`：迭代原则、优先级矩阵、边界约束
- `context/user-persona.md`：用户角色、核心目标、痛点和使用场景
- `context/permission-model.md`：权限模型类型（RBAC/ABAC/PBAC）及角色定义，撰写 PRD 权限控制章节时读取
- `context/platform-support.md`：产品支持的端清单及各端约束（由用户自行维护，模板中的端列表仅为示例），撰写 PRD 端差异说明章节时读取
- `context/iteration-requirement-list.md`：历史迭代需求汇总表（可选），供 `/ingest-prd` 匹配需求 ID；文件不存在时跳过，不影响其他功能
- `context/business-glossary.md`：产品业务术语字典，随需求迭代增长；PRD §4 只写本需求新引入术语，已有术语引用此文件；由 `/requirement-clarifier` 保存 RDD 后 AI 提议追加，用户确认写入
- `context/product-feature-map.md`：产品功能结构树（Mermaid）+ 功能编号前缀映射表；PRD §5 只写本需求新增/调整节点，完整结构见此文件；仅在 PRD 移入正式区（prds/）后 AI 提议更新，用户确认写入

---

## 斜杠命令速查

### PRD 生命周期命令

| 命令 | 用途 | 典型场景 |
|------|------|----------|
| `/new-prd [story-card\|feature\|iteration\|epic] [标题]` | 新建 PRD，含迭代类型识别和两轮澄清 | 有新需求或迭代优化时 |
| `/ingest-prd` | 录入历史PRD，自动重建结构、更新注册表和需求清单，输出缺口问题 | 历史需求归档 |
| `/update-prd [标题] [变更描述]` | 更新 PRD + 自动归档旧版本 + 写 changelog | 评审后需求变更 |
| `/generate-page-spec [标题]` | 从 PRD 提取页面规格卡（原型生成的前置步骤） | PRD 确认后，生成原型前 |
| `/generate-prototype [标题]` | 从页面规格卡（优先）或 PRD 生成 HTML 可交互原型 | 需要对齐界面结构时 |
| `/sync-docs [标题]` | 检查 PRD、页面规格卡、原型的一致性，列出差异和建议操作 | PRD 更新后核查关联文档 |
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

**Feature PRD 章节结构（§1-§11）**：

| 章节 | 标题 | 说明 |
|------|------|------|
| §1 | 文档元数据 | 含关联 RDD/规格卡/原型字段 |
| §2 | 文档修订记录 | |
| §3 | 需求概要 | 3.1 问题与机会 / 3.2 目标用户 / 3.3 方案概述 / 3.4 成功指标 |
| §4 | 需求对象与概念模型 | 只写本 PRD **新引入**术语，已有术语引用 `context/business-glossary.md` |
| §5 | 功能结构 | 只写本 PRD **新增/调整**节点，完整结构见 `context/product-feature-map.md` |
| §6 | 用户故事与用例 | Epic + Must Have，含 Gherkin AC（故事级） |
| §7 | 功能清单 | 编号格式 `[AREA]-[CAT]-[SEQ]`，先查前缀映射表；名称全限定；动词具体 |
| §8 | 功能需求说明书 | 逐功能展开；§8.x.1-§8.x.3 必填；§8.x.4-§8.x.9 按条件填（不适用填「不涉及」） |
| §9 | 非功能性需求 | 性能 / 安全 / 可用性 / 兼容性 / 数据统计 |
| §10 | 范围外（Out of Scope） | |
| §11 | 开放问题 | approved 前须清空 |

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
新需求（模糊）
  → /requirement-clarifier [需求描述]     （JTBD 发现真实问题，生成 RDD 卡片）
  → 自动衔接：/new-prd [标题]            （读取 RDD，跳过需求讨论）

新需求（明确）/ 迭代优化
  → /new-prd [type] [标题]               （AI 询问新功能 or 迭代，选对应模板）

草稿阶段（两轮澄清）
  → AI 主动提问：方案细节澄清             （产品视角，≤3问/轮）
  → AI 判断收敛 → 建议移入正式区
  → 「确认 [标题] PRD 移入正式区」         （移入 prds/，注册）
  → AI 提议更新 context 文件              （product-feature-map.md 新节点 + business-glossary.md 新术语，用户确认后写入）
  → AI 自动判断是否涉及页面变更

涉及页面变更
  → /generate-page-spec [标题]            （PRD → 页面规格卡）
  → /generate-prototype [标题]            （页面规格卡 → 可交互原型）

评审 & 迭代
  → /prd-summary [标题或ID]              （评审前对齐）
  → /update-prd [标题] [变更描述]         （更新 + 自动存档）
  → /sync-docs [标题]                    （检查关联文档一致性）
  → 用 /update-prd 将 status 改为 approved → released
```

### 字段清单标准

每个字段必须包含：字段名 / 标识符 / 类型 / 长度 / 必填 / 默认值 / 说明 / 业务规则

### 原型生成原则

- 简单需求（单页面/纯逻辑）：文字说明即可，不强制生成原型
- 复杂需求（多页面/需对齐界面）：运行 `/generate-prototype`
- 原型页面与 PRD "页面 & 交互说明"章节一一对应

### 命令变更规范

任何斜杠命令的新增或修改，必须同步更新以下四个文件（"四件套"）：

| 文件 | 作用 | 不更新的后果 |
|------|------|-------------|
| `.claude/commands/xxx.md` | 命令行为定义（两平台共用单一源） | AI 执行逻辑与预期不符 |
| `CLAUDE.md` 速查表 + 目录结构 + 工作流 | Claude Code 用户认知对齐 | 参数格式、流程描述与实际行为矛盾 |
| `AGENTS.md` 意图映射表 | Codex 用户意图→命令文件映射 | Codex 用户无法正确路由到命令 |
| `evals/commands/TC-xxx.md` | 行为验证基准 | 测试通过但验证的是错误行为 |

**四者不一致 = 变更未完成。** AI 在修改命令定义后，应主动检查并同步其余三个文件。

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
| PRD 变更后 RDD 未同步 | `/update-prd` 步骤 7.3 自动检查 `rdd.md` 是否受影响，涉及核心范围/AC/指标变更时主动提示 |

---

## 项目演进日志

| 日期 | 事件 |
|------|------|
| （首次使用时填写） | 项目初始化 |
| 2026-04-10 | **串联流水线**：`/requirement-clarifier` 完成后自动保存 RDD 至 `drafts/[标题]/rdd.md` 并引导进入 `/new-prd`；`/new-prd` 新增步骤0（新功能/迭代识别）、步骤5.5（PRD细节两轮澄清，AI自判收敛）、移入正式区后自动判断是否涉及页面变更并引导后续步骤 |
| 2026-04-10 | **新增命令 `/generate-page-spec`**：PRD → 页面规格卡，作为原型生成的前置中间层，保存至 `prds/[标题]/page-spec.md`，写入 `source-prd-version` 和 `last-updated` 元数据 |
| 2026-04-10 | **新增命令 `/sync-docs`**：读取 PRD CHANGELOG 与关联文档元数据，比对版本差异，输出潜在不一致清单 + 建议操作；`/update-prd`、`/generate-prototype` 末尾同步加入轻量提示 |
| 2026-04-10 | **新增模板 `templates/iteration-prd.md`**：迭代类 PRD 精简模板，含 `modifies` 关联字段、变更前→变更后结构、只写变化部分的页面/规则章节；`/new-prd` 步骤0新增迭代类型识别和模板路由 |
| 2026-04-10 | **对话开场引导**：CLAUDE.md 顶部新增路径选择菜单（8条路径），模糊输入或触发词时展示，命令速查表和标准工作流同步更新 |
| 2026-04-13 | **`/update-prd` 新增步骤 7.3 RDD 同步检查**：变更涉及核心范围/用户角色/AC/成功指标时，自动检测 `rdd.md` 是否存在并提示用户同步更新，避免 RDD 与 PRD 静默漂移 |
| 2026-04-13 | **新增 Codex Agent 支持**（`codex-support` 分支）：创建 `AGENTS.md` 作为 Codex 入口，`.claude/commands/` 升级为两平台共用单一源，命令变更规范从"三件套"升级为"四件套"（新增 AGENTS.md 映射表同步要求） |
| 2026-04-15 | **PRD 输出质量升级**：(1) `/requirement-clarifier` 新增 Step 0 按需读取 6 个 context 文件、Step 5 输出 RDD 双节结构（需求摘要 7 维 + 初步方案 6 小节）、Step 6.5 业务术语提议；(2) `templates/feature-prd.md` 重写为 §1-§11 完整结构，含 §7 功能清单（[AREA]-[CAT]-[SEQ] 编号）和 §8 逐功能展开（§8.1-§8.9 条件填写）；(3) 新建 `templates/rdd.md` 作为 RDD 格式基准；(4) 新建 `context/business-glossary.md`（业务术语字典）和 `context/product-feature-map.md`（功能结构树 + 前缀映射表），由需求/PRD 流程联动维护；(5) `/new-prd` 新增 5a 功能编号生成、5b §8 展开指引、Step 7 后 context 同步提示；(6) `/update-prd` 新增 Step 7.7 自动质检 + Step 8 context 同步检查；(7) `/ingest-prd` 新增 Step 9 context 同步；(8) `rules/prd-quality-gates.md` 新增 G7（功能清单规范）和 G8（§8 必填完整性） |
