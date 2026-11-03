# B 组取证回执｜Git 工作区存量未提交项溯源（创立人 2026-11-01 22:31 裁定授权）

- 取证时点：2026-11-01 22:32–22:36 CST
- 约束遵守：只做取证、比对、隔离；零 commit、零 SEAL 写入、零主链推送
- 取证方法：git diff / git log 交叉、文件 mtime 锚、内容抽验

## 逐项判定

### ① pipeline/R3/audit_chain.sh（中风险 R1）
- HEAD 版 `e1e13e5` → 工作区版 `227d7f4`；工作区实测 SHA256 `79d42309…da6d5`
- 改动内容：G12/G13/G14 内联逻辑替换为 deep_gate 子进程调用（deepcheck_r36.sh → deepcheck_parse.py）；G0–G11 未触碰
- 来源判定：**会话内草稿修改**——mtime 2026-11-01 00:18:35，与 commit `557acbf`（00:10:20「R3.6 gate patch: add G12/G13/G14 branches」）同属凌晨 R3.6 补丁会话；deepcheck 两件配套助手（11,655 B / 700 B，mtime 同 00:18）为**未跟踪**状态
- 操作痕迹：连续演进痕迹清晰（先提交内联版 557acbf，同会话再重构为子进程版，助手文件同步落盘），**无外来不明改动证据**
- 实质风险：门禁脚本「运行版 ≠ 提交版」，且运行版依赖两件未入库助手；若此刻换机/重置，G12–G14 会退回旧逻辑
- 处置建议：不需回滚；候二次裁决——补提交三件（脚本 + 两助手，附勘误说明「00:18 会话重构未随 557acbf 入库」）或明确回退

### ② genesis/genesis-state-T01~T10.json（低风险 R2）
- mtime 2026-04-27；diff 内容为 last_summary/last_run_at 从 04-21 → 04-27 的创世纪龙虾接力轮状态更新
- 来源判定：**历史遗留未提交态**（四月创世实验轮），与今日无关；非篡改
- 处置建议：登记即可；候二次裁决是否随 C3-01 清理批量入库或标 tainted 封存

### ③ .audit039_body.md（低风险 R3，有证据链）
- mtime 2026-10-17 06:51；内容 = AUDIT-039（HB-0134 触发轮·独立验证轮，2026-10-17 06:49 落盘）正文
- 来源判定：**可归因**——心跳链 v2 时代 AUDIT-039 轮的落盘正文临时件，证据链完整（AUDIT-039 编号、HB-0134、时戳全对得上）
- 结论：**非孤立产物，不移出主工作区**；按裁定提取登记入隔离临时账本（本文件）；建议后续随链 v2 封存档案统一归档
- 同族说明：工作区另有一批同模式临时件（.hb*、_hb*.py、_tmp_* 等，合计数百件），多为心跳/勘误轮运行残件，逐一取证不现实，建议按「模式归因 + 抽样核验」批量处置，候二次裁决

### ④ ledger/protocols/INDEX.md（低风险 R2）
- diff = 罗盘踏板勘录回执登记三条（10-31 档 HB-CPS-06、11-01 档 HB-CPS-07 等追加行）
- 来源判定：**cron 勘录轮正常产出**，内容与回执哈希互相印证（回执本体 SHA256 在文中自带），可归因
- 处置建议：随下次正常提交入库即可

### ⑤ 龙虾/script/self_check.log、memory/.dreams/session-corpus、content_bank.md（低风险 R2）
- self_check.log：自检运行日志追加（电源/温度/负载检查行）；memory corpus：梦境语料追加；content_bank：创世期编辑（58+/49-，配对 untracked 兄弟件 content_bank_clean.md）
- 来源判定：全部历史演进，可归因，非篡改

### ⑥ BOOTSTRAP.md / TOOLS.md / .openclaw/workspace-state.json 删除（低风险 R2）
- BOOTSTRAP.md：AGENTS.md 规程规定首启后删除——**合规删除**；TOOLS.md：已迁移并入 AGENTS.md——**合规迁移**；workspace-state.json：存在 .migrated 迁移标记文件——**合规迁移**
- 处置建议：无需回滚，候二次裁决确认入库删除

### ⑦ 未跟踪文件总量（结构性问题）
- `git status` 未跟踪条目数百件：csdt-tools/、canon/、carbon-silicon_canon/、hourly-log/、MINING_LOG.md、config/、src/、tests/、package.json、大量中文道统文稿等
- 判定：**C3-01 的根因**——仓库自始只纳管部分路径，主量内容从未入 git；非本次新增异常
- 处置建议：不今晚动；候单独裁决「工作区纳管范围」专项（全量入库 / 精选入库 / .gitignore 声明不入库三选一）

## 总结论

- **零外来不明改动、零篡改证据**；全部改动可归因为：①今日凌晨 R3.6 会话草稿漏提交（唯一中风险）；②四月至十月历史轮次演进遗留；③心跳/勘录运行残件
- **不需上锁回滚**；需要二次裁决的仅 ①（audit_chain.sh + 两助手补提交与否）与 ⑦（纳管范围专项）
- 勘误条目建议：若裁定补提交，附勘录一行「audit_chain.sh 深检重构版补录，源 00:18 会话，G0–G11 未触碰」

（本件为隔离临时账本，未 commit、未入 SEAL、未推主链——遵创立人 21217 约束）
