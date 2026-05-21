# 命令：/export-openapi [api-name] [version?]

两阶段过滤 + 敏感内容扫描，生成对外精简版 OpenAPI 文档。

$ARGUMENTS

## 参数说明

- `[api-name]`：API 规范文件名（不含 .yaml 扩展名），如 `order-api`
- `[version]`（可选）：版本号，如 `1.1.0`。提供时同时生成版本快照文件；省略时仅覆盖 latest 文件

---

## 执行步骤

### Step 1：前置检查

1. 检查 `openapi/[api-name].yaml` 是否存在：
   - **不存在** → 停止，输出："未找到 `openapi/[api-name].yaml`，请先运行 `/import-openapi [api-name]`。"

2. 读取 `openapi/_hidden-interfaces.md`：
   - 文件存在 → 解析接口级隐藏表和参数级隐藏表
   - 文件不存在 → 视为两张空表，继续执行

### Step 2：第一阶段过滤——接口级

读取内部完整版 `openapi/[api-name].yaml`，移除"接口级隐藏"表中列出的所有 endpoint：

- 按 `endpoint 路径 + HTTP 方法` 精确匹配
- 保留所有未列入接口级隐藏表的 endpoint

记录：接口级过滤 N 条，剩余 M 条。

### Step 2b：Webhook 级过滤

读取 `openapi/_hidden-interfaces.md` 中「Webhook 级隐藏」表（如有）：

- 按事件名称精确匹配，从 yaml `x-webhooks.events` 中移除对应事件
- 记录：Webhook 级过滤 W 条

若无「Webhook 级隐藏」表或表为空，静默跳过。

### Step 3：第二阶段过滤——参数级

在**第一阶段保留的 endpoint** 中，逐条检查"参数级隐藏"表：

- 按 `endpoint 路径 + HTTP 方法 + 字段位置 + 字段名` 精确匹配
- 从对应位置（requestBody / response / query params / path params）移除匹配字段
- 不影响未列入参数级隐藏表的字段

记录：参数级过滤 P 处。

### Step 4：敏感内容扫描

对**第二阶段过滤后保留的内容**（含保留的 x-webhooks 和 x-error-codes）执行敏感词扫描，检查所有 `description`、`example`、`x-*` 扩展字段：

**敏感词模式**（命中任一触发警告）：
- 内网地址：`10.x.x.x`、`192.168.x.x`、`172.16-31.x.x`、`localhost`、内网域名（含 `.internal`、`.corp`、`.intranet`）
- 内部系统名：包含"OMS"、"ERP"、"内部系统"、"后台管理"、"内网"等模式
- 密钥/令牌样例：包含 `Bearer `、`sk-`、`token`、`secret` 且后跟非占位符内容（如实际字符串值）

**无命中**：继续至 Step 5。

**有命中**：记录所有命中字段路径（如 `GET /v1/orders → description`），在摘要中展示（见 Step 5）。

### Step 4b：规范质检（OAPI-QC-003）

对**第二阶段过滤后保留的全量内容**执行阻断模式规范质检（5 个维度）。

读取 `rules/openapi-conventions.md`：
- **rules 文件不存在** → 跳过规范质检，Step 5 摘要中追加"规范质检：未启用（`rules/openapi-conventions.md` 不存在）"，继续导出流程
- **过滤后无保留内容** → 跳过规范质检，继续原流程

**无违规时**（结果追加到 Step 5 摘要末尾，继续流程）：
```
✅ 规范质检：5 个维度无违规项
```

**有违规时**（结果追加到 Step 5 摘要末尾，**阻断导出**）：
```
❌ 规范质检：发现 N 处违规，导出已阻断

| 维度 | endpoint / 字段 | 违规规则 | 具体问题 | 期望值 |
|------|----------------|---------|---------|--------|
| OAC-PATH | GET /openapi/v1/cancelOrder | OAC-PATH-004 | 动作应用 POST+子路径 | POST /openapi/v1/orders/{id}/cancel |

请修正以上问题后，重新运行 /export-openapi。
```

