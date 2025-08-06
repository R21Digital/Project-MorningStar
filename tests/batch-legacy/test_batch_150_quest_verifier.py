#!/usr/bin/env python3
"""Test suite for Batch 150 - Quest Log Completion Verifier.

Comprehensive tests covering:
- Quest verification functionality
- OCR integration
- System log parsing
- Session tracking
- CLI operations
- Error handling
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.quest_verifier import (
    QuestVerifier,
    get_quest_verifier,
    verify_quest_completed,
    mark_quest_completed,
    get_completion_status
)


class TestQuestVerifier(unittest.TestCase):
    """Test cases for QuestVerifier class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.test_history_file = Path(self.test_dir) / "quest_history.json"
        
        # Mock OCR engine
        self.mock_ocr = Mock()
        self.mock_ocr.extract_text_from_screen.return_value = Mock(
            text="Sample quest log text",
            confidence=85.0
        )
        
        # Create verifier with test configuration
        with patch('core.quest_verifier.OCREngine') as mock_ocr_class:
            mock_ocr_class.return_value = self.mock_ocr
            self.verifier = QuestVerifier()
            self.verifier.history_file = self.test_history_file
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary files
        if self.test_history_file.exists():
            self.test_history_file.unlink()
        if self.test_dir and os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)
    
    def test_initialization(self):
        """Test QuestVerifier initialization."""
        self.assertIsNotNone(self.verifier)
        self.assertIsNotNone(self.verifier.ocr_engine)
        self.assertIsNotNone(self.verifier.quest_history)
        self.assertIn("completed_quests", self.verifier.quest_history)
        self.assertIn("completion_dates", self.verifier.quest_history)
        self.assertIn("verification_methods", self.verifier.quest_history)
    
    def test_load_quest_history_new_file(self):
        """Test loading quest history when file doesn't exist."""
        # Remove test file if it exists
        if self.test_history_file.exists():
            self.test_history_file.unlink()
        
        # Test loading non-existent file
        history = self.verifier._load_quest_history()
        
        self.assertIn("completed_quests", history)
        self.assertIn("completion_dates", history)
        self.assertIn("verification_methods", history)
        self.assertIn("last_updated", history)
        self.assertEqual(len(history["completed_quests"]), 0)
    
    def test_load_quest_history_existing_file(self):
        """Test loading quest history from existing file."""
        # Create test history file
        test_history = {
            "completed_quests": {"Test Quest": True},
            "completion_dates": {"Test Quest": "2024-01-15T10:30:00"},
            "verification_methods": {"Test Quest": "manual"},
            "last_updated": "2024-01-15T10:30:00"
        }
        
        with open(self.test_history_file, 'w', encoding='utf-8') as f:
            json.dump(test_history, f)
        
        # Test loading existing file
        history = self.verifier._load_quest_history()
        
        self.assertIn("Test Quest", history["completed_quests"])
        self.assertEqual(history["completed_quests"]["Test Quest"], True)
        self.assertEqual(history["completion_dates"]["Test Quest"], "2024-01-15T10:30:00")
        self.assertEqual(history["verification_methods"]["Test Quest"], "manual")
    
    def test_save_quest_history(self):
        """Test saving quest history to file."""
        # Add test data
        self.verifier.quest_history["completed_quests"]["Test Quest"] = True
        self.verifier.quest_history["completion_dates"]["Test Quest"] = "2024-01-15T10:30:00"
        self.verifier.quest_history["verification_methods"]["Test Quest"] = "manual"
        
        # Save history
        self.verifier._save_quest_history()
        
        # Verify file was created
        self.assertTrue(self.test_history_file.exists())
        
        # Verify content
        with open(self.test_history_file, 'r', encoding='utf-8') as f:
            saved_history = json.load(f)
        
        self.assertIn("Test Quest", saved_history["completed_quests"])
        self.assertEqual(saved_history["completed_quests"]["Test Quest"], True)
    
    def test_check_internal_history(self):
        """Test checking internal quest history."""
        # Add test quest to history
        self.verifier.quest_history["completed_quests"]["Test Quest"] = True
        
        # Test existing quest
        result = self.verifier._check_internal_history("Test Quest")
        self.assertTrue(result)
        
        # Test non-existing quest
        result = self.verifier._check_internal_history("Non-existent Quest")
        self.assertFalse(result)
        
        # Test case-insensitive matching
        result = self.verifier._check_internal_history("test quest")
        self.assertTrue(result)
    
    def test_check_quest_log_ui_success(self):
        """Test OCR quest log UI checking with success."""
        # Mock OCR result with quest name and completion indicator
        self.mock_ocr.extract_text_from_screen.return_value = Mock(
            text="Legacy Quest Part IV completed",
            confidence=85.0
        )
        
        result = self.verifier._check_quest_log_ui("Legacy Quest Part IV")
        self.assertTrue(result)
    
    def test_check_quest_log_ui_no_completion_indicator(self):
        """Test OCR quest log UI checking without completion indicator."""
        # Mock OCR result with quest name but no completion indicator
        self.mock_ocr.extract_text_from_screen.return_value = Mock(
            text="Legacy Quest Part IV in progress",
            confidence=85.0
        )
        
        result = self.verifier._check_quest_log_ui("Legacy Quest Part IV")
        self.assertFalse(result)
    
    def test_check_quest_log_ui_quest_not_found(self):
        """Test OCR quest log UI checking when quest not found."""
        # Mock OCR result without quest name
        self.mock_ocr.extract_text_from_screen.return_value = Mock(
            text="Other quest completed",
            confidence=85.0
        )
        
        result = self.verifier._check_quest_log_ui("Legacy Quest Part IV")
        self.assertFalse(result)
    
    def test_check_system_logs_success(self):
        """Test system log checking with success."""
        # Create temporary log file
        log_file = Path(self.test_dir) / "test.log"
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("Legacy Quest Part IV quest completed successfully\n")
        
        # Mock log paths to include our test file
        with patch.object(self.verifier, 'completion_patterns', ["quest completed"]):
            with patch('os.path.exists', return_value=True):
                with patch('builtins.open', create=True) as mock_open:
                    mock_open.return_value.__enter__.return_value.read.return_value = "Legacy Quest Part IV quest completed"
                    
                    result = self.verifier._check_system_logs("Legacy Quest Part IV")
                    self.assertTrue(result)
    
    def test_check_system_logs_no_match(self):
        """Test system log checking with no match."""
        # Mock log paths
        with patch('os.path.exists', return_value=True):
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = "Other quest completed"
                
                result = self.verifier._check_system_logs("Legacy Quest Part IV")
                self.assertFalse(result)
    
    def test_check_session_tracking_success(self):
        """Test session tracking checking with success."""
        # Mock session data with completed quest
        mock_session_data = {
            "completed_quests": ["Legacy Quest Part IV"]
        }
        
        with patch('core.quest_verifier.load_session', return_value=mock_session_data):
            result = self.verifier._check_session_tracking("Legacy Quest Part IV")
            self.assertTrue(result)
    
    def test_check_session_tracking_no_match(self):
        """Test session tracking checking with no match."""
        # Mock session data without quest
        mock_session_data = {
            "completed_quests": ["Other Quest"]
        }
        
        with patch('core.quest_verifier.load_session', return_value=mock_session_data):
            result = self.verifier._check_session_tracking("Legacy Quest Part IV")
            self.assertFalse(result)
    
    def test_verify_quest_completed_all_methods_fail(self):
        """Test quest verification when all methods fail."""
        # Mock all verification methods to return False
        with patch.object(self.verifier, '_check_internal_history', return_value=False):
            with patch.object(self.verifier, '_check_quest_log_ui', return_value=False):
                with patch.object(self.verifier, '_check_system_logs', return_value=False):
                    with patch.object(self.verifier, '_check_session_tracking', return_value=False):
                        result = self.verifier.verify_quest_completed("Test Quest")
                        self.assertFalse(result)
    
    def test_verify_quest_completed_internal_history_success(self):
        """Test quest verification with internal history success."""
        # Add quest to internal history
        self.verifier.quest_history["completed_quests"]["Test Quest"] = True
        
        result = self.verifier.verify_quest_completed("Test Quest")
        self.assertTrue(result)
    
    def test_verify_quest_completed_ocr_success(self):
        """Test quest verification with OCR success."""
        # Mock OCR to find quest with completion indicator
        self.mock_ocr.extract_text_from_screen.return_value = Mock(
            text="Test Quest completed",
            confidence=85.0
        )
        
        # Mock other methods to fail
        with patch.object(self.verifier, '_check_internal_history', return_value=False):
            with patch.object(self.verifier, '_check_system_logs', return_value=False):
                with patch.object(self.verifier, '_check_session_tracking', return_value=False):
                    result = self.verifier.verify_quest_completed("Test Quest")
                    self.assertTrue(result)
    
    def test_record_completion(self):
        """Test recording quest completion."""
        # Record completion
        self.verifier._record_completion("Test Quest", "manual")
        
        # Verify it was recorded
        self.assertIn("Test Quest", self.verifier.quest_history["completed_quests"])
        self.assertIn("Test Quest", self.verifier.quest_history["completion_dates"])
        self.assertIn("Test Quest", self.verifier.quest_history["verification_methods"])
        
        self.assertTrue(self.verifier.quest_history["completed_quests"]["Test Quest"])
        self.assertEqual(self.verifier.quest_history["verification_methods"]["Test Quest"], "manual")
    
    def test_mark_quest_completed(self):
        """Test manually marking quest as completed."""
        # Mark quest as completed
        self.verifier.mark_quest_completed("Test Quest", "manual")
        
        # Verify it was recorded
        self.assertIn("Test Quest", self.verifier.quest_history["completed_quests"])
        self.assertTrue(self.verifier.quest_history["completed_quests"]["Test Quest"])
    
    def test_get_completion_status(self):
        """Test getting completion status."""
        # Add test quest to history
        self.verifier.quest_history["completed_quests"]["Test Quest"] = True
        self.verifier.quest_history["completion_dates"]["Test Quest"] = "2024-01-15T10:30:00"
        self.verifier.quest_history["verification_methods"]["Test Quest"] = "manual"
        
        # Get status
        status = self.verifier.get_completion_status("Test Quest")
        
        # Verify status
        self.assertEqual(status["quest_name"], "Test Quest")
        self.assertTrue(status["is_completed"])
        self.assertEqual(status["completion_date"], "2024-01-15T10:30:00")
        self.assertEqual(status["verification_method"], "manual")
        self.assertIn("last_checked", status)
    
    def test_get_completed_quests(self):
        """Test getting list of completed quests."""
        # Add test quests
        self.verifier.quest_history["completed_quests"]["Quest 1"] = True
        self.verifier.quest_history["completed_quests"]["Quest 2"] = True
        
        completed_quests = self.verifier.get_completed_quests()
        
        self.assertIn("Quest 1", completed_quests)
        self.assertIn("Quest 2", completed_quests)
        self.assertEqual(len(completed_quests), 2)
    
    def test_clear_quest_history_specific(self):
        """Test clearing specific quest history."""
        # Add test quest
        self.verifier.quest_history["completed_quests"]["Test Quest"] = True
        self.verifier.quest_history["completion_dates"]["Test Quest"] = "2024-01-15T10:30:00"
        self.verifier.quest_history["verification_methods"]["Test Quest"] = "manual"
        
        # Clear specific quest
        self.verifier.clear_quest_history("Test Quest")
        
        # Verify it was removed
        self.assertNotIn("Test Quest", self.verifier.quest_history["completed_quests"])
        self.assertNotIn("Test Quest", self.verifier.quest_history["completion_dates"])
        self.assertNotIn("Test Quest", self.verifier.quest_history["verification_methods"])
    
    def test_clear_quest_history_all(self):
        """Test clearing all quest history."""
        # Add test quests
        self.verifier.quest_history["completed_quests"]["Quest 1"] = True
        self.verifier.quest_history["completed_quests"]["Quest 2"] = True
        
        # Clear all history
        self.verifier.clear_quest_history()
        
        # Verify all were removed
        self.assertEqual(len(self.verifier.quest_history["completed_quests"]), 0)
        self.assertEqual(len(self.verifier.quest_history["completion_dates"]), 0)
        self.assertEqual(len(self.verifier.quest_history["verification_methods"]), 0)


