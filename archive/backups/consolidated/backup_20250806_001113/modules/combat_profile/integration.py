"""Skill Calculator Integration Module for Batch 041.

This module provides the complete workflow for importing SWGR skill calculator
URLs and auto-configuring combat logic for MS11.
"""

import logging
from typing import Dict, Optional, Any
from pathlib import Path

from .skill_calculator import SkillCalculator, parse_swgr_url, generate_combat_profile
from .profession_analyzer import ProfessionAnalyzer, analyze_professions, determine_role
from .combat_generator import CombatGenerator, generate_combat_config


class SkillCalculatorIntegration:
    """Main integration class for SWGR skill calculator integration."""
    
    def __init__(self):
        """Initialize the integration module."""
        self.logger = logging.getLogger(__name__)
        self.skill_calculator = SkillCalculator()
        self.profession_analyzer = ProfessionAnalyzer()
        self.combat_generator = CombatGenerator()
    
    def import_swgr_build(self, url: str, character_name: str = None) -> Optional[Dict[str, Any]]:
        """Import SWGR skill calculator build and generate combat profile.
        
        Parameters
        ----------
        url : str
            SWGR skill calculator URL
        character_name : str, optional
            Character name for the profile
            
        Returns
        -------
        dict or None
            Complete combat profile if successful, None otherwise
        """
        try:
            self.logger.info(f"Importing SWGR build: {url}")
            
            # Parse SWGR URL
            skill_tree = self.skill_calculator.parse_swgr_url(url)
            if not skill_tree:
                self.logger.error("Failed to parse SWGR URL")
                return None
            
            # Generate combat profile
            combat_profile = self.skill_calculator.generate_combat_profile(skill_tree)
            if not combat_profile:
                self.logger.error("Failed to generate combat profile")
                return None
            
            # Save combat profile
            if character_name:
                profile_name = f"{character_name}_combat_profile"
                self.combat_generator.save_combat_profile(combat_profile, profile_name)
                
                # Update character config
                self.combat_generator.update_character_config(combat_profile, character_name)
            
            self.logger.info(f"Successfully imported SWGR build for {character_name or 'Unknown'}")
            return combat_profile
            
        except Exception as e:
            self.logger.error(f"Error importing SWGR build: {e}")
            return None
    
    def analyze_skill_tree(self, skill_tree) -> Dict[str, Any]:
        """Analyze skill tree and generate detailed analysis.
        
        Parameters
        ----------
        skill_tree : SkillTree
            Parsed skill tree data
            
        Returns
        -------
        dict
            Detailed analysis results
        """
        try:
            self.logger.info("Analyzing skill tree")
            
            # Analyze professions
            profession_analysis = self.profession_analyzer.analyze_professions(skill_tree.professions)
            
            # Determine role
            role_analysis = self.profession_analyzer.determine_role(profession_analysis)
            
            # Generate combat config
            combat_config = self.combat_generator.generate_combat_config(
                skill_tree, profession_analysis, role_analysis
            )
            
            # Create comprehensive analysis
            analysis = {
                "skill_tree": {
                    "character_level": skill_tree.character_level,
                    "total_points": skill_tree.total_points,
                    "professions": skill_tree.professions,
                    "build_hash": skill_tree.build_hash,
                    "url": skill_tree.url
                },
                "profession_analysis": profession_analysis,
                "role_analysis": {
                    "primary_role": role_analysis.primary_role.value,
                    "secondary_roles": [role.value for role in role_analysis.secondary_roles],
                    "primary_profession": role_analysis.primary_profession,
                    "secondary_professions": role_analysis.secondary_professions,
                    "combat_abilities": role_analysis.combat_abilities,
                    "support_abilities": role_analysis.support_abilities,
                    "weapon_preferences": role_analysis.weapon_preferences,
                    "combat_distance": role_analysis.combat_distance,
                    "support_capacity": role_analysis.support_capacity
                },
                "combat_config": combat_config
            }
            
            self.logger.info("Completed skill tree analysis")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing skill tree: {e}")
            return {}
    
    def generate_character_config(self, combat_profile: Dict[str, Any], character_name: str) -> bool:
        """Generate character configuration from combat profile.
        
        Parameters
        ----------
        combat_profile : dict
            Combat profile data
        character_name : str
            Character name
            
        Returns
        -------
        bool
            True if configuration generated successfully
        """
        try:
            self.logger.info(f"Generating character config for {character_name}")
            
            # Update character config
            success = self.combat_generator.update_character_config(combat_profile, character_name)
            
            if success:
                self.logger.info(f"Successfully generated character config for {character_name}")
            else:
                self.logger.error(f"Failed to generate character config for {character_name}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error generating character config: {e}")
            return False
    
    def save_combat_profile(self, combat_profile: Dict[str, Any], profile_name: str) -> bool:
        """Save combat profile to file.
        
        Parameters
        ----------
        combat_profile : dict
            Combat profile data
        profile_name : str
            Name for the profile file
            
        Returns
        -------
        bool
            True if saved successfully
        """
        try:
            success = self.combat_generator.save_combat_profile(combat_profile, profile_name)
            
            if success:
                self.logger.info(f"Successfully saved combat profile: {profile_name}")
            else:
                self.logger.error(f"Failed to save combat profile: {profile_name}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error saving combat profile: {e}")
            return False
    
    def load_combat_profile(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """Load combat profile from file.
        
        Parameters
        ----------
        profile_name : str
            Name of the profile file
            
        Returns
        -------
        dict or None
            Combat profile data if loaded successfully
        """
        try:
            profile = self.combat_generator.load_combat_profile(profile_name)
            
            if profile:
                self.logger.info(f"Successfully loaded combat profile: {profile_name}")
            else:
                self.logger.warning(f"Combat profile not found: {profile_name}")
            
            return profile
            
        except Exception as e:
            self.logger.error(f"Error loading combat profile: {e}")
            return None
    
    def get_available_profiles(self) -> list:
        """Get list of available combat profiles.
        
        Returns
        -------
        list
            List of available profile names
        """
        try:
            profiles_dir = Path(__file__).resolve().parents[2] / "data" / "combat_profiles"
            
            if not profiles_dir.exists():
                return []
            
            profiles = []
            for profile_file in profiles_dir.glob("*.json"):
                profile_name = profile_file.stem
                profiles.append(profile_name)
            
            return profiles
            
        except Exception as e:
            self.logger.error(f"Error getting available profiles: {e}")
            return []
    
    def validate_swgr_url(self, url: str) -> bool:
        """Validate SWGR skill calculator URL.
        
        Parameters
        ----------
        url : str
            URL to validate
            
        Returns
        -------
        bool
            True if URL is valid
        """
        try:
            # Try to parse the URL
            skill_tree = self.skill_calculator.parse_swgr_url(url)
            return skill_tree is not None
            
        except Exception as e:
            self.logger.error(f"Error validating SWGR URL: {e}")
            return False


# Global integration instance
_integration = None

def get_integration() -> SkillCalculatorIntegration:
    """Get global integration instance."""
    global _integration
    if _integration is None:
        _integration = SkillCalculatorIntegration()
    return _integration


def import_swgr_build(url: str, character_name: str = None) -> Optional[Dict[str, Any]]:
    """Import SWGR skill calculator build and generate combat profile.
    
    Parameters
    ----------
    url : str
        SWGR skill calculator URL
    character_name : str, optional
        Character name for the profile
        
    Returns
    -------
    dict or None
        Complete combat profile if successful, None otherwise
    """
    integration = get_integration()
    return integration.import_swgr_build(url, character_name)


def analyze_skill_tree(skill_tree) -> Dict[str, Any]:
    """Analyze skill tree and generate detailed analysis.
    
    Parameters
    ----------
    skill_tree : SkillTree
        Parsed skill tree data
        
    Returns
    -------
    dict
        Detailed analysis results
    """
    integration = get_integration()
    return integration.analyze_skill_tree(skill_tree)


def validate_swgr_url(url: str) -> bool:
    """Validate SWGR skill calculator URL.
    
    Parameters
    ----------
    url : str
        URL to validate
        
    Returns
    -------
    bool
        True if URL is valid
    """
    integration = get_integration()
    return integration.validate_swgr_url(url)


def get_available_profiles() -> list:
    """Get list of available combat profiles.
    
    Returns
    -------
    list
        List of available profile names
    """
    integration = get_integration()
    return integration.get_available_profiles() 