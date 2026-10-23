# E4-OVERDUE-NOTE｜EP02-MOTIVE-OS-R1.2 逾期登记（方案 A）

- 生成时刻：2026-10-23 21:53 CST｜依据：创立人 21:53「选定方案 A」指示
- 对象卷：E4 = `EP02-MOTIVE-OS-R1.2`（EP02 融合定稿）
- 待裁文件：`ledger/ep02-motive-os-R1.2-pending-rulings.yaml`
- 状态：`OVERDUE_REGISTERED / PENDING_RULING_HELD / NOT_SEALED / NOT_APPROVED / hash: PENDING`
- 本件性质：**逾期事实登记**，不是裁定、不是落盘、不产生任何生效变更。

## 一、逾期事实

| 项 | 值 |
|---|---|
| 原定裁定截止 | `2026-10-23T20:00:00+08:00` |
| 实际状态 | 逾期（截至本件生成 21:53，逾期约 1h53m） |
| 20:00 勘录是否收录 | 否——回执范围不含 E4，INDEX 无 E4 条目 |
| HB 台账记载口径 | 「E4 已过期无新事实」，各轮沿用 |
| 待裁项完成数 | 0 / 5 |

## 二、五项待裁条目（原样留存，裁决权归正规定席）

| ID | 议题 | 阻断性 | 推荐选项 | 证据级 |
|---|---|---|---|---|
| RUL-PEND-E4-01 | 旧版02 与 R1.0-R1.2 谱系关系（并存+ERRATUM指针 / 直接替换） | false | `coexist_with_erratum_pointer` | B |
| **RUL-PEND-E4-02** | **L1-L4 命名空间冲突（MOTIVE 前缀改称 / 保留裸编号+作用域注记）** | **true** | `rename_to_MOTIVE_L1_L4` | A |
| RUL-PEND-E4-03 | L4 锚定争议层构成机制（补写 / 标 UNDEFINED 照常落盘） | false | `mark_undefined` | B |
| RUL-PEND-E4-04 | 四件哈希归档策略（E4主基线+E1~E3历史切片 / 仅E4） | false | `E4_main_baseline_plus_E1_E2_E3_history_slices` | B |
| RUL-PEND-E4-05 | 硬件工程清单层级混叠（拆附卷 EP02-R12-ENG-PLAN / 内嵌） | false | `split_to_EP02_R12_ENG_PLAN` | B |

## 三、前置约束（写入并锁定）

1. **RUL-PEND-E4-02 为强制阻断项。** 未裁定前 E4 正文不得落盘：本件通篇裸 `L1-L4` 与已冻结命名空间 `ARC-L0~L3 / STACK-L1~L4 / PIPE-L1~L4`（依 `RUL-BASELINE-01`）撞号，落盘即产生编号冲突。此项阻断性是结构性的，不因逾期时间长而递减。
2. 其余 4 项（01/03/04/05）可先行草拟推荐方案，**但一律不生效**：草稿标 `DRAFT_ONLY / NOT_EFFECTIVE`，不进正文、不改状态、不参与哈希。
3. 全部 5 项裁决权保留给正规定席；本件不提供默认值、不做隐式裁断、不因逾期而自动降级为"超时视为通过"。
4. 待裁事项永不自动闭合（长期流程规则第③条适用）。

## 四、台账与隔离（依创立人指示）

- 台账留痕口径：仅在 HB 各轮标注「E4 已过期无新事实」，不因本件改变该口径。
- 本件**不纳入** 2026-10-23 20:00 勘录回执与 INDEX——即未向 `ledger/protocols/compass-pedal-survey-2026-10-23-2000.md` 与 `ledger/protocols/INDEX.md` 追加任何内容，两者哈希保持不变。
- 不触发 Git 落盘动作；本件落盘后为未跟踪文件。
- **谱系隔离**：E4 逾期条目与 EP18 四卷（R1／R1.1-AUDIT／EP01 候选稿／R2 预批次）无谱系交叉，互不干扰；EP18 侧七项待仲裁队列不受本件影响，仍为 7 项。

## 五、解除条件

E4 转为可落盘状态，须同时满足：
1. RUL-PEND-E4-02 由正规定席裁定（二者择一）；
2. 其余 4 项各自裁定或明示标空位（如 03 选 `mark_undefined`）；
3. 按裁定结果对四件（E1~E4）执行 `sha256sum` 全量实测，回填 `lineage.*.hash` 的 `PENDING` 字段；
4. 依 `E4_main_baseline_plus_E1_E2_E3_history_slices` 策略（若采纳）建立历史切片独立哈希归档。

四项齐备前，E4 维持 `THEORY_FUSED / PENDING`，正文不动。
