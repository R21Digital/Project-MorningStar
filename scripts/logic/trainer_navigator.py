# -*- coding: utf-8 -*-
"""Helper utilities for navigating to profession trainers.

The module provides functions to locate trainers relative to the player's
current position and log training interactions.  It relies on
``utils.load_trainers.load_trainers`` for loading the trainer location
data from ``data/trainers.json`` or an overridden path.
"""

from __future__ import annotations

import math
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from utils.load_trainers import load_trainers
from utils.get_trainer_location import get_trainer_location
from src.training.trainer_visit import visit_trainer
from src.utils.logger import log_event

# Default log files under the project's ``logs`` directory.
DEFAULT_LOG_PATH = os.path.join("logs", "training_log.txt")
DEFAULT_JSON_PATH = os.path.join("logs", "training.json")

# Type aliases for clarity
Coords = Tuple[int, int]
TrainerEntry = Dict[str, int | str]


def _distance(a: Coords, b: Coords) -> float:
    """Return the Euclidean distance between two ``(x, y)`` points."""
    return math.hypot(a[0] - b[0], a[1] - b[1])


def find_nearby_trainers(
    player_pos: Coords,
    planet: str,
    city: str,
    *,
    threshold: float = 1000.0,
    trainer_file: Optional[str] = None,
) -> List[Dict[str, object]]:
    """Return trainers within ``threshold`` distance of ``player_pos``.

    The returned list contains dictionaries with ``profession``, ``name``,
    ``x``, ``y`` and ``distance`` keys sorted by distance.
    """
    # Delegate reading trainer data to :func:`utils.load_trainers.load_trainers`
    # so callers benefit from environment variable overrides and consistent
    # path handling.
    data = load_trainers(trainer_file)
    results: List[Dict[str, object]] = []

    for profession, entries in data.items():
        for entry in entries:
            if (
                entry.get("planet", "").lower() != planet.lower()
                or entry.get("city", "").lower() != city.lower()
            ):
                continue
            coords = entry.get("coords") or [entry.get("x"), entry.get("y")]
            trainer_coords = (coords[0], coords[1])
            dist = _distance(player_pos, trainer_coords)
            if dist <= threshold:
                results.append(
                    {
                        "profession": profession,
                        "name": entry.get("name", "Unknown"),
                        "x": trainer_coords[0],
                        "y": trainer_coords[1],
                        "distance": dist,
                    }
                )

    results.sort(key=lambda r: r["distance"])  # closest first
    return results


def log_training_event(
    profession: str,
    trainer_name: str,
    distance: float,
    log_path: str = DEFAULT_LOG_PATH,
    *,
    json_path: Optional[str] = None,
) -> None:
    """Append a training event to ``log_path`` with a timestamp.

    If ``json_path`` is provided, the event is also appended as JSON to that
    file (one object per line).
    """
    if os.path.abspath(log_path) == os.path.abspath(DEFAULT_LOG_PATH):
        # Ensure the default ``logs`` directory exists when writing the
        # standard ``training_log.txt`` file.
        os.makedirs("logs", exist_ok=True)
    else:
        dir_name = os.path.dirname(log_path)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
    timestamp = datetime.now().isoformat()
    message = f"{timestamp} - Trained with {trainer_name} ({profession}) at distance {distance:.1f}\n"
    with open(log_path, "a", encoding="utf-8") as fh:
        fh.write(message)

    if json_path:
        if os.path.abspath(json_path) == os.path.abspath(DEFAULT_JSON_PATH):
            os.makedirs("logs", exist_ok=True)
        else:
            dir_name = os.path.dirname(json_path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
        entry = {
            "timestamp": timestamp,
            "profession": profession,
            "trainer": trainer_name,
            "distance": distance,
        }
        with open(json_path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")


def navigate_to_trainer(
    trainer_name: str, planet: str, city: str, agent
) -> Optional[Tuple[str, int, int]]:
    """Travel to the requested trainer and log the visit.

    The function looks up coordinates using :func:`utils.get_trainer_location`
    or :func:`utils.load_trainers.load_trainers`.  It then delegates movement to
    :func:`src.training.trainer_visit.visit_trainer` and records the trip with
    :func:`log_training_event`.
    """

    log_event(f"Starting trainer visit: {trainer_name} in {city}, {planet}")

    location = get_trainer_location(trainer_name, planet, city)
    if not location:
        data = load_trainers()
        location = None
        for entry in data.get(trainer_name, []):
            if (
                entry.get("planet", "").lower() == planet.lower()
                and entry.get("city", "").lower() == city.lower()
            ):
                coords = entry.get("coords") or [entry.get("x"), entry.get("y")]
                location = (
                    entry.get("name", f"{trainer_name} trainer"),
                    coords[0],
                    coords[1],
                )
                break

    visit_trainer(agent, trainer_name, planet=planet, city=city)

    if location:
        log_training_event(trainer_name, location[0], 0.0)
    else:
        log_training_event(trainer_name, f"{trainer_name} trainer", 0.0)

    log_event(f"Completed trainer visit: {trainer_name} in {city}, {planet}")

    return location

