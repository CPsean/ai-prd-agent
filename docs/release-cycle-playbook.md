# 完整发布闭环 Playbook

> 本文件将"研发→测试→回归→记录→git 发布→codex-support 研发→测试→回归→记录→git 发布"固化为 10 阶段可复用模板。比 `feature-dev-playbook.md` 增加了 codex-support 专属研发/测试/发布步骤，适用于需要在所有分支完整落地的功能发布。

---

## 使用方式

1. 打开 `~/.claude/plans/` 目录，创建新计划文件（如 `release-F-0XX.md`）
2. 将本文件内容复制进去，替换所有 `[FEATURE-ID]`、`[FEATURE-TITLE]` 和 `[vX.X]` 占位符
3. 根据功能特点裁剪各阶段（如无 codex-support 适配需求可跳过 Phase 7-10）
4. 每完成一个子任务打 `[x]`

---

## Context

[FEATURE-ID] [FEATURE-TITLE] 的需求已明确，涉及以下文件变更（填写具体列表）：

| 文件 | 操作 | 来源 | 是否入 template |
|------|------|------|----------------|
| `evals/commands/TC-xxx.md` | 新增用例 | [功能] | ✓ |
| `.claude/commands/xxx.md` | 新建/修改 | [功能] | ✓ |
| `CLAUDE.md` | 修改路由/描述 | [功能] | ✓ |
| `context/xxx.md` | 工作区专属变更 | [功能] | ✗ |

---

## Phase 1：TDD — 测试用例先行

> 原则：测试先于实现，验收标准可执行。

- [ ] 编写命令级测试用例：`evals/commands/TC-[PREFIX]-xx.md`
  - 覆盖正向场景、负向/边界场景
  - 沿用现有 TC 格式（参考 `TC-new-prd.md` 结构）
- [ ] 新增集成测试用例（如有跨命令链路）：`evals/integration/TC-workflow-chain.md`
- [ ] 更新 `evals/README.md` 目录和 ID 前缀表

---

## Phase 2：研发实现

> 按测试用例的预期行为逐项实现，优先级由高到低。

- [ ] 修改/新建命令文件 `.claude/commands/xxx.md`
- [ ] 修改模板文件 `templates/xxx.md`（如有；新增 AI 指引须加 `[AI-ONLY]` 标记）
- [ ] 修改规则文件 `rules/xxx.md`（如有）
- [ ] 更新 CLAUDE.md（三件套：菜单/速查表/路由规则/工作流/飞轮触发表）
- [ ] 更新 `docs/prd-standards.md`（如有新目录或 AI 读取规则变更）

---

## Phase 3：本地集成测试 + 回归

- [ ] 执行 Phase 1 所有新增用例（逐条人工运行）
- [ ] 回归受影响的已有用例：

| 修改文件 | 必须回归 |
|---------|----------|
| `CLAUDE.md` | TC-cmd-routing.md（路由相关） |
| `new-prd.md` | TC-new-prd.md（全量） |
| `update-prd.md` | TC-update-prd.md（全量） |
| `requirement-clarifier.md` | TC-requirement-clarifier.md（全量） |
| `prd-quality-gates.md` | TC-prd-migrate.md + QG-fail-cases.md |
| `data-flywheel.md` | TC-workflow-chain.md（飞轮链路） |

---

## Phase 4：版本记录

- [ ] `docs/HISTORY.md`：追加事件行（日期 + 所有变更内容摘要）
- [ ] `README.md`：更新需求澄清 / 命令速查等描述（如有外观变化）

---

## Phase 5：origin/main 提交 + 推送

> 提交工作区所有变更（包含工作区专属文件 context/、backlog/ 等）。

```bash
git add \
  <框架文件列表> \
  <工作区文件列表>
# 如有已删除文件：
# git rm <deleted-file-paths>
git commit -m "feat([FEATURE-ID]): [简短描述]"
git push origin main
```

---

## Phase 6：template 分支同步 + 三端推送

> 只同步框架文件，工作区专属文件（context/、backlog/、drafts/）不入 template。

