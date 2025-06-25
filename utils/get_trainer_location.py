"""Lookup helpers for trainer coordinates."""

from typing import Optional, Tuple

from .load_trainers import load_trainers


# Return type for clarity: (name, x, y)
TrainerLocation = Tuple[str, int, int]


def get_trainer_location(profession: str, planet: str, city: str) -> Optional[TrainerLocation]:
    """Return the trainer's name and coordinates if available."""
    data = load_trainers()
    try:
        entry = data[profession][planet][city]
        return (entry["name"], entry["x"], entry["y"])
    except KeyError:
        return None
