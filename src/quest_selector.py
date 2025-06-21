"""Quest selection utilities.

This module provides minimal logic for choosing which quest to run
next. More sophisticated selection strategies will be implemented
later.
"""

from typing import Any, Dict, List, Optional


def choose_next_quest(quests: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Return the next quest to execute from ``quests``.

    This stub simply returns the first quest in the list or ``None`` if
    the list is empty.
    """
    return quests[0] if quests else None
