"""Simple in-memory state tracker with persistence."""

from __future__ import annotations

import json
import os
from typing import Any, Dict

STATE_FILE = os.path.join("logs", "state.json")

_DEFAULT_STATE: Dict[str, Any] = {
    "mode": None,
    "target": None,
    "location": None,
    "loot": None,
    "xp": 0,
}

_state: Dict[str, Any] = _DEFAULT_STATE.copy()


def _load() -> None:
    """Load state from :data:`STATE_FILE` if it exists."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                for key in _DEFAULT_STATE:
                    if key in data:
                        _state[key] = data[key]
        except Exception:
            pass


_load()


def _save() -> None:
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as fh:
        json.dump(_state, fh, indent=2)


def get_state() -> Dict[str, Any]:
    """Return a copy of the current state."""
    return dict(_state)


def update_state(**kwargs: Any) -> None:
    """Update state values and persist them."""
    changed = False
    for key in _DEFAULT_STATE:
        if key in kwargs:
            _state[key] = kwargs[key]
            changed = True
    if changed:
        _save()


def reset_state() -> None:
    """Reset state to defaults and persist."""
    _state.clear()
    _state.update(_DEFAULT_STATE)
    _save()
