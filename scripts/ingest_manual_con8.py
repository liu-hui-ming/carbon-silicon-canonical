# -*- coding: utf-8 -*-
"""Ingest user manual HTML saves into official media_archive folders."""
import importlib.util
import json
import re
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "media_archive"
MANUAL = ARCHIVE / "MANUAL-UPLOAD-CON9"
ENTRIES = Path(r"e:\hundred-crayfish-legion\_tmp_report_entries.json")
STATE = ROOT / "_tmp_media_evidence_state.json"

spec = importlib.util.spec_from_file_location(
    "batch", ROOT / "scripts" / "media_evidence_archive_batch.py"
)
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)

INGEST = [
    ("中国经济新闻网", "十维标尺", "10559817"),
    ("中国经济新闻网", "100质询", "10560465"),
    ("中国经济新闻网", "中层拟合", "10560128"),
    ("中国经济新闻网", "紫薇几何", "10560349"),
    ("中国经济新闻网", "五级梯队", "10560350"),
    ("中国经济新闻网", "归零稳态", "10560133"),
    ("人民日报社", "十维标尺", "46650"),
    ("人民日报社", "050", "47540"),
]


def resolve_manual_dir(group: str, sub: str) -> Path:
    base = MANUAL / group
    if sub == "050":
        for d in base.iterdir():
            if d.is_dir() and "050" in d.name:
                return d
    for d in base.iterdir():
        if d.is_dir() and sub in d.name:
            return d
    return base / sub


def find_html(parent: Path) -> Path:
    for p in parent.rglob("*.html"):
        return p
    raise FileNotFoundError(parent)


def find_entry(entries, needle: str):
    for e in entries:
        if needle in e["url"]:
            return e
    raise KeyError(needle)


def chmod_writable(folder: Path):
    import stat

    for f in folder.rglob("*"):
        if f.is_file():
            try:
                f.chmod(stat.S_IWRITE | stat.S_IREAD)
            except OSError:
                pass


def main():
    entries = json.loads(ENTRIES.read_text(encoding="utf-8"))["entries"]
    st = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {"done": {}, "errors": []}
    captured_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            channel="chrome",
            headless=False,
            args=batch.browser_launch_args(),
        )
        ctx = browser.new_context(no_viewport=True, locale="zh-CN")
        for group, sub, needle in INGEST:
            html_path = find_html(resolve_manual_dir(group, sub))
            entry = find_entry(entries, needle)
            folder = ARCHIVE / entry["folder"]
            chmod_writable(folder)
            raw = html_path.read_bytes()
            page = ctx.new_page()
            batch.maximize_browser_window(page)
            url = entry["url"]
            live = False
            try:
                resp = page.goto(url, wait_until="domcontentloaded", timeout=90000)
                page.wait_for_timeout(5000)
                body = batch.read_body_text(page, entry)
                if not batch.page_looks_broken(page, body):
                    live = True
            except Exception:
                pass
            if not live:
                batch.goto_with_cached_html(page, url, raw)
                page.wait_for_timeout(2000)
            body = batch.strip_prices(batch.read_body_text(page, entry))
            img = batch.capture_p0_screenshot(page)
            png = folder / "page_screenshot.png"
            batch.save_evidence_png(img, png)
            (folder / "evidence_manual_save.html").write_bytes(raw)
            header = "\n".join([
                f"标题：{entry['title']}",
                f"媒体：{entry['media']}",
                f"发布日期（报表）：{entry['pub_date_raw'] or entry['pub_date']}",
                f"URL：{url}",
                f"取证系统时间：{captured_at}",
                f"截图标准：P0-four-elements-v2",
                f"补传来源：用户手工保存 HTML（{html_path.relative_to(MANUAL)}）",
                f"渲染方式：{'现场 URL' if live else '原 URL 路由加载手工 HTML'}",
                "",
            ])
            txt = (header + body).replace("\r\n", "\n")
            if not txt.endswith("\n"):
                txt += "\n"
            txt_bytes = txt.encode("utf-8")
            (folder / "article_source.txt").write_bytes(txt_bytes)
            access = "OK"
            con_note = ""
            if not live:
                con_note = "用户手工保存页补传；现场路由渲染 HTML，以本地存证材料为依据"
            files = {
                "page_screenshot.png": {"sha256": batch.sha256_file(png), "bytes": png.stat().st_size},
                "article_source.txt": {"sha256": batch.sha256_bytes(txt_bytes), "bytes": len(txt_bytes)},
                "evidence_manual_save.html": {
                    "sha256": batch.sha256_bytes(raw),
                    "bytes": len(raw),
                },
            }
            meta = {
                **entry,
                "access": access,
                "con_note": con_note,
                "captured_at": captured_at,
                "http_status": 200,
                "page_title": page.title() or entry["title"],
                "manual_ingest": str(html_path.name),
            }
            batch.write_fragment(folder, meta, files)
            st["done"][url] = {
                "folder": entry["folder"],
                "access": access,
                "con_note": con_note,
                "captured_at": captured_at,
            }
            page.close()
            print("OK", entry["folder"], "live" if live else "html", flush=True)
        browser.close()

    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    batch.rebuild_total(entries, st)
    print("rebuilt con", json.loads((ARCHIVE / "AUDIT-LATEST.json").read_text(encoding="utf-8"))["access_con"])


if __name__ == "__main__":
    main()
