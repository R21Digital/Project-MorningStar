import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from modules.farming.terminal_farm import TerminalFarmer
import core.session_tracker as session_tracker


def test_parse_missions_filters_invalid_lines():
    farmer = TerminalFarmer()
    text = """
    Bandit Camp 100,200 300m
    Not a mission
    Rebel Hideout -50,-75 500m
    """
    missions = farmer.parse_missions(text)
    assert missions == [
        {"name": "Bandit Camp", "coords": (100, 200), "distance": 300},
        {"name": "Rebel Hideout", "coords": (-50, -75), "distance": 500},
    ]


def test_execute_run_logs_result(monkeypatch):
    farmer = TerminalFarmer()
    farmer.profile["distance_limit"] = 60
    board_text = """
    Close Target 10,10 50m 500c
    Far Target 20,20 100m 2000c
    """
    calls = []

    def fake_log(mobs, credits):
        calls.append((mobs, credits))

    monkeypatch.setattr("modules.farming.terminal_farm.log_farming_result", fake_log)

    logs = []

    class DummyLogger:
        def info(self, msg, *args):
            logs.append(msg % args)

    monkeypatch.setattr(
        "modules.farming.terminal_farm.logger",
        DummyLogger(),
    )

    accepted = farmer.execute_run(board_text=board_text)
    assert accepted == [
        {"name": "Close Target", "coords": (10, 10), "distance": 50, "credits": 500}
    ]
    assert calls == [(["Close Target"], 500)]
    assert logs == ["[TerminalFarmer] Mission Close Target at (10, 10) 50m"]


def test_filter_missions_by_class_affinity(monkeypatch):
    farmer = TerminalFarmer()
    farmer.profile["class_requirements"] = ["bounty_hunter"]
    board = """
    Bandit Camp 1,1 100m
    Mutant Nest 2,2 150m
    Smuggler Base 3,3 120m
    """
    monkeypatch.setattr(
        "modules.farming.terminal_farm.AFFINITY_MAP",
        {"bounty_hunter": ["bandit", "smuggler"]},
    )
    monkeypatch.setattr(
        "modules.farming.terminal_farm.log_farming_result",
        lambda *a, **k: None,
    )
    monkeypatch.setattr(
        "modules.farming.terminal_farm.logger",
        type("L", (), {"info": lambda *a, **k: None})(),
    )
    accepted = farmer.execute_run(board_text=board)
    assert accepted == [
        {"name": "Bandit Camp", "coords": (1, 1), "distance": 100},
        {"name": "Smuggler Base", "coords": (3, 3), "distance": 120},
    ]

def test_execute_run_affinity_logging(monkeypatch):
    farmer = TerminalFarmer()
    farmer.profile["class_requirements"] = ["bounty_hunter"]
    board = """
    Bandit Camp 1,1 100m 100c
    Creature Den 2,2 90m 80c
    Smuggler Base 3,3 110m 120c
    Mutant Nest 4,4 70m 60c
    """
    monkeypatch.setattr(
        "modules.farming.terminal_farm.AFFINITY_MAP",
        {"bounty_hunter": ["bandit", "smuggler"]},
    )
    calls = []

    def fake_log(mobs, credits):
        calls.append((mobs, credits))

    monkeypatch.setattr(
        "modules.farming.terminal_farm.log_farming_result",
        fake_log,
    )
    monkeypatch.setattr(
        "modules.farming.terminal_farm.logger",
        type("L", (), {"info": lambda *a, **k: None})(),
    )
    accepted = farmer.execute_run(board_text=board)
    assert accepted == [
        {"name": "Bandit Camp", "coords": (1, 1), "distance": 100, "credits": 100},
        {"name": "Smuggler Base", "coords": (3, 3), "distance": 110, "credits": 120},
    ]
    assert calls == [(["Bandit Camp", "Smuggler Base"], 220)]
