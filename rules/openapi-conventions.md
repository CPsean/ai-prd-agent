# OpenAPI 规范约束规则

> **定位**：SaaS 平台对外开放 API 的设计规范约束基准，覆盖 AI 生成 OpenAPI yaml 时最易出错的 11 个维度。
> 规则编号格式：`OAC-[维度]-[序号]`（OAC = OpenAPI Convention）

---

## 顶层设计原则

> 以下 3 条原则统领全局，是具体规则背后的设计动机。规则判断有歧义时，回归原则裁决。

**原则一：对外 API 是产品契约，不是内部接口的镜像**
面向外部调用方设计资源模型，使用调用方能理解的业务概念（accounts、orders、projects），
不暴露内部实现对象（UserDO、OrderEntity、ProcessInstance、RuntimeContext）。

**原则二：契约一旦发布，默认长期维护**
已发布的 API 应视为对外承诺。设计时考虑向前兼容：新增字段、不删除字段、不改字段含义。
不兼容变更必须发布新版本。

**原则三：API 设计面向调用方理解，而非实现便利**
命名和结构应让外部开发者一眼读懂，无需查阅内部文档。
字段名、错误码、枚举值都应是自解释的。

---

## 版本声明规则

| 规则 | 说明 |
|------|------|
| 新建 yaml 文件 | 头部写入 `openapi: 3.1.0` |
| Webhook 写法 | 使用原生 `webhooks:` 字段，不使用 `x-webhooks:` 扩展 |
| 导入 3.0.x 文件 | 不修改原版本字段；质检报告末尾追加版本升级提示 |

---

## OAC-PATH：路径命名规范

### OAC-PATH-001：路径单词使用小写连字符（kebab-case）
**要求**：URL 路径中的多词资源名使用小写字母和连字符，禁止驼峰、下划线、大写
**违规**：`/openapi/v1/apiKeys` `/openapi/v1/UserGroups` `/openapi/v1/billing_accounts`
**合规**：`/openapi/v1/api-keys` `/openapi/v1/user-groups` `/openapi/v1/billing-accounts`

### OAC-PATH-002：资源名使用复数名词
**要求**：路径中的资源名使用复数形式，不使用动词或单数
**违规**：`/openapi/v1/user` `/openapi/v1/getOrder` `/openapi/v1/createProject`
**合规**：`/openapi/v1/users` `/openapi/v1/orders` `/openapi/v1/projects`

### OAC-PATH-003：路径结构遵循 `/openapi/v{N}/resources` 格式
**要求**：对外开放 API 路径必须包含版本号，使用 `/openapi/v1/...` 或 `/partner/v1/...` 前缀
**违规**：`/api/users` `/v1/orders` `/users`
**合规**：`/openapi/v1/users` `/openapi/v2/orders` `/partner/v1/projects`

### OAC-PATH-004：非 CRUD 业务动作使用动作子路径
**要求**：明确的业务动作（状态变更、触发操作）使用 `POST /resources/{id}/action` 形式，不在主资源路径中使用动词
**违规**：`GET /openapi/v1/orders/{id}/cancel` `POST /openapi/v1/cancelOrder`
**合规**：`POST /openapi/v1/orders/{orderId}/cancel` `POST /openapi/v1/users/{userId}/disable`

### OAC-PATH-005：不暴露内部对象名称
**要求**：路径中只使用外部调用方理解的业务资源名，不暴露内部技术命名
**违规**：`/openapi/v1/userDO` `/openapi/v1/orderEntities` `/openapi/v1/processInstances`
**合规**：`/openapi/v1/users` `/openapi/v1/orders` `/openapi/v1/workflows`

---

## OAC-HTTP：HTTP Method 语义规范

### OAC-HTTP-001：GET 只用于查询，不触发副作用
**要求**：GET 请求必须是幂等且无副作用的查询操作，任何状态变更禁止使用 GET
**违规**：`GET /openapi/v1/users/{id}/disable` `GET /openapi/v1/orders/{id}/cancel`
**合规**：`POST /openapi/v1/users/{id}/disable` `DELETE /openapi/v1/orders/{id}`

### OAC-HTTP-002：HTTP Method 与操作语义匹配
**要求**：创建资源用 POST，局部更新用 PATCH，全量替换用 PUT，删除用 DELETE
**违规**：`POST /openapi/v1/users/{id}`（更新用了POST） `GET /openapi/v1/projects/{id}/delete`
**合规**：`POST /openapi/v1/projects`（创建）`PATCH /openapi/v1/projects/{id}`（局部更新）`DELETE /openapi/v1/projects/{id}`

