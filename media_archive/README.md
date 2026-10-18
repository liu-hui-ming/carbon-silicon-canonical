# 媒体首发证据链归档

分支：`media-evidence-archive`（与 `main` 永久分离）

目录规范：`media_archive/YYYYMMDD_媒体名称_<hash8>/`

每稿文件夹：

- `page_screenshot.png` — 全屏取证（含浏览器地址栏与系统任务栏时间）
- `article_source.txt` — 正文文本（不含报表价格字段）
- `manifest.fragment.json` — 本文件夹内文件 SHA256

根目录：

- `manifest_total.json` — 全局索引与卷宗总哈希
- `SHA256SUMS.txt` — 全量文件哈希清单
- `AUDIT-LATEST.json` — 最近批次审计（总数 / OK / CON）
- `CON_LEDGER.json` — 链接失效或取证异常旁审台账

清单 / 统计 / 重采列表在仓库根目录 **`media-evidence-ledger/`**（与本案证据目录分离）。

源表留在私有仓，不进 GitHub：

- `碳硅道统-发布报表.xlsx`（P0-176，已冻结）
- `2碳硅道体明细表-更新至20261012.xlsx`（DT5322 扩展批次，5294 去重链接，不含价格列入库）

扩展批次说明见 `../media-evidence-ledger/stats/AUDIT-BATCH-DT5322-20261014.md`。
