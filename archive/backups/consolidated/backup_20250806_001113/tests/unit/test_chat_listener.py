import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from network.chat_listener import listen_for_chat


def test_callback_receives_input(monkeypatch):
    results = []

    def callback(text):
        results.append(text)

    called = False

    def fake_input(_):
        nonlocal called
        if not called:
            called = True
            return "Test message"
        raise EOFError

    monkeypatch.setattr("builtins.input", fake_input)
    thread = listen_for_chat(callback)
    thread.join(timeout=1)
    assert results == ["Test message"]