### OAC-HTTP-003：HTTP 状态码语义正确，禁止用 200 包装所有错误
**要求**：成功返回 2xx，客户端错误返回 4xx，服务端错误返回 5xx；不允许所有响应都返回 200
**违规**：`HTTP 200` + body `{"code": "RESOURCE_NOT_FOUND", ...}`（错误用了200）
**合规**：`HTTP 404` + body `{"code": "RESOURCE_NOT_FOUND", ...}`

### OAC-HTTP-004：异步操作返回 202 并提供任务查询接口
**要求**：耗时操作使用 202 Accepted，响应体包含 jobId 和状态查询入口
**违规**：长耗时操作直接同步返回 200，无任务 ID
**合规**：`HTTP 202` + `{"data": {"jobId": "job_123", "status": "PROCESSING"}}` + `GET /openapi/v1/jobs/{jobId}`

---

## OAC-ERR：错误响应体结构规范

### OAC-ERR-001：成功响应使用统一结构
**要求**：成功响应体固定格式为 `{code, message, requestId, data}`，字段不得增删或改名
**违规**：`{"status": "ok", "result": {...}}` `{"success": true, "payload": {...}}`
**合规**：`{"code": "SUCCESS", "message": "success", "requestId": "req_123", "data": {...}}`

### OAC-ERR-002：错误响应使用统一结构，支持 details 数组
**要求**：错误响应体固定格式为 `{code, message, requestId, details[]}`，details 每项含 `{field, reason}`
**违规**：`{"error": "not found"}` `{"msg": "参数错误", "errCode": 1001}`
**合规**：`{"code": "VALIDATION_FAILED", "message": "...", "requestId": "req_123", "details": [{"field": "userId", "reason": "..."}]}`

### OAC-ERR-003：错误码使用 UPPER_SNAKE_CASE 格式
**要求**：`code` 字段值使用大写字母和下划线，使用预定义错误码集合
**违规**：`"code": "resourceNotFound"` `"code": "404"` `"code": "error_1001"`
**合规**：`"code": "RESOURCE_NOT_FOUND"` `"code": "VALIDATION_FAILED"` `"code": "RATE_LIMIT_EXCEEDED"`

> 预定义错误码（可扩展，不可修改已发布含义）：
> `INVALID_REQUEST` / `UNAUTHORIZED` / `FORBIDDEN` / `RESOURCE_NOT_FOUND` /
> `RESOURCE_STATE_CONFLICT` / `VALIDATION_FAILED` / `RATE_LIMIT_EXCEEDED` /
> `QUOTA_EXCEEDED` / `IDEMPOTENCY_CONFLICT` / `INTERNAL_SERVER_ERROR`

### OAC-ERR-004：禁止在响应中暴露内部信息
**要求**：错误响应不得包含内部堆栈信息、内部系统名称、数据库字段名、内网地址
**违规**：`"message": "NullPointerException at OrderService.java:142"` `"reason": "OMS系统调用失败"`
**合规**：`"message": "Internal server error, please retry later."` `"reason": "Service temporarily unavailable."`

---

## OAC-FIELD：参数命名规范

### OAC-FIELD-001：请求/响应 body 字段使用 lowerCamelCase
**要求**：JSON body 中所有字段名使用小写驼峰，禁止下划线、PascalCase、连字符
**违规**：`"user_name"` `"UserName"` `"user-name"` `"USERNAME"`
**合规**：`"userName"` `"projectId"` `"createdAt"` `"expiresAt"`

### OAC-FIELD-002：时间字段使用 ISO 8601 格式
**要求**：所有时间字段类型为 `string`，格式为 ISO 8601（含时区），schema 中注明 `format: date-time`
**违规**：`"createdAt": 1716278400`（时间戳）`"createdAt": "2026/05/21"`（非标准格式）
**合规**：`"createdAt": "2026-05-21T10:00:00Z"` + schema: `{type: string, format: date-time}`

### OAC-FIELD-003：枚举字段必须在 schema 中列出全部枚举值
**要求**：枚举类型字段使用 `enum` 关键字列出所有合法值，枚举值使用 UPPER_SNAKE_CASE
**违规**：字段类型为 string 但未列 enum，或 enum 值为 `["1", "2", "3"]`
**合规**：`{type: string, enum: ["ACTIVE", "DISABLED", "PENDING"]}` 并在 description 说明各值含义

### OAC-FIELD-004：不通过 Header 传递业务身份信息
**要求**：tenantId、userId、orgId 等业务身份信息必须从可信 Token 中解析，不接受外部 Header 传入
**违规**：请求文档要求传入 `X-Tenant-Id: xxx` `X-User-Id: xxx`
**合规**：在 description 中说明"租户信息从 Access Token 中解析，无需传入"

