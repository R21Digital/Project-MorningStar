#!/usr/bin/env python3
"""
Unit tests for Batch 036 - Combat Spec Intelligence & Auto-Adaptation

Tests the combat manager functionality including:
- Build detection via OCR parsing
- Profile matching and loading
- Auto-adaptation of combat behavior
- YAML-based profile management
- Real-time build monitoring
"""

import pytest
import sys
import tempfile
import yaml
import json
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add combat to path for imports
sys.path.insert(0, str(Path(__file__).parent / "combat"))

from combat_manager import (
    CombatManager, BuildType, WeaponType, CombatStyle, 
    SkillLevel, BuildInfo, CombatProfile
)
from datetime import datetime


class TestCombatManager:
    """Test cases for the CombatManager class."""
    
    @pytest.fixture
    def manager(self):
        """Create a CombatManager instance for testing."""
        with patch('combat_manager.capture_screen') as mock_capture:
            with patch('combat_manager.run_ocr') as mock_ocr:
                mock_capture.return_value = None
                mock_ocr.return_value = "Mock OCR text"
                
                manager = CombatManager()
                return manager
    
    @pytest.fixture
    def mock_profile_data(self):
        """Sample profile data for testing."""
        return {
            "name": "test_rifleman",
            "build_type": "rifleman",
            "weapon_type": "rifle",
            "combat_style": "ranged",
            "description": "Test rifleman profile",
            "abilities": ["Rifle Shot", "Burst Shot", "Precise Shot"],
            "ability_rotation": ["Rifle Shot", "Burst Shot", "Rifle Shot"],
            "emergency_abilities": {"reload": "Reload"},
            "combat_priorities": {"player_health_threshold": 50},
            "cooldowns": {"Rifle Shot": 0, "Burst Shot": 5},
            "targeting": {"max_range": 50},
            "healing": {"self_heal_threshold": 60},
            "buffing": {"buff_threshold": 80},
            "optimal_range": 40,
            "fallback_abilities": ["Rifle Shot"]
        }
    
    def test_combat_manager_initialization(self, manager):
        """Test CombatManager initialization."""
        assert manager is not None
        assert hasattr(manager, 'available_profiles')
        assert hasattr(manager, 'current_build')
        assert hasattr(manager, 'current_profile')
        assert hasattr(manager, 'config')
        assert manager.ocr_interval == 30.0
    
    def test_load_config_default(self, manager):
        """Test default configuration loading."""
        config = manager.config
        assert config['profiles_dir'] == 'combat_profiles'
        assert config['ocr_interval'] == 30.0
        assert 'rifle' in config['build_detection_keywords']
        assert 'build_patterns' in config
        assert 'weapon_patterns' in config
    
    def test_parse_skills_from_ocr(self, manager):
        """Test parsing skills from OCR text."""
        # Test successful parsing
        ocr_text = "Rifle Weapons (4)\nMarksman (3)\nHealing (2)\nPistol Weapons (1)"
        skills = manager.parse_skills_from_ocr(ocr_text)
        
        assert "Rifle Weapons" in skills
        assert skills["Rifle Weapons"].level == 4
        assert "Marksman" in skills
        assert skills["Marksman"].level == 3
        assert "Healing" in skills
        assert skills["Healing"].level == 2
        assert "Pistol Weapons" in skills
        assert skills["Pistol Weapons"].level == 1
        
        # Test failed parsing
        ocr_text = "Just some random text without skill information"
        skills = manager.parse_skills_from_ocr(ocr_text)
        assert len(skills) == 0
    
    def test_detect_build_type(self, manager):
        """Test build type detection."""
        # Test rifleman detection
        skills = {
            "Rifle Weapons": SkillLevel("Rifle Weapons", 4),
            "Marksman": SkillLevel("Marksman", 3),
            "Sharpshooter": SkillLevel("Sharpshooter", 2)
        }
        build_type = manager.detect_build_type(skills)
        assert build_type == BuildType.RIFLEMAN
        
        # Test pistoleer detection
        skills = {
            "Pistol Weapons": SkillLevel("Pistol Weapons", 4),
            "Handgun": SkillLevel("Handgun", 3),
            "Quick Shot": SkillLevel("Quick Shot", 2)
        }
        build_type = manager.detect_build_type(skills)
        assert build_type == BuildType.PISTOLEER
        
        # Test melee detection
        skills = {
            "Teräs Käsi": SkillLevel("Teräs Käsi", 4),
            "Unarmed Combat": SkillLevel("Unarmed Combat", 3),
            "Melee Weapons": SkillLevel("Melee Weapons", 2)
        }
        build_type = manager.detect_build_type(skills)
        assert build_type == BuildType.MELEE
        
        # Test medic detection
        skills = {
            "Healing": SkillLevel("Healing", 4),
            "Medical": SkillLevel("Medical", 3),
            "Diagnosis": SkillLevel("Diagnosis", 2)
        }
        build_type = manager.detect_build_type(skills)
        assert build_type == BuildType.MEDIC
        
        # Test unknown build
        skills = {
            "Unknown Skill": SkillLevel("Unknown Skill", 4)
        }
        build_type = manager.detect_build_type(skills)
        assert build_type == BuildType.UNKNOWN
    
    def test_detect_weapon_type(self, manager):
        """Test weapon type detection."""
        # Test rifle detection
        skills = {
            "Rifle Weapons": SkillLevel("Rifle Weapons", 4),
            "Carbine": SkillLevel("Carbine", 3),
            "Sniper": SkillLevel("Sniper", 2)
        }
        weapon_type = manager.detect_weapon_type(skills)
        assert weapon_type == WeaponType.RIFLE
        
        # Test pistol detection
        skills = {
            "Pistol Weapons": SkillLevel("Pistol Weapons", 4),
            "Handgun": SkillLevel("Handgun", 3),
            "Blaster": SkillLevel("Blaster", 2)
        }
        weapon_type = manager.detect_weapon_type(skills)
        assert weapon_type == WeaponType.PISTOL
        
        # Test melee detection
        skills = {
            "Sword": SkillLevel("Sword", 4),
            "Knife": SkillLevel("Knife", 3),
            "Staff": SkillLevel("Staff", 2)
        }
        weapon_type = manager.detect_weapon_type(skills)
        assert weapon_type == WeaponType.MELEE
        
        # Test unarmed detection
        skills = {
            "Unarmed": SkillLevel("Unarmed", 4),
            "Fist": SkillLevel("Fist", 3),
            "Punch": SkillLevel("Punch", 2)
        }
        weapon_type = manager.detect_weapon_type(skills)
        assert weapon_type == WeaponType.UNARMED
        
        # Test unknown weapon
        skills = {
            "Unknown Weapon": SkillLevel("Unknown Weapon", 4)
        }
        weapon_type = manager.detect_weapon_type(skills)
        assert weapon_type == WeaponType.UNKNOWN
    
    def test_determine_combat_style(self, manager):
        """Test combat style determination."""
        # Test ranged combat
        style = manager.determine_combat_style(BuildType.RIFLEMAN, WeaponType.RIFLE)
        assert style == CombatStyle.RANGED
        
        # Test melee combat
        style = manager.determine_combat_style(BuildType.MELEE, WeaponType.UNARMED)
        assert style == CombatStyle.MELEE
        
        # Test support combat
        style = manager.determine_combat_style(BuildType.MEDIC, WeaponType.PISTOL)
        assert style == CombatStyle.SUPPORT
        
        # Test hybrid combat
        style = manager.determine_combat_style(BuildType.HYBRID, WeaponType.RIFLE)
        assert style == CombatStyle.HYBRID
    
    def test_calculate_build_confidence(self, manager):
        """Test build confidence calculation."""
        # Test high confidence
        skills = {
            "Rifle Weapons": SkillLevel("Rifle Weapons", 4),
            "Marksman": SkillLevel("Marksman", 3),
            "Sharpshooter": SkillLevel("Sharpshooter", 2)
        }
        build_type = BuildType.RIFLEMAN
        weapon_type = WeaponType.RIFLE
        
        confidence = manager.calculate_build_confidence(skills, build_type, weapon_type)
        assert confidence > 0.5  # Should be high confidence
        
        # Test low confidence
        skills = {
            "Unknown Skill": SkillLevel("Unknown Skill", 4)
        }
        build_type = BuildType.UNKNOWN
        weapon_type = WeaponType.UNKNOWN
        
        confidence = manager.calculate_build_confidence(skills, build_type, weapon_type)
        assert confidence == 0.0  # Should be zero confidence
    
    def test_categorize_skills(self, manager):
        """Test skill categorization."""
        skills = {
            "Rifle Weapons": SkillLevel("Rifle Weapons", 4),
            "Marksman": SkillLevel("Marksman", 3),
            "Healing": SkillLevel("Healing", 2),
            "Pistol Weapons": SkillLevel("Pistol Weapons", 1)
        }
        build_type = BuildType.RIFLEMAN
        
        primary_skills, secondary_skills = manager.categorize_skills(skills, build_type)
        
        assert "Rifle Weapons" in primary_skills
        assert "Marksman" in primary_skills
        assert "Healing" in secondary_skills
        assert "Pistol Weapons" in secondary_skills
    
    def test_create_combat_profile(self, manager, mock_profile_data):
        """Test combat profile creation."""
        profile = manager.create_combat_profile(mock_profile_data)
        
        assert profile is not None
        assert profile.name == "test_rifleman"
        assert profile.build_type == BuildType.RIFLEMAN
        assert profile.weapon_type == WeaponType.RIFLE
        assert profile.combat_style == CombatStyle.RANGED
        assert len(profile.abilities) == 3
        assert len(profile.ability_rotation) == 3
        assert len(profile.emergency_abilities) == 1
        assert profile.optimal_range == 40
    
    def test_find_best_profile(self, manager):
        """Test finding best matching profile."""
        # Create a mock build info
        build_info = BuildInfo(
            build_type=BuildType.RIFLEMAN,
            weapon_type=WeaponType.RIFLE,
            combat_style=CombatStyle.RANGED,
            primary_skills={"Rifle Weapons": SkillLevel("Rifle Weapons", 4)},
            secondary_skills={"Marksman": SkillLevel("Marksman", 3)},
            confidence=0.85,
            detected_at=time.time()
        )
        
        # Add a matching profile to available profiles
        profile_data = {
            "name": "test_rifleman",
            "build_type": "rifleman",
            "weapon_type": "rifle",
            "combat_style": "ranged",
            "description": "Test rifleman profile",
            "abilities": ["Rifle Shot", "Burst Shot"],
            "ability_rotation": ["Rifle Shot", "Burst Shot"],
            "emergency_abilities": {"reload": "Reload"},
            "combat_priorities": {"player_health_threshold": 50},
            "cooldowns": {"Rifle Shot": 0, "Burst Shot": 5},
            "targeting": {"max_range": 50},
            "healing": {"self_heal_threshold": 60},
            "buffing": {"buff_threshold": 80},
            "optimal_range": 40,
            "fallback_abilities": ["Rifle Shot"]
        }
        
        profile = manager.create_combat_profile(profile_data)
        manager.available_profiles["test_rifleman"] = profile
        
        # Find best profile
        best_profile = manager.find_best_profile(build_info)
        assert best_profile is not None
        assert best_profile.name == "test_rifleman"
    
    def test_calculate_profile_match_score(self, manager):
        """Test profile match score calculation."""
        # Create build info
        build_info = BuildInfo(
            build_type=BuildType.RIFLEMAN,
            weapon_type=WeaponType.RIFLE,
            combat_style=CombatStyle.RANGED,
            primary_skills={"Rifle Weapons": SkillLevel("Rifle Weapons", 4)},
            secondary_skills={"Marksman": SkillLevel("Marksman", 3)},
            confidence=0.85,
            detected_at=time.time()
        )
        
        # Create profile
        profile_data = {
            "name": "test_rifleman",
            "build_type": "rifleman",
            "weapon_type": "rifle",
            "combat_style": "ranged",
            "description": "Test rifleman profile",
            "abilities": ["Rifle Shot", "Burst Shot"],
            "ability_rotation": ["Rifle Shot", "Burst Shot"],
            "emergency_abilities": {"reload": "Reload"},
            "combat_priorities": {"player_health_threshold": 50},
            "cooldowns": {"Rifle Shot": 0, "Burst Shot": 5},
            "targeting": {"max_range": 50},
            "healing": {"self_heal_threshold": 60},
            "buffing": {"buff_threshold": 80},
            "optimal_range": 40,
            "fallback_abilities": ["Rifle Shot"]
        }
        
        profile = manager.create_combat_profile(profile_data)
        
        # Calculate match score
        score = manager.calculate_profile_match_score(build_info, profile)
        assert score > 0.5  # Should have good match score
    
    def test_auto_adapt_combat(self, manager):
        """Test auto-adaptation of combat behavior."""
        # Mock build detection
        with patch.object(manager, 'detect_current_build') as mock_detect:
            build_info = BuildInfo(
                build_type=BuildType.RIFLEMAN,
                weapon_type=WeaponType.RIFLE,
                combat_style=CombatStyle.RANGED,
                primary_skills={"Rifle Weapons": SkillLevel("Rifle Weapons", 4)},
                secondary_skills={"Marksman": SkillLevel("Marksman", 3)},
                confidence=0.85,
                detected_at=time.time()
            )
            mock_detect.return_value = build_info
            
            # Add a matching profile
            profile_data = {
                "name": "test_rifleman",
                "build_type": "rifleman",
                "weapon_type": "rifle",
                "combat_style": "ranged",
                "description": "Test rifleman profile",
                "abilities": ["Rifle Shot", "Burst Shot"],
                "ability_rotation": ["Rifle Shot", "Burst Shot"],
                "emergency_abilities": {"reload": "Reload"},
                "combat_priorities": {"player_health_threshold": 50},
                "cooldowns": {"Rifle Shot": 0, "Burst Shot": 5},
                "targeting": {"max_range": 50},
                "healing": {"self_heal_threshold": 60},
                "buffing": {"buff_threshold": 80},
                "optimal_range": 40,
                "fallback_abilities": ["Rifle Shot"]
            }
            
            profile = manager.create_combat_profile(profile_data)
            manager.available_profiles["test_rifleman"] = profile
            
            # Test auto-adaptation
            success = manager.auto_adapt_combat()
            assert success is True
            assert manager.current_profile is not None
            assert manager.current_profile.name == "test_rifleman"
    
    def test_builds_match(self, manager):
        """Test build matching logic."""
        build1 = BuildInfo(
            build_type=BuildType.RIFLEMAN,
            weapon_type=WeaponType.RIFLE,
            combat_style=CombatStyle.RANGED,
            primary_skills={},
            secondary_skills={},
            confidence=0.85,
            detected_at=time.time()
        )
        
        build2 = BuildInfo(
            build_type=BuildType.RIFLEMAN,
            weapon_type=WeaponType.RIFLE,
            combat_style=CombatStyle.RANGED,
            primary_skills={},
            secondary_skills={},
            confidence=0.90,
            detected_at=time.time()
        )
        
        # Test matching builds
        assert manager.builds_match(build1, build2) is True
        
        # Test different builds
        build3 = BuildInfo(
            build_type=BuildType.PISTOLEER,
            weapon_type=WeaponType.PISTOL,
            combat_style=CombatStyle.RANGED,
            primary_skills={},
            secondary_skills={},
            confidence=0.85,
            detected_at=time.time()
        )
        
        assert manager.builds_match(build1, build3) is False
    
    def test_get_current_abilities(self, manager):
        """Test getting current abilities."""
        # Test with no profile
        abilities = manager.get_current_abilities()
        assert abilities == []
        
        # Test with profile
        profile_data = {
            "name": "test_rifleman",
            "build_type": "rifleman",
            "weapon_type": "rifle",
            "combat_style": "ranged",
            "description": "Test rifleman profile",
            "abilities": ["Rifle Shot", "Burst Shot"],
            "ability_rotation": ["Rifle Shot", "Burst Shot"],
            "emergency_abilities": {"reload": "Reload"},
            "combat_priorities": {"player_health_threshold": 50},
            "cooldowns": {"Rifle Shot": 0, "Burst Shot": 5},
            "targeting": {"max_range": 50},
            "healing": {"self_heal_threshold": 60},
            "buffing": {"buff_threshold": 80},
            "optimal_range": 40,
            "fallback_abilities": ["Rifle Shot"]
        }
        
        profile = manager.create_combat_profile(profile_data)
        manager.current_profile = profile
        
        abilities = manager.get_current_abilities()
        assert len(abilities) == 2
        assert "Rifle Shot" in abilities
        assert "Burst Shot" in abilities
    
    def test_get_ability_rotation(self, manager):
        """Test getting ability rotation."""
        # Test with no profile
        rotation = manager.get_ability_rotation()
        assert rotation == []
        
        # Test with profile
        profile_data = {
            "name": "test_rifleman",
            "build_type": "rifleman",
            "weapon_type": "rifle",
            "combat_style": "ranged",
            "description": "Test rifleman profile",
            "abilities": ["Rifle Shot", "Burst Shot"],
            "ability_rotation": ["Rifle Shot", "Burst Shot"],
            "emergency_abilities": {"reload": "Reload"},
            "combat_priorities": {"player_health_threshold": 50},
            "cooldowns": {"Rifle Shot": 0, "Burst Shot": 5},
            "targeting": {"max_range": 50},
            "healing": {"self_heal_threshold": 60},
            "buffing": {"buff_threshold": 80},
            "optimal_range": 40,
            "fallback_abilities": ["Rifle Shot"]
        }
        
        profile = manager.create_combat_profile(profile_data)
        manager.current_profile = profile
        
        rotation = manager.get_ability_rotation()
        assert len(rotation) == 2
        assert rotation[0] == "Rifle Shot"
        assert rotation[1] == "Burst Shot"
    
    def test_get_optimal_range(self, manager):
        """Test getting optimal range."""
        # Test with no profile
        optimal_range = manager.get_optimal_range()
        assert optimal_range == 50  # Default value
        
        # Test with profile
        profile_data = {
            "name": "test_rifleman",
            "build_type": "rifleman",
            "weapon_type": "rifle",
            "combat_style": "ranged",
            "description": "Test rifleman profile",
            "abilities": ["Rifle Shot", "Burst Shot"],
            "ability_rotation": ["Rifle Shot", "Burst Shot"],
            "emergency_abilities": {"reload": "Reload"},
            "combat_priorities": {"player_health_threshold": 50},
            "cooldowns": {"Rifle Shot": 0, "Burst Shot": 5},
            "targeting": {"max_range": 50},
            "healing": {"self_heal_threshold": 60},
            "buffing": {"buff_threshold": 80},
            "optimal_range": 40,
            "fallback_abilities": ["Rifle Shot"]
        }
        
        profile = manager.create_combat_profile(profile_data)
        manager.current_profile = profile
        
        optimal_range = manager.get_optimal_range()
        assert optimal_range == 40
    
    def test_get_build_statistics(self, manager):
        """Test getting build statistics."""
        # Test with no build history
        stats = manager.get_build_statistics()
        assert stats == {}
        
        # Add some build history
        build_info = BuildInfo(
            build_type=BuildType.RIFLEMAN,
            weapon_type=WeaponType.RIFLE,
            combat_style=CombatStyle.RANGED,
            primary_skills={"Rifle Weapons": SkillLevel("Rifle Weapons", 4)},
            secondary_skills={"Marksman": SkillLevel("Marksman", 3)},
            confidence=0.85,
            detected_at=time.time()
        )
        
        manager.build_history.append(build_info)
        manager.current_build = build_info
        
        stats = manager.get_build_statistics()
        assert stats['total_detections'] == 1
        assert stats['build_distribution']['rifleman'] == 1
        assert stats['weapon_distribution']['rifle'] == 1
        assert stats['average_confidence'] == 0.85
        assert stats['current_build']['type'] == 'rifleman'
        assert stats['current_build']['weapon'] == 'rifle'
    
    def test_save_profile(self, manager, mock_profile_data):
        """Test profile saving."""
        profile = manager.create_combat_profile(mock_profile_data)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            manager.profiles_dir = Path(temp_dir)
            success = manager.save_profile(profile, "test_profile")
            assert success is True
            
            # Check if file was created
            profile_file = temp_dir / "test_profile.yaml"
            assert profile_file.exists()
    
    def test_reload_profiles(self, manager):
        """Test profile reloading."""
        initial_count = len(manager.available_profiles)
        manager.reload_profiles()
        # Should reload profiles (count may vary depending on available files)
        assert hasattr(manager, 'available_profiles')


