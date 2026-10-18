# DT5322 媒体证据 · GitHub 上载统计（2026-10-17）

> 网页 `media_archive/` 目录常因 GitHub **1000 条列表上限**或 **仓库体积过大** 无法正常加载；**Git/API/clone 仍可用**。本文件供离线核对。

## 远程（GitHub API 实测）

| 项 | 值 |
|----|-----|
| 仓库 | `liu-hui-ming/carbon-silicon-canonical`（public） |
| 分支 | `media-evidence-archive` |
| 最新 commit | `d8c6d062`（2026-10-17T14:02:39Z） |
| 本分支相对 main 提交数 | 40（含 Batch0 + 31 批文件夹） |
| GitHub 显示 repo size | ~351414 KB（平台计量，非未压缩体积） |

## 本地 / Git 跟踪（与远程 HEAD 一致：`d8c6d062`）

| 项 | 值 |
|----|-----|
| 证据文件夹数 | 5471 |
| 磁盘文件总数 | 17026 |
| `page_screenshot.png` 数 | 5474 |
| 未压缩体积 | **≈ 7.56 GB**（8116792580 字节） |
| `git ls-files media_archive` | 16990 |

## 台账 AUDIT-LATEST.json（2026-10-17）

| 项 | 值 |
|----|-----|
| entry_total | 5470 |
| success_archived | 5467 |
| access_ok | 2847 |
| access_con | 2620 |
| pending | 3 |
| 标准 | P0-four-elements-v2 |

## 网页打不开时怎么用

1. `git clone -b media-evidence-archive --depth 1 https://github.com/liu-hui-ming/carbon-silicon-canonical.git`
2. 直接打开本机：`media_archive/AUDIT-LATEST.json`、`manifest_total.json`、`SHA256SUMS.txt`
3. 单条证据：已知文件夹名时访问  
   `https://github.com/liu-hui-ming/carbon-silicon-canonical/tree/media-evidence-archive/media_archive/<文件夹名>/`

<!-- project: path:/e/carbon-silicon-canonical -->
