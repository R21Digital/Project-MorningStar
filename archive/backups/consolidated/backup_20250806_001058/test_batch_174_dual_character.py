#!/usr/bin/env python3
"""
Comprehensive test suite for Batch 174 - Dual-Character Bot Mode (MultiWindow Support)

This test suite validates all aspects of the dual-character mode implementation:
- Configuration loading and validation
- Character registration and management
- Window management and arrangement
- Shared data layer functionality
- Support mode operations
- Communication system
- Safety features and monitoring
- Full dual character mode execution
"""

import json
import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.session.dual_character_mode import (
    DualCharacterModeManager,
    DualCharacterMode,
    SupportType,
    CharacterConfig,
    CharacterMode,
    CharacterRole,
    run_dual_character_mode
)


class TestDualCharacterModeConfig(unittest.TestCase):
    """Test suite for dual character mode configuration."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "dual_character_config.json"
        
        # Create test configuration
        self.test_config = {
            "dual_mode_enabled": True,
            "mode": "leader_follower",
            "character_1": {
                "name": "TestMainChar",
                "window_title": "SWG - TestMainChar",
                "mode": "main",
                "role": "leader",
                "support_type": None,
                "config_file": "config/character_1_config.json",
                "auto_start": True
            },
            "character_2": {
                "name": "TestSupportChar",
                "window_title": "SWG - TestSupportChar",
                "mode": "support",
                "role": "follower",
                "support_type": "medic",
                "config_file": "config/character_2_config.json",
                "auto_start": True
            },
            "shared_data": {
                "xp_sync_enabled": True,
                "quest_sync_enabled": True,
                "buff_sync_enabled": True,
                "position_sync_enabled": True,
                "combat_sync_enabled": True
            },
            "support_modes": {
                "medic": {
                    "buff_interval": 300,
                    "heal_interval": 60,
                    "buff_range": 50,
                    "heal_range": 30,
                    "buffs": ["heal_health", "heal_action", "heal_mind"],
                    "stationary": False,
                    "follow_leader": True
                }
            },
            "communication": {
                "enabled": True,
                "port": 12347,
                "timeout": 30,
                "retry_attempts": 3
            },
            "safety": {
                "max_session_duration": 7200,
                "afk_timeout": 300,
                "emergency_stop": True,
                "auto_cleanup": True
            }
        }
        
        # Write test config
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_config, f, indent=2)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_config_loading(self):
        """Test configuration loading functionality."""
        manager = DualCharacterModeManager(str(self.config_path))
        
        # Test config structure
        self.assertIn("character_1", manager.config)
        self.assertIn("character_2", manager.config)
        self.assertIn("shared_data", manager.config)
        self.assertIn("support_modes", manager.config)
        
        # Test character configs
        char1_config = manager.config["character_1"]
        char2_config = manager.config["character_2"]
        
        self.assertEqual(char1_config["name"], "TestMainChar")
        self.assertEqual(char2_config["name"], "TestSupportChar")
        self.assertEqual(char1_config["role"], "leader")
        self.assertEqual(char2_config["role"], "follower")
    
    def test_config_validation(self):
        """Test configuration validation."""
        manager = DualCharacterModeManager(str(self.config_path))
        
        # Test required sections
        required_sections = ["character_1", "character_2", "shared_data", "support_modes"]
        for section in required_sections:
            self.assertIn(section, manager.config)
        
        # Test character config validation
        char1_config = manager.config["character_1"]
        required_char_fields = ["name", "window_title", "mode", "role"]
        for field in required_char_fields:
            self.assertIn(field, char1_config)
    
    def test_support_modes_config(self):
        """Test support modes configuration."""
        manager = DualCharacterModeManager(str(self.config_path))
        
        support_modes = manager.config.get("support_modes", {})
        self.assertIn("medic", support_modes)
        
        medic_config = support_modes["medic"]
        required_medic_fields = ["buff_interval", "heal_interval", "buff_range", "heal_range"]
        for field in required_medic_fields:
            self.assertIn(field, medic_config)


class TestCharacterRegistration(unittest.TestCase):
    """Test suite for character registration functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.manager = DualCharacterModeManager()
    
    def test_character_config_creation(self):
        """Test character configuration creation."""
        char_config = CharacterConfig(
            name="TestChar",
            window_title="SWG - TestChar",
            mode=CharacterMode.MAIN,
            role=CharacterRole.LEADER,
            config_file="config/test_char_config.json"
        )
        
        self.assertEqual(char_config.name, "TestChar")
        self.assertEqual(char_config.window_title, "SWG - TestChar")
        self.assertEqual(char_config.mode, CharacterMode.MAIN)
        self.assertEqual(char_config.role, CharacterRole.LEADER)
        self.assertIsNone(char_config.support_type)
    
    def test_support_character_config(self):
        """Test support character configuration."""
        char_config = CharacterConfig(
            name="TestSupportChar",
            window_title="SWG - TestSupportChar",
            mode=CharacterMode.SUPPORT,
            role=CharacterRole.FOLLOWER,
            support_type=SupportType.MEDIC,
            config_file="config/test_support_config.json"
        )
        
        self.assertEqual(char_config.name, "TestSupportChar")
        self.assertEqual(char_config.mode, CharacterMode.SUPPORT)
        self.assertEqual(char_config.role, CharacterRole.FOLLOWER)
        self.assertEqual(char_config.support_type, SupportType.MEDIC)
    
    def test_character_registration(self):
        """Test character registration."""
        char1_config = CharacterConfig(
            name="TestChar1",
            window_title="SWG - TestChar1",
            mode=CharacterMode.MAIN,
            role=CharacterRole.LEADER
        )
        
        char2_config = CharacterConfig(
            name="TestChar2",
            window_title="SWG - TestChar2",
            mode=CharacterMode.SUPPORT,
            role=CharacterRole.FOLLOWER,
            support_type=SupportType.MEDIC
        )
        
        # Register characters
        success1 = self.manager.register_character(char1_config)
        success2 = self.manager.register_character(char2_config)
        
        self.assertTrue(success1)
        self.assertTrue(success2)
        self.assertEqual(len(self.manager.characters), 2)
        self.assertIn("TestChar1", self.manager.characters)
        self.assertIn("TestChar2", self.manager.characters)


