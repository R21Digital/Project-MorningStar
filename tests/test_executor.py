import os
import sys
import json


from src.execution.quest_executor import QuestExecutor


def test_executor_runs_sample_quest(tmp_path):
    sample_quest = [
        {"type": "quest", "id": "intro", "action": "start"},
        {"type": "move", "to": {"planet": "Tatooine", "city": "Mos Eisley"}},
        {"type": "dialogue", "npc": "Trainer"},
    ]
    quest_file = tmp_path / "sample_quest.json"
    quest_file.write_text(json.dumps(sample_quest))

    executor = QuestExecutor(str(quest_file))
    executor.run()
