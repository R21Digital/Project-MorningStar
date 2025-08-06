import sys
from importlib import reload


from src import runner
from src.runner.step_runner import run_step_list


def test_version_option_prints_version(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog", "--version"])
    # Reload to ensure argparse parses the new argv
    reload(runner)
    runner.main()
    captured = capsys.readouterr()
    assert captured.out.strip() == "0.1.0"

def test_debug_mode_replays_logs(monkeypatch, capsys):
    lines = ["line1", "line2", "line3", "line4", "line5"]

    def fake_read_logs(path, num_lines=5):
        assert path == "ams11.log"
        assert num_lines == 5
        return lines

    monkeypatch.setattr(sys, "argv", ["prog", "--mode", "debug"])
    reload(runner)
    monkeypatch.setattr(runner, "read_logs", fake_read_logs)
    monkeypatch.setattr(runner, "DEFAULT_LOG_PATH", "ams11.log", raising=False)
    runner.main()
    captured = capsys.readouterr()
    for line in lines:
        assert line in captured.out


def test_run_mode_dispatches(monkeypatch):
    calls = []

    class FakeXP:
        def __init__(self, character):
            pass

        def record_action(self, action):
            calls.append(action)

        def end_session(self):
            calls.append("end")

    monkeypatch.setattr(runner, "XPManager", FakeXP)
    monkeypatch.setattr(runner, "MODE_DISPATCH", {"quest": lambda xp: xp.record_action("quest_complete")})
    runner.run_mode("quest")
    assert calls == ["quest_complete", "end"]


def test_run_step_list(monkeypatch):
    monkeypatch.setattr(
        "builtins.open",
        lambda f, _=None, **__: __import__("io").StringIO(
            '[{"type":"quest","id":"intro_mission","action":"start"}]'
        ),
    )
    run_step_list("fake_path.json")
