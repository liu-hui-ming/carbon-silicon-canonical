#!/usr/bin/env python3
"""EP-anchor-01 · 光明网经济科技首发 · 储能装机 1.5亿千瓦 · P0 (Edge) → media_archive."""
from __future__ import annotations

import argparse
import hashlib
import shutil
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import media_archive_p0_gate as p0gate  # noqa: E402
import media_evidence_archive_batch as snap  # noqa: E402
from media_archive_1118_settlement_batch import ARCHIVE_ROOT, process_job, safe_name  # noqa: E402

AUDIT = ROOT / "compass-pedal-audit/media-archive-20261118-gmw-storage-15gw.log"
TZ_CN = timezone(timedelta(hours=8))

TITLE = "储能装机迈过1.5亿千瓦之后 产研适配这一环怎么补"
MEDIA = "光明网经济科技首发"
URL = "https://economy.gmw.cn/2026-11/18/content_39108332.htm"
SEQ = 208


def build_job() -> dict:
    url_hash = hashlib.sha256(URL.encode("utf-8")).hexdigest()[:8]
    media_slug = safe_name(MEDIA)[:24]
    folder = f"20261118_{SEQ:04d}_{media_slug}_{url_hash}"
    stem = f"{TITLE}_{MEDIA}"
    return {
        "seq": SEQ,
        "title": TITLE,
        "media": MEDIA,
        "url": URL,
        "submit_batch": None,
        "folder": folder,
        "md_name": safe_name(stem) + ".md",
        "png_name": safe_name(stem) + "_snapshot.png",
    }


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


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundled-chromium", action="store_true", help="use bundled Chromium instead of Edge")
    args = ap.parse_args()
    job = build_job()
    skip, reason = p0gate.should_skip_capture(job["url"], job["folder"], ARCHIVE_ROOT)
    if skip:
        AUDIT.parent.mkdir(parents=True, exist_ok=True)
        with AUDIT.open("a", encoding="utf-8", newline="\n") as f:
            f.write(f"{datetime.now(TZ_CN).isoformat()} skip reason={reason}\n")
        print(f"skip {reason}")
        return 0

    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(TZ_CN).strftime("%Y-%m-%dT%H:%M+08:00")
    with AUDIT.open("a", encoding="utf-8", newline="\n") as f:
        f.write(f"{stamp} start folder={job['folder']} edge={int(not args.bundled_chromium)}\n")

    profile = tempfile.mkdtemp(prefix="ep20261118_gmw_storage_")
    use_chrome = not args.bundled_chromium
    try:
        with sync_playwright() as p:
            launch_kw = dict(
                user_data_dir=profile,
                headless=False,
                no_viewport=True,
                locale="zh-CN",
                args=snap.browser_launch_args(),
            )
            if args.bundled_chromium:
                context = p.chromium.launch_persistent_context(**launch_kw)
            else:
                context = p.chromium.launch_persistent_context(**launch_kw, channel="msedge")
            page = _acquire_work_page(context)
            snap.prepare_maximized_page(page, rounds=3)
            result = process_job(job, page, use_chrome=use_chrome)
            context.close()
        with AUDIT.open("a", encoding="utf-8", newline="\n") as f:
            f.write(
                f"ok md={result['md_sha256']} png={result['png_sha256']} "
                f"path=media_archive/{job['folder']}/\n"
            )
        print("ok", job["folder"], result)
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())