import json
import os
import sys
from pathlib import Path


from utils.load_mob_affinity import load_mob_affinity, MOB_AFFINITY_FILE


def test_load_mob_affinity_missing(monkeypatch):
    missing = Path("nope.json")
    monkeypatch.setattr("utils.load_mob_affinity.MOB_AFFINITY_FILE", missing)
    monkeypatch.delenv("MOB_AFFINITY_FILE", raising=False)
    data = load_mob_affinity()
    assert data == {}


def test_load_mob_affinity_env_override(monkeypatch, tmp_path):
    path = tmp_path / "custom.json"
    path.write_text(json.dumps({"medic": ["mutant"]}))
    monkeypatch.setenv("MOB_AFFINITY_FILE", str(path))
    result = load_mob_affinity()
    assert result == {"medic": ["mutant"]}


def test_load_mob_affinity_arg_override(monkeypatch, tmp_path):
    path = tmp_path / "override.json"
    path.write_text(json.dumps({"bh": ["bandit"]}))
    monkeypatch.setenv("MOB_AFFINITY_FILE", "ignored")
    result = load_mob_affinity(path)
    assert result == {"bh": ["bandit"]}
