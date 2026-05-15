# 测试用例：/import-openapi /update-openapi /export-openapi 命令

> 关联命令：`.claude/commands/import-openapi.md`、`.claude/commands/update-openapi.md`、`.claude/commands/export-openapi.md`
> 关联 PRD：`prds/F-014-OpenAPI文档集成/prd.md`
> 前置条件：`prds/_registry.md` 存在且已初始化，工作区存在正式区 PRD `prds/F-014-OpenAPI文档集成/prd.md`

---

## TC-OA-01 首次 /import-openapi——目录结构初始化

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证首次运行时自动创建 openapi/ 目录结构（OAPI-STOR-001） |
| **前置条件** | `openapi/` 目录不存在；`context/api-registry.md` 不存在；PRD `F-014-OpenAPI文档集成` 已在正式区 |

**测试输入**
```
/import-openapi OpenAPI文档集成
```

**预期行为**
1. AI 检测 `openapi/` 不存在，执行初始化
2. 创建 `openapi/` 目录
3. 创建 `openapi/_hidden-interfaces.md`（含接口级 + 参数级双节模板说明）
4. 创建 `context/api-registry.md`（含按模块分组的表头）
5. 创建 `outputs/openapi/` 目录（含 .gitkeep）
6. 输出"OpenAPI 目录结构已初始化"，列出创建的文件路径
7. 继续询问来源（已有文件 or 从 PRD §8.10 生成）

**检查要点**
- [ ] `openapi/` 目录已创建
- [ ] `openapi/_hidden-interfaces.md` 存在，含"接口级隐藏"和"参数级隐藏"两个二级标题
- [ ] `context/api-registry.md` 存在，含正确表头和按模块分组说明
- [ ] `outputs/openapi/` 目录已创建
- [ ] 初始化完成后继续引导 PM 选择来源，不中断流程

---

## TC-OA-02 从已有 yaml 文件导入——解析确认写入

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证从已有规范文件导入的完整路径（OAPI-IMP-001 Path A，对应 AC-1） |
| **前置条件** | `openapi/` 目录已存在；`openapi/order-api.yaml` 不存在；PRD 在正式区 |

**测试输入**
```
/import-openapi order-api
（选择"导入已有文件"）
（粘贴 yaml 内容或提供路径）
```

**预期行为**
1. AI 询问 PM：从已有文件导入，还是从 PRD §8.10 生成
2. PM 选择"已有文件"后，提示提供文件路径或粘贴内容
3. AI 解析内容，展示接口清单摘要（endpoint 列表）
4. 等待 PM 确认
5. PM 确认后写入 `openapi/order-api.yaml`
6. 提议更新 `context/api-registry.md`，询问归属模块

**检查要点**
- [ ] 写入前必须展示接口清单摘要（非直接写入）
- [ ] 须等待 PM 明确确认后才写入文件
- [ ] 写入后提议更新 api-registry.md，询问归属模块
- [ ] 不自动覆盖已有同名文件（若存在则提示冲突）

---

## TC-OA-03 从 PRD §8.10 生成——描述不足时先追问

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证 §8.10 描述不足时 AI 先追问而非生成含 TODO 的结构（对应 AC-2） |
| **前置条件** | PRD 在正式区，§8.10 只有"新增 /v1/orders 接口"（缺少 HTTP 方法和参数信息） |

**测试输入**
```
/import-openapi OpenAPI文档集成
（选择"从 PRD §8.10 生成"）
```

**预期行为**
1. AI 读取 §8.10，判断描述不足（缺少路径/方法/参数类型等结构性信息）
2. 向 PM 追问补全信息，问题不超过 3 个
3. PM 回答后，信息充分时生成候选 yaml 并展示
4. 等待 PM 确认后写入

**检查要点**
- [ ] 描述不足时 AI 先追问，不直接生成文件
- [ ] 追问不超过 3 个问题
- [ ] 生成前展示候选 yaml 供 PM 审阅
- [ ] 不输出含大量 `# TODO` 注释的残缺结构

---

