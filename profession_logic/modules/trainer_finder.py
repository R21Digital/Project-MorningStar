"""Locate profession trainers in game data."""

from __future__ import annotations
from typing import Dict, Optional


def find_trainer(profession: str, planet: Optional[str] = None, city: Optional[str] = None) -> Dict:
    """Return placeholder location details for a trainer."""
    return {
        "profession": profession,
        "planet": planet or "tatooine",
        "city": city or "mos_eisley",
        "x": 0,
        "y": 0,
    }
