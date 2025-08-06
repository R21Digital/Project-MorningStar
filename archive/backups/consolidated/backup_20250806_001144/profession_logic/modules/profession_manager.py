"""High-level interface for profession progression."""

from __future__ import annotations
from typing import Dict
import json

from .. import config


class ProfessionManager:
    """Placeholder manager handling profession profiles."""

    def __init__(self) -> None:
        self.profiles: Dict[str, Dict] = {}

    def load_profiles(self, path: str = config.PROFILE_DIR + "/master_build_profiles.json") -> None:
        """Load master build profiles from ``path``."""
        try:
            with open(path, "r", encoding="utf-8") as fh:
                self.profiles = json.load(fh)
        except FileNotFoundError:
            self.profiles = {}
