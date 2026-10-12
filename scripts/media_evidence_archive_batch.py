# -*- coding: utf-8 -*-
"""Batch media first-publication evidence capture. No price fields."""
import hashlib
import json
import re
import sys
import time
import urllib.request
from datetime import datetime
from html import unescape
from pathlib import Path

from PIL import ImageGrab
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "media_archive"
STATE = ROOT / "_tmp_media_evidence_state.json"
PRICE_LINE = re.compile(
    r"(^|\n)\s*(价格|单价|费用|报价|稿酬|金额)\s*[:：].*$",
    re.M,
)
PRICE_YEN = re.compile(r"¥\s*[\d,.]+|[\d,.]+\s*元\s*(?:/篇|每篇)?")


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


def load_entries(path: Path):
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["entries"]


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
        "files": files,
    }
    raw = (json.dumps(frag, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    (folder / "manifest.fragment.json").write_bytes(raw)
    files["manifest.fragment.json"] = {
        "sha256": sha256_bytes(raw),
        "bytes": len(raw),
    }


def rebuild_total(entries, st):
    rows = []
    con = []
    ok = 0
    for e in entries:
        key = e["url"]
        rec = st["done"].get(key)
        if not rec:
            continue
        folder = ARCHIVE / rec["folder"]
        frag_path = folder / "manifest.fragment.json"
        if not frag_path.exists():
            continue
        frag = json.loads(frag_path.read_text(encoding="utf-8"))
        if rec["access"] == "CON":
            con.append({
                "url": e["url"],
                "title": e["title"],
                "media": e["media"],
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
        "source_workbook": "碳硅道统-发布报表.xlsx",
        "entry_total": len(entries),
        "archived_count": len(st["done"]),
        "access_ok": ok,
        "access_con": len(con),
        "volume_sha256": sha256_bytes(body) if body else None,
        "volume_basis": "sorted sha256  path lines UTF-8 LF",
        "con_entries": con,
        "items": [
            {
                "url": u,
                **st["done"][u],
            }
            for u in sorted(st["done"].keys())
        ],
    }
    man = (json.dumps(total, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    (ARCHIVE / "manifest_total.json").write_bytes(man)
    audit = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "entry_total": len(entries),
        "success_archived": len(st["done"]),
        "access_ok": ok,
        "access_con": len(con),
        "pending": len(entries) - len(st["done"]),
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


def capture_one(page, entry, folder: Path):
    url = entry["url"]
    resp = page.goto(url, wait_until="domcontentloaded", timeout=120000)
    page.wait_for_timeout(2000)
    status = resp.status if resp else 0
    page_title = page.title()
    try:
        body_text = page.inner_text("body")
    except Exception:
        body_text = ""
    body_text = strip_prices(body_text)
    captured_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    header = "\n".join([
        f"标题：{entry['title']}",
        f"媒体：{entry['media']}",
        f"发布日期（报表）：{entry['pub_date_raw'] or entry['pub_date']}",
        f"URL：{url}",
        f"取证系统时间：{captured_at}",
        f"HTTP：{status}",
        f"页面标题：{page_title}",
        "",
    ])
    txt = (header + body_text).replace("\r\n", "\n").replace("\r", "\n")
    if not txt.endswith("\n"):
        txt += "\n"
    txt_bytes = txt.encode("utf-8")
    time.sleep(0.4)
    img = ImageGrab.grab(all_screens=False)
    png_path = folder / "page_screenshot.png"
    img.save(png_path, format="PNG")
    txt_path = folder / "article_source.txt"
    txt_path.write_bytes(txt_bytes)
    access = "OK"
    con_note = ""
    if status >= 400 or status == 0:
        access = "CON"
        con_note = f"HTTP {status}"
    elif len(body_text.strip()) < 80:
        access = "CON"
        con_note = "正文过短或不可读"
    files = {
        "page_screenshot.png": {"sha256": sha256_file(png_path), "bytes": png_path.stat().st_size},
        "article_source.txt": {"sha256": sha256_bytes(txt_bytes), "bytes": len(txt_bytes)},
    }
    meta = {
        **entry,
        "access": access,
        "con_note": con_note,
        "captured_at": captured_at,
        "http_status": status,
        "page_title": page_title,
    }
    write_fragment(folder, meta, files)
    return meta


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
    return status, text.strip()


def capture_fallback(page, entry, folder: Path, exc: Exception):
    url = entry["url"]
    status = 0
    page_title = ""
    body_text = ""
    for _ in range(2):
        try:
            resp = page.goto(url, wait_until="commit", timeout=180000)
            page.wait_for_timeout(4000)
            status = resp.status if resp else 0
            page_title = page.title()
            try:
                body_text = page.inner_text("body")
            except Exception:
                body_text = ""
            if body_text.strip():
                break
        except Exception:
            time.sleep(2)
    if len(body_text.strip()) < 80:
        try:
            status, fetched = _http_fetch_body(url)
            if len(fetched) > len(body_text):
                body_text = fetched
        except Exception as fe:
            body_text = (
                body_text
                + f"\n[无法拉取正文] fetch_error: {fe}\n[capture_error] {exc}\n"
            )
    body_text = strip_prices(body_text)
    captured_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    header = "\n".join([
        f"标题：{entry['title']}",
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
    time.sleep(0.4)
    img = ImageGrab.grab(all_screens=False)
    png_path = folder / "page_screenshot.png"
    img.save(png_path, format="PNG")
    txt_path = folder / "article_source.txt"
    txt_path.write_bytes(txt_bytes)
    access = "CON"
    con_note = "源链接已失效，以归档本地存证材料为依据"
    if status >= 400 or status == 0:
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
        "access": access,
        "con_note": con_note,
        "captured_at": captured_at,
        "http_status": status,
        "page_title": page_title,
    }
    write_fragment(folder, meta, files)
    return meta


def main():
    default_entries = Path(r"e:\hundred-crayfish-legion\_tmp_report_entries.json")
    entries_path = Path(sys.argv[1]) if len(sys.argv) > 1 else default_entries
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    offset = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    entries = load_entries(entries_path)
    st = load_state()
    todo = [e for e in entries if e["url"] not in st["done"]]
    if offset:
        todo = todo[offset:]
    if limit:
        todo = todo[:limit]
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",
            headless=False,
            args=["--window-position=40,40", "--window-size=1280,760", "--disable-infobars"],
        )
        context = browser.new_context(viewport={"width": 1280, "height": 720}, locale="zh-CN")
        page = context.new_page()
        for i, entry in enumerate(todo, 1):
            folder = ARCHIVE / entry["folder"]
            folder.mkdir(parents=True, exist_ok=True)
            try:
                meta = capture_one(page, entry, folder)
                st["done"][entry["url"]] = {
                    "folder": entry["folder"],
                    "access": meta["access"],
                    "con_note": meta.get("con_note", ""),
                    "captured_at": meta["captured_at"],
                }
            except Exception as exc:
                st["errors"].append({"url": entry["url"], "error": str(exc)})
                meta = capture_fallback(page, entry, folder, exc)
                st["done"][entry["url"]] = {
                    "folder": entry["folder"],
                    "access": meta["access"],
                    "con_note": meta.get("con_note", ""),
                    "captured_at": meta["captured_at"],
                }
            save_state(st)
            rebuild_total(entries, st)
            print(f"{i}/{len(todo)} {entry['url'][:60]}")
        browser.close()
    rebuild_total(entries, st)
    print("done", len(st["done"]), "errors", len(st["errors"]))


if __name__ == "__main__":
    main()
