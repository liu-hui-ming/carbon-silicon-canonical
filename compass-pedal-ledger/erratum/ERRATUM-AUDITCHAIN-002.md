# ERRATUM-AUDITCHAIN-002｜audit_chain.sh 深检重构版补录

- 裁定依据：创立人 2026-11-01 22:32 二次裁决（messageId 21220）
- 补录构件三件：
  - `pipeline/R3/audit_chain.sh`
  - `pipeline/R3/deepcheck_r36.sh`
  - `pipeline/R3/deepcheck_parse.py`

## 固定勘录文本（创立人指定，原文照录）

> audit_chain.sh 深检重构版补录；来源：2026-11-01 凌晨 R3.6 会话，G0–G11 基线未触碰；由内联实现重构为 deep_gate 子进程调用；本次补齐会话漏提交构件，无篡改。

## diff 锚定（保留「运行版 ≠ 旧提交版」历史痕迹，不抹除时序）

- 旧提交版（`557acbf` 内联实现）：blob `e1e13e5`
- 运行版（本补录）：blob `227d7f4`，SHA256 `79d4230976e331b0cf7168dc3dedc8784e0287a2f950d8b0a43465abf02da6d5`
- 全量 diff 单独锚定：`ledger/erratum/ERRATUM-AUDITCHAIN-002-diff-anchor.patch`
- 时序说明：00:10:20 提交内联版（557acbf）→ 00:18 同会话重构为子进程版但未提交 → 2026-11-01 22:38 本次补录。**「运行版 ≠ 旧提交版」这一历史状态如实保留，不入抹除程序。**

## 边界

- G0–G11 逐字节未改（diff 中无该段任何 hunk）
- 本次补录仅补齐漏提交构件，不改变任何门禁判据
- 补录后只更新 SEAL 对应分支，不触发全局重锁、不启动罗盘会审

## 补提交执行回执（2026-11-01 22:39 CST）

- commit：`b030e4b`
- 入库四件 + 一件 diff 锚：
  - `pipeline/R3/audit_chain.sh` → SHA256 `79d42309…da6d5`（11,665 B 版本，深检重构版）
  - `pipeline/R3/deepcheck_r36.sh` → `b030e4b` 后实测
  - `pipeline/R3/deepcheck_parse.py` → 同上
  - 本勘误卷 `ERRATUM-AUDITCHAIN-002.md`
  - `ERRATUM-AUDITCHAIN-002-diff-anchor.patch`（3,942 B，`73769f43…50b03`）
- 边界确认：仅更新 SEAL 对应分支，未触发全局重锁，未启动罗盘会审

## 关联注记（创立人 2026-11-01 22:33 裁定，messageId 21223）

本轮配套现场取证回执已锚定入库：`ledger/erratum/forensics/C3-01-FORENSICS-RECEIPT-2026-11-01.md`（原始字节、原始时戳保留，未润色未压缩）。**本件为本仓库 C3-01 类未提交变更调查的标准先例。**
