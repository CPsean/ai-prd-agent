# 集成测试：完整工作流链路

> **测试目标**：验证跨命令的端到端工作流链路，确保命令之间的数据流转、状态协同和提示联动正确。
> **执行说明**：集成测试需按场景内顺序执行，后续用例依赖前置用例的输出。各场景之间可独立执行。
> **覆盖范围**：F-001 ~ F-008 跨命令交互链路

---

## 场景一：需求分析 → PRD 生成 → Context 同步

> 链路：`/requirement-clarifier` → rdd.md → `/new-prd` → 移入正式区 → context 文件同步提议

### TC-INT-01 Phase 1 完成后 rdd.md 正确创建

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **关联模块** | F-001 |
| **测试目标** | 验证 Phase 1 用户故事确认后立即创建 rdd.md，状态和结构正确 |
| **前置条件** | `drafts/报销单批量导出/` 目录不存在 |

**测试输入**
```
/requirement-clarifier 财务人员需要每月将费用报销单批量导出为 Excel，目前只能逐条下载 PDF，非常耗时，导致月末结账时大量等待。
```

**预期行为**
1. AI 完成 X-Y 诊断，生成用户故事草稿和建议标题
2. 展示故事，等待用户确认（**阻塞**，不直接进入 Phase 2）
3. 用户回复"确认"
4. 立即创建 `drafts/报销单批量导出/rdd.md`

**检查要点**
- [ ] Phase 1 输出了 As a / I want to / So that 格式用户故事
- [ ] 用户确认前，AI **未**自动进入 Phase 2
- [ ] `drafts/报销单批量导出/rdd.md` 已创建
- [ ] rdd.md frontmatter `status: story-confirmed`、`phase: 1`、`story-version: 1`
- [ ] rdd.md 中"节 1 需求摘要"标注"（待 Phase 2 填充）"

---

### TC-INT-02 中断后续接——status=story-confirmed 状态恢复

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **关联模块** | F-001 |
| **测试目标** | 验证 Phase 1 完成后中断，新对话中续接时跳过 Phase 1，直接进入 Phase 2 |
| **前置条件** | TC-INT-01 已执行，`drafts/报销单批量导出/rdd.md` 存在且 `status: story-confirmed` |

**测试输入**（新对话中）
```
/requirement-clarifier 报销单批量导出
```

**预期行为**
1. AI 读取 rdd.md，检测到 `status: story-confirmed`
2. 展示已确认的用户故事摘要，**不重新执行** Phase 1
3. 直接进入 Phase 2 第一轮澄清问题

**检查要点**
- [ ] AI 引用了已确认的用户故事内容
- [ ] AI **未**重新生成用户故事草稿或询问"方向是否正确"
- [ ] AI 进入了 Phase 2 的澄清提问

---

### TC-INT-03 Phase 2 对话触发 permission-model 按需加载

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **关联模块** | F-001, F-003 |
| **测试目标** | 验证 Phase 2 对话中出现权限信号时才加载 permission-model.md |
| **前置条件** | TC-INT-02 已进入 Phase 2；`context/permission-model.md` 存在 |

**测试场景**：在 Phase 2 澄清对话中，用户回复：
```
导出功能只有财务专员和财务主管可以用，普通员工无权导出。
```

**预期行为**
1. AI 识别到"权限"/"只有…可以用"信号
2. **此时**读取 `context/permission-model.md`
3. 后续 RDD 内容体现角色权限约束
4. rdd.md frontmatter `context-loaded` 列表追加 `permission-model`

**检查要点**
- [ ] 用户提到权限**之前**，AI 输出中无权限模型相关内容
- [ ] 用户提到权限**之后**，AI 输出中体现了角色区分
- [ ] rdd.md `context-loaded` 包含 `permission-model`
- [ ] rdd.md `status: rdd-in-progress`

---

