# -*- coding: utf-8 -*-
"""Local web dashboard for DT5322 / media_archive P0 screenshot progress."""
from __future__ import annotations

import json
import os
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "media_archive"
AUDIT = ARCHIVE / "AUDIT-LATEST.json"
STATE_DT5322 = ROOT / "_tmp_media_evidence_state_dt5322.json"
CATALOG = Path(r"e:\hundred-crayfish-legion\_tmp_media_evidence_catalog.json")
ENTRIES_DT5322 = Path(r"e:\hundred-crayfish-legion\_tmp_dt5322_report_entries.json")
PROBE = ROOT / "_tmp_dt5322_url_probe.json"

DEFAULT_PORT = 8765

HTML_PAGE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>媒体首发证据链 · P0 截图进度</title>
  <style>
    :root { --bg:#0f1419; --card:#1a2332; --text:#e7ecf3; --muted:#8b9cb3;
      --ok:#3dd68c; --warn:#f5a524; --con:#f97066; --accent:#6ea8fe; }
    body { font-family: system-ui, sans-serif; background: var(--bg); color: var(--text);
      margin: 0; padding: 24px 20px 48px; line-height: 1.5; }
    h1 { font-size: 1.35rem; margin: 0 0 6px; }
    .sub { color: var(--muted); font-size: 0.9rem; margin-bottom: 24px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 14px; margin-bottom: 24px; }
    .card { background: var(--card); border-radius: 10px; padding: 16px 18px; border: 1px solid #2a3548; }
    .card .label { color: var(--muted); font-size: 0.78rem; }
    .card .value { font-size: 1.75rem; font-weight: 700; margin-top: 4px; font-variant-numeric: tabular-nums; }
    .bar-wrap { background: #2a3548; border-radius: 999px; height: 14px; overflow: hidden; margin: 8px 0 4px; }
    .bar { height: 100%; background: linear-gradient(90deg, var(--accent), var(--ok)); transition: width 0.4s; }
    .pct { font-size: 0.85rem; color: var(--muted); }
    table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
    th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid #2a3548; }
    th { color: var(--muted); }
    td a { color: var(--accent); word-break: break-all; }
    .tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 600; }
    .tag-ok { background: rgba(61,214,140,0.15); color: var(--ok); }
    .tag-con { background: rgba(249,112,102,0.15); color: var(--con); }
    .refresh { color: var(--muted); font-size: 0.8rem; margin-top: 20px; }
  </style>
</head>
<body>
  <h1>媒体首发证据链 · P0 截图进度</h1>
  <p class="sub">分支 media-evidence-archive · 本地看板</p>
  <div class="grid" id="stats"></div>
  <div class="card" style="margin-bottom:20px">
    <div class="label">全库完成度</div>
    <div class="bar-wrap"><div class="bar" id="bar-all"></div></div>
    <div class="pct" id="pct-all"></div>
  </div>
  <div class="card" style="margin-bottom:24px">
    <div class="label">DT5322 批次</div>
    <div class="bar-wrap"><div class="bar" id="bar-dt"></div></div>
    <div class="pct" id="pct-dt"></div>
  </div>
  <div class="card">
    <div class="label">最近取证</div>
    <table><thead><tr><th>时间</th><th>状态</th><th>媒体</th><th>链接</th></tr></thead>
    <tbody id="recent"></tbody></table>
  </div>
  <p class="refresh">每 10 秒刷新 · 更新：<span id="updated">—</span></p>
  <script>
    const REFRESH_MS = 10000;
    function fmt(n) { return n == null || isNaN(n) ? "—" : Number(n).toLocaleString("zh-CN"); }
    function pct(d,t) { return t ? Math.min(100, d/t*100) : 0; }
    function tag(a) {
      const c = a==="OK"?"tag-ok":a==="CON"?"tag-con":"tag-ok";
      return `<span class="tag ${c}">${a||"?"}</span>`;
    }
    async function load() {
      const d = await (await fetch("/api/progress?"+Date.now())).json();
      const s = d.stats;
      document.getElementById("stats").innerHTML = [
        ["全库应归档",s.catalog_total],["已归档",s.catalog_archived],["待 P0",s.catalog_pending],
        ["OK",s.catalog_ok],["CON",s.catalog_con],["DT5322 已截",s.dt5322_done],
        ["DT5322 总量",s.dt5322_total],["报错条数",s.dt5322_errors],
      ].map(([l,v])=>`<div class="card"><div class="label">${l}</div><div class="value">${fmt(v)}</div></div>`).join("");
      const pA = pct(s.catalog_archived,s.catalog_total);
      document.getElementById("bar-all").style.width=pA+"%";
      document.getElementById("pct-all").textContent=`${fmt(s.catalog_archived)} / ${fmt(s.catalog_total)} (${pA.toFixed(2)}%)`;
      const pD = pct(s.dt5322_done,s.dt5322_total);
      document.getElementById("bar-dt").style.width=pD+"%";
      document.getElementById("pct-dt").textContent=`${fmt(s.dt5322_done)} / ${fmt(s.dt5322_total)} (${pD.toFixed(2)}%)`;
      document.getElementById("recent").innerHTML = (d.recent||[]).map(r=>
        `<tr><td>${r.captured_at||"—"}</td><td>${tag(r.access)}</td><td>${r.media||"—"}</td>
        <td><a href="${r.url}" target="_blank">${r.url}</a></td></tr>`).join("") || "<tr><td colspan=4>暂无</td></tr>";
      document.getElementById("updated").textContent = d.generated_at;
    }
    load(); setInterval(load, REFRESH_MS);
  </script>
</body>
</html>
"""


def load_json(path: Path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def build_progress_payload() -> dict:
    audit = load_json(AUDIT) or {}
    state = load_json(STATE_DT5322) or {"done": {}, "errors": []}
    entries = load_json(ENTRIES_DT5322) or {}
    probe = load_json(PROBE) or {}

    dt_total = entries.get("count") or len(entries.get("entries") or []) or 5294
    done_map = state.get("done") or {}
    url_meta = {e["url"]: e for e in (entries.get("entries") or [])}
    recent = sorted(
        [
            {
                "url": u,
                "access": rec.get("access", ""),
                "captured_at": rec.get("captured_at", ""),
                "media": url_meta.get(u, {}).get("media", ""),
            }
            for u, rec in done_map.items()
        ],
        key=lambda x: x.get("captured_at") or "",
        reverse=True,
    )[:30]

    stats = {
        "catalog_total": audit.get("entry_total"),
        "catalog_archived": audit.get("success_archived"),
        "catalog_pending": audit.get("pending"),
        "catalog_ok": audit.get("access_ok"),
        "catalog_con": audit.get("access_con"),
        "dt5322_done": len(done_map),
        "dt5322_total": dt_total,
        "dt5322_errors": len(state.get("errors") or []),
        "probe_ok": probe.get("access_ok"),
        "probe_con": probe.get("access_con"),
    }
    return {"generated_at": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), "stats": stats, "recent": recent}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        if self.path.split("?", 1)[0] in ("/", "/index.html"):
            body = HTML_PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if self.path.split("?", 1)[0] == "/api/progress":
            body = json.dumps(build_progress_payload(), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_error(404)


def main():
    port = int(os.environ.get("MEDIA_PROGRESS_PORT", DEFAULT_PORT))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"Progress dashboard: http://127.0.0.1:{port}/", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
