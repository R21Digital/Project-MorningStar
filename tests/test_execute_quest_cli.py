import os
import sys
from importlib import reload


from scripts.cli import execute_quest


def test_cli_selects_and_logs(monkeypatch, tmp_path, capsys):
    quest = {"title": "Q1", "planet": "Naboo", "type": "Hero"}
    log_path = tmp_path / "quest.log"

    monkeypatch.setattr(sys, "argv", ["prog", "--character", "Ezra"])
    reload(execute_quest)
    monkeypatch.setattr(execute_quest, "select_quest", lambda *a, **k: quest)
    monkeypatch.setattr(execute_quest, "DEFAULT_LOG_PATH", str(log_path), raising=False)
    execute_quest.main()

    captured = capsys.readouterr()
    assert "Q1" in captured.out
    assert log_path.exists()
    assert "Q1" in log_path.read_text()


def test_cli_no_quest(monkeypatch, tmp_path, capsys):
    log_path = tmp_path / "quest.log"
    monkeypatch.setattr(sys, "argv", ["prog", "--character", "Ezra"])
    reload(execute_quest)
    monkeypatch.setattr(execute_quest, "select_quest", lambda *a, **k: None)
    monkeypatch.setattr(execute_quest, "DEFAULT_LOG_PATH", str(log_path), raising=False)
    execute_quest.main()

    captured = capsys.readouterr()
    assert "No eligible quest" in captured.out
    assert not log_path.exists()
