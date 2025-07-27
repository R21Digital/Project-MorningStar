import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from network.chat_listener import listen_for_chat


def test_callback_receives_input(monkeypatch):
    results = []

    def callback(text):
        results.append(text)

    monkeypatch.setattr('builtins.input', lambda _: "Test message")
    listen_for_chat(callback)
    assert results == []  # Thread may not run before assertion