class TestQuestVerifierIntegration(unittest.TestCase):
    """Integration tests for quest verifier."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_history_file = Path(self.test_dir) / "quest_history.json"
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.test_history_file.exists():
            self.test_history_file.unlink()
        if self.test_dir and os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)
    
    def test_verify_quest_completed_function(self):
        """Test the convenience verify_quest_completed function."""
        with patch('core.quest_verifier.get_quest_verifier') as mock_get_verifier:
            mock_verifier = Mock()
            mock_verifier.verify_quest_completed.return_value = True
            mock_get_verifier.return_value = mock_verifier
            
            result = verify_quest_completed("Test Quest")
            
            self.assertTrue(result)
            mock_verifier.verify_quest_completed.assert_called_once_with("Test Quest")
    
    def test_mark_quest_completed_function(self):
        """Test the convenience mark_quest_completed function."""
        with patch('core.quest_verifier.get_quest_verifier') as mock_get_verifier:
            mock_verifier = Mock()
            mock_get_verifier.return_value = mock_verifier
            
            mark_quest_completed("Test Quest", "manual")
            
            mock_verifier.mark_quest_completed.assert_called_once_with("Test Quest", "manual")
    
    def test_get_completion_status_function(self):
        """Test the convenience get_completion_status function."""
        with patch('core.quest_verifier.get_quest_verifier') as mock_get_verifier:
            mock_verifier = Mock()
            mock_status = {"quest_name": "Test Quest", "is_completed": True}
            mock_verifier.get_completion_status.return_value = mock_status
            mock_get_verifier.return_value = mock_verifier
            
            result = get_completion_status("Test Quest")
            
            self.assertEqual(result, mock_status)
            mock_verifier.get_completion_status.assert_called_once_with("Test Quest")


class TestQuestVerifierErrorHandling(unittest.TestCase):
    """Test error handling in quest verifier."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_history_file = Path(self.test_dir) / "quest_history.json"
        
        # Mock OCR engine
        self.mock_ocr = Mock()
        self.mock_ocr.extract_text_from_screen.return_value = Mock(
            text="Sample text",
            confidence=85.0
        )
        
        with patch('core.quest_verifier.OCREngine') as mock_ocr_class:
            mock_ocr_class.return_value = self.mock_ocr
            self.verifier = QuestVerifier()
            self.verifier.history_file = self.test_history_file
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.test_history_file.exists():
            self.test_history_file.unlink()
        if self.test_dir and os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)
    
    def test_ocr_error_handling(self):
        """Test error handling in OCR operations."""
        # Mock OCR to raise exception
        self.mock_ocr.extract_text_from_screen.side_effect = Exception("OCR Error")
        
        # Should not raise exception, should return False
        result = self.verifier._check_quest_log_ui("Test Quest")
        self.assertFalse(result)
    
    def test_file_read_error_handling(self):
        """Test error handling when reading files."""
        # Mock file operations to raise exception
        with patch('builtins.open', side_effect=Exception("File Error")):
            result = self.verifier._check_system_logs("Test Quest")
            self.assertFalse(result)
    
    def test_session_data_error_handling(self):
        """Test error handling in session data operations."""
        # Mock session loading to raise exception
        with patch('core.quest_verifier.load_session', side_effect=Exception("Session Error")):
            result = self.verifier._check_session_tracking("Test Quest")
            self.assertFalse(result)
    
    def test_save_history_error_handling(self):
        """Test error handling when saving history."""
        # Mock file operations to raise exception
        with patch('builtins.open', side_effect=Exception("Save Error")):
            # Should not raise exception
            self.verifier._record_completion("Test Quest", "manual")
            # Should continue without error


class TestQuestVerifierCLI(unittest.TestCase):
    """Test CLI functionality."""
    
    def test_cli_import(self):
        """Test that CLI module can be imported."""
        try:
            from cli.quest_verifier_cli import main
            self.assertTrue(True)  # Import successful
        except ImportError as e:
            self.fail(f"Failed to import CLI module: {e}")


def run_tests():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestQuestVerifier,
        TestQuestVerifierIntegration,
        TestQuestVerifierErrorHandling,
        TestQuestVerifierCLI
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 