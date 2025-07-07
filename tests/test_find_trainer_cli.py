import sys
from importlib import reload


from scripts.cli import find_trainer


def test_cli_reports_coords(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["prog", "artisan", "--planet", "tatooine", "--city", "mos_eisley"])
    reload(find_trainer)
    monkeypatch.setattr(find_trainer, "get_trainer_location", lambda p, pl, c: ("Trainer", 1, 2))
    find_trainer.main()
    out = capsys.readouterr().out
    assert "Trainer" in out
    assert "(1, 2)" in out


def test_cli_handles_missing(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["prog", "brawler"])
    reload(find_trainer)
    monkeypatch.setattr(find_trainer, "get_trainer_location", lambda *a, **k: None)
    find_trainer.main()
    out = capsys.readouterr().out
    assert "No trainer found" in out
