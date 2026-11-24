#!/usr/bin/env python3
"""Ingest shots_1124_misc_成功4条.zip · 储能（二）待补 seq 1/25/30/31."""
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

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "scripts"))
from media_archive_1118_settlement_batch import INDEX_PATH  # noqa: E402

ARCHIVE_ROOT = ROOT / "media_archive"
ANCHOR = "EP-anchor-01"
MIN_PNG = 50_000
TZ_CN = timezone(timedelta(hours=8))
BAD = re.compile(r'[\\/:*?"<>|]')
ZIP_PATH = Path(r"e:/hundred-crayfish-legion/carbon-silicon-daotong/归档日报/shots_1124_misc_成功4条.zip")
JOBS_PATH = ROOT / "compass-pedal-audit/media-archive-chuneng-1120-20261120.json"
STATE_PATH = ROOT / "compass-pedal-audit/media-archive-chuneng-1120-20261120.state.json"
AUDIT = ROOT / "compass-pedal-audit/media-archive-manual-shots-chuneng-20261124.log"
EXTRACT = ROOT / "compass-pedal-audit/shots_manual_chuneng_20261124"
CAPTURE_TAG = "manual_zip_shots_1124_misc"
SKIP_VERDICT = re.compile(r"打不开|空白|失败|FAIL", re.I)


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


def pick_png(shot_dir: Path, verdict: str, shot_label: str) -> Path | None:
    v = verdict or ""
    s = shot_label or ""
    if "本地" in s or "localrender" in v.lower() or "渲染" in s or shot_dir.name.startswith("1124_0030"):
        order = ["page_screenshot_localrender.png", "page_screenshot.png"]
    elif "手动" in s or "手动" in v:
        order = [
            "page_screenshot_manual_2.png",
            "page_screenshot_manual_1.png",
            "page_screenshot_manual_3.png",
            "page_screenshot.png",
        ]
    else:
        order = ["page_screenshot.png", "page_screenshot_localrender.png", "page_screenshot_manual_1.png"]
    for name in order:
        p = shot_dir / name
        if p.is_file() and p.stat().st_size >= MIN_PNG:
            return p
    pngs = [p for p in shot_dir.glob("*.png") if p.stat().st_size >= MIN_PNG]
    return max(pngs, key=lambda x: x.stat().st_size) if pngs else None


def pick_dom(shot_dir: Path) -> Path | None:
    for name in ("dom.html", "dom_urllib.html", "render.html", "dom_chrome404.html", "body.txt", "body.html"):
        p = shot_dir / name
        if p.is_file() and p.stat().st_size > 100:
            return p
    return None


def write_md(base: Path, job: dict, body: str, note: str) -> Path:
    lines = [
        f"# {job['title']}",
        "",
        f"- **媒体**：{job['media']}",
        f"- **来源**：{job['media']}",
        f"- **回链**：{job['url']}",
        f"- **提交批次**：{job.get('submit_batch', '')}",
        f"- **采集**：{note}",
        f"- **页面发布日期**：（以截图为准）",
        "",
        "---",
        "",
        body.strip() if body.strip() else "（正文自页面抽取为空，以截图与回链为准）",
        "",
    ]
    md_path = base / job["md_name"]
    md_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return md_path


