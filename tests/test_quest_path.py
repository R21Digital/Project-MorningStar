import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import src.automation.quest_path as qp


def test_visit_trainer_invokes_navigation(monkeypatch):
    calls = {}
    monkeypatch.setattr(qp, "should_train_skills", lambda: True)
    monkeypatch.setattr(qp, "navigate_to_trainer", lambda t, p, c, a: calls.setdefault("args", (t, p, c, a)))
    result = qp.visit_trainer_if_needed(agent="A", trainer="artisan")
    assert result is True
    assert calls["args"] == ("artisan", "tatooine", "mos_eisley", "A")


def test_visit_trainer_skipped(monkeypatch):
    monkeypatch.setattr(qp, "should_train_skills", lambda: False)
    called = []
    monkeypatch.setattr(qp, "navigate_to_trainer", lambda *a, **k: called.append(True))
    result = qp.visit_trainer_if_needed()
    assert result is False
    assert not called
