#!/usr/bin/env python3
"""Test suite for Batch 043 - NPC Quest Signal + Smart Detection Logic.

This test suite validates all aspects of the NPC detection module including:
- Quest icon detection using OCR and computer vision
- NPC name scanning and extraction
- NPC-quest matching with multiple strategies
- Smart quest acquisition logic
- Unmatched NPC logging for future training
"""

import unittest
import tempfile
import json
import yaml
import time
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

# Import the modules to test
from modules.npc_detection import (
    QuestIconDetector, detect_quest_icons, scan_npc_names,
    NPCMatcher, match_npc_to_quests, get_available_quests,
    QuestAcquisition, trigger_quest_acquisition, log_unmatched_npc,
    SmartDetection, detect_quest_npcs, process_npc_signals
)


class TestQuestIconDetector(unittest.TestCase):
    """Test quest icon detection functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = QuestIconDetector()
        
        # Mock quest icons for testing
        self.mock_quest_icons = [
            {
                'x': 500, 'y': 200, 'width': 25, 'height': 25,
                'confidence': 0.85, 'icon_type': 'quest'
            },
            {
                'x': 800, 'y': 300, 'width': 20, 'height': 20,
                'confidence': 0.92, 'icon_type': 'repeatable'
            }
        ]
    
    def test_quest_icon_detector_initialization(self):
        """Test quest icon detector initialization."""
        self.assertIsNotNone(self.detector)
        self.assertIsInstance(self.detector.quest_icons, dict)
        self.assertIn('quest', self.detector.quest_icons)
        self.assertIn('repeatable', self.detector.quest_icons)
        self.assertIn('daily', self.detector.quest_icons)
    
    def test_detection_regions(self):
        """Test detection regions configuration."""
        regions = self.detector.get_detection_regions()
        self.assertIsInstance(regions, list)
        self.assertGreater(len(regions), 0)
        
        for region in regions:
            self.assertIsInstance(region, tuple)
            self.assertEqual(len(region), 4)  # x, y, width, height
    
    @patch('modules.npc_detection.quest_icon_detector.capture_screen')
    @patch('modules.npc_detection.quest_icon_detector.cv2')
    @patch('modules.npc_detection.quest_icon_detector.np')
    def test_detect_quest_icons_success(self, mock_np, mock_cv2, mock_capture):
        """Test successful quest icon detection."""
        # Mock screen capture
        mock_screenshot = Mock()
        mock_capture.return_value = mock_screenshot
        
        # Mock OpenCV operations
        mock_cv2.cvtColor.return_value = Mock()
        mock_cv2.findContours.return_value = ([Mock()], None)
        mock_cv2.boundingRect.return_value = (500, 200, 25, 25)
        mock_cv2.contourArea.return_value = 625  # 25 * 25
        
        # Mock numpy
        mock_np.array.return_value = Mock()
        mock_np.cvtColor.return_value = Mock()
        mock_np.inRange.return_value = Mock()
        
        icons = self.detector.detect_quest_icons()
        
        self.assertIsInstance(icons, list)
        mock_capture.assert_called_once()
    
    @patch('modules.npc_detection.quest_icon_detector.capture_screen')
    def test_detect_quest_icons_failure(self, mock_capture):
        """Test quest icon detection failure."""
        mock_capture.return_value = None
        
        icons = self.detector.detect_quest_icons()
        
        self.assertEqual(icons, [])
    
    def test_clean_npc_name_valid(self):
        """Test NPC name cleaning with valid input."""
        test_cases = [
            ("Mos Eisley Merchant", "Mos Eisley Merchant"),
            ("  Coronet Security  ", "Coronet Security"),
            ("Theed\nPalace\rGuard", "Theed Palace Guard"),
            ("Anchorhead|Mechanic", "Anchorhead Mechanic"),
            ("Bestine-Mayor", "Bestine Mayor")
        ]
        
        for input_name, expected in test_cases:
            result = self.detector._clean_npc_name(input_name)
            self.assertEqual(result, expected)
    
    def test_clean_npc_name_invalid(self):
        """Test NPC name cleaning with invalid input."""
        invalid_names = [
            "",  # Empty
            "   ",  # Whitespace only
            "A",  # Too short
            "A" * 60,  # Too long
            "123456789",  # No letters
            "!@#$%^&*()",  # No letters
            "123ABC456",  # Mixed but mostly numbers
        ]
        
        for name in invalid_names:
            result = self.detector._clean_npc_name(name)
            self.assertIsNone(result)
    
    @patch('modules.npc_detection.quest_icon_detector.capture_screen')
    @patch('modules.npc_detection.quest_icon_detector.run_ocr')
    def test_scan_npc_names_success(self, mock_ocr, mock_capture):
        """Test successful NPC name scanning."""
        # Mock screen capture
        mock_screenshot = Mock()
        mock_capture.return_value = mock_screenshot
        
        # Mock OCR
        mock_ocr.return_value = "Mos Eisley Merchant"
        
        # Create mock quest icons
        mock_icons = []
        for icon_data in self.mock_quest_icons:
            icon = Mock()
            icon.x = icon_data['x']
            icon.y = icon_data['y']
            icon.width = icon_data['width']
            icon.height = icon_data['height']
            icon.confidence = icon_data['confidence']
            icon.icon_type = icon_data['icon_type']
            mock_icons.append(icon)
        
        detections = self.detector.scan_npc_names(mock_icons)
        
        self.assertIsInstance(detections, list)
        self.assertEqual(len(detections), len(mock_icons))
        
        for detection in detections:
            self.assertIsNotNone(detection.name)
            self.assertIsInstance(detection.coordinates, tuple)
            self.assertIsInstance(detection.confidence, float)
    
    @patch('modules.npc_detection.quest_icon_detector.capture_screen')
    def test_scan_npc_names_failure(self, mock_capture):
        """Test NPC name scanning failure."""
        mock_capture.return_value = None
        
        detections = self.detector.scan_npc_names([])
        
        self.assertEqual(detections, [])


class TestNPCMatcher(unittest.TestCase):
    """Test NPC-quest matching functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.matcher = NPCMatcher()
        
        # Mock quest database
        self.mock_quest_database = {
            'quest_1': {
                'quest_id': 'quest_1',
                'name': 'Tatooine Artifact Hunt',
                'npc': 'mos eisley merchant',
                'planet': 'tatooine',
                'quest_type': 'legacy',
                'level_requirement': 15
            },
            'quest_2': {
                'quest_id': 'quest_2',
                'name': 'Coronet Security Patrol',
                'npc': 'coronet security',
                'planet': 'corellia',
                'quest_type': 'legacy',
                'level_requirement': 20
            },
            'quest_3': {
                'quest_id': 'quest_3',
                'name': 'Theed Palace Guard Duty',
                'npc': 'theed palace guard',
                'planet': 'naboo',
                'quest_type': 'legacy',
                'level_requirement': 25
            }
        }
        
        # Mock quest index
        self.mock_quest_index = {
            'tatooine': [
                {
                    'quest_id': 'quest_1',
                    'name': 'Tatooine Artifact Hunt',
                    'npc': 'mos eisley merchant',
                    'planet': 'tatooine'
                }
            ],
            'corellia': [
                {
                    'quest_id': 'quest_2',
                    'name': 'Coronet Security Patrol',
                    'npc': 'coronet security',
                    'planet': 'corellia'
                }
            ]
        }
    
    @patch.object(NPCMatcher, '_load_quest_database')
    @patch.object(NPCMatcher, '_load_quest_index')
    def test_npc_matcher_initialization(self, mock_load_index, mock_load_db):
        """Test NPC matcher initialization."""
        mock_load_db.return_value = self.mock_quest_database
        mock_load_index.return_value = self.mock_quest_index
        
        matcher = NPCMatcher()
        
        self.assertIsNotNone(matcher)
        self.assertEqual(len(matcher.quest_database), 3)
        self.assertEqual(len(matcher.quest_index), 2)
    
    def test_find_exact_matches(self):
        """Test exact NPC name matching."""
        self.matcher.quest_database = self.mock_quest_database
        
        matches = self.matcher._find_exact_matches('mos eisley merchant')
        
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].quest_id, 'quest_1')
        self.assertEqual(matches[0].match_confidence, 1.0)
        self.assertEqual(matches[0].match_type, 'exact')
    
    def test_find_fuzzy_matches(self):
        """Test fuzzy NPC name matching."""
        self.matcher.quest_database = self.mock_quest_database
        
        matches = self.matcher._find_fuzzy_matches('mos eisley merch')
        
        self.assertGreater(len(matches), 0)
        for match in matches:
            self.assertGreaterEqual(match.match_confidence, self.matcher.fuzzy_threshold)
            self.assertEqual(match.match_type, 'fuzzy')
    
    def test_find_partial_matches(self):
        """Test partial NPC name matching."""
        self.matcher.quest_database = self.mock_quest_database
        
        matches = self.matcher._find_partial_matches('merchant')
        
        self.assertGreater(len(matches), 0)
        for match in matches:
            self.assertGreaterEqual(match.match_confidence, self.matcher.partial_threshold)
            self.assertEqual(match.match_type, 'partial')
    
    def test_find_alias_matches(self):
        """Test alias-based NPC name matching."""
        self.matcher.quest_database = self.mock_quest_database
        
        matches = self.matcher._find_alias_matches('merchant')
        
        # Should find matches through aliases
        self.assertGreater(len(matches), 0)
        for match in matches:
            self.assertEqual(match.match_type, 'alias')
    
    def test_match_npc_to_quests_success(self):
        """Test successful NPC-quest matching."""
        self.matcher.quest_database = self.mock_quest_database
        
        # Create mock NPC detection
        class MockNPCDetection:
            def __init__(self):
                self.name = "Mos Eisley Merchant"
                self.coordinates = (500, 225)
                self.detected_time = time.time()
        
        detection = MockNPCDetection()
        result = self.matcher.match_npc_to_quests(detection)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.npc_name, "Mos Eisley Merchant")
        self.assertIsNotNone(result.best_match)
        self.assertEqual(result.best_match.quest_id, 'quest_1')
    
    def test_match_npc_to_quests_no_matches(self):
        """Test NPC-quest matching with no matches."""
        self.matcher.quest_database = self.mock_quest_database
        
        # Create mock NPC detection with no matches
        class MockNPCDetection:
            def __init__(self):
                self.name = "Unknown NPC"
                self.coordinates = (100, 100)
                self.detected_time = time.time()
        
        detection = MockNPCDetection()
        result = self.matcher.match_npc_to_quests(detection)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.npc_name, "Unknown NPC")
        self.assertIsNone(result.best_match)
        self.assertEqual(result.total_matches, 0)
    
    def test_get_available_quests(self):
        """Test getting available quests for an NPC."""
        self.matcher.quest_database = self.mock_quest_database
        self.matcher.quest_index = self.mock_quest_index
        
        quests = self.matcher.get_available_quests('mos eisley merchant', planet='tatooine')
        
        self.assertIsInstance(quests, list)
        self.assertGreater(len(quests), 0)
        
        for quest in quests:
            self.assertIn('quest_id', quest)
            self.assertIn('name', quest)
            self.assertIn('level_requirement', quest)
    
    def test_is_npc_match(self):
        """Test NPC matching logic."""
        # Test exact match
        self.assertTrue(self.matcher._is_npc_match('mos eisley merchant', 'mos eisley merchant'))
        
        # Test fuzzy match
        self.assertTrue(self.matcher._is_npc_match('mos eisley merch', 'mos eisley merchant'))
        
        # Test partial match
        self.assertTrue(self.matcher._is_npc_match('merchant', 'mos eisley merchant'))
        
        # Test no match
        self.assertFalse(self.matcher._is_npc_match('unknown npc', 'mos eisley merchant'))


