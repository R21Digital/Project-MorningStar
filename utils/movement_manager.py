"""Simplified movement utilities used by the quest engine."""

def travel_to(zone: str, coords: tuple[int, int]) -> None:
    """Simulate traveling to a set of coordinates."""
    x, y = coords
    print(f"[MOVE] Traveling to {zone} at ({x}, {y})")
