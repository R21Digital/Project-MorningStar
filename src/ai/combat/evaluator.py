from typing import Dict, List


def is_spamming(action: str, recent_actions: List[str], limit: int = 2) -> bool:
    """Return True if the action appears ``limit`` or more times in history."""

    return recent_actions.count(action) >= limit


def evaluate_state(
    player_state: Dict,
    target_state: Dict,
    difficulty: str = "normal",
    behavior: str = "tactical",
    debug: bool = False,
    recent_actions: List[str] | None = None,
) -> str:
    """Evaluate the current combat state and return a suggested action.

    Parameters
    ----------
    player_state:
        Dictionary describing the player's status. ``hp`` defaults to ``100``.
        Healing items can be specified via ``healing_items`` or the legacy
        ``has_heal`` boolean. Buff status can be provided as ``buffed`` or the
        older ``is_buffed`` key.
    target_state:
        Dictionary with the enemy's status. Only ``hp`` is currently consulted
        and it defaults to ``100`` when absent.
    recent_actions:
        Sequence of previous actions used to prevent spamming the same
        decision repeatedly.
    """

    recent_actions = list(recent_actions or [])

    hp = player_state.get("hp", 100)

    healing_count = player_state.get("healing_items")
    if healing_count is None:
        healing_count = 1 if player_state.get("has_heal", False) else 0
    has_healing = healing_count > 0

    is_buffed = player_state.get(
        "buffed",
        player_state.get("is_buffed", False),
    )
    target_hp = target_state.get("hp", 100)

    if debug:
        print(
            f"[DEBUG] HP: {hp}, Target HP: {target_hp}, Behavior: {behavior}, Recent Actions: {recent_actions}"
        )

    behavior = behavior.lower()

    if behavior == "aggressive":
        if target_hp < 20 and not is_spamming("attack", recent_actions):
            return "attack"
        if not is_buffed and not is_spamming("buff", recent_actions):
            return "buff"
        return "attack"

    if behavior == "defensive":
        if hp < 50 and has_healing and not is_spamming("heal", recent_actions):
            return "heal"
        if not is_buffed and not is_spamming("buff", recent_actions):
            return "buff"
        if hp < 30:
            return "retreat"
        return "idle"

    # Tactical default
    if hp < 35 and has_healing and not is_spamming("heal", recent_actions):
        return "heal"
    if hp < 20 and not has_healing:
        return "retreat"
    if not is_buffed and not is_spamming("buff", recent_actions):
        return "buff"
    if not is_spamming("attack", recent_actions):
        return "attack"
    return "idle"
