"""Shuttle travel utilities."""

from __future__ import annotations

import json
import os
from collections import deque
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from src.movement.movement_profiles import travel_to_city, walk_to_coords

# Path to the default shuttle configuration file under ``data``.
SHUTTLE_FILE = Path(__file__).resolve().parents[1] / "data" / "shuttles.json"

# Type aliases for clarity
Coords = Tuple[int, int]
ShuttleEntry = Dict[str, object]


def load_shuttles(shuttle_file: Optional[str] = None) -> Dict[str, List[ShuttleEntry]]:
    """Return shuttle configuration data from ``shuttle_file``.

    The ``SHUTTLE_FILE`` environment variable overrides the default path.
    """
    env_override = os.environ.get("SHUTTLE_FILE")
    path = Path(shuttle_file or env_override or SHUTTLE_FILE)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        return {}


def _distance(a: Coords, b: Coords) -> float:
    """Return the Euclidean distance between two points."""
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def _lookup_entry(data: Dict[str, List[ShuttleEntry]], planet: str, city: str) -> Optional[ShuttleEntry]:
    for entry in data.get(planet, []):
        if entry.get("city") == city:
            return entry
    return None


def nearest_shuttle(
    position: Coords, planet: str, shuttle_data: Optional[Dict[str, List[ShuttleEntry]]] = None
) -> Optional[ShuttleEntry]:
    """Return the closest shuttle entry to ``position`` on ``planet``."""
    data = shuttle_data or load_shuttles()
    best: Optional[ShuttleEntry] = None
    for entry in data.get(planet, []):
        dist = _distance(position, (entry.get("x", 0), entry.get("y", 0)))
        if best is None or dist < best.get("distance", float("inf")):
            best = dict(entry)
            best["distance"] = dist
    return best


def plan_route(
    start_city: str,
    dest_city: str,
    *,
    start_planet: str = "tatooine",
    dest_planet: Optional[str] = None,
    shuttle_data: Optional[Dict[str, List[ShuttleEntry]]] = None,
) -> List[ShuttleEntry]:
    """Return the shuttle stops needed to travel from ``start_city`` to ``dest_city``."""
    data = shuttle_data or load_shuttles()
    if dest_planet is None:
        dest_planet = start_planet

    graph = {}
    for planet, entries in data.items():
        for entry in entries:
            node = (planet, entry.get("city"))
            graph[node] = [(d["planet"], d["city"]) for d in entry.get("destinations", [])]

    start = (start_planet, start_city)
    dest = (dest_planet, dest_city)

    queue: deque[Tuple[Tuple[str, str], List[Tuple[str, str]]]] = deque([(start, [start])])
    visited = set()

    while queue:
        node, path = queue.popleft()
        if node == dest:
            result = []
            for p, c in path:
                entry = _lookup_entry(data, p, c) or {"city": c, "x": 0, "y": 0}
                result.append({"planet": p, **entry})
            return result
        if node in visited:
            continue
        visited.add(node)
        for nxt in graph.get(node, []):
            if nxt not in visited:
                queue.append((nxt, path + [nxt]))
    return []


def navigate_to(
    city: str,
    agent,
    *,
    start_city: str = "mos_eisley",
    start_planet: str = "tatooine",
    dest_planet: Optional[str] = None,
    shuttle_file: Optional[str] = None,
) -> None:
    """Travel to ``city`` then walk to its shuttle coordinates."""
    data = load_shuttles(shuttle_file)
    route = plan_route(
        start_city,
        city,
        start_planet=start_planet,
        dest_planet=dest_planet or start_planet,
        shuttle_data=data,
    )
    if not route:
        return

    # Walk the route one city at a time
    for stop in route[1:]:
        travel_to_city(agent, stop["city"])

    dest_entry = route[-1]
    walk_to_coords(agent, dest_entry.get("x", 0), dest_entry.get("y", 0))
