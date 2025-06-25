import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.travel import shuttle


sample_data = {
    "tatooine": [
        {
            "city": "mos_eisley",
            "npc": "Shuttle Conductor",
            "x": 0,
            "y": 0,
            "destinations": [{"planet": "corellia", "city": "coronet"}],
        },
        {
            "city": "anchorhead",
            "npc": "Shuttle Attendant",
            "x": 100,
            "y": 0,
            "destinations": [{"planet": "tatooine", "city": "mos_eisley"}],
        },
    ],
    "corellia": [
        {
            "city": "coronet",
            "npc": "Shuttle Conductor",
            "x": 10,
            "y": 0,
            "destinations": [{"planet": "tatooine", "city": "mos_eisley"}],
        }
    ],
}


def test_nearest_shuttle():
    res = shuttle.nearest_shuttle((80, 0), "tatooine", sample_data)
    assert res["city"] == "anchorhead"


def test_plan_route_simple():
    route = shuttle.plan_route(
        "mos_eisley",
        "coronet",
        start_planet="tatooine",
        dest_planet="corellia",
        shuttle_data=sample_data,
    )
    assert [r["city"] for r in route] == ["mos_eisley", "coronet"]


def test_navigate_to_invokes_movement(monkeypatch):
    calls = []

    def fake_travel(agent, city):
        calls.append(("travel", city))

    def fake_walk(agent, x, y):
        calls.append(("walk", x, y))

    monkeypatch.setattr(shuttle, "travel_to_city", fake_travel)
    monkeypatch.setattr(shuttle, "walk_to_coords", fake_walk)
    monkeypatch.setattr(shuttle, "load_shuttles", lambda f=None: sample_data)

    shuttle.navigate_to(
        "coronet",
        agent="A",
        start_city="mos_eisley",
        start_planet="tatooine",
        dest_planet="corellia",
    )

    assert calls == [("travel", "coronet"), ("walk", 10, 0)]
