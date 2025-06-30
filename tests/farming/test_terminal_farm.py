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
    farmer.profile["max_distance"] = 60
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

