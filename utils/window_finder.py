"""Simple helpers for locating the game window."""

from __future__ import annotations

from typing import Iterable, List, Optional

import pygetwindow


def find_game_window(title_keywords: str | Iterable[str] | None = None):
    """Return the first window whose title contains ``title_keywords``.

    Parameters
    ----------
    title_keywords:
        Keyword or iterable of keywords that must all be present in the window
        title.  When ``None`` the active window is returned if possible.

    Returns
    -------
    pygetwindow.Window | None
        The matched window object or ``None`` if no window is found.
    """
    if title_keywords is None:
        try:
            return pygetwindow.getActiveWindow()
        except Exception:  # pragma: no cover - platform specific
            return None

    if isinstance(title_keywords, str):
        keywords = [title_keywords.lower()]
    else:
        keywords = [kw.lower() for kw in title_keywords]

    for win in pygetwindow.getAllWindows():
        title = win.title.lower()
        if all(kw in title for kw in keywords):
            return win

    return None
