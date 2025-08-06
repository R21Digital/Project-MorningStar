"""Example script demonstrating the ``StateManager``."""

from src.state import StateManager
from profession_logic.utils.logger import logger


def on_mission_board():
    logger.info("Mission Board detected")


def on_quest_completed():
    logger.info("Quest completed!")


def on_error():
    logger.info("Error detected!")


if __name__ == "__main__":
    callbacks = {
        "mission board": on_mission_board,
        "quest completed": on_quest_completed,
        "error": on_error,
    }
    manager = StateManager(callbacks, interval=0.5)
    manager.run(duration=10)