class TestQuestAcquisition(unittest.TestCase):
    """Test quest acquisition functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.acquisition = QuestAcquisition()
        
        # Mock quest match
        class MockQuestMatch:
            def __init__(self):
                self.npc_name = "Mos Eisley Merchant"
                self.quest_id = "quest_1"
                self.quest_name = "Tatooine Artifact Hunt"
                self.match_confidence = 0.9
                self.quest_data = {
                    'level_requirement': 15,
                    'prerequisites': [],
                    'rewards': ['credits', 'experience'],
                    'objectives': ['Find artifact', 'Return to merchant']
                }
        
        self.mock_quest_match = MockQuestMatch()
    
    def test_quest_acquisition_initialization(self):
        """Test quest acquisition initialization."""
        self.assertIsNotNone(self.acquisition)
        self.assertIsInstance(self.acquisition.auto_threshold, float)
        self.assertIsInstance(self.acquisition.suggest_threshold, float)
        self.assertIsInstance(self.acquisition.log_threshold, float)
    
    def test_trigger_quest_acquisition_automatic(self):
        """Test automatic quest acquisition."""
        # Create mock match result with high confidence
        class MockMatchResult:
            def __init__(self, mock_quest_match):
                self.npc_name = "Mos Eisley Merchant"
                self.coordinates = (500, 225)
                self.detected_time = time.time()
                self.matches = [mock_quest_match]
                self.total_matches = 1
                self.best_match = mock_quest_match
        
        match_result = MockMatchResult(self.mock_quest_match)
        result = self.acquisition.trigger_quest_acquisition(match_result)
        
        self.assertIsInstance(result, dict)
        self.assertIn('success', result)
        self.assertIn('acquisition_type', result)
        self.assertEqual(result['acquisition_type'], 'automatic')
    
    def test_trigger_quest_acquisition_suggested(self):
        """Test suggested quest acquisition."""
        # Create mock match result with medium confidence
        class MockMatchResult:
            def __init__(self, mock_quest_match):
                self.npc_name = "Mos Eisley Merchant"
                self.coordinates = (500, 225)
                self.detected_time = time.time()
                self.matches = [mock_quest_match]
                self.total_matches = 1
                self.best_match = mock_quest_match
        
        # Lower the confidence to trigger suggested acquisition
        self.mock_quest_match.match_confidence = 0.7
        
        match_result = MockMatchResult(self.mock_quest_match)
        result = self.acquisition.trigger_quest_acquisition(match_result)
        
        self.assertEqual(result['acquisition_type'], 'suggested')
    
    def test_trigger_quest_acquisition_manual(self):
        """Test manual quest acquisition."""
        # Create mock match result with low confidence
        class MockMatchResult:
            def __init__(self, mock_quest_match):
                self.npc_name = "Mos Eisley Merchant"
                self.coordinates = (500, 225)
                self.detected_time = time.time()
                self.matches = [mock_quest_match]
                self.total_matches = 1
                self.best_match = mock_quest_match
        
        # Lower the confidence to trigger manual acquisition
        self.mock_quest_match.match_confidence = 0.5
        
        match_result = MockMatchResult(self.mock_quest_match)
        result = self.acquisition.trigger_quest_acquisition(match_result)
        
        self.assertEqual(result['acquisition_type'], 'manual')
    
    def test_trigger_quest_acquisition_no_matches(self):
        """Test quest acquisition with no matches."""
        # Create mock match result with no matches
        class MockMatchResult:
            def __init__(self):
                self.npc_name = "Unknown NPC"
                self.coordinates = (100, 100)
                self.detected_time = time.time()
                self.matches = []
                self.total_matches = 0
                self.best_match = None
        
        match_result = MockMatchResult()
        result = self.acquisition.trigger_quest_acquisition(match_result)
        
        self.assertFalse(result['success'])
        self.assertEqual(result['reason'], 'no_matches')
    
    def test_log_unmatched_npc(self):
        """Test logging unmatched NPCs."""
        # Create mock NPC detection
        class MockNPCDetection:
            def __init__(self):
                self.name = "Unknown Merchant"
                self.coordinates = (1500, 400)
                self.detected_time = time.time()
                self.quest_icon = type('MockIcon', (), {'icon_type': 'quest'})()
                self.confidence = 0.45
        
        npc_detection = MockNPCDetection()
        success = self.acquisition.log_unmatched_npc(npc_detection, planet="tatooine")
        
        self.assertTrue(success)
    
    def test_check_prerequisites(self):
        """Test prerequisite checking."""
        # Test with no prerequisites
        quest_data = {'prerequisites': []}
        result = self.acquisition._check_prerequisites(quest_data)
        self.assertTrue(result)
        
        # Test with prerequisites (should pass for now as we assume they're met)
        quest_data = {'prerequisites': ['quest_1', 'quest_2']}
        result = self.acquisition._check_prerequisites(quest_data)
        self.assertTrue(result)
    
    def test_check_level_requirement(self):
        """Test level requirement checking."""
        # Test with level requirement met
        quest_data = {'level_requirement': 15}
        result = self.acquisition._check_level_requirement(quest_data)
        self.assertTrue(result)
        
        # Test with level requirement not met
        quest_data = {'level_requirement': 100}
        result = self.acquisition._check_level_requirement(quest_data)
        self.assertFalse(result)
    
    def test_get_acquisition_stats(self):
        """Test acquisition statistics."""
        stats = self.acquisition.get_acquisition_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('stats', stats)
        self.assertIn('total_unmatched', stats)
        self.assertIn('recent_acquisitions', stats)


class TestSmartDetection(unittest.TestCase):
    """Test smart detection workflow."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = SmartDetection()
    
    def test_smart_detection_initialization(self):
        """Test smart detection initialization."""
        self.assertIsNotNone(self.detector)
        self.assertIsInstance(self.detector.scan_interval, float)
        self.assertIsInstance(self.detector.max_detections_per_scan, int)
        self.assertIsInstance(self.detector.confidence_threshold, float)
    
    @patch.object(SmartDetection, 'detect_quest_npcs')
    def test_process_npc_signals_limited_cycles(self, mock_detect):
        """Test NPC signal processing with limited cycles."""
        # Mock detection result
        class MockDetectionResult:
            def __init__(self):
                self.npc_detections = []
                self.match_results = []
                self.acquisition_results = []
                self.total_detected = 0
                self.total_matched = 0
                self.total_acquired = 0
                self.processing_time = 0.5
        
        mock_detect.return_value = MockDetectionResult()
        
        results = self.detector.process_npc_signals(continuous=False, max_cycles=3)
        
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 3)
        self.assertEqual(mock_detect.call_count, 3)
    
    def test_configure_detection(self):
        """Test detection configuration."""
        original_interval = self.detector.scan_interval
        original_max_detections = self.detector.max_detections_per_scan
        original_threshold = self.detector.confidence_threshold
        
        self.detector.configure_detection(
            scan_interval=5.0,
            max_detections=15,
            confidence_threshold=0.6
        )
        
        self.assertEqual(self.detector.scan_interval, 5.0)
        self.assertEqual(self.detector.max_detections_per_scan, 15)
        self.assertEqual(self.detector.confidence_threshold, 0.6)
        
        # Restore original values
        self.detector.scan_interval = original_interval
        self.detector.max_detections_per_scan = original_max_detections
        self.detector.confidence_threshold = original_threshold
    
    def test_reset_stats(self):
        """Test statistics reset."""
        # Set some stats
        self.detector.stats['total_scans'] = 10
        self.detector.stats['total_detections'] = 20
        
        self.detector.reset_stats()
        
        self.assertEqual(self.detector.stats['total_scans'], 0)
        self.assertEqual(self.detector.stats['total_detections'], 0)
    
    def test_get_detection_stats(self):
        """Test detection statistics retrieval."""
        stats = self.detector.get_detection_stats()
        
        self.assertIsInstance(stats, dict)
        self.assertIn('detection_stats', stats)
        self.assertIn('acquisition_stats', stats)
        self.assertIn('performance', stats)
    
    def test_calculate_rates(self):
        """Test rate calculations."""
        # Set up some test data
        self.detector.stats['total_scans'] = 10
        self.detector.stats['total_detections'] = 20
        self.detector.stats['total_matches'] = 15
        self.detector.stats['total_acquisitions'] = 10
        
        detection_rate = self.detector._calculate_detection_rate()
        match_rate = self.detector._calculate_match_rate()
        acquisition_rate = self.detector._calculate_acquisition_rate()
        
        self.assertEqual(detection_rate, 2.0)  # 20/10
        self.assertEqual(match_rate, 0.75)     # 15/20
        self.assertAlmostEqual(acquisition_rate, 0.67, places=1)  # 10/15 (approximately)


