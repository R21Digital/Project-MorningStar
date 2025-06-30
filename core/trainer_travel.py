"""Helpers for automating trainer travel via waypoints or macros."""

from __future__ import annotations

from typing import Dict

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


__all__ = ["get_travel_macro", "start_travel_to_trainer"]
