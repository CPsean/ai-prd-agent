# codex-support 同步操作手册

> 供维护者在 template 分支有重要更新后，将变更同步到 codex-support 分支时重复使用。

---

## 适用场景

以下情况需执行本手册：

- template 分支有新命令、命令逻辑重大变更、或新章节上线
- codex-support 落后 template **3 个以上提交**，或跨越主要版本（如 v5.x → v6.x）
- 快速判断方法：`git log template --oneline -1` 获取 template 最新提交，与 AGENTS.md 顶部溯源块的 `基于 template 提交` 对比，哈希不同即需同步

---

## 前置检查清单

在切换到 codex-support 分支之前，先确认：

- [ ] 当前分支（product/PM助手）无未提交修改，或已 `git stash`
- [ ] `git fetch upstream` 已拉取 template 最新状态
- [ ] 执行 `git log template --oneline -5` 确认 template 的更新范围
- [ ] 确认本次同步要覆盖的版本区间（如 v5.1 → v5.3）

---

## 同步文件分类规则

| 分类 | 操作 | 文件示例 |
|------|------|---------|
| **直接覆盖** | `git checkout template -- <file>` | `.claude/commands/*.md`、`CLAUDE.md`、`docs/HISTORY.md`、`docs/contributing.md`、`templates/`、`rules/` |
| **手动合并** | 不覆盖，手动 diff 并编辑 | `AGENTS.md`、`README.md` |
| **evals 特殊处理** | 先覆盖，再回补 Codex 字段 | `evals/commands/TC-*.md`、`evals/integration/TC-workflow-chain.md`、`evals/README.md` |
| **codex 独有** | 永不从 template 覆盖 | `AGENTS.md`（Codex 专用入口） |
| **私有，永不同步** | 忽略 | `.claude/settings.local.json` |

**需要删除的文件**：若 template 废弃了某个文件，在 codex-support 也执行 `git rm`（如 `templates/iteration-prd.md`）。

---

## 标准操作步骤

```bash
# 1. 切换到 codex-support
git checkout codex-support

# 2. 直接覆盖框架文件（按需调整文件列表）
git checkout template -- \
  .claude/commands/ \
  CLAUDE.md \
  docs/HISTORY.md \
  docs/contributing.md \
  templates/ \
  rules/

# 3. 同步 evals（先覆盖获取最新内容）
git checkout template -- evals/

# 4. 回补 Codex 字段（见 evals 适配检查清单）

# 5. 手动更新 AGENTS.md（见 AGENTS.md 更新检查清单）

# 6. 手动合并 README.md（见 README 合并要点）

# 7. 提交并推送
git add -A -- ':!.claude/settings.local.json'
git commit -m "merge: 同步 template vX.X~vX.X 更新至 codex-support（简述）"
git push upstream codex-support
```

---

## AGENTS.md 更新检查清单

> 每次同步时逐条核对。**第一项必须最先更新**。

- [ ] **更新版本溯源元数据块**（文件顶部）：
  - `基于 template 版本`：填写本次同步到的版本号（如 v5.3）
  - `基于 template 提交`：填写 `git log template --oneline -1` 的 commit hash（前 7 位）
  - `同步日期`：填写今天日期（YYYY-MM-DD）
  - `同步内容摘要`：一句话描述本次同步内容
- [ ] 意图→命令文件映射表：新增命令需补映射行
- [ ] 对话开场菜单：新增路径需补编号
- [ ] PRD 目录结构：路径格式是否有变化
- [ ] 产品上下文文件列表：新增 context 文件需补说明
- [ ] 标准工作流：是否有新的流程节点
- [ ] 数据飞轮准则：触发事件/强制规则是否有变化
- [ ] 上下文按需加载：信号词表是否有新增
- [ ] 经验教训表：是否有新的经验需补充
- [ ] 命令变更三件套：三件套文件引用是否仍准确

---

## evals Codex 适配检查清单

**新增 TC 文件**（template 有 codex-support 无）：

