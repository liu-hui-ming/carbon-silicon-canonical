# 11-24 11:00 清单 · P0 归档进度

**清单：** `media-archive-pub-1124-1100.json`  
**标题：** 碳硅道统｜Cu‑Si二元高温实验审计标尺：检验η‑Cu₃Si假说的证据归档与勘伪规约（3）  
**入队：** **33**（退稿 seq 5、33 未入队）  
**进度：** **27/33** · `media-archive-pub-1124-1100.state.json` · `errors` 余 **6**

## 待补（6）

| seq | 媒体 | URL | 本机错误 |
| --- | --- | --- | --- |
| 1 | 赛迪网首发 | https://www.ccidnet.com/wltxyaq/1017252.jhtml | ERR_CONNECTION_TIMED_OUT |
| 24 | 廊坊新闻网 | https://www.lfnews.cn/portal.php?mod=view&aid=144295 | ERR_HTTP2_PROTOCOL_ERROR |
| 25 | 衡阳新闻网 | http://www.e0734.com/content/2026/1124/707_692509.html | ERR_CONNECTION_TIMED_OUT |
| 26 | 云上孝感 | https://m.xgnews.cn/p/294574.html | ERR_CONNECTION_TIMED_OUT |
| 29 | 四平新闻网 | http://www.spxww.com.cn/…&id=75402 | ERR_NAME_NOT_RESOLVED |
| 30 | 沧州广电网 | https://www.czgd.tv/Article/des?infoid=143172&modelid=2 | ERR_CONNECTION_TIMED_OUT |

`python scripts/media_archive_puxi_014_016_batch.py --jobs-json compass-pedal-audit/media-archive-pub-1124-1100.json --bundled-chromium --retry-errors`