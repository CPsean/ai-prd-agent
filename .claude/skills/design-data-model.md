---
name: design-data-model
description: 应用领域驱动设计（DDD）原则生成企业级数据库Schema，识别聚合根，强制类型安全和软删除等标准规范
tags: [architecture, database, ddd, schema]
---

## 触发条件（When）
- 用户请求"数据库设计"、"表结构"、"ER图"、"数据建模"
- 上下文涉及定义持久化存储结构
- 架构设计阶段明确提到数据模型

## 不适用场景（Do NOT use）
- 仅涉及内存数据结构或JSON Mock
- 用户只需要SQL查询优化（使用 `optimize-sql` 替代）

## 输入
- `business_context`：业务需求描述
- `tech_stack`（可选）：目标数据库，默认MySQL

## 企业级Schema标准规范

| 规范项 | 要求 |
|--------|------|
| 主键 | 雪花ID（BigInt） |
| 审计字段 | `created_at` / `updated_at` / `created_by` / `updated_by` |
| 软删除 | `is_deleted` |
| 乐观锁 | `version` |
| 金额类型 | 必须 `DECIMAL(p,s)`，禁止 `FLOAT`/`DOUBLE` |
| 字符串 | 优先 `VARCHAR(N)` 具体长度，非必要不用 `TEXT` |

## 输出结构

1. **ER图**（Mermaid语法代码块）
2. **Schema表格**（表名 / 字段 / 类型 / 约束）
3. **设计说明**（聚合根选择理由 / 索引策略）

## 失败策略

业务背景过于模糊时，停止并追问：
> "请提供具体的业务实体或核心字段，以便继续建模。"

## 对应斜杠命令

调用方式：`/design-data-model [业务场景描述]`

命令文件：`.claude/commands/design-data-model.md`
