"""Placeholder utilities for shuttle travel pathfinding."""

from __future__ import annotations

from typing import List

# --------------------------------------------------------------
def get_shuttle_path(from_city: str, to_city: str) -> List[str]:
    """Return the shuttle travel path from ``from_city`` to ``to_city``.

    This is a temporary stand-in for a future system that will
    compute optimal multi-hop shuttle routes between cities.
    """
    return [from_city, to_city]


__all__ = ["get_shuttle_path"]
