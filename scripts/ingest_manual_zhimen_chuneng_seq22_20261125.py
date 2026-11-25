#!/usr/bin/env python3
"""Manual P0 · chuneng-1120 seq 22 智门财经 · pasted TIFF screenshots."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
import sys

sys.path.insert(0, str(ROOT / "scripts"))
from media_archive_1118_settlement_batch import INDEX_PATH  # noqa: E402

ARCHIVE_ROOT = ROOT / "media_archive"
ANCHOR = "EP-anchor-01"
MIN_PNG = 50_000
TZ_CN = timezone(timedelta(hours=8))
BAD = re.compile(r'[\\/:*?"<>|]')
JOBS_PATH = ROOT / "compass-pedal-audit/media-archive-chuneng-1120-20261120.json"
STATE_PATH = ROOT / "compass-pedal-audit/media-archive-chuneng-1120-20261120.state.json"
SHOTS_DIR = Path(r"e:/hundred-crayfish-legion/carbon-silicon-daotong/归档日报")
CAPTURE_TAG = "manual_paste_tiff_20261125_zhimen_seq22"
URL = "https://www.zhimen.com/index.php/caijing/24315.html?admin_id=1"
SEQ = 22


def safe_name(name: str) -> str:
    return BAD.sub("_", name).strip() or "untitled"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


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


def tiff_to_png(tiff: Path, png: Path) -> None:
    with Image.open(tiff) as im:
        im = im.convert("RGB")
        png.parent.mkdir(parents=True, exist_ok=True)
        im.save(png, "PNG", optimize=True)


def main() -> int:
    tiffs = sorted(SHOTS_DIR.glob("*.tiff"), key=lambda p: p.name)
    if len(tiffs) < 1:
        raise SystemExit(f"no tiff in {SHOTS_DIR}")
    jobs = json.loads(JOBS_PATH.read_text(encoding="utf-8"))
    raw = next(j for j in jobs if j["seq"] == SEQ and j["url"].strip() == URL)
    job = enrich_job(raw)
    work = ROOT / "compass-pedal-audit/shots_manual_zhimen_20261125"
    work.mkdir(parents=True, exist_ok=True)
    pngs: list[Path] = []
    for i, tiff in enumerate(tiffs[:2], start=1):
        out = work / f"page_screenshot_manual_{i}.png"
        tiff_to_png(tiff, out)
        pngs.append(out)
    png_src = max(pngs, key=lambda p: p.stat().st_size)
    if png_src.stat().st_size < MIN_PNG:
        raise SystemExit(f"png too small {png_src.stat().st_size}")

    note = f"手动四要素补档 {CAPTURE_TAG}（用户粘贴全屏截图×{len(pngs)} · 正文未抓取）"
    body = "（本机 Playwright 超时；正文以截图与回链为准）"
    base = ARCHIVE_ROOT / job["folder"]
    ev = base / "evidence-snapshots"
    ev.mkdir(parents=True, exist_ok=True)
    png_dst = ev / job["png_name"]
    png_dst.write_bytes(png_src.read_bytes())
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
        body,
        "",
    ]
    md_path = base / job["md_name"]
    md_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    md_h = sha256_file(md_path)
    png_h = sha256_file(png_dst)
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
            job["md_name"]: {"sha256": md_h, "bytes": md_path.stat().st_size},
            f"evidence-snapshots/{job['png_name']}": {"sha256": png_h, "bytes": png_dst.stat().st_size},
        },
    }
    (base / "manifest.fragment.json").write_text(
        json.dumps(frag, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    (base / "SHA256SUMS.txt").write_text(
        f"{md_h}  {job['md_name']}\n{png_h}  evidence-snapshots/{job['png_name']}\n",
        encoding="utf-8",
        newline="\n",
    )
    date_row = job.get("date_row", "2026-11-20")
    rel = f"media_archive/{job['folder']}/"
    line = f"| {date_row} | {ANCHOR} | {job['media']} | {job['title']} | `{md_h}` | `{png_h}` | `{rel}` |"
    text = INDEX_PATH.read_text(encoding="utf-8") if INDEX_PATH.is_file() else ""
    if md_h not in text:
        INDEX_PATH.write_text(text.rstrip() + "\n" + line + "\n", encoding="utf-8", newline="\n")

    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    state.setdefault("done_urls", {})[job["url"]] = {
        "folder": job["folder"],
        "md_sha256": md_h,
        "png_sha256": png_h,
        "manual_zip": CAPTURE_TAG,
    }
    state.get("errors", {}).pop(job["url"], None)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    audit = ROOT / "compass-pedal-audit/media-archive-manual-zhimen-20261125.log"
    stamp = datetime.now(TZ_CN).strftime("%Y-%m-%dT%H:%M+08:00")
    with audit.open("a", encoding="utf-8", newline="\n") as f:
        f.write(f"{stamp} ok folder={job['folder']} png_bytes={png_dst.stat().st_size}\n")
    print(json.dumps({"folder": job["folder"], "png_bytes": png_dst.stat().st_size}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())