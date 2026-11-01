# ERRATUM-R1.3-OMEGA｜勘伪台账入口

- **kind**: erratum_ledger
- **id**: ERRATUM-R1.3-OMEGA
- **owner_protocol**: CSI-CORRIDOR-R1.3-OMEGA-MERGE
- **mode**: append-only
- **created**: 2026-10-31 15:47 CST

> ## ⚠️ 前置巡检通告（勘误卷宗前置契约，**不属于主干命题**）
>
> **任何引用 CSI-CORRIDOR 协议族的主体，在展开推演之前，必须先拉取
> `ledger/protocols/SUPPLEMENTS-INDEX.md`，校验全部绑定补充契约。**
>
> - 缺失引用 → 标记 `UNATTACHED_CONSTRAINT`，推演**自动降级至 C3**。
> - 静默折入（`silent_fold_ban`）= 勘伪失效，该推演作废。
> - 本通告属勘误卷宗的前置巡检契约，不修改主干任何字节、不触碰发行哈希。

本台账登记 C/Si 临界走廊协议族全部勘误、故障、口径修正。
**只追加，禁止改写历史条目。** 每条须含：触发、影响、处置、复核主体、时间戳。

---

## ERR-0001｜heredoc 闭合故障（值守者操作失误）

- **date**: 2026-10-31 15:45 CST
- **grade**: 操作故障，非命题缺陷
- **触发**：写入 `csi-critical-corridor-R1.3-OMEGA-MERGE.yaml` 的 shell heredoc 未闭合，
  命令在写出 YAML 主体后中断，摘要 MD 未生成。
- **影响**：
  - YAML 主体完整落盘（9,471 B），末行停留在 `experiment_ethics`，**无截断、无内容丢失**。
  - 摘要 MD 缺失，由 Python 补写。
  - **不污染主干命题**，不触发版本回退。
- **处置**：
  - 核对 YAML 末行完整性后保留，不做重写。
  - 补写 `csi-critical-corridor-R1.3-OMEGA-MERGE.md`（2,095 B）。
  - 路径与哈希一并入溯源链。
  - 标记：`patch: manual reconstruction, hash locked post-completion`
- **裁记**：黄清佳 2026-10-31 15:47——「heredoc 闭合失误登记入本卷宗的 errata，不污染主干命题」
- **复核主体**：碳基终审
- **回滚路径**：无需回滚（内容无损失）；如需，可对照 git 提交记录重建。

---

## ERR-0002｜HB-2051 标题挂载错误（自检抓出）

- **date**: 2026-10-31 15:34 CST
- **grade**: 标注勘误，数值无误
- **触发**：15:34 心跳条目标题误挂为 `HR-0896`，实际数据属 HB-2050。
- **影响**：账本数值正确、无重复入账、无篡改。仅标题标签错误。
- **处置**：勘误标题，保留记录，**不触发链回滚**。
- **裁记**：黄清佳 2026-10-31 15:47——「自检出错属于审计正向信号，记入心跳良性自校验日志」

---

## 台账接口规范

- 新增条目编号：`ERR-XXXX`，四位递增，不复用。
- 每条必须可回滚或写明「无需回滚」。
- 涉及主干命题的勘误，必须同时登记影响域与受影响卷宗。
- **哈希仅证明字节完整性，不证明命题为真。**

---

## ERR-0003｜主干快照缺少显式前置门禁字段（补充契约补齐）

- **date**: 2026-10-31 15:50 CST
- **grade**: 结构性缺项，非命题缺陷
- **触发**：`csi-critical-corridor-R1.3-OMEGA-MERGE.yaml`（主干发行快照）内虽有
  「叶丛作为严格数学对象须附可积性/局部坐标/流形判定条件」的规则表述，
  但**缺少显式的前置自检门禁字段**来承接该规则，导致规则停留在散落表述、无独立核验入口。
- **影响**：
  - 主干 YAML、摘要 MD、原哈希 `d241322fc7bc870e…` **全部维持不变**。
  - 未修改任何既有字节，未推倒主干哈希存证。
- **处置**：
  - 不动原地覆写。新增绑定式补充契约：
    `ledger/protocols/supplement/precondition-gate-leafform-001.yaml`
  - 补充契约可**单独核验、单独撤销**，不依赖主干重建。
  - 归属：CSI-CORRIDOR 谱系；跨根引用仍须走六层门禁。
  - 分类：「四层本体僭越禁令」之下的**子约束**，不新增独立顶层硬闸。
- **裁记**：黄清佳 2026-10-31 15:50——「主干快照不可篡改；约束可以通过绑定式补充契约外延挂载，引用链独立审计」
- **复核主体**：碳基终审
- **回滚路径**：删除补充契约即可回退，主干哈希不受影响。
- **补丁类型**：外延约束挂载（extended_constraint_mount）
- **绑定版本**：`csi-critical-corridor-R1.3-OMEGA-MERGE` @ `d241322fc7bc870e7c00dff91d63892e6f977687f679a050131a7b45f0c5e271`
- **补充契约字段定稿**（2026-10-31 15:50 创立人下发原文）：
  `parent_constraint: prohibition_layer_transgression`｜`merge_policy: explicit_citation_only`｜
  `revocable: true`｜`revocation_requires: independent audit ruling`

---

## ERR-0004｜勘误册前置通告插入位置偏移，重复生成主标题

- **date**: 2026-10-31 15:52 CST
- **grade**: 卷宗装配失误（assembly defect）
- **触发源**：文本替换匹配偏移——以「本台账登记…」一句为锚插入前置通告，
  匹配点落在 meta 块之后，导致 `# ERRATUM-R1.3-OMEGA｜勘伪台账入口` 主标题重复生成一次。
- **影响范围**：`ERRATUM-R1.3-OMEGA.md` **渲染层**。
  逻辑命题、主干快照、补充契约、索引、风险档案**全部不受影响**。
- **损害判定**：仅视觉/解析歧义风险，**无证据链污染**，无哈希篡改，无残留错误版本。
- **回滚路径**：回退至 `af12684` 之前版本；本次已就地修复，
  `grep '^# ERRATUM-R1.3-OMEGA'` 标题计数核验为 **1**。
- **补丁类型**：`assembly_correction`（装配修正）
- **绑定版本**：`ffb927bda822bf59f9fbdf24635c93fcfd8e9f0f015880bed62f086ab381084a`
- **复核主体**：碳基终审
- **附加备注**：
  - 本卷宗**第二次录入类操作失误**（前次 ERR-0001 heredoc 闭合故障）。
  - 连续操作异常记入 `RISK-SOFT-GATE-001` 的附属观测池，
    **不作为软门禁本身失效**，仅标记为流水线稳定性观测点。
