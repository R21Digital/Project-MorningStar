#!/usr/bin/env python3
"""
Batch 150 - Quest Verification Integration Tests

This test suite validates the quest completion verification system including:
- OCR scanning functionality
- Log parsing capabilities
- Cache management
- Manual override functionality
- Error handling
- Performance optimization

Usage:
    python test_batch_150_integration.py
"""

import json
import logging
import os
import shutil
import sys
import tempfile
import time
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from core.quest_verifier import (
    QuestVerifier,
    QuestCompletionStatus,
    QuestLogRegion,
    get_quest_verifier,
    verify_quest_completed,
    get_completed_quests,
    add_manual_quest_completion,
    export_quest_completion_report
)


class TestQuestVerifier(unittest.TestCase):
    """Test suite for QuestVerifier class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.test_cache_file = os.path.join(self.test_dir, "test_quest_completions.json")
        
        # Mock OCR and screenshot components
        self.mock_ocr_engine = Mock()
        self.mock_screenshot_manager = Mock()
        
        # Create test verifier with mocked components
        with patch('core.quest_verifier.get_ocr_engine', return_value=self.mock_ocr_engine):
            with patch('core.quest_verifier.get_screenshot_manager', return_value=self.mock_screenshot_manager):
                self.verifier = QuestVerifier(cache_file=self.test_cache_file)
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test QuestVerifier initialization."""
        self.assertIsNotNone(self.verifier)
        self.assertEqual(self.verifier.cache_file, Path(self.test_cache_file))
        self.assertEqual(len(self.verifier.completed_quests), 0)
        self.assertIsNotNone(self.verifier.ocr_engine)
        self.assertIsNotNone(self.verifier.screenshot_manager)
    
    def test_load_completion_cache_empty(self):
        """Test loading empty completion cache."""
        # Cache file doesn't exist initially
        self.assertEqual(len(self.verifier.completed_quests), 0)
    
    def test_load_completion_cache_with_data(self):
        """Test loading completion cache with existing data."""
        # Create test cache file
        test_data = {
            "completed_quests": ["Quest 1", "Quest 2", "Quest 3"],
            "total_completed": 3
        }
        with open(self.test_cache_file, 'w') as f:
            json.dump(test_data, f)
        
        # Create new verifier to load the cache
        with patch('core.quest_verifier.get_ocr_engine', return_value=self.mock_ocr_engine):
            with patch('core.quest_verifier.get_screenshot_manager', return_value=self.mock_screenshot_manager):
                verifier = QuestVerifier(cache_file=self.test_cache_file)
        
        self.assertEqual(len(verifier.completed_quests), 3)
        self.assertIn("Quest 1", verifier.completed_quests)
        self.assertIn("Quest 2", verifier.completed_quests)
        self.assertIn("Quest 3", verifier.completed_quests)
    
    def test_save_completion_cache(self):
        """Test saving completion cache."""
        # Add some test quests
        self.verifier.completed_quests.add("Test Quest 1")
        self.verifier.completed_quests.add("Test Quest 2")
        
        # Save cache
        self.verifier.save_completion_cache()
        
        # Verify file was created
        self.assertTrue(os.path.exists(self.test_cache_file))
        
        # Verify content
        with open(self.test_cache_file, 'r') as f:
            data = json.load(f)
        
        self.assertIn("completed_quests", data)
        self.assertIn("total_completed", data)
        self.assertIn("last_updated", data)
        self.assertEqual(data["total_completed"], 2)
        self.assertIn("Test Quest 1", data["completed_quests"])
        self.assertIn("Test Quest 2", data["completed_quests"])
    
    def test_verify_quest_completed_cache_hit(self):
        """Test quest verification with cache hit."""
        # Add quest to cache
        self.verifier.completed_quests.add("Cached Quest")
        
        # Verify quest
        status = self.verifier.verify_quest_completed("Cached Quest")
        
        self.assertTrue(status.is_completed)
        self.assertEqual(status.confidence, 1.0)
        self.assertEqual(status.method, "cache")
        self.assertEqual(status.quest_name, "Cached Quest")
    
    def test_verify_quest_completed_not_found(self):
        """Test quest verification when quest is not found."""
        status = self.verifier.verify_quest_completed("Non-existent Quest")
        
        self.assertFalse(status.is_completed)
        self.assertEqual(status.confidence, 0.0)
        self.assertEqual(status.method, "none")
        self.assertEqual(status.quest_name, "Non-existent Quest")
    
    def test_scan_quest_log_ocr_success(self):
        """Test OCR scanning with successful result."""
        # Mock OCR result
        mock_ocr_result = Mock()
        mock_ocr_result.text = "Legacy Questline completed ✓"
        mock_ocr_result.confidence = 85.0
        
        self.mock_ocr_engine.extract_text.return_value = mock_ocr_result
        
        # Mock screenshot
        mock_screenshot = Mock()
        self.mock_screenshot_manager.capture_region.return_value = mock_screenshot
        
        # Test OCR scanning
        status = self.verifier._scan_quest_log_ocr("Legacy Questline")
        
        self.assertTrue(status.is_completed)
        self.assertGreater(status.confidence, 0.8)
        self.assertEqual(status.method, "ocr")
        self.assertIn("Found 'Legacy Questline' in quest log OCR text", status.evidence)
    
    def test_scan_quest_log_ocr_found_no_completion(self):
        """Test OCR scanning when quest is found but not marked as completed."""
        # Mock OCR result
        mock_ocr_result = Mock()
        mock_ocr_result.text = "Legacy Questline in progress"
        mock_ocr_result.confidence = 75.0
        
        self.mock_ocr_engine.extract_text.return_value = mock_ocr_result
        
        # Mock screenshot
        mock_screenshot = Mock()
        self.mock_screenshot_manager.capture_region.return_value = mock_screenshot
        
        # Test OCR scanning
        status = self.verifier._scan_quest_log_ocr("Legacy Questline")
        
        self.assertFalse(status.is_completed)
        self.assertEqual(status.confidence, 0.3)
        self.assertEqual(status.method, "ocr")
        self.assertIn("Found 'Legacy Questline' in quest log but no completion indicators", status.evidence)
    
    def test_scan_quest_log_ocr_not_found(self):
        """Test OCR scanning when quest is not found."""
        # Mock OCR result
        mock_ocr_result = Mock()
        mock_ocr_result.text = "Other quests here"
        mock_ocr_result.confidence = 80.0
        
        self.mock_ocr_engine.extract_text.return_value = mock_ocr_result
        
        # Mock screenshot
        mock_screenshot = Mock()
        self.mock_screenshot_manager.capture_region.return_value = mock_screenshot
        
        # Test OCR scanning
        status = self.verifier._scan_quest_log_ocr("Legacy Questline")
        
        self.assertFalse(status.is_completed)
        self.assertEqual(status.confidence, 0.1)
        self.assertEqual(status.method, "ocr")
        self.assertIn("Quest 'Legacy Questline' not found in quest log OCR", status.evidence)
    
    def test_scan_quest_log_ocr_error(self):
        """Test OCR scanning with error."""
        # Mock OCR to raise exception
        self.mock_ocr_engine.extract_text.side_effect = Exception("OCR failed")
        
        # Test OCR scanning
        status = self.verifier._scan_quest_log_ocr("Legacy Questline")
        
        self.assertFalse(status.is_completed)
        self.assertEqual(status.confidence, 0.0)
        self.assertEqual(status.method, "ocr_error")
        self.assertIn("OCR scanning failed", status.evidence[0])
    
    def test_parse_system_chat_log_success(self):
        """Test system chat log parsing with success."""
        # Create temporary log file
        log_file = os.path.join(self.test_dir, "system_chat.log")
        with open(log_file, 'w') as f:
            f.write("Some chat messages\n")
            f.write("Legacy Questline completed successfully\n")
            f.write("More chat messages\n")
        
        # Mock Path.exists to return True for our log file
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open', create=True) as mock_open:
                mock_open.return_value.__enter__.return_value.read.return_value = \
                    "Legacy Questline completed successfully"
                
                status = self.verifier._parse_system_chat_log("Legacy Questline")
        
        self.assertTrue(status.is_completed)
        self.assertEqual(status.confidence, 0.8)
        self.assertEqual(status.method, "system_chat_log")
        self.assertIn("Found completion message", status.evidence[0])
    
    def test_parse_system_chat_log_not_found(self):
        """Test system chat log parsing when quest is not found."""
        # Mock Path.exists to return False
        with patch('pathlib.Path.exists', return_value=False):
            status = self.verifier._parse_system_chat_log("Legacy Questline")
        
        self.assertFalse(status.is_completed)
        self.assertEqual(status.confidence, 0.0)
        self.assertEqual(status.method, "system_chat_log")
        self.assertIn("No completion messages found in system chat logs", status.evidence)
    
    def test_parse_saved_quest_log_success(self):
        """Test saved quest log parsing with success."""
        # Mock read_saved_quest_log to return test data
        test_log_lines = [
            "Legacy Questline completed ✓",
            "Other quest in progress",
            "Another quest completed"
        ]
        
        with patch('core.quest_verifier.read_saved_quest_log', return_value=test_log_lines):
            status = self.verifier._parse_saved_quest_log("Legacy Questline")
        
        self.assertTrue(status.is_completed)
        self.assertEqual(status.confidence, 0.9)
        self.assertEqual(status.method, "saved_quest_log")
        self.assertIn("Found completion in saved quest log", status.evidence[0])
    
    def test_parse_saved_quest_log_not_found(self):
        """Test saved quest log parsing when quest is not found."""
        # Mock read_saved_quest_log to return empty list
        with patch('core.quest_verifier.read_saved_quest_log', return_value=[]):
            status = self.verifier._parse_saved_quest_log("Legacy Questline")
        
        self.assertFalse(status.is_completed)
        self.assertEqual(status.confidence, 0.0)
        self.assertEqual(status.method, "saved_quest_log")
        self.assertIn("Quest not found in saved quest log", status.evidence)
    
    def test_get_completed_quests_list(self):
        """Test getting list of completed quests."""
        # Add some test quests
        self.verifier.completed_quests.add("Quest A")
        self.verifier.completed_quests.add("Quest B")
        self.verifier.completed_quests.add("Quest C")
        
        completed_list = self.verifier.get_completed_quests_list()
        
        self.assertEqual(len(completed_list), 3)
        self.assertIn("Quest A", completed_list)
        self.assertIn("Quest B", completed_list)
        self.assertIn("Quest C", completed_list)
        # Should be sorted
        self.assertEqual(completed_list, sorted(completed_list))
    
    def test_add_manual_completion(self):
        """Test manual quest completion override."""
        # Add quest as completed
        self.verifier.add_manual_completion("Manual Quest", True)
        self.assertIn("Manual Quest", self.verifier.completed_quests)
        
        # Remove quest from completed
        self.verifier.add_manual_completion("Manual Quest", False)
        self.assertNotIn("Manual Quest", self.verifier.completed_quests)
    
    def test_clear_completion_cache(self):
        """Test clearing completion cache."""
        # Add some quests
        self.verifier.completed_quests.add("Quest 1")
        self.verifier.completed_quests.add("Quest 2")
        
        # Clear cache
        self.verifier.clear_completion_cache()
        
        self.assertEqual(len(self.verifier.completed_quests), 0)
    
    def test_export_completion_report(self):
        """Test exporting completion report."""
        # Add some test quests
        self.verifier.completed_quests.add("Exported Quest 1")
        self.verifier.completed_quests.add("Exported Quest 2")
        
        # Export report
        report_file = os.path.join(self.test_dir, "test_report.json")
        exported_path = self.verifier.export_completion_report(report_file)
        
        # Verify file was created
        self.assertTrue(os.path.exists(exported_path))
        
        # Verify content
        with open(exported_path, 'r') as f:
            data = json.load(f)
        
        self.assertIn("export_timestamp", data)
        self.assertIn("total_completed_quests", data)
        self.assertIn("completed_quests", data)
        self.assertIn("cache_file", data)
        self.assertIn("export_method", data)
        self.assertEqual(data["total_completed_quests"], 2)
        self.assertIn("Exported Quest 1", data["completed_quests"])
        self.assertIn("Exported Quest 2", data["completed_quests"])