### TC-INT-04 new-prd 遇到未完成的 rdd.md 给出提示

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **关联模块** | F-001, F-002 |
| **测试目标** | 验证 new-prd 检测到 rdd.md 状态为 story-confirmed 时给出提示 |
| **前置条件** | `drafts/报销单批量导出/rdd.md` 存在且 `status: story-confirmed` |

**测试输入**
```
/new-prd feature 报销单批量导出
```

**预期行为**
1. Step 5-0 读取 rdd.md，检测到 `status: story-confirmed`
2. 输出提示：检测到需求分析尚未完成
3. 提供 A（继续基于现有内容）/ B（先去完成分析）选项
4. **阻塞**等待用户回复

**检查要点**
- [ ] 输出中说明了 rdd.md 当前状态
- [ ] 提供了 A/B 选项
- [ ] 选项 B 包含 `/requirement-clarifier 报销单批量导出` 引导
- [ ] 用户未回复前，AI 未填充 prd.md

---

### TC-INT-05 PRD 移入正式区后 context 同步提议

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **关联模块** | F-002, F-003 |
| **测试目标** | 验证 PRD 移入 prds/ 后，AI 正确提议更新 glossary 和 feature-map |
| **前置条件** | `drafts/报销单批量导出/prd.md` 已存在且内容完整，含 §4 新术语和 §5 新功能节点 |

**测试输入**（new-prd Step 7 询问移入正式区时）
```
B
```

**预期行为**
1. 执行移入操作（drafts/ → prds/，更新 _registry.md）
2. 读取 PRD §5，提议追加新功能节点到 `context/product-feature-map.md`
3. 提议追加新术语到 `context/business-glossary.md`
4. 等待用户确认后才写入

**检查要点**
- [ ] 输出中包含 product-feature-map.md 更新建议
- [ ] 输出中包含 business-glossary.md 更新建议（若有新术语）
- [ ] 用户确认后 context 文件有更新
- [ ] 用户未确认时 context 文件**未**被修改

---

## 场景二：Import Context → 下游命令读取

> 链路：`/import-context` → context 文件写入 → `/new-prd` 或 `/requirement-clarifier` 读取

### TC-INT-06 import-context 写入术语 → new-prd §4 读取避免重复

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **关联模块** | F-003, F-002 |
| **测试目标** | 验证 import-context 写入的术语能被后续 new-prd 读取并避免重复定义 |
| **前置条件** | `context/business-glossary.md` 存在但不含"审批流"术语 |

**测试输入**（分两步执行）

Step 1：
```
/import-context 业务术语：审批流是指报销单从提交到完成的审批路径，包含多级审批节点
→ 确认
```

Step 2：
```
/new-prd feature 报销审批优化
```

**预期行为**
1. Step 1：import-context 将"审批流"追加到 business-glossary.md
2. Step 2：new-prd 写 §4 时读取 glossary，发现"审批流"已定义
3. §4 中引用已有术语定义，不重复定义"审批流"

**检查要点**
- [ ] business-glossary.md 中有"审批流"定义（Step 1 写入）
- [ ] prd.md §4 中引用了已有术语，而非重新定义
- [ ] 仅本 PRD 新引入的术语出现在 §4 定义表中

---

### TC-INT-07 import-context 截图 → generate-prototype 读取视觉风格

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **关联模块** | F-003, F-005 |
| **测试目标** | 验证通过 import-context 导入的截图能被 generate-prototype 读取并提取视觉风格 |
| **前置条件** | 正式区有"报销审批"PRD 和 page-spec.md |

**测试输入**（分两步执行）

Step 1：
```
/import-context （粘贴报销管理模块截图）这是报销管理模块的列表页
→ 确认模块归属和文件名
```

Step 2：
```
/generate-prototype 报销审批
```

**预期行为**
1. Step 1：截图存入 `context/screenshots/报销管理/`
2. Step 2：generate-prototype Step 2 检查截图库，找到对应模块截图
3. 从截图提取视觉风格（色调、字体、间距），应用到原型 CSS
4. 原型未使用默认线框风格

