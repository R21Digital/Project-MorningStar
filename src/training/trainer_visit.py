from .trainer_data_loader import get_trainer_coords
from src.movement.movement_profiles import travel_to_city


def visit_trainer(agent, profession, planet="tatooine", city="mos_eisley"):
    trainer_info = get_trainer_coords(profession, planet, city)

    if trainer_info:
        name, x, y = trainer_info
        print(f"[Trainer] Found static trainer data: {name} at ({x}, {y})")
        travel_to_city(agent, city)
        # Future: move to exact coordinates
    else:
        print("[Trainer] No static data. Will try /find or scan logic next.")
        # Stub: implement /find fallback here
