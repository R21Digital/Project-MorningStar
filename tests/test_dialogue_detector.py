"""Unit tests for the dialogue detection system."""

import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
import json
import numpy as np
from datetime import datetime
from pathlib import Path

from core.dialogue_detector import (
    DialogueDetector,
    DialogueDetection,
    DialoguePreprocessor,
    DialogueTextAnalyzer,
    DialogueActionExecutor,
    DialogueLogger,
    detect_dialogue,
    scan_dialogues,
    register_custom_dialogue_pattern,
    DIALOGUE_PATTERNS,
    RESPONSE_ACTIONS,
)


class TestDialogueDetection:
    """Test the DialogueDetection dataclass."""

    def test_dialogue_detection_creation(self):
        """Test creating a DialogueDetection object."""
        detection = DialogueDetection(
            dialogue_type="quest_offer",
            text_content="Would you help me with a task?",
            confidence=0.8,
            timestamp=datetime.now()
        )
        
        assert detection.dialogue_type == "quest_offer"
        assert detection.text_content == "Would you help me with a task?"
        assert detection.confidence == 0.8
        assert detection.response_action is None
        assert detection.region_used == "full_screen"

    def test_dialogue_detection_with_action(self):
        """Test DialogueDetection with response action."""
        action = {"key": "1", "description": "Accept quest"}
        detection = DialogueDetection(
            dialogue_type="quest_offer",
            text_content="Test",
            confidence=0.5,
            timestamp=datetime.now(),
            response_action=action,
            region_used="dialogue_box"
        )
        
        assert detection.response_action == action
        assert detection.region_used == "dialogue_box"


class TestDialoguePreprocessor:
    """Test the DialoguePreprocessor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.preprocessor = DialoguePreprocessor()

    @patch('cv2.cvtColor')
    @patch('cv2.GaussianBlur')
    @patch('cv2.adaptiveThreshold')
    @patch('cv2.morphologyEx')
    def test_enhance_for_ocr(self, mock_morph, mock_thresh, mock_blur, mock_cvt):
        """Test image enhancement for OCR."""
        # Mock image
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Mock return values
        mock_cvt.return_value = np.zeros((100, 100), dtype=np.uint8)
        mock_blur.return_value = np.zeros((100, 100), dtype=np.uint8)
        mock_thresh.return_value = np.zeros((100, 100), dtype=np.uint8)
        mock_morph.return_value = np.zeros((100, 100), dtype=np.uint8)
        
        result = self.preprocessor.enhance_for_ocr(test_image)
        
        # Verify all processing steps were called
        mock_cvt.assert_called_once()
        mock_blur.assert_called_once()
        mock_thresh.assert_called_once()
        mock_morph.assert_called_once()
        
        assert result.shape == (100, 100)

    def test_extract_dialogue_region_full_screen(self):
        """Test extracting full screen region."""
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        result = self.preprocessor.extract_dialogue_region(test_image, "full_screen")
        
        assert np.array_equal(result, test_image)

    def test_extract_dialogue_region_specific(self):
        """Test extracting specific dialogue region."""
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Test with dialogue_box region (0.2, 0.6, 0.6, 0.3)
        result = self.preprocessor.extract_dialogue_region(test_image, "dialogue_box")
        
        # Expected dimensions: x=20, y=60, width=60, height=30
        assert result.shape == (30, 60, 3)

    def test_extract_dialogue_region_invalid(self):
        """Test extracting invalid region falls back to full screen."""
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        result = self.preprocessor.extract_dialogue_region(test_image, "invalid_region")
        
        assert np.array_equal(result, test_image)


class TestDialogueTextAnalyzer:
    """Test the DialogueTextAnalyzer class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = DialogueTextAnalyzer()

    def test_analyze_quest_offer_text(self):
        """Test analyzing quest offer text."""
        text = "Would you help me with this urgent task? I need assistance!"
        dialogue_type, confidence = self.analyzer.analyze_text(text)
        
        assert dialogue_type == "quest_offer"
        assert confidence > 0.3

    def test_analyze_trainer_dialogue_text(self):
        """Test analyzing trainer dialogue text."""
        text = "I can teach you new abilities. Train your skills with me!"
        dialogue_type, confidence = self.analyzer.analyze_text(text)
        
        assert dialogue_type == "trainer_dialogue"
        assert confidence > 0.3

    def test_analyze_unrecognized_text(self):
        """Test analyzing unrecognized text."""
        text = "Random text that doesn't match any patterns."
        dialogue_type, confidence = self.analyzer.analyze_text(text)
        
        assert dialogue_type is None
        assert confidence == 0.0

    def test_calculate_confidence_multiple_matches(self):
        """Test confidence calculation with multiple pattern matches."""
        text = "would you help me with this urgent task for you"
        patterns = ["would you.*help", "task.*for you", "urgent"]
        confidence = self.analyzer._calculate_confidence(text, patterns)
        
        # Should be higher than single match due to bonus
        assert confidence > 0.6

    def test_calculate_confidence_single_match(self):
        """Test confidence calculation with single pattern match."""
        text = "would you help me"
        patterns = ["would you.*help", "task.*for you", "urgent"]
        confidence = self.analyzer._calculate_confidence(text, patterns)
        
        assert confidence == pytest.approx(0.33, rel=0.1)

    def test_calculate_confidence_no_matches(self):
        """Test confidence calculation with no pattern matches."""
        text = "random text"
        patterns = ["would you.*help", "task.*for you", "urgent"]
        confidence = self.analyzer._calculate_confidence(text, patterns)
        
        assert confidence == 0.0


