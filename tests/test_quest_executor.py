

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


def test_quest_executor_logs(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    import importlib
    import utils.logger as base_logger

    base_logger.logger.handlers.clear()
    importlib.reload(base_logger)

    import src.execution.quest_executor as qe
    importlib.reload(qe)

    quest_file = tmp_path / "quest.json"
    quest_file.write_text("[{\"type\": \"dialogue\"}]")

    executor = qe.QuestExecutor(str(quest_file))
    executor.run()
    captured = capsys.readouterr()
    output = captured.out
    assert "[QUEST EXECUTOR] Starting quest sequence..." in output
    assert "Executing step 1" in output


