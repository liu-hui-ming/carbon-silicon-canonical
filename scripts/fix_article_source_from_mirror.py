# -*- coding: utf-8 -*-
"""Rebuild stub article_source.txt from evidence_mirror.html (UTF-8 text, not empty header-only)."""
from __future__ import annotations

import importlib.util
import json
import re
from datetime import datetime
from html import unescape
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "media_archive"
CATALOG = Path(r"e:\hundred-crayfish-legion\_tmp_media_evidence_catalog.json")
INGEST = (
    ROOT
    / "media-evidence-ledger/recapture-domestic-ip-20261019/INGEST-REPORT-20261020.json"
)
STATE = ROOT / "_tmp_media_evidence_state_dt5322.json"


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self._skip = True

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"):
            self._skip = False
        if tag in ("p", "div", "br", "li", "h1", "h2", "h3", "tr"):
            self.parts.append("\n")

    def handle_data(self, data):
        if not self._skip:
            t = data.strip()
            if t:
                self.parts.append(t + " ")


def html_to_text(html: str) -> str:
    p = TextExtractor()
    p.feed(html)
    text = unescape("".join(p.parts))
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def is_stub(txt_path: Path) -> bool:
    if not txt_path.exists():
        return True
    text = txt_path.read_text(encoding="utf-8", errors="replace")
    if "国内IP人工重采" not in text and "Mac 无头" not in text:
        return False
    body = text.split("\n\n", 1)[1].strip() if "\n\n" in text else ""
    return len(body) < 80


def main():
    spec = importlib.util.spec_from_file_location(
        "batch", ROOT / "scripts/media_evidence_archive_batch.py"
    )
    batch = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(batch)

    by_folder = {
        e["folder"]: e for e in json.loads(CATALOG.read_text(encoding="utf-8"))["entries"]
    }
    targets: list[str] = []
    if INGEST.exists():
        rep = json.loads(INGEST.read_text(encoding="utf-8"))
        targets = [r["target"] for r in rep.get("ingested", [])]

    fixed = 0
    skipped = 0
    for folder_name in targets:
        folder = ARCHIVE / folder_name
        txt_path = folder / "article_source.txt"
        if not is_stub(txt_path):
            continue
        mirror = folder / "evidence_mirror.html"
        if not mirror.exists():
            mirror = folder / "dom.html"
        if not mirror.exists():
            skipped += 1
            continue

        entry = by_folder.get(folder_name, {})
        frag_path = folder / "manifest.fragment.json"
        frag = (
            json.loads(frag_path.read_text(encoding="utf-8"))
            if frag_path.exists()
            else {}
        )
        url = frag.get("url") or entry.get("url", "")
        media = entry.get("media") or frag.get("media", "")
        title = entry.get("title") or frag.get("title", "")
        pub = entry.get("pub_date_raw") or entry.get("pub_date") or frag.get("pub_date", "")

        html = mirror.read_text(encoding="utf-8", errors="replace")
        body = html_to_text(html)
        if len(body) < 40:
            skipped += 1
            continue
        # first line often page title
        page_title = body.split("\n", 1)[0][:120] if body else title

        captured_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        header = "\n".join(
            [
                f"标题：{title}",
                f"媒体：{media}",
                f"发布日期（报表）：{pub}",
                f"URL：{url}",
                f"取证系统时间：{captured_at}",
                f"HTTP：未知",
                f"页面标题：{page_title}",
                "截图标准：P0-four-elements-v2（国内IP重采；正文自 evidence_mirror.html 提取）",
                "链接失效：否",
                "",
            ]
        )
        out = (header + body).replace("\r\n", "\n").replace("\r", "\n")
        if not out.endswith("\n"):
            out += "\n"
        txt_path.write_text(out, encoding="utf-8")
        fixed += 1

        if frag_path.exists():
            frag["captured_at"] = captured_at
            files = frag.get("files", {})
            txt_bytes = txt_path.read_bytes()
            files["article_source.txt"] = {
                "sha256": batch.sha256_bytes(txt_bytes),
                "bytes": len(txt_bytes),
            }
            if (folder / "page_screenshot.png").exists():
                png = folder / "page_screenshot.png"
                files["page_screenshot.png"] = {
                    "sha256": batch.sha256_file(png),
                    "bytes": png.stat().st_size,
                }
            frag["files"] = files
            batch.write_fragment(folder, frag, files)

    entries = json.loads(CATALOG.read_text(encoding="utf-8"))["entries"]
    st = (
        json.loads(STATE.read_text(encoding="utf-8"))
        if STATE.exists()
        else {"done": {}, "errors": []}
    )
    batch.rebuild_total(entries, st)

    # sync audit from fragments
    con = []
    ok = 0
    for e in entries:
        f = json.loads((ARCHIVE / e["folder"] / "manifest.fragment.json").read_text(encoding="utf-8"))
        if f.get("access") == "OK":
            ok += 1
        else:
            con.append(
                {
                    "url": e["url"],
                    "title": e.get("title", ""),
                    "media": e.get("media", ""),
                    "folder": e["folder"],
                    "note": f.get("con_note", ""),
                }
            )
    audit_path = ARCHIVE / "AUDIT-LATEST.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    audit.update(
        {
            "access_ok": ok,
            "access_con": len(con),
            "con_list": con,
            "success_archived": len(entries),
            "entry_total": len(entries),
        }
    )
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (ARCHIVE / "CON_LEDGER.json").write_text(
        json.dumps(
            {
                "note": "源链接已失效或取证异常时，仍以本地截图与 article_source.txt 为据",
                "entries": con,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print("fixed", fixed, "skipped", skipped)


if __name__ == "__main__":
    main()
