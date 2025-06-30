import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.ai.combat.evaluator import evaluate_state


def test_attack_when_healthy():
    state = {"player_hp": 80, "target_hp": 50}
    assert evaluate_state(state) == "attack"


def test_heal_when_low_hp_and_heal_item():
    state = {"player_hp": 20, "target_hp": 50, "has_heal": True}
    assert evaluate_state(state) == "heal"


def test_retreat_when_low_hp_and_no_heal():
    state = {"player_hp": 20, "target_hp": 50, "has_heal": False}
    assert evaluate_state(state) == "retreat"


def test_buff_when_no_target_and_not_buffed():
    state = {"player_hp": 100, "target_hp": 0, "is_buffed": False}
    assert evaluate_state(state) == "buff"


def test_idle_when_no_conditions_met():
    state = {"player_hp": 100, "target_hp": 0, "is_buffed": True}
    assert evaluate_state(state) == "idle"
