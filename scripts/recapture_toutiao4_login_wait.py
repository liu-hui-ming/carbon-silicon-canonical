# -*- coding: utf-8 -*-
"""
4 Toutiao P0 captures.

Default (--attach): connect to YOUR Chrome (already logged in), no login popups.

1) Quit all Chrome, then start once:
   chrome.exe --remote-debugging-port=9222
2) Log in at https://www.toutiao.com/ in that window (you did this).
3) Run: python recapture_toutiao4_login_wait.py --attach
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import media_evidence_archive_batch as batch  # noqa: E402

ENTRIES = ROOT / "media-evidence-ledger/recapture-likely_ok-20261018/entries_toutiao4.json"
STATE = ROOT / "_tmp_con_recapture_likely_ok_state.json"
CATALOG = Path(r"e:\hundred-crayfish-legion\_tmp_media_evidence_catalog.json")
PROFILE = ROOT / "_tmp_chrome_profile_toutiao"
CDP_URL = "http://127.0.0.1:9222"

argv = sys.argv[1:]
ATTACH = "--attach" in argv or "--logged-in" in argv
USE_PLAYWRIGHT_LOGIN = "--playwright-login" in argv
CDP = CDP_URL
for i, a in enumerate(argv):
    if a == "--cdp" and i + 1 < len(argv):
        CDP = argv[i + 1]


def safe_focus(page):
    try:
        batch.focus_browser(page)
    except Exception:
        pass


def pick_page(context):
    for pg in context.pages:
        if pg.url and "toutiao.com" in pg.url and "closed" not in str(pg.url).lower():
            return pg
    return context.pages[0] if context.pages else context.new_page()


def run_captures(context, entries, st, catalog_entries):
    page = context.new_page()
    batch.maximize_browser_window(page)
    print("新开标签页采集（沿用当前 Chrome 登录态）", flush=True)

    for i, entry in enumerate(entries, 1):
        folder = batch.ARCHIVE / entry["folder"]
        folder.mkdir(parents=True, exist_ok=True)
        if not batch.page_is_alive(page):
            page = context.new_page()
            batch.maximize_browser_window(page)
        try:
            meta = batch.capture_one(page, entry, folder)
        except Exception as exc:
            if not batch.page_is_alive(page):
                raise RuntimeError("Chrome 页面已关闭，请保持浏览器打开后重试。") from exc
            meta = batch.capture_fallback(page, entry, folder, exc)
        st["done"][entry["url"]] = {
            "folder": entry["folder"],
            "access": meta["access"],
            "con_note": meta.get("con_note", ""),
            "captured_at": meta["captured_at"],
        }
        batch.save_state(st)
        print(f"{i}/{len(entries)} {meta['access']} {entry['url']}", flush=True)

    batch.rebuild_total(catalog_entries, st)
    print("toutiao4 complete", flush=True)


def main():
    batch.focus_browser = safe_focus
    batch.STATE = STATE
    entries = batch.load_entries(ENTRIES)
    st = batch.load_state() if STATE.exists() else {"done": {}, "errors": []}
    for e in entries:
        st["done"].pop(e["url"], None)
    batch.save_state(st)
    catalog_entries = batch.load_entries(CATALOG)

    with sync_playwright() as p:
        if ATTACH and not USE_PLAYWRIGHT_LOGIN:
            print(f"附加到已打开的 Chrome（{CDP}），不弹登录窗。", flush=True)
            try:
                browser = p.chromium.connect_over_cdp(CDP)
            except Exception as e:
                print(
                    "无法连接 Chrome。请先关闭全部 Chrome，再用调试端口启动一次：\n"
                    '  chrome.exe --remote-debugging-port=9222\n'
                    "在你自己的窗口登录 https://www.toutiao.com/ 后，再运行本脚本 --attach\n"
                    f"错误: {e}",
                    flush=True,
                )
                sys.exit(1)
            if not browser.contexts:
                print("未找到浏览器上下文。", flush=True)
                sys.exit(1)
            run_captures(browser.contexts[0], entries, st, catalog_entries)
            return

        # Legacy: separate Playwright profile (only if --playwright-login)
        PROFILE.mkdir(parents=True, exist_ok=True)
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE),
            channel="chrome",
            headless=False,
            no_viewport=True,
            locale="zh-CN",
            args=batch.browser_launch_args(),
        )
        context.set_default_timeout(batch.NAV_TIMEOUT_MS)
        page = context.pages[0] if context.pages else context.new_page()
        batch.maximize_browser_window(page)
        run_captures(context, entries, st, catalog_entries)
        context.close()


if __name__ == "__main__":
    main()
