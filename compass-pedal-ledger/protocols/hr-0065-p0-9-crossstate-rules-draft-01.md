# HR-0065｜P0-⑨ 三套状态机交叉态规则表（初稿 DRAFT-01）

- 状态：`DRAFT / PENDING_ADJUDICATION`（仅供前置审阅；三选一最终裁定权归提交方）
- 生成时间：2026-10-23 10:36 GMT+8
- 对应条目：整改台账 P0-⑨（含并入的⑥）
- 母卷：HR-0065（状态不变：`AUDIT_PENDING / REVIEW_REQUIRED`）
- 性质：**初稿不等于裁定**。每格的强制路径均标注 [待裁]，需提交方逐格确认或改判后才可并入母卷。

## 一、三套状态机回顾（不改定义，仅交叉）

```
状态机A 命题成熟度：  DRAFT → PROPOSED → SPECIFIED → TESTABLE → EVALUATED
状态机B 证据结论：    UNASSESSED → SUPPORTED / REFUTED / INCONCLUSIVE
状态机C 治理版本：    ACTIVE → FROZEN → SUSPENDED → REOPENED → SUPERSEDED / RETIRED
```

交叉态问题：A/B/C 各自合法，但组合可能矛盾。本表规定**矛盾组合出现时的强制路径**。

## 二、核心交叉态规则表（B×C 全矩阵）

| # | 证据结论(B) | 治理版本(C) | 判定 | 强制路径 [待裁] |
|---|---|---|---|---|
| X01 | REFUTED | ACTIVE | **矛盾态**：已证伪仍生效 | 自动转 SUSPENDED ＋ 同步生成 ERRATUM 附卷 ＋ 通知人工复核。三动作必须同时发生，不得只做其一 |
| X02 | REFUTED | FROZEN | 冻结的已证伪卷宗 | 保留 FROZEN（历史保护），追加 ERRATUM 登记证伪事实；解冻前须先走 REOPENED→SUPERSEDED 链 |
| X03 | REFUTED | SUSPENDED | 一致（均已停用） | 无动作；登记交叉态记录，等待 SUPERSEDED 或勘误反转证据 |
| X04 | REFUTED | SUPERSEDED/RETIRED | 一致（已退役） | 无动作；确认为合法终态 |
| X05 | REFUTED | REOPENED | **高危态**：证伪卷宗被重新启用 | 禁止自动放行。强制人工终审＋须提交与原反例不冲突的新证据；无新证据则退回 SUSPENDED |
| X06 | SUPPORTED | ACTIVE | 正常态 | 无动作；常规续验窗口照常 |
| X07 | SUPPORTED | FROZEN | 合法（封存但获支持） | 无动作；支持结论不因冻结失效，亦不因冻结升格 |
| X08 | SUPPORTED | SUSPENDED | 中性偏保守 | 允许；SUSPENDED 解除条件照旧，支持结论作为恢复参考而非自动放行依据 |
| X09 | SUPPORTED | REOPENED | 允许，但注意 | 重开期间新证据仍按正常流程；不得引用重开前的 SUPPORTED 直接豁免复测 |
| X10 | SUPPORTED | SUPERSEDED/RETIRED | 合法退役 | 无动作；退役卷宗的 SUPPORTED 不得被新卷宗自动继承（对齐 D9 迁移不变量） |
| X11 | INCONCLUSIVE | ACTIVE | **挂账态**：证据不足仍生效 | 强制挂 `EVIDENCE-INSUFFICIENT` 标签＋限期补证计划；限期到未补证 → 自动降 SUSPENDED [补证期限数值待裁，建议 30 天] |
| X12 | INCONCLUSIVE | FROZEN | 冻结的未决卷宗 | 允许；解冻须先补证或改判，不得凭"冻结期间无新反例"推定升级为 SUPPORTED |
| X13 | INCONCLUSIVE | SUSPENDED/RETIRED | 一致保守 | 无动作 |
| X14 | UNASSESSED | ACTIVE | **缺口态**：未经评估即生效 | 视同 X11 处理；UNASSESSED 超过 [待裁：7 天] 未入评估队列 → 自动降 SUSPENDED |
| X15 | 任何B | C 任意 | 通用兜底 | 状态机间同步必须留痕：触发时刻、触发证据引用、执行的强制路径、执行主体、复核人。缺任何一项，同步操作无效 |

## 三、配套执行约束

1. **自动转 SUSPENDED 不是裁决**：X01/X11/X14 的自动降级是**安全动作**（fail-safe），不是对命题真假的新判定；真伪仍走证据流程。
2. **ERRATUM 链路唯一**：X01/X02 的证伪登记只能走 ERRATUM 附卷，禁止原地改写证据结论字段。
3. **X05 是全表唯一人工必经格**：证伪卷宗重开，绕过人工终审＝权限越界，按 P0 风险处置。
4. **双向留痕**：任何 B→C 或 C→B 的状态变化若导致交叉态迁移，双侧台账须各自登记同一事件 ID。
5. **禁止静默折叠**：本表任何一格都不允许"保持原状且不记录"这一输出；无动作格也须登记"已核查、判定一致"。

## 四、与既有规则的衔接

- X01 与 BRIDGE-003 双层门禁一致：权限完整性冻结门负责阻断，本表负责证伪后的状态迁移，二者不重叠、不互代。
- X10 与 D9 跨域迁移不变量一致：迁移机制不迁移结论。
- X11/X14 的自动降级期限是**唯一新增数值参数**，按纪律须预先冻结、不得试点中临时改。

## 五、待裁清单（提交方逐项确认）

| # | 待裁项 | 本稿建议 | 备选 |
|---|---|---|---|
| D1 | X01 三动作是否必须同时（降级＋ERRATUM＋通知） | 是 | 降级先行、余项限时 |
| D2 | X05 证伪卷宗重开是否允许自动路径 | 禁止自动，人工必经 | 允许带条件自动 |
| D3 | X11 补证期限 | 30 天 | 14／60 天／按维分档 |
| D4 | X14 UNASSESSED 生效宽限 | 7 天 | 3／14 天 |
| D5 | 自动降级是否需要事后人工确认 | 需要复核但不撤销降级 | 降级即时生效免复核 |
| D6 | 本表并入母卷的方式 | 作为 HR-0065 ERRATUM 附卷 | 直接写入正文（不符合 append-only，不建议） |

## 六、状态声明

- 本初稿不改母卷、不改台账条目状态；⑨ 仍为"待裁定"，不因初稿存在而闭环。
- 裁定后产出：逐格确认记录 ＋ D1–D6 裁定文本，随附卷入 20:00 会审。
- 初稿哈希见落盘回执；后续修订走 ERRATUM 追加，不覆写本文件。

<!-- project: /home/user/.openclaw/workspace -->
