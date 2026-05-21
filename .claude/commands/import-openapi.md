# 命令：/import-openapi [api-name]

新建或差异比对更新 OpenAPI 规范文件，含目录结构初始化。

$ARGUMENTS

## 参数说明

- `[api-name]`：API 规范文件名（不含 .yaml 扩展名），如 `order-api`

---

## 执行步骤

### Step 1：正式区门控

读取 `prds/_registry.md`，检查当前工作区是否存在至少一个在 `prds/` 下的 PRD：

- **有正式区 PRD**：继续执行
- **无正式区 PRD**（当前仅有草稿区 PRD 或未找到 PRD）：
  - **阻断执行**，输出："OpenAPI 写入不可用：未找到正式区 PRD，请先确认 PRD 已从 drafts/ 移入 prds/"
  - 不创建任何文件，停止命令

若用户明确指定了关联 PRD（如"关联 F-014"），额外检查该 PRD 是否在 `prds/` 目录下：
- 在 drafts/ 下 → **阻断**，输出："PRD [ID]-[标题] 尚未移入正式区，OpenAPI 写入不可用，请先确认 PRD 移入 prds/"
- 在 prds/ 下 → 继续

### Step 2：目录结构初始化（OAPI-STOR-001）

检查 `openapi/` 目录是否存在：

**不存在时**，执行初始化（幂等，已存在则静默跳过各项）：

1. 创建 `openapi/` 目录
2. 创建 `openapi/_hidden-interfaces.md`，内容如下：

```markdown
# 隐藏接口清单

> 本文件维护导出对外版时需要过滤的接口和字段。
> `/export-openapi` 读取本文件执行两阶段过滤。

---

## 接口级隐藏（整条 endpoint 不出现在对外版）

| endpoint 路径 | HTTP 方法 | 隐藏原因 | 备注 |
|--------------|-----------|----------|------|
| | | | |

---

## 参数级隐藏（endpoint 保留，但特定字段/参数不出现在对外版）

| endpoint 路径 | HTTP 方法 | 字段位置（requestBody/response/params） | 字段名 | 隐藏原因 |
|--------------|-----------|----------------------------------------|--------|----------|
| | | | | |
```

3. 检查 `context/api-registry.md` 是否存在：
   - 不存在 → 创建，内容如下：

```markdown
# API 注册表

> 记录工作区所有 OpenAPI 规范文件的模块归属和版本信息。
> 按业务模块分组，同一 API 只归属一个模块。

---

## 模块：[业务模块名称]

| API 名称 | 文件路径 | 当前版本 | 关联 PRD | 最后同步日期 | 备注 |
|---------|---------|---------|---------|------------|------|
| | | | | | |
```

4. 创建 `outputs/openapi/` 目录，放置 `.gitkeep` 占位文件

5. 输出："OpenAPI 目录结构已初始化"，列出创建的文件路径

**已存在时**：静默跳过，直接进入 Step 3。

### Step 3：路径判断

检查 `openapi/[api-name].yaml` 是否存在：

- **不存在** → 进入 **Path A（新建规范）**
- **已存在** → 进入 **Path B（差异比对）**

---

## Path A：新建规范

### A-1 询问来源

向 PM 询问：

> **`[api-name].yaml` 尚不存在，请选择来源：**
> - **A. 导入已有文件**：提供现有 yaml/json 文件路径，或直接粘贴内容
> - **B. 从 PRD §8.10 生成**：基于关联 PRD 的接口变更说明自动生成
>
> 请回复 A 或 B。

### A-2a 来源 A：导入已有文件

