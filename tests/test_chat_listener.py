import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from network.chat_listener import listen_for_chat
import time


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
    listen_for_chat(callback)
    time.sleep(0.2)
    assert results == ["Test message"]
