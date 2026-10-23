# EP03-FINAL-MERGE｜勘疑台账附卷 AUDIT-NOTE-002

- 卷宗锚：`EP03-FINAL-MERGE-20261023`
- 主卷状态：`SEALED_STRUCTURE / THEORY_PROPOSED / REVIEW_REQUIRED`
- 附卷纪律：仅追加勘疑、推荐裁定方案、挂账条目；不改动主正文。
- 裁定截止：`2026-10-23T20:00:00+08:00`
- 证据等级说明：以下为提交方提供的原文、问题陈述及推荐方案；本文件登记其内容，不代表方案已获独立核验或正式裁定。

## RUL-EP03-001｜证据五态与溯源标签分层
- blocking: false
- 问题：C 组证据五态与 I 组溯源失效标记职责边界不清。
- 推荐：五态作为强制基础状态；I 组标记作为可叠加审计标签，不替代基础状态。
- 映射建议：`SOURCE_MISSING` 可叠加 `PROVENANCE_GAP`；`INCONCLUSIVE` 可叠加 `SOURCE_COMPLETENESS_UNKNOWN`；不得自动推定标签，按证据记录审查。
- 裁定状态：`PENDING_REVIEW`

## RUL-EP03-002｜自定义熵指标准入
- blocking: false
- 问题：自定义熵指标缺准入主体与校验材料。
- 推荐：纳入 Meta-Dim 注册审批及 Measurement 字段校验；通过注册前不得接入判定链路。提交材料包括数学定义/值域/单位/系统边界、预设反例集、适用域与禁用域。Meta-Dim 维度管理员初审；重大指标抄送 EP01 元裁判复核。
- 裁定状态：`PENDING_REVIEW`

## RUL-EP03-003｜双账本与三层评价映射
- blocking: true
- 问题：J 组账本与三层评价架构映射不明确，可能重复计权。
- 推荐：保护资格账本映射硬约束层；不可公度独立价值账本映射独立价值层；绩效评价账本映射条件绩效层。资格不通过即终止后续绩效计算；条目不得跨账本重复登记资格判定。
- 裁定状态：`PENDING_HUMAN_RULING`

## RUL-EP03-004｜Lifecycle 字段托管位置
- blocking: false
- 问题：A–N 条目没有逐维展开 Lifecycle 实例字段。
- 方案 A（推荐）：生命周期字段统一外置托管于 Meta-Dim 注册表，主卷仅以固定注释引用注册表记录及哈希。
- 方案 B：在主卷 A–N 条目逐项追加 Lifecycle 小节；与当前结构冻结纪律冲突。
- 裁定状态：`PENDING_REVIEW`

## RUL-EP03-005｜FD 根测试判据
- blocking: true
- 问题：FD-01/03/10 缺预先冻结的 PASS/FAIL/NOT_TESTED/INCONCLUSIVE 判据、输入样例、预期输出及边缘案例。
- 推荐：外置 `ep03-fd-root-criteria.yaml`，为三项根测试定义可机器校验断言，并作为测试门禁基线链接；判据冻结前不启动验收测试。
- 裁定状态：`PENDING_HUMAN_RULING`

## RUL-EP03-006｜硬约束冲突裁决
- blocking: true
- 问题：多项硬约束互斥时，裁决主体、权限来源及申诉流程未定义。
- 推荐：路由至 EP01 元裁判实例；生成冲突存根与听证记录；临时冻结依赖冲突约束集的适配结论；裁决记入 ERRATUM 附卷，并保留复核、撤销路径。
- 裁定状态：`PENDING_HUMAN_RULING`

## RUL-EP03-007｜权限依赖与规范冲突检出
- blocking: true
- 问题：两类耦合缺少可执行检出与人工复核触发规范。
- 推荐：权限依赖以权限矩阵交叉扫描识别同一主体兼持维度定义、数据源控制、最终处置等权限的情形并标风险；规范冲突以规则 AST 静态比对及反例注入检测同一输入触发互斥强制动作的情形并标冲突。检出脚本与阈值外置托管于 `csdt-tools`，通过索引引用；检测结果不自动成为裁决。
- 裁定状态：`PENDING_HUMAN_RULING`

## 汇总
- 待裁定：7 项（RUL-EP03-001–007）
- 阻塞：003、005、006、007
- 非阻塞：001、002、004
- 状态：全部待会审；推荐方案不等同于已采纳裁定。
