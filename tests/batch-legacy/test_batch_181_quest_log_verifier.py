#!/usr/bin/env python3
"""
Test suite for Batch 181 - MS11 Quest Log Verifier Module

This test suite covers:
- Quest log checking functionality
- Quest chain verification
- Session manager integration
- Fallback alert system
- Terminal message output
- Configuration management
"""

import os
import sys
import time
import json
import unittest
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from src.ms11.utils.quest_log_checker import (
        QuestLogChecker,
        QuestChain,
        QuestEntry,
        QuestStatus,
        verify_quest_chain,
        check_quest_log,
        get_eligible_quest_chains,
        get_completed_quests,
        add_completed_quest,
        save_quest_log,
        get_quest_log_status
    )
    from core.session_manager import SessionManager
    from utils.license_hooks import requires_license
    from profession_logic.utils.logger import logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory")
    # Don't call sys.exit() in tests - raise exception instead
    raise ImportError(f"Failed to import required modules: {e}") from e


class TestQuestStatus(unittest.TestCase):
    """Test quest status enum."""
    
    def test_quest_status_values(self):
        """Test quest status enum values."""
        self.assertEqual(QuestStatus.NOT_STARTED.value, "not_started")
        self.assertEqual(QuestStatus.IN_PROGRESS.value, "in_progress")
        self.assertEqual(QuestStatus.COMPLETED.value, "completed")
        self.assertEqual(QuestStatus.FAILED.value, "failed")
        self.assertEqual(QuestStatus.UNKNOWN.value, "unknown")


class TestQuestEntry(unittest.TestCase):
    """Test quest entry functionality."""
    
    def test_quest_entry_creation(self):
        """Test quest entry creation."""
        entry = QuestEntry(
            quest_name="Test Quest",
            quest_id="test_quest_123",
            status=QuestStatus.COMPLETED
        )
        
        self.assertEqual(entry.quest_name, "Test Quest")
        self.assertEqual(entry.quest_id, "test_quest_123")
        self.assertEqual(entry.status, QuestStatus.COMPLETED)
        self.assertIsNotNone(entry.completion_date)
    
    def test_quest_entry_defaults(self):
        """Test quest entry default values."""
        entry = QuestEntry("Test Quest")
        
        self.assertEqual(entry.status, QuestStatus.UNKNOWN)
        self.assertIsNotNone(entry.completion_date)
        self.assertIsNone(entry.quest_id)
        self.assertIsNone(entry.quest_chain)
        self.assertIsNone(entry.quest_type)
        self.assertIsNone(entry.location)
        self.assertIsNone(entry.npc)


class TestQuestChain(unittest.TestCase):
    """Test quest chain functionality."""
    
    def test_quest_chain_creation(self):
        """Test quest chain creation."""
        chain = QuestChain(
            chain_name="Test Chain",
            chain_id="test_chain_123",
            quests=["Quest 1", "Quest 2", "Quest 3"],
            required_level=10,
            faction="neutral",
            planet="Tatooine"
        )
        
        self.assertEqual(chain.chain_name, "Test Chain")
        self.assertEqual(chain.chain_id, "test_chain_123")
        self.assertEqual(len(chain.quests), 3)
        self.assertEqual(chain.required_level, 10)
        self.assertEqual(chain.faction, "neutral")
        self.assertEqual(chain.planet, "Tatooine")
    
    def test_quest_chain_eligibility(self):
        """Test quest chain eligibility checking."""
        chain = QuestChain(
            chain_name="Test Chain",
            chain_id="test_chain_123",
            quests=["Quest 1", "Quest 2", "Quest 3"]
        )
        
        # Test with no completed quests
        completed_quests = set()
        self.assertTrue(chain.is_eligible(completed_quests))
        
        # Test with one quest completed
        completed_quests = {"Quest 1"}
        self.assertFalse(chain.is_eligible(completed_quests))
        
        # Test with different quest completed
        completed_quests = {"Other Quest"}
        self.assertTrue(chain.is_eligible(completed_quests))


