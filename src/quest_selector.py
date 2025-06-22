"""Utilities for selecting quests from the database or other sources."""

from typing import Optional, Any, List
import json

from src.data.legacy_quest_manager import LegacyQuestManager
from src.db.queries import select_best_quest


def _filter_quests(quests: List[dict], planet: str | None, quest_type: str | None) -> List[dict]:
    """Return quests matching the provided filters."""
    results = quests
    if planet:
        planet = planet.lower()
        results = [q for q in results if planet in q.get("planet", "").lower()]
    if quest_type:
        qtype = quest_type.lower()
        results = [q for q in results if qtype in q.get("type", "").lower()]
    return results


def select_quest(
    character_name: str,
    planet: str | None = None,
    quest_type: str | None = None,
) -> Optional[Any]:
    """Return the next quest for ``character_name``.

    The function first searches the legacy quest data using ``planet`` and
    ``quest_type`` filters. If no matching quest is found, it falls back to the
    quest database via :func:`select_best_quest`.
    """
    manager = LegacyQuestManager()
    quests = manager.list_all_quests()
    filtered = _filter_quests(quests, planet, quest_type)

    for quest in filtered:
        if quest.get("steps"):
            return quest

    db_result = select_best_quest(character_name)
    if db_result:
        qid, title, steps_json = db_result
        return {"id": qid, "title": title, "steps": json.loads(steps_json)}
    return None
