# R3.6 可复用操作规程 v1（REUSABLE-OPS-R3.6-v1）

> 用途：把 2026-10-31 ~ 2026-11-01 之间建成的 R3.6 链路，提炼成**换机可重建、换人可接手**的操作规程。
> 本文件是操作手册，不是卷宗正文。卷宗正文以 git 实际文件为准。

---

## 0. 一句话总览

一条只读、append-only、可审计的样本链路：**锚点 → 预言机账本 → 误差账本 → 指纹向量库 → 门禁校核 → 双轨调度**。
所有写入默认 dry-run，所有裁决归人，所有账本永不改写只追加。

---

## 1. 资产地图（重建时照抄这个结构）

```
pipeline/R3/
├── audit_chain.sh              # 主门禁 G0–G14（只读，输出 PASS/FAIL/SKIP）
├── deepcheck_r36.sh            # 深检子脚本入口（被 audit_chain 调用）
├── deepcheck_parse.py          # CSV 引用安全解析器 + G12/G13/G14 规则
├── SEAL_manifest.txt           # append-only 封卷台账
├── arc_v18_manifest.yaml       # 命名空间与版本清单
├── patches/                    # 补丁集 + 规格 + 应用校验脚本
└── r36/
    ├── oracle/    store/oracle_ledger.csv        (12 列, R3.6-01)
    ├── error/     store/error_ledger.csv         (13 列, R3.6-02)
    ├── fingerprint/ store/vec_ledger.csv         (13 列, 向量专用)
    │              store/sim_audit.csv            (相似度审计, 与向量表分离)
    ├── ingest/    ingest/batch_ingest.py         (原子三账本写入器)
    └── ... schema/ 各模块 JSON Schema

dual/
├── dual_trail.yaml             # 调度契约（配额/共振/隔离/开关）
├── schedule_dual_trail.py      # 调度器
├── anchors/inbox/              # 正式采样池（灌这里）
├── anchors/_test/              # 测试锚隔离区
├── feed/{media,sandbox}/       # 两轨产物分区
├── log/dual_trail_audit.csv    # 双轨审计流水
└── quarantine/{media,sandbox}/ # 失败批次隔离
```

---

## 2. 五条铁律（违反任一条，链路即失效）

1. **append-only**：任何账本只追加，永不截断/改写/删除。回滚用「撤销标记行」，不是删行。
2. **dry-run 默认**：写入器与调度器不带 `--commit` 时零落盘。想看计划就裸跑。
3. **只读门禁**：`audit_chain.sh` 全程不写任何文件；SKIP 表示校验对象缺失，**绝不强置 PASS**。
4. **裁决归人**：机器只做生成/粗筛/归档/登记；准入、升格、合并、封存由创立人终审。`git push` 与 `chattr +i` 永远手动。
5. **比特 ≠ 事实**：哈希只担保符号层完整性，不担保语义与事实对应。任何「哈希对上所以内容为真」的推论都无效。

---

## 3. 日常操作（四个动作，覆盖 95% 场景）

### 3.1 跑门禁自检
```bash
bash pipeline/R3/audit_chain.sh pipeline/R3
```
期望输出：`=== SUMMARY: PASS=N FAIL=0 SKIP=M ===` + `[AUDIT] gate check: PASS (with declared SKIPs)`
FAIL 非零则**先停下查明**，不要继续灌样本。

### 3.2 灌入标定样本（dry-run 先看计划）
```bash
cat batch.json | python3 pipeline/R3/r36/ingest/ingest/batch_ingest.py            # 只打印计划
cat batch.json | python3 pipeline/R3/r36/ingest/ingest/batch_ingest.py --commit   # 真写入
```
前置：`batch.json` 的每条样本必须带 `media/lineage/grade/anchor_sha256(64hex)/draft_sha256(64hex)`；L0 另需 `manual_review_sha`。
写入后自动再跑一轮 audit；FAIL 则批次标 `tainted` 锁入 `store/tainted.csv`。

### 3.3 灌入双轨锚点
把经 G12 预检的锚 JSON 放进 `dual/anchors/inbox/`，字段：
`anchor_id / anchor_sha256 / anchor_uri / title / predicate_tokens / media / lineage_tag / grade / observed_ts`
```bash
python3 dual/schedule_dual_trail.py --trigger manual            # 预演
python3 dual/schedule_dual_trail.py --trigger manual --commit   # 落盘
```
池空会自动走空载连通性自测，只跑路由/日志/相似度，**不生成正文**。

### 3.4 封卷（写完必做）
```bash
sha256sum <每个改动文件>            # 逐字节哈希，双次回读一致
wc -c <每个改动文件>                # 字节数
printf '<版本> | <上游> | DE | <sha256> | <时间> CST | qiongzhu (...)\n' >> pipeline/R3/SEAL_manifest.txt
git add <明确路径>                  # 不用 git add -A
git commit -m "<模块: 做了什么; 修了什么; 验证结果>"
```
回执必备四要素：**路径 / SHA-256 / 字节 / commit**。

---

## 4. 门禁语义速查

| 状态 | 含义 | 处理 |
|---|---|---|
| PASS | 校验对象存在且合规 | 放行 |
| SKIP | 校验对象缺失（未就绪） | 记录，不算失败 |
| FAIL | 对象存在但违规 | **阻断**，先修再走 |

G0–G11：清单/命名空间/快照完整性/沙盘依赖
G12–G14：预言机锚、误差账本外键与环、指纹向量解析与隔离（深检，走 `deepcheck_parse.py`）

---

## 5. 双轨共振规则（易错点）

- **同锚跨轨孪生对**：默认豁免，不判 SIM-COLLISION；距离仍记录，标 `[ignored: same anchor twin]`
- **不同锚之间、同轨内部**：一律严格阈值（low 0.62 / high 0.78）
- 同源孪生在锚骨架之外仍高度重合 → 触发 `cross-track semantic bleed`，**只告警不阻断**

---

## 6. 踩过的坑（血泪清单，重建时别再踩）

1. `Path(**file**)` —— 对话粘贴通道会把双下划线改写，脚本必崩。**所有代码以磁盘文件为准，不以聊天文本为准。**
2. 相对路径 `../../store` 自子目录解析落空 —— 一律用 `Path(__file__).resolve().parents[n]` 锚定。
3. CSV 用裸逗号拼接测试数据 → 引号内逗号击穿校验。**测试数据必须用 `csv.writer` 生成。**
4. 校验器用 `grep -c '|'` 数 CSV 行 → 恒为 0，账本有数据也报 empty。**CSV 必须用 csv 模块解析。**
5. 写入器未实现却记 `status="closed"` → 伪造档案。**没有真写入，就不许写成功状态。**
6. 把向量写进 `sim_audit.csv`（相似度审计表）→ 破坏 schema。**向量走 `vec_ledger.csv`，两表分离。**
7. 预言机账本 12 列，凭感觉写 9 列 → 列错位脏数据。**写入前先读表头。**

---

## 7. 待办（已登记，未完成）

- G13 `active` 统计过滤：被 supersede 的原记录在统计链路自动跳过（当前仅报告计数）
- 媒体轨生成器：目前为槽位占位，正文由会话模型或人工录入
- `chattr +i` 冻结：候正式封卷版本点名后执行

---

## 8. 迁移最小单元

换机器时搬运以下整体，不可拆开：`pipeline/` + `dual/` + `ledger/sealed/` + `SEAL_manifest.txt` + 勘误链 + 证据账本。
单独搬脚本而不搬账本，等于搬了一具空壳。

---
本规程随链路演进更新；每次更新追加新条目，不覆写旧版。
