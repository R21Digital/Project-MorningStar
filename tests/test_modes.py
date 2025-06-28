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
def test_mode_stubs_run(module_name):
    mod = importlib.import_module(f"android_ms11.modes.{module_name}")
    mod.run({})

@pytest.mark.parametrize("mode", list(STUB_MAP.keys()))
def test_main_selector_invokes_stub(monkeypatch, mode):
    import src.main as main
    main_mod = importlib.reload(main)

    calls = {}
    monkeypatch.setattr(main_mod, "load_config", lambda path=None: {})
    monkeypatch.setattr(main_mod, "load_runtime_profile", lambda name: {})

    def fake_session(*a, **kw):
        calls["session"] = kw.get("mode") if kw else a[0] if a else None
    monkeypatch.setattr(main_mod, "SessionManager", fake_session)

    def handler(cfg):
        calls["handler"] = mode
    monkeypatch.setitem(main_mod.MODE_HANDLERS, mode, handler)

    main_mod.main(["--mode", mode])

    assert calls == {"session": mode, "handler": mode}

