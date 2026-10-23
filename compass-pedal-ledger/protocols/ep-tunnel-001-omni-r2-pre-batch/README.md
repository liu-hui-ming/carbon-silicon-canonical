# EP-TUNNEL-001-OMNI-R2 预备批次包

- 挂载链顶锚点：`5b49abe0d8806e31725f8cd8dc71f7dbc5a98903a7409318d34d554d824719aa`（R1 审阅记录回执前版本）
- 批次定级：`PRE_R2_BATCH / NOT_SEALED / NOT_APPROVED / REVIEW_REQUIRED / NOT_IMPLEMENTED / NOT_TESTED`
- 性质：提案工件，独立文件；不覆写 R1-UNIFY 主卷正文；20:00 会审表决通过后方可并入 R2 正式分支
- 来源：创立人 14:40 提交的批次包原文（本地落盘，字节忠实）

## 文件清单
| 文件 | 对应缺陷 | 状态 |
|---|---|---|
| `p0-label-patch.yaml` | P0 元标签 REQUIRED vs 正文已采用 | PENDING_2000_REVIEW |
| `dual-axis-state-machine.yaml` | P2 单链八态机解耦 | PENDING_2000_REVIEW |
| `sva_dual_axis_state_machine.sv` | P2 断言套件 | NOT_COMPILED / NOT_SIMULATED |
| `negative_result_schema.yaml` | P3 四类负结果接收字段 | PENDING_2000_REVIEW |

## 落盘时发现的原文缺陷（已就地标注，不静默改写）
1. `sva_dual_axis_state_machine.sv` 断言 1 原写作 `e_state != G_RETIRED`——跨枚举类型比较，无法编译；断言 5 `!$rose(g_state == G_RETIRED)` 语法非标准。已改为可编译形式并保留注释说明；语义待会审确认。
2. `dual-axis-state-machine.yaml` 的 `legal_state_combos` 原文存在两行粘连（`...ACTIVE    # 审阅指出的缺失合法落点EVIDENCE=CONTRADICTED, GOVERNANCE=RETIRED`），已拆分为两条独立条目。
3. 原文引用 `sm_transition_matrix.csv`，但批次未包含该文件 → 已登记 `declared_but_missing`。
4. 参考的 `a1_award_sha` 原文截短为 `b8953d5d…`，已补全为完整 SHA256。
5. layer/权限语义：本批次未包含 P1（TUN 子域注册）与层级≠终审权声明，该两项仍属 PENDING。

## 验证状态
- 未编译、未仿真、未导入状态机、未接入 SYS-DIM-BENCH。
- `NEGATIVE_RESULT` Schema 未跑校验器，`retention_policy` 与 90 天临时清理规则的冲突尚未裁决（P4 待办）。

---

## 追加勘录｜落盘校验回执与缺陷补丁提案（14:43，append-only）
- 元标记：`FALLBACK_CHECK / BATCH_DEFECT_NOTE / APPEND_ONLY`
- 双锚：`chain_top_at_ack = 5b49abe0d8806e31725f8cd8dc71f7dbc5a98903a7409318d34d554d824719aa`；`chain_top_now = 309eb6462fcc56030720aeacc4f01e01ec253b344e3cbccf5f0338088506b38c`；历史锚 `deeeb293…`/`a94cf1…` 保持 `CONTEXT_TRACE_ONLY`。
- 定级维持：`PRE_R2_BATCH / NOT_SEALED / NOT_APPROVED / REVIEW_REQUIRED / NOT_IMPLEMENTED / NOT_TESTED`。

### 缺陷签收与处置台账
| 编号 | 内容 | 创立人处置 | 本地落盘状态 |
|---|---|---|---|
| D01 | SVA 断言1 跨枚举类型比较 | 待 20:00 会审表决（方案A 删除／方案B 转编译宏门禁） | 已移除该断言，转 `dual-axis-state-machine.yaml` 的 `type_domain_isolation_note`；**最终形式待表决** |
| D02 | 断言5 `$rose` 入参语法 | ✅ 修订（引入 `g_retired_sig` 位信号，语义不变） | 已按修订版替换 |
| D03 | `legal_state_combos` 行粘连 | ✅ 排版拆分，语义不变 | 已完成 |
| D04 | `sm_transition_matrix.csv` 缺失 | ✅ 补 CSV 模板，待填充实测路径 | 已落盘（11 条转移） |
| D05 | P1 工件缺位 | ⏳ 分置于 20:00 独立提案，不入本批次 | 未落盘（按创始人口径不属本批次） |
| D06 | `retention_policy` 与 90 天清理冲突 | ✅ Schema 增补 `classification_tag` + 条件门禁 | 已增补 |

