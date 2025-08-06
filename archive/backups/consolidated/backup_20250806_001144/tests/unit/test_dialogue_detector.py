"""Unit tests for dialogue detection system."""

import pytest
import tempfile
import os
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

import numpy as np
import cv2
from unittest.mock import patch, MagicMock

from core.dialogue_detector import (
    DialogueWindow, DialogueDetector, get_dialogue_detector,
    detect_dialogue_window, handle_quest_dialogue, handle_trainer_dialogue,
    auto_accept_quests, auto_complete_quests
)


class TestDialogueWindow:
    """Test DialogueWindow dataclass."""
    
    def test_dialogue_window_creation(self):
        """Test creating a DialogueWindow instance."""
        window = DialogueWindow(
            x=100, y=200, width=300, height=400,
            text="Test dialogue text",
            options=["Accept", "Decline"],
            confidence=85.5,
            window_type="quest"
        )
        
        assert window.x == 100
        assert window.y == 200
        assert window.width == 300
        assert window.height == 400
        assert window.text == "Test dialogue text"
        assert window.options == ["Accept", "Decline"]
        assert window.confidence == 85.5
        assert window.window_type == "quest"
        assert window.timestamp is not None
    
    def test_dialogue_window_timestamp(self):
        """Test that timestamp is automatically set."""
        window = DialogueWindow(
            x=0, y=0, width=100, height=100,
            text="Test",
            options=[],
            confidence=50.0,
            window_type="general"
        )
        
        assert window.timestamp is not None
        # Verify it's a valid ISO timestamp
        datetime.fromisoformat(window.timestamp)


