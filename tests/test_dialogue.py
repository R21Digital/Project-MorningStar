import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.execution.dialogue import execute_dialogue


def test_execute_dialogue_logs_expected(capsys):
    step = {
        "type": "dialogue",
        "npc": "Lieutenant Serk",
        "options": ["Who are you?", "Where am I?", "Goodbye."],
    }
    execute_dialogue(step)
    captured = capsys.readouterr()
    assert "[Dialogue] Interacting with Lieutenant Serk" in captured.out
    assert "1. Who are you?" in captured.out
    assert "2. Where am I?" in captured.out
    assert "3. Goodbye." in captured.out
    assert "You selected: 'Who are you?'" in captured.out
