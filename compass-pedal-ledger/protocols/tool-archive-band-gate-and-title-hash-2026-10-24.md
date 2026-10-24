# 方案存档：带内/带外判定工具 + 标题清单哈希双工具（长期基准）

- 归档日期：2026-10-24 11:05 CST
- 授权：创立人 2026-10-24 11:00「好的方案要懂得存档值得长期进行使用」
- 状态：`ARCHIVED_FOR_REUSE / NOT_EFFECTIVE`
  - 工具可复用、可长期维护；**纪律不因此放宽**：`band_threshold` 未裁定前，任何判定结论不得作为正式门禁依据。
- 归属：`config/hr-review-gates.yaml`（规则与判例锚）+ `csdt-tools/`（可执行实现）。本文件只做「方案层」存档，不复制规则正文，避免同步负担。

---

## 一、为什么存档

HB-1107 判例（cache 0.8888 < 0.9 → 非主导）第一次让「改口径」落在文件上而非叙事里。同批产出的两个工具与三类设计取舍，属于可被后续轮次反复调用的**方法资产**，不是一轮一次性产物。若不存档，下一轮重新发明，误差复利。

---

## 二、存档清单（三件可执行 + 一份规则载体）

| 工件 | SHA256 | 职责域 | 状态 |
|---|---|---|---|
| `csdt-tools/band-gate-evaluator.py` | `254f9b9a45df060718e2e92c19820b513bd180a2e5b51ac8c2e775fc98603041` | 带内/带外 + 可比判定 | 原型，pending fail-closed |
| `csdt-tools/title-list-hash.py` | `084b5a7052aff4f12830272a5eda5486058dd78950317b2c5abe2e293ef3e2e0` | canonical 标题清单哈希（L2 基准） | 在用，`93c53507bc3b` 可复现 |
| `csdt-tools/title-list-file-hash.py` | `2d99d3215b97832824744cb6529220e5b7feacf9f967d99b1eebc55c97019092` | 独立 JSON 文件字节哈希 + 清单自检 | 新增，无默认路径 |
| `config/hr-review-gates.yaml` | `94a6e86a6162eb8b2cecc45dbd4d5646308b262999c08e6d903644106aee0509` | 门禁规则 + 判例锚 | `EFFECTIVE_TEXT_ONLY / NOT_IMPLEMENTED` |

全部 `??` 未跟踪，零 Git 操作。

---

## 三、归档的设计取舍（复用时要守住的五条）

1. **度量对象不可混**：canonical 清单哈希 ≠ 文件字节哈希。前者回答「源档标题提取后规范化是否同源」，后者回答「这份 JSON 字节是否变动、清单是否干净」。混用即口径漂移。为此 `title-list-file-hash.py` 输出固定带 `hash_scope: raw_file_bytes` 字段，人类可读输出亦打印 scope 行。

2. **未裁定即 fail-closed**：`ACTIVE_STATUSES = frozenset({"ACTIVE"})` 白名单，其余任何值（含 `ACTIVE_ISH`、`active`、带尾空格）一律返回 `UNDEFINED`。降级为「只挡一个枚举值」等于留后门。

3. **严格键、fail-fast**：`C1_COMPLETION / C2_SAME_DENOMINATOR / C3_SELF_DECLARED` 必须全为 bool 且齐备，缺键或类型错直接抛 `ValueError`。**不得**用 `.get(key, False)` 默认补齐——那会把「传错字段」伪装成「条件不满足」。不得加短键别名。

4. **无静默默认**：需要路径的地方强制显式指定。默认值指向不存在文件，会把「路径配错」误报成「配置问题」。

5. **哈希与校验分离**：`--verify` 失败不污染 hash 字段；hash 可算但清单有错时，两件事分别报告，不互相掩盖。

---

## 四、预警区结构（保留 + 待裁）

- 原草案 `warning_zone: (0.15, 0.30)` 与 `inner_lower: 0.15` 重叠，判定顺序会使下半区永远无法命中 `WARNING_ZONE` → 属真 bug。
- 现结构：`warning_margin: 0.05` 对称外扩，`warn_low = max(0, lower - margin)`、`warn_high = upper + margin`，并校验 `0 ≤ lower ≤ upper`、`margin ≥ 0`。
- `inner_lower` / `inner_upper` / `margin` 数值本身**仍为占位**，随 A 分母裁定（`scoring-100x100-draft` 四问①）一并定。改动这些数值 = 改口径 → 须先报。

---

## 五、复用规程

- 启用前必须替换：`BAND_THRESHOLD["status"]`（改为 `ACTIVE` 且只由裁定授权）+ 三个阈值数值 + 记录裁定出处。
- 启用后首轮须留痕：谁改的、依哪条裁定、改前改后哈希。
- 归档不构成「已实现」：`config` 侧仍为 `EFFECTIVE_TEXT_ONLY / NOT_IMPLEMENTED`，除非另有执行层接入记录。
- 任何一条取舍要改，按「改口径先报」处理，不得静默放宽。

---

## 六、与判例锚的关系

判例正文归 `config/hr-review-gates.yaml` → `dominant_component.precedents`（`HB-1107-DOMINANT-REJECTED`），本文件只引用不复述。追溯判例确立时间，以 config 注释与（将来启用的）git history 为准。
