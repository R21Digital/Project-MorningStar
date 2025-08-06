"""Quest engagement monitoring and waypoint tracking."""

from __future__ import annotations

import time
from typing import Callable, Iterable, Tuple

from utils.db import get_db_connection
from utils.logging_utils import log_event

Coords = Tuple[int, int]


class QuestMonitor:
    """Monitor quest engagement times and mission waypoints."""

    def __init__(self, *, timeout: float = 300.0, db=None) -> None:
        self.timeout = float(timeout)
        self.db = db or get_db_connection()
        self.last_engagement = time.time()

    # --------------------------------------------------
    def record_engagement(self, now: float | None = None) -> None:
        """Record the most recent engagement time."""
        self.last_engagement = now if now is not None else time.time()

    # --------------------------------------------------
    def check_relocation(self, now: float | None = None) -> bool:
        """Return ``True`` if a relocation scan was triggered."""
        now = now if now is not None else time.time()
        if now - self.last_engagement >= self.timeout:
            self.sweep_area()
            self.last_engagement = now
            return True
        return False

    # --------------------------------------------------
    def sweep_area(self) -> None:  # pragma: no cover - placeholder
        """Scan nearby lairs/NPCs for updated mission waypoints."""
        log_event("[QuestMonitor] Sweeping area for mission waypoints")
        # Placeholder for real scanning logic

    # --------------------------------------------------
    def update_waypoint(self, coords: Iterable[int]) -> None:
        """Persist ``coords`` to the mission database."""
        xy = tuple(int(c) for c in coords)
        if len(xy) != 2:
            raise ValueError("coords must contain two values")
        try:
            self.db.missions.update_one(
                {"x": xy[0], "y": xy[1]},
                {"$set": {"x": xy[0], "y": xy[1]}},
                upsert=True,
            )
            log_event(f"[QuestMonitor] Updated mission waypoint: {xy}")
        except Exception:
            log_event("[QuestMonitor] Failed to update mission DB")

    # --------------------------------------------------
    def manual_override(
        self,
        is_held: Callable[[], bool],
        get_position: Callable[[], Coords],
        now: float | None = None,
    ) -> bool:
        """Log the current position when the override key is held."""
        if not is_held():
            return False
        coords = get_position()
        self.update_waypoint(coords)
        self.record_engagement(now)
        return True


__all__ = ["QuestMonitor"]
