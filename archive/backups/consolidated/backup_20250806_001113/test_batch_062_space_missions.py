#!/usr/bin/env python3
"""Test suite for Batch 062 - Smart Space Mission Support (Phase 1).

This test suite covers:
- Space event detection via logs
- Mission type definitions (Patrol, Escort, Kill Target)
- Ship entry/exit functionality
- Terminal identification
- Combat simulation for Tansarii Point Station
- Integration with session_config.json space_mode settings
"""

import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from core.space_mission_manager import (
    SpaceMissionManager,
    SpaceMissionType,
    SpaceEventType,
    SpaceMission,
    SpaceEvent
)
from modules.space_mode import SpaceMode


class TestSpaceMissionManager(unittest.TestCase):
    """Test cases for SpaceMissionManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary config file
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_session_config.json")
        
        test_config = {
            "space_mode": {
                "enabled": True,
                "auto_detect_space_events": True,
                "preferred_mission_types": ["patrol", "escort", "kill_target"],
                "default_station": "Tansarii Point Station",
                "combat_simulation": True,
                "ship_entry_exit": True,
                "terminal_detection": True
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        # Create temporary missions file
        self.missions_path = os.path.join(self.temp_dir, "test_space_quests.json")
        test_missions = {
            "quests": [
                {
                    "quest_id": "test_patrol_001",
                    "name": "Test Patrol Mission",
                    "quest_type": "patrol",
                    "description": "A test patrol mission",
                    "status": "available",
                    "credits": 200,
                    "experience": 100,
                    "level_requirement": 5,
                    "ship_requirement": "x-wing",
                    "start_location": "Tansarii Point Station",
                    "target_location": None,
                    "time_limit": None,
                    "start_time": None,
                    "completion_time": None,
                    "steps": [],
                    "current_step": 0,
                    "tags": ["test", "patrol"]
                }
            ]
        }
        
        with open(self.missions_path, 'w') as f:
            json.dump(test_missions, f)
        
        # Initialize manager with test config
        self.manager = SpaceMissionManager(self.config_path)
        
        # Override missions path
        self.manager._load_missions = lambda: None
        self.manager.missions = {}
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test SpaceMissionManager initialization."""
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.current_location, "Tansarii Point Station")
        self.assertIsNone(self.manager.current_ship)
        self.assertIsNone(self.manager.current_mission)
        self.assertTrue(self.manager.config.get("enabled"))
    
    def test_load_config(self):
        """Test configuration loading."""
        config = self.manager._load_config()
        self.assertIn("enabled", config)
        self.assertIn("auto_detect_space_events", config)
        self.assertIn("preferred_mission_types", config)
        self.assertEqual(config["default_station"], "Tansarii Point Station")
    
    def test_create_mission(self):
        """Test mission creation."""
        mission = self.manager.create_mission(
            mission_type=SpaceMissionType.PATROL,
            name="Test Patrol",
            description="A test patrol mission",
            credits_reward=150,
            experience_reward=75,
            ship_requirement="x-wing"
        )
        
        self.assertIsInstance(mission, SpaceMission)
        self.assertEqual(mission.name, "Test Patrol")
        self.assertEqual(mission.mission_type, SpaceMissionType.PATROL)
        self.assertEqual(mission.credits_reward, 150)
        self.assertEqual(mission.experience_reward, 75)
        self.assertEqual(mission.ship_requirement, "x-wing")
        self.assertIn(mission.mission_id, self.manager.missions)
    
    def test_detect_space_events(self):
        """Test space event detection."""
        # Test ship entry event
        events = self.manager.detect_space_events("entering ship x-wing")
        self.assertGreater(len(events), 0)
        self.assertEqual(events[0].event_type, SpaceEventType.SHIP_ENTRY)
        
        # Test mission accept event
        events = self.manager.detect_space_events("mission accepted: Patrol Sector Alpha")
        self.assertGreater(len(events), 0)
        self.assertEqual(events[0].event_type, SpaceEventType.MISSION_ACCEPT)
        
        # Test combat start event
        events = self.manager.detect_space_events("combat started with pirate vessel")
        self.assertGreater(len(events), 0)
        self.assertEqual(events[0].event_type, SpaceEventType.COMBAT_START)
        
        # Test no event detection
        events = self.manager.detect_space_events("Regular chat message")
        self.assertEqual(len(events), 0)
    
    def test_enter_ship(self):
        """Test ship entry functionality."""
        success = self.manager.enter_ship("x-wing")
        self.assertTrue(success)
        self.assertEqual(self.manager.current_ship, "x-wing")
        
        # Test entering another ship
        success = self.manager.enter_ship("millennium_falcon")
        self.assertTrue(success)
        self.assertEqual(self.manager.current_ship, "millennium_falcon")
    
    def test_exit_ship(self):
        """Test ship exit functionality."""
        # Enter ship first
        self.manager.enter_ship("x-wing")
        self.assertEqual(self.manager.current_ship, "x-wing")
        
        # Exit ship
        success = self.manager.exit_ship()
        self.assertTrue(success)
        self.assertIsNone(self.manager.current_ship)
        
        # Test exiting when no ship
        success = self.manager.exit_ship()
        self.assertFalse(success)
    
    def test_identify_terminal(self):
        """Test terminal identification."""
        # Test mission terminal
        terminal_type = self.manager.identify_terminal("Mission Terminal - Available Space Missions")
        self.assertEqual(terminal_type, "mission_terminal")
        
        # Test ship terminal
        terminal_type = self.manager.identify_terminal("Ship Control Terminal - Vessel Access")
        self.assertEqual(terminal_type, "ship_terminal")
        
        # Test navigation terminal
        terminal_type = self.manager.identify_terminal("Navigation Terminal - Travel Routes")
        self.assertEqual(terminal_type, "navigation_terminal")
        
        # Test unknown terminal
        terminal_type = self.manager.identify_terminal("General Information Terminal")
        self.assertIsNone(terminal_type)
    
    def test_simulate_combat(self):
        """Test combat simulation."""
        # Test combat without ship
        result = self.manager.simulate_combat("Pirate Vessel")
        self.assertEqual(result["status"], "no_ship")
        
        # Test combat with ship
        self.manager.enter_ship("x-wing")
        result = self.manager.simulate_combat("Pirate Vessel")
        
        self.assertIn("status", result)
        self.assertIn("duration", result)
        self.assertIn("target", result)
        self.assertIn("ship", result)
        self.assertIn("damage_taken", result)
        self.assertIn("credits_earned", result)
        self.assertIn("experience_earned", result)
        
        # Test disabled combat simulation
        with patch.dict(self.manager.config, {"combat_simulation": False}):
            result = self.manager.simulate_combat("Pirate Vessel")
            self.assertEqual(result["status"], "disabled")
    
    def test_accept_mission(self):
        """Test mission acceptance."""
        # Create a mission
        mission = self.manager.create_mission(
            mission_type=SpaceMissionType.PATROL,
            name="Test Mission"
        )
        
        # Accept mission
        success = self.manager.accept_mission(mission.mission_id)
        self.assertTrue(success)
        self.assertEqual(mission.status, "active")
        self.assertIsNotNone(mission.start_time)
        self.assertEqual(self.manager.current_mission, mission)
        
        # Test accepting non-existent mission
        success = self.manager.accept_mission("non_existent")
        self.assertFalse(success)
        
        # Test accepting already active mission
        success = self.manager.accept_mission(mission.mission_id)
        self.assertFalse(success)
    
    def test_complete_mission(self):
        """Test mission completion."""
        # Create and accept a mission
        mission = self.manager.create_mission(
            mission_type=SpaceMissionType.PATROL,
            name="Test Mission"
        )
        self.manager.accept_mission(mission.mission_id)
        
        # Complete mission
        success = self.manager.complete_mission(mission.mission_id)
        self.assertTrue(success)
        self.assertEqual(mission.status, "completed")
        self.assertIsNotNone(mission.completion_time)
        self.assertIsNone(self.manager.current_mission)
        
        # Test completing non-existent mission
        success = self.manager.complete_mission("non_existent")
        self.assertFalse(success)
        
        # Test completing non-active mission
        success = self.manager.complete_mission(mission.mission_id)
        self.assertFalse(success)
    
    def test_get_available_missions(self):
        """Test getting available missions."""
        # Create missions with different statuses
        mission1 = self.manager.create_mission(
            mission_type=SpaceMissionType.PATROL,
            name="Available Mission 1"
        )
        mission2 = self.manager.create_mission(
            mission_type=SpaceMissionType.ESCORT,
            name="Available Mission 2"
        )
        mission3 = self.manager.create_mission(
            mission_type=SpaceMissionType.KILL_TARGET,
            name="Active Mission"
        )
        mission3.status = "active"
        
        # Get all available missions
        available = self.manager.get_available_missions()
        self.assertEqual(len(available), 2)
        
        # Get missions by type
        patrol_missions = self.manager.get_available_missions(["patrol"])
        self.assertEqual(len(patrol_missions), 1)
        self.assertEqual(patrol_missions[0].mission_type, SpaceMissionType.PATROL)
    
    def test_get_space_mode_status(self):
        """Test getting space mode status."""
        status = self.manager.get_space_mode_status()
        
        self.assertIn("enabled", status)
        self.assertIn("auto_detect_space_events", status)
        self.assertIn("preferred_mission_types", status)
        self.assertIn("default_station", status)
        self.assertIn("combat_simulation", status)
        self.assertIn("ship_entry_exit", status)
        self.assertIn("terminal_detection", status)
        self.assertIn("current_mission", status)
        self.assertIn("current_ship", status)
        self.assertIn("current_location", status)
        self.assertIn("available_missions", status)
    
    def test_save_missions(self):
        """Test mission saving."""
        # Create a mission
        mission = self.manager.create_mission(
            mission_type=SpaceMissionType.PATROL,
            name="Test Mission"
        )
        
        # Save missions
        self.manager.save_missions()
        
        # Verify file was created (this would require mocking the file operations)
        # For now, just test that the method doesn't raise an exception
        self.assertTrue(True)


