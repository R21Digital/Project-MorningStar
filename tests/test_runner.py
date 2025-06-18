import os
import sys
from importlib import reload

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import runner, __version__


def test_version_option_prints_version(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["prog", "--version"])
    # Reload to ensure argparse parses the new argv
    reload(runner)
    runner.main()
    captured = capsys.readouterr()
    assert captured.out.strip() == __version__
