#!/usr/bin/env python3
"""Export gap lists: two Excel files (1118 + distribution) + optional markdown index."""
from __future__ import annotations

import hashlib
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import openpyxl
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import media_archive_p0_gate as p0gate  # noqa: E402
from media_archive_1118_settlement_batch import XLSX_DEFAULT, load_entries  # noqa: E402

ARCHIVE = ROOT / "media_archive"
OUT_DIR = Path(r"e:/hundred-crayfish-legion/carbon-silicon-daotong/归档日报")
OUT_XLSX_1118 = OUT_DIR / "1118结算-待补P0.xlsx"
OUT_XLSX_DIST = OUT_DIR / "三清单分发-待补P0.xlsx"
OUT_MD = OUT_DIR / "媒体归档-未采集汇总.md"
JOBS_PATH = ROOT / "compass-pedal-audit/media-archive-distribution-1113-1116.json"
STATE_PATH = ROOT / "compass-pedal-audit/media-archive-distribution-1113-1116.state.json"
SETTLE_STATE = ROOT / "compass-pedal-audit/media-archive-1118-settlement.state.json"
BAD = re.compile(r'[\\/:*?"<>|]')
CS = {"satellite-1113": "sat29", "suanli-1116": "suanli", "qiyuan-1116": "qiyuan"}
CMAP = {"satellite-1113": "卫星29", "suanli-1116": "算力", "qiyuan-1116": "启元"}
TZ_CN = timezone(timedelta(hours=8))


def safe(s: str) -> str:
    return BAD.sub("_", s).strip() or "untitled"


def dist_folder(j: dict) -> str:
    h = hashlib.sha256(j["url"].strip().encode()).hexdigest()[:8]
    return f"{j['date_prefix']}_{CS[j['campaign']]}_{j['seq']:04d}_{safe(j['media'])[:24]}_{h}"


def err_short(msg: str, n: int = 120) -> str:
    m = (msg or "").replace("\n", " ")
    for tag in (
        "ERR_BLOCKED_BY_CLIENT",
        "ERR_CONNECTION_TIMED_OUT",
        "ERR_HTTP2_PROTOCOL_ERROR",
        "ERR_CONNECTION_REFUSED",
        "ERR_ABORTED",
        "ERR_EMPTY_RESPONSE",
    ):
        if tag in m:
            return tag
    return m[:n] or ""


def on_disk_status(folder: Path) -> str:
    if not folder.is_dir():
        return "无目录"
    if not list(folder.glob("*.md")):
        return "empty_dir"
    ev = folder / "evidence-snapshots"
    pngs = list(ev.glob("*.png")) if ev.is_dir() else []
    if not pngs:
        return "无PNG"
    mx = max(p.stat().st_size for p in pngs)
    if mx < 50_000:
        return f"PNG过小({mx})"
    if not (folder / "manifest.fragment.json").is_file():
        return "无manifest"
    return "partial"


def collect_1118_gaps() -> tuple[list[dict], int]:
    state = json.loads(SETTLE_STATE.read_text(encoding="utf-8")) if SETTLE_STATE.is_file() else {}
    errors = state.get("errors", {})
    entries = load_entries(XLSX_DEFAULT)
    rows: list[dict] = []
    valid = 0
    for e in entries:
        if p0gate.should_skip_capture(e["url"], e["folder"], ARCHIVE)[0]:
            valid += 1
            continue
        folder = ARCHIVE / e["folder"]
        err_full = str(errors.get(e["url"], {}).get("error", ""))
        rows.append(
            {
                "序号": e["seq"],
                "媒体": e["media"],
                "标题": e["title"],
                "回链": e["url"],
                "归档目录": e["folder"],
                "磁盘状态": on_disk_status(folder),
                "末次错误摘要": err_short(err_full),
                "末次错误全文": err_full[:2000],
            }
        )
    rows.sort(key=lambda r: r["序号"])
    return rows, valid


