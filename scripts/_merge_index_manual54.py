#!/usr/bin/env python3
"""Merge 54 manual-ingest INDEX rows into HEAD INDEX (do not bulk-add unrelated local rows)."""
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "media-archive/INDEX.md"
BAD = re.compile(r'[\\/:*?"<>|]')
data = json.loads((ROOT / "compass-pedal-audit/1110-pending-urls-by-category.json").read_text(encoding="utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def folder_rel(seq: int, media: str, url: str) -> str:
    uh = hashlib.sha256(url.encode()).hexdigest()[:8]
    ms = BAD.sub("_", media)[:24]
    return f"media_archive/20261110_{seq:04d}_{ms}_{uh}/"


lines_new: list[str] = []
for items in data["by_media"].values():
    for e in items:
        rel = folder_rel(e["seq"], e["media"], e["url"])
        base = ROOT / rel.rstrip("/")
        md = next(base.glob("*.md"))
        png = next((base / "evidence-snapshots").glob("*.png"))
        md_h = sha256_file(md)
        png_h = sha256_file(png)
        title = e["title"]
        lines_new.append(
            f"| 2026-11-10 | EP-anchor-01 | {e['media']} | {title} | `{md_h}` | `{png_h}` | `{rel}` |"
        )

head = subprocess.check_output(
    ["git", "-C", str(ROOT), "show", "HEAD:media-archive/INDEX.md"],
    text=True,
    encoding="utf-8",
)
rels = {ln.split("|")[-2].strip().strip("`") for ln in lines_new}
out: list[str] = []
for ln in head.splitlines():
    skip = False
    for rel in rels:
        if rel in ln:
            skip = True
            break
    if not skip:
        out.append(ln)
out.extend(lines_new)
INDEX.write_text("\n".join(out).rstrip() + "\n", encoding="utf-8", newline="\n")
print(f"INDEX rows total={len(out)} manual54={len(lines_new)}")
