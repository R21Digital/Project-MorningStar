"""Utilities for selecting quests from the database or other sources."""

from __future__ import annotations

import json
import os
import random
import sqlite3
from typing import Optional, Any, Dict, List

from utils.db import get_db_connection

from src.data.legacy_quest_manager import LegacyQuestManager
from src.db.queries import select_best_quest
from .db.database import get_connection


# Map quest modes to JSON data paths. Modes not in this map
# are expected to be stored in MongoDB.
QUEST_DATA_MAP = {
    "legacy": os.path.join("data", "legacy_quests.json"),
    "ground": os.path.join("data", "commands", "ground.json"),
    "mustafar": os.path.join("data", "mustafar", "mustafar_quests.json"),
    "themeparks": os.path.join("data", "themeparks", "themeparks.json"),
}


def load_quests_from_file(file_path: str) -> list:
    """Load quest data from ``file_path`` if it exists."""
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_quests_from_db(mode: str) -> list:
    """Retrieve quest documents from MongoDB for ``mode``."""
    db = get_db_connection()
    return list(db.quests.find({"type": mode}))


def get_random_quest(mode: str):
    """Return a random quest dict for ``mode``."""
    if mode in QUEST_DATA_MAP:
        quests = load_quests_from_file(QUEST_DATA_MAP[mode])
    else:
        quests = load_quests_from_db(mode)

    return random.choice(quests) if quests else None


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


def _load_quests(character_name: str) -> list[Dict[str, Any]]:
    """Load quests for ``character_name`` from the database."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM quests")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()

    quests = []
    for row in rows:
        if row.get("character") and row["character"] != character_name:
            continue
        steps = row.get("steps")
        if isinstance(steps, str):
            try:
                row["steps"] = json.loads(steps)
            except json.JSONDecodeError:
                pass
        quests.append(row)
    return quests


def select_quest(
    character_name: str,
    *,
    planet: str | None = None,
    npc: str | None = None,
    quest_type: str | None = None,
    min_xp: int | None = None,
    randomize: bool = False,
) -> Optional[Dict[str, Any]]:
    """Return the next quest for ``character_name``."""

    # Load quests from legacy source and DB
    manager = LegacyQuestManager()
    legacy_quests = manager.list_all_quests()
    filtered_legacy = _filter_quests(legacy_quests, planet, quest_type)

    for quest in filtered_legacy:
        if quest.get("steps"):
            return quest

    # Load from database
    db_quests = _load_quests(character_name)

    def matches(q: Dict[str, Any]) -> bool:
        if planet and q.get("planet") != planet:
            return False
        if npc and q.get("npc") != npc:
            return False
        if quest_type and quest_type.lower() not in q.get("type", "").lower():
            return False
        if min_xp is not None and q.get("xp_reward", 0) < min_xp:
            return False
        return True

    filtered = [q for q in db_quests if matches(q)]
    if not filtered:
        db_result = select_best_quest(character_name)
        if db_result:
            qid, title, steps_json = db_result
            return {"id": qid, "title": title, "steps": json.loads(steps_json)}
        return None

    filtered.sort(key=lambda q: q.get("fallback_rank", 0))

    if randomize and len(filtered) > 1:
        return random.choice(filtered)
    return filtered[0]
