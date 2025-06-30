from typing import Dict

from .strategies import (
    should_buff,
    should_idle,
)


def evaluate_state(
    player_state: Dict,
    target_state: Dict,
    debug: bool = False,
    difficulty: str = "normal",
) -> str:
    """Evaluate the current combat state and return a suggested action.

    Set ``debug`` to ``True`` to print the chosen decision and relevant
    state information. This can help when troubleshooting combat logic.

    Parameters
    ----------
    player_state:
        Dictionary describing the player's status. ``hp`` (hit points)
        defaults to ``100`` when not provided. ``has_heal`` and
        ``is_buffed`` default to ``False`` if missing.
    target_state:
        Dictionary with the enemy's status. Only ``hp`` is currently
        consulted and it defaults to ``100`` when absent.

    Returns
    -------
    str
        One of the following action strings:

        ``"heal"``
            The player should use a healing item when low on HP and a heal is
            available.
        ``"retreat"``
            The player is low on HP and has no heal available, so the best
            option is to retreat.
        ``"attack"``
            The enemy still has HP remaining and the player is healthy enough
            to continue attacking.
        ``"buff"``
            The player is safe but lacks a buff, so applying one is
            recommended.
        ``"idle"``
            No specific action is required because the encounter is over and
            the player is already buffed.
    """

    # Difficulty-based HP threshold for low health decisions
    low_hp = player_state.get("hp", 100) < {
        "easy": 50,
        "normal": 30,
        "hard": 20,
    }.get(difficulty, 30)

    has_heal = player_state.get("has_heal", False)

    attack_threshold = {"easy": 30, "normal": 30, "hard": 20}.get(difficulty, 30)
    attack_ready = target_state.get("hp", 100) > 0 and player_state.get("hp", 100) >= attack_threshold

    if low_hp and has_heal:
        if debug:
            print(f"[{difficulty.upper()}] Decision: heal")
        return "heal"
    elif low_hp and not has_heal and difficulty != "hard":
        if debug:
            print(f"[{difficulty.upper()}] Decision: retreat")
        return "retreat"
    elif attack_ready:
        if debug:
            print(f"[{difficulty.upper()}] Decision: attack")
        return "attack"
    elif difficulty != "easy" and should_buff(player_state, target_state):
        if debug:
            print(f"[{difficulty.upper()}] Decision: buff")
        return "buff"
    elif should_idle(player_state, target_state):
        if debug:
            print(f"[{difficulty.upper()}] Decision: idle")
        return "idle"

    if debug:
        print(f"[{difficulty.upper()}] Decision: idle (fallback)")
    return "idle"
