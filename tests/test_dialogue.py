import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.execution.dialogue import execute_dialogue


def test_execute_dialogue_logs_expected(capsys):
    step = {
        "type": "dialogue",
        "npc": "Lieutenant Sef",
        "options": ["Who are you?", "Where am I?", "Goodbye."],
    }
    execute_dialogue(step)
    captured = capsys.readouterr()
    output = captured.out.strip().splitlines()

    assert output[0] == "🗨️ [Dialogue] Interacting with Lieutenant Sef"
    assert "💬 Dialogue Options:" in output[1]
    assert output[-1] == "  3. Goodbye."