**检查要点**
- [ ] 截图已存入 context/screenshots/报销管理/
- [ ] generate-prototype 输出中提及"基于截图提取视觉风格"
- [ ] 原型 CSS 体现截图中的产品风格
- [ ] 未出现"截图库暂无对应模块截图"提示

---

## 场景三：PRD → 规格卡 → 原型 → 同步检查

> 链路：`/new-prd` → `/generate-page-spec` → `/generate-prototype` → `/sync-docs`

### TC-INT-08 完整交付链路：PRD → 规格卡 → 原型

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **关联模块** | F-002, F-005 |
| **测试目标** | 验证 PRD 移入正式区后，按序生成规格卡和原型的链路畅通 |
| **前置条件** | `prds/报销审批/prd.md` 已注册，PRD 涉及 3 个页面 |

**测试输入**（按序执行）

Step 1：
```
/generate-page-spec 报销审批
```

Step 2（规格卡生成后）：
```
/generate-prototype 报销审批
→ 确认规划清单
```

**预期行为**
1. Step 1：生成 `prds/报销审批/page-spec.md`，包含 3 个页面卡片
2. Step 2：generate-prototype 检测到 page-spec.md 存在，以其为主要输入
3. 输出规划清单后等待确认
4. 确认后生成 `outputs/prototypes/报销审批/` 目录，含 index.html + 各页面 HTML
5. 创建 prototype-meta.md，更新 prd.md 的 has-prototype 字段

**检查要点**
- [ ] page-spec.md 页面数量与 PRD 一致
- [ ] generate-prototype 以 page-spec 为输入（非 PRD）
- [ ] 原型输出在 `outputs/prototypes/报销审批/`
- [ ] prototype-meta.md 中 prd-version 与当前 PRD 版本一致
- [ ] prd.md frontmatter `has-prototype: true`

---

### TC-INT-09 无规格卡时 generate-prototype 阻断

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **关联模块** | F-005 |
| **测试目标** | 验证跳过 generate-page-spec 直接生成原型时被阻断 |
| **前置条件** | `prds/消息通知设置/prd.md` 已注册，无 page-spec.md |

**测试输入**
```
/generate-prototype 消息通知设置
```

**预期行为**
1. 检查 prds/ 和 drafts/ 均无 page-spec.md
2. **阻断执行**，提示先运行 `/generate-page-spec 消息通知设置`
3. **不**回退读取 PRD 继续生成

**检查要点**
- [ ] 未创建任何原型文件
- [ ] 提示包含 `/generate-page-spec` 命令引导
- [ ] 明确说明阻断原因

---

## 场景四：PRD 更新 → 过期提示 → 同步检查

> 链路：`/update-prd` → 原型过期提示 + sync-docs 提示 → `/sync-docs` 检测差异

### TC-INT-10 update-prd 后触发原型过期和 sync-docs 提示

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **关联模块** | F-005, F-006 |
| **测试目标** | 验证 PRD 更新后，输出末尾同时追加原型过期提示和 sync-docs 提示 |
| **前置条件** | `prds/报销审批/prd.md` 已注册（v1.0），`prds/报销审批/page-spec.md` 存在，`outputs/prototypes/报销审批/prototype-meta.md` 存在（prd-version: 1.0） |

**测试输入**
```
/update-prd 报销审批 新增批量操作页面
```

**预期行为**
1. update-prd 正常执行（归档 v1.0 → 更新内容 → 版本升至 v1.1）
2. Step 7.5 检测到 page-spec.md 存在 → 追加 sync-docs 提示
3. Step 7.5 检测到 prototype-meta.md 存在且 prd-version=1.0 < 新版本 1.1 → 追加 ⚠️ 原型过期提示
4. 两个提示均为非阻断

**检查要点**
- [ ] update-prd 主流程正常完成
- [ ] 输出末尾有"建议运行 `/sync-docs 报销审批`"提示
- [ ] 输出末尾有 ⚠️ 原型过期提示，含版本号对比（1.0 → 1.1）
- [ ] 两个提示未阻断主流程

