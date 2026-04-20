# 集成测试：完整工作流链路

> **测试目标**：验证从需求输入到 PRD 确认的完整工作流，以及 context 文件与 PRD 之间的双向一致性。
> **关联命令**：`requirement-clarifier` → `new-prd` → `sync-docs`
> **执行说明**：集成测试需按顺序执行，后续测试用例依赖前置用例的输出。可按场景分组独立执行。

---

## 场景一：两阶段需求分析 + rdd.md 渐进式写入

### TC-INT-01 Phase 1 完成后 rdd.md 正确创建

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证 Phase 1 用户故事确认后立即创建 rdd.md，状态和结构正确 |
| **前置条件** | `drafts/报销单批量导出/` 目录不存在 |

**测试输入**
```
/requirement-clarifier 财务人员需要每月将费用报销单批量导出为 Excel，目前只能逐条下载 PDF，非常耗时，导致月末结账时大量等待。
```

**预期行为**
1. AI 完成 P1-3 X-Y 诊断，生成用户故事草稿和建议标题
2. 展示故事，等待用户确认（**阻塞**，不直接进入 Phase 2）
3. 用户回复"确认"
4. 立即创建 `drafts/报销单批量导出/rdd.md`

**检查要点**
- [ ] Phase 1 输出中展示了用户故事草稿（As a / I want to / So that 格式）
- [ ] 用户确认前，AI **未**自动进入 Phase 2 提问
- [ ] `drafts/报销单批量导出/rdd.md` 文件已创建
- [ ] rdd.md frontmatter `status: story-confirmed`
- [ ] rdd.md frontmatter `phase: 1`
- [ ] rdd.md frontmatter `story-version: 1`
- [ ] rdd.md 中"用户故事（已确认）"小节有实质内容
- [ ] rdd.md 中"节 1 需求摘要"标注"（待 Phase 2 填充）"

---

### TC-INT-02 中断后续接——status=story-confirmed 状态恢复

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证 Phase 1 完成后中断，新对话中续接时跳过 Phase 1，直接进入 Phase 2 |
| **前置条件** | TC-INT-01 已执行，`drafts/报销单批量导出/rdd.md` 存在且 `status: story-confirmed` |

**测试输入**（新对话中）
```
/requirement-clarifier 报销单批量导出
```

**预期行为**
1. AI 读取 `drafts/报销单批量导出/rdd.md`，检测到 `status: story-confirmed`
2. 展示已确认的用户故事摘要
3. 提示"继续 Phase 2 分析"，**不重新执行** Phase 1
4. 直接进入 Phase 2 第一轮澄清问题

**检查要点**
- [ ] AI 输出中引用了已确认的用户故事内容
- [ ] AI **未**重新生成用户故事草稿
- [ ] AI **未**询问"方向是否正确"（已在 Phase 1 确认）
- [ ] AI 进入了 Phase 2 的澄清提问

---

### TC-INT-03 Phase 2 对话触发 permission-model 按需加载

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证 Phase 2 对话中出现权限信号时才加载 permission-model.md，Phase 1 未加载 |
| **前置条件** | TC-INT-01 已执行；`context/permission-model.md` 存在，含角色定义 |

**测试场景**：在 Phase 2 澄清对话中，用户回复：
```
导出功能只有财务专员和财务主管可以用，普通员工无权导出。
```

**预期行为**
1. AI 识别到"权限"/"只有…可以用"信号
2. **此时**读取 `context/permission-model.md`
3. 在后续 RDD 节 2 的"功能模块"或"风险提示"中体现角色权限约束
4. rdd.md frontmatter `context-loaded` 列表追加 `permission-model`

**检查要点**
- [ ] 在用户提到权限**之前**，AI 输出中无权限模型相关内容
- [ ] 用户提到权限**之后**，AI 输出中体现了角色区分（财务专员 vs 财务主管 vs 普通员工）
- [ ] rdd.md 更新后 `context-loaded` 包含 `permission-model`
- [ ] rdd.md `status: rdd-in-progress`

---

## 场景二：new-prd 与 rdd.md 状态协同

### TC-INT-04 new-prd 遇到未完成的 rdd.md 给出提示

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证 new-prd 检测到 rdd.md 状态为 story-confirmed 时，给出提示让用户选择 |
| **前置条件** | `drafts/报销单批量导出/rdd.md` 存在且 `status: story-confirmed`（TC-INT-01 后，未执行 TC-INT-02） |