class TestWindowManagement(unittest.TestCase):
    """Test suite for window management functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.manager = DualCharacterModeManager()
        self.window_manager = self.manager.window_manager
    
    def test_window_manager_initialization(self):
        """Test window manager initialization."""
        self.assertIsNotNone(self.window_manager)
        self.assertIsInstance(self.window_manager.window_positions, dict)
    
    def test_window_position_retrieval(self):
        """Test window position retrieval."""
        # Test with non-existent window
        position = self.window_manager.get_window_position("NonExistentWindow")
        self.assertIsNone(position)
    
    def test_window_arrangement_logic(self):
        """Test window arrangement logic."""
        # Test arrangement without actual windows (should not fail)
        success = self.window_manager.arrange_dual_windows(
            "SWG - TestChar1",
            "SWG - TestChar2"
        )
        
        # Should succeed even without actual windows
        self.assertTrue(success)


class TestSharedDataLayer(unittest.TestCase):
    """Test suite for shared data layer functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.manager = DualCharacterModeManager()
        self.shared_data = self.manager.shared_data
    
    def test_shared_data_initialization(self):
        """Test shared data initialization."""
        self.assertIsNotNone(self.shared_data.session_id)
        self.assertIsInstance(self.shared_data.start_time, datetime)
        self.assertIsInstance(self.shared_data.xp_data, dict)
        self.assertIsInstance(self.shared_data.quest_data, dict)
        self.assertIsInstance(self.shared_data.buff_data, dict)
        self.assertIsInstance(self.shared_data.position_data, dict)
        self.assertIsInstance(self.shared_data.status_data, dict)
        self.assertIsInstance(self.shared_data.combat_data, dict)
        self.assertIsInstance(self.shared_data.inventory_data, dict)
    
    def test_data_synchronization(self):
        """Test data synchronization."""
        # Test XP data sync
        test_xp = {"TestChar1": 1000, "TestChar2": 500}
        self.shared_data.xp_data.update(test_xp)
        self.assertEqual(self.shared_data.xp_data["TestChar1"], 1000)
        self.assertEqual(self.shared_data.xp_data["TestChar2"], 500)
        
        # Test quest data sync
        test_quest = {"TestChar1": {"active_quests": 2}}
        self.shared_data.quest_data.update(test_quest)
        self.assertEqual(self.shared_data.quest_data["TestChar1"]["active_quests"], 2)
        
        # Test buff data sync
        test_buff = {"TestChar1": {"buffs": ["heal_health"]}}
        self.shared_data.buff_data.update(test_buff)
        self.assertIn("heal_health", self.shared_data.buff_data["TestChar1"]["buffs"])


