# N16 会审议案包｜归档出口裁决

- 议题：语义锁（仅 `E_CONTRADICTED` 可终审下线）导致非证伪算子永久不可归档。
- 状态：`PENDING_2000_REVIEW / NOT_APPROVED / NOT_SEALED / NOT_IMPLEMENTED`
- 基线：`sm_transition_matrix.csv` v0.4（40 边，语义锁生效，`ead7f6da32ed868c…`）
- 性质：**议案文本，不是生效转移表**。任一方表决通过前，不得并入主 CSV；两案互斥，不可并用。
- 创立人会审建议（照录）：先锁 D01、N04 基础规则，N16 最后表决，避免上层归档规则反向侵蚀底层证伪门禁。

## 两案速览

| 项 | 方案A 严格版 | 方案B 废弃分支版 |
|---|---|---|
| 新增状态 | 无 | 治理轴 +`G_OBSOLETE` |
| 新增边 | 0（仍 40） | +8（共 48） |
| 新增权限域主体 | 无 | 无（扩充 `CROSS_LAYER_REVIEW_BOARD` 动作集） |
| SVA 新增 | 1 条 | 3 条 |
| 归档可达 | 仅 `CONTRADICTED` | `CONTRADICTED` + `REPLICATED`/`TESTED_SCOPE`（经 OBSOLETE） |
| 台账完整性 | 分裂，需独立活跃台账 | 统一闭环 |
| 主要风险 | 「废弃」无合法表达，退化为冻结或伪造冲突观测 | 「无迭代价值」判据 UNSET，存在滥用与主观争议 |
| 弃权/未决 | `fail_closed = true` | `fail_closed = true` |

## 机器核验（本地执行，非仿真）

两案均以 v0.4 为基线做静态图校验：

- 方案A：非证伪态通向 `G_RETIRED`/`G_ARCHIVED` 的既有边数 **0**（v0.4 已满足，A 为"零改动+断言固化"）。
- 方案B（叠加 8 条新边后，48 边）：
  - `G_OBSOLETE → G_RETIRED` 边数 **0**（物理隔离成立）
  - 非 CONTRADICTED 起点通向 `G_RETIRED` 边数 **0**（语义锁未被放宽）
  - 全 35 个状态（7 证据态 × 5 治理态）中不可达 15 个：`E_PROPOSED/E_DEFINED/E_ESTIMATED/E_UNKNOWN` × `{RETIRED, ARCHIVED, OBSOLETE}`（均为应然不可达）+ `E_CONTRADICTED+G_OBSOLETE`（应然：证伪条目走 RETIRED）+ `E_REPLICATED/E_TESTED_SCOPE + G_RETIRED`（应然：稳定条目走 OBSOLETE）
  - 即：不可达集合与设计意图完全一致，无意外孤岛。

## 方案B 的必答前置问题（会审须先定）

1. **「无迭代价值」判据 UNSET**：目前 `obsolescence_motion` 无量化门槛。若不设判据，会审即为纯主观表决，与本体系"可证伪门禁"精神冲突。建议候选判据：连续 N 个观测周期零新证据 + 零引用 + 无待验分支（N、周期数需赋值）。
2. **枚举位宽变更**：`governance_state_t` 需由 `logic [1:0]` 扩为 `logic [2:0]`，属接口变更，影响所有已编译引用方。
3. **废弃后能否复活**：方案B 现设计 `OBSOLETE→ACTIVE` 仅经 `obsolescence_withdraw`（会审撤销）。若 `ARCHIVED` 后需复活，与 N04 的 `s_always` 永久锁直接冲突——**N16-B 与 N04 存在依赖，须按 A→B 顺序表决**。
4. **双通道滥用防线**：需权限域前置校验 + 3 条 SVA 同时生效；单靠 CSV 白名单不足以拦截"用废弃通道处理未验证条目"。

