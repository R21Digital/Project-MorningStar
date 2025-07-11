"""Track session metrics and adjust mode if needed."""

from __future__ import annotations

from typing import Dict, Any

from core import state_tracker
from utils.logging_utils import log_event

FATIGUE_THRESHOLD = 3
LOW_XP_RATE = 20.0
HIGH_XP_RATE = 200.0


def monitor_session(perf_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Record metrics to :mod:`core.state_tracker` and update mode.

    Parameters
    ----------
    perf_metrics:
        Dictionary with optional ``xp``, ``loot`` and ``xp_rate`` keys.

    Returns
    -------
    dict
        Updated state dictionary after applying fatigue logic and mode selection.
    """
    state = state_tracker.get_state()
    xp = perf_metrics.get("xp")
    loot = perf_metrics.get("loot")
    xp_rate = float(perf_metrics.get("xp_rate", 0.0))

    prev_fatigue = int(state.get("fatigue_level", 0))
    prev_mode = state.get("mode")
    fatigue = prev_fatigue
    if xp_rate < LOW_XP_RATE:
        fatigue += 1
        mode = "bounty_mode"
    elif xp_rate > HIGH_XP_RATE:
        fatigue = max(fatigue - 1, 0)
        mode = None
    else:
        mode = state.get("mode")

    crossed_threshold = prev_fatigue < FATIGUE_THRESHOLD <= fatigue
    mode_changed = prev_mode != mode

    updates: Dict[str, Any] = {"fatigue_level": fatigue}
    if xp is not None:
        updates["xp"] = xp
    if loot is not None:
        updates["loot"] = loot
    updates["mode"] = mode

    state_tracker.update_state(**updates)

    if crossed_threshold or mode_changed:
        log_event(
            f"Fatigue detected in mode: {prev_mode}. Switching to: {mode}"
        )

    log_event(
        f"Session summary - XP/hr: {xp_rate:.2f}, Loot: {len(loot) if isinstance(loot, list) else 0}, Fatigue: {fatigue}, Mode: {mode}"
    )

    return state_tracker.get_state()


__all__ = ["monitor_session"]
