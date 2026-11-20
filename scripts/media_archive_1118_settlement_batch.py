#!/usr/bin/env python3
"""
1118结算 · 大总表 380 篇 · P0 四要素批量归档 → media_archive/<folder>/
断点：compass-pedal-audit/media-archive-1118-settlement.state.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import openpyxl
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import media_archive_p0_gate as p0gate  # noqa: E402
import media_evidence_archive_batch as snap  # noqa: E402

TZ_CN = timezone(timedelta(hours=8))
XLSX_DEFAULT = Path(r"e:/hundred-crayfish-legion/1118结算.xlsx")
STATE_PATH = ROOT / "compass-pedal-audit/media-archive-1118-settlement.state.json"
INDEX_PATH = ROOT / "media-archive/INDEX.md"
AUDIT_LOG = ROOT / "compass-pedal-audit/media-archive-20261118-settlement.log"
ARCHIVE_ROOT = ROOT / "media_archive"
DATE_ROW = "2026-11-18"
ANCHOR = "EP-anchor-01"

BAD_FILENAME = re.compile(r'[\\/:*?"<>|]')


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_name(name: str) -> str:
    return BAD_FILENAME.sub("_", name).strip() or "untitled"


def load_entries(xlsx: Path) -> list[dict]:
    wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
    ws = wb["大总表"]
    it = ws.iter_rows(values_only=True)
    next(it)
    next(it)
    out: list[dict] = []
    for row in it:
        if not row or row[0] is None:
            continue
        seq_raw = str(row[0]).strip().rstrip("、")
        if not seq_raw.isdigit():
            continue
        seq = int(seq_raw)
        submit_batch = row[1]
        if submit_batch is not None and not isinstance(submit_batch, str):
            submit_batch = str(submit_batch)
        title = (row[2] or "").strip() if isinstance(row[2], str) else str(row[2] or "").strip()
        media = (row[3] or "").strip() if isinstance(row[3], str) else str(row[3] or "").strip()
        url = (row[4] or "").strip() if isinstance(row[4], str) else str(row[4] or "").strip()
        if not url or not title:
            continue
        url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[:8]
        media_slug = safe_name(media)[:24]
        folder = f"20261118_{seq:04d}_{media_slug}_{url_hash}"
        stem = f"{title}_{media}"
        out.append(
            {
                "seq": seq,
                "title": title,
                "media": media,
                "url": url,
                "submit_batch": (submit_batch or "").strip() if submit_batch else None,
                "folder": folder,
                "md_name": safe_name(stem) + ".md",
                "png_name": safe_name(stem) + "_snapshot.png",
            }
        )
    wb.close()
    return out


MIN_PNG_BYTES = 50_000


def folder_has_valid_p0(job: dict) -> bool:
    """Skip when canonical folder or same URL already has valid P0."""
    skip, _ = p0gate.should_skip_capture(job["url"], job["folder"], ARCHIVE_ROOT)
    return skip


def load_state() -> dict:
    if STATE_PATH.is_file():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"done_urls": {}, "errors": {}}


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fresh_reset() -> None:
    """Remove prior 1118 settlement artifacts for a clean rerun."""
    if STATE_PATH.is_file():
        STATE_PATH.unlink()
    removed = 0
    if ARCHIVE_ROOT.is_dir():
        for d in ARCHIVE_ROOT.iterdir():
            if d.is_dir() and d.name.startswith("20261118_"):
                shutil.rmtree(d, ignore_errors=True)
                removed += 1
    if INDEX_PATH.is_file():
        lines = INDEX_PATH.read_text(encoding="utf-8").splitlines()
        kept = [
            ln
            for ln in lines
            if "media_archive/20261118_" not in ln and "media_archive\\20261118_" not in ln
        ]
        INDEX_PATH.write_text("\n".join(kept).rstrip() + "\n", encoding="utf-8", newline="\n")
    stamp = datetime.now(TZ_CN).strftime("%Y-%m-%dT%H:%M+08:00")
    AUDIT_LOG.write_text(
        f"{stamp} 1118 settlement FRESH reset removed_dirs={removed}\n",
        encoding="utf-8",
        newline="\n",
    )


def extract_body(page) -> tuple[str, str]:
    """Return (body_text, pub_date)."""
    pub = ""
    for sel in (
        "time[datetime]",
        ".time",
        ".date",
        "#pubtime",
        ".article-time",
        ".source-time",
    ):
        try:
            el = page.query_selector(sel)
            if el:
                pub = (el.get_attribute("datetime") or el.inner_text() or "").strip()[:64]
                if pub:
                    break
        except Exception:
            pass
    text = page.evaluate(
        """() => {
        const article = document.querySelector('article')
          || document.querySelector('.article-content')
          || document.querySelector('.content')
          || document.querySelector('#content')
          || document.querySelector('.post-content')
          || document.querySelector('main');
        const raw = article ? article.innerText : document.body.innerText;
        return (raw || '').replace(/\\s+/g, ' ').trim();
    }"""
    )
    text = re.sub(r"\n{3,}", "\n\n", text or "")
    if len(text) > 120000:
        text = text[:120000] + "\n\n（正文截断：超长页面）\n"
    return text, pub


def write_md(base: Path, job: dict, body: str, pub: str) -> Path:
    lines = [
        f"# {job['title']}",
        "",
        f"- **媒体**：{job['media']}",
        f"- **来源**：{job['media']}",
        f"- **回链**：{job['url']}",
    ]
    if job.get("submit_batch"):
        lines.append(f"- **提交批次**：{job['submit_batch']}")
    lines.append(f"- **页面发布日期**：{pub or '（页内未解析，以截图为准）'}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(body.strip() if body.strip() else "（正文自页面抽取为空，以截图与回链为准）")
    lines.append("")
    md_path = base / job["md_name"]
    md_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return md_path


def append_index(job: dict, md_hash: str, png_hash: str) -> None:
    media = job["media"]
    title = job["title"]
    rel = f"media_archive/{job['folder']}/"
    line = f"| {DATE_ROW} | {ANCHOR} | {media} | {title} | `{md_hash}` | `{png_hash}` | `{rel}` |"
    text = INDEX_PATH.read_text(encoding="utf-8") if INDEX_PATH.is_file() else (
        "# media-archive INDEX\n\n| 日期 | 锚点 | 媒体 | 标题 | MD SHA256 | PNG SHA256 | 路径 |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
    )
    if md_hash not in text:
        INDEX_PATH.write_text(text.rstrip() + "\n" + line + "\n", encoding="utf-8", newline="\n")


def write_folder_manifest(base: Path, job: dict, md_hash: str, png_hash: str, md_bytes: int, png_bytes: int) -> None:
    frag = {
        "anchor": ANCHOR,
        "capture_standard": "P0-four-elements-v2",
        "date": DATE_ROW,
        "seq": job["seq"],
        "title": job["title"],
        "media": job["media"],
        "url": job["url"],
        "files": {
            job["md_name"]: {"sha256": md_hash, "bytes": md_bytes},
            f"evidence-snapshots/{job['png_name']}": {"sha256": png_hash, "bytes": png_bytes},
        },
    }
    (base / "manifest.fragment.json").write_text(
        json.dumps(frag, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    sums = f"{md_hash}  {job['md_name']}\n{png_hash}  evidence-snapshots/{job['png_name']}\n"
    (base / "SHA256SUMS.txt").write_text(sums, encoding="utf-8", newline="\n")


def _job_budget_exceeded(deadline: float | None) -> bool:
    return deadline is not None and time.monotonic() >= deadline


def _acquire_work_page(context):
    """Persistent Edge opens a default tab; extra new_page() leaves it on about:blank while automation uses another tab."""
    for extra in list(context.pages)[1:]:
        try:
            extra.close()
        except Exception:
            pass
    if context.pages:
        page = context.pages[0]
    else:
        page = context.new_page()
    try:
        page.bring_to_front()
    except Exception:
        pass
    return page


def process_job(
    job: dict,
    page,
    *,
    use_chrome: bool,
    goto_timeout_ms: int = 120_000,
    job_deadline: float | None = None,
    fast_capture: bool = False,
) -> dict:
    base = ARCHIVE_ROOT / job["folder"]
    ev = base / "evidence-snapshots"
    ev.mkdir(parents=True, exist_ok=True)
    png_path = ev / job["png_name"]

    if _job_budget_exceeded(job_deadline):
        raise TimeoutError(f"job budget exceeded before goto seq={job['seq']}")
    # fast_capture: "commit" avoids hanging on sites that never reach domcontentloaded (spinner forever).
    wait_until = "commit" if fast_capture else "domcontentloaded"
    try:
        page.bring_to_front()
    except Exception:
        pass
    try:
        page.goto(job["url"], wait_until=wait_until, timeout=goto_timeout_ms)
    except Exception as exc:  # noqa: BLE001
        raise exc
    page.wait_for_timeout(1200 if fast_capture else 2800)
    if _job_budget_exceeded(job_deadline):
        raise TimeoutError(f"job budget exceeded after goto seq={job['seq']}")
    body, pub = extract_body(page)
    if use_chrome:
        rounds = 2 if fast_capture else 4
        panels = 6 if fast_capture else 12
        snap.prepare_maximized_page(page, rounds=rounds)
        if _job_budget_exceeded(job_deadline):
            raise TimeoutError(f"job budget exceeded before capture seq={job['seq']}")
        img = snap.capture_p0_screenshot(page, max_panels=panels)
        snap.save_evidence_png(img, png_path)
    else:
        from playwright.sync_api import TimeoutError as PwTimeout

        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except PwTimeout:
            pass
        page.screenshot(path=str(png_path), full_page=True)

    md_path = write_md(base, job, body, pub)
    md_hash = sha256_file(md_path)
    png_hash = sha256_file(png_path)
    write_folder_manifest(base, job, md_hash, png_hash, md_path.stat().st_size, png_path.stat().st_size)
    append_index(job, md_hash, png_hash)
    return {"md_sha256": md_hash, "png_sha256": png_hash}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--xlsx", type=Path, default=XLSX_DEFAULT)
    ap.add_argument("--start", type=int, default=1, help="seq inclusive")
    ap.add_argument("--end", type=int, default=99999)
    ap.add_argument("--chrome", action="store_true", help="P0 desktop chrome capture (default)")
    ap.add_argument("--headless", action="store_true", help="fast playwright only (non-P0)")
    ap.add_argument("--fresh", action="store_true", help="wipe 20261118_* dirs + state + INDEX rows, restart")
    ap.add_argument(
        "--retry-errors",
        action="store_true",
        help="only jobs without valid P0 on disk (failed / empty); never skip solely because url is in done_urls",
    )
    ap.add_argument(
        "--bundled-chromium",
        action="store_true",
        help="Playwright bundled Chromium instead of system Chrome (may reduce ERR_BLOCKED_BY_CLIENT)",
    )
    ap.add_argument(
        "--edge",
        action="store_true",
        help="P0 desktop capture via Microsoft Edge (Playwright channel=msedge), not Google Chrome",
    )
    ap.add_argument(
        "--goto-timeout",
        type=int,
        default=170_000,
        metavar="MS",
        help="page.goto timeout in ms; single attempt, then skip URL (default 170000)",
    )
    ap.add_argument(
        "--job-budget-sec",
        type=int,
        default=180,
        metavar="SEC",
        help="wall-clock budget per URL; exceed → error and next job (default 180)",
    )
    ap.add_argument(
        "--fast-capture",
        action="store_true",
        help="shorter waits + fewer scroll panels (for retry batches)",
    )
    args = ap.parse_args()
    if args.edge and args.bundled_chromium:
        print("ERROR: use either --edge or --bundled-chromium, not both", file=sys.stderr)
        return 2
    use_chrome = not args.headless

    if args.fresh:
        fresh_reset()

    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    entries = [e for e in load_entries(args.xlsx) if args.start <= e["seq"] <= args.end]
    if args.retry_errors:
        retry_set = {e["url"] for e in entries if not folder_has_valid_p0(e)}
        entries = [e for e in entries if e["url"] in retry_set]
        retry_banner = (
            f"{datetime.now(TZ_CN).strftime('%Y-%m-%dT%H:%M+08:00')} "
            f"1118 settlement RETRY-ERRORS start queue={len(entries)} "
            f"edge={int(args.edge)} bundled={int(args.bundled_chromium)} "
            f"goto_ms={args.goto_timeout} job_budget_sec={args.job_budget_sec}\n"
        )
        with AUDIT_LOG.open("a", encoding="utf-8", newline="\n") as f:
            f.write(retry_banner)
        print(f"retry-errors queue={len(entries)}", flush=True)
    state = load_state()
    done = state.setdefault("done_urls", {})
    errors = state.setdefault("errors", {})

    if not AUDIT_LOG.is_file() or args.fresh:
        AUDIT_LOG.write_text(
            f"{datetime.now(TZ_CN).strftime('%Y-%m-%dT%H:%M+08:00')} "
            f"1118 settlement batch start total={len(entries)} chrome_maximized=1\n",
            encoding="utf-8",
        )

    ok = 0
    prof_tag = "edge" if args.edge else "chrome"
    profile_dir = tempfile.mkdtemp(prefix=f"oc1118_{prof_tag}_")
    with sync_playwright() as p:
        if use_chrome:
            launch_kw: dict = {
                "user_data_dir": profile_dir,
                "headless": False,
                "no_viewport": True,
                "locale": "zh-CN",
                "args": snap.browser_launch_args(),
            }
            if args.edge:
                context = p.chromium.launch_persistent_context(**launch_kw, channel="msedge")
            elif args.bundled_chromium:
                context = p.chromium.launch_persistent_context(**launch_kw)
            else:
                context = p.chromium.launch_persistent_context(**launch_kw, channel="chrome")
        else:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1920, "height": 1080}, locale="zh-CN")

        page = _acquire_work_page(context)
        if use_chrome:
            snap.prepare_maximized_page(page, rounds=3)

        for job in entries:
            url = job["url"]
            skip, why = p0gate.should_skip_capture(url, job["folder"], ARCHIVE_ROOT)
            if skip and not args.fresh:
                print(f"SKIP [{job['seq']}] {why}", flush=True)
                errors.pop(url, None)
                if url not in done:
                    done[url] = {"seq": job["seq"], "folder": job["folder"], "skipped": why}
                    save_state(state)
                continue
            try:
                print(f"[{job['seq']}] {job['title'][:40]} …", flush=True)
                deadline = time.monotonic() + max(30, args.job_budget_sec)
                meta = process_job(
                    job,
                    page,
                    use_chrome=use_chrome,
                    goto_timeout_ms=min(args.goto_timeout, args.job_budget_sec * 1000),
                    job_deadline=deadline,
                    fast_capture=args.fast_capture or args.retry_errors,
                )
                done[url] = {"seq": job["seq"], "folder": job["folder"], **meta}
                errors.pop(url, None)
                ok += 1
                with AUDIT_LOG.open("a", encoding="utf-8", newline="\n") as f:
                    f.write(
                        f"entry seq={job['seq']} url={url} md={meta['md_sha256']} png={meta['png_sha256']}\n"
                    )
            except Exception as exc:  # noqa: BLE001
                errors[url] = {"seq": job["seq"], "error": str(exc)[:500]}
                print("ERROR", job["seq"], exc, flush=True)
            save_state(state)

        context.close()
        if not use_chrome:
            browser.close()
    shutil.rmtree(profile_dir, ignore_errors=True)

    print(json.dumps({"processed": ok, "total_in_range": len(entries), "done_total": len(done)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
