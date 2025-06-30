import argparse
import os
import sys
from importlib import reload


import src.main as main
from core import profile_loader, state_tracker


def test_cli_farming_target_overrides_profile(monkeypatch):
    main_mod = reload(main)
    cli_target = {"planet": "Dantooine", "city": "Mining", "hotspot": "Cave"}

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
            farming_target=cli_target,
        )
        return ns

    monkeypatch.setattr(main_mod, "parse_args", fake_parse_args)
    base_profile = {"farming_target": {"planet": "Naboo", "city": "Theed", "hotspot": "Cantina"}}
    monkeypatch.setattr(profile_loader, "load_profile", lambda name: base_profile.copy())
    monkeypatch.setattr(state_tracker, "reset_state", lambda: None)
    monkeypatch.setattr(main_mod, "load_config", lambda path=None: {})
    monkeypatch.setattr(
        main_mod,
        "SessionManager",
        lambda mode: type("S", (), {"profile": {"build": {"skills": []}}})(),
    )
    monkeypatch.setattr(main_mod, "check_and_train_skills", lambda *a, **k: None)
    monkeypatch.setattr(main_mod, "MovementAgent", lambda session=None: None)
    monkeypatch.setattr(main_mod, "monitor_session", lambda *a, **k: {})

    captured = {}

    def fake_run_mode(mode, session, profile, config, *, max_loops=None):
        captured["profile"] = profile
        return {}

    monkeypatch.setattr(main_mod, "run_mode", fake_run_mode)

    main_mod.main([])

    assert captured["profile"]["farming_target"] == cli_target
