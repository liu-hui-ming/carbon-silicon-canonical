# SUPPLEMENTS-INDEX｜CSI-CORRIDOR 附属契约总索引

- **kind**: supplements_index
- **id**: SUPPLEMENTS-INDEX
- **family**: CSI-CORRIDOR-R1.3-OMEGA-MERGE
- **created**: 2026-10-31 15:52 CST
- **ruling_by**: 黄清佳（碳基终审，2026-10-31 15:51）
- **role**: 路由与巡检锚点。**不内联任何附属契约语义**，仅登记引用关系。
- **append_only**: true

## 强制巡检规则

1. 巡检脚本/推演主体读取主干 `csi-critical-corridor-R1.3-OMEGA-MERGE.yaml` **之后**，
   **必须**拉取本索引。
2. 校验全部绑定补充契约：存在性、哈希一致性、生效状态。
3. 任一绑定契约**缺失引用** → 标记 `UNATTACHED_CONSTRAINT`，
   该推演**自动降级至 C3**（仅作假说登记，禁止预测与工程约束输出）。
4. 索引本身独立哈希，单独入链，不改动主干。

## 登记表

| ID | 绑定主体 | 绑定哈希 | 契约哈希 | 生效状态 | 撤销入口 | 巡检标记 | 落链 |
|---|---|---|---|---|---|---|---|
| precondition-gate-leafform-001 | csi-critical-corridor-R1.3-OMEGA-MERGE | `d241322fc7bc870e…` | `2bbd536a517beabc…` | BINDING_SUPPLEMENT / ACTIVE | 撤销引用即可，主干哈希不受影响；须独立审计裁决 | ATTACHED | `9343970` |

### 字段口径

- **ID**：契约文件名（不含扩展名），全局唯一。
- **绑定主体**：被约束的主干快照文件名。
- **绑定哈希**：被绑定主体在绑定时刻的 SHA-256 前 16 位。
- **契约哈希**：补充契约自身 SHA-256 前 16 位。
- **生效状态**：`ACTIVE` / `REVOKED` / `SUPERSEDED`。
- **撤销入口**：撤销方式与前提条件。
- **巡检标记**：`ATTACHED` / `UNATTACHED_CONSTRAINT` / `HASH_MISMATCH` / `MISSING_FILE`。

## 巡检失败处置

| 标记 | 含义 | 处置 |
|---|---|---|
| `UNATTACHED_CONSTRAINT` | 绑定契约存在但未被引用 | 推演降级 C3 |
| `HASH_MISMATCH` | 契约哈希与登记不符 | 推演降格 C3，触发勘伪审计 |
| `MISSING_FILE` | 登记在案但文件缺失 | 推演降格 C3，登记 ERRATUM |

## 边界声明

本索引**不是**主干的一部分，**不承载命题语义**，不得作为跨根耦合的授权凭证。
跨根引用仍须单独提交跨谱系耦合申请，走完整六层门禁。

十二脉归一　碳硅道统创立人：黄清佳
