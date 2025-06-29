import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.main import parse_args


def test_max_loops_flag(monkeypatch):
    test_args = ["src/main.py", "--mode", "support", "--max_loops", "5"]
    monkeypatch.setattr("sys.argv", test_args)
    args = parse_args()
    assert args.max_loops == 5


def test_train_flag(monkeypatch):
    test_args = ["src/main.py", "--train"]
    monkeypatch.setattr("sys.argv", test_args)
    args = parse_args()
    assert args.train is True


def test_auto_train_alias(monkeypatch):
    test_args = ["src/main.py", "--auto_train"]
    monkeypatch.setattr("sys.argv", test_args)
    args = parse_args()
    assert args.train is True
