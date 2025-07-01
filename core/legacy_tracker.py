"""Utilities for working with legacy quest steps."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List, Dict

LEGACY_FILE = Path(__file__).resolve().parents[1] / "data" / "legacy_steps.json"


def load_steps() -> List[Dict[str, Any]]:
    """Return the list of legacy quest steps."""
    with open(LEGACY_FILE, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    if isinstance(data, dict) and "steps" in data:
        return list(data["steps"])
    return list(data)

__all__ = ["load_steps", "LEGACY_FILE"]
