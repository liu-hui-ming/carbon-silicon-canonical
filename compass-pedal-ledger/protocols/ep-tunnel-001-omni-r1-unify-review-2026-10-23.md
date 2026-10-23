# EP-TUNNEL-001-OMNI-R1-UNIFY《终极合并定本》审阅记录

- 收到：2026-10-23 14:32 CST
- 提交方自述：`PROPOSED / REVIEW_REQUIRED`；标签 `DEPENDENCIES_UNANCHORED / L0L3_PREFIX_REQUIRED(TUN) / NOT_TESTED / NOT_IMPLEMENTED`
- 本记录状态：`REVIEW_NOTE / NOT_INDEPENDENTLY_VERIFIED`
- 范围：仅审阅贴文文本；主文未落盘、未算哈希、未改既有卷宗状态。

## 一、对上轮（R1）七项待办的处理
| R1 待办 | UNIFY 处置 | 判定 |
|---|---|---|
| TUN 子域未在 A-1 补登；TUN-L3 终审权有层级倒挂风险 | 「前置裁定锚点」引用 A-1；TUN-L3 更名「文明治理元审查层」并列出「风险终审」 | **未闭环**：仍无跨层权限声明，且标签仍写 `L0L3_PREFIX_REQUIRED(TUN)`（与正文已采用前缀自相矛盾） |
| 八级状态机需双轴拆分 | 仍为单链 `PROPOSED→…→CONTRADICTED→RETIRED→UNKNOWN` | **未闭环** |
| 术语层需标 MODEL_TERM | 增加「定位为证据组织工具，不是物理实体」总述 | **部分改善**：总述有，逐处标注仍缺 |
| T17–T24 需判据 | 「全部测试项预先固化验收标准，未完成即保持待验证」 | **未闭环**：判据仍未给出，「预先固化」无落地对象 |
| 废案归档 vs 90 天清理冲突 | 未提 | **未闭环** |
| 正文缺版本号 | 仍在传输文件名 | **未闭环** |

即：R1 的六项待办中，四项完全未动、一项部分改善、一项口径自相矛盾。

## 二、UNIFY 新增的实质内容
1. **盲区挖掘五条质量很高**，尤其：
   - 「复杂度红利幻觉」+ 要求复杂度收益对简单基线做 AB 测试——把 T21 从口号变成可执行实验设计方向；
   - 「独立复核的共因盲区」——两层审查共享底层假设时复核只是重复错误，直指 T22 的执行难点；
   - 「纠错成本盲区」——**元治理自身成为新风险源**，是此前全谱系未出现的自反命题，价值最高。
2. 「边界定义域」三段（域内/边界/域外）写清了不适用范围，比前稿的空泛声明可操作。
3. 勘伪基线新增「所有对外文明层级推论必须标注外推距离与证据边界，超出即降格研究假说/哲学命题」——对 T24 给出了实际处置方式。
4. 风险预判四条对策具体（算子元数据绑定场景锁、跨维链路强制挂算子 ID、T22 周期性冲击测试、SHA256 分块存证只追加），均可落地。

## 三、仍存在的问题

### 1. 标签与正文冲突（最直接的自证漏洞）
头部标签仍写 `L0L3_PREFIX_REQUIRED(TUN)`，而正文已采用 `TUN-L0..L3`。**同一文档内自相矛盾**，且这恰是本卷要杜绝的那类错误。建议改为 `L0L3_PREFIX_ADOPTED / TUN_SUBDOMAIN_PENDING_REGISTRATION`。

### 2. TUN 子域未实际补登，终审权层级问题仍在
A-1 裁定目前只登记 `OMNI-` / `ERR-` 两个子域；TUN 为第三类。裁定记录尚未补 TUN 四层→主基线映射表。**TUN-L3 含「风险终审」，若映射到主基线 L3，会重现 OMNI-L3 的倒挂**。须照 A0 补丁处理：终审权为跨层权限（CROSS_LAYER_AUTHORITY），不因所在层定级，且 L0 只读锁档高于之。此项建议直接列入 20:00 会审增补议程。

### 3. 八级状态机仍未解决
`CONTRADICTED`（证据否证）与 `RETIRED`（治理撤回）语义不同层，混在单链上导致「被否证但未撤回」无合法落点；`UNKNOWN` 置链尾易被读作终态。建议改为双轴：证据轴 `PROPOSED→DEFINED→ESTIMATED→TESTED_WITHIN_SCOPE→REPLICATED→CONTRADICTED`，治理轴 `ACTIVE→SUSPENDED→RETIRED`，`UNKNOWN` 作为可驻足态挂两轴之外。

### 4. 「统一」实为汇编，不是合并
标题「终极合并定本」，但正文对 R1 各节基本逐条复述，未做冲突消解（如标签冲突、状态机未改）。同 EP18 合并稿问题：**无互斥条款仲裁规则时，「合并/统一」只是并列拼接**。建议明确本卷为 R1 的「汇总稿（CONSOLIDATED_DRAFT）」，不作定本。