---

### TC-INT-11 sync-docs 检测 update-prd 后的文档差异

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **关联模块** | F-006 |
| **测试目标** | 验证 update-prd 新增页面后，sync-docs 能检测到 PRD↔规格卡差异 |
| **前置条件** | TC-INT-10 已执行；PRD v1.1 包含"批量操作页"，page-spec.md 仍为 v1.0（只有 2 个页面） |

**测试输入**
```
/sync-docs 报销审批
```

**预期行为**
1. Step 1：输出文档清单（PRD ✅ / 规格卡 ✅ / 原型 ✅）
2. Step 2 PRD↔规格卡对比：发现 PRD 有"批量操作页"但规格卡无对应卡片
3. 标注为"确定差异"
4. Step 3 飞轮检测正常执行
5. 输出两块报告格式

**检查要点**
- [ ] 报告块一检测到页面数量差异（确定差异）
- [ ] 差异描述含"批量操作页"
- [ ] 建议操作包含 `/generate-page-spec`
- [ ] 报告包含块二（飞轮待处理项）
- [ ] 报告格式符合两块结构

---

## 场景五：飞轮闭环

> 链路：`/requirement-clarifier` 提议术语 → pending-flywheel.md → `/sync-docs` 展示待处理项

### TC-INT-12 飞轮提议 → sync-docs 展示未处理项

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **关联模块** | F-001, F-006 |
| **测试目标** | 验证 requirement-clarifier 产生的飞轮提议能在 sync-docs 中展示 |
| **前置条件** | `context/pending-flywheel.md` 存在，含 1 条未处理提议（来源：/requirement-clarifier） |

**测试输入**
```
/sync-docs [任意已注册标题]
```

**预期行为**
1. 块一正常执行文档对比
2. 块二读取 pending-flywheel.md，列出未处理提议
3. 每项包含：提议内容、来源命令、提议日期
4. 输出处理方式提示

**检查要点**
- [ ] 块二列出了未处理提议
- [ ] 来源标注为 `/requirement-clarifier`
- [ ] 提供了"确认写入"或"跳过"的处理方式
- [ ] 飞轮检测未影响块一的正常输出

---

## 场景六：知识库提问四层检索链路

> 链路：`/prd-qa` 依次检索 context/ → prds/ → drafts/

### TC-INT-13 prd-qa 跨层检索：context 未命中 → 正式区命中

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **关联模块** | F-007 |
| **测试目标** | 验证第一层 context 未命中时正确回退到第二/三层正式区 PRD |
| **前置条件** | `context/` 中无"批量导出"相关内容；`prds/报销单批量导出/prd.md` 存在且 §8 包含导出规则 |

**测试输入**
```
/prd-qa 报销单批量导出的导出格式有哪些？
```

**预期行为**
1. 第一层 context/ 检索 → 未命中
2. 第二层 _registry.md → 定位到"报销单批量导出"PRD
3. 第三层读取 prd.md，找到导出格式说明
4. 输出答案 + 正式区来源标注

**检查要点**
- [ ] 答案来自 prds/报销单批量导出/prd.md（非 context/）
- [ ] 来源标注格式：`> 来源：prds/报销单批量导出/prd.md §[章节]`
- [ ] 无草稿区警告（正式区已命中）

---

### TC-INT-14 prd-qa 跨层检索：正式区未命中 → 草稿区兜底

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **关联模块** | F-007 |
| **测试目标** | 验证前三层未命中时回退到草稿区，输出带 ⚠️ 警告的答案 |
| **前置条件** | `prds/` 中无"用户登录优化"PRD；`drafts/用户登录优化/prd.md` 存在且有验收标准 |

**测试输入**
```
/prd-qa 用户登录优化的验收标准是什么？
```

**预期行为**
1. context/ 未命中 → _registry.md 未命中 → drafts/ 命中
2. 输出答案 + ⚠️ 草稿警告
3. 来源标注：`> ⚠️ 来源：drafts/用户登录优化/prd.md（草稿文档，未正式发布）`

