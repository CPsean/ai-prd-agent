# drafts/ — 草稿暂存区

> 所有 AI 生成的初稿都先落在这里，用户确认后再流转到正式区。

---

## 存放内容

| 来源 | 产物 | 后续流向 |
|------|------|----------|
| `/new-prd` | PRD 初稿（`[标题]/prd.md`） | 用户确认 → 移入 `prds/` |
| `/design-solution` | 方案设计文档 | 用户确认 → 移入 `outputs/` 或留存 |
| 手动记录 | 会议纪要、灵感草稿、探索方案 | 按需整理 |

---

## 流转规则

```
drafts/[标题]/prd.md
    ↓ 用户说「确认移入正式区」
prds/[标题]/prd.md  +  _registry.md 注册

drafts/[日期]-[主题]-solution.md
    ↓ 用户说「整理到 outputs」
outputs/[文件名]
```

**触发方式**：直接告诉 AI「确认 [标题] PRD 移入正式区」或「把 [文件] 整理到 outputs」即可，无需额外命令。

---

## 目录结构示例

```
drafts/
  用户登录/               ← /new-prd 生成的 PRD 草稿
    prd.md
    CHANGELOG.md
    archive/
  2026-04-09-登录方案设计.md  ← /design-solution 生成的方案文档
  会议记录-需求评审.md         ← 手动记录
```

---

## 注意事项

- 草稿区内容**不被 AI 自动消费**，不会影响正式 PRD 的读取和生成
- `prds/_registry.md` 只收录已确认的 PRD，草稿不在其中
- 可随时清理过期草稿，不影响正式区
