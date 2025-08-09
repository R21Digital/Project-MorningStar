from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple


try:
    import win32gui
    import win32con
    import win32process
    import win32api
    WINDOWS = True
except Exception:
    WINDOWS = False


SWG_TITLE_HINTS = ["Star Wars Galaxies", "SWGEmu", "SWG"]


@dataclass
class SwgWindow:
    handle: int
    title: str
    rect: Tuple[int, int, int, int]


def find_swg_window() -> Optional[SwgWindow]:
    if not WINDOWS:
        return None
    found: Optional[SwgWindow] = None

    def _enum_cb(hwnd, _):
        nonlocal found
        if not win32gui.IsWindowVisible(hwnd):
            return
        title = win32gui.GetWindowText(hwnd) or ""
        if not any(h.lower() in title.lower() for h in SWG_TITLE_HINTS):
            return
        rect = win32gui.GetWindowRect(hwnd)
        w = rect[2] - rect[0]
        h = rect[3] - rect[1]
        if w < 640 or h < 480:
            return
        found = SwgWindow(handle=hwnd, title=title, rect=rect)

    try:
        win32gui.EnumWindows(_enum_cb, None)
    except Exception:
        return None
    return found


def focus_window(hwnd: int) -> bool:
    if not WINDOWS:
        return False
    try:
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        return True
    except Exception:
        return False