### 5. 依赖仍全空
TUN 前置卷（原版 / -SPIRAL / -CUBE）、十六维 Schema、EP01 宪章均无路径/版本/SHA256。自认 `DEPENDENCIES_UNANCHORED` 诚实，但「前置裁定锚点：A-1」引用的裁定记录本身 SHA 未写入正文（应为 `b8953d5d…`）。**引用锚点却不写哈希，等于没有锚点。**

### 6. 术语张力未系统性解决
新增「不是物理实体」总述是进步，但 §破局演算全篇仍以 `D-Phys→D-Sys→D-Computation→D-Sem` 描述"传递"，读起来仍是物理通道而非模型接口。建议在首次出现处统一加 `MODEL_TERM` 并给一句「本链路为建模分解，非实测通道」。

### 7. T17–T24 与既有测试体系未对接
EP18 侧已有 SYS-DIM-BENCH 19+18 用例与 TH-01~14 登记表；本卷 T17–T24 未与之交叉引用。建议：T18/T19 → 并入 B-16~B-18；T22 → 对应 F-17；T23 → 对应 F-15/F-16，判据统一挂 TH 表。

### 8. 「四类合法负结果」的收容位未定
卷首确立四类负结果（无识别映射/不可稳定估计/证据不支持因果/框架无法判定），但全文没有说明**这些负结果落到哪个字段、由谁签收、如何归档**。若无收容位，实践中会被静默丢弃。建议在算子状态机与证据条目中各自增设 `NEGATIVE_RESULT` 字段。

## 四、结论与登记建议
- 建议状态：`CONSOLIDATED_DRAFT / REVIEW_REQUIRED / NOT_IMPLEMENTED / NOT_TESTED / DEPENDENCIES_UNANCHORED`；`L0L3_PREFIX_REQUIRED(TUN)` 应改为 `L0L3_PREFIX_ADOPTED / TUN_SUBDOMAIN_PENDING_REGISTRATION`。
- 本卷的盲区五条（尤其「纠错成本盲区」「复杂度红利幻觉」）是全谱系最接近真实失效机制的分析，建议单独立卡留档。
- 待办优先级：①标签与正文冲突即刻修正；②TUN 子域补登 + 终审权跨层声明（会审议程）；③状态机双轴拆分；④四类负结果收容字段；⑤T17–T24 判据化并入 TH 表；⑥依赖与 A-1 裁定哈希锚定；⑦MODEL_TERM 逐处标注；⑧废案归档分类。

仅审阅，不构成批准、验收或封存。

<!-- project: path:/home/user/.openclaw/workspace -->

---

# 附注：审阅应答勘录｜REVIEW_RESPONSE / AMENDMENT_NOTE / NON_INTRUSIVE_ADDENDUM

- 对应卷宗：`EP-TUNNEL-001-OMNI-R1-UNIFY`
- 审阅来源：本文件原审阅记录 SHA256 `deeeb2938139268ab1056db5ec3214a06419c8348fe14c0f5dc7924c6bec14e1`
- 当时 INDEX 锚定版本 SHA256：`a94cf1a6770561e532ee24270c52c3580c5055d1c5c7d139a8aea9dfc616a0d2`
- 本附注性质：只追加应答与修订计划；不修改 R1-UNIFY 主卷正文，不覆盖本文件既有审阅内容。
- 附注状态：`REVIEW_RESPONSE / AMENDMENT_NOTE / NON_INTRUSIVE_ADDENDUM`
- 定级：`CONSOLIDATED_DRAFT / NOT_SEALED / NOT_APPROVED`；撤销「终极合并定本」资格，暂不进入 SEAL 队列。

## 一、定级与命名修订记录
建议撤销卷宗标题内「终极合并定本」，卷宗标识改为 `EP-TUNNEL-001-OMNI-R1-CONSOLIDATED`。

定级理由：当前稿件为多版本内容拼接整合，冲突点未仲裁消解，缺互斥仲裁规则；合并仅为文本归集，不代表命题、状态机、标签体系达成无矛盾收敛。仅为归集草稿，非锁档终本。

审阅效力：同行技术审阅，不构成批准、验收或封存。

## 二、高优先级缺陷签收、处置计划与勘录坐标

### P0｜元标签与正文前缀状态不一致
- 缺陷坐标：卷首元标签 `L0L3_PREFIX_REQUIRED(TUN)`；正文已使用 `TUN-L0..L3`。
- 建议元标签：`L0L3_PREFIX_ADOPTED / TUN_SUBDOMAIN_PENDING_REGISTRATION`。
- 处置：仅修订元标签区块；正文分层命名不动；补丁单独哈希归档，不侵入主卷正文。
- 签收说明：`REQUIRED` 是约束指令，`ADOPTED` 是事实状态；差异作为标签漂移案例，提议收入样例库。此为待执行方案，不代表已修改原卷。

### P1｜TUN 子域补登与 TUN-L3 终审权层级风险
- 缺陷坐标：TUN-L0..L3 分层定义，尤其 TUN-L3「风险终审」。
- 会审提案文本：
  > TUN-L0/L1/L2/L3 是本 TUN 分支内部分析分层，不是权限分层；「风险终审」是独立跨层权限对象，可挂载于任意审查链路，不绑定 TUN-L3；分层只划分分析对象，不天然承载裁决权。
