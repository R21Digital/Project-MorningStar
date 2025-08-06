"""Buff Advisor Module for MS11.

This module provides comprehensive buff and template recommendation capabilities including:
- Character stat analysis via parsed /stats logs or user input
- Buff food recommendations based on stat goals
- Entertainer dance recommendations for optimal performance
- Armor setup recommendations tied to build awareness
- Integration with stat optimizer and build-aware behavior systems
"""

from .buff_advisor import BuffAdvisor, create_buff_advisor
from .stat_analyzer import CharacterStatAnalyzer, create_stat_analyzer
from .buff_recommender import BuffRecommender, create_buff_recommender
from .template_recommender import TemplateRecommender, create_template_recommender
from .build_integration import BuildIntegration, create_build_integration

__all__ = [
    "BuffAdvisor",
    "create_buff_advisor",
    "CharacterStatAnalyzer", 
    "create_stat_analyzer",
    "BuffRecommender",
    "create_buff_recommender",
    "TemplateRecommender",
    "create_template_recommender",
    "BuildIntegration",
    "create_build_integration"
] 