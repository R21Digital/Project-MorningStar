import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.travel import trainer_travel
from scripts.travel import shuttle
from src.movement import movement_profiles


def test_travel_to_trainer_invokes_navigation(monkeypatch):
    calls = []

    def fake_nav(city, agent, start_city="mos_eisley", start_planet="tatooine", dest_planet=None, shuttle_file=None):
        calls.append(("nav", city, start_city, start_planet, dest_planet))
        return "NAV"

    def fake_walk(agent, x, y):
        calls.append(("walk", x, y))

    monkeypatch.setattr(shuttle, "navigate_to", fake_nav)
    monkeypatch.setattr(trainer_travel, "walk_to_coords", fake_walk)
    monkeypatch.setattr(shuttle, "plan_route", lambda *a, **k: [{"city": "mos_eisley"}, {"city": "coronet"}])

    data = {
        "artisan": [
            {"planet": "tatooine", "city": "mos_eisley", "name": "Trainer", "coords": [1, 2]}
        ]
    }
    result = trainer_travel.travel_to_trainer("artisan", data, agent="A")

    assert result == "NAV"
    assert calls == [
        ("nav", "mos_eisley", "mos_eisley", "tatooine", "tatooine"),
        ("walk", 1, 2),
    ]


def test_travel_to_trainer_logs_route(monkeypatch, capsys):
    monkeypatch.setattr(shuttle, "navigate_to", lambda *a, **k: None)
    monkeypatch.setattr(trainer_travel, "walk_to_coords", lambda *a, **k: None)
    monkeypatch.setattr(shuttle, "plan_route", lambda *a, **k: [{"city": "mos_eisley"}, {"city": "anchorhead"}])

    data = {
        "brawler": [
            {"planet": "tatooine", "city": "anchorhead", "name": "Brawl", "coords": [5, 6]}
        ]
    }
    trainer_travel.travel_to_trainer("brawler", data, agent="A")

    out = capsys.readouterr().out
    assert "mos_eisley -> anchorhead" in out