class TestQuestVerifierIntegration(unittest.TestCase):
    """Integration tests for quest verifier functionality."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_cache_file = os.path.join(self.test_dir, "integration_test_cache.json")
        
        # Create test log files
        self.system_chat_log = os.path.join(self.test_dir, "system_chat.log")
        with open(self.system_chat_log, 'w', encoding='utf-8') as f:
            f.write("System chat log for testing\n")
            f.write("Legacy Questline completed successfully\n")
            f.write("Combat Training finished\n")
        
        # Create test quest log
        self.quest_log = os.path.join(self.test_dir, "quest_log.txt")
        with open(self.quest_log, 'w', encoding='utf-8') as f:
            f.write("Legacy Questline completed ✓\n")
            f.write("Combat Training in progress\n")
            f.write("Exploration Mission done\n")
    
    def tearDown(self):
        """Clean up integration test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_full_verification_workflow(self):
        """Test complete quest verification workflow."""
        # Mock OCR and screenshot components
        mock_ocr_engine = Mock()
        mock_screenshot_manager = Mock()
        
        # Mock OCR result
        mock_ocr_result = Mock()
        mock_ocr_result.text = "Legacy Questline completed ✓"
        mock_ocr_result.confidence = 90.0
        mock_ocr_engine.extract_text.return_value = mock_ocr_result
        
        # Mock screenshot
        mock_screenshot = Mock()
        mock_screenshot_manager.capture_region.return_value = mock_screenshot
        
        # Create verifier with mocked components
        with patch('core.quest_verifier.get_ocr_engine', return_value=mock_ocr_engine):
            with patch('core.quest_verifier.get_screenshot_manager', return_value=mock_screenshot_manager):
                verifier = QuestVerifier(cache_file=self.test_cache_file)
        
        # Test verification workflow
        status = verifier.verify_quest_completed("Legacy Questline")
        
        # Verify result
        self.assertTrue(status.is_completed)
        self.assertGreater(status.confidence, 0.8)
        self.assertEqual(status.method, "ocr")
        
        # Verify quest was added to cache
        self.assertIn("Legacy Questline", verifier.completed_quests)
        
        # Test cache hit
        status2 = verifier.verify_quest_completed("Legacy Questline")
        self.assertTrue(status2.is_completed)
        self.assertEqual(status2.method, "cache")
    
    def test_multiple_verification_methods(self):
        """Test that multiple verification methods are tried."""
        # Mock OCR to fail
        mock_ocr_engine = Mock()
        mock_ocr_engine.extract_text.side_effect = Exception("OCR failed")
        
        # Mock screenshot
        mock_screenshot_manager = Mock()
        mock_screenshot = Mock()
        mock_screenshot_manager.capture_region.return_value = mock_screenshot
        
        # Create verifier
        with patch('core.quest_verifier.get_ocr_engine', return_value=mock_ocr_engine):
            with patch('core.quest_verifier.get_screenshot_manager', return_value=mock_screenshot_manager):
                verifier = QuestVerifier(cache_file=self.test_cache_file)
        
        # Mock system chat log parsing to succeed
        with patch.object(verifier, '_parse_system_chat_log') as mock_parse_log:
            mock_parse_log.return_value = QuestCompletionStatus(
                quest_name="Test Quest",
                is_completed=True,
                confidence=0.8,
                method="system_chat_log",
                timestamp=datetime.now(),
                evidence=["Found in log"]
            )
            
            status = verifier.verify_quest_completed("Test Quest")
        
        # Verify OCR was tried first, then log parsing succeeded
        self.assertTrue(status.is_completed)
        self.assertEqual(status.method, "system_chat_log")
        self.assertIn("Test Quest", verifier.completed_quests)


