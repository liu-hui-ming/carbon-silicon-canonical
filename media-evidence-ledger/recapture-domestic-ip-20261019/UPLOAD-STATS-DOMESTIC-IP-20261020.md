# 国内 IP 重采 · 上载统计（2026-10-20）

> 远程分支 `media-evidence-archive` HEAD 以本机 `git rev-parse HEAD` 为准。

## 一、partA/partB → GitHub（本次国内机回传）

| 项 | 数量 | 说明 |
|----|------|------|
| 回传包文件夹（partA+partB，剔除前） | 124 | 含无 PNG 的创业家 staging |
| **已合并并 push 到 `media_archive/`** | **122** | 见 `INGEST-REPORT-20261020.json` → `ingested` |
| **未进入主归档（未上传）** | **1** | `20260902_创业邦首发_005c7b29`：hash8 不在 5470 catalog |
| **已从清单剔除（不再重采）** | **1** | 创业家 `d145a260`：源站内容不存在 |
| partA/B 现剩 staging 目录 | 123 | 已删创业家 staging；创业邦包仍在（未 merge） |

## 二、清单 CSV（`同域待重采_CON`）

| 项 | 数量 |
|----|------|
| 更新后行数 | 119 |
| 本次删除（创业家 d145a260 等） | 0 |

## 三、全库 `media_archive/`（GitHub 证据分支）

| 项 | 值 |
|----|-----|
| AUDIT `entry_total` | 5470 |
| `access_ok` / `access_con` | 2851 / 2621 |
| 磁盘证据目录数 | 5471 |
| `page_screenshot.png` 文件数 | 5469 |
| **无 PNG 目录** | 2：20260706_创业家（头条号）_d145a260, MANUAL-UPLOAD-CON9 |

## 四、结论（你要的两句话）

- **国内回传 batch：已上传 GitHub `122` 条**（目录级合并 + batch 40 与后续台账 commit）。
- **仍未上传主归档：`1` 条**（创业邦 845135 / `005c7b29`，仅 staging 在 `partA`，未进 5470 catalog）；**创业家 d145a260 不计入待传，已从清单删除。**

## 五、本地与远程

- 执行本脚本后请 `git status media_archive`：若无未提交改动，则与 `origin/media-evidence-archive` 一致。
- 私表 `2碳硅道体明细表-更新至20261012.xlsx` 仍 **禁公仓**。