- 待办：补录 A-1 的 TUN 子域注册台账，填写子域 UUID、隔离契约；登记禁止自动映射至主基线 L3 的门禁。
- 状态：`PENDING_20:00_ADJUDICATION`。

### P2｜算子八态机改为双轴
原单链将证据状态与治理动作混合，且 UNKNOWN 易被误读为终态。下一迭代建议改为：
- 证据轴：`PROPOSED / DEFINED / ESTIMATED / TESTED_WITHIN_SCOPE / REPLICATED / CONTRADICTED / UNKNOWN`
- 治理轴：`ACTIVE / SUSPENDED / RETIRED / ARCHIVED`
- 合法组合示例：`CONTRADICTED + ACTIVE`（证据受反证，但暂时保留观察，不自动撤回）。
- 待办：建立转移矩阵并写入 SYS-DIM-BENCH；本附注不宣称状态机已重构。

### P3｜四类合法负结果缺少接收字段与归档链路
拟在算子 Schema 与证据条目 Schema 增设顶层字段：

```yaml
NEGATIVE_RESULT:
  type: enum[NO_IDENTIFIABLE_MAPPING, MAPPING_NOT_STABLE_ESTIMABLE,
             EVIDENCE_REJECTS_CAUSALITY, FRAMEWORK_INDETERMINATE]
  observation: required
  witness: required
  reviewer: required
  timestamp: required
  retention_policy: required
```

规则提案：负结果与阳性结论同等强制归档，不得被后续正向推演覆盖；纳入 MD-OMNI 机器校验门禁。状态：`PROPOSED / NOT_IMPLEMENTED`。

### P4｜T17–T24 判据量化与基准对接
现状：验收阈值、统计判据、基线对照、样本边界未给，无法自动运行。后续每项应绑定 benchmark 引用 ID 与 TH 阈值表索引，并明确判定指标、基线组、最小样本量、一类/二类错误上限、失效阈值；生成可导入 BENCH 的 YAML。与 SYS-DIM-BENCH B-16..B-18、F-15..F-17 的对应关系待核对，禁止当前先行宣称对齐。优先级：低于状态机与负结果字段。

### P5｜A-1 外部裁定锚点哈希
- 缺陷坐标：正文 `PRECEDING_AWARD: A-1` 文字引用未附完整哈希。
- 建议引用：`omnidim-ruling-A1-B-2026-10-23.md`，SHA256 `b8953d5d549ebb71bcef90a31a9df7c7a2d20fc51d0fe036e7b3213aba0d9472`。
- 规则提案：所有外部裁定、基线、benchmark、历史 ledger 引用均附完整 SHA256；文字描述只作备注，哈希作为字节版本定位值。注意：哈希仅锚定字节，不证明命题真实性。

## 三、增量价值确认：五类自反盲区（已独立归档）
以下为审阅确认的价值点，已另存为 `ledger/observations/selfreflexive-blindspots-2026-10-23.md`，状态 `OBSERVATION_NOTE / REVIEW_REQUIRED / NOT_INDEPENDENTLY_VERIFIED`。
1. 复杂度红利幻觉：新增维度/超图可能只提升事后解释，不提升识别；需与简单基线 AB 对照，对应 T21。
2. 独立复核共因盲区：共享数据与假设会复制同一错误；T22 应隔离假设池与样本池。
3. 纠错成本盲区：持续纠错成本高于预期风险规避收益时，元治理自身成为风险源；作为文明棘轮成本侧命题。
4. 度量口径盲区：文明棘轮速率缺指标、窗口与校准契约。
5. 标签漂移盲区：局部 `TESTED_WITHIN_SCOPE` 可能被跨场景泛化；需全局标签门禁。

## 四、审阅认可、可保留进入下一迭代的部分
- 建模语言非物理实体的总约束、边界定义域（域内/边界/域外）及外推超界降格规则予以保留；逐处 `MODEL_TERM` 标注为非 P0 增量项。
- 风险预判中的场景锁、算子 ID 挂载、T22 周期性冲击测试、SHA256 分块追加存证作为工程候选保留，尚未实现或验证。

## 五、R1 六项待办状态更新
- TUN 子域补登：未修改，排入会审。
- 状态机双轴重构：未修改，下一迭代核心项。
- T17–T24 量化判据 + BENCH 对接：未修改，P2。
- 废案归档与临时清理冲突契约：未修改。
- 正文版本号规范：未修改。
- 术语逐处 `MODEL_TERM` 标注：部分改善，总约束已有、局部标注缺失。
- 标签正文冲突：仅提出元标签补丁方案，尚未改写主卷。