### 修订后文件（现场复算 SHA256）
- `sva_dual_axis_state_machine.sv`＝`965fd5370b6b177f01ffb1c7eafcd8eaaa7236405aec35c9761793e8a5646c99`
- `negative_result_schema.yaml`＝`3f6d1694039c007e1aea06ef16e872adc5cbb8c3f8439eac775e03f9a267e648`
- `dual-axis-state-machine.yaml`＝`3b2649d7a302f373f3a4c79bfc4982013c66335c1829d062786af0f8e22834dc`
- `sm_transition_matrix.csv`＝`14422f95718e9f7f37d51ff269356a32ce8fbbc4d899298c3e004d6dc420f672`
- `batch_meta.yaml`＝`7a7ab8def19e95f73f7915d82765b3c8db3e4caeafb9ec4613fd09abbc0aa702`
- `p0-label-patch.yaml`＝`69eae27e250c7672980aff3e69ce19686baad820b75ec16ae50878402527a42e`（未变）

### 复核中新增的独立发现（不在 D01–D06 清单内）
1. **`sm_transition_matrix.csv` 与 `legal_state_combos` 不一致**：CSV 最后三行的 `EVIDENCE_NEXT` 写作 `_`（通配），但 `dual-axis` 侧 `EVIDENCE=*, GOVERNANCE=SUSPENDED/RETIRED/ARCHIVED` 是 YAML 通配写法；CSV 未定义通配行的机器语义（展开？保持字面？），导入状态机时会歧义。
2. **CSV 缺少 `UNKNOWN → DEFINED/ESTIMATED` 的复位转移**：YAML 明确允许"UNKNOWN 可回退升级"，但转移表只有 `PROPOSED→UNKNOWN` 一条进入方向，没有出边。按表执行会得到"UNKNOWN 无法回退"的相反语义，直接违反断言3。
3. **CSV 缺少 `CONTRADICTED → RETIRED` 之外的举报/撤回路径**，以及 `ACTIVE→SUSPENDED` 的恢复边（`SUSPENDED→ACTIVE`）缺失。
4. **断言4 语义过窄**：`$past(g_state == G_ARCHIVED)` 只覆盖"进入 ARCHIVED 后一拍"，第二拍起可回落。若意图为永久不可逆，应改为 `$rose(...) |-> always (...)`。已在 `.sv` 尾部备注，不擅自改判。
5. **`classification_tag` 与 `retention_policy` 的强制关系仍是文字规则**，Schema 内无机器可校验的 `if/then`（如 JSON Schema `dependentSchemas`），当前无法自动报错。

以上 1–5 均为待会审/待实现项，未计入 D01–D06 已闭环统计。本批次仍**未编译、未仿真、未接 BENCH**。

---

## 追加勘录｜新缺陷 N01–N05 收敛补丁（14:45，append-only）
- 元标记：`NEW_DEFECT_RECONCILIATION / STATE_TRANSITION_CONSISTENCY / SCHEMA_DEPENDENCY_GATE`
- 双锚：`chain_top_at_ack = 309eb6462fcc56030720aeacc4f01e01ec253b344e3cbccf5f0338088506b38c`；`chain_top_now = fcdb31e54bd0355e…`；`index_root = 396f12c97ae56adc…`；自反盲区 `ccf733a3…` 不变。
- 归档纪律签收：提案阶段允许原地更新；转正后强制版本后缀 + 快照目录，已写入 `batch_meta.yaml` 的 `archive_discipline`。

### 落盘结果（现场复算 SHA256）
- `sm_transition_matrix.csv` v0.2（38 条全显式转移）＝`3e48ea163ebdc1768dbbb18c2b50799a098598208ca3485c9e0a48164e672775`
- `sva_dual_axis_state_machine.sv` v0.3＝`596951875c3e5fb920a9972688a98f471c48525ac87d48a207cbae30a352abd1`
- `negative_result_schema.yaml` v0.2（含 `dependent_schemas`）＝`6c0c8309ec544ebe65edbc594aa781135ff598123c45d8cdc7db7246351a31ad`
- `batch_meta.yaml`（含归档纪律与工件版本）＝`ed51aac80e193468a0b289804533f46990e3e7308ce26dc0b558e584b7df19e3`
- `dual-axis-state-machine.yaml` 未变＝`3b2649d7a302f373…`；`p0-label-patch.yaml` 未变＝`69eae27e250c7672…`

