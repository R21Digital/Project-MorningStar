import importlib
import pytest
from core import profile_loader, state_tracker

# Allow imports from project root

STUB_MAP = {
    "combat": "combat_assist_mode",
    "crafting": "crafting_mode",
    "dancer": "dancer_mode",
    "medic": "medic_mode",
    "profession": "profession_mode",
    "quest": "quest_mode",
    "whisper": "whisper_mode",
}

@pytest.mark.parametrize("module_name", STUB_MAP.values())
def test_mode_stubs_run(module_name, monkeypatch):
    mod = importlib.import_module(f"android_ms11.modes.{module_name}")

    if module_name == "quest_mode":
        monkeypatch.setattr(mod, "select_quest", lambda *a, **k: {"title": "Demo", "steps": []})
        monkeypatch.setattr(mod, "execute_quest", lambda *a, **k: None)
    if module_name == "combat_assist_mode":
        monkeypatch.setattr(mod, "start_afk_combat", lambda *a, **k: None)

    class DummySession:
        def __init__(self):
            self.profile = {"build": {"skills": []}}

        def add_action(self, *a, **k):
            pass

    mod.run({}, DummySession())

@pytest.mark.parametrize("mode", list(STUB_MAP.keys()))
def test_main_selector_invokes_stub(monkeypatch, mode):
    import src.main as main
    main_mod = importlib.reload(main)

    calls = {}
    monkeypatch.setattr(main_mod, "load_config", lambda path=None: {})
    monkeypatch.setattr(profile_loader, "load_profile", lambda name: {"build": {"skills": []}})
    monkeypatch.setattr(state_tracker, "reset_state", lambda: None)

    class DummySession:
        def __init__(self):
            self.profile = {"build": {"skills": []}}

    def fake_session(*a, **kw):
        inst = DummySession()
        calls["session"] = kw.get("mode") if kw else a[0] if a else None
        calls["instance"] = inst
        return inst

    monkeypatch.setattr(main_mod, "SessionManager", fake_session)

    def handler(cfg, session, profile=None):
        calls["handler"] = mode
        calls["used_session"] = session
        calls["profile"] = profile

    monkeypatch.setitem(main_mod.MODE_HANDLERS, mode, handler)

    main_mod.main(["--mode", mode, "--profile", "demo"])

    assert calls["session"] == mode
    assert calls["handler"] == mode
    assert calls["used_session"] is calls["instance"]
    assert calls["profile"] == {"build": {"skills": []}}


def test_main_loads_profile_and_passes_to_handler(monkeypatch):
    import src.main as main
    main_mod = importlib.reload(main)

    captured = {}
    monkeypatch.setattr(main_mod, "load_config", lambda path=None: {})

    def fake_load(name):
        captured["profile_name"] = name
        return {"setting": 1, "build": {"skills": []}}

    monkeypatch.setattr(profile_loader, "load_profile", fake_load)
    monkeypatch.setattr(state_tracker, "reset_state", lambda: captured.setdefault("reset", True))

    class DummySession:
        def __init__(self):
            self.profile = {"build": {"skills": []}}

    def fake_session(*a, **k):
        captured["session_mode"] = k.get("mode") if k else a[0] if a else None
        return DummySession()

    monkeypatch.setattr(main_mod, "SessionManager", fake_session)

    def handler(cfg, session, profile=None):
        captured["profile"] = profile

    monkeypatch.setitem(main_mod.MODE_HANDLERS, "combat", handler)

    main_mod.main(["--mode", "combat", "--profile", "demo"])

    assert captured["profile_name"] == "demo"
    assert captured.get("reset") is True
    assert captured["session_mode"] == "combat"
    assert captured["profile"] == {"setting": 1, "build": {"skills": []}}