---

## OAC-TYPE：参数类型定义规范

### OAC-TYPE-001：string 类型字段必须有 maxLength 约束
**要求**：所有 `type: string` 的请求字段必须在 schema 中声明 `maxLength`
**违规**：`{type: string}` 无长度限制
**合规**：`{type: string, maxLength: 200}` `{type: string, maxLength: 50, description: "项目名称，最多50字符"}`

### OAC-TYPE-002：array 类型字段必须有 maxItems 约束
**要求**：所有 `type: array` 的请求字段必须在 schema 中声明 `maxItems`
**违规**：`{type: array, items: {type: string}}` 无数量限制
**合规**：`{type: array, maxItems: 100, items: {type: string}}`

### OAC-TYPE-003：金额字段必须说明精度和货币单位
**要求**：涉及金额的字段，description 中必须明确货币单位和精度（小数位数）
**违规**：`{type: number, description: "金额"}` `{type: integer, description: "price"}`
**合规**：`{type: integer, description: "金额（单位：分，精度：2位小数，币种由currency字段指定）"}`

### OAC-TYPE-004：ID 字段使用 string 类型
**要求**：所有业务对象 ID 字段类型使用 `string`，不使用 `integer` 或 `number`，避免大整数精度丢失
**违规**：`"userId": {type: integer}` `"orderId": {type: number}`
**合规**：`"userId": {type: string, description: "用户唯一标识"}` `"orderId": {type: string}`

### OAC-TYPE-005：boolean 字段语义明确，禁用数字代替
**要求**：布尔值使用 `type: boolean`（true/false），禁用 0/1 或 "0"/"1" 代替
**违规**：`{type: integer, enum: [0, 1], description: "是否启用"}` `{type: string, enum: ["Y", "N"]}`
**合规**：`{type: boolean, description: "是否启用，true=启用，false=禁用"}`

---

## OAC-AUTH：认证与授权规范

### OAC-AUTH-001：securitySchemes 必须声明认证方式
**要求**：每个 OpenAPI 文件必须在 `components/securitySchemes` 中声明认证方式，且需要认证的路径必须应用 `security` 字段
**违规**：无 `securitySchemes` 声明；路径无 `security` 字段
**合规**：`securitySchemes: {bearerAuth: {type: http, scheme: bearer}}` + 路径写 `security: [{bearerAuth: []}]`

### OAC-AUTH-002：OAuth2 Scope 命名使用 `resource.action` 格式
**要求**：Scope 名称使用 `资源名.动作` 格式（全小写+点分隔），动作限于 `read` / `write` / `manage` / `upload` / `download` / `export`
**违规**：`"all"` `"admin"` `"api"` `"full_access"` `"ORDER_READ"` `"openapi:order:read"`
**合规**：`"users.read"` `"orders.write"` `"files.upload"` `"reports.export"` `"webhooks.manage"`

### OAC-AUTH-003：OAuth2 flow 中每个 scope 必须有描述
**要求**：`securitySchemes` 中 OAuth2 flow 的 `scopes` 字段每个条目必须提供非空描述，不允许留空字符串
**违规**：`scopes: {"users.read": ""}` 或 scopes 为空对象 `{}`
**合规**：`scopes: {"users.read": "读取用户基本信息", "orders.write": "创建和更新订单"}`

---

## OAC-HDR：请求头规范

### OAC-HDR-001：Authorization 使用 Bearer 格式，禁用自定义 Token Header
**要求**：认证 token 必须通过标准 `Authorization: Bearer <token>` 传递，`securitySchemes` 中 scheme 为 `bearer`；禁止使用 `X-Api-Token`、`X-Access-Token` 等自定义 Header 传递令牌
**违规**：`X-Api-Token: xxx`（自定义 Header 传 Token）`Authorization: token xxx`（非 Bearer 格式）
**合规**：`Authorization: Bearer eyJxxx`；securitySchemes 声明 `{type: http, scheme: bearer, bearerFormat: JWT}`

### OAC-HDR-002：关键操作必须在参数中声明 Idempotency-Key
**要求**：创建关键业务资源、提交业务命令、触发异步任务等 POST 接口，必须在 `parameters` 中声明 `Idempotency-Key` header 参数（必填），并在 description 中说明幂等行为
**违规**：创建订单、发起支付等接口未声明 Idempotency-Key
**合规**：`{name: Idempotency-Key, in: header, required: true, schema: {type: string, maxLength: 64, description: "幂等键，相同 key 重复调用返回首次结果"}}`

