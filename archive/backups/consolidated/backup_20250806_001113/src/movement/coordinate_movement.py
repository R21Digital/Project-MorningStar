"""Helpers for coordinate-based movement."""

from .agent_mover import MovementAgent


def move_to_coordinates(agent: MovementAgent, x: int, y: int) -> None:
    """Move ``agent`` to the given ``x``/``y`` coordinates.

    This function simply prints a message and records the action using the
    agent's session. It does not attempt to simulate any game-specific
    navigation logic.
    """
    action = f"Moving to coordinates ({x}, {y})"
    print(action)
    agent.session.add_action(action)
