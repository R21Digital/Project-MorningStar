import os
import sys
import json


from core.profession_leveler import ProfessionLeveler
from core.travel_manager import TravelManager


def test_level_all_professions_skips_unknown(monkeypatch, tmp_path):
    plan = ["artisan", "missing"]
    plan_file = tmp_path / "plan.json"
    plan_file.write_text(json.dumps(plan))

    monkeypatch.setattr(TravelManager, "load_trainers", lambda self: None)
    lvl = ProfessionLeveler("dummy.json", str(plan_file))
    lvl.travel_manager.trainers = {"artisan": {}}

    calls = []
    monkeypatch.setattr(lvl, "level_profession", lambda prof: calls.append(prof))

    logs = []

    class DummyLogger:
        def info(self, msg, *args):
            logs.append(msg % args)

    monkeypatch.setattr("core.profession_leveler.logger", DummyLogger())

    lvl.level_all_professions()
    assert calls == ["artisan"]
    assert "[Leveler] No trainer entry for missing" in logs


def test_level_profession_invokes_training(monkeypatch, tmp_path):
    plan_file = tmp_path / "plan.json"
    plan_file.write_text("[]")

    monkeypatch.setattr(TravelManager, "load_trainers", lambda self: None)
    lvl = ProfessionLeveler("dummy.json", str(plan_file))
    lvl.travel_manager.trainers = {"artisan": {}}

    tm_calls = {}

    def fake_scan():
        tm_calls.setdefault("scan", True)
        return ["Skill"]

    monkeypatch.setattr(lvl.travel_manager.trainer_scanner, "scan", fake_scan)
    monkeypatch.setattr(
        lvl.travel_manager,
        "train_profession",
        lambda prof: tm_calls.setdefault("train", prof),
    )

    logs = []

    class DummyLogger:
        def info(self, msg, *args):
            logs.append(msg % args)

    monkeypatch.setattr("core.profession_leveler.logger", DummyLogger())

    skills = lvl.level_profession("artisan")

    assert tm_calls["train"] == "artisan"
    assert tm_calls["scan"] is True
    assert skills == ["Skill"]
    assert "[Leveler] artisan trainer offers: ['Skill']" in logs
