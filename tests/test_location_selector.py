import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.travel import location_selector
from scripts.travel import shuttle


def test_select_target_invokes_movement(monkeypatch):
    calls = []

    def fake_travel(agent, city):
        calls.append(("travel", city))

    def fake_walk(agent, x, y):
        calls.append(("walk", x, y))

    monkeypatch.setattr(location_selector, "travel_to_city", fake_travel)
    monkeypatch.setattr(location_selector, "walk_to_coords", fake_walk)
    monkeypatch.setattr(
        shuttle,
        "plan_route",
        lambda *a, **k: [
            {"city": "mos_eisley"},
            {"city": "coronet", "x": 5, "y": 6},
        ],
    )

    location_selector.select_target("corellia", "coronet", agent="A")

    assert calls == [("travel", "coronet"), ("walk", 5, 6)]


def test_select_target_multi_stop(monkeypatch):
    calls = []

    def fake_travel(agent, city):
        calls.append(("travel", city))

    def fake_walk(agent, x, y):
        calls.append(("walk", x, y))

    monkeypatch.setattr(location_selector, "travel_to_city", fake_travel)
    monkeypatch.setattr(location_selector, "walk_to_coords", fake_walk)
    monkeypatch.setattr(
        shuttle,
        "plan_route",
        lambda *a, **k: [
            {"city": "mos_eisley"},
            {"city": "anchorhead"},
            {"city": "coronet", "x": 1, "y": 2},
        ],
    )

    location_selector.select_target("corellia", "coronet", agent="A")

    assert calls == [
        ("travel", "anchorhead"),
        ("travel", "coronet"),
        ("walk", 1, 2),
    ]
