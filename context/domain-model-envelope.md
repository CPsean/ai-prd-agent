# 领域模型参考：Envelope 域

> AI 技术参考文件。写 PRD 字段清单、数据模型或接口设计时，直接引用此文件中的字段名和业务规则，不要自造字段名。

---

## Envelope（信封 / 聚合根）

**概念**：信封域的聚合根，负责全生命周期（草稿→计划→运行→结束），聚合任务、参与者、文档、活动等对象，通过状态机和领域事件驱动业务一致性。

### 核心字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `envelopeId` | UUID | 信封唯一 ID |
| `envelopeTopic` | String | 标题 |
| `envelopeDesc` | String | 说明 |
| `status` | String | 当前状态（由 `EnvelopeStatus` 控制） |
| `startTime / endTime / expireTime` | Timestamp | 启动、结束、过期时间 |
| `appId / version` | String | 应用 ID、版本 |
| `runtimeId / runtimeContext` | String / Map | 运行实例标识、上下文 |
| `interruptBizStatus / interruptReason / cancelReason` | String | 异常信息 |
| `profile` | Map | 扩展配置 |
| `documents / participants / tasks / activities` | List | 子集合 |
| `events` | List | 信封内产生的领域事件（transient） |
| `interruptRecovery / skipInterrupt` | Boolean | 中断恢复、跳过下次中断标记 |

### 生命周期行为

- **生命周期**：`start / finish / interrupt / cancel / expire / postpone`
- **调度相关**：`scheduleStart / modifyScheduleTime / cancelScheduleStart`
- **任务流**：`startTask / completeTask / commitTaskDocuments / interruptTask / transferTask`，支持批量排序、放弃/归回/后续任务
- **权限与人员**：`changeInitiator / changeMember / updateTaskExecutor` 触发权限变更事件

---

## EnvelopeTask（任务节点）

**概念**：信封内的可执行任务节点，维护顺序、模式、执行人，通过 `EnvelopeTaskStateMachine` 控制状态。

### 核心字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `envelopeId / taskId` | UUID | 信封 ID、任务 ID |
| `taskType / taskMode / taskGroupId` | String | 类型、模式（AND/OR）、分组 |
| `taskStatus / taskBizStatus` | String | 状态、业务状态 |
| `taskOrder` | String | 执行顺序（可解析为 float） |
| `participantId / participants` | String / List | 当前执行人 ID、执行人列表 |
| `outerId` | String | 外部引用 |
| `interruptReason` | String | 中断原因 |
| `startTime / endTime / expireTime` | Timestamp | 时间记录 |
| `profile` | Map | 任务扩展配置 |

### 行为

- `assignParticipant / participant() / transfer`：管理执行人
- `start / complete / interrupt`：驱动任务状态机
- `allowManualTransfer`：读取 profile 配置判断是否允许手动转交

---

## EnvelopeParticipant（参与者）

**概念**：信封参与主体（发起人/签署人/抄送人），支持个人/组织类型，多种标识与扩展信息。

### 核心字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `envelopeId / participantId` | UUID | 信封 ID、参与者 ID |
| `participantType` | Enum | 参与者类型（`EnvelopeParticipantType`） |
| `participantName / participantSubject` | String | 名称、主体 |
| `participantExt / participantSubjectExt` | Map | 扩展 Map |
| `participantRole` | Enum | 角色（INITIATOR/SIGNER/CC） |
| `memberId` | String | 成员 ID |
| `subjectId` | String | 主体标识符 |

### 关键存储对齐

- **`participantRole`**：在 `participantExt`（Profile）中存储含 `roleId` 与 `roleName` 的 JSON 对象
- **`instantSync`**：即时通知激活标识，标记该参与方是否启用即时通知语义

### 行为

- `isInitiator / isSigner / isCC`：角色判断
- `isSame`：使用比较（供工厂类）
- `changeMember`：记录新 memberId 并重新绑定
- IdentifierFactory：解析邮箱/手机号/证件/memberId
- `formatParticipantName / bindSubject / bindMember`：DTO 输出

