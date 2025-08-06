"""Waypoint utilities for movement routes."""

WAYPOINTS = {
    "Anchorhead-Loop": ["Anchorhead", "Wayfar", "Bestine", "Anchorhead"],
    "Theed-Bounce": ["Theed", "Moenia", "Theed"],
}


def get_waypoint_route(name: str):
    """Return the waypoint route list for ``name``."""
    return WAYPOINTS.get(name, [])

