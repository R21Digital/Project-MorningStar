"""Demo entry point for Android MS11."""

import argparse
import json
import os
import threading
import time
from typing import Dict, Any, Mapping

try:
    from discord.ext import commands
    import discord_relay
except Exception:  # pragma: no cover - optional dependency
    commands = None
    discord_relay = None

from core.session_manager import SessionManager
from core import profile_loader, state_tracker, mode_selector
from core.session_monitor import monitor_session, FATIGUE_THRESHOLD
from core import mode_scheduler
from core.repeat_utils import run_repeating_mode
from utils.logging_utils import log_event
from utils.load_trainers import load_trainers
from utils.check_buff_status import update_buff_state
from utils.license_hooks import requires_license
from modules.skills.training_check import get_trainable_skills
from modules.travel.trainer_travel import travel_to_trainer
from src.movement.agent_mover import MovementAgent
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


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command line options for the demo runner."""
    parser = argparse.ArgumentParser(description="Android MS11 demo")
    parser.add_argument("--mode", type=str, help="Override session mode")
    parser.add_argument("--profile", type=str, help="Runtime profile name")
    parser.add_argument(
        "--smart",
        action="store_true",
        help="Automatically select mode based on state",
    )
    parser.add_argument(
        "--loop",
        action="store_true",
        help="Run the selected mode continuously",
    )
    parser.add_argument(
        "--repeat",
        action="store_true",
        help="Repeat selected mode in an infinite loop",
    )
    parser.add_argument(
        "--rest",
        type=int,
        default=10,
        help="Rest time (in seconds) between loops when using --repeat",
    )
    parser.add_argument(
        "--max_loops",
        type=int,
        default=None,
        help="Maximum iterations to run within a mode",
    )
    parser.add_argument(
        "--train",
        "--auto_train",
        dest="train",
        action="store_true",
        help="Check for trainable skills after each iteration",
    )
    parser.add_argument(
        "--farming_target",
        type=str,
        help="JSON string specifying planet, city and hotspot for farming runs",
    )
    args = parser.parse_args(argv)
    if args.farming_target:
        try:
            args.farming_target = json.loads(args.farming_target)
            if not isinstance(args.farming_target, dict):
                raise ValueError("farming_target must be a JSON object")
        except Exception as exc:  # pragma: no cover - arg parsing
            parser.error(f"Invalid --farming_target value: {exc}")
    return args


def run_mode(
    mode: str,
    session: SessionManager,
    profile: Mapping[str, Any],
    config: Mapping[str, Any],
    *,
    max_loops: int | None = None,
) -> Dict[str, Any]:
    """Execute a single iteration of ``mode`` and return metrics."""
    handler = MODE_HANDLERS.get(mode)
    if not handler:
        print(f"[MODE] Unknown mode '{mode}'")
        return {}

    import inspect

    params = inspect.signature(handler).parameters
    kwargs: Dict[str, Any] = {}
    if "config" in params or "cfg" in params:
        kwargs[next(p for p in params if p in ("config", "cfg"))] = config
    if "session" in params:
        kwargs["session"] = session
    if "profile" in params:
        kwargs["profile"] = profile
    if max_loops is not None:
        if "max_loops" in params:
            kwargs["max_loops"] = max_loops
        elif "loop_count" in params:
            kwargs["loop_count"] = max_loops

    try:
        return handler(**kwargs) or {}
    except TypeError as exc:
        print(f"[MODE] Handler call failed: {exc}")
        return {}


@requires_license
def main(argv: list[str] | None = None) -> None:
    """Run a demo session using the selected runtime profile."""

    args = parse_args(argv)

    config = load_config()
    profile = profile_loader.load_profile(args.profile) if args.profile else {}
    args.train = args.train or profile.get("auto_train", False)
    if getattr(args, "farming_target", None):
        profile["farming_target"] = args.farming_target

    if args.smart:
        state = state_tracker.get_state()
        update_buff_state(state)
        mode = mode_selector.select_mode(profile, state)
    else:
        state_tracker.reset_state()
        mode = args.mode or profile.get("mode") or config.get("default_mode", "medic")
    args.mode = mode

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

    print(f"[MODE] Selected mode '{mode}'")

    # Initialize new session using the mode from CLI or profile
    session = SessionManager(mode=mode)

    if args.repeat:
        run_repeating_mode(
            args.mode,
            lambda: run_mode(
                args.mode,
                session,
                profile,
                config,
                max_loops=args.max_loops,
            ),
            args.rest,
        )
        return

    current_mode = mode
    state = state_tracker.get_state()

    while True:
        session_metrics = run_mode(
            current_mode,
            session,
            profile,
            config,
            max_loops=args.max_loops,
        )

        if args.train:
            check_and_train_skills(
                MovementAgent(session=session),
                profile.get("character_skills", {}),
                profile.get("profession_tree", {}),
            )

        if args.smart or args.loop:
            state = monitor_session(session_metrics)

        if args.loop:
            fatigue = int(state.get("fatigue_level", 0))
            if fatigue > FATIGUE_THRESHOLD:
                next_mode = mode_scheduler.get_next_mode(profile, state)
                log_event(
                    f"[MODE LOOP] Fatigue {fatigue} > {FATIGUE_THRESHOLD}; switching {current_mode} -> {next_mode}"
                )
                state_tracker.update_state(mode=next_mode)
                current_mode = next_mode
                continue
            continue

        if args.smart:
            new_mode = state.get("mode")
            if new_mode and new_mode != current_mode:
                print(f"[Smart Switch] {current_mode} -> {new_mode}")
                current_mode = new_mode
                run_mode(
                    current_mode,
                    session,
                    profile,
                    config,
                    max_loops=args.max_loops,
                )
        break


if __name__ == "__main__":
    main()