def write_manifest(base: Path, job: dict, md_hash: str, png_hash: str, md_b: int, png_b: int) -> None:
    frag = {
        "anchor": ANCHOR,
        "capture_standard": "P0-four-elements-v2",
        "date": job.get("date_row", "2026-11-20"),
        "campaign": job.get("campaign"),
        "seq": job.get("seq"),
        "title": job["title"],
        "media": job["media"],
        "url": job["url"],
        "submit_batch": job.get("submit_batch"),
        "capture_mode": CAPTURE_TAG,
        "files": {
            job["md_name"]: {"sha256": md_hash, "bytes": md_b},
            f"evidence-snapshots/{job['png_name']}": {"sha256": png_hash, "bytes": png_b},
        },
    }
    (base / "manifest.fragment.json").write_text(
        json.dumps(frag, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    (base / "SHA256SUMS.txt").write_text(
        f"{md_hash}  {job['md_name']}\n{png_hash}  evidence-snapshots/{job['png_name']}\n",
        encoding="utf-8",
        newline="\n",
    )


def append_index(job: dict, md_hash: str, png_hash: str) -> None:
    date_row = job.get("date_row", "2026-11-20")
    rel = f"media_archive/{job['folder']}/"
    line = f"| {date_row} | {ANCHOR} | {job['media']} | {job['title']} | `{md_hash}` | `{png_hash}` | `{rel}` |"
    text = INDEX_PATH.read_text(encoding="utf-8") if INDEX_PATH.is_file() else (
        "# media-archive INDEX\n\n| 日期 | 锚点 | 媒体 | 标题 | MD SHA256 | PNG SHA256 | 路径 |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
    )
    if md_hash not in text:
        INDEX_PATH.write_text(text.rstrip() + "\n" + line + "\n", encoding="utf-8", newline="\n")


def enrich_job(raw: dict) -> dict:
    url = raw["url"].strip()
    url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[:8]
    media_slug = safe_name(raw["media"])[:24]
    folder = f"{raw['date_prefix']}_cn1120_{raw['seq']:04d}_{media_slug}_{url_hash}"
    stem = f"{raw['title']}_{raw['media']}"
    return {
        **raw,
        "url": url,
        "folder": folder,
        "md_name": safe_name(stem) + ".md",
        "png_name": safe_name(stem) + "_snapshot.png",
    }


def jobs_by_seq() -> dict[int, dict]:
    jobs = json.loads(JOBS_PATH.read_text(encoding="utf-8"))
    return {int(j["seq"]): enrich_job(j) for j in jobs}


def find_shot_dir(root: Path, row_folder: str) -> Path | None:
    direct = root / row_folder
    if direct.is_dir():
        return direct
    m = re.match(r"1124_(\d{4})_", row_folder)
    if m:
        seq = m.group(1)
        for d in root.iterdir():
            if d.is_dir() and d.name.startswith(f"1124_{seq}_"):
                return d
    for d in root.iterdir():
        if d.is_dir() and row_folder in d.name:
            return d
    return None


def load_tsv(zf: zipfile.ZipFile) -> list[dict]:
    for name in zf.namelist():
        if name.endswith("result.tsv"):
            raw = zf.read(name).decode("utf-8")
            return list(csv.DictReader(io.StringIO(raw), delimiter="\t"))
    return []


def main() -> int:
    if not ZIP_PATH.is_file():
        raise SystemExit(f"missing {ZIP_PATH}")
    EXTRACT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(TZ_CN).strftime("%Y-%m-%dT%H:%M+08:00")
    AUDIT.write_text(f"{stamp} chuneng 1124 manual zip start\n", encoding="utf-8", newline="\n")

    with zipfile.ZipFile(ZIP_PATH) as zf:
        zf.extractall(EXTRACT)
        rows = load_tsv(zf)
    shots_root = EXTRACT / "shots_1124_misc"
    if not shots_root.is_dir():
        for d in EXTRACT.iterdir():
            if d.is_dir():
                shots_root = d
                break

    by_seq = jobs_by_seq()
    state = json.loads(STATE_PATH.read_text(encoding="utf-8")) if STATE_PATH.is_file() else {"done_urls": {}, "errors": {}}
    done = state.setdefault("done_urls", {})
    errors = state.setdefault("errors", {})
    ok = 0
    fail: list[str] = []
    skipped: list[str] = []

    for row in rows:
        verdict = (row.get("verdict") or "").strip()
        try:
            png_b = int(row.get("pngBytes") or 0)
        except ValueError:
            png_b = 0
        try:
            seq = int(row.get("seq") or 0)
        except ValueError:
            seq = 0
        if not seq or seq not in by_seq:
            fail.append(f"bad seq row={row}")
            continue
        job = by_seq[seq]
        folder = job["folder"]
        row_folder = (row.get("folder") or "").strip()
        shot_dir = find_shot_dir(shots_root, row_folder)
        if not shot_dir:
            if SKIP_VERDICT.search(verdict) or png_b < MIN_PNG:
                skipped.append(f"seq={seq} no dir verdict={verdict}")
                continue
            fail.append(f"no shot dir seq={seq} folder={row_folder}")
            continue
        png_src = pick_png(shot_dir, verdict, row.get("shot", ""))
        if not png_src:
            if SKIP_VERDICT.search(verdict) or png_b < MIN_PNG:
                skipped.append(f"seq={seq} verdict={verdict}")
                continue
            fail.append(f"no png seq={seq}")
            continue
        dom = pick_dom(shot_dir)
        if dom and dom.suffix in {".txt", ".html"}:
            body = dom.read_text(encoding="utf-8", errors="replace") if dom.suffix == ".txt" else html_to_text(dom)
        else:
            body = html_to_text(dom) if dom else ""
        note = f"手动四要素补档 {CAPTURE_TAG}（{verdict} · {row.get('shot', '')}）"
        base = ARCHIVE_ROOT / folder
        ev = base / "evidence-snapshots"
        ev.mkdir(parents=True, exist_ok=True)
        png_dst = ev / job["png_name"]
        shutil.copy2(png_src, png_dst)
        md_path = write_md(base, job, body, note)
        md_h = sha256_file(md_path)
        png_h = sha256_file(png_dst)
        write_manifest(base, job, md_h, png_h, md_path.stat().st_size, png_dst.stat().st_size)
        append_index(job, md_h, png_h)
        done[job["url"]] = {
            "folder": folder,
            "md_sha256": md_h,
            "png_sha256": png_h,
            "manual_zip": CAPTURE_TAG,
        }
        errors.pop(job["url"], None)
        ok += 1
        with AUDIT.open("a", encoding="utf-8", newline="\n") as f:
            f.write(f"ok seq={seq} folder={folder} png_bytes={png_dst.stat().st_size}\n")

    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    with AUDIT.open("a", encoding="utf-8", newline="\n") as f:
        f.write(f"ingested={ok} skipped={skipped} fail={fail}\n")
    print(json.dumps({"ingested": ok, "skipped": skipped, "failed": fail}, ensure_ascii=False, indent=2))
    return 0 if not fail else 1


if __name__ == "__main__":
    raise SystemExit(main())