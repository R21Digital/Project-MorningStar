"""Utilities for selecting rare mobs."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import random

from android_ms11.data_importers import rls_importer


def select_highest_rarity_mob(path: str | Path = "data/rls_mobs.json") -> Optional[Dict[str, Any]]:
    """Return the mob with the highest rarity from ``path``.

    Mobs are loaded using :func:`rls_importer.load_rls_mobs`. The highest
    rarity mob is determined by the ``level`` field if present. If the
    file contains no mobs, ``None`` is returned.
    """
    mobs: List[Dict[str, Any]] = rls_importer.load_rls_mobs(path)
    if not mobs:
        return None
    return max(mobs, key=lambda mob: mob.get("level", 0))



def choose_next_target(path: str | Path = "data/rls_mobs.json") -> Optional[Dict[str, Any]]:
    """Return a random mob from ``path`` or ``None`` if no mobs exist."""

    mobs: List[Dict[str, Any]] = rls_importer.load_rls_mobs(path)
    if not mobs:
        return None
    return random.choice(mobs)


__all__ = ["select_highest_rarity_mob", "choose_next_target"]