### 机器校验（本地执行，非仿真）
- CSV 枚举合法性：38/38 通过，无 `_` 通配残留。
- 冻结/解冻：`admin_suspend` 7 条、`admin_restore` 7 条，7 个证据态全覆盖，冻结不再死锁。
- 可达性 BFS（起点 `E_PROPOSED+G_ACTIVE`）：7×4=28 个状态**全部可达**。
- 终态检查：7 个 `*+G_ARCHIVED` 为唯一无出边状态，符合"归档固化"语义。

### 本次复核发现的新问题（N06 起，未纳入创立人台账）
1. **`E_CONTRADICTED+G_ACTIVE` 与 `E_REPLICATED+G_ACTIVE` 无 ACTIVE 内出边**：只能冻结/下线/归档，不能继续采集或升级到新证据态。这意味着"证伪存案、持续观测"这条本批次的核心设计**在转移表里没有落地路径**——观测只能记在新条目上，不能更新本算子的证据态。请确认是否为设计意图；若不是，需补 `CONTRADICTED→DEFINED`（新阳性证据，如上一版已写）与 `REPLICATED→CONTRADICTED`。
2. **`E_CONTRADICTED+G_ACTIVE` 有两条 `admin_retire` 分支**：`governance_vote_retire`（会审下线）与 `admin_retire`（治理主动下线）都指向 `E_CONTRADICTED+G_RETIRED`，状态对重复而触发条件不同——机器上合法（键含 TRIGGER），但审计口径上同一状态迁移由两种不同权限通道达成，需要明确二者权限等级是否等价。
3. **`negative_result_schema.yaml` 的 `dependent_schemas` 是自定义键名**：标准 JSON Schema 关键字为 `dependentSchemas`（驼峰），且其结构应为「属性名 → 子 schema」。当前写法在标准校验器（jsonschema、ajv）中会被当作未知关键字**静默忽略**，机器强校验实际仍未生效。建议改为：
   ```yaml
   dependentSchemas:
     classification_tag:
       properties:
         classification_tag:
           const: FORMAL_EVIDENCE
       then_required: ...
   ```
   更稳妥的做法是直接写 `allOf` + `if/then`。
4. **`classification_tag` 未加入 `required_fields`**：虽然 `field_definition` 有默认值 `FORMAL_EVIDENCE`，但缺失字段时校验器不会强制，等于把"默认值"当成了"必填"。建议加入 `required_fields`。
5. **SVA 断言4 的 `always` 用法**：`$rose(...) |-> always(g_state == G_ARCHIVED)` 在 SVA 中 `always` 不是标准序列算子（标准为 `s_always` 或 `[*0:$]`）。若走 SystemVerilog 2017，应写 `s_always[1:$] (g_state == G_ARCHIVED)`；否则多数工具报语法错误。此外，一旦进入 ARCHIVED，该断言在当前时钟域内要求永久成立——与 `negative_result_schema` 的"归档后仍可追加勘录"并不冲突（后者是记录层，不影响状态位），但需在会审时讲清。
6. **CSV 的 `LEGAL` 列恒为 1**：没有非法转移样本行，也没有 `0` 行来声明"哪些转移非法"。若导入脚本依赖白名单，则不需要；若依赖显式拒绝，则缺黑名单。当前语义下"表内即合法"，未列出的即为非法——建议在 README 里写死这个解释，否则不同实现会分叉。

以上 1–6 均为新发现，未计入 N01–N05 的闭环统计。本批次仍**未编译、未仿真、未导入状态机、未接 SYS-DIM-BENCH**。

---

## 追加勘录｜N06–N11 收敛补丁 + P1 提案落盘（14:47–14:49，append-only）
- 元标记：`SEMANTIC_TRADEOFF / SCHEMA_COMPAT_FIX / SVA_STD_FIX / GOVERNANCE_RIGHTS_DEMARCATION`
- 双锚：`chain_top_at_ack = fcdb31e54bd0355e…`；`chain_top_now = 14a588f00e75f6b8…`；`index_root = f8649e4912ec20b4…`。

### 创立人两项前置决议（已照录并执行）
- 决议1（N06）：常态观测=追加 result 条目不动算子主状态；仅颠覆性证据触发跃迁。CSV 已补 `CONTRADICTED→DEFINED`(new_positive_evidence)、`REPLICATED→CONTRADICTED`(conflicting_observation)。
- 决议2（N07）：权限不等价。`governance_vote_retire`→`G_RETIRED`（终审）；`admin_retire`→`G_SUSPENDED`（紧急冻结）。CSV 已改：7 条 `admin_retire` 全部改指 `G_SUSPENDED`，`governance_vote_retire` 唯一通向 `G_RETIRED`。

