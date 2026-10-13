# -*- coding: utf-8 -*-
"""Copy user manual HTML into archive folders; no browser / no live fetch."""
import hashlib
import importlib.util
import json
import re
from datetime import datetime
from html import unescape
from pathlib import Path

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
    for p in sorted(parent.rglob("*.html")):
        return p
    raise FileNotFoundError(parent)


def html_to_text(raw: str) -> str:
    raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.I | re.S)
    text = unescape(re.sub(r"<[^>]+>", "\n", raw))
    text = re.sub(r"\n{3,}", "\n\n", text)
    return batch.strip_prices(text.strip())


def find_entry(entries, needle: str):
    for e in entries:
        if needle in e["url"]:
            return e
    raise KeyError(needle)


def chmod_writable(path: Path):
    import stat

    if path.is_file():
        try:
            path.chmod(stat.S_IWRITE | stat.S_IREAD)
        except OSError:
            pass


def main():
    entries = json.loads(ENTRIES.read_text(encoding="utf-8"))["entries"]
    st = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {"done": {}, "errors": []}
    captured_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    for group, sub, needle in INGEST:
        src = find_html(resolve_manual_dir(group, sub))
        entry = find_entry(entries, needle)
        folder = ARCHIVE / entry["folder"]
        folder.mkdir(parents=True, exist_ok=True)
        raw = src.read_bytes()
        dst_html = folder / "evidence_manual_save.html"
        chmod_writable(dst_html)
        dst_html.write_bytes(raw)

        body = html_to_text(raw.decode("utf-8", errors="replace"))
        header = "\n".join([
            f"标题：{entry['title']}",
            f"媒体：{entry['media']}",
            f"发布日期（报表）：{entry['pub_date_raw'] or entry['pub_date']}",
            f"URL：{entry['url']}",
            f"归档时间：{captured_at}",
            f"补传方式：用户手工保存 HTML 直传（未在本机重新打开页面）",
            f"源文件：{src.relative_to(MANUAL)}",
            "",
        ])
        txt = (header + body).replace("\r\n", "\n")
        if not txt.endswith("\n"):
            txt += "\n"
        txt_bytes = txt.encode("utf-8")
        txt_path = folder / "article_source.txt"
        chmod_writable(txt_path)
        txt_path.write_bytes(txt_bytes)

        files = {}
        png = folder / "page_screenshot.png"
        if png.exists():
            files["page_screenshot.png"] = {
                "sha256": batch.sha256_file(png),
                "bytes": png.stat().st_size,
            }
        files["article_source.txt"] = {
            "sha256": batch.sha256_bytes(txt_bytes),
            "bytes": len(txt_bytes),
        }
        files["evidence_manual_save.html"] = {
            "sha256": batch.sha256_bytes(raw),
            "bytes": len(raw),
        }

        access = "OK"
        con_note = "用户手工 HTML 直传归档；香港 IP 未做现场复核，以 HTML+既有截图为准"
        meta = {
            **entry,
            "access": access,
            "con_note": con_note,
            "captured_at": captured_at,
            "http_status": None,
            "page_title": entry["title"],
            "manual_ingest": src.name,
            "ingest_mode": "html_direct",
        }
        batch.write_fragment(folder, meta, files)
        st["done"][entry["url"]] = {
            "folder": entry["folder"],
            "access": access,
            "con_note": con_note,
            "captured_at": captured_at,
        }
        print("ingested", entry["folder"], flush=True)

    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    batch.rebuild_total(entries, st)
    audit = json.loads((ARCHIVE / "AUDIT-LATEST.json").read_text(encoding="utf-8"))
    print("access_ok", audit["access_ok"], "access_con", audit["access_con"], flush=True)


if __name__ == "__main__":
    main()
