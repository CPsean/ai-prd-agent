# PRD 索引

> **AI 读取指南**：这是所有 PRD 的导航入口。
> 回答关于任何需求的问题前，先查此文件确定路径，再读取对应 `prd.md`。
> 只读 `prd.md`，不读 `archive/` 下的历史文件。

---

## 活跃 PRD

| ID | 标题 | 类型 | 状态 | 路径 | 最后更新 |
|----|------|------|------|------|----------|
| F-001 | 指定个人签名印章的模板章以及手绘签名颜色 | feature-prd | released | prds/F-001-印章颜色偏好配置/prd.md | 2026-04-05 |
| F-002 | 骑缝章签署区能力覆盖国际站 | feature-prd | released | prds/F-002-骑缝章国际站适配/prd.md | 2026-04-06 |
| F-003 | 租户级流程中下载权限控制 | feature-prd | released | prds/F-003-流程下载权限控制/prd.md | 2026-04-06 |
| F-004 | 转交信封用户重定向逻辑补充 | feature-prd | released | prds/F-004-转交后重定向逻辑/prd.md | 2026-04-06 |
| F-005 | 跨企业印章授权 | feature-prd | in-review | prds/F-005-跨企业印章授权/prd.md | 2026-04-06 | 排期0416迭代，上线后补需求ID |
| F-006 | 接入产品规格，支持在签署页展示AI助理和合同比对入口 | feature-prd | released | prds/F-006-签署页AI助理合同比对入口/prd.md | 2026-04-06 |
| F-007 | 支持 SingPass 原文签署 TSP 能力 | feature-prd | in-review | prds/F-007-SingPass原文签署TSP/prd.md | 2026-04-06 | 需求15863，方案预研阶段 |
| F-008 | 发起时可指定印章ID发起 | feature-prd | in-review | prds/F-008-发起时指定印章ID/prd.md | 2026-04-06 | 0402迭代，需求ID未匹配；依赖F-005；天印暂不接入 |
| F-009 | 签署页引导步骤条文案规范 | feature-prd | released | prds/F-009-签署页引导步骤条文案规范/prd.md | 2026-04-07 | 需求15191；填签一体页；PC+H5双端文案规则 |
| F-010 | 签署页文档标签状态规范 | feature-prd | in-review | prds/F-010-签署页文档标签状态规范/prd.md | 2026-04-07 | V2=需求15013已上线；V3=0416迭代需求ID待补；国际站不含未读/已读 |

---

## 归档 PRD

| ID | 标题 | 归档日期 | 归档原因 |
|----|------|----------|----------|
| — | — | — | — |

---

## ID 命名规则

| 前缀 | 类型 | 示例 |
|------|------|------|
| `SC-` | 用户故事卡（Story Card） | SC-001 |
| `F-` | 功能 PRD（Feature PRD） | F-001 |
| `E-` | 史诗 PRD（Epic PRD） | E-001 |

---

## 状态说明

| 状态 | 含义 |
|------|------|
| `draft` | 起草中，未经评审 |
| `in-review` | 评审中，可能有变更 |
| `approved` | 已审批，进入开发 |
| `released` | 已上线 |
| `archived` | 已归档，不再维护 |

---

## 维护说明

- 新建 PRD：运行 `/new-prd [story-card|feature|epic] [标题]`，AI 自动更新此表格
- 归档 PRD：将文件夹移至 `archive/`，并在归档表格登记
- 禁止直接编辑 `archive/` 下的历史文件
