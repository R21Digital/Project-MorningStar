"""Buff status helpers for runtime state management.

Usage:
    state = {...}
    update_buff_state(state)
"""

from __future__ import annotations
from typing import MutableMapping, Any


def update_buff_state(state: MutableMapping[str, Any]) -> None:
    """Update ``state[\"has_buff\"]`` using placeholder logic."""
    # Placeholder: treat any existing timer value as buff active
    if state.get("buff_timer"):
        state["has_buff"] = True
    else:
        state["has_buff"] = False

__all__ = ["update_buff_state"]
