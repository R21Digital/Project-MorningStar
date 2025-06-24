import re
from typing import List, Dict

from src.automation.handlers import STATE_HANDLERS

# A global dictionary to hold patterns for each screen state
state_patterns: Dict[str, List[str]] = {}


def register_state(state_name: str, match_phrases: List[str]):
    """Register a screen state with match phrases."""
    state_patterns[state_name] = match_phrases


def detect_state(screen_text: str) -> str:
    """Check if ``screen_text`` matches any known state. Return state name if matched."""
    for state_name, phrases in state_patterns.items():
        if all(re.search(phrase, screen_text, re.IGNORECASE) for phrase in phrases):
            return state_name
    return ""


def handle_state(state_name: str):
    """Call the handler for the matched state."""
    handler = STATE_HANDLERS.get(state_name)
    if handler:
        handler()
