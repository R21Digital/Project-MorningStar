"""Demo entry point for Android MS11."""

import argparse
import json
import os
import threading
from typing import Dict, Any

try:
    from discord.ext import commands
    import discord_relay
except Exception:  # pragma: no cover - optional dependency
    commands = None
    discord_relay = None

from core.session_manager import SessionManager
from src.movement.agent_mover import MovementAgent
from src.movement.movement_profiles import patrol_route
from src.training.trainer_visit import visit_trainer
from modules.skills.training_check import get_trainable_skills
from modules.travel.trainer_travel import travel_to_trainer
from utils.load_trainers import load_trainers

DEFAULT_PROFILE_DIR = os.path.join("profiles", "runtime")
CONFIG_PATH = os.path.join("config", "config.json")
SESSION_CONFIG_PATH = os.path.join("config", "session_config.json")
DISCORD_CONFIG_PATH = os.path.join("config", "discord_config.json")


def load_runtime_profile(name: str, directory: str = DEFAULT_PROFILE_DIR) -> Dict[str, Any]:
    """Return runtime profile data for ``name`` if available."""
    path = os.path.join(directory, f"{name}.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_json(path: str) -> Dict[str, Any]:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}


def load_config(path: str | None = None) -> Dict[str, Any]:
    """Return global configuration data."""
    return load_json(path or CONFIG_PATH)


def check_and_train_skills(
    agent,
    character_skills: Dict[str, int],
    profession_tree: Dict[str, Any],
) -> None:
    """Check for trainable skills and visit trainers if available."""

    trainer_data = load_trainers()
    trainable = get_trainable_skills(character_skills, profession_tree)
    for profession, next_level in trainable:
        print(f"[TRAIN] {profession} -> level {next_level}")
        travel_to_trainer(profession, trainer_data, agent=agent)


def main(argv: list[str] | None = None) -> None:
    """Run a demo session using the selected runtime profile."""

    parser = argparse.ArgumentParser(description="Android MS11 demo")
    parser.add_argument("--mode", type=str, help="Override session mode")
    parser.add_argument("--profile", type=str, help="Runtime profile name")
    args = parser.parse_args(argv)

    config = load_config()
    profile = load_runtime_profile(args.profile) if args.profile else {}

    mode = args.mode or profile.get("mode") or config.get("default_mode", "medic")

    relay_enabled = config.get("enable_discord_relay")
    if relay_enabled is None:
        session_cfg = load_json(SESSION_CONFIG_PATH)
        relay_enabled = session_cfg.get("enable_discord_relay", False)
    bot = None
    if relay_enabled and commands and discord_relay:
        discord_cfg = load_json(DISCORD_CONFIG_PATH)
        if not discord_cfg.get("discord_token"):
            env_token = os.getenv("DISCORD_TOKEN")
            if env_token:
                discord_cfg["discord_token"] = env_token
        bot = commands.Bot(command_prefix="!")
        discord_relay.setup(bot, discord_cfg)
        threading.Thread(
            target=bot.run,
            args=(discord_cfg["discord_token"],),
            daemon=True,
        ).start()
    elif relay_enabled:
        print("[DISCORD] discord.py not available; relay disabled")

    # Initialize new session using the mode from CLI or profile
    session = SessionManager(mode=mode)

    location = profile.get("location")
    objectives = profile.get("objectives", [])

    if location:
        session.add_action(f"Travel to {location}")
    for obj in objectives:
        session.add_action(obj)

    # Simulated: retrieve credits before and after
    session.set_start_credits(2000)
    session.add_action("Entered Theed Medical Center")
    session.add_action("Began healing nearby players")
    session.set_end_credits(2300)

    # Movement Test
    agent = MovementAgent(session=session)
    patrol_route(agent, "Anchorhead-Loop")

    # Try visiting artisan trainer
    visit_trainer(agent, "artisan", planet="tatooine", city="mos_eisley")

    # Check for new skills after quest completion
    sample_skills = {"artisan": 0}
    skill_tree = {"artisan": [0, 1]}
    check_and_train_skills(agent, sample_skills, skill_tree)

    # End session and save log
    session.end_session()


if __name__ == "__main__":
    main()
