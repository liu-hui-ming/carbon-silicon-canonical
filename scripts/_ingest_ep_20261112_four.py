#!/usr/bin/env python3
"""EP-anchor-01 · 2026-11-12 four articles · P0 desktop capture (Edge)."""
from __future__ import annotations

import hashlib
import json
import re
import sys
import tempfile
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import media_evidence_snapshot_helpers as snap  # noqa: E402

ANCHOR = "EP-anchor-01"
DATE_ROW = "2026-11-12"
INDEX_PATH = ROOT / "media-archive/INDEX.md"
AUDIT = ROOT / "compass-pedal-audit/media-archive-20261112-ep-four.log"
TZ_CN = timezone(timedelta(hours=8))
BAD = re.compile(r'[\\/:*?"<>|]')


def safe(s: str) -> str:
    return BAD.sub("_", s).strip() or "untitled"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


JOBS = [
    {
        "media_key": "gmw",
        "title": "智能硬件“行为风险”进入承保视野 保险定价探索前置到出厂前",
        "media": "光明网公益",
        "source": "光明网公益（转载）",
        "url": "https://gongyi.gmw.cn/2026-11/12/content_39098346.htm",
        "md_suffix": "光明网公益",
    },
    {
        "media_key": "news-cn",
        "title": "2026大湾区科学论坛启幕 发布四十项举措助力湾区科创建设",
        "media": "新华网转发",
        "source": "新华网 · 数字频道（转载）",
        "url": "https://www.news.cn/digital/20261111/d742ff607fc142fc9e860ebef997e47a/c.html",
        "md_suffix": "新华网",
    },
    {
        "media_key": "cctv",
        "title": "适配人口结构新变化 我国前瞻优化教育资源配置",
        "media": "央视网",
        "source": "央视网 · 经济频道（独家首发）",
        "url": "https://jingji.cctv.com/2026/11/12/ARTIyGIDYam9tXQcxF4LzyEY261112.shtml",
        "md_suffix": "央视网",
    },
    {
        "media_key": "gmw",
        "title": "卫星互联网低轨29组升空：太空组网进入批量部署",
        "media": "光明网经济科技首发",
        "source": "光明网 · 经济科技（首发）",
        "url": "https://economy.gmw.cn/2026-11/12/content_39098453.htm",
        "md_suffix": "光明网经济",
    },
]


def extract_body(page) -> tuple[str, str]:
    pub = ""
    for sel in ("time[datetime]", ".time", ".date", "#pubtime", ".article-time", ".source-time"):
        try:
            el = page.query_selector(sel)
            if el:
                pub = (el.get_attribute("datetime") or el.inner_text() or "").strip()[:64]
                if pub:
                    break
        except Exception:
            pass
    text = page.evaluate(
        """() => {
        const article = document.querySelector('article')
          || document.querySelector('.article-content')
          || document.querySelector('.content')
          || document.querySelector('#content')
          || document.querySelector('.TRS_Editor')
          || document.querySelector('main');
        const raw = article ? article.innerText : document.body.innerText;
        return (raw || '').replace(/\\s+/g, ' ').trim();
    }"""
    )
    text = re.sub(r"\n{3,}", "\n\n", text or "")
    if len(text) > 120000:
        text = text[:120000] + "\n\n（正文截断：超长页面）\n"
    return text, pub


def write_md(base: Path, job: dict, body: str, pub: str) -> tuple[Path, str, str]:
    md_name = f"{safe(job['title'])}_{safe(job['md_suffix'])}.md"
    png_name = f"{safe(job['title'])}_{safe(job['md_suffix'])}_snapshot.png"
    lines = [
        f"# {job['title']}",
        "",
        f"- **媒体**：{job['media']}",
        f"- **来源**：{job['source']}",
        f"- **回链**：{job['url']}",
        f"- **页面发布日期**：{pub or '（页内未解析，以截图为准）'}",
        "",
        "---",
        "",
        body.strip() if body.strip() else "（正文自页面抽取为空，以截图与回链为准）",
        "",
    ]
    md_path = base / md_name
    md_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return md_path, md_name, png_name