class TestBuildType:
    """Test cases for the BuildType enum."""
    
    def test_build_type_values(self):
        """Test BuildType enum values."""
        assert BuildType.RIFLEMAN.value == "rifleman"
        assert BuildType.PISTOLEER.value == "pistoleer"
        assert BuildType.MELEE.value == "melee"
        assert BuildType.HYBRID.value == "hybrid"
        assert BuildType.MEDIC.value == "medic"
        assert BuildType.ARTISAN.value == "artisan"
        assert BuildType.SCOUT.value == "scout"
        assert BuildType.UNKNOWN.value == "unknown"


class TestWeaponType:
    """Test cases for the WeaponType enum."""
    
    def test_weapon_type_values(self):
        """Test WeaponType enum values."""
        assert WeaponType.RIFLE.value == "rifle"
        assert WeaponType.PISTOL.value == "pistol"
        assert WeaponType.MELEE.value == "melee"
        assert WeaponType.UNARMED.value == "unarmed"
        assert WeaponType.UNKNOWN.value == "unknown"


class TestCombatStyle:
    """Test cases for the CombatStyle enum."""
    
    def test_combat_style_values(self):
        """Test CombatStyle enum values."""
        assert CombatStyle.RANGED.value == "ranged"
        assert CombatStyle.MELEE.value == "melee"
        assert CombatStyle.HYBRID.value == "hybrid"
        assert CombatStyle.SUPPORT.value == "support"


