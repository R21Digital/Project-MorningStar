"""Utilities for selecting quests from the database or other sources."""

from __future__ import annotations

import json
import random
import sqlite3
from typing import Optional, Any, Dict

from .db.database import get_connection


def _load_quests(character_name: str) -> list[Dict[str, Any]]:
    """Load quests for ``character_name`` from the database."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    # Pull everything so optional columns won't cause SQL errors
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
    min_xp: int | None = None,
    randomize: bool = False,
) -> Optional[Dict[str, Any]]:
    """Return the next quest for ``character_name``.

    Parameters
    ----------
    character_name:
        Name of the character requesting the quest.
    planet:
        If provided, only quests matching this planet are considered.
    npc:
        Optionally filter by quest giver.
    min_xp:
        Minimum XP reward required.
    randomize:
        When ``True`` choose a quest at random from the candidates.
    """

    quests = _load_quests(character_name)

    def matches(q: Dict[str, Any]) -> bool:
        if planet and q.get("planet") != planet:
            return False
        if npc and q.get("npc") != npc:
            return False
        if min_xp is not None and q.get("xp_reward", 0) < min_xp:
            return False
        return True

    filtered = [q for q in quests if matches(q)]
    if not filtered:
        return None

    filtered.sort(key=lambda q: q.get("fallback_rank", 0))

    if randomize and len(filtered) > 1:
        return random.choice(filtered)
    return filtered[0]
