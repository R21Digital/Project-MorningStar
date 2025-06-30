import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.ai.combat.combat_runtime import CombatRunner


def test_tick_attack_action():
    runner = CombatRunner()
    player = {"hp": 80}
    target = {"hp": 40}
    assert runner.tick(player, target) == "attack"


def test_tick_heal_action_when_low_hp():
    runner = CombatRunner()
    player = {"hp": 15, "has_heal": True}
    target = {"hp": 60}
    assert runner.tick(player, target) == "heal"