class TestDialogueActionExecutor:
    """Test the DialogueActionExecutor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.executor = DialogueActionExecutor()

    @patch('pyautogui.press')
    @patch('time.sleep')
    def test_execute_response_quest_offer(self, mock_sleep, mock_press):
        """Test executing response for quest offer."""
        result = self.executor.execute_response("quest_offer")
        
        assert result is True
        mock_press.assert_called_with("1")
        assert mock_sleep.call_count >= 1

    @patch('pyautogui.press')
    @patch('time.sleep')
    def test_execute_response_continue_prompt(self, mock_sleep, mock_press):
        """Test executing response for continue prompt."""
        result = self.executor.execute_response("continue_prompt")
        
        assert result is True
        mock_press.assert_called_with("enter")
        assert mock_sleep.call_count >= 1

    def test_execute_response_unknown_type(self):
        """Test executing response for unknown dialogue type."""
        result = self.executor.execute_response("unknown_type")
        
        assert result is False

    @patch('pyautogui.press')
    @patch('time.sleep')
    def test_execute_response_exception(self, mock_sleep, mock_press):
        """Test handling exception during response execution."""
        mock_press.side_effect = Exception("Test exception")
        
        result = self.executor.execute_response("quest_offer")
        
        assert result is False


class TestDialogueLogger:
    """Test the DialogueLogger class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.logger = DialogueLogger()

    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', new_callable=mock_open)
    def test_log_detection(self, mock_file, mock_mkdir):
        """Test logging a dialogue detection."""
        detection = DialogueDetection(
            dialogue_type="quest_offer",
            text_content="Test dialogue",
            confidence=0.8,
            timestamp=datetime.now()
        )
        
        # Mock JSON file operations
        with patch('json.load', return_value=[]), \
             patch('json.dump') as mock_json_dump:
            
            self.logger.log_detection(detection)
            
            # Verify directory creation
            mock_mkdir.assert_called_once()
            
            # Verify file operations
            assert mock_file.call_count >= 2  # Session log and JSON log
            mock_json_dump.assert_called_once()

    @patch('pathlib.Path.mkdir')
    @patch('json.load')
    @patch('json.dump')
    @patch('builtins.open', new_callable=mock_open)
    def test_append_json_log_with_existing_logs(self, mock_file, mock_json_dump, mock_json_load, mock_mkdir):
        """Test appending to existing JSON logs."""
        # Mock existing logs
        existing_logs = [{"test": "log"}] * 500
        mock_json_load.return_value = existing_logs
        
        detection = DialogueDetection(
            dialogue_type="quest_offer",
            text_content="Test",
            confidence=0.8,
            timestamp=datetime.now()
        )
        
        self.logger._append_json_log(detection)
        
        # Verify JSON operations
        mock_json_load.assert_called_once()
        mock_json_dump.assert_called_once()
        
        # Check that new log was added
        dumped_data = mock_json_dump.call_args[0][0]
        assert len(dumped_data) == 501

    @patch('pathlib.Path.mkdir')
    @patch('json.load')
    @patch('json.dump')
    @patch('builtins.open', new_callable=mock_open)
    def test_append_json_log_truncation(self, mock_file, mock_json_dump, mock_json_load, mock_mkdir):
        """Test JSON log truncation when exceeding limit."""
        # Mock logs that exceed the limit
        existing_logs = [{"test": "log"}] * 1000
        mock_json_load.return_value = existing_logs
        
        detection = DialogueDetection(
            dialogue_type="quest_offer",
            text_content="Test",
            confidence=0.8,
            timestamp=datetime.now()
        )
        
        self.logger._append_json_log(detection)
        
        # Check that logs were truncated to 1000
        dumped_data = mock_json_dump.call_args[0][0]
        assert len(dumped_data) == 1000


