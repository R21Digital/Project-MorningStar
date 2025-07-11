import time

from src.vision.ocr import capture_screen, extract_text
from src.vision.states import detect_state, handle_state
from profession_logic.utils.logger import log_info
from . import mode_manager
from .quest_path import visit_trainer_if_needed


def _questing_behavior() -> None:
    """Default questing loop behavior."""
    image = capture_screen()
    text = extract_text(image)
    state = detect_state(text)

    if state:
        log_info(f"[MATCHED STATE] {state}")
        handle_state(state)
    else:
        log_info("[NO MATCH] Continuing scan...")
        visit_trainer_if_needed()


def _combat_behavior() -> None:
    """Placeholder combat mode behavior."""
    print("[COMBAT] Engaging enemies...")


def _vendor_behavior() -> None:
    """Placeholder vendor mode behavior."""
    print("[VENDOR] Checking vendor inventory...")


MODE_BEHAVIORS = {
    "questing": _questing_behavior,
    "combat": _combat_behavior,
    "vendor": _vendor_behavior,
}


def run_state_monitor_loop(delay: float = 2.0, iterations: int | None = None) -> None:
    """Run the state monitor loop for ``iterations`` cycles or indefinitely."""
    log_info("[AUTOMATOR] Starting screen state detection loop.")
    count = 0
    while iterations is None or count < iterations:
        behavior = MODE_BEHAVIORS.get(mode_manager.current_mode, _questing_behavior)
        behavior()
        count += 1
        time.sleep(delay)
