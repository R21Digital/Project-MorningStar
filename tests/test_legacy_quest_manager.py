import os
import sys
from importlib import reload


from src.data import legacy_quest_manager


def test_list_all_quests():
    mgr = legacy_quest_manager.LegacyQuestManager()
    quests = mgr.list_all_quests()
    assert isinstance(quests, list)
    assert len(quests) > 0


def test_search_cli(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["prog", "--search", "Corellia"])
    reload(legacy_quest_manager)
    legacy_quest_manager.main()
    captured = capsys.readouterr()
    assert "Corellia" in captured.out
