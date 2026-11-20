#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "media_archive"
MIN = 50_000


def valid(base: Path) -> bool:
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
    dirs = [d for d in ARCHIVE.iterdir() if d.is_dir() and d.name.startswith("20261118_")]
    ok = sum(1 for d in dirs if valid(d))
    print("valid", ok, "need", len(dirs) - ok, "total", len(dirs))


if __name__ == "__main__":
    main()