---

## EnvelopeDocument（文档）

**概念**：信封中的单个业务文档，支持阶段（phase）与扩展配置管理，用于签署或展示。

### 核心字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `envelopeId` | UUID | 所属信封 ID |
| `documentId` | UUID | 文档 ID（UUID 去横杠） |
| `documentName / documentType` | String | 名称、类型 |
| `documentStatus` | String | 状态（DTO 转枚举） |
| `fileKey` | String | 存储 Key |
| `showOrder` | Integer | 展示顺序（默认 `Integer.MAX_VALUE`） |
| `profile` | Map | 扩展配置 |
| `phase` | Map | 阶段记录（默认 ORIGIN） |
| `uploaderId` | String | 上传者 ID |
| `uploadTime` | Timestamp | 上传时间 |

### 关键字段说明

- **资源对齐逻辑**：在 `profile` 中存储 `docTemplateDocumentId`，保存来源文件模板的具体 ID，用于文档属性溯源
- `updateDocument`：对关键字段执行非空覆盖并合并 profile

---

## EnvelopeActivity（活动日志）

**概念**：记录信封动作的状态变化快照和上下文，辅助审计和状态追踪。

| 字段 | 类型 | 说明 |
|------|------|------|
| `envelopeId / activityId` | UUID | 信封、活动 ID |
| `actionType` | Enum | `EnvelopeActionEnum` |
| `instantaneousStatus / currentStatus` | String | 动作前/后的状态 |
| `context` | Map | 业务上下文 |
| `innerData` | Boolean | 是否租户内部记录 |

---

## EnvelopeTicket（JWT 票据）

**概念**：用于信封访问/签署的 JWT 票据实体，支持策略、有效期和自定义 payload。

| 字段 | 类型 | 说明 |
|------|------|------|
| `ticketId` | String | 票据 ID |
| `issueTime / expireTime` | Timestamp | 签发、过期时间（默认 2 小时） |
| `status` | Enum | `TicketStatus` |
| `strategy` | Enum | `TicketStrategy` |
| `useCount` | Integer | 使用次数 |
| `payload / securityData` | Map | 自定义载荷、安全数据 |

- `issueTicket()`：生成 HMAC256 签名的 JWT，Issuer 固定为 `epaas-envelope`

---

## EnvelopeTransferTask（批量转移任务）

**概念**：批量转移任务及权限的工作对象，记录源/目标、条件、进度和状态。

| 字段 | 类型 | 说明 |
|------|------|------|
| `taskId` | UUID | 转移任务 ID |
| `transferType` | String | 资源维度（默认 memberId） |
| `sourceId / targetId` | String | 源与目标 |
| `transferCondition` | String | 筛选条件 |
| `batchMarker` | String | 游标 |
| `status` | Enum | `EnvelopeTransferTaskStatus` |
| `version` | Integer | 乐观锁（默认 1） |

---

## 查询/辅助对象速查

| 类 | 用途 |
|----|------|
| `EnvelopeDocumentQuery` | 文档查询 Builder |
| `EnvelopeParticipantQuery` | 参与者查询 Builder |
| `EnvelopeTaskQuery` | 任务查询 Builder |
| `TaskOuterIdItem` | 批量绑定任务 outerId |
| `EnvelopePermissionHelper` | 根据角色/信封/任务构建权限模板参数，生成 ERN 字符串，支持跨租户授权 |

---

## 组件

| 组件 | 说明 |
|------|------|
| `EnvelopeComponentRegister` | 注册催签超时流组件 |
| `EnvelopeUrgeTimeLimitComponent` | 校验首次/间隔催签（默认 30 分钟），写入缓存 |
| `EnvelopeUrgeConfig` | `firstTime` / `intervalTime` 配置（默认 30 分钟） |
