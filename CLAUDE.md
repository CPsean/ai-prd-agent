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
- 描述新功能需求 → **默认走①**（`/requirement-clarifier`）  
  以下情况才走②（直接 `/new-prd`）：  
  · 用户明确说"不需要澄清"/"直接写 PRD"/"方案已定"  
  · 且输入中不含任何 X-Y 风险信号  

  **X-Y 风险信号——命中任一条强制走①，不询问**：  
  · 用户直接给出解决方案而非问题（如"系统自动调整至页面边缘"）  
  · 缺少边界条件定义（无阈值 / 范围 / 异常处理说明）  
  · 涉及多角色但只描述了一个角色的视角  
  · 可能是已有功能的边界场景而非全新独立功能  
  · 命中 `rules/routing-signals.md` 中的产品专属信号
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
- `context/platform-support.md`：产品支持的端清单及各端约束（由用户自行维护，模板中的端列表仅为示例）；读取命令：`/requirement-clarifier` Phase 1 背景读取（识别端约束信号）、`/new-prd` 写 §9.4 兼容性时读取
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
| `/requirement-clarifier [需求描述 \| 标题]` | 两阶段：Phase 1 生成用户故事确认方向 → Phase 2 多轮对话生成 RDD（对话信号驱动按需加载 context）；传入已有标题可续接中断的分析 | 需求发现 |
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
├─ 有一个功能想法/需求（无论描述是否清晰）
│   └─ → /requirement-clarifier         （默认路径）
│       （JTBD 快速诊断 X-Y 问题，输出 RDD 卡片）
│       ⚠️ 输出的用户故事是草稿，不是开发规格
│       ℹ️ 仅当用户明确说"方案已定，直接写PRD"且无 X-Y 风险信号时才走 /new-prd
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

> 详见 [`docs/prd-standards.md`](docs/prd-standards.md)。
> 执行 `/new-prd`、`/update-prd`、`/prd-summary`、`/generate-page-spec` 时读取。

关键速查：
- 三层 ID 前缀：SC-（故事卡）/ F-（功能PRD）/ E-（史诗PRD）
- PRD 权威位置：`prds/[标题]/prd.md`（草稿在 `drafts/`）
- Feature PRD 章节：§1 元数据 → §6 用户故事 → §7 功能清单 → §8 功能说明 → §11 开放问题

---

## 文件夹说明

> 各目录用途详见 [`docs/prd-standards.md`](docs/prd-standards.md)。

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
| `rules/data-flywheel.md` | 执行任何 PRD 命令时，判断飞轮触发条件、新术语/新功能节点的认定标准和输出格式 |

---

## 工作规范

### 标准工作流

```
新需求（标准路径）
  → /requirement-clarifier [需求描述]     （Phase 1：生成用户故事，用户确认方向）
  → /requirement-clarifier [标题]         （Phase 2：多轮对话，对话信号驱动按需加载 context，生成完整 RDD）
  → rdd.md status=rdd-complete            （自动衔接：/new-prd [标题] 读取 RDD，跳过需求讨论）
  → 中断续接：新对话中运行 /requirement-clarifier [标题] 从断点恢复

新需求（用户主动跳过澄清）
  → /new-prd [type] [标题]               （需用户明确说"方案已定"/"直接写 PRD"，且无 X-Y 风险信号）
  → AI 在 Step 5-0 标注"跳过澄清"，rdd.md 缺失时仍给出提示

迭代优化
  → /new-prd iteration [标题]

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

> 修改任何斜杠命令时，必须同步"四件套"。详见 [`docs/contributing.md`](docs/contributing.md)。

---

## 数据飞轮准则

> 详细判断逻辑见 [`rules/data-flywheel.md`](rules/data-flywheel.md)。

**写出方向（PRD → Context）——以下事件触发时，AI 必须主动提议，不可跳过**：

| 触发事件 | 必须执行的动作 |
|---------|--------------|
| `/requirement-clarifier` RDD 保存 | 提议追加新术语到 `context/business-glossary.md` |
| `/new-prd` PRD 移入正式区 | 提议更新 `context/product-feature-map.md` 新功能节点 |
| `/update-prd` 变更含新术语/新功能 | 提议同步对应 context 文件 |

**读入方向（Context → PRD）——写到对应章节时，按需读取（文件存在时）**：

| 写到哪个章节 | 必须读取 |
|------------|---------|
| §4 需求对象与概念模型 | `context/business-glossary.md`（避免重复定义已有术语） |
| §5 功能结构 / §7 功能清单 | `context/product-feature-map.md`（获取已有编号前缀） |

**强制规则**：AI 不得自动写入 context 文件——必须输出提议，等待用户确认后才写入。

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
| 命令改了但速查表/测试没同步 | 命令变更必须同步四件套（见命令变更规范） |

---

## 项目演进日志

> 详见 [`docs/HISTORY.md`](docs/HISTORY.md)。
