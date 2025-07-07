import json
import sys
from importlib import reload


import src.main as main
from core import profile_loader, state_tracker


def test_load_config(monkeypatch, tmp_path):
    cfg = {"character_name": "Bob", "default_mode": "questing", "enable_discord_relay": True}
    path = tmp_path / "config.json"
    path.write_text(json.dumps(cfg))
    reload(main)
    monkeypatch.setattr(main, "CONFIG_PATH", str(path), raising=False)
    loaded = main.load_config()
    assert loaded == cfg


def test_main_uses_default_mode(monkeypatch, tmp_path):
    cfg = {"character_name": "Bob", "default_mode": "questing", "enable_discord_relay": False}
    path = tmp_path / "config.json"
    path.write_text(json.dumps(cfg))
    main_mod = reload(main)
    monkeypatch.setattr(main_mod, "CONFIG_PATH", str(path), raising=False)

    captured = {}

    class DummySession:
        def __init__(self, mode):
            captured["mode"] = mode
            self.profile = {"build": {"skills": []}}

        def add_action(self, *a, **k):
            pass

        def set_start_credits(self, *a, **k):
            pass

        def set_end_credits(self, *a, **k):
            pass

        def end_session(self):
            pass

    monkeypatch.setattr(main_mod, "SessionManager", DummySession)
    monkeypatch.setattr(main_mod, "MovementAgent", lambda session=None: None)
    monkeypatch.setattr(main_mod, "patrol_route", lambda *a, **k: None)
    monkeypatch.setattr(main_mod, "visit_trainer", lambda *a, **k: None)
    monkeypatch.setattr(main_mod, "check_and_train_skills", lambda *a, **k: None)
    monkeypatch.setattr(profile_loader, "load_profile", lambda name: {"build": {"skills": []}})
    monkeypatch.setattr(state_tracker, "reset_state", lambda: None)
    monkeypatch.setattr(sys, "argv", ["prog"])

    main_mod.main(["--profile", "demo"])
    assert captured["mode"] == "questing"
