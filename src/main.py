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
from utils.load_trainers import load_trainers
from modules.skills.training_check import get_trainable_skills
from modules.travel.trainer_travel import travel_to_trainer
from src.movement.agent_mover import MovementAgent  # noqa: F401
from src.movement.movement_profiles import patrol_route  # noqa: F401
from src.training.trainer_visit import visit_trainer  # noqa: F401

MovementAgent
patrol_route
visit_trainer

from android_ms11.modes import (
    quest_mode,
    profession_mode,
    combat_assist_mode,
    dancer_mode,
    medic_mode,
    crafting_mode,
    whisper_mode,
    support_mode,
    bounty_farming_mode,
    entertainer_mode,
    rls_mode,
)

DEFAULT_PROFILE_DIR = os.path.join("profiles", "runtime")
CONFIG_PATH = os.path.join("config", "config.json")
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


MODE_HANDLERS = {
    "quest": quest_mode.run,
    "profession": profession_mode.run,
    "combat": combat_assist_mode.run,
    "dancer": dancer_mode.run,
    "medic": medic_mode.run,
    "crafting": crafting_mode.run,
    "whisper": whisper_mode.run,
    "support": support_mode.run,
    "bounty": bounty_farming_mode.run,
    "entertainer": entertainer_mode.run,
    "rls": rls_mode.run,
}


def main(argv: list[str] | None = None) -> None:
    """Run a demo session using the selected runtime profile."""

    parser = argparse.ArgumentParser(description="Android MS11 demo")
    parser.add_argument("--mode", type=str, help="Override session mode")
    parser.add_argument("--profile", type=str, help="Runtime profile name")
    args = parser.parse_args(argv)

    config = load_config()
    profile = load_runtime_profile(args.profile) if args.profile else {}

    mode = args.mode or profile.get("mode") or config.get("default_mode", "medic")

    relay_enabled = config.get("enable_discord_relay", False)
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

    handler = MODE_HANDLERS.get(mode)
    if handler:
        handler(config, session)
    else:
        print(f"[MODE] Unknown mode '{mode}'")


if __name__ == "__main__":
    main()