## 文件
- `n16-plan-a-strict.yamlish`＝`ed98d984f1491c49…`（边定义 + 权限域配置 + 1 条 SVA + 代价）
- `n16-plan-b-obsolete-branch.yamlish`＝`9210b9504b6d1b42…`（8 条边 + 黑名单 + 权限域 + 3 条 SVA + 代价）

---

## N16 议案包收束回执（创立人 14:55，照录固化）
- 元标记：`N16_BUNDLE_ACK / TOPOLOGY_DEPENDENCY_LOCK / VOTE_ORDER_LOCK`；链锚 `d0aea358f131a866… → b744be52d40dee76…`，INDEX `b50f3d42438755a5…`。
- **基线冻结**：主 `sm_transition_matrix.csv` v0.4（40 边）保持不动；两案均为叠加补丁包，不预写入主干。
- **表决序列锁死（不可调换）**：`D01 → N04 → P1 → N16`；逻辑链＝底层断言→归档固化→权限主体边界→上层归档拓扑。逆序投票会产生矛盾可组合态。
- **B 案四项硬前置（任一无共识即 B 案自动失效，不进入执行分支）**：
  1. `obsolescence_motion` 量化判据待赋值（周期、零证据、零引用阈值）
  2. `governance_state_t` 位宽扩容（[1:0]→[2:0]，跨接口变更）
  3. 与 N04 强耦合：永久归档不可解封 / 允许撤销复活，**二选一，不可同时成立**
  4. 防线须为「权限网关前置 + CSV 白名单 + 配套 SVA」三重串联
- **表决后合并脚本（暂不执行）**：
  - 投 A → 主干 CSV 不变，仅追加 `a_optionA_no_stable_archive` 断言；同步立项「长期活跃算子台账」工件开发任务。
  - 投 B → 合并 8 条新边、更新状态枚举与 `governance_state_t` 定义、注入 3 条 SVA、录入 obsolescence 量化阈值，README 勘录接口变更风险。
- 工件隔离：`review-n16/` 与主干哈希台账分开登记，防预污染。
- 台账：✅ N01–N15、N17；⏳ 会审队列（顺序固定）D01、N04、P1、N16；📦 表决后启动 Testbench、权限越权注入、SYS-DIM-BENCH 接入、T17–T24 判据模板。

---

## 会审前置终版快照回执（创立人 14:56，照录固化）
- 元标记：`PRE_MEETING_FREEZE / A_SIDE_EFFECT_RISK_REGISTER`；链锚 `c3dd9d92eeb96126…`，INDEX `b50f3d42438755a5…`，主干 CSV `ead7f6da32ed868c…`（锁定）。
- **A 案配套台账治理参数（新增登记，A 案表决生效后必须同步落地；参数未达共识则 A 案暂缓生效，维持临时冻结兜底）**：
  1. 维护主体：`META_VALIDATION_L3` 负责快照归集、哈希锚定、索引校验；`OBSERVER` 只读、仅可提交勘录异议，无权修改台账状态。
  2. 快照策略：固定周期全量快照 + 增量变更日志；快照永久归档，增量日志随主 ledger 链式存证。
  3. 更新频率：待会上赋值（候选：日增量 / 周全快照）。
- **工件隔离终态**：主干（40 边 CSV、SVA v0.4、P1 声明、Schema 双向锚定）只读封存、无预合并；`review-n16/` 补丁分支独立哈希台账；合并脚本休眠，触发条件严格绑定表决结果，无手动旁路，`fail_closed`。
- **依赖链校验（顺序不可变）**：D01（所有 SVA 基底）→ N04（归档锁，直接约束 B 案 OBSOLETE 分支）→ P1（`AUTHORIZED_DOMAIN` 法理来源）→ N16（A/B 依赖全部前项结论）。
- **会后自动启动项（表决全部落定、哈希勘录完成后）**：Testbench（40 基础转移 + 权限域越权注入 + Schema 异常注入三测试集）、SYS-DIM-BENCH 接入适配、T17–T24 判据模板、全批次自检流水线/哈希校验脚本/审计报告链路。
