# AI PRD 工作空间

> 为产品经理打造的高效 AI IDE 工作空间，基于 Claude Code，支持 PRD 撰写、需求分析、原型生成和业务分析等日常工作。

---

## 前提条件

本工作空间基于 **Claude Code** 运行，使用前请先安装：

```bash
npm install -g @anthropic-ai/claude-code
```

安装完成后，在本项目根目录打开终端，运行 `claude` 即可启动。

---

## 项目结构

```
AI PRD/
├── .claude/                   # Claude Code 配置中心（核心）
│   ├── commands/              # 斜杠命令（/new-prd、/prd-qa 等）
│   └── skills/                # AI 技能包（jobs-to-be-done、user-story 等）
├── analysis/                  # 业务分析产物
├── assets/                    # 图片、原型图、流程图等资源
├── context/                   # 项目上下文（用户画像、产品策略）
├── docs/                      # 参考文档库
├── drafts/                    # AI 协作草稿区（过程产物）
├── outputs/                   # 最终对外交付物
├── prds/                      # 正式 PRD（唯一权威来源）
│   └── _registry.md           # PRD 索引（AI 首先读这里）
├── templates/                 # 文档模板库
├── CLAUDE.md                  # 全局知识库（AI 自动加载）
└── README.md                  # 本文件
```

---

## 快速开始

### 第一步：了解两个核心文件

- **`CLAUDE.md`**：全局知识库，AI 每次对话自动加载，记录了所有规范和命令说明
- **`prds/_registry.md`**：PRD 索引，记录了所有正式需求的路径和状态

### 第二步：从一个新需求开始

```
1. 启动 Claude Code，在对话中输入：

   /requirement-clarifier 我想做一个用户登录功能

2. AI 会帮你澄清需求，确认后再创建 PRD：

   /new-prd feature 用户登录

3. 填写生成的 prd.md 文件内容

4. 需要对齐时输出摘要：

   /prd-summary

5. 需求变更时更新（自动存档旧版本）：

   /update-prd 增加了手机号登录方式
```

---

## 斜杠命令速查

### PRD 生命周期

| 命令 | 用途 |
|------|------|
| `/new-prd [story-card\|feature\|epic] [标题]` | 新建 PRD，自动创建文件夹和注册 |
| `/update-prd [变更描述]` | 更新 PRD，自动归档旧版本并写 changelog |
| `/prd-summary` | 输出 PRD 对齐摘要，适合评审前使用 |
| `/prd-qa [问题]` | 基于 PRD 回答问题（产品/研发/测试均可用） |
| `/generate-prototype` | 从 PRD 生成可交互 HTML 原型 |

### 需求分析

| 命令 | 用途 |
|------|------|
| `/requirement-clarifier [需求描述]` | 识别真实问题，生成需求诊断卡片 |
| `/analyze-requirement [需求描述]` | 深度需求分析，输出分析报告 |
| `/design-solution` | 基于分析报告输出方案设计文档 |
| `/write-user-story [需求描述]` | 生成 Gherkin 格式用户故事 |
| `/design-data-model [业务场景]` | 生成企业级数据库 Schema |

---

## PRD 三层体系

根据需求规模选择对应类型：

| 类型 | 命令参数 | 适用场景 | 模板 |
|------|---------|----------|------|
| 用户故事卡 | `story-card` | 单场景小需求 | `templates/story-card.md` |
| 功能 PRD | `feature` | 一个完整功能模块 | `templates/feature-prd.md` |
| 史诗 PRD | `epic` | 大型项目，含多个功能 | `templates/epic-prd.md` |

---

## 标准工作流

```
新需求
  → /requirement-clarifier    # 澄清真实问题
  → /new-prd [type] [标题]    # 创建 PRD 文件结构
  → 填写 prd.md               # 按模板撰写内容
  → /prd-summary              # 对齐评审
  → /update-prd [变更描述]    # 评审后更新（自动存档）
  → /generate-prototype       # 按需生成原型
```

---

## 文件夹说明

| 文件夹 | 用途 |
|--------|------|
| `.claude/commands/` | 斜杠命令定义，Claude Code 自动识别 |
| `.claude/skills/` | 技能规格文档，供命令引用 |
| `prds/` | 正式 PRD，每个需求一个子文件夹，`prd.md` 是唯一有效版本 |
| `drafts/` | 草稿区，AI 生成的初稿和试错过程 |
| `outputs/` | 最终对外交付物（PRD、演示材料、交接文档） |
| `analysis/` | 业务分析产物（需求分析报告、流程推演等） |
| `context/` | 项目上下文（用户画像、产品策略、背景） |
| `templates/` | 文档模板，新建 PRD 时自动使用 |
| `assets/` | 图片、原型图、流程图等资源文件 |
| `prompts/` | 有效提示词沉淀 |

---

## 更新日志

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-02-27 | v1.0 | ��目初始化 |
| 2026-03-28 | v2.0 | 迁移至 Claude Code，重构为斜杠命令体系，更新 README |
