import json


from profession_logic.modules import xp_estimator


def test_log_xp_and_estimate(monkeypatch, tmp_path):
    monkeypatch.setattr(xp_estimator, "LOG_ROOT", tmp_path)
    xp_estimator.log_xp("medic", "healing", 100, 2)
    xp_estimator.log_xp("medic", "healing", 50, 1)

    log_file = tmp_path / "medic_healing.json"
    assert log_file.exists()
    data = json.loads(log_file.read_text())
    assert len(data) == 2

    avg = xp_estimator.estimate_xp_per_hour("medic", "healing")
    assert avg == 150 / 3


def test_log_action_uses_estimator(monkeypatch, tmp_path):
    monkeypatch.setattr(xp_estimator, "LOG_ROOT", tmp_path)
    monkeypatch.setattr("profession_logic.modules.xp_estimator.StaticXPEstimator.log_action", lambda self, a, x: None)
    monkeypatch.setattr("profession_logic.modules.xp_estimator.estimate_xp", lambda a: 200)
    gained = xp_estimator.log_action("fighter", "mob_kill", 0.5)
    assert gained == 200
    log_file = tmp_path / "fighter_mob_kill.json"
    data = json.loads(log_file.read_text())
    assert data[0]["xp"] == 200 and data[0]["hours"] == 0.5
