#!/usr/bin/env python3
"""
MS11 Batch 094 - Heroic Support & Group Questing Mode (Phase 1) Tests

This test suite validates the core functionalities of the heroic support system:
- Heroic database management
- Group detection and coordination
- Auto-follow functionality
- Configuration management
- Group state management
"""

import pytest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from core.heroic_support import (
    HeroicSupport, HeroicDatabase, GroupDetector, GroupFollower, GroupCoordinator,
    GroupStatus, HeroicDifficulty, GroupMember, HeroicInstance, GroupState, FollowTarget
)


class TestHeroicDatabase:
    """Test heroic database functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir) / "heroics"
        self.data_dir.mkdir()
        
        # Create test heroics index
        self.heroics_index = {
            "heroics": {
                "test_heroic": {
                    "name": "Test Heroic",
                    "planet": "test_planet",
                    "location": "test_location",
                    "coordinates": [100, 200],
                    "difficulty_tiers": ["normal"],
                    "level_requirement": 80,
                    "group_size": "4-8 players"
                }
            }
        }
        
        # Create test heroic file
        self.heroic_data = {
            "heroic_id": "test_heroic",
            "name": "Test Heroic",
            "planet": "test_planet",
            "location": "test_location",
            "coordinates": [100, 200],
            "difficulty_tiers": ["normal"],
            "level_requirement": 80,
            "group_size": "4-8 players",
            "prerequisites": {
                "quests": [{"quest_id": "test_quest", "name": "Test Quest"}]
            },
            "bosses": [{"name": "Test Boss", "level": 85}],
            "rewards": {"normal": {"experience": 50000}}
        }
        
        # Write test files
        import yaml
        with open(self.data_dir / "heroics_index.yml", 'w') as f:
            yaml.dump(self.heroics_index, f)
            
        with open(self.data_dir / "test_heroic.yml", 'w') as f:
            yaml.dump(self.heroic_data, f)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_init(self):
        """Test database initialization."""
        db = HeroicDatabase(str(self.data_dir))
        assert len(db.heroics) == 1
        assert "test_heroic" in db.heroics
    
    def test_get_heroic(self):
        """Test getting heroic by ID."""
        db = HeroicDatabase(str(self.data_dir))
        heroic = db.get_heroic("test_heroic")
        
        assert heroic is not None
        assert heroic.heroic_id == "test_heroic"
        assert heroic.name == "Test Heroic"
        assert heroic.planet == "test_planet"
    
    def test_get_heroic_not_found(self):
        """Test getting non-existent heroic."""
        db = HeroicDatabase(str(self.data_dir))
        heroic = db.get_heroic("non_existent")
        
        assert heroic is None
    
    def test_get_available_heroics(self):
        """Test getting available heroics for character level."""
        db = HeroicDatabase(str(self.data_dir))
        
        # Level 70 should not have access
        heroics_70 = db.get_available_heroics(70)
        assert len(heroics_70) == 0
        
        # Level 80 should have access
        heroics_80 = db.get_available_heroics(80)
        assert len(heroics_80) == 1
        assert heroics_80[0].heroic_id == "test_heroic"
        
        # Level 90 should have access
        heroics_90 = db.get_available_heroics(90)
        assert len(heroics_90) == 1
    
    def test_get_heroic_by_location(self):
        """Test getting heroic by location."""
        db = HeroicDatabase(str(self.data_dir))
        heroic = db.get_heroic_by_location("test_planet", "test_location")
        
        assert heroic is not None
        assert heroic.heroic_id == "test_heroic"
    
    def test_get_heroic_by_location_not_found(self):
        """Test getting heroic by non-existent location."""
        db = HeroicDatabase(str(self.data_dir))
        heroic = db.get_heroic_by_location("wrong_planet", "wrong_location")
        
        assert heroic is None


class TestGroupDetector:
    """Test group detection functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            "heroic_mode": {"enabled": True},
            "group_behavior": {"follow_distance": 10}
        }
        self.detector = GroupDetector(self.config)
    
    def test_detect_group_status_solo(self):
        """Test detecting solo status."""
        status = self.detector.detect_group_status()
        assert status == GroupStatus.SOLO
    
    def test_detect_group_status_forming_chat(self):
        """Test detecting forming status from chat."""
        chat_text = "Player invites you to join their group"
        status = self.detector.detect_group_status(chat_text=chat_text)
        assert status == GroupStatus.FORMING
    
    def test_detect_group_status_ready_chat(self):
        """Test detecting ready status from chat."""
        chat_text = "Everyone ready for the boss fight?"
        status = self.detector.detect_group_status(chat_text=chat_text)
        assert status == GroupStatus.READY
    
    def test_detect_group_status_in_progress_chat(self):
        """Test detecting in-progress status from chat."""
        chat_text = "Inside heroic - following leader"
        status = self.detector.detect_group_status(chat_text=chat_text)
        assert status == GroupStatus.IN_PROGRESS
    
    def test_detect_group_status_ui_forming(self):
        """Test detecting forming status from UI."""
        ui_elements = {"group_window": True, "member_list": True}
        status = self.detector.detect_group_status(ui_elements=ui_elements)
        assert status == GroupStatus.FORMING
    
    def test_detect_group_status_ui_ready(self):
        """Test detecting ready status from UI."""
        ui_elements = {"group_ready_indicator": True}
        status = self.detector.detect_group_status(ui_elements=ui_elements)
        assert status == GroupStatus.READY
    
    def test_detect_group_status_ui_in_progress(self):
        """Test detecting in-progress status from UI."""
        ui_elements = {"heroic_instance_indicator": True}
        status = self.detector.detect_group_status(ui_elements=ui_elements)
        assert status == GroupStatus.IN_PROGRESS
    
    def test_has_group_interface(self):
        """Test group interface detection."""
        ui_elements = {"group_window": True}
        assert self.detector._has_group_interface(ui_elements) is True
        
        ui_elements = {"other_element": True}
        assert self.detector._has_group_interface(ui_elements) is False
    
    def test_has_group_chat(self):
        """Test group chat detection."""
        chat_text = "Player invites you to join their group"
        assert self.detector._has_group_chat(chat_text) is True
        
        chat_text = "Regular chat message"
        assert self.detector._has_group_chat(chat_text) is False


