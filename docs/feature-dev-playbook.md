# 功能研发流程 Playbook

> 本文件是 F-011 研发计划（`async-wondering-moon.md`）的通用化版本。
> 每次新功能交付时，复制此结构在 `~/.claude/plans/` 下创建具体计划。

---

## 使用方式

1. 打开 `~/.claude/plans/` 目录，创建新计划文件（如 `feature-F-0XX.md`）
2. 将本文件内容复制进去，替换所有 `[FEATURE-ID]` 和 `[FEATURE-TITLE]` 占位符
3. 根据功能特点裁剪/补充各阶段任务
4. 每完成一个子任务打 `[x]`，每推进一个阶段更新"当前进度"

---

## Context

[FEATURE-ID] [FEATURE-TITLE] PRD 已完成并移入正式区（`prds/[FEATURE-ID]-[FEATURE-TITLE]/prd.md`）。现需完成：TDD 编写测试用例 → 研发实现 → 集成测试 → 分支同步推送 → codex 兼容发布。

本项目的"研发"产物通常为以下组合（按功能类型裁剪）：
- 命令文件 `.claude/commands/xxx.md`（新命令或修改已有命令）
- 模板文件 `templates/xxx.md`（模板变更）
- 规则文件 `rules/xxx.md`（质量门禁、飞轮规则等）
- CLAUDE.md 路由/菜单/工作流更新
- `context/` 文件（初始化或补充）

测试用例是 `evals/` 下的人工可执行 prompt 验证用例，不涉及自动化测试。

---

## 阶段一：TDD — 测试用例先行

> 原则：测试先于实现，确保验收标准可执行。

### 1.1 新建或更新命令级测试

基于 PRD §6（用户故事）和 §10（AC 验收清单）编写，沿用现有 TC 格式（参考 `TC-new-prd.md` 结构）。

**文件路径**：`evals/commands/TC-[command-name].md`

| 用例 ID | 覆盖 AC | 测试要点 |
|---------|---------|----------|
| TC-[PREFIX]-01 | AC-1 | [正向场景] |
| TC-[PREFIX]-02 | AC-2 | [正向场景] |
| TC-[PREFIX]-NN | — | [负向/边界场景] |

### 1.2 新建或更新集成测试

**文件路径**：`evals/integration/TC-workflow-chain.md`

在相关场景中追加新用例，覆盖跨命令工作流链路。

| 用例 ID | 场景描述 | 涉及命令 |
|---------|---------|---------|
| TC-INT-NN | [工作流描述] | [命令列表] |

### 1.3 更新 evals/README.md

- 目录结构追加新增 TC 文件
- ID 前缀表追加对应行（如 `TC-[PREFIX]-`）

---

## 阶段二：研发 — 实现功能

> 按 PRD §7 功能清单逐项实现，优先级由高到低。

### 2.1 新建/修改命令文件

**文件**：`.claude/commands/[command-name].md`

核心结构要点：
- 参数解析（`$ARGUMENTS`）
- 前置检查（文件是否存在等）
- 主流程步骤（编号清晰）
- 错误处理和用户反馈
- 上下文按需读取（信号驱动）

### 2.2 修改模板文件（如有）

**文件**：`templates/[template-name].md`

注意：新增 AI 指引内容必须添加 `[AI-ONLY]` 标记（见 `docs/contributing.md`）。

### 2.3 修改规则文件（如有）

**文件**：`rules/[rule-name].md`

常见修改：
- `rules/prd-quality-gates.md`：新增检查组（G-XX）
- `rules/data-flywheel.md`：新增飞轮触发行
- `rules/business-rules.md`：新增全局业务规则

### 2.4 更新 CLAUDE.md（三件套）

对照三件套规范（`docs/contributing.md`），检查以下位置是否需要更新：

- [ ] 对话开场菜单（新路径时）
- [ ] 斜杠命令速查表
- [ ] 意图匹配规则
- [ ] 标准工作流
- [ ] 数据飞轮准则触发表（如有飞轮集成）
- [ ] 上下文按需加载信号词表（如有新信号词）

### 2.5 更新 docs/prd-standards.md（如有）

- 新增目录说明（如新目录）
- 更新 AI 读取规则表

---

## 阶段三：集成测试

依次执行（人工运行，不需要自动化）：

1. 阶段一编写的所有命令级测试用例（TC-[PREFIX]-xx）
2. 集成测试新增用例（TC-INT-xx）
3. 回归验证受影响的已有用例（检查已有行为无退化）