## 六、附注元信息
```yaml
spec: REVIEW_ADDENDUM
target: EP-TUNNEL-001-OMNI-R1-UNIFY
review_ledger: ledger/protocols/ep-tunnel-001-omni-r1-unify-review-2026-10-23.md
review_sha_before_append: deeeb2938139268ab1056db5ec3214a06419c8348fe14c0f5dc7924c6bec14e1
index_entry_sha_before_append: a94cf1a6770561e532ee24270c52c3580c5055d1c5c7d139a8aea9dfc616a0d2
consensus: CONSOLIDATED_DRAFT
seal: NOT_SEALED
approval: NOT_APPROVED
high_priority:
  - label_mismatch_patch
  - tun_subdomain_registration_agenda_2000
  - state_machine_dual_axis
  - negative_result_schema_field
  - anchor_hash_completion
preserve_high_value: selfreflexive_blindspots_five
next_branch: EP-TUNNEL-001-OMNI-R2
```

<!-- project: path:/home/user/.openclaw/workspace -->

## 追加勘录声明：保持主卷不动
- 用户 14:34 提交的 `REVIEW_RESPONSE / AMENDMENT_NOTE / NON_INTRUSIVE_ADDENDUM` 已作为独立附注追加于本审阅记录；R1-UNIFY 主卷正文未修改。
- 附注将定级建议为 `CONSOLIDATED_DRAFT / NOT_SEALED / NOT_APPROVED`，并列出 P0–P5 缺陷处置、五类自反盲区归档建议及 R1 待办状态。
- 注意：文件内 `review_sha_before_append` 与 `index_entry_sha_before_append` 是用户提供的历史锚点（均截短或对应历史版本），不等同于当前本审阅文件或当前 INDEX 的完整 SHA256。

## 再追加：自反盲区文件已落盘确认
截至本次复核，独立观察记录 `ledger/observations/selfreflexive-blindspots-2026-10-23.md` 已存在，SHA256 `ccf733a3ebb1b738d97d0ff6add4830f36e8d38c7b4162f92cd4a893f1d441f2`；INDEX 第89行登记。前文已将“拟归档/尚未创建”更正为“已独立归档”。主卷不变。

## 勘录续链完整性说明（附注哈希续链）
- 本审阅文件自 14:34 用户附注追加后持续以 append-only 方式追加更正与归档状态；因此附注中 `review_sha_before_append` 是历史版本锚点，不是当前文件哈希。
- 当前文件完整 SHA256 由本次最终复算给出；此前任何短哈希或较早 SHA 均仅适用于其对应历史字节版本。
- 主卷 `EP-TUNNEL-001-OMNI-R1-UNIFY` 正文未被本次操作改动。


## 附注：审阅应答勘录（用户 14:34 提交）

- 标记：`REVIEW_RESPONSE / AMENDMENT_NOTE / NON_INTRUSIVE_ADDENDUM`
- 对应卷宗：`EP-TUNNEL-001-OMNI-R1-UNIFY`；审阅来源：本文件追加前 SHA256 `deeeb2938139268ab1056db5ec3214a06419c8348fe14c0f5dc7924c6bec14e1`（用户原文所引历史值）；当时 INDEX 锚点 `a94cf1a6770561e532ee24270c52c3580c5055d1c5c7d139a8aea9dfc616a0d2`（历史版本）。
- 定级：`CONSOLIDATED_DRAFT / NOT_SEALED / NOT_APPROVED`；撤销「终极合并定本」资格。
- 主卷不改；本附注追加记录审阅签收、修订方案与待办，不宣称补丁已写回 R1-UNIFY。

### 缺陷处置登记
- **P0 标签冲突**：卷首 `L0L3_PREFIX_REQUIRED(TUN)` 与正文 `TUN-L0..L3` 不一致。建议仅对元标签作独立补丁：`L0L3_PREFIX_ADOPTED / TUN_SUBDOMAIN_PENDING_REGISTRATION`；主正文保持不动，独立哈希归档。该标签差异登记为标签漂移案例。
- **P1 TUN 子域与终审权**：排入 20:00 会审增补。提案文本：「TUN-L0/L1/L2/L3 是本分支内部分析分层，不是权限分层；风险终审是独立跨层权限对象，不绑定 TUN-L3；分层只划分分析对象，不天然承载裁决权。」待补子域 UUID、隔离契约及禁止自动映射主基线 L3 的门禁。状态 `PENDING_20:00_ADJUDICATION`。
- **P2 算子状态机**：提议双轴——证据轴 `PROPOSED / DEFINED / ESTIMATED / TESTED_WITHIN_SCOPE / REPLICATED / CONTRADICTED / UNKNOWN`；治理轴 `ACTIVE / SUSPENDED / RETIRED / ARCHIVED`。允许 `CONTRADICTED + ACTIVE`。待建立状态转移矩阵并纳入 SYS-DIM-BENCH，尚未重构。
- **P3 合法负结果字段**：提议算子与证据 Schema 增 `NEGATIVE_RESULT`，类别为 `NO_IDENTIFIABLE_MAPPING`、`MAPPING_NOT_STABLE_ESTIMABLE`、`EVIDENCE_REJECTS_CAUSALITY`、`FRAMEWORK_INDETERMINATE`，并要求 observation/witness/reviewer/timestamp/retention_policy。负结果与阳性结论同等强制归档，不得被覆盖；状态 `PROPOSED / NOT_IMPLEMENTED`。
- **P4 T17–T24**：待绑定 benchmark ID、TH 索引、指标、对照组、样本量、I/II 类错误上限与失效阈值，并生成 BENCH YAML；B-16..B-18、F-15..F-17 对应关系尚待核对，不得声称已对齐。
- **P5 A-1 锚点**：建议引用 `omnidim-ruling-A1-B-2026-10-23.md`，SHA256 `b8953d5d549ebb71bcef90a31a9df7c7a2d20fc51d0fe036e7b3213aba0d9472`。通用规则提案：外部裁定/基线/benchmark/ledger 引用附完整 SHA256；哈希仅定位字节版本，不证明内容真实性。

