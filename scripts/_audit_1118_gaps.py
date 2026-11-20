#!/usr/bin/env python3
"""Summarize 1118 gaps: why no valid P0 on disk."""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import media_archive_p0_gate as p0gate  # noqa: E402
from media_archive_1118_settlement_batch import XLSX_DEFAULT, load_entries  # noqa: E402

STATE = ROOT / "compass-pedal-audit/media-archive-1118-settlement.state.json"
ARCHIVE = ROOT / "media_archive"


def err_kind(msg: str) -> str:
    m = msg or ""
    if "ERR_BLOCKED_BY_CLIENT" in m:
        return "ERR_BLOCKED_BY_CLIENT"
    if "ERR_CONNECTION_REFUSED" in m:
        return "ERR_CONNECTION_REFUSED"
    if "ERR_CONNECTION_TIMED_OUT" in m or "Timeout" in m:
        return "TIMEOUT"
    if "ERR_HTTP2_PROTOCOL_ERROR" in m:
        return "ERR_HTTP2_PROTOCOL_ERROR"
    if "Target page, context or browser has been closed" in m:
        return "BROWSER_CLOSED"
    if "ERR_ABORTED" in m:
        return "ERR_ABORTED"
    if "ERR_EMPTY_RESPONSE" in m:
        return "ERR_EMPTY_RESPONSE"
    return "OTHER"


def host_of(url: str) -> str:
    try:
        return urlparse(url).netloc or url[:40]
    except Exception:
        return "?"


def partial_note(folder: Path) -> str:
    if not folder.is_dir():
        return "no_dir"
    ev = folder / "evidence-snapshots"
    pngs = list(ev.glob("*.png")) if ev.is_dir() else []
    if not pngs:
        return "empty_dir"
    mx = max(p.stat().st_size for p in pngs)
    if mx < 50_000:
        return f"png_small({mx})"
    if not (folder / "manifest.fragment.json").is_file():
        return "no_manifest"
    if not list(folder.glob("*.md")):
        return "no_md"
    return "?"


def main() -> None:
    entries = load_entries(XLSX_DEFAULT)
    state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.is_file() else {}
    errors = state.get("errors", {})

    gaps = [e for e in entries if not p0gate.should_skip_capture(e["url"], e["folder"], ARCHIVE)[0]]
    kinds: Counter[str] = Counter()
    hosts: Counter[str] = Counter()
    media_c: Counter[str] = Counter()
    partial: Counter[str] = Counter()

    print(f"gaps={len(gaps)}")
    for e in gaps:
        url = e["url"]
        folder = ARCHIVE / e["folder"]
        partial[partial_note(folder)] += 1
        err = errors.get(url, {})
        msg = str(err.get("error", ""))
        kinds[err_kind(msg)] += 1
        media_c[e["media"][:24]] += 1
        hosts[host_of(url)] += 1

    print("\n=== last_error_kind (state) ===")
    for k, n in kinds.most_common():
        print(f"  {k}: {n}")

    print("\n=== on_disk_partial ===")
    for k, n in partial.most_common():
        print(f"  {k}: {n}")

    print("\n=== host (top 12) ===")
    for h, n in hosts.most_common(12):
        print(f"  {h}: {n}")

    print("\n=== media (top 12) ===")
    for m, n in media_c.most_common(12):
        print(f"  {m}: {n}")


if __name__ == "__main__":
    main()