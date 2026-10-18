# -*- coding: utf-8 -*-
"""4 Toutiao: each URL — launch Chrome, goto article only, screenshot, quit."""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import media_evidence_archive_batch as batch  # noqa: E402
from recapture_toutiao4_fast import (  # noqa: E402
    CATALOG,
    ENTRIES,
    STATE,
    capture_toutiao_fast,
    safe_focus,
)


def main():
    batch.focus_browser = safe_focus
    batch.STATE = STATE
    entries = batch.load_entries(ENTRIES)
    st = batch.load_state() if STATE.exists() else {"done": {}, "errors": []}
    catalog_entries = batch.load_entries(CATALOG)

    for i, entry in enumerate(entries, 1):
        print(f"{i}/4 直接打开文章（加载完再截，勿关浏览器）…", flush=True)
        folder = batch.ARCHIVE / entry["folder"]
        folder.mkdir(parents=True, exist_ok=True)
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    channel="chrome",
                    headless=False,
                    args=batch.browser_launch_args(),
                )
                context = browser.new_context(no_viewport=True, locale="zh-CN")
                context.set_default_timeout(120000)
                page = context.new_page()
                batch.maximize_browser_window(page)
                meta = capture_toutiao_fast(page, entry, folder)
                context.close()
                browser.close()
        except Exception as exc:
            print(f"  FAIL {exc}", flush=True)
            st.setdefault("errors", []).append({"url": entry["url"], "error": str(exc)})
            batch.save_state(st)
            continue
        st["done"][entry["url"]] = {
            "folder": entry["folder"],
            "access": meta["access"],
            "con_note": meta.get("con_note", ""),
            "captured_at": meta["captured_at"],
        }
        batch.save_state(st)
        print(f"  -> {meta['access']}", flush=True)

    batch.rebuild_total(catalog_entries, st)
    print("4 条结束", flush=True)


if __name__ == "__main__":
    main()
