import time


from modules.quest_monitor import QuestMonitor


class DummyCollection:
    def __init__(self) -> None:
        self.updates = []

    def update_one(self, query, update, upsert=False):
        self.updates.append((query, update, upsert))


class DummyDB:
    def __init__(self) -> None:
        self.missions = DummyCollection()


def test_relocation_trigger(monkeypatch):
    db = DummyDB()
    monitor = QuestMonitor(timeout=10, db=db)
    t = [0]
    monkeypatch.setattr(time, "time", lambda: t[0])
    monitor.record_engagement()

    t[0] = 5
    assert monitor.check_relocation() is False

    t[0] = 15
    called = []
    monkeypatch.setattr(monitor, "sweep_area", lambda: called.append(True))
    assert monitor.check_relocation() is True
    assert called == [True]
    assert monitor.last_engagement == 15


def test_manual_override_resets(monkeypatch):
    db = DummyDB()
    monitor = QuestMonitor(timeout=10, db=db)
    t = [0]
    monkeypatch.setattr(time, "time", lambda: t[0])
    monitor.record_engagement()

    t[0] = 12
    monkeypatch.setattr(monitor, "update_waypoint", lambda c: db.missions.update_one({}, {"$set": {"coords": c}}, True))
    monitor.manual_override(lambda: True, lambda: (100, 200))
    assert db.missions.updates[-1][1]["$set"]["coords"] == (100, 200)
    assert monitor.last_engagement == 12

    t[0] = 20
    assert monitor.check_relocation() is False
