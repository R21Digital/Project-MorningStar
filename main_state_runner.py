"""Example script demonstrating the ``StateManager``."""

from src.state import StateManager


def on_mission_board():
    print("Mission Board detected")


def on_quest_completed():
    print("Quest completed!")


def on_error():
    print("Error detected!")


if __name__ == "__main__":
    callbacks = {
        "mission board": on_mission_board,
        "quest completed": on_quest_completed,
        "error": on_error,
    }
    manager = StateManager(callbacks, interval=0.5)
    manager.run(duration=10)
