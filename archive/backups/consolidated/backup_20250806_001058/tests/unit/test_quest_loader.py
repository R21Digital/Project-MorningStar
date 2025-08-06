import json

from core.quest_loader import load_quest_steps


def test_load_quest_steps(tmp_path):
    data = {"steps": [{"type": "move"}, {"type": "talk"}]}
    path = tmp_path / "quest.json"
    path.write_text(json.dumps(data))

    steps = load_quest_steps(str(path))
    assert steps == data["steps"]

