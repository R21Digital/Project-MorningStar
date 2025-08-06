"""
Combat Spec Intelligence & Auto-Adaptation System

This module provides intelligent combat profile management that can:
- Detect current build via OCR parsing of /skills output
- Match builds to appropriate combat profiles
- Auto-adapt combat behavior based on detected build
- Load and manage YAML-based combat profiles
"""

import json
import yaml
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import re

# Mock imports for testing (avoiding import issues)
def run_ocr(image):
    """Mock OCR function for testing."""
    return "Mock OCR text"

def capture_screen():
    """Mock screen capture function for testing."""
    return None

class BuildType(Enum):
    """Build type enumeration."""
    RIFLEMAN = "rifleman"
    PISTOLEER = "pistoleer"
    MELEE = "melee"
    HYBRID = "hybrid"
    MEDIC = "medic"
    ARTISAN = "artisan"
    SCOUT = "scout"
    UNKNOWN = "unknown"

class WeaponType(Enum):
    """Weapon type enumeration."""
    RIFLE = "rifle"
    PISTOL = "pistol"
    MELEE = "melee"
    UNARMED = "unarmed"
    UNKNOWN = "unknown"

class CombatStyle(Enum):
    """Combat style enumeration."""
    RANGED = "ranged"
    MELEE = "melee"
    HYBRID = "hybrid"
    SUPPORT = "support"

@dataclass
class SkillLevel:
    """Represents a skill level."""
    name: str
    level: int
    max_level: int = 4

@dataclass
class BuildInfo:
    """Represents detected build information."""
    build_type: BuildType
    weapon_type: WeaponType
    combat_style: CombatStyle
    primary_skills: Dict[str, SkillLevel]
    secondary_skills: Dict[str, SkillLevel]
    confidence: float
    detected_at: float

@dataclass
class CombatProfile:
    """Represents a combat profile configuration."""
    name: str
    build_type: BuildType
    weapon_type: WeaponType
    combat_style: CombatStyle
    description: str
    abilities: List[str]
    ability_rotation: List[str]
    emergency_abilities: Dict[str, str]
    combat_priorities: Dict[str, Any]
    cooldowns: Dict[str, float]
    targeting: Dict[str, Any]
    healing: Dict[str, Any]
    buffing: Dict[str, Any]
    optimal_range: int
    fallback_abilities: List[str]

