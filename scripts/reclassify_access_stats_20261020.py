# -*- coding: utf-8 -*-
"""Reclassify OK vs CON; export 打不开 URL stats (2026-10-20)."""
from __future__ import annotations

import csv
import importlib.util
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "media_archive"
CATALOG = Path(r"e:\hundred-crayfish-legion\_tmp_media_evidence_catalog.json")
INGEST_REPORT = (
    ROOT
    / "media-evidence-ledger/recapture-domestic-ip-20261019/INGEST-REPORT-20261020.json"
)
STATE = ROOT / "_tmp_media_evidence_state_dt5322.json"
STATS_DIR = ROOT / "media-evidence-ledger/stats"

MIN_PNG_OK = 80_000  # bytes; normal full-screen capture
ERROR_TITLE = re.compile(r"404|不存在|Not Found|错误页", re.I)
DEAD_NOTE = re.compile(r"404|失效|不存在|410", re.I)
HTTP0_NOTE = re.compile(r"HTTP\s*0\b", re.I)
HTTP_BLOCK = re.compile(r"HTTP\s*(403|502|503|521|567)\b", re.I)

EXCLUDE_DEAD = {"d145a260"}  # 创业家：源站无内容，无 PNG


def load_batch():
    spec = importlib.util.spec_from_file_location(
        "batch", ROOT / "scripts/media_evidence_archive_batch.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def parse_article(folder: Path) -> dict:
    p = folder / "article_source.txt"
    if not p.exists():
        return {"_body": "", "_body_len": 0}
    text = p.read_text(encoding="utf-8", errors="replace")
    meta: dict = {"_raw": text}
    body_start = 0
    for i, line in enumerate(text.splitlines()):
        if line.strip() == "" and i > 5:
            body_start = i + 1
            break
    body = "\n".join(text.splitlines()[body_start:]).strip()
    meta["_body"] = body
    meta["_body_len"] = len(body)
    for line in text.splitlines()[:25]:
        if "：" in line:
            k, v = line.split("：", 1)
            meta[k.strip()] = v.strip()
    return meta


def classify(entry: dict, folder: Path, domestic_targets: set[str]) -> tuple[str, str, str]:
    """Returns access, con_note, unreachable_bucket (empty if OK)."""
    name = folder.name
    h8 = name.rsplit("_", 1)[-1]
    png = folder / "page_screenshot.png"
    meta = parse_article(folder)
    title = meta.get("标题") or meta.get("页面标题") or ""
    link_dead = meta.get("链接失效") == "是"

    if h8 in EXCLUDE_DEAD or (not png.exists() and link_dead):
        return (
            "CON",
            "源链接已失效（404/资源不存在），以归档本地存证材料为依据",
            "源站无内容/无PNG",
        )

    if not png.exists():
        old_note = ""
        frag = folder / "manifest.fragment.json"
        if frag.exists():
            old_note = json.loads(frag.read_text(encoding="utf-8")).get("con_note", "")
        if HTTP0_NOTE.search(old_note):
            return "CON", old_note or "HTTP 0", "HTTP0_不可达"
        if DEAD_NOTE.search(old_note):
            return "CON", old_note, "404_失效"
        return "CON", old_note or "缺少 page_screenshot.png", "无截图"

    png_bytes = png.stat().st_size
    is_domestic = name in domestic_targets

    # Error-only page (e.g. toutiao 404 shell) — still 打不开
    if ERROR_TITLE.search(title) and meta.get("_body_len", 0) < 200:
        if "内容不存在" in meta.get("_body", "") or "404" in title:
            return (
                "CON",
                "源链接已失效（404/资源不存在），以归档本地存证材料为依据",
                "404_错误页截图",
            )

    # Normal capture: PNG present + substantive OR domestic recapture
    substantive = meta.get("_body_len", 0) >= 200 or (
        title and title[:6] in meta.get("_body", "")
    )
    large_png = png_bytes >= MIN_PNG_OK
    medium_png = png_bytes >= 45_000

    if is_domestic and medium_png and not link_dead:
        note = "国内IP重采；截图已覆盖" if not substantive else ""
        return "OK", note, ""

    if large_png and (substantive or is_domestic):
        return "OK", "", ""

    if large_png and not ERROR_TITLE.search(title):
        return "OK", "", ""

    # PNG but weak — check historical note
    frag_note = ""
    fp = folder / "manifest.fragment.json"
    if fp.exists():
        frag_note = json.loads(fp.read_text(encoding="utf-8")).get("con_note", "")

    if HTTP0_NOTE.search(frag_note) and not is_domestic:
        return "CON", frag_note, "HTTP0_不可达"
    if DEAD_NOTE.search(frag_note):
        return "CON", frag_note, "404_失效"
    if HTTP_BLOCK.search(frag_note):
        return "CON", frag_note, "HTTP拦截"
    if meta.get("_body_len", 0) < 120 and not large_png:
        return "CON", frag_note or "正文过短或不可读", "正文过短"
    if medium_png:
        return "OK", "截图存证；正文提取偏短", ""

    return "CON", frag_note or "正文过短或不可读", "其他CON"


def main():
    batch = load_batch()
    entries = json.loads(CATALOG.read_text(encoding="utf-8"))["entries"]
    domestic_targets: set[str] = set()
    if INGEST_REPORT.exists():
        rep = json.loads(INGEST_REPORT.read_text(encoding="utf-8"))
        domestic_targets = {r["target"] for r in rep.get("ingested", [])}

    done: dict = {}
    unreachable_rows: list[dict] = []
    bucket_counter: Counter = Counter()
    access_counter: Counter = Counter()

    for entry in entries:
        folder = ARCHIVE / entry["folder"]
        access, con_note, bucket = classify(entry, folder, domestic_targets)
        access_counter[access] += 1
        if access == "CON":
            bucket_counter[bucket or "其他CON"] += 1
            unreachable_rows.append(
                {
                    "folder": entry["folder"],
                    "url": entry["url"],
                    "media": entry.get("media", ""),
                    "con_note": con_note,
                    "打不开分类": bucket or "其他CON",
                    "has_png": (folder / "page_screenshot.png").exists(),
                }
            )

        captured_at = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        fp = folder / "manifest.fragment.json"
        if fp.exists():
            frag = json.loads(fp.read_text(encoding="utf-8"))
            captured_at = frag.get("captured_at", captured_at)
            frag["access"] = access
            frag["con_note"] = con_note
            files = frag.get("files", {})
            if (folder / "page_screenshot.png").exists():
                p = folder / "page_screenshot.png"
                files["page_screenshot.png"] = {
                    "sha256": batch.sha256_file(p),
                    "bytes": p.stat().st_size,
                }
            if (folder / "article_source.txt").exists():
                t = folder / "article_source.txt"
                files["article_source.txt"] = {
                    "sha256": batch.sha256_bytes(t.read_bytes()),
                    "bytes": t.stat().st_size,
                }
            frag["files"] = files
            raw = (json.dumps(frag, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            fp.write_bytes(raw)
            files["manifest.fragment.json"] = {
                "sha256": batch.sha256_bytes(raw),
                "bytes": len(raw),
            }

        done[entry["url"]] = {
            "folder": entry["folder"],
            "access": access,
            "con_note": con_note,
            "captured_at": captured_at,
        }

    st = {"done": done, "errors": []}
    STATE.write_text(json.dumps(st, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    batch.rebuild_total(entries, st)

    audit = json.loads((ARCHIVE / "AUDIT-LATEST.json").read_text(encoding="utf-8"))
    # fix success_archived display in audit if drift
    audit["success_archived"] = len(entries)
    audit["entry_total"] = len(entries)
    (ARCHIVE / "AUDIT-LATEST.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    STATS_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = STATS_DIR / "URL-UNREACHABLE-20261020.csv"
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "folder",
                "url",
                "media",
                "打不开分类",
                "con_note",
                "has_png",
            ],
        )
        w.writeheader()
        w.writerows(sorted(unreachable_rows, key=lambda r: r["打不开分类"]))

    md = f"""# ACCESS 重算统计（2026-10-20）

## 口径

- **OK**：`page_screenshot.png` 为正常体积取证（≥{MIN_PNG_OK//1000}KB 或国内重采 ≥45KB），且非「404/内容不存在」错误页。
- **CON / 打不开**：无 PNG、HTTP0、404/失效、403/502 等；见 **`URL-UNREACHABLE-20261020.csv`**。
- **国内 IP 回传** {len(domestic_targets)} 条：有中等以上 PNG 且无「链接失效：是」→ 优先 **OK**。

## 汇总

| 项 | 数量 |
|----|------|
| 总条目 | {len(entries)} |
| **OK** | **{access_counter['OK']}** |
| **CON（打不开/异常）** | **{access_counter['CON']}** |

## CON 按「打不开」分类

| 分类 | 条数 |
|------|------|
"""
    for k, v in bucket_counter.most_common():
        md += f"| {k} | {v} |\n"

    md += f"""
## AUDIT（重算后）

- `access_ok`: {audit.get('access_ok')}
- `access_con`: {audit.get('access_con')}
- `pending`: {audit.get('pending', 0)}

## 文件

- `{csv_path.relative_to(ROOT).as_posix()}`
"""
    md_path = STATS_DIR / "ACCESS-RECLASS-20261020.md"
    md_path.write_text(md, encoding="utf-8")

    print("OK", access_counter["OK"], "CON", access_counter["CON"])
    print("csv", csv_path)
    print("md", md_path)


if __name__ == "__main__":
    main()
