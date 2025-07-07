import json
from importlib import reload


import src.main as main


def test_load_runtime_profile(tmp_path, monkeypatch):
    data = {"mode": "questing", "location": "Test", "objectives": ["A"], "priority": 1}
    path = tmp_path / "demo.json"
    path.write_text(json.dumps(data))
    reload(main)
    prof = main.load_runtime_profile("demo", directory=str(tmp_path))
    assert prof == data

