import threading
import time


def listen_for_chat(callback):
    """Start a background thread that forwards input lines to ``callback``."""

    def chat_loop():
        time.sleep(0.1)
        # Placeholder for real chat input logic
        pass

    thread = threading.Thread(target=chat_loop, daemon=True)
    thread.start()
    thread.join(0.2)