class TestDialogueDetector:
    """Test the main DialogueDetector class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = DialogueDetector()

    @patch('core.dialogue_detector.capture_screen')
    @patch('pytesseract.image_to_string')
    def test_detect_and_handle_dialogue_success(self, mock_ocr, mock_capture):
        """Test successful dialogue detection and handling."""
        # Mock screen capture and OCR
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_capture.return_value = mock_image
        mock_ocr.return_value = "Would you help me with this urgent task?"
        
        # Mock the action executor
        with patch.object(self.detector.executor, 'execute_response', return_value=True) as mock_execute:
            detection = self.detector.detect_and_handle_dialogue(auto_respond=True)
            
            assert detection is not None
            assert detection.dialogue_type == "quest_offer"
            assert detection.confidence > 0.3
            mock_execute.assert_called_once_with("quest_offer")

    @patch('core.dialogue_detector.capture_screen')
    @patch('pytesseract.image_to_string')
    def test_detect_and_handle_dialogue_no_text(self, mock_ocr, mock_capture):
        """Test dialogue detection with no text extracted."""
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_capture.return_value = mock_image
        mock_ocr.return_value = ""
        
        detection = self.detector.detect_and_handle_dialogue()
        
        assert detection is None

    @patch('core.dialogue_detector.capture_screen')
    @patch('pytesseract.image_to_string')
    def test_detect_and_handle_dialogue_unrecognized(self, mock_ocr, mock_capture):
        """Test dialogue detection with unrecognized text."""
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_capture.return_value = mock_image
        mock_ocr.return_value = "Random unrecognized text"
        
        detection = self.detector.detect_and_handle_dialogue()
        
        assert detection is None

    @patch('core.dialogue_detector.capture_screen')
    @patch('pytesseract.image_to_string')
    def test_detect_and_handle_dialogue_no_auto_respond(self, mock_ocr, mock_capture):
        """Test dialogue detection without auto-response."""
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_capture.return_value = mock_image
        mock_ocr.return_value = "Would you help me with this task?"
        
        with patch.object(self.detector.executor, 'execute_response') as mock_execute:
            detection = self.detector.detect_and_handle_dialogue(auto_respond=False)
            
            assert detection is not None
            assert detection.dialogue_type == "quest_offer"
            mock_execute.assert_not_called()

    @patch('core.dialogue_detector.capture_screen')
    @patch('pytesseract.image_to_string')
    @patch('time.sleep')
    @patch('time.time')
    def test_scan_for_dialogues(self, mock_time, mock_sleep, mock_ocr, mock_capture):
        """Test scanning for dialogues over time."""
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_capture.return_value = mock_image
        
        # Mock time progression
        mock_time.side_effect = [0, 1, 2, 15]  # Start, iter1, iter2, end
        
        # Mock OCR responses
        mock_ocr.side_effect = [
            "Would you help me?",  # First detection
            "Random text",          # No detection
            "Train your skills!"    # Second detection
        ]
        
        detections = self.detector.scan_for_dialogues(duration=10.0, interval=2.0, auto_respond=False)
        
        assert len(detections) == 2
        assert detections[0].dialogue_type == "quest_offer"
        assert detections[1].dialogue_type == "trainer_dialogue"

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_get_dialogue_history(self, mock_json_load, mock_file):
        """Test retrieving dialogue history."""
        # Mock dialogue history
        history_data = [
            {"timestamp": "2023-01-01T00:00:00", "dialogue_type": "quest_offer"},
            {"timestamp": "2023-01-01T00:01:00", "dialogue_type": "trainer_dialogue"}
        ]
        mock_json_load.return_value = history_data
        
        history = self.detector.get_dialogue_history(limit=10)
        
        assert len(history) == 2
        assert history[0]["dialogue_type"] == "quest_offer"
        assert history[1]["dialogue_type"] == "trainer_dialogue"

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_get_dialogue_history_file_not_found(self, mock_json_load, mock_file):
        """Test retrieving dialogue history when file doesn't exist."""
        mock_json_load.side_effect = FileNotFoundError()
        
        history = self.detector.get_dialogue_history()
        
        assert history == []


