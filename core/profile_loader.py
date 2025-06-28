from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

PROFILE_DIR = Path(__file__).resolve().parents[1] / "profiles"

REQUIRED_FIELDS = {
    "support_target": str,
    "preferred_trainers": dict,
    "default_mode": str,
    "skip_modes": list,
    "farming_targets": list,
}


def load_profile(name: str) -> Dict[str, Any]:
    """Return profile data for ``name`` or an empty dict if unavailable."""
    path = PROFILE_DIR / f"{name}.json"
    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
        if not isinstance(data[field], expected_type):
            raise ValueError(f"{field} must be of type {expected_type.__name__}")

    return data
