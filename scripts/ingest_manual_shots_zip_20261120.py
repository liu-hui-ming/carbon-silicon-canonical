#!/usr/bin/env python3
"""Ingest shots_1118_p0_20261120.zip + shots_1120_p0_20261120.zip manual P0 captures."""
from __future__ import annotations

import argparse
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
from media_archive_1118_settlement_batch import (  # noqa: E402
    INDEX_PATH,
    load_entries as load_entries_1118,
)
from media_archive_1118_settlement_batch import XLSX_DEFAULT  # noqa: E402

ARCHIVE_ROOT = ROOT / "media_archive"
ANCHOR = "EP-anchor-01"
MIN_PNG = 50_000
TZ_CN = timezone(timedelta(hours=8))
BAD = re.compile(r'[\\/:*?"<>|]')
ZIP_1118 = Path(r"e:/hundred-crayfish-legion/carbon-silicon-daotong/归档日报/shots_1118_p0_20261120.zip")
ZIP_DIST = Path(r"e:/hundred-crayfish-legion/carbon-silicon-daotong/归档日报/shots_1120_p0_20261120.zip")
JOBS_PATH = ROOT / "compass-pedal-audit/media-archive-distribution-1113-1116.json"
STATE_1118 = ROOT / "compass-pedal-audit/media-archive-1118-settlement.state.json"
STATE_DIST = ROOT / "compass-pedal-audit/media-archive-distribution-1113-1116.state.json"
AUDIT = ROOT / "compass-pedal-audit/media-archive-manual-shots-20261120.log"
EXTRACT = ROOT / "compass-pedal-audit/shots_manual_20261120"
CS = {"satellite-1113": "sat29", "suanli-1116": "suanli", "qiyuan-1116": "qiyuan"}


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
    if "本地" in s or "localrender" in v.lower() or "渲染" in s:
        order = ["page_screenshot_localrender.png", "page_screenshot.png"]
    elif "正文" in v or "回退" in v or "urllib" in v.lower():
        order = ["page_screenshot.png", "page_screenshot_localrender.png"]
    elif "手动" in s:
        order = [
            "page_screenshot_manual_2.png",
            "page_screenshot_manual_1.png",
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
        f"- **采集**：{note}",
    ]
    if job.get("submit_batch"):
        lines.append(f"- **提交批次**：{job['submit_batch']}")
    lines.append("- **页面发布日期**：（以截图为准）")
    lines.append("")
    lines.append("---")
    lines.append("")
    if body.strip():
        lines.append(body.strip())
    else:
        lines.append("（正文自页面抽取为空，以截图与回链为准）")
    lines.append("")
    md_path = base / job["md_name"]
    md_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return md_path


