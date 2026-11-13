#!/usr/bin/env python3
"""Print paths for 54 manual-ingest folders (for git add)."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BAD = re.compile(r'[\\/:*?"<>|]')
data = json.loads((ROOT / "compass-pedal-audit/1110-pending-urls-by-category.json").read_text(encoding="utf-8"))
folders: list[str] = []
for items in data["by_media"].values():
    for e in items:
        uh = hashlib.sha256(e["url"].encode()).hexdigest()[:8]
        ms = BAD.sub("_", e["media"])[:24]
        folders.append(f"media_archive/20261110_{e['seq']:04d}_{ms}_{uh}")

if __name__ == "__main__":
    for f in folders:
        print(f)
    if "--add" in sys.argv:
        subprocess.check_call(["git", "-C", str(ROOT), "add", "--"] + folders)
