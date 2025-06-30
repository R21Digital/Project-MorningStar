import os
import sys
from unittest.mock import MagicMock


from src.db import quest_utils


def test_log_progress(monkeypatch):
    fake_cursor = MagicMock()
    fake_conn = MagicMock()
    fake_conn.cursor.return_value = fake_cursor
    monkeypatch.setattr(quest_utils, 'get_connection', lambda: fake_conn)

    quest_utils.log_progress("PlayerX", 3, completed=True)

    fake_cursor.execute.assert_called()
    fake_conn.commit.assert_called_once()
    fake_conn.close.assert_called_once()
