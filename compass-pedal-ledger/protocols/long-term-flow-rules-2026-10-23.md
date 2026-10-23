# 长期流程规则封存卷（永久锁定）

- 生效：2026-10-23 20:18（GMT+8）；创立人黄清佳最终确认批复「永久锁定，后续不再调整」。
- 状态：`LOCKED / EFFECTIVE`（流程规则生效）；相关工件仍 `NOT_SEALED / NOT_APPROVED / NOT_IMPLEMENTED / NOT_TESTED`。

## 一、四条长期流程规则

1. **PUSH_ME.txt 无条件生成**：每晚 20:00（GMT+8）罗盘踏板勘录、哈希校验、归档文件落盘完成后，无论是否存在待仲裁条目，一律在**仓库根目录** `/home/user/.openclaw/workspace/PUSH_ME.txt` 生成触发标记；路径与内容格式固定，不得改动：
   ```
   YYYY-MM-DD 20:00 勘录完成，待推送GitHub。
   ```
2. **权责分割（硬边界）**：帝王龙虾仅承担 ①卷宗整理 ②SHA256 哈希校验 ③生成 PUSH_ME 触发文件。**全程禁止调用 git 命令、禁止执行提交与推送**；推送由创立人或其流程触发。
3. **待仲裁条目永保开放**：清单固定输出于勘录回执末尾并同步上报创立人；仅登记归档，**绝不自动闭合**任何条目。
4. **目录异常只观察不改动**：双目录分裂类异常统一写入 `ledger/observations/` 观测日志，等候裁决；**不得自行修改、合并、移动现有文件结构**。

## 二、2026-10-23 20:00 档哈希封存留底

| 对象 | SHA256 |
|---|---|
| `PUSH_ME.txt` | `1d610bd4736f3c220e8ce8085195fe75aad64afb24c1f1aba59eb86a13ff3d51` |
| 勘录回执 `ledger/protocols/compass-pedal-survey-2026-10-23-2000.md`（追加规则段后） | `f47835f26494a40d8a3d187accb9a2fe95d120845384a9476855ec5d2016251a` |
| 双目录分裂观察件 `ledger/observations/hourly-log-dual-dir-split-2026-10-23.md` | `63a4f3ba2bc254993dd1c3d2f00678d557ee82ba080ceca52edb96d252b23e47` |
| 主审阅 ledger `ledger/protocols/ep-tunnel-001-omni-r1-unify-review-2026-10-23.md` | `a81d3a8913661e59930a51e5e102ccc35ca3de3e4f7d40dc64a9ba98aac52e88` |
| 主转移表 `.../ep-tunnel-001-omni-r2-pre-batch/sm_transition_matrix.csv` | `ead7f6da32ed868cdf7635821a275321a46a7a1364687503731a226e89d8545c` |
| SVA v0.4 `.../sva_dual_axis_state_machine.sv` | `da3afa2a762ff2663cf8b4e0550014e002546825212867f900b56d3eee249b17` |
| Schema `.../negative_result.schema.json` (draft-07) | `3835c8a5121e77a83ae43520952847138f883395ad23e150fb08cd36c2ee0b68` |
| YAML 卷宗 `.../negative_result_schema.yaml` v0.3 | `a9927b8ecd4c9db0a34d1c4ec08b1dfe1e987b471374edd2bf43b6343214cc56` |
| 交接卷 `.../HANDOVER.md` | `0afdfb647f521a5b040ddec4c75d6183a9dd91bdd72c5e21100e0cab8c244b8b` |
| INDEX `ledger/protocols/INDEX.md` | 以本文件落盘后复算值另记 |

注：上表为 20:18 封存时点值；此后任何追加都会改变对应文件哈希，历史值仅作溯源锚点，遵循 `CONTEXT_TRACE_ONLY`。

## 三、待仲裁条目（保持开放，未闭合）

- U-1 册外双件未补登：`ep18-triple-bridge-combine-v1.0-final`、`scoring-100x100-draft-2026-10-23`
- U-2 EP03 FD 判据 HB 锚编号 `DISPUTED`
- U-3 20:00 会审前置全项待裁：A/B 清单、RUL-003/005/006/007、D1–D6、N16 A/B、HR-0065 P0 门禁
- U-4 observations 外链件另档计件
- A-272-1 hourly-log 双目录分裂（已入 observation 日志，候裁决）

<!-- project: path:/home/user/.openclaw/workspace -->