class TestQuestLogChecker(unittest.TestCase):
    """Test quest log checker functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_quest_log_config.json")
        
        # Create test configuration
        test_config = {
            "enabled": True,
            "use_journal_command": True,
            "use_ui_detection": True,
            "fallback_alert": True,
            "quest_chains_file": os.path.join(self.temp_dir, "test_quest_chains.json"),
            "completed_quests_file": os.path.join(self.temp_dir, "test_completed_quests.json")
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f, indent=2)
        
        # Create test quest chains
        test_chains = [
            {
                "chain_name": "Test Chain 1",
                "chain_id": "test_chain_1",
                "quests": ["Quest 1A", "Quest 1B", "Quest 1C"]
            },
            {
                "chain_name": "Test Chain 2",
                "chain_id": "test_chain_2",
                "quests": ["Quest 2A", "Quest 2B"]
            }
        ]
        
        with open(test_config["quest_chains_file"], 'w') as f:
            json.dump(test_chains, f, indent=2)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_quest_log_checker_initialization(self):
        """Test quest log checker initialization."""
        checker = QuestLogChecker(self.config_path)
        
        self.assertIsNotNone(checker.config)
        self.assertEqual(len(checker.quest_chains), 2)
        self.assertEqual(len(checker.completed_quests), 0)
        self.assertIsNone(checker.last_check_time)
    
    @patch('src.ms11.utils.quest_log_checker.pyautogui')
    def test_get_quest_log_via_journal(self, mock_pyautogui):
        """Test getting quest log via journal command."""
        checker = QuestLogChecker(self.config_path)
        
        quest_entries = checker._get_quest_log_via_journal()
        
        # Verify journal command was called
        mock_pyautogui.write.assert_called_with("/journal")
        mock_pyautogui.press.assert_called_with('enter')
        
        # Should return empty list for now (placeholder implementation)
        self.assertEqual(len(quest_entries), 0)
    
    @patch('src.ms11.utils.quest_log_checker.pyautogui')
    def test_get_quest_log_via_ui(self, mock_pyautogui):
        """Test getting quest log via UI detection."""
        checker = QuestLogChecker(self.config_path)
        
        # Mock screenshot
        mock_screenshot = Mock()
        mock_pyautogui.screenshot.return_value = mock_screenshot
        
        quest_entries = checker._get_quest_log_via_ui()
        
        # Should return sample quests (placeholder implementation)
        self.assertGreater(len(quest_entries), 0)
    
    def test_load_saved_quest_log(self):
        """Test loading saved quest log."""
        checker = QuestLogChecker(self.config_path)
        
        # Create test completed quests file
        test_completed_quests = {
            "last_updated": datetime.now().isoformat(),
            "total_completed": 2,
            "quests": [
                {
                    "quest_name": "Completed Quest 1",
                    "status": "completed",
                    "completion_date": datetime.now().isoformat()
                },
                {
                    "quest_name": "Completed Quest 2",
                    "status": "completed",
                    "completion_date": datetime.now().isoformat()
                }
            ]
        }
        
        with open(checker.config.get("completed_quests_file"), 'w') as f:
            json.dump(test_completed_quests, f, indent=2)
        
        quest_entries = checker._load_saved_quest_log()
        
        self.assertEqual(len(quest_entries), 2)
        self.assertEqual(quest_entries[0].quest_name, "Completed Quest 1")
        self.assertEqual(quest_entries[1].quest_name, "Completed Quest 2")
    
    def test_update_completed_quests(self):
        """Test updating completed quests."""
        checker = QuestLogChecker(self.config_path)
        
        # Create test quest entries
        quest_entries = [
            QuestEntry("Quest 1", status=QuestStatus.COMPLETED),
            QuestEntry("Quest 2", status=QuestStatus.IN_PROGRESS),
            QuestEntry("Quest 3", status=QuestStatus.COMPLETED)
        ]
        
        checker._update_completed_quests(quest_entries)
        
        self.assertEqual(len(checker.completed_quests), 2)
        self.assertIn("Quest 1", checker.completed_quests)
        self.assertIn("Quest 3", checker.completed_quests)
        self.assertNotIn("Quest 2", checker.completed_quests)
    
    def test_cache_validation(self):
        """Test cache validation."""
        checker = QuestLogChecker(self.config_path)
        
        # Test with no last check time
        self.assertFalse(checker._is_cache_valid())
        
        # Test with recent check time
        checker.last_check_time = datetime.now()
        self.assertTrue(checker._is_cache_valid())
        
        # Test with old check time
        checker.last_check_time = datetime.now() - timedelta(minutes=10)
        self.assertFalse(checker._is_cache_valid())
    
    def test_verify_quest_chain_eligibility(self):
        """Test quest chain eligibility verification."""
        checker = QuestLogChecker(self.config_path)
        
        # Test with eligible chain
        is_eligible, message = checker.verify_quest_chain_eligibility("test_chain_1")
        
        self.assertTrue(is_eligible)
        self.assertIn("eligible", message)
        
        # Test with non-existent chain
        is_eligible, message = checker.verify_quest_chain_eligibility("non_existent_chain")
        
        self.assertFalse(is_eligible)
        self.assertIn("not found", message)
    
    def test_get_eligible_quest_chains(self):
        """Test getting eligible quest chains."""
        checker = QuestLogChecker(self.config_path)
        
        eligible_chains = checker.get_eligible_quest_chains()
        
        self.assertEqual(len(eligible_chains), 2)
        chain_ids = [chain.chain_id for chain in eligible_chains]
        self.assertIn("test_chain_1", chain_ids)
        self.assertIn("test_chain_2", chain_ids)
    
    def test_add_completed_quest(self):
        """Test adding completed quest."""
        checker = QuestLogChecker(self.config_path)
        
        checker.add_completed_quest("New Completed Quest")
        
        self.assertIn("New Completed Quest", checker.completed_quests)
    
    def test_save_quest_log(self):
        """Test saving quest log."""
        checker = QuestLogChecker(self.config_path)
        
        # Add some completed quests
        checker.add_completed_quest("Quest 1")
        checker.add_completed_quest("Quest 2")
        
        # Save quest log
        checker.save_quest_log()
        
        # Verify file was created
        completed_quests_file = checker.config.get("completed_quests_file")
        self.assertTrue(os.path.exists(completed_quests_file))
        
        # Verify file contents
        with open(completed_quests_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(data["total_completed"], 2)
        self.assertEqual(len(data["quests"]), 2)


class TestSessionManagerIntegration(unittest.TestCase):
    """Test session manager integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_quest_log_config.json")
        
        # Create test configuration
        test_config = {
            "enabled": True,
            "quest_chains_file": os.path.join(self.temp_dir, "test_quest_chains.json"),
            "completed_quests_file": os.path.join(self.temp_dir, "test_completed_quests.json")
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f, indent=2)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('core.session_manager.verify_quest_chain')
    def test_verify_quest_chain_eligibility(self, mock_verify):
        """Test session manager quest chain verification."""
        # Mock the verify_quest_chain function
        mock_verify.return_value = (True, "Quest chain 'Test Chain' is eligible")
        
        session = SessionManager(mode="quest")
        
        is_eligible, message = session.verify_quest_chain_eligibility("test_chain_1")
        
        self.assertTrue(is_eligible)
        self.assertTrue(session.quest_log_verified)
        self.assertIsNotNone(session.last_quest_verification)
        
        # Verify the mock was called
        mock_verify.assert_called_with("test_chain_1")
    
    @patch('core.session_manager.check_quest_log')
    def test_check_quest_log(self, mock_check):
        """Test session manager quest log checking."""
        # Mock the check_quest_log function
        mock_check.return_value = True
        
        session = SessionManager(mode="quest")
        
        success = session.check_quest_log()
        
        self.assertTrue(success)
        self.assertTrue(session.quest_log_verified)
        self.assertIsNotNone(session.last_quest_verification)
        
        # Verify the mock was called
        mock_check.assert_called_with(False)
    
    def test_record_quest_completion(self):
        """Test recording quest completion."""
        session = SessionManager(mode="quest")
        
        # Mock the add_completed_quest function
        with patch('core.session_manager.add_completed_quest') as mock_add:
            session.record_quest_completion("Test Quest")
            
            self.assertIn("Test Quest", session.quests_completed)
            mock_add.assert_called_with("Test Quest")


