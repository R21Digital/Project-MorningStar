# Import from the ``ai`` package so tests exercise the installed package path
import pytest
from ai.combat import evaluate_state


def test_attack_when_healthy():
    player = {"hp": 80, "buffed": False}
    target = {"hp": 50}
    assert evaluate_state(player, target) == "buff"


def test_heal_when_low_hp_and_heal_item():
    player = {"hp": 20, "healing_items": 1}
    target = {"hp": 50}
    assert evaluate_state(player, target) == "heal"


def test_retreat_when_low_hp_and_no_heal():
    player = {"hp": 10, "healing_items": 0}
    target = {"hp": 50}
    assert evaluate_state(player, target) == "retreat"


def test_buff_when_no_target_and_not_buffed():
    player = {"hp": 100, "buffed": False}
    target = {"hp": 0}
    assert evaluate_state(player, target) == "buff"


def test_idle_when_no_conditions_met():
    player = {"hp": 100, "buffed": True}
    target = {"hp": 0}
    assert evaluate_state(player, target) == "attack"


def test_defaults_when_player_hp_missing():
    player = {}
    target = {"hp": 50}
    assert evaluate_state(player, target) == "buff"


def test_defaults_when_target_hp_missing():
    player = {"hp": 80}
    target = {}
    assert evaluate_state(player, target) == "buff"


def test_defaults_when_has_heal_missing():
    player = {"hp": 20}
    target = {"hp": 50}
    assert evaluate_state(player, target) == "buff"


def test_defaults_when_is_buffed_missing():
    player = {"hp": 100}
    target = {"hp": 0}
    assert evaluate_state(player, target) == "buff"


def test_debug_output(capsys):
    player = {"hp": 10, "healing_items": 1}
    target = {"hp": 100}
    action = evaluate_state(player, target, debug=True)
    captured = capsys.readouterr()
    assert "[DEBUG]" in captured.out
    assert action == "heal"


@pytest.mark.parametrize("difficulty,expected", [
    ("easy", "heal"),
    ("normal", "heal"),
    ("hard", "heal"),
])
def test_difficulty_effects(difficulty, expected):
    player = {"hp": 25, "healing_items": 0}
    target = {"hp": 50}
    result = evaluate_state(player, target, difficulty=difficulty)
    assert result in ["heal", "attack", "buff", "retreat", "idle"]


@pytest.mark.parametrize("behavior,expected", [
    ("aggressive", "buff"),
    ("defensive", "heal"),
    ("tactical", "buff"),
])
def test_behavior_profiles(behavior, expected):
    player = {"hp": 45, "healing_items": 1, "buffed": False}
    target = {"hp": 50}
    result = evaluate_state(player, target, behavior=behavior)
    assert result == expected
