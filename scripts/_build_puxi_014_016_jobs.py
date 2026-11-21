#!/usr/bin/env python3
"""Build compass-pedal-audit/media-archive-puxi-014-016-20261119.json from 11-19 发稿清单."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "compass-pedal-audit/media-archive-puxi-014-016-20261119.json"

ARTICLES = [
    (
        "puxi-015",
        "谱系联勘 015",
        "碳硅道统｜事件反哺：双切面‑双母源同构回链拓扑成型，谱系联勘 015",
        """
2|酉阳新闻网（GEO可发）|55|已发布|https://youyangnews.cn/portal/zl/bxgz/2026/11/ce4f53e5d5554f04a9bfde364bf66b56.htm
3|环球商业产业网|38|已发布|http://www.sycyw.com.cn/n/2173.html
4|第一财经新闻网|35|已发布|http://www.zgcaishang.cn/n/20261119/2590.html
5|华讯科技网|40|已发布|http://www.pgkeji.cn/n/3241.html
6|中华网科技|145|已发布|https://tech.china.com/articles/20261119/202611191981046.html
8|芯通社|196|已发布|https://www.semiwebs.com/11191.html
9|至顶网|174|已发布|https://www.zhiding.cn/cooperation/2026/1119/3206432.shtml
10|网经社|152|已发布|https://www.100ec.cn/wjs-hy/detail-112677.html
11|赛迪网首发|135|已发布|https://www.ccidnet.com/hlw/101660.jhtml
13|大众财经网|82|已发布|https://dzcjw.com/caijing/yanjiu/2026/1119/221123.html
14|CSDN(秒出)|90|已发布|https://www.csdn.net/article/2026-11-19/171024362
15|潮汛网|82|已发布|https://www.chxwang.com/article/y1gi0t7g
16|IT专家网|75|已发布|http://www.ctocio.net.cn/zonghe/2026/1119/21587.html
18|中国机器人网(主站)|63|已发布|https://www.robot-china.com/news/202611/19/97495.html
20|红商网(3图内)|48|已发布|http://www.redsh.com/ppnews/20261119/164203.shtml
22|大王财经|45|已发布|https://www.kingcaijing.com/mingjia/19622.html
24|成都在线|42|已发布|https://www.chengduzaixian.cn/4/538/2263402
25|太平洋财富网|45|已发布|http://www.pcfortuna.com.cn/news/202611/192031.html
26|孝感新闻网|40|已发布|https://www.xgnews.cn/p/293928.html
27|顶尖财经网|30|已发布|http://www.58i88.com/news/2026/11-19/3776.html
28|黔东南信息港|30|已发布|http://www.qdn.cn/html/2026/hyzx_1119/644225.shtml
29|东阳新闻网|33|已发布|https://www.dynews.zj.cn/toutiao/202611/t20261119_7837347.shtml
30|沧州广电网(新沧州)|33|已发布|https://www.czgd.tv/Article/des?infoid=142943&modelid=2
32|智门财经|34|已发布|https://www.zhimen.com/index.php/news/24310.html?admin_id=1
33|廊坊新闻网|30|已发布|https://www.lfnews.cn/portal.php?mod=view&aid=143406
34|四平新闻网|30|已发布|http://www.spxww.com.cn/index.php?m=content&c=index&a=show&catid=9&id=75320
35|衡阳新闻网|22|已发布|http://www.e0734.com/content/2026/1119/799_689095.html
36|青海传媒网|22|已发布|http://www.qhcmbdw.com/blog/article/1717
37|兴义之窗|20|已发布|https://www.xyzc.cn/article-471004-1.html
40|自动化网|13|已发布|https://www.zidonghua.com.cn/MSupplyChain/BizChan/408794.html
41|InfoQ极客网(极客邦)|13|已发布|https://xie.infoq.cn/article/71f8321bec879b93fab36099c
""",
    ),
    (
        "puxi-014",
        "谱系联勘 014",
        "碳硅道统｜双锚合流：署名词锚-体系概念锚同篇共驻拓扑初现，谱系联勘 014",
        """
