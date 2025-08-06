"""Combat Profile Integration Module for Batch 041.

This module provides integration with SWGR skill calculator to automatically
generate combat profiles based on character skill builds.
"""

from .skill_calculator import SkillCalculator, parse_swgr_url, generate_combat_profile
from .profession_analyzer import ProfessionAnalyzer, analyze_professions, determine_role
from .combat_generator import CombatGenerator, generate_combat_config
from .integration import (
    SkillCalculatorIntegration, 
    import_swgr_build, 
    analyze_skill_tree, 
    validate_swgr_url,
    get_available_profiles,
    get_integration
)

__all__ = [
    'SkillCalculator',
    'parse_swgr_url', 
    'generate_combat_profile',
    'ProfessionAnalyzer',
    'analyze_professions',
    'determine_role',
    'CombatGenerator',
    'generate_combat_config',
    'SkillCalculatorIntegration',
    'import_swgr_build',
    'analyze_skill_tree',
    'validate_swgr_url',
    'get_available_profiles',
    'get_integration'
] 