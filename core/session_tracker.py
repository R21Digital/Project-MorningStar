"""Simple session persistence utilities."""

from __future__ import annotations

import json
import os
from typing import Any, Dict

from utils.load_mob_affinity import load_mob_affinity

# Load mob affinity data once on import to avoid re-reading the file on every
# farming result log.
AFFINITY_MAP = load_mob_affinity()

SESSION_FILE = "session_state.json"
DEFAULT_SESSION: Dict[str, Any] = {}


def load_session() -> Dict[str, Any]:
    """Return data from :data:`SESSION_FILE` or defaults."""
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                return data
        except Exception:
            pass
    return DEFAULT_SESSION.copy()


def save_session(session_data: Dict[str, Any]) -> None:
    """Write ``session_data`` to :data:`SESSION_FILE`."""
    with open(SESSION_FILE, "w", encoding="utf-8") as fh:
        json.dump(session_data, fh, indent=2)


def update_session_key(key: str, value: Any) -> None:
    """Update ``key`` in the saved session."""
    data = load_session()
    data[key] = value
    save_session(data)


def log_farming_result(mobs: list[str], earned_credits: int) -> None:
    """Update farming statistics in :data:`SESSION_FILE`.

    Parameters
    ----------
    mobs:
        Sequence of mob names defeated during a mission.
    earned_credits:
        Credits earned from the mission.
    """

    data = load_session()
    data["missions_completed"] = int(data.get("missions_completed", 0)) + 1
    data["total_credits_earned"] = int(data.get("total_credits_earned", 0)) + int(
        earned_credits
    )

    mob_counts = data.setdefault("mob_counts", {})
    for mob in mobs:
        mob_counts[mob] = int(mob_counts.get(mob, 0)) + 1

    affinity_counts = data.setdefault("affinity_counts", {})
    for profession, keywords in AFFINITY_MAP.items():
        for mob in mobs:
            if any(k.lower() in mob.lower() for k in keywords):
                affinity_counts[profession] = (
                    int(affinity_counts.get(profession, 0)) + 1
                )

    save_session(data)


__all__ = [
    "load_session",
    "save_session",
    "update_session_key",
    "log_farming_result",
    "AFFINITY_MAP",
]
