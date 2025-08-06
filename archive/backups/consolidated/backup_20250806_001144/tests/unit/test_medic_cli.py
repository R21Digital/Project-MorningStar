import sys
from importlib import reload


from src.guild import medic


def test_medic_bandage_cli(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["prog", "bandage", "--quantity", "2"])
    reload(medic)
    medic.main()
    captured = capsys.readouterr()
    assert "Crafted 2 bandages" in captured.out
