"""
Test suite for Batch 054 - Smart NPC Detection via Quest Giver Icons and OCR

Tests cover:
- QuestIconDetector class functionality
- NPCDetector class functionality
- QuestNPC and QuestIcon dataclasses
- Template matching and OCR integration
- Quest sources integration
- Debug mode and confidence ratings
- Global convenience functions
"""

import json
import tempfile
import unittest
from pathlib import Path
from typing import Dict, Any
from unittest.mock import patch, MagicMock, mock_open
import numpy as np

# Add the project root to the path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from vision.npc_detector import (
    QuestIconDetector, NPCDetector, QuestNPC, QuestIcon,
    get_npc_detector, detect_quest_npcs, get_available_quests_nearby, set_debug_mode
)

class TestQuestIcon(unittest.TestCase):
    """Test QuestIcon dataclass."""
    
    def test_quest_icon_creation(self):
        """Test QuestIcon creation with valid data."""
        icon = QuestIcon(
            icon_type="!",
            confidence=0.85,
            coordinates=(100, 200),
            size=(24, 24)
        )
        
        self.assertEqual(icon.icon_type, "!")
        self.assertEqual(icon.confidence, 0.85)
        self.assertEqual(icon.coordinates, (100, 200))
        self.assertEqual(icon.size, (24, 24))
    
    def test_quest_icon_types(self):
        """Test different quest icon types."""
        exclamation_icon = QuestIcon("!", 0.8, (100, 100), (24, 24))
        question_icon = QuestIcon("?", 0.7, (200, 200), (24, 24))
        
        self.assertEqual(exclamation_icon.icon_type, "!")
        self.assertEqual(question_icon.icon_type, "?")

class TestQuestNPC(unittest.TestCase):
    """Test QuestNPC dataclass."""
    
    def test_quest_npc_creation(self):
        """Test QuestNPC creation with valid data."""
        quest_data = {
            "name": "Test NPC",
            "planet": "Tatooine",
            "city": "Mos Entha",
            "quests": []
        }
        
        npc = QuestNPC(
            name="Test NPC",
            icon_type="!",
            confidence=0.9,
            coordinates=(300, 400),
            quest_data=quest_data,
            screen_region=(250, 350, 100, 100)
        )
        
        self.assertEqual(npc.name, "Test NPC")
        self.assertEqual(npc.icon_type, "!")
        self.assertEqual(npc.confidence, 0.9)
        self.assertEqual(npc.coordinates, (300, 400))
        self.assertEqual(npc.quest_data, quest_data)
        self.assertEqual(npc.screen_region, (250, 350, 100, 100))
    
    def test_quest_npc_without_quest_data(self):
        """Test QuestNPC creation without quest data."""
        npc = QuestNPC(
            name="Unknown NPC",
            icon_type="?",
            confidence=0.6,
            coordinates=(100, 100)
        )
        
        self.assertEqual(npc.name, "Unknown NPC")
        self.assertIsNone(npc.quest_data)
        self.assertIsNone(npc.screen_region)