1. 提示 PM 提供文件路径或粘贴内容
2. 解析收到的 yaml/json/Postman Collection 内容
3. **忠实导入约束（OAPI-IMP-FAITHFUL）**：对源文档执行字段级三项充足性检查：
   - **描述非空**：endpoint/字段的 description 有实质内容（非空、非占位符如"TODO"）
   - **字段名清晰**：字段名为有意义的英文命名（如 `orderStatus`），可直接理解语义
   - **分组完整**：endpoint 已按业务模块/资源分组（如按 tag 或路径前缀），结构清晰

   处理规则：
   - 三项均充足 → 直接引用原文写入 yaml，不得改写描述、扩写说明、重新分组
   - 部分不充足 → 仅对不充足字段向 PM 追问（≤3 个问题），已充足内容仍引用原文不动
   - 全部不充足 → 视为残缺文档，按"从 PRD §8.10 生成"路径处理（追问补全后生成）
   - **Webhook/错误码同等适用**：webhook 事件描述、回调参数表、错误码 message/reason 同样执行三项检查

4. **Webhook 与错误码识别**：解析源文档中的回调事件/Webhook 章节和错误码表：
   - Webhook → 写入 yaml `x-webhooks` 扩展（含事件类型、payload schema、示例）
   - 错误码 → 写入 yaml `x-error-codes` 扩展（数组格式，每项含 code/message/reason）
   - 回调事件中的公共结构 → 提取到 `components/schemas` 复用（如 WebhookSignerInfo）
   - 忠实导入约束同样适用于 webhook 事件描述和错误码文字
   - 源文档无 webhook/错误码章节时静默跳过，不追问

5. **展示接口清单��要**（非直接写入），格式如下：
   ```
   解析完成：
   - REST endpoint：N 条
     - GET /v1/xxx — [描述]
     - POST /v1/yyy — [描述]
     ...（超过 10 条时省略后续，标注"共 N 条，已展示前 10 条"）
   - Webhook 事件：W 个（如有）
     - ENVELOPE_START — [描述]
     - ENVELOPE_FINISH — [描述]
   - 错误码：E 条（如有）
   ```
5b. **警告模式规范质检（OAPI-QC-001）**

   读取 `rules/openapi-conventions.md`，对解析后的 yaml 内容按质检速查表逐维度检查：

   - **rules 文件不存在** → 跳过质检，输出提示"规范约束文件未找到，跳过质检（可创建 `rules/openapi-conventions.md` 启用）"，继续步骤 6。

   **无违规时**：
   ```
   ✅ 规范质检通过（5 个维度无违规项）
   ```
   继续步骤 6（等待 PM 确认）。

   **有违规时**：
   ```
   ⚠️ 规范质检报告（警告模式）：
   发现 N 处不符合 rules/openapi-conventions.md 的内容：

   | 维度 | endpoint / 字段 | 违规规则 | 具体问题 | 期望值 |
   |------|----------------|---------|---------|--------|
   | OAC-PATH | GET /openapi/v1/getUser | OAC-PATH-002 | 路径包含动词 | /openapi/v1/users/{userId} |
   | OAC-FIELD | POST body.user_name | OAC-FIELD-001 | 字段名非 lowerCamelCase | userName |

   选择处理方式：
   A. 接受导入（后续渐进维护升级）
   B. 停止，我先调整后重新导入
   ```

   - PM 选 **A**：继续写入，步骤 7 写入 yaml 时在头部 changelog 末尾追加 `# [待升级] N 处不合规项（OAC-PATH-002, OAC-FIELD-001）`（列出涉及的规则编号）
   - PM 选 **B**：停止执行，不写入任何文件

   **版本字段检测**（独立检查，不计入违规数 N）：
   若源文档 `openapi:` 字段为 `3.0.x`，在报告末尾追加独立提示行（有无违规均追加）：
   ```
   ℹ️ 版本提示：当前文件为 OpenAPI 3.0.x，建议升级至 3.1.0（webhooks 字段写法有变化）
   ```

6. **等待 PM 明确确认**（步骤 5b 中的 A 选择即视为确认；无违规时等待"确认"/"写入"/"没问题"）后才写入文件
7. 写入 `openapi/[api-name].yaml`

### A-2b 来源 B：从 PRD §8.10 生成

1. 读取关联 PRD 的 §8.10 章节内容
2. **判断描述充分性**：必须含有路径/HTTP方法/参数类型等结构性信息才视为充分：
   - **描述充分**：生成候选 yaml，进入步骤 4
   - **描述不足**（缺少关键结构信息）：向 PM **追问**，不超过 3 个问题，例如：
     - "接口路径和 HTTP 方法是什么？（如 POST /v1/orders）"
     - "主要请求参数有哪些？（字段名 + 类型 + 是否必填）"
     - "成功响应的主要字段结构是什么？"
