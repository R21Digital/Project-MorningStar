"""Strategy functions for common movement behaviors."""

from .agent_mover import MovementAgent
from .waypoints import get_waypoint_route


def travel_to_city(agent: MovementAgent, destination: str) -> None:
    """Move the agent directly to the given destination."""
    agent.destination = destination
    agent.move_to()


def patrol_route(agent: MovementAgent, route_name: str) -> None:
    """Patrol through the stops in the named waypoint route."""
    route = get_waypoint_route(route_name)
    if not route:
        agent.session.add_action(f"Route '{route_name}' not found.")
        return

    for stop in route:
        agent.destination = stop
        agent.move_to()


def idle(agent: MovementAgent) -> None:
    """Perform no movement."""
    agent.session.add_action("Staying idle, no movement performed.")
