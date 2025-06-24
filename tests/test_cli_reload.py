import os
import sys
from importlib import reload

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.cli import execute_quest


def test_cli_script_reload(monkeypatch, tmp_path, capsys):
    sample_quest = {"title": "Quest 42", "planet": "Hoth", "type": "Side"}
    log_path = tmp_path / "quest.log"

    monkeypatch.setattr(sys, "argv", ["prog", "--character", "Ezra"])
    reload(execute_quest)
    monkeypatch.setattr(execute_quest, "select_quest", lambda *a, **k: sample_quest)
    monkeypatch.setattr(execute_quest, "DEFAULT_LOG_PATH", str(log_path), raising=False)

    execute_quest.main()

    captured = capsys.readouterr()
    assert "Quest 42" in captured.out
    assert log_path.exists()
    assert "Quest 42" in log_path.read_text()
