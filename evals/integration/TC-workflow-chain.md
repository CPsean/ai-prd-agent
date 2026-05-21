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
| **Codex 状态** | — |
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
| **Codex 状态** | — |
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
| **Codex 状态** | — |
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
| **Codex 状态** | — |
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
| **Codex 状态** | — |
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
| **Codex 状态** | — |
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
| **Codex 状态** | — |
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
| **Codex 状态** | — |
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
| **Codex 状态** | — |
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
| **Codex 状态** | — |
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
| **Codex 状态** | — |
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
| **Codex 状态** | — |
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
| **Codex 状态** | — |
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
| **Codex 状态** | — |
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
| **Codex 状态** | — |
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
| **Codex 状态** | — |
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
| **Codex 状态** | — |
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
| **Codex 状态** | — |
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
| **Codex 状态** | — |
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
| **Codex 状态** | — |
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
| **Codex 状态** | — |
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
| **Codex 状态** | — |
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

---

## 场景十一：prd-qa 自然语言触发 → 问题收敛 → 检索回答全链路

> 链路：自然语言触发（无具体问题）→ 输出引导语 → 用户给出问题 → 清晰度收敛 → 四层检索 → 强制来源标注 → 启发式追问引导

### TC-INT-24 prd-qa 自然语言触发 → 引导 → 检索 → 来源标注 → 追问建议

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **Codex 状态** | — |
| **关联模块** | F-013（KQA-RTG-001 + KQA-QRY-004 + KQA-ANS-002 + KQA-GDE-001） |
| **测试目标** | 验证从自然语言模糊触发到有来源标注的完整回答链路，含引导等待、清晰度收敛和追问引导 |
| **前置条件** | `prds/_registry.md` 存在且有至少一个已注册功能 PRD；对应 `prd.md` 有实质内容 |

**测试步骤**

**步骤 1：自然语言触发（无具体问题）**
```
Round 1 - 用户: 我想问几个产品问题
```

**步骤 1 预期行为**
- 输出引导语：「我会基于产品上下文和 PRD 帮你检索，请说出你的问题。」
- 不进入检索，不输出任何 PRD 内容，等待用户说出具体问题

**步骤 1 检查要点**
- [ ] 输出了引导语（含"请说出你的问题"或同义表述）
- [ ] 未提前触发清晰度收敛或检索
- [ ] 未输出任何来源标注或 PRD 内容

**步骤 2：用户给出无锚点的模糊问题**
```
Round 2 - 用户: 这个功能的权限是怎么规定的？
```

**步骤 2 预期行为**
- 识别无可检索锚点（无功能名/PRD ID/角色名）
- 输出一句话追问：询问具体功能名或 PRD ID
- 不进入检索

**步骤 2 检查要点**
- [ ] 输出了一句话追问（不超过 1 句）
- [ ] 追问中要求用户提供锚点（功能名 / PRD ID / 字段名等）
- [ ] 未进入检索，未输出来源标注

**步骤 3：用户补充锚点，触发检索**
```
Round 3 - 用户: 是 F-007 知识库提问这个功能的
```

**步骤 3 预期行为**
1. 锚点明确（F-007 + 功能名），进入四层检索
2. 读取 `prds/_registry.md` 定位 F-007 路径
3. 读取 `prds/F-007-知识库提问/prd.md` 权限相关章节
4. 生成自然语言回答 + 强制来源标注
5. 回答末尾追加 2-3 条完整问句的追问建议（范围限 F-007 PRD 内）

**步骤 3 检查要点**
- [ ] 进入检索并命中 F-007 权限相关章节
- [ ] 输出了来源标注（格式：`> 来源：prds/F-007-知识库提问/prd.md §[章节编号] [章节名]`）
- [ ] 未输出 ⚠️ 草稿警告（F-007 在正式区）
- [ ] 回答末尾包含「**你可能还想问：**」追问建议块
- [ ] 追问建议为完整可读句，不少于 2 条
- [ ] 追问建议范围限定在 F-007 同一 PRD 内（不跨 PRD）