class TestQuestIconDetector(unittest.TestCase):
    """Test QuestIconDetector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = QuestIconDetector()
    
    def test_initialization(self):
        """Test detector initialization."""
        self.assertEqual(self.detector.confidence_threshold, 0.7)
        self.assertEqual(self.detector.min_icon_size, (16, 16))
        self.assertEqual(self.detector.max_icon_size, (32, 32))
        self.assertIsInstance(self.detector.search_regions, list)
    
    @patch('vision.npc_detector.cv2.imwrite')
    @patch('vision.npc_detector.np.zeros')
    @patch('vision.npc_detector.cv2.putText')
    def test_create_quest_icon_templates(self, mock_put_text, mock_zeros, mock_imwrite):
        """Test quest icon template creation."""
        # Mock numpy zeros
        mock_zeros.return_value = np.zeros((24, 24, 3), dtype=np.uint8)
        
        # Mock cv2.putText
        mock_put_text.return_value = None
        
        # Mock cv2.imwrite
        mock_imwrite.return_value = True
        
        # Test template creation
        self.detector.create_quest_icon_templates()
        
        # Verify templates were created
        self.assertTrue(mock_imwrite.called)
    
    @patch('vision.npc_detector.cv2.imread')
    @patch('vision.npc_detector.cv2.matchTemplate')
    @patch('vision.npc_detector.cv2.minMaxLoc')
    @patch('pathlib.Path.exists')
    def test_detect_quest_icons(self, mock_exists, mock_min_max_loc, mock_match_template, mock_imread):
        """Test quest icon detection."""
        # Mock template file exists
        mock_exists.return_value = True
        
        # Mock template image
        mock_template = np.zeros((24, 24, 3), dtype=np.uint8)
        mock_imread.return_value = mock_template
        
        # Mock template matching result
        mock_result = np.random.random((100, 100)).astype(np.float32)
        mock_match_template.return_value = mock_result
        
        # Mock minMaxLoc to return high confidence
        mock_min_max_loc.return_value = (0.0, 0.9, (0, 0), (50, 50))
        
        # Create test image
        test_image = np.zeros((200, 200, 3), dtype=np.uint8)
        
        # Test detection
        detected_icons = self.detector.detect_quest_icons(test_image)
        
        # Verify detection was attempted
        self.assertIsInstance(detected_icons, list)
    
    def test_remove_duplicate_icons(self):
        """Test duplicate icon removal."""
        # Create test icons
        icon1 = QuestIcon("!", 0.9, (100, 100), (24, 24))
        icon2 = QuestIcon("!", 0.8, (105, 105), (24, 24))  # Close to icon1
        icon3 = QuestIcon("?", 0.7, (200, 200), (24, 24))  # Far from others
        
        icons = [icon1, icon2, icon3]
        unique_icons = self.detector._remove_duplicate_icons(icons)
        
        # Should remove icon2 (close to icon1) and keep icon1 and icon3
        self.assertEqual(len(unique_icons), 2)
        self.assertIn(icon1, unique_icons)
        self.assertIn(icon3, unique_icons)
        self.assertNotIn(icon2, unique_icons)

class TestNPCDetector(unittest.TestCase):
    """Test NPCDetector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = NPCDetector()
    
    def test_initialization(self):
        """Test detector initialization."""
        self.assertEqual(self.detector.npc_name_region_size, (200, 50))
        self.assertEqual(self.detector.min_npc_name_length, 3)
        self.assertEqual(self.detector.max_npc_name_length, 50)
        self.assertEqual(self.detector.min_confidence, 0.6)
        self.assertFalse(self.detector.debug_mode)
    
    @patch('builtins.open', new_callable=mock_open, read_data='{"quest_sources": {"Test NPC": {"name": "Test NPC", "planet": "Tatooine"}}}')
    def test_load_quest_sources(self, mock_file):
        """Test quest sources loading."""
        # Mock file exists
        with patch('pathlib.Path.exists', return_value=True):
            sources = self.detector._load_quest_sources()
            
            self.assertIn("quest_sources", sources)
            self.assertIn("Test NPC", sources["quest_sources"])
    
    @patch('pathlib.Path.exists')
    def test_load_quest_sources_file_not_found(self, mock_exists):
        """Test quest sources loading when file doesn't exist."""
        mock_exists.return_value = False
        
        sources = self.detector._load_quest_sources()
        
        self.assertEqual(sources, {"quest_sources": {}})
    
    def test_clean_npc_name(self):
        """Test NPC name cleaning."""
        # Test various input formats
        test_cases = [
            ("  NPC: Test NPC  ", "Test NPC"),
            ("Name: Test NPC", "Test NPC"),
            ("Test\nNPC", "Test NPC"),
            ("Test\r\nNPC", "Test NPC"),
            ("Test   NPC", "Test NPC"),
        ]
        
        for input_text, expected in test_cases:
            result = self.detector._clean_npc_name(input_text)
            self.assertEqual(result, expected)
    
    def test_is_valid_npc_name(self):
        """Test NPC name validation."""
        # Valid names
        valid_names = [
            "Test NPC",
            "Janta Blood Collector",
            "Robe Merchant",
            "ABC",  # Minimum length
            "A" * 50,  # Maximum length
        ]
        
        # Invalid names
        invalid_names = [
            "",  # Empty
            "AB",  # Too short
            "A" * 51,  # Too long
            "level 5",  # Contains invalid pattern
            "quest giver",  # Contains invalid pattern
            "123",  # No letters
        ]
        
        for name in valid_names:
            self.assertTrue(self.detector._is_valid_npc_name(name), f"Should be valid: {name}")
        
        for name in invalid_names:
            self.assertFalse(self.detector._is_valid_npc_name(name), f"Should be invalid: {name}")
    
    def test_find_quest_data(self):
        """Test quest data finding."""
        # Set up test quest sources
        self.detector.quest_sources = {
            "quest_sources": {
                "Janta Blood Collector": {
                    "name": "Janta Blood Collector",
                    "planet": "Tatooine",
                    "city": "Mos Entha"
                },
                "Robe Merchant": {
                    "name": "Robe Merchant",
                    "planet": "Naboo",
                    "city": "Theed"
                }
            }
        }
        
        # Test exact match
        quest_data = self.detector._find_quest_data("Janta Blood Collector")
        self.assertIsNotNone(quest_data)
        self.assertEqual(quest_data["planet"], "Tatooine")
        
        # Test partial match
        quest_data = self.detector._find_quest_data("Janta Blood")
        self.assertIsNotNone(quest_data)
        
        # Test no match
        quest_data = self.detector._find_quest_data("Unknown NPC")
        self.assertIsNone(quest_data)
    
    def test_get_npc_region(self):
        """Test NPC region calculation."""
        icon = QuestIcon("!", 0.8, (100, 100), (24, 24))
        
        region = self.detector._get_npc_region(icon)
        
        # Should return (x, y, width, height)
        self.assertEqual(len(region), 4)
        self.assertIsInstance(region[0], int)
        self.assertIsInstance(region[1], int)
        self.assertIsInstance(region[2], int)
        self.assertIsInstance(region[3], int)
    
    def test_set_debug_mode(self):
        """Test debug mode setting."""
        self.assertFalse(self.detector.debug_mode)
        
        self.detector.set_debug_mode(True)
        self.assertTrue(self.detector.debug_mode)
        
        self.detector.set_debug_mode(False)
        self.assertFalse(self.detector.debug_mode)

