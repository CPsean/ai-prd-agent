# 项目演进日志

> 记录每次重要功能更新。遇到命令行为疑问时，在此查阅历史变更原因。

---

| 日期 | 事件 |
|------|------|
| （首次使用时填写） | 项目初始化 |
| 2026-04-10 | **串联流水线**：`/requirement-clarifier` 完成后自动保存 RDD 至 `drafts/[标题]/rdd.md` 并引导进入 `/new-prd`；`/new-prd` 新增步骤0（新功能/迭代识别）、步骤5.5（PRD细节两轮澄清，AI自判收敛）、移入正式区后自动判断是否涉及页面变更并引导后续步骤 |
| 2026-04-10 | **新增命令 `/generate-page-spec`**：PRD → 页面规格卡，作为原型生成的前置中间层，保存至 `prds/[标题]/page-spec.md`，写入 `source-prd-version` 和 `last-updated` 元数据 |
| 2026-04-10 | **新增命令 `/sync-docs`**：读取 PRD CHANGELOG 与关联文档元数据，比对版本差异，输出潜在不一致清单 + 建议操作；`/update-prd`、`/generate-prototype` 末尾同步加入轻量提示 |
| 2026-04-10 | **新增模板 `templates/iteration-prd.md`**：迭代类 PRD 精简模板，含 `modifies` 关联字段、变更前→变更后结构、只写变化部分的页面/规则章节；`/new-prd` 步骤0新增迭代类型识别和模板路由 |
| 2026-04-10 | **对话开场引导**：CLAUDE.md 顶部新增路径选择菜单（8条路径），模糊输入或触发词时展示，命令速查表和标准工作流同步更新 |
| 2026-04-15 | **PRD 输出质量升级**：(1) `/requirement-clarifier` 新增 Step 0 按需读取 6 个 context 文件、Step 5 输出 RDD 双节结构（需求摘要 7 维 + 初步方案 6 小节）、Step 6.5 业务术语提议；(2) `templates/feature-prd.md` 重写为 §1-§11 完整结构，含 §7 功能清单（[AREA]-[CAT]-[SEQ] 编号）和 §8 逐功能展开（§8.1-§8.9 条件填写）；(3) 新建 `templates/rdd.md` 作为 RDD 格式基准；(4) 新建 `context/business-glossary.md`（业务术语字典）和 `context/product-feature-map.md`（功能结构树 + 前缀映射表），由需求/PRD 流程联动维护；(5) `/new-prd` 新增 5a 功能编号生成、5b §8 展开指引、Step 7 后 context 同步提示；(6) `/update-prd` 新增 Step 8 context 同步检查；(7) `/ingest-prd` 新增 Step 9 context 同步；(8) `rules/prd-quality-gates.md` 新增 G7（功能清单规范）和 G8（§8 必填完整性） |
| 2026-04-16 | **数据飞轮完善 + 两阶段需求分析重构**：(1) `/requirement-clarifier` 重构为两阶段流程——Phase 1（仅读 user-persona + product-background + platform-support，生成用户故事，阻塞确认）→ Phase 2（对话信号驱动按需加载剩余 context，多轮澄清生成 RDD）；支持传入标题续接中断分析；(2) `templates/rdd.md` 新增 status/phase/context-loaded/story-version frontmatter 字段，rdd.md 改为渐进式写入（story-confirmed → rdd-in-progress → rdd-complete）；(3) `/new-prd` 新增 Step 5-0 rdd.md 状态检查（未完成时给出提示和选项），按 PRD 章节分步加载 context 文件；(4) 修复 `context/platform-support.md` 孤岛——接入 requirement-clarifier Phase 1 和 new-prd §9.4；(5) `/sync-docs` 新增 Step 5 context 一致性检查（术语孤岛 + 功能前缀未注册），飞轮由单向变双向；(6) `rules/prd-quality-gates.md` 新增 G9（平台兼容性，条件触发）；(7) 新增 `evals/integration/TC-workflow-chain.md`（8 个端到端集成测试），补充 TC-RC-09/10/11/12、TC-NP-16/17、TC-SD-07/08/09 |
| 2026-04-16 | **路由规则升级 + CLAUDE.md 瘦身**：(1) 意图匹配从"AI主观判断清晰度"改为"默认走①，4条通用信号+产品专属信号强制路由"；(2) 产品专属 X-Y 信号迁移至 `rules/routing-signals.md`；(3) CLAUDE.md 非运行时内容（PRD规范/目录说明/变更规范/演进日志）迁移至 `docs/` 独立文档，CLAUDE.md 从 ~353 行缩减至 ~190 行 |
