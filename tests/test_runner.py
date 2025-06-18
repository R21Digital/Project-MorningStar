import os
import sys
from importlib import reload

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import runner


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
        assert path == "ms.log"
        assert num_lines == 5
        return lines

    monkeypatch.setattr(sys, "argv", ["prog", "--mode", "debug"])
    reload(runner)
    monkeypatch.setattr(runner, "read_logs", fake_read_logs)
    monkeypatch.setattr(runner, "DEFAULT_LOG_PATH", "ms.log", raising=False)
    runner.main()
    captured = capsys.readouterr()
    for l in lines:
        assert l in captured.out
