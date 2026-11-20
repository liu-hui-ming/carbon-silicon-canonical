#!/usr/bin/env python3
"""Check 75-list gaps: never collected vs partial vs duplicate URL elsewhere."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "media_archive"
JOBS_PATH = ROOT / "compass-pedal-audit/media-archive-distribution-1113-1116.json"
STATE_PATH = ROOT / "compass-pedal-audit/media-archive-distribution-1113-1116.state.json"
SETTLE_STATE = ROOT / "compass-pedal-audit/media-archive-1118-settlement.state.json"
MIN = 50_000
BAD = re.compile(r'[\\/:*?"<>|]')
CS = {"satellite-1113": "sat29", "suanli-1116": "suanli", "qiyuan-1116": "qiyuan"}


def safe(s: str) -> str:
    return BAD.sub("_", s).strip() or "untitled"


def folder_for(j: dict) -> str:
    h = hashlib.sha256(j["url"].strip().encode()).hexdigest()[:8]
    return f"{j['date_prefix']}_{CS[j['campaign']]}_{j['seq']:04d}_{safe(j['media'])[:24]}_{h}"


def valid_p0(base: Path) -> bool:
    if not base.is_dir():
        return False
    ev = base / "evidence-snapshots"
    pngs = list(ev.glob("*.png")) if ev.is_dir() else []
    if not pngs or max(p.stat().st_size for p in pngs) < MIN:
        return False
    if not (base / "manifest.fragment.json").is_file():
        return False
    return bool(list(base.glob("*.md")))


def main() -> None:
    jobs = json.loads(JOBS_PATH.read_text(encoding="utf-8"))
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    settle_urls: set[str] = set()
    if SETTLE_STATE.is_file():
        s = json.loads(SETTLE_STATE.read_text(encoding="utf-8"))
        for k in s.get("done_urls", {}):
            settle_urls.add(k)

    by_manifest_url: dict[str, str] = {}
    by_url_hash: dict[str, list[str]] = {}
    for d in ARCHIVE.iterdir():
        if not d.is_dir():
            continue
        tail = d.name.rsplit("_", 1)
        if len(tail) == 2:
            by_url_hash.setdefault(tail[1], []).append(d.name)
        mf = d / "manifest.fragment.json"
        if mf.is_file():
            try:
                m = json.loads(mf.read_text(encoding="utf-8"))
                u = (m.get("source_url") or m.get("url") or "").strip()
                if u:
                    by_manifest_url[u] = d.name
            except json.JSONDecodeError:
                pass

    done = state.get("done_urls", {})
    errors = state.get("errors", {})

    never, partial, in_state_only = 0, 0, 0
    print("campaign\tseq\tmedia\tstatus\tfolder_exists\tdone_urls\terrors\t1118_done\talt_folder")
    for j in jobs:
        folder = folder_for(j)
        base = ARCHIVE / folder
        if valid_p0(base):
            continue
        u = j["url"]
        h = hashlib.sha256(u.strip().encode()).hexdigest()[:8]
        exists = base.is_dir()
        in_done = u in done
        in_err = u in errors

        status = "never"
        if exists:
            status = "partial"
            partial += 1
        else:
            never += 1

        alt = by_manifest_url.get(u)
        alts_hash = [x for x in by_url_hash.get(h, []) if x != folder]
        in_1118 = u in settle_urls

        if in_done and status == "never":
            in_state_only += 1

        err_short = ""
        if in_err:
            err_short = str(errors[u].get("error", ""))[:80]

        print(
            f"{j['campaign']}\t{j['seq']}\t{j['media'][:18]}\t{status}\t{exists}\t"
            f"{in_done}\t{in_err}\t{in_1118}\t{alt or (alts_hash[0] if alts_hash else '-')}"
        )
        if err_short:
            print(f"  err: {err_short}")

    missing = sum(1 for j in jobs if not valid_p0(ARCHIVE / folder_for(j)))
    print("---")
    print(f"missing_total={missing} never_dir={never} partial_dir={partial}")
    print(f"state_done_but_no_p0={in_state_only}")
    print(f"urls_also_in_1118_done={sum(1 for j in jobs if not valid_p0(ARCHIVE/folder_for(j)) and j['url'] in settle_urls)}")


if __name__ == "__main__":
    main()