### OAC-HDR-003：建议声明 X-Request-Id 追踪参数
**要求**：接口 `parameters` 中建议声明 `X-Request-Id` header（非必填），用于客户端侧请求追踪和问题排查
**合规**：`{name: X-Request-Id, in: header, required: false, schema: {type: string, maxLength: 64}}`

---

## OAC-IDEM：幂等规范

### OAC-IDEM-001：关键操作必须说明幂等行为
**要求**：POST 接口且涉及创建资源、状态变更、支付/计费等场景，API description 中必须说明幂等行为（相同 Idempotency-Key 重复调用返回首次执行结果）
**判断依据**：接口为 POST 且路径动作含 create/submit/confirm/pay/trigger/cancel 等语义

### OAC-IDEM-002：幂等冲突返回 409 IDEMPOTENCY_CONFLICT
**要求**：相同 Idempotency-Key 但请求参数不一致时，返回 `HTTP 409`，错误码为 `IDEMPOTENCY_CONFLICT`
**违规**：幂等冲突用 `400 INVALID_REQUEST` 或 `200` + 自定义错误返回
**合规**：`HTTP 409` + `{"code": "IDEMPOTENCY_CONFLICT", "message": "Conflicting request with same idempotency key.", "requestId": "...", "details": []}`

---

## OAC-PAGE：分页规范

### OAC-PAGE-001：列表接口使用游标分页，禁用偏移分页
**要求**：列表查询接口使用 `pageSize + pageToken` 游标分页，禁止使用 `page + offset` 偏移分页（数据量大时存在性能和数据一致性问题）
**违规**：`GET /resources?page=2&limit=20` `GET /resources?offset=40&size=20`
**合规**：`GET /resources?pageSize=20&pageToken=xxx`

### OAC-PAGE-002：pageSize 参数必须声明 maximum 约束
**要求**：`pageSize` 参数 schema 中必须声明 `maximum`（建议不超过 100）和 `default`，避免调用方传入超大分页导致性能问题
**违规**：`{type: integer}` 无上限约束
**合规**：`{type: integer, minimum: 1, maximum: 100, default: 20}`

### OAC-PAGE-003：分页响应结构必须包含 nextPageToken 和 hasMore
**要求**：列表响应 `data` 对象中必须包含 `items`（array）、`nextPageToken`（string，末页为空字符串或 null）、`hasMore`（boolean）
**违规**：`{"data": {"list": [...], "total": 100}}`（使用 total 偏移式结构）或只返回 nextCursor 不含 hasMore
**合规**：`{"data": {"items": [...], "nextPageToken": "eyJxxx", "hasMore": true}}`

---

## OAC-COMPAT：兼容性规范

### OAC-COMPAT-001：以下变更属于向后兼容，可在同版本内发布
**兼容变更清单**：
- 新增 API 接口
- 新增可选请求字段
- 新增响应字段
- 新增错误码
- 放宽字段长度限制
- 新增 Webhook 事件类型
- 新增可选查询条件
- 新增枚举值（调用方须容错处理未知枚举）

### OAC-COMPAT-002：以下变更属于不兼容变更，必须发布新版本
**不兼容变更清单**：
- 删除或重命名字段
- 修改字段类型
- 修改字段含义
- 新增必填请求字段
- 删除枚举值
- 修改枚举含义
- 修改 URL 或 HTTP Method
- 修改认证方式或权限语义
- 修改错误码含义
- 修改分页规则

**合规要求**：不兼容变更必须发布至新版本路径（如 `/openapi/v2/...`），旧版本保留并进入废弃流程（普通 API 至少 3 个月，核心 API 至少 6 个月）

---

## OAC-WEBHOOK：Webhook 规范

### OAC-WEBHOOK-001：事件类型命名使用 `resource.action` 格式
**要求**：Webhook 事件类型使用 `资源名.动作` 格式（全小写+点分隔），动作使用过去时（created / updated / deleted / status_changed / completed / failed / paid / canceled）
**违规**：`"order_created"` `"ORDER.CREATED"` `"onOrderCreate"` `"orderCreatedEvent"`
**合规**：`"order.created"` `"invoice.paid"` `"project.archived"` `"job.completed"` `"subscription.canceled"`

### OAC-WEBHOOK-002：Webhook Payload 必须包含事件元数据字段
**要求**：Webhook 事件体 schema 中必须包含 `eventId`（string）、`eventType`（string）、`occurredAt`（string，format: date-time）、`data`（object）
**违规**：只有 `data` 字段无元数据；事件 ID 字段命名为 `id` 或 `uuid`
**合规**：`{eventId: "evt_123", eventType: "order.created", occurredAt: "2026-05-20T10:00:00Z", data: {...}}`

