"""
Test suite for Batch 026 - Quest Availability Detection & Scanning Radius Logic

This test suite covers:
- Quest scanner initialization and configuration
- Quest detection logic
- Scanning radius functionality
- NPC name and dialogue scanning
- Quest overlay UI system
- Integration with existing quest data
"""

import json
import time
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

# Import the modules to test
try:
    from core.questing.quest_scanner import (
        QuestScanner, QuestLocation, QuestDetection, ScanningRadius,
        QuestType, QuestDifficulty, get_quest_scanner, scan_for_quests,
        get_available_quests, mark_quest_completed, get_scanning_status
    )
    from ui.overlay.quest_overlay import (
        QuestOverlay, QuestOverlayItem, OverlayConfig, OverlayPosition,
        get_quest_overlay, update_quest_overlay, show_quest_overlay,
        hide_quest_overlay, toggle_quest_overlay, get_overlay_status
    )
    QUEST_SCANNER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import quest scanner modules: {e}")
    QUEST_SCANNER_AVAILABLE = False


class TestQuestScanner(unittest.TestCase):
    """Test cases for the QuestScanner class."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not QUEST_SCANNER_AVAILABLE:
            self.skipTest("Quest scanner modules not available")
        
        # Create temporary test data
        self.test_quest_data = {
            "planets": {
                "tatooine": {
                    "quests": {
                        "test_quest_1": {
                            "name": "Test Quest 1",
                            "type": "combat",
                            "difficulty": "medium",
                            "level_requirement": 10,
                            "coordinates": [100, 200],
                            "npc": "Test NPC 1",
                            "file_path": "tatooine/test_quest_1.yaml"
                        },
                        "test_quest_2": {
                            "name": "Test Quest 2",
                            "type": "delivery",
                            "difficulty": "easy",
                            "level_requirement": 5,
                            "coordinates": [300, 400],
                            "npc": "Test NPC 2",
                            "file_path": "tatooine/test_quest_2.yaml"
                        }
                    }
                }
            }
        }
        
        # Mock the internal index file
        self.mock_internal_index = Mock()
        self.mock_internal_index.exists.return_value = True
        
        # Create scanner with mocked dependencies
        with patch('core.questing.quest_scanner.Path') as mock_path:
            mock_path.return_value = self.mock_internal_index
            with patch('builtins.open', create=True) as mock_open:
                with patch('yaml.safe_load') as mock_yaml_load:
                    mock_yaml_load.return_value = self.test_quest_data
                    self.scanner = QuestScanner()
    
    def test_scanner_initialization(self):
        """Test quest scanner initialization."""
        self.assertIsNotNone(self.scanner)
        self.assertEqual(len(self.scanner.available_quests), 2)
        self.assertEqual(self.scanner.scan_interval, 5.0)
        self.assertIsInstance(self.scanner.scanning_radius, ScanningRadius)
    
    def test_quest_location_creation(self):
        """Test quest location creation from data."""
        quest_location = self.scanner.available_quests["test_quest_1"]
        self.assertEqual(quest_location.quest_id, "test_quest_1")
        self.assertEqual(quest_location.name, "Test Quest 1")
        self.assertEqual(quest_location.planet, "tatooine")
        self.assertEqual(quest_location.coordinates, (100, 200))
        self.assertEqual(quest_location.npc_name, "Test NPC 1")
        self.assertEqual(quest_location.quest_type, QuestType.COMBAT)
        self.assertEqual(quest_location.difficulty, QuestDifficulty.MEDIUM)
        self.assertEqual(quest_location.level_requirement, 10)
    
    def test_distance_calculation(self):
        """Test distance calculation between coordinates."""
        quest_location = self.scanner.available_quests["test_quest_1"]
        distance = quest_location.distance_to((150, 250))
        expected_distance = ((150 - 100) ** 2 + (250 - 200) ** 2) ** 0.5
        self.assertAlmostEqual(distance, expected_distance, places=2)
    
    def test_scanning_radius_configuration(self):
        """Test scanning radius configuration."""
        radius = self.scanner.scanning_radius
        self.assertEqual(radius.get_radius_for_location("indoor"), 50)
        self.assertEqual(radius.get_radius_for_location("outdoor"), 150)
        self.assertEqual(radius.get_radius_for_location("terminal"), 25)
        self.assertEqual(radius.get_radius_for_location("npc"), 75)
        self.assertEqual(radius.get_radius_for_location("unknown"), 100)
    
    @patch('core.questing.quest_scanner.extract_text_from_screen')
    def test_quest_detection_with_ui_indicators(self, mock_extract_text):
        """Test quest detection with UI indicators."""
        # Mock screen text with UI indicators only (no NPC name to avoid conflict)
        mock_extract_text.return_value = "Available Quests\nQuest Terminal\nSome other text"
        
        quest_location = self.scanner.available_quests["test_quest_1"]
        current_location = (120, 220)
        
        detection = self.scanner._detect_quest_availability(quest_location, current_location)
        
        self.assertIsNotNone(detection)
        self.assertEqual(detection.quest_id, "test_quest_1")
        self.assertGreater(detection.confidence, 0.3)
        # The detection method could be ui_indicator or npc_name depending on which matches first
        self.assertIn(detection.detection_method, ["ui_indicator", "npc_name"])
        self.assertIn("Available Quests", detection.ui_indicators)
    
    @patch('core.questing.quest_scanner.extract_text_from_screen')
    def test_quest_detection_with_npc_dialogue(self, mock_extract_text):
        """Test quest detection with NPC dialogue."""
        # Mock screen text with NPC dialogue
        mock_extract_text.return_value = "I have a mission for you\nWe need your help"
        
        quest_location = self.scanner.available_quests["test_quest_1"]
        current_location = (120, 220)
        
        detection = self.scanner._detect_quest_availability(quest_location, current_location)
        
        self.assertIsNotNone(detection)
        self.assertEqual(detection.quest_id, "test_quest_1")
        self.assertGreater(detection.confidence, 0.3)
        self.assertEqual(detection.detection_method, "npc_dialogue")
        self.assertIn("I have a mission for you", detection.npc_dialogue)
    
    @patch('core.questing.quest_scanner.extract_text_from_screen')
    def test_quest_detection_with_npc_name(self, mock_extract_text):
        """Test quest detection with NPC name."""
        # Mock screen text with NPC name
        mock_extract_text.return_value = "Test NPC 1\nSome dialogue"
        
        quest_location = self.scanner.available_quests["test_quest_1"]
        current_location = (120, 220)
        
        detection = self.scanner._detect_quest_availability(quest_location, current_location)
        
        self.assertIsNotNone(detection)
        self.assertEqual(detection.quest_id, "test_quest_1")
        self.assertGreater(detection.confidence, 0.3)
        self.assertEqual(detection.detection_method, "npc_name")
    
    @patch('core.questing.quest_scanner.extract_text_from_screen')
    def test_quest_detection_with_quest_name(self, mock_extract_text):
        """Test quest detection with quest name."""
        # Mock screen text with quest name
        mock_extract_text.return_value = "Test Quest 1\nAvailable"
        
        quest_location = self.scanner.available_quests["test_quest_1"]
        current_location = (120, 220)
        
        detection = self.scanner._detect_quest_availability(quest_location, current_location)
        
        self.assertIsNotNone(detection)
        self.assertEqual(detection.quest_id, "test_quest_1")
        self.assertGreater(detection.confidence, 0.3)
        self.assertEqual(detection.detection_method, "quest_name")
    
    @patch('core.questing.quest_scanner.extract_text_from_screen')
    def test_quest_detection_low_confidence(self, mock_extract_text):
        """Test quest detection with low confidence."""
        # Mock screen text with no quest indicators
        mock_extract_text.return_value = "Random text\nNo quest indicators"
        
        quest_location = self.scanner.available_quests["test_quest_1"]
        current_location = (120, 220)
        
        detection = self.scanner._detect_quest_availability(quest_location, current_location)
        
        self.assertIsNone(detection)
    
    def test_scan_for_quests_within_radius(self):
        """Test scanning for quests within radius."""
        current_location = (120, 220)
        
        # Mock the detection method
        with patch.object(self.scanner, '_detect_quest_availability') as mock_detect:
            mock_detect.return_value = Mock(
                quest_id="test_quest_1",
                location=self.scanner.available_quests["test_quest_1"],
                detected_at=datetime.now(),
                confidence=0.8,
                detection_method="ui_indicator",
                ui_indicators=["Available Quests"],
                npc_dialogue=[]
            )
            
            detections = self.scanner.scan_for_quests(current_location, "outdoor")
            
            self.assertEqual(len(detections), 1)
            self.assertEqual(detections[0].quest_id, "test_quest_1")
    
    def test_scan_for_quests_outside_radius(self):
        """Test scanning for quests outside radius."""
        current_location = (1000, 1000)  # Far from quest locations
        
        detections = self.scanner.scan_for_quests(current_location, "outdoor")
        
        self.assertEqual(len(detections), 0)
    
    def test_scan_for_quests_completed_quest(self):
        """Test scanning excludes completed quests."""
        # Mark a quest as completed
        self.scanner.mark_quest_completed("test_quest_1")
        
        current_location = (120, 220)
        detections = self.scanner.scan_for_quests(current_location, "outdoor")
        
        # Should not detect completed quest
        self.assertEqual(len(detections), 0)
    
    @patch('core.questing.quest_scanner.extract_text_from_screen')
    def test_scan_npc_names(self, mock_extract_text):
        """Test scanning for NPC names."""
        mock_extract_text.return_value = "Test NPC 1\nMERCHANT\nGuard Captain"
        
        npc_names = self.scanner.scan_npc_names()
        
        self.assertIn("Test NPC 1", npc_names)
        self.assertIn("MERCHANT", npc_names)
        self.assertIn("Guard Captain", npc_names)
    
    @patch('core.questing.quest_scanner.extract_text_from_screen')
    def test_scan_dialogue_lines(self, mock_extract_text):
        """Test scanning for dialogue lines."""
        mock_extract_text.return_value = 'NPC says: "I have a mission for you"\n"Can you help us?"\nRandom text'
        
        dialogue_lines = self.scanner.scan_dialogue_lines()
        
        self.assertIn('NPC says: "I have a mission for you"', dialogue_lines)
        self.assertIn('"Can you help us?"', dialogue_lines)
    
    def test_get_available_quests_with_location(self):
        """Test getting available quests with location filtering."""
        current_location = (120, 220)
        available_quests = self.scanner.get_available_quests(current_location)
        
        # Should return quests within outdoor radius (150m)
        self.assertEqual(len(available_quests), 1)  # Only test_quest_1 is close enough
        self.assertEqual(available_quests[0].quest_id, "test_quest_1")
    
    def test_get_available_quests_without_location(self):
        """Test getting all available quests without location filtering."""
        available_quests = self.scanner.get_available_quests()
        
        # Should return all non-completed quests
        self.assertEqual(len(available_quests), 2)
        quest_ids = [q.quest_id for q in available_quests]
        self.assertIn("test_quest_1", quest_ids)
        self.assertIn("test_quest_2", quest_ids)
    
    def test_get_recent_detections(self):
        """Test getting recent detections."""
        # Add some mock detections
        mock_detection = Mock(
            quest_id="test_quest_1",
            detected_at=datetime.now()
        )
        self.scanner.detected_quests = [mock_detection]
        
        recent_detections = self.scanner.get_recent_detections(minutes=30)
        self.assertEqual(len(recent_detections), 1)
    
    def test_get_scanning_status(self):
        """Test getting scanning status."""
        status = self.scanner.get_scanning_status()
        
        self.assertIn("available_quests", status)
        self.assertIn("completed_quests", status)
        self.assertIn("recent_detections", status)
        self.assertIn("scanning_radius", status)
        self.assertIn("scan_interval", status)
        self.assertIn("ocr_available", status)
        
        self.assertEqual(status["available_quests"], 2)
        self.assertEqual(status["completed_quests"], 0)


class TestQuestOverlay(unittest.TestCase):
    """Test cases for the QuestOverlay class."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not QUEST_SCANNER_AVAILABLE:
            self.skipTest("Quest scanner modules not available")
        
        # Create overlay with test configuration
        config = OverlayConfig(
            position=OverlayPosition.TOP_RIGHT,
            width=300,
            height=400,
            opacity=0.9,
            auto_hide=False,  # Disable auto-hide for testing
            max_items=5
        )
        
        # Mock tkinter to avoid GUI issues in tests
        with patch('ui.overlay.quest_overlay.TKINTER_AVAILABLE', False):
            self.overlay = QuestOverlay(config)
    
    def test_overlay_initialization(self):
        """Test overlay initialization."""
        self.assertIsNotNone(self.overlay)
        self.assertEqual(self.overlay.config.position, OverlayPosition.TOP_RIGHT)
        self.assertEqual(self.overlay.config.width, 300)
        self.assertEqual(self.overlay.config.height, 400)
        self.assertEqual(self.overlay.config.opacity, 0.9)
        self.assertFalse(self.overlay.config.auto_hide)
        self.assertEqual(self.overlay.config.max_items, 5)
    
    def test_overlay_config_defaults(self):
        """Test overlay configuration defaults."""
        config = OverlayConfig()
        
        self.assertEqual(config.position, OverlayPosition.TOP_RIGHT)
        self.assertEqual(config.width, 300)
        self.assertEqual(config.height, 400)
        self.assertEqual(config.opacity, 0.9)
        self.assertTrue(config.auto_hide)
        self.assertEqual(config.auto_hide_delay, 10)
        self.assertEqual(config.max_items, 10)
        self.assertTrue(config.show_confidence)
        self.assertTrue(config.show_distance)
        self.assertEqual(config.highlight_threshold, 0.7)
    
    def test_quest_overlay_item_creation(self):
        """Test quest overlay item creation."""
        item = QuestOverlayItem(
            quest_id="test_quest",
            name="Test Quest",
            npc_name="Test NPC",
            quest_type="combat",
            difficulty="medium",
            confidence=0.8,
            distance=50.0,
            detected_at=datetime.now(),
            is_highlighted=True
        )
        
        self.assertEqual(item.quest_id, "test_quest")
        self.assertEqual(item.name, "Test Quest")
        self.assertEqual(item.npc_name, "Test NPC")
        self.assertEqual(item.quest_type, "combat")
        self.assertEqual(item.difficulty, "medium")
        self.assertEqual(item.confidence, 0.8)
        self.assertEqual(item.distance, 50.0)
        self.assertTrue(item.is_highlighted)
    
    def test_overlay_status(self):
        """Test overlay status information."""
        status = self.overlay.get_status()
        
        self.assertIn("visible", status)
        self.assertIn("items_count", status)
        self.assertIn("tkinter_available", status)
        self.assertIn("root_available", status)
        self.assertIn("last_update", status)
        self.assertIn("config", status)
        
        self.assertFalse(status["visible"])
        self.assertEqual(status["items_count"], 0)
        # Tkinter availability depends on the actual system
        self.assertIsInstance(status["tkinter_available"], bool)
        # When tkinter is not available, root_available should be False
        self.assertFalse(status["root_available"])  # No root when tkinter unavailable