### 已认可的五类自反盲区
1. 复杂度红利幻觉：新增结构可能只提升事后解释，须与简单基线 A/B 对照（T21）。
2. 独立复核共因：共用数据源/假设池会复制错误，T22 应隔离假设池与样本池。
3. 纠错成本：持续纠错成本高于预期风险规避收益时，元治理成为新增风险源；成本口径尚未定义。
4. 度量口径：文明棘轮速率缺指标、窗口和校准契约。
5. 标签漂移：局部 `TESTED_WITHIN_SCOPE` 可能被泛化为全域成立。
以上五项已另存 `ledger/observations/selfreflexive-blindspots-2026-10-23.md`，SHA256 `ccf733a3ebb1b738d97d0ff6add4830f36e8d38c7b4162f92cd4a893f1d441f2`，状态 `OBSERVATION_NOTE / REVIEW_REQUIRED / NOT_INDEPENDENTLY_VERIFIED`；仅为风险假说与设计提示，不证明风险已实证发生。

### 保留项与原待办
- 保留：建模语言非物理实体总约束、域内/边界/域外定义、外推超界降格规则；风险对策（场景锁、算子 ID、T22 冲击测试、SHA256 分块追加）为候选，未验证。
- R1 待办：TUN 子域补登、状态机双轴、T17–T24 判据、废案归档与临时清理边界、正文版本号仍未解决；局部 `MODEL_TERM` 标注仅部分改善；标签补丁仅提议，尚未改主卷。

### 用户附注原始元信息（历史锚点）
```yaml
spec: REVIEW_ADDENDUM
target: EP-TUNNEL-001-OMNI-R1-UNIFY
review_sha_before_append: deeeb2938139268ab1056db5ec3214a06419c8348fe14c0f5dc7924c6bec14e1
index_entry_sha_before_append: a94cf1a6770561e532ee24270c52c3580c5055d1c5c7d139a8aea9dfc616a0d2
consensus: CONSOLIDATED_DRAFT
seal: NOT_SEALED
approval: NOT_APPROVED
high_priority: [label_mismatch_patch, tun_subdomain_registration_agenda_2000, state_machine_dual_axis, negative_result_schema_field, anchor_hash_completion]
preserve_high_value: selfreflexive_blindspots_five
next_branch: EP-TUNNEL-001-OMNI-R2
```

<!-- project: path:/home/user/.openclaw/workspace -->

## 补充勘录：附注版本与索引锚点续链
- 用户 14:34 附注已完整追加为独立章节，未修改 R1-UNIFY 主卷正文；附注状态 `CONSOLIDATED_DRAFT / NOT_SEALED / NOT_APPROVED`。
- 五类自反盲区已独立登记于 `ledger/observations/selfreflexive-blindspots-2026-10-23.md`，其 SHA256 `ccf733a3ebb1b738d97d0ff6add4830f36e8d38c7b4162f92cd4a893f1d441f2`。
- 当前文件完整 SHA256 由本条追加后现场复算；历史 `review_sha_before_append` / INDEX 锚点仅代表附注提交时所指历史版本，不替代当前哈希。

## 本次核验结论：14:34 应答附注勘录状态
- 核验对象：本文件中「附注：审阅应答勘录｜REVIEW_RESPONSE / AMENDMENT_NOTE / NON_INTRUSIVE_ADDENDUM」及其后续追加记录；原始用户提交为 2026-10-23 14:34。
- 结果：附注已完整落盘；其所列 P0–P5 处置建议、五类自反盲区、R1 待办状态及历史锚点均保留。另附的续链声明保留 append-only 事实。
- 附注内提到的索引锚 `a94cf1…` 与审阅原始哈希 `deeeb293…` 是用户提交时引用的**历史值**，不作为本文件当前 SHA 或当前 INDEX SHA。
- 五类观察已独立落盘：`ledger/observations/selfreflexive-blindspots-2026-10-23.md`，SHA256 `ccf733a3ebb1b738d97d0ff6add4830f36e8d38c7b4162f92cd4a893f1d441f2`；状态 `OBSERVATION_NOTE / REVIEW_REQUIRED / NOT_INDEPENDENTLY_VERIFIED`。
- 本次不修改 EP-TUNNEL-001-OMNI-R1-UNIFY 主卷正文；无状态升格、无会审签署、无 SEAL。
- 当前审阅及应答记录 SHA256 以本次追加后现场复算值为准；此前文件内列出的哈希均为对应历史字节版本锚点。

