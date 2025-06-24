import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.state.character import update_location, log_quest_progress, character_state


def test_update_location():
    update_location("Tatooine", "Mos Eisley")
    assert character_state["location"]["planet"] == "Tatooine"
    assert character_state["location"]["city"] == "Mos Eisley"


def test_log_quest_progress():
    log_quest_progress("intro_mission", "started")
    assert character_state["quests"]["intro_mission"] == "started"
