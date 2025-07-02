"""Helpers for automating trainer travel via waypoints or macros."""

from __future__ import annotations

from typing import Dict, List

from utils.movement_manager import CURRENT_LOCATION

from utils.logger import logger


# --------------------------------------------------------------
def get_travel_macro(trainer: Dict) -> str:
    """Return a ``/waypoint`` macro string for ``trainer``."""
    coords = trainer.get("coords") or [trainer.get("x"), trainer.get("y")]
    if not coords or len(coords) < 2:
        raise ValueError("trainer missing coordinates")
    x, y = float(coords[0]), float(coords[1])
    name = trainer.get("name", "").strip()
    return f"/waypoint {x} {y} {name}".rstrip()


# --------------------------------------------------------------
def start_travel_to_trainer(trainer: Dict) -> None:
    """Log the travel macro and simulate execution (placeholder)."""
    macro = get_travel_macro(trainer)
    logger.info("[TrainerTravel] Executing macro: %s", macro)
    print(macro)


# --------------------------------------------------------------
def is_same_planet(trainer: Dict) -> bool:
    """Return ``True`` if the trainer is on the current planet."""
    trainer_planet = trainer.get("planet")
    current_planet = CURRENT_LOCATION["planet"]

    if not trainer_planet:
        return False

    return str(trainer_planet).lower() == str(current_planet).lower()


# --------------------------------------------------------------
def plan_travel_to_trainer(trainer: Dict) -> List[str]:
    """Return a list of travel steps required to reach ``trainer``."""
    current_planet = CURRENT_LOCATION.get("planet", "")
    steps: List[str] = []
    if not is_same_planet(trainer):
        logger.info(
            "[TrainerTravel] On %s, trainer on %s", current_planet, trainer.get("planet")
        )
        steps.append("Travel to shuttleport")
        steps.append(f"Fly to {trainer.get('planet', '').title()}")
        steps.append("Waypoint to Trainer")
    else:
        steps.append(get_travel_macro(trainer))
    return steps


__all__ = [
    "get_travel_macro",
    "start_travel_to_trainer",
    "is_same_planet",
    "plan_travel_to_trainer",
]
