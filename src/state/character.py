character_state = {
    "location": {"planet": None, "city": None},
    "quests": {}
}


def update_location(planet: str, city: str):
    character_state["location"] = {"planet": planet, "city": city}


def log_quest_progress(quest_id: str, action: str):
    character_state["quests"][quest_id] = action
