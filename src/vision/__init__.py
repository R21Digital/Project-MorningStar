from .ocr import screen_text, capture_screen, extract_text
from .states import register_state, detect_state, handle_state

__all__ = [
    "screen_text",
    "capture_screen",
    "extract_text",
    "register_state",
    "detect_state",
    "handle_state",
]