**测试输入**
```
/new-prd feature 报销单批量导出
```

**预期行为**
1. Step 5-0 读取 rdd.md，检测到 `status: story-confirmed`
2. 输出提示：检测到需求分析尚未完成（当前：story-confirmed）
3. 提供 A（继续）/ B（先去完成分析）选项
4. 等待用户回复，**不自动继续**

**检查要点**
- [ ] 输出中说明了 rdd.md 当前状态（story-confirmed）
- [ ] 提供了 A/B 选项
- [ ] 选项 B 包含 `/requirement-clarifier 报销单批量导出` 命令引导
- [ ] 用户未回复前，AI 未填充 prd.md 内容

---

### TC-INT-05 new-prd 确认移入正式区后 context 同步提议

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证 PRD 移入 prds/ 后，AI 正确提议更新 glossary 和 feature-map |
| **前置条件** | `drafts/报销单批量导出/prd.md` 已存在且内容完整，含 §4 新术语和 §5 新功能节点 |

**测试输入**（接 new-prd 的 A/B 询问）
```
B
```

**预期行为**
1. 执行移入操作
2. 读取 PRD §5，提取新增功能节点
3. 输出建议追加到 `context/product-feature-map.md` 的内容
4. 输出建议追加到 `context/business-glossary.md` 的新术语（如"批量导出任务"）
5. 等待用户确认后写入

**检查要点**
- [ ] 输出中包含"建议追加到 context/product-feature-map.md"
- [ ] 输出中包含"建议追加到 context/business-glossary.md"（若有新术语）
- [ ] 用户确认后，两个 context 文件均有更新
- [ ] 用户未确认时，context 文件**未**被修改

---

## 场景三：sync-docs context 一致性检查

### TC-INT-06 sync-docs 检测 PRD §4 术语未在 glossary 登记

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证 sync-docs 的 context 一致性检查能识别出术语孤岛 |
| **前置条件** | `prds/报销单批量导出/prd.md` 已注册；§4 中包含"批量导出任务"术语；`context/business-glossary.md` 中**未**包含该术语 |

**测试输入**
```
/sync-docs 报销单批量导出
```

**预期行为**
1. 完成文档版本检查（Step 1-4）
2. Step 5a：读取 §4 新引入术语，与 glossary 比对
3. 识别"批量导出任务"未在 glossary 中登记
4. 在报告末尾追加"Context 一致性"小节，列出该术语

**检查要点**
- [ ] 报告中包含"Context 一致性"小节
- [ ] "批量导出任务"出现在术语孤岛列表中
- [ ] 建议操作包含"追加到 context/business-glossary.md"
- [ ] 已在 glossary 中登记的术语**不**出现在孤岛列表

---

### TC-INT-07 sync-docs 检测 PRD §7 前缀未在 feature-map 注册

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证 sync-docs 能识别出功能编号前缀未注册的情况 |
| **前置条件** | `prds/报销单批量导出/prd.md` 已注册；§7 中有编号前缀 `EXP-`；`context/product-feature-map.md` 前缀映射表中**未**包含 `EXP-` |

**测试输入**
```
/sync-docs 报销单批量导出
```

**预期行为**
1. Step 5b：读取 §7 功能清单，提取所有前缀
2. 识别 `EXP-` 未在 feature-map 前缀映射表中
3. 在"Context 一致性"小节中列出未注册前缀

**检查要点**
- [ ] `EXP-` 出现在功能前缀未注册列表中
- [ ] 建议操作包含"追加到 context/product-feature-map.md 前缀映射表"
- [ ] 已注册的前缀**不**出现在未注册列表

---

## 附：context 文件不存在时的降级行为

### TC-INT-08 context 文件均不存在时 sync-docs 跳过一致性检查

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证 business-glossary.md 和 product-feature-map.md 均不存在时，Step 5 静默跳过，不报错 |
| **前置条件** | `prds/报销单批量导出/prd.md` 已注册；`context/business-glossary.md` 和 `context/product-feature-map.md` 均**不存在** |

**测试输入**
```
/sync-docs 报销单批量导出
```

**预期行为**
- 正常完成文档版本检查（Step 1-4）
- Step 5 静默跳过，输出中**不包含**"Context 一致性"小节
- 无报错，无任何关于 context 文件缺失的警告

**检查要点**
- [ ] 输出中不包含"Context 一致性"字样
- [ ] 无报错或警告信息
- [ ] 文档版本检查部分正常输出
