from typing import Dict

from .evaluator import evaluate_state


class CombatRunner:
    """Simple combat runtime wrapper around :func:`evaluate_state`.

    The runner keeps track of the action returned on the last call to
    :py:meth:`tick` via the :pyattr:`last_action` attribute.
    """

    def __init__(self) -> None:
        self.last_action: str | None = None

    def tick(self, player_state: Dict, target_state: Dict) -> str:
        """Return the next action given player and target state.

        The returned value is stored on :pyattr:`last_action` for later
        inspection.
        """

        self.last_action = evaluate_state(player_state, target_state)
        return self.last_action
