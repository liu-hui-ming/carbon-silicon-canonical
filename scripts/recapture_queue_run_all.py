# -*- coding: utf-8 -*-
"""Run recapture queues in order: pending3 → http0 → still-con-650."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "media-evidence-ledger" / "recapture-queue"
STATE = ROOT / "_tmp_recapture_queue_state.json"
SCRIPT = ROOT / "scripts" / "recapture_slow_one_by_one.py"

PHASES = [
    "02-http0-skip-bozhou-ccidnet.json",
    "03-still-con-from-650.json",
]


def main():
    for name in PHASES:
        p = QUEUE / name
        if not p.exists():
            print("skip missing", p, flush=True)
            continue
        print("=== PHASE", name, "===", flush=True)
        r = subprocess.run(
            [sys.executable, str(SCRIPT), str(p), str(STATE)],
            cwd=str(ROOT),
        )
        if r.returncode != 0:
            print("phase failed", name, r.returncode, flush=True)
            sys.exit(r.returncode)
    print("ALL PHASES DONE", flush=True)


if __name__ == "__main__":
    main()
