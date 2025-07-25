"""Core runtime utilities."""

from .location_selector import locate_hotspot, travel_to_target
from .profession_leveler import ProfessionLeveler
from .build_manager import BuildManager
from .trainer_ocr import (
    extract_text_from_trainer_region,
    get_untrained_skills_from_text,
    preprocess_image,
    scan_and_detect_untrained_skills,
)
from .trainer_scanner import TrainerScanner, scan_trainer_skills
from .travel_manager import TravelManager
from .waypoint_verifier import verify_waypoint_stability
from .trainer_travel import (
    get_travel_macro,
    execute_travel_macro,
    start_travel_to_trainer,
    plan_travel_to_trainer,
    is_same_planet,
)
from .shuttle_travel import get_shuttle_path
from .progress_tracker import load_session, save_session, record_skill
from .session_tracker import (
    load_session as load_session_state,
    save_session as save_session_state,
    update_session_key,
)
from . import legacy_tracker
from src.engine import quest_executor as quest_engine
from .quest_engine import execute_quest_step, execute_with_retry
from .legacy_tracker import load_legacy_steps, read_quest_log
from .legacy_loop import run_full_legacy_quest
from .legacy_dashboard import display_legacy_progress, render_legacy_table
from .quest_state import (
    parse_quest_log,
    is_step_completed,
    scan_log_file_for_step,
    extract_quest_log_from_screenshot,
    read_saved_quest_log,
    get_step_status,
)
from .themepark_tracker import (
    read_themepark_log,
    is_themepark_quest_active,
    get_themepark_status,
    load_themepark_chains,
)
from .themepark_dashboard import display_themepark_progress, render_themepark_table
from .constants import (
    STATUS_COMPLETED,
    STATUS_FAILED,
    STATUS_IN_PROGRESS,
    STATUS_NOT_STARTED,
    STATUS_UNKNOWN,
    STATUS_EMOJI_MAP,
    STATUS_NAME_FROM_EMOJI,
    VALID_STATUS_EMOJIS,
)
from .dashboard_utils import (
    group_quests_by_category,
    build_summary_table,
    print_summary_counts,
    group_steps_by_category,
    summarize_status_counts,
    calculate_completion_percentage,
)

__all__ = [
    "preprocess_image",
    "extract_text_from_trainer_region",
    "get_untrained_skills_from_text",
    "scan_and_detect_untrained_skills",
    "scan_trainer_skills",
    "TrainerScanner",
    "TravelManager",
    "ProfessionLeveler",
    "BuildManager",
    "travel_to_target",
    "locate_hotspot",
    "verify_waypoint_stability",
    "get_travel_macro",
    "execute_travel_macro",
    "start_travel_to_trainer",
    "plan_travel_to_trainer",
    "is_same_planet",
    "get_shuttle_path",
    "load_session",
    "save_session",
    "record_skill",
    "load_session_state",
    "save_session_state",
    "update_session_key",
    "legacy_tracker",
    "quest_engine",
    "execute_quest_step",
    "execute_with_retry",
    "load_legacy_steps",
    "read_quest_log",
    "run_full_legacy_quest",
    "display_legacy_progress",
    "render_legacy_table",
    "show_legacy_dashboard",
    "parse_quest_log",
    "is_step_completed",
    "scan_log_file_for_step",
    "extract_quest_log_from_screenshot",
    "read_saved_quest_log",
    "get_step_status",
    "read_themepark_log",
    "is_themepark_quest_active",
    "get_themepark_status",
    "load_themepark_chains",
    "display_themepark_progress",
    "render_themepark_table",
    "show_unified_dashboard",
    "group_quests_by_category",
    "build_summary_table",
    "print_summary_counts",
    "group_steps_by_category",
    "summarize_status_counts",
    "calculate_completion_percentage",
    "STATUS_COMPLETED",
    "STATUS_FAILED",
    "STATUS_IN_PROGRESS",
    "STATUS_NOT_STARTED",
    "STATUS_UNKNOWN",
    "STATUS_EMOJI_MAP",
    "STATUS_NAME_FROM_EMOJI",
    "VALID_STATUS_EMOJIS",
]
