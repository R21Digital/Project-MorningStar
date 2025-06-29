"""Helpers for verifying that the player remains at a waypoint."""

from __future__ import annotations

import re
import time
from typing import Tuple

from src.vision import screen_text

_COORD_RE = re.compile(r"(-?\d+)\s*[,:]?\s*(-?\d+)")

Coords = Tuple[int, int]


def _detect_position() -> Coords:
    """Return the player's coordinates parsed from the screen."""
    text = screen_text()
    match = _COORD_RE.search(text)
    if match:
        return int(match.group(1)), int(match.group(2))
    return 0, 0


def _distance(a: Coords, b: Coords) -> float:
    """Return Euclidean distance between two coordinate pairs."""
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def verify_waypoint_stability(coords: Coords, delay: float = 1.0) -> bool:
    """Return ``True`` if the player stays near ``coords`` after ``delay`` seconds."""
    start = _detect_position()
    start_dist = _distance(start, coords)
    time.sleep(delay)
    end = _detect_position()
    end_dist = _distance(end, coords)
    if end_dist > start_dist:
        print(
            f"[WaypointVerifier] Player moved from {start} to {end}; distance increased."
        )
        return False
    print(f"[WaypointVerifier] Position stable at {start}.")
    return True
