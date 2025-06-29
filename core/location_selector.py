"""High level helpers for selecting travel targets."""

from __future__ import annotations

from typing import Mapping, Optional, Tuple

from modules.travel.location_selector import select_target
from src.movement.movement_profiles import walk_to_coords

# Simplified hotspot coordinate lookup table.
HOTSPOTS: dict[str, dict[str, dict[str, Tuple[int, int]]]] = {
    "tatooine": {
        "mos_eisley": {"cantina": (3520, -4800)},
    },
    "dantooine": {"mining": {"cave": (50, 75)}},
}


def locate_hotspot(planet: str, city: str, hotspot: str) -> Optional[Tuple[int, int]]:
    """Return coordinates for ``hotspot`` in ``city`` on ``planet`` if known."""
    return HOTSPOTS.get(planet.lower(), {}).get(city.lower(), {}).get(hotspot.lower())


def travel_to_target(target: Mapping[str, str], agent=None) -> Optional[dict]:
    """Travel to the desired target and walk to its hotspot if provided."""
    planet = target.get("planet", "tatooine")
    city = target.get("city", "mos_eisley")
    hotspot = target.get("hotspot")

    dest = select_target(planet, city, agent=agent)

    if hotspot:
        coords = locate_hotspot(planet, city, hotspot)
        if coords:
            walk_to_coords(agent, coords[0], coords[1])
    return dest
