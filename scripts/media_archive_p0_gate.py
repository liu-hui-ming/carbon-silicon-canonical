"""Skip capture when canonical folder or same URL already has valid P0 on disk."""
from __future__ import annotations

import json
from pathlib import Path

MIN_PNG_BYTES = 50_000


def folder_has_valid_p0_dir(base: Path, min_png: int = MIN_PNG_BYTES) -> bool:
    if not base.is_dir():
        return False
    if not [p for p in base.glob("*.md") if p.is_file()]:
        return False
    if not (base / "manifest.fragment.json").is_file():
        return False
    ev = base / "evidence-snapshots"
    if not ev.is_dir():
        return False
    pngs = [p for p in ev.glob("*.png") if p.is_file()]
    return bool(pngs) and max(p.stat().st_size for p in pngs) >= min_png


def _url_from_manifest(mf: Path) -> str:
    try:
        data = json.loads(mf.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return ""
    url = (data.get("source_url") or data.get("url") or "").strip()
    return url


def find_valid_folder_for_url(url: str, archive_root: Path) -> Path | None:
    u = url.strip()
    if not u:
        return None
    for d in archive_root.iterdir():
        if not d.is_dir():
            continue
        if not folder_has_valid_p0_dir(d):
            continue
        mf = d / "manifest.fragment.json"
        if not mf.is_file():
            continue
        if _url_from_manifest(mf) == u:
            return d
    return None


def should_skip_capture(url: str, canonical_folder: str, archive_root: Path) -> tuple[bool, str]:
    """Return (skip, reason). reason: canonical | reused:<folder> | empty."""
    base = archive_root / canonical_folder
    if folder_has_valid_p0_dir(base):
        return True, "canonical"
    other = find_valid_folder_for_url(url, archive_root)
    if other is not None:
        return True, f"reused:{other.name}"
    return False, ""