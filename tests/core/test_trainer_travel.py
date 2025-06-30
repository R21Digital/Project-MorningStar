from core.trainer_travel import get_travel_macro, start_travel_to_trainer


def test_get_travel_macro_formats():
    trainer = {"coords": [1234, -567], "name": "Medic Trainer"}
    assert get_travel_macro(trainer) == "/waypoint 1234.0 -567.0 Medic Trainer"


def test_start_travel_to_trainer_logs(monkeypatch):
    logs = []

    class DummyLogger:
        def info(self, msg, *args):
            logs.append(msg % args)

    import core.trainer_travel as tt
    monkeypatch.setattr(tt, "logger", DummyLogger())
    monkeypatch.setattr("builtins.print", lambda *a, **k: None)

    trainer = {"coords": [10, 20], "name": "Trainer"}
    start_travel_to_trainer(trainer)

    assert any("/waypoint 10.0 20.0 Trainer" in m for m in logs)
