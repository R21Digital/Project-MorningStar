import os
import sys
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.db import queries


def test_select_best_quest(monkeypatch):
    fake_cursor = MagicMock()
    fake_cursor.fetchone.return_value = (1, 'Q', '[]')
    fake_conn = MagicMock()
    fake_conn.cursor.return_value = fake_cursor
    monkeypatch.setattr(queries, 'get_connection', lambda: fake_conn)

    result = queries.select_best_quest('Hero')
    assert result == (1, 'Q', '[]')
    fake_cursor.execute.assert_called()
    fake_conn.close.assert_called_once()
