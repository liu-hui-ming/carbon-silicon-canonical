# -*- coding: utf-8 -*-
"""Move manual PNG/TIFF into official folders; stitch to page_screenshot.png."""
import importlib.util
import json
import stat
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "media_archive"
MANUAL = ARCHIVE / "MANUAL-UPLOAD-CON9"
ENTRIES = Path(r"e:\hundred-crayfish-legion\_tmp_report_entries.json")
STATE = ROOT / "_tmp_media_evidence_state.json"

spec = importlib.util.spec_from_file_location(
    "batch", ROOT / "scripts" / "media_evidence_archive_batch.py"
)
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)

INGEST = [
    ("中国经济新闻网", "十维标尺", "10559817"),
    ("中国经济新闻网", "100质询", "10560465"),
    ("中国经济新闻网", "中层拟合", "10560128"),
    ("中国经济新闻网", "紫薇几何", "10560349"),
    ("中国经济新闻网", "五级梯队", "10560350"),
    ("中国经济新闻网", "归零稳态", "10560133"),
    ("人民日报社", "十维标尺", "46650"),
    ("人民日报社", "050", "47540"),
]

IMG_EXT = {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".bmp"}


def resolve_manual_dir(group: str, sub: str) -> Path:
    base = MANUAL / group
    if sub == "050":
        for d in base.iterdir():
            if d.is_dir() and "050" in d.name:
                return d
    for d in base.iterdir():
        if d.is_dir() and sub in d.name:
            return d
    return base / sub


def find_entry(entries, needle: str):
    for e in entries:
        if needle in e["url"]:
            return e
    raise KeyError(needle)


def chmod_writable(p: Path):
    if p.exists():
        try:
            p.chmod(stat.S_IWRITE | stat.S_IREAD)
        except OSError:
            pass


def collect_images(src_dir: Path):
    return sorted(
        p for p in src_dir.iterdir() if p.is_file() and p.suffix.lower() in IMG_EXT
    )


def stitch_images(paths, out: Path):
    panels = []
    for p in paths:
        im = Image.open(p).convert("RGB")
        panels.append(im)
    w = max(im.width for im in panels)
    h = sum(im.height for im in panels)
    canvas = Image.new("RGB", (w, h), (255, 255, 255))
    y = 0
    for im in panels:
        canvas.paste(im, (0, y))
        y += im.height
    chmod_writable(out)
    canvas.save(out, format="PNG", optimize=True)


def main():
    entries = json.loads(ENTRIES.read_text(encoding="utf-8"))["entries"]
    st = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {"done": {}, "errors": []}

    for group, sub, needle in INGEST:
        src_dir = resolve_manual_dir(group, sub)
        entry = find_entry(entries, needle)
        folder = ARCHIVE / entry["folder"]
        imgs = collect_images(src_dir)
        if not imgs:
            print("skip no images", folder.name, flush=True)
            continue
        png = folder / "page_screenshot.png"
        stitch_images(imgs, png)
        files = {}
        frag_path = folder / "manifest.fragment.json"
        if frag_path.exists():
            files = dict(json.loads(frag_path.read_text(encoding="utf-8")).get("files", {}))
        txt_path = folder / "article_source.txt"
        html_path = folder / "evidence_manual_save.html"
        files["page_screenshot.png"] = {
            "sha256": batch.sha256_file(png),
            "bytes": png.stat().st_size,
        }
        if txt_path.exists():
            files["article_source.txt"] = {
                "sha256": batch.sha256_file(txt_path),
                "bytes": txt_path.stat().st_size,
            }
        if html_path.exists():
            files["evidence_manual_save.html"] = {
                "sha256": batch.sha256_file(html_path),
                "bytes": html_path.stat().st_size,
            }
        prev = json.loads(frag_path.read_text(encoding="utf-8")) if frag_path.exists() else {}
        meta = {
            **entry,
            "access": prev.get("access", "OK"),
            "con_note": prev.get("con_note", ""),
            "captured_at": prev.get("captured_at", ""),
            "capture_source": "user_manual_screenshot_stitch",
        }
        batch.write_fragment(folder, meta, files)
        print("ok", folder.name, len(imgs), "images", flush=True)

    batch.rebuild_total(entries, st)


if __name__ == "__main__":
    main()