```bash
git checkout -f template
git checkout product/PM助手 -- \
  <框架文件列表（不含 context/ backlog/ drafts/）>
git status  # 确认无私有文件混入
git add <框架文件列表>
git commit -m "feat([FEATURE-ID]): [简短描述]"
git push origin template
git push upstream template
git push upstream template:main
git checkout -f product/PM助手
```

**推送前检查**：`git diff template..product/PM助手 --name-only` 确认无私有文件泄漏。

---

## Phase 7：codex-support 研发适配

> codex-support 有自己的专属文件（AGENTS.md、README.md codex 版），需单独维护。

### 7.1 覆盖框架文件

```bash
git checkout codex-support
git checkout template -- \
  <Phase 6 同步的框架文件列表>
```

### 7.2 手动更新 AGENTS.md

- [ ] 溯源元数据：更新版本、template commit hash、日期、摘要
- [ ] 意图映射表：同步 CLAUDE.md 中变更的命令描述和路由逻辑
- [ ] 菜单/工作流：与 CLAUDE.md 对应章节保持一致

### 7.3 evals Codex 字段适配

- [ ] 新增的 TC 文件：添加 `Codex 等效输入` 行和 `Codex 状态` 行
- [ ] 被覆盖的已有 TC 文件：检查 Codex 字段是否保留完整

---

## Phase 8：codex-support 测试 + 回归

冒烟测试（至少包含）：
- [ ] TC-RC-01（典型 X-Y 输入，验证基础路由）
- [ ] 本次新增的核心用例（如 TC-[PREFIX]-10）
- [ ] TC-RC-03（极度模糊输入，验证兜底行为）

回归重点：与 Phase 3 回归列表相同，关注 codex 环境下的差异（如无文件系统时的降级行为）。

---

## Phase 9：codex-support 版本记录（AGENTS.md）

- [ ] AGENTS.md 版本历史章节追加本次发布记录（日期 + 摘要）

---

## Phase 10：codex-support 发布

```bash
git add -A -- ':!.claude/settings.local.json'
git commit -m "merge: 同步 template [vX.X] 更新至 codex-support（[FEATURE-ID] [FEATURE-TITLE]）"
git push upstream codex-support
```

---

## 关键文件清单模板

> 复制到具体计划时，填写实际文件列表并标注是否入 template。

| 文件 | 操作 | 来源功能 | 入 template |
|------|------|---------|------------|
| `evals/commands/TC-[xxx].md` | 新建/修改 | [功能] | ✓ |
| `.claude/commands/[xxx].md` | 新建/修改 | [功能] | ✓ |
| `.claude/skills/[xxx]/SKILL.md` | 新建/修改 | [功能] | ✓ |
| `rules/[xxx].md` | 修改 | [功能] | ✓ |
| `CLAUDE.md` | 修改 | [功能] | ✓ |
| `README.md` | 修改 | 记录 | ✓ |
| `docs/HISTORY.md` | 修改 | 记录 | ✓ |
| `context/[xxx].md` | 修改 | 工作区 | ✗ |
| `backlog/requirement-pool.md` | 修改 | 工作区 | ✗ |
| `AGENTS.md`（codex-support 专属） | 修改 | codex 发布 | — |

---

## 验收检查清单

完成所有阶段后逐项确认：

- [ ] Phase 1：所有测试用例已写入 `evals/` 且格式符合规范
- [ ] Phase 2：所有计划文件均已修改，无遗漏
- [ ] Phase 3：新增用例全部通过；回归用例无退化
- [ ] Phase 4：HISTORY.md 事件行已追加；README.md 描述已更新
- [ ] Phase 5：`git push origin main` 成功；提交 message 准确
- [ ] Phase 6：`git push origin template` / `upstream template` / `upstream template:main` 三端均成功；`git status` 确认无私有文件
- [ ] Phase 7：AGENTS.md 溯源元数据和意图映射表已更新；evals Codex 字段已适配
- [ ] Phase 8：codex-support 冒烟测试通过；无回归
- [ ] Phase 9：AGENTS.md 版本历史已追加
- [ ] Phase 10：`git push upstream codex-support` 成功
