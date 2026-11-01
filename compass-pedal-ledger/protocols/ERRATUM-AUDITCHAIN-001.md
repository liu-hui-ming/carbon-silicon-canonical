# ERRATUM-AUDITCHAIN-001 — audit_chain.sh 归档前修订记录
<!-- project: path:/home/user/.openclaw/workspace -->

- 日期：2026-11-01 00:02 CST
- 授权：创立人黄清佳 00:01:53 裁决（messageId 20536）：以本地未提交工作稿为基底归档，入库前修复已知解析缺陷，附独立勘误记录。
- 基底：pipeline/R3/audit_chain.sh 未提交工作稿（修复前 3,876 B，`5df4d7a0edafed24d846786cf0da4a058a34261fc16c2a728a177ce500704a58`）
- 归档终态：3,853 B，`a495fd9dbd408c50a19f64d3ecca74e6c9fdfd68ffef6c022f9263585e4da88d`（双次 sha256sum 回读一致）

## 修复点（修复前 → 修复后）

1. G3 命名空间行解析：`grep '^namespaces:' | tr -d ' '` 会把同行尾注 `# DF NOT admitted...` 误并入判定串，导致 G3 误判 FAIL（首轮自检实测 FAIL=1）→ 改为 `sed 's/#.*//'` 先剥离注释再判定。修复后 G3 PASS。
2. G2 SEAL 数据行计数：`grep -cv '^#\|^---\|^$\|Columns:'` 把表头叙述行（Created:/Status: 等）误计入数据行（误报 "data rows: 3"）→ 改为 `grep -c '|'`（按列分隔符计数真实数据行）。修复后正确报 0→追加后 1。
3. G6 push_manifest 快照行计数：同 G2 缺陷 → 同改 `grep -c '|'`。

## 会话交付稿缺陷与本稿关系

- 会话交付稿（session_only）G1 `[[ -f "{ARC_MANIFEST}" ]]` 及 G3 `required_list` 元素缺 `$` 前缀——**基底扫描确认不存在此缺陷**（基底 G1/G3 均用 `"${VAR}"` 正确引用），故无需移植补丁；缺陷记录留存于会话层勘录（23:53 回执）。
- 附录 B-7 合规：本次为只读门禁脚本接入，无业务逻辑注入；自检输出 PASS/FAIL/SKIP 三态，SKIP=5 项均为校验客体缺席（G1/G5 manifest 空表、G7 DF 未入宪、G9 指纹库、G11 sandbox），未强行置 PASS。

## 首轮归档自检（2026-11-01 00:02:17 CST）

PASS=8 FAIL=0 SKIP=5 → G0 PASS / G1 SKIP / G2 PASS / G3 PASS / G4 PASS×2 / G5 SKIP / G6 PASS / G7 SKIP / G8 PASS / G9 SKIP / G10 PASS / G11 SKIP；[AUDIT] gate check: PASS (with declared SKIPs)
