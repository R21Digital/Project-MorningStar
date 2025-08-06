"""Simplified loot table definitions."""

from __future__ import annotations

from typing import List

# Sample static loot table
LOOT_TABLE = {
    "bantha": ["bantha milk", "bantha hide"],
    "bolma": ["bolma meat", "bolma hide"],
    "canyon krayt dragon": ["krayt scale", "krayt pearl"],
}


def get_loot_for_mob(name: str) -> List[str]:
    """Return possible loot drops for ``name``."""
    return LOOT_TABLE.get(name.lower(), [])


__all__ = ["LOOT_TABLE", "get_loot_for_mob"]
