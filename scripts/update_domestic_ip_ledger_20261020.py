# -*- coding: utf-8 -*-
"""Refresh domestic-IP lists (drop dead links) and write upload stats."""
from __future__ import annotations

import csv
import json
import shutil
from datetime import datetime
from pathlib import Path

import openpyxl
from openpyxl.styles import Alignment, Font

CANON = Path(r"e:\carbon-silicon-canonical")
LEGION = Path(r"e:\hundred-crayfish-legion")
LEDGER = CANON / "media-evidence-ledger" / "recapture-domestic-ip-20261019"

EXCLUDE_HASH8 = frozenset({"d145a260"})  # 创业家头条：源站内容不存在，不再重采
EXCLUDE_REASON = {
    "d145a260": "源站内容不存在；已自清单剔除（无 PNG，仅 CON 文本存证）",
}


def hash8(name: str) -> str:
    return name.rsplit("_", 1)[-1]


def folder_excluded(folder: str) -> bool:
    return hash8(folder) in EXCLUDE_HASH8


def load_ingest():
    p = LEDGER / "INGEST-REPORT-20261020.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    ingested_targets = {r["target"] for r in data.get("ingested", [])}
    errors = data.get("errors", [])
    skipped = data.get("skipped", [])
    # move d145 from errors to excluded in report
    new_errors = [e for e in errors if "d145a260" not in e.get("src", "")]
    excluded = [
        {
            "src": "unknown_创业家（头条号）_d145a260",
            "folder": "20260706_创业家（头条号）_d145a260",
            "reason": EXCLUDE_REASON["d145a260"],
        }
    ]
    data["errors"] = new_errors
    data["excluded"] = excluded
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return ingested_targets, skipped, excluded


def remove_staging_d145():
    for part in ("media_archive_partA", "media_archive_partB"):
        base = LEDGER / part / "media_archive"
        if not base.exists():
            continue
        for d in list(base.iterdir()):
            if d.is_dir() and hash8(d.name) in EXCLUDE_HASH8:
                shutil.rmtree(d, ignore_errors=True)


def filter_csv(path: Path, ingested: set[str], out_path: Path):
    rows_in = list(csv.DictReader(path.read_text(encoding="utf-8-sig").splitlines()))
    header = rows_in[0].keys() if rows_in else []
    fieldnames = list(header)
    if "上传状态" not in fieldnames:
        fieldnames.append("上传状态")
    if "备注" not in fieldnames:
        fieldnames.append("备注")

    kept = []
    removed = 0
    for row in rows_in:
        folder = row.get("归档folder") or row.get("folder") or ""
        url = row.get("表内URL") or row.get("url") or ""
        h = ""
        if folder:
            h = hash8(folder)
        if h in EXCLUDE_HASH8:
            removed += 1
            continue
        if folder and folder in ingested:
            row["上传状态"] = "已上传GitHub"
        elif row.get("国内IP试截") == "已确认OK":
            row["上传状态"] = "已试截确认"
        else:
            row["上传状态"] = row.get("上传状态") or "待重采/未上传"
        kept.append(row)

    with out_path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(kept)
    return len(kept), removed


def write_stats(ingested: set, skipped: list, excluded: list, csv_kept: int, csv_removed: int):
    arch = CANON / "media_archive"
    png = sum(1 for _ in arch.rglob("page_screenshot.png"))
    folders = sum(1 for d in arch.iterdir() if d.is_dir())
    no_png = [d.name for d in arch.iterdir() if d.is_dir() and not (d / "page_screenshot.png").exists()]
    audit = json.loads((arch / "AUDIT-LATEST.json").read_text(encoding="utf-8"))

    staging = 0
    for part in ("media_archive_partA", "media_archive_partB"):
        b = LEDGER / part / "media_archive"
        if b.exists():
            staging += sum(1 for d in b.iterdir() if d.is_dir())

    # domestic batch: 124 original staging; 122 merged; 1 skip; 1 excluded
    uploaded_folders = len(ingested)
    not_uploaded = staging + len(skipped)  # staging left + skipped not in catalog

    md = f"""# 国内 IP 重采 · 上载统计（{datetime.now().strftime("%Y-%m-%d")}）

> 远程分支 `media-evidence-archive` HEAD 以本机 `git rev-parse HEAD` 为准。

## 一、partA/partB → GitHub（本次国内机回传）

| 项 | 数量 | 说明 |
|----|------|------|
| 回传包文件夹（partA+partB，剔除前） | 124 | 含无 PNG 的创业家 staging |
| **已合并并 push 到 `media_archive/`** | **{uploaded_folders}** | 见 `INGEST-REPORT-20261020.json` → `ingested` |
| **未进入主归档（未上传）** | **{len(skipped)}** | `20260902_创业邦首发_005c7b29`：hash8 不在 5470 catalog |
| **已从清单剔除（不再重采）** | **{len(excluded)}** | 创业家 `d145a260`：源站内容不存在 |
| partA/B 现剩 staging 目录 | {staging} | 已删创业家 staging；创业邦包仍在（未 merge） |

## 二、清单 CSV（`同域待重采_CON`）

| 项 | 数量 |
|----|------|
| 更新后行数 | {csv_kept} |
| 本次删除（创业家 d145a260 等） | {csv_removed} |

## 三、全库 `media_archive/`（GitHub 证据分支）

| 项 | 值 |
|----|-----|
| AUDIT `entry_total` | {audit["entry_total"]} |
| `access_ok` / `access_con` | {audit["access_ok"]} / {audit["access_con"]} |
| 磁盘证据目录数 | {folders} |
| `page_screenshot.png` 文件数 | {png} |
| **无 PNG 目录** | {len(no_png)}：{", ".join(no_png[:5])}{"…" if len(no_png)>5 else ""} |

## 四、结论（你要的两句话）

- **国内回传 batch：已上传 GitHub `{uploaded_folders}` 条**（目录级合并 + batch 40 与后续台账 commit）。
- **仍未上传主归档：`{len(skipped)}` 条**（创业邦 845135 / `005c7b29`，仅 staging 在 `partA`，未进 5470 catalog）；**创业家 d145a260 不计入待传，已从清单删除。**

## 五、本地与远程

- 执行本脚本后请 `git status media_archive`：若无未提交改动，则与 `origin/media-evidence-archive` 一致。
- 私表 `2碳硅道体明细表-更新至20261012.xlsx` 仍 **禁公仓**。

"""
    out = LEDGER / "UPLOAD-STATS-DOMESTIC-IP-20261020.md"
    out.write_text(md, encoding="utf-8")
    return out


def main():
    ingested, skipped, excluded = load_ingest()
    remove_staging_d145()

    src_csv = LEGION / "国内IP试截与待重采清单-20261019_同域待重采_CON.csv"
    if not src_csv.exists():
        src_csv = LEDGER / "国内IP试截与待重采清单-20261019_同域待重采_CON.csv"
    out_csv = LEDGER / "国内IP试截与待重采清单-20261020_同域待重采_CON.csv"
    kept, removed = filter_csv(src_csv, ingested, out_csv)
    # mirror to legion
    shutil.copy2(out_csv, LEGION / out_csv.name)

    stats_path = write_stats(ingested, skipped, excluded, kept, removed)
    print("csv", out_csv, "rows", kept, "removed", removed)
    print("stats", stats_path)


if __name__ == "__main__":
    main()