**检查要点**
- [ ] 正确回退到草稿区检索
- [ ] 输出了 ⚠️ 草稿警告
- [ ] 答案内容来自草稿区 prd.md

---

## 场景七：路由 → 纠错 → 文件清理

> 链路：意图路由 → 命令执行 → 纠错信号 → 终止 + 文件清理 → 重新路由

### TC-INT-15 路由纠错全链路：有文件 → 询问删除 → 重新路由

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **关联模块** | F-004 |
| **测试目标** | 验证路由纠错完整流程：终止 → 文件询问 → 重新识别 |
| **前置条件** | 无特殊前置条件 |

**测试输入**（多轮对话）
```
Round 1 - PM: 帮我起草一个需求
Round 1 - AI: [进入 requirement-clarifier，创建了 drafts/xxx/rdd.md]
Round 2 - PM: 不对，我是要直接写 PRD
Round 2 - AI: [询问是否删除 rdd.md]
Round 3 - PM: 删除吧
```

**预期行为**
1. Round 2：AI 识别纠错信号，终止当前命令
2. Round 2：检测到已产生 rdd.md，询问是否删除（列出路径）
3. Round 3：PM 确认后删除文件
4. Round 3：重新识别"直接写 PRD" → 进入 /new-prd 流程

**检查要点**
- [ ] 纠错后立即终止 requirement-clarifier
- [ ] 列出了已产生文件的具体路径
- [ ] PM 确认前未删除文件
- [ ] 删除后正确进入 /new-prd 流程

---

## 场景八：技能创建 → 质检 → 激活 → 管理

> 链路：创建技能 → 三级质检 → PM 确认激活 → 查看/禁用

### TC-INT-16 技能创建全链路：引导 → 质检通过 → 激活 → 列表可见

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **关联模块** | F-008 |
| **测试目标** | 验证技能创建到激活的完整链路，激活后在技能列表中可见 |
| **前置条件** | `.claude/skills/` 中无 `competitive-analysis` 目录 |

**测试输入**（多轮对话）
```
Round 1 - PM: 帮我创建一个竞品分析的技能
Round 2 - PM: [提供 name/description/执行步骤]
Round 3 - PM: [质检报告展示后] 确认激活
Round 4 - PM: 查看现有技能
```

**预期行为**
1. Round 1-2：AI 引导创建，生成候选 SKILL.md
2. Round 2-3：自动执行三级质检，输出报告（Level 1/2/3 分块）
3. Round 3：PM 确认后写入 `.claude/skills/competitive-analysis/SKILL.md`
4. Round 4：技能列表中包含 competitive-analysis（名称 + 描述 + 启用状态）

**检查要点**
- [ ] 质检报告按 Level 1/2/3 分块展示
- [ ] 激活前文件未写入 `.claude/skills/`
- [ ] 激活后 `.claude/skills/competitive-analysis/SKILL.md` 存在
- [ ] "查看现有技能"列表中包含新激活的技能

---

## 场景九：Context 一致性检查

> 链路：PRD §4/§7 内容 vs context/ 文件 → `/sync-docs` 检测孤岛

### TC-INT-17 sync-docs 检测术语孤岛

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **关联模块** | F-006 |
| **测试目标** | 验证 sync-docs Step 2.5 能识别 PRD §4 中未在 glossary 登记的术语 |
| **前置条件** | `prds/报销单批量导出/prd.md` §4 包含"批量导出任务"术语；`context/business-glossary.md` 中**未**包含该术语 |

**测试输入**
```
/sync-docs 报销单批量导出
```

**预期行为**
1. Step 2.5 术语孤岛检查：读取 §4 术语，与 glossary 比对
2. 识别"批量导出任务"未登记
3. 报告块一包含"Context 一致性"小节

**检查要点**
- [ ] 报告包含"Context 一致性"小节
- [ ] "批量导出任务"出现在术语孤岛列表
- [ ] 已在 glossary 中定义的术语**不**误报
- [ ] 建议追加到 business-glossary.md

