# data/normalizer.py

def normalize_quest(raw):
    return {
        "id": int(raw.get("Quest ID", 0)),
        "name": raw["Title"],
        "type": raw.get("Type", "unknown"),
        "zone": raw.get("Planet", "unknown"),
        "quest_giver": raw.get("NPC", "unknown"),
        "description": raw.get("Description", ""),
        "rewards": {
            "xp": int(raw.get("XP", 0)),
            "credits": int(raw.get("Credits", 0)),
            "items": raw.get("Reward Items", [])
        },
        "prerequisites": raw.get("Requires", []),
        "coordinates": tuple(map(float, raw.get("Coords", (0, 0)))),
        "faction": raw.get("Faction"),
        "chain_id": int(raw.get("Chain ID", 0)),
        "step": int(raw.get("Step", 0)),
    }
