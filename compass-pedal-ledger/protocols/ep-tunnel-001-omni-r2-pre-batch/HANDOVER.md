# R2 预备批次包｜长期使用交接卷

- 生成：2026-10-23 14:56（GMT+8）；创立人指示「好的方案要存档，值得长期使用」后建此索引。
- 本文件是批次包的**长期使用入口**：后续任何人（含下一会话的我）从这里进入，不必重读全链消息。

## 一、这套方案为什么值得长期用
双轴状态机（证据轴 × 治理轴）+ 全显式白名单转移表 + 权限域前置网关 + 可真机校验的负结果 Schema，四件套合起来回答了一个通用问题：
**如何在任何"状态机 + 权限 + 证据"类系统里，防止状态被权限越权改写、防止负结果被静默丢弃。**
与具体领域（晶体管隧穿）解耦，可作为治理骨架复用到其他项目。

## 二、核心工件与哈希（权威值，现场复算于 14:56）

| 工件 | 作用 | SHA256 |
|---|---|---|
| `sm_transition_matrix.csv` v0.4 | 40 条全显式白名单转移 + AUTHORIZED_DOMAIN 权限列 + Semantic Lock（仅 E_CONTRADICTED 可终审下线） | `ead7f6da32ed868cdf7635821a275321a46a7a1364687503731a226e89d8545c` |
| `sva_dual_axis_state_machine.sv` v0.4 | 4 条运行时断言（$rose/s_always 已标准化） | `da3afa2a762ff2663cf8b4e0550014e002546825212867f900b56d3eee249b17` |
| `negative_result.schema.json` draft-07 | 负结果机器校验入口（四类枚举 + classification_tag 强绑定） | `3835c8a5121e77a83ae43520952847138f883395ad23e150fb08cd36c2ee0b68` |
| `negative_result_schema.yaml` v0.3 | 上项的人类可读卷宗版（双向哈希锚定，改一必同步另一） | `a9927b8ecd4c9db0a34d1c4ec08b1dfe1e987b471374edd2bf43b6343214cc56` |
| `p0-label-patch.yaml` | P0 元标签补丁（REQUIRED→ADOPTED） | `69eae27e250c7672980aff3e69ce19686baad820b75ec16ae50878402527a42e` |
| `tun-subdomain-registration-and-authority-declaration.yaml` v0.1 | P1 五权分立权限契约（分析分层 ≠ 权限分层） | `a6a0699e36913c2e3abaa7f9c827a6bbd6c24f66861db33352dcbd4381e5d302` |
| `dual-axis-state-machine.yaml` v0.2 | 双轴定义 + 合法组合 + 类型域隔离说明 | `3b2649d7a302f373f3a4c79bfc4982013c66335c1829d062786af0f8e22834dc` |
| `batch_meta.yaml` | 批次清单 + 归档纪律（转正后版本化快照，禁原地覆盖） | `7a39f421d8a9c5636f1f99772854c4f8b8eb1a9ed58736f92ba187a5b06fe42d` |

## 三、长期使用的设计要点（迁移时照抄这几条，不要重新发明）

1. **白名单契约**：表内即合法，未列即非法，导入器 `fail_closed`。LEGAL 列留三态（1/0/2）。
2. **权限前置网关两层**：第一层匹配（当前态，事件，目标态）白名单；第二层校验触发者 ∈ AUTHORIZED_DOMAIN，不匹配拦截。
3. **权限不等价**：管理员只有紧急冻结权（→SUSPENDED），终审下线（→RETIRED）必须跨层表决。常规冻结与紧急冻结同目标，差异由外部元 payload（urgent_flag + mandatory_review_deadline）承载，不进状态机。
4. **语义锁**：`Semantic Lock` 写在 CSV 头部，机器可验证（通向 RETIRED 的边唯一）。
5. **证据轴与治理轴分类型**：两个枚举类型互斥，越权由编译期静态检查兜底。
6. **负结果一等公民**：与阳性结论同级，无 reviewer_id 无效，归档后只可追加不可删除，推翻旧负结果必须新增条目。
7. **分类标签强制留存**：FORMAL_EVIDENCE → PERMANENT（draft-07 allOf/if/then 机器强校验，已实测拦截）。
8. **归档纪律**：提案阶段可原地更新；转正后强制版本后缀 + 快照目录，禁止原地覆盖。

## 四、状态（不要误用）

- 本批次 `PRE_R2_BATCH / NOT_SEALED / NOT_APPROVED / NOT_IMPLEMENTED / NOT_TESTED`
- 未编译、未仿真、未导入状态机、未接 SYS-DIM-BENCH
- 待 20:00 会审表决（顺序锁死）：`D01 → N04 → P1 → N16`
- 表决后合并脚本休眠待命：投 A → 加 1 断言 + 立项活跃台账；投 B → +8 边 + 枚举扩位 + 3 断言 + 量化阈值
- N16 议案包：`review-n16/`（A 案 `ed98d984…`、B 案 `9210b950…`、README `f605d6e3…`）

## 五、后续复用路径

1. 新项目套用：复制四件套（CSV/SVA/schema.json/batch 归档纪律），替换状态枚举与权限域名。
2. 验证顺序：jsonschema 校验（立即可跑）→ CSV 图校验（立即可跑）→ SVA 编译仿真（需 Verilator/商业工具，未装）→ SYS-DIM-BENCH 接入（待判据表）。
3. 本工作区可立即复跑的验证：`python3 + jsonschema`（已验证可用）；CSV 图校验脚本逻辑见批次 README 追加段。

<!-- project: path:/home/user/.openclaw/workspace -->
