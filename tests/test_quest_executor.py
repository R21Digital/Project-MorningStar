import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.quest_executor import execute_quest


def test_execute_quest_order(capsys):
    quest = {"title": "Demo", "steps": ["one", "two", "three"]}
    status = execute_quest(quest, dry_run=True)
    captured = capsys.readouterr()
    lines = captured.out.strip().splitlines()
    expected_lines = [
        "[DEBUG] Executing quest: {'title': 'Demo', 'steps': ['one', 'two', 'three']}",
        "[DRY-RUN] 1: one",
        "[DRY-RUN] 2: two",
        "[DRY-RUN] 3: three",
    ]
    assert lines == expected_lines
    assert status == {"in_progress": False, "completed": True, "failed": False}

