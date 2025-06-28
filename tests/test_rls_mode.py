from android_ms11.modes import rls_mode


def test_rls_mode_stub_runs_once(capsys):
    rls_mode.run()
    output = capsys.readouterr().out.lower()
    assert "rare loot" in output

