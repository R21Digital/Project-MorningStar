from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict
import json

from . import progress_tracker
from core.session_tracker import load_session


class ProfileValidationError(Exception):
    """Raised when a profile file fails validation."""


def validate_profile(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate ``data`` and attach build information.

    Returns the validated profile dict.
    """

    for field, expected_type in REQUIRED_FIELDS.items():
        if field not in data:
            raise ProfileValidationError(f"Missing required field: {field}")
        if not isinstance(data[field], expected_type):
            raise ProfileValidationError(
                f"{field} must be of type {expected_type.__name__}"
            )

    for field, expected_type in OPTIONAL_FIELDS.items():
        if field in data:
            if not isinstance(data[field], expected_type):
                raise ProfileValidationError(
                    f"{field} must be of type {expected_type.__name__}"
                )
            if field == "farming_target":
                required_keys = {"planet", "city", "hotspot"}
                missing = required_keys - data[field].keys()
                if missing:
                    raise ProfileValidationError(
                        f"farming_target missing keys: {', '.join(sorted(missing))}"
                    )
                if not all(isinstance(data[field][k], str) for k in required_keys):
                    raise ProfileValidationError("farming_target values must be strings")

    data.setdefault("auto_train", False)

    build_name = data.get("skill_build")
    json_path = BUILD_DIR / f"{build_name}.json"
    txt_path = BUILD_DIR / f"{build_name}.txt"
    if json_path.exists():
        build_path = json_path
    elif txt_path.exists():
        build_path = txt_path
    else:
        raise ProfileValidationError(f"Build file not found: {build_name}")

    logging.info("Using build file %s", build_path)

    try:
        with open(build_path, "r", encoding="utf-8") as fh:
            build_data = json.load(fh)
    except Exception as exc:
        raise ProfileValidationError(f"Invalid build file: {build_name}") from exc
    if not isinstance(build_data, dict):
        raise ProfileValidationError("Invalid build file structure")

    data["build"] = build_data

    return data

PROFILE_DIR = Path(__file__).resolve().parents[1] / "profiles"
BUILD_DIR = PROFILE_DIR / "builds"
RUNTIME_PROFILE = Path("runtime") / "profile.runtime.json"
SESSION_STATE = Path("runtime") / "session_state.json"

REQUIRED_FIELDS = {
    "support_target": str,
    "preferred_trainers": dict,
    "default_mode": str,
    "skip_modes": list,
    "farming_targets": list,
    "skill_build": str,
}

# Optional fields and their expected types. If present in a profile file they
# must match these types but absence is allowed.
OPTIONAL_FIELDS = {
    "mode_sequence": list,
    "fatigue_threshold": int,
    "farming_target": dict,
    "auto_train": bool,
}


def assert_profile_ready(profile: Dict[str, Any] | None) -> None:
    """Ensure ``profile`` contains loaded build data."""

    if not profile or not profile.get("build"):
        raise RuntimeError("Build data not loaded in profile. Cannot continue.")


def load_profile(name: str) -> Dict[str, Any]:
    """Return profile data for ``name`` or an empty dict if unavailable."""
    path = PROFILE_DIR / f"{name}.json"
    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as fh:
        try:
            data = json.load(fh)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid profile file: {path}") from exc

    profile = validate_profile(data)
    profile["runtime"] = {"progress": load_session()}

    progress = progress_tracker.load_session(SESSION_STATE)
    profile["build_progress"] = {
        "completed_skills": progress.get("completed_skills", []),
        "total_skills": len(profile.get("build", {}).get("skills", [])),
    }
    profile["recovery_path"] = str(SESSION_STATE)

    RUNTIME_PROFILE.parent.mkdir(parents=True, exist_ok=True)
    with open(RUNTIME_PROFILE, "w", encoding="utf-8") as f:
        json.dump(profile, f, indent=2)

    return profile
