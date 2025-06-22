# data/quest_import/data_importer.py

import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..")

def load_command_data():
    path = os.path.join(DATA_DIR, "commands", "ground.json")
    with open(path, "r") as f:
        commands = json.load(f)
    return commands

def show_sample(commands):
    print("=== Sample Commands ===")
    for c in commands[:5]:
        print(f"{c['command']} - {c['description']}")

if __name__ == "__main__":
    commands = load_command_data()
    show_sample(commands)
