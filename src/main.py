"""Demo entry point for Android MS11."""

import argparse
import inspect
import json
import logging
import os
import threading
import sys
from typing import Dict, Any, Mapping

# Configure logging early
import os
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/ms11.log', mode='a', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Check for required dependencies
try:
    from discord.ext import commands
    import discord_relay
    DISCORD_AVAILABLE = True
    logger.info("Discord dependencies loaded successfully")
except ImportError as e:
    logger.warning(f"Discord dependencies not available: {e}")
    logger.warning("Discord relay functionality will be disabled")
    commands = None
    discord_relay = None
    DISCORD_AVAILABLE = False

try:
    import pytesseract
    import cv2
    import pyautogui
    logger.info("Vision dependencies loaded successfully")
except ImportError as e:
    logger.error(f"Vision dependencies missing: {e}")
    logger.error("Please install: pip install pytesseract opencv-python pyautogui")
    sys.exit(1)

# Import with fallbacks for missing modules
try:
    from core.session_manager import SessionManager
    from core.window_manager import WindowManager
    from core import profile_loader, state_tracker, mode_selector
    from core.profile_loader import ProfileValidationError
    from core.session_monitor import monitor_session, FATIGUE_THRESHOLD
    from core import mode_scheduler
    from core.repeat_utils import run_repeating_mode
    CORE_MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Core modules not available: {e}")
    logger.info("Using fallback implementations")
    CORE_MODULES_AVAILABLE = False
    
    # Create fallback classes
    class SessionManager:
        def __init__(self, *args, **kwargs):
            logger.warning("Using fallback SessionManager")
    
    class WindowManager:
        def __init__(self, *args, **kwargs):
            logger.warning("Using fallback WindowManager")
        
        def update_status(self):
            """Fallback update_status method."""
            logger.debug("Fallback WindowManager update_status called")
            pass
            
    class ProfileValidationError(Exception):
        pass
        
    # Create fallback functions and modules
    def monitor_session(*args, **kwargs):
        logger.warning("Session monitoring not available")
        return {"status": "fallback"}
        
    class profile_loader:
        @staticmethod
        def validate_profile(profile):
            return profile
        
        @staticmethod
        def assert_profile_ready(profile):
            if not profile:
                raise ProfileValidationError("Profile is empty")
    
    class state_tracker:
        @staticmethod
        def get_state():
            return {"mode": "medic", "fatigue_level": 0}
            
        @staticmethod
        def reset_state():
            pass
            
        @staticmethod
        def update_state(**kwargs):
            pass
    
    class mode_selector:
        @staticmethod
        def select_mode(profile, state):
            return profile.get("mode", "medic")
    
    class mode_scheduler:
        @staticmethod
        def get_next_mode(profile, state):
            return profile.get("mode", "medic")
    
    def run_repeating_mode(mode, func, rest_time):
        logger.warning("Repeating mode not available")
        
    FATIGUE_THRESHOLD = 100

try:
    from utils.logging_utils import log_event
except ImportError:
    def log_event(event, **kwargs):
        logger.info(f"Event: {event} - {kwargs}")
# Import additional utilities with fallbacks
try:
    from utils.load_trainers import load_trainers
    from utils.check_buff_status import update_buff_state
    from utils.license_hooks import requires_license
    from modules.skills.training_check import get_trainable_skills
    from modules.travel.trainer_travel import travel_to_trainer
    UTILS_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Utility modules not available: {e}")
    UTILS_AVAILABLE = False
    
    # Fallback functions
    def load_trainers():
        return {}
    def update_buff_state(*args, **kwargs):
        pass
    def requires_license(func):
        return func
    def get_trainable_skills(*args, **kwargs):
        return []
    def travel_to_trainer(*args, **kwargs):
        return False

try:
    from src.movement.agent_mover import MovementAgent
    from src.movement.movement_profiles import patrol_route  # noqa: F401
    from src.training.trainer_visit import visit_trainer  # noqa: F401
    MOVEMENT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Movement modules not available: {e}")
    MOVEMENT_AVAILABLE = False
    
    class MovementAgent:
        def __init__(self, *args, **kwargs):
            pass
    
    def patrol_route(*args, **kwargs):
        pass
    
    def visit_trainer(*args, **kwargs):
        return False