class TestDialogueDetector:
    """Test DialogueDetector class."""
    
    @pytest.fixture
    def detector(self):
        """Create a DialogueDetector instance for testing."""
        return DialogueDetector()
    
    @pytest.fixture
    def mock_ocr_result(self):
        """Create a mock OCR result."""
        mock_result = Mock()
        mock_result.text = "Accept Quest\n1. Accept\n2. Decline"
        mock_result.confidence = 85.0
        return mock_result
    
    def test_detector_initialization(self, detector):
        """Test DialogueDetector initialization."""
        assert detector.ocr_engine is not None
        assert detector.log_dir == os.path.join("logs", "dialogue")
        assert "quest_accept" in detector.dialogue_patterns
        assert "quest_complete" in detector.dialogue_patterns
        assert "training" in detector.dialogue_patterns
    
    def test_log_dialogue_event(self, detector, tmp_path):
        """Test dialogue event logging."""
        # Mock the log directory
        detector.log_dir = str(tmp_path)
        
        # Create a test dialogue window
        dialogue = DialogueWindow(
            x=100, y=200, width=300, height=400,
            text="Test dialogue",
            options=["Accept", "Decline"],
            confidence=80.0,
            window_type="quest"
        )
        
        # Test logging
        detector.log_dialogue_event("test_event", dialogue, "test_action", True, {"test": "data"})
        
        # Check that log file was created
        date_str = datetime.now().strftime("%Y%m%d")
        log_file = os.path.join(detector.log_dir, f"dialogue_{date_str}.json")
        assert os.path.exists(log_file)
        
        # Check log content
        with open(log_file, 'r') as f:
            logs = json.load(f)
        
        assert len(logs) == 1
        log_entry = logs[0]
        assert log_entry["event_type"] == "test_event"
        assert log_entry["action"] == "test_action"
        assert log_entry["success"] is True
        assert log_entry["details"]["test"] == "data"
        assert "dialogue" in log_entry
    
    @patch('core.dialogue_detector.capture_screen')
    @patch('core.dialogue_detector.get_ocr_engine')
    def test_detect_dialogue_window_success(self, mock_get_ocr, mock_capture, detector):
        """Test successful dialogue window detection."""
        # Mock screenshot
        mock_image = np.array([[0, 0, 0] for _ in range(800 * 1200)]).reshape(800, 1200, 3).astype(np.uint8)
        mock_capture.return_value = mock_image
        
        # Mock OCR engine
        mock_ocr = Mock()
        mock_result = Mock()
        mock_result.text = "Accept Quest\n1. Accept\n2. Decline"
        mock_result.confidence = 85.0
        mock_ocr.extract_text.return_value = mock_result
        mock_get_ocr.return_value = mock_ocr
        
        # Test detection
        result = detector.detect_dialogue_window()
        
        assert result is not None
        assert result.text == "Accept Quest\n1. Accept\n2. Decline"
        assert result.confidence == 85.0
        assert result.window_type == "quest"
        assert len(result.options) == 2
    
    @patch('core.dialogue_detector.capture_screen')
    @patch('core.dialogue_detector.get_ocr_engine')
    def test_detect_dialogue_window_no_dialogue(self, mock_get_ocr, mock_capture, detector):
        """Test dialogue detection when no dialogue is present."""
        # Mock screenshot
        mock_image = np.array([[0, 0, 0] for _ in range(800 * 1200)]).reshape(800, 1200, 3).astype(np.uint8)
        mock_capture.return_value = mock_image
        
        # Mock OCR engine with no dialogue text
        mock_ocr = Mock()
        mock_result = Mock()
        mock_result.text = "Some random text"
        mock_result.confidence = 90.0
        mock_ocr.extract_text.return_value = mock_result
        mock_get_ocr.return_value = mock_ocr
        
        # Test detection
        result = detector.detect_dialogue_window()
        
        assert result is None
    
    def test_is_dialogue_text_quest_keywords(self, detector):
        """Test dialogue text detection with quest keywords."""
        text = "Would you like to accept this quest?"
        assert detector._is_dialogue_text(text, "quest") is True
        
        text = "Please help me with this mission"
        assert detector._is_dialogue_text(text, "quest") is True
    
    def test_is_dialogue_text_training_keywords(self, detector):
        """Test dialogue text detection with training keywords."""
        text = "Would you like to train your skills?"
        assert detector._is_dialogue_text(text, "trainer") is True
        
        text = "Learn new abilities here"
        assert detector._is_dialogue_text(text, "trainer") is True
    
    def test_is_dialogue_text_numbered_options(self, detector):
        """Test dialogue text detection with numbered options."""
        text = "1. Accept\n2. Decline"
        assert detector._is_dialogue_text(text, "general") is True
    
    def test_is_dialogue_text_capitalized_options(self, detector):
        """Test dialogue text detection with capitalized options."""
        text = "Accept\nDecline\nCancel"
        assert detector._is_dialogue_text(text, "general") is True
    
    def test_is_dialogue_text_not_dialogue(self, detector):
        """Test that non-dialogue text is not detected."""
        text = "This is just some random text without any dialogue indicators"
        assert detector._is_dialogue_text(text, "general") is False
    
    def test_extract_dialogue_options_numbered(self, detector):
        """Test extracting numbered dialogue options."""
        text = "1. Accept the quest\n2. Decline the quest\n3. Ask for more information"
        options = detector._extract_dialogue_options(text)
        
        assert len(options) == 3
        assert "Accept the quest" in options
        assert "Decline the quest" in options
        assert "Ask for more information" in options
    
    def test_extract_dialogue_options_capitalized(self, detector):
        """Test extracting capitalized dialogue options."""
        text = "Accept\nDecline\nCancel"
        options = detector._extract_dialogue_options(text)
        
        assert len(options) == 3
        assert "Accept" in options
        assert "Decline" in options
        assert "Cancel" in options
    
    def test_extract_dialogue_options_uppercase(self, detector):
        """Test extracting uppercase dialogue options."""
        text = "ACCEPT\nDECLINE\nCANCEL"
        options = detector._extract_dialogue_options(text)
        
        assert len(options) == 3
        assert "ACCEPT" in options
        assert "DECLINE" in options
        assert "CANCEL" in options
    
    def test_extract_dialogue_options_duplicates(self, detector):
        """Test that duplicate options are removed."""
        text = "Accept\nAccept\nDecline\nDecline"
        options = detector._extract_dialogue_options(text)
        
        assert len(options) == 2
        assert options.count("Accept") == 1
        assert options.count("Decline") == 1
    
    @patch('pyautogui.click')
    def test_click_dialogue_option_success(self, mock_click, detector):
        """Test successful dialogue option clicking."""
        dialogue = DialogueWindow(
            x=100, y=200, width=300, height=400,
            text="Test dialogue",
            options=["Accept", "Decline"],
            confidence=80.0,
            window_type="quest"
        )
        
        result = detector.click_dialogue_option(0, dialogue)
        
        assert result is True
        mock_click.assert_called_once()
    
    @patch('pyautogui.click')
    def test_click_dialogue_option_invalid_index(self, mock_click, detector):
        """Test clicking with invalid option index."""
        dialogue = DialogueWindow(
            x=100, y=200, width=300, height=400,
            text="Test dialogue",
            options=["Accept", "Decline"],
            confidence=80.0,
            window_type="quest"
        )
        
        result = detector.click_dialogue_option(5, dialogue)
        
        assert result is False
        mock_click.assert_not_called()
    
    @patch('pyautogui.click')
    def test_click_dialogue_option_exception(self, mock_click, detector):
        """Test clicking when an exception occurs."""
        mock_click.side_effect = Exception("Click failed")
        
        dialogue = DialogueWindow(
            x=100, y=200, width=300, height=400,
            text="Test dialogue",
            options=["Accept", "Decline"],
            confidence=80.0,
            window_type="quest"
        )
        
        result = detector.click_dialogue_option(0, dialogue)
        
        assert result is False
    
    def test_click_dialogue_option_by_text_exact_match(self, detector):
        """Test clicking dialogue option by exact text match."""
        dialogue = DialogueWindow(
            x=100, y=200, width=300, height=400,
            text="Test dialogue",
            options=["Accept", "Decline"],
            confidence=80.0,
            window_type="quest"
        )
        
        with patch.object(detector, 'click_dialogue_option') as mock_click:
            mock_click.return_value = True
            result = detector.click_dialogue_option_by_text("Accept", dialogue)
            
            assert result is True
            mock_click.assert_called_once_with(0, dialogue)
    
    def test_click_dialogue_option_by_text_partial_match(self, detector):
        """Test clicking dialogue option by partial text match."""
        dialogue = DialogueWindow(
            x=100, y=200, width=300, height=400,
            text="Test dialogue",
            options=["Accept Quest", "Decline Quest"],
            confidence=80.0,
            window_type="quest"
        )
        
        with patch.object(detector, 'click_dialogue_option') as mock_click:
            mock_click.return_value = True
            result = detector.click_dialogue_option_by_text("Accept", dialogue)
            
            assert result is True
            mock_click.assert_called_once_with(0, dialogue)
    
    def test_click_dialogue_option_by_text_fuzzy_match(self, detector):
        """Test clicking dialogue option by fuzzy matching."""
        dialogue = DialogueWindow(
            x=100, y=200, width=300, height=400,
            text="Test dialogue",
            options=["Yes, I'll help", "No, not now"],
            confidence=80.0,
            window_type="quest"
        )
        
        with patch.object(detector, 'click_dialogue_option') as mock_click:
            mock_click.return_value = True
            result = detector.click_dialogue_option_by_text("accept", dialogue)
            
            assert result is True
            mock_click.assert_called_once_with(0, dialogue)
    
    def test_click_dialogue_option_by_text_not_found(self, detector):
        """Test clicking dialogue option when text is not found."""
        dialogue = DialogueWindow(
            x=100, y=200, width=300, height=400,
            text="Test dialogue",
            options=["Accept", "Decline"],
            confidence=80.0,
            window_type="quest"
        )
        
        with patch.object(detector, 'click_dialogue_option') as mock_click:
            result = detector.click_dialogue_option_by_text("Not Found", dialogue)
            
            assert result is False
            mock_click.assert_not_called()
    
    @patch.object(DialogueDetector, 'detect_dialogue_window')
    @patch.object(DialogueDetector, 'click_dialogue_option_by_text')
    def test_handle_quest_dialogue_accept(self, mock_click, mock_detect, detector):
        """Test handling quest accept dialogue."""
        dialogue = DialogueWindow(
            x=100, y=200, width=300, height=400,
            text="Accept Quest",
            options=["Accept", "Decline"],
            confidence=80.0,
            window_type="quest"
        )
        mock_detect.return_value = dialogue
        mock_click.return_value = True
        
        result = detector.handle_quest_dialogue("accept")
        
        assert result is True
        mock_click.assert_called()
    
    @patch.object(DialogueDetector, 'detect_dialogue_window')
    @patch.object(DialogueDetector, 'click_dialogue_option_by_text')
    def test_handle_quest_dialogue_complete(self, mock_click, mock_detect, detector):
        """Test handling quest complete dialogue."""
        dialogue = DialogueWindow(
            x=100, y=200, width=300, height=400,
            text="Complete Quest",
            options=["Complete", "Cancel"],
            confidence=80.0,
            window_type="quest"
        )
        mock_detect.return_value = dialogue
        mock_click.return_value = True
        
        result = detector.handle_quest_dialogue("complete")
        
        assert result is True
        mock_click.assert_called()
    
    @patch.object(DialogueDetector, 'detect_dialogue_window')
    @patch.object(DialogueDetector, 'click_dialogue_option_by_text')
    def test_handle_quest_dialogue_decline(self, mock_click, mock_detect, detector):
        """Test handling quest decline dialogue."""
        dialogue = DialogueWindow(
            x=100, y=200, width=300, height=400,
            text="Decline Quest",
            options=["Accept", "Decline"],
            confidence=80.0,
            window_type="quest"
        )
        mock_detect.return_value = dialogue
        mock_click.return_value = True
        
        result = detector.handle_quest_dialogue("decline")
        
        assert result is True
        mock_click.assert_called()
    
    @patch.object(DialogueDetector, 'detect_dialogue_window')
    def test_handle_quest_dialogue_no_dialogue(self, mock_detect, detector):
        """Test handling quest dialogue when no dialogue is present."""
        mock_detect.return_value = None
        
        result = detector.handle_quest_dialogue("accept")
        
        assert result is False
    
    @patch.object(DialogueDetector, 'detect_dialogue_window')
    @patch.object(DialogueDetector, 'click_dialogue_option_by_text')
    def test_handle_trainer_dialogue(self, mock_click, mock_detect, detector):
        """Test handling trainer dialogue."""
        dialogue = DialogueWindow(
            x=100, y=200, width=300, height=400,
            text="Train Skills",
            options=["Train", "Cancel"],
            confidence=80.0,
            window_type="trainer"
        )
        mock_detect.return_value = dialogue
        mock_click.return_value = True
        
        result = detector.handle_trainer_dialogue()
        
        assert result is True
        mock_click.assert_called()
    
    @patch.object(DialogueDetector, 'detect_dialogue_window')
    def test_wait_for_dialogue_success(self, mock_detect, detector):
        """Test waiting for dialogue with success."""
        dialogue = DialogueWindow(
            x=100, y=200, width=300, height=400,
            text="Test dialogue",
            options=["Accept"],
            confidence=80.0,
            window_type="quest"
        )
        mock_detect.return_value = dialogue
        
        result = detector.wait_for_dialogue(timeout=1.0)
        
        assert result == dialogue
    
    @patch.object(DialogueDetector, 'detect_dialogue_window')
    def test_wait_for_dialogue_timeout(self, mock_detect, detector):
        """Test waiting for dialogue with timeout."""
        mock_detect.return_value = None
        
        result = detector.wait_for_dialogue(timeout=0.1)
        
        assert result is None
    
    @patch.object(DialogueDetector, 'detect_dialogue_window')
    @patch.object(DialogueDetector, 'handle_quest_dialogue')
    def test_auto_accept_quests(self, mock_handle, mock_detect, detector):
        """Test auto-accepting quests."""
        dialogue = DialogueWindow(
            x=100, y=200, width=300, height=400,
            text="Would you like to accept this quest?",
            options=["Accept", "Decline"],
            confidence=80.0,
            window_type="quest"
        )
        mock_detect.return_value = dialogue
        mock_handle.return_value = True
        
        result = detector.auto_accept_quests()
        
        assert result is True
        mock_handle.assert_called_once_with("accept")
    
    @patch.object(DialogueDetector, 'detect_dialogue_window')
    @patch.object(DialogueDetector, 'handle_quest_dialogue')
    def test_auto_complete_quests(self, mock_handle, mock_detect, detector):
        """Test auto-completing quests."""
        dialogue = DialogueWindow(
            x=100, y=200, width=300, height=400,
            text="Would you like to complete this quest?",
            options=["Complete", "Cancel"],
            confidence=80.0,
            window_type="quest"
        )
        mock_detect.return_value = dialogue
        mock_handle.return_value = True
        
        result = detector.auto_complete_quests()
        
        assert result is True
        mock_handle.assert_called_once_with("complete")