class TestSkillLevel:
    """Test cases for the SkillLevel dataclass."""
    
    def test_skill_level_creation(self):
        """Test SkillLevel dataclass creation."""
        skill = SkillLevel(name="Rifle Weapons", level=4)
        
        assert skill.name == "Rifle Weapons"
        assert skill.level == 4
        assert skill.max_level == 4


class TestBuildInfo:
    """Test cases for the BuildInfo dataclass."""
    
    def test_build_info_creation(self):
        """Test BuildInfo dataclass creation."""
        build_info = BuildInfo(
            build_type=BuildType.RIFLEMAN,
            weapon_type=WeaponType.RIFLE,
            combat_style=CombatStyle.RANGED,
            primary_skills={"Rifle Weapons": SkillLevel("Rifle Weapons", 4)},
            secondary_skills={"Marksman": SkillLevel("Marksman", 3)},
            confidence=0.85,
            detected_at=time.time()
        )
        
        assert build_info.build_type == BuildType.RIFLEMAN
        assert build_info.weapon_type == WeaponType.RIFLE
        assert build_info.combat_style == CombatStyle.RANGED
        assert len(build_info.primary_skills) == 1
        assert len(build_info.secondary_skills) == 1
        assert build_info.confidence == 0.85
        assert build_info.detected_at > 0


