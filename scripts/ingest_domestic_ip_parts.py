# -*- coding: utf-8 -*-
"""Merge media_archive_partA/B (domestic IP captures) into media_archive + rebuild ledgers."""
from __future__ import annotations

import importlib.util
import json
import re
import shutil
import stat
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "media_archive"
PARTS_ROOT = (
    ROOT
    / "media-evidence-ledger"
    / "recapture-domestic-ip-20261019"
)
CATALOG = Path(r"e:\hundred-crayfish-legion\_tmp_media_evidence_catalog.json")
STATE = ROOT / "_tmp_media_evidence_state_dt5322.json"

spec = importlib.util.spec_from_file_location(
    "batch", ROOT / "scripts" / "media_evidence_archive_batch.py"
)
batch = importlib.util.module_from_spec(spec)
spec.loader.exec_module(batch)

HEADER_END = re.compile(r"^链接失效：", re.M)


def hash8_from_folder(name: str) -> str:
    return name.rsplit("_", 1)[-1]


def build_hash_index(entries: list[dict]) -> dict[str, dict]:
    idx: dict[str, dict] = {}
    for e in entries:
        folder = e.get("folder") or ""
        if folder:
            idx[hash8_from_folder(folder)] = e
    return idx


def parse_article_source(path: Path) -> dict:
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    meta = {}
    for line in text.splitlines()[:20]:
        if "：" in line:
            k, v = line.split("：", 1)
            meta[k.strip()] = v.strip()
    body = ""
    m = HEADER_END.search(text)
    if m:
        body = text[m.end() :].lstrip("\n")
    else:
        parts = text.split("\n\n", 1)
        body = parts[1] if len(parts) > 1 else ""
    meta["_body"] = body
    meta["_body_len"] = len(body.strip())
    return meta


def classify_from_upload(meta: dict, entry: dict) -> tuple[str, str]:
    dead = meta.get("链接失效", "") == "是"
    if dead:
        return "CON", "源链接已失效（404/资源不存在），以归档本地存证材料为依据"
    blen = meta.get("_body_len", 0)
    title = meta.get("标题") or meta.get("页面标题") or entry.get("title", "")
    if blen >= 200 or (title and title[:8] in meta.get("_body", "")):
        note = ""
        cap = meta.get("截图标准", "")
        if "非 P0" in cap or "Mac" in cap:
            note = "国内IP人工重采（Mac/无头侦察PNG，待P0复核）"
        return "OK", note
    if blen >= 80:
        return "CON", "正文过短或不可读"
    return "CON", "正文过短或不可读"


def chmod_tree(folder: Path):
    for f in folder.rglob("*"):
        if f.is_file():
            try:
                f.chmod(stat.S_IWRITE | stat.S_IREAD)
            except OSError:
                pass


def ingest_folder(src: Path, entry: dict, target_name: str) -> dict:
    dst = ARCHIVE / target_name
    dst.mkdir(parents=True, exist_ok=True)
    chmod_tree(dst)

    png = src / "page_screenshot.png"
    if not png.exists():
        raise FileNotFoundError(f"no page_screenshot.png in {src}")

    shutil.copy2(png, dst / "page_screenshot.png")

    art_src = src / "article_source.txt"
    art_dst = dst / "article_source.txt"
    if art_src.exists():
        shutil.copy2(art_src, dst / "article_source.txt")
    elif (src / "dom.html").exists():
        # minimal stub if only dom+png
        url = (src / "url.txt").read_text(encoding="utf-8").strip() if (src / "url.txt").exists() else entry["url"]
        art_dst.write_text(
            f"标题：{entry.get('title', '')}\n"
            f"媒体：{entry.get('media', '')}\n"
            f"URL：{url}\n"
            f"取证系统时间：{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}\n"
            f"截图标准：国内IP人工重采\n\n",
            encoding="utf-8",
        )

    dom = src / "dom.html"
    if dom.exists():
        shutil.copy2(dom, dst / "evidence_mirror.html")

    meta = parse_article_source(art_dst)
    url = meta.get("URL") or entry["url"]
    if (src / "url.txt").exists():
        url_from_txt = (src / "url.txt").read_text(encoding="utf-8").strip()
        if url_from_txt.startswith("http"):
            url = url_from_txt

    access, con_note = classify_from_upload(meta, entry)
    captured_at = meta.get("取证系统时间") or datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    files = {}
    png_path = dst / "page_screenshot.png"
    files["page_screenshot.png"] = {
        "sha256": batch.sha256_file(png_path),
        "bytes": png_path.stat().st_size,
    }
    txt_bytes = art_dst.read_bytes()
    files["article_source.txt"] = {
        "sha256": batch.sha256_bytes(txt_bytes),
        "bytes": len(txt_bytes),
    }
    frag_meta = {
        **entry,
        "url": url,
        "title": meta.get("标题") or entry.get("title", ""),
        "access": access,
        "con_note": con_note,
        "captured_at": captured_at,
        "capture_standard": "P0-four-elements-v2",
        "ingest_source": str(src.relative_to(PARTS_ROOT)),
    }
    batch.write_fragment(dst, frag_meta, files)
    return {
        "url": url,
        "folder": target_name,
        "access": access,
        "con_note": con_note,
        "captured_at": captured_at,
    }


def main():
    if not CATALOG.exists():
        raise SystemExit(f"missing catalog: {CATALOG}")
    catalog_entries = json.loads(CATALOG.read_text(encoding="utf-8"))["entries"]
    by_hash = build_hash_index(catalog_entries)

    if STATE.exists():
        st = json.loads(STATE.read_text(encoding="utf-8"))
    else:
        st = {"done": {}, "errors": []}

    report = {"ingested": [], "skipped": [], "errors": []}

    for part in ("media_archive_partA", "media_archive_partB"):
        base = PARTS_ROOT / part / "media_archive"
        if not base.exists():
            continue
        for src in sorted(base.iterdir()):
            if not src.is_dir():
                continue
            h8 = hash8_from_folder(src.name)
            entry = by_hash.get(h8)
            if not entry:
                report["skipped"].append({"src": src.name, "reason": "hash8 not in catalog"})
                continue
            target = entry["folder"]
            try:
                rec = ingest_folder(src, entry, target)
                st["done"][rec["url"]] = rec
                report["ingested"].append({"src": src.name, "target": target, **rec})
                print("OK", src.name, "->", target, rec["access"])
            except Exception as exc:
                report["errors"].append({"src": src.name, "error": str(exc)})
                print("ERR", src.name, exc)

    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    batch.rebuild_total(catalog_entries, st)

    out = PARTS_ROOT / "INGEST-REPORT-20261020.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("ingested", len(report["ingested"]), "skipped", len(report["skipped"]), "errors", len(report["errors"]))
    print("report", out)


if __name__ == "__main__":
    main()