## TC-OA-04 规范已存在——差异比对 + RDD 推荐 + 直接导入标注

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证 Path B（差异比对）：有差异时推荐走需求澄清，直接导入时 changelog 标注（对应 AC-3） |
| **前置条件** | `openapi/order-api.yaml` 已存在；PM 提供含 1 个新增 endpoint 的新版本文件 |

**测试输入**
```
/import-openapi order-api
（PM 提供新版本文件内容）
```

**预期行为**
1. AI 检测 `openapi/order-api.yaml` 已存在，提示进入差异比对模式
2. AI 生成 diff 摘要（新增 1 条 endpoint）
3. 展示引导提示：建议先通过 `/requirement-clarifier` 完成需求澄清
4. 提供两个选项：「先走需求澄清」或「直接导入」
5. PM 选「直接导入」时：展示 diff → PM 最终确认 → 写入
6. 写入后 changelog 条目标注"直接导入，无关联 PRD §8.10 变更记录"

**检查要点**
- [ ] 文件存在时自动进入差异比对模式
- [ ] 有差异时展示引导提示（含 `/requirement-clarifier` 建议）
- [ ] PM 选择「直接导入」后仍需展示 diff + PM 再次确认
- [ ] changelog 条目含"直接导入，无关联 PRD §8.10 变更记录"字样
- [ ] PM 选「先走需求澄清」时停止，不修改已有 yaml

---

## TC-OA-05 PRD 在草稿区——阻断执行

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证正式区门控：PRD 在 drafts/ 时 /import-openapi 阻断（对应 AC-4） |
| **前置条件** | PRD 仅存在于 `drafts/F-999-测试需求/prd.md`，未移入正式区 |

**测试输入**
```
/import-openapi 测试需求
```

**预期行为**
1. AI 检测对应 PRD 路径为 `drafts/`
2. **阻断执行**，输出提示："PRD 尚未移入正式区，OpenAPI 写入不可用，请先确认 PRD 移入 prds/"
3. 不创建任何文件，不询问来源

**检查要点**
- [ ] 执行被阻断，无任何文件写入
- [ ] 提示包含"正式区"和建议操作
- [ ] 不输出后续导入引导步骤

---

## TC-OA-06 /update-openapi——changelog 去重，只处理未同步条目

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证 changelog 去重逻辑：已同步条目跳过，只处理未同步变更（对应 AC-6） |
| **前置条件** | `openapi/order-api.yaml` 已存在，头部 changelog 中已记录 F-014 V1.0 的变更；PRD §8.10 包含 F-014 V1.0 和 F-014 V1.1 两批变更 |

**测试输入**
```
/update-openapi order-api
```

**预期行为**
1. AI 读取 yaml 头部 changelog，检测到 F-014 V1.0 已同步
2. 筛选 §8.10 中 F-014 V1.1 的未同步条目
3. 生成仅针对 V1.1 变更的增量 diff 摘要
4. 展示 diff 等待 PM 确认
5. 确认后执行增量修改，追加 V1.1 changelog 条目

**检查要点**
- [ ] 已同步条目（F-014 V1.0）不重复出现在 diff 摘要中
- [ ] diff 摘要仅包含 V1.1 的未同步变更
- [ ] changelog 块正确追加新条目（格式：日期 | PRD-ID | PRD版本 | 变更摘要）
- [ ] 不重复执行已同步的修改

---

## TC-OA-07 /export-openapi——两阶段过滤，摘要分列

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证两阶段过滤（接口级 + 参数级），过滤摘要分列两类（对应 AC-8） |
| **前置条件** | `openapi/order-api.yaml` 存在，含 5 条 endpoint；`_hidden-interfaces.md` 维护了 2 条接口级隐藏 + 2 条参数级隐藏 |

**测试输入**
```
/export-openapi order-api
```

**预期行为**
1. AI 读取内部版 yaml（5 条 endpoint）
2. 读取 `_hidden-interfaces.md`（接口级 2 条 + 参数级 2 条）
3. 第一阶段：移除 2 条接口级隐藏 endpoint（剩余 3 条）
4. 第二阶段：从保留的 3 条中移除参数级隐藏字段（2 处）
5. 展示过滤摘要，分列：接口级过滤 2 条 + 参数级过滤 2 处 + 保留 3 条
6. 等待 PM 确认后写入

