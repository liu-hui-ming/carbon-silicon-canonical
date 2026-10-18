# 媒体证据台账与导出（与 `media_archive/` 分离）

`media_archive/` 下为五千余条 `YYYYMMDD_媒体_<hash8>/` 证据目录；**重采清单、统计、批次说明** 放在仓库根目录本文件夹，不进入 `media_archive/`。

## 审计主文件（仍在 `media_archive/` 根）

| 文件 | 说明 |
|------|------|
| `media_archive/AUDIT-LATEST.json` | 最新归档审计（OK / CON / pending） |
| `media_archive/manifest_total.json` | 总 manifest |
| `media_archive/SHA256SUMS.txt` | 校验和 |
| `media_archive/CON_LEDGER.json` | CON 旁审台账 |

## 本目录结构

| 路径 | 说明 |
|------|------|
| `stats/` | CON 细分、上传统计、历史 `AUDIT-BATCH-*.md` |
| `recapture-http0-20261017/` | **796 条 HTTP 0** 国内 IP 重采清单（CSV / JSON / urls.txt） |

重采截图写回 **`media_archive/<folder>/page_screenshot.png`**（CSV 的 `folder` 列），不要放进本目录。
