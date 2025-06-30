import os
import sys


from src.main import parse_args


def test_repeat_flag_sets_loop(monkeypatch):
    test_args = ["src/main.py", "--mode", "entertainer", "--repeat"]
    monkeypatch.setattr("sys.argv", test_args)
    args = parse_args()
    assert args.repeat is True

