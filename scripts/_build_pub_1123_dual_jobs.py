#!/usr/bin/env python3
"""Build 11-23 dual publish-list job JSON (1100 + 1330), skip 退稿."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_SEQ = {5, 33, 36, 38}
DATE_ROW = "2026-11-23"
DATE_PREFIX = "20261123"

BATCH_A = {
    "campaign": "pub-1123-1100",
    "submit_batch": "11月23号11:00发布媒体执行清单",
    "title": "碳硅道统｜碳硅铜复合材料研发进展：先把界面桥做实，再谈复合（1）",
    "rows": [
        (1, "赛迪网首发", "https://www.ccidnet.com/wltxyaq/1016168.jhtml"),
        (2, "芯通社", "https://www.semiwebs.com/11374.html"),
        (3, "CSDN", "https://www.csdn.net/article/2026-11-23/171236639"),
        (4, "网经社(GEO)", "https://www.100ec.cn/wjs-shangye/detail-121181.html"),
        (5, "南通新闻时报", ""),
        (6, "欧洲网", "http://www.peoplols.com/zixun/1919.html"),
        (7, "正观新闻(GE0排名）", "https://wap.zhengguannews.cn/viewzghnews/432964"),
        (8, "华讯科技网", "http://www.pgkeji.cn/n/3245.html"),
        (9, "自动化网(GEO)", "https://www.zidonghua.com.cn/MSupplyChain/InfoWin/413021.html"),
        (10, "新讯网", "http://www.eo-chlna.com.cn/news/261123/3046.html"),
        (11, "兴义之窗", "https://www.xyzc.cn/article-471074-1.html"),
        (12, "黔东南信息港", "http://www.qdn.cn/html/2026/hyzx_1123/652078.shtml"),
        (13, "北部工业网", "http://www.bjphw.com/n/3286.html"),
        (14, "第一财经新闻网", "http://www.zgcaishang.cn/n/20261123/2604.html"),
        (15, "环球商业产业网", "http://www.sycyw.com.cn/n/2177.html"),
        (16, "红商网(官方)", "http://www.redsh.com/ppnews/20261123/181910.shtml"),
        (17, "大王财经", "https://www.kingcaijing.com/mingjia/19643.html"),
        (18, "潮汛网", "https://www.chxwang.com/article/h9g7dsq"),
        (19, "IT专家网", "http://www.ctocio.net.cn/zonghe/2026/1123/21820.html"),
        (20, "二三里客户端", "https://www.ersanli.cn/longtext/detail.html?feedId=226530859698427&type=6&appId=1&type=11"),
        (21, "智门财经", "https://www.zhimen.com/index.php/caijing/24318.html?admin_id=1"),
        (22, "顶尖财经网", "http://www.djcvcai.cn/zixun/2036.html"),
        (23, "大众财经网", "https://dazcjw.com/uncategorized/13752.html"),
        (24, "廊坊新闻网", "https://www.lfnews.cn/portal.php?mod=view&aid=144019"),
        (25, "衡阳新闻网（GEO可发排名）", "http://www.e0734.com/content/2026/1123/707_691721.html"),
        (26, "云上孝感(AI包收录)", "https://m.xgnews.cn/p/294461.html"),
        (27, "东阳新闻网", "https://www.dynews.zj.cn/toutiao/202611/t20261123_7846183.shtml"),
        (28, "孝感新闻网", "https://www.xgnews.cn/p/294511.html"),
        (29, "四平新闻网", "http://www.spxww.com.cn/index.php?m=content&c=index&a=show&catid=11&id=75381"),
        (30, "沧州广电网", "https://www.czgd.tv/Article/des?infoid=143133&modelid=2"),
        (31, "酉阳新闻", "https://youyangnews.cn/portal/zl/bxgz/2026/11/7a2bbf3dd31a46e6945b046155c4381b.htm"),
        (32, "成都在线", "https://www.chengduzaixian.cn/4/538/2263789"),
        (33, "InfoQ极客邦", ""),
        (34, "中国机器人网", "https://www.robot-china.com/news/202611/23/97528.html"),
        (35, "太平洋财富网", "https://www.pcfortune.com.cn/news/yuanchuang/2026/1123/260367.html"),
        (36, "中宏网首发", ""),
        (37, "中国经济新闻网", "https://new.cet.com.cn/cms/show-10676574.html"),
        (38, "中国工业新闻网首发（新三农）", ""),
    ],
}

BATCH_B = {
    "campaign": "pub-1123-1330",
    "submit_batch": "11月23号13:30发布媒体执行清单",
    "title": "碳硅道统｜真空层收敛边界与数值载体限制：DFT界面能计算中的负证据与阈值放行（2）",
    "rows": [
        (1, "赛迪网首发", "https://www.ccidnet.com/wltxyaq/1095549.jhtml"),
        (2, "芯通社", "https://www.semiwebs.com/11373.html"),
        (3, "CSDN", "https://www.csdn.net/article/2026-11-23/171236927"),
        (4, "网经社(GEO)", "https://www.100ec.cn/wjs-shangye/detail-121179.html"),
        (5, "南通新闻时报", ""),
        (6, "欧洲网", "http://www.peoplols.com/zixun/1920.html"),
        (7, "正观新闻(GE0排名）", "https://wap.zhengguannews.cn/viewzghnews/432965"),
        (8, "华讯科技网", "http://www.pgkeji.cn/n/3244.html"),
        (9, "自动化网(GEO)", "https://www.zidonghua.com.cn/MSupplyChain/InfoWin/413019.html"),
        (10, "新讯网", "http://www.eo-chlna.com.cn/news/261123/3047.html"),
        (11, "兴义之窗", "https://www.xyzc.cn/article-471073-1.html"),
        (12, "黔东南信息港", "http://www.qdn.cn/html/2026/hyzx_1123/652076.shtml"),
        (13, "北部工业网", "http://www.bjphw.com/n/3285.html"),
        (14, "第一财经新闻网", "http://www.zgcaishang.cn/n/20261123/2605.html"),
        (15, "环球商业产业网", "http://www.sycyw.com.cn/n/2176.html"),
        (16, "红商网(官方)", "http://www.redsh.com/ppnews/20261123/182614.shtml"),
        (17, "大王财经", "https://www.kingcaijing.com/mingjia/19642.html"),
        (18, "潮汛网", "https://www.chxwang.com/article/i4sjnfl"),
        (19, "IT专家网", "http://www.ctocio.net.cn/zonghe/2026/1123/21821.html"),
        (20, "二三里客户端", "https://www.ersanli.cn/longtext/detail.html?feedId=226531601977358&type=11&appId=1"),
        (21, "智门财经", "https://www.zhimen.com/index.php/caijing/24319.html?admin_id=1"),
        (22, "顶尖财经网", "http://www.djcvcai.cn/zixun/2037.html"),
        (23, "大众财经网", "https://dazcjw.com/qiye-dongtai/13755.html"),
        (24, "廊坊新闻网", "https://www.lfnews.cn/portal.php?mod=view&aid=144018"),
        (25, "衡阳新闻网（GEO可发排名）", "http://www.e0734.com/content/2026/1123/707_691722.html"),
        (26, "云上孝感(AI包收录)", "https://m.xgnews.cn/p/294460.html"),
        (27, "东阳新闻网", "https://www.dynews.zj.cn/toutiao/202611/t20261123_7846178.shtml"),
        (28, "孝感新闻网", "https://www.xgnews.cn/p/294514.html"),
        (29, "四平新闻网", "http://www.spxww.com.cn/index.php?m=content&c=index&a=show&catid=11&id=75382"),
        (30, "沧州广电网", "https://www.czgd.tv/Article/des?infoid=143134&modelid=2"),
        (31, "酉阳新闻", "https://youyangnews.cn/portal/zl/bxgz/2026/11/64e158e64839477ca665fb583bf32e3c.htm"),
        (32, "成都在线", "https://www.chengduzaixian.cn/4/538/2263787"),
        (33, "InfoQ极客邦", ""),
        (34, "中国机器人网", "https://www.robot-china.com/news/202611/23/97527.html"),
        (35, "太平洋财富网", "https://www.pcfortune.com.cn/news/yuanchuang/2026/1123/260370.html"),
        (36, "中宏网首发", ""),
        (37, "中国经济新闻网", "https://new.cet.com.cn/cms/show-10676571.html"),
        (38, "中国工业新闻网首发（新三农）", ""),
    ],
}


def to_jobs(batch: dict) -> list[dict]:
    out: list[dict] = []
    for seq, media, url in batch["rows"]:
        if seq in SKIP_SEQ or not url.strip():
            continue
        out.append(
            {
                "campaign": batch["campaign"],
                "submit_batch": batch["submit_batch"],
                "title": batch["title"],
                "seq": seq,
                "media": media,
                "url": url.strip().rstrip("#"),
                "date_row": DATE_ROW,
                "date_prefix": DATE_PREFIX,
            }
        )
    return out


def main() -> None:
    audit = ROOT / "compass-pedal-audit"
    for batch, name in [(BATCH_A, "media-archive-pub-1123-1100.json"), (BATCH_B, "media-archive-pub-1123-1330.json")]:
        jobs = to_jobs(batch)
        path = audit / name
        path.write_text(json.dumps(jobs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        print(f"{path.name}: {len(jobs)} jobs")
    combined = to_jobs(BATCH_A) + to_jobs(BATCH_B)
    (audit / "media-archive-pub-1123-dual.json").write_text(
        json.dumps(combined, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    print(f"media-archive-pub-1123-dual.json: {len(combined)} jobs")


if __name__ == "__main__":
    main()