import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from android_ms11.core.ocr_loot_scanner import scan_for_loot


def test_scan_for_loot_returns_list():
    loot = scan_for_loot()
    assert isinstance(loot, list)
    assert loot
    assert all(isinstance(item, str) for item in loot)