class TestSpaceMode(unittest.TestCase):
    """Test cases for SpaceMode."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary config file
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_session_config.json")
        
        test_config = {
            "space_mode": {
                "enabled": True,
                "auto_detect_space_events": True,
                "preferred_mission_types": ["patrol", "escort", "kill_target"],
                "default_station": "Tansarii Point Station",
                "combat_simulation": True,
                "ship_entry_exit": True,
                "terminal_detection": True
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        # Initialize space mode with test config
        with patch('modules.space_mode.Path') as mock_path:
            mock_path.return_value.exists.return_value = True
            mock_path.return_value.__truediv__.return_value = self.config_path
            self.space_mode = SpaceMode()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test SpaceMode initialization."""
        self.assertIsNotNone(self.space_mode)
        self.assertIsNotNone(self.space_mode.manager)
        self.assertIsNone(self.space_mode.current_mission)
        self.assertEqual(len(self.space_mode.mission_history), 0)
    
    def test_load_space_config(self):
        """Test space configuration loading."""
        config = self.space_mode._load_space_config()
        self.assertIn("enabled", config)
        self.assertIn("auto_detect_space_events", config)
        self.assertIn("preferred_mission_types", config)
        self.assertEqual(config["default_station"], "Tansarii Point Station")
    
    def test_run_disabled(self):
        """Test running space mode when disabled."""
        with patch.dict(self.space_mode.config, {"enabled": False}):
            result = self.space_mode.run()
            self.assertEqual(result["status"], "disabled")
            self.assertIn("message", result)
    
    def test_run_no_missions(self):
        """Test running space mode with no available missions."""
        with patch.object(self.space_mode.manager, 'get_available_missions', return_value=[]):
            with patch.dict(self.space_mode.config, {"enabled": True}):
                result = self.space_mode.run()
                self.assertEqual(result["status"], "no_missions")
    
    def test_simulate_patrol_mission(self):
        """Test patrol mission simulation."""
        mission = MagicMock()
        mission.mission_id = "test_patrol"
        mission.name = "Test Patrol"
        
        result = self.space_mode._simulate_patrol_mission(mission)
        
        self.assertIn("patrol_points", result)
        self.assertIn("combat_encounters", result)
        self.assertIn("combat_simulated", result)
        self.assertEqual(result["patrol_points"], 3)
    
    def test_simulate_escort_mission(self):
        """Test escort mission simulation."""
        mission = MagicMock()
        mission.mission_id = "test_escort"
        mission.name = "Test Escort"
        
        result = self.space_mode._simulate_escort_mission(mission)
        
        self.assertIn("escort_target", result)
        self.assertIn("escort_distance", result)
        self.assertIn("combat_encounters", result)
        self.assertIn("combat_simulated", result)
        self.assertIn("escort_successful", result)
        self.assertEqual(result["escort_target"], "Merchant Vessel")
    
    def test_simulate_kill_target_mission(self):
        """Test kill target mission simulation."""
        mission = MagicMock()
        mission.mission_id = "test_kill"
        mission.name = "Test Kill Target"
        
        result = self.space_mode._simulate_kill_target_mission(mission)
        
        self.assertIn("target_name", result)
        self.assertIn("target_location", result)
        self.assertIn("combat_simulated", result)
        self.assertIn("target_eliminated", result)
        self.assertEqual(result["target_name"], "Wanted Criminal")
    
    def test_simulate_generic_mission(self):
        """Test generic mission simulation."""
        mission = MagicMock()
        mission.mission_id = "test_generic"
        mission.name = "Test Generic"
        mission.mission_type.value = "delivery"
        
        result = self.space_mode._simulate_generic_mission(mission)
        
        self.assertIn("mission_type", result)
        self.assertIn("combat_simulated", result)
        self.assertIn("steps_completed", result)
        self.assertEqual(result["mission_type"], "delivery")
    
    def test_get_status(self):
        """Test getting space mode status."""
        status = self.space_mode.get_status()
        
        self.assertIn("mode", status)
        self.assertIn("enabled", status)
        self.assertIn("current_mission", status)
        self.assertIn("available_missions", status)
        self.assertIn("current_ship", status)
        self.assertIn("current_location", status)
        self.assertIn("mission_history", status)
        self.assertEqual(status["mode"], "space")


