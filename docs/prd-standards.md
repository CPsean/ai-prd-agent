# PRD 规范参考手册

> 本文件在以下时机读取：执行 `/new-prd`、`/update-prd`、`/prd-summary`、`/generate-page-spec` 时。
> CLAUDE.md 中已有读取指引，无需手动加载。

---

## PRD 结构规范

### 三层文档体系

| 层级 | 类型 | ID 前缀 | 适用场景 | 模板 |
|------|------|---------|----------|------|
| Layer 1 | 用户故事卡（Story Card） | SC- | 单场景小需求、子故事 | `templates/story-card.md` |
| Layer 2 | 功能 PRD（Feature PRD） | F- | 一个完整功能模块 | `templates/feature-prd.md` |
| Layer 3 | 史诗 PRD（Epic PRD） | E- | 大型项目，含多个功能 | `templates/epic-prd.md` |

**用户故事在每层都是必须项。**

**Feature PRD 章节结构（§1-§12）**：

| 章节 | 标题 | 说明 |
|------|------|------|
| §1 | 文档元数据 | 含关联 RDD/规格卡/原型字段 |
| §2 | 文档修订记录 | |
| §3 | 需求概要 | 3.1 问题与机会 / 3.2 目标用户 / 3.3 方案概述 / 3.4 成功指标 |
| §4 | 需求对象与概念模型 | 只写本 PRD **新引入**术语，已有术语引用 `context/business-glossary.md` |
| §5 | 功能结构 | 5.1 新增/调整节点 / 5.2 核心业务流程 / 5.3 核心业务规则（BR-XX，跨功能全局约束） |
| §6 | 用户故事与用例 | Epic + Must Have，含 Gherkin AC（故事级） |
| §7 | 功能清单 | 编号格式 `[AREA]-[CAT]-[SEQ]`，先查前缀映射表；名称全限定；动词具体 |
| §8 | 功能需求说明书 | 逐功能展开；§8.x.1-§8.x.3 必填；§8.x.4-§8.x.9 按条件填（不适用填「不涉及」） |
| §9 | 非功能性需求 | 性能 / 安全 / 可用性 / 兼容性 / 数据统计 |
| §10 | 验收检查清单 | 从 §6 Gherkin AC 汇总的 checkbox 索引视图，AI 全章节写完后统一回填 |
| §11 | 范围外（Out of Scope） | |
| §12 | 开放问题 | approved 前须清空 |

---

## PRD 目录结构

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

- `prd.md` 永远是当前有效版本
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
