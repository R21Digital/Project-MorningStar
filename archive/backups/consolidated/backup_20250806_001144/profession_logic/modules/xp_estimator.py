"""XP estimation utilities with logging support."""

from __future__ import annotations

import json
import os
from collections import defaultdict
from datetime import datetime
from typing import List, Dict

from src.xp_tracker import estimate_xp
from src.xp_paths import LOG_ROOT

# Ensure the root log directory exists
os.makedirs(LOG_ROOT, exist_ok=True)

# Shared log file for global action logging
LOG_FILE = "xp_actions.log"


# ---------------------------------------------------------------------------
# Helper functions for profession activity tracking
# ---------------------------------------------------------------------------

def _sanitize(name: str) -> str:
    """Normalize names for file paths."""
    return name.lower().replace(" ", "_")


def _log_path(profession: str, activity: str) -> str:
    prof = _sanitize(profession)
    act = _sanitize(activity)
    filename = f"{prof}_{act}.json"
    return os.path.join(LOG_ROOT, filename)


def _load(path: str) -> List[Dict]:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []


def _save(path: str, data: List[Dict]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def log_xp(profession: str, activity: str, xp: int, hours: float) -> None:
    """Append an XP entry for a profession and activity."""
    path = _log_path(profession, activity)
    entries = _load(path)
    entries.append({
        "timestamp": datetime.utcnow().isoformat(),
        "xp": xp,
        "hours": hours,
    })
    _save(path, entries)


def log_action(profession: str, activity: str, hours: float = 0.0) -> int:
    """Log XP for ``activity`` and record the action globally."""
    xp = estimate_xp(activity)
    log_xp(profession, activity, xp, hours)
    # Also log to the global action log for learning models
    StaticXPEstimator().log_action(activity, xp)
    return xp


def estimate_xp_per_hour(profession: str, activity: str) -> float:
    """Return the average XP earned per hour for ``activity``."""
    path = _log_path(profession, activity)
    entries = _load(path)
    total_xp = sum(e.get("xp", 0) for e in entries)
    total_hours = sum(e.get("hours", 0.0) for e in entries)
    return total_xp / total_hours if total_hours else 0.0


# ---------------------------------------------------------------------------
# Global action logging and learning estimators
# ---------------------------------------------------------------------------

class StaticXPEstimator:
    """Log actions and compute average XP per action."""

    def __init__(self, log_dir: str = LOG_ROOT):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_path = os.path.join(self.log_dir, LOG_FILE)

    def log_action(self, action: str, xp: int) -> None:
        timestamp = datetime.now().isoformat()
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(f"{timestamp},{action},{xp}\n")

    def average_xp(self, action: str) -> float:
        if not os.path.exists(self.log_path):
            return 0.0
        total = 0
        count = 0
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) != 3:
                    continue
                _, act, xp_str = parts
                if act == action:
                    try:
                        total += int(xp_str)
                        count += 1
                    except ValueError:
                        continue
        return total / count if count else 0.0


class LearningXPEstimator:
    """Update XP estimates from logged data."""

    def __init__(self, log_dir: str = LOG_ROOT):
        self.log_dir = log_dir
        self.log_path = os.path.join(self.log_dir, LOG_FILE)
        self.estimates: Dict[str, float] = {}

    def update(self) -> None:
        """Recompute averages using the saved log."""
        counts: Dict[str, List[int]] = defaultdict(lambda: [0, 0])
        if os.path.exists(self.log_path):
            with open(self.log_path, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split(",")
                    if len(parts) != 3:
                        continue
                    _, action, xp_str = parts
                    try:
                        xp = int(xp_str)
                    except ValueError:
                        continue
                    counts[action][0] += xp
                    counts[action][1] += 1
        self.estimates = {
            a: total / count if count else 0
            for a, (total, count) in counts.items()
        }

    def estimate(self, action: str) -> float:
        """Return the current XP estimate for ``action``."""
        return self.estimates.get(action, 0.0)

__all__ = [
    "log_xp",
    "log_action",
    "estimate_xp_per_hour",
    "StaticXPEstimator",
    "LearningXPEstimator",
]
