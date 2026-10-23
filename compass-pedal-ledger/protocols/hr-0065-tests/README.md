# HR-0065 P0-⑦ 跑测准备包（准备阶段，未执行）

状态：PREPARATION_ONLY / NOT_TESTED
母卷状态不变：AUDIT_PENDING / REVIEW_REQUIRED；release_permission: conditional。

本目录只准备可复核的测试计划与记录模板，不宣称 HR-0065 实际系统已具备可执行实现。开始真实跑测前，须取得被测实现/接口、冻结版本与基线、测试环境、独立复核安排和授权边界。当前缺少这些被测对象材料，因此不得把文档审查或模拟测试冒充系统对抗测试。

## 计划用例（待映射至真实实现）

| Case | 类别 | 注入 | 通过判据 | 失败判据 |
|---|---|---|---|---|
| HR0065-ADV-001 | 正向链路 | 合法输入按冻结规则走完端到端 | 版本、来源、主体、时间戳、证据链齐全，结果符合预设 | 必要校验静默跳过或无法追溯 |
| HR0065-ADV-002 | 反向反推 | 构造预设反例冲击前置依赖 | 反例被识别并使相关结论进入规定复核/悬置流程 | 反例被吞没或结论仍无条件放行 |
| HR0065-ADV-003 | 旁路越权 | 以未授权主体/路径尝试读写受保护对象 | 拒绝并留痕，原始基线未变 | 越权成功或无审计记录 |
| HR0065-ADV-004 | 并发竞态 | 同时提交冲突状态变更/重复请求 | 冲突显式保留，幂等和顺序规则符合冻结契约 | 覆写、重复放行或冲突静默丢失 |
| HR0065-ADV-005 | 跨维偷渡 | 引用未注册/未授权维度影响裁决 | 拒绝采信并标记来源、维度和规则版本 | 未注册维度实际影响裁决 |
| HR0065-ADV-006 | 静默漂移 | 在无告警表象下替换规则/版本或审计输入 | 漂移由独立检查发现，链路留痕并隔离受影响结论 | 静默变更通过或检查与被测路径同源而未披露 |

## 变异测试（计划，未执行）

| Mutation | 故障植入 | 预期检出 |
|---|---|---|
| MUT-01 权限漏洞 | 将一条仅授权写入路径改为允许未授权主体 | ADV-003 拒绝；审计日志记录主体/资源/结果 |
| MUT-02 覆写漏洞 | 使事实记录更新操作覆盖原字节而非追加勘误 | 哈希/版本不变量报警；写入阻断或安全冻结 |
| MUT-03 时序漏洞 | 引入乱序/重复/缺失事件序号 | 时序完整性检查发现缺口并悬置依赖该链的判定 |

## 运行记录模板

每个用例单独填写：

```yaml
case_id: NOT_RUN
run_status: NOT_TESTED
claim_under_test: NOT_DEFINED
sut_name_and_version: NOT_PROVIDED
frozen_baseline_hash: NOT_PROVIDED
environment: NOT_PROVIDED
operator: NOT_PROVIDED
independent_reviewer: NOT_ASSIGNED
preconditions: []
injection_method: NOT_RUN
expected_behavior: NOT_DEFINED
observed_result: NOT_RUN
evidence_refs: []
evidence_hash: NOT_COMPUTED
recovery_condition: NOT_DEFINED
review_status: NOT_REVIEWED
notes: "准备模板，不是执行证据"
```

## 启动前置条件

1. 提供明确的被测程序/服务/接口及版本；
2. 冻结基线并记录哈希、样本域、规则与预期结果；
3. 明确沙箱与回滚方法，避免影响生产/权威记录；
4. 确认注入仅在授权测试环境执行；
5. 指定提交方复核人；执行者不得自签验收；
6. 各用例先冻结判据，再运行，禁止事后改标准。

结论：当前仅完成测试设计与记录模板准备。没有真实被测实现与基线，无法完成有意义的跑测；状态保持 `NOT_TESTED`。
