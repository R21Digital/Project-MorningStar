import os
import sys
import json


from core.xp_estimator import XPEstimator


def test_xp_estimator_rolling_average(tmp_path):
    log_file = tmp_path / "history.json"
    est = XPEstimator(log_path=str(log_file))
    est.log_action("quest", 100)
    est.log_action("quest", 200)

    assert log_file.exists()
    data = json.loads(log_file.read_text())
    assert len(data) == 2
    assert est.average_xp("quest") == 150

    # Reload and ensure averages persist
    est2 = XPEstimator(log_path=str(log_file))
    assert est2.average_xp("quest") == 150
