"""Basic performance monitoring helpers."""

from __future__ import annotations

from typing import Dict, Any
from core.state_tracker import update_state, get_state
from utils.logger import log_performance_summary


def monitor_session(perf_metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Record ``perf_metrics`` and persist them using :mod:`core.state_tracker`.

    Parameters
    ----------
    perf_metrics:
        Dictionary containing performance values such as ``xp`` or ``loot``.

    Returns
    -------
    dict
        Updated state dictionary after persisting values.
    """
    loot = perf_metrics.get("loot")
    xp = perf_metrics.get("xp")

    updates: Dict[str, Any] = {}
    if loot is not None:
        updates["loot"] = loot
    if xp is not None:
        updates["xp"] = xp

    if updates:
        update_state(**updates)

    stats = {
        "xp_rate": perf_metrics.get("xp_rate", 0.0),
        "loot": len(loot) if isinstance(loot, list) else 0,
    }
    log_performance_summary(stats)

    return get_state()

__all__ = ["monitor_session"]
