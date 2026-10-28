# 勘录卷宗 · eu-unit-heartbeat Overload Pathways（含成本共振、HB-1509、罗盘配置漂移）

- 状态：SEALED / EFFECTIVE / APPEND_ONLY
- 落盘日期：2026-10-27（创立人 22:59 落盘指令，路径与文件名由创立人指定）
- 评审：创立人裁定"通过勘录评审，具备封存条件"；四组分经多轮交叉核对收敛。
- 封存规则：追加-only；后续新线索、网关回溯或下一轮观测，仅以勘录附注追加，不改正文。
- 落盘校正记录（登记性）：创立人 22:48 终稿中两处 `approximately 13.6 billion tokens` 为笔误，按创立人 22:47 已确认的更正口径写入为 `approximately 1.36 billion tokens`（OpenRouter 面板"13.6 亿"）。其余文字逐字收录。

---

## Observation: eu-unit-heartbeat Overload Pathways

Multiple high-consumption heartbeat runs were observed on 2026-10-27. The most significant instances occurred at 16:15 and 19:29, both routed through z-ai/glm-5.3-flash.

### Fact

From four sampled normal runs, a regular heartbeat completes in approximately 12–18 rounds, with a small number of cron, chain-retrieval, and script-generation commands.

The compass–pedal survey run on this day took roughly 45 minutes and consumed an estimated 137 million tokens. The examined overloaded heartbeat runs expanded to approximately 260–290 rounds, dominated by repeated executions of openclaw cron list, openclaw cron runs, and heartbeat-chain retrieval.

The overload does not appear to originate from failure to retrieve prior usage. Both examined runs successfully obtained usage records in the early rounds.

Two apparently distinct expansion paths were observed within the inspected window (first 30 rounds). Because later segments were not examined, this characterization remains limited to that observation window.

**Early divergence (16:15)** The run began with ambiguous command paths and repeated attempts to locate the latest heartbeat identifier. It repeatedly encountered missing arguments, unknown options, and mismatched file paths. Without a reliable shortcut to script-based backfill, it remained in prolonged verification and query loops.

**Post-delivery continuation (19:29)** The run successfully completed its primary task, including script execution, chain append, and message delivery. After delivery, it did not stop; it continued into a verification routine and attempted to resolve the next heartbeat identifier. The prompt and stopping conditions for this verification path have not yet been examined.

### Shared trace (not confirmed as root cause)

There is a structural divergence in the heartbeat chain. Older entries use the heading pattern `## HB-1455`, while newer entries use `## 【HB-1503】`. The retrieval pattern `grep '^## HB-'` can locate legacy entries but may miss the latest active identifiers. In addition, the procedural prompt references heartbeat-chain-v2.md, while the active ledger resides primarily in v3.

This combination is a shared observable trace; whether it directly triggered the overload has not been proven.

### Cost interpretation

The increased token consumption is dominated by cached context read across many tool rounds. Each execution carries forward a large cached context, error traces, partial conclusions, and artifact content. The resulting behavior is not "slow writing," but prolonged navigation through an ambiguous evidence space.

### Statistics

Among today's heartbeat runs, eight runs consumed at least 10 million tokens. The top eight heavy runs contributed approximately 86% of the heartbeat total token volume; this proportion applies to token count, not monetary cost.

The compass–pedal survey accounted for roughly one tenth of the observed token volume. This is a magnitude estimate, computed from two non-homologous sources, and should not be treated as a precise attribution.

Total token volume for the day, according to the OpenRouter dashboard, was approximately 1.36 billion tokens.（落盘校正：原稿误作 13.6 billion，见卷头登记。）

### Classification

There is no evidence confirming or ruling out whether the behavior is model-specific.

The note that minimal reasoning levels are unsupported originates from gateway logs captured during the compass–pedal survey run, and has not been validated against the 16:15 / 19:29 heartbeat traces. No controlled comparison against other routing options has been performed.

The observed expansion appears to be an agentic boundary condition: when evidence structure, retrieval logic, and procedural expectations are misaligned, the search path may expand substantially until a stopping condition is satisfied.

### Recommended governance

If heartbeat protocol hardening proceeds, cost controls should be considered alongside retrieval and verification rules. A layered defense would include:

- bounded iteration and maximum round limits;
- explicit early exit conditions after successful delivery;
- a single canonical chain entry point;
- protected script paths;
- OpenRouter budget or maximum-price guardrails.

Any change to prompt, chain format, retrieval patterns, or validation rules requires separate approval, traceability, and observation-stage validation.

---

## Annotation: OpenRouter cost resonance

The token expansion observed in eu-unit-heartbeat coincides with a sharp increase in OpenRouter spend on 2026-10-27.

