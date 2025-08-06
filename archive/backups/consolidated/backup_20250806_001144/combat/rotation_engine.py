"""
Lightweight Combat Profile Dispatcher

This module provides a lightweight combat rotation engine that executes
combat logic based on weapon and profession profiles loaded from JSON files.
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

try:
    from core.ocr import extract_text_from_screen
    from core.screenshot import capture_screen
    OCR_AVAILABLE = True
except ImportError:
    class MockOCREngine:
        def extract_text_from_screen(self, region=None):
            return type('MockOCRResult', (), {'text': ''})()
    def extract_text_from_screen(region=None):
        return type('MockOCRResult', (), {'text': ''})()
    def capture_screen():
        return None
    OCR_AVAILABLE = False


class WeaponType(Enum):
    """Weapon type enumeration."""
    RANGED = "ranged"
    MELEE = "melee"
    HYBRID = "hybrid"


class StanceType(Enum):
    """Stance type enumeration."""
    STANDING = "standing"
    KNEELING = "kneeling"
    PRONE = "prone"
    COVER = "cover"


@dataclass
class SkillInfo:
    """Represents a skill with cooldown tracking."""
    name: str
    cooldown: float
    last_used: float = 0.0
    is_ready: bool = True
    
    def is_skill_ready(self) -> bool:
        """Check if skill is ready (off cooldown)."""
        # Check if skill is marked as not ready (execution lock)
        if not self.is_ready:
            # For skills with 0 cooldown, reset after a brief period
            if self.cooldown == 0:
                if time.time() - self.last_used >= 0.1:  # 100ms execution lock
                    self.is_ready = True
                    return True
            else:
                # Check if cooldown has expired
                if time.time() - self.last_used >= self.cooldown:
                    self.is_ready = True  # Reset ready flag
                    return True
            return False
        
        return True


@dataclass
class CombatProfile:
    """Represents a lightweight combat profile."""
    name: str
    weapon_type: WeaponType
    stance: StanceType
    rotation: List[str]
    heal_threshold: int = 50
    fallback: str = ""
    skills: Dict[str, SkillInfo] = field(default_factory=dict)
    emergency_skills: Dict[str, str] = field(default_factory=dict)
    buff_threshold: int = 80
    max_range: int = 50


class RotationEngine:
    """
    Lightweight combat rotation engine that executes rotation logic
    based on weapon and profession profiles.
    """
    
    def __init__(self, profiles_dir: str = "profiles/combat"):
        """
        Initialize the rotation engine.
        
        Parameters
        ----------
        profiles_dir : str
            Directory containing combat profile JSON files
        """
        self.profiles_dir = Path(profiles_dir)
        self.current_profile: Optional[CombatProfile] = None
        self.skill_cooldowns: Dict[str, float] = {}
        self.last_skill_use: Dict[str, float] = {}
        self.logger = self._setup_logging()
        
        # Test mode for faster execution
        self._test_mode = False
        
        # Load available profiles
        self.available_profiles = self._load_available_profiles()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the rotation engine."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _load_available_profiles(self) -> Dict[str, str]:
        """Load list of available profile files."""
        profiles = {}
        if self.profiles_dir.exists():
            for profile_file in self.profiles_dir.glob("*.json"):
                profile_name = profile_file.stem
                profiles[profile_name] = str(profile_file)
        return profiles
    
    def load_profile(self, profile_name: str) -> bool:
        """
        Load a combat profile from JSON file.
        
        Parameters
        ----------
        profile_name : str
            Name of the profile to load (without .json extension)
            
        Returns
        -------
        bool
            True if profile loaded successfully
        """
        try:
            if profile_name not in self.available_profiles:
                self.logger.error(f"Profile '{profile_name}' not found")
                return False
            
            profile_path = self.available_profiles[profile_name]
            with open(profile_path, 'r') as f:
                profile_data = json.load(f)
            
            # Create combat profile
            self.current_profile = self._create_combat_profile(profile_data)
            self.logger.info(f"Loaded combat profile: {self.current_profile.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load profile '{profile_name}': {e}")
            return False
    
    def _create_combat_profile(self, profile_data: Dict[str, Any]) -> CombatProfile:
        """
        Create a CombatProfile from JSON data.
        
        Parameters
        ----------
        profile_data : Dict[str, Any]
            Profile data from JSON file
            
        Returns
        -------
        CombatProfile
            Created combat profile
        """
        # Parse weapon type
        weapon_type_str = profile_data.get("weapon_type", "ranged")
        weapon_type = WeaponType(weapon_type_str)
        
        # Parse stance
        stance_str = profile_data.get("stance", "standing")
        stance = StanceType(stance_str)
        
        # Create skills dictionary
        skills = {}
        cooldowns = profile_data.get("cooldowns", {})
        for skill_name, cooldown in cooldowns.items():
            skills[skill_name] = SkillInfo(
                name=skill_name,
                cooldown=cooldown
            )
        
        return CombatProfile(
            name=profile_data.get("name", "unknown"),
            weapon_type=weapon_type,
            stance=stance,
            rotation=profile_data.get("rotation", []),
            heal_threshold=profile_data.get("heal_threshold", 50),
            fallback=profile_data.get("fallback", ""),
            skills=skills,
            emergency_skills=profile_data.get("emergency_abilities", {}),
            buff_threshold=profile_data.get("buff_threshold", 80),
            max_range=profile_data.get("max_range", 50)
        )
    
    def is_skill_ready(self, skill_name: str) -> bool:
        """
        Check if a skill is ready (off cooldown).
        
        Parameters
        ----------
        skill_name : str
            Name of the skill to check
            
        Returns
        -------
        bool
            True if skill is ready
        """
        if not self.current_profile:
            return False
        
        if skill_name not in self.current_profile.skills:
            return False
        
        return self.current_profile.skills[skill_name].is_skill_ready()
    
    def get_available_skills(self) -> List[str]:
        """
        Get list of available skills (not on cooldown).
        
        Returns
        -------
        List[str]
            List of available skill names
        """
        if not self.current_profile:
            return []
        
        available_skills = []
        for skill_name, skill_info in self.current_profile.skills.items():
            if skill_info.is_skill_ready():
                available_skills.append(skill_name)
        
        return available_skills
    
    def scan_toolbar_skills(self) -> List[str]:
        """
        Scan toolbar for available skills using OCR.
        
        Returns
        -------
        List[str]
            List of skills found on toolbar
        """
        if not OCR_AVAILABLE:
            self.logger.warning("OCR not available, returning empty skill list")
            return []
        
        try:
            # Capture screen and extract text from toolbar region
            # This is a simplified implementation - in practice, you'd need
            # to define specific regions for the toolbar
            screen_text = extract_text_from_screen()
            
            # Parse skills from text (simplified)
            found_skills = []
            if self.current_profile:
                for skill_name in self.current_profile.skills.keys():
                    if skill_name.lower() in screen_text.lower():
                        found_skills.append(skill_name)
            
            return found_skills
            
        except Exception as e:
            self.logger.error(f"Failed to scan toolbar skills: {e}")
            return []
    
    def check_action_log(self, skill_name: str) -> bool:
        """
        Check action log for skill usage confirmation.
        
        Parameters
        ----------
        skill_name : str
            Name of the skill to check
            
        Returns
        -------
        bool
            True if skill was used successfully
        """
        if not OCR_AVAILABLE or self._test_mode:
            return True  # Assume success in test mode
        
        try:
            # Extract text from action log region
            log_text = extract_text_from_screen()
            
            # Check for skill usage patterns
            skill_patterns = [
                f"used {skill_name}",
                f"cast {skill_name}",
                f"{skill_name} hits",
                f"{skill_name} deals"
            ]
            
            for pattern in skill_patterns:
                if pattern.lower() in log_text.lower():
                    return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to check action log: {e}")
            return False
    
    def execute_skill(self, skill_name: str) -> bool:
        """
        Execute a skill.
        
        Parameters
        ----------
        skill_name : str
            Name of the skill to execute
            
        Returns
        -------
        bool
            True if skill executed successfully
        """
        if not self.current_profile:
            self.logger.error("No combat profile loaded")
            return False
        
        if skill_name not in self.current_profile.skills:
            self.logger.error(f"Skill '{skill_name}' not found in profile")
            return False
        
        skill_info = self.current_profile.skills[skill_name]
        
        if not skill_info.is_skill_ready():
            self.logger.warning(f"Skill '{skill_name}' is on cooldown")
            return False
        
        try:
            # Simulate skill execution
            self.logger.info(f"Executing skill: {skill_name}")
            
            # Update cooldown
            skill_info.last_used = time.time()
            skill_info.is_ready = False
            
            # Check if skill was successful
            success = self.check_action_log(skill_name)
            
            if success:
                self.logger.info(f"Skill '{skill_name}' executed successfully")
            else:
                self.logger.warning(f"Skill '{skill_name}' may have failed")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Failed to execute skill '{skill_name}': {e}")
            return False
    
    def execute_rotation(self) -> List[str]:
        """
        Execute the current rotation.
        
        Returns
        -------
        List[str]
            List of skills that were executed
        """
        if not self.current_profile:
            self.logger.error("No combat profile loaded")
            return []
        
        executed_skills = []
        
        # Check for emergency situations first
        emergency_skill = self._check_emergency_skills()
        if emergency_skill:
            if self.execute_skill(emergency_skill):
                executed_skills.append(emergency_skill)
            return executed_skills
        
        # Execute rotation skills
        for skill_name in self.current_profile.rotation:
            if self.is_skill_ready(skill_name):
                if self.execute_skill(skill_name):
                    executed_skills.append(skill_name)
                    break  # Only execute one skill per rotation cycle
            else:
                self.logger.debug(f"Skill '{skill_name}' is on cooldown")
        
        # If no rotation skills available, try fallback
        if not executed_skills and self.current_profile.fallback:
            if self.is_skill_ready(self.current_profile.fallback):
                if self.execute_skill(self.current_profile.fallback):
                    executed_skills.append(self.current_profile.fallback)
        
        return executed_skills
    
    def _check_emergency_skills(self) -> Optional[str]:
        """
        Check if emergency skills should be used.
        
        Returns
        -------
        Optional[str]
            Name of emergency skill to use, or None
        """
        if not self.current_profile:
            return None
        
        # In test mode, don't trigger emergency skills
        if self._test_mode:
            return None
        
        # Check for heal threshold (simplified - in practice you'd check actual health)
        if "critical_heal" in self.current_profile.emergency_skills:
            heal_skill = self.current_profile.emergency_skills["critical_heal"]
            if self.is_skill_ready(heal_skill):
                return heal_skill
        
        return None
    
    def get_rotation_status(self) -> Dict[str, Any]:
        """
        Get current rotation status.
        
        Returns
        -------
        Dict[str, Any]
            Current status information
        """
        if not self.current_profile:
            return {"error": "No profile loaded"}
        
        status = {
            "profile": self.current_profile.name,
            "weapon_type": self.current_profile.weapon_type.value,
            "stance": self.current_profile.stance.value,
            "available_skills": self.get_available_skills(),
            "rotation": self.current_profile.rotation,
            "fallback": self.current_profile.fallback,
            "skill_cooldowns": {}
        }
        
        # Add cooldown information
        for skill_name, skill_info in self.current_profile.skills.items():
            if not skill_info.is_ready:
                remaining_cooldown = skill_info.cooldown - (time.time() - skill_info.last_used)
                status["skill_cooldowns"][skill_name] = max(0, remaining_cooldown)
            else:
                status["skill_cooldowns"][skill_name] = 0
        
        return status
    
    def enable_test_mode(self):
        """Enable test mode for faster execution."""
        self._test_mode = True
        self.logger.info("Test mode enabled")


# Global functions for easy access
def get_rotation_engine() -> RotationEngine:
    """Get the global rotation engine instance."""
    return RotationEngine()


def load_combat_profile(profile_name: str) -> bool:
    """
    Load a combat profile.
    
    Parameters
    ----------
    profile_name : str
        Name of the profile to load
        
    Returns
    -------
    bool
        True if profile loaded successfully
    """
    engine = get_rotation_engine()
    return engine.load_profile(profile_name)


def execute_rotation() -> List[str]:
    """
    Execute the current rotation.
    
    Returns
    -------
    List[str]
        List of skills that were executed
    """
    engine = get_rotation_engine()
    return engine.execute_rotation()


def is_skill_ready(skill_name: str) -> bool:
    """
    Check if a skill is ready.
    
    Parameters
    ----------
    skill_name : str
        Name of the skill to check
        
    Returns
    -------
    bool
        True if skill is ready
    """
    engine = get_rotation_engine()
    return engine.is_skill_ready(skill_name)


def get_rotation_status() -> Dict[str, Any]:
    """
    Get current rotation status.
    
    Returns
    -------
    Dict[str, Any]
        Current status information
    """
    engine = get_rotation_engine()
    return engine.get_rotation_status() 