# Import modes conditionally to avoid Discord dependency issues
try:
    from android_ms11.modes import (
        quest_mode,
        profession_mode,
        combat_assist_mode,
        dancer_mode,
        medic_mode,
        crafting_mode,
        whisper_mode,
        support_mode,
        follow_mode,
        bounty_farming_mode,
        entertainer_mode,
        rls_mode,
        special_goals_mode,
    )
    MODES_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Android MS11 modes not available: {e}")
    print("[WARNING] Using fallback mode handlers")
    MODES_AVAILABLE = False
    # Create fallback mode handlers
    def fallback_mode(*args, **kwargs):
        print("[MODE] Fallback mode - no specific handler available")
        return {"status": "fallback"}
    
    quest_mode = type('obj', (object,), {'run': fallback_mode})
    profession_mode = type('obj', (object,), {'run': fallback_mode})
    combat_assist_mode = type('obj', (object,), {'run': fallback_mode})
    dancer_mode = type('obj', (object,), {'run': fallback_mode})
    medic_mode = type('obj', (object,), {'run': fallback_mode})
    crafting_mode = type('obj', (object,), {'run': fallback_mode})
    whisper_mode = type('obj', (object,), {'run': fallback_mode})
    support_mode = type('obj', (object,), {'run': fallback_mode})
    follow_mode = type('obj', (object,), {'run': fallback_mode})
    bounty_farming_mode = type('obj', (object,), {'run': fallback_mode})
    entertainer_mode = type('obj', (object,), {'run': fallback_mode})
    rls_mode = type('obj', (object,), {'run': fallback_mode})
    special_goals_mode = type('obj', (object,), {'run': fallback_mode})

DEFAULT_PROFILE_DIR = os.path.join("profiles", "runtime")
CONFIG_PATH = os.path.join("config", "config.json")
DISCORD_CONFIG_PATH = os.path.join("config", "discord_config.json")


def load_runtime_profile(name: str, directory: str = DEFAULT_PROFILE_DIR) -> Dict[str, Any]:
    """Return runtime profile data for ``name`` if available."""
    # Security: Validate profile name to prevent path traversal
    if not _is_safe_filename(name):
        logger.warning(f"Unsafe profile name rejected: {name}")
        return {}
    
    path = os.path.join(directory, f"{name}.json")
    
    # Security: Ensure path is within the expected directory
    if not _is_path_safe(path, directory):
        logger.warning(f"Path traversal attempt blocked: {path}")
        return {}
    
    return load_json(path)


def _is_safe_filename(filename: str) -> bool:
    """Check if filename is safe (no path traversal, special chars)."""
    if not filename:
        return False
    
    # Check for path traversal attempts
    dangerous_patterns = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|', '\x00']
    for pattern in dangerous_patterns:
        if pattern in filename:
            return False
    
    # Check for absolute paths
    if os.path.isabs(filename):
        return False
    
    # Check length (prevent buffer overflow attempts)
    if len(filename) > 255:
        return False
    
    return True


def _is_path_safe(path: str, expected_dir: str) -> bool:
    """Check if resolved path is within expected directory."""
    try:
        # Resolve to absolute paths
        abs_path = os.path.abspath(path)
        abs_expected = os.path.abspath(expected_dir)
        
        # Check if path starts with expected directory
        return abs_path.startswith(abs_expected)
    except Exception:
        return False


def load_json(path: str) -> Dict[str, Any]:
    """Load JSON file with error handling and security validation."""
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                # Security validation: only accept dict objects for config
                if isinstance(data, dict):
                    # Remove potentially dangerous prototype pollution keys
                    dangerous_keys = ['__proto__', 'constructor', 'prototype']
                    for key in dangerous_keys:
                        if key in data:
                            logger.warning(f"Removed dangerous key '{key}' from JSON data")
                            del data[key]
                    
                    # Recursively clean nested objects
                    data = _sanitize_json_object(data)
                    
                    logger.debug(f"Successfully loaded and sanitized JSON from {path}")
                    return data
                else:
                    # Non-dict JSON is not valid for configuration - return empty dict
                    logger.warning(f"Non-dict JSON rejected from {path}: {type(data)}")
                    return {}
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in {path}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Error loading JSON from {path}: {e}")
            return {}
    logger.debug(f"JSON file not found: {path}")
    return {}


