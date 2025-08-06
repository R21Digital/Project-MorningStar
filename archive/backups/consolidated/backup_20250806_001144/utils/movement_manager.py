"""Simplified movement utilities used by the quest engine."""

CURRENT_LOCATION = {"planet": "tatooine"}


def travel_to(coords: list, planet: str | None = None) -> None:
    """Simulate traveling to ``coords`` on ``planet`` if provided."""
    x, y = coords
    current_planet = CURRENT_LOCATION["planet"]

    if planet and planet.lower() != current_planet.lower():
        print(
            f"[MOVEMENT] Taking shuttleport from {current_planet} to {planet}."
        )
        CURRENT_LOCATION["planet"] = planet
        current_planet = planet

    print(f"[MOVEMENT] Traveling to {current_planet} at coordinates ({x}, {y})")
    # Placeholder for pathing logic, shuttleport use, etc.
    # Can later hook into minimap clicker or NavMesh walker
