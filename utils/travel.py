"""Basic movement helpers for navigating to waypoints."""

from __future__ import annotations

from typing import Iterable, Sequence, Tuple, Any, Optional

from modules.travel.location_selector import select_target
from src.movement.movement_profiles import walk_to_coords
from core.waypoint_verifier import verify_waypoint_stability as _verify_waypoint

Coords = Sequence[int]


def travel_to(planet: str, city: str, coords: Sequence[int]) -> None:
    print(f"[TRAVEL] Heading to {city}, {planet} at {coords}")
    # later: inject waypoints, trigger macro, interact with shuttle terminal


def go_to_waypoint(
    coords: Iterable[int], *, planet: str | None = None, city: str | None = None, agent: Any = None
) -> Optional[dict]:
    """Travel to ``coords`` optionally navigating to ``planet`` and ``city`` first."""

    if planet and city:
        select_target(planet, city, agent=agent)
    xy = tuple(coords)
    if len(xy) != 2:
        raise ValueError("coords must contain two values")
    x, y = xy
    walk_to_coords(agent, int(x), int(y))
    return {"x": int(x), "y": int(y)}


def verify_location(
    coords: Iterable[int], *, planet: str | None = None, city: str | None = None, agent: Any = None
) -> bool:
    """Verify that the player remains near ``coords``."""

    # ``planet`` and ``city`` parameters are currently unused but included for
    # API compatibility with :class:`core.TravelManager`.
    xy = tuple(coords)
    if len(xy) != 2:
        raise ValueError("coords must contain two values")
    return _verify_waypoint((int(xy[0]), int(xy[1])))