def _sanitize_json_object(obj: Any) -> Any:
    """Recursively sanitize JSON object removing dangerous keys and null values."""
    if isinstance(obj, dict):
        dangerous_keys = ['__proto__', 'constructor', 'prototype', 'eval', 'import', 'require']
        sanitized = {}
        for key, value in obj.items():
            if key not in dangerous_keys:
                # Skip null values for configuration
                if value is not None:
                    sanitized[key] = _sanitize_json_object(value)
            else:
                logger.warning(f"Sanitized dangerous key: {key}")
        return sanitized
    elif isinstance(obj, list):
        return [_sanitize_json_object(item) for item in obj if item is not None]
    else:
        return obj


def load_required_profile(profile_path: str) -> Dict[str, Any]:
    """Load and validate a runtime profile or exit on failure."""
    try:
        # First load the runtime profile
        prof = load_runtime_profile(profile_path)
        if not prof:
            logger.error(f"Profile not found: {profile_path}")
            sys.exit(1)
        
        # Then validate it using the profile_loader
        prof = profile_loader.validate_profile(prof)
        character_name = prof.get('character_name', 'Unnamed Character')
        logger.info(f"Successfully loaded profile for: {character_name}")
        return prof
    except ProfileValidationError as e:
        logger.error(f"Profile validation failed: {e}")
        sys.exit(1)
    except Exception as e:  # pragma: no cover - unexpected
        logger.error(f"Unexpected error loading profile: {e}", exc_info=True)
        sys.exit(1)


def load_config(path: str | None = None) -> Dict[str, Any]:
    """Return global configuration data."""
    config = load_json(path or CONFIG_PATH)
    if not config:
        print("[WARNING] No config.json found, using defaults")
        config = {
            "character_name": "Default",
            "default_mode": "medic",
            "enable_discord_relay": False
        }
    return config


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
    "follow": follow_mode.run,
    "bounty": bounty_farming_mode.run,
    "entertainer": entertainer_mode.run,
    "rls": rls_mode.run,
    "special-goals": special_goals_mode.run,
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
    parser.add_argument(
        "--follow-character",
        type=str,
        help="Name of character to follow in follow mode",
    )
    parser.add_argument(
        "--quest-log-verifier",
        action="store_true",
        help="Enable quest log UI scanning for completion verification",
    )
    parser.add_argument(
        "--quest-log-verifier-prompt",
        action="store_true",
        help="Prompt user for uncertain quest completion results",
    )
    parser.add_argument(
        "--quest-chain-id",
        type=str,
        help="Quest chain identifier for batch verification",
    )
    args = parser.parse_args(argv)
    
    # Security validation of arguments
    if args.mode is not None and args.mode != "" and not _is_safe_mode_name(args.mode):
        parser.error(f"Invalid mode name: {args.mode}")
        
    if args.profile is not None and args.profile != "" and not _is_safe_filename(args.profile):
        parser.error(f"Invalid profile name: {args.profile}")
        
    if args.rest is not None and args.rest < 0:
        parser.error("Rest time cannot be negative")
        
    if args.max_loops is not None and args.max_loops > 1000000:
        parser.error("Max loops too large (limit: 1,000,000)")
        
    if args.farming_target:
        try:
            args.farming_target = json.loads(args.farming_target)
            if not isinstance(args.farming_target, dict):
                raise ValueError("farming_target must be a JSON object")
            # Sanitize the farming target
            args.farming_target = _sanitize_json_object(args.farming_target)
        except Exception as exc:  # pragma: no cover - arg parsing
            parser.error(f"Invalid --farming_target value: {exc}")
    return args


