import json
import os
from datetime import datetime
from typing import List, Dict

from src.xp_tracker import estimate_xp
from scripts.xp_estimator.static_estimator import StaticXPEstimator
from src.xp_paths import LOG_ROOT

os.makedirs(LOG_ROOT, exist_ok=True)


def _sanitize(name: str) -> str:
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
    """Log XP for ``activity`` using :func:`estimate_xp` from ``xp_tracker``."""
    xp = estimate_xp(activity)
    log_xp(profession, activity, xp, hours)
    # Also reuse the existing StaticXPEstimator for centralized logs
    StaticXPEstimator().log_action(activity, xp)
    return xp


def estimate_xp_per_hour(profession: str, activity: str) -> float:
    """Return the average XP earned per hour for ``activity``."""
    path = _log_path(profession, activity)
    entries = _load(path)
    total_xp = sum(e.get("xp", 0) for e in entries)
    total_hours = sum(e.get("hours", 0.0) for e in entries)
    return total_xp / total_hours if total_hours else 0.0
