"""Entertainer mode stub."""

from utils.license_hooks import requires_license
from core.profile_loader import assert_profile_ready


@requires_license
def run(session=None):
    """Placeholder for entertainer behavior."""
    assert_profile_ready(getattr(session, "profile", None))
    print("🎭 Performing entertainment routines...")
