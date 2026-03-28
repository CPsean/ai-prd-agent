---
name: requirement-clarifier
description: 用JTBD（Jobs-to-be-Done）框架分析原始需求，识别X-Y问题，生成结构化RDD需求定义卡片
tags: [requirement, jtbd, prd, phase-1]
---

## 触发条件（When）
- 用户提出新功能、想法或解决方案，但底层问题或业务价值不清晰时
- Phase 1 需求发现阶段

## 不适用场景（Do NOT use）
- 用户要求直接生成代码、修复Bug、技术架构设计（已有经过验证的PRD时）
- 没有具体需求，正在做用户研究或客户发现 → 改用 `jobs-to-be-done` skill
- 需求已澄清，需要输出开发可交付的正式用户故事（含 Gherkin 验收标准）→ 改用 `/write-user-story`

## 输入
- `raw_requirement`：用户提出的初始功能请求或解决方案

## 执行逻辑

1. **X-Y问题分析**：评估 `raw_requirement` 描述的是"解决方案(Y)"还是"问题(X)"
2. **JTBD追问**（递进式）：如果真实问题被隐藏，��于JTBD框架提1-2个高价值问题，等待用户回应
3. **价值回路验证**：确认成功衡量方式（指标/验证方法），缺失时主动建议
4. **生成RDD**：核心问题明确后，输出最终RDD卡片

## 输出结构（RDD卡片）

```markdown
# 📋 RDD（需求定义文档）

- **⚠️ 核心洞察（X vs Y）**：[初始请求 vs 真实问题]
- **🎯 JTBD / 用户故事**：作为 [角色]，我希望 [行为]，以便 [价值]。
- **✅ 验收标准**：
    1. [标准1]
    2. [标准2]
- **🚀 MVP方案**：[最轻量的验证解法]
- **📈 成功指标**：[上线后如何衡量成功]
```

## 对应斜杠命令

调用方式：`/requirement-clarifier [需求描述]`

命令文件：`.claude/commands/requirement-clarifier.md`