class TestFallbackAlert(unittest.TestCase):
    """Test fallback alert functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_quest_log_config.json")
        
        # Create test configuration with fallback enabled
        test_config = {
            "enabled": True,
            "fallback_alert": True,
            "quest_chains_file": os.path.join(self.temp_dir, "test_quest_chains.json"),
            "completed_quests_file": os.path.join(self.temp_dir, "test_completed_quests.json")
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f, indent=2)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.ms11.utils.quest_log_checker.logger')
    def test_send_fallback_alert(self, mock_logger):
        """Test sending fallback alert."""
        checker = QuestLogChecker(self.config_path)
        
        checker._send_fallback_alert()
        
        # Verify warning was logged
        mock_logger.warning.assert_called_with("[QUEST_LOG] Quest log detection failed - using fallback mode")
    
    def test_fallback_alert_disabled(self):
        """Test fallback alert when disabled."""
        # Update config to disable fallback alert
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        config["fallback_alert"] = False
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        checker = QuestLogChecker(self.config_path)
        
        # The fallback alert should still work but might behave differently
        # This is implementation dependent
        self.assertFalse(checker.config.get("fallback_alert", True))


class TestTerminalMessage(unittest.TestCase):
    """Test terminal message output."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_quest_log_config.json")
        
        # Create test configuration
        test_config = {
            "enabled": True,
            "quest_verification": {
                "show_eligibility_message": True,
                "terminal_message_format": "✔ Quest log verified – ready for chain."
            },
            "quest_chains_file": os.path.join(self.temp_dir, "test_quest_chains.json"),
            "completed_quests_file": os.path.join(self.temp_dir, "test_completed_quests.json")
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f, indent=2)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('builtins.print')
    def test_terminal_message_output(self, mock_print):
        """Test terminal message output."""
        session = SessionManager(mode="quest")
        
        # Mock the verify_quest_chain function to return success
        with patch('core.session_manager.verify_quest_chain') as mock_verify:
            mock_verify.return_value = (True, "Quest chain 'Test Chain' is eligible")
            
            session.verify_quest_chain_eligibility("test_chain_1")
            
            # Verify the terminal message was printed
            mock_print.assert_called_with("✔ Quest log verified – ready for chain.")


