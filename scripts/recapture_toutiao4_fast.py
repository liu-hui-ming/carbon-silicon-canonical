# -*- coding: utf-8 -*-
"""4 Toutiao: your Chrome Default profile, goto + screenshot (no cache re-render, no CDP)."""
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import media_evidence_archive_batch as batch  # noqa: E402

ENTRIES = ROOT / "media-evidence-ledger/recapture-likely_ok-20261018/entries_toutiao4.json"
STATE = ROOT / "_tmp_con_recapture_likely_ok_state.json"
CATALOG = Path(r"e:\hundred-crayfish-legion\_tmp_media_evidence_catalog.json")
USER_DATA = Path(os.environ.get("LOCALAPPDATA", "")) / "Google/Chrome/User Data"
GOTO_TIMEOUT = 45000
LOAD_SETTLE_MS = 3000
NETWORKIDLE_MS = 15000
SHOT_DEADLINE_SEC = 90
MAX_PANELS = 15
FAST_HOSTS = ("bozhou.cn", "hsnewsnet.com", "shangyexinzhi.com")


def safe_focus(page):
    try:
        batch.focus_browser(page)
    except Exception:
        pass


def capture_bozhou_instant(page, entry, folder: Path):
    """亳州站易 ERR_EMPTY_RESPONSE：commit 10s + 全屏，不滚动。"""
    url = entry["url"]
    captured_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    status = 0
    page_title = entry["title"]
    body_text = ""
    print(f"  [亳州快截] {url}", flush=True)
    try:
        resp = page.goto(url, wait_until="commit", timeout=12000)
        status = resp.status if resp else 0
        page.wait_for_timeout(600)
        page_title = page.title() or page_title
        body_text = page.inner_text("body") or ""
    except Exception as exc:
        print(f"  导航: {str(exc)[:80]}", flush=True)
    batch.maximize_browser_window(page)
    safe_focus(page)
    img = batch.grab_full_screen()
    body_text = batch.strip_prices(body_text)
    header = "\n".join([
        f"标题：{page_title}",
        f"媒体：{entry['media']}",
        f"发布日期（报表）：{entry['pub_date_raw'] or entry['pub_date']}",
        f"URL：{url}",
        f"取证系统时间：{captured_at}",
        f"HTTP：{status}",
        f"备注：亳州站快截（站点常空响应，全屏存证）",
        "",
    ]) + body_text
    if not header.endswith("\n"):
        header += "\n"
    txt_bytes = header.encode("utf-8")
    png_path = folder / "page_screenshot.png"
    batch.save_evidence_png(img, png_path)
    (folder / "article_source.txt").write_bytes(txt_bytes)
    access, con_note = "CON", "HTTP 0"
    if status == 200 and len(body_text.strip()) >= 200:
        access, con_note = batch.classify_access(entry, status, body_text, page, False)
    files = {
        "page_screenshot.png": {"sha256": batch.sha256_file(png_path), "bytes": png_path.stat().st_size},
        "article_source.txt": {"sha256": batch.sha256_bytes(txt_bytes), "bytes": len(txt_bytes)},
    }
    meta = {
        **entry,
        "title": page_title,
        "access": access,
        "con_note": con_note if access == "CON" else "",
        "captured_at": captured_at,
        "http_status": status,
        "page_title": page_title,
    }
    batch.write_fragment(folder, meta, files)
    print(f"  -> {access}", flush=True)
    return meta


