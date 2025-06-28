import importlib

from android_ms11.modes import rls_mode


def test_mode_handlers_contains_rls():
    import src.main as main
    main_mod = importlib.reload(main)
    assert main_mod.MODE_HANDLERS["rls"] is rls_mode.run


def test_rls_mode_stub_runs_once(capsys):
    rls_mode.run()
    output = capsys.readouterr().out.lower()
    assert "rare loot" in output

