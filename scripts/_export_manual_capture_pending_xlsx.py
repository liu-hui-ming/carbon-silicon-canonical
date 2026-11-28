#!/usr/bin/env python3
"""Export manual-capture pending rows (state.errors) to per-batch + combined xlsx."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "compass-pedal-audit"
LEGION = Path(r"e:/hundred-crayfish-legion/carbon-silicon-daotong/归档日报")
STAMP = "20261128"

HEADERS = [
    "序号",
    "清单标识",
    "发布批次",
    "清单seq",
    "媒体",
    "稿件标题",
    "链接",
    "预定归档目录",
    "失败原因",
    "采集状态",
    "人工备注",
]

BATCHES = [
    {
        "label": "11-23双清单",
        "jobs": OUT / "media-archive-pub-1123-dual.json",
        "state": OUT / "media-archive-pub-1123-dual.state.json",
        "xlsx": OUT / f"待补采集-11-23双清单-{STAMP}.xlsx",
        "sheet": "11-23待补",
    },
    {
        "label": "11-24-11:00",
        "jobs": OUT / "media-archive-pub-1124-1100.json",
        "state": OUT / "media-archive-pub-1124-1100.state.json",
        "xlsx": OUT / f"待补采集-11-24-1100清单-{STAMP}.xlsx",
        "sheet": "11-24-1100待补",
    },
    {
        "label": "11-24-14:00",
        "jobs": OUT / "media-archive-pub-1124-1400.json",
        "state": OUT / "media-archive-pub-1124-1400.state.json",
        "xlsx": OUT / f"待补采集-11-24-1400双清单-{STAMP}.xlsx",
        "sheet": "11-24-1400待补",
    },
    {
        "label": "1126大总表38家",
        "jobs": OUT / "media-archive-settlement-1126.json",
        "state": OUT / "media-archive-settlement-1126.state.json",
        "xlsx": OUT / f"待补采集-1126大总表-{STAMP}.xlsx",
        "sheet": "1126待补",
    },
]

COMBINED = OUT / f"待补采集-汇总-{STAMP}.xlsx"

ERR_SHORT = re.compile(r"net::ERR_[A-Z0-9_]+|Timeout \d+ms|scrollHeight")


def short_err(msg: str) -> str:
    m = ERR_SHORT.search(msg or "")
    if m:
        return m.group(0)
    return (msg or "").split("\n", 1)[0][:120]


def job_by_url(jobs: list[dict]) -> dict[str, dict]:
    return {j["url"].strip(): j for j in jobs}


def collect_rows(spec: dict) -> list[list]:
    if not spec["jobs"].is_file() or not spec["state"].is_file():
        return []
    jobs = json.loads(spec["jobs"].read_text(encoding="utf-8"))
    state = json.loads(spec["state"].read_text(encoding="utf-8"))
    errors = state.get("errors") or {}
    by_url = job_by_url(jobs)
    rows: list[list] = []
    for url, err in sorted(errors.items(), key=lambda x: by_url.get(x[0], {}).get("seq", 0)):
        job = by_url.get(url, {})
        folder = err.get("folder", "")
        rows.append(
            [
                spec["label"],
                job.get("submit_batch", ""),
                job.get("seq", ""),
                job.get("media", ""),
                job.get("title", ""),
                url,
                f"media_archive/{folder}/" if folder else "",
                short_err(err.get("error", "")),
                "待人工采集",
                "",
            ]
        )
    return rows


def style_header(ws) -> None:
    ws.append(HEADERS)
    for c in range(1, len(HEADERS) + 1):
        cell = ws.cell(row=1, column=c)
        cell.font = Font(bold=True)
        cell.alignment = Alignment(wrap_text=True, vertical="top")


def autosize(ws) -> None:
    for col in ws.columns:
        max_len = 0
        col_letter = col[0].column_letter
        for cell in col:
            if cell.value:
                max_len = max(max_len, min(60, len(str(cell.value))))
        ws.column_dimensions[col_letter].width = max(10, max_len + 2)


def write_workbook(path: Path, sheet: str, data_rows: list[list]) -> int:
    wb = Workbook()
    ws = wb.active
    ws.title = sheet
    style_header(ws)
    for i, body in enumerate(data_rows, start=1):
        ws.append([i, *body])
    autosize(ws)
    wb.save(path)
    return len(data_rows)


def main() -> None:
    all_rows: list[list] = []
    for spec in BATCHES:
        data = collect_rows(spec)
        n = 0
        if spec["xlsx"]:
            n = write_workbook(spec["xlsx"], spec["sheet"], data)
        all_rows.extend(data)
        print(f"{spec['xlsx'].name}: {n} rows")

    wb = Workbook()
    ws = wb.active
    ws.title = "待补汇总"
    style_header(ws)
    for i, body in enumerate(all_rows, start=1):
        ws.append([i, *body])
    autosize(ws)
    wb.save(COMBINED)
    print(f"{COMBINED.name}: {len(all_rows)} rows (combined)")

    if LEGION.is_dir():
        LEGION.mkdir(parents=True, exist_ok=True)
        for spec in BATCHES:
            if spec["xlsx"].is_file():
                shutil.copy2(spec["xlsx"], LEGION / spec["xlsx"].name)
        shutil.copy2(COMBINED, LEGION / COMBINED.name)
        print(f"legion copies -> {LEGION}")


if __name__ == "__main__":
    main()