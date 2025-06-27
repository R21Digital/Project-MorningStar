"""Screen capture utilities for grabbing specific regions."""

from __future__ import annotations

from typing import Tuple, Optional

import pyautogui


def capture_screen_region(region: Tuple[int, int, int, int] | None = None):
    """Return a screenshot of ``region`` using :func:`pyautogui.screenshot`.

    Parameters
    ----------
    region:
        Optional ``(left, top, width, height)`` tuple defining the region to
        capture.  When ``None`` the entire screen is captured.

    Returns
    -------
    PIL.Image.Image
        Screenshot image captured by ``pyautogui``.
    """
    return pyautogui.screenshot(region=region)
