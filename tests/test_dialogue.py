import os
import sys
import random
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.execution.dialogue import execute_dialogue


def test_execute_dialogue_no_options(capsys):
    step = {"npc": "Merchant"}
    execute_dialogue(step)
    captured = capsys.readouterr()
    assert "[Dialogue] Interacting with Merchant" in captured.out
    assert "No dialogue options provided." in captured.out


def test_execute_dialogue_random_selection(monkeypatch, capsys):
    step = {
        "npc": "Lieutenant Serk",
        "options": ["Who are you?", "Where am I?", "Goodbye."],
    }
    monkeypatch.setattr(time, "sleep", lambda *_: None)
    monkeypatch.setattr(random, "randint", lambda a, b: 1)
    execute_dialogue(step)
    captured = capsys.readouterr()
    assert "1. Who are you?" in captured.out
    assert "2. Where am I?" in captured.out
    assert "3. Goodbye." in captured.out
    assert "You selected: 'Where am I?'" in captured.out


def test_execute_dialogue_selected_index(monkeypatch, capsys):
    step = {
        "npc": "Guard",
        "options": ["Hello", "Bye"],
        "selected_index": 1,
    }
    monkeypatch.setattr(time, "sleep", lambda *_: None)
    execute_dialogue(step)
    captured = capsys.readouterr()
    assert "You selected: 'Bye'" in captured.out