class TestIntegration(unittest.TestCase):
    """Test integration between components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.addCleanup(self._cleanup_temp_dir)
    
    def _cleanup_temp_dir(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow."""
        # This would test the complete workflow from detection to acquisition
        # For now, we'll test the integration points
        
        # Test that all components can be imported and initialized
        detector = QuestIconDetector()
        matcher = NPCMatcher()
        acquisition = QuestAcquisition()
        smart_detector = SmartDetection()
        
        self.assertIsNotNone(detector)
        self.assertIsNotNone(matcher)
        self.assertIsNotNone(acquisition)
        self.assertIsNotNone(smart_detector)
    
    def test_data_persistence(self):
        """Test data persistence functionality."""
        # Test that unmatched NPCs can be logged and retrieved
        acquisition = QuestAcquisition()
        
        # Create mock unmatched NPC
        class MockUnmatchedNPC:
            def __init__(self):
                self.name = "Test NPC"
                self.coordinates = (100, 100)
                self.detected_time = time.time()
                self.quest_icon = type('MockIcon', (), {'icon_type': 'quest'})()
                self.confidence = 0.5
        
        npc = MockUnmatchedNPC()
        success = acquisition.log_unmatched_npc(npc)
        
        self.assertTrue(success)
    
    def test_error_handling(self):
        """Test error handling across components."""
        # Test that components handle errors gracefully
        
        # Test with invalid inputs
        matcher = NPCMatcher()
        quests = matcher.get_available_quests("")
        self.assertIsInstance(quests, list)
        
        # Test with None inputs
        quests = matcher.get_available_quests(None)
        self.assertIsInstance(quests, list)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2) 