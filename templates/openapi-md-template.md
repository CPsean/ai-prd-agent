# 对外 API 文档模板（MD 格式）

> **使用说明**：
> - 本模板由 `/export-openapi` 联动生成对外 MD 文档时使用
> - 所有 `{{...}}` 占位符由 AI 从 `openapi/[api-name].yaml` 对应位置读取填充
> - yaml 中无对应内容时，该区块整体不输出（不输出空表格或空代码块）
> - 示例严格从 yaml example 字段读取，缺失时留空并汇总到「待补齐示例」章节
> - AI 不得改写、扩写 yaml 中的描述文字（BR-04 yaml 单一权威源原则）
>
> **数据来源映射**：
> - REST endpoints → yaml `paths`
> - 分组 → yaml `tags`（tag 顺序即章节顺序）
> - Webhook → yaml `x-webhooks` 扩展（OpenAPI 3.0.x）或 `webhooks` key（OpenAPI 3.1）
> - 错误码 → yaml `x-error-codes` 扩展
> - 公共 schema → yaml `components/schemas`（嵌套对象引用）

---

# {{API_NAME}} REST API 文档

> {{从 yaml info.description 读取}}

---

## 概述

| 项目 | 内容 |
|------|------|
| Base URL | {{yaml servers[0].url}} |
| 协议 | HTTPS |
| 认证方式 | {{yaml components.securitySchemes 摘要}} |
| 请求格式 | JSON（Content-Type: application/json），特殊格式在接口处标注 |
| 响应格式 | JSON |
| 版本 | {{yaml info.version，无则不输出此行}} |

---

## 认证

{{从 yaml paths 中 tag 为 "认证"/"OAuth"/"Auth" 的 endpoint 生成，结构同下方 endpoint 模板}}

---

## {{Tag 名称}}

> {{yaml tags[].description，无则不输出此行}}

<!-- 按 tag 内 endpoint 顺序逐个生成 -->

### {{operationId 或 summary}}

> `{{METHOD}} {{path}}`

#### 接口描述

{{yaml paths.[path].[method].description}}

#### 请求参数

| 参数名称 | 类型 | 必填 | 说明 |
|----------|------|------|------|
| {{name}} | {{schema.type}} | {{required: true/false}} | {{description}} |
| └ {{nested_name}} | {{type}} | {{required}} | {{description，嵌套用 └ 前缀}} |

> 嵌套层级规则：一级无前缀，二级 └，三级 　└（全角空格+└）

#### 请求示例

```json
{{yaml requestBody.content.[mediaType].example}}
```

#### 响应参数

| 参数名称 | 类型 | 说明 |
|----------|------|------|
| {{name}} | {{type}} | {{description}} |
| └ {{nested_name}} | {{type}} | {{description}} |

#### 响应示例

```json
{{yaml responses.200.content.[mediaType].example}}
```

---

<!-- 所有 tag 分组的 endpoint 生成完毕后，输出 Webhook 和错误码章节 -->

## Webhook 回调事件

### 概述

{{yaml x-webhooks.description 或 info.x-webhook-overview}}

| 项目 | 内容 |
|------|------|
| 请求协议 | HTTPS（HTTP POST） |
| 成功条件 | {{yaml x-webhooks.x-success-condition，无则不输出}} |
| 超时设置 | {{yaml x-webhooks.x-timeout，无则不输出}} |
| 重试机制 | {{yaml x-webhooks.x-retry-policy，无则不输出}} |

### 支持的事件类型

| 事件类型 | 说明 |
|----------|------|
| {{event_name}} | {{yaml x-webhooks.events.[event].description}} |

---

### {{事件名称}}（逐事件生成）

{{yaml x-webhooks.events.[event].description — 触发条件说明}}

#### 回调参数

| 参数名称 | 类型 | 说明 |
|----------|------|------|
| {{name}} | {{type}} | {{description}} |
| └ {{nested}} | {{type}} | {{description}} |

#### 回调示例

```json
{{yaml x-webhooks.events.[event].example}}
```

---

## 错误码

| 错误码 | 错误信息 | 错误原因 |
|--------|----------|----------|
| {{code}} | {{message}} | {{reason，无则填 —}} |

> 数据来源：yaml `x-error-codes` 扩展

---

## 待补齐示例

> 以下位置在 yaml 中未定义 example，建议在 `openapi/{{api-name}}.yaml` 中补全后重新生成。

| 类型 | 路径/事件 | 缺失位置 |
|------|-----------|----------|
| endpoint | {{METHOD}} {{path}} | request example 缺失 |
| endpoint | {{METHOD}} {{path}} | response example 缺失 |
| webhook | {{event_name}} | 回调 example 缺失 |

> 本章节仅在存在缺失时输出，全部补齐时不输出此章节。
