# -*- coding: utf-8 -*-
"""Re-capture remaining CON ledger entries with alternates + sibling body fallback."""
import importlib.util
import json
import re
from datetime import datetime
from html import escape
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "media_archive"
LEDGER = ARCHIVE / "CON_LEDGER.json"
ENTRIES = Path(r"e:\hundred-crayfish-legion\_tmp_report_entries.json")
STATE = ROOT / "_tmp_media_evidence_state.json"

spec = importlib.util.spec_from_file_location(
    "batch", ROOT / "scripts" / "media_evidence_archive_batch.py"
)
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)

XUEXI_ALT = (
    "https://jinrongfuwu.libaokj.com/qgh5#/financeInfo"
    "?id=86&token=af5d96f2ab6340daadc88343ee739deb&type=0&jumpQg=0"
)


def alternate_urls(url: str):
    alts = []
    if url.startswith("https://"):
        alts.append("http://" + url[len("https://") :])
    if url == "https://jinrongfuwu.libaokj.com/qgh5":
        alts.append(XUEXI_ALT)
    return alts


def extract_body_from_txt(path: Path) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    start = 0
    for i, line in enumerate(lines):
        if line.startswith("截图标准：") or line.startswith("路由缓存渲染："):
            start = i + 1
    while start < len(lines) and not lines[start].strip():
        start += 1
    body = "\n".join(lines[start:]).strip()
    return body


def find_sibling_body(entry, exclude_url: str) -> str:
    title = entry["title"]
    candidates = []
    for frag_path in ARCHIVE.glob("**/manifest.fragment.json"):
        frag = json.loads(frag_path.read_text(encoding="utf-8"))
        if frag.get("url") == exclude_url or frag.get("title") != title:
            continue
        txt_path = frag_path.parent / "article_source.txt"
        if not txt_path.exists():
            continue
        body = extract_body_from_txt(txt_path)
        if len(body) < 200:
            continue
        ok = frag.get("access") == "OK"
        candidates.append((ok, len(body), body))
    if not candidates:
        return ""
    candidates.sort(key=lambda x: (not x[0], -x[1]))
    return candidates[0][2]


def text_to_article_html(body: str) -> str:
    parts = []
    for para in re.split(r"\n\s*\n", body):
        p = para.strip()
        if not p or p in ("南方报业",):
            continue
        if len(p) < 4:
            continue
        parts.append(f"<p>{escape(p)}</p>")
    return "\n".join(parts) if parts else f"<pre>{escape(body[:50000])}</pre>"


def build_cached_html(entry, inner_html: str, captured_at: str) -> str:
    pub = entry["pub_date_raw"] or entry["pub_date"]
    banner = (
        f"<p><strong>原始链接：</strong>{escape(entry['url'])}</p>"
        f"<p><strong>报表发布日期：</strong>{escape(str(pub))}</p>"
        f"<p><strong>取证系统时间：</strong>{escape(captured_at)}</p>"
        f"<p><strong>媒体：</strong>{escape(entry['media'])}</p>"
    )
    return (
        "<!DOCTYPE html><html><head><meta charset='utf-8'>"
        f"<title>{escape(entry['title'])}</title>"
        "<style>body{font-family:'Microsoft YaHei',sans-serif;max-width:920px;"
        "margin:20px auto;line-height:1.75;font-size:17px;padding:0 20px 40px;}"
        "h1{font-size:22px;line-height:1.4;}"
        ".meta{color:#666;font-size:14px;margin:12px 0 24px;}"
        ".evidence-banner{background:#fff8e1;border:1px solid #e0c060;"
        "padding:12px 16px;margin-bottom:20px;font-size:14px;}</style></head><body>"
        f"<div class='evidence-banner'>{banner}</div>"
        f"<h1>{escape(entry['title'])}</h1>"
        f"<div class='meta'>发布日期：{escape(str(pub))}</div>"
        f"<article>{inner_html}</article></body></html>"
    )


def try_live(page, url: str, entry, wait_ms: int = 8000):
    resp = page.goto(url, wait_until="domcontentloaded", timeout=120000)
    page.wait_for_timeout(wait_ms)
    status = resp.status if resp else 0
    body = batch.read_body_text(page, entry)
    return status, body, page.title() or ""


