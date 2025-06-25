# -*- coding: utf-8 -*-
"""Helper utilities for navigating to profession trainers.

The module provides functions to locate trainers relative to the player's
current position and log training interactions.  It relies on
``utils.load_trainers.load_trainers`` for loading the trainer location
data from ``data/trainers.yaml`` or an overridden path.
"""

from __future__ import annotations

import math
import os
from datetime import datetime
from typing import Dict, Iterable, List, Optional, Tuple

from utils.load_trainers import load_trainers

# Default log file under the project's ``logs`` directory.
DEFAULT_LOG_PATH = os.path.join("logs", "training_log.txt")

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

    for profession, planets in data.items():
        planet_data = planets.get(planet, {})
        entry = planet_data.get(city)
        if not entry:
            continue
        trainer_coords = (entry.get("x"), entry.get("y"))
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
) -> None:
    """Append a training event to ``log_path`` with a timestamp."""
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

