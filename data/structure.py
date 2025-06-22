# data/structure.py

QUEST_SCHEMA = {
    "id": int,
    "name": str,
    "type": str,
    "zone": str,
    "quest_giver": str,
    "description": str,
    "rewards": {
        "xp": int,
        "credits": int,
        "items": list  # Optional
    },
    "prerequisites": list,
    "coordinates": tuple,  # (x, y, planet)
    "faction": str,  # Optional
    "chain_id": int,
    "step": int,
}
