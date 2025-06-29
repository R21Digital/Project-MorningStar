import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from android_ms11.modes import quest_mode, combat_assist_mode


class DummySession:
    def __init__(self):
        self.actions = []
        self.profile = {"build": {"skills": []}}

    def add_action(self, action: str):
        self.actions.append(action)

    def set_start_credits(self, *a, **k):
        pass

    def set_end_credits(self, *a, **k):
        pass

    def end_session(self):
        pass


def test_quest_mode_run_invokes_utils(monkeypatch):
    called = {}
    monkeypatch.setattr(quest_mode, "select_quest", lambda name: {"title": "Demo", "steps": []})

    def fake_exec(q, dry_run=True):
        called["quest"] = q
    monkeypatch.setattr(quest_mode, "execute_quest", fake_exec)

    session = DummySession()
    quest_mode.run({"character_name": "Ezra"}, session)

    assert called["quest"]["title"] == "Demo"
    assert session.actions[0] == "quest_mode_start"
    assert session.actions[-1] == "quest_mode_end"


def test_combat_assist_mode_run_invokes_loop(monkeypatch):
    captured = {}

    def fake_start(name):
        captured["name"] = name
    monkeypatch.setattr(combat_assist_mode, "start_afk_combat", fake_start)

    session = DummySession()
    combat_assist_mode.run({"character_name": "Ezra"}, session)

    assert captured["name"] == "Ezra"
    assert "combat_assist_start" in session.actions
    assert session.actions[-1] == "combat_assist_end"
