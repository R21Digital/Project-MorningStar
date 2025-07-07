from unittest.mock import MagicMock


from src.db import queries


def test_insert_note(monkeypatch):
    fake_cursor = MagicMock()
    fake_conn = MagicMock()
    fake_conn.cursor.return_value = fake_cursor
    monkeypatch.setattr(queries, "get_connection", lambda: fake_conn)

    queries.insert_note("Hero", "tips", "use force")

    fake_cursor.execute.assert_called()
    fake_conn.commit.assert_called_once()
    fake_conn.close.assert_called_once()


def test_get_notes(monkeypatch):
    expected = [(1, "Hero", "tips", "note", "2024-01-01")]
    fake_cursor = MagicMock()
    fake_cursor.fetchall.return_value = expected
    fake_conn = MagicMock()
    fake_conn.cursor.return_value = fake_cursor
    monkeypatch.setattr(queries, "get_connection", lambda: fake_conn)

    result = queries.get_notes("Hero")

    fake_cursor.execute.assert_called()
    fake_conn.close.assert_called_once()
    assert result == expected


def test_get_notes_filtered(monkeypatch):
    fake_cursor = MagicMock()
    fake_cursor.fetchall.return_value = []
    fake_conn = MagicMock()
    fake_conn.cursor.return_value = fake_cursor
    monkeypatch.setattr(queries, "get_connection", lambda: fake_conn)

    result = queries.get_notes("Hero", topic="tips")

    fake_cursor.execute.assert_called()
    fake_conn.close.assert_called_once()
    assert result == []