3. PM 回答后重新评估充分性，充分时继续
4. **生成候选 yaml**（内部，尚未展示给 PM）：
   - 版本字段写入 `openapi: 3.1.0`（OAPI-VER-001）
   - Webhook 相关内容使用原生 `webhooks:` 字段，不使用 `x-webhooks:` 扩展
5. **阻断模式规范自检（OAPI-QC-002）**：

   读取 `rules/openapi-conventions.md`，对生成内容按质检速查表逐维度检查：

   - **rules 文件不存在** → 跳过自检，在生成内容末尾追加提示"规范约束未启用，建议创建 `rules/openapi-conventions.md`"，继续步骤 6。

   **自检通过** → 直接展示候选内容给 PM，继续步骤 6。

   **自检未通过（阻断模式）**：
   - **不向 PM 展示违规内容**
   - AI 根据违规规则直接修正（如路径驼峰→连字符、字段名下划线→驼峰等机械性转换）
   - 修正后重新自检，循环直到通过
   - 若同一问题修正后循环超过 **2 次**仍未通过：展示给 PM，说明无法自动修正的具体规则编号和原因，请 PM 提供补充信息

   复杂语义判断（字段含义是否清晰等）不自动修正，直接上报 PM。

6. **展示已通过自检的候选 yaml**（完整内容）给 PM
7. **不输出含大量 `# TODO` 注释的残缺结构**——如信息仍不足，继续追问而非输出占位结构
8. **等待 PM 确认**后写入 `openapi/[api-name].yaml`

---

## Path B：差异比对

### B-1 提示进入比对模式

输出："检测到 `openapi/[api-name].yaml` 已存在，进入差异比对模式。请提供新版本文件内容或路径。"

等待 PM 提供新版本内容。

### B-2 生成 diff 摘要

解析新旧两版本，生成结构化 diff 摘要：

```
差异比对结果：
+ 新增 endpoint：POST /v1/xxx（[描述]）
~ 修改 endpoint：GET /v1/yyy — 新增参数 status（string）
- 废弃 endpoint：DELETE /v1/zzz
共 N 处变更
```

### B-3 引导提示（有差异时）

若 diff 非空，展示以下引导：

> **检测到 N 处接口变更。**
> 建议先通过需求澄清流程（`/requirement-clarifier`）完成需求分析，确保变更有对应 PRD §8.10 记录，再执行同步。
>
> 选择操作：
> - **A. 先走需求澄清**：停止，不修改已有文件
> - **B. 直接导入**：继续，changelog 将标注"直接导入，无关联 PRD §8.10 变更记录"
>
> 请回复 A 或 B。

### B-4a 选 A（先走需求澄清）

停止执行，不修改已有 yaml，输出建议步骤：
1. 运行 `/requirement-clarifier [需求描述]`
2. 澄清完成后更新 PRD §8.10
3. 再运行 `/update-openapi [api-name]` 同步

### B-4b 选 B（直接导入）

1. 再次展示 diff 摘要，等待 PM **最终确认**
2. PM 确认后，覆盖写入 `openapi/[api-name].yaml`
3. 在 yaml 头部追加 changelog 条目：
   ```yaml
   # [今天日期] | 直接导入 | — | 直接导入，无关联 PRD §8.10 变更记录
   ```

---

## Step 4：完成后提议更新 api-registry.md（OAPI-REG-001）

写入完成后，检查 `context/api-registry.md` 是否已包含该 API：

- **未包含**：询问 PM 归属模块，然后输出提议：
  > **建议在 `context/api-registry.md` 注册该 API：**
  > 模块：[PM 指定的模块名]，API 名称：[api-name]，文件路径：`openapi/[api-name].yaml`
  >
  > 回复"确认"写入，或告知需要调整。

- **已包含**：输出"api-registry.md 中已有该 API 记录，无需更新。"