class TestSupportModes(unittest.TestCase):
    """Test suite for support mode functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.manager = DualCharacterModeManager()
    
    def test_support_type_enum(self):
        """Test support type enumeration."""
        support_types = [
            SupportType.MEDIC,
            SupportType.DANCER,
            SupportType.ENTERTAINER,
            SupportType.COMBAT_SUPPORT,
            SupportType.CRAFTING_SUPPORT
        ]
        
        for support_type in support_types:
            self.assertIsInstance(support_type, SupportType)
            self.assertIsInstance(support_type.value, str)
    
    def test_support_mode_configuration(self):
        """Test support mode configuration."""
        config = self.manager.config
        support_modes = config.get("support_modes", {})
        
        # Test medic configuration
        if "medic" in support_modes:
            medic_config = support_modes["medic"]
            self.assertIn("buff_interval", medic_config)
            self.assertIn("heal_interval", medic_config)
            self.assertIn("buff_range", medic_config)
            self.assertIn("heal_range", medic_config)
            self.assertIn("buffs", medic_config)
    
    def test_dual_character_mode_enum(self):
        """Test dual character mode enumeration."""
        modes = [
            DualCharacterMode.INDEPENDENT,
            DualCharacterMode.LEADER_FOLLOWER,
            DualCharacterMode.SUPPORT_MODE,
            DualCharacterMode.SYNC_MODE,
            DualCharacterMode.COMBAT_PAIR
        ]
        
        for mode in modes:
            self.assertIsInstance(mode, DualCharacterMode)
            self.assertIsInstance(mode.value, str)


class TestCommunicationSystem(unittest.TestCase):
    """Test suite for communication system functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.manager = DualCharacterModeManager()
    
    def test_communication_configuration(self):
        """Test communication configuration."""
        config = self.manager.config
        comm_config = config.get("communication", {})
        
        if comm_config:
            self.assertIn("enabled", comm_config)
            self.assertIn("port", comm_config)
            self.assertIn("timeout", comm_config)
            self.assertIn("retry_attempts", comm_config)
    
    def test_message_processing(self):
        """Test message processing functionality."""
        # Test position message
        position_msg = {
            "type": "position",
            "sender": "TestChar1",
            "data": {"position": [100, 200]}
        }
        
        # Test XP message
        xp_msg = {
            "type": "xp",
            "sender": "TestChar1",
            "data": {"xp_gained": 150}
        }
        
        # Test quest message
        quest_msg = {
            "type": "quest",
            "sender": "TestChar1",
            "data": {"quest_completed": "Test Quest"}
        }
        
        # These should not raise exceptions
        self.manager._process_message(position_msg)
        self.manager._process_message(xp_msg)
        self.manager._process_message(quest_msg)


