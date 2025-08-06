#!/usr/bin/env python3
"""MS11 Batch 081 - Anti-Detection Defense Layer v2 Test Suite"""

import unittest
import tempfile
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

from core.anti_detection import (
    DefenseManager,
    TimingRandomizer,
    EmoteSystem,
    EmoteContext,
    AntiPingLogic,
    SessionTracker
)


class TestTimingRandomizer(unittest.TestCase):
    """Test timing randomization functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
        
        # Create test config
        test_config = {
            "timing_randomization": {
                "idle_timing": {
                    "enabled": True,
                    "base_delay": 1.0,
                    "variance_range": [0.2, 5.0],
                    "max_consecutive_similar": 3
                },
                "action_timing": {
                    "enabled": True,
                    "base_delay": 0.5,
                    "variance_range": [0.1, 2.0],
                    "human_like_patterns": True
                },
                "login_logout_windows": {
                    "enabled": True,
                    "base_login_time": "08:00",
                    "base_logout_time": "22:00",
                    "variance_minutes": 30,
                    "session_duration_variance": [2.0, 4.0]
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        self.timing_randomizer = TimingRandomizer(str(self.config_path))
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_get_randomized_idle_timing(self):
        """Test idle timing randomization."""
        timing = self.timing_randomizer.get_randomized_idle_timing()
        self.assertIsInstance(timing, float)
        self.assertGreater(timing, 0.0)
        self.assertLess(timing, 10.0)  # Should be within reasonable range
    
    def test_get_randomized_action_timing(self):
        """Test action timing randomization."""
        timing = self.timing_randomizer.get_randomized_action_timing()
        self.assertIsInstance(timing, float)
        self.assertGreater(timing, 0.0)
        self.assertLess(timing, 5.0)  # Should be within reasonable range
    
    def test_get_login_window(self):
        """Test login window generation."""
        login_time, logout_time = self.timing_randomizer.get_login_window()
        self.assertIsInstance(login_time, datetime)
        self.assertIsInstance(logout_time, datetime)
        self.assertLess(login_time, logout_time)
    
    def test_get_session_duration(self):
        """Test session duration generation."""
        duration = self.timing_randomizer.get_session_duration()
        self.assertIsInstance(duration, float)
        self.assertGreater(duration, 1.0)
        self.assertLess(duration, 6.0)
    
    def test_should_take_break(self):
        """Test break logic."""
        # Should not take break for short sessions
        self.assertFalse(self.timing_randomizer.should_take_break(1.0))
        
        # Should take break for long sessions (with 30% probability)
        # We'll test multiple times to catch the probabilistic behavior
        breaks_taken = 0
        for _ in range(10):
            if self.timing_randomizer.should_take_break(3.0):
                breaks_taken += 1
        
        # Should have taken some breaks (not all or none)
        self.assertGreater(breaks_taken, 0)
        self.assertLess(breaks_taken, 10)
    
    def test_get_statistics(self):
        """Test statistics generation."""
        # Generate some timings first
        for _ in range(5):
            self.timing_randomizer.get_randomized_idle_timing()
        
        stats = self.timing_randomizer.get_statistics()
        self.assertIn("total_timings", stats)
        self.assertIn("average_timing", stats)
        self.assertGreater(stats["total_timings"], 0)


class TestEmoteSystem(unittest.TestCase):
    """Test emote system functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
        
        # Create test config
        test_config = {
            "emote_system": {
                "enabled": True,
                "emote_frequency": {
                    "min_interval_seconds": 60,
                    "max_interval_seconds": 300,
                    "probability_per_check": 0.3
                },
                "emotes": [
                    {"command": "/sit", "description": "Sit down", "probability": 0.4, "context": ["idle", "social"]},
                    {"command": "/mood", "description": "Show mood", "probability": 0.2, "context": ["idle", "social"]},
                    {"command": "/dance", "description": "Dance emote", "probability": 0.1, "context": ["social", "celebration"]}
                ],
                "context_triggers": {
                    "player_nearby": True,
                    "idle_time": 120,
                    "social_events": True
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        self.emote_system = EmoteSystem(str(self.config_path))
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_should_trigger_emote(self):
        """Test emote triggering logic."""
        # Test with idle context
        idle_context = EmoteContext(idle_time_seconds=180.0)
        should_trigger = self.emote_system.should_trigger_emote(idle_context)
        self.assertIsInstance(should_trigger, bool)
        
        # Test with social context
        social_context = EmoteContext(player_nearby=True, social_event=True)
        should_trigger = self.emote_system.should_trigger_emote(social_context)
        self.assertIsInstance(should_trigger, bool)
    
    def test_get_random_emote(self):
        """Test random emote selection."""
        context = EmoteContext(idle_time_seconds=180.0)
        emote = self.emote_system.get_random_emote(context)
        
        if emote:  # May return None due to probability
            self.assertIsInstance(emote.command, str)
            self.assertIsInstance(emote.description, str)
            self.assertIsInstance(emote.probability, float)
            self.assertIsInstance(emote.context, list)
    
    def test_execute_emote(self):
        """Test emote execution."""
        emote = self.emote_system.emotes[0]  # Get first emote
        success = self.emote_system.execute_emote(emote)
        self.assertTrue(success)
    
    def test_get_emote_statistics(self):
        """Test emote statistics."""
        # Execute some emotes first
        for emote in self.emote_system.emotes[:2]:
            self.emote_system.execute_emote(emote)
        
        stats = self.emote_system.get_emote_statistics()
        self.assertIn("total_emotes", stats)
        self.assertIn("emote_breakdown", stats)
        self.assertGreater(stats["total_emotes"], 0)


class TestAntiPingLogic(unittest.TestCase):
    """Test anti-ping logic functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
        
        # Create test config
        test_config = {
            "anti_ping_logic": {
                "enabled": True,
                "response_settings": {
                    "enabled": True,
                    "response_delay_range": [2.0, 8.0],
                    "max_responses_per_session": 5,
                    "response_probability": 0.7
                },
                "tell_detection": {
                    "enabled": True,
                    "scan_interval": 1.0,
                    "keywords": ["tell", "whisper", "private"],
                    "response_templates": [
                        "Sorry, I'm busy right now.",
                        "Can't talk, in combat."
                    ]
                },
                "ignore_list": {
                    "enabled": True,
                    "players": ["SpamPlayer"],
                    "guild_mates": True,
                    "friends": True
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        self.anti_ping = AntiPingLogic(str(self.config_path))
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_detect_tell_message(self):
        """Test tell message detection."""
        # Test valid tell message
        screen_text = "Player1 tells you: Hey, are you there?"
        tell_message = self.anti_ping.detect_tell_message(screen_text)
        self.assertIsNotNone(tell_message)
        self.assertEqual(tell_message.sender, "Player1")
        self.assertIn("Hey, are you there?", tell_message.message)
        
        # Test ignored player
        screen_text = "SpamPlayer tells you: Hello"
        tell_message = self.anti_ping.detect_tell_message(screen_text)
        self.assertIsNone(tell_message)
        
        # Test regular chat message
        screen_text = "Regular chat message"
        tell_message = self.anti_ping.detect_tell_message(screen_text)
        self.assertIsNone(tell_message)
    
    def test_should_respond_to_tell(self):
        """Test response decision logic."""
        tell_message = self.anti_ping.tell_history[0] if self.anti_ping.tell_history else None
        if tell_message:
            should_respond = self.anti_ping.should_respond_to_tell(tell_message)
            self.assertIsInstance(should_respond, bool)
    
    def test_get_response_for_tell(self):
        """Test response generation."""
        tell_message = self.anti_ping.tell_history[0] if self.anti_ping.tell_history else None
        if tell_message:
            response = self.anti_ping.get_response_for_tell(tell_message)
            if response:
                self.assertIsInstance(response, str)
                self.assertGreater(len(response), 0)
    
    def test_get_response_delay(self):
        """Test response delay generation."""
        delay = self.anti_ping.get_response_delay()
        self.assertIsInstance(delay, float)
        self.assertGreater(delay, 1.0)
        self.assertLess(delay, 10.0)
    
    def test_ignore_list_management(self):
        """Test ignore list management."""
        original_count = len(self.anti_ping.ignore_list)
        
        # Add player to ignore list
        self.anti_ping.add_to_ignore_list("TestPlayer")
        self.assertEqual(len(self.anti_ping.ignore_list), original_count + 1)
        self.assertIn("testplayer", self.anti_ping.ignore_list)
        
        # Remove player from ignore list
        self.anti_ping.remove_from_ignore_list("TestPlayer")
        self.assertEqual(len(self.anti_ping.ignore_list), original_count)
        self.assertNotIn("testplayer", self.anti_ping.ignore_list)
    
    def test_get_tell_statistics(self):
        """Test tell statistics generation."""
        stats = self.anti_ping.get_tell_statistics()
        self.assertIn("total_tells", stats)
        self.assertIn("responses_sent", stats)
        self.assertIn("response_rate", stats)
        self.assertIsInstance(stats["response_rate"], float)


class TestSessionTracker(unittest.TestCase):
    """Test session tracking functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
        
        # Create test config
        test_config = {
            "session_tracking": {
                "enabled": True,
                "tracking_settings": {
                    "per_character": True,
                    "per_day": True,
                    "max_sessions_per_day": 3,
                    "min_session_gap_hours": 2
                },
                "session_limits": {
                    "max_daily_hours": 8,
                    "max_consecutive_hours": 4,
                    "mandatory_break_hours": 1
                },
                "character_profiles": {
                    "track_individual_stats": True,
                    "rotation_enabled": True,
                    "max_characters_per_day": 2
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        self.session_tracker = SessionTracker(str(self.config_path))
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_start_session(self):
        """Test session start functionality."""
        # Add a character profile first
        self.session_tracker.add_character_profile("TestCharacter")
        
        # Test starting a session
        success = self.session_tracker.start_session("TestCharacter")
        self.assertTrue(success)
        self.assertIsNotNone(self.session_tracker.current_session)
        self.assertEqual(self.session_tracker.current_session.character_name, "TestCharacter")
    
    def test_end_session(self):
        """Test session end functionality."""
        # Start a session first
        self.session_tracker.add_character_profile("TestCharacter")
        self.session_tracker.start_session("TestCharacter")
        
        # End the session
        session_data = self.session_tracker.end_session("Test completed")
        self.assertIsNotNone(session_data)
        self.assertEqual(session_data.character_name, "TestCharacter")
        self.assertIsNotNone(session_data.end_time)
        self.assertGreater(session_data.duration_hours, 0.0)
    
    def test_get_character_daily_stats(self):
        """Test daily statistics retrieval."""
        stats = self.session_tracker.get_character_daily_stats("TestCharacter")
        self.assertIn("character_name", stats)
        self.assertIn("date", stats)
        self.assertIn("total_hours", stats)
        self.assertIn("sessions_count", stats)
    
    def test_add_character_profile(self):
        """Test character profile addition."""
        original_count = len(self.session_tracker.character_profiles)
        
        self.session_tracker.add_character_profile("NewCharacter", max_daily_hours=6.0)
        
        self.assertEqual(len(self.session_tracker.character_profiles), original_count + 1)
        self.assertIn("NewCharacter", self.session_tracker.character_profiles)
        
        profile = self.session_tracker.character_profiles["NewCharacter"]
        self.assertEqual(profile.max_daily_hours, 6.0)
    
    def test_get_available_characters(self):
        """Test available characters retrieval."""
        # Add some character profiles
        self.session_tracker.add_character_profile("Char1")
        self.session_tracker.add_character_profile("Char2")
        
        available = self.session_tracker.get_available_characters()
        self.assertIsInstance(available, list)
        self.assertGreater(len(available), 0)
    
    def test_get_session_statistics(self):
        """Test session statistics generation."""
        stats = self.session_tracker.get_session_statistics()
        self.assertIn("total_sessions", stats)
        self.assertIn("total_hours", stats)
        self.assertIn("characters_used", stats)
        self.assertIsInstance(stats["total_sessions"], int)
        self.assertIsInstance(stats["total_hours"], float)


class TestDefenseManager(unittest.TestCase):
    """Test defense manager integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
        
        # Create comprehensive test config
        test_config = {
            "anti_detection": {
                "enabled": True,
                "version": "2.0"
            },
            "timing_randomization": {
                "idle_timing": {
                    "enabled": True,
                    "base_delay": 1.0,
                    "variance_range": [0.2, 5.0],
                    "max_consecutive_similar": 3
                },
                "action_timing": {
                    "enabled": True,
                    "base_delay": 0.5,
                    "variance_range": [0.1, 2.0],
                    "human_like_patterns": True
                },
                "login_logout_windows": {
                    "enabled": True,
                    "base_login_time": "08:00",
                    "base_logout_time": "22:00",
                    "variance_minutes": 30,
                    "session_duration_variance": [2.0, 4.0]
                }
            },
            "emote_system": {
                "enabled": True,
                "emote_frequency": {
                    "min_interval_seconds": 60,
                    "max_interval_seconds": 300,
                    "probability_per_check": 0.3
                },
                "emotes": [
                    {"command": "/sit", "description": "Sit down", "probability": 0.4, "context": ["idle", "social"]}
                ],
                "context_triggers": {
                    "player_nearby": True,
                    "idle_time": 120,
                    "social_events": True
                }
            },
            "anti_ping_logic": {
                "enabled": True,
                "response_settings": {
                    "enabled": True,
                    "response_delay_range": [2.0, 8.0],
                    "max_responses_per_session": 5,
                    "response_probability": 0.7
                },
                "tell_detection": {
                    "enabled": True,
                    "scan_interval": 1.0,
                    "keywords": ["tell", "whisper", "private"],
                    "response_templates": [
                        "Sorry, I'm busy right now."
                    ]
                },
                "ignore_list": {
                    "enabled": True,
                    "players": [],
                    "guild_mates": True,
                    "friends": True
                }
            },
            "session_tracking": {
                "enabled": True,
                "tracking_settings": {
                    "per_character": True,
                    "per_day": True,
                    "max_sessions_per_day": 3,
                    "min_session_gap_hours": 2
                },
                "session_limits": {
                    "max_daily_hours": 8,
                    "max_consecutive_hours": 4,
                    "mandatory_break_hours": 1
                },
                "character_profiles": {
                    "track_individual_stats": True,
                    "rotation_enabled": True,
                    "max_characters_per_day": 2
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        self.defense_manager = DefenseManager(str(self.config_path))
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_start_defense(self):
        """Test defense start functionality."""
        # Add character profile first
        self.defense_manager.add_character_profile("TestCharacter")
        
        # Start defense
        success = self.defense_manager.start_defense("TestCharacter")
        self.assertTrue(success)
        self.assertTrue(self.defense_manager.is_defense_active())
        self.assertEqual(self.defense_manager.get_current_character(), "TestCharacter")
    
    def test_stop_defense(self):
        """Test defense stop functionality."""
        # Start defense first
        self.defense_manager.add_character_profile("TestCharacter")
        self.defense_manager.start_defense("TestCharacter")
        
        # Stop defense
        session_data = self.defense_manager.stop_defense("Test completed")
        self.assertFalse(self.defense_manager.is_defense_active())
        self.assertIsNone(self.defense_manager.get_current_character())
        
        if session_data:
            self.assertEqual(session_data.character_name, "TestCharacter")
    
    def test_get_randomized_timing(self):
        """Test timing retrieval."""
        idle_timing = self.defense_manager.get_randomized_timing("idle")
        action_timing = self.defense_manager.get_randomized_timing("action")
        
        self.assertIsInstance(idle_timing, float)
        self.assertIsInstance(action_timing, float)
        self.assertGreater(idle_timing, 0.0)
        self.assertGreater(action_timing, 0.0)
    
    def test_trigger_emote(self):
        """Test emote triggering."""
        emote = self.defense_manager.trigger_emote("idle")
        # May return None due to probability, but should be string if not None
        if emote:
            self.assertIsInstance(emote, str)
            self.assertIn("/", emote)
    
    def test_process_tell_message(self):
        """Test tell message processing."""
        screen_text = "Player1 tells you: Hello there"
        response = self.defense_manager.process_tell_message(screen_text)
        
        # May return None due to probability, but should be dict if not None
        if response:
            self.assertIsInstance(response, dict)
            self.assertIn("response", response)
            self.assertIn("delay_seconds", response)
    
    def test_get_defense_statistics(self):
        """Test defense statistics generation."""
        stats = self.defense_manager.get_defense_statistics()
        
        self.assertIn("defense_state", stats)
        self.assertIn("timing_randomizer", stats)
        self.assertIn("emote_system", stats)
        self.assertIn("anti_ping_logic", stats)
        self.assertIn("session_tracker", stats)
        
        defense_state = stats["defense_state"]
        self.assertIn("is_active", defense_state)
        self.assertIn("current_character", defense_state)
    
    def test_character_management(self):
        """Test character management functionality."""
        # Add character profiles
        self.defense_manager.add_character_profile("Char1")
        self.defense_manager.add_character_profile("Char2")
        
        # Test available characters
        available = self.defense_manager.get_available_characters()
        self.assertIsInstance(available, list)
        
        # Test character rotation
        rotation = self.defense_manager.get_character_rotation()
        self.assertIsInstance(rotation, list)
    
    def test_break_logic(self):
        """Test break logic."""
        # Add character profile and start session
        self.defense_manager.add_character_profile("TestCharacter")
        self.defense_manager.start_defense("TestCharacter")
        
        # Test break logic
        should_break = self.defense_manager.should_take_break()
        self.assertIsInstance(should_break, bool)
        
        break_duration = self.defense_manager.get_break_duration()
        self.assertIsInstance(break_duration, float)
        self.assertGreater(break_duration, 0.0)
        
        # Clean up
        self.defense_manager.stop_defense()


class TestIntegration(unittest.TestCase):
    """Integration tests for the anti-detection system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
        
        # Create minimal test config
        test_config = {
            "anti_detection": {"enabled": True, "version": "2.0"},
            "timing_randomization": {
                "idle_timing": {"enabled": True, "base_delay": 1.0, "variance_range": [0.2, 5.0], "max_consecutive_similar": 3},
                "action_timing": {"enabled": True, "base_delay": 0.5, "variance_range": [0.1, 2.0], "human_like_patterns": True},
                "login_logout_windows": {"enabled": True, "base_login_time": "08:00", "base_logout_time": "22:00", "variance_minutes": 30, "session_duration_variance": [2.0, 4.0]}
            },
            "emote_system": {
                "enabled": True,
                "emote_frequency": {"min_interval_seconds": 60, "max_interval_seconds": 300, "probability_per_check": 0.3},
                "emotes": [{"command": "/sit", "description": "Sit down", "probability": 0.4, "context": ["idle", "social"]}],
                "context_triggers": {"player_nearby": True, "idle_time": 120, "social_events": True}
            },
            "anti_ping_logic": {
                "enabled": True,
                "response_settings": {"enabled": True, "response_delay_range": [2.0, 8.0], "max_responses_per_session": 5, "response_probability": 0.7},
                "tell_detection": {"enabled": True, "scan_interval": 1.0, "keywords": ["tell", "whisper", "private"], "response_templates": ["Sorry, I'm busy right now."]},
                "ignore_list": {"enabled": True, "players": [], "guild_mates": True, "friends": True}
            },
            "session_tracking": {
                "enabled": True,
                "tracking_settings": {"per_character": True, "per_day": True, "max_sessions_per_day": 3, "min_session_gap_hours": 2},
                "session_limits": {"max_daily_hours": 8, "max_consecutive_hours": 4, "mandatory_break_hours": 1},
                "character_profiles": {"track_individual_stats": True, "rotation_enabled": True, "max_characters_per_day": 2}
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_full_defense_cycle(self):
        """Test a complete defense cycle."""
        defense_manager = DefenseManager(str(self.config_path))
        
        # Add character profile
        defense_manager.add_character_profile("IntegrationTest")
        
        # Start defense
        self.assertTrue(defense_manager.start_defense("IntegrationTest"))
        self.assertTrue(defense_manager.is_defense_active())
        
        # Test various features during active defense
        timing = defense_manager.get_randomized_timing("idle")
        self.assertIsInstance(timing, float)
        
        emote = defense_manager.trigger_emote("idle")
        # May be None due to probability
        
        response = defense_manager.process_tell_message("Player1 tells you: Hello")
        # May be None due to probability
        
        # Stop defense
        session_data = defense_manager.stop_defense("Integration test completed")
        self.assertFalse(defense_manager.is_defense_active())
        
        if session_data:
            self.assertEqual(session_data.character_name, "IntegrationTest")
    
    def test_multi_character_session(self):
        """Test multi-character session management."""
        defense_manager = DefenseManager(str(self.config_path))
        
        # Add multiple character profiles
        characters = ["Char1", "Char2", "Char3"]
        for char in characters:
            defense_manager.add_character_profile(char)
        
        # Test character rotation
        rotation = defense_manager.get_character_rotation()
        self.assertIsInstance(rotation, list)
        self.assertGreater(len(rotation), 0)
        
        # Test available characters
        available = defense_manager.get_available_characters()
        self.assertIsInstance(available, list)
        
        # Test session with each character
        for char in characters[:2]:  # Test with first 2 characters
            self.assertTrue(defense_manager.start_defense(char))
            self.assertEqual(defense_manager.get_current_character(), char)
            
            session_data = defense_manager.stop_defense(f"Session for {char}")
            if session_data:
                self.assertEqual(session_data.character_name, char)


def run_tests():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestTimingRandomizer,
        TestEmoteSystem,
        TestAntiPingLogic,
        TestSessionTracker,
        TestDefenseManager,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Test Summary:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*60}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1) 