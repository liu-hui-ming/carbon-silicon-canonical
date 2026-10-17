# -*- coding: utf-8 -*-
"""Batch media first-publication evidence capture. No price fields."""
import hashlib
import json
import re
import sys
import time
import urllib.request
from datetime import datetime
from html import escape, unescape
from pathlib import Path

from PIL import Image, ImageGrab
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "media_archive"
STATE = ROOT / "_tmp_media_evidence_state.json"
SOURCE_WORKBOOK = "碳硅道统-发布报表.xlsx"
REBUILD_EVERY = 25
NAV_TIMEOUT_MS = 90000
CAPTURE_MAX_WALL_SEC = 180
PRICE_LINE = re.compile(
    r"(^|\n)\s*(价格|单价|费用|报价|稿酬|金额)\s*[:：].*$",
    re.M,
)
PRICE_YEN = re.compile(r"¥\s*[\d,.]+|[\d,.]+\s*元\s*(?:/篇|每篇)?")
ERROR_HINTS = re.compile(
    r"无法访问此网站|ERR_|404|Not Found|页面不存在|访问被拒绝|"
    r"资源不存在|您访问的资源不存在|抱歉",
    re.I,
)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(p: Path) -> str:
    return sha256_bytes(p.read_bytes())


def strip_prices(text: str) -> str:
    text = PRICE_LINE.sub("", text)
    lines = []
    for line in text.splitlines():
        if PRICE_YEN.search(line) and len(line) < 80:
            continue
        lines.append(line)
    return "\n".join(lines).strip() + "\n"


def screen_size():
    import ctypes

    user32 = ctypes.windll.user32
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)


def _chrome_hwnds():
    import ctypes
    from ctypes import wintypes

    user32 = ctypes.windll.user32
    found = []

    def callback(hwnd, _):
        buf = ctypes.create_unicode_buffer(512)
        user32.GetWindowTextW(hwnd, buf, 512)
        title = buf.value
        if "Chrome" in title or "Google Chrome" in title:
            found.append(hwnd)
        return True

    WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows(WNDENUMPROC(callback), 0)
    return found, user32


def maximize_browser_window(page):
    """Maximize Chrome so address bar + page + taskbar fit P0 framing."""
    try:
        page.bring_to_front()
        found, user32 = _chrome_hwnds()
        SW_MAXIMIZE = 3
        for hwnd in found:
            user32.ShowWindow(hwnd, SW_MAXIMIZE)
            user32.SetForegroundWindow(hwnd)
            break
    except Exception:
        pass
    time.sleep(0.5)


def focus_browser(page):
    try:
        page.bring_to_front()
        found, user32 = _chrome_hwnds()
        if found:
            user32.SetForegroundWindow(found[0])
    except Exception:
        page.bring_to_front()
    time.sleep(0.35)


def page_is_alive(page) -> bool:
    try:
        page.evaluate("1")
        return True
    except Exception:
        return False


def grab_full_screen():
    sw, sh = screen_size()
    return ImageGrab.grab(bbox=(0, 0, sw, sh))


def stitch_vertical(images):
    if not images:
        raise ValueError("no images")
    if len(images) == 1:
        return images[0]
    w = max(im.width for im in images)
    h = sum(im.height for im in images)
    canvas = Image.new("RGB", (w, h), (255, 255, 255))
    y = 0
    for im in images:
        canvas.paste(im, (0, y))
        y += im.height
    return canvas


def capture_p0_screenshot(page, max_panels: int = 35, deadline: float | None = None):
    """Full-screen panels (URL bar + taskbar clock) while scrolling for full body."""
    if not page_is_alive(page):
        raise RuntimeError("browser_page_closed")
    maximize_browser_window(page)
    sw, sh = screen_size()
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(600)
    focus_browser(page)
    scroll_height = page.evaluate(
        "() => Math.max("
        "document.body.scrollHeight || 0,"
        "document.documentElement.scrollHeight || 0)"
    )
    viewport_h = page.evaluate("window.innerHeight") or 720
    step = max(int(viewport_h * 0.82), 400)
    panels = []
    y = 0
    for _ in range(max_panels):
        if deadline and time.monotonic() > deadline:
            break
        page.evaluate(f"window.scrollTo(0, {y})")
        page.wait_for_timeout(450)
        focus_browser(page)
        panels.append(grab_full_screen())
        if y + viewport_h >= scroll_height - 30:
            break
        y += step
    return stitch_vertical(panels)