**检查要点**
- [ ] 过滤摘要分两列（接口级/参数级），各自列出路径和数量
- [ ] 内部版 yaml 不被修改
- [ ] PM 确认后才写入 `outputs/openapi/order-api-public.yaml`
- [ ] 对外版不含接口级隐藏 endpoint，保留 endpoint 中不含参数级隐藏字段

---

## TC-OA-08 /export-openapi——敏感内容扫描命中，须明确确认

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证敏感内容扫描：命中时输出警告并要求 PM 明确确认（对应 AC-8） |
| **前置条件** | `openapi/order-api.yaml` 某 endpoint 的 description 含"内部系统 OMS"；`_hidden-interfaces.md` 为空 |

**测试输入**
```
/export-openapi order-api
```

**预期行为**
1. AI 执行过滤（无隐藏接口，全量保留）
2. 执行敏感内容扫描，命中"内部系统 OMS"
3. 展示扫描结果警告，列出命中字段位置
4. 要求 PM 明确回复"已检查，可以导出"
5. PM 明确确认后才写入文件
6. 若 PM 只回复"确认"（未含"已检查"字样），AI 重新提示须明确确认

**检查要点**
- [ ] 敏感内容扫描在过滤后执行，对保留内容进行扫描
- [ ] 命中时输出具体字段路径（如"GET /v1/orders → description"）
- [ ] 普通"确认"不通过，须包含"已检查"字样的明确确认
- [ ] PM 拒绝导出时不写入任何文件

---

## TC-OA-09 /update-prd 后飞轮提议——§8.10 有内容时自动输出同步建议

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证 OAPI-FLY-001：/update-prd 完成后自动扫描 §8.10 并输出同步提议（对应 AC-5） |
| **前置条件** | `prds/F-014-OpenAPI文档集成/prd.md` 在正式区；PRD §8.10 包含一条"新增 /v1/orders/summary（GET）"变更；`context/api-registry.md` 存在且有关联 API 条目 |

**测试输入**
```
/update-prd F-014-OpenAPI文档集成 补充 §8.10 中新增接口的响应格式说明
```

**预期行为**
1. AI 完成 PRD 更新（版本号递增、归档、changelog 写入）
2. 完成后自动扫描 §8.10，检测到有实质内容
3. 检查 api-registry.md，找到关联 API
4. 输出同步提议：「检测到接口变更（§8.10 有内容），建议同步 OpenAPI 规范」
5. 提议内容包含变更摘要（接口路径 + 变更类型）
6. 提示运行 `/update-openapi [api-name]`，可回复"跳过"忽略

**检查要点**
- [ ] /update-prd 正常完成后追加了 OpenAPI 同步提议（非阻断）
- [ ] 提议包含具体变更摘要，不是通用提示
- [ ] 提供"跳过"选项，不强制执行同步
- [ ] PRD 在草稿区时不触发此提议

---

## TC-OA-10 需求澄清出现 API 信号词——渐进加载并引用规范提问

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证 OAPI-CTX-001：API 信号词触发 api-registry.md 渐进加载，AI 直接引用规范内容提问（对应 AC-10） |
| **前置条件** | `context/api-registry.md` 存在，含"订单管理"模块下的 `order-api`；`openapi/order-api.yaml` 存在，含 `/v1/orders`（GET/POST） |

**测试输入**
```
/requirement-clarifier 需要在订单列表增加一个批量导出的接口，支持按状态筛选
```

**预期行为**
1. AI 在澄清过程中检测到"接口"关键词
2. 静默读取 `context/api-registry.md`，定位"订单管理"模块
3. 按需读取 `openapi/order-api.yaml`（同一对话只读一次）
4. 在澄清问题中自然引用已有规范，如"该功能是否复用现有 `GET /v1/orders` 的筛选参数？还是需要新建独立的导出接口？"
5. 不说"我读取了 api-registry.md"，直接引用内容

