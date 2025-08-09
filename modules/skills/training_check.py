"""Utilities to determine which profession skills are trainable."""

from __future__ import annotations

from typing import Dict, Iterable, List, Tuple, Union


def get_trainable_skills(
    character_data: Dict[str, int],
    profession_tree: Dict[str, Union[Iterable[int], Dict[str, Union[int, str]]]],
) -> List[Tuple[str, int]]:
    """Return a list of professions that can train a higher skill level.

    Parameters
    ----------
    character_data:
        Mapping of profession names to the current trained level.
    profession_tree:
        Mapping of professions to either an iterable of possible levels or a dict with max_level, current_level, next_level.

    Returns
    -------
    List[Tuple[str, int]]
        Each tuple contains a profession name and the next trainable level.
    """
    trainable: List[Tuple[str, int]] = []
    for profession, levels in profession_tree.items():
        current = character_data.get(profession, 0)
        
        # Handle new profession_tree structure (dict with max_level, current_level, next_level)
        if isinstance(levels, dict):
            max_level = levels.get("max_level", 0)
            next_level = levels.get("next_level", 1)
            if current < max_level:
                trainable.append((profession, next_level))
        # Handle old profession_tree structure (iterable of levels)
        elif isinstance(levels, (list, tuple)) and levels:
            if current < max(levels):
                trainable.append((profession, current + 1))
    
    return trainable