def load_entries(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    return data["entries"]


def load_prior_done() -> dict:
    """Keep P0-176 (or prior manifest) in global index while batching DT5322."""
    man = ARCHIVE / "manifest_total.json"
    if not man.exists():
        return {}
    try:
        total = json.loads(man.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    out = {}
    for item in total.get("items") or []:
        url = item.get("url")
        if url:
            out[url] = {
                "folder": item.get("folder", ""),
                "access": item.get("access", "OK"),
                "con_note": item.get("con_note", ""),
                "captured_at": item.get("captured_at", ""),
            }
    return out


def merged_done(st: dict) -> dict:
    prior = load_prior_done()
    merged = dict(prior)
    merged.update(st.get("done") or {})
    return merged


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"done": {}, "errors": []}


def save_state(st):
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_fragment(folder: Path, meta: dict, files: dict):
    frag = {
        "folder": folder.name,
        "url": meta["url"],
        "title": meta["title"],
        "media": meta["media"],
        "pub_date": meta["pub_date"],
        "access": meta["access"],
        "captured_at": meta["captured_at"],
        "capture_standard": "P0-four-elements-v2",
        "files": files,
    }
    raw = (json.dumps(frag, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    (folder / "manifest.fragment.json").write_bytes(raw)
    files["manifest.fragment.json"] = {
        "sha256": sha256_bytes(raw),
        "bytes": len(raw),
    }


def entry_by_url(entries):
    return {e["url"]: e for e in entries}


def rebuild_total(catalog_entries, st):
    done = merged_done(st)
    catalog = entry_by_url(catalog_entries)
    rows = []
    con = []
    ok = 0
    for key, rec in sorted(done.items()):
        folder = ARCHIVE / rec["folder"]
        frag_path = folder / "manifest.fragment.json"
        if not frag_path.exists():
            continue
        frag = json.loads(frag_path.read_text(encoding="utf-8"))
        meta = catalog.get(key, {})
        if rec["access"] == "CON":
            con.append({
                "url": key,
                "title": meta.get("title", frag.get("title", "")),
                "media": meta.get("media", frag.get("media", "")),
                "folder": rec["folder"],
                "note": rec.get("con_note", ""),
            })
        else:
            ok += 1
        for name, info in frag["files"].items():
            rows.append(f"{info['sha256']}  {rec['folder']}/{name}")
    rows.sort()
    body = ("\n".join(rows) + "\n").encode("utf-8") if rows else b""
    total = {
        "canonical": "MEDIA-EVIDENCE-ARCHIVE",
        "generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "source_workbook": SOURCE_WORKBOOK,
        "entry_total": len(catalog_entries),
        "archived_count": len(done),
        "access_ok": ok,
        "access_con": len(con),
        "volume_sha256": sha256_bytes(body) if body else None,
        "volume_basis": "sorted sha256  path lines UTF-8 LF",
        "capture_standard": "P0-four-elements-v2",
        "con_entries": con,
        "items": [
            {
                "url": u,
                **done[u],
            }
            for u in sorted(done.keys())
        ],
    }
    man = (json.dumps(total, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    (ARCHIVE / "manifest_total.json").write_bytes(man)
    audit = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "entry_total": len(catalog_entries),
        "success_archived": len(done),
        "access_ok": ok,
        "access_con": len(con),
        "pending": len(catalog_entries) - len([e for e in catalog_entries if e["url"] in done]),
        "capture_standard": "P0-four-elements-v2",
        "con_list": con,
        "manifest_total_sha256": sha256_bytes(man),
    }
    (ARCHIVE / "AUDIT-LATEST.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    con_ledger = {
        "note": "源链接已失效或取证异常时，仍以本地截图与 article_source.txt 为据",
        "entries": con,
    }
    (ARCHIVE / "CON_LEDGER.json").write_text(
        json.dumps(con_ledger, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if body:
        (ARCHIVE / "SHA256SUMS.txt").write_bytes(body)


def _http_fetch_body(url: str):
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        },
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        status = resp.status
        raw = resp.read().decode("utf-8", errors="replace")
    text = unescape(re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.I | re.S))
    text = re.sub(r"<[^>]+>", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return status, text.strip(), raw


def navigate_with_retry(page, url: str):
    last_exc = None
    for attempt in range(4):
        try:
            resp = page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=120000 if attempt < 2 else 180000,
            )
            page.wait_for_timeout(2500 + attempt * 500)
            return resp
        except Exception as exc:
            last_exc = exc
            time.sleep(2 + attempt)
    raise last_exc


def goto_with_cached_html(page, url: str, raw_html: bytes):
    def handler(route):
        route.fulfill(
            status=200,
            body=raw_html,
            headers={"Content-Type": "text/html; charset=utf-8"},
        )

    page.route(url, handler)
    try:
        return page.goto(url, wait_until="domcontentloaded", timeout=120000)
    finally:
        page.unroute(url, handler)


def write_mirror_html(folder: Path, entry, body_html: str, captured_at: str) -> Path:
    pub = entry["pub_date_raw"] or entry["pub_date"]
    banner = (
        f"<p><strong>原始链接：</strong>{escape(entry['url'])}</p>"
        f"<p><strong>报表发布日期：</strong>{escape(str(pub))}</p>"
        f"<p><strong>取证系统时间：</strong>{escape(captured_at)}</p>"
        f"<p><strong>标题：</strong>{escape(entry['title'])}</p>"
        f"<p><strong>媒体：</strong>{escape(entry['media'])}</p>"
        "<hr/>"
    )
    html = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<title>{escape(entry['title'])}</title>"
        "<style>body{font-family:system-ui,sans-serif;max-width:920px;margin:24px auto;"
        "line-height:1.65;font-size:16px;padding:0 16px 48px;}"
        ".evidence-banner{background:#fff8e1;border:1px solid #e0c060;padding:12px 16px;"
        "margin-bottom:20px;font-size:14px;}</style></head><body>"
        f"<div class='evidence-banner'>{banner}</div>"
        f"{body_html}</body></html>"
    )
    path = folder / "evidence_mirror.html"
    path.write_text(html, encoding="utf-8")
    return path


def page_looks_broken(page, body_text: str) -> bool:
    title = page.title() or ""
    if ERROR_HINTS.search(f"{title}\n{body_text[:1200]}"):
        return True
    if len(body_text.strip()) < 120:
        return True
    if ERROR_HINTS.search(title) and len(body_text.strip()) < 400:
        return True
    if ERROR_HINTS.search(body_text[:800]) and len(body_text.strip()) < 400:
        return True
    return False


def is_dead_link(status: int, body_text: str, page_title: str) -> bool:
    if status in (404, 410):
        return True
    return bool(ERROR_HINTS.search(f"{page_title}\n{body_text[:1500]}"))


def read_body_text(page, entry) -> str:
    host = entry["url"]
    if "huanqiu.com" in host or "kjrb.com.cn" in host:
        page.wait_for_timeout(8000)
    try:
        text = page.inner_text("body")
    except Exception:
        text = ""
    if len(text.strip()) < 120:
        try:
            text = page.evaluate(
                "() => document.body ? document.body.innerText || document.body.textContent || '' : ''"
            )
        except Exception:
            pass
    return text or ""


def classify_access(entry, status: int, body_text: str, page, served_from_cache: bool):
    title_key = entry["title"][:8]
    page_title = page.title() or ""
    substantive = (
        len(body_text.strip()) >= 200
        or title_key in body_text
        or title_key in page_title
    )
    if served_from_cache:
        return "CON", "源链接现场超时/不可达，已用同 URL 路由缓存渲染正文；以本地存证材料为依据"
    if substantive and not page_looks_broken(page, body_text):
        if status in (0, 403) or (200 <= status < 400):
            return "OK", ""
    if status >= 400 or status == 0:
        return "CON", f"HTTP {status}"
    if page_looks_broken(page, body_text):
        return "CON", "正文过短或不可读"
    return "OK", ""


def save_evidence_png(img: Image.Image, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        try:
            import stat

            path.chmod(stat.S_IWRITE | stat.S_IREAD)
        except OSError:
            pass
    img.save(path, format="PNG", optimize=True)


def capture_one(page, entry, folder: Path):
    url = entry["url"]
    captured_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    status = 0
    page_title = ""
    body_text = ""
    served_from_cache = False
    display_title = entry["title"]

    try:
        resp = navigate_with_retry(page, url)
        status = resp.status if resp else 0
        page_title = page.title()
        if page_title and len(page_title.strip()) > 4:
            display_title = page_title.strip()
        body_text = read_body_text(page, entry)
    except Exception:
        body_text = ""
        status = 0

    dead_link = is_dead_link(status, body_text, page_title)

    if not dead_link and page_looks_broken(page, body_text):
        try:
            fetch_status, fetched, raw_html = _http_fetch_body(url)
            if fetch_status and not status:
                status = fetch_status
            if len(fetched) > len(body_text):
                body_text = fetched
            if raw_html.strip():
                write_mirror_html(folder, entry, raw_html, captured_at)
                goto_with_cached_html(page, url, raw_html.encode("utf-8", errors="replace"))
                page.wait_for_timeout(1200)
                page_title = page.title() or entry["title"]
                body_text = read_body_text(page, entry) or body_text
                served_from_cache = True
        except Exception:
            pass
        dead_link = is_dead_link(status, body_text, page_title)

    body_text = strip_prices(body_text)
    header = "\n".join([
        f"标题：{display_title}",
        f"媒体：{entry['media']}",
        f"发布日期（报表）：{entry['pub_date_raw'] or entry['pub_date']}",
        f"URL：{url}",
        f"取证系统时间：{captured_at}",
        f"HTTP：{status}",
        f"页面标题：{page_title}",
        f"截图标准：P0-four-elements-v2（全屏含任务栏时间+滚动拼接正文）",
        f"路由缓存渲染：{'是' if served_from_cache else '否'}",
        f"链接失效：{'是' if dead_link else '否'}",
        "",
    ])
    txt = (header + body_text).replace("\r\n", "\n").replace("\r", "\n")
    if not txt.endswith("\n"):
        txt += "\n"
    txt_bytes = txt.encode("utf-8")

    maximize_browser_window(page)
    focus_browser(page)
    if dead_link:
        img = grab_full_screen()
    else:
        deadline = time.monotonic() + CAPTURE_MAX_WALL_SEC
        img = capture_p0_screenshot(page, deadline=deadline)
    png_path = folder / "page_screenshot.png"
    save_evidence_png(img, png_path)
    txt_path = folder / "article_source.txt"
    txt_path.write_bytes(txt_bytes)

    access, con_note = classify_access(entry, status, body_text, page, served_from_cache)
    if dead_link:
        access = "CON"
        con_note = "源链接已失效（404/资源不存在），以归档本地存证材料为依据"

    files = {
        "page_screenshot.png": {"sha256": sha256_file(png_path), "bytes": png_path.stat().st_size},
        "article_source.txt": {"sha256": sha256_bytes(txt_bytes), "bytes": len(txt_bytes)},
    }
    meta = {
        **entry,
        "title": display_title,
        "access": access,
        "con_note": con_note,
        "captured_at": captured_at,
        "http_status": status,
        "page_title": page_title,
    }
    write_fragment(folder, meta, files)
    return meta


def capture_fallback(page, entry, folder: Path, exc: Exception):
    url = entry["url"]
    status = 0
    page_title = ""
    body_text = ""
    display_title = entry["title"]
    captured_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    raw_html = ""
    for _ in range(2):
        try:
            resp = page.goto(url, wait_until="commit", timeout=180000)
            page.wait_for_timeout(4000)
            status = resp.status if resp else 0
            page_title = page.title()
            if page_title and len(page_title.strip()) > 4:
                display_title = page_title.strip()
            body_text = page.inner_text("body")
            if body_text.strip():
                break
        except Exception:
            time.sleep(2)
    served_from_cache = False
    raw_html = ""
    if len(body_text.strip()) < 80:
        try:
            status, fetched, raw_html = _http_fetch_body(url)
            body_text = fetched if len(fetched) > len(body_text) else body_text
        except Exception as fe:
            body_text = body_text + f"\n[fetch_error] {fe}\n[capture_error] {exc}\n"
    if raw_html.strip():
        try:
            write_mirror_html(folder, entry, raw_html, captured_at)
            goto_with_cached_html(page, url, raw_html.encode("utf-8", errors="replace"))
            page.wait_for_timeout(1200)
            served_from_cache = True
            page_title = page.title() or entry["title"]
            if page_title and len(str(page_title).strip()) > 4:
                display_title = str(page_title).strip()
            body_text = page.inner_text("body") or body_text
        except Exception:
            pass

    body_text = strip_prices(body_text)
    header = "\n".join([
        f"标题：{display_title}",
        f"媒体：{entry['media']}",
        f"发布日期（报表）：{entry['pub_date_raw'] or entry['pub_date']}",
        f"URL：{url}",
        f"取证系统时间：{captured_at}",
        f"HTTP：{status}",
        f"页面标题：{page_title}",
        "备注：源链接已失效或取证异常，以归档本地存证材料为依据",
        "",
    ])
    txt = (header + body_text).replace("\r\n", "\n").replace("\r", "\n")
    if not txt.endswith("\n"):
        txt += "\n"
    txt_bytes = txt.encode("utf-8")
    img = capture_p0_screenshot(page)
    png_path = folder / "page_screenshot.png"
    save_evidence_png(img, png_path)
    txt_path = folder / "article_source.txt"
    txt_path.write_bytes(txt_bytes)
    access = "CON"
    con_note = "源链接已失效，以归档本地存证材料为依据"
    if served_from_cache:
        con_note = "源链接现场不可达，已用同 URL 路由缓存渲染；以本地存证材料为依据"
    elif status >= 400 or status == 0:
        con_note = f"{con_note}；HTTP {status}"
    elif len(body_text.strip()) < 80:
        con_note = f"{con_note}；正文过短或不可读"
    else:
        con_note = f"{con_note}；capture_error: {exc}"[:400]
    files = {
        "page_screenshot.png": {"sha256": sha256_file(png_path), "bytes": png_path.stat().st_size},
        "article_source.txt": {"sha256": sha256_bytes(txt_bytes), "bytes": len(txt_bytes)},
    }
    meta = {
        **entry,
        "title": display_title,
        "access": access,
        "con_note": con_note,
        "captured_at": captured_at,
        "http_status": status,
        "page_title": page_title,
    }
    write_fragment(folder, meta, files)
    return meta


def load_skip_urls(path: Path | None) -> set:
    if not path or not path.exists():
        return set()
    return {
        line.strip().split("#", 1)[0].strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }


def capture_skip_stub(entry, folder: Path, reason: str):
    url = entry["url"]
    captured_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    header = "\n".join([
        f"标题：{entry['title']}",
        f"媒体：{entry['media']}",
        f"发布日期（报表）：{entry['pub_date_raw'] or entry['pub_date']}",
        f"URL：{url}",
        f"取证系统时间：{captured_at}",
        "备注：跳过已知卡顿链接，待人工补截或换链",
        f"跳过原因：{reason}",
        "",
        "[正文未抓取：skip-list]\n",
    ])
    txt = header.encode("utf-8")
    img = Image.new("RGB", (8, 8), (240, 240, 240))
    png_path = folder / "page_screenshot.png"
    img.save(png_path, format="PNG")
    (folder / "article_source.txt").write_bytes(txt)
    meta = {
        **entry,
        "access": "CON",
        "con_note": f"skip-list：{reason}",
        "captured_at": captured_at,
        "http_status": 0,
        "page_title": "",
    }
    files = {
        "page_screenshot.png": {"sha256": sha256_file(png_path), "bytes": png_path.stat().st_size},
        "article_source.txt": {"sha256": sha256_bytes(txt), "bytes": len(txt)},
    }
    write_fragment(folder, meta, files)
    return meta


def browser_launch_args():
    return [
        "--start-maximized",
        "--disable-infobars",
    ]


def parse_cli():
    raw = sys.argv[1:]
    force = "--force" in raw
    recapture_list = None
    state_path = STATE
    catalog_path = None
    skip_list = None
    source_wb = SOURCE_WORKBOOK
    i = 0
    positional = []
    while i < len(raw):
        a = raw[i]
        if a == "--force":
            i += 1
            continue
        if a == "--recapture-list" and i + 1 < len(raw):
            recapture_list = Path(raw[i + 1])
            i += 2
            continue
        if a == "--state" and i + 1 < len(raw):
            state_path = Path(raw[i + 1])
            i += 2
            continue
        if a == "--catalog" and i + 1 < len(raw):
            catalog_path = Path(raw[i + 1])
            i += 2
            continue
        if a == "--source-workbook" and i + 1 < len(raw):
            source_wb = raw[i + 1]
            i += 2
            continue
        if a == "--skip-list" and i + 1 < len(raw):
            skip_list = Path(raw[i + 1])
            i += 2
            continue
        positional.append(a)
        i += 1
    return force, recapture_list, state_path, catalog_path, skip_list, source_wb, positional


def main():
    global STATE, SOURCE_WORKBOOK
    default_entries = Path(r"e:\hundred-crayfish-legion\_tmp_dt5322_report_entries.json")
    default_catalog = Path(r"e:\hundred-crayfish-legion\_tmp_media_evidence_catalog.json")
    default_skip = ROOT / "_tmp_media_evidence_skip_urls.txt"
    force, recapture_list, state_path, catalog_path, skip_list, source_wb, argv = parse_cli()
    skip_list = skip_list or (default_skip if default_skip.exists() else None)
    skip_urls = load_skip_urls(skip_list)
    STATE = state_path
    SOURCE_WORKBOOK = source_wb
    entries_path = Path(argv[0]) if argv else default_entries
    limit = int(argv[1]) if len(argv) > 1 else 0
    offset = int(argv[2]) if len(argv) > 2 else 0
    entries = load_entries(entries_path)
    catalog_entries = load_entries(catalog_path or default_catalog if default_catalog.exists() else entries_path)
    st = {"done": {}, "errors": []} if force else load_state()
    if force:
        save_state(st)
    if recapture_list:
        urls = {
            line.strip()
            for line in recapture_list.read_text(encoding="utf-8").splitlines()
            if line.strip()
        }
        for u in urls:
            st["done"].pop(u, None)
        save_state(st)
        todo = [e for e in entries if e["url"] in urls]
    elif force:
        todo = entries
    else:
        todo = [e for e in entries if e["url"] not in st["done"]]
    if offset:
        todo = todo[offset:]
    if limit:
        todo = todo[:limit]
    ARCHIVE.mkdir(parents=True, exist_ok=True)

    def fresh_page(ctx):
        pg = ctx.new_page()
        maximize_browser_window(pg)
        return pg

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",
            headless=False,
            args=browser_launch_args(),
        )
        context = browser.new_context(no_viewport=True, locale="zh-CN")
        context.set_default_timeout(NAV_TIMEOUT_MS)
        page = fresh_page(context)
        for i, entry in enumerate(todo, 1):
            folder = ARCHIVE / entry["folder"]
            folder.mkdir(parents=True, exist_ok=True)
            if entry["url"] in skip_urls:
                meta = capture_skip_stub(entry, folder, "known hang / manual skip list")
                st["done"][entry["url"]] = {
                    "folder": entry["folder"],
                    "access": meta["access"],
                    "con_note": meta.get("con_note", ""),
                    "captured_at": meta["captured_at"],
                }
                save_state(st)
                if i % REBUILD_EVERY == 0 or i == len(todo):
                    rebuild_total(catalog_entries, st)
                print(f"{i}/{len(todo)} SKIP-LIST {entry['url'][:60]}", flush=True)
                continue
            if not page_is_alive(page):
                page = fresh_page(context)
            try:
                meta = capture_one(page, entry, folder)
                st["done"][entry["url"]] = {
                    "folder": entry["folder"],
                    "access": meta["access"],
                    "con_note": meta.get("con_note", ""),
                    "captured_at": meta["captured_at"],
                }
            except Exception as exc:
                page = fresh_page(context)
                try:
                    meta = capture_fallback(page, entry, folder, exc)
                except Exception as exc2:
                    page = fresh_page(context)
                    try:
                        meta = capture_fallback(page, entry, folder, exc2)
                    except Exception as exc3:
                        st["errors"].append({"url": entry["url"], "error": str(exc3)})
                        save_state(st)
                        print(f"{i}/{len(todo)} SKIP {entry['url'][:60]}", flush=True)
                        continue
                st["errors"].append({"url": entry["url"], "error": str(exc)})
                st["done"][entry["url"]] = {
                    "folder": entry["folder"],
                    "access": meta["access"],
                    "con_note": meta.get("con_note", ""),
                    "captured_at": meta["captured_at"],
                }
            save_state(st)
            if i % REBUILD_EVERY == 0 or i == len(todo):
                rebuild_total(catalog_entries, st)
            print(f"{i}/{len(todo)} {entry['url'][:60]}", flush=True)
        browser.close()
    rebuild_total(catalog_entries, st)
    print("done", len(st["done"]), "errors", len(st["errors"]), flush=True)


if __name__ == "__main__":
    main()