class TestGlobalFunctions:
    """Test global functions from dialogue_detector module."""
    
    @patch('core.dialogue_detector.get_dialogue_detector')
    def test_detect_dialogue_window_global(self, mock_get_detector):
        """Test global detect_dialogue_window function."""
        mock_detector = Mock()
        mock_get_detector.return_value = mock_detector
        mock_detector.detect_dialogue_window.return_value = "test_result"
        
        result = detect_dialogue_window()
        
        assert result == "test_result"
        mock_detector.detect_dialogue_window.assert_called_once()
    
    @patch('core.dialogue_detector.get_dialogue_detector')
    def test_handle_quest_dialogue_global(self, mock_get_detector):
        """Test global handle_quest_dialogue function."""
        mock_detector = Mock()
        mock_get_detector.return_value = mock_detector
        mock_detector.handle_quest_dialogue.return_value = True
        
        result = handle_quest_dialogue("accept")
        
        assert result is True
        mock_detector.handle_quest_dialogue.assert_called_once_with("accept")
    
    @patch('core.dialogue_detector.get_dialogue_detector')
    def test_handle_trainer_dialogue_global(self, mock_get_detector):
        """Test global handle_trainer_dialogue function."""
        mock_detector = Mock()
        mock_get_detector.return_value = mock_detector
        mock_detector.handle_trainer_dialogue.return_value = True
        
        result = handle_trainer_dialogue()
        
        assert result is True
        mock_detector.handle_trainer_dialogue.assert_called_once()
    
    @patch('core.dialogue_detector.get_dialogue_detector')
    def test_auto_accept_quests_global(self, mock_get_detector):
        """Test global auto_accept_quests function."""
        mock_detector = Mock()
        mock_get_detector.return_value = mock_detector
        mock_detector.auto_accept_quests.return_value = True
        
        result = auto_accept_quests()
        
        assert result is True
        mock_detector.auto_accept_quests.assert_called_once()
    
    @patch('core.dialogue_detector.get_dialogue_detector')
    def test_auto_complete_quests_global(self, mock_get_detector):
        """Test global auto_complete_quests function."""
        mock_detector = Mock()
        mock_get_detector.return_value = mock_detector
        mock_detector.auto_complete_quests.return_value = True
        
        result = auto_complete_quests()
        
        assert result is True
        mock_detector.auto_complete_quests.assert_called_once()


class TestIntegration:
    """Integration tests for dialogue detection."""
    
    def test_dialogue_detector_singleton(self):
        """Test that get_dialogue_detector returns the same instance."""
        detector1 = get_dialogue_detector()
        detector2 = get_dialogue_detector()
        
        assert detector1 is detector2
    
    def test_dialogue_window_serialization(self):
        """Test that DialogueWindow can be serialized to JSON."""
        window = DialogueWindow(
            x=100, y=200, width=300, height=400,
            text="Test dialogue",
            options=["Accept", "Decline"],
            confidence=80.0,
            window_type="quest"
        )
        
        # Test that it can be converted to dict
        window_dict = {
            "x": window.x,
            "y": window.y,
            "width": window.width,
            "height": window.height,
            "text": window.text,
            "options": window.options,
            "confidence": window.confidence,
            "window_type": window.window_type,
            "timestamp": window.timestamp
        }
        
        # Test JSON serialization
        json_str = json.dumps(window_dict)
        assert json_str is not None
        assert "Test dialogue" in json_str 