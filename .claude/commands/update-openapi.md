# 命令：/update-openapi [api-name]

增量同步 PRD §8.10 接口变更到 OpenAPI 规范文件，基于 changelog 头部去重，只处理未同步条目。

$ARGUMENTS

## 参数说明

- `[api-name]`：API 规范文件名（不含 .yaml 扩展名），如 `order-api`

---

## 执行步骤

### Step 1：前置检查

1. 检查 `openapi/[api-name].yaml` 是否存在：
   - **不存在** → 停止，输出："未找到 `openapi/[api-name].yaml`，请先运行 `/import-openapi [api-name]` 建立规范文件。"

2. 检查关联 PRD 是否在正式区（`prds/`）：
   - 若用户指定了 PRD 且仅在 drafts/ → **阻断**，不写入任何文件，提示移入正式区

### Step 2：读取 changelog，确认已同步记录

读取 `openapi/[api-name].yaml` 头部的 changelog 块（以 `# ` 开头的注释行，位于 yaml 内容之前）。

已同步记录格式示例：
```
# 2026-05-01 | F-014 | V1.0 | 新增 /v1/orders（GET/POST）
```

提取所有已同步的 `PRD-ID + PRD版本` 组合（如"F-014 V1.0"），记录为已同步集合。

### Step 3：读取 PRD §8.10，筛选未同步条目

1. 读取 `prds/_registry.md`，查找关联 PRD
2. 读取该 PRD 的所有 §8.x.10（或 §8.10）章节
3. 按 PRD 版本分组，对照已同步集合筛选未同步条目
4. **已同步版本的条目完全跳过**，不出现在后续操作中

**无未同步条目时**：输出"所有接口变更已同步，`openapi/[api-name].yaml` 已是最新状态。"，结束命令。

### Step 4：生成增量 diff 摘要

针对未同步条目，生成增量 diff 摘要：

```
待同步变更（来源：F-014 V1.1）：
+ 新增 endpoint：GET /v1/orders/summary — 订单汇总查询
~ 修改 endpoint：POST /v1/orders — 新增请求参数 source（string，可选）
共 N 处变更
```

**展示 diff 摘要，等待 PM 确认**，不立即修改文件。

### Step 5：执行增量修改

PM 确认后：

1. 对 yaml 文件执行增量修改（仅修改 diff 中涉及的部分，不触碰其他内容）
2. 在 yaml 头部 changelog 块**末尾追加**新条目（格式：`# 日期 | PRD-ID | PRD版本 | 变更摘要`）：
   ```
   # [今天日期] | F-014 | V1.1 | [变更摘要，不超过 50 字]
   ```
3. 写入完成后输出："`openapi/[api-name].yaml` 已更新，追加 changelog 条目 V1.1。"

### Step 6：废弃接口提示

检查 diff 中是否有"废弃 endpoint"条目：

- **有废弃接口** 且 `_hidden-interfaces.md` 中**未收录**该接口 → 提示：
  > **检测到废弃接口：[路径]**
  > 建议将其加入 `openapi/_hidden-interfaces.md` 的接口级隐藏清单，以确保下次导出时从对外版中移除。
  >
  > 回复"确认"写入，或回复"跳过"不处理。

- 已在 `_hidden-interfaces.md` 中 → 静默跳过
- 无废弃接口 → 静默跳过
