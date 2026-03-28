# 用户故事卡模板（Story Card）

> **使用场景**：单一场景的小需求，或大型 Feature PRD 的子故事拆解。
> **复制方法**：运行 `/new-prd story-card [标题]`，AI 自动从此模板创建。

---

```yaml
---
type: story-card
id: SC-XXX
title: [标题]
status: draft
version: "1.0"
created: YYYY-MM-DD
updated: YYYY-MM-DD
author:
feature-area:
epic:             # 所属史诗 PRD 的 ID，如 E-001（无则留空）
parent-feature:   # 所属功能 PRD 的 ID，如 F-001（无则留空）
has-prototype: false
---
```

---

# [标题]

## 用户故事

> **As a** [用户角色]，
> **I want to** [期望行为]，
> **so that** [业务 / 用户价值]。

---

## 验收标准

- [ ] **AC-1**：
- [ ] **AC-2**：
- [ ] **AC-3**：

---

## 备注 & 约束

<!-- 边界条件、不包含范围、特殊说明 -->

-

---

## 变更记录

> 详细变更历史见同目录 `CHANGELOG.md`。

| 版本 | 日期 | 变更摘要 |
|------|------|----------|
| 1.0 | YYYY-MM-DD | 初始版本 |
