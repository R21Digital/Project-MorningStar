import os
import sys
import importlib
import pytest

# Allow imports from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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
        def add_action(self, *a, **k):
            pass

    mod.run({}, DummySession())

@pytest.mark.parametrize("mode", list(STUB_MAP.keys()))
def test_main_selector_invokes_stub(monkeypatch, mode):
    import src.main as main
    main_mod = importlib.reload(main)

    calls = {}
    monkeypatch.setattr(main_mod, "load_config", lambda path=None: {})
    monkeypatch.setattr(main_mod, "load_runtime_profile", lambda name: {})

    class DummySession:
        pass

    def fake_session(*a, **kw):
        inst = DummySession()
        calls["session"] = kw.get("mode") if kw else a[0] if a else None
        calls["instance"] = inst
        return inst

    monkeypatch.setattr(main_mod, "SessionManager", fake_session)

    def handler(cfg, session):
        calls["handler"] = mode
        calls["used_session"] = session

    monkeypatch.setitem(main_mod.MODE_HANDLERS, mode, handler)

    main_mod.main(["--mode", mode])

    assert calls["session"] == mode
    assert calls["handler"] == mode
    assert calls["used_session"] is calls["instance"]

