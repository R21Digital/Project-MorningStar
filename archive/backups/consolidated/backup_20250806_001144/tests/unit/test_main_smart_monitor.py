import importlib


from core import profile_loader, state_tracker, mode_selector

import src.main as main


def test_smart_mode_invokes_monitor(monkeypatch):
    main_mod = importlib.reload(main)

    monkeypatch.setattr(main_mod, "load_config", lambda path=None: {})
    monkeypatch.setattr(profile_loader, "load_profile", lambda name: {"build": {"skills": []}})
    monkeypatch.setattr(state_tracker, "get_state", lambda: {})
    monkeypatch.setattr(main_mod, "update_buff_state", lambda state: None)
    monkeypatch.setattr(mode_selector, "select_mode", lambda profile, state: "combat")

    class DummySession:
        def __init__(self):
            self.profile = {"build": {"skills": []}}

    monkeypatch.setattr(main_mod, "SessionManager", lambda mode: DummySession())

    calls = {}

    def combat_handler(cfg, session, profile=None):
        calls["combat"] = True
        return {"xp": 100, "xp_rate": 50.0}

    def support_handler(cfg, session, profile=None):
        calls["support"] = True
        return {}

    monkeypatch.setitem(main_mod.MODE_HANDLERS, "combat", combat_handler)
    monkeypatch.setitem(main_mod.MODE_HANDLERS, "support", support_handler)

    def fake_monitor(metrics):
        calls["metrics"] = metrics
        return {"mode": "support"}

    monkeypatch.setattr(main_mod, "monitor_session", fake_monitor)

    main_mod.main(["--smart", "--profile", "demo"])

    assert calls["combat"] is True
    assert calls["metrics"] == {"xp": 100, "xp_rate": 50.0}
    assert calls["support"] is True
