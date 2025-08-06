#!/usr/bin/env python3
"""
Test suite for Batch 076 - Anti-Detection Defense Layer v1

This test suite validates all anti-detection features including:
- Session randomization and limits
- Human-like delay injection
- AFK whisper scanning and RP replies
- Cooldown tracking and management
- Dynamic movement injection
- Session warning system
"""

import unittest
import json
import time
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import our anti-detection components
from core.anti_detection import (
    create_anti_detection_defense,
    AntiDetectionDefense,
    SessionLimits,
    HumanLikeDelays,
    CooldownLimits,
    DynamicMovement,
    SessionWarnings
)
from services.afk_reply_manager import (
    create_afk_reply_manager,
    AFKReplyManager,
    WhisperScanning,
    RPReplies,
    AutoAFKDetection
)


class TestAntiDetectionDefense(unittest.TestCase):
    """Test the main anti-detection defense system."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_defense_config.json"
        
        # Create test config
        test_config = {
            "session_limits": {
                "max_hours_per_day": 6,
                "max_consecutive_hours": 3,
                "session_randomization_enabled": True
            },
            "human_like_delays": {
                "enabled": True,
                "min_delay": 0.1,
                "max_delay": 1.0
            },
            "cooldown_tracker": {
                "enabled": True,
                "tracked_actions": ["combat_skill", "movement"],
                "cooldown_limits": {
                    "combat_skill": {"max_uses_per_hour": 50, "cooldown_duration": 30},
                    "movement": {"max_actions_per_hour": 100, "cooldown_duration": 15}
                }
            },
            "dynamic_movement": {
                "enabled": True,
                "injection_frequency": 0.1
            },
            "session_warnings": {
                "enabled": True
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        self.defense = create_anti_detection_defense(str(self.config_path))

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test anti-detection defense initialization."""
        self.assertIsInstance(self.defense, AntiDetectionDefense)
        self.assertTrue(self.defense.config)
        self.assertIsInstance(self.defense.session_limits, SessionLimits)
        self.assertIsInstance(self.defense.human_like_delays, HumanLikeDelays)
        self.assertIsInstance(self.defense.cooldown_limits, CooldownLimits)
        self.assertIsInstance(self.defense.dynamic_movement, DynamicMovement)
        self.assertIsInstance(self.defense.session_warnings, SessionWarnings)

    def test_session_start(self):
        """Test session start functionality."""
        session_data = self.defense.start_session()
        
        self.assertIn("session_id", session_data)
        self.assertIn("start_time", session_data)
        self.assertIn("planned_duration", session_data)
        self.assertIn("break_scheduled", session_data)
        
        self.assertIsNotNone(self.defense.session_start_time)

    def test_session_limits_check(self):
        """Test session limits checking."""
        # Start session
        self.defense.start_session()
        
        # Check limits
        limits_status = self.defense.check_session_limits()
        
        self.assertIn("status", limits_status)
        self.assertIn("session_duration", limits_status)
        self.assertIn("total_today_hours", limits_status)
        self.assertIn("warnings", limits_status)

    def test_human_like_delays(self):
        """Test human-like delay injection."""
        # Test different delay types
        delay_types = ["typing", "movement", "combat", "general"]
        
        for delay_type in delay_types:
            start_time = time.time()
            delay_duration = self.defense.inject_human_delay(delay_type)
            actual_delay = time.time() - start_time
            
            self.assertIsInstance(delay_duration, float)
            self.assertGreaterEqual(delay_duration, 0)
            self.assertGreaterEqual(actual_delay, 0)

    def test_random_action_injection(self):
        """Test random action injection."""
        # Test multiple calls
        actions = []
        for _ in range(10):
            action = self.defense.inject_random_action()
            if action:
                actions.append(action)
        
        # Should have some actions (depending on frequency)
        self.assertIsInstance(actions, list)
        
        # All actions should be valid types
        valid_actions = ["look_around", "adjust_camera", "check_inventory", "emote", "sit_stand"]
        for action in actions:
            self.assertIn(action, valid_actions)

    def test_action_tracking(self):
        """Test action tracking and cooldown management."""
        # Test normal actions
        action_types = ["combat_skill", "movement"]
        
        for action_type in action_types:
            allowed = self.defense.track_action(action_type, {"test": True})
            self.assertTrue(allowed)
        
        # Test rapid actions (should hit limits)
        for _ in range(60):  # More than the limit
            allowed = self.defense.track_action("combat_skill", {"test": True})
            # Some should be blocked
            if not allowed:
                break
        else:
            self.fail("No actions were blocked despite hitting limits")

    def test_dynamic_movement_injection(self):
        """Test dynamic movement injection."""
        movements = []
        for _ in range(10):
            movement = self.defense.inject_dynamic_movement()
            if movement:
                movements.append(movement)
        
        # Should have some movements (depending on frequency)
        self.assertIsInstance(movements, list)
        
        # All movements should have required fields
        for movement in movements:
            self.assertIn("pattern", movement)
            self.assertIn("duration", movement)
            self.assertIn("timestamp", movement)

    def test_session_summary(self):
        """Test session summary generation."""
        # Start session
        self.defense.start_session()
        
        # Track some actions
        self.defense.track_action("combat_skill", {"test": True})
        self.defense.track_action("movement", {"test": True})
        
        # Get summary
        summary = self.defense.get_session_summary()
        
        self.assertIn("session_status", summary)
        self.assertIn("cooldown_status", summary)
        self.assertIn("config_loaded", summary)
        self.assertIn("features_enabled", summary)

    def test_session_end(self):
        """Test session ending."""
        # Start session
        self.defense.start_session()
        
        # End session
        end_data = self.defense.end_session()
        
        self.assertIn("end_time", end_data)
        self.assertIn("duration", end_data)
        self.assertIn("total_actions", end_data)
        
        # Session should be ended
        self.assertIsNone(self.defense.session_start_time)

    def test_config_loading_error(self):
        """Test handling of config loading errors."""
        # Create defense with non-existent config
        defense = create_anti_detection_defense("non_existent_config.json")
        
        # Should still initialize with defaults
        self.assertIsInstance(defense, AntiDetectionDefense)
        self.assertEqual(defense.config, {})


