import threading
import time


def listen_for_chat(callback):
    """Start a background thread that forwards input lines to ``callback``.

    Returns
    -------
    threading.Thread
        The background thread running the chat loop so callers may join or
        otherwise manage it.
    """

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
    return thread