class TestConvenienceFunctions:
    """Test convenience functions."""

    @patch('core.dialogue_detector.DialogueDetector')
    def test_detect_dialogue(self, mock_detector_class):
        """Test detect_dialogue convenience function."""
        mock_detector = Mock()
        mock_detector_class.return_value = mock_detector
        mock_detection = Mock()
        mock_detector.detect_and_handle_dialogue.return_value = mock_detection
        
        result = detect_dialogue(auto_respond=False)
        
        mock_detector_class.assert_called_once()
        mock_detector.detect_and_handle_dialogue.assert_called_once_with(auto_respond=False)
        assert result == mock_detection

    @patch('core.dialogue_detector.DialogueDetector')
    def test_scan_dialogues(self, mock_detector_class):
        """Test scan_dialogues convenience function."""
        mock_detector = Mock()
        mock_detector_class.return_value = mock_detector
        mock_detections = [Mock(), Mock()]
        mock_detector.scan_for_dialogues.return_value = mock_detections
        
        result = scan_dialogues(duration=5.0, auto_respond=True)
        
        mock_detector_class.assert_called_once()
        mock_detector.scan_for_dialogues.assert_called_once_with(duration=5.0, auto_respond=True)
        assert result == mock_detections

    def test_register_custom_dialogue_pattern(self):
        """Test registering custom dialogue pattern."""
        original_patterns = DIALOGUE_PATTERNS.copy()
        original_actions = RESPONSE_ACTIONS.copy()
        
        try:
            register_custom_dialogue_pattern(
                "custom_type",
                ["custom.*pattern"],
                {"key": "2", "description": "Custom action"}
            )
            
            assert "custom_type" in DIALOGUE_PATTERNS
            assert "custom_type" in RESPONSE_ACTIONS
            assert DIALOGUE_PATTERNS["custom_type"] == ["custom.*pattern"]
            assert RESPONSE_ACTIONS["custom_type"]["key"] == "2"
            
        finally:
            # Restore original patterns
            DIALOGUE_PATTERNS.clear()
            DIALOGUE_PATTERNS.update(original_patterns)
            RESPONSE_ACTIONS.clear()
            RESPONSE_ACTIONS.update(original_actions)


class TestIntegration:
    """Integration tests for the complete dialogue system."""

    @patch('core.dialogue_detector.capture_screen')
    @patch('pytesseract.image_to_string')
    @patch('pyautogui.press')
    @patch('time.sleep')
    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', new_callable=mock_open)
    def test_full_dialogue_workflow(self, mock_file, mock_mkdir, mock_sleep, mock_press, mock_ocr, mock_capture):
        """Test complete dialogue detection and response workflow."""
        # Setup mocks
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_capture.return_value = mock_image
        mock_ocr.return_value = "Would you help me with this urgent quest?"
        
        # Mock JSON operations
        with patch('json.load', return_value=[]), \
             patch('json.dump') as mock_json_dump:
            
            detector = DialogueDetector()
            detection = detector.detect_and_handle_dialogue(auto_respond=True)
            
            # Verify detection
            assert detection is not None
            assert detection.dialogue_type == "quest_offer"
            assert detection.confidence > 0.3
            
            # Verify action execution
            mock_press.assert_called_with("1")
            
            # Verify logging
            mock_json_dump.assert_called_once()
            
            # Verify delays for human-like behavior
            assert mock_sleep.call_count >= 2