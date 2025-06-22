"""Utilities for selecting quests from the database or other sources."""

from typing import Optional, Any


def select_quest(character_name: str) -> Optional[Any]:
    """Return the next quest for ``character_name``.

    This is a placeholder that returns ``None`` until selection logic is
    implemented.
    """
    # TODO: query the quest database and choose the best quest
    return None