---

## 场景十二：OpenAPI 文档集成飞轮链路

> 链路：PRD §8.10 填写 → `/update-prd` → 飞轮提议 `/update-openapi` → 执行同步 → `/export-openapi` 带版本号 → 生成快照 + 更新 latest

### TC-WF-OA-01 PRD §8.10 变更 → 飞轮提议 → 同步 → 导出带版本号快照

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **Codex 状态** | — |
| **关联模块** | F-014（OAPI-FLY-001, OAPI-UPD-001, OAPI-EXP-001） |
| **测试目标** | 验证从 PRD 接口变更到 OpenAPI 规范同步再到对外版本导出的完整链路 |
| **前置条件** | `prds/F-014-OpenAPI文档集成/prd.md` 在正式区；`openapi/order-api.yaml` 存在（含 changelog 头部，F-014 V1.0 已同步）；`context/api-registry.md` 存在，含"订单管理"模块下的 order-api；`_hidden-interfaces.md` 含 1 条接口级隐藏 |

**测试步骤**（按序执行，后续步骤依赖前置输出）

**步骤 1：update-prd 触发飞轮**
```
/update-prd F-014-OpenAPI文档集成 §8.10 补充新增 /v1/orders/summary（GET）接口的响应字段说明
```

**步骤 1 预期行为**
1. update-prd 正常完成（归档 V1.0 → 更新内容 → 版本升至 V1.1）
2. 飞轮 OAPI-FLY-001 触发：扫描 §8.10，检测到有实质内容
3. 检查 api-registry.md，找到关联 API（order-api）
4. 输出同步提议，含变更摘要（接口路径 + 变更类型）
5. 提示运行 `/update-openapi order-api`，可回复"跳过"

**步骤 1 检查要点**
- [ ] update-prd 主流程正常完成（版本号递增、changelog 写入）
- [ ] 输出末尾有 OpenAPI 同步提议，含具体接口路径
- [ ] 提议为非阻断（提供"跳过"选项）
- [ ] PRD 在草稿区时不触发此提议（已由 TC-OA-05 覆盖，此处验证正式区触发）

**步骤 2：执行 update-openapi 增量同步**
```
/update-openapi order-api
```

**步骤 2 预期行为**
1. 读取 yaml 头部 changelog，确认 F-014 V1.0 已同步
2. 读取 PRD §8.10，筛选 V1.1 的未同步条目（新增 /v1/orders/summary）
3. 生成增量 diff 摘要，展示等待确认
4. 确认后执行增量修改，追加 V1.1 changelog 条目

**步骤 2 检查要点**
- [ ] diff 摘要仅包含 V1.1 未同步变更（不重复显示 V1.0 内容）
- [ ] changelog 条目正确追加（格式：`# 日期 | F-014 | V1.1 | 变更摘要`）
- [ ] yaml 文件已更新，包含新增 endpoint

**步骤 3：export-openapi 带版本号导出**
```
/export-openapi order-api 1.1.0
```

**步骤 3 预期行为**
1. 读取内部完整版 yaml + `_hidden-interfaces.md`（1 条接口级隐藏）
2. 第一阶段：移除接口级隐藏 endpoint
3. 第二阶段：检查参数级隐藏（本次无参数级隐藏，跳过）
4. 执行敏感内容扫描（无命中）
5. 展示过滤摘要（接口级过滤 1 条，参数级过滤 0 处）
6. PM 确认后写入快照文件和 latest 文件

**步骤 3 检查要点**
- [ ] 写入 `outputs/openapi/order-api-public-v1.1.0.yaml`（版本号快照）
- [ ] 写入或更新 `outputs/openapi/order-api-public.yaml`（latest 文件）
- [ ] 对外版不含接口级隐藏 endpoint
- [ ] 内部版 `openapi/order-api.yaml` 未被修改
- [ ] 过滤摘要分列两类（接口级 / 参数级），各自列出数量

---

## 场景十三：截图导入 → 导航图建立 → 下游命令读取（F-015）

