"""Grind mode utilities."""

from __future__ import annotations

import random
from typing import Iterable, Mapping, Optional, Sequence

from data.loot_table import get_loot_for_mob


def choose_grind_target(
    mobs: Iterable[Mapping[str, object]],
    *,
    preferred_loot: Sequence[str] | None = None,
    min_level: int = 1,
    max_level: int = 90,
) -> Optional[Mapping[str, object]]:
    """Return the best grind target from ``mobs``.

    Each entry in ``mobs`` should provide at least ``name`` and ``level`` keys.
    The optional ``loot`` key may list possible drops. When missing, loot is
    looked up via :func:`data.loot_table.get_loot_for_mob` using the mob name.

    Parameters
    ----------
    mobs:
        Iterable of mob information mappings.
    preferred_loot:
        Sequence of loot names to prioritize when selecting a target.
    min_level, max_level:
        Inclusive level range for valid targets.

    Returns
    -------
    mapping or None
        The chosen mob mapping or ``None`` when no candidates match.
    """

    pref = {str(item).lower() for item in preferred_loot or []}
    best: Optional[Mapping[str, object]] = None
    best_score = -1

    for mob in mobs:
        level = int(mob.get("level", 0))
        if level < min_level or level > max_level:
            continue

        loot = mob.get("loot")
        if loot is None:
            loot = get_loot_for_mob(str(mob.get("name", "")))
        loot_set = {str(item).lower() for item in loot}
        match_count = len(pref.intersection(loot_set)) if pref else 0
        score = match_count * 100 + level

        if score > best_score:
            best = mob
            best_score = score

    if best is None and mobs:
        candidates = [m for m in mobs if min_level <= int(m.get("level", 0)) <= max_level]
        if candidates:
            best = random.choice(candidates)

    return best


__all__ = ["choose_grind_target"]
