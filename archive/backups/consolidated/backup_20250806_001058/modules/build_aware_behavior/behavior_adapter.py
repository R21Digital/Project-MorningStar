"""
Behavior Adapter - MS11 Combat Behavior Adjustment

This module adjusts MS11's combat behavior based on parsed build information:
- Combat range adjustments (ranged vs melee)
- Cooldown timing modifications
- Target selection preferences
- Movement behavior optimization
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum

from .skillcalc_parser import BuildInfo, CombatRange
from .build_analyzer import BuildAnalysis, CombatStyle

logger = logging.getLogger(__name__)


class BehaviorAdjustmentType(Enum):
    """Types of behavior adjustments."""
    COMBAT_RANGE = "combat_range"
    COOLDOWN_TIMING = "cooldown_timing"
    TARGET_SELECTION = "target_selection"
    MOVEMENT_BEHAVIOR = "movement_behavior"
    ABILITY_PRIORITY = "ability_priority"


@dataclass
class BehaviorAdjustment:
    """Individual behavior adjustment."""
    adjustment_type: BehaviorAdjustmentType
    parameter: str
    value: Any
    description: str
    priority: int = 1


@dataclass
class BehaviorProfile:
    """Complete behavior profile for MS11."""
    combat_range: str
    cooldown_modifiers: Dict[str, float]
    target_preferences: Dict[str, str]
    movement_settings: Dict[str, str]
    ability_priorities: List[str]
    is_active: bool = True


class BehaviorAdapter:
    """MS11 behavior adjustment system."""
    
    def __init__(self):
        """Initialize the behavior adapter."""
        # Default behavior settings
        self.default_cooldowns = {
            "offensive": 1.0,
            "defensive": 1.0,
            "utility": 1.0
        }
        
        self.default_target_preferences = {
            "primary": "closest",
            "secondary": "weakest",
            "avoidance": "strongest"
        }
        
        self.default_movement = {
            "engagement": "standard",
            "retreat": "standard",
            "positioning": "standard"
        }
        
        logger.info("BehaviorAdapter initialized")
    
    def create_behavior_profile(self, build_analysis: BuildAnalysis) -> BehaviorProfile:
        """Create a behavior profile from build analysis.
        
        Parameters
        ----------
        build_analysis : BuildAnalysis
            Build analysis results
            
        Returns
        -------
        BehaviorProfile
            Complete behavior profile
        """
        adjustments = build_analysis.behavior_adjustments
        
        # Extract combat range
        combat_range = adjustments.get("combat_range", "mixed")
        
        # Calculate cooldown modifiers
        cooldown_modifiers = self._calculate_cooldown_modifiers(build_analysis)
        
        # Determine target preferences
        target_preferences = adjustments.get("target_selection", self.default_target_preferences)
        
        # Get movement settings
        movement_settings = adjustments.get("movement_behavior", self.default_movement)
        
        # Determine ability priorities
        ability_priorities = self._determine_ability_priorities(build_analysis)
        
        return BehaviorProfile(
            combat_range=combat_range,
            cooldown_modifiers=cooldown_modifiers,
            target_preferences=target_preferences,
            movement_settings=movement_settings,
            ability_priorities=ability_priorities
        )
    
    def _calculate_cooldown_modifiers(self, build_analysis: BuildAnalysis) -> Dict[str, float]:
        """Calculate cooldown timing modifiers.
        
        Parameters
        ----------
        build_analysis : BuildAnalysis
            Build analysis results
            
        Returns
        -------
        dict
            Cooldown modifiers
        """
        modifiers = self.default_cooldowns.copy()
        
        # Adjust based on combat style
        combat_style = build_analysis.combat_preference.combat_style
        
        if combat_style == CombatStyle.AGGRESSIVE:
            modifiers["offensive"] = 0.8  # Faster offensive abilities
            modifiers["defensive"] = 1.2  # Slower defensive abilities
        elif combat_style == CombatStyle.DEFENSIVE:
            modifiers["offensive"] = 1.2  # Slower offensive abilities
            modifiers["defensive"] = 0.8  # Faster defensive abilities
        elif combat_style == CombatStyle.SPECIALIZED:
            modifiers["offensive"] = 0.9
            modifiers["defensive"] = 0.9
            modifiers["utility"] = 1.3  # Slower utility abilities
        
        return modifiers
    
    def _determine_ability_priorities(self, build_analysis: BuildAnalysis) -> List[str]:
        """Determine ability usage priorities.
        
        Parameters
        ----------
        build_analysis : BuildAnalysis
            Build analysis results
            
        Returns
        -------
        list
            Ability priority list
        """
        priorities = []
        
        # Add offensive skills first
        priorities.extend(build_analysis.combat_preference.offensive_skills)
        
        # Add defensive skills
        priorities.extend(build_analysis.combat_preference.defensive_skills)
        
        # Add avoidance skills last
        priorities.extend(build_analysis.combat_preference.avoidance_skills)
        
        return priorities
    
    def apply_behavior_profile(self, profile: BehaviorProfile) -> Dict[str, Any]:
        """Apply behavior profile to MS11.
        
        Parameters
        ----------
        profile : BehaviorProfile
            Behavior profile to apply
            
        Returns
        -------
        dict
            Applied behavior settings
        """
        applied_settings = {
            "combat_range": profile.combat_range,
            "cooldown_modifiers": profile.cooldown_modifiers,
            "target_preferences": profile.target_preferences,
            "movement_settings": profile.movement_settings,
            "ability_priorities": profile.ability_priorities,
            "is_active": profile.is_active
        }
        
        logger.info(f"Applied behavior profile: {profile.combat_range} combat range")
        return applied_settings
    
    def get_behavior_summary(self, profile: BehaviorProfile) -> Dict[str, Any]:
        """Get a summary of the behavior profile.
        
        Parameters
        ----------
        profile : BehaviorProfile
            Behavior profile to summarize
            
        Returns
        -------
        dict
            Behavior summary
        """
        return {
            "combat_range": profile.combat_range,
            "cooldown_modifiers": profile.cooldown_modifiers,
            "target_preferences": profile.target_preferences,
            "movement_settings": profile.movement_settings,
            "ability_priorities": profile.ability_priorities[:5],  # Top 5 priorities
            "is_active": profile.is_active
        } 