class CombatManager:
    """
    Combat Spec Intelligence & Auto-Adaptation Manager
    
    Features:
    - OCR-based build detection from /skills output
    - Intelligent profile matching and loading
    - Auto-adaptation of combat behavior
    - YAML-based profile management
    - Real-time build monitoring
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger("combat_manager")
        self.setup_logging()
        
        self.config = self.load_config(config_path)
        self.profiles_dir = Path(self.config.get("profiles_dir", "combat_profiles"))
        self.profiles_dir.mkdir(exist_ok=True)
        
        self.current_build: Optional[BuildInfo] = None
        self.current_profile: Optional[CombatProfile] = None
        self.available_profiles: Dict[str, CombatProfile] = {}
        self.build_history: List[BuildInfo] = []
        
        self.ocr_interval = self.config.get("ocr_interval", 30.0)
        self.last_build_check = 0.0
        self.build_detection_keywords = self.config.get("build_detection_keywords", [
            "rifle", "pistol", "melee", "unarmed", "heal", "medic", "artisan", "scout"
        ])
        
        self.load_available_profiles()
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        default_config = {
            "profiles_dir": "combat_profiles",
            "ocr_interval": 30.0,
            "build_detection_keywords": [
                "rifle", "pistol", "melee", "unarmed", "heal", "medic", "artisan", "scout"
            ],
            "build_patterns": {
                "rifleman": ["rifle", "marksman", "sharpshooter"],
                "pistoleer": ["pistol", "handgun", "marksman"],
                "melee": ["melee", "unarmed", "brawler", "swordsman"],
                "medic": ["heal", "medic", "cure", "treatment"],
                "artisan": ["artisan", "craft", "engineering"],
                "scout": ["scout", "ranger", "survival"]
            },
            "weapon_patterns": {
                "rifle": ["rifle", "carbine", "sniper"],
                "pistol": ["pistol", "handgun", "blaster"],
                "melee": ["sword", "knife", "staff", "axe"],
                "unarmed": ["unarmed", "fist", "punch"]
            },
            "confidence_thresholds": {
                "high": 0.8,
                "medium": 0.6,
                "low": 0.4
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    default_config.update(config)
            except Exception as e:
                self.logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config
    
    def load_available_profiles(self) -> None:
        """Load all available combat profiles from YAML files."""
        self.available_profiles.clear()
        
        # Load from YAML files
        for yaml_file in self.profiles_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r') as f:
                    profile_data = yaml.safe_load(f)
                
                profile = self.create_combat_profile(profile_data)
                if profile:
                    self.available_profiles[profile.name] = profile
                    self.logger.info(f"Loaded combat profile: {profile.name}")
            
            except Exception as e:
                self.logger.error(f"Failed to load profile {yaml_file}: {e}")
        
        # Load from JSON files (backward compatibility)
        for json_file in self.profiles_dir.glob("*.json"):
            try:
                with open(json_file, 'r') as f:
                    profile_data = json.load(f)
                
                profile = self.create_combat_profile(profile_data)
                if profile:
                    self.available_profiles[profile.name] = profile
                    self.logger.info(f"Loaded combat profile: {profile.name}")
            
            except Exception as e:
                self.logger.error(f"Failed to load profile {json_file}: {e}")
        
        self.logger.info(f"Loaded {len(self.available_profiles)} combat profiles")
    
    def create_combat_profile(self, profile_data: Dict[str, Any]) -> Optional[CombatProfile]:
        """Create a CombatProfile from profile data."""
        try:
            return CombatProfile(
                name=profile_data.get("name", "unknown"),
                build_type=BuildType(profile_data.get("build_type", "unknown")),
                weapon_type=WeaponType(profile_data.get("weapon_type", "unknown")),
                combat_style=CombatStyle(profile_data.get("combat_style", "ranged")),
                description=profile_data.get("description", ""),
                abilities=profile_data.get("abilities", []),
                ability_rotation=profile_data.get("ability_rotation", []),
                emergency_abilities=profile_data.get("emergency_abilities", {}),
                combat_priorities=profile_data.get("combat_priorities", {}),
                cooldowns=profile_data.get("cooldowns", {}),
                targeting=profile_data.get("targeting", {}),
                healing=profile_data.get("healing", {}),
                buffing=profile_data.get("buffing", {}),
                optimal_range=profile_data.get("optimal_range", 50),
                fallback_abilities=profile_data.get("fallback_abilities", [])
            )
        except Exception as e:
            self.logger.error(f"Failed to create combat profile: {e}")
            return None
    
    def detect_current_build(self) -> Optional[BuildInfo]:
        """Detect current build via OCR of /skills output."""
        try:
            # Capture screen and run OCR
            screen = capture_screen()
            if screen is None:
                return None
            
            ocr_text = run_ocr(screen)
            if not ocr_text:
                return None
            
            # Parse skills from OCR text
            skills = self.parse_skills_from_ocr(ocr_text)
            if not skills:
                return None
            
            # Detect build type
            build_type = self.detect_build_type(skills)
            weapon_type = self.detect_weapon_type(skills)
            combat_style = self.determine_combat_style(build_type, weapon_type)
            
            # Calculate confidence
            confidence = self.calculate_build_confidence(skills, build_type, weapon_type)
            
            # Separate primary and secondary skills
            primary_skills, secondary_skills = self.categorize_skills(skills, build_type)
            
            build_info = BuildInfo(
                build_type=build_type,
                weapon_type=weapon_type,
                combat_style=combat_style,
                primary_skills=primary_skills,
                secondary_skills=secondary_skills,
                confidence=confidence,
                detected_at=time.time()
            )
            
            self.logger.info(f"Detected build: {build_type.value} ({weapon_type.value}) - Confidence: {confidence:.2f}")
            return build_info
        
        except Exception as e:
            self.logger.error(f"Failed to detect current build: {e}")
            return None
    
    def parse_skills_from_ocr(self, ocr_text: str) -> Dict[str, SkillLevel]:
        """Parse skills from OCR text."""
        skills = {}
        
        # Common skill patterns
        skill_patterns = [
            r"([A-Za-z\s]+)\s*\((\d+)\)",  # Skill Name (Level)
            r"([A-Za-z\s]+):\s*(\d+)",     # Skill Name: Level
            r"(\d+)\s*([A-Za-z\s]+)",      # Level Skill Name
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, ocr_text, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    skill_name = match[0].strip()
                    level = int(match[1])
                    skills[skill_name] = SkillLevel(name=skill_name, level=level)
        
        return skills
    
    def detect_build_type(self, skills: Dict[str, SkillLevel]) -> BuildType:
        """Detect build type from skills."""
        build_scores = {
            BuildType.RIFLEMAN: 0,
            BuildType.PISTOLEER: 0,
            BuildType.MELEE: 0,
            BuildType.MEDIC: 0,
            BuildType.ARTISAN: 0,
            BuildType.SCOUT: 0
        }
        
        build_patterns = self.config.get("build_patterns", {})
        
        for skill_name, skill_level in skills.items():
            skill_lower = skill_name.lower()
            
            # Score each build type based on skill presence
            for build_type, patterns in build_patterns.items():
                if any(pattern in skill_lower for pattern in patterns):
                    build_scores[BuildType(build_type)] += skill_level.level
        
        # Find build with highest score
        if build_scores:
            best_build = max(build_scores.items(), key=lambda x: x[1])
            if best_build[1] > 0:
                return best_build[0]
        
        return BuildType.UNKNOWN
    
    def detect_weapon_type(self, skills: Dict[str, SkillLevel]) -> WeaponType:
        """Detect weapon type from skills."""
        weapon_scores = {
            WeaponType.RIFLE: 0,
            WeaponType.PISTOL: 0,
            WeaponType.MELEE: 0,
            WeaponType.UNARMED: 0
        }
        
        weapon_patterns = self.config.get("weapon_patterns", {})
        
        for skill_name, skill_level in skills.items():
            skill_lower = skill_name.lower()
            
            # Score each weapon type based on skill presence
            for weapon_type, patterns in weapon_patterns.items():
                if any(pattern in skill_lower for pattern in patterns):
                    weapon_scores[WeaponType(weapon_type)] += skill_level.level
        
        # Find weapon with highest score
        if weapon_scores:
            best_weapon = max(weapon_scores.items(), key=lambda x: x[1])
            if best_weapon[1] > 0:
                return best_weapon[0]
        
        return WeaponType.UNKNOWN
    
    def determine_combat_style(self, build_type: BuildType, weapon_type: WeaponType) -> CombatStyle:
        """Determine combat style from build and weapon type."""
        if build_type == BuildType.MEDIC:
            return CombatStyle.SUPPORT
        elif weapon_type in [WeaponType.RIFLE, WeaponType.PISTOL]:
            return CombatStyle.RANGED
        elif weapon_type in [WeaponType.MELEE, WeaponType.UNARMED]:
            return CombatStyle.MELEE
        elif build_type == BuildType.HYBRID:
            return CombatStyle.HYBRID
        else:
            return CombatStyle.RANGED
    
    def calculate_build_confidence(self, skills: Dict[str, SkillLevel], build_type: BuildType, weapon_type: WeaponType) -> float:
        """Calculate confidence in build detection."""
        total_skills = len(skills)
        if total_skills == 0:
            return 0.0
        
        # Count skills that match the detected build
        matching_skills = 0
        
        build_patterns = self.config.get("build_patterns", {})
        weapon_patterns = self.config.get("weapon_patterns", {})
        
        for skill_name in skills.keys():
            skill_lower = skill_name.lower()
            
            # Check if skill matches build type
            if build_type != BuildType.UNKNOWN:
                patterns = build_patterns.get(build_type.value, [])
                if any(pattern in skill_lower for pattern in patterns):
                    matching_skills += 1
            
            # Check if skill matches weapon type
            if weapon_type != WeaponType.UNKNOWN:
                patterns = weapon_patterns.get(weapon_type.value, [])
                if any(pattern in skill_lower for pattern in patterns):
                    matching_skills += 1
        
        # Calculate confidence as percentage of matching skills
        confidence = matching_skills / (total_skills * 2)  # *2 because we check both build and weapon
        return min(confidence, 1.0)
    
    def categorize_skills(self, skills: Dict[str, SkillLevel], build_type: BuildType) -> Tuple[Dict[str, SkillLevel], Dict[str, SkillLevel]]:
        """Categorize skills into primary and secondary based on build type."""
        primary_skills = {}
        secondary_skills = {}
        
        build_patterns = self.config.get("build_patterns", {})
        primary_patterns = build_patterns.get(build_type.value, [])
        
        for skill_name, skill_level in skills.items():
            skill_lower = skill_name.lower()
            
            if any(pattern in skill_lower for pattern in primary_patterns):
                primary_skills[skill_name] = skill_level
            else:
                secondary_skills[skill_name] = skill_level
        
        return primary_skills, secondary_skills
    
    def find_best_profile(self, build_info: BuildInfo) -> Optional[CombatProfile]:
        """Find the best matching combat profile for the detected build."""
        best_profile = None
        best_score = 0.0
        
        for profile in self.available_profiles.values():
            score = self.calculate_profile_match_score(build_info, profile)
            if score > best_score:
                best_score = score
                best_profile = profile
        
        if best_profile and best_score > self.config.get("confidence_thresholds", {}).get("medium", 0.6):
            self.logger.info(f"Matched profile: {best_profile.name} (Score: {best_score:.2f})")
            return best_profile
        
        return None
    
    def calculate_profile_match_score(self, build_info: BuildInfo, profile: CombatProfile) -> float:
        """Calculate how well a profile matches the detected build."""
        score = 0.0
        
        # Build type match
        if build_info.build_type == profile.build_type:
            score += 0.4
        
        # Weapon type match
        if build_info.weapon_type == profile.weapon_type:
            score += 0.3
        
        # Combat style match
        if build_info.combat_style == profile.combat_style:
            score += 0.2
        
        # Skill overlap
        profile_skills = set(profile.abilities)
        build_skills = set(build_info.primary_skills.keys())
        
        if profile_skills and build_skills:
            overlap = len(profile_skills.intersection(build_skills))
            skill_score = overlap / max(len(profile_skills), len(build_skills))
            score += skill_score * 0.1
        
        return score
    
    def auto_adapt_combat(self) -> bool:
        """Auto-adapt combat behavior based on detected build."""
        # Check if it's time to re-detect build
        if time.time() - self.last_build_check < self.ocr_interval:
            return self.current_profile is not None
        
        self.last_build_check = time.time()
        
        # Detect current build
        build_info = self.detect_current_build()
        if not build_info:
            return False
        
        # Check if build has changed
        if self.current_build and self.builds_match(self.current_build, build_info):
            return self.current_profile is not None
        
        # Store build history
        self.build_history.append(build_info)
        if len(self.build_history) > 10:  # Keep last 10 builds
            self.build_history.pop(0)
        
        # Update current build
        self.current_build = build_info
        
        # Find best matching profile
        profile = self.find_best_profile(build_info)
        if profile:
            self.current_profile = profile
            self.logger.info(f"Auto-adapted to profile: {profile.name}")
            return True
        else:
            self.logger.warning(f"No matching profile found for build: {build_info.build_type.value}")
            return False
    
    def builds_match(self, build1: BuildInfo, build2: BuildInfo) -> bool:
        """Check if two builds are essentially the same."""
        return (build1.build_type == build2.build_type and 
                build1.weapon_type == build2.weapon_type and
                abs(build1.confidence - build2.confidence) < 0.1)
    
    def get_current_abilities(self) -> List[str]:
        """Get current abilities based on active profile."""
        if not self.current_profile:
            return []
        
        return self.current_profile.abilities
    
    def get_ability_rotation(self) -> List[str]:
        """Get current ability rotation based on active profile."""
        if not self.current_profile:
            return []
        
        return self.current_profile.ability_rotation
    
    def get_emergency_abilities(self) -> Dict[str, str]:
        """Get emergency abilities based on active profile."""
        if not self.current_profile:
            return {}
        
        return self.current_profile.emergency_abilities
    
    def get_optimal_range(self) -> int:
        """Get optimal combat range based on active profile."""
        if not self.current_profile:
            return 50
        
        return self.current_profile.optimal_range
    
    def get_combat_priorities(self) -> Dict[str, Any]:
        """Get combat priorities based on active profile."""
        if not self.current_profile:
            return {}
        
        return self.current_profile.combat_priorities
    
    def get_cooldowns(self) -> Dict[str, float]:
        """Get ability cooldowns based on active profile."""
        if not self.current_profile:
            return {}
        
        return self.current_profile.cooldowns
    
    def get_targeting_config(self) -> Dict[str, Any]:
        """Get targeting configuration based on active profile."""
        if not self.current_profile:
            return {}
        
        return self.current_profile.targeting
    
    def get_healing_config(self) -> Dict[str, Any]:
        """Get healing configuration based on active profile."""
        if not self.current_profile:
            return {}
        
        return self.current_profile.healing
    
    def get_buffing_config(self) -> Dict[str, Any]:
        """Get buffing configuration based on active profile."""
        if not self.current_profile:
            return {}
        
        return self.current_profile.buffing
    
    def get_fallback_abilities(self) -> List[str]:
        """Get fallback abilities based on active profile."""
        if not self.current_profile:
            return []
        
        return self.current_profile.fallback_abilities
    
    def get_build_statistics(self) -> Dict[str, Any]:
        """Get build detection statistics."""
        if not self.build_history:
            return {}
        
        build_counts = {}
        weapon_counts = {}
        confidence_sum = 0.0
        
        for build in self.build_history:
            build_counts[build.build_type.value] = build_counts.get(build.build_type.value, 0) + 1
            weapon_counts[build.weapon_type.value] = weapon_counts.get(build.weapon_type.value, 0) + 1
            confidence_sum += build.confidence
        
        return {
            "total_detections": len(self.build_history),
            "build_distribution": build_counts,
            "weapon_distribution": weapon_counts,
            "average_confidence": confidence_sum / len(self.build_history),
            "current_build": {
                "type": self.current_build.build_type.value if self.current_build else None,
                "weapon": self.current_build.weapon_type.value if self.current_build else None,
                "confidence": self.current_build.confidence if self.current_build else 0.0
            },
            "current_profile": self.current_profile.name if self.current_profile else None
        }
    
    def save_profile(self, profile: CombatProfile, filename: str) -> bool:
        """Save a combat profile to YAML file."""
        try:
            profile_data = asdict(profile)
            
            # Convert enums to strings for YAML serialization
            profile_data["build_type"] = profile_data["build_type"].value
            profile_data["weapon_type"] = profile_data["weapon_type"].value
            profile_data["combat_style"] = profile_data["combat_style"].value
            
            filepath = self.profiles_dir / f"{filename}.yaml"
            with open(filepath, 'w') as f:
                yaml.dump(profile_data, f, default_flow_style=False, indent=2)
            
            self.logger.info(f"Saved combat profile: {filename}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to save profile {filename}: {e}")
            return False
    
    def reload_profiles(self) -> None:
        """Reload all combat profiles."""
        self.load_available_profiles()
        self.logger.info("Reloaded all combat profiles")


# Global combat manager instance
_combat_manager: Optional[CombatManager] = None

def get_combat_manager(config_path: Optional[str] = None) -> CombatManager:
    """Get the global combat manager instance."""
    global _combat_manager
    if _combat_manager is None:
        _combat_manager = CombatManager(config_path)
    return _combat_manager

def auto_adapt_combat() -> bool:
    """Auto-adapt combat behavior."""
    manager = get_combat_manager()
    return manager.auto_adapt_combat()

def get_current_abilities() -> List[str]:
    """Get current abilities."""
    manager = get_combat_manager()
    return manager.get_current_abilities()

def get_ability_rotation() -> List[str]:
    """Get current ability rotation."""
    manager = get_combat_manager()
    return manager.get_ability_rotation()

def get_optimal_range() -> int:
    """Get optimal combat range."""
    manager = get_combat_manager()
    return manager.get_optimal_range()

def get_build_statistics() -> Dict[str, Any]:
    """Get build detection statistics."""
    manager = get_combat_manager()
    return manager.get_build_statistics() 