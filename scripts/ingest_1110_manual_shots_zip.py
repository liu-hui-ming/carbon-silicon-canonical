#!/usr/bin/env python3
"""Ingest shots_1110_20261113.zip manual captures into media_archive/20261110_*."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import shutil
import zipfile
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
ZIP_DEFAULT = Path(r"e:/hundred-crayfish-legion/shots_1110_20261113.zip")
EXTRACT_DIR = ROOT / "compass-pedal-audit/shots_1110_20261113"
ARCHIVE_ROOT = ROOT / "media_archive"
INDEX_PATH = ROOT / "media-archive/INDEX.md"
STATE_PATH = ROOT / "compass-pedal-audit/media-archive-1110-settlement.state.json"
AUDIT_LOG = ROOT / "compass-pedal-audit/media-archive-1110-manual-ingest-20261113.log"
XLSX = Path(r"e:/hundred-crayfish-legion/1110结算.xlsx")
DATE_ROW = "2026-11-10"
ANCHOR = "EP-anchor-01"
MIN_PNG = 50_000
TZ_CN = timezone(timedelta(hours=8))
BAD = re.compile(r'[\\/:*?"<>|]')


def safe_name(name: str) -> str:
    return BAD.sub("_", name).strip() or "untitled"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []
        self._skip = False

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip = True

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"}:
            self._skip = False
        if tag in {"p", "br", "div", "li", "h1", "h2", "h3", "tr"}:
            self._chunks.append("\n")

    def handle_data(self, data: str) -> None:
        if not self._skip and data.strip():
            self._chunks.append(data.strip())


def html_to_text(path: Path) -> str:
    if not path.is_file():
        return ""
    raw = path.read_text(encoding="utf-8", errors="replace")
    p = _TextExtractor()
    p.feed(raw)
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(p._chunks))
    text = re.sub(r"[ \t]+\n", "\n", text).strip()
    if len(text) > 120000:
        text = text[:120000] + "\n\n（正文截断：超长页面）\n"
    return text


def load_entries() -> list[dict]:
    wb = openpyxl.load_workbook(XLSX, read_only=True, data_only=True)
    ws = wb["大总表"]
    it = ws.iter_rows(values_only=True)
    next(it)
    next(it)
    out: list[dict] = []
    for row in it:
        if not row or row[0] is None:
            continue
        seq_raw = str(row[0]).strip().rstrip("、")
        if not seq_raw.isdigit():
            continue
        seq = int(seq_raw)
        submit_batch = row[1]
        title = (row[2] or "").strip()
        media = (row[3] or "").strip()
        url = (row[4] or "").strip()
        if not url or not title:
            continue
        url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[:8]
        media_slug = safe_name(media)[:24]
        folder = f"20261110_{seq:04d}_{media_slug}_{url_hash}"
        stem = f"{title}_{media}"
        out.append(
            {
                "seq": seq,
                "title": title,
                "media": media,
                "url": url,
                "submit_batch": (str(submit_batch).strip() if submit_batch else None),
                "folder": folder,
                "md_name": safe_name(stem) + ".md",
                "png_name": safe_name(stem) + "_snapshot.png",
            }
        )
    wb.close()
    return out


def folder_has_valid_p0(base: Path) -> bool:
    if not base.is_dir():
        return False
    md_files = list(base.glob("*.md"))
    if not md_files or not (base / "manifest.fragment.json").is_file():
        return False
    ev = base / "evidence-snapshots"
    if not ev.is_dir():
        return False
    pngs = list(ev.glob("*.png"))
    return bool(pngs) and max(p.stat().st_size for p in pngs) >= MIN_PNG


def pick_png(shot_dir: Path, verdict: str, shot_label: str) -> Path | None:
    order: list[str] = []
    v = verdict or ""
    s = shot_label or ""
    if "本地渲染" in s or "localrender" in v.lower():
        order = ["page_screenshot_localrender.png", "page_screenshot.png"]
    elif "手动" in s or "手动" in v:
        order = [
            "page_screenshot_manual_2.png",
            "page_screenshot_manual_1.png",
            "page_screenshot.png",
        ]
    else:
        order = ["page_screenshot.png", "page_screenshot_localrender.png"]
    for name in order:
        p = shot_dir / name
        if p.is_file() and p.stat().st_size >= MIN_PNG:
            return p
    pngs = [p for p in shot_dir.glob("*.png") if p.stat().st_size >= MIN_PNG]
    return max(pngs, key=lambda x: x.stat().st_size) if pngs else None


def pick_dom(shot_dir: Path) -> Path | None:
    for name in ("dom.html", "dom_urllib.html", "render.html", "dom_chrome404.html"):
        p = shot_dir / name
        if p.is_file() and p.stat().st_size > 200:
            return p
    return None


def write_md(base: Path, job: dict, body: str, note: str) -> Path:
    lines = [
        f"# {job['title']}",
        "",
        f"- **媒体**：{job['media']}",
        f"- **来源**：{job['media']}",
        f"- **回链**：{job['url']}",
        f"- **采集**：{note}",
    ]
    if job.get("submit_batch"):
        lines.append(f"- **提交批次**：{job['submit_batch']}")
    lines.append("- **页面发布日期**：（以截图为准）")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(body.strip() if body.strip() else "（正文自页面抽取为空，以截图与回链为准）")
    lines.append("")
    md_path = base / job["md_name"]
    md_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return md_path


def write_folder_manifest(base: Path, job: dict, md_hash: str, png_hash: str, md_bytes: int, png_bytes: int) -> None:
    frag = {
        "anchor": ANCHOR,
        "capture_standard": "P0-four-elements-v2",
        "date": DATE_ROW,
        "seq": job["seq"],
        "title": job["title"],
        "media": job["media"],
        "url": job["url"],
        "capture_mode": "manual_zip_shots_1110_20261113",
        "files": {
            job["md_name"]: {"sha256": md_hash, "bytes": md_bytes},
            f"evidence-snapshots/{job['png_name']}": {"sha256": png_hash, "bytes": png_bytes},
        },
    }
    (base / "manifest.fragment.json").write_text(
        json.dumps(frag, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    sums = f"{md_hash}  {job['md_name']}\n{png_hash}  evidence-snapshots/{job['png_name']}\n"
    (base / "SHA256SUMS.txt").write_text(sums, encoding="utf-8", newline="\n")


def upsert_index_line(job: dict, md_hash: str, png_hash: str) -> None:
    rel = f"media_archive/{job['folder']}/"
    new_line = f"| {DATE_ROW} | {ANCHOR} | {job['media']} | {job['title']} | `{md_hash}` | `{png_hash}` | `{rel}` |"
    header = (
        "# media-archive INDEX\n\n| 日期 | 锚点 | 媒体 | 标题 | MD SHA256 | PNG SHA256 | 路径 |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
    )
    lines = INDEX_PATH.read_text(encoding="utf-8").splitlines() if INDEX_PATH.is_file() else header.splitlines()
    out: list[str] = []
    replaced = False
    for ln in lines:
        if rel in ln and job["title"] in ln:
            out.append(new_line)
            replaced = True
        elif f"| {job['title']} |" in ln and rel.split("/")[0] in ln:
            out.append(new_line)
            replaced = True
        else:
            out.append(ln)
    if not replaced and md_hash not in "\n".join(out):
        out.append(new_line)
    INDEX_PATH.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8", newline="\n")


def load_tsv_from_zip(zf: zipfile.ZipFile) -> dict[int, dict]:
    raw = zf.read("shots_1110/result.tsv").decode("utf-8")
    rows = list(csv.DictReader(io.StringIO(raw), delimiter="\t"))
    return {int(r["seq"]): r for r in rows}


def main() -> int:
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    if not ZIP_DEFAULT.is_file():
        raise SystemExit(f"missing zip: {ZIP_DEFAULT}")
    with zipfile.ZipFile(ZIP_DEFAULT) as zf:
        zf.extractall(EXTRACT_DIR)
        tsv = load_tsv_from_zip(zf)

    entries = {e["seq"]: e for e in load_entries()}
    pending = [e for e in entries.values() if not folder_has_valid_p0(ARCHIVE_ROOT / e["folder"])]
    stamp = datetime.now(TZ_CN).strftime("%Y-%m-%dT%H:%M+08:00")
    AUDIT_LOG.write_text(
        f"{stamp} manual zip ingest start pending={len(pending)} zip={ZIP_DEFAULT}\n",
        encoding="utf-8",
        newline="\n",
    )

    state = json.loads(STATE_PATH.read_text(encoding="utf-8")) if STATE_PATH.is_file() else {"done_urls": {}, "errors": {}}
    done = state.setdefault("done_urls", {})
    errors = state.setdefault("errors", {})
    ok = 0
    fail: list[str] = []

    for job in sorted(pending, key=lambda x: x["seq"]):
        seq = job["seq"]
        row = tsv.get(seq)
        if not row:
            fail.append(f"seq={seq}: missing in result.tsv")
            continue
        shots_root = EXTRACT_DIR / "shots_1110"
        matches = sorted(d.name for d in shots_root.iterdir() if d.is_dir() and d.name.startswith(f"{seq}_"))
        if not matches:
            fail.append(f"seq={seq}: no shots_1110/{seq}_* dir")
            continue
        shot_dir = shots_root / matches[0]
        png_src = pick_png(shot_dir, row.get("verdict", ""), row.get("shot", ""))
        if not png_src:
            fail.append(f"seq={seq}: no png>={MIN_PNG}")
            continue
        dom = pick_dom(shot_dir)
        body = html_to_text(dom) if dom else ""
        verdict = row.get("verdict", "OK")
        note = f"手动四要素补档 shots_1110_20261113（{verdict} · {row.get('shot','')}）"

        base = ARCHIVE_ROOT / job["folder"]
        ev = base / "evidence-snapshots"
        ev.mkdir(parents=True, exist_ok=True)
        png_dst = ev / job["png_name"]
        shutil.copy2(png_src, png_dst)
        md_path = write_md(base, job, body, note)
        md_h = sha256_file(md_path)
        png_h = sha256_file(png_dst)
        write_folder_manifest(base, job, md_h, png_h, md_path.stat().st_size, png_dst.stat().st_size)
        upsert_index_line(job, md_h, png_h)
        done[job["url"]] = {"seq": seq, "folder": job["folder"], "md_sha256": md_h, "png_sha256": png_h}
        errors.pop(job["url"], None)
        ok += 1
        with AUDIT_LOG.open("a", encoding="utf-8", newline="\n") as f:
            f.write(f"seq={seq} md={md_h} png={png_h} src={png_src.name} bytes={png_dst.stat().st_size}\n")

    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    summary = {"ingested": ok, "failed": fail, "pending_before": len(pending)}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not fail else 1


if __name__ == "__main__":
    raise SystemExit(main())
