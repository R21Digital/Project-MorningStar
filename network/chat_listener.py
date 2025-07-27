import threading
import time


def listen_for_chat(callback):
    """Start a background thread that forwards input lines to ``callback``."""

    def chat_loop():
        time.sleep(0.1)
        while True:
            try:
                line = input("")
            except EOFError:
                break
            callback(line)

    thread = threading.Thread(target=chat_loop, daemon=True)
    thread.start()
    # Intentionally do not join so the listener stays active
