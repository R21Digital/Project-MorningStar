from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

PROFILES_DIR = Path(__file__).resolve().parents[2] / "data" / "combat_profiles"


def load_combat_profile(name: str) -> Dict:
    """Load combat profile ``name`` from :data:`PROFILES_DIR`."""
    path = PROFILES_DIR / f"{name}.json"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_profile(name: str) -> Dict:
    """Alias for :func:`load_combat_profile`."""
    return load_combat_profile(name)