class TestGroupFollower:
    """Test group following functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            "group_behavior": {
                "follow_distance": 10,
                "follow_timeout": 60
            }
        }
        self.follower = GroupFollower(self.config)
    
    def test_start_following(self):
        """Test starting to follow a target."""
        success = self.follower.start_following("TestLeader", "leader")
        
        assert success is True
        assert self.follower.is_following is True
        assert self.follower.current_target is not None
        assert self.follower.current_target.target_name == "TestLeader"
        assert self.follower.current_target.target_type == "leader"
    
    def test_stop_following(self):
        """Test stopping following."""
        self.follower.start_following("TestLeader", "leader")
        success = self.follower.stop_following()
        
        assert success is True
        assert self.follower.is_following is False
        assert self.follower.current_target is None
    
    def test_stop_following_not_following(self):
        """Test stopping following when not following."""
        success = self.follower.stop_following()
        
        assert success is True
        assert self.follower.is_following is False
    
    def test_update_target_position(self):
        """Test updating target position."""
        self.follower.start_following("TestLeader", "leader")
        success = self.follower.update_target_position([100, 200])
        
        assert success is True
        assert self.follower.current_target.last_position == [100, 200]
    
    def test_update_target_position_not_following(self):
        """Test updating target position when not following."""
        success = self.follower.update_target_position([100, 200])
        
        assert success is False
    
    def test_check_follow_timeout_not_started(self):
        """Test checking timeout when following hasn't started."""
        timeout = self.follower.check_follow_timeout()
        assert timeout is False
    
    def test_check_follow_timeout_not_expired(self):
        """Test checking timeout when not expired."""
        self.follower.start_following("TestLeader", "leader")
        timeout = self.follower.check_follow_timeout()
        assert timeout is False
    
    @patch('core.heroic_support.datetime')
    def test_check_follow_timeout_expired(self, mock_datetime):
        """Test checking timeout when expired."""
        # Mock current time to be after timeout
        mock_datetime.now.return_value = datetime.now() + timedelta(seconds=70)
        
        self.follower.start_following("TestLeader", "leader")
        timeout = self.follower.check_follow_timeout()
        assert timeout is True


