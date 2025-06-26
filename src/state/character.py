"""Helpers for tracking global character state.

The :data:`character_state` dictionary is a lightweight, in-memory store used
across modules to share the player's progress.  It currently tracks two pieces
of information:

``location``
    A mapping with ``"planet"`` and ``"city"`` keys describing the player's
    current position.

``quests``
    A mapping of quest identifiers to a short description of the most recent
    action performed for that quest.
"""


character_state = {
    "location": {"planet": None, "city": None},
    "quests": {},
}


def update_location(planet: str, city: str):
    """Update the ``location`` entry in :data:`character_state`."""
    character_state["location"] = {"planet": planet, "city": city}


def log_quest_progress(quest_id: str, action: str):
    """Record the last ``action`` performed for ``quest_id``."""
    character_state["quests"][quest_id] = action
