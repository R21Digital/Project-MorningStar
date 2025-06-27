import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import src.automation.quest_path as qp


def test_visit_trainer_invokes_navigation():
    with patch("src.automation.quest_path.should_train_skills", return_value=True), patch(
        "src.automation.quest_path.navigate_to_trainer"
    ) as mock_nav:
        result = qp.visit_trainer_if_needed(agent="A", trainer="artisan")
        assert result is True
        mock_nav.assert_called_once_with("artisan", "tatooine", "mos_eisley", "A")


def test_visit_trainer_skipped():
    with patch("src.automation.quest_path.should_train_skills", return_value=False), patch(
        "src.automation.quest_path.navigate_to_trainer"
    ) as mock_nav:
        result = qp.visit_trainer_if_needed()
        assert result is False
        mock_nav.assert_not_called()
