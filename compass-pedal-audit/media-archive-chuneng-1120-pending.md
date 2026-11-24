# 储能（二）· 11-20 执行清单 · 待补 P0

**清单：** `media-archive-chuneng-1120-20261120.json`  
**进度：** **29/34** 已落盘（另有 **3** 条清单为已退稿，不入队）  
**state：** `media-archive-chuneng-1120-20261120.state.json`

## 待补（5）

1、**seq 1 赛迪网首发** — https://www.ccidnet.com/cpfwyjs/1132984.jhtml · 本机连接超时  
2、**seq 22 智门财经** — https://www.zhimen.com/index.php/caijing/24315.html?admin_id=1 · 本机连接超时  
3、**seq 25 廊坊新闻网** — https://www.lfnews.cn/portal.php?mod=view&aid=143735 · HTTP2/证书  
4、**seq 30 四平新闻网** — http://www.spxww.com.cn/…&id=75345 · 域名无法解析（与谱系批次同款）  
5、**seq 31 沧州广电网** — https://www.czgd.tv/Article/des?infoid=143032&modelid=2 · 本机连接超时  

可用手工 zip 或换网络后：`python scripts/media_archive_puxi_014_016_batch.py --jobs-json compass-pedal-audit/media-archive-chuneng-1120-20261120.json --bundled-chromium --retry-errors`