from utils.license_hooks import requires_license
from core.profile_loader import assert_profile_ready


@requires_license
def run(config, session=None):
    """Main entry point for this mode."""
    assert_profile_ready(getattr(session, "profile", None))
    pass
