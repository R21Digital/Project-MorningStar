"""Track XP rate and loot accumulation."""

from __future__ import annotations

from datetime import datetime
from typing import List, Dict, Any

from src.utils.logger import log_performance_summary


class PerformanceTracker:
    """Record XP gains and loot drops during a session."""

    def __init__(self) -> None:
        self.start_time = datetime.now()
        self.xp_gained = 0
        self.loot: List[str] = []

    # ------------------------------------------------------------------
    def add_xp(self, amount: int) -> None:
        """Increase the tracked XP by ``amount``."""
        self.xp_gained += max(0, int(amount))

    def add_loot(self, item: str) -> None:
        """Record a loot ``item``."""
        self.loot.append(item)

    # ------------------------------------------------------------------
    def xp_per_hour(self) -> float:
        """Return the average XP gained per hour."""
        elapsed = (datetime.now() - self.start_time).total_seconds() / 3600
        return self.xp_gained / elapsed if elapsed > 0 else 0.0

    def summary(self) -> Dict[str, Any]:
        """Return a summary dictionary of performance stats."""
        return {
            "xp_rate": round(self.xp_per_hour(), 2),
            "loot": len(self.loot),
        }

    def log_summary(self) -> Dict[str, Any]:
        """Log the current performance summary and return it."""
        stats = self.summary()
        log_performance_summary(stats)
        return stats


__all__ = ["PerformanceTracker"]
