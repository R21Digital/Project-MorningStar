import os
import sys
from unittest.mock import MagicMock


from src.db import quest_utils


def test_get_next_quest_in_chain(monkeypatch):
    fake_cursor = MagicMock()
    fake_cursor.fetchone.return_value = {"id": 2}
    fake_conn = MagicMock()
    fake_conn.cursor.return_value = fake_cursor
    monkeypatch.setattr(quest_utils, 'get_connection', lambda: fake_conn)

    result = quest_utils.get_next_quest_in_chain(1, 1)
    assert result == {"id": 2}
    fake_cursor.execute.assert_called()
    fake_conn.close.assert_called_once()
