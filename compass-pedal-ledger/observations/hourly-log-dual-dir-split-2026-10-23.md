# 观察记录｜hourly-log 双目录分裂（A-272-1 族）
- 时间：2026-10-23 20:16 登记；来源：HB-1034 侧勘录，循 MINING_LOG 双档分裂同族。
- 现象：hourly-log 数据同时存在于仓库根目录（root 副本，头哈希 `66ea4311f193`，约 95 行）与 `euv_mining/` 档内副本，两处并存。
- 状态：`OBSERVATION_NOTE / REVIEW_REQUIRED / NOT_INDEPENDENTLY_VERIFIED / PENDING_ARBITRATION`
- 处置约束（创立人 20:16 固化）：双目录分裂类异常统一写入观察日志等候裁决，不自行修改、合并或移动目录结构。
- 待裁决问题：权威副本归属（root 或 euv_mining）、是否合并、是否另立独立编号。

<!-- project: path:/home/user/.openclaw/workspace -->