## 追加勘录：14:34 用户应答完整性复核（续链）
- 用户原始提交要求：应答附注 append-only 追加；主卷正文不改；补充五类自反盲区观察记录；更新状态为 `CONSOLIDATED_DRAFT / NOT_SEALED / NOT_APPROVED`。
- 当前记录已含上述附注内容，含 P0–P5、五类盲区、保留项、R1 待办台账与历史锚点；主卷正文未修改。独立观察文件存在且 SHA256 为 `ccf733a3ebb1b738d97d0ff6add4830f36e8d38c7b4162f92cd4a893f1d441f2`。
- 注意：用户提供的历史审阅 SHA `deeeb293…` 与 INDEX SHA `a94cf1…` 是附注提交时的历史锚点，不是当前文件值；当前完整哈希以本条之后 `sha256sum` 复算为准。

## 链锚勘录回执｜CHAIN_ACK / HASH_RECONCILIATION / CONTINUITY_NOTE
- 目标卷宗：`EP-TUNNEL-001-OMNI-R1-UNIFY`；回执位置：本文件尾部（append-only，不覆写历史锚点）。
- 历史锚点（**永久留存、不替换、仅作溯源上下文**）：`review_sha_old = deeeb2938139268a…`，`index_old = a94cf1a6770561e5…`；`legacy_ref_policy = CONTEXT_TRACE_ONLY`。
- 创立人回执声明之链顶值：`review_sha_current = 5b49abe0d8806e31725f8cd8dc71f7dbc5a98903a7409318d34d554d824719aa`，`blindspot_note_sha = ccf733a3ebb1b738d97d0ff6add4830f36e8d38c7b4162f92cd4a893f1d441f2`，`top_index_sha = ea5605413e1c9f80c9f1736b610b32ff933d7f65e5597804a42dcbbc63551ff1`。
- **勘录警示（链连续性）**：本回执本身是对本文件的追加写入，追加后文件字节变更，`5b49abe0…` 随即成为"回执前"版本锚点，不再是回执后的当前文件哈希。此为 append-only 链的必然结果，不是哈希错位；后续引用应区分"回执前链顶"与"回执后现场复算值"。
- 自反盲区记录 `ccf733a3…` 自建立后未再变更，仍与回执一致；其状态 `OBSERVATION_NOTE / REVIEW_REQUIRED / NOT_INDEPENDENTLY_VERIFIED`，不并入主卷命题、不升格为公理。
- INDEX 在回执登记后同样发生字节变更，`ea560541…` 为登记前版本；本次登记后以现场复算值为准。
- 文件状态固化：本文件追加式生长；R1-UNIFY 主卷正文全程未改动；定级维持 `CONSOLIDATED_DRAFT / NOT_SEALED / NOT_APPROVED`。
- 待办台账未因哈希迭代重置：P0 标签补丁 → P1 TUN 子域注册＋20:00 会审层级≠终审权限声明 → P2 双轴状态机/SVA/NEGATIVE_RESULT Schema → P3 T17–T24 判据与 SYS-DIM-BENCH/TH 绑定 → P4 废案归档冲突契约与正文版本规范 → P5 术语逐点 `MODEL_TERM` 增量标注（非阻断）。
- 本次为追加勘录与哈希迭代，**非版本封存**；不构成批准、验收或 SEAL。

```yaml
spec: CHAIN_ACKNOWLEDGEMENT
target: EP-TUNNEL-001-OMNI-R1-UNIFY
chain_top_review_sha_at_ack: "5b49abe0d8806e31725f8cd8dc71f7dbc5a98903a7409318d34d554d824719aa"
blindspot_sha: "ccf733a3ebb1b738d97d0ff6add4830f36e8d38c7b4162f92cd4a893f1d441f2"
index_root_sha_before_ack_registration: "ea5605413e1c9f80c9f1736b610b32ff933d7f65e5597804a42dcbbc63551ff1"
legacy_ref: ["deeeb2938139268a…", "a94cf1a6770561e5…"]
legacy_ref_policy: CONTEXT_TRACE_ONLY
draft_class: CONSOLIDATED_DRAFT
seal_state: NOT_SEALED
approval_state: NOT_APPROVED
blindspot_state: OBSERVATION_NOTE, REVIEW_REQUIRED, NOT_INDEPENDENTLY_VERIFIED
next_planned_branch: EP-TUNNEL-001-OMNI-R2
```

## 勘录：R2 预备批次包接收（14:40）
- 批次：`EP-TUNNEL-001-OMNI-R2_PRE_BATCH`，本地落盘目录 `ledger/protocols/ep-tunnel-001-omni-r2-pre-batch/`。
- 定级：`PRE_R2_BATCH / NOT_SEALED / NOT_APPROVED / REVIEW_REQUIRED / NOT_IMPLEMENTED / NOT_TESTED`；提案工件，不覆写 R1-UNIFY 主卷正文。
- 文件（现场复算 SHA256）：
  - `p0-label-patch.yaml`＝`69eae27e250c7672980aff3e69ce19686baad820b75ec16ae50878402527a42e`
  - `dual-axis-state-machine.yaml`＝`1a869ce26e93858e3eb3db185c788792c5c0536c1fd84b459206efd927b64aac`
  - `sva_dual_axis_state_machine.sv`＝`e9ab2e8dc4d588c84c7295b151e5fa2ca6de62b192e325dd8f74a5c66c16fdc8`
  - `negative_result_schema.yaml`＝`7e94ba104f1cf2b3061e3931d9cce36f3ce6af20d25cd0130059478f3dc0b2b4`
  - `batch_meta.yaml`＝`607c163092a2c02dbde886911c05838a35d309fb483beb0526aa2be92a331d07`
  - `README.md`＝`974ca17aca6b2ae98d02e52df98d3cdbd4d49a2e31b661b7aeb9c1beb57903b2`
