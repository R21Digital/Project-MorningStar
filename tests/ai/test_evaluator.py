import os
import sys


from src.ai.combat.evaluator import evaluate_state


def test_attack_when_healthy():
    player = {"hp": 80}
    target = {"hp": 50}
    assert evaluate_state(player, target) == "attack"


def test_heal_when_low_hp_and_heal_item():
    player = {"hp": 20, "has_heal": True}
    target = {"hp": 50}
    assert evaluate_state(player, target) == "heal"


def test_retreat_when_low_hp_and_no_heal():
    player = {"hp": 20, "has_heal": False}
    target = {"hp": 50}
    assert evaluate_state(player, target) == "retreat"


def test_buff_when_no_target_and_not_buffed():
    player = {"hp": 100, "is_buffed": False}
    target = {"hp": 0}
    assert evaluate_state(player, target) == "buff"


def test_idle_when_no_conditions_met():
    player = {"hp": 100, "is_buffed": True}
    target = {"hp": 0}
    assert evaluate_state(player, target) == "idle"