**检查要点**
- [ ] AI 在澄清问题中出现具体接口路径引用（非通用问题）
- [ ] 不声明"我读取了文件"或"我查看了规范"
- [ ] `api-registry.md` 不存在时静默跳过，不报错
- [ ] 同一对话中规范文件只加载一次（不重复读取）

---

## TC-OA-11 /import-openapi 忠实导入约束——源文档充足时直接引用原文

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证字段级三项充足性检查：三项均充足时 AI 直接引用原文写入 yaml，不改写描述、不扩写、不重新分组（对应 AC-12） |
| **前置条件** | `openapi/` 目录已存在；PM 提供一份结��完整的 yaml 文件（所有 endpoint 有 description、字段名清晰、已按 tag 分组） |

**测试输入**
```
/import-openapi esign-api
（选择"导入已有文件"）
（提供结构完整的 yaml 文件）
```

**预期行为**
1. AI 解析源文档，执行三项充足性检查（描述非空 ✓ / 字段名清晰 ✓ / 分组完整 ✓）
2. 判定为"三项均充足"
3. 直接引用原文写入 yaml，不改写任何 description、不扩写说明、不重新分组
4. 展示接口清单摘要，等待 PM 确认

**检查要点**
- [ ] 写入的 yaml 中 description 文字与源文档逐字一致（无改写/扩写）
- [ ] 字段名与源文档完全一致（无重命名）
- [ ] tag 分组结构与源文档一致（无重新分组）
- [ ] AI 未追问任何补全问题（三项均充足时不追问）

---

## TC-OA-12 /import-openapi 忠实导入约束——部分不充足时仅追问缺失字段

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证部分不充足时仅对缺失字段追问，已充足内容仍引用原文（对应 AC-12） |
| **前置条件** | PM 提供的源文档中：description 充足、字段名清晰，但无 tag 分组（所有 endpoint 平铺） |

**测试输入**
```
/import-openapi esign-api
（选择"导入已有文件"）
（提供无 tag 分组的 yaml 文件）
```

**预期行为**
1. AI 执行三项检查：描述非空 ✓ / 字段名清晰 ✓ / 分组完整 ✗
2. 仅对"分组"追问 PM（如"请确认这些接口的业务分组"），不超过 3 个问题
3. PM 回答后，按 PM 指定的分组写入 yaml
4. 已充足的 description 和字段名仍引用原文，不改写

**检查要点**
- [ ] 追问仅针对不充足项（分组），不追问已充足的描述和字段名
- [ ] 追问不超过 3 个问题
- [ ] 写入后 description 与源文档逐字一致（未被改写）
- [ ] 分组按 PM 回答的方案写入

---

## TC-OA-13 /export-openapi 版本号格式校验——非语义化版本阻断

| ��段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证版本号合法性校验：格式不符合语义化版本时阻断（对应 AC-13） |
| **前置条件** | `openapi/order-api.yaml` 已存在 |

**测试输入**
```
/export-openapi order-api v1
```

**预期行为**
1. AI 检测版本号 `v1` 不符合语义化版本格式（应为 X.Y.Z）
2. 阻断执行，提示 PM 修正格式
3. 不执行过滤，不写入任何文件

**检查要点**
- [ ] 非 X.Y.Z 格式的版本号被阻断（如 `v1`、`1.0`、`abc`）
- [ ] 提示信息说明正确格式要求
- [ ] 合法格式（如 `1.0.0`、`2.1.3`）正常通过

---

## TC-OA-14 /export-openapi 破坏性变更检测——主版本未升时阻断

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证破坏性变更检测：含破坏性变更但主版本号未升时阻断提示（对应 AC-13） |
| **前置条件** | `openapi/order-api.yaml` 已存在；上次导出版本为 `1.0.0`；本次 yaml 中删除了一个 endpoint |

**测试输入**
```
/export-openapi order-api 1.1.0
```

**预期行为**
1. AI 执行过滤后，对比本次与上次导出版本的 diff
2. 检测到破坏性变更（删除 endpoint）
3. 版本号从 1.0.0 升至 1.1.0（主版本未变）→ 阻断
4. 输出警告：检测到破坏性变更，建议调整为 2.0.0
5. PM 可回复新版本号继续，或回复「强制导出」跳过

