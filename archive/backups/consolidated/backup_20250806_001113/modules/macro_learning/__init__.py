"""Macro Learning module for Batch 065 - Macro/Alias Learning + Shortcut Helper.

This module provides comprehensive macro and alias learning capabilities including:
- Parse /alias and macro folders
- Build fallback map if macro is missing
- Store best practice macros in data/macros/
- Recommend missing macros and alert via Discord if critical ones aren't found
"""

from .macro_parser import MacroParser
from .alias_analyzer import AliasAnalyzer
from .macro_recommender import MacroRecommender
from .shortcut_helper import ShortcutHelper
from .discord_macro_alerts import DiscordMacroAlerts

__all__ = [
    "MacroParser",
    "AliasAnalyzer", 
    "MacroRecommender",
    "ShortcutHelper",
    "DiscordMacroAlerts"
] 