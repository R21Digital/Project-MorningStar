

import src.main as main


def test_check_and_train_triggers_travel(monkeypatch):
    calls = {}

    monkeypatch.setattr(
        main,
        "load_trainers",
        lambda: {"artisan": [{"planet": "tatooine", "city": "mos_eisley", "name": "Trainer", "coords": [1, 2]}]},
    )
    monkeypatch.setattr(
        main, "get_trainable_skills", lambda skills, tree: [("artisan", 1)]
    )
    def fake_travel(prof, data, agent=None):
        calls["args"] = (prof, data, agent)
    monkeypatch.setattr(main, "travel_to_trainer", fake_travel)

    main.check_and_train_skills("AGENT", {}, {})

    assert calls["args"][0] == "artisan"
    assert calls["args"][2] == "AGENT"