- [ ] 文件头部添加 `> Codex 等效输入：「自然语言描述」` 行（在最后一个 `>` 行后）
- [ ] 状态表中添加 `| **Codex 状态** | — |` 行（在 `| **状态** |` 行后）
- [ ] `evals/README.md` 补对应 TC 前缀说明

**已有 TC 文件**（从 template 覆盖后）：

- [ ] 批量添加 Codex 状态行：`sed -i 's/| \*\*状态\*\* |/| **状态** |\n| **Codex 状态** | — |/g' evals/commands/*.md`（注意 Windows 下 sed -i 语法差异，可用 PowerShell 替代）
- [ ] 逐文件检查 `Codex 等效输入` 是否已有；若被覆盖丢失，重新添加

**evals/README.md**：

- [ ] 确认包含"OpenAI Codex"执行方式章节
- [ ] 确认新增 TC 文件的 ID 前缀已补入规范表

---

## README.md 合并要点

codex-support 的 README 是双平台版本（Codex 优先展示），不可直接覆盖：

- [ ] PRD 生命周期命令表：补入新命令行（如 abandon-prd、import-context）
- [ ] PRD 体系：确认层级数量与 template 一致（当前为三层，无 iteration-prd.md）
- [ ] 更新日志：补入新版本条目（v5.x 等）
- [ ] 保留 Codex 专有章节：`## 运行平台`、`## 快速开始（Codex）`、Codex 等效输入列

---

## 提交推送目标

| 仓库 | 分支 | 命令 |
|------|------|------|
| upstream（公开框架仓库） | codex-support | `git push upstream codex-support` |

> 不推送到 origin（私有仓库），codex-support 是纯公开框架分支。

---

## Codex 冒烟测试清单（推送后执行）

在 Codex 环境中执行以下 5 项，全部通过（✅ 或 ⚠️）后视为同步完成：

| # | Codex 输入 | 验证要点 |
|---|-----------|----------|
| 1 | `帮助` 或 `从哪里开始` | 展示开场菜单，含 ⑨⑩ 路径 |
| 2 | `放弃草稿：测试功能` | AI 正确读取 abandon-prd.md 执行 |
| 3 | `导入上下文：我们的产品叫XX` | AI 正确读取 import-context.md 执行 |
| 4 | `新建功能PRD：测试功能` | 草稿创建在 `drafts/[ID]-[标题]/`（含 ID 前缀） |
| 5 | 执行中说「不对，不是这个」 | AI 终止当前命令，重新路由 |

---

## 完整 TC 执行优先级

| 优先级 | TC 文件 | 说明 |
|--------|---------|------|
| P0 新增命令 | TC-abandon-prd、TC-context-manage | 本次新增，优先验证 |
| P1 核心升级 | TC-new-prd、TC-requirement-clarifier、TC-cmd-routing | 影响主流程 |
| P2 功能增强 | TC-prd-qa、TC-sync-docs、TC-update-prd、TC-skill-manage | 功能升级验证 |
| P3 补充验证 | TC-prd-migrate、TC-generate-page-spec、TC-generate-prototype 及其余 | 完整覆盖 |

执行方式：使用每个 TC 文件头部 `Codex 等效输入` 行中的自然语言触发，结果记录到 `Codex 状态` 行。

---

## 验证通过标准

同步完成后，确认以下均满足：

1. **版本溯源**：AGENTS.md 顶部溯源块 commit hash 与 `git log template --oneline -1` 一致
2. **文件完整性**：`git diff template..codex-support --name-only` 差异仅剩 codex-support 独有文件
3. **命令对齐**：`.claude/commands/` 文件列表两分支完全一致
4. **evals Codex 字段**：抽查 3 个 TC 文件，确认均含 `Codex 等效输入` 和 `Codex 状态` 字段
5. **README 版本日志**：确认包含本次同步覆盖的所有版本条目
6. **冒烟测试**：Step 5 的 5 项全部通过
