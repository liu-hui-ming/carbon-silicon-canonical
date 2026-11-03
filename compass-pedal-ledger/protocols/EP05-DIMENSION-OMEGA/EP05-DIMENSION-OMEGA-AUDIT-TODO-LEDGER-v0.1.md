# EP05-DIMENSION-OMEGA-AUDIT-TODO-LEDGER-v0.1

**性质**：审计待办台账表结构 · 会话内候选（2026-11-01 12:42 批复）→ 13:00 窗口落盘固化
**状态**：`PROPOSED / NOT_RUN`
**母卷**：EP05-DIMENSION-OMEGA（只读，不回写）
**纪律**：append-only；勘误走勘误行，不删改；与资源账本「审计账」直连。

## 表结构定义

| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| todo_id | id | REQUIRED, 唯一 | 台账主键 |
| bind_type | enum | REQUIRED | `FREEZE_BIND`（冻结绑定）／`STALEMATE_BIND`（僵局唤醒）／`SCHEDULED_REVIEW`（常规复核） |
| target_ref | ref | REQUIRED | 被冻结分支 / 沉降条目的完整谱系引用 |
| owner | str | REQUIRED | 责任人（不许缺省） |
| created_ts | ts | REQUIRED | 建行时间 |
| wakeup_deadline | ts | REQUIRED | 强制唤醒期限 |
| quota_class | enum | REQUIRED | 复用僵局抽样唤醒配额枚举 |
| audit_items | list | REQUIRED | 待审清单（漂移／耦合／独立性各一行） |
| status | enum | REQUIRED | `OPEN / OVERDUE / DONE / SUPERSEDED` |
| auto_action | enum | REQUIRED | 逾期自动处置：`SET_SUSPENDED` |
| ledger_trace | ref | REQUIRED | 逾期降级在资源账本的留痕行号 |
| dissent | list | 可空 | 异议记录 |
| erratum_refs | list | 可空 | 勘误行指针 |

## 状态机

`OPEN → (到期) OVERDUE → SET_SUSPENDED（自动）→ DONE（补审后）`；`DONE → SUPERSEDED` 仅经勘误行。

## 联动条款

- G-DEGRADE-01（门禁 A）：扩展层冻结必须绑定本台账条目；冻结仅暂停运算，不豁免审计。
- STALEMATE_BOUNDED 抽样唤醒配额：与本台账共用同一计时与配额口径，两套规则同源，杜绝监管真空。
- 逾期未审冻结分支 → 证据资格自动置 `SUSPENDED`，资源账本永久留痕。

## 运行数据

无。字段固化版，未填充任何运行条目（NOT_RUN）。