- 落盘时标注的原文缺陷：断言 1 跨枚举类型比较不可编译；断言 5 语法非标准；`legal_state_combos` 两行粘连已拆分；引用 `sm_transition_matrix.csv` 但未随批提交；`a1_award_sha` 原文截短已补全。
- 本批次**未编译、未仿真、未导入状态机、未接 SYS-DIM-BENCH**；不得据其宣称 P2/P3 闭环。
- 本回执追加后本文件哈希再次变更，链顶值仍以现场复算为准；哈希迭代不等于封存。

## 勘录：R2 批次的缺陷补丁回执（14:43）
- 缺陷 D01–D06 已按创立人口径逐条签收；D01 待 20:00 表决，D02/D03/D04/D06 已落盘，D05 移出本批次。
- 批次文件已在原地更新（`.sv`、`negative_result_schema.yaml`、`dual-axis-state-machine.yaml`、`batch_meta.yaml`），并新增 `sm_transition_matrix.csv`。
- 复核新增 5 项独立发现（转移表通配语义未定义、缺失 UNKNOWN 复位边、缺失 SUSPENDED 恢复边、断言4 语义过窄、`classification_tag` 未机器化），详见批次 `README.md` 追加段。
- 备注：本批次为提案工件，`PRE_R2_BATCH` 目录内对同一文件的原地更新**不属于**主卷 append-only 约束范围（主卷正文始终未改）；但目录若进入正式归档，需转为版本化文件名或另建快照，避免"原地覆盖"与"字节忠实落档"原则冲突。

## 勘录：R2 批次 N01–N05 收敛补丁（14:45）
- N01（CSV 通配歧义）→ 全显式 38 条，无 `_` 残留；N02（UNKNOWN 出边）→ 补 2 条；N03（SUSPENDED 恢复边）→ 补 7 条；N04（断言4 永久锁定版）→ 已换入 v0.3，弱约束版本保留为注释待会审二选一；N05（Schema 依赖门禁）→ 已加 `dependent_schemas` 块。
- 机器校验：28 状态全可达；仅 7 个 `*+G_ARCHIVED` 无出边（符合归档语义）；无重复键。
- 复核新增 6 项问题（N06–N11 口径）：`CONTRADICTED/REPLICATED + ACTIVE` 无 ACTIVE 内出边（"持续观测"无落地路径）、同一目标状态双权限通道、`dependent_schemas` 键名与结构不符合标准 JSON Schema（会被校验器静默忽略）、`classification_tag` 未入必填、SVA `always` 非标准算子、CSV `LEGAL` 列恒 1 缺少非法转移声明方式。详见批次 `README.md`。
- 批次仍 `PRE_R2_BATCH / NOT_SEALED / NOT_APPROVED / NOT_IMPLEMENTED / NOT_TESTED`；未编译未仿真未接 BENCH。

## 勘录：R2 批次 N06–N11 补丁 + P1 提案接收（14:47–14:49）
- 创立人两项前置决议照录执行：常态观测只追加条目不回滚状态；admin_retire 降格为紧急冻结（→SUSPENDED），RETIRED 仅由会审表决可达。
- 落盘：CSV v0.3（40 条+白名单契约头）、SVA v0.4（标准 s_always）、Schema v0.3（allOf+必填 classification_tag）、P1 提案 `tun-subdomain-registration-and-authority-declaration.yaml` v0.1。
- 机器校验：28→40 边无死锁，但 BFS 显示除 CONTRADICTED 外 6 个证据态的 RETIRED/ARCHIVED 全部不可达——"只有证伪才可下线"若非意图，会审须补会审表决边。新标注 N12–N14（admin_retire/admin_suspend 重复边、Schema 仍非可直接校验的 JSON Schema 文档、CSV 缺权限域列）。
- 批次定级不变；仍未编译未仿真未接 BENCH。