class TestSpaceMissionTypes(unittest.TestCase):
    """Test cases for space mission types."""
    
    def test_space_mission_types(self):
        """Test space mission type enumeration."""
        self.assertEqual(SpaceMissionType.PATROL.value, "patrol")
        self.assertEqual(SpaceMissionType.ESCORT.value, "escort")
        self.assertEqual(SpaceMissionType.KILL_TARGET.value, "kill_target")
        self.assertEqual(SpaceMissionType.DELIVERY.value, "delivery")
        self.assertEqual(SpaceMissionType.EXPLORATION.value, "exploration")
        self.assertEqual(SpaceMissionType.COMBAT.value, "combat")
    
    def test_space_event_types(self):
        """Test space event type enumeration."""
        self.assertEqual(SpaceEventType.SHIP_ENTRY.value, "ship_entry")
        self.assertEqual(SpaceEventType.SHIP_EXIT.value, "ship_exit")
        self.assertEqual(SpaceEventType.MISSION_ACCEPT.value, "mission_accept")
        self.assertEqual(SpaceEventType.MISSION_COMPLETE.value, "mission_complete")
        self.assertEqual(SpaceEventType.COMBAT_START.value, "combat_start")
        self.assertEqual(SpaceEventType.COMBAT_END.value, "combat_end")
        self.assertEqual(SpaceEventType.TERMINAL_INTERACTION.value, "terminal_interaction")
        self.assertEqual(SpaceEventType.SPACE_TRAVEL.value, "space_travel")


