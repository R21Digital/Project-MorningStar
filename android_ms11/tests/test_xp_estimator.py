import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from profession_logic.modules.xp_estimator import (
    StaticXPEstimator,
    LearningXPEstimator,
)


def test_logging_and_average(tmp_path):
    est = StaticXPEstimator(log_dir=tmp_path)
    est.log_action("quest", 100)
    est.log_action("quest", 200)

    log_file = tmp_path / "xp_actions.log"
    assert log_file.exists()
    with open(log_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
    assert len(lines) == 2

    avg = est.average_xp("quest")
    assert avg == 150


def test_learning_model_update(tmp_path):
    est = StaticXPEstimator(log_dir=tmp_path)
    est.log_action("kill", 50)
    est.log_action("kill", 100)

    model = LearningXPEstimator(log_dir=tmp_path)
    model.update()
    assert model.estimate("kill") == 75

