# -*- coding: utf-8 -*-
"""P0 four-elements desktop capture (URL bar + page + taskbar clock)."""
from __future__ import annotations

import time
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageGrab
from playwright.sync_api import Page


def browser_launch_args() -> list[str]:
    return ["--start-maximized", "--window-position=0,0"]


def maximize_browser_window(page: Page) -> None:
    try:
        page.evaluate(
            """() => {
              window.moveTo(0, 0);
              window.resizeTo(screen.availWidth, screen.availHeight);
            }"""
        )
    except Exception:
        pass


def focus_browser(page: Page) -> None:
    try:
        page.bring_to_front()
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        found: list[int] = []

        def callback(hwnd, _):
            buf = ctypes.create_unicode_buffer(512)
            user32.GetWindowTextW(hwnd, buf, 512)
            title = buf.value
            if "Chrome" in title or "Google Chrome" in title:
                found.append(hwnd)
            return True

        WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        user32.EnumWindows(WNDENUMPROC(callback), 0)
        if found:
            user32.SetForegroundWindow(found[0])
    except Exception:
        page.bring_to_front()
    time.sleep(0.35)


def grab_full_screen() -> Image.Image:
    img = ImageGrab.grab(all_screens=False)
    return img.convert("RGB")


def save_evidence_png(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    path.write_bytes(buf.getvalue())


def capture_p0_screenshot(page: Page, max_panels: int = 12) -> Image.Image:
    maximize_browser_window(page)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(500)
    panels: list[Image.Image] = []
    y = 0
    step = max(400, int(page.evaluate("() => window.innerHeight") or 800) - 80)
    last_hash = None
    for _ in range(max_panels):
        page.evaluate(f"window.scrollTo(0, {y})")
        page.wait_for_timeout(450)
        focus_browser(page)
        panel = grab_full_screen()
        h = panel.tobytes()[::997]
        if h == last_hash:
            break
        last_hash = h
        panels.append(panel)
        y += step
        at_bottom = page.evaluate(
            "() => window.scrollY + window.innerHeight >= document.body.scrollHeight - 4"
        )
        if at_bottom:
            break
    if len(panels) == 1:
        return panels[0]
    w = max(p.width for p in panels)
    total_h = sum(p.height for p in panels)
    out = Image.new("RGB", (w, total_h))
    off = 0
    for p in panels:
        out.paste(p, (0, off))
        off += p.height
    return out
