from typing import Dict

from .evaluator import evaluate_state


class CombatRunner:
    """Simple combat runtime wrapper around :func:`evaluate_state`."""

    def tick(self, player_status: Dict, target_status: Dict) -> str:
        """Return the next action given player and target status."""
        return evaluate_state(player_status, target_status)
