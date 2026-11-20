#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "media_archive"
JOBS = ROOT / "compass-pedal-audit/media-archive-distribution-1113-1116.json"
MIN = 50_000
BAD = re.compile(r'[\\/:*?"<>|]')
CS = {"satellite-1113": "sat29", "suanli-1116": "suanli", "qiyuan-1116": "qiyuan"}


def safe(s: str) -> str:
    return BAD.sub("_", s).strip() or "untitled"


def folder_for(j: dict) -> str:
    h = hashlib.sha256(j["url"].strip().encode()).hexdigest()[:8]
    return f"{j['date_prefix']}_{CS[j['campaign']]}_{j['seq']:04d}_{safe(j['media'])[:24]}_{h}"


def main() -> None:
    jobs = json.loads(JOBS.read_text(encoding="utf-8"))
    ok, bad = 0, []
    for j in jobs:
        base = ARCHIVE / folder_for(j)
        ev = base / "evidence-snapshots"
        pngs = list(ev.glob("*.png")) if ev.is_dir() else []
        good = (
            pngs
            and max(p.stat().st_size for p in pngs) >= MIN
            and (base / "manifest.fragment.json").is_file()
            and list(base.glob("*.md"))
        )
        if good:
            ok += 1
        else:
            bad.append(folder_for(j))
    print("valid", ok, "need", len(bad), "total", len(jobs))
    for name in bad[:20]:
        print(" ", name)


if __name__ == "__main__":
    main()