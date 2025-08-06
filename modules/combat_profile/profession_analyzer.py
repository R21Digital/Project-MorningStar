"""Profession Analysis Module for Batch 041.

This module analyzes skill trees to determine player professions, roles,
and ability sets for automatic combat profile generation.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class CombatRole(Enum):
    """Combat role enumeration."""
    DPS = "dps"
    HEALER = "healer"
    TANK = "tank"
    SUPPORT = "support"
    HYBRID = "hybrid"


@dataclass
class ProfessionAnalysis:
    """Analysis results for a profession."""
    name: str
    points: int
    primary_skills: List[str]
    secondary_skills: List[str]
    combat_capabilities: List[str]
    support_capabilities: List[str]
    role_indicators: List[str]


@dataclass
class RoleAnalysis:
    """Analysis results for character role."""
    primary_role: CombatRole
    secondary_roles: List[CombatRole]
    primary_profession: str
    secondary_professions: List[str]
    combat_abilities: List[str]
    support_abilities: List[str]
    weapon_preferences: List[str]
    combat_distance: str
    support_capacity: str


class ProfessionAnalyzer:
    """Analyzes skill trees to determine professions and roles."""
    
    def __init__(self):
        """Initialize the profession analyzer."""
        self.logger = logging.getLogger(__name__)
        
        # Profession role mappings
        self.profession_roles = {
            "Brawler": CombatRole.DPS,
            "Marksman": CombatRole.DPS,
            "Scout": CombatRole.SUPPORT,
            "Artisan": CombatRole.SUPPORT,
            "Entertainer": CombatRole.SUPPORT,
            "Medic": CombatRole.HEALER,
            "Officer": CombatRole.SUPPORT,
            "Smuggler": CombatRole.DPS,
            "Spy": CombatRole.DPS,
            "Trader": CombatRole.SUPPORT,
            "Bounty Hunter": CombatRole.DPS,
            "Commando": CombatRole.DPS,
            "Force Sensitive": CombatRole.HYBRID,
            "Jedi": CombatRole.HYBRID,
            "Sith": CombatRole.HYBRID
        }
        
        # Combat skill indicators
        self.combat_skills = {
            "Brawler": ["unarmed_combat", "melee_combat", "brawler_combat"],
            "Marksman": ["pistol_combat", "rifle_combat", "marksman_combat"],
            "Scout": ["scout_combat", "ranged_combat"],
            "Medic": ["medical_combat", "healing_combat"],
            "Smuggler": ["smuggler_combat", "pistol_combat"],
            "Spy": ["spy_combat", "melee_combat"],
            "Bounty Hunter": ["bounty_hunter_combat", "ranged_combat"],
            "Commando": ["commando_combat", "heavy_weapons"],
            "Jedi": ["lightsaber_combat", "force_combat"],
            "Sith": ["lightsaber_combat", "force_combat"]
        }
        
        # Support skill indicators
        self.support_skills = {
            "Medic": ["healing", "medical", "support"],
            "Scout": ["scouting", "tracking", "survival"],
            "Artisan": ["crafting", "engineering", "repair"],
            "Entertainer": ["entertainment", "buffing", "morale"],
            "Officer": ["leadership", "tactics", "command"],
            "Trader": ["trading", "business", "economics"]
        }
        
        # Weapon preferences by profession
        self.weapon_preferences = {
            "Brawler": ["unarmed", "melee"],
            "Marksman": ["pistol", "rifle", "carbine"],
            "Scout": ["rifle", "carbine", "pistol"],
            "Medic": ["pistol", "rifle"],
            "Smuggler": ["pistol", "carbine"],
            "Spy": ["pistol", "melee"],
            "Bounty Hunter": ["rifle", "pistol"],
            "Commando": ["heavy_weapon", "rifle"],
            "Jedi": ["lightsaber", "force"],
            "Sith": ["lightsaber", "force"]
        }
    
    def analyze_professions(self, professions: Dict[str, Dict[str, Any]]) -> Dict[str, ProfessionAnalysis]:
        """Analyze professions in skill tree.
        
        Parameters
        ----------
        professions : dict
            Professions data from skill tree
            
        Returns
        -------
        dict
            Analysis results for each profession
        """
        try:
            self.logger.info(f"Analyzing {len(professions)} professions")
            
            analysis = {}
            
            for profession_name, profession_data in professions.items():
                points = profession_data.get('points', 0)
                skills = profession_data.get('skills', {})
                
                # Analyze skills
                primary_skills = self._get_primary_skills(profession_name, skills)
                secondary_skills = self._get_secondary_skills(profession_name, skills)
                combat_capabilities = self._get_combat_capabilities(profession_name, skills)
                support_capabilities = self._get_support_capabilities(profession_name, skills)
                role_indicators = self._get_role_indicators(profession_name, skills)
                
                # Create analysis
                analysis[profession_name] = ProfessionAnalysis(
                    name=profession_name,
                    points=points,
                    primary_skills=primary_skills,
                    secondary_skills=secondary_skills,
                    combat_capabilities=combat_capabilities,
                    support_capabilities=support_capabilities,
                    role_indicators=role_indicators
                )
            
            self.logger.info(f"Completed profession analysis")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing professions: {e}")
            return {}
    
    def determine_role(self, profession_analysis: Dict[str, ProfessionAnalysis]) -> RoleAnalysis:
        """Determine character role based on profession analysis.
        
        Parameters
        ----------
        profession_analysis : dict
            Analysis results for professions
            
        Returns
        -------
        RoleAnalysis
            Determined role analysis
        """
        try:
            self.logger.info("Determining character role")
            
            # Find primary profession (most points)
            primary_profession = max(profession_analysis.keys(), 
                                   key=lambda p: profession_analysis[p].points)
            
            # Determine primary role
            primary_role = self.profession_roles.get(primary_profession, CombatRole.HYBRID)
            
            # Find secondary professions
            sorted_professions = sorted(profession_analysis.keys(),
                                     key=lambda p: profession_analysis[p].points,
                                     reverse=True)
            secondary_professions = sorted_professions[1:3]  # Top 2-3 after primary
            
            # Determine secondary roles
            secondary_roles = []
            for prof in secondary_professions:
                role = self.profession_roles.get(prof, CombatRole.SUPPORT)
                if role != primary_role and role not in secondary_roles:
                    secondary_roles.append(role)
            
            # Analyze combat abilities
            combat_abilities = []
            support_abilities = []
            weapon_preferences = []
            
            for prof_name, analysis in profession_analysis.items():
                combat_abilities.extend(analysis.combat_capabilities)
                support_abilities.extend(analysis.support_capabilities)
                weapon_preferences.extend(self.weapon_preferences.get(prof_name, []))
            
            # Remove duplicates
            combat_abilities = list(set(combat_abilities))
            support_abilities = list(set(support_abilities))
            weapon_preferences = list(set(weapon_preferences))
            
            # Determine combat distance and support capacity
            combat_distance = self._determine_combat_distance(weapon_preferences, primary_role)
            support_capacity = self._determine_support_capacity(support_abilities, primary_role)
            
            # Create role analysis
            role_analysis = RoleAnalysis(
                primary_role=primary_role,
                secondary_roles=secondary_roles,
                primary_profession=primary_profession,
                secondary_professions=secondary_professions,
                combat_abilities=combat_abilities,
                support_abilities=support_abilities,
                weapon_preferences=weapon_preferences,
                combat_distance=combat_distance,
                support_capacity=support_capacity
            )
            
            self.logger.info(f"Determined role: {primary_role.value} ({primary_profession})")
            return role_analysis
            
        except Exception as e:
            self.logger.error(f"Error determining role: {e}")
            # Return default analysis
            return RoleAnalysis(
                primary_role=CombatRole.HYBRID,
                secondary_roles=[],
                primary_profession="Unknown",
                secondary_professions=[],
                combat_abilities=[],
                support_abilities=[],
                weapon_preferences=[],
                combat_distance="medium",
                support_capacity="low"
            )
    
    def _get_primary_skills(self, profession: str, skills: Dict[str, Any]) -> List[str]:
        """Get primary skills for a profession."""
        primary_skills = []
        
        # Get profession-specific primary skills
        profession_primary = {
            "Brawler": ["unarmed_combat", "melee_combat"],
            "Marksman": ["pistol_combat", "rifle_combat"],
            "Medic": ["healing", "medical"],
            "Jedi": ["lightsaber_combat", "force_combat"],
            "Sith": ["lightsaber_combat", "force_combat"]
        }
        
        primary_list = profession_primary.get(profession, [])
        
        for skill in primary_list:
            if skill in skills and skills[skill].get('level', 0) > 0:
                primary_skills.append(skill)
        
        return primary_skills
    
    def _get_secondary_skills(self, profession: str, skills: Dict[str, Any]) -> List[str]:
        """Get secondary skills for a profession."""
        secondary_skills = []
        
        # Get profession-specific secondary skills
        profession_secondary = {
            "Brawler": ["brawler_combat", "unarmed_speed"],
            "Marksman": ["marksman_combat", "pistol_accuracy"],
            "Medic": ["medical_combat", "healing_combat"],
            "Jedi": ["force_healing", "force_lightning"],
            "Sith": ["force_healing", "force_lightning"]
        }
        
        secondary_list = profession_secondary.get(profession, [])
        
        for skill in secondary_list:
            if skill in skills and skills[skill].get('level', 0) > 0:
                secondary_skills.append(skill)
        
        return secondary_skills
    
    def _get_combat_capabilities(self, profession: str, skills: Dict[str, Any]) -> List[str]:
        """Get combat capabilities for a profession."""
        capabilities = []
        
        # Check for combat skills
        combat_skills = self.combat_skills.get(profession, [])
        
        for skill in combat_skills:
            if skill in skills and skills[skill].get('level', 0) > 0:
                capabilities.append(skill)
        
        return capabilities
    
    def _get_support_capabilities(self, profession: str, skills: Dict[str, Any]) -> List[str]:
        """Get support capabilities for a profession."""
        capabilities = []
        
        # Check for support skills
        support_skills = self.support_skills.get(profession, [])
        
        for skill in support_skills:
            if skill in skills and skills[skill].get('level', 0) > 0:
                capabilities.append(skill)
        
        return capabilities
    
    def _get_role_indicators(self, profession: str, skills: Dict[str, Any]) -> List[str]:
        """Get role indicators for a profession."""
        indicators = []
        
        # Add profession-based role indicator
        role = self.profession_roles.get(profession, CombatRole.SUPPORT)
        indicators.append(role.value)
        
        # Add skill-based indicators
        if any("healing" in skill for skill in skills):
            indicators.append("healer")
        
        if any("combat" in skill for skill in skills):
            indicators.append("combat")
        
        if any("support" in skill for skill in skills):
            indicators.append("support")
        
        return list(set(indicators))
    
    def _determine_combat_distance(self, weapon_preferences: List[str], primary_role: CombatRole) -> str:
        """Determine preferred combat distance."""
        if not weapon_preferences:
            return "medium"
        
        # Analyze weapon preferences
        melee_weapons = ["unarmed", "melee", "lightsaber"]
        ranged_weapons = ["rifle", "carbine", "pistol", "heavy_weapon"]
        
        melee_count = sum(1 for weapon in weapon_preferences if weapon in melee_weapons)
        ranged_count = sum(1 for weapon in weapon_preferences if weapon in ranged_weapons)
        
        if melee_count > ranged_count:
            return "close"
        elif ranged_count > melee_count:
            return "long"
        else:
            return "medium"
    
    def _determine_support_capacity(self, support_abilities: List[str], primary_role: CombatRole) -> str:
        """Determine support capacity."""
        if primary_role == CombatRole.HEALER:
            return "high"
        
        if len(support_abilities) > 3:
            return "high"
        elif len(support_abilities) > 1:
            return "medium"
        else:
            return "low"


def analyze_professions(professions: Dict[str, Dict[str, Any]]) -> Dict[str, ProfessionAnalysis]:
    """Analyze professions in skill tree.
    
    Parameters
    ----------
    professions : dict
        Professions data from skill tree
        
    Returns
    -------
    dict
        Analysis results for each profession
    """
    analyzer = ProfessionAnalyzer()
    return analyzer.analyze_professions(professions)


def determine_role(profession_analysis: Dict[str, ProfessionAnalysis]) -> RoleAnalysis:
    """Determine character role based on profession analysis.
    
    Parameters
    ----------
    profession_analysis : dict
        Analysis results for professions
        
    Returns
    -------
    RoleAnalysis
        Determined role analysis
    """
    analyzer = ProfessionAnalyzer()
    return analyzer.determine_role(profession_analysis) 