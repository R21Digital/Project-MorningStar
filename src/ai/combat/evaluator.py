from typing import Dict

from .strategies import (
    should_attack,
    should_buff,
    should_heal,
    should_idle,
    should_retreat,
)


def evaluate_state(player_state: Dict, target_state: Dict, debug: bool = False) -> str:
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

    if should_heal(player_state):
        if debug:
            print(
                f"Decision: heal (HP low and healing available) | player={player_state} | target={target_state}"
            )
        return "heal"
    elif should_retreat(player_state):
        if debug:
            print(
                f"Decision: retreat (HP low and no healing available) | player={player_state} | target={target_state}"
            )
        return "retreat"
    elif should_attack(player_state, target_state):
        if debug:
            print(
                f"Decision: attack (Target alive and player HP sufficient) | player={player_state} | target={target_state}"
            )
        return "attack"
    elif should_buff(player_state, target_state):
        if debug:
            print(
                f"Decision: buff (Player not buffed and target alive) | player={player_state} | target={target_state}"
            )
        return "buff"
    elif should_idle(player_state, target_state):
        if debug:
            print(
                f"Decision: idle (Target is dead) | player={player_state} | target={target_state}"
            )
        return "idle"

    if debug:
        print(
            f"Decision: idle (Default/fallback) | player={player_state} | target={target_state}"
        )
    return "idle"