def rescue_one(page, entry, folder: Path):
    primary = entry["url"]
    captured_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    status = 0
    body_text = ""
    page_title = ""
    rescue = "live"
    nav_url = primary

    for url in [primary, *alternate_urls(primary)]:
        try:
            status, body_text, page_title = try_live(page, url, entry, 12000 if "libaokj" in url else 8000)
            nav_url = url
            if not batch.page_looks_broken(page, body_text):
                rescue = "alternate" if url != primary else "live"
                break
        except Exception:
            continue

    if batch.page_looks_broken(page, body_text):
        sibling = find_sibling_body(entry, primary)
        if sibling:
            html = build_cached_html(entry, text_to_article_html(sibling), captured_at)
            batch.goto_with_cached_html(page, primary, html.encode("utf-8"))
            page.wait_for_timeout(1500)
            body_text = batch.read_body_text(page, entry)
            page_title = entry["title"]
            status = 200
            rescue = "sibling_cache"
        else:
            try:
                fetch_status, fetched, raw = batch._http_fetch_body(primary)
                if len(fetched) > len(body_text):
                    html = build_cached_html(
                        entry,
                        text_to_article_html(fetched) if fetched else f"<pre>{escape(raw[:30000])}</pre>",
                        captured_at,
                    )
                    batch.goto_with_cached_html(page, primary, html.encode("utf-8"))
                    page.wait_for_timeout(1500)
                    body_text = batch.read_body_text(page, entry) or fetched
                    page_title = entry["title"]
                    status = fetch_status or status
                    rescue = "fetch_cache"
            except Exception:
                pass

    body_text = batch.strip_prices(body_text)
    served_cache = rescue in ("sibling_cache", "fetch_cache")
    access, con_note = batch.classify_access(entry, status, body_text, page, served_cache)
    if rescue == "sibling_cache":
        access, con_note = (
            "CON",
            "源链接现场不可达，同标题已归档正文路由渲染；以本地存证材料为依据",
        )
        if not batch.page_looks_broken(page, body_text):
            pass
    elif rescue == "fetch_cache" and not batch.page_looks_broken(page, body_text):
        access, con_note = (
            "CON",
            "源链接现场不可达，HTTP抓取正文路由渲染；以本地存证材料为依据",
        )

    header = "\n".join([
        f"标题：{entry['title']}",
        f"媒体：{entry['media']}",
        f"发布日期（报表）：{entry['pub_date_raw'] or entry['pub_date']}",
        f"URL：{primary}",
        f"导航URL：{nav_url}",
        f"取证系统时间：{captured_at}",
        f"HTTP：{status}",
        f"页面标题：{page_title}",
        f"截图标准：P0-four-elements-v2",
        f"救援方式：{rescue}",
        "",
    ])
    txt = (header + body_text).replace("\r\n", "\n")
    if not txt.endswith("\n"):
        txt += "\n"
    txt_bytes = txt.encode("utf-8")

    img = batch.capture_p0_screenshot(page)
    png = folder / "page_screenshot.png"
    batch.save_evidence_png(img, png)
    (folder / "article_source.txt").write_bytes(txt_bytes)

    files = {
        "page_screenshot.png": {"sha256": batch.sha256_file(png), "bytes": png.stat().st_size},
        "article_source.txt": {"sha256": batch.sha256_bytes(txt_bytes), "bytes": len(txt_bytes)},
    }
    meta = {
        **entry,
        "access": access,
        "con_note": con_note,
        "captured_at": captured_at,
        "http_status": status,
        "page_title": page_title,
        "rescue": rescue,
    }
    batch.write_fragment(folder, meta, files)
    return meta


def main():
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))["entries"]
    all_entries = json.loads(ENTRIES.read_text(encoding="utf-8"))["entries"]
    by_url = {e["url"]: e for e in all_entries}
    st = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {"done": {}, "errors": []}

    for f in ARCHIVE.rglob("*"):
        if f.is_file():
            try:
                import stat

                f.chmod(stat.S_IWRITE | stat.S_IREAD)
            except OSError:
                pass

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",
            headless=False,
            args=batch.browser_launch_args(),
        )
        ctx = browser.new_context(
            no_viewport=True,
            locale="zh-CN",
            extra_http_headers={"Referer": "https://www.eastday.com/"},
        )
        for i, rec in enumerate(ledger, 1):
            entry = by_url[rec["url"]]
            folder = ARCHIVE / entry["folder"]
            folder.mkdir(parents=True, exist_ok=True)
            page = ctx.new_page()
            batch.maximize_browser_window(page)
            meta = {"rescue": "error"}
            try:
                meta = rescue_one(page, entry, folder)
                st["done"][entry["url"]] = {
                    "folder": entry["folder"],
                    "access": meta["access"],
                    "con_note": meta.get("con_note", ""),
                    "captured_at": meta["captured_at"],
                }
            except Exception as exc:
                st.setdefault("errors", []).append({"url": entry["url"], "error": str(exc)})
            finally:
                page.close()
            STATE.write_text(json.dumps(st, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            batch.rebuild_total(all_entries, st)
            print(f"{i}/{len(ledger)} {entry['url'][:65]} {meta.get('rescue','err')}", flush=True)
        browser.close()
    batch.rebuild_total(all_entries, st)
    print("done", len(ledger), flush=True)


if __name__ == "__main__":
    main()
