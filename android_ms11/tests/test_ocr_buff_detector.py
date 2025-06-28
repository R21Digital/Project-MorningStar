import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from android_ms11.core.ocr_buff_detector import detect_buffs


def test_detect_buffs_returns_list():
    buffs = detect_buffs()
    assert isinstance(buffs, list)
    assert buffs
    assert all(isinstance(b, str) for b in buffs)
