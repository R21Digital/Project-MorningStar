"""Lookup helpers for trainer coordinates."""

from typing import Optional, Tuple

from .load_trainers import load_trainers


# Return type for clarity: (name, x, y)
TrainerLocation = Tuple[str, int, int]


def get_trainer_location(
    profession: str, planet: str, city: str
) -> Optional[TrainerLocation]:
    """Return the trainer's name and coordinates if available."""
    data = load_trainers()
    entries = data.get(profession, [])
    for entry in entries:
        if (
            entry.get("planet", "").lower() == planet.lower()
            and entry.get("city", "").lower() == city.lower()
        ):
            coords = entry.get("coords") or [entry.get("x"), entry.get("y")]
            return (
                entry.get("name", f"{profession} trainer"),
                coords[0],
                coords[1],
            )
    return None
