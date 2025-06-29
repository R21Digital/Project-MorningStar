import importlib

from android_ms11.modes import rls_mode
from android_ms11.core import loot_session, ocr_loot_scanner, rls_logic


def test_mode_handlers_contains_rls():
    import src.main as main
    main_mod = importlib.reload(main)
    assert "rls" in main_mod.MODE_HANDLERS
    assert main_mod.MODE_HANDLERS["rls"] is rls_mode.run


def test_rls_mode_logs_loot(monkeypatch):
    loot_session._loot_log.clear()

    monkeypatch.setattr(rls_logic, "choose_next_target", lambda: {"name": "Test"})
    monkeypatch.setattr(ocr_loot_scanner, "scan_for_loot", lambda: ["Artifact"])
    monkeypatch.setattr(loot_session, "export_log", lambda: "dummy.json")

    dummy_session = type("S", (), {"profile": {"build": {"skills": []}}})()
    rls_mode.run(loop_count=1, session=dummy_session)

    assert any(entry["item"] == "Artifact" for entry in loot_session._loot_log)