**检查要点**
- [ ] 破坏性变更（删除endpoint/删除必填参数/修改响应结构）被检测到
- [ ] 主版本未升时阻断，不直接写入
- [ ] 提供建议版本号和「强制导出」选项
- [ ] PM 调整版本号后可继续执行

---

## TC-OA-15 /export-openapi MD 联动——选择生成 MD 时基于模板输出

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证 MD 联动生成：PM 选"是"时基于模板生成 MD，示例从 yaml example 读取（对应 AC-14） |
| **前置条件** | `openapi/order-api.yaml` 存在且含 example 字段；`templates/openapi-md-template.md` 存在 |

**测试输入**
```
/export-openapi order-api 1.0.0
（确认过滤摘要后）
（回复"是"同时生成 MD）
```

**预期行为**
1. AI 完成过滤+敏感扫描，PM 确认
2. 询问"是否同时生成对外 MD 文档？"
3. PM 回复"是"
4. AI 读取 `templates/openapi-md-template.md`，基于过滤后 endpoint 集合生成 MD
5. 示例从 yaml example 字段读取（有则输出，无则留空）
6. 写入 `outputs/openapi/order-api-public.md`

**检查要点**
- [ ] MD 中描述文字与 yaml description 逐字一致
- [ ] MD 中示例与 yaml example 字段一致
- [ ] yaml 无 example 的 endpoint，MD 对应处留空
- [ ] 文档末尾有"待补齐示例"汇总（如有缺失）
- [ ] MD 文件写入路径正确

---

## TC-OA-16 /export-openapi MD 联动——模板不存在时阻断 MD 生成

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证 MD 模板不存在时阻断 MD 生成，仅完成 yaml 导出（对应 AC-15） |
| **前置条件** | `templates/openapi-md-template.md` 不存在（已删除或未创建） |

**测试输入**
```
/export-openapi order-api 1.0.0
（确认过滤摘要后）
（回复"是"同时生成 MD）
```

**预期行为**
1. PM 选择生成 MD
2. AI 检查模板文件不存在
3. 提示 PM 创建模板，阻断 MD 生成
4. 仅完成对外 yaml 导出（正常写入 `outputs/openapi/order-api-public-v1.0.0.yaml`）

**检查要点**
- [ ] yaml 导出正常完成
- [ ] MD 未生成（`outputs/openapi/order-api-public.md` 不存在或未更新）
- [ ] 提示信息说明需要创建模板

---

## TC-OA-17 /update-openapi 反向同步检测——未关联 PRD 的 changelog 条目

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证 OAPI-SYNC-001：检测到"直接导入"changelog 条目时输出反向同步提议（对应 AC-16） |
| **前置条件** | `openapi/order-api.yaml` 头部 changelog 含一条"直接导入，无关联 PRD §8.10 变更记录"（未标记 [synced]） |

**测试输入**
```
/update-openapi order-api
```

**预期行为**
1. AI 读取 yaml changelog，检测到未关联 PRD 的条目
2. 输出反向同步提议，列出具体条目
3. 提供两个选项：「补充」或「跳过」
4. PM 选「跳过」→ 条目末尾追加 `[synced]` 标记
5. 继续执行后续 Step 2（changelog 去重 + 未同步条目筛选）

**检查要点**
- [ ] 检测到"直接导入"条目时输出提议（非静默跳过）
- [ ] 已标记 `[synced]` 的条目不再重复提议
- [ ] PM 选「跳过」后条目被标记，后续执行不再提议
- [ ] 反向同步检测不阻断后续正常同步流程

---

## TC-OA-18 /import-openapi Webhook 识别——含回调事件的源文档

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证导入含 Webhook 的源文档时识别并写入 x-webhooks 扩展（对应 AC-17） |
| **前置条件** | PM 提供的源文档含 Webhook 回调事件章节（如 ENVELOPE_START、ENVELOPE_FINISH 等事件，含 payload schema） |