def write_manifest(base: Path, job: dict, md_hash: str, png_hash: str, md_b: int, png_b: int, capture_tag: str) -> None:
    frag = {
        "anchor": ANCHOR,
        "capture_standard": "P0-four-elements-v2",
        "date": job.get("date_row", "2026-11-18"),
        "seq": job.get("seq"),
        "title": job["title"],
        "media": job["media"],
        "url": job["url"],
        "capture_mode": capture_tag,
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
    date_row = job.get("date_row", "2026-11-18")
    rel = f"media_archive/{job['folder']}/"
    line = f"| {date_row} | {ANCHOR} | {job['media']} | {job['title']} | `{md_hash}` | `{png_hash}` | `{rel}` |"
    text = INDEX_PATH.read_text(encoding="utf-8") if INDEX_PATH.is_file() else (
        "# media-archive INDEX\n\n| 日期 | 锚点 | 媒体 | 标题 | MD SHA256 | PNG SHA256 | 路径 |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
    )
    if md_hash not in text:
        INDEX_PATH.write_text(text.rstrip() + "\n" + line + "\n", encoding="utf-8", newline="\n")
    elif rel not in text:
        INDEX_PATH.write_text(text.rstrip() + "\n" + line + "\n", encoding="utf-8", newline="\n")


def load_tsv(zf: zipfile.ZipFile) -> list[dict]:
    for name in zf.namelist():
        if name.endswith("result.tsv"):
            raw = zf.read(name).decode("utf-8")
            return list(csv.DictReader(io.StringIO(raw), delimiter="\t"))
    return []


def dist_jobs_by_folder() -> dict[str, dict]:
    jobs = json.loads(JOBS_PATH.read_text(encoding="utf-8"))
    out: dict[str, dict] = {}
    for j in jobs:
        h = hashlib.sha256(j["url"].strip().encode()).hexdigest()[:8]
        folder = f"{j['date_prefix']}_{CS[j['campaign']]}_{j['seq']:04d}_{safe_name(j['media'])[:24]}_{h}"
        stem = f"{j['title']}_{j['media']}"
        out[folder] = {
            **j,
            "folder": folder,
            "md_name": safe_name(stem) + ".md",
            "png_name": safe_name(stem) + "_snapshot.png",
            "date_row": j.get("date_row", "2026-11-16"),
        }
    return out


def entries_1118_by_folder() -> dict[str, dict]:
    return {e["folder"]: e for e in load_entries_1118(XLSX_DEFAULT)}


def find_shot_dir(root: Path, folder: str) -> Path | None:
    direct = root / folder
    if direct.is_dir():
        return direct
    suffix = folder.rsplit("_", 1)[-1]
    for d in root.iterdir():
        if d.is_dir() and d.name.endswith(suffix):
            return d
    for d in root.iterdir():
        if d.is_dir() and folder in d.name:
            return d
    return None


def ingest_rows(
    rows: list[dict],
    shots_root: Path,
    job_by_folder: dict[str, dict],
    capture_tag: str,
    state_path: Path,
    *,
    force: bool = False,
) -> tuple[int, list[str]]:
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else {"done_urls": {}, "errors": {}}
    done = state.setdefault("done_urls", {})
    errors = state.setdefault("errors", {})
    ok = 0
    fail: list[str] = []

    for row in rows:
        folder = (row.get("folder") or "").strip()
        job = job_by_folder.get(folder)
        if not job:
            fail.append(f"no job for folder={folder}")
            continue
        base = ARCHIVE_ROOT / folder
        ev = base / "evidence-snapshots"
        png_dst = ev / job["png_name"]
        if not force and base.is_dir() and png_dst.is_file() and png_dst.stat().st_size >= MIN_PNG:
            if (base / "manifest.fragment.json").is_file() and list(base.glob("*.md")):
                continue
        shot_dir = find_shot_dir(shots_root, folder)
        if not shot_dir:
            fail.append(f"no shot dir folder={folder}")
            continue
        png_src = pick_png(shot_dir, row.get("verdict", ""), row.get("shot", ""))
        if not png_src:
            fail.append(f"no png folder={folder}")
            continue
        dom = pick_dom(shot_dir)
        if dom and dom.suffix in {".txt", ".html"}:
            body = dom.read_text(encoding="utf-8", errors="replace") if dom.suffix == ".txt" else html_to_text(dom)
        else:
            body = html_to_text(dom) if dom else ""
        verdict = row.get("verdict", "OK")
        shot = row.get("shot", "")
        note = f"手动四要素补档 {capture_tag}（{verdict} · {shot}）"

        ev.mkdir(parents=True, exist_ok=True)
        shutil.copy2(png_src, png_dst)
        md_path = write_md(base, job, body, note)
        md_h = sha256_file(md_path)
        png_h = sha256_file(png_dst)
        write_manifest(base, job, md_h, png_h, md_path.stat().st_size, png_dst.stat().st_size, capture_tag)
        append_index(job, md_h, png_h)
        done[job["url"]] = {
            "seq": job.get("seq"),
            "folder": folder,
            "md_sha256": md_h,
            "png_sha256": png_h,
            "manual_zip": capture_tag,
        }
        errors.pop(job["url"], None)
        ok += 1
        with AUDIT.open("a", encoding="utf-8", newline="\n") as f:
            f.write(f"ok folder={folder} png_bytes={png_dst.stat().st_size}\n")

    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ok, fail


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--1118-only", action="store_true", dest="only_1118")
    ap.add_argument("--dist-only", action="store_true")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    EXTRACT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(TZ_CN).strftime("%Y-%m-%dT%H:%M+08:00")
    AUDIT.write_text(f"{stamp} manual shots 20261120 start\n", encoding="utf-8", newline="\n")

    total_ok = 0
    all_fail: list[str] = []

    if not args.dist_only:
        if not ZIP_1118.is_file():
            raise SystemExit(f"missing {ZIP_1118}")
        with zipfile.ZipFile(ZIP_1118) as zf:
            zf.extractall(EXTRACT)
            rows = load_tsv(zf)
        shots_root = EXTRACT / "shots_1118_p0"
        ok, fail = ingest_rows(
            rows,
            shots_root,
            entries_1118_by_folder(),
            "manual_zip_shots_1118_20261120",
            STATE_1118,
            force=args.force,
        )
        total_ok += ok
        all_fail.extend(fail)
        with AUDIT.open("a", encoding="utf-8", newline="\n") as f:
            f.write(f"1118 ingested={ok} fail={len(fail)}\n")

    if not args.only_1118:
        if not ZIP_DIST.is_file():
            raise SystemExit(f"missing {ZIP_DIST}")
        with zipfile.ZipFile(ZIP_DIST) as zf:
            zf.extractall(EXTRACT)
            rows = load_tsv(zf)
        shots_root = EXTRACT / "shots_1120_p0"
        ok, fail = ingest_rows(
            rows,
            shots_root,
            dist_jobs_by_folder(),
            "manual_zip_shots_1120_20261120",
            STATE_DIST,
            force=args.force,
        )
        total_ok += ok
        all_fail.extend(fail)
        with AUDIT.open("a", encoding="utf-8", newline="\n") as f:
            f.write(f"dist ingested={ok} fail={len(fail)}\n")

    print(json.dumps({"ingested_total": total_ok, "failed": all_fail}, ensure_ascii=False, indent=2))
    return 0 if not all_fail else 1


if __name__ == "__main__":
    raise SystemExit(main())