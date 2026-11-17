#!/usr/bin/env python3
"""Repair 11-11 EUV triple: short filenames + legion WeChat P0 PNGs."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import shutil
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGION = Path(r"e:/hundred-crayfish-legion")
INDEX = ROOT / "media-archive/INDEX.md"
AUDIT = ROOT / "compass-pedal-audit/media-archive-20261117-euv-triple-repair.log"
ANCHOR = "EP-anchor-01"
DATE_ROW = "2026-11-11"
TZ_CN = timezone(timedelta(hours=8))
BAD = re.compile(r'[\\/:*?"<>|]')


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_triple():
    triple = ROOT / "scripts/_ingest_euv_triple_20261111.py"
    spec = importlib.util.spec_from_file_location("euv_triple", triple)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod.TITLE, mod.BODY, mod.JOBS


def short_stem(job: dict) -> str:
    if job["slug"] == "apnews":
        return "EP-EUV-001_APNews美联社"
    if job["slug"] == "manila-times":
        return "EP-EUV-MANILA_马尼拉时报"
    return "EP-EUV-SINA_新浪网香港"


def prune(base: Path) -> None:
    for p in list(base.iterdir()):
        if p.is_file() and p.suffix not in {".md", ".json", ".txt"}:
            p.unlink(missing_ok=True)
    ev = base / "evidence-snapshots"
    if ev.is_dir():
        for p in ev.iterdir():
            if p.is_file() and not p.name.startswith("EP-EUV-"):
                p.unlink(missing_ok=True)


def write_md(base: Path, title: str, job: dict) -> tuple[Path, str]:
    md_name = f"{short_stem(job)}.md"
    lines = [
        f"# {title}",
        "",
        f"- **媒体**：{job['media_index']}",
        f"- **来源**：{job['source']}",
        f"- **回链**：{job['url']}",
        f"- **页面发布日期**：{job['pub']}",
        "",
        "---",
        "",
        BODY.strip(),
        "",
    ]
    md_path = base / md_name
    md_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return md_path, md_name


def patch_index(media: str, title: str, md_h: str, png_h: str, rel: str) -> None:
    line = f"| {DATE_ROW} | {ANCHOR} | {media} | {title} | `{md_h}` | `{png_h}` | `{rel}` |"
    text = INDEX.read_text(encoding="utf-8")
    out: list[str] = []
    for ln in text.splitlines():
        if title in ln and media in ln and ANCHOR in ln and ln.strip().startswith("|"):
            out.append(line)
        else:
            out.append(ln)
    INDEX.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")


def main() -> None:
    global BODY
    title, BODY, jobs = load_triple()
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(TZ_CN).strftime("%Y-%m-%dT%H:%M+08:00")
    AUDIT.write_text(f"{stamp} EUV triple repair short names + wx P0\n", encoding="utf-8", newline="\n")
    for job in jobs:
        base = ROOT / "media-archive" / job["slug"] / ANCHOR
        ev = base / "evidence-snapshots"
        ev.mkdir(parents=True, exist_ok=True)
        prune(base)
        src = LEGION / job["wx_png"]
        if not src.is_file():
            raise FileNotFoundError(src)
        stem = short_stem(job)
        png_name = f"{stem}_snapshot.png"
        shutil.copy2(src, ev / png_name)
        md_path, md_name = write_md(base, title, job)
        md_h = sha256_file(md_path)
        png_h = sha256_file(ev / png_name)
        manifest = {
            "anchor": ANCHOR,
            "capture_standard": "P0-four-elements-v2",
            "ingests": [
                {
                    "date": DATE_ROW,
                    "title": title,
                    "media": job["media_index"],
                    "source": job["source"],
                    "url": job["url"],
                    "pub_date_page": job["pub"],
                }
            ],
            "files": {
                md_name: {"sha256": md_h, "bytes": md_path.stat().st_size},
                f"evidence-snapshots/{png_name}": {
                    "sha256": png_h,
                    "bytes": (ev / png_name).stat().st_size,
                },
            },
        }
        (base / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        sums = f"{md_h}  {md_name}\n{png_h}  evidence-snapshots/{png_name}\n"
        (base / "SHA256SUMS.txt").write_text(sums, encoding="utf-8", newline="\n")
        rel = f"media-archive/{job['slug']}/{ANCHOR}/"
        patch_index(job["media_index"], title, md_h, png_h, rel)
        with AUDIT.open("a", encoding="utf-8", newline="\n") as f:
            f.write(f"ok {job['slug']} md={md_h} png={png_h} png_bytes={(ev/png_name).stat().st_size}\n")
    print("done triple repair")


if __name__ == "__main__":
    main()