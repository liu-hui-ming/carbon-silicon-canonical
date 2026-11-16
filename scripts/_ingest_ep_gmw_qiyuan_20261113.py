#!/usr/bin/env python3
"""EP-anchor-01 · 光明网经济 · 启元机器人个人机器人实现万台下线 · P0 Edge."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import media_evidence_snapshot_helpers as snap  # noqa: E402

ANCHOR = "EP-anchor-01"
DATE_ROW = "2026-11-13"
INDEX_PATH = ROOT / "media-archive/INDEX.md"
AUDIT = ROOT / "compass-pedal-audit/media-archive-20261116-gmw-qiyuan.log"
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


def _acquire_work_page(context):
    for extra in list(context.pages)[1:]:
        try:
            extra.close()
        except Exception:
            pass
    page = context.pages[0] if context.pages else context.new_page()
    try:
        page.bring_to_front()
    except Exception:
        pass
    return page


JOB = {
    "media_key": "gmw",
    "title": "启元机器人个人机器人实现万台下线",
    "media": "光明网",
    "source": "光明网 · 经济频道",
    "url": "https://economy.gmw.cn/2026-11/13/content_39100464.htm",
    "md_suffix": "光明网经济",
}


def extract_body(page) -> tuple[str, str]:
    pub = ""
    for sel in (".time", ".date", "#pubtime", ".article-time", ".source-time", "time[datetime]"):
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
        const article = document.querySelector('.u-article')
          || document.querySelector('article')
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
    if md_path.read_bytes()[:3] == b"\xef\xbb\xbf":
        raise RuntimeError("BOM detected")
    return md_path, md_name, png_name


def merge_manifest(base: Path, job: dict, md_name: str, png_name: str, md_h: str, png_h: str, md_b: int, png_b: int, pub: str) -> None:
    mp = base / "manifest.json"
    data = (
        json.loads(mp.read_text(encoding="utf-8"))
        if mp.is_file()
        else {"anchor": ANCHOR, "capture_standard": "P0-four-elements-v2", "ingests": [], "files": {}}
    )
    if not any(i.get("url") == job["url"] for i in data.get("ingests", [])):
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
    text = INDEX_PATH.read_text(encoding="utf-8") if INDEX_PATH.is_file() else ""
    if md_h not in text:
        INDEX_PATH.write_text(text.rstrip() + "\n" + line + "\n", encoding="utf-8", newline="\n")


def main() -> int:
    job = JOB
    base = ROOT / "media-archive" / job["media_key"] / ANCHOR
    ev = base / "evidence-snapshots"
    ev.mkdir(parents=True, exist_ok=True)
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(TZ_CN).strftime("%Y-%m-%dT%H:%M+08:00")
    AUDIT.write_text(f"{stamp} gmw qiyuan ingest start edge=1\n", encoding="utf-8", newline="\n")
    profile = tempfile.mkdtemp(prefix="ep_gmw_qiyuan_")
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
            page = _acquire_work_page(context)
            snap.prepare_maximized_page(page, rounds=3)
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
                f.write(f"ok md={md_h} png={png_h} png_bytes={png_path.stat().st_size}\n")
            context.close()
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    print(f"md={md_h}")
    print(f"png={png_h}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())