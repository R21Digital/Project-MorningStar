import pytest


from core.mode_selector import select_mode


@pytest.mark.parametrize(
    "state,skip_modes,expected",
    [
        ({"has_buff": False, "in_party": True, "credits": 2000}, [], "whisper"),
        ({"has_buff": True, "in_party": False, "credits": 2000}, [], "support"),
        ({"has_buff": True, "in_party": True, "credits": 500}, [], "bounty"),
        (
            {"has_buff": False, "in_party": False, "credits": 500},
            ["whisper", "support", "bounty"],
            "quest",
        ),
    ],
)
def test_select_mode(state, skip_modes, expected):
    profile = {"default_mode": "quest", "skip_modes": skip_modes}
    assert select_mode(profile, state) == expected
