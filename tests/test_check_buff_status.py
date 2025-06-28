import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.check_buff_status import update_buff_state


def test_update_buff_state_sets_has_buff():
    state = {}
    update_buff_state(state)
    assert "has_buff" in state
    assert isinstance(state["has_buff"], bool)
