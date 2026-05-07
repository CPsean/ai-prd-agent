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

### Step 3：第二阶段过滤——参数级

在**第一阶段保留的 endpoint** 中，逐条检查"参数级隐藏"表：

- 按 `endpoint 路径 + HTTP 方法 + 字段位置 + 字段名` 精确匹配
- 从对应位置（requestBody / response / query params / path params）移除匹配字段
- 不影响未列入参数级隐藏表的字段

记录：参数级过滤 P 处。

### Step 4：敏感内容扫描

对**第二阶段过滤后保留的内容**执行敏感词扫描，检查所有 `description`、`example`、`x-*` 扩展字段：

**敏感词模式**（命中任一触发警告）：
- 内网地址：`10.x.x.x`、`192.168.x.x`、`172.16-31.x.x`、`localhost`、内网域名（含 `.internal`、`.corp`、`.intranet`）
- 内部系统名：包含"OMS"、"ERP"、"内部系统"、"后台管理"、"内网"等模式
- 密钥/令牌样例：包含 `Bearer `、`sk-`、`token`、`secret` 且后跟非占位符内容（如实际字符串值）

**无命中**：继续至 Step 5。

**有命中**：记录所有命中字段路径（如 `GET /v1/orders → description`），在摘要中展示（见 Step 5）。

### Step 5：展示过滤摘要 + 确认断点

强制输出摘要，**不可跳过**：

```
过滤摘要：
- 接口级过滤：N 条（已移除：[路径1], [路径2], ...）
- 参数级过滤：P 处（已移除：[路径+字段1], [路径+字段2], ...）
- 保留 endpoint：M 条

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
