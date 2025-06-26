"""High level travel helper for visiting profession trainers."""

from __future__ import annotations

from typing import Dict, Optional

from scripts.travel import shuttle
from src.movement.movement_profiles import walk_to_coords


DEFAULT_START_CITY = "mos_eisley"
DEFAULT_START_PLANET = "tatooine"


def travel_to_trainer(profession: str, trainer_data: Dict[str, dict], agent=None):
    """Travel via shuttle to the trainer for ``profession``.

    Parameters
    ----------
    profession:
        Name of the profession to look up.
    trainer_data:
        Mapping of profession information typically returned by
        ``utils.load_trainers.load_trainers``.
    agent:
        Optional movement agent passed to the underlying navigation helpers.

    Returns
    -------
    object
        Whatever value :func:`scripts.travel.shuttle.navigate_to` returns.
    """
    prof_entry = trainer_data.get(profession)
    if not prof_entry:
        print(f"[Travel] No trainer data for {profession}")
        return None

    # Pick the first available planet/city entry
    planet, cities = next(iter(prof_entry.items()))
    city, entry = next(iter(cities.items()))
    dest_x = entry.get("x", 0)
    dest_y = entry.get("y", 0)

    # Plan the shuttle route so we can log the chosen path
    route = shuttle.plan_route(
        DEFAULT_START_CITY,
        city,
        start_planet=DEFAULT_START_PLANET,
        dest_planet=planet,
    )
    if route:
        path = " -> ".join(stop["city"] for stop in route)
        print(f"[Travel] Planned shuttle route: {path}")
    else:
        print("[Travel] No shuttle route found.")

    result = shuttle.navigate_to(
        city,
        agent=agent,
        start_city=DEFAULT_START_CITY,
        start_planet=DEFAULT_START_PLANET,
        dest_planet=planet,
    )

    walk_to_coords(agent, dest_x, dest_y)
    return result
