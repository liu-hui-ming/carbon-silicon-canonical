#!/usr/bin/env python3
"""Mark done_urls for distribution jobs that already have valid P0 (no re-capture)."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import media_archive_p0_gate as p0gate

ROOT = Path(__file__).resolve().parents[1]
JOBS = ROOT / "compass-pedal-audit/media-archive-distribution-1113-1116.json"
STATE = ROOT / "compass-pedal-audit/media-archive-distribution-1113-1116.state.json"
ARCHIVE = ROOT / "media_archive"
BAD = re.compile(r'[\\/:*?"<>|]')
CS = {"satellite-1113": "sat29", "suanli-1116": "suanli", "qiyuan-1116": "qiyuan"}


def safe(s: str) -> str:
    return BAD.sub("_", s).strip() or "untitled"


def folder_for(j: dict) -> str:
    h = hashlib.sha256(j["url"].strip().encode()).hexdigest()[:8]
    return f"{j['date_prefix']}_{CS[j['campaign']]}_{j['seq']:04d}_{safe(j['media'])[:24]}_{h}"


def main() -> None:
    jobs = json.loads(JOBS.read_text(encoding="utf-8"))
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.is_file() else {"done_urls": {}, "errors": {}}
    done = state.setdefault("done_urls", {})
    errors = state.setdefault("errors", {})
    added = 0
    for j in jobs:
        url = j["url"]
        folder = folder_for(j)
        skip, why = p0gate.should_skip_capture(url, folder, ARCHIVE)
        if not skip:
            continue
        errors.pop(url, None)
        if url not in done or done[url].get("skipped") != why:
            done[url] = {"folder": folder, "skipped": why}
            added += 1
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"synced skip markers added_or_updated={added} done_total={len(done)}")


if __name__ == "__main__":
    main()