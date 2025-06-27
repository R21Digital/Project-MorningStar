import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.mode_medic import start_medic
from src.mode_afk_combat import start_afk_combat
from src.mode_crafting import start_crafting
from src.mode_buff_by_tell import start_buff_by_tell


def test_start_medic_outputs_stub(capsys):
    start_medic("Ezra")
    captured = capsys.readouterr()
    assert "Monitoring group status" in captured.out


def test_start_afk_combat_outputs_stub(capsys):
    start_afk_combat("Ezra")
    captured = capsys.readouterr()
    assert "Rotating through targets" in captured.out


def test_start_crafting_outputs_stub(capsys):
    start_crafting("Ezra")
    captured = capsys.readouterr()
    assert "Surveying resources" in captured.out


def test_start_buff_by_tell_outputs_stub(capsys):
    start_buff_by_tell("Ezra")
    captured = capsys.readouterr()
    assert "Listening for buff requests" in captured.out