---

### TC-INT-18 sync-docs 检测功能前缀未注册

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **关联模块** | F-006 |
| **测试目标** | 验证 sync-docs Step 2.5 能识别 §7 中未注册的功能编号前缀 |
| **前置条件** | `prds/报销单批量导出/prd.md` §7 有前缀 `EXP-`；`context/product-feature-map.md` 未注册 `EXP` |

**测试输入**
```
/sync-docs 报销单批量导出
```

**预期行为**
1. Step 2.5 功能前缀检查：提取 §7 编号前缀，与映射表比对
2. 识别 `EXP` 未注册

**检查要点**
- [ ] `EXP` 出现在未注册前缀列表
- [ ] 已注册前缀**不**误报
- [ ] 建议追加到 product-feature-map.md 前缀映射表

---

### TC-INT-19 context 文件均不存在时 sync-docs 静默跳过

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **关联模块** | F-006 |
| **测试目标** | 验证 glossary 和 feature-map 均不存在时 Step 2.5 静默跳过 |
| **前置条件** | `context/business-glossary.md` 和 `context/product-feature-map.md` 均**不存在** |

**测试输入**
```
/sync-docs [任意已注册标题]
```

**预期行为**
- 正常完成文档对比和飞轮检测
- 输出中**不包含**"Context 一致性"小节
- 无报错

**检查要点**
- [ ] 输出不包含"Context 一致性"字样
- [ ] 无报错或警告
- [ ] 两块报告结构正常输出

---

### TC-INT-20 端到端：requirement-clarifier → new-prd → 移入正式区全链路（含文件夹命名和草稿清理）

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **关联模块** | F-009（PRD-GEN-008 + PRD-GEN-009 + PRD-MIG-004） |
| **测试目标** | 验证从需求澄清到 PRD 正式化的完整链路：rdd.md 创建 → new-prd 重命名目录并预注册 → 移入正式区后 drafts/ 完全清理 |
| **前置条件** | `prds/_registry.md` 存在，`drafts/` 中无同名目录 |

**测试步骤**

**步骤 1：执行需求澄清**
```
/requirement-clarifier 测试端到端功能

需求描述：用户希望在列表页支持按多个条件组合筛选，目前只能单条件筛选。
```
- 完成 Phase 1（确认用户故事）和 Phase 2（多轮澄清至收敛）
- 验证 `drafts/[标题]/rdd.md` 已创建（旧格式，无 ID 前缀）

**步骤 2：执行新建 PRD**
```
/new-prd feature [标题]
```
（使用步骤 1 确认的标题）

**步骤 2 检查要点**
- [ ] AI 检测到 `drafts/[标题]/rdd.md` 存在，无冲突阻断
- [ ] 目录被重命名为 `drafts/[ID]-[标题]/`（含 ID 前缀）
- [ ] `drafts/[ID]-[标题]/rdd.md` 存在且内容与重命名前一致
- [ ] `drafts/[ID]-[标题]/prd.md` 正常创建，内容基于 rdd.md 填充
- [ ] `drafts/_draft-registry.md` 中有对应 ID 条目（状态 in-draft）
- [ ] AI 读取 rdd.md 用于填充 PRD（步骤 5-0 正常执行）

**步骤 3：确认移入正式区**
```
B
```
（选择移入正式区）

**步骤 3 检查要点**
- [ ] `prds/[ID]-[标题]/` 目录存在
- [ ] `prds/[ID]-[标题]/prd.md` 存在
- [ ] `prds/[ID]-[标题]/rdd.md` 存在（随目录一并移动）
- [ ] `prds/[ID]-[标题]/CHANGELOG.md` 存在
- [ ] `drafts/[ID]-[标题]/` **不存在**（已清理）
- [ ] `drafts/[标题]/` **不存在**（旧格式目录也不存在）
- [ ] `drafts/_draft-registry.md` 中无对应 ID 条目（已删除）
- [ ] `prds/_registry.md` 新行路径为 `prds/[ID]-[标题]/prd.md`（含 ID 前缀）
- [ ] AI 输出包含"草稿目录已清理"或同义表述

