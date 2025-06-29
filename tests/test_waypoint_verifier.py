import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.waypoint_verifier import verify_waypoint


def test_verify_waypoint_stable(monkeypatch):
    calls = {"count": 0}

    def fake_detect():
        calls["count"] += 1
        return (100, 100)

    monkeypatch.setattr("utils.waypoint_verifier._detect_position", fake_detect)
    monkeypatch.setattr("time.sleep", lambda *_: None)

    assert verify_waypoint((100, 100)) is True
    assert calls["count"] == 2


def test_verify_waypoint_moved(monkeypatch):
    positions = [(100, 100), (105, 100)]

    def fake_detect():
        return positions.pop(0)

    monkeypatch.setattr("utils.waypoint_verifier._detect_position", fake_detect)
    monkeypatch.setattr("time.sleep", lambda *_: None)

    assert verify_waypoint((100, 100)) is False

