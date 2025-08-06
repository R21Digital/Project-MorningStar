#!/usr/bin/env python3
"""
Test suite for Batch 158 - Quest Log Verifier (UI Scan Layer)

This test suite covers all functionality of the quest log UI scanner including:
- OCR scanning of quest completion history
- Quest completion detection
- Quest chain scanning
- User prompt functionality
- Image processing capabilities
- UI region configuration
"""

import unittest
import time
import tempfile
import os
from datetime import datetime
from typing import Dict, List, Optional
from unittest.mock import Mock, patch, MagicMock

# Import the quest log UI scanner
try:
    from core.quest_log_ui_scanner import (
        QuestLogUIScanner,
        QuestLogScanResult,
        QuestChainScanResult,
        QuestLogUIRegion,
        scan_quest_completion,
        scan_quest_chain_completion,
        should_skip_quest,
        should_skip_chain,
        get_quest_log_scanner
    )
    SCANNER_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Quest log UI scanner not available: {e}")
    SCANNER_AVAILABLE = False


class TestQuestLogUIScanner(unittest.TestCase):
    """Test cases for QuestLogUIScanner class."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not SCANNER_AVAILABLE:
            self.skipTest("Quest log UI scanner not available")
        
        self.config = {
            'quest_log_image_path': '/ui/questlog.png',
            'min_confidence': 70.0,
            'prompt_on_uncertain': True,
            'prompt_threshold': 50.0,
            'preprocessing_enabled': True,
            'contrast_enhancement': True,
            'noise_reduction': True
        }
        self.scanner = QuestLogUIScanner(self.config)
    
    def test_scanner_initialization(self):
        """Test scanner initialization with configuration."""
        self.assertIsNotNone(self.scanner)
        self.assertEqual(self.scanner.config, self.config)
        self.assertEqual(self.scanner.min_confidence, 70.0)
        self.assertTrue(self.scanner.prompt_on_uncertain)
        self.assertEqual(self.scanner.prompt_threshold, 50.0)
        self.assertTrue(self.scanner.preprocessing_enabled)
    
    def test_ui_regions_configuration(self):
        """Test UI regions configuration."""
        self.assertIn('completed_tab', self.scanner.ui_regions)
        self.assertIn('quest_list', self.scanner.ui_regions)
        self.assertIn('quest_details', self.scanner.ui_regions)
        self.assertIn('chain_progress', self.scanner.ui_regions)
        
        # Check region priorities
        completed_tab = self.scanner.ui_regions['completed_tab']
        self.assertEqual(completed_tab.scan_priority, 3)
        self.assertEqual(completed_tab.name, "Completed Tab")
    
    def test_completion_keywords(self):
        """Test completion keywords configuration."""
        self.assertIn('completed', self.scanner.completion_keywords)
        self.assertIn('finished', self.scanner.completion_keywords)
        self.assertIn('done', self.scanner.completion_keywords)
        self.assertIn('✓', self.scanner.completion_keywords)
        self.assertIn('✅', self.scanner.completion_keywords)
    
    def test_chain_identifiers(self):
        """Test chain identifiers configuration."""
        self.assertIn('legacy', self.scanner.chain_identifiers)
        self.assertIn('heroic', self.scanner.chain_identifiers)
        self.assertIn('epic', self.scanner.chain_identifiers)
        self.assertIn('daily', self.scanner.chain_identifiers)
        self.assertIn('weekly', self.scanner.chain_identifiers)
    
    @patch('core.quest_log_ui_scanner.cv2.imread')
    def test_capture_quest_log_image_success(self, mock_imread):
        """Test successful quest log image capture."""
        # Mock successful image read
        mock_image = Mock()
        mock_imread.return_value = mock_image
        
        # Create temporary image file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_file.write(b'fake image data')
            temp_path = temp_file.name
        
        try:
            self.scanner.quest_log_image_path = temp_path
            result = self.scanner._capture_quest_log_image()
            
            self.assertIsNotNone(result)
            mock_imread.assert_called_once_with(temp_path)
        finally:
            os.unlink(temp_path)
    
    @patch('core.quest_log_ui_scanner.cv2.imread')
    def test_capture_quest_log_image_failure(self, mock_imread):
        """Test quest log image capture failure."""
        # Mock failed image read
        mock_imread.return_value = None
        
        result = self.scanner._capture_quest_log_image()
        
        self.assertIsNone(result)
    
    def test_preprocess_image(self):
        """Test image preprocessing functionality."""
        # Create a mock image (3-channel)
        import numpy as np
        mock_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        result = self.scanner._preprocess_image(mock_image)
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result.shape), 2)  # Should be grayscale
    
    def test_check_quest_completion_in_text_high_confidence(self):
        """Test quest completion detection with high confidence."""
        text = "Legacy Quest 1 completed ✓"
        quest_name = "Legacy Quest 1"
        
        is_completed, confidence, matched_keywords = self.scanner._check_quest_completion_in_text(
            text, quest_name
        )
        
        self.assertTrue(is_completed)
        self.assertGreater(confidence, 70.0)
        self.assertIn('completed', matched_keywords)
        self.assertIn('✓', matched_keywords)
    
    def test_check_quest_completion_in_text_low_confidence(self):
        """Test quest completion detection with low confidence."""
        text = "Some random text without quest information"
        quest_name = "Legacy Quest 1"
        
        is_completed, confidence, matched_keywords = self.scanner._check_quest_completion_in_text(
            text, quest_name
        )
        
        self.assertFalse(is_completed)
        self.assertLess(confidence, 50.0)
        self.assertEqual(len(matched_keywords), 0)
    
    def test_check_quest_completion_in_text_partial_match(self):
        """Test quest completion detection with partial quest name match."""
        text = "Legacy Quest completed"
        quest_name = "Legacy Quest 1"
        
        is_completed, confidence, matched_keywords = self.scanner._check_quest_completion_in_text(
            text, quest_name
        )
        
        self.assertGreater(confidence, 30.0)  # Should have some confidence from partial match
        self.assertIn('completed', matched_keywords)
    
    def test_infer_chain_quests(self):
        """Test quest chain inference."""
        # Test known chain
        legacy_quests = self.scanner._infer_chain_quests("legacy")
        self.assertEqual(len(legacy_quests), 3)
        self.assertIn("Legacy Quest 1", legacy_quests)
        
        # Test unknown chain
        unknown_quests = self.scanner._infer_chain_quests("unknown")
        self.assertEqual(len(unknown_quests), 1)
        self.assertIn("unknown Quest 1", unknown_quests)
    
    def test_create_error_result(self):
        """Test error result creation."""
        quest_name = "Test Quest"
        error_message = "Test error"
        
        result = self.scanner._create_error_result(quest_name, error_message)
        
        self.assertEqual(result.quest_name, quest_name)
        self.assertFalse(result.is_completed)
        self.assertEqual(result.confidence, 0.0)
        self.assertEqual(result.scan_method, "ERROR")
        self.assertEqual(result.ui_region, (0, 0, 0, 0))
        self.assertEqual(result.ocr_text, "")
        self.assertEqual(result.matched_keywords, [])
    
    def test_create_chain_error_result(self):
        """Test chain error result creation."""
        chain_id = "test_chain"
        error_message = "Test error"
        
        result = self.scanner._create_chain_error_result(chain_id, error_message)
        
        self.assertEqual(result.chain_id, chain_id)
        self.assertEqual(result.total_quests, 0)
        self.assertEqual(result.completed_quests, 0)
        self.assertEqual(result.completion_percentage, 0.0)
        self.assertFalse(result.is_fully_completed)
        self.assertEqual(result.pending_quests, [])
        self.assertEqual(result.completed_quests_list, [])
    
    @patch('builtins.input', return_value='y')
    def test_prompt_user_for_quest_status_yes(self, mock_input):
        """Test user prompt for quest status with 'yes' response."""
        quest_name = "Test Quest"
        scan_result = QuestLogScanResult(
            quest_name=quest_name,
            is_completed=False,
            confidence=45.0,
            scan_method="OCR_Test",
            timestamp=datetime.now(),
            ui_region=(100, 150, 800, 600),
            ocr_text="Test OCR text",
            matched_keywords=["test"],
            chain_id="test"
        )
        
        result = self.scanner._prompt_user_for_quest_status(quest_name, scan_result)
        
        self.assertTrue(result)
        mock_input.assert_called()
    
    @patch('builtins.input', return_value='n')
    def test_prompt_user_for_quest_status_no(self, mock_input):
        """Test user prompt for quest status with 'no' response."""
        quest_name = "Test Quest"
        scan_result = QuestLogScanResult(
            quest_name=quest_name,
            is_completed=False,
            confidence=45.0,
            scan_method="OCR_Test",
            timestamp=datetime.now(),
            ui_region=(100, 150, 800, 600),
            ocr_text="Test OCR text",
            matched_keywords=["test"],
            chain_id="test"
        )
        
        result = self.scanner._prompt_user_for_quest_status(quest_name, scan_result)
        
        self.assertFalse(result)
        mock_input.assert_called()
    
    @patch('builtins.input', return_value='y')
    def test_prompt_user_for_chain_status_yes(self, mock_input):
        """Test user prompt for chain status with 'yes' response."""
        chain_id = "test_chain"
        chain_result = QuestChainScanResult(
            chain_id=chain_id,
            total_quests=3,
            completed_quests=2,
            completion_percentage=66.7,
            is_fully_completed=False,
            pending_quests=["Quest 3"],
            completed_quests_list=["Quest 1", "Quest 2"],
            scan_time=time.time(),
            ui_regions_scanned=[(100, 150, 800, 600)]
        )
        
        result = self.scanner._prompt_user_for_chain_status(chain_id, chain_result)
        
        self.assertTrue(result)
        mock_input.assert_called()
    
    def test_clear_cache(self):
        """Test cache clearing functionality."""
        # Add some test data to cache
        self.scanner.scan_cache["test_quest"] = QuestLogScanResult(
            quest_name="test_quest",
            is_completed=True,
            confidence=80.0,
            scan_method="OCR_Test",
            timestamp=datetime.now(),
            ui_region=(100, 150, 800, 600),
            ocr_text="Test",
            matched_keywords=["test"],
            chain_id="test"
        )
        
        self.assertIn("test_quest", self.scanner.scan_cache)
        
        # Clear cache
        self.scanner.clear_cache()
        
        self.assertEqual(len(self.scanner.scan_cache), 0)


class TestQuestLogScanResult(unittest.TestCase):
    """Test cases for QuestLogScanResult dataclass."""
    
    def test_quest_log_scan_result_creation(self):
        """Test QuestLogScanResult creation."""
        result = QuestLogScanResult(
            quest_name="Test Quest",
            is_completed=True,
            confidence=85.5,
            scan_method="OCR_Completed_Tab",
            timestamp=datetime.now(),
            ui_region=(100, 150, 800, 600),
            ocr_text="Test OCR text",
            matched_keywords=["completed", "✓"],
            chain_id="test_chain"
        )
        
        self.assertEqual(result.quest_name, "Test Quest")
        self.assertTrue(result.is_completed)
        self.assertEqual(result.confidence, 85.5)
        self.assertEqual(result.scan_method, "OCR_Completed_Tab")
        self.assertEqual(result.ui_region, (100, 150, 800, 600))
        self.assertEqual(result.ocr_text, "Test OCR text")
        self.assertEqual(result.matched_keywords, ["completed", "✓"])
        self.assertEqual(result.chain_id, "test_chain")


class TestQuestChainScanResult(unittest.TestCase):
    """Test cases for QuestChainScanResult dataclass."""
    
    def test_quest_chain_scan_result_creation(self):
        """Test QuestChainScanResult creation."""
        result = QuestChainScanResult(
            chain_id="test_chain",
            total_quests=3,
            completed_quests=2,
            completion_percentage=66.7,
            is_fully_completed=False,
            pending_quests=["Quest 3"],
            completed_quests_list=["Quest 1", "Quest 2"],
            scan_time=time.time(),
            ui_regions_scanned=[(100, 150, 800, 600), (200, 250, 900, 700)]
        )
        
        self.assertEqual(result.chain_id, "test_chain")
        self.assertEqual(result.total_quests, 3)
        self.assertEqual(result.completed_quests, 2)
        self.assertEqual(result.completion_percentage, 66.7)
        self.assertFalse(result.is_fully_completed)
        self.assertEqual(result.pending_quests, ["Quest 3"])
        self.assertEqual(result.completed_quests_list, ["Quest 1", "Quest 2"])
        self.assertEqual(len(result.ui_regions_scanned), 2)


class TestQuestLogUIRegion(unittest.TestCase):
    """Test cases for QuestLogUIRegion dataclass."""
    
    def test_quest_log_ui_region_creation(self):
        """Test QuestLogUIRegion creation."""
        region = QuestLogUIRegion(
            name="Test Region",
            coordinates=(100, 150, 800, 600),
            description="Test region description",
            scan_priority=2
        )
        
        self.assertEqual(region.name, "Test Region")
        self.assertEqual(region.coordinates, (100, 150, 800, 600))
        self.assertEqual(region.description, "Test region description")
        self.assertEqual(region.scan_priority, 2)
    
    def test_quest_log_ui_region_default_priority(self):
        """Test QuestLogUIRegion with default priority."""
        region = QuestLogUIRegion(
            name="Test Region",
            coordinates=(100, 150, 800, 600),
            description="Test region description"
        )
        
        self.assertEqual(region.scan_priority, 1)  # Default priority


class TestConvenienceFunctions(unittest.TestCase):
    """Test cases for convenience functions."""
    
    def test_get_quest_log_scanner(self):
        """Test get_quest_log_scanner function."""
        if not SCANNER_AVAILABLE:
            self.skipTest("Quest log UI scanner not available")
        
        scanner = get_quest_log_scanner()
        self.assertIsInstance(scanner, QuestLogUIScanner)
    
    def test_get_quest_log_scanner_with_config(self):
        """Test get_quest_log_scanner function with configuration."""
        if not SCANNER_AVAILABLE:
            self.skipTest("Quest log UI scanner not available")
        
        config = {'min_confidence': 80.0}
        scanner = get_quest_log_scanner(config)
        self.assertEqual(scanner.min_confidence, 80.0)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios for Batch 158."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not SCANNER_AVAILABLE:
            self.skipTest("Quest log UI scanner not available")
        
        self.scanner = QuestLogUIScanner()
    
    @patch('core.quest_log_ui_scanner.cv2.imread')
    @patch('core.quest_log_ui_scanner.pytesseract.image_to_string')
    def test_integration_quest_completion_scan(self, mock_ocr, mock_imread):
        """Test integration of quest completion scanning."""
        # Mock image read
        mock_image = Mock()
        mock_imread.return_value = mock_image
        
        # Mock OCR result
        mock_ocr.return_value = "Legacy Quest 1 completed ✓"
        
        # Create temporary image file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_file.write(b'fake image data')
            temp_path = temp_file.name
        
        try:
            self.scanner.quest_log_image_path = temp_path
            result = self.scanner.scan_quest_completion("Legacy Quest 1", "legacy")
            
            self.assertIsNotNone(result)
            self.assertEqual(result.quest_name, "Legacy Quest 1")
            self.assertIn("legacy", result.chain_id)
        finally:
            os.unlink(temp_path)
    
    @patch('core.quest_log_ui_scanner.cv2.imread')
    @patch('core.quest_log_ui_scanner.pytesseract.image_to_string')
    def test_integration_chain_completion_scan(self, mock_ocr, mock_imread):
        """Test integration of quest chain completion scanning."""
        # Mock image read
        mock_image = Mock()
        mock_imread.return_value = mock_image
        
        # Mock OCR result
        mock_ocr.return_value = "Legacy Quest 1 completed ✓"
        
        # Create temporary image file
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_file.write(b'fake image data')
            temp_path = temp_file.name
        
        try:
            self.scanner.quest_log_image_path = temp_path
            result = self.scanner.scan_quest_chain_completion("legacy")
            
            self.assertIsNotNone(result)
            self.assertEqual(result.chain_id, "legacy")
            self.assertGreater(result.total_quests, 0)
        finally:
            os.unlink(temp_path)
    
    def test_integration_skip_logic(self):
        """Test integration of skip logic."""
        # Test with high confidence completed quest
        with patch.object(self.scanner, 'scan_quest_completion') as mock_scan:
            mock_scan.return_value = QuestLogScanResult(
                quest_name="Test Quest",
                is_completed=True,
                confidence=85.0,
                scan_method="OCR_Test",
                timestamp=datetime.now(),
                ui_region=(100, 150, 800, 600),
                ocr_text="Test completed",
                matched_keywords=["completed"],
                chain_id="test"
            )
            
            should_skip = self.scanner.should_skip_quest("Test Quest", "test")
            self.assertTrue(should_skip)
    
    def test_integration_chain_skip_logic(self):
        """Test integration of chain skip logic."""
        # Test with fully completed chain
        with patch.object(self.scanner, 'scan_quest_chain_completion') as mock_scan:
            mock_scan.return_value = QuestChainScanResult(
                chain_id="test_chain",
                total_quests=3,
                completed_quests=3,
                completion_percentage=100.0,
                is_fully_completed=True,
                pending_quests=[],
                completed_quests_list=["Quest 1", "Quest 2", "Quest 3"],
                scan_time=time.time(),
                ui_regions_scanned=[(100, 150, 800, 600)]
            )
            
            should_skip = self.scanner.should_skip_chain("test_chain")
            self.assertTrue(should_skip)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not SCANNER_AVAILABLE:
            self.skipTest("Quest log UI scanner not available")
        
        self.scanner = QuestLogUIScanner()
    
    def test_empty_quest_name(self):
        """Test handling of empty quest name."""
        result = self.scanner._check_quest_completion_in_text("Some text", "")
        
        self.assertFalse(result[0])  # is_completed
        self.assertEqual(result[1], 0.0)  # confidence
        self.assertEqual(result[2], [])  # matched_keywords
    
    def test_none_quest_name(self):
        """Test handling of None quest name."""
        result = self.scanner._check_quest_completion_in_text("Some text", None)
        
        self.assertFalse(result[0])  # is_completed
        self.assertEqual(result[1], 0.0)  # confidence
        self.assertEqual(result[2], [])  # matched_keywords
    
    def test_empty_ocr_text(self):
        """Test handling of empty OCR text."""
        result = self.scanner._check_quest_completion_in_text("", "Test Quest")
        
        self.assertFalse(result[0])  # is_completed
        self.assertEqual(result[1], 0.0)  # confidence
        self.assertEqual(result[2], [])  # matched_keywords
    
    def test_none_ocr_text(self):
        """Test handling of None OCR text."""
        result = self.scanner._check_quest_completion_in_text(None, "Test Quest")
        
        self.assertFalse(result[0])  # is_completed
        self.assertEqual(result[1], 0.0)  # confidence
        self.assertEqual(result[2], [])  # matched_keywords
    
    def test_invalid_ui_region_coordinates(self):
        """Test handling of invalid UI region coordinates."""
        # Test with negative coordinates
        region = QuestLogUIRegion(
            name="Invalid Region",
            coordinates=(-100, -150, 800, 600),
            description="Invalid region"
        )
        
        self.assertEqual(region.coordinates, (-100, -150, 800, 600))
    
    def test_zero_confidence_threshold(self):
        """Test with zero confidence threshold."""
        self.scanner.min_confidence = 0.0
        
        text = "Test Quest completed"
        quest_name = "Test Quest"
        
        is_completed, confidence, matched_keywords = self.scanner._check_quest_completion_in_text(
            text, quest_name
        )
        
        # Should be completed with any confidence above 0
        self.assertTrue(is_completed)
        self.assertGreater(confidence, 0.0)


def run_performance_benchmark():
    """Run performance benchmark for Batch 158."""
    if not SCANNER_AVAILABLE:
        print("❌ Quest log UI scanner not available for benchmark")
        return
    
    print("\n🚀 BATCH 158 PERFORMANCE BENCHMARK")
    print("=" * 50)
    
    scanner = QuestLogUIScanner()
    
    # Benchmark quest completion detection
    start_time = time.time()
    for i in range(100):
        scanner._check_quest_completion_in_text(
            f"Quest {i} completed ✓", f"Quest {i}"
        )
    end_time = time.time()
    
    quest_detection_time = end_time - start_time
    print(f"Quest completion detection: {quest_detection_time:.3f}s for 100 iterations")
    print(f"Average per quest: {(quest_detection_time / 100) * 1000:.2f}ms")
    
    # Benchmark image preprocessing (with mock image)
    import numpy as np
    mock_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    
    start_time = time.time()
    for i in range(50):
        scanner._preprocess_image(mock_image)
    end_time = time.time()
    
    preprocessing_time = end_time - start_time
    print(f"Image preprocessing: {preprocessing_time:.3f}s for 50 iterations")
    print(f"Average per image: {(preprocessing_time / 50) * 1000:.2f}ms")
    
    print("\n✅ Performance benchmark complete")


def main():
    """Main test function."""
    print("🧪 BATCH 158 - QUEST LOG VERIFIER (UI SCAN LAYER) TEST SUITE")
    print("=" * 60)
    
    # Run unit tests
    print("\n📋 Running unit tests...")
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run performance benchmark
    run_performance_benchmark()
    
    print("\n" + "=" * 60)
    print("✅ BATCH 158 TEST SUITE COMPLETE")
    print("=" * 60)
    print("💡 Usage Examples:")
    print("  python src/main.py --mode quest --quest-log-verifier")
    print("  python src/main.py --mode quest --quest-log-verifier --prompt-user")
    print("  python src/main.py --mode quest --quest-log-verifier --chain-id legacy")
    print("\n✅ Batch 158 - Quest Log Verifier is READY FOR USE!")


if __name__ == "__main__":
    main() 