class TestQuestVerifierPerformance(unittest.TestCase):
    """Performance tests for quest verifier."""
    
    def setUp(self):
        """Set up performance test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_cache_file = os.path.join(self.test_dir, "performance_test_cache.json")
        
        # Mock components
        self.mock_ocr_engine = Mock()
        self.mock_screenshot_manager = Mock()
        
        # Create verifier
        with patch('core.quest_verifier.get_ocr_engine', return_value=self.mock_ocr_engine):
            with patch('core.quest_verifier.get_screenshot_manager', return_value=self.mock_screenshot_manager):
                self.verifier = QuestVerifier(cache_file=self.test_cache_file)
    
    def tearDown(self):
        """Clean up performance test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_cache_performance(self):
        """Test that cache provides performance benefits."""
        # Add quest to cache
        self.verifier.completed_quests.add("Performance Test Quest")
        
        # Time cache hit
        start_time = time.time()
        status1 = self.verifier.verify_quest_completed("Performance Test Quest")
        cache_time = time.time() - start_time
        
        # Time cache miss (should be slower)
        start_time = time.time()
        status2 = self.verifier.verify_quest_completed("Non-cached Quest")
        no_cache_time = time.time() - start_time
        
        # Cache hit should be faster
        self.assertLess(cache_time, no_cache_time)
        self.assertTrue(status1.is_completed)
        self.assertFalse(status2.is_completed)
    
    def test_large_cache_performance(self):
        """Test performance with large number of cached quests."""
        # Add many quests to cache
        for i in range(1000):
            self.verifier.completed_quests.add(f"Quest {i}")
        
        # Time lookup in large cache
        start_time = time.time()
        status = self.verifier.verify_quest_completed("Quest 500")
        lookup_time = time.time() - start_time
        
        # Should be fast even with large cache
        self.assertLess(lookup_time, 0.1)  # Should be under 100ms
        self.assertTrue(status.is_completed)


