import sys
from importlib import reload


from cli.trainer import find_trainer


def test_cli_invokes_navigate(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog", "--trainer", "artisan"])
    reload(find_trainer)
    called = {}
    monkeypatch.setattr(find_trainer, "navigate_to_trainer", lambda t, p, c, a: called.setdefault("args", (t, p, c, a)))
    find_trainer.main()
    assert called["args"] == ("artisan", "tatooine", "mos_eisley", None)


def test_cli_custom_options(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog", "--trainer", "marksman", "--planet", "corellia", "--city", "coronet"])
    reload(find_trainer)
    called = {}
    monkeypatch.setattr(find_trainer, "navigate_to_trainer", lambda t, p, c, a: called.setdefault("args", (t, p, c, a)))
    find_trainer.main()
    assert called["args"] == ("marksman", "corellia", "coronet", None)
