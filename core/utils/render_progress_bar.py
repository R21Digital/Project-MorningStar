"""Helpers for rendering textual progress bars."""

from __future__ import annotations

from typing import List

from ..constants import (
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_IN_PROGRESS,
    STATUS_NOT_STARTED,
    STATUS_UNKNOWN,
)

# Map quest status emoji to block characters for the visual bar
_BLOCK_MAP = {
    STATUS_COMPLETED: "█",
    STATUS_FAILED: "▒",
    STATUS_IN_PROGRESS: "▓",
    STATUS_NOT_STARTED: "░",
    STATUS_UNKNOWN: "░",
}


def render_progress_bar(statuses: List[str]) -> str:
    """Return a textual progress bar for ``statuses``.

    ``statuses`` should contain status emoji as defined in ``core.constants``.
    The resulting string combines block characters with the original emoji to
    illustrate progress.
    """

    if not statuses:
        return ""

    blocks = "".join(_BLOCK_MAP.get(s, _BLOCK_MAP[STATUS_UNKNOWN]) for s in statuses)
    return f"{blocks} {''.join(statuses)}"


__all__ = ["render_progress_bar"]
