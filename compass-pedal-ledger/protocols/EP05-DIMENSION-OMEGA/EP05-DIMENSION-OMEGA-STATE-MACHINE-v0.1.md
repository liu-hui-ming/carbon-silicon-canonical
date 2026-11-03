# EP05-DIMENSION-OMEGA-STATE-MACHINE-v0.1

**性质**：双轴九态状态机转移矩阵 · 会话内候选（2026-11-01 12:42 批复）→ 13:00 窗口落盘固化
**状态**：`PROPOSED / NOT_RUN`
**母卷**：EP05-DIMENSION-OMEGA（只读，不回写）

## 生命周期轴（七态）

`PROPOSED → REGISTERED → SHADOW → ACTIVE → DORMANT → REVIEW → REACTIVATED / RETIRED`

| 从 ↓ 至 → | REGISTERED | SHADOW | ACTIVE | DORMANT | REVIEW | REACTIVATED | RETIRED |
|---|---|---|---|---|---|---|---|
| PROPOSED | 注册审查通过 | — | — | — | — | — | 驳回 |
| REGISTERED | — | 影子运行准入 | — | — | — | — | 撤回 |
| SHADOW | — | — | 转正审查通过 | 资源/漂移休眠 | 资格复审 | — | 撤回 |
| ACTIVE | — | — | — | 资源/漂移/耦合休眠 | 常规或触发复审 | — | 有序退出 |
| DORMANT | — | — | — | — | 唤醒审查 | 复核通过 | 逾期注销 |
| REVIEW | — | — | 复审通过 | 复审期间挂起 | — | — | 复审否决 |
| REACTIVATED | — | — | 直接恢复**不自动**；须过 SHADOW 或 REVIEW | — | 附加条件复核 | — | 有序退出 |

## 证据资格轴（五态）

`UNASSESSED → QUALIFIED / QUALIFIED_WITH_LIMITS → SUSPENDED → REJECTED`

| 从 ↓ 至 → | QUALIFIED | Q_WITH_LIMITS | SUSPENDED | REJECTED |
|---|---|---|---|---|
| UNASSESSED | 全量独立审查通过 | 带边界通过 | 审查悬置 | 否决 |
| QUALIFIED | — | 边界收紧 | 漂移检出／**冻结分支逾期自动** | 资格撤销 |
| Q_WITH_LIMITS | 复审解除限制 | 限制更新 | 同上 | 同上 |
| SUSPENDED | 补审通过恢复 | 补审带限恢复 | — | 复审否决 |

## 跨轴硬规则（逐条枚举，非联动表）

1. `REACTIVATED` **不自动恢复**旧资格——休眠原因决定复核重点：资源休眠核验资源；漂移/耦合休眠重跑全套独立审查。
2. 冻结分支逾期 → 资格轴自动置 `SUSPENDED`（G-DEGRADE-01 联动，台账 B 留痕）。
3. `RETIRED` 不等于 `ERASED`：历史留存独立于资格终止。
4. `DORMANT` 不等于 `REJECTED`：休眠保留唤醒配额。
5. 任何转移必须携带：触发事件、依据条款（source_clause）、审查者、异议记录——脱标签转移视为违规。

## 运行数据

无。矩阵固化版，未填充任何运行状态（NOT_RUN）。