> 链路：`/import-context`（截图）→ 导航图写入 → `/prd-qa` 读取 → `/update-prd` 飞轮提议 → `/generate-prototype` 覆盖检查

### TC-INT-25 截图导入全链路：父页面收集 → 写入导航图 → prd-qa 读取

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **Codex 状态** | — |
| **关联模块** | F-015（CTX-IMP-004~008, CTX-NAV-001~005） |
| **测试目标** | 验证截图导入时的父页面收集流程，以及写入后 prd-qa 能准确读取导航关系 |
| **前置条件** | `context/page-navigation.md` 存在含「首页」；`context/screenshots/发起流程/navigation.md` 存在含「发起页」；`backlog/` 存在 |

**测试步骤**（按序执行）

**步骤 1：表达导入截图意图**
```
我要导入一张截图
```

**步骤 1 检查要点**
- [ ] AI 输出 assets 目录整理建议，含路径格式 `assets/[功能名]/`
- [ ] 建议为非阻断，可继续

**步骤 2：粘贴截图，完成父页面 + 触发方式填写**
```
（粘贴截图）这是文件上传页，属于发起流程
→ 选择父页面：发起页
→ 触发方式：点击上传按钮
→ 确认写入
```

**步骤 2 检查要点**
- [ ] 展示了已有节点列表，含 Other 选项
- [ ] AI 询问了触发方式
- [ ] 写入预览包含正确的方形节点格式 `[文件上传页\n文件上传页.png]`
- [ ] 确认后 `context/screenshots/发起流程/navigation.md` 更新，含新节点和连边
- [ ] AI 询问是否删除 assets 中的原始文件（若来源为 assets）

**步骤 3：prd-qa 读取导航关系**
```
/prd-qa 从发起页可以跳转到哪些页面？
```

**步骤 3 检查要点**
- [ ] 输出「可跳转至：文件上传页（点击上传按钮）」
- [ ] 标注来源文件路径（context/screenshots/发起流程/navigation.md）
- [ ] 答案区分页面和弹窗

---

### TC-INT-26 update-prd 含新页面 → 飞轮提议补录导航

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **Codex 状态** | — |
| **关联模块** | F-015（CTX-FLY-005） |
| **测试目标** | 验证 /update-prd 完成后，若 §8 含未录入导航图的新页面，在输出末尾追加补录建议 |
| **前置条件** | `prds/发起流程/prd.md` 在正式区；导航图中无「签署结果页」 |

**测试输入**
```
/update-prd 发起流程 新增签署结果页，展示签署完成状态和证书信息
```

**预期行为**
1. update-prd 正常完成
2. AI 扫描 §8，识别「签署结果页」未在导航图中
3. 输出末尾追加：「检测到新页面 签署结果页 尚未录入导航图，建议通过 /import-context 补录」

**检查要点**
- [ ] update-prd 主流程正常完成
- [ ] 输出末尾有导航图补录建议
- [ ] 建议包含页面名和 /import-context 引导
- [ ] 已在导航图中的页面不重复提议

---

### TC-INT-27 generate-prototype 完成 → 导航节点覆盖检查

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **Codex 状态** | — |
| **关联模块** | F-015（CTX-FLY-006） |
| **测试目标** | 验证 /generate-prototype 完成后，对比原型页面与导航图节点，有缺口时列出 |
| **前置条件** | 原型含「发起页」「文件上传页」「签署结果页」；导航图含前两页，无「签署结果页」 |

**测试输入**
```
/generate-prototype 发起流程
→ 确认
```

**预期行为**
1. 原型生成完成
2. AI 对比原型页面列表（3 页）与导航图（2 节点）
3. 输出末尾追加缺口提示：「签署结果页 尚未在导航图中录入，建议通过 /import-context 导入对应截图」
4. 无缺口时静默

**检查要点**
- [ ] 原型生成正常完成
- [ ] 输出末尾包含缺口页面列表
- [ ] 提示包含 /import-context 引导
- [ ] 导航图中已有的页面不出现在缺口列表