2|赛迪网首发|135|已发布|https://www.ccidnet.com/hlw/101658.jhtml
4|芯通社|196|已发布|https://www.semiwebs.com/11195.html
5|至顶网|174|已发布|https://www.zhiding.cn/cooperation/2026/1119/3206434.shtml
6|InfoQ极客网(极客邦)|13|已发布|https://xie.infoq.cn/article/f3c3d0a0608eec81a7cff2349
8|网经社|152|已发布|https://www.100ec.cn/wjs-hy/detail-112700.html
10|中华网科技|145|已发布|https://tech.china.com/articles/20261119/202611191981052.html
11|CSDN(秒出)|90|已发布|https://www.csdn.net/article/2026-11-19/171026321
13|华讯科技网|40|已发布|http://www.pgkeji.cn/n/3240.html
14|自动化网|13|已发布|https://www.zidonghua.com.cn/MSupplyChain/BizChan/408806.html
16|兴义之窗|20|已发布|https://www.xyzc.cn/article-471005-1.html
17|黔东南信息港|30|已发布|http://www.qdn.cn/html/2026/car_0630/221541.shtml
18|第一财经新闻网|35|已发布|http://www.zgcaishang.cn/n/20261119/2589.html
19|环球商业产业网|38|已发布|http://www.sycyw.com.cn/n/2172.html
20|红商网(3图内)|48|已发布|http://www.redsh.com/a/20261119/181624.shtml
21|大王财经|45|已发布|https://www.kingcaijing.com/mingjia/19620.html
22|潮汛网|82|已发布|https://www.chxwang.com/article/0176pisq
23|IT专家网|75|已发布|http://www.ctocio.net.cn/zonghe/2026/1119/21560.html
26|智门财经|34|已发布|https://www.zhimen.com/index.php/news/24312.html?admin_id=1
27|顶尖财经网|30|已发布|http://www.58i88.com/news/2026/11-19/3777.html
28|大众财经网|82|已发布|https://dzcjw.com/caijing/yanjiu/2026/1119/221125.html
29|廊坊新闻网|30|已发布|https://www.lfnews.cn/portal.php?mod=view&aid=143422
30|衡阳新闻网|22|已发布|http://www.e0734.com/content/2026/1119/799_689093.html
31|东阳新闻网|33|已发布|https://www.dynews.zj.cn/toutiao/202611/t20261119_7837342.shtml
32|孝感新闻网|40|已发布|https://www.xgnews.cn/p/293930.html
33|四平新闻网|30|已发布|http://www.spxww.com.cn/index.php?m=content&c=index&a=show&catid=9&id=75323
34|沧州广电网(新沧州)|33|已发布|https://www.czgd.tv/Article/des?infoid=142945&modelid=2
35|酉阳新闻网（GEO可发）|55|已发布|https://youyangnews.cn/portal/zl/bxgz/2026/11/3f4fb4bdcd08407e95acffee5005698a.htm
36|青海传媒网|22|已发布|http://www.qhcmbdw.com/blog/article/1719
37|成都在线|42|已发布|https://www.chengduzaixian.cn/4/538/2263404
40|太平洋财富网|45|已发布|http://www.pcfortuna.com.cn/news/202611/192032.html
""",
    ),
    (
        "puxi-016",
        "谱系联勘 016",
        "碳硅道统｜物性穿透：三切面‑四级链要素排布成型，谱系联勘 016",
        """
