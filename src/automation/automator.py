import time

from src.vision.ocr import capture_screen, extract_text
from src.vision.states import detect_state, handle_state


def run_state_monitor_loop(delay: float = 2.0):
    print("[AUTOMATOR] Starting screen state detection loop.")
    while True:
        image = capture_screen()
        text = extract_text(image)
        state = detect_state(text)

        if state:
            print(f"[MATCHED STATE] {state}")
            handle_state(state)
        else:
            print("[NO MATCH] Continuing scan...")

        time.sleep(delay)
