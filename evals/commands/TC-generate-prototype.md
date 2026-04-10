# 测试用例：/generate-prototype 命令

> 关联命令：`.claude/commands/generate-prototype.md`
> 参数格式：`/generate-prototype [标题或ID]`
> 前置条件：目标 PRD 已在 `prds/` 正式区注册

---

## TC-GP-01 正常生成原型（Feature PRD）

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证基于正式区 PRD 正常生成 HTML 原型，文件结构和内容符合规范 |
| **前置条件** | `prds/消息通知设置/prd.md` 存在且包含"页面 & 交互说明"章节，定义了至少 2 个页面 |

**测试输入**
```
/generate-prototype 消息通知设置
```

**预期行为**
1. 从 `_registry.md` 定位 `prds/消息通知设置/prd.md`
2. 读取 PRD，识别"页面 & 交互说明"中定义的所有页面
3. 输出规划清单（页面名称、元素、交互规则），等待用户确认
4. 确认后生成 `prds/消息通知设置/prototype/index.html`
5. 更新 `prd.md` frontmatter：`has-prototype: true`
6. 输出确认信息：文件路径、页面清单、预览提示

**检查要点**
- [ ] `prototype/index.html` 存在于对应 PRD 文件夹下
- [ ] HTML 为纯 HTML + CSS + JS，无外部 CDN 依赖
- [ ] 页面间有 Tab 或导航切换
- [ ] 每个 PRD 页面对应原型中的一个 section
- [ ] 包含空状态、加载态、错误态占位
- [ ] 每个页面底部有折叠区"对应 PRD 章节"
- [ ] `prd.md` 中 `has-prototype` 已改为 `true`

---

## TC-GP-02 目标 PRD 仍在草稿区

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证草稿区 PRD 无法生成原型，AI 正确拒绝并提示 |
| **前置条件** | `drafts/用户登录失败提示优化/prd.md` 存在，`prds/` 中无此 PRD |

**测试输入**
```
/generate-prototype 用户登录失败提示优化
```

**预期行为**
- 查 `_registry.md` 未找到该 PRD
- 停止执行，告知用户该 PRD 尚未移入正式区
- 建议先确认发布后再运行此命令
- **不**在 drafts/ 中生成任何原型文件

**检查要点**
- [ ] 未创建任何 prototype/ 文件
- [ ] AI 明确说明"尚未移入正式区，无法生成原型"
- [ ] 提供了发布操作的引导

---

## TC-GP-03 PRD 不存在

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证 PRD 在 registry 中不存在时正确报错 |
| **前置条件** | 无任何名为"购物车结算"的 PRD |

**测试输入**
```
/generate-prototype 购物车结算
```

**预期行为**
- 查 `_registry.md` 未找到
- 明确告知用户该 PRD 不存在
- 建议使用 `/new-prd` 创建

**检查要点**
- [ ] 未创建任何文件
- [ ] AI 明确说明未在注册表中找到
- [ ] 提供了 `/new-prd` 建议

---

## TC-GP-04 生成前输出规划清单并等待确认

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证 AI 不直接生成代码，而是先输出规划清单让用户确认 |
| **前置条件** | 任意正式区 PRD 存在 |

**测试输入**
```
/generate-prototype [已存在的 PRD 标题]
```

**预期行为**
1. 读取 PRD 后输出规划清单：每个页面的名称、核心元素、交互规则
2. 等待用户确认后再生成代码
3. **不**在输出规划清单的同时就创建文件

**检查要点**
- [ ] 第一轮输出仅包含规划清单，不包含代码
- [ ] 规划清单中的页面与 PRD "页面 & 交互说明"章节一一对应
- [ ] AI 明确询问"确认后开始生成"

---

## TC-GP-05 有 page-spec.md 时优先以其为输入

| 字段 | 内容 |
|------|------|
| **状态** | ✅ 2026-04-10 |
| **测试目标** | 验证 page-spec.md 存在时，AI 优先读取 page-spec 而非 PRD 的"页面 & 交互说明"章节 |
| **前置条件** | `prds/消息推送设置/prd.md` 存在，`prds/消息推送设置/page-spec.md` 存在（由 TC-GPS-01 生成） |

**测试输入**
```
/generate-prototype 消息推送设置
```

**预期行为**
1. 检查 `prds/消息推送设置/page-spec.md` 存在
2. 以 page-spec.md 为主要输入（页面列表、区块结构、状态、操作说明）
3. 生成的原型 `<head>` 注释中 `generated-from-page-spec` 填写 page-spec 的 `source-prd-version`
4. **不**需要提示"建议先运行 /generate-page-spec"

**检查要点**
- [ ] AI 输出中未出现"未找到页面规格卡"或"建议先运行 /generate-page-spec"的提示
- [ ] `prototype/index.html` 的 `<head>` 注释中 `generated-from-page-spec` 字段有值（非 N/A）
- [ ] 规划清单中的页面结构与 page-spec.md 内容一致（而非仅基于 PRD 推断）

---

## TC-GP-06 无 page-spec.md 时回退 PRD 并提示建议

| 字段 | 内容 |
|------|------|
| **状态** | ✅ 2026-04-10 |
| **测试目标** | 验证无 page-spec 时，AI 回退读取 PRD 并输出"建议先运行 /generate-page-spec"的提示 |
| **前置条件** | `prds/消息通知设置/prd.md` 存在，无 page-spec.md |

**测试输入**
```
/generate-prototype 消息通知设置
```

**预期行为**
1. 检查 `prds/消息通知设置/page-spec.md`，不存在
2. 输出提示：
   > "未找到页面规格卡，将直接基于 PRD 生成原型。建议先运行 `/generate-page-spec 消息通知设置` 以提升原型准确性。"
3. 回退读取 `prd.md` 的"页面 & 交互说明"章节，继续执行后续步骤
4. 生成的原型 `<head>` 注释中 `generated-from-page-spec: N/A`

**检查要点**
- [ ] AI 输出中包含"未找到页面规格卡"相关提示
- [ ] 提示中包含 `/generate-page-spec 消息通知设置` 命令
- [ ] 生成流程未中断，最终仍生成了 `prototype/index.html`
- [ ] `<head>` 注释中 `generated-from-page-spec: N/A`

---

## TC-GP-07 生成完成后：有关联 page-spec 时提示 /sync-docs

| 字段 | 内容 |
|------|------|
| **状态** | ✅ 2026-04-10 |
| **测试目标** | 验证有 page-spec 时，原型生成完毕后输出 /sync-docs 引导提示 |
| **前置条件** | `prds/消息推送设置/page-spec.md` 存在，原型已确认生成 |

**预期行为**（步骤 5 输出确认部分）
- 输出文件路径、页面列表、预览说明
- 附加提示：
  > "如后续 PRD 或页面规格有变更，可运行 `/sync-docs 消息推送设置` 检查文档一致性。"

**检查要点**
- [ ] 输出中包含 `/sync-docs [标题]` 引导
- [ ] 引导出现在步骤 5 的确认信息末尾（非中途打断）
- [ ] 无 page-spec 时（TC-GP-06 场景）**不**包含此引导