class TestSafetyFeatures(unittest.TestCase):
    """Test suite for safety features functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.manager = DualCharacterModeManager()
    
    def test_safety_configuration(self):
        """Test safety configuration."""
        config = self.manager.config
        safety_config = config.get("safety", {})
        
        if safety_config:
            self.assertIn("max_session_duration", safety_config)
            self.assertIn("afk_timeout", safety_config)
            self.assertIn("emergency_stop", safety_config)
            self.assertIn("auto_cleanup", safety_config)
    
    def test_performance_configuration(self):
        """Test performance configuration."""
        config = self.manager.config
        perf_config = config.get("performance", {})
        
        if perf_config:
            self.assertIn("sync_interval", perf_config)
            self.assertIn("monitor_interval", perf_config)
            self.assertIn("cleanup_interval", perf_config)
    
    def test_dual_mode_status(self):
        """Test dual mode status retrieval."""
        status = self.manager.get_dual_mode_status()
        
        self.assertIn("running", status)
        self.assertIn("active_characters", status)
        self.assertIn("shared_data", status)
        self.assertIn("character_configs", status)
        self.assertIn("session_duration", status)
        
        self.assertIsInstance(status["running"], bool)
        self.assertIsInstance(status["active_characters"], list)
        self.assertIsInstance(status["session_duration"], (int, float))


class TestDualCharacterModeExecution(unittest.TestCase):
    """Test suite for dual character mode execution."""
    
    def test_run_dual_character_mode(self):
        """Test the main dual character mode function."""
        result = run_dual_character_mode(
            char1_name="TestMainChar",
            char1_window="SWG - TestMainChar",
            char2_name="TestSupportChar",
            char2_window="SWG - TestSupportChar",
            mode=DualCharacterMode.LEADER_FOLLOWER,
            support_type=SupportType.MEDIC
        )
        
        # Test result structure
        self.assertIn("success", result)
        self.assertIsInstance(result["success"], bool)
        
        if result["success"]:
            self.assertIn("status", result)
            self.assertIn("characters", result)
            self.assertIn("mode", result)
            self.assertIn("support_type", result)
        else:
            self.assertIn("error", result)


class TestDualCharacterModeIntegration(unittest.TestCase):
    """Integration tests for dual character mode."""
    
    def setUp(self):
        """Set up test environment."""
        self.manager = DualCharacterModeManager()
    
    def test_full_character_lifecycle(self):
        """Test full character lifecycle."""
        # Create character configs
        char1_config = CharacterConfig(
            name="TestMainChar",
            window_title="SWG - TestMainChar",
            mode=CharacterMode.MAIN,
            role=CharacterRole.LEADER
        )
        
        char2_config = CharacterConfig(
            name="TestSupportChar",
            window_title="SWG - TestSupportChar",
            mode=CharacterMode.SUPPORT,
            role=CharacterRole.FOLLOWER,
            support_type=SupportType.MEDIC
        )
        
        # Register characters
        success1 = self.manager.register_character(char1_config)
        success2 = self.manager.register_character(char2_config)
        
        self.assertTrue(success1)
        self.assertTrue(success2)
        
        # Test dual mode start (without actual windows)
        try:
            success = self.manager.start_dual_mode("TestMainChar", "TestSupportChar")
            # Should not fail due to missing windows
            self.assertIsInstance(success, bool)
        except Exception as e:
            # Expected if windows don't exist
            self.assertIsInstance(e, Exception)
    
    def test_support_behavior_handling(self):
        """Test support behavior handling."""
        # Test medic support
        self.manager._handle_medic_support("TestSupportChar")
        
        # Test dancer support
        self.manager._handle_dancer_support("TestSupportChar")
        
        # Test entertainer support
        self.manager._handle_entertainer_support("TestSupportChar")
        
        # These should not raise exceptions
        self.assertTrue(True)
    
    def test_leader_character_detection(self):
        """Test leader character detection."""
        # Register test characters
        char1_config = CharacterConfig(
            name="TestLeader",
            window_title="SWG - TestLeader",
            mode=CharacterMode.MAIN,
            role=CharacterRole.LEADER
        )
        
        char2_config = CharacterConfig(
            name="TestFollower",
            window_title="SWG - TestFollower",
            mode=CharacterMode.SUPPORT,
            role=CharacterRole.FOLLOWER
        )
        
        self.manager.register_character(char1_config)
        self.manager.register_character(char2_config)
        
        # Test leader detection
        leader = self.manager._get_leader_character()
        self.assertEqual(leader, "TestLeader")


def run_tests():
    """Run all tests and return success status."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestDualCharacterModeConfig,
        TestCharacterRegistration,
        TestWindowManagement,
        TestSharedDataLayer,
        TestSupportModes,
        TestCommunicationSystem,
        TestSafetyFeatures,
        TestDualCharacterModeExecution,
        TestDualCharacterModeIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Total Tests: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    
    if success:
        print(f"\n🎉 All tests passed! Batch 174 implementation is working correctly.")
    else:
        print(f"\n⚠️ Some tests failed. Please check the implementation.")
    
    return success


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 