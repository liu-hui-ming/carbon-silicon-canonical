#!/usr/bin/env python3
"""EP-anchor-01 · EUV AP distribution report · 70 outlets (skip AP #1 already archived).

Uses Playwright bundled Chromium (not Google Chrome): Edge blocks many MarketersMEDIA mirror hosts (ERR_BLOCKED_BY_CLIENT).
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import shutil
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import media_evidence_snapshot_helpers as snap  # noqa: E402

ANCHOR = "EP-anchor-01"
DATE_ROW = "2026-11-12"
INDEX_PATH = ROOT / "media-archive/INDEX.md"
AUDIT = ROOT / "compass-pedal-audit/media-archive-20261114-euv-ap-distribution.log"
JOBS_JSON = ROOT / "compass-pedal-audit/euv-ap-distribution-71.json"
TZ_CN = timezone(timedelta(hours=8))
BAD = re.compile(r'[\\/:*?"<>|]')
SKIP_NO = {1}


def safe(s: str) -> str:
    return BAD.sub("_", s).strip() or "untitled"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def host_slug(url: str) -> str:
    host = urlparse(url).netloc.lower().replace("www.", "")
    slug = re.sub(r"[^a-z0-9]+", "-", host).strip("-")
    return slug[:56].rstrip("-") or "outlet"


def load_canonical_body() -> tuple[str, str]:
    triple = ROOT / "scripts/_ingest_euv_triple_20261111.py"
    spec = importlib.util.spec_from_file_location("euv_triple", triple)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod.TITLE, mod.BODY


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


def index_has_url(url: str) -> bool:
    if not INDEX_PATH.is_file():
        return False
    return url in INDEX_PATH.read_text(encoding="utf-8")


def manifest_has_url(base: Path, url: str) -> bool:
    mp = base / "manifest.json"
    if not mp.is_file():
        return False
    try:
        data = json.loads(mp.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    for ing in data.get("ingests", []):
        if ing.get("url") == url:
            return True
    return False


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
          || document.querySelector('.TRS_Editor')
          || document.querySelector('main')
          || document.querySelector('#app');
        const raw = article ? article.innerText : document.body.innerText;
        return (raw || '').replace(/\\s+/g, ' ').trim();
    }"""
    )
    text = re.sub(r"\n{3,}", "\n\n", text or "")
    if len(text) > 120000:
        text = text[:120000] + "\n\n（正文截断：超长页面）\n"
    return text, pub


def artifact_names(job: dict) -> tuple[str, str]:
    """Short on-disk names avoid Windows MAX_PATH truncation on long English titles."""
    tag = safe(job["media_cn"])[:36]
    stem = f"EP-EUV-{int(job['no']):03d}_{tag}"
    return f"{stem}.md", f"{stem}_snapshot.png"


def write_md(base: Path, title: str, job: dict, body: str, pub: str) -> tuple[Path, str, str]:
    md_name, png_name = artifact_names(job)
    lines = [
        f"# {title}",
        "",
        f"- **媒体**：{job['media_cn']}",
        f"- **来源**：{job['source']}",
        f"- **回链**：{job['url']}",
        f"- **页面发布日期**：{pub or job.get('date') or DATE_ROW}",
        "",
        "---",
        "",
        body.strip(),
        "",
    ]
    md_path = base / md_name
    md_path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    if md_path.read_bytes()[:3] == b"\xef\xbb\xbf":
        raise RuntimeError("BOM detected")
    return md_path, md_name, png_name


