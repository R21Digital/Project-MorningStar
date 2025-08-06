"""NPC Quest Signal Detection Module for Batch 043.

This module provides functionality to detect quest-giving NPCs based on in-game
visual markers and match them with the imported quest database.
"""

from .quest_icon_detector import QuestIconDetector, detect_quest_icons, scan_npc_names
from .npc_matcher import NPCMatcher, match_npc_to_quests, get_available_quests
from .quest_acquisition import QuestAcquisition, trigger_quest_acquisition, log_unmatched_npc
from .smart_detection import SmartDetection, detect_quest_npcs, process_npc_signals

__all__ = [
    'QuestIconDetector',
    'detect_quest_icons',
    'scan_npc_names',
    'NPCMatcher',
    'match_npc_to_quests',
    'get_available_quests',
    'QuestAcquisition',
    'trigger_quest_acquisition',
    'log_unmatched_npc',
    'SmartDetection',
    'detect_quest_npcs',
    'process_npc_signals'
] 