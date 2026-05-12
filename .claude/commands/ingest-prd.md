执行 `.claude/skills/ingest-prd/SKILL.md` 中定义的历史PRD录入流程。

用户已提供原始PRD内容（需求ID可选）。按 skill 定义的流程完整执行：

**前置阶段**（ingest 独有）：
- Step 0：读取上下文文��（_registry.md 必读，失败则停止）
- Step 0.5：需求ID确认（不创建任何文件）
- Step 1：确定 PRD 层级
- Step 2：提取历史内容，构建章节填充映射表
- Step 2.5：输出前置阶段摘要

**后置阶段**（完全复用 /new-prd）：
- 从 `/new-prd` Step 3 开始完整执行至结束
- 适配项：author/created 字段来源、跳过 rdd.md 检查、CHANGELOG 注明历史录入来源
- 移入正式区后额外更新 `context/iteration-requirement-list.md` 关联PRD列

关键约束：
- Step 0 必须先读文件，不得依赖记忆中的数据
- 内容缺失时写占位符，不杜撰业务逻辑
- 质检门控（❌ 项）阻断移入正式区
- 数据飞轮（feature-map、glossary、需求池、页面导航）在移入正式区后完整触发
