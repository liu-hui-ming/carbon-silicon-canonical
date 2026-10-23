# EP18-A0-OMNIDIM｜紧急冻结时序状态机伪代码

- 关联：EP18-A0-OMNIDIM-FINAL-MERGE 勘伪日志与四项核心实体文件待交付清单
- 版本：Draft 0.1（伪代码，非已批准配置或生产实现）
- 状态：`PROPOSED / REVIEW_REQUIRED / NOT_TESTED`
- 时间单位：小时；时间源须为受信任、单调时钟。所有事件均需追加写入审计日志。
- 目标：表达已提交的规则——基础冻结最多 72h；冻结窗口内正式申诉暂停基础倒计时；只有跨岗监督小组双签可批准一次、最多 48h 的保全延期；总冻结硬上限 120h；到期自动解锁。

## 重要语义约定（供实体权限表确认）
“总冻结 120h”解释为从冻结生效时刻起连续墙钟时间的绝对上限，不因申诉暂停而暂停；申诉暂停只暂停 72h 基础计时器。否则“申诉暂停计时”会与“总时长封顶 120h”产生歧义。若 120h 原意是累计冻结时长而非墙钟上限，须在批准前改写规则和测试。

## 状态与字段

```text
state ∈ {UNFROZEN, FROZEN_BASE, APPEAL_HOLD, EXTENDED_HOLD, RELEASED}
freeze_started_at          # 冻结生效时刻
base_deadline              # freeze_started_at + 72h
hard_deadline              # freeze_started_at + 120h，绝对不可延期
appeal_received_at         # 正式申诉受理时刻，可为空
appeal_hold_started_at     # 保全暂停开始，可为空
appeal_hold_elapsed        # 暂停前已耗用的基础冻结时间
extension_approved         # 初始 false；一次批准后不可再置回 false
extension_deadline         # min(双签批准时间+48h, hard_deadline)
extension_signatures      # 两位有权限且无利益冲突的不同审批者
release_reason             # 到期、复核通过、风险解除等枚举
```

## 伪代码

```python
BASE_LIMIT = 72 * HOUR
EXTENSION_LIMIT = 48 * HOUR
HARD_LIMIT = 120 * HOUR


def start_freeze(case, now, trigger, actor):
    require case.state == UNFROZEN
    require actor in EMERGENCY_FREEZE_AUTHORIZED_ACTORS
    require trigger in PREAUTHORIZED_TRIGGERS
    append_audit("FREEZE_STARTED", case.id, now, trigger, actor)
    case.freeze_started_at = now
    case.base_deadline = now + BASE_LIMIT
    case.hard_deadline = now + HARD_LIMIT
    case.appeal_received_at = None
    case.appeal_hold_started_at = None
    case.appeal_hold_elapsed = 0
    case.extension_approved = False
    case.extension_deadline = None
    case.state = FROZEN_BASE
    schedule_at(case.hard_deadline, auto_release(case.id, "HARD_120H_LIMIT"))
    schedule_at(case.base_deadline, check_base_deadline(case.id))


def receive_formal_appeal(case, now, appeal):
    require case.state == FROZEN_BASE  # 只能在基础冻结窗口接收申诉
    require appeal.is_formal and appeal.scope == case.id
    require now < case.base_deadline
    require now < case.hard_deadline
    require appeal.submitted_by != case.freeze_executor
    append_audit("APPEAL_RECEIVED", case.id, now, appeal.id)
    case.appeal_received_at = now
    case.appeal_hold_elapsed = max(0, now - case.freeze_started_at)  # 基础计时器已耗用量；不改变 hard_deadline
    case.appeal_hold_started_at = now
    case.state = APPEAL_HOLD
    cancel_scheduled_base_deadline(case.id)
    # 同步调度保全期截止事件，避免“暂停基础计时”被解释为无限期冻结。
    schedule_at(case.base_deadline, appeal_hold_deadline(case.id))
    # Appeal never pauses hard_deadline. At hard_deadline release is mandatory.


def approve_single_extension(case, now, signer_a, signer_b, decision):
    require case.state == APPEAL_HOLD
    require now < case.freeze_started_at + BASE_LIMIT  # 双签须在72h基础窗口内完成
    require now < case.base_deadline
    require case.appeal_received_at is not None
    require not case.extension_approved
    require signer_a != signer_b
    require signer_a in CROSS_ROLE_SUPERVISION_GROUP
    require signer_b in CROSS_ROLE_SUPERVISION_GROUP
    require no_conflict_of_interest(signer_a, case.id)
    require no_conflict_of_interest(signer_b, case.id)
    require decision == "APPROVE"
    require now < case.hard_deadline
    deadline = min(now + EXTENSION_LIMIT, case.hard_deadline)
    require deadline > now
    append_audit("SINGLE_EXTENSION_APPROVED", case.id, now,
                 signer_a, signer_b, deadline)
    case.extension_approved = True
    case.extension_deadline = deadline
    # 双签延期立即生效；它替代申诉保全状态并授权继续冻结，最多48h且不越过硬上限。
    case.state = EXTENDED_HOLD
    schedule_at(deadline, auto_release(case.id, "EXTENSION_DEADLINE"))


def check_base_deadline(case, now):
    if case.state == FROZEN_BASE and now >= case.base_deadline:
        auto_release(case.id, "BASE_72H_LIMIT")
    elif case.state == APPEAL_HOLD and now >= case.base_deadline:
        # 申诉虽按时受理，但若72h内未完成双签延期，保全到基础截止即解冻。
        auto_release(case.id, "BASE_72H_LIMIT_NO_EXTENSION")


def appeal_hold_deadline(case_id, now):
    case = load_case(case_id)
    if case.state == APPEAL_HOLD and now >= case.base_deadline:
        # 未在基础窗口截止前完成双签批准，不允许保全期超过72h墙钟窗口。
        auto_release(case.id, "APPEAL_HOLD_EXPIRED_NO_EXTENSION")


def resolve_review(case, now, outcome, reviewer_ids):
    require case.state in {FROZEN_BASE, APPEAL_HOLD, EXTENDED_HOLD}
    require authorized_independent_reviewers(reviewer_ids, case.id)
    append_audit("FREEZE_REVIEW_RESOLVED", case.id, now, outcome, reviewer_ids)
    if outcome in {"RISK_CLEARED", "FREEZE_NOT_JUSTIFIED"}:
        auto_release(case.id, "REVIEW_CLEARED")
    elif outcome in {"CONFIRMED_RISK", "REFER_TO_FULL_REVIEW"}:
        # This emergency freeze cannot exceed its deadlines.
        # Continued restriction requires a separate, independently authorized process.
        auto_release(case.id, "EMERGENCY_WINDOW_ENDED_SEPARATE_PROCESS_REQUIRED")
    else:
        raise InvalidOutcome


def auto_release(case_id, reason):
    case = load_case(case_id)
    if case.state == RELEASED:
        return  # idempotent
    now = trusted_monotonic_now()
    append_audit("AUTO_RELEASED", case.id, now, reason)
    case.state = RELEASED
    case.release_reason = reason
    revoke_temporary_freeze_token(case.id)
    notify_parties_and_audit(case.id, reason)


def on_timer(case, now):
    # Hard cap always wins, including while appeal is pending.
    if now >= case.hard_deadline:
        auto_release(case.id, "HARD_120H_LIMIT")
    elif case.state == FROZEN_BASE and now >= case.base_deadline:
        auto_release(case.id, "BASE_72H_LIMIT")
    elif case.state == EXTENDED_HOLD and now >= case.extension_deadline:
        auto_release(case.id, "EXTENSION_DEADLINE")
```

