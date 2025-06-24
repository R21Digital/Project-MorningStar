"""Strategy functions for common movement behaviors."""

from .agent_mover import MovementAgent


def travel_to_city(agent: MovementAgent, destination: str) -> None:
    """Move the agent directly to the given destination."""
    agent.destination = destination
    agent.move_to()


def patrol_route(agent: MovementAgent, route) -> None:
    """Patrol through each stop in the provided route."""
    for stop in route:
        agent.destination = stop
        agent.move_to()


def idle(agent: MovementAgent) -> None:
    """Perform no movement."""
    agent.session.add_action("Staying idle, no movement performed.")
