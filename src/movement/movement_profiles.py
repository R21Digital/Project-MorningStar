"""Strategy functions for common movement behaviors."""

from .agent_mover import MovementAgent
from .waypoints import get_waypoint_route
import time
import random


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

        # Simulate human-like pause between moves
        wait_time = random.uniform(5.0, 15.0)
        agent.session.add_action(
            f"Waiting {wait_time:.1f} seconds before next move."
        )
        time.sleep(wait_time)


def idle(agent: MovementAgent) -> None:
    """Perform no movement."""
    agent.session.add_action("Staying idle, no movement performed.")


def walk_to_coords(agent: MovementAgent, x: int, y: int) -> None:
    """Walk the agent to the specified ``x`` and ``y`` coordinates."""

    print(f"[Movement] Walking to coordinates: ({x}, {y})...")

    # TODO: Implement screen recognition & WASD walking here
    import time

    time.sleep(2)
    print("[Movement] Arrived at destination.")
