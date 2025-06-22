from typing import List, Dict, Optional


def select_quest(quests: List[Dict], preferred_id: Optional[int] = None) -> Dict:
    """Return the preferred quest or the first available one."""
    if not isinstance(quests, list):
        raise TypeError("quests must be a list of dicts")
    if not quests:
        raise ValueError("quests list is empty")

    if preferred_id is not None:
        for quest in quests:
            if quest.get("id") == preferred_id:
                return quest
    return quests[0]


def sort_quests_by_rank(quests: List[Dict], key: str = "rank") -> List[Dict]:
    """Sort quests by the provided ``key`` value."""
    if not all(isinstance(q, dict) for q in quests):
        raise TypeError("quests must be a list of dicts")
    return sorted(quests, key=lambda q: q.get(key, 0))
