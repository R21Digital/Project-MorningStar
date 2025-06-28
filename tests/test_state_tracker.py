import os
import sys
import json
from importlib import reload

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import core.state_tracker as state_tracker


def test_state_persistence(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    mod = reload(state_tracker)
    mod.update_state(mode="combat", xp=42)

    state_file = tmp_path / "logs" / "state.json"
    assert state_file.exists()
    data = json.loads(state_file.read_text())
    assert data["mode"] == "combat"
    assert data["xp"] == 42

    mod2 = reload(state_tracker)
    assert mod2.get_state()["mode"] == "combat"
    assert mod2.get_state()["xp"] == 42