### 落盘结果（现场复算 SHA256）
- `sm_transition_matrix.csv` v0.3（40 条，头部白名单契约）＝`39134c5d76779f7f8e6de370a9eba9ac4eb808daed2d16f76b509a3bfad61a8c`
- `sva_dual_axis_state_machine.sv` v0.4＝`da3afa2a762ff2663cf8b4e0550014e002546825212867f900b56d3eee249b17`
- `negative_result_schema.yaml` v0.3（allOf 条件 + classification_tag 入必填）＝`a9927b8ecd4c9db0a34d1c4ec08b1dfe1e987b471374edd2bf43b6343214cc56`
- `tun-subdomain-registration-and-authority-declaration.yaml` v0.1＝`a6a0699e36913c2e3abaa7f9c827a6bbd6c24f66861db33352dcbd4381e5d302`
- `batch_meta.yaml`＝`7a39f421d8a9c5636f1f99772854c4f8b8eb1a9ed58736f92ba187a5b06fe42d`

### 落盘时对原提案的必要校正（未改语义）
1. 原文 `rose(...)` 缺 `$`、`s_always[1:]` 缺 `$`：已按 SV 1800-2017 补全为 `$rose` 与 `s_always [1:$]`，注释留痕。
2. N11 契约以 `#` 注释行写入 CSV 头；导入脚本须跳过 `#` 行。

### 机器校验（本地执行，非仿真）
- 枚举合法 40/40，无通配残留；重复键 0。
- 从 `E_PROPOSED+G_ACTIVE` BFS：**12 个状态不可达**——除 `E_CONTRADICTED` 外，其余 6 个证据态的 `+G_RETIRED` 与 `+G_ARCHIVED` 全部不可达（治理轴 `admin_retire` 改指 SUSPENDED 后，全表仅 `governance_vote_retire` 一条入 RETIRED 的边，且仅限 CONTRADICTED 起点）。
  - 语义后果：**当前表内只有"已证伪"的算子能被下线/归档**。`REPLICATED` 或 `ESTIMATED` 状态的算子即使治理上要下线，也没有合法路径，只能靠先制造一条 CONTRADICTED 观测。若这不是意图，需为会审补 `governance_vote_retire` 对全部 ACTIVE 状态的边，或新增会审表决事件；若是意图（"只有证伪才可下线"），请在 YAML 文档层写明此强约束。
- `E_CONTRADICTED+G_ACTIVE` 现有 4 条出边（恢复跃迁/终审/双冻结通道），无死锁。
- 无出边状态仅剩 7 个 `*+G_ARCHIVED`（符合归档固化）。

### 新标注问题（N12 起）
- N12：`admin_retire` 与 `admin_suspend` 现为**同源同目标的重复边**（ACTIVE→SUSPENDED，仅注释不同）。机器无碍，但二者权限语义若不同（紧急 vs 常规），目标状态应区分或加时间窗（紧急冻结须限时复核），否则是一物两名。
- N13：`negative_result_schema.yaml` 的 `allOf` 仍为**自造顶层键**，不是 JSON Schema 文档的 `properties/allOf` 结构——本文件是 YAML 描述而非可直接校验的 JSON Schema 文档。若要真机校验，需另出 `negative_result.schema.json`（`type: object` + `required` + `allOf`）转换层；当前 v0.3 改善了结构，但"AJV 可校验"仍不成立。
- N14：P1 声明与 CSV 的对齐缺口——声明禁止 L3 直接触发 `G_RETIRED`，但 CSV 中 `governance_vote_retire` 未绑定权限域字段，导入器无法判"是谁触发的"。需在 CSV 增列 `AUTHORIZED_DOMAIN` 或在导入器外部做权限前置检查。

以上 N12–N14 未计入 N06–N11 闭环统计。批次仍 `PRE_R2_BATCH / NOT_SEALED / NOT_APPROVED / NOT_IMPLEMENTED / NOT_TESTED`；未编译、未仿真、未接 BENCH。

---

## 追加勘录｜N12–N14 收敛 + 「仅证伪可下线」口径固化（14:51，append-only）
- 元标记：`ACCESSOR_BINDING / SCHEMA_SHIM_LAYER / TRIGGER_DOMAIN_TAG / SEMANTIC_GATE_LOCK`
- 双锚：`chain_top_at_ack = 14a588f00e75f6b8…`；`chain_top_now = 2fea300339d92b68…`；`index_root = f8649e4912ec20b4…`。

