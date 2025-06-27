"""Simplified movement utilities used by the quest engine."""


def travel_to(zone: str, coords: list) -> None:
    """Simulate traveling to a set of coordinates."""
    x, y = coords
    print(f"[MOVEMENT] Traveling to {zone} at coordinates ({x}, {y})")
    # Placeholder for pathing logic, shuttleport use, etc.
    # Can later hook into minimap clicker or NavMesh walker
