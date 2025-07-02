"""Utilities for working with legacy quest steps."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List, Dict

from .quest_state import read_saved_quest_log

LEGACY_FILE = Path(__file__).resolve().parents[1] / "data" / "legacy_steps.json"


def load_steps() -> List[Dict[str, Any]]:
    """Return the list of legacy quest steps."""
    with open(LEGACY_FILE, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, dict) and "steps" in data:
        return list(data["steps"])
    return list(data)

def load_legacy_steps() -> List[Dict[str, Any]]:
    """Alias for :func:`load_steps` for backward compatibility."""
    return load_steps()


def read_quest_log() -> List[str]:
    """Alias for :func:`core.quest_state.read_saved_quest_log`."""
    return read_saved_quest_log()


__all__ = ["load_steps", "load_legacy_steps", "read_quest_log", "LEGACY_FILE"]