class TestQuestVerifierErrorHandling(unittest.TestCase):
    """Error handling tests for quest verifier."""
    
    def setUp(self):
        """Set up error handling test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_cache_file = os.path.join(self.test_dir, "error_test_cache.json")
        
        # Mock components
        self.mock_ocr_engine = Mock()
        self.mock_screenshot_manager = Mock()
        
        # Create verifier
        with patch('core.quest_verifier.get_ocr_engine', return_value=self.mock_ocr_engine):
            with patch('core.quest_verifier.get_screenshot_manager', return_value=self.mock_screenshot_manager):
                self.verifier = QuestVerifier(cache_file=self.test_cache_file)
    
    def tearDown(self):
        """Clean up error handling test environment."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_cache_file_corruption(self):
        """Test handling of corrupted cache file."""
        # Create corrupted cache file
        with open(self.test_cache_file, 'w') as f:
            f.write("Invalid JSON content")
        
        # Should handle gracefully
        verifier = QuestVerifier(cache_file=self.test_cache_file)
        self.assertEqual(len(verifier.completed_quests), 0)
    
    def test_ocr_failure_graceful(self):
        """Test graceful handling of OCR failures."""
        # Mock OCR to always fail
        self.mock_ocr_engine.extract_text.side_effect = Exception("OCR failed")
        
        # Mock screenshot
        mock_screenshot = Mock()
        self.mock_screenshot_manager.capture_region.return_value = mock_screenshot
        
        # Should not crash
        status = self.verifier._scan_quest_log_ocr("Test Quest")
        
        self.assertFalse(status.is_completed)
        self.assertEqual(status.method, "ocr_error")
    
    def test_screenshot_failure_graceful(self):
        """Test graceful handling of screenshot failures."""
        # Mock screenshot to fail
        self.mock_screenshot_manager.capture_region.side_effect = Exception("Screenshot failed")
        
        # Should not crash
        status = self.verifier._scan_quest_log_ocr("Test Quest")
        
        self.assertFalse(status.is_completed)
        self.assertEqual(status.method, "ocr_error")


def run_tests():
    """Run all tests."""
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes using TestLoader
    loader = unittest.TestLoader()
    test_suite.addTest(loader.loadTestsFromTestCase(TestQuestVerifier))
    test_suite.addTest(loader.loadTestsFromTestCase(TestQuestVerifierIntegration))
    test_suite.addTest(loader.loadTestsFromTestCase(TestQuestVerifierPerformance))
    test_suite.addTest(loader.loadTestsFromTestCase(TestQuestVerifierErrorHandling))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 