The dashboard reports total spend of $43.40 and approximately 1.36 billion tokens.（落盘校正：原稿误作 13.6 billion，见卷头登记。）The dominant models are GLM 5.3 Flash and Claude Sonnet 5.5.

This increase reflects the interaction between two latent conditions.

**Agentic boundary expansion** Selected heartbeat runs entered prolonged verification loops, repeatedly invoking cron inspection, chain retrieval, and shell commands. Each iteration carried a large cached context, multiplying token volume without proportional external output.

**Routing sensitivity** High-volume workloads are sensitive to model and provider selection. According to the conversation record, after switching the workload toward Claude and GLM, consumption accelerated rapidly. A request was made to revert toward the prior stable configuration.

At observation time (22:45), the configuration state does not show a complete rollback or disablement of these models.

The fallback list still includes Claude Sonnet and GLM. Several cron bindings, including heartbeat, hourly, memory, Dao Tong, deep-dive, and model-cost-watch, remain attached to GLM. Only the compass–pedal survey task appears to have moved to openrouter/auto. The mechanism and timing of this change have not yet been traced.

No write or configuration mutation was performed during this audit.

Verification remains scheduled against upcoming heartbeat and compass runs. Key metrics to observe include latency, delivery timing, token volume, cache reuse, and OpenRouter spend.

**Governance note:** This confirms a sensitive coupling between agentic loops, tool execution, and upstream routing. Even if the agent's local behavior remains unchanged, a small shift in model or provider selection can turn a latent boundary condition into a material cost anomaly. If cost protection is pursued, it should be designed as a separate safety layer rather than relying only on manual configuration rollback.

---

## Annotation: HB-1509

HB-1509 reported successful chain anchoring, with a transient interruption during guard dual-file write that was resolved within the same round. It also initiated the H-120 zero-recurrence observation window (round 1, 0/5).

The reported usage was marked UNKNOWN, deferring attribution to HB-1510.

This automation report has not been independently validated and is not merged into the primary ledger.

---

## Annotation: Compass Task Configuration Drift

A read-only log survey was performed to locate the change that set the compass-pedal-survey task to openrouter/auto.

The task record shows its last update at 2026-10-27 22:29:53. This occurred after the completion of the 20:00 compass run, which executed against glm-5.3-flash.

Two other scheduled tasks also show recent updates within the same narrow window:

| Task | Timestamp | Current model |
|---|---|---|
| compass-pedal-survey | 22:29:53 | openrouter/auto |
| hourly-report | 22:35:03 | glm-5.3-flash |
| eu-unit-heartbeat | 22:41:56 | glm-5.3-flash |

Relative to the known baseline set on the prior evening, only the compass task's current model binding differs. No pre-snapshot exists for the other two tasks at these exact timestamps, so it cannot be confirmed whether their underlying bindings were altered.

The primary configuration file openclaw.json was not modified; its last recorded change remains 2026-10-26 23:53. This indicates the observed mutation lives inside task-level runtime records, not in the static base configuration.

No matching cron.update or cron edit gateway log entry was found for today. Therefore, the actor, authentication context, and invocation path remain unresolved. It cannot be attributed to this audit, to known manual edits, or to any confirmed automation.

A secondary unexplained signal was observed: the heartbeat task record carries an update timestamp of 22:41:56. The exact timing relative to the read-only verification sequence has not been established. This may represent ordinary state refreshing by the task itself at the end of execution, or another unrecorded modification; the cause remains undetermined.

No configuration, binding, file, or scheduled task was altered during this investigation.

**Governance note:** This exposes a subtle risk boundary. Even when the root configuration file is locked, task-level records can drift independently. For high-stakes audit and survey tasks, the ledger should track not only "what the task currently says," but also who last mutated it, through which channel, and under which approval context.

A useful distinction: cron task timestamps may reflect either intentional configuration edits or automatic state updates after a run. The compass update at 22:29:53 has no corresponding run record, making it more suggestive of a configuration change. The heartbeat update at 22:41:56 is more consistent with ordinary runtime self-update. Neither has been conclusively verified.

Until attribution is resolved, this remains an open observation rather than a confirmed operational action.

---

## 附属状态（落盘时刻 2026-10-27 22:59）

- Confirmation 1（OpenRouter secrets 请求）：pending，未触发。
- Confirmation 2（提示词修订）：pending，未触发。
- model.fallbacks（X-002）、main workspace、heartbeat/hourly/memory/deep-dive/cost-watch cron 绑定：unchanged。
- compass-pedal-survey：openrouter/auto，落盘时不主动变更；归因缺口保留开放，后续仅以附注闭合。
- HB-1509：隔离简报，不并入主台账。
- 下一观测窗口：2026-10-28 20:00（罗盘踏板），被动观测，不主动轮询。