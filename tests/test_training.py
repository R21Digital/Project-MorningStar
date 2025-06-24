import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.automation.training import train_with_npc


def test_train_with_npc(capfd):
    step = {"type": "dialogue", "npc": "Trainer"}
    train_with_npc(step)
    out, _ = capfd.readouterr()
    assert "Learning new abilities from Trainer" in out
