import os
import sys
import sqlite3
import json
import random

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src import quest_selector


def make_db():
    conn = sqlite3.connect(":memory:")
    conn.execute(
        """CREATE TABLE quests (
            id INTEGER PRIMARY KEY,
            character TEXT,
            title TEXT,
            steps TEXT,
            fallback_rank INTEGER,
            planet TEXT,
            npc TEXT,
            xp_reward INTEGER
        )"""
    )
    quests = [
        (1, "Ezra", "Q1", json.dumps(["a"]), 2, "Naboo", "Rex", 100),
        (2, "Ezra", "Q2", json.dumps(["b"]), 1, "Tatooine", "Rex", 50),
        (3, "Ezra", "Q3", json.dumps(["c"]), 3, "Naboo", "Mira", 200),
    ]
    conn.executemany(
        "INSERT INTO quests VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        quests,
    )
    conn.commit()
    return conn


def test_basic_selection(monkeypatch):
    conn = make_db()
    monkeypatch.setattr(quest_selector, "get_connection", lambda: conn)
    quest = quest_selector.select_quest("Ezra")
    assert quest["title"] == "Q2"


def test_filter_planet(monkeypatch):
    conn = make_db()
    monkeypatch.setattr(quest_selector, "get_connection", lambda: conn)
    quest = quest_selector.select_quest("Ezra", planet="Naboo")
    assert quest["title"] == "Q1"


def test_filter_npc_and_xp(monkeypatch):
    conn = make_db()
    monkeypatch.setattr(quest_selector, "get_connection", lambda: conn)
    quest = quest_selector.select_quest("Ezra", npc="Rex", min_xp=80)
    assert quest["title"] == "Q1"


def test_randomize(monkeypatch):
    conn = make_db()
    monkeypatch.setattr(quest_selector, "get_connection", lambda: conn)

    def pick_last(seq):
        return seq[-1]

    monkeypatch.setattr(random, "choice", pick_last)
    quest = quest_selector.select_quest("Ezra", randomize=True)
    assert quest["title"] == "Q3"