def merge_manifest(base: Path, job: dict, md_name: str, png_name: str, md_h: str, png_h: str, md_b: int, png_b: int, pub: str) -> None:
    mp = base / "manifest.json"
    data = (
        json.loads(mp.read_text(encoding="utf-8"))
        if mp.is_file()
        else {"anchor": ANCHOR, "capture_standard": "P0-four-elements-v2", "ingests": [], "files": {}}
    )
    data.setdefault("ingests", []).append(
        {
            "date": DATE_ROW,
            "title": job["title"],
            "media": job["media"],
            "source": job["source"],
            "url": job["url"],
            "pub_date_page": pub or DATE_ROW,
        }
    )
    data.setdefault("files", {})[md_name] = {"sha256": md_h, "bytes": md_b}
    data["files"][f"evidence-snapshots/{png_name}"] = {"sha256": png_h, "bytes": png_b}
    mp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def rebuild_sums(base: Path) -> None:
    pairs: list[tuple[str, Path]] = []
    for md in sorted(base.glob("*.md")):
        pairs.append((md.name, md))
    ev = base / "evidence-snapshots"
    if ev.is_dir():
        for png in sorted(ev.glob("*.png")):
            pairs.append((f"evidence-snapshots/{png.name}", png))
    lines = [f"{sha256_file(p)}  {name}" for name, p in pairs]
    (base / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def append_index(job: dict, md_h: str, png_h: str) -> None:
    rel = f"media-archive/{job['media_key']}/{ANCHOR}/"
    line = f"| {DATE_ROW} | {ANCHOR} | {job['media']} | {job['title']} | `{md_h}` | `{png_h}` | `{rel}` |"
    text = INDEX_PATH.read_text(encoding="utf-8") if INDEX_PATH.is_file() else (
        "# media-archive INDEX\n\n| 日期 | 锚点 | 媒体 | 标题 | MD SHA256 | PNG SHA256 | 路径 |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
    )
    if md_h not in text:
        INDEX_PATH.write_text(text.rstrip() + "\n" + line + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(TZ_CN).strftime("%Y-%m-%dT%H:%M+08:00")
    AUDIT.write_text(f"{stamp} EP four ingest start edge=1\n", encoding="utf-8", newline="\n")
    results: list[dict] = []
    profile = tempfile.mkdtemp(prefix="ep20261112_edge_")
    try:
        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                profile,
                channel="msedge",
                headless=False,
                no_viewport=True,
                locale="zh-CN",
                args=snap.browser_launch_args(),
            )
            page = context.new_page()
            page.goto("about:blank")
            snap.prepare_maximized_page(page, rounds=4)
            for job in JOBS:
                base = ROOT / "media-archive" / job["media_key"] / ANCHOR
                ev = base / "evidence-snapshots"
                ev.mkdir(parents=True, exist_ok=True)
                print(f"capture: {job['title'][:48]}…", flush=True)
                page.goto(job["url"], wait_until="domcontentloaded", timeout=180_000)
                page.wait_for_timeout(3000)
                body, pub = extract_body(page)
                snap.prepare_maximized_page(page)
                img = snap.capture_p0_screenshot(page)
                md_path, md_name, png_name = write_md(base, job, body, pub)
                png_path = ev / png_name
                snap.save_evidence_png(img, png_path)
                md_h = sha256_file(md_path)
                png_h = sha256_file(png_path)
                merge_manifest(base, job, md_name, png_name, md_h, png_h, md_path.stat().st_size, png_path.stat().st_size, pub)
                rebuild_sums(base)
                append_index(job, md_h, png_h)
                with AUDIT.open("a", encoding="utf-8", newline="\n") as f:
                    f.write(f"entry title={job['title'][:60]} md={md_h} png={png_h}\n")
                results.append({"title": job["title"], "md": md_h, "png": png_h})
            context.close()
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