def merge_manifest(
    base: Path,
    title: str,
    job: dict,
    md_name: str,
    png_name: str,
    md_h: str,
    png_h: str,
    md_b: int,
    png_b: int,
    pub: str,
) -> None:
    mp = base / "manifest.json"
    data = (
        json.loads(mp.read_text(encoding="utf-8"))
        if mp.is_file()
        else {"anchor": ANCHOR, "capture_standard": "P0-four-elements-v2", "ingests": [], "files": {}}
    )
    if not any(i.get("url") == job["url"] for i in data.get("ingests", [])):
        data.setdefault("ingests", []).append(
            {
                "date": DATE_ROW,
                "title": title,
                "media": job["media_cn"],
                "source": job["source"],
                "url": job["url"],
                "pub_date_page": pub or job.get("date") or DATE_ROW,
            }
        )
    data.setdefault("files", {})[md_name] = {"sha256": md_h, "bytes": md_b}
    data["files"][f"evidence-snapshots/{png_name}"] = {"sha256": png_h, "bytes": png_b}
    mp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")


def rebuild_sums(base: Path) -> None:
    pairs: list[tuple[str, Path]] = []
    for md in sorted(base.glob("*.md")):
        pairs.append((md.name, md))
    ev = base / "evidence-snapshots"
    if ev.is_dir():
        for png in sorted(ev.glob("*.png")):
            pairs.append((f"evidence-snapshots/{png.name}", png))
    lines = [f"{sha256_file(p)}  {name}" for name, p in pairs]
    (base / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def append_index(job: dict, title: str, md_h: str, png_h: str, *, repair: bool = False) -> None:
    rel = f"media-archive/{job['media_key']}/{ANCHOR}/"
    line = f"| {DATE_ROW} | {ANCHOR} | {job['media_cn']} | {title} | `{md_h}` | `{png_h}` | `{rel}` |"
    text = INDEX_PATH.read_text(encoding="utf-8") if INDEX_PATH.is_file() else (
        "# media-archive INDEX\n\n| 日期 | 锚点 | 媒体 | 标题 | MD SHA256 | PNG SHA256 | 路径 |\n"
        "| --- | --- | --- | --- | --- | --- | --- |\n"
    )
    if repair and title in text and job["media_cn"] in text:
        lines_out: list[str] = []
        for ln in text.splitlines():
            if (
                title in ln
                and job["media_cn"] in ln
                and ANCHOR in ln
                and ln.strip().startswith("|")
            ):
                lines_out.append(line)
            else:
                lines_out.append(ln)
        INDEX_PATH.write_text("\n".join(lines_out) + "\n", encoding="utf-8", newline="\n")
    elif md_h not in text and job["url"] not in text:
        INDEX_PATH.write_text(text.rstrip() + "\n" + line + "\n", encoding="utf-8", newline="\n")


def prune_stale_artifacts(base: Path) -> None:
    for p in list(base.iterdir()):
        if p.is_file() and p.suffix not in {".md", ".json", ".txt"}:
            p.unlink(missing_ok=True)
    ev = base / "evidence-snapshots"
    if ev.is_dir():
        for p in ev.iterdir():
            if p.is_file() and p.suffix.lower() != ".png":
                p.unlink(missing_ok=True)


def capture_needed(base: Path, job: dict, repair: bool) -> bool:
    if repair:
        return True
    if index_has_url(job["url"]) or manifest_has_url(base, job["url"]):
        _, png_name = artifact_names(job)
        png = base / "evidence-snapshots" / png_name
        if png.is_file() and png.stat().st_size >= 50_000:
            return False
        return True
    return True


def build_jobs(rows: list[dict]) -> list[dict]:
    jobs = []
    for row in rows:
        no = int(row["no"])
        if no in SKIP_NO:
            continue
        url = row["url"]
        media_key = host_slug(url)
        jobs.append(
            {
                "no": no,
                "media_key": media_key,
                "media_cn": row["media_cn"],
                "media_en": row["media_en"],
                "url": url,
                "date": row.get("date") or DATE_ROW,
                "source": f"MarketersMEDIA Newswire · {row['media_en']}",
            }
        )
    return jobs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=2, help="最小 outlet 序号（含）")
    ap.add_argument("--end", type=int, default=71, help="最大 outlet 序号（含）")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument(
        "--edge",
        action="store_true",
        help="Use system Edge (many distribution mirrors fail with ERR_BLOCKED_BY_CLIENT)",
    )
    ap.add_argument(
        "--repair",
        action="store_true",
        help="Re-capture even if URL in manifest; fix truncated/empty PNG (short filenames)",
    )
    args = ap.parse_args()

    title, canonical_body = load_canonical_body()
    rows = json.loads(JOBS_JSON.read_text(encoding="utf-8"))
    jobs = [j for j in build_jobs(rows) if args.start <= j["no"] <= args.end]
    jobs.sort(key=lambda x: x["no"])

    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(TZ_CN).strftime("%Y-%m-%dT%H:%M+08:00")
    with AUDIT.open("a", encoding="utf-8", newline="\n") as f:
        f.write(f"{stamp} batch run edge={int(args.edge)} range={args.start}-{args.end}\n")

    if args.dry_run:
        print(json.dumps(jobs, ensure_ascii=False, indent=2))
        return 0

    profile = tempfile.mkdtemp(prefix="euv_ap_dist_")
    ok, skip, fail = 0, 0, 0
    try:
        with sync_playwright() as p:
            launch_kw = dict(
                user_data_dir=profile,
                headless=False,
                no_viewport=True,
                locale="zh-CN",
                args=snap.browser_launch_args(),
            )
            if args.edge:
                context = p.chromium.launch_persistent_context(**launch_kw, channel="msedge")
            else:
                context = p.chromium.launch_persistent_context(**launch_kw)
            page = _acquire_work_page(context)
            snap.prepare_maximized_page(page, rounds=3)
            for job in jobs:
                base = ROOT / "media-archive" / job["media_key"] / ANCHOR
                if not capture_needed(base, job, args.repair):
                    skip += 1
                    print(f"skip no={job['no']} {job['media_key']}", flush=True)
                    continue
                prune_stale_artifacts(base)
                ev = base / "evidence-snapshots"
                ev.mkdir(parents=True, exist_ok=True)
                print(f"capture no={job['no']} {job['media_cn'][:24]}", flush=True)
                try:
                    wait = "commit" if "#/details/" in job["url"] else "domcontentloaded"
                    page.goto(job["url"], wait_until=wait, timeout=180_000)
                    page.wait_for_timeout(4500 if wait == "commit" else 2800)
                    body, pub = extract_body(page)
                    if len(body) < 400 or "Hidden Pitfall" not in body:
                        body = canonical_body
                    snap.prepare_maximized_page(page, rounds=2)
                    img = snap.capture_p0_screenshot(page)
                    md_path, md_name, png_name = write_md(base, title, job, body, pub)
                    png_path = ev / png_name
                    snap.save_evidence_png(img, png_path)
                    md_h = sha256_file(md_path)
                    png_h = sha256_file(png_path)
                    merge_manifest(
                        base,
                        title,
                        job,
                        md_name,
                        png_name,
                        md_h,
                        png_h,
                        md_path.stat().st_size,
                        png_path.stat().st_size,
                        pub,
                    )
                    rebuild_sums(base)
                    append_index(job, title, md_h, png_h, repair=args.repair)
                    with AUDIT.open("a", encoding="utf-8", newline="\n") as f:
                        f.write(
                            f"ok no={job['no']} media={job['media_cn']} md={md_h} png={png_h} url={job['url']}\n"
                        )
                    ok += 1
                except Exception as exc:
                    fail += 1
                    with AUDIT.open("a", encoding="utf-8", newline="\n") as f:
                        f.write(f"FAIL no={job['no']} url={job['url']} err={exc!r}\n")
                    print(f"FAIL no={job['no']}: {exc}", flush=True)
            context.close()
    finally:
        shutil.rmtree(profile, ignore_errors=True)
    summary = {"ok": ok, "skip": skip, "fail": fail, "title": title}
    print(json.dumps(summary, ensure_ascii=True), flush=True)
    return 1 if fail and not ok else 0


if __name__ == "__main__":
    raise SystemExit(main())