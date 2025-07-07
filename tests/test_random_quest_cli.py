import sys
from importlib import reload


from cli import main as quest_cli


def test_cli_prints_random_quest(monkeypatch, capsys):
    sample = {"name": "Heroic Quest", "description": "Do heroic things"}
    monkeypatch.setattr(sys, "argv", ["prog", "--quest-mode", "legacy"])
    reload(quest_cli)
    monkeypatch.setattr(quest_cli, "get_random_quest", lambda mode: sample)
    quest_cli.main()
    out = capsys.readouterr().out
    assert "Heroic Quest" in out


def test_cli_handles_no_results(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["prog", "--quest-mode", "legacy"])
    reload(quest_cli)
    monkeypatch.setattr(quest_cli, "get_random_quest", lambda mode: None)
    quest_cli.main()
    out = capsys.readouterr().out
    assert "No quests found" in out
