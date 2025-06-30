from utils.get_trainer_location import get_trainer_location
from src.movement.movement_profiles import travel_to_city, walk_to_coords
import utils.logger

# Keep a simple in-memory log of NPCs we've attempted to visit.  This can be
# inspected by other modules or unit tests for validation purposes.
visited_npcs = []

# Default fallback locations to search if the trainer is not immediately found.
# These coordinates are intentionally generic and may be adjusted for specific
# cities in the future.
COMMON_LOCATIONS = [
    ("mission terminal", (0, 0)),
    ("cantina", (10, 10)),
]


def visit_trainer(agent, profession, planet="tatooine", city="mos_eisley"):
    trainer_info = get_trainer_location(profession, planet, city)

    if trainer_info:
        name, x, y = trainer_info
        utils.logger.logger.info(
            f"[Trainer] Found trainer: {name} at ({x}, {y}) in {city.title()}, {planet.title()}"
        )
        travel_to_city(agent, city)
        walk_to_coords(agent, x, y)
        visited_npcs.append(name)
        if getattr(agent, "session", None):
            agent.session.add_action(f"Visited trainer {name}")
    else:
        utils.logger.logger.info(
            f"[Trainer] Trainer not found for {profession} in {city}, {planet}."
        )
        chat_cmd = f"/find {profession} trainer"
        utils.logger.logger.info("[Trainer] Attempting /find command...")
        # Simulate sending the chat command through the agent if possible
        if hasattr(agent, "send_chat"):
            agent.send_chat(chat_cmd)
        else:
            utils.logger.logger.info(f"[Chat] {chat_cmd}")

        for location, (x, y) in COMMON_LOCATIONS:
            utils.logger.logger.info(f"[Trainer] Searching {location} at ({x}, {y})")
            walk_to_coords(agent, x, y)

        visited_npcs.append(f"{profession} trainer")
        if getattr(agent, "session", None):
            agent.session.add_action(f"Searched for {profession} trainer")
