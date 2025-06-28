import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from android_ms11.core.loot_session import log_loot, export_log


def test_log_and_export(tmp_path):
    log_loot("Gold Coin")
    log_loot("Magic Sword")

    path = export_log(log_dir=tmp_path)
    assert os.path.exists(path)

    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)

    assert len(data) == 2
    assert data[0]["item"] == "Gold Coin"
    assert data[1]["item"] == "Magic Sword"
