"""Combat Profile Generator Module for Batch 041.

This module auto-generates combat profiles including combat distance,
support capacity, and weapon preferences based on skill analysis.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

from .skill_calculator import SkillTree
from .profession_analyzer import RoleAnalysis, CombatRole


class CombatGenerator:
    """Generates combat profiles from skill analysis."""
    
    def __init__(self):
        """Initialize the combat generator."""
        self.logger = logging.getLogger(__name__)
        
        # Combat profile templates
        self.combat_templates = {
            CombatRole.DPS: {
                "combat_style": "aggressive",
                "target_priority": "nearest",
                "retreat_threshold": 0.3,
                "support_threshold": 0.5,
                "ability_rotation": "damage_focused"
            },
            CombatRole.HEALER: {
                "combat_style": "defensive",
                "target_priority": "ally_lowest_health",
                "retreat_threshold": 0.5,
                "support_threshold": 0.2,
                "ability_rotation": "healing_focused"
            },
            CombatRole.SUPPORT: {
                "combat_style": "balanced",
                "target_priority": "nearest",
                "retreat_threshold": 0.4,
                "support_threshold": 0.3,
                "ability_rotation": "support_focused"
            },
            CombatRole.TANK: {
                "combat_style": "defensive",
                "target_priority": "nearest",
                "retreat_threshold": 0.2,
                "support_threshold": 0.6,
                "ability_rotation": "tank_focused"
            },
            CombatRole.HYBRID: {
                "combat_style": "adaptive",
                "target_priority": "nearest",
                "retreat_threshold": 0.4,
                "support_threshold": 0.4,
                "ability_rotation": "balanced"
            }
        }
        
        # Weapon-specific combat settings
        self.weapon_settings = {
            "unarmed": {
                "combat_distance": "close",
                "movement_speed": "fast",
                "attack_speed": "fast",
                "damage_type": "melee"
            },
            "melee": {
                "combat_distance": "close",
                "movement_speed": "medium",
                "attack_speed": "medium",
                "damage_type": "melee"
            },
            "lightsaber": {
                "combat_distance": "close",
                "movement_speed": "fast",
                "attack_speed": "fast",
                "damage_type": "energy"
            },
            "pistol": {
                "combat_distance": "medium",
                "movement_speed": "medium",
                "attack_speed": "fast",
                "damage_type": "ranged"
            },
            "rifle": {
                "combat_distance": "long",
                "movement_speed": "slow",
                "attack_speed": "medium",
                "damage_type": "ranged"
            },
            "carbine": {
                "combat_distance": "medium",
                "movement_speed": "medium",
                "attack_speed": "fast",
                "damage_type": "ranged"
            },
            "heavy_weapon": {
                "combat_distance": "long",
                "movement_speed": "slow",
                "attack_speed": "slow",
                "damage_type": "ranged"
            },
            "force": {
                "combat_distance": "medium",
                "movement_speed": "medium",
                "attack_speed": "medium",
                "damage_type": "energy"
            }
        }
        
        # Profession-specific ability sets
        self.ability_sets = {
            "Brawler": {
                "primary_abilities": ["unarmed_combat", "melee_combat"],
                "secondary_abilities": ["brawler_combat", "unarmed_speed"],
                "special_abilities": ["brawler_special"]
            },
            "Marksman": {
                "primary_abilities": ["pistol_combat", "rifle_combat"],
                "secondary_abilities": ["marksman_combat", "pistol_accuracy"],
                "special_abilities": ["marksman_special"]
            },
            "Medic": {
                "primary_abilities": ["healing", "medical"],
                "secondary_abilities": ["medical_combat", "healing_combat"],
                "special_abilities": ["medic_special"]
            },
            "Jedi": {
                "primary_abilities": ["lightsaber_combat", "force_combat"],
                "secondary_abilities": ["force_healing", "force_lightning"],
                "special_abilities": ["jedi_special"]
            },
            "Sith": {
                "primary_abilities": ["lightsaber_combat", "force_combat"],
                "secondary_abilities": ["force_healing", "force_lightning"],
                "special_abilities": ["sith_special"]
            }
        }
    
    def generate_combat_config(self, skill_tree: SkillTree, profession_analysis: Dict[str, Any], 
                              role_analysis: RoleAnalysis) -> Dict[str, Any]:
        """Generate combat configuration from skill analysis.
        
        Parameters
        ----------
        skill_tree : SkillTree
            Parsed skill tree data
        profession_analysis : dict
            Analysis results for professions
        role_analysis : RoleAnalysis
            Determined role analysis
            
        Returns
        -------
        dict
            Generated combat configuration
        """
        try:
            self.logger.info("Generating combat configuration")
            
            # Get base template for role
            base_config = self.combat_templates.get(role_analysis.primary_role, self.combat_templates[CombatRole.HYBRID])
            
            # Generate weapon-specific settings
            weapon_config = self._generate_weapon_config(role_analysis.weapon_preferences)
            
            # Generate ability configuration
            ability_config = self._generate_ability_config(role_analysis.primary_profession, skill_tree)
            
            # Generate support configuration
            support_config = self._generate_support_config(role_analysis)
            
            # Combine configurations
            combat_config = {
                "role": role_analysis.primary_role.value,
                "primary_profession": role_analysis.primary_profession,
                "secondary_professions": role_analysis.secondary_professions,
                "combat_distance": role_analysis.combat_distance,
                "support_capacity": role_analysis.support_capacity,
                "weapon_preferences": role_analysis.weapon_preferences,
                "combat_abilities": role_analysis.combat_abilities,
                "support_abilities": role_analysis.support_abilities,
                "combat_style": base_config["combat_style"],
                "target_priority": base_config["target_priority"],
                "retreat_threshold": base_config["retreat_threshold"],
                "support_threshold": base_config["support_threshold"],
                "ability_rotation": base_config["ability_rotation"],
                "weapon_config": weapon_config,
                "ability_config": ability_config,
                "support_config": support_config,
                "character_level": skill_tree.character_level,
                "total_points": skill_tree.total_points
            }
            
            self.logger.info(f"Generated combat config for {role_analysis.primary_role.value} role")
            return combat_config
            
        except Exception as e:
            self.logger.error(f"Error generating combat config: {e}")
            return {}
    
    def _generate_weapon_config(self, weapon_preferences: List[str]) -> Dict[str, Any]:
        """Generate weapon-specific configuration.
        
        Parameters
        ----------
        weapon_preferences : list
            List of preferred weapons
            
        Returns
        -------
        dict
            Weapon configuration
        """
        weapon_config = {}
        
        for weapon in weapon_preferences:
            if weapon in self.weapon_settings:
                weapon_config[weapon] = self.weapon_settings[weapon]
        
        # Set primary weapon (first preference)
        if weapon_preferences:
            primary_weapon = weapon_preferences[0]
            weapon_config["primary_weapon"] = primary_weapon
            weapon_config["primary_settings"] = self.weapon_settings.get(primary_weapon, {})
        
        return weapon_config
    
    def _generate_ability_config(self, primary_profession: str, skill_tree: SkillTree) -> Dict[str, Any]:
        """Generate ability configuration.
        
        Parameters
        ----------
        primary_profession : str
            Primary profession name
        skill_tree : SkillTree
            Skill tree data
            
        Returns
        -------
        dict
            Ability configuration
        """
        ability_config = {
            "primary_abilities": [],
            "secondary_abilities": [],
            "special_abilities": [],
            "ability_priorities": {}
        }
        
        # Get profession-specific abilities
        profession_abilities = self.ability_sets.get(primary_profession, {})
        
        # Add primary abilities
        for ability in profession_abilities.get("primary_abilities", []):
            if self._has_ability(skill_tree, primary_profession, ability):
                ability_config["primary_abilities"].append(ability)
                ability_config["ability_priorities"][ability] = "high"
        
        # Add secondary abilities
        for ability in profession_abilities.get("secondary_abilities", []):
            if self._has_ability(skill_tree, primary_profession, ability):
                ability_config["secondary_abilities"].append(ability)
                ability_config["ability_priorities"][ability] = "medium"
        
        # Add special abilities
        for ability in profession_abilities.get("special_abilities", []):
            if self._has_ability(skill_tree, primary_profession, ability):
                ability_config["special_abilities"].append(ability)
                ability_config["ability_priorities"][ability] = "high"
        
        return ability_config
    
    def _generate_support_config(self, role_analysis: RoleAnalysis) -> Dict[str, Any]:
        """Generate support configuration.
        
        Parameters
        ----------
        role_analysis : RoleAnalysis
            Role analysis data
            
        Returns
        -------
        dict
            Support configuration
        """
        support_config = {
            "support_capacity": role_analysis.support_capacity,
            "support_abilities": role_analysis.support_abilities,
            "healing_priority": "self",
            "buff_priority": "group",
            "support_threshold": 0.3
        }
        
        # Adjust based on role
        if role_analysis.primary_role == CombatRole.HEALER:
            support_config["healing_priority"] = "group"
            support_config["support_threshold"] = 0.2
        elif role_analysis.primary_role == CombatRole.SUPPORT:
            support_config["buff_priority"] = "group"
            support_config["support_threshold"] = 0.4
        else:
            support_config["healing_priority"] = "self"
            support_config["support_threshold"] = 0.5
        
        return support_config
    
    def _has_ability(self, skill_tree: SkillTree, profession: str, ability: str) -> bool:
        """Check if character has a specific ability.
        
        Parameters
        ----------
        skill_tree : SkillTree
            Skill tree data
        profession : str
            Profession name
        ability : str
            Ability name
            
        Returns
        -------
        bool
            True if character has the ability
        """
        profession_skills = skill_tree.get_profession_skills(profession)
        return ability in profession_skills and profession_skills[ability].get('level', 0) > 0
    
    def save_combat_profile(self, combat_config: Dict[str, Any], profile_name: str) -> bool:
        """Save combat profile to file.
        
        Parameters
        ----------
        combat_config : dict
            Combat configuration to save
        profile_name : str
            Name for the profile file
            
        Returns
        -------
        bool
            True if saved successfully
        """
        try:
            # Ensure profiles directory exists
            profiles_dir = Path(__file__).resolve().parents[2] / "data" / "combat_profiles"
            profiles_dir.mkdir(parents=True, exist_ok=True)
            
            # Save profile
            profile_path = profiles_dir / f"{profile_name}.json"
            with open(profile_path, 'w', encoding='utf-8') as f:
                json.dump(combat_config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved combat profile: {profile_path}")
            return True
            
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
            Combat configuration if loaded successfully
        """
        try:
            profiles_dir = Path(__file__).resolve().parents[2] / "data" / "combat_profiles"
            profile_path = profiles_dir / f"{profile_name}.json"
            
            if not profile_path.exists():
                self.logger.warning(f"Combat profile not found: {profile_path}")
                return None
            
            with open(profile_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.logger.info(f"Loaded combat profile: {profile_path}")
            return config
            
        except Exception as e:
            self.logger.error(f"Error loading combat profile: {e}")
            return None
    
    def update_character_config(self, combat_config: Dict[str, Any], character_name: str) -> bool:
        """Update character configuration with combat profile.
        
        Parameters
        ----------
        combat_config : dict
            Combat configuration
        character_name : str
            Character name
            
        Returns
        -------
        bool
            True if updated successfully
        """
        try:
            # Load current character config
            config_dir = Path(__file__).resolve().parents[2] / "config"
            config_path = config_dir / "config.json"
            
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {}
            
            # Update with combat profile data
            config["character_name"] = character_name
            config["combat_profile"] = {
                "role": combat_config.get("role", "hybrid"),
                "primary_profession": combat_config.get("primary_profession", "Unknown"),
                "combat_distance": combat_config.get("combat_distance", "medium"),
                "support_capacity": combat_config.get("support_capacity", "low"),
                "weapon_preferences": combat_config.get("weapon_preferences", []),
                "combat_abilities": combat_config.get("combat_abilities", []),
                "support_abilities": combat_config.get("support_abilities", [])
            }
            
            # Save updated config
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Updated character config for {character_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating character config: {e}")
            return False


def generate_combat_config(skill_tree: SkillTree, profession_analysis: Dict[str, Any], 
                          role_analysis: RoleAnalysis) -> Dict[str, Any]:
    """Generate combat configuration from skill analysis.
    
    Parameters
    ----------
    skill_tree : SkillTree
        Parsed skill tree data
    profession_analysis : dict
        Analysis results for professions
    role_analysis : RoleAnalysis
        Determined role analysis
        
    Returns
    -------
    dict
        Generated combat configuration
    """
    generator = CombatGenerator()
    return generator.generate_combat_config(skill_tree, profession_analysis, role_analysis) 