

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


def test_quest_executor_logs(tmp_path, monkeypatch, caplog):
    monkeypatch.chdir(tmp_path)
    import importlib
    import logging
    import sys
    from types import ModuleType

    sys.modules.setdefault("modules", ModuleType("modules"))

    loaded_real = True
    try:
        import profession_logic.utils.logger as base_logger
        importlib.reload(base_logger)
    except Exception:
        loaded_real = False
        base_logger = ModuleType("profession_logic.utils.logger")
        tmp_logger = logging.getLogger("ms11")
        tmp_logger.addHandler(logging.NullHandler())

        def log_info(msg: str) -> None:
            tmp_logger.info(msg)

        base_logger.log_info = log_info
        base_logger.logger = tmp_logger
        sys.modules["profession_logic.utils.logger"] = base_logger

    import importlib.util
    from pathlib import Path

    repo_root = Path(__file__).resolve().parent.parent
    spec = importlib.util.spec_from_file_location(
        "core.quest_loader", repo_root / "core" / "quest_loader.py"
    )
    quest_loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(quest_loader)
    core_module = sys.modules.setdefault("core", ModuleType("core"))
    sys.modules["core.quest_loader"] = quest_loader
    core_module.quest_loader = quest_loader

    if loaded_real and hasattr(base_logger, "logger"):
        base_logger.logger.handlers.clear()
        importlib.reload(base_logger)
    import src.logging.session_log as session_log
    importlib.reload(session_log)

    import src.execution.quest_executor as qe
    importlib.reload(qe)

    quest_file = tmp_path / "quest.json"
    quest_file.write_text("[{\"type\": \"dialogue\"}]")

    executor = qe.QuestExecutor(str(quest_file))
    with caplog.at_level("INFO", logger="ms11"):
        executor.run()
    output = caplog.text
    assert "[QUEST EXECUTOR] Starting quest sequence..." in output
    assert "Executing step 1" in output


