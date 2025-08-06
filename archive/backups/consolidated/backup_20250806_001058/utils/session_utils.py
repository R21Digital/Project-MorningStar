"""Helpers for tracking session XP gains."""

from __future__ import annotations

from typing import Optional, Dict

from core.xp_estimator import XPEstimator
from src import session_logger


def track_xp_gain(
    session_id: str,
    action: str,
    start_xp: int,
    end_xp: Optional[int],
    estimator: Optional[XPEstimator] = None,
) -> int:
    """Determine XP gained and record it.

    Parameters
    ----------
    session_id:
        Unique ID for the active session.
    action:
        Descriptive name of the action performed.
    start_xp:
        XP value at the start of the action.
    end_xp:
        XP value at the end. If ``None`` the estimator is used.
    estimator:
        Optional :class:`XPEstimator` instance. If not provided a new one is
        created using the default log path.
    """
    if estimator is None:
        estimator = XPEstimator()

    if end_xp is not None:
        xp_gain = max(0, end_xp - start_xp)
    else:
        # Fallback to estimator if OCR failed
        xp_gain = int(estimator.average_xp(action))
        end_xp = start_xp + xp_gain

    estimator.log_action(action, xp_gain)

    entry: Dict = {
        "action": action,
        "start_xp": start_xp,
        "end_xp": end_xp,
        "xp_gain": xp_gain,
        "xp_per_action": estimator.average_xp(action),
    }
    session_logger.append_entry(session_id, entry)
    return xp_gain
