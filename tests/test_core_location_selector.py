

from core import location_selector


def test_travel_to_target_invokes_helpers(monkeypatch):
    calls = []

    def fake_select(planet, city, agent=None):
        calls.append(("select", planet, city))
        return {"city": city}

    def fake_walk(agent, x, y):
        calls.append(("walk", x, y))

    monkeypatch.setattr(location_selector, "select_target", fake_select)
    monkeypatch.setattr(location_selector, "locate_hotspot", lambda *a, **k: (1, 2))
    monkeypatch.setattr(location_selector, "walk_to_coords", fake_walk)

    target = {"planet": "corellia", "city": "coronet", "hotspot": "cantina"}
    location_selector.travel_to_target(target, agent="A")

    assert calls == [("select", "corellia", "coronet"), ("walk", 1, 2)]


def test_travel_to_target_no_coords(monkeypatch):
    calls = []

    def fake_select(planet, city, agent=None):
        calls.append(("select", planet, city))
        return {"city": city}

    monkeypatch.setattr(location_selector, "select_target", fake_select)
    monkeypatch.setattr(location_selector, "locate_hotspot", lambda *a, **k: None)
    monkeypatch.setattr(
        location_selector, "walk_to_coords", lambda *a, **k: calls.append(("walk",))
    )

    target = {"planet": "corellia", "city": "coronet"}
    location_selector.travel_to_target(target, agent="A")

    assert calls == [("select", "corellia", "coronet")]
