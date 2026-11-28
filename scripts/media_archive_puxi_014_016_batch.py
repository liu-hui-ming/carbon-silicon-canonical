#!/usr/bin/env python3
"""谱系联勘 014/015/016 · 11-19 发稿清单 · P0 → media_archive/."""
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

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import media_archive_p0_gate as p0gate  # noqa: E402
import media_evidence_archive_batch as snap  # noqa: E402

JOBS_JSON = ROOT / "compass-pedal-audit/media-archive-puxi-014-016-20261119.json"
STATE_PATH = ROOT / "compass-pedal-audit/media-archive-puxi-014-016-20261119.state.json"
INDEX_PATH = ROOT / "media-archive/INDEX.md"
AUDIT_LOG = ROOT / "compass-pedal-audit/media-archive-puxi-014-016-20261119.log"
ARCHIVE_ROOT = ROOT / "media_archive"
ANCHOR = "EP-anchor-01"
TZ_CN = timezone(timedelta(hours=8))
BAD_FILENAME = re.compile(r'[\\/:*?"<>|]')
MIN_PNG_BYTES = 50_000

CAMPAIGN_SHORT = {
    "puxi-014": "puxi014",
    "puxi-015": "puxi015",
    "puxi-016": "puxi016",
    "chuneng-1120": "cn1120",
    "ep-1123": "ep1123",
    "ep-1124": "ep1124",
    "pub-1123-1100": "p112311",
    "pub-1123-1330": "p112313",
    "ep-gmw-1119": "gmw1119",
    "pub-1124-1100": "p112411",
    "pub-1124-1400-kunlun": "p112414k",
    "pub-1124-1400-shuangmiao": "p112414s",
    "settlement-1126": "s1126",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_name(name: str) -> str:
    return BAD_FILENAME.sub("_", name).strip() or "untitled"


def enrich_job(raw: dict) -> dict:
    url = raw["url"].strip()
    url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[:8]
    media_slug = safe_name(raw["media"])[:24]
    camp = CAMPAIGN_SHORT.get(raw["campaign"], raw["campaign"][:8])
    folder = f"{raw['date_prefix']}_{camp}_{raw['seq']:04d}_{media_slug}_{url_hash}"
    stem = f"{raw['title']}_{raw['media']}"
    return {
        **raw,
        "url": url,
        "folder": folder,
        "md_name": safe_name(stem) + ".md",
        "png_name": safe_name(stem) + "_snapshot.png",
    }


def folder_has_valid_p0(job: dict) -> bool:
    skip, _ = p0gate.should_skip_capture(job["url"], job["folder"], ARCHIVE_ROOT)
    return skip


def load_state() -> dict:
    if STATE_PATH.is_file():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {"done_urls": {}, "errors": {}}


def save_state(state: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def extract_body(page) -> tuple[str, str]:
    pub = ""
    for sel in ("time[datetime]", ".time", ".date", "#pubtime", ".article-time", ".source-time"):
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
        const body = document.body;
        const raw = article ? article.innerText : (body && body.innerText) || '';
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
        f"- **提交批次**：{job['submit_batch']}",
        f"- **页面发布日期**：{pub or '（页内未解析，以截图为准）'}",
        "",
        "---",
        "",
        body.strip() if body.strip() else "（正文自页面抽取为空，以截图与回链为准）",
        "",
    ]
    md_path = base / job["md_name"]
    md_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    if md_path.read_bytes()[:3] == b"\xef\xbb\xbf":
        raise RuntimeError("BOM detected")
    return md_path


def append_index(job: dict, md_hash: str, png_hash: str) -> None:
    date_row = job["date_row"]
    rel = f"media_archive/{job['folder']}/"
    line = f"| {date_row} | {ANCHOR} | {job['media']} | {job['title']} | `{md_hash}` | `{png_hash}` | `{rel}` |"
    text = INDEX_PATH.read_text(encoding="utf-8") if INDEX_PATH.is_file() else (
        "# media-archive INDEX\n\n| 日期 | 锚点 | 媒体 | 标题 | MD SHA256 | PNG SHA256 | 路径 |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
    )
    if job["url"] not in text and md_hash not in text:
        INDEX_PATH.write_text(text.rstrip() + "\n" + line + "\n", encoding="utf-8", newline="\n")


def write_folder_manifest(base: Path, job: dict, md_hash: str, png_hash: str, md_bytes: int, png_bytes: int) -> None:
    frag = {
        "anchor": ANCHOR,
        "capture_standard": "P0-four-elements-v2",
        "date": job["date_row"],
        "campaign": job["campaign"],
        "seq": job["seq"],
        "title": job["title"],
        "media": job["media"],
        "url": job["url"],
        "submit_batch": job["submit_batch"],
        "capture_mode": job.get("capture_mode", "playwright_edge_p0"),
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
    for extra in list(context.pages)[1:]:
        try:
            extra.close()
        except Exception:
            pass
    page = context.pages[0] if context.pages else context.new_page()
    try:
        page.bring_to_front()
    except Exception:
        pass
    return page


def _prune_extra_tabs(page) -> None:
    for extra in list(page.context.pages)[1:]:
        try:
            extra.close()
        except Exception:
            pass
    try:
        page.bring_to_front()
    except Exception:
        pass


def process_job(job: dict, page, *, goto_timeout_ms: int, job_deadline: float | None, fast_capture: bool) -> dict:
    base = ARCHIVE_ROOT / job["folder"]
    ev = base / "evidence-snapshots"
    ev.mkdir(parents=True, exist_ok=True)
    png_path = ev / job["png_name"]
    _prune_extra_tabs(page)
    if _job_budget_exceeded(job_deadline):
        raise TimeoutError(f"job budget before goto {job['folder']}")
    wait_until = "commit" if fast_capture else "domcontentloaded"
    page.goto(job["url"], wait_until=wait_until, timeout=goto_timeout_ms)
    extra_wait = 4500 if "pconline" in job["url"] or "toutiao" in job["url"] else (1200 if fast_capture else 2800)
    page.wait_for_timeout(extra_wait)
    if _job_budget_exceeded(job_deadline):
        raise TimeoutError(f"job budget after goto {job['folder']}")
    body, pub = extract_body(page)
    rounds = 2 if fast_capture else 4
    panels = 6 if fast_capture else 12
    snap.prepare_maximized_page(page, rounds=rounds)
    img = snap.capture_p0_screenshot(page, max_panels=panels)
    snap.save_evidence_png(img, png_path)
    md_path = write_md(base, job, body, pub)
    md_hash = sha256_file(md_path)
    png_hash = sha256_file(png_path)
    if png_path.stat().st_size < MIN_PNG_BYTES:
        raise RuntimeError(f"PNG too small {png_path.stat().st_size}")
    write_folder_manifest(base, job, md_hash, png_hash, md_path.stat().st_size, png_path.stat().st_size)
    append_index(job, md_hash, png_hash)
    return {"md_sha256": md_hash, "png_sha256": png_hash}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--campaign", choices=list(CAMPAIGN_SHORT.keys()) + ["all"], default="all")
    ap.add_argument("--start-seq", type=int, default=0)
    ap.add_argument("--end-seq", type=int, default=999)
    ap.add_argument("--bundled-chromium", action="store_true")
    ap.add_argument("--edge", action="store_true")
    ap.add_argument("--retry-errors", action="store_true")
    ap.add_argument("--goto-timeout", type=int, default=170_000)
    ap.add_argument("--job-budget-sec", type=int, default=120)
    ap.add_argument("--fast-capture", action="store_true", default=True)
    ap.add_argument("--slow-capture", action="store_true")
    ap.add_argument(
        "--jobs-json",
        type=Path,
        default=None,
        help="Override job list (default: media-archive-puxi-014-016-20261119.json)",
    )
    args = ap.parse_args()
    if args.slow_capture:
        args.fast_capture = False
    use_edge = not args.bundled_chromium

    global STATE_PATH
    jobs_json = args.jobs_json or JOBS_JSON
    global AUDIT_LOG
    if args.jobs_json:
        STATE_PATH = jobs_json.with_suffix(".state.json")
        AUDIT_LOG = jobs_json.with_suffix(".log")
    elif args.campaign != "all":
        STATE_PATH = STATE_PATH.with_name(f"{STATE_PATH.stem}-{args.campaign}.state.json")

    if not jobs_json.is_file():
        print(f"MISSING {jobs_json} — run scripts/_build_puxi_014_016_jobs.py", file=sys.stderr)
        return 2

    raw = json.loads(jobs_json.read_text(encoding="utf-8"))
    jobs = [enrich_job(j) for j in raw]
    if args.campaign != "all":
        jobs = [j for j in jobs if j["campaign"] == args.campaign]
    jobs = [j for j in jobs if args.start_seq <= j["seq"] <= args.end_seq]
    jobs = [j for j in jobs if not folder_has_valid_p0(j)]

    AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(TZ_CN).strftime("%Y-%m-%dT%H:%M+08:00")
    with AUDIT_LOG.open("a", encoding="utf-8", newline="\n") as f:
        f.write(
            f"{stamp} puxi batch queue={len(jobs)} campaign={args.campaign} "
            f"edge={int(use_edge)} bundled={int(args.bundled_chromium)}\n"
        )

    state = load_state()
    done = state.setdefault("done_urls", {})
    errors = state.setdefault("errors", {})

    profile_dir = tempfile.mkdtemp(prefix="puxi014_016_")
    ok = 0
    try:
        with sync_playwright() as p:
            edge_extra = [
                "--disable-features=msTrackingPrevention,msEdgeAdBlock,msSmartScreenProtection",
            ]
            launch_args = snap.browser_launch_args() + ([] if args.bundled_chromium else edge_extra)
            launch_kw = dict(
                user_data_dir=profile_dir,
                headless=False,
                no_viewport=True,
                locale="zh-CN",
                args=launch_args,
            )
            if args.bundled_chromium:
                context = p.chromium.launch_persistent_context(**launch_kw)
            else:
                context = p.chromium.launch_persistent_context(**launch_kw, channel="msedge")
            page = _acquire_work_page(context)
            snap.prepare_maximized_page(page, rounds=3)
            for job in jobs:
                url = job["url"]
                skip, why = p0gate.should_skip_capture(url, job["folder"], ARCHIVE_ROOT)
                if skip:
                    print(f"SKIP [{job['campaign']} #{job['seq']}] {why}", flush=True)
                    errors.pop(url, None)
                    if url not in done:
                        done[url] = {"folder": job["folder"], "skipped": why}
                    save_state(state)
                    continue
                try:
                    print(f"[{job['campaign']} #{job['seq']}] {job['media']}", flush=True)
                    deadline = time.monotonic() + max(30, args.job_budget_sec)
                    meta = process_job(
                        job,
                        page,
                        goto_timeout_ms=min(args.goto_timeout, args.job_budget_sec * 1000),
                        job_deadline=deadline,
                        fast_capture=args.fast_capture or args.retry_errors,
                    )
                    done[url] = {"folder": job["folder"], **meta}
                    errors.pop(url, None)
                    ok += 1
                    with AUDIT_LOG.open("a", encoding="utf-8", newline="\n") as f:
                        f.write(f"ok folder={job['folder']} url={url} md={meta['md_sha256']}\n")
                except Exception as exc:  # noqa: BLE001
                    errors[url] = {"folder": job["folder"], "error": str(exc)[:500]}
                    print("ERROR", job["folder"], exc, flush=True)
                    with AUDIT_LOG.open("a", encoding="utf-8", newline="\n") as f:
                        f.write(f"err folder={job['folder']} url={url} {exc}\n")
                    _prune_extra_tabs(page)
                save_state(state)
            context.close()
    finally:
        shutil.rmtree(profile_dir, ignore_errors=True)

    print(json.dumps({"ok": ok, "queued": len(jobs), "errors": len(errors)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())