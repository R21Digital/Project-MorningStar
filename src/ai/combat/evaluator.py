from typing import Dict


def evaluate_state(player_state: Dict, target_state: Dict) -> str:
    """Evaluate the current combat state and return a suggested action.

    Parameters
    ----------
    player_state:
        Dictionary describing the player's status. Expected keys are
        ``hp`` (hit points), ``has_heal`` to signal a healing item is
        available and ``is_buffed`` for whether a buff is active.
    target_state:
        Dictionary with the enemy's status. Only ``hp`` is currently
        consulted.

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

    hp = player_state.get("hp", 100)
    target_hp = target_state.get("hp", 100)
    has_healing_item = player_state.get("has_heal", False)
    is_buffed = player_state.get("is_buffed", False)

    if hp < 30 and has_healing_item:
        return "heal"
    if hp < 30:
        return "retreat"
    if target_hp > 0:
        return "attack"
    if not is_buffed:
        return "buff"
    return "idle"