有违规时：不进入 Step 5 的 PM 确认交互，不生成任何输出文件，直接终止命令。

### Step 5：展示过滤摘要 + 确认断点

强制输出摘要，**不可跳过**：

```
过滤摘要：
- 接口级过滤：N 条（已移除：[路径1], [路径2], ...）
- Webhook 级过滤：W 条（已移除：[事件1], [事件2], ...）
- 参数级过滤：P 处（已移除：[路径+字段1], [路径+字段2], ...）
- 保留 endpoint：M 条
- 保留 Webhook 事件：X 个

[若有敏感内容命中，追加：]
⚠️ 敏感内容扫描：命中 Q 处
  - GET /v1/orders → description："...含内部系统名 OMS..."
  - ...
  建议在导出前修改或移除上述字段内容。
```

**无敏感内容命中时**：询问 PM：
> "以上为过滤结果，确认导出请回复「确认」。"

**有敏感内容命中时**：必须要求 PM 明确确认：
> "检测到敏感内容，请确认已检查所有命中字段，回复「**已检查，可以导出**」后继续。"
>
> - 仅回复"确认"（不含"已检查"字样）→ **不通过**，重新提示须明确确认
> - 回复"已检查，可以导出"或同义明确表述 → 通过
> - PM 选择不导出 → 停止，不写入任何文件

### Step 5b：版本号合法性校验（有版本参数时）

1. **格式校验**：版本号须符合语义化版本格式（`X.Y.Z`，X/Y/Z 为非负整数）
   - 不合法（如 `v1`、`1.0`、`abc`）→ 阻断，提示 PM 修正格式
2. **破坏性变更检测**：对比本次 yaml 与上次导出版本（`outputs/openapi/[api-name]-public.yaml`）的 diff：
   - 破坏性变更定义：删除 endpoint / 删除必填参数 / 修改响应结构（字段类型变更或移除）
   - 若含破坏性变更但版本号主版本（X）未升 → 阻断并提示：
     > ⚠️ 检测到破坏性变更（[具体变更]），但版本号仅从 [旧版本] 升至 [新版本]（主版本未变）。
     > 建议将版本号调整为 [建议版本]。回复新版本号继续，或回复「强制导出」跳过校验。
   - 无上次导出版本（首次导出）→ 跳过破坏性变更检测

### Step 5c：MD 文档联动询问

版本号校验通过后（或无版本参数时），追加询问：

> 是否同时生成对外 MD 文档？回复「是」同时生成，回复「否」仅导出 yaml。

选「否」→ 直接进入 Step 6 写入 yaml。

选「是」→ 执行 MD 生成：
1. 检查 `templates/openapi-md-template.md` 是否存在：
   - **不存在** → 提示 PM 创建模板，阻断 MD 生成，仅完成 yaml 导出
   - **存在** → 继续
2. 读取模板，基于过滤后 endpoint 集合 + 保留的 x-webhooks + x-error-codes 生成 MD：
   - 描述/字段名/示例严格从 yaml 读取，不自由发挥（BR-04）
   - yaml 有 example → 直接输出到 MD
   - yaml 无 example → MD 对应处留空，文档末尾汇总"待补齐示例清单"
3. 写入 `outputs/openapi/[api-name]-public.md`（覆盖）

### Step 6：写入文件

PM 确认后：

**无版本参数时（覆盖 latest）**：
- 写入 `outputs/openapi/[api-name]-public.yaml`（覆盖）

**有版本参数时（快照 + 更新 latest）**：
1. 检查 `outputs/openapi/[api-name]-public-v[version].yaml` 是否已存在：
   - **已存在** → 提示："版本快照 `[api-name]-public-v[version].yaml` 已存在，确认覆盖请回复「确认覆盖」，否则回复版本号进行调整。"
   - **不存在** → 直接写入
2. 写入 `outputs/openapi/[api-name]-public-v[version].yaml`（版本快照）
3. 同步覆盖 `outputs/openapi/[api-name]-public.yaml`（latest 文件）

**完成后输出**：已生成对外版文件（列出写入路径）。内部版 `openapi/[api-name].yaml` 未被修改。
