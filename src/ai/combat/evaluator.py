from typing import Dict


def evaluate_state(state: Dict) -> str:
    """Evaluate the current combat state and return a suggested action."""
    hp = state.get("player_hp", 100)
    target_hp = state.get("target_hp", 100)
    has_healing_item = state.get("has_heal", False)
    is_buffed = state.get("is_buffed", False)

    if hp < 30 and has_healing_item:
        return "heal"
    if hp < 30:
        return "retreat"
    if target_hp > 0:
        return "attack"
    if not is_buffed:
        return "buff"
    return "idle"