def capture_toutiao_fast(page, entry, folder: Path):
    url = entry["url"]
    if "bozhou.cn" in url:
        return capture_bozhou_instant(page, entry, folder)
    captured_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    print(f"  打开 {url[:70]}…", flush=True)
    status = 0
    page_title = entry["title"]
    body_text = ""
    nav_ok = False
    wait_until = "domcontentloaded"
    if "toutiao.com" in url:
        wait_until = "load"
    try:
        resp = page.goto(url, wait_until=wait_until, timeout=GOTO_TIMEOUT)
        status = resp.status if resp else 0
        nav_ok = True
        print("  等待页面稳定…", flush=True)
        if "toutiao.com" in url:
            try:
                page.wait_for_load_state("networkidle", timeout=45000)
            except Exception:
                pass
            page.wait_for_timeout(LOAD_SETTLE_MS)
        elif any(h in url for h in FAST_HOSTS):
            page.wait_for_timeout(2000)
        else:
            try:
                page.wait_for_load_state("networkidle", timeout=NETWORKIDLE_MS)
            except Exception:
                pass
            page.wait_for_timeout(LOAD_SETTLE_MS)
        page_title = page.title() or page_title
        try:
            body_text = page.inner_text("body") or ""
        except Exception:
            pass
        print(f"  正文约 {len(body_text.strip())} 字，开始截图", flush=True)
    except Exception as exc:
        print(f"  导航失败（仍全屏存证）: {str(exc)[:120]}", flush=True)
        nav_ok = False
        try:
            page_title = page.title() or page_title
            body_text = page.inner_text("body") or ""
        except Exception:
            pass

    body_text = batch.strip_prices(body_text)
    header = "\n".join([
        f"标题：{page_title}",
        f"媒体：{entry['media']}",
        f"发布日期（报表）：{entry['pub_date_raw'] or entry['pub_date']}",
        f"URL：{url}",
        f"取证系统时间：{captured_at}",
        f"HTTP：{status}",
        f"页面标题：{page_title}",
        f"截图标准：P0-four-elements-v2（头条快速重采）",
        "",
    ])
    txt = (header + body_text).replace("\r\n", "\n").replace("\r", "\n")
    if not txt.endswith("\n"):
        txt += "\n"
    txt_bytes = txt.encode("utf-8")

    print("  截图…", flush=True)
    batch.maximize_browser_window(page)
    safe_focus(page)
    use_scroll = nav_ok and len(body_text.strip()) >= 80 and batch.page_is_alive(page)
    if use_scroll:
        try:
            img = batch.capture_p0_screenshot(
                page, max_panels=MAX_PANELS, deadline=time.monotonic() + SHOT_DEADLINE_SEC
            )
        except Exception as exc:
            print(f"  滚动截图失败，改全屏: {exc}", flush=True)
            img = batch.grab_full_screen()
    else:
        img = batch.grab_full_screen()
    png_path = folder / "page_screenshot.png"
    batch.save_evidence_png(img, png_path)
    (folder / "article_source.txt").write_bytes(txt_bytes)

    access, con_note = batch.classify_access(entry, status, body_text, page, False)
    files = {
        "page_screenshot.png": {"sha256": batch.sha256_file(png_path), "bytes": png_path.stat().st_size},
        "article_source.txt": {"sha256": batch.sha256_bytes(txt_bytes), "bytes": len(txt_bytes)},
    }
    meta = {
        **entry,
        "title": page_title,
        "access": access,
        "con_note": con_note,
        "captured_at": captured_at,
        "http_status": status,
        "page_title": page_title,
    }
    batch.write_fragment(folder, meta, files)
    return meta


def main():
    batch.focus_browser = safe_focus
    batch.STATE = STATE
    entries = batch.load_entries(ENTRIES)
    st = batch.load_state() if STATE.exists() else {"done": {}, "errors": []}
    for e in entries:
        st["done"].pop(e["url"], None)
    batch.save_state(st)
    catalog_entries = batch.load_entries(CATALOG)

    print("关闭旧 Chrome → 用本机 Default 配置启动 → 4 条打开即截", flush=True)
    subprocess.run(["taskkill", "/F", "/T", "/IM", "chrome.exe"], capture_output=True)
    time.sleep(2)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(USER_DATA),
            channel="chrome",
            headless=False,
            no_viewport=True,
            locale="zh-CN",
            args=[
                "--profile-directory=Default",
                "--start-maximized",
                "--disable-infobars",
            ],
        )
        context.set_default_timeout(GOTO_TIMEOUT)
        page = context.new_page()
        batch.maximize_browser_window(page)

        for i, entry in enumerate(entries, 1):
            print(f"{i}/4", flush=True)
            folder = batch.ARCHIVE / entry["folder"]
            folder.mkdir(parents=True, exist_ok=True)
            try:
                meta = capture_toutiao_fast(page, entry, folder)
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

        context.close()

    batch.rebuild_total(catalog_entries, st)
    print("完成", flush=True)


if __name__ == "__main__":
    main()
