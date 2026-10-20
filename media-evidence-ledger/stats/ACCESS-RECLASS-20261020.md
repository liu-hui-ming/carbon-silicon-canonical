# ACCESS 重算统计（2026-10-20）

## 口径

- **OK**：`page_screenshot.png` 为正常体积取证（≥80KB 或国内重采 ≥45KB），且非「404/内容不存在」错误页。
- **CON / 打不开**：无 PNG、HTTP0、404/失效、403/502 等；见 **`URL-UNREACHABLE-20261020.csv`**。
- **国内 IP 回传** 122 条：有中等以上 PNG 且无「链接失效：是」→ 优先 **OK**。

## 汇总

| 项 | 数量 |
|----|------|
| 总条目 | 5470 |
| **OK** | **5358** |
| **CON（打不开/异常）** | **112** |

## CON 按「打不开」分类

| 分类 | 条数 |
|------|------|
| 404_错误页截图 | 109 |
| 其他CON | 2 |
| 源站无内容/无PNG | 1 |

## AUDIT（重算后）

- `access_ok`: 5359
- `access_con`: 113
- `pending`: 0

## 文件

- `media-evidence-ledger/stats/URL-UNREACHABLE-20261020.csv`
