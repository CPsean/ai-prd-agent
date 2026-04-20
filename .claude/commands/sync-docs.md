# 命令：检查文档一致性

检查指定需求的 PRD、页面规格卡、原型是否保持一致，列出潜在差异并给出建议操作：

$ARGUMENTS

## 执行步骤

**1. 定位文档**

- 从 `$ARGUMENTS` 提取标题或 ID
- 查 `prds/_registry.md` 定位 PRD，读取 `prd.md` 和 `CHANGELOG.md`
- 读取 PRD YAML，获取：
  - `version`：当前版本号
  - `has-page-spec` / `page-spec-path`：是否有页面规格卡
  - `has-prototype` / `prototype-path`：是否有原型
- 若 PRD 未在注册表中：停止执行，提示用户确认标题是否正确

**2. 读取关联文档元数据**

- **page-spec.md**（若存在）：读取文件头部元数据，获取 `source-prd-version` 和 `last-updated`
- **prototype/index.html**（若存在）：读取 `<head>` 中的生成记录注释，获取 `generated-from-prd-version` 和 `generated-date`

**3. 识别潜在不一致**

读取 `CHANGELOG.md`，找出所有版本号**晚于** page-spec 或原型生成时所基于版本的变更记录。

对每条晚于关联文档的 CHANGELOG 条目，判断其 **影响范围** 是否可能波及下游文档：

| 影响范围关键词 | 可能影响 |
|-------------|---------|
| 页面、入口、弹窗、流程、交互、操作 | page-spec + 原型 |
| 布局、组件、文案、状态 | page-spec + 原型 |
| 权限、角色、数据范围 | page-spec（部分）+ 原型（部分）|
| 业务规则、字段、接口 | 通常不影响 page-spec / 原型 |

**4. 输出检查结果**

按以下格式输出，每条潜在不一致附建议操作：

---

**文档一致性检查报告 — [标题]**

当前 PRD 版本：v[x.x] （更新于 [日期]）
页面规格卡基于：PRD v[x.x]（生成于 [日期]）
原型基于：PRD v[x.x]（生成于 [日期]）

**发现 [N] 处潜在不一致：**

1. **[变更类型]**（PRD v[x.x] → [日期]）
   变更内容：[CHANGELOG 中的变更描述]
   影响范围：[受影响章节/页面]
   可能波及：page-spec / 原型
   建议操作：重新运行 `/generate-page-spec [标题]` 更新页面规格，再运行 `/generate-prototype [标题]` 同步原型

2. [下一条...]

---

**若无不一致**，输出：
> 所有关联文档与当前 PRD 保持一致，无需同步。

**5. Context 一致性检查**（可选，context 文件存在时执行）

在文档版本检查完成后，额外检查 PRD 与产品上下文文件的一致性。

**5a. 术语孤岛检查**（`context/business-glossary.md` 存在时）

1. 读取 PRD §4（需求对象与概念模型）中列出的新引入术语
2. 与 `context/business-glossary.md` 比对，找出 §4 中有但 glossary 中没有的术语
3. 找出 glossary 中已有但 §4 未引用（本 PRD 明显用到但未提及）的术语

**5b. 功能前缀检查**（`context/product-feature-map.md` 存在时）

1. 读取 PRD §7（功能清单）中的所有功能编号前缀（`[AREA]` 部分）
2. 与 `context/product-feature-map.md` 前缀映射表比对，找出未注册的前缀

**5c. 输出格式**

在文档版本检查报告之后，追加「Context 一致性」小节：

```
**Context 一致性检查：**

术语孤岛（§4 有但 glossary 未登记）：
- [术语名]（建议追加到 context/business-glossary.md）

功能前缀未注册（§7 有但 feature-map 未登记）：
- [前缀]（如 USR-，建议追加到 context/product-feature-map.md 前缀映射表）
```

若两项均无问题，输出：`✅ Context 一致性：无孤岛`

若 context 文件均不存在，跳过本步骤，不输出任何提示。

**6. 询问是否立即执行**

> 是否现在开始同步？请告知需要处理哪几条，或回复"全部"由 AI 依次执行。

## 适用场景

- PRD 更新后，检查 page-spec 和原型是否需要同步
- 原型评审后发现问题，反向检查 PRD 是否需要更新
- 阶段性做全面文档核查

不适用于：草稿区 PRD（尚未有关联文档）。