class TestGlobalFunctions(unittest.TestCase):
    """Test cases for global functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not QUEST_SCANNER_AVAILABLE:
            self.skipTest("Quest scanner modules not available")
    
    def test_get_quest_scanner(self):
        """Test getting global quest scanner instance."""
        scanner = get_quest_scanner()
        self.assertIsInstance(scanner, QuestScanner)
        
        # Should return the same instance
        scanner2 = get_quest_scanner()
        self.assertIs(scanner, scanner2)
    
    def test_get_quest_overlay(self):
        """Test getting global quest overlay instance."""
        overlay = get_quest_overlay()
        self.assertIsInstance(overlay, QuestOverlay)
        
        # Should return the same instance
        overlay2 = get_quest_overlay()
        self.assertIs(overlay, overlay2)
    
    def test_scan_for_quests_global(self):
        """Test global scan_for_quests function."""
        current_location = (100, 200)
        detections = scan_for_quests(current_location, "outdoor")
        
        # Should return a list (may be empty depending on mock data)
        self.assertIsInstance(detections, list)
    
    def test_get_available_quests_global(self):
        """Test global get_available_quests function."""
        quests = get_available_quests()
        self.assertIsInstance(quests, list)
    
    def test_mark_quest_completed_global(self):
        """Test global mark_quest_completed function."""
        # This should not raise an exception
        mark_quest_completed("test_quest")
    
    def test_get_scanning_status_global(self):
        """Test global get_scanning_status function."""
        status = get_scanning_status()
        self.assertIsInstance(status, dict)
        self.assertIn("available_quests", status)
    
    def test_overlay_functions(self):
        """Test overlay global functions."""
        # These should not raise exceptions even without tkinter
        update_quest_overlay([], (100, 200))
        show_quest_overlay()
        hide_quest_overlay()
        toggle_quest_overlay()
        
        status = get_overlay_status()
        self.assertIsInstance(status, dict)


class TestIntegration(unittest.TestCase):
    """Integration tests for quest scanner system."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not QUEST_SCANNER_AVAILABLE:
            self.skipTest("Quest scanner modules not available")
    
    def test_scanner_with_overlay_integration(self):
        """Test integration between scanner and overlay."""
        scanner = get_quest_scanner()
        overlay = get_quest_overlay()
        
        # Mock quest detections
        mock_detection = Mock(
            quest_id="test_quest",
            location=Mock(
                name="Test Quest",
                npc_name="Test NPC",
                quest_type=Mock(value="combat"),
                difficulty=Mock(value="medium"),
                coordinates=(100, 200),
                distance_to=Mock(return_value=50.0)
            ),
            detected_at=datetime.now(),
            confidence=0.8
        )
        
        # Update overlay with detections
        overlay.update_quests([mock_detection], (120, 220))
        
        # Check overlay status
        status = overlay.get_status()
        self.assertEqual(status["items_count"], 1)
    
    def test_quest_index_file_structure(self):
        """Test quest index file structure."""
        quest_index_path = Path("data/quest_index.yaml")
        
        if quest_index_path.exists():
            import yaml
            with open(quest_index_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Check required sections
            self.assertIn("quest_availability", data)
            self.assertIn("scanning_config", data)
            self.assertIn("detection_patterns", data)
            self.assertIn("detection_history", data)
            self.assertIn("metadata", data)
            
            # Check scanning config
            scanning_config = data["scanning_config"]
            self.assertIn("base_radius", scanning_config)
            self.assertIn("indoor_radius", scanning_config)
            self.assertIn("outdoor_radius", scanning_config)
            self.assertIn("terminal_radius", scanning_config)
            self.assertIn("npc_radius", scanning_config)
            
            # Check detection patterns
            patterns = data["detection_patterns"]
            self.assertIn("ui_indicators", patterns)
            self.assertIn("npc_dialogue", patterns)
            self.assertIn("quest_keywords", patterns)


class TestErrorHandling(unittest.TestCase):
    """Test error handling in quest scanner system."""
    
    def setUp(self):
        """Set up test fixtures."""
        if not QUEST_SCANNER_AVAILABLE:
            self.skipTest("Quest scanner modules not available")
    
    def test_scanner_with_missing_data_file(self):
        """Test scanner behavior with missing data file."""
        with patch('pathlib.Path.exists', return_value=False):
            scanner = QuestScanner()
            # Should not raise exception
            self.assertIsNotNone(scanner)
    
    def test_scanner_with_invalid_yaml(self):
        """Test scanner behavior with invalid YAML data."""
        with patch('builtins.open', side_effect=Exception("File error")):
            scanner = QuestScanner()
            # Should not raise exception
            self.assertIsNotNone(scanner)
    
    def test_overlay_without_tkinter(self):
        """Test overlay behavior without tkinter."""
        with patch('ui.overlay.quest_overlay.TKINTER_AVAILABLE', False):
            overlay = QuestOverlay()
            # Should not raise exception
            self.assertIsNotNone(overlay)
    
    def test_ocr_unavailable_handling(self):
        """Test handling when OCR is unavailable."""
        with patch('core.questing.quest_scanner.OCR_AVAILABLE', False):
            scanner = QuestScanner()
            # Should still work with mock OCR
            self.assertIsNotNone(scanner)


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2) 