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

---

## 斜杠命令速查

### PRD 生命周期命令

| 命令 | 用途 | 典型场景 |
|------|------|----------|
| `/new-prd [story-card\|feature\|epic] [标题]` | 新建 PRD，自动创建文件夹、文件和注册 | 有新需求时第一步 |
| `/ingest-prd` | 录入历史PRD，自动重建结构、更新注册表和需求清单，输出缺口问题 | 历史需求归档 |
| `/update-prd [变更描述]` | 更新 PRD + 自动归档旧版本 + 写 changelog | 评审后需求变更 |
| `/generate-prototype` | 从 PRD 生成 HTML 可交互原型 | 需要对齐界面结构时 |
| `/prd-qa [问题]` | 基于 PRD 回答具体问题（产品/研发/测试均可问） | 开发过程中的疑问 |
| `/prd-summary` | 输出 PRD 的对齐摘要 | 评审前、开发启动前 |

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

```
prds/
  _registry.md                ← AI 首先读这里，找到对应 PRD 路径
  [需求中文标题]/
    prd.md                    ← 当前有效版本（AI 主要消费此文件）
    CHANGELOG.md              ← 变更记录（不作为主要参考）
    fields.md                 ← 字段清单（Feature/Epic 级别）
    prototype/
      index.html              ← 可交互 HTML 原型（按需生成）
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
| `drafts/` | AI 协作草稿区（过程产物） |
| `outputs/` | 最终对外交付物 |
| `prds/` | 正式 PRD（唯一权威来源） |
| `prompts/` | 有效提示词沉淀 |
| `templates/` | 文档模板库 |

---

## 工作规范

### 标准工作流

```
新需求
  → /requirement-clarifier    （澄清真实问题，生成 RDD）
  → /new-prd [type] [标题]    （创建 PRD 文件结构）
  → 填写 prd.md               （按模板撰写内容）
  → /prd-summary              （对齐评审）
  → 评审发现问题
  → /update-prd [变更描述]    （更新 + 自动存档）
  → /generate-prototype       （按需生成原型）
  → 状态改为 approved → released
```

### 字段清单标准

每个字段必须包含：字段名 / 标识符 / 类型 / 长度 / 必填 / 默认值 / 说明 / 业务规则

### 原型生成原则

- 简单需求（单页面/纯逻辑）：文字说明即可，不强制生成原型
- 复杂需求（多页面/需对齐界面）：运行 `/generate-prototype`
- 原型页面与 PRD "页面 & 交互说明"章节一一对应

---

## 最佳实践

1. 模糊需求先过 `/requirement-clarifier`，再建 PRD
2. PRD 只有一个权威文件（`prd.md`），不要在外部复制维护
3. 研发/测试有疑问时直接用 `/prd-qa` 问 AI，而非口头询问
4. 每次需求变更用 `/update-prd`，不要直接编辑 `prd.md` 而不留记录

---

## 经验教训

| 问题 | 解决方案 |
|------|----------|
| 需求理解偏差 | 先用 `/requirement-clarifier` 暴露 X-Y 问题 |
| 版本混乱 | 所有变更通过 `/update-prd`，禁止直接覆盖 |
| 研发对需求有疑问 | 用 `/prd-qa` 基于 PRD 回答，发现缺陷及时补充 |
| 输出不一致 | 使用标准化斜杠命令，不自由发挥提示词 |

---

## 项目演进日志

| 日期 | 事件 |
|------|------|
| （首次使用时填写） | 项目初始化 |
