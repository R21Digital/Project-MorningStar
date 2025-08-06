#!/usr/bin/env python3
"""
Test suite for Batch 179 - Dual-Character Support for Same Account

This test suite covers:
- Configuration loading and validation
- Session manager functionality
- Dual mode support features
- Discord integration
- Session monitoring
- Logging functionality
- Full integration scenarios
"""

import os
import sys
import time
import json
import unittest
import tempfile
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from src.session_manager import (
        DualCharacterSessionManager,
        DualModeConfig,
        CharacterSession,
        SharedSessionData,
        run_dual_character_mode,
        get_dual_session_status,
        stop_dual_session
    )
    from src.ms11.modes.dual_mode_support import (
        DualModeSupport,
        DualModeConfig as DualModeSupportConfig,
        DualModeType,
        run as run_dual_mode,
        get_dual_mode_status,
        stop_dual_mode
    )
    from utils.license_hooks import requires_license
    from profession_logic.utils.logger import logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


class TestDualModeConfig(unittest.TestCase):
    """Test dual mode configuration functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_session_config.json")
        
        # Create test configuration
        self.test_config = {
            "dual_mode": True,
            "primary_character": {
                "name": "TestPrimary",
                "mode": "quest",
                "role": "leader",
                "window_title": "SWG - TestPrimary"
            },
            "secondary_character": {
                "name": "TestSecondary",
                "mode": "medic",
                "role": "follower",
                "window_title": "SWG - TestSecondary"
            },
            "shared_discord_channel": {
                "enabled": True,
                "channel_id": "test_channel_123",
                "tag_format": "[{character}] {message}"
            },
            "session_monitor": {
                "enabled": True,
                "check_interval": 30,
                "drop_threshold": 60,
                "auto_reconnect": True
            },
            "sync_settings": {
                "shared_session_id": True,
                "sync_positions": True,
                "sync_combat": True,
                "sync_quests": True
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(self.test_config, f, indent=2)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_config_loading(self):
        """Test configuration loading from file."""
        config = DualModeConfig(self.config_path)
        
        self.assertTrue(config.config["dual_mode"])
        self.assertEqual(config.config["primary_character"]["name"], "TestPrimary")
        self.assertEqual(config.config["secondary_character"]["name"], "TestSecondary")
        self.assertTrue(config.config["shared_discord_channel"]["enabled"])
    
    def test_config_saving(self):
        """Test configuration saving to file."""
        config = DualModeConfig(self.config_path)
        
        # Update configuration
        success = config.update_config(dual_mode=False)
        self.assertTrue(success)
        
        # Reload and verify
        new_config = DualModeConfig(self.config_path)
        self.assertFalse(new_config.config["dual_mode"])
    
    def test_default_config(self):
        """Test default configuration creation."""
        # Remove config file to trigger default creation
        os.remove(self.config_path)
        
        config = DualModeConfig(self.config_path)
        
        self.assertFalse(config.config["dual_mode"])
        self.assertIn("primary_character", config.config)
        self.assertIn("secondary_character", config.config)
        self.assertIn("shared_discord_channel", config.config)
        self.assertIn("session_monitor", config.config)


class TestCharacterSession(unittest.TestCase):
    """Test character session functionality."""
    
    def test_character_session_creation(self):
        """Test character session creation."""
        session = CharacterSession(
            character_name="TestChar",
            window_title="SWG - TestChar",
            mode="quest",
            role="leader",
            session_id="test_session_123"
        )
        
        self.assertEqual(session.character_name, "TestChar")
        self.assertEqual(session.window_title, "SWG - TestChar")
        self.assertEqual(session.mode, "quest")
        self.assertEqual(session.role, "leader")
        self.assertEqual(session.session_id, "test_session_123")
        self.assertFalse(session.is_active)
        self.assertIsNotNone(session.last_activity)
    
    def test_character_session_defaults(self):
        """Test character session default values."""
        session = CharacterSession(
            character_name="TestChar",
            window_title="SWG - TestChar",
            mode="quest",
            role="leader",
            session_id="test_session_123"
        )
        
        self.assertEqual(session.status, "idle")
        self.assertEqual(session.xp_gained, 0)
        self.assertEqual(session.credits_earned, 0)
        self.assertEqual(session.quests_completed, 0)
        self.assertEqual(session.combat_kills, 0)


class TestSharedSessionData(unittest.TestCase):
    """Test shared session data functionality."""
    
    def test_shared_session_data_creation(self):
        """Test shared session data creation."""
        shared_data = SharedSessionData(
            session_id="test_session_123",
            start_time=datetime.now()
        )
        
        self.assertEqual(shared_data.session_id, "test_session_123")
        self.assertEqual(shared_data.total_xp_gained, 0)
        self.assertEqual(shared_data.total_credits_earned, 0)
        self.assertEqual(shared_data.total_quests_completed, 0)
        self.assertEqual(shared_data.total_combat_kills, 0)
        self.assertIsNotNone(shared_data.shared_activities)
        self.assertIsNotNone(shared_data.discord_messages)


class TestDualCharacterSessionManager(unittest.TestCase):
    """Test dual character session manager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_session_config.json")
        
        # Create test configuration
        test_config = {
            "dual_mode": True,
            "primary_character": {
                "name": "TestPrimary",
                "mode": "quest",
                "role": "leader",
                "window_title": "SWG - TestPrimary"
            },
            "secondary_character": {
                "name": "TestSecondary",
                "mode": "medic",
                "role": "follower",
                "window_title": "SWG - TestSecondary"
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f, indent=2)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.session_manager.pygetwindow')
    @patch('src.session_manager.socket')
    def test_session_manager_initialization(self, mock_socket, mock_pygetwindow):
        """Test session manager initialization."""
        manager = DualCharacterSessionManager(self.config_path)
        
        self.assertIsNotNone(manager.config)
        self.assertEqual(len(manager.character_sessions), 0)
        self.assertIsNone(manager.shared_data)
        self.assertFalse(manager.is_running)
    
    @patch('src.session_manager.pygetwindow')
    @patch('src.session_manager.socket')
    def test_start_dual_session(self, mock_socket, mock_pygetwindow):
        """Test starting dual session."""
        manager = DualCharacterSessionManager(self.config_path)
        
        success = manager.start_dual_session(
            "TestPrimary", "SWG - TestPrimary",
            "TestSecondary", "SWG - TestSecondary"
        )
        
        self.assertTrue(success)
        self.assertTrue(manager.is_running)
        self.assertIsNotNone(manager.shared_data)
        self.assertEqual(len(manager.character_sessions), 2)
    
    @patch('src.session_manager.pygetwindow')
    @patch('src.session_manager.socket')
    def test_session_status(self, mock_socket, mock_pygetwindow):
        """Test getting session status."""
        manager = DualCharacterSessionManager(self.config_path)
        
        # Start session
        manager.start_dual_session(
            "TestPrimary", "SWG - TestPrimary",
            "TestSecondary", "SWG - TestSecondary"
        )
        
        status = manager.get_session_status()
        
        self.assertIn("session_id", status)
        self.assertIn("characters", status)
        self.assertEqual(len(status["characters"]), 2)
    
    @patch('src.session_manager.pygetwindow')
    @patch('src.session_manager.socket')
    def test_stop_dual_session(self, mock_socket, mock_pygetwindow):
        """Test stopping dual session."""
        manager = DualCharacterSessionManager(self.config_path)
        
        # Start session
        manager.start_dual_session(
            "TestPrimary", "SWG - TestPrimary",
            "TestSecondary", "SWG - TestSecondary"
        )
        
        # Stop session
        manager.stop_dual_session()
        
        self.assertFalse(manager.is_running)


class TestDualModeSupport(unittest.TestCase):
    """Test dual mode support functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.dual_support = DualModeSupport()
    
    def test_dual_mode_support_initialization(self):
        """Test dual mode support initialization."""
        self.assertIsNotNone(self.dual_support.config)
        self.assertIsNone(self.dual_support.primary_session)
        self.assertIsNone(self.dual_support.secondary_session)
        self.assertIsNone(self.dual_support.shared_session_id)
        self.assertFalse(self.dual_support.is_running)
    
    def test_create_character_session(self):
        """Test character session creation."""
        self.dual_support.shared_session_id = "test_session_123"
        
        session = self.dual_support._create_character_session(
            "TestChar", "SWG - TestChar", "leader"
        )
        
        self.assertEqual(session["character_name"], "TestChar")
        self.assertEqual(session["window_title"], "SWG - TestChar")
        self.assertEqual(session["role"], "leader")
        self.assertEqual(session["session_id"], "test_session_123")
        self.assertFalse(session["is_active"])
    
    def test_start_dual_mode_disabled(self):
        """Test starting dual mode when disabled."""
        self.dual_support.config.dual_mode_enabled = False
        
        success = self.dual_support.start_dual_mode("TestPrimary", "TestSecondary")
        
        self.assertFalse(success)
    
    @patch('src.ms11.modes.dual_mode_support.pygetwindow')
    @patch('src.ms11.modes.dual_mode_support.socket')
    def test_start_dual_mode_enabled(self, mock_socket, mock_pygetwindow):
        """Test starting dual mode when enabled."""
        self.dual_support.config.dual_mode_enabled = True
        
        success = self.dual_support.start_dual_mode("TestPrimary", "TestSecondary")
        
        self.assertTrue(success)
        self.assertTrue(self.dual_support.is_running)
        self.assertIsNotNone(self.dual_support.shared_session_id)
        self.assertIsNotNone(self.dual_support.primary_session)
        self.assertIsNotNone(self.dual_support.secondary_session)
    
    def test_get_session_status_not_started(self):
        """Test getting session status when not started."""
        status = self.dual_support.get_session_status()
        
        self.assertEqual(status["status"], "not_started")
    
    @patch('src.ms11.modes.dual_mode_support.pygetwindow')
    @patch('src.ms11.modes.dual_mode_support.socket')
    def test_get_session_status_started(self, mock_socket, mock_pygetwindow):
        """Test getting session status when started."""
        self.dual_support.config.dual_mode_enabled = True
        self.dual_support.start_dual_mode("TestPrimary", "TestSecondary")
        
        status = self.dual_support.get_session_status()
        
        self.assertIn("session_id", status)
        self.assertIn("dual_mode_type", status)
        self.assertIn("characters", status)
    
    def test_dual_mode_types(self):
        """Test all dual mode types."""
        mode_types = [
            DualModeType.QUEST_MEDIC,
            DualModeType.QUEST_DANCER,
            DualModeType.QUEST_ENTERTAINER,
            DualModeType.COMBAT_PAIR,
            DualModeType.CRAFTING_SUPPORT
        ]
        
        for mode_type in mode_types:
            self.dual_support.config.dual_mode_type = mode_type
            self.assertEqual(self.dual_support.config.dual_mode_type, mode_type)


class TestDiscordIntegration(unittest.TestCase):
    """Test Discord integration functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.dual_support = DualModeSupport()
        self.dual_support.config.shared_discord_enabled = True
        self.dual_support.config.discord_tag_format = "[{character}] {message}"
    
    def test_send_discord_alert(self):
        """Test sending Discord alert."""
        with patch('src.ms11.modes.dual_mode_support.logger') as mock_logger:
            self.dual_support._send_discord_alert("Test message")
            
            mock_logger.info.assert_called_with("[DISCORD] [System] Test message")
    
    def test_send_discord_alert_disabled(self):
        """Test sending Discord alert when disabled."""
        self.dual_support.config.shared_discord_enabled = False
        
        with patch('src.ms11.modes.dual_mode_support.logger') as mock_logger:
            self.dual_support._send_discord_alert("Test message")
            
            mock_logger.info.assert_not_called()
    
    def test_handle_discord_message(self):
        """Test handling Discord message."""
        with patch('src.ms11.modes.dual_mode_support.logger') as mock_logger:
            message_data = {"message": "Hello from character!"}
            self.dual_support._handle_discord_message("TestChar", message_data)
            
            mock_logger.info.assert_called_with("[DISCORD] [TestChar] Hello from character!")


class TestSessionMonitoring(unittest.TestCase):
    """Test session monitoring functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.dual_support = DualModeSupport()
        self.dual_support.config.session_monitor_enabled = True
        self.dual_support.config.monitor_interval = 1  # Fast for testing
        self.dual_support.config.drop_threshold = 5
    
    @patch('src.ms11.modes.dual_mode_support.pygetwindow')
    @patch('src.ms11.modes.dual_mode_support.socket')
    def test_session_monitor_start(self, mock_socket, mock_pygetwindow):
        """Test starting session monitor."""
        self.dual_support.config.dual_mode_enabled = True
        self.dual_support.start_dual_mode("TestPrimary", "TestSecondary")
        
        self.assertIsNotNone(self.dual_support.monitor_thread)
        self.assertTrue(self.dual_support.monitor_thread.is_alive())
    
    def test_session_monitor_disabled(self):
        """Test session monitor when disabled."""
        self.dual_support.config.session_monitor_enabled = False
        self.dual_support._start_session_monitor()
        
        self.assertIsNone(self.dual_support.monitor_thread)
    
    def test_handle_character_drop(self):
        """Test handling character drop."""
        with patch('src.ms11.modes.dual_mode_support.logger') as mock_logger:
            session = {"character_name": "TestChar"}
            self.dual_support._handle_character_drop(session, "Primary")
            
            mock_logger.warning.assert_called_with("[DUAL_MODE] Primary character dropped - attempting recovery")
    
    def test_attempt_reconnect(self):
        """Test attempting reconnection."""
        session = {
            "window_title": "SWG - TestChar",
            "window_handle": None,
            "is_active": False,
            "last_activity": datetime.now()
        }
        
        with patch('src.ms11.modes.dual_mode_support.pygetwindow') as mock_pygetwindow:
            # Mock window found
            mock_window = Mock()
            mock_pygetwindow.getWindowsWithTitle.return_value = [mock_window]
            
            with patch('src.ms11.modes.dual_mode_support.logger') as mock_logger:
                self.dual_support._attempt_reconnect(session, "Primary")
                
                mock_logger.info.assert_called_with("[DUAL_MODE] Successfully reconnected Primary character")
                self.assertEqual(session["window_handle"], mock_window)
                self.assertTrue(session["is_active"])


class TestLogging(unittest.TestCase):
    """Test logging functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.dual_support = DualModeSupport()
        self.dual_support.config.dual_mode_enabled = True
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.ms11.modes.dual_mode_support.Path')
    @patch('src.ms11.modes.dual_mode_support.json')
    def test_save_session_logs(self, mock_json, mock_path):
        """Test saving session logs."""
        # Mock log directory
        mock_log_dir = Mock()
        mock_path.return_value = mock_log_dir
        mock_log_dir.exists.return_value = True
        
        # Set up session data
        self.dual_support.shared_session_id = "test_session_123"
        self.dual_support.primary_session = {
            "character_name": "TestPrimary",
            "xp_gained": 1000,
            "quests_completed": 5
        }
        self.dual_support.secondary_session = {
            "character_name": "TestSecondary",
            "xp_gained": 500,
            "quests_completed": 2
        }
        
        # Mock file operations
        mock_file = Mock()
        mock_open = Mock(return_value=mock_file)
        
        with patch('builtins.open', mock_open):
            self.dual_support._save_session_logs()
            
            mock_open.assert_called()
            mock_json.dump.assert_called()


class TestIntegration(unittest.TestCase):
    """Test integration scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_session_config.json")
        
        # Create test configuration
        test_config = {
            "dual_mode": True,
            "primary_character": {
                "name": "TestPrimary",
                "mode": "quest",
                "role": "leader",
                "window_title": "SWG - TestPrimary"
            },
            "secondary_character": {
                "name": "TestSecondary",
                "mode": "medic",
                "role": "follower",
                "window_title": "SWG - TestSecondary"
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f, indent=2)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.session_manager.pygetwindow')
    @patch('src.session_manager.socket')
    def test_run_dual_character_mode(self, mock_socket, mock_pygetwindow):
        """Test running dual character mode."""
        result = run_dual_character_mode(
            "TestPrimary", "SWG - TestPrimary",
            "TestSecondary", "SWG - TestSecondary"
        )
        
        self.assertIn("status", result)
        self.assertIn("session_id", result)
        self.assertIn("message", result)
    
    @patch('src.ms11.modes.dual_mode_support.DualModeConfig')
    @patch('src.ms11.modes.dual_mode_support.DualModeSupport')
    def test_run_dual_mode(self, mock_dual_support_class, mock_config_class):
        """Test running dual mode."""
        # Mock dual mode support
        mock_dual_support = Mock()
        mock_dual_support_class.return_value = mock_dual_support
        mock_dual_support.start_dual_mode.return_value = True
        mock_dual_support.is_running = True
        mock_dual_support.shared_session_id = "test_session_123"
        
        # Mock session
        mock_session = Mock()
        mock_session.profile = {"test": "profile"}
        
        result = run_dual_mode(config={}, session=mock_session, max_loops=5)
        
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["session_id"], "test_session_123")
    
    def test_get_dual_session_status(self):
        """Test getting dual session status."""
        status = get_dual_session_status()
        
        self.assertIsInstance(status, dict)
    
    def test_get_dual_mode_status(self):
        """Test getting dual mode status."""
        status = get_dual_mode_status()
        
        self.assertIsInstance(status, dict)


class TestConfigurationValidation(unittest.TestCase):
    """Test configuration validation."""
    
    def test_valid_configuration(self):
        """Test valid configuration."""
        config = {
            "dual_mode": True,
            "primary_character": {
                "name": "TestPrimary",
                "mode": "quest",
                "role": "leader"
            },
            "secondary_character": {
                "name": "TestSecondary",
                "mode": "medic",
                "role": "follower"
            }
        }
        
        # This should not raise any exceptions
        dual_config = DualModeConfig()
        for key, value in config.items():
            if "." in key:
                keys = key.split(".")
                current = dual_config.config
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                current[keys[-1]] = value
            else:
                dual_config.config[key] = value
    
    def test_invalid_configuration(self):
        """Test invalid configuration handling."""
        # Test with missing required fields
        dual_config = DualModeConfig()
        
        # This should handle missing fields gracefully
        self.assertIsNotNone(dual_config.config)
        self.assertIn("dual_mode", dual_config.config)


if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestDualModeConfig,
        TestCharacterSession,
        TestSharedSessionData,
        TestDualCharacterSessionManager,
        TestDualModeSupport,
        TestDiscordIntegration,
        TestSessionMonitoring,
        TestLogging,
        TestIntegration,
        TestConfigurationValidation
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
    print(f"Tests run: {result.testsRun}")
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
    print(f"\n{'✅ PASSED' if success else '❌ FAILED'}")
    
    sys.exit(0 if success else 1) 