"""Simple session persistence utilities."""

from __future__ import annotations

import json
import os
from typing import Any, Dict

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


__all__ = ["load_session", "save_session", "update_session_key"]
