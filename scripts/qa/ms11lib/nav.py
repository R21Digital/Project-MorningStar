from __future__ import annotations

from typing import List, Tuple


def is_mesh_available() -> bool:
    # Placeholder. Later: verify navmesh files for current zone
    return True


def find_path(start: Tuple[float, float], end: Tuple[float, float]) -> List[Tuple[float, float]]:
    # Placeholder for future mesh pathing. Return direct segment for now.
    return [start, end]


