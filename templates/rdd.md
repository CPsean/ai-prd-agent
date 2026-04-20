# RDD 模板（需求定义文档）

> **使用场景**：由 `/requirement-clarifier` 自动生成，保存于 `drafts/[标题]/rdd.md`。
> **用途**：作为 `/new-prd` 的输入源，AI 读取后自动填充 PRD §3 需求概要和 §7 功能清单初稿。
> **不适合直接手动复制**：内容由 AI 在澄清对话结束后根据讨论结果填写。
> **渐进式写入**：Phase 1 完成后创建（status: story-confirmed），Phase 2 逐步填充，完成后更新为 rdd-complete。

---

```yaml
---
status: story-confirmed | rdd-in-progress | rdd-complete
phase: 1 | 2
context-loaded:           # Phase 2 中已按需加载的 context 文件列表
  - user-persona
  - product-background
  - platform-support      # 若 Phase 1 读取
  # Phase 2 按信号追加：permission-model / product-feature-map / business-glossary / product-strategy
story-version: 1          # 用户故事修订次数（Phase 2 中修正方向时 +1）
created: YYYY-MM-DD
---
```

> 修订注记（若 story-version > 1，在此追加）：
> `> [修订 v2] YYYY-MM-DD：[修订原因一句话]`

# RDD：[需求标题]

## 节 1：需求摘要

| 维度 | 内容 |
| --- | --- |
| 业务对象 | [本需求涉及的核心业务实体] |
| 用户角色 | [核心用户 / 次级用户] |
| 使用场景 | [触发本需求的典型场景] |
| 核心动作 | [用户/系统的关键操作] |
| 预期价值 | [对用户/业务的实际收益] |
| 成功指标 | [上线后如何衡量成功] |
| 需求优先级 | P0 / P1 / P2 / P3 |

## 节 2：初步方案

> 总字数 ≤ 400 字，聚焦产品决策，不写技术实现细节。

### 方案边界

- **本版做**：
- **本版不做**：
- **后续规划**：

### 功能模块

| 模块名 | 类型 | 说明 |
| --- | --- | --- |
| | 新增 / 调整 / 复用 | |

### 页面结构

```
[页面/入口名]
├── [子页面/弹窗/抽屉]
└── [子页面/弹窗/抽屉]
```

### 核心流程

- **主流程**：[步骤1] → [步骤2] → [步骤3]
- **异常流程**：[触发条件] → [系统行为]

### 关键设计决策

| 决策点 | 方案 A | 方案 B | 推荐 & 理由 |
| --- | --- | --- | --- |
| | | | |

### 风险提示

- P[编号]：[风险描述]（类型：权限 / 合规 / 平台 / 依赖）
