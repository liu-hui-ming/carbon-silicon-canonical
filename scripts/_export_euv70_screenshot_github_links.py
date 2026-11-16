#!/usr/bin/env python3
"""Emit GitHub blob links for EUV batch #2-#71 P0 screenshots (from manifest paths)."""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
JSON = ROOT / "compass-pedal-audit/euv-ap-distribution-71.json"
OUT = ROOT / "compass-pedal-audit/euv-ap-70-screenshot-github-links.md"
REPO = "https://github.com/liu-hui-ming/carbon-silicon-canonical/blob/main"


def host_slug(url: str) -> str:
    import re
    from urllib.parse import urlparse

    host = urlparse(url).netloc.lower().replace("www.", "")
    slug = re.sub(r"[^a-z0-9]+", "-", host).strip("-")
    return slug[:56].rstrip("-") or "outlet"


def main() -> None:
    rows = json.loads(JSON.read_text(encoding="utf-8"))
    lines = [
        "# EUV 通发 #2–#71 · P0 截图 GitHub 直链（70）",
        "",
        f"仓库：[carbon-silicon-canonical]({REPO.replace('/blob/main', '')})",
        "",
        "| # | 媒体 | host-slug | 截图 |",
        "| --- | --- | --- | --- |",
    ]
    for row in sorted(rows, key=lambda r: int(r["no"])):
        if int(row["no"]) == 1:
            continue
        slug = host_slug(row["url"])
        base = ROOT / "media-archive" / slug / "EP-anchor-01"
        mp = base / "manifest.json"
        png_key = None
        if mp.is_file():
            data = json.loads(mp.read_text(encoding="utf-8"))
            for k in data.get("files", {}):
                if k.startswith("evidence-snapshots/") and k.endswith(".png"):
                    png_key = k
                    break
        if not png_key:
            lines.append(f"| {row['no']} | {row['media_cn']} | `{slug}` | （manifest 未登记 png） |")
            continue
        rel = f"media-archive/{slug}/EP-anchor-01/{png_key}"
        url = f"{REPO}/{quote(rel, safe='/')}"
        lines.append(f"| {row['no']} | {row['media_cn']} | `{slug}` | [打开]({url}) |")
    lines.extend(["", f"*生成自 `manifest.json` · 路径 `{OUT.relative_to(ROOT).as_posix()}`*", ""])
    OUT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(OUT)


if __name__ == "__main__":
    main()