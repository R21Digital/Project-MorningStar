import os
import sys
from importlib import reload

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import run_quest


def test_run_quest_executes_and_records(monkeypatch, capsys):
    fake_quest = {"title": "Test Quest", "steps": ["a"]}

    def fake_select(character, planet=None, quest_type=None):
        assert character == "Ezra"
        assert planet == "Corellia"
        assert quest_type is None
        return fake_quest

    executed = {}
    def fake_execute(q):
        executed["quest"] = q

    recorded = {}
    def fake_insert(character, topic, content):
        recorded.update({"character": character, "topic": topic, "content": content})

    monkeypatch.setattr(sys, "argv", ["prog", "--character", "Ezra", "--planet", "Corellia"])
    reload(run_quest)
    monkeypatch.setattr(run_quest, "select_quest", fake_select)
    monkeypatch.setattr(run_quest, "execute_quest", fake_execute)
    monkeypatch.setattr(run_quest, "insert_note", fake_insert)

    run_quest.main()
    captured = capsys.readouterr()

    assert "Quest executed" in captured.out
    assert executed.get("quest") == fake_quest
    assert recorded["character"] == "Ezra"
    assert recorded["topic"] == "quest"