class TestConfigurationManagement(unittest.TestCase):
    """Test configuration management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_quest_log_config.json")
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_default_config_creation(self):
        """Test default configuration creation."""
        # Remove config file to trigger default creation
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        
        checker = QuestLogChecker(self.config_path)
        
        self.assertIsNotNone(checker.config)
        self.assertIn("enabled", checker.config)
        self.assertIn("use_journal_command", checker.config)
        self.assertIn("use_ui_detection", checker.config)
        self.assertIn("fallback_alert", checker.config)
    
    def test_config_validation(self):
        """Test configuration validation."""
        # Create valid config
        valid_config = {
            "enabled": True,
            "use_journal_command": True,
            "use_ui_detection": True,
            "fallback_alert": True
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(valid_config, f, indent=2)
        
        checker = QuestLogChecker(self.config_path)
        
        self.assertTrue(checker.config.get("enabled"))
        self.assertTrue(checker.config.get("use_journal_command"))
        self.assertTrue(checker.config.get("use_ui_detection"))
        self.assertTrue(checker.config.get("fallback_alert"))


class TestIntegration(unittest.TestCase):
    """Test integration scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_quest_log_config.json")
        
        # Create test configuration
        test_config = {
            "enabled": True,
            "quest_chains_file": os.path.join(self.temp_dir, "test_quest_chains.json"),
            "completed_quests_file": os.path.join(self.temp_dir, "test_completed_quests.json")
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f, indent=2)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('src.ms11.utils.quest_log_checker.verify_quest_chain')
    def test_verify_quest_chain_function(self, mock_verify):
        """Test the main verify_quest_chain function."""
        # Mock the verify_quest_chain function
        mock_verify.return_value = (True, "Quest chain is eligible")
        
        is_eligible, message = verify_quest_chain("test_chain_1")
        
        self.assertTrue(is_eligible)
        self.assertEqual(message, "Quest chain is eligible")
        
        # Verify the mock was called
        mock_verify.assert_called_with("test_chain_1")
    
    @patch('src.ms11.utils.quest_log_checker.check_quest_log')
    def test_check_quest_log_function(self, mock_check):
        """Test the main check_quest_log function."""
        # Mock the check_quest_log function
        mock_check.return_value = True
        
        success = check_quest_log()
        
        self.assertTrue(success)
        
        # Verify the mock was called
        mock_check.assert_called_with(False)
    
    def test_get_quest_log_status(self):
        """Test getting quest log status."""
        status = get_quest_log_status()
        
        self.assertIsInstance(status, dict)
        self.assertIn("enabled", status)
        self.assertIn("completed_quests_count", status)
        self.assertIn("quest_chains_count", status)
        self.assertIn("last_check_time", status)
        self.assertIn("cache_valid", status)


if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestQuestStatus,
        TestQuestEntry,
        TestQuestChain,
        TestQuestLogChecker,
        TestSessionManagerIntegration,
        TestFallbackAlert,
        TestTerminalMessage,
        TestConfigurationManagement,
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