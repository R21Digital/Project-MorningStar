def test_support_mode_stub():
    from android_ms11.modes import support_mode
    from types import SimpleNamespace

    dummy_session = SimpleNamespace(config={})
    support_mode.run(max_loops=1, session=dummy_session)  # should execute without error