## 勘录：R2 批次 N12–N14 收敛与语义锁固化（14:51）
- 决议A（仅 E_CONTRADICTED 可入终审下线链）已写入 CSV 头部 Semantic Lock 并经机器校验：全表通向 G_RETIRED 的边仅 1 条，起点唯一为 CONTRADICTED。此为「证伪优先」强约束，不留宽松分支。
- 决议B（admin_suspend/admin_retire 同目标、差异由外部元 payload 承载）已固化为 CSV 元契约注释；状态机主转移层不分叉。
- N13 已产出 `negative_result.schema.json`（draft 2020-12），jsonschema 实测：合法样本通过、`FORMAL_EVIDENCE+TEMP` 被正确拒绝——Schema 门禁首次真机生效（此前 N05/N08 仅为描述层）。
- N14 已在 CSV 新增 `AUTHORIZED_DOMAIN` 列，40 行全部标注，权限域违规 0。
- 新标注 N15（该列由助手按 P1 矩阵映射填充，非创立人逐行确认；P1 若调整须整列重生成）、N16（全链唯一归档路径为 CONTRADICTED→RETIRED→ARCHIVED，非证伪算子永久不可归档）。
- 批次定级不变；未编译未仿真未接 BENCH。

## 勘录：创立人授权域权威行接收（14:51:45）
- N15 已解决：创立人逐行提供 AUTHORIZED_DOMAIN 权威值（与助手临时映射有 8 处差异，主要把观测采集类归 OBSERVER、推导判定类归 META_VALIDATION_L3、reset_reinit 归 ADMIN_EMERGENCY）。CSV v0.4 已覆写为创立人行，当前 SHA256 `ead7f6da32ed868cdf7635821a275321a46a7a1364687503731a226e89d8545c`，40/40 校验通过，语义锁不变。
- N17（新）：创立人版 negative_result.schema.json（draft-07）传输截断，盘上为助手版 draft 2020-12（已实测生效）；待补发或确认后双锚登记。

## 勘录：N12–N14 回执接收与 draft-07 Shim 确权（14:52）
- 创立人回执 N12/N13/N14 全部签收照录；语义决议（仅 E_CONTRADICTED 可终审下线）已在 CSV 头部与机器校验中固化。
- N13 最终版采用创立人 draft-07 全文：`negative_result.schema.json` SHA256 `3835c8a5121e77a83ae43520952847138f883395ad23e150fb08cd36c2ee0b68`；与 YAML 卷宗版（`a9927b8ecd4c9db0…`）双向锚定。
- Draft7Validator 真机实测四例：合规通过、`FORMAL_EVIDENCE+TEMP` 拒绝、`TRIAL_RUN+TEMP` 通过、非法枚举拒绝。N17 关闭。
- 待会审表决：D01、N04；批次合批放行以会审为准。定级不变，未编译未仿真未接 BENCH。

## 勘录：N16 会审议案包产出（14:54）
- 依创立人要求产出两版可直接上会的「状态机边定义 + 权限域配置」文本，独立目录 `ep-tunnel-001-omni-r2-pre-batch/review-n16/`，主 CSV 未改。
- 方案A（严格零改动＋1 条 SVA 固化）`ed98d984f1491c49…`；方案B（+G_OBSOLETE、+8 边、4 黑名单、3 条 SVA）`9210b9504b6d1b42…`；议案包 README 说明两案速览、机器核验与必答前置问题。
- 核验：A 案非证伪通向 RETIRED/ARCHIVED 边 0；B 案 48 边下 `OBSOLETE→RETIRED` 边 0、非 CONTRADICTED 通向 RETIRED 边 0。
- 依赖提示：N16-B 与 N04（`s_always` 永久锁）互相约束；建议表决顺序 D01 → N04 → P1 → N16。

## 勘录：N16 议案包收束回执（创立人 14:55）
- 基线冻结：主 CSV v0.4 不动；两案为叠加补丁包，表决后才合并；表决序列锁死 D01→N04→P1→N16，不可逆序。
- B 案四项硬前置登记（量化判据赋值、位宽扩容、N04 二选一、三重串联防线），任一无共识 B 案自动失效。
- 表决后合并脚本已登记：投 A 仅加断言＋立项活跃算子台账；投 B 合并 8 边＋枚举扩位＋3 SVA＋量化阈值。
- 本回执为登记性固化，未执行任何合并。

## 勘录：会审前置终版快照回执（创立人 14:56）
- A 案台账治理参数三项登记（维护主体 META_VALIDATION_L3 主控、快照永久归档+增量链式存证、更新频率待会上赋值）；A 案参数未达共识则暂缓生效，临时冻结兜底。
- 工件隔离终态固化：主干只读、补丁分支独立、合并脚本休眠 fail_closed、无手动旁路。
- 依赖链校验照录：D01→N04→P1→N16 不可变。
- 会后启动项清单照录。当前全部工件就位，静待 20:00 会审。

## 勘录：长期使用交接卷落盘（创立人 14:56 指示）
- 创立人指示「今天好的方案要懂得存档，值得长期使用」。已建 `ep-tunnel-001-omni-r2-pre-batch/HANDOVER.md`（SHA256 `0afdfb647f521a5b040ddec4c75d6183a9dd91bdd72c5e21100e0cab8c244b8b`）。
- 内容：四件套权威哈希、八条可迁移设计要点（白名单契约/两层权限网关/权限不等价/语义锁/类型域隔离/负结果一等公民/分类标签强制留存/归档纪律）、真实状态警示与复用路径。
- HANDOVER 定级 `HANDOVER_NOTE / PRE_R2_BATCH / NOT_SEALED / NOT_APPROVED`；不改变会审队列与批次定级。INDEX 已登记。
