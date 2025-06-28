import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from android_ms11.core.pre_buff_manager import run_pre_buff


def test_run_pre_buff_prints_messages(capsys):
    run_pre_buff()
    captured = capsys.readouterr().out
    assert "Starting pre-buff routine" in captured
    assert "Applying defensive buffs" in captured
    assert "Applying offensive buffs" in captured
    assert "Pre-buff complete" in captured
