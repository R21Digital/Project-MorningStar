from typing import Dict

from .evaluator import evaluate_state


class CombatRunner:
    """Simple combat runtime wrapper around :func:`evaluate_state`.

    The runner keeps track of the action returned on the last call to
    :py:meth:`tick` via the :pyattr:`last_action` attribute.
    """

    def __init__(self) -> None:
        self.last_action: str | None = None

    def tick(self, player_status: Dict, target_status: Dict) -> str:
        """Return the next action given player and target status.

        The returned value is stored on :pyattr:`last_action` for later
        inspection.
        """

        self.last_action = evaluate_state(player_status, target_status)
        return self.last_action
