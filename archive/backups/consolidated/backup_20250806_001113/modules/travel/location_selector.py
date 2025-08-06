"""Travel to arbitrary city using shuttle routes."""

from __future__ import annotations

from typing import Optional

from scripts.travel import shuttle
from src.movement.movement_profiles import travel_to_city, walk_to_coords

DEFAULT_START_CITY = "mos_eisley"
DEFAULT_START_PLANET = "tatooine"


def select_target(planet: str, city: str, agent=None) -> Optional[dict]:
    """Travel via shuttle to ``city`` on ``planet`` using movement profiles."""
    route = shuttle.plan_route(
        DEFAULT_START_CITY,
        city,
        start_planet=DEFAULT_START_PLANET,
        dest_planet=planet,
    )
    if not route:
        print("[Location] No shuttle route found.")
        return None

    for stop in route[1:]:
        travel_to_city(agent, stop["city"])

    dest = route[-1]
    walk_to_coords(agent, dest.get("x", 0), dest.get("y", 0))
    return dest
