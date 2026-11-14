#!/usr/bin/env python3
from pathlib import Path
import json
import openpyxl

ROOT = Path(r"E:/hundred-crayfish-legion")
xlsx = list(ROOT.glob("*美联社*反馈*.xlsx"))[0]
wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
ws = wb["Report"]
rows = []
for row in ws.iter_rows(values_only=True):
    rows.append(row)
wb.close()

# Find header row with URL column
start = 0
for i, row in enumerate(rows):
    if row and isinstance(row[0], int) and row[5] and str(row[5]).startswith("http"):
        start = i
        break

outlets = []
for row in rows[start:]:
    if not row[0] or not row[5]:
        continue
    url = str(row[5]).strip()
    if not url.startswith("http"):
        continue
    outlets.append(
        {
            "no": row[0],
            "date": str(row[1])[:10] if row[1] else None,
            "media_cn": row[2],
            "media_en": row[3],
            "headline": row[4],
            "url": url,
            "lang": row[6],
            "type": row[7],
            "cat": row[8],
        }
    )

out = Path(__file__).resolve().parents[1] / "compass-pedal-audit/euv-ap-distribution-71.json"
out.write_text(json.dumps(outlets, ensure_ascii=False, indent=2), encoding="utf-8")
print(len(outlets))