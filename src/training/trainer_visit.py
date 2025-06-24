from .trainer_data_loader import get_trainer_coords
from src.movement.movement_profiles import travel_to_city, walk_to_coords


def visit_trainer(agent, profession, planet="tatooine", city="mos_eisley"):
    trainer_info = get_trainer_coords(profession, planet, city)

    if trainer_info:
        name, x, y = trainer_info
        print(
            f"[Trainer] Found trainer: {name} at ({x}, {y}) in {city.title()}, {planet.title()}"
        )
        travel_to_city(agent, city)
        walk_to_coords(agent, x, y)
    else:
        print(f"[Trainer] Trainer not found for {profession} in {city}, {planet}.")
        print("[Trainer] Attempting /find or fallback logic (not yet implemented)")