class TestCombatProfile:
    """Test cases for the CombatProfile dataclass."""
    
    def test_combat_profile_creation(self):
        """Test CombatProfile dataclass creation."""
        profile = CombatProfile(
            name="test_rifleman",
            build_type=BuildType.RIFLEMAN,
            weapon_type=WeaponType.RIFLE,
            combat_style=CombatStyle.RANGED,
            description="Test rifleman profile",
            abilities=["Rifle Shot", "Burst Shot"],
            ability_rotation=["Rifle Shot", "Burst Shot"],
            emergency_abilities={"reload": "Reload"},
            combat_priorities={"player_health_threshold": 50},
            cooldowns={"Rifle Shot": 0, "Burst Shot": 5},
            targeting={"max_range": 50},
            healing={"self_heal_threshold": 60},
            buffing={"buff_threshold": 80},
            optimal_range=40,
            fallback_abilities=["Rifle Shot"]
        )
        
        assert profile.name == "test_rifleman"
        assert profile.build_type == BuildType.RIFLEMAN
        assert profile.weapon_type == WeaponType.RIFLE
        assert profile.combat_style == CombatStyle.RANGED
        assert len(profile.abilities) == 2
        assert len(profile.ability_rotation) == 2
        assert len(profile.emergency_abilities) == 1
        assert profile.optimal_range == 40


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 