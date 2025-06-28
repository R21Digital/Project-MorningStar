import os
import sys
from unittest.mock import MagicMock

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
