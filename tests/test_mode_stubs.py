import os
import sys


from android_ms11.modes.medic_mode import start_medic
from android_ms11.modes.combat_assist_mode import start_afk_combat
from android_ms11.modes.crafting_mode import start_crafting
from android_ms11.modes.whisper_mode import start_buff_by_tell


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
