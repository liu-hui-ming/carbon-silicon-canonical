# -*- coding: utf-8 -*-
"""One Chrome session: all bozhou.cn HTTP0 URLs, ~15s each, full screen only."""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import media_evidence_archive_batch as batch  # noqa: E402
from recapture_toutiao4_fast import capture_bozhou_instant, safe_focus  # noqa: E402

QUEUE = ROOT / "media-evidence-ledger/recapture-queue/02-http0-796.json"
STATE = ROOT / "_tmp_recapture_queue_state.json"
CATALOG = Path(r"e:\hundred-crayfish-legion\_tmp_media_evidence_catalog.json")


def main():
    batch.focus_browser = safe_focus
    batch.STATE = STATE
    entries = [e for e in batch.load_entries(QUEUE) if "bozhou.cn" in e["url"]]
    st = batch.load_state() if STATE.exists() else {"done": {}, "errors": []}
    catalog = batch.load_entries(CATALOG)
    print(f"亳州 {len(entries)} 条，单浏览器快截", flush=True)
    for i, entry in enumerate(entries, 1):
        url = entry["url"]
        print(f"{i}/{len(entries)}", flush=True)
        folder = batch.ARCHIVE / entry["folder"]
        folder.mkdir(parents=True, exist_ok=True)
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    channel="chrome", headless=False, args=batch.browser_launch_args()
                )
                ctx = browser.new_context(no_viewport=True, locale="zh-CN")
                ctx.set_default_timeout(15000)
                page = ctx.new_page()
                batch.maximize_browser_window(page)
                meta = capture_bozhou_instant(page, entry, folder)
                ctx.close()
                browser.close()
        except Exception as exc:
            print(f"  FAIL {exc}", flush=True)
            continue
        st["done"][url] = {
            "folder": entry["folder"],
            "access": meta["access"],
            "con_note": meta.get("con_note", ""),
            "captured_at": meta["captured_at"],
        }
        batch.save_state(st)
    batch.rebuild_total(catalog, st)
    print("亳州批次结束", flush=True)


if __name__ == "__main__":
    main()
