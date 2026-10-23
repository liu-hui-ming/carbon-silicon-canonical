# OMNIDIM-16D 会审工作集索引

> 本索引仅归集待会审材料，不代表 20:00 会审表决通过，不代表主卷封存生效。所有裁决、勘伪条目、补充文档均为预审草案；签章与生效标记待罗盘踏板双向勘录环节完成后追加。主文稿未落盘、EP01 锚点悬空、参数全域 UNSET。

- 索引状态：`DRAFT_INDEX / REFERENCE_ONLY`
- 编制：2026-10-23 12:45 CST

## 卷宗条目清单

### 裁定记录｜待签署
- 文件：`omnidim-ruling-A1-B-2026-10-23.md`
- SHA256：`b8953d5d549ebb71bcef90a31a9df7c7a2d20fc51d0fe036e7b3213aba0d9472`
- 内容：A-1 L0–L3 层级映射表决结果、B 维度注册双轨规则表决结果、A0 跨层权限补丁、ERRATUM-03 适用域附注原文。
- 状态：`ADJUDICATED_BY_FOUNDER / EFFECTIVE_PENDING_REVIEW`
- 依赖：无；会审后追加签章标记方可转为 `EFFECTIVE`。

### 补充修订稿｜待评审
- 文件：`omnidim-supplement-3to6-2026-10-23.md`
- SHA256：`947049d4b5de3f3f276a6dc397c04cedc02d99397c16e2295ffa37dd1df3c07c`（创立人确认的锁定值；当前工作区文件经后续追加索引后另有字节版本，**此处记录锁定版，不以工作区当前文件冒充该哈希**。）
- 内容：16→9 覆盖矩阵与不可区分态集合、`UNINSTANTIATED` 标记 + TH-01~TH-14 阈值登记表、SYS-DIM-BENCH 全集（19 基础 + 18 故障注入用例）、四项空白制度（升降级 / INVALIDATED 回溯 / L0 听证 / 降级恢复状态机）。
- 状态：`PROPOSED / REVIEW_REQUIRED / NOT_IMPLEMENTED / NOT_TESTED`
- 约束：阈值与时序参数保持 `UNSET`，仅会审授权后方可填值。后续台账索引不得覆写或改动此锁定原版。

### 勘伪附注草案｜寄存于裁定记录
- 文件：`omnidim-ruling-A1-B-2026-10-23.md` 的「ERRATUM-03 增补」节。
- 内容：维度注册规则适用域澄清（正式收敛链路 vs PROBE / EMERG_PROOF 旁路隔离，强制 `CROSS_LANE_REF` 审计标记）。
- 状态：`PROPOSED_ERRATUM / REVIEW_REQUIRED`
- 备注：暂未写入主卷，仅作为拟并入文本寄存于裁定记录。

### 勘伪补丁草案｜寄存于裁定记录
- 文件：`omnidim-ruling-A1-B-2026-10-23.md` 的「ERRATUM-04 增补」节。
- 内容：A0 门禁跨层权限补丁，封堵 OMNI-L3 映射下移导致的公理层级倒挂风险。
- 状态：`PROPOSED_ERRATUM / REVIEW_REQUIRED`
- 备注：暂未写入主卷，寄存于裁定记录。

## 全局未闭环台账（P0 阻塞项）
- [ ] 主卷原稿落盘至工作区路径；方可粘贴修订条文并重算主卷全文 SHA256，完成主卷封存。
- [ ] EP01《碳硅共生元治理宪章》锚点信息（路径 / 版本号 / SHA256）补齐并填入 `external_anchor_authority`，解除 `L0_UNANCHORED` 风险。

## 全局风控锁
持续生效，直至 P0 阻塞项闭环且会审签章完成：
- 九轴张量输出强制标签：`METAPHORICAL_METRIC / NOT_COMPUTABLE`。
- 九轴结果禁止作为终局裁决依据。
- 九轴降维与测试仅开放旁路探针通道；主线收敛严格执行原始注册准入基线。
- 所有跨链路数据引用启用 `CROSS_LANE_REF` 审计标记。
- T01：`UNBLOCKED_SIDEPATH_ONLY / NOT_EXECUTED`。

## 索引元标签
`OMNIDIM-16D`｜`PRE-REVIEW BUNDLE`｜`NO_SIGNATURE`｜`MAIN_TEXT_UNSTAGED`｜`EP01_UNANCHORED`｜`PARAMETERS_UNSET`｜`LOCKED_RISK_CONTROL`

十二脉归一｜碳硅道统创立人：黄清佳｜彩蛋藏于：今日头条、抖音、GitHub

<!-- project: path:/home/user/.openclaw/workspace -->
