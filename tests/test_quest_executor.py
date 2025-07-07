

from src.quest_executor import execute_quest


def test_execute_quest_order(capsys):
    quest = {
        "title": "Demo",
        "steps": [
            {"type": "move", "coords": [0, 0]},
            {"type": "combat", "enemy": "rat"},
            {"type": "dialogue", "npc": "Bob"},
        ],
    }
    status = execute_quest(quest, dry_run=True)
    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()
    expected_lines = [
        "🚀 Executing quest: Demo",
        "➡️ Step 1: move",
        "➡️ Step 2: combat",
        "➡️ Step 3: dialogue",
    ]
    assert lines == expected_lines
    assert status == {"in_progress": False, "completed": True, "failed": False}

