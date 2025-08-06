"""Utilities for shuttle-based travel."""

from __future__ import annotations

import re
from typing import Dict, Tuple, Optional

from src.vision import screen_text
from src.movement.movement_profiles import travel_to_city, walk_to_coords
from scripts.travel import shuttle

# Configuration for known shuttle coordinates keyed by planet and city
SHUTTLE_COORDS: Dict[str, Dict[str, Tuple[int, int]]] = {
    "tatooine": {
        "mos_eisley": (3520, -4800),
        "anchorhead": (-100, 200),
    },
    "corellia": {
        "coronet": (123, 456),
    },
}

# Simplified trainer locations for quick reference
TRAINER_LOCATIONS: Dict[str, Dict[str, Dict[str, Tuple[int, int]]]] = {
    "artisan": {
        "tatooine": {"mos_eisley": (3432, -4795)},
        "corellia": {"coronet": (-123, 44)},
    },
    "marksman": {
        "corellia": {"coronet": (-150, 60)},
    },
}

# Regex used to parse coordinates from the on-screen text
_COORD_RE = re.compile(r"(-?\d+)\s*[,:]?\s*(-?\d+)")


def _detect_position() -> Tuple[int, int]:
    """Attempt to detect the player's coordinates from the screen."""
    text = screen_text()
    match = _COORD_RE.search(text)
    if match:
        return int(match.group(1)), int(match.group(2))
    return 0, 0


def travel_via_shuttle(
    agent,
    destination: str,
    *,
    start_planet: str = "tatooine",
    dest_planet: Optional[str] = None,
) -> None:
    """Travel from the player's current position to ``destination`` via shuttle."""
    position = _detect_position()
    print(f"[Shuttle] Current position: {position}")
    nearest = shuttle.nearest_shuttle(position, start_planet)
    if not nearest:
        print("[Shuttle] No shuttle found on this planet.")
        return

    print(
        f"[Shuttle] Nearest shuttle is in {nearest['city']} at ({nearest['x']}, {nearest['y']})"
    )
    walk_to_coords(agent, nearest.get("x", 0), nearest.get("y", 0))

    route = shuttle.plan_route(
        nearest.get("city"),
        destination,
        start_planet=start_planet,
        dest_planet=dest_planet,
    )
    if not route:
        print("[Shuttle] No route found to destination.")
        return

    for stop in route[1:-1]:
        travel_to_city(agent, stop["city"])
    final_stop = route[-1]
    travel_to_city(agent, final_stop["city"])
    walk_to_coords(agent, final_stop.get("x", 0), final_stop.get("y", 0))