def collect_dist_gaps() -> tuple[list[dict], int]:
    jobs = json.loads(JOBS_PATH.read_text(encoding="utf-8"))
    state = json.loads(STATE_PATH.read_text(encoding="utf-8")) if STATE_PATH.is_file() else {}
    errors = state.get("errors", {})
    rows: list[dict] = []
    valid = 0
    for j in jobs:
        folder_name = dist_folder(j)
        if p0gate.should_skip_capture(j["url"], folder_name, ARCHIVE)[0]:
            valid += 1
            continue
        folder = ARCHIVE / folder_name
        err_full = str(errors.get(j["url"], {}).get("error", ""))
        rows.append(
            {
                "清单": CMAP.get(j["campaign"], j["campaign"]),
                "campaign": j["campaign"],
                "序号": j["seq"],
                "媒体": j["media"],
                "标题": j.get("title", ""),
                "回链": j["url"],
                "提交批次": j.get("submit_batch", ""),
                "归档目录": folder_name,
                "磁盘状态": on_disk_status(folder),
                "末次错误摘要": err_short(err_full),
                "末次错误全文": err_full[:2000],
            }
        )
    rows.sort(key=lambda r: (r["campaign"], r["序号"]))
    return rows, valid


def write_sheet(wb: openpyxl.Workbook, title: str, headers: list[str], rows: list[dict], meta: str) -> None:
    ws = wb.active
    ws.title = title[:31]
    ws["A1"] = meta
    ws["A1"].font = Font(bold=True)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=max(len(headers), 1))
    for col, h in enumerate(headers, start=1):
        cell = ws.cell(row=3, column=col, value=h)
        cell.font = Font(bold=True)
    for ri, row in enumerate(rows, start=4):
        for ci, h in enumerate(headers, start=1):
            ws.cell(row=ri, column=ci, value=row.get(h, ""))
    for col in range(1, len(headers) + 1):
        letter = get_column_letter(col)
        max_len = max(len(headers[col - 1]), 10)
        for r in range(4, 4 + len(rows)):
            v = ws.cell(row=r, column=col).value
            if v is not None:
                max_len = min(max(max_len, len(str(v))), 80)
        ws.column_dimensions[letter].width = max_len + 2


def main() -> int:
    stamp = datetime.now(TZ_CN).strftime("%Y-%m-%d %H:%M")
    rows1118, v1118 = collect_1118_gaps()
    rows_dist, v_dist = collect_dist_gaps()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    h1118 = ["序号", "媒体", "标题", "回链", "归档目录", "磁盘状态", "末次错误摘要", "末次错误全文"]
    wb1 = openpyxl.Workbook()
    write_sheet(
        wb1,
        "待补38",
        h1118,
        rows1118,
        f"1118结算大总表207篇 · 有效P0 {v1118}/207 · 待补 {len(rows1118)} · 盘检 {stamp} · 口径 md+manifest+PNG≥50KB",
    )
    wb1.save(OUT_XLSX_1118)

    hdist = [
        "清单",
        "序号",
        "媒体",
        "标题",
        "回链",
        "提交批次",
        "归档目录",
        "磁盘状态",
        "末次错误摘要",
        "末次错误全文",
    ]
    wb2 = openpyxl.Workbook()
    write_sheet(
        wb2,
        "待补20",
        hdist,
        rows_dist,
        f"三清单分发75URL · 有效P0 {v_dist}/75 · 待补 {len(rows_dist)} · 盘检 {stamp}",
    )
    wb2.save(OUT_XLSX_DIST)

    OUT_MD.write_text(
        "\n".join(
            [
                f"# 媒体归档 · 未采集完汇总 · {stamp}",
                "",
                "Excel 分表（主交付）：",
                "",
                f"- 表一：[1118结算-待补P0.xlsx](./1118结算-待补P0.xlsx)（{len(rows1118)} 行 · 有效 {v1118}/207）",
                f"- 表二：[三清单分发-待补P0.xlsx](./三清单分发-待补P0.xlsx)（{len(rows_dist)} 行 · 有效 {v_dist}/75）",
                "",
                f"*合计待补 {len(rows1118) + len(rows_dist)} · 生成脚本 `carbon-silicon-canonical/scripts/_export_gap_tables.py`*",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    print("wrote", OUT_XLSX_1118)
    print("wrote", OUT_XLSX_DIST)
    print("wrote", OUT_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())