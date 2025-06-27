import os
import sys
import bs4

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.profession_manager import ProfessionManager
import utils.ocr_scanner as ocr_scanner


def test_train_missing_skills_travels(monkeypatch):
    pm = ProfessionManager()
    calls = {}

    monkeypatch.setattr("core.profession_manager.scan_skills_ui", lambda: [])

    def fake_travel(coords, planet=None):
        calls.setdefault("travel", []).append((coords, planet))

    def fake_interact(name, skill):
        calls.setdefault("interact", []).append((name, skill))
        return True

    monkeypatch.setattr("core.profession_manager.travel_to", fake_travel)
    monkeypatch.setattr("core.profession_manager.interact_with_trainer", fake_interact)

    pm.train_missing_skills()

    assert calls["travel"][0][1] == "tatooine"
    assert calls["travel"][0][0] == [3432, -4795]
    assert calls["interact"][0] == ("Artisan Trainer", "Novice Artisan")


def test_train_missing_skills_no_action(monkeypatch):
    pm = ProfessionManager()
    monkeypatch.setattr(
        "core.profession_manager.scan_skills_ui",
        lambda: ["Novice Artisan", "Novice Marksman"],
    )

    called = False

    def fake_travel(*a, **k):
        nonlocal called
        called = True

    monkeypatch.setattr("core.profession_manager.travel_to", fake_travel)
    monkeypatch.setattr(
        "core.profession_manager.interact_with_trainer", lambda n, s: True
    )

    pm.train_missing_skills()

    assert not called
