import re
from typing import Callable, List, Dict, Tuple

# A global dictionary to hold state handlers
screen_states: Dict[str, Tuple[List[str], Callable]] = {}


def register_state(state_name: str, match_phrases: List[str], handler: Callable):
    """Register a screen state with match phrases and a handler."""
    screen_states[state_name] = (match_phrases, handler)


def detect_state(screen_text: str) -> str:
    """Check if ``screen_text`` matches any known state. Return state name if matched."""
    for state_name, (phrases, _) in screen_states.items():
        if all(re.search(phrase, screen_text, re.IGNORECASE) for phrase in phrases):
            return state_name
    return ""


def handle_state(state_name: str):
    """Call the handler for the matched state."""
    if state_name in screen_states:
        _, handler = screen_states[state_name]
        handler()
