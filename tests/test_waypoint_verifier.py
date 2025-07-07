

from core.waypoint_verifier import verify_waypoint_stability


def test_verify_waypoint_stable(monkeypatch):
    calls = {"count": 0}

    def fake_detect():
        calls["count"] += 1
        return (100, 100)

    monkeypatch.setattr("core.waypoint_verifier._detect_position", fake_detect)
    monkeypatch.setattr("time.sleep", lambda *_: None)

    logs = []

    class DummyLogger:
        def info(self, msg, *args):
            logs.append(msg % args)

    monkeypatch.setattr("core.waypoint_verifier.logger", DummyLogger())

    assert verify_waypoint_stability((100, 100)) is True
    assert calls["count"] == 2
    assert "[WaypointVerifier] Position stable at (100, 100)." in logs


def test_verify_waypoint_moved(monkeypatch):
    positions = [(100, 100), (105, 100)]

    def fake_detect():
        return positions.pop(0)

    monkeypatch.setattr("core.waypoint_verifier._detect_position", fake_detect)
    monkeypatch.setattr("time.sleep", lambda *_: None)

    logs = []

    class DummyLogger:
        def info(self, msg, *args):
            logs.append(msg % args)

    monkeypatch.setattr("core.waypoint_verifier.logger", DummyLogger())

    assert verify_waypoint_stability((100, 100)) is False
    assert "distance increased" in logs[0]
