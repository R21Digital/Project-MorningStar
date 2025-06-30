from typing import Dict

from .evaluator import evaluate_state


class CombatRunner:
    """Simple combat runtime wrapper around :func:`evaluate_state`."""

    def tick(self, player_status: Dict, target_status: Dict) -> str:
        """Return the next action given player and target status."""
        state = {
            "player_hp": player_status.get("hp", 100),
            "has_heal": player_status.get("has_heal", False),
            "is_buffed": player_status.get("is_buffed", False),
            "target_hp": target_status.get("hp", 100),
        }
        return evaluate_state(state)
