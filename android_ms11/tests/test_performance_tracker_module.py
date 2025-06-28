import os
import sys
from datetime import timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from android_ms11.core.performance_tracker import PerformanceTracker


def test_tracker_rates_and_logging(monkeypatch, tmp_path):
    from android_ms11.core import performance_tracker as pt_mod

    logged = {}
    monkeypatch.setattr(pt_mod, "log_performance_summary", lambda stats: logged.setdefault("stats", stats))

    tracker = PerformanceTracker()
    tracker.add_xp(100)
    tracker.add_loot("Gold")
    # Pretend the session has been running for 2 hours
    tracker.start_time -= timedelta(hours=2)

    rate = tracker.xp_per_hour()
    assert 49.5 < rate < 50.5

    summary = tracker.log_summary()
    assert logged["stats"] == summary
    assert summary["loot"] == 1