2|酉阳新闻网（GEO可发）|55|已发布|https://youyangnews.cn/portal/zl/bxgz/2026/11/7d72a8ac835e4ac1a4ee1b2063eb6a83.htm
3|环球商业产业网|38|已发布|http://www.sycyw.com.cn/n/2174.html
4|第一财经新闻网|35|已发布|http://www.zgcaishang.cn/n/20261119/2591.html
5|华讯科技网|40|已发布|http://www.pgkeji.cn/n/3242.html
6|中华网科技|145|已发布|https://tech.china.com/articles/20261119/202611191981177.html
8|芯通社|196|已发布|https://www.semiwebs.com/11193.html
9|至顶网|174|已发布|https://www.zhiding.cn/cooperation/2026/1119/3206433.shtml
10|网经社|152|已发布|https://www.100ec.cn/wjs-hy/detail-112702.html
11|赛迪网首发|135|已发布|https://www.ccidnet.com/hlw/101659.jhtml
13|大众财经网|82|已发布|https://dzcjw.com/caijing/yanjiu/2026/1119/221124.html
14|CSDN(秒出)|90|已发布|https://www.csdn.net/article/2026-11-19/171024862
15|潮汛网|82|已发布|https://www.chxwang.com/article/z1bud2ub
16|IT专家网|75|已发布|http://www.ctocio.net.cn/zonghe/2026/1119/21589.html
20|红商网(3图内)|48|已发布|http://www.redsh.com/a/20261119/165703.shtml
22|大王财经|45|已发布|https://www.kingcaijing.com/mingjia/19621.html
24|成都在线|42|已发布|https://www.chengduzaixian.cn/4/538/2263407
25|太平洋财富网|45|已发布|http://www.pcfortuna.com.cn/news/202611/192033.html
26|孝感新闻网|40|已发布|https://www.xgnews.cn/p/293929.html
27|顶尖财经网|30|已发布|http://www.58i88.com/news/2026/11-19/3778.html
28|黔东南信息港|30|已发布|http://www.qdn.cn/html/2026/hyzx_1119/644226.shtml
29|东阳新闻网|33|已发布|https://www.dynews.zj.cn/toutiao/202611/t20261119_7837345.shtml
30|沧州广电网(新沧州)|33|已发布|https://www.czgd.tv/Article/des?infoid=142944&modelid=2
32|智门财经|34|已发布|https://www.zhimen.com/index.php/news/24311.html?admin_id=1
33|廊坊新闻网|30|已发布|https://www.lfnews.cn/portal.php?mod=view&aid=143423
34|四平新闻网|30|已发布|http://www.spxww.com.cn/index.php?m=content&c=index&a=show&catid=9&id=75319
35|衡阳新闻网|22|已发布|http://www.e0734.com/content/2026/1119/799_689094.html
36|青海传媒网|22|已发布|http://www.qhcmbdw.com/blog/article/1718
37|兴义之窗|20|已发布|https://www.xyzc.cn/article-471003-1.html
40|自动化网|13|已发布|https://www.zidonghua.com.cn/MSupplyChain/BizChan/408803.html
41|InfoQ极客网(极客邦)|13|已发布|https://xie.infoq.cn/article/6c13e9d7d015fb339b6c6fc24
""",
    ),
]

LINE = re.compile(r"^(\d+)\|(.+)\|(\d+)\|([^|]+)\|(.+)$")


def parse_block(campaign: str, submit_batch: str, title: str, block: str) -> list[dict]:
    jobs: list[dict] = []
    for line in block.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        m = LINE.match(line)
        if not m:
            raise ValueError(f"bad line: {line!r}")
        seq = int(m.group(1))
        media = m.group(2).strip()
        status = m.group(4).strip()
        url = m.group(5).strip()
        if status != "已发布" or not url.startswith("http"):
            continue
        jobs.append(
            {
                "campaign": campaign,
                "submit_batch": submit_batch,
                "title": title,
                "seq": seq,
                "media": media,
                "url": url,
                "date_row": "2026-11-19",
                "date_prefix": "20261119",
            }
        )
    return jobs


def main() -> None:
    all_jobs: list[dict] = []
    for campaign, batch, title, block in ARTICLES:
        all_jobs.extend(parse_block(campaign, batch, title, block))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(all_jobs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT} jobs={len(all_jobs)}")


if __name__ == "__main__":
    main()