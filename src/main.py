"""Demo entry point for Android MS11."""

import argparse
import json
import os
from typing import Dict, Any

from core.session_manager import SessionManager
from src.movement.agent_mover import MovementAgent
from src.movement.movement_profiles import patrol_route
from src.training.trainer_visit import visit_trainer

DEFAULT_PROFILE_DIR = os.path.join("profiles", "runtime")


def load_runtime_profile(name: str, directory: str = DEFAULT_PROFILE_DIR) -> Dict[str, Any]:
    """Return runtime profile data for ``name`` if available."""
    path = os.path.join(directory, f"{name}.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main(argv: list[str] | None = None) -> None:
    """Run a demo session using the selected runtime profile."""

    parser = argparse.ArgumentParser(description="Android MS11 demo")
    parser.add_argument("--mode", type=str, help="Override session mode")
    parser.add_argument("--profile", type=str, help="Runtime profile name")
    args = parser.parse_args(argv)

    profile = load_runtime_profile(args.profile) if args.profile else {}

    mode = args.mode or profile.get("mode", "medic")

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

    # End session and save log
    session.end_session()


if __name__ == "__main__":
    main()
