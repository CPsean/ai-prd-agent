# prds/ — 正式 PRD 存放区

> 这里是所有 PRD 的唯一权威来源。每个需求一个子文件夹，`prd.md` 是当前有效版本。

---

## 目录结构

```
prds/
  _registry.md              ← AI 首先读这里，找到对应 PRD 路径（勿手动改格式）
  [需求中文标题]/
    prd.md                  ← 当前有效版本（AI 主要消费此文件）
    CHANGELOG.md            ← 变更记录（不作为主要参考）
    fields.md               ← 字段清单（feature/epic 类型，按需生成）
    prototype/
      index.html            ← 可交互 HTML 原型（按需生成）
    archive/
      prd-v1.0.md           ← 历史快照（禁止修改）
  archive/                  ← 整体归档（需求废弃或完工后移入）
```

---

## 操作规范

| 操作 | 方式 | 说明 |
|------|------|------|
| 新建 PRD | `/new-prd [type] [标题]` | 草稿先进入 `drafts/`，用户确认后移入此处 |
| 更新 PRD | `/update-prd [标题] [变更描述]` | AI 自动归档旧版本，勿直接覆盖 `prd.md` |
| 查找 PRD | 先读 `_registry.md` | 根据索引定位路径，再读 `prd.md` |
| 归档需求 | 移入 `prds/archive/` | 需求废弃或完工时整体移入 |

---

## AI 读取规则

1. **优先读 `_registry.md`** → 定位目标 PRD 路径
2. **只读 `prd.md`** → 当前版本，不读 `archive/` 下的历史文件
3. **`CHANGELOG.md`** → 仅在被问及历史变更时读取
4. **`fields.md`** → 被问及字段详情或生成摘要时读取

---

## 版本管理规则

- `prd.md` 永远是当前有效版本
- 每次变更：自动归档旧版本 → 更新 `prd.md` → 追加 `CHANGELOG.md`
- 小修改：版本号 +0.1（1.0 → 1.1）；重大重构：升主版本（1.x → 2.0）
- **禁止**直接编辑 `archive/` 下的任何文件