class TestAFKReplyManager(unittest.TestCase):
    """Test the AFK reply manager system."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_defense_config.json"
        
        # Create test config
        test_config = {
            "afk_reply_manager": {
                "whisper_scanning": {
                    "enabled": True,
                    "scan_interval": 1,
                    "response_delay_min": 1,
                    "response_delay_max": 3
                },
                "rp_replies": {
                    "enabled": True,
                    "reply_templates": ["Test reply 1", "Test reply 2"],
                    "emote_templates": ["/test1", "/test2"]
                },
                "auto_afk_detection": {
                    "enabled": True,
                    "inactivity_threshold": 5,
                    "afk_message": "Test AFK",
                    "return_message": "Test Return"
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        self.afk_manager = create_afk_reply_manager(str(self.config_path))

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test AFK reply manager initialization."""
        self.assertIsInstance(self.afk_manager, AFKReplyManager)
        self.assertTrue(self.afk_manager.config)
        self.assertIsInstance(self.afk_manager.whisper_scanning, WhisperScanning)
        self.assertIsInstance(self.afk_manager.rp_replies, RPReplies)
        self.assertIsInstance(self.afk_manager.auto_afk_detection, AutoAFKDetection)

    def test_activity_update(self):
        """Test activity update functionality."""
        initial_time = self.afk_manager.last_activity
        time.sleep(0.1)
        
        self.afk_manager.update_activity()
        
        self.assertGreater(self.afk_manager.last_activity, initial_time)

    def test_whisper_scanning(self):
        """Test whisper scanning functionality."""
        # Test scanning without chat log (simulation)
        whispers = self.afk_manager.scan_for_whispers()
        
        self.assertIsInstance(whispers, list)
        
        # Test scanning with chat log
        test_chat_log = "[Whisper from Player1]: Hey there!"
        whispers = self.afk_manager.scan_for_whispers(test_chat_log)
        
        if whispers:
            whisper = whispers[0]
            self.assertIn("sender", whisper)
            self.assertIn("message", whisper)
            self.assertIn("timestamp", whisper)
            self.assertIn("type", whisper)

    def test_whisper_parsing(self):
        """Test whisper parsing from chat log."""
        test_chat_log = """
        [Whisper from Player1]: Hey there!
        <Player2 whispers>: How are you?
        Whisper from Player3: Want to group up?
        """
        
        whispers = self.afk_manager._parse_whispers_from_log(test_chat_log)
        
        self.assertIsInstance(whispers, list)
        self.assertGreaterEqual(len(whispers), 1)
        
        for whisper in whispers:
            self.assertIn("sender", whisper)
            self.assertIn("message", whisper)
            self.assertEqual(whisper["type"], "whisper")

    def test_afk_detection(self):
        """Test AFK detection functionality."""
        # Initially not AFK
        afk_status = self.afk_manager.check_afk_status()
        self.assertFalse(afk_status.get("afk", True))
        
        # Simulate inactivity
        self.afk_manager.last_activity = time.time() - 10  # 10 seconds ago
        
        afk_status = self.afk_manager.check_afk_status()
        self.assertTrue(afk_status.get("afk", False))
        
        # Simulate activity return
        self.afk_manager.update_activity()
        afk_status = self.afk_manager.check_afk_status()
        self.assertFalse(afk_status.get("afk", True))

    def test_rp_reply_generation(self):
        """Test RP reply generation."""
        test_whisper = {
            "sender": "TestPlayer",
            "message": "Hello there!",
            "timestamp": time.time(),
            "type": "whisper"
        }
        
        reply = self.afk_manager._generate_rp_reply(test_whisper)
        
        self.assertIsInstance(reply, str)
        self.assertGreater(len(reply), 0)

    def test_whisper_response_logic(self):
        """Test whisper response logic."""
        test_whisper = {
            "sender": "TestPlayer",
            "message": "Hello!",
            "timestamp": time.time(),
            "type": "whisper"
        }
        
        # Test normal response
        should_respond = self.afk_manager._should_respond_to_whisper(test_whisper)
        self.assertIsInstance(should_respond, bool)
        
        # Test spam detection
        for _ in range(5):
            self.afk_manager._process_whisper(test_whisper)
        
        should_respond = self.afk_manager._should_respond_to_whisper(test_whisper)
        self.assertFalse(should_respond)  # Should be blocked as spam

    def test_afk_summary(self):
        """Test AFK summary generation."""
        # Update activity
        self.afk_manager.update_activity()
        
        # Get summary
        summary = self.afk_manager.get_afk_summary()
        
        self.assertIn("afk_status", summary)
        self.assertIn("inactivity_duration", summary)
        self.assertIn("whisper_history_count", summary)
        self.assertIn("reply_history_count", summary)
        self.assertIn("features_enabled", summary)
        self.assertIn("config_loaded", summary)

    def test_reply_statistics(self):
        """Test reply statistics generation."""
        # Add some test replies
        test_whisper = {
            "sender": "TestPlayer",
            "message": "Hello!",
            "timestamp": time.time(),
            "type": "whisper"
        }
        
        self.afk_manager._process_whisper(test_whisper)
        
        stats = self.afk_manager.get_reply_statistics()
        
        self.assertIn("total_replies", stats)
        self.assertIn("average_delay", stats)
        self.assertIn("sender_counts", stats)
        self.assertIn("reply_rate", stats)

    def test_recent_whispers(self):
        """Test recent whispers retrieval."""
        # Add some test whispers
        test_whisper = {
            "sender": "TestPlayer",
            "message": "Hello!",
            "timestamp": time.time(),
            "type": "whisper"
        }
        
        self.afk_manager.whisper_history.append(test_whisper)
        
        recent_whispers = self.afk_manager.get_recent_whispers(minutes=10)
        
        self.assertIsInstance(recent_whispers, list)
        self.assertGreaterEqual(len(recent_whispers), 1)

    def test_history_clearing(self):
        """Test history clearing functionality."""
        # Add some test data
        test_whisper = {
            "sender": "TestPlayer",
            "message": "Hello!",
            "timestamp": time.time(),
            "type": "whisper"
        }
        
        self.afk_manager.whisper_history.append(test_whisper)
        self.afk_manager.reply_history.append({"test": "data"})
        
        # Clear history
        self.afk_manager.clear_history()
        
        self.assertEqual(len(self.afk_manager.whisper_history), 0)
        self.assertEqual(len(self.afk_manager.reply_history), 0)


