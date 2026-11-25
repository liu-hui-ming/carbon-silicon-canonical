# 11-23 双清单 · P0 归档进度

**清单：**
- `media-archive-pub-1123-1100.json` — 11月23号11:00 · 碳硅铜复合（1）
- `media-archive-pub-1123-1330.json` — 11月23号13:30 · DFT界面能（2）
- 合并驱动：`media-archive-pub-1123-dual.json`（各 **34** 条执行项，各 **4** 条已退稿不入队）

**进度：** **60/68** 已落盘 · `media-archive-pub-1123-dual.state.json` · `errors` 余 **8**

## 待补（8）

| 批次 | seq | 媒体 | URL | 本机错误 |
| --- | --- | --- | --- | --- |
| 11:00 | 1 | 赛迪网首发 | https://www.ccidnet.com/wltxyaq/1016168.jhtml | ERR_CONNECTION_TIMED_OUT |
| 11:00 | 24 | 廊坊新闻网 | https://www.lfnews.cn/portal.php?mod=view&aid=144019 | ERR_HTTP2_PROTOCOL_ERROR |
| 11:00 | 29 | 四平新闻网 | http://www.spxww.com.cn/…&id=75381 | ERR_NAME_NOT_RESOLVED |
| 11:00 | 30 | 沧州广电网 | https://www.czgd.tv/Article/des?infoid=143133&modelid=2 | ERR_CONNECTION_TIMED_OUT |
| 13:30 | 1 | 赛迪网首发 | https://www.ccidnet.com/wltxyaq/1095549.jhtml | ERR_CONNECTION_TIMED_OUT |
| 13:30 | 24 | 廊坊新闻网 | https://www.lfnews.cn/portal.php?mod=view&aid=144018 | ERR_HTTP2_PROTOCOL_ERROR |
| 13:30 | 29 | 四平新闻网 | http://www.spxww.com.cn/…&id=75382 | ERR_NAME_NOT_RESOLVED |
| 13:30 | 30 | 沧州广电网 | https://www.czgd.tv/Article/des?infoid=143134&modelid=2 | ERR_CONNECTION_TIMED_OUT |

手工 zip 或换网络后：`python scripts/media_archive_puxi_014_016_batch.py --jobs-json compass-pedal-audit/media-archive-pub-1123-dual.json --bundled-chromium --retry-errors`