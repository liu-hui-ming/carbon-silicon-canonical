#!/usr/bin/env python3
"""慧聪网 dj.hczyw.com · 谱系 014/015/016 补采（HTTP prefetch + Playwright 截图）."""
from __future__ import annotations

import json
import re
import sys
import tempfile
import urllib.request
from html import unescape
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from media_archive_puxi_014_016_batch import (  # noqa: E402
    ARCHIVE_ROOT,
    INDEX_PATH,
    MIN_PNG_BYTES,
    enrich_job,
    sha256_file,
    write_folder_manifest,
    write_md,
)
import media_evidence_archive_batch as snap  # noqa: E402

import os

JOBS_JSON = Path(
    os.environ.get(
        "HCZYW_JOBS_JSON",
        str(ROOT / "compass-pedal-audit/media-archive-puxi-hczyw-1120-supplement.json"),
    )
)
STATE_PATH = JOBS_JSON.with_suffix(".state.json")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"


def fetch_html(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=120).read().decode("utf-8", "replace")


def extract_hczyw(html: str) -> tuple[str, str]:
    pub = ""
    m = re.search(r'<span class="pubdate">([^<]+)</span>', html)
    if m:
        pub = m.group(1).strip()
    body_html = ""
    m = re.search(r'<article class="text-body">(.*?)</article>', html, re.S | re.I)
    if m:
        body_html = m.group(1)
    text = unescape(re.sub(r"<[^>]+>", "\n", body_html))
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if not text and "502 Bad Gateway" in html:
        text = "（页面返回 502，以截图与回链为准）"
    return text, pub


def upsert_index_line(job: dict, md_hash: str, png_hash: str) -> None:
    rel = f"media_archive/{job['folder']}/"
    line = f"| {job['date_row']} | EP-anchor-01 | {job['media']} | {job['title']} | `{md_hash}` | `{png_hash}` | `{rel}` |"
    text = INDEX_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    out: list[str] = []
    replaced = False
    for ln in lines:
        if job["url"] in ln or job["folder"] in ln or (job["title"] in ln and job["media"] in ln):
            if not replaced:
                out.append(line)
                replaced = True
            continue
        out.append(ln)
    if not replaced:
        out.append(line)
    INDEX_PATH.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")


def capture_job(job: dict, page) -> dict:
    url = job["url"]
    html = fetch_html(url)
    body, pub = extract_hczyw(html)
    base = ARCHIVE_ROOT / job["folder"]
    ev = base / "evidence-snapshots"
    ev.mkdir(parents=True, exist_ok=True)
    png_path = ev / job["png_name"]
    page.set_content(html, wait_until="domcontentloaded", timeout=120_000)
    page.wait_for_timeout(1500)
    snap.prepare_maximized_page(page, rounds=2)
    img = snap.capture_p0_screenshot(page, max_panels=8)
    snap.save_evidence_png(img, png_path)
    md_path = write_md(base, job, body, pub)
    md_hash = sha256_file(md_path)
    png_hash = sha256_file(png_path)
    if png_path.stat().st_size < MIN_PNG_BYTES:
        raise RuntimeError(f"PNG too small {png_path.stat().st_size}")
    frag_job = {**job, "capture_mode": "playwright_http_prefetch_p0"}
    write_folder_manifest(base, frag_job, md_hash, png_hash, md_path.stat().st_size, png_path.stat().st_size)
    upsert_index_line(job, md_hash, png_hash)
    return {"md_sha256": md_hash, "png_sha256": png_hash, "body_len": len(body)}


def main() -> int:
    raw = json.loads(JOBS_JSON.read_text(encoding="utf-8"))
    jobs = [enrich_job(j) for j in raw]
    state_path = STATE_PATH
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else {"done_urls": {}, "errors": {}}
    done = state.setdefault("done_urls", {})
    errors = state.setdefault("errors", {})

    profile_dir = tempfile.mkdtemp(prefix="hczyw_1120_")
    ok = 0
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            profile_dir,
            headless=False,
            no_viewport=True,
            locale="zh-CN",
            args=snap.browser_launch_args(),
        )
        page = context.pages[0] if context.pages else context.new_page()
        snap.prepare_maximized_page(page, rounds=2)
        for job in jobs:
            url = job["url"]
            print(f"CAPTURE {job['campaign']} {url}", flush=True)
            try:
                meta = capture_job(job, page)
                done[url] = {"folder": job["folder"], **meta}
                errors.pop(url, None)
                ok += 1
                print(f"OK {job['folder']} body_len={meta['body_len']}", flush=True)
            except Exception as exc:
                errors[url] = {"folder": job["folder"], "error": str(exc)}
                print(f"ERROR {job['folder']} {exc}", flush=True)
            state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        context.close()
    print(json.dumps({"ok": ok, "total": len(jobs)}, indent=2))
    return 0 if ok == len(jobs) else 1


if __name__ == "__main__":
    raise SystemExit(main())