class TestGroupCoordinator:
    """Test group coordination functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = {
            "heroic_mode": {"enabled": True, "auto_follow_leader": True},
            "group_behavior": {"wait_timeout": 120}
        }
        
        # Mock heroic database
        self.mock_db = Mock()
        self.coordinator = GroupCoordinator(self.config, self.mock_db)
    
    def test_create_group_state(self):
        """Test creating group state."""
        state = self.coordinator._create_group_state(GroupStatus.FORMING)
        
        assert state is not None
        assert state.status == GroupStatus.FORMING
        assert state.group_id.startswith("group_")
        assert state.heroic_id == ""
        assert state.difficulty == HeroicDifficulty.NORMAL
    
    def test_update_group_state_forming(self):
        """Test updating group state to forming."""
        state = self.coordinator.update_group_state(
            chat_text="Player invites you to join their group"
        )
        
        assert state is not None
        assert state.status == GroupStatus.FORMING
    
    def test_update_group_state_ready(self):
        """Test updating group state to ready."""
        # First create a group
        self.coordinator.update_group_state(
            chat_text="Player invites you to join their group"
        )
        
        # Then make it ready
        state = self.coordinator.update_group_state(
            chat_text="Everyone ready for the boss fight?"
        )
        
        assert state is not None
        assert state.status == GroupStatus.READY
    
    def test_update_group_state_solo(self):
        """Test updating group state to solo."""
        # First create a group
        self.coordinator.update_group_state(
            chat_text="Player invites you to join their group"
        )
        
        # Then disband it
        state = self.coordinator.update_group_state(
            chat_text="Group disbanded"
        )
        
        assert state is None
        assert self.coordinator.current_group is None
    
    def test_get_group_info_no_group(self):
        """Test getting group info when no group exists."""
        info = self.coordinator.get_group_info()
        
        assert info["status"] == "no_group"
    
    def test_get_group_info_with_group(self):
        """Test getting group info when group exists."""
        # Create a group
        self.coordinator.update_group_state(
            chat_text="Player invites you to join their group"
        )
        
        info = self.coordinator.get_group_info()
        
        assert info["status"] == "forming"
        assert "group_id" in info
        assert "formation_time" in info
    
    def test_wait_for_group_timeout(self):
        """Test waiting for group with timeout."""
        # Mock the group to never be ready
        self.coordinator.current_group = self.coordinator._create_group_state(GroupStatus.FORMING)
        
        success = self.coordinator.wait_for_group(timeout=1)
        assert success is False
    
    def test_handle_group_actions(self):
        """Test handling group actions."""
        # Test forming
        self.coordinator._handle_group_actions(GroupStatus.FORMING)
        
        # Test ready
        self.coordinator._handle_group_actions(GroupStatus.READY)
        
        # Test in progress
        self.coordinator._handle_group_actions(GroupStatus.IN_PROGRESS)
        
        # Test completed
        self.coordinator._handle_group_actions(GroupStatus.COMPLETED)


class TestHeroicSupport:
    """Test main heroic support system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "heroic_config.json"
        
        # Create test config
        self.test_config = {
            "heroic_mode": {
                "enabled": False,
                "auto_follow_leader": True,
                "wait_for_group": True,
                "group_timeout": 300
            },
            "group_behavior": {
                "follow_distance": 10,
                "follow_timeout": 60,
                "wait_timeout": 120
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(self.test_config, f)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_init(self):
        """Test heroic support initialization."""
        support = HeroicSupport(str(self.config_path))
        
        assert support.is_enabled is False
        assert support.config == self.test_config
        assert support.heroic_db is not None
        assert support.group_coordinator is not None
    
    def test_enable_heroic_mode(self):
        """Test enabling heroic mode."""
        support = HeroicSupport(str(self.config_path))
        success = support.enable_heroic_mode()
        
        assert success is True
        assert support.is_enabled is True
        assert support.config["heroic_mode"]["enabled"] is True
    
    def test_disable_heroic_mode(self):
        """Test disabling heroic mode."""
        support = HeroicSupport(str(self.config_path))
        support.enable_heroic_mode()
        success = support.disable_heroic_mode()
        
        assert success is True
        assert support.is_enabled is False
        assert support.config["heroic_mode"]["enabled"] is False
    
    def test_update_state_disabled(self):
        """Test updating state when disabled."""
        support = HeroicSupport(str(self.config_path))
        state = support.update_state()
        
        assert state["enabled"] is False
    
    def test_update_state_enabled(self):
        """Test updating state when enabled."""
        support = HeroicSupport(str(self.config_path))
        support.enable_heroic_mode()
        state = support.update_state()
        
        assert state["enabled"] is True
        assert "group_info" in state
        assert "available_heroics" in state
        assert "following_active" in state
    
    def test_get_heroic_info(self):
        """Test getting heroic information."""
        support = HeroicSupport(str(self.config_path))
        
        # Test with non-existent heroic
        info = support.get_heroic_info("non_existent")
        assert "error" in info
        
        # Test with existing heroic (would need mock data)
        # This test would need actual heroic data to be more comprehensive
    
    def test_get_available_heroics(self):
        """Test getting available heroics."""
        support = HeroicSupport(str(self.config_path))
        heroics = support.get_available_heroics(80)
        
        # This would return actual heroics if data exists
        assert isinstance(heroics, list)
    
    def test_wait_for_group_ready(self):
        """Test waiting for group ready."""
        support = HeroicSupport(str(self.config_path))
        success = support.wait_for_group_ready(timeout=1)
        
        # Should timeout since no group is forming
        assert success is False


class TestDataClasses:
    """Test data class functionality."""
    
    def test_group_member(self):
        """Test GroupMember dataclass."""
        member = GroupMember(
            name="TestPlayer",
            level=80,
            profession="Marksman",
            role="dps",
            is_leader=True,
            is_ready=True
        )
        
        assert member.name == "TestPlayer"
        assert member.level == 80
        assert member.profession == "Marksman"
        assert member.role == "dps"
        assert member.is_leader is True
        assert member.is_ready is True
    
    def test_heroic_instance(self):
        """Test HeroicInstance dataclass."""
        instance = HeroicInstance(
            heroic_id="test_heroic",
            name="Test Heroic",
            planet="test_planet",
            location="test_location",
            coordinates=[100, 200],
            difficulty=HeroicDifficulty.NORMAL,
            level_requirement=80,
            group_size="4-8 players",
            prerequisites={},
            bosses=[],
            rewards={}
        )
        
        assert instance.heroic_id == "test_heroic"
        assert instance.name == "Test Heroic"
        assert instance.planet == "test_planet"
        assert instance.difficulty == HeroicDifficulty.NORMAL
        assert instance.level_requirement == 80
    
    def test_group_state(self):
        """Test GroupState dataclass."""
        state = GroupState(
            group_id="test_group",
            heroic_id="test_heroic",
            difficulty=HeroicDifficulty.NORMAL,
            members=[],
            leader="TestLeader",
            status=GroupStatus.FORMING,
            formation_time=datetime.now(),
            current_location="test_location",
            quest_step="forming",
            last_activity=datetime.now()
        )
        
        assert state.group_id == "test_group"
        assert state.heroic_id == "test_heroic"
        assert state.difficulty == HeroicDifficulty.NORMAL
        assert state.leader == "TestLeader"
        assert state.status == GroupStatus.FORMING
    
    def test_follow_target(self):
        """Test FollowTarget dataclass."""
        target = FollowTarget(
            target_name="TestTarget",
            target_type="leader",
            distance=5.0,
            last_position=[100, 200],
            last_seen=datetime.now(),
            is_active=True
        )
        
        assert target.target_name == "TestTarget"
        assert target.target_type == "leader"
        assert target.distance == 5.0
        assert target.last_position == [100, 200]
        assert target.is_active is True


def test_integration():
    """Test full system integration."""
    # This test would validate the complete workflow
    # from group detection to heroic completion
    
    # Create temporary config
    temp_dir = tempfile.mkdtemp()
    config_path = Path(temp_dir) / "test_config.json"
    
    test_config = {
        "heroic_mode": {"enabled": True, "auto_follow_leader": True},
        "group_behavior": {"follow_distance": 10, "wait_timeout": 120}
    }
    
    with open(config_path, 'w') as f:
        json.dump(test_config, f)
    
    try:
        # Initialize system
        support = HeroicSupport(str(config_path))
        
        # Enable heroic mode
        support.enable_heroic_mode()
        assert support.is_enabled is True
        
        # Simulate group formation
        state = support.update_state(chat_text="Player invites you to join their group")
        assert state["enabled"] is True
        
        # Simulate group ready
        state = support.update_state(chat_text="Everyone ready for the boss fight?")
        assert state["enabled"] is True
        
        # Disable heroic mode
        support.disable_heroic_mode()
        assert support.is_enabled is False
        
    finally:
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 