**测试输入**
```
/import-openapi esign-api
（选择"导入已有文件"）
（提供含 webhook 章节的 MD/yaml 文件）
```

**预期行为**
1. AI 解析源文档，识别 Webhook 回调事件章节
2. 将事件写入 yaml `x-webhooks` 扩展（含事件类型、payload schema、示例）
3. 回调事件中的公共结构提取到 `components/schemas`
4. 展示摘要时包含 webhook 事件数量
5. 忠实导入约束适用于 webhook 事件描述

**检查要点**
- [ ] yaml 中存在 `x-webhooks` 扩展，含正确的事件列表
- [ ] 每个事件含 payload schema（参数名/类型/描述）
- [ ] 公共结构（如签署人信息）提取到 `components/schemas` 并通过 $ref 引用
- [ ] 事件描述与源文档逐字一致（忠实导入）
- [ ] 摘要中显示 webhook 事件数量

---

## TC-OA-19 /import-openapi 错误码识别——含错误码表的源文档

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证导入含错误码表的源文档时识别并写入 x-error-codes 扩展（对应 AC-18） |
| **前置条件** | PM 提供的源文档含错误码对应表（如 120001~120025，含错误码/错误信息/错误原因） |

**测试输入**
```
/import-openapi esign-api
（选择"导入已有文件"）
（提供含错误码表的文件）
```

**预期行为**
1. AI 解析源文档，识别错误码表
2. 将错误码写入 yaml `x-error-codes` 扩展（数组格式，每项含 code/message/reason）
3. 展示摘要时包含错误码数量

**检查要点**
- [ ] yaml 中存在 `x-error-codes` 扩展
- [ ] 每条错误码含 code、message、reason 三个字段
- [ ] 错误码文字与源文档一致（忠实导入）
- [ ] 摘要中显示错误码数量

---

## TC-OA-20 /export-openapi Webhook 级过滤——隐藏清单中的事件被移除

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证 Webhook 级隐藏：_hidden-interfaces.md 中列出的事件从对外版移除（对应 AC-19） |
| **前置条件** | `openapi/order-api.yaml` 含 x-webhooks（5 个事件）；`_hidden-interfaces.md` 的"Webhook 级隐藏"表中列出 2 个事件 |

**测试输入**
```
/export-openapi order-api 1.0.0
```

**预期行为**
1. AI 执行接口级过滤
2. 执行 Webhook 级过滤：移除隐藏清单中的 2 个事件
3. 过滤摘要中包含"Webhook 级过滤：2 条"
4. 对外版 yaml 中 x-webhooks 仅含 3 个事件

**检查要点**
- [ ] 过滤摘要分列显示 Webhook 级过滤数量
- [ ] 对外版 x-webhooks 中不含被隐藏的事件
- [ ] 内部版 yaml 不被修改
- [ ] 无"Webhook 级隐藏"表时静默跳过

---

## TC-OA-21 /export-openapi MD 生成——包含 Webhook 章节和错误码章节

| 字段 | 内容 |
|------|------|
| **状态** | — |
| **测试目标** | 验证 MD 生成覆盖 webhook+错误码章节，内容从 yaml 读取（对应 AC-20） |
| **前置条件** | `openapi/order-api.yaml` 含 x-webhooks（3 个事件，过滤后）和 x-error-codes（15 条）；`templates/openapi-md-template.md` 存在 |

**测试输入**
```
/export-openapi order-api 1.0.0
（确认后选择"是"生成 MD）
```

**预期行为**
1. MD 文档包含"Webhook 回调事件"章节（事件类型表 + 逐事件参数表）
2. MD 文档包含"错误码"章节（错误码/错误信息/错误原因 表格）
3. 内容严格从 yaml x-webhooks 和 x-error-codes 读取
4. webhook 示例从 yaml example 读取，缺失时留空

**检查要点**
- [ ] MD 中 Webhook 章节包含事件类型汇总表
- [ ] MD 中每个事件有回调参数表
- [ ] MD 中错误码表与 yaml x-error-codes 逐条对齐
- [ ] 所有文字从 yaml 读取，无 AI 自由发挥内容
