

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


def test_farming_target_parsing(monkeypatch):
    json_arg = '{"planet": "Tatooine", "city": "Mos Eisley", "hotspot": "Cantina"}'
    test_args = ["src/main.py", "--farming_target", json_arg]
    monkeypatch.setattr("sys.argv", test_args)
    args = parse_args()
    assert args.farming_target == {
        "planet": "Tatooine",
        "city": "Mos Eisley",
        "hotspot": "Cantina",
    }
