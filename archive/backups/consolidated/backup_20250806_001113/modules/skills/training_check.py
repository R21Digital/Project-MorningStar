"""Utilities to determine which profession skills are trainable."""

from __future__ import annotations

from typing import Dict, Iterable, List, Tuple


def get_trainable_skills(
    character_data: Dict[str, int],
    profession_tree: Dict[str, Iterable[int]],
) -> List[Tuple[str, int]]:
    """Return a list of professions that can train a higher skill level.

    Parameters
    ----------
    character_data:
        Mapping of profession names to the current trained level.
    profession_tree:
        Mapping of professions to an iterable of possible levels.

    Returns
    -------
    List[Tuple[str, int]]
        Each tuple contains a profession name and the next trainable level.
    """
    trainable: List[Tuple[str, int]] = []
    for profession, levels in profession_tree.items():
        current = character_data.get(profession, 0)
        if levels and current < max(levels):
            trainable.append((profession, current + 1))
    return trainable
