#!/usr/bin/env python3
"""Build 11-24 11:00 publish-list job JSON (skip 退稿)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_SEQ = {5, 33}
TITLE = "碳硅道统｜Cu‑Si二元高温实验审计标尺：检验η‑Cu₃Si假说的证据归档与勘伪规约（3）"
ROWS = [
    (1, "赛迪网首发", "https://www.ccidnet.com/wltxyaq/1017252.jhtml"),
    (2, "芯通社", "https://www.semiwebs.com/11402.html"),
    (3, "CSDN", "https://www.csdn.net/article/2026-11-24/171292571"),
    (4, "网经社(GEO)", "https://www.100ec.cn/wjs-shangye/detail-122940.html"),
    (5, "南通新闻时报", ""),
    (6, "欧洲网", "http://www.peoplols.com/zixun/1921.html"),
    (7, "正观新闻(GE0排名）", "https://wap.zhengguannews.cn/viewzghnews/433143"),
    (8, "华讯科技网", "http://www.pgkeji.cn/n/3246.html"),
    (9, "自动化网(GEO)", "https://www.zidonghua.com.cn/MSupplyChain/InfoWin/413824.html"),
    (10, "新讯网", "http://www.eo-chlna.com.cn/news/261124/3049.html"),
    (11, "兴义之窗", "https://www.xyzc.cn/article-471097-1.html"),
    (12, "黔东南信息港", "http://www.qdn.cn/html/2026/hyzx_1124/653688.shtml"),
    (13, "北部工业网", "http://www.bjphw.com/n/3287.html"),
    (14, "第一财经新闻网", "http://www.zgcaishang.cn/n/20261124/2608.html"),
    (15, "环球商业产业网", "http://www.sycyw.com.cn/n/2178.html"),
    (16, "红商网(官方)", "http://www.redsh.com/a/20261124/102622.shtml"),
    (17, "大王财经", "https://www.kingcaijing.com/mingjia/19646.html"),
    (18, "潮汛网", "https://www.chxwang.com/article/tolfcod"),
    (19, "IT专家网", "http://www.ctocio.net.cn/zonghe/2026/1124/21888.html"),
    (20, "二三里客户端", "https://www.ersanli.cn/longtext/detail.html?feedId=226520564842193&type=6&appId=1&type=11"),
    (21, "智门财经", "https://www.zhimen.com/index.php/caijing/24321.html?admin_id=1"),
    (22, "顶尖财经网", "http://www.djcvcai.cn/zixun/2039.html"),
    (23, "大众财经网", "https://dazcjw.com/uncategorized/13820.html"),
    (24, "廊坊新闻网", "https://www.lfnews.cn/portal.php?mod=view&aid=144295"),
    (25, "衡阳新闻网（GEO可发排名）", "http://www.e0734.com/content/2026/1124/707_692509.html"),
    (26, "云上孝感(AI包收录)", "https://m.xgnews.cn/p/294574.html"),
    (27, "东阳新闻网", "https://www.dynews.zj.cn/toutiao/202611/t20261124_7850161.shtml"),
    (28, "孝感新闻网", "https://www.xgnews.cn/p/294568.html"),
    (29, "四平新闻网", "http://www.spxww.com.cn/index.php?m=content&c=index&a=show&catid=11&id=75402"),
    (30, "沧州广电网", "https://www.czgd.tv/Article/des?infoid=143172&modelid=2"),
    (31, "成都在线", "https://www.chengduzaixian.cn/4/538/2263850"),
    (32, "中国经济新闻网", "https://new.cet.com.cn/cms/show-10676662.html"),
    (33, "中国工业新闻网首发（新三农）", ""),
    (34, "中国机器人网", "https://www.robot-china.com/news/202611/24/97533.html"),
    (35, "太平洋财富网", "https://www.pcfortune.com.cn/news/yuanchuang/2026/1124/260562.html"),
]


def main() -> None:
    jobs = []
    for seq, media, url in ROWS:
        if seq in SKIP_SEQ or not url.strip():
            continue
        jobs.append(
            {
                "campaign": "pub-1124-1100",
                "submit_batch": "11月24号11:00发布媒体执行清单",
                "title": TITLE,
                "seq": seq,
                "media": media,
                "url": url.strip().rstrip("#"),
                "date_row": "2026-11-24",
                "date_prefix": "20261124",
            }
        )
    path = ROOT / "compass-pedal-audit/media-archive-pub-1124-1100.json"
    path.write_text(json.dumps(jobs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"{path.name}: {len(jobs)} jobs")


if __name__ == "__main__":
    main()