class TestIntegration(unittest.TestCase):
    """Test integration between anti-detection components."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_defense_config.json"
        
        # Create comprehensive test config
        test_config = {
            "session_limits": {
                "max_hours_per_day": 4,
                "max_consecutive_hours": 2,
                "session_randomization_enabled": True
            },
            "human_like_delays": {
                "enabled": True,
                "min_delay": 0.05,
                "max_delay": 0.5
            },
            "cooldown_tracker": {
                "enabled": True,
                "tracked_actions": ["combat_skill", "movement"],
                "cooldown_limits": {
                    "combat_skill": {"max_uses_per_hour": 20, "cooldown_duration": 10},
                    "movement": {"max_actions_per_hour": 50, "cooldown_duration": 5}
                }
            },
            "dynamic_movement": {
                "enabled": True,
                "injection_frequency": 0.2
            },
            "session_warnings": {
                "enabled": True
            },
            "afk_reply_manager": {
                "whisper_scanning": {
                    "enabled": True,
                    "scan_interval": 1,
                    "response_delay_min": 1,
                    "response_delay_max": 2
                },
                "rp_replies": {
                    "enabled": True,
                    "reply_templates": ["Test reply"],
                    "emote_templates": ["/test"]
                },
                "auto_afk_detection": {
                    "enabled": True,
                    "inactivity_threshold": 3,
                    "afk_message": "Test AFK",
                    "return_message": "Test Return"
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        self.defense = create_anti_detection_defense(str(self.config_path))
        self.afk_manager = create_afk_reply_manager(str(self.config_path))

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_integrated_session_management(self):
        """Test integrated session management."""
        # Start session
        session_data = self.defense.start_session()
        self.assertIn("session_id", session_data)
        
        # Update AFK activity
        self.afk_manager.update_activity()
        
        # Check both systems
        limits_status = self.defense.check_session_limits()
        afk_status = self.afk_manager.check_afk_status()
        
        self.assertIn("status", limits_status)
        self.assertIn("afk", afk_status)

    def test_integrated_action_processing(self):
        """Test integrated action processing."""
        # Start session
        self.defense.start_session()
        
        # Process actions with both systems
        for i in range(5):
            # Track action
            allowed = self.defense.track_action("combat_skill", {"skill": f"Skill_{i}"})
            self.assertTrue(allowed)
            
            # Inject delay
            delay = self.defense.inject_human_delay("combat")
            self.assertGreaterEqual(delay, 0)
            
            # Update AFK activity
            self.afk_manager.update_activity()
            
            # Check AFK status
            afk_status = self.afk_manager.check_afk_status()
            self.assertFalse(afk_status.get("afk", True))

    def test_integrated_whisper_handling(self):
        """Test integrated whisper handling."""
        # Start session
        self.defense.start_session()
        
        # Simulate whisper
        test_chat_log = "[Whisper from TestPlayer]: Hello!"
        whispers = self.afk_manager.scan_for_whispers(test_chat_log)
        
        if whispers:
            # Process whisper
            self.afk_manager._process_whisper(whispers[0])
            
            # Check reply history
            self.assertGreaterEqual(len(self.afk_manager.reply_history), 1)

    def test_integrated_movement_injection(self):
        """Test integrated movement injection."""
        # Start session
        self.defense.start_session()
        
        # Inject movement
        movement = self.defense.inject_dynamic_movement()
        
        if movement:
            # Update AFK activity
            self.afk_manager.update_activity()
            
            # Check AFK status
            afk_status = self.afk_manager.check_afk_status()
            self.assertFalse(afk_status.get("afk", True))

    def test_integrated_session_summaries(self):
        """Test integrated session summaries."""
        # Start session
        self.defense.start_session()
        
        # Perform some actions
        self.defense.track_action("combat_skill", {"test": True})
        self.afk_manager.update_activity()
        
        # Get summaries
        defense_summary = self.defense.get_session_summary()
        afk_summary = self.afk_manager.get_afk_summary()
        
        self.assertIn("session_status", defense_summary)
        self.assertIn("afk_status", afk_summary)

    def test_integrated_session_end(self):
        """Test integrated session ending."""
        # Start session
        self.defense.start_session()
        
        # Perform actions
        self.defense.track_action("combat_skill", {"test": True})
        self.afk_manager.update_activity()
        
        # End session
        end_data = self.defense.end_session()
        
        self.assertIn("duration", end_data)
        self.assertIsNone(self.defense.session_start_time)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in anti-detection components."""

    def test_config_loading_error(self):
        """Test handling of config loading errors."""
        # Test with non-existent config
        defense = create_anti_detection_defense("non_existent_config.json")
        afk_manager = create_afk_reply_manager("non_existent_config.json")
        
        # Should still initialize
        self.assertIsInstance(defense, AntiDetectionDefense)
        self.assertIsInstance(afk_manager, AFKReplyManager)

    def test_invalid_action_tracking(self):
        """Test handling of invalid action tracking."""
        defense = create_anti_detection_defense()
        
        # Test with invalid action type
        allowed = defense.track_action("invalid_action", {})
        self.assertTrue(allowed)  # Should default to allowed

    def test_invalid_delay_type(self):
        """Test handling of invalid delay types."""
        defense = create_anti_detection_defense()
        
        # Test with invalid delay type
        delay = defense.inject_human_delay("invalid_type")
        self.assertIsInstance(delay, float)
        self.assertGreaterEqual(delay, 0)

    def test_invalid_whisper_parsing(self):
        """Test handling of invalid whisper parsing."""
        afk_manager = create_afk_reply_manager()
        
        # Test with invalid chat log
        whispers = afk_manager._parse_whispers_from_log("Invalid log content")
        self.assertIsInstance(whispers, list)

    def test_invalid_afk_detection(self):
        """Test handling of invalid AFK detection."""
        afk_manager = create_afk_reply_manager()
        
        # Test with invalid state
        afk_manager.last_activity = None
        afk_status = afk_manager.check_afk_status()
        self.assertIn("error", afk_status)


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2) 