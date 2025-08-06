"""Space Quest Support Module (Extended Phase) - Batch 068.

This module provides enhanced support for space missions, zone transitions, 
and higher-level content including:

- Hyperspace pathing simulation
- Specific mission locations (Corellia Starport, Naboo Orbital)
- Tiered ship upgrades system
- Foundation for AI piloting routines
"""

from .hyperspace_pathing import HyperspacePathingSimulator
from .mission_locations import MissionLocationManager
from .ship_upgrades import ShipUpgradeManager
from .ai_piloting import AIPilotingFoundation, PilotSkill
from .quest_support import SpaceQuestSupport

__all__ = [
    "HyperspacePathingSimulator",
    "MissionLocationManager", 
    "ShipUpgradeManager",
    "AIPilotingFoundation",
    "PilotSkill",
    "SpaceQuestSupport"
] 