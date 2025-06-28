import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.mode_scheduler import get_next_mode


def test_get_next_mode_wraparound():
    profile = {"default_mode": "quest", "mode_sequence": ["quest", "combat", "crafting"]}
    state = {"mode": "combat"}
    assert get_next_mode(profile, state) == "crafting"
    assert get_next_mode(profile, {"mode": "crafting"}) == "quest"


def test_get_next_mode_missing_current():
    profile = {"default_mode": "quest", "mode_sequence": ["quest", "combat", "crafting"]}
    state = {"mode": "unknown"}
    assert get_next_mode(profile, state) == "quest"


def test_get_next_mode_no_sequence():
    profile = {"default_mode": "quest"}
    state = {"mode": "quest"}
    assert get_next_mode(profile, state) == "quest"