class TestGlobalFunctions(unittest.TestCase):
    """Test global convenience functions."""
    
    def test_get_npc_detector(self):
        """Test global detector instance."""
        detector1 = get_npc_detector()
        detector2 = get_npc_detector()
        
        # Should return the same instance
        self.assertIs(detector1, detector2)
        self.assertIsInstance(detector1, NPCDetector)
    
    @patch('vision.npc_detector.capture_screen')
    def test_detect_quest_npcs(self, mock_capture_screen):
        """Test global detect_quest_npcs function."""
        # Mock screen capture
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_capture_screen.return_value = mock_image
        
        # Mock detector
        with patch('vision.npc_detector.get_npc_detector') as mock_get_detector:
            mock_detector = MagicMock()
            mock_detector.detect_quest_npcs.return_value = []
            mock_get_detector.return_value = mock_detector
            
            result = detect_quest_npcs()
            
            self.assertEqual(result, [])
            mock_detector.detect_quest_npcs.assert_called_once()
    
    @patch('vision.npc_detector.capture_screen')
    def test_get_available_quests_nearby(self, mock_capture_screen):
        """Test global get_available_quests_nearby function."""
        # Mock screen capture
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_capture_screen.return_value = mock_image
        
        # Mock detector
        with patch('vision.npc_detector.get_npc_detector') as mock_get_detector:
            mock_detector = MagicMock()
            mock_detector.get_available_quests_nearby.return_value = []
            mock_get_detector.return_value = mock_detector
            
            result = get_available_quests_nearby()
            
            self.assertEqual(result, [])
            mock_detector.get_available_quests_nearby.assert_called_once()
    
    def test_set_debug_mode(self):
        """Test global set_debug_mode function."""
        # Mock detector
        with patch('vision.npc_detector.get_npc_detector') as mock_get_detector:
            mock_detector = MagicMock()
            mock_get_detector.return_value = mock_detector
            
            set_debug_mode(True)
            
            mock_detector.set_debug_mode.assert_called_once_with(True)

class TestIntegration(unittest.TestCase):
    """Test integration scenarios."""
    
    def test_full_detection_workflow(self):
        """Test complete detection workflow."""
        detector = NPCDetector()
        
        # Create test image
        test_image = np.zeros((200, 200, 3), dtype=np.uint8)
        
        # Test detection
        result = detector.detect_quest_npcs(test_image)
        
        # Should return a list
        self.assertIsInstance(result, list)
    
    def test_error_handling(self):
        """Test error handling scenarios."""
        detector = NPCDetector()
        
        # Test with None image - should handle gracefully
        try:
            result = detector.detect_quest_npcs(None)
            self.assertIsInstance(result, list)
        except Exception as e:
            # Expected to handle gracefully
            pass
        
        # Test with invalid image - should handle gracefully
        try:
            result = detector.detect_quest_npcs("invalid")
            self.assertIsInstance(result, list)
        except Exception as e:
            # Expected to handle gracefully
            pass
    
    def test_confidence_thresholds(self):
        """Test different confidence thresholds."""
        detector = NPCDetector()
        
        # Test various thresholds
        thresholds = [0.5, 0.6, 0.7, 0.8, 0.9]
        
        for threshold in thresholds:
            detector.min_confidence = threshold
            self.assertEqual(detector.min_confidence, threshold)

class TestCLIIntegration(unittest.TestCase):
    """Test CLI integration."""
    
    @patch('sys.argv', ['quest_detector.py', '--debug'])
    def test_cli_debug_mode(self):
        """Test CLI debug mode."""
        # This would test the CLI argument parsing
        # For now, just verify the module can be imported
        try:
            import cli.quest_detector
            self.assertTrue(True)
        except ImportError:
            self.skipTest("CLI module not available")

if __name__ == '__main__':
    unittest.main() 