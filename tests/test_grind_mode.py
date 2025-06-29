import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.grinding import grind_mode
from data import loot_table


def test_get_loot_for_mob():
    items = loot_table.get_loot_for_mob("bantha")
    assert "bantha milk" in items


def test_choose_grind_target_pref_loot():
    mobs = [
        {"name": "Bantha", "level": 15},
        {"name": "Canyon Krayt Dragon", "level": 80},
    ]
    target = grind_mode.choose_grind_target(mobs, preferred_loot=["krayt pearl"])
    assert target["name"].lower() == "canyon krayt dragon"

