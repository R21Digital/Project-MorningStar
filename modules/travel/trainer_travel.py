"""High level travel helper for visiting profession trainers."""

from __future__ import annotations

from typing import Dict, Optional

from core.waypoint_verifier import verify_waypoint_stability
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

    entry = prof_entry[0]
    planet = entry.get("planet", DEFAULT_START_PLANET)
    city = entry.get("city", DEFAULT_START_CITY)
    coords = entry.get("coords") or [entry.get("x", 0), entry.get("y", 0)]
    dest_x, dest_y = coords

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
    verify_waypoint_stability((dest_x, dest_y))
    return result