### 前置会审决议（已照录并固化）
- **决议A（语义锁）**：仅进入 `E_CONTRADICTED` 证伪态的算子，才允许走 `governance_vote_retire` 终审下线链路。`E_REPLICATED`/待验证/未知态**不提供直接终审下线通道**。治理侧若要关停稳定有效算子，须先提交冲突观测驱动状态进入 CONTRADICTED，再启动会审表决。此为本体系「证伪优先」核心治理规则，不做宽松兼容分支。已写入 CSV 头部 `Semantic Lock` 注释。
- **决议B（元数据分层）**：`admin_suspend`（常规冻结，无强制复核时限）与 `admin_retire`（紧急冻结，携带 `urgent_flag=true` + `mandatory_review_deadline`）目标同为 `G_SUSPENDED`；语义差异由外部元 payload 承载，状态机主转移层不分叉。超时未复核→审计告警，不自动解冻、不自动下线。

### 落盘结果（现场复算 SHA256）
- `sm_transition_matrix.csv` v0.4（40 条，新增 `AUTHORIZED_DOMAIN` 列）＝`39134c5d…`→见下复算
- `negative_result.schema.json`（N13 Shim 层，draft 2020-12）＝首版新建

### 机器校验（本地执行）
- 40/40 行枚举与权限域枚举合法；权限域违规 0（`admin_*` 全挂 `ADMIN_EMERGENCY`，`governance_vote_retire`/`archive_job` 全挂 `CROSS_LAYER_REVIEW_BOARD`，观测类挂 `OBSERVER`/`META_VALIDATION_L3`）。
- **语义锁验证通过**：全表通向 `G_RETIRED` 的边仅 1 条（`E_CONTRADICTED+G_ACTIVE` ← `governance_vote_retire` ← `CROSS_LAYER_REVIEW_BOARD`）；从非 CONTRADICTED 起点通向 RETIRED 的边为 0。决议A 已在表内机器可验证。
- **N13 Shim 实测**：用 `jsonschema` Draft202012Validator 校验——合法样本通过；`FORMAL_EVIDENCE + retention_policy=TEMP` 被正确拒绝（`'PERMANENT' was expected`）。N05/N08/N13 门禁首次真正生效。

### 新标注（N15–N16）
- N15：`AUTHORIZED_DOMAIN` 由我按 P1 权限矩阵映射填充，**非创立人逐行确认**。映射规则：观测/建立类→`META_VALIDATION_L3`，冲突/反证类→`OBSERVER`，治理表决/归档→`CROSS_LAYER_REVIEW_BOARD`，冻结/解冻/紧急冻结→`ADMIN_EMERGENCY`（分布 8/3/8/21）。若 P1 会审通过时权限归属有调整，本列须整列重生成，不能局部打补丁。
- N16：`archive_job` 现同时要求 `CROSS_LAYER_REVIEW_BOARD` 且起点为 `G_RETIRED`，而进入 `G_RETIRED` 又只能经 CONTRADICTED。故全链唯一归档路径为：`CONTRADICTED+ACTIVE →(会审) RETIRED →(会审) ARCHIVED`。这是决议A 的直接推论，可在会审时作为"治理收敛度"证据，但也意味着 `G_ARCHIVED` 无法通过其他路径到达——档案完整性上需要注意：非证伪算子永久停在 ACTIVE/SUSPENDED，不能归档。

批次仍 `PRE_R2_BATCH / NOT_SEALED / NOT_APPROVED / NOT_IMPLEMENTED / NOT_TESTED`；未编译、未仿真、未接 BENCH。

---

## 追加勘录｜创立人授权域权威行接收（14:51:45）
- N15 **已解决**：创立人逐行给出 `AUTHORIZED_DOMAIN` 权威值，替换助手临时映射。CSV v0.4 已按创立人行覆写。
- 创立人口径与助手临时映射的差异（5 处）：`user_declare`、`measurement_sample`、`controlled_test`、`new_positive_evidence`、`sufficient_evidence_arrive` → **OBSERVER**（助手原判 META_VALIDATION_L3）；`independent_repeat`、`conflicting_observation`（两条）→ **META_VALIDATION_L3**（助手原判 OBSERVER）；`reset_reinit` → **ADMIN_EMERGENCY**（助手原判 META_VALIDATION_L3）。语义要点：观测采集类归 OBSERVER，推导/冲突判定类归 META_VALIDATION_L3，重置类归 ADMIN_EMERGENCY。
- `sm_transition_matrix.csv` 当前 SHA256：`ead7f6da32ed868cdf7635821a275321a46a7a1364687503731a226e89d8545c`；校验 40/40 合法，权限域分布 22/8/5/5，语义锁保持（通向 G_RETIRED 的边仅 1 条，起点唯一 CONTRADICTED）。

