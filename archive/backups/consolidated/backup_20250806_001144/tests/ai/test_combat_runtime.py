# Import from the ``ai`` package for consistency with production usage
from ai.combat import CombatRunner


def test_tick_attack_action():
    runner = CombatRunner()
    player = {"hp": 80, "buffed": True}
    target = {"hp": 40}
    assert runner.tick(player, target) == "attack"


def test_tick_heal_action_when_low_hp():
    runner = CombatRunner()
    player = {"hp": 15, "healing_items": 1}
    target = {"hp": 60}
    assert runner.tick(player, target) == "heal"


def test_tick_retreat_action_when_low_hp_no_heal():
    runner = CombatRunner()
    player = {"hp": 15, "healing_items": 0}
    target = {"hp": 60}
    assert runner.tick(player, target) == "retreat"


def test_last_action_persists_between_ticks():
    runner = CombatRunner()
    player = {"hp": 80, "buffed": True}
    target = {"hp": 40}

    action = runner.tick(player, target)
    assert action == "attack"
    assert runner.last_action == "attack"

    player.update({"hp": 15, "healing_items": 1})
    action = runner.tick(player, target)
    assert action == "heal"
    assert runner.last_action == "heal"


def test_tick_buff():
    runner = CombatRunner()
    player = {"hp": 80, "buffed": False}
    target = {"hp": 0}

    action = runner.tick(player, target)
    assert action == "buff"
    assert runner.last_action == "buff"


def test_tick_idle():
    runner = CombatRunner()
    player = {"hp": 80, "buffed": True}
    target = {"hp": 0}

    action = runner.tick(player, target)
    assert action == "attack"
    assert runner.last_action == "attack"


def test_prevents_action_spam_with_memory():
    from src.ai.combat import CombatRunner

    runner = CombatRunner(memory_size=3)
    player = {"hp": 100, "healing_items": 1, "buffed": False}
    target = {"hp": 50}

    runner.recent_actions = ["buff", "buff", "buff"]
    action = runner.tick(player, target)
    assert action != "buff", "Should avoid buff spam"