---

## 场景十：需求池飞轮闭环

> 链路：`/new-prd` 移入正式区 → 扫描 TODO/OQ → 提议入池 → `/update-prd` 增量扫描 → RDD 状态变化 → 条目状态更新

### TC-INT-21 new-prd 移入正式区后自动扫描 TODO/OQ 提议入池

| 字段 | 内容 |
|------|------|
| **��态** | — |
| **关联模块** | F-011（BKL-FLY-001） |
| **测试目标** | 验证 PRD 移入正式区后，Agent 自动扫描 §12 和正文 TODO，提议入池 |
| **前置条件** | `backlog/requirement-pool.md` 已存在；PRD 草稿存在且 §12 有 2 条开放问题 |

**测试步骤**

**步骤 1：创建 PRD 并移入正式区**
```
/new-prd feature [标题]
→ 完成草稿填充
→ 选择 B 移入正式区
```

**预期行为**
1. 移入正式区后，Agent 读取新 PRD 的 §12 和正文
2. 发现 2 条开放问题和若干 TODO
3. 在 context 同步提议之后，追加需求池同步提议块
4. 逐条列出，等待 PM 确认

**检查要点**
- [ ] 移入正式区后输出中包含需求池同步提议
- [ ] 提议中列出了 §12 的开放问题
- [ ] PM 确认后条目写入 `backlog/requirement-pool.md` 对应章节
- [ ] PM 拒绝时不写入
- [ ] 无 TODO/OQ 时不输出提议（静默跳过）

---

### TC-INT-22 update-prd 后扫描增量 TODO/OQ 入池

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **关联模块** | F-011（BKL-FLY-002） |
| **测试目标** | 验证 /update-prd 完成后，Agent 扫描新增的行动项/开放问题并提议入池 |
| **前置条件** | `prds/[标题]/prd.md` 已注册；`backlog/requirement-pool.md` 已存在；PRD 当前 §12 有 1 条已确认的开放问题 |

**测试输入**
```
/update-prd [标题] 新增异步处理模块，§12 补充关于消息队列选型的开放问题
```

**预期行为**
1. update-prd 正常执行（归档 → 更新 → 版本升级）
2. Agent 对比更新前后内容，识别新增的开放问题
3. 与需求池比对，过滤已存在条目
4. 输出增量入池提议

**检查要点**
- [ ] update-prd 主流程正常完成
- [ ] 输出末尾包含需求池增量入池提议
- [ ] 仅新增的 TODO/OQ 出现在提议中（已有的不重复提议）
- [ ] PM 确认后写入对应章节

---

### TC-INT-23 RDD/PRD 状态变化 → Agent 提议更新需求池条目状态

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **关联模块** | F-011（BKL-FLY-003） |
| **测试目标** | 验证关联 RDD 完成时，Agent 提议更新需求池条目状态 |
| **前置条件** | `backlog/requirement-pool.md` 中有 REQ-005，状态「待澄清」，标题与下述 RDD 标题匹配 |

**测试步骤**

**步骤 1：完成需求澄清**
```
/requirement-clarifier [REQ-005 对应的标题]
→ 完成 Phase 1 和 Phase 2，rdd.md 状态变为 rdd-complete
```

**预期行为**
1. RDD 保存后，Agent 检查需求池中是否有关联条目
2. 发现 REQ-005 标题匹配
3. 提议将 REQ-005 状态从「待澄清」更新为「RDD中」
4. PM 确认后写入

**检查要点**
- [ ] Agent 在 RDD 完成后输出状态更新提议
- [ ] 提议中包含条目 ID（REQ-005）和新旧状态
- [ ] PM 确认后 `backlog/requirement-pool.md` 中 REQ-005 状态更新
- [ ] 无关联条目时静默跳过
