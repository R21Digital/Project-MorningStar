from typing import Dict


def should_heal(player: Dict) -> bool:
    return player.get("hp", 100) < 30 and player.get("has_heal", False)


def should_retreat(player: Dict) -> bool:
    return player.get("hp", 100) < 30 and not player.get("has_heal", False)


def should_attack(player: Dict, target: Dict) -> bool:
    return target.get("hp", 100) > 0 and player.get("hp", 100) >= 30


def should_buff(player: Dict, target: Dict) -> bool:
    return not player.get("is_buffed", False) and target.get("hp", 100) <= 0


def should_idle(player: Dict, target: Dict) -> bool:
    return target.get("hp", 100) <= 0
