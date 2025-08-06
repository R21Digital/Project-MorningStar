

from src.vision import register_state, detect_state, handle_state
from src.vision import states as states_module
from src.automation import handlers as handlers_module


def setup_module(module):
    # ensure clean state before tests
    states_module.state_patterns.clear()
    handlers_module.STATE_HANDLERS.clear()


def test_known_state_triggers_handler(monkeypatch):
    states_module.state_patterns.clear()
    handlers_module.STATE_HANDLERS.clear()
    triggered = []

    def fake_handler():
        triggered.append("continue")

    handlers_module.STATE_HANDLERS["continue_prompt"] = fake_handler
    register_state("continue_prompt", ["press", "continue"])

    text = "please PRESS enter to CONTINUE"
    state = detect_state(text)
    assert state == "continue_prompt"
    handle_state(state)
    assert triggered == ["continue"]


def test_unknown_state_no_handler(monkeypatch):
    states_module.state_patterns.clear()
    handlers_module.STATE_HANDLERS.clear()
    triggered = []

    # register a state without mapping to handler
    register_state("npc_dialogue", ["greetings"])

    text = "random text with greetings"
    state = detect_state(text)
    assert state == "npc_dialogue"

    # since there is no handler, nothing should be triggered
    handle_state(state)
    assert triggered == []

    # also ensure completely unknown text returns empty state
    unknown = detect_state("no match here")
    assert unknown == ""