**回归重点**（修改了以下文件时必须回归）：

| 修改文件 | 必须回归的测试 |
|---------|-------------|
| `CLAUDE.md` | TC-cmd-routing.md（路由相关用例） |
| `new-prd.md` | TC-new-prd.md（全量） |
| `update-prd.md` | TC-update-prd.md（全量） |
| `prd-quality-gates.md` | TC-prd-migrate.md + QG-fail-cases.md |
| `data-flywheel.md` | TC-workflow-chain.md（飞轮链路） |

---

## 阶段四：分支同步推送

按 `docs/branch-strategy.md` 第五节标准操作流程执行。

### 4.1 本地提交（product/PM助手 分支）

提交本次所有变更（命令文件、CLAUDE.md、evals、rules、docs、templates 等）。

```bash
git add <具体文件列表>
git commit -m "feat([FEATURE-ID]): [简短描述]"
```

### 4.2 更新版本信息

- `README.md` 更新日志追加版本条目（如 v5.X）
- `docs/HISTORY.md` 追加对应事件行

### 4.3 同步到 template 分支

```bash
git checkout -f template
git checkout product/PM助手 -- \
  <变更的框架文件列表>
# 确认 git status 无意外文件
git add <files> && git commit -m "feat([FEATURE-ID]): [简短描述]"
```

### 4.4 推送三个目标

```bash
git push origin template
git push upstream template
git push upstream template:main
```

### 4.5 同步 origin/main

```bash
git checkout -f main
git checkout template -- README.md docs/HISTORY.md
git add README.md docs/HISTORY.md
git commit -m "docs: 同步 template vX.X 框架文件更新"
git push origin main
```

### 4.6 切回工作分支

```bash
git checkout -f product/PM助手
```

---

## 阶段五：codex-support 分支兼容与发布

按 `docs/codex-sync-playbook.md` 操作手册执行。

### 5.1 切换到 codex-support

```bash
git checkout codex-support
```

### 5.2 直接覆盖框架文件

```bash
git checkout template -- \
  .claude/commands/ \
  CLAUDE.md \
  docs/HISTORY.md \
  docs/contributing.md \
  templates/ \
  rules/ \
  evals/
```

### 5.3 手动更新 codex 专有文件

- **AGENTS.md**：
  - 更新溯源元数据（版本、template commit hash、日期、摘要）
  - 按 CLAUDE.md 变更对应同步意图映射表、菜单、工作流等

- **README.md**（codex-support 版）：
  - 命令速查表同步
  - 更新日志追加版本条目
  - 保留 Codex 专有章节不覆盖

### 5.4 evals Codex 字段适配

- 新增的 TC 文件：添加 `Codex 等效输入` 行和 `Codex 状态` 行
- 被覆盖的已有 TC 文件：检查 Codex 字段是否保留

### 5.5 提交推送

```bash
git add -A -- ':!.claude/settings.local.json'
git commit -m "merge: 同步 template vX.X 更新至 codex-support（[FEATURE-ID] [FEATURE-TITLE]）"
git push upstream codex-support
```

### 5.6 冒烟测试

按 `docs/codex-sync-playbook.md` 底部冒烟测试清单 + 追加本功能验证用例。

---

## 关键文件清单模板

> 复制到具体计划时，填写实际文件列表。

| 文件 | 操作 | 阶段 |
|------|------|------|
| `.claude/commands/[xxx].md` | 新建/修改 | 研发 |
| `templates/[xxx].md` | 修改 | 研发 |
| `rules/[xxx].md` | 修改 | 研发 |
| `CLAUDE.md` | 修改 | 研发 |
| `evals/commands/TC-[xxx].md` | 新建/修改 | TDD |
| `evals/integration/TC-workflow-chain.md` | 修改 | TDD |
| `evals/README.md` | 修改 | TDD |
| `README.md` | 修改 | 发布 |
| `docs/HISTORY.md` | 修改 | 发布 |
| `AGENTS.md`（codex-support） | 修改 | codex 发布 |

---

## 验证方式

1. **TDD 验证**：研发完成后逐条执行命令级测试用例
2. **集成验证**：执行新增集成测试用例 + 关键回归用例
3. **推送前验证**：`git diff template..product/PM助手 --name-only` 确认无私有文件泄漏
4. **codex 验证**：推送后执行冒烟测试清单