def _is_safe_mode_name(mode: str) -> bool:
    """Validate mode name for security."""
    if not mode:
        return False
    
    # Allow only alphanumeric, dash, underscore
    allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_')
    if not all(c in allowed_chars for c in mode):
        return False
    
    # Reasonable length limit
    if len(mode) > 50:
        return False
        
    return True


def run_mode(
    mode: str,
    session: SessionManager,
    profile: Mapping[str, Any],
    config: Mapping[str, Any],
    *,
    max_loops: int | None = None,
    follow_character: str = None,
    quest_log_verifier: bool = False,
    quest_log_verifier_prompt: bool = False,
    quest_chain_id: str = None,
) -> Dict[str, Any]:
    """Execute a single iteration of ``mode`` and return metrics."""
    profile_loader.assert_profile_ready(profile)
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
    if follow_character is not None:
        if "follow_character" in params:
            kwargs["follow_character"] = follow_character
    if quest_log_verifier:
        if "quest_log_verifier" in params:
            kwargs["quest_log_verifier"] = quest_log_verifier
    if quest_log_verifier_prompt:
        if "quest_log_verifier_prompt" in params:
            kwargs["quest_log_verifier_prompt"] = quest_log_verifier_prompt
    if quest_chain_id is not None:
        if "quest_chain_id" in params:
            kwargs["quest_chain_id"] = quest_chain_id

    try:
        return handler(**kwargs) or {}
    except TypeError as exc:
        print(f"[MODE] Handler call failed: {exc}")
        return {}
    except Exception as exc:
        print(f"[MODE] Unexpected error in {mode}: {exc}")
        return {}


@requires_license
def main(argv: list[str] | None = None) -> None:
    """Run a demo session using the selected runtime profile."""

    args = parse_args(argv)

    config = load_config()
    if not args.profile:
        print("[✘] --profile is required to start the bot")
        return
    profile = load_required_profile(args.profile)
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

    relay_enabled = config.get("enable_discord_relay", False) and DISCORD_AVAILABLE
    bot = None
    if relay_enabled and commands and discord_relay:
        discord_cfg = load_json(DISCORD_CONFIG_PATH)
        if not discord_cfg.get("discord_token"):
            env_token = os.getenv("DISCORD_TOKEN")
            if env_token:
                discord_cfg["discord_token"] = env_token
            else:
                print("[WARNING] No Discord token found, relay disabled")
                relay_enabled = False
        
        if relay_enabled:
            try:
                bot = commands.Bot(command_prefix="!")
                discord_relay.setup(bot, discord_cfg)
                threading.Thread(
                    target=bot.run,
                    args=(discord_cfg["discord_token"],),
                    daemon=True,
                ).start()
            except Exception as e:
                print(f"[ERROR] Failed to start Discord bot: {e}")
                relay_enabled = False
    elif relay_enabled:
        print("[DISCORD] discord.py not available; relay disabled")

    print(f"[MODE] Selected mode '{mode}'")

    # Initialize new session
    session = SessionManager()
    window_manager = WindowManager(session)
    
    # Show initial status
    window_manager.update_status()
    setattr(session, "profile", profile)
    setattr(session, "mode", mode)

    if args.repeat:
        run_repeating_mode(
            args.mode,
            lambda: run_mode(
                args.mode,
                session,
                profile,
                config,
                max_loops=args.max_loops,
                follow_character=args.follow_character,
                quest_log_verifier=args.quest_log_verifier,
                quest_log_verifier_prompt=args.quest_log_verifier_prompt,
                quest_chain_id=args.quest_chain_id,
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
            follow_character=args.follow_character,
            quest_log_verifier=args.quest_log_verifier,
            quest_log_verifier_prompt=args.quest_log_verifier_prompt,
            quest_chain_id=args.quest_chain_id,
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
                    follow_character=args.follow_character,
                    quest_log_verifier=args.quest_log_verifier,
                    quest_log_verifier_prompt=args.quest_log_verifier_prompt,
                    quest_chain_id=args.quest_chain_id,
                )
        break


if __name__ == "__main__":
    main()
