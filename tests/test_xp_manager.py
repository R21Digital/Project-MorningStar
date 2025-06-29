import os
import sys
from unittest.mock import MagicMock
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.xp_manager import XPManager


def test_end_session_prints_path(monkeypatch, capsys):
    fake_session = MagicMock()
    fake_session.save.return_value = "/tmp/foo.json"
    monkeypatch.setattr('src.xp_manager.XPSession', MagicMock(return_value=fake_session))

    manager = XPManager("Hero")
    manager.end_session()
    captured = capsys.readouterr()
    assert "XP session saved to: /tmp/foo.json" in captured.out
    fake_session.finalize.assert_called_once()
    fake_session.save.assert_called_once()


def test_record_action_accumulates_skill_xp(monkeypatch):
    monkeypatch.setattr('src.xp_manager.track_xp_sync', lambda *args, **kwargs: 50)

    manager = XPManager("Hero")

    manager.record_action("quest_complete", skill="sword")
    manager.record_action("mob_kill", skill="sword")
    manager.record_action("healing_tick", skill="medic")

    assert manager.session.skills["sword"] == 100
    assert manager.session.skills["medic"] == 50
