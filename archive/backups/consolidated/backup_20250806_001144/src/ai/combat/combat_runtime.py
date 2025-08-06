from typing import Dict

from .evaluator import evaluate_state


class CombatRunner:
    """Simple combat runtime wrapper around :func:`evaluate_state`.

    The runner keeps track of the action returned on the last call to
    :py:meth:`tick` via the :pyattr:`last_action` attribute. Recent actions are
    stored to help avoid repeating the same decision over and over.
    """

    def __init__(self, difficulty: str = "normal", behavior: str = "tactical", memory_size: int = 3) -> None:
        self.last_action: str | None = None
        self.recent_actions: list[str] = []
        self.difficulty = difficulty
        self.behavior = behavior
        self.memory_size = memory_size

    def tick(self, player_state: Dict, target_state: Dict) -> str:
        """Return the next action given player and target state.

        The returned value is stored on :pyattr:`last_action` for later
        inspection.
        """

        decision = evaluate_state(
            player_state=player_state,
            target_state=target_state,
            difficulty=self.difficulty,
            behavior=self.behavior,
            recent_actions=self.recent_actions,
        )

        self.last_action = decision
        self.recent_actions.append(decision)
        if len(self.recent_actions) > self.memory_size:
            self.recent_actions.pop(0)

        return decision
