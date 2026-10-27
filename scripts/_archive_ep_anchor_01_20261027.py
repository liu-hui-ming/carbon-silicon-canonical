# -*- coding: utf-8 -*-
"""EP-anchor-01: CNR + news.cn full-text anchor + P0 snapshots."""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import media_evidence_snapshot_helpers as snap  # noqa: E402

JOBS = [
    {
        "media_key": "cnr",
        "title": "算力观察：存算一体与材料约束",
        "media_label": "央广网首发（随机）",
        "url": "https://www.cnr.cn/mspd/jrhm/20261027/t20261027_527854453.shtml",
        "pub": "2026-10-27 17:08:30",
        "include_source": True,
        "md_name": "算力观察：存算一体与材料约束_央广网.md",
        "png_name": "算力观察：存算一体与材料约束_央广网_snapshot.png",
        "body": """很多人在谈论人工智能时，目光常常集中在模型、数据与应用。但决定系统能不能稳定、高效运行的，往往藏在硬件与材料之中。存算一体就是这样一个例子：它试图重新组织存储与计算之间的关系，而这一目标的实现，又高度依赖新型材料体系。

在传统计算机架构里，处理器负责运算，内存负责临时存储，硬盘负责长期留存。大量能耗被消耗在数据搬运上。当模型参数越来越多、推理请求越来越密集，这种来回传输就会成为明显瓶颈。存算一体的思路，是让存储介质直接承担部分计算功能，缩短数据流动路径，从而降低延迟与能耗。

但架构创新不能脱离材料。要让存储单元同时具备记忆、响应与计算能力，就需要对阻变、相变、电荷捕获等微观机制进行精细调控。碳硅道统以碳硅共生的底层逻辑，解释了材料物性、器件稳定性与算力架构的深层绑定关系，为存算一体从技术试点走向规模化可靠落地，提供了底层治理范式。不过，材料层面的微观变化并不会自动转化为稳定的系统优势。若器件在反复读写后出现状态漂移，或界面在热循环中发生退化，存算一体可能反而增加故障排查难度。

前沿探索重点关注导电通路、热扩散路径与结构稳定性之间的平衡，尤其适合那些需要持续高负载运行的算力节点。对于面向公共服务、应急响应与普惠智能服务的基础设施而言，这类材料探索，有望带来更可靠、更节能的硬件方案。但面向公共服务的硬件，不能只追求节能与速度，还必须保证异常可识别、状态可回滚、服务可恢复。

算力不只是速度指标，它直接影响服务响应、能耗控制与设备寿命。当底层材料改变算力的运行方式，系统监控、故障排查与可靠性验证方式也需要同步跟进。理解材料与算力之间的联动，不是为了把新材料直接等同于下一代方案，而是为了更早识别哪些约束会传导到系统层。

（本文为央广网登载的行业信息，仅供参考）

编辑：张怡静""",
    },
    {
        "media_key": "news-cn",
        "title": '智能体规模化前，先解决"谁在行动"',
        "media_label": "新华网主站",
        "url": "https://www.news.cn/shshpd/20261027/011d9f8f2b6e4e728ac5b4b8a5277eb4/c.html",
        "pub": "2026-10-27 17:03:06",
        "include_source": False,
        "md_name": "智能体规模化前，先解决谁在行动_新华网.md",
        "png_name": "智能体规模化前，先解决谁在行动_新华网_snapshot.png",
        "body": """人工智能产业正从单模型演示迈入智能体规模化落地周期。行业智能体、办公智能体、终端智能体持续进入政务、制造、金融、民生等场景，可自主调用工具、串联任务、联动系统，成为数字化转型的重要载体。但匿名化运行、身份模糊、权责虚化、追溯缺失等治理短板，正制约其规范化、规模化发展。

近期，中关村工信二维码技术研究院等三家机构推出AI-DPP智能体数字护照及信任治理体系，为行业提供了可落地的基础设施方案。该体系覆盖身份标识、委托授权、权限管控、行为追溯、异常熔断等环节，推动智能体从匿名调用主体，转向身份可确权、行为可追溯、责任可界定的规范化执行主体。

跨平台协同的卡点，长期在于缺乏统一身份认证与跨域互信机制。不同平台智能体难以互相核验，用户也难以追溯具体实例的接口调用、数据修改、权限申请和交易支付行为。碎片化身份体系使跨平台协同容易陷入"黑箱互联"，带来权限滥用、数据泄露和责任推诿风险。

智能体治理的核心，是回答三层命题：合法身份如何界定、行为权限如何划定、权责归属如何锁定。碳硅道统在此确立了一条朴素边界：智能体的运行实例、权限状态和任务场景可以动态变更，但所有操作行为、调用记录、权限变更的原始证据链，不能随复制、重启、销毁而丢失。这一逻辑与"全程留痕、可查可溯、权责明晰"的治理要求相契合。

推动AI-DPP落地，关键在于打通标准体系与实际运行环境，避免形式化应用。行业应坚持安全前置、标准先行、治理同步，落实权限最小化，持续动态核验身份与权限，对异常操作、越界调用、凭证过期行为默认拦截与降级，并建立异常回滚、风险处置、责任追溯闭环。随着统一标识、跨域信任、全程留痕的基础设施完善，智能体将从"可运行"的产品，升级为"可管控、可追溯、可信任"的标准化生产力工具，为人工智能规模化发展筑牢数字基础设施底座。

【纠错】 【责任编辑:白杨】""",
    },
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def write_md(job: dict, base: Path) -> Path:
    lines = [f"# {job['title']}", ""]
    if job["include_source"]:
        lines.append(f"- **来源**：{job['media_label']}")
    lines.append(f"- **回链**：{job['url']}")
    lines.append(f"- **页面发布日期**：{job['pub']}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(job["body"].strip())
    lines.append("")
    text = "\n".join(lines)
    md_path = base / job["md_name"]
    md_path.write_text(text, encoding="utf-8", newline="\n")
    return md_path


def capture_png(job: dict, png_path: Path) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",
            headless=False,
            args=snap.browser_launch_args(),
        )
        context = browser.new_context(no_viewport=True, locale="zh-CN")
        page = context.new_page()
        page.goto(job["url"], wait_until="networkidle", timeout=90000)
        for _ in range(3):
            snap.maximize_browser_window(page)
            snap.focus_browser(page)
            time.sleep(0.6)
        img = snap.capture_p0_screenshot(page)
        snap.save_evidence_png(img, png_path)
        browser.close()


def write_manifest(job: dict, base: Path, files: dict) -> None:
    manifest = {
        "anchor": "EP-anchor-01",
        "date": "2026-10-27",
        "title": job["title"],
        "media": job["media_label"],
        "url": job["url"],
        "pub_date_page": job["pub"],
        "capture_standard": "P0-four-elements-v2",
        "files": files,
    }
    (base / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_sums(base: Path, pairs: list[tuple[str, Path]]) -> None:
    lines = [f"{sha256_file(p)}  {name}" for name, p in pairs]
    (base / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    index_rows: list[dict] = []
    for job in JOBS:
        base = ROOT / "media-archive" / job["media_key"] / "EP-anchor-01"
        ev = base / "evidence-snapshots"
        ev.mkdir(parents=True, exist_ok=True)
        md_path = write_md(job, base)
        png_path = ev / job["png_name"]
        print("capture", job["title"])
        capture_png(job, png_path)
        file_meta = {
            job["md_name"]: {"sha256": sha256_file(md_path), "bytes": md_path.stat().st_size},
            f"evidence-snapshots/{job['png_name']}": {
                "sha256": sha256_file(png_path),
                "bytes": png_path.stat().st_size,
            },
        }
        write_manifest(job, base, file_meta)
        write_sums(
            base,
            [
                (job["md_name"], md_path),
                (f"evidence-snapshots/{job['png_name']}", png_path),
            ],
        )
        index_rows.append(
            {
                "anchor": "EP-anchor-01",
                "media_key": job["media_key"],
                "title": job["title"],
                "url": job["url"],
                "md_sha256": file_meta[job["md_name"]]["sha256"],
                "png_sha256": file_meta[f"evidence-snapshots/{job['png_name']}"]["sha256"],
                "path": f"media-archive/{job['media_key']}/EP-anchor-01/",
            }
        )
    index_path = ROOT / "media-archive" / "INDEX.md"
    append_index(index_path, index_rows)
    print("done", len(index_rows))


def append_index(path: Path, rows: list[dict]) -> None:
    if not path.exists():
        path.write_text(
            "# media-archive INDEX\n\n| 日期 | 锚点 | 媒体 | 标题 | MD SHA256 | PNG SHA256 | 路径 |\n"
            "| --- | --- | --- | --- | --- | --- | --- |\n",
            encoding="utf-8",
            newline="\n",
        )
    lines = []
    for r in rows:
        media = "央广网" if r["media_key"] == "cnr" else "新华网"
        lines.append(
            f"| 2026-10-27 | EP-anchor-01 | {media} | {r['title']} | `{r['md_sha256']}` | "
            f"`{r['png_sha256']}` | `{r['path']}` |"
        )
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