## 新标注（N17）
- 创立人随附的 `negative_result.schema.json` 文本在传输中被截断（止于 `"version": "v0.`），且其 `$schema` 为 **draft-07**；盘上现存文件为助手版 **draft 2020-12**（`b3064b84d4eb0653…`，已实测拦截违规条目）。draft-07 与 2020-12 均可被 AJV/jsonschema 校验，`allOf/if/then` 两者通用。待创立人补发完整 draft-07 版或确认采用 2020-12 版；确认前盘上文件不替换，双锚（yaml↔json SHA256）待版本确定后同步登记。

---

## 追加勘录｜N12–N14 补丁回执与 draft-07 Shim 确权（14:52，append-only）
- 元标记：`ACCESSOR_BINDING / SCHEMA_SHIM_LAYER / TRIGGER_DOMAIN_TAG / SEMANTIC_GATE_LOCK`
- 创立人回执台账照录：N12 ✅（常规/紧急冻结区分，时效标记剥离外部元 payload）；N13 ✅（独立 JSON Schema Shim）；N14 ✅（CSV AUTHORIZED_DOMAIN 列）；语义决议 ✅（仅 E_CONTRADICTED 可终审下线归档，证伪优先）。
- 待会审表决清单：D01（断言1取舍）、N04（s_always 永久锁定语义是否启用）；"本批次全部工件合批放行"以会审表决为准。

### N13 Shim 最终版：draft-07（创立人全文接收完整版）
- `negative_result.schema.json` 已替换为创立人 draft-07 全文，当前 SHA256 `3835c8a5121e77a83ae43520952847138f883395ad23e150fb08cd36c2ee0b68`。
- 双向锚定登记：YAML 卷宗版 `negative_result_schema.yaml`＝`a9927b8ecd4c9db0a34d1c4ec08b1dfe1e987b471374edd2bf43b6343214cc56` ⇄ JSON 机器校验版 `3835c8a5…`（YAML 为人类可读卷宗，JSON 为校验入口；改其一必同步勘录另一哈希）。
- Draft7Validator 真机实测（本机 jsonschema）：
  - `FORMAL_EVIDENCE + PERMANENT` → 通过
  - `FORMAL_EVIDENCE + TEMP` → **拒绝**（门禁生效）
  - `TRIAL_RUN + TEMP` → 通过（弱绑定正确）
  - `negative_type` 非法枚举 → 拒绝
- 真机校验统计：N17 关闭（draft 版本确权完成，采用 draft-07）。盘上曾短暂存在的 2020-12 中间版（`b3064b84d4eb0653…`）仅为过渡工件，已被创立人版覆盖，属提案阶段原地更新，归档时按 archive_discipline 快照化。


---

## 追加勘录｜N16 会审议案包产出（14:54）
- 依创立人要求，N16 两套方案已整理为可直接上会的**状态机边定义 + 权限域配置**文本，独立目录 `review-n16/`，不入主 CSV。
- `n16-plan-a-strict.yamlish`：零新增边、零新增状态、1 条 SVA（`a_optionA_no_stable_archive`）、权限域沿用创立人权威版映射。
- `n16-plan-b-obsolete-branch.yamlish`：新增治理态 `G_OBSOLETE`、8 条边、4 条黑名单、3 条 SVA（含 `a_optionB_retired_path_unchanged` 复核语义锁未被放宽）。
- 静态图核验：A 案非证伪态通向 RETIRED/ARCHIVED 边数 0；B 案叠加后 48 边，`OBSOLETE→RETIRED` 边数 0、非 CONTRADICTED 起点通向 RETIRED 边数 0，不可达集合与设计意图一致。
- 关键依赖提示：**N16-B 与 N04 互相约束**——若 N04 采用 `s_always` 永久锁，则 OBSOLETE→ARCHIVED 后不可复活；若需复活，须先否 N04。按创立人建议顺序表决：D01 → N04 → P1 → N16。
- 两案 `fail_closed = true`，未决即不生效；主 CSV 未改动。