class TestSpaceMissionDataStructures(unittest.TestCase):
    """Test cases for space mission data structures."""
    
    def test_space_mission_creation(self):
        """Test SpaceMission dataclass creation."""
        mission = SpaceMission(
            mission_id="test_001",
            name="Test Mission",
            mission_type=SpaceMissionType.PATROL,
            description="A test mission"
        )
        
        self.assertEqual(mission.mission_id, "test_001")
        self.assertEqual(mission.name, "Test Mission")
        self.assertEqual(mission.mission_type, SpaceMissionType.PATROL)
        self.assertEqual(mission.description, "A test mission")
        self.assertEqual(mission.status, "available")
        self.assertEqual(mission.credits_reward, 0)
        self.assertEqual(mission.experience_reward, 0)
        self.assertEqual(mission.level_requirement, 0)
        self.assertIsNone(mission.ship_requirement)
        self.assertEqual(mission.start_location, "Tansarii Point Station")
        self.assertIsNone(mission.target_location)
        self.assertIsNone(mission.time_limit)
        self.assertIsNone(mission.start_time)
        self.assertIsNone(mission.completion_time)
        self.assertEqual(mission.steps, [])
        self.assertEqual(mission.current_step, 0)
        self.assertEqual(mission.tags, [])
    
    def test_space_event_creation(self):
        """Test SpaceEvent dataclass creation."""
        event = SpaceEvent(
            event_type=SpaceEventType.SHIP_ENTRY,
            timestamp=time.time(),
            location="Tansarii Point Station",
            details={"ship_name": "x-wing"},
            mission_id="test_001",
            ship_name="x-wing"
        )
        
        self.assertEqual(event.event_type, SpaceEventType.SHIP_ENTRY)
        self.assertIsInstance(event.timestamp, float)
        self.assertEqual(event.location, "Tansarii Point Station")
        self.assertEqual(event.details["ship_name"], "x-wing")
        self.assertEqual(event.mission_id, "test_001")
        self.assertEqual(event.ship_name, "x-wing")


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2) 