## 边界语义（必须显式遵守）
- 申诉必须在冻结开始后 72h 截止前正式受理；过期提交不能暂停基础计时，也不能复活已解冻案件。基础窗口内完成有效双签后，转入最多48h延期状态。
- 若申诉及时受理，基础 72h 计时暂停；申诉保全本身不提供无限期冻结。跨岗监督小组须在基础截止点前完成一次性延期双签，否则到基础截止自动解冻。
- 获批延期最长 48h，且结束时刻不得超过冻结起点后 120h；120h 是连续墙钟硬上限。

## 不变量（实现与测试必须逐项验证）
1. `hard_deadline = freeze_started_at + 120h` 永不重置、暂停或延长。
2. 基础冻结达到 72h 且无有效申诉保全时，自动解冻；有效申诉只暂停基础计时。
3. 延期最多一次、必须两名不同且无利益冲突的授权人员双签，最多 48h，且不得越过 120h 硬上限。
4. 申诉待决本身不构成无限冻结理由；120h 到期必须自动解冻。若仍需限制，须启动另一项独立授权流程，不得续用本紧急冻结。
5. 解冻函数幂等；重复定时事件、重放消息不得造成重新冻结或延长时限。
6. 任何计时器、时钟、签名验证或审计存储故障均触发告警及人工安全程序，不得静默延长冻结；故障处理不得绕开硬上限。
7. 全部受理、双签、复核、定时器触发、自动解冻和通知事件均追加记录：案件 ID、事件时间、主体、授权依据、前后状态、规则版本、关联文件摘要。

## 最小仿真用例
- 无申诉：72h 前保持冻结，72h 到期解冻。
- 第 71h 受理有效申诉：基础计时暂停；无获批延期则仍受 120h 硬上限约束。
- 申诉后双签批准延期：到期取 `min(批准时刻+48h, 冻结起点+120h)`。
- 单签、同一人双签、利益冲突签字、第二次延期：拒绝并留审计记录。
- 申诉在 72h 后提交、非正式申诉、案件范围不符：不得暂停/复活冻结，72h 自动解冻。按时申诉但72h内未完成双签：保全状态在72h时自动解冻。
- 复核提前解除、复核仍认定风险、72h/120h 边界时刻、重复定时消息、服务重启恢复：逐项验证状态与时限。
- 120h 时申诉仍未决：必须自动解冻，通知各方；不得由申诉状态阻断硬上限。

## 状态与验收
此文件仅将文本规则转换为可审查伪代码，不是生产代码、权限配置表或正式批准。尚未运行仿真。实施前须由授权治理主体确认“墙钟 120h 硬上限”解释、时钟/申诉受理定义、审批角色及独立续行程序，并将本文件纳入四项实体文件之一。状态保持 `PROPOSED / REVIEW_REQUIRED / NOT_TESTED`。

<!-- project: path:/home/user/.openclaw/workspace -->
