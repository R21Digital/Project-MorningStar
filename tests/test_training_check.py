import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.skills import training_check


def test_get_trainable_skills_basic():
    character = {"artisan": 1, "marksman": 0}
    tree = {
        "artisan": [0, 1, 2],
        "marksman": [0, 1],
        "scout": [0, 1],
    }
    result = training_check.get_trainable_skills(character, tree)
    assert sorted(result) == [
        ("artisan", 2),
        ("marksman", 1),
        ("scout", 1),
    ]


def test_get_trainable_skills_none():
    character = {"artisan": 2}
    tree = {"artisan": [0, 1, 2]}
    result = training_check.get_trainable_skills(character, tree)
    assert result == []

