# -*- coding: utf-8 -*-
"""Slow load + one Chrome per URL. Usage: python recapture_slow_one_by_one.py <entries.json> [state.json]"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import media_evidence_archive_batch as batch  # noqa: E402
from recapture_toutiao4_fast import capture_toutiao_fast, safe_focus  # noqa: E402

CATALOG = Path(r"e:\hundred-crayfish-legion\_tmp_media_evidence_catalog.json")
DEFAULT_STATE = ROOT / "_tmp_recapture_queue_state.json"
REBUILD_EVERY = 10


def main():
    entries_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if not entries_path or not entries_path.exists():
        raise SystemExit("用法: python recapture_slow_one_by_one.py <entries.json> [state.json]")
    state_path = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_STATE

    batch.focus_browser = safe_focus
    batch.STATE = state_path
    entries = batch.load_entries(entries_path)
    st = batch.load_state() if state_path.exists() else {"done": {}, "errors": []}
    catalog_entries = batch.load_entries(CATALOG)
    n = len(entries)

    for i, entry in enumerate(entries, 1):
        url = entry["url"]
        prev = st.get("done", {}).get(url)
        if prev and prev.get("access") == "OK":
            print(f"{i}/{n} skip OK", flush=True)
            continue
        if prev:
            print(f"{i}/{n} skip 已采过 ({prev.get('access')})", flush=True)
            continue
        print(f"{i}/{n} {url[:65]}…", flush=True)
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
            st.setdefault("errors", []).append({"url": url, "error": str(exc)})
            batch.save_state(st)
            continue
        st["done"][url] = {
            "folder": entry["folder"],
            "access": meta["access"],
            "con_note": meta.get("con_note", ""),
            "captured_at": meta["captured_at"],
        }
        batch.save_state(st)
        print(f"  -> {meta['access']}", flush=True)
        if i % REBUILD_EVERY == 0 or i == n:
            batch.rebuild_total(catalog_entries, st)

    batch.rebuild_total(catalog_entries, st)
    print(f"队列结束 {entries_path.name} ({n} 条)", flush=True)


if __name__ == "__main__":
    main()
