#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JOBS = ROOT / "compass-pedal-audit/media-archive-puxi-014-016-20261119.json"
ARCH = ROOT / "media_archive"
MIN = 50_000
BAD = re.compile(r'[\\/:*?"<>|]')


def safe(n: str) -> str:
    return BAD.sub("_", n).strip() or "untitled"


def folder_for(j: dict) -> str:
    cs = {"puxi-014": "puxi014", "puxi-015": "puxi015", "puxi-016": "puxi016"}
    h = hashlib.sha256(j["url"].strip().encode()).hexdigest()[:8]
    return f"{j['date_prefix']}_{cs[j['campaign']]}_{j['seq']:04d}_{safe(j['media'])[:24]}_{h}"


def valid(folder: str) -> bool:
    p = ARCH / folder
    if not p.is_dir():
        return False
    if not (p / "manifest.fragment.json").is_file():
        return False
    if not list(p.glob("*.md")):
        return False
    ev = p / "evidence-snapshots"
    if not ev.is_dir():
        return False
    return any(x.stat().st_size >= MIN for x in ev.glob("*.png"))


def main() -> None:
    jobs = json.loads(JOBS.read_text(encoding="utf-8"))
    by: dict[str, list[str]] = {}
    ok: list[str] = []
    need: list[str] = []
    for j in jobs:
        f = folder_for(j)
        by.setdefault(j["campaign"], []).append(f)
        if valid(f):
            ok.append(f)
        else:
            need.append(f)
    for camp in ("puxi-014", "puxi-015", "puxi-016"):
        subset = [j for j in jobs if j["campaign"] == camp]
        v = sum(1 for j in subset if valid(folder_for(j)))
        print(f"{camp} valid {v}/{len(subset)}")
    print(f"valid {len(ok)} need {len(need)} total {len(jobs)}")
    for f in need[:8]:
        print(f"  {f}")
    if len(need) > 8:
        print(f"  ... +{len(need) - 8} more")


if __name__ == "__main__":
    main()