### OAC-WEBHOOK-003：Webhook 必须声明签名验证 Header
**要求**：OpenAPI `webhooks` 定义中必须声明 `X-Webhook-Signature` header 参数（必填），description 中说明签名算法；同时建议声明 `X-Webhook-Timestamp` 用于防重放
**违规**：Webhook 定义无签名 header；或只有 timestamp 无签名
**合规**：`{name: X-Webhook-Signature, in: header, required: true, description: "HMAC-SHA256 签名，格式：sha256=<hex>"}`

---

## 质检速查表

| 维度 | 规则编号 | 检查重点 |
|------|---------|---------|
| PATH | OAC-PATH-001 | 路径是否含大写、驼峰、下划线 |
| PATH | OAC-PATH-002 | 资源名是否为复数名词（非动词） |
| PATH | OAC-PATH-003 | 是否含 `/openapi/v{N}/` 前缀 |
| PATH | OAC-PATH-004 | 业务动作是否用 POST + 子路径（非 GET） |
| PATH | OAC-PATH-005 | 是否暴露内部对象名（DO/Entity/DTO/VO后缀等） |
| HTTP | OAC-HTTP-001 | GET 是否触发了状态变更 |
| HTTP | OAC-HTTP-002 | Method 与 CRUD 语义是否匹配 |
| HTTP | OAC-HTTP-003 | 是否有错误包在 HTTP 200 里返回 |
| HTTP | OAC-HTTP-004 | 异步操作是否返回 202 + jobId |
| ERR  | OAC-ERR-001 | 成功响应是否包含 code/message/requestId/data |
| ERR  | OAC-ERR-002 | 错误响应是否包含 code/message/requestId/details[] |
| ERR  | OAC-ERR-003 | code 值是否为 UPPER_SNAKE_CASE |
| ERR  | OAC-ERR-004 | message/reason 是否含内部堆栈/系统名/内网地址 |
| FIELD | OAC-FIELD-001 | body 字段名是否为 lowerCamelCase |
| FIELD | OAC-FIELD-002 | 时间字段是否为 ISO 8601 + format: date-time |
| FIELD | OAC-FIELD-003 | 枚举字段是否列出所有 enum 值 |
| FIELD | OAC-FIELD-004 | 是否要求传入 X-Tenant-Id / X-User-Id 等 Header |
| TYPE  | OAC-TYPE-001 | string 字段是否有 maxLength |
| TYPE  | OAC-TYPE-002 | array 字段是否有 maxItems |
| TYPE  | OAC-TYPE-003 | 金额字段 description 是否说明精度和货币 |
| TYPE  | OAC-TYPE-004 | ID 字段是否为 string 类型 |
| TYPE  | OAC-TYPE-005 | boolean 字段是否用 true/false（非 0/1） |
| AUTH  | OAC-AUTH-001 | securitySchemes 是否声明认证方式，路径是否应用 security |
| AUTH  | OAC-AUTH-002 | OAuth2 Scope 是否使用 resource.action 格式（非 all/admin 等宽泛值） |
| AUTH  | OAC-AUTH-003 | OAuth2 Scope 每个条目是否有非空描述 |
| HDR   | OAC-HDR-001 | 是否使用 Bearer 认证，禁用自定义 Token Header |
| HDR   | OAC-HDR-002 | 关键 POST 操作是否声明 Idempotency-Key 参数 |
| IDEM  | OAC-IDEM-001 | 关键操作 description 是否说明幂等行为 |
| IDEM  | OAC-IDEM-002 | 幂等冲突是否返回 409 IDEMPOTENCY_CONFLICT |
| PAGE  | OAC-PAGE-001 | 列表接口是否使用游标分页（pageSize+pageToken，非 page+offset） |
| PAGE  | OAC-PAGE-002 | pageSize 参数是否声明 maximum 约束 |
| PAGE  | OAC-PAGE-003 | 分页响应是否包含 items、nextPageToken、hasMore |
| COMPAT | OAC-COMPAT-002 | 含不兼容变更时是否发布新版本路径 |
| WEBHOOK | OAC-WEBHOOK-001 | 事件类型是否使用 resource.action 格式（全小写+点分隔） |
| WEBHOOK | OAC-WEBHOOK-002 | Webhook Payload 是否包含 eventId/eventType/occurredAt/data |
| WEBHOOK | OAC-WEBHOOK-003 | Webhook 定义是否声明 X-Webhook-Signature 签名 header |
