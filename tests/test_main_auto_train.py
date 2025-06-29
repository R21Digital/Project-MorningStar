import argparse
import os
import sys
from importlib import reload

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import src.main as main
from core import profile_loader, state_tracker


def test_profile_auto_train_sets_flag(monkeypatch):
    main_mod = reload(main)

    captured = {}

    def fake_parse_args(argv=None):
        ns = argparse.Namespace(
            mode="combat",
            profile="demo",
            smart=False,
            loop=False,
            repeat=False,
            rest=10,
            max_loops=None,
            train=False,
        )
        captured["args"] = ns
        return ns

    monkeypatch.setattr(main_mod, "parse_args", fake_parse_args)
    monkeypatch.setattr(main_mod, "load_config", lambda path=None: {})
    monkeypatch.setattr(profile_loader, "load_profile", lambda name: {"auto_train": True})
    monkeypatch.setattr(state_tracker, "reset_state", lambda: None)
    monkeypatch.setattr(main_mod, "SessionManager", lambda mode: object())
    monkeypatch.setattr(main_mod, "run_mode", lambda *a, **k: {})
    monkeypatch.setattr(main_mod, "check_and_train_skills", lambda *a, **k: None)
    monkeypatch.setattr(main_mod, "MovementAgent", lambda session=None: None)
    monkeypatch.setattr(main_mod, "monitor_session", lambda *a, **k: {})

    main_mod.main([])

    assert captured["args"].train is True
