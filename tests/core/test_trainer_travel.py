from core import (
    get_travel_macro,
    execute_travel_macro,
    start_travel_to_trainer,
    plan_travel_to_trainer,
    is_same_planet,
)
from utils.movement_manager import CURRENT_LOCATION


def test_get_travel_macro_formats():
    trainer = {"coords": [1234, -567], "name": "Medic Trainer"}
    assert get_travel_macro(trainer) == "/waypoint 1234.0 -567.0 Medic Trainer"


def test_start_travel_to_trainer_logs(monkeypatch):
    logs = []

    class DummyLogger:
        def info(self, msg, *args):
            logs.append(msg % args)

    import core.trainer_travel as tt
    monkeypatch.setattr(tt, "logger", DummyLogger())
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)

    trainer = {"coords": [10, 20], "name": "Trainer"}
    start_travel_to_trainer(trainer)

    assert any("/waypoint 10.0 20.0 Trainer" in m for m in logs)


def test_execute_travel_macro_logs(monkeypatch):
    logs = []

    class DummyLogger:
        def info(self, msg, *args):
            logs.append(msg % args)

    import core.trainer_travel as tt
    monkeypatch.setattr(tt, "logger", DummyLogger())
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)

    execute_travel_macro("/waypoint 1 2 Trainer")

    assert any("/waypoint 1 2 Trainer" in m for m in logs)


def test_is_same_planet_matching(monkeypatch):
    monkeypatch.setitem(CURRENT_LOCATION, "planet", "tatooine")
    assert is_same_planet({"planet": "Tatooine"}) is True


def test_is_same_planet_nonmatching(monkeypatch):
    monkeypatch.setitem(CURRENT_LOCATION, "planet", "tatooine")
    assert is_same_planet({"planet": "naboo"}) is False


def test_plan_travel_same_planet(monkeypatch):
    monkeypatch.setattr("core.trainer_travel.is_same_planet", lambda t: True)
    trainer = {"coords": [1, 2], "name": "Trainer", "planet": "tatooine"}
    steps = plan_travel_to_trainer(trainer)
    assert steps == [get_travel_macro(trainer)]


def test_plan_travel_remote(monkeypatch):
    monkeypatch.setattr("core.trainer_travel.is_same_planet", lambda t: False)
    trainer = {"coords": [1, 2], "name": "Trainer", "planet": "naboo"}
    steps = plan_travel_to_trainer(trainer)
    assert steps == [
        "Travel to shuttleport",
        "Fly to Naboo",
        "Waypoint to Trainer",
    ]


def test_plan_travel_to_trainer_same_planet_returns_macro(monkeypatch):
    monkeypatch.setattr("core.trainer_travel.is_same_planet", lambda t: True)
    trainer = {"coords": [50, 60], "name": "Combat Trainer", "planet": "tatooine"}
    steps = plan_travel_to_trainer(trainer)
    assert steps == [get_travel_macro(trainer)]


def test_plan_travel_to_trainer_different_planet(monkeypatch):
    monkeypatch.setattr("core.trainer_travel.is_same_planet", lambda t: False)
    trainer = {"coords": [80, 90], "name": "Scout Trainer", "planet": "dantooine"}
    steps = plan_travel_to_trainer(trainer)
    assert steps == [
        "Travel to shuttleport",
        "Fly to Dantooine",
        "Waypoint to Trainer",
    ]


def test_plan_travel_to_trainer_same_planet_returns_waypoint_macro(monkeypatch):
    monkeypatch.setattr("core.trainer_travel.is_same_planet", lambda t: True)
    trainer = {"coords": [12, 34], "name": "Ranged Trainer", "planet": "tatooine"}
    steps = plan_travel_to_trainer(trainer)
    assert steps == [get_travel_macro(trainer)]


def test_plan_travel_to_trainer_different_planet_lists_shuttle_steps(monkeypatch):
    monkeypatch.setattr("core.trainer_travel.is_same_planet", lambda t: False)
    trainer = {"coords": [45, 56], "name": "Remote Trainer", "planet": "corellia"}
    steps = plan_travel_to_trainer(trainer)
    assert steps == [
        "Travel to shuttleport",
        "Fly to Corellia",
        "Waypoint to Trainer",
    ]
