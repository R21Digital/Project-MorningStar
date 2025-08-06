#!/usr/bin/env python3
"""
Unit tests for Batch 037 - Interactive NPC & Terminal Logic

Tests cover:
- NPC interaction functionality
- Chatbox scanning and message classification
- Dialogue parsing and response determination
- Fallback logic and error handling
- Statistics and tracking
"""

import sys
import pytest
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add interactions and core to path for imports
sys.path.insert(0, str(Path(__file__).parent / "interactions"))
sys.path.insert(0, str(Path(__file__).parent / "core" / "ocr"))

from npc_interactor import (
    NPCInteractor, InteractionType, ResponseType, NPCDialogue, 
    InteractionAttempt, get_npc_interactor, interact_with_npc, 
    get_interaction_statistics
)
from chatbox_scanner import (
    ChatboxScanner, MessageType, ChatMessage, get_chatbox_scanner,
    scan_chatbox, get_npc_messages, get_messages_requiring_response,
    get_chat_statistics
)


class TestNPCInteractor:
    """Test NPC Interactor functionality."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.interactor = NPCInteractor()
    
    def test_initialization(self):
        """Test NPCInteractor initialization."""
        assert self.interactor is not None
        assert hasattr(self.interactor, 'config')
        assert hasattr(self.interactor, 'interaction_history')
        assert hasattr(self.interactor, 'stats')
    
    def test_load_config(self):
        """Test configuration loading."""
        config = self.interactor.load_config()
        assert isinstance(config, dict)
        assert 'response_patterns' in config
        assert 'fallback_sequences' in config
        assert 'ocr_keywords' in config
    
    def test_parse_dialogue_from_ocr(self):
        """Test dialogue parsing from OCR text."""
        ocr_text = "John Smith: Hello there! I have a quest for you. [Accept] [Decline]"
        dialogue_info = self.interactor.parse_dialogue_from_ocr(ocr_text)
        
        assert dialogue_info is not None
        assert dialogue_info['npc_name'] == "John Smith"
        assert "quest" in dialogue_info['dialogue_text'].lower()
        assert len(dialogue_info['response_options']) > 0
        assert dialogue_info['interaction_type'] == InteractionType.QUEST_GIVER
    
    def test_extract_npc_name(self):
        """Test NPC name extraction."""
        # Test various name patterns
        test_cases = [
            ("John Smith: Hello", "John Smith"),
            ("JOHN: Hello", "JOHN"),
            ("John: Hello", "John"),
            ("Unknown text", "Unknown NPC")
        ]
        
        for ocr_text, expected_name in test_cases:
            name = self.interactor.extract_npc_name(ocr_text)
            assert name == expected_name
    
    def test_extract_dialogue_text(self):
        """Test dialogue text extraction."""
        ocr_text = "John Smith: Hello there! I have a quest for you."
        dialogue_text = self.interactor.extract_dialogue_text(ocr_text)
        
        assert "Hello there" in dialogue_text
        assert "quest" in dialogue_text.lower()
        assert "John Smith:" not in dialogue_text
    
    def test_extract_response_options(self):
        """Test response option extraction."""
        ocr_text = "John: Would you like to accept? [Accept] [Decline] 1. Yes 2. No"
        options = self.interactor.extract_response_options(ocr_text)
        
        assert len(options) > 0
        assert any("accept" in opt.lower() for opt in options)
        assert any("decline" in opt.lower() for opt in options)
    
    def test_determine_interaction_type(self):
        """Test interaction type determination."""
        test_cases = [
            ("quest accept mission", InteractionType.QUEST_GIVER),
            ("train skill learn", InteractionType.TRAINER),
            ("terminal computer system", InteractionType.TERMINAL),
            ("buy sell shop vendor", InteractionType.VENDOR),
            ("random text", InteractionType.UNKNOWN)
        ]
        
        for ocr_text, expected_type in test_cases:
            interaction_type = self.interactor.determine_interaction_type(ocr_text)
            assert interaction_type == expected_type
    
    def test_calculate_dialogue_confidence(self):
        """Test dialogue confidence calculation."""
        ocr_text = "John Smith: Hello there! I have a quest for you. [Accept] [Decline]"
        interaction_type = InteractionType.QUEST_GIVER
        
        confidence = self.interactor.calculate_dialogue_confidence(ocr_text, interaction_type)
        
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.5  # Should be reasonably confident
    
    def test_determine_response(self):
        """Test response determination."""
        # Test quest giver
        dialogue = NPCDialogue(
            npc_name="John",
            dialogue_text="I have a quest for you. Would you like to accept?",
            response_options=["Accept", "Decline"],
            interaction_type=InteractionType.QUEST_GIVER,
            confidence=0.8
        )
        
        response = self.interactor.determine_response(dialogue)
        assert response == ResponseType.ACCEPT
        
        # Test trainer
        dialogue.interaction_type = InteractionType.TRAINER
        dialogue.dialogue_text = "I can teach you new skills. Would you like to train?"
        response = self.interactor.determine_response(dialogue)
        assert response == ResponseType.TRAIN
    
    @patch('npc_interactor.click_at')
    def test_execute_response(self, mock_click):
        """Test response execution."""
        dialogue = NPCDialogue(
            npc_name="John",
            dialogue_text="Hello there!",
            response_options=["Accept", "Decline"],
            interaction_type=InteractionType.QUEST_GIVER,
            confidence=0.8
        )
        
        response = ResponseType.ACCEPT
        success = self.interactor.execute_response(response, dialogue)
        
        assert success is True
        mock_click.assert_called_once()
    
    @patch('npc_interactor.press_key')
    @patch('npc_interactor.wait')
    def test_execute_fallback_sequence(self, mock_wait, mock_press_key):
        """Test fallback sequence execution."""
        success = self.interactor.execute_fallback_sequence(InteractionType.QUEST_GIVER)
        
        assert success is True
        assert mock_press_key.call_count > 0
        assert mock_wait.call_count > 0
    
    @patch('npc_interactor.scan_npc_dialogue')
    def test_interact_with_npc(self, mock_scan):
        """Test NPC interaction."""
        # Mock successful dialogue
        mock_dialogue = NPCDialogue(
            npc_name="John",
            dialogue_text="Hello there!",
            response_options=["Accept"],
            interaction_type=InteractionType.QUEST_GIVER,
            confidence=0.8
        )
        mock_scan.return_value = mock_dialogue
        
        # Mock successful response execution
        with patch.object(self.interactor, 'execute_response', return_value=True):
            success = self.interactor.interact_with_npc("John")
            assert success is True
    
    def test_record_interaction_attempt(self):
        """Test interaction attempt recording."""
        initial_count = len(self.interactor.interaction_history)
        
        self.interactor.record_interaction_attempt(
            npc_name="John",
            interaction_type=InteractionType.QUEST_GIVER,
            ocr_text="Test dialogue",
            response=ResponseType.ACCEPT,
            success=True,
            response_time=1.0,
            fallback_used=False
        )
        
        assert len(self.interactor.interaction_history) == initial_count + 1
        assert self.interactor.stats['total_interactions'] > 0
        assert self.interactor.stats['successful_interactions'] > 0
    
    def test_get_interaction_statistics(self):
        """Test interaction statistics."""
        # Add some test data
        self.interactor.record_interaction_attempt(
            npc_name="John",
            interaction_type=InteractionType.QUEST_GIVER,
            ocr_text="Test dialogue",
            response=ResponseType.ACCEPT,
            success=True,
            response_time=1.0,
            fallback_used=False
        )
        
        stats = self.interactor.get_interaction_statistics()
        
        assert 'total_interactions' in stats
        assert 'successful_interactions' in stats
        assert 'failed_interactions' in stats
        assert 'fallback_usage' in stats
        assert 'average_response_time' in stats
    
    def test_clear_history(self):
        """Test history clearing."""
        # Add some test data
        self.interactor.record_interaction_attempt(
            npc_name="John",
            interaction_type=InteractionType.QUEST_GIVER,
            ocr_text="Test dialogue",
            response=ResponseType.ACCEPT,
            success=True,
            response_time=1.0,
            fallback_used=False
        )
        
        assert len(self.interactor.interaction_history) > 0
        
        self.interactor.clear_history()
        
        assert len(self.interactor.interaction_history) == 0
        assert self.interactor.stats['total_interactions'] == 0


class TestChatboxScanner:
    """Test Chatbox Scanner functionality."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.scanner = ChatboxScanner()
    
    def test_initialization(self):
        """Test ChatboxScanner initialization."""
        assert self.scanner is not None
        assert hasattr(self.scanner, 'config')
        assert hasattr(self.scanner, 'message_history')
        assert hasattr(self.scanner, 'stats')
    
    def test_load_config(self):
        """Test configuration loading."""
        config = self.scanner.load_config()
        assert isinstance(config, dict)
        assert 'message_patterns' in config
        assert 'npc_keywords' in config
        assert 'response_indicators' in config
    
    def test_parse_single_message(self):
        """Test single message parsing."""
        # Test NPC speech
        line = "John Smith: Hello there! I have a quest for you."
        message = self.scanner.parse_single_message(line)
        
        assert message is not None
        assert message.sender == "John Smith"
        assert message.message_type == MessageType.NPC_SPEECH
        assert "quest" in message.content.lower()
        assert message.requires_response is True
    
    def test_determine_message_type(self):
        """Test message type determination."""
        test_cases = [
            ("John: Hello", MessageType.NPC_SPEECH),
            ("Quest: Accept mission", MessageType.QUEST_MESSAGE),
            ("Trainer: Learn skills", MessageType.TRAINER_MESSAGE),
            ("Terminal: System access", MessageType.TERMINAL_MESSAGE),
            ("Vendor: Buy items", MessageType.VENDOR_MESSAGE),
            ("System: You gained XP", MessageType.SYSTEM_MESSAGE),
            ("Player123: Hello", MessageType.PLAYER_MESSAGE),
            ("Random text", MessageType.UNKNOWN)
        ]
        
        for line, expected_type in test_cases:
            message_type = self.scanner.determine_message_type(line)
            assert message_type == expected_type
    
    def test_extract_sender(self):
        """Test sender extraction."""
        test_cases = [
            ("John Smith: Hello", MessageType.NPC_SPEECH, "John Smith"),
            ("JOHN: Hello", MessageType.NPC_SPEECH, "JOHN"),
            ("Player123: Hello", MessageType.PLAYER_MESSAGE, "Player123"),
            ("System: Message", MessageType.SYSTEM_MESSAGE, "System"),
            ("Random text", MessageType.UNKNOWN, "Unknown")
        ]
        
        for line, message_type, expected_sender in test_cases:
            sender = self.scanner.extract_sender(line, message_type)
            assert sender == expected_sender
    
    def test_extract_content(self):
        """Test content extraction."""
        test_cases = [
            ("John Smith: Hello there!", "John Smith", "Hello there!"),
            ("Player123: Anyone want to group?", "Player123", "Anyone want to group?"),
            ("Random text", "Unknown", "Random text")
        ]
        
        for line, sender, expected_content in test_cases:
            content = self.scanner.extract_content(line, sender)
            assert content == expected_content
    
    def test_detect_response_requirement(self):
        """Test response requirement detection."""
        test_cases = [
            ("Accept the quest?", True),
            ("Would you like to train?", True),
            ("[Accept] [Decline]", True),
            ("1. Yes 2. No", True),
            ("You gained experience.", False),
            ("Hello there!", False)
        ]
        
        for line, expected_requires_response in test_cases:
            requires_response = self.scanner.detect_response_requirement(line)
            assert requires_response == expected_requires_response
    
    def test_calculate_message_confidence(self):
        """Test message confidence calculation."""
        line = "John Smith: Hello there! I have a quest for you."
        message_type = MessageType.NPC_SPEECH
        
        confidence = self.scanner.calculate_message_confidence(line, message_type)
        
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.5  # Should be reasonably confident
    
    def test_filter_new_messages(self):
        """Test message filtering."""
        # Add a message to history
        test_message = ChatMessage(
            sender="John",
            message_type=MessageType.NPC_SPEECH,
            content="Hello there!",
            timestamp=time.time(),
            confidence=0.8,
            requires_response=True
        )
        self.scanner.message_history.append(test_message)
        
        # Try to add the same message again
        messages = [test_message]
        new_messages = self.scanner.filter_new_messages(messages)
        
        # Should filter out duplicate
        assert len(new_messages) == 0
    
    def test_update_statistics(self):
        """Test statistics updating."""
        initial_total = self.scanner.stats['total_messages']
        
        message = ChatMessage(
            sender="John",
            message_type=MessageType.NPC_SPEECH,
            content="Hello there!",
            timestamp=time.time(),
            confidence=0.8,
            requires_response=True
        )
        
        self.scanner.update_statistics(message)
        
        assert self.scanner.stats['total_messages'] == initial_total + 1
        assert self.scanner.stats['npc_messages'] > 0
        assert self.scanner.stats['response_required'] > 0
    
    def test_get_npc_messages(self):
        """Test NPC message retrieval."""
        # Add some test messages
        npc_message = ChatMessage(
            sender="John",
            message_type=MessageType.NPC_SPEECH,
            content="Hello there!",
            timestamp=time.time(),
            confidence=0.8,
            requires_response=True
        )
        self.scanner.message_history.append(npc_message)
        
        npc_messages = self.scanner.get_npc_messages()
        assert len(npc_messages) > 0
        assert all(msg.message_type == MessageType.NPC_SPEECH for msg in npc_messages)
    
    def test_get_messages_requiring_response(self):
        """Test response-requiring message retrieval."""
        # Add some test messages
        response_message = ChatMessage(
            sender="John",
            message_type=MessageType.NPC_SPEECH,
            content="Accept quest?",
            timestamp=time.time(),
            confidence=0.8,
            requires_response=True
        )
        self.scanner.message_history.append(response_message)
        
        response_messages = self.scanner.get_messages_requiring_response()
        assert len(response_messages) > 0
        assert all(msg.requires_response for msg in response_messages)
    
    def test_get_chat_statistics(self):
        """Test chat statistics."""
        # Add some test data
        message = ChatMessage(
            sender="John",
            message_type=MessageType.NPC_SPEECH,
            content="Hello there!",
            timestamp=time.time(),
            confidence=0.8,
            requires_response=True
        )
        self.scanner.message_history.append(message)
        
        stats = self.scanner.get_chat_statistics()
        
        assert 'total_messages' in stats
        assert 'npc_messages' in stats
        assert 'quest_messages' in stats
        assert 'trainer_messages' in stats
        assert 'terminal_messages' in stats
        assert 'vendor_messages' in stats
        assert 'response_required' in stats
    
    def test_clear_history(self):
        """Test history clearing."""
        # Add some test data
        message = ChatMessage(
            sender="John",
            message_type=MessageType.NPC_SPEECH,
            content="Hello there!",
            timestamp=time.time(),
            confidence=0.8,
            requires_response=True
        )
        self.scanner.message_history.append(message)
        
        assert len(self.scanner.message_history) > 0
        
        self.scanner.clear_history()
        
        assert len(self.scanner.message_history) == 0
        assert self.scanner.stats['total_messages'] == 0


class TestIntegration:
    """Test integration between NPC interactor and chatbox scanner."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.interactor = NPCInteractor()
        self.scanner = ChatboxScanner()
    
    def test_integrated_workflow(self):
        """Test integrated workflow."""
        # Simulate chatbox message
        chat_message = ChatMessage(
            sender="John Smith",
            message_type=MessageType.NPC_SPEECH,
            content="Hello there! I have a quest for you. [Accept] [Decline]",
            timestamp=time.time(),
            confidence=0.8,
            requires_response=True
        )
        
        # Add to scanner history
        self.scanner.message_history.append(chat_message)
        
        # Parse dialogue from chat message
        dialogue_info = self.interactor.parse_dialogue_from_ocr(chat_message.content)
        assert dialogue_info is not None
        
        # Create dialogue object
        dialogue = NPCDialogue(
            npc_name=dialogue_info['npc_name'],
            dialogue_text=dialogue_info['dialogue_text'],
            response_options=dialogue_info['response_options'],
            interaction_type=dialogue_info['interaction_type'],
            confidence=dialogue_info['confidence']
        )
        
        # Determine response
        response = self.interactor.determine_response(dialogue)
        assert response == ResponseType.ACCEPT
        
        # Record interaction
        self.interactor.record_interaction_attempt(
            npc_name=dialogue.npc_name,
            interaction_type=dialogue.interaction_type,
            ocr_text=chat_message.content,
            response=response,
            success=True,
            response_time=1.0,
            fallback_used=False
        )
        
        # Verify statistics
        interactor_stats = self.interactor.get_interaction_statistics()
        scanner_stats = self.scanner.get_chat_statistics()
        
        assert interactor_stats['total_interactions'] > 0
        assert scanner_stats['npc_messages'] > 0


class TestGlobalFunctions:
    """Test global function wrappers."""
    
    def test_get_npc_interactor(self):
        """Test global NPC interactor getter."""
        interactor = get_npc_interactor()
        assert isinstance(interactor, NPCInteractor)
    
    def test_get_chatbox_scanner(self):
        """Test global chatbox scanner getter."""
        scanner = get_chatbox_scanner()
        assert isinstance(scanner, ChatboxScanner)
    
    @patch('npc_interactor.get_npc_interactor')
    def test_interact_with_npc(self, mock_get_interactor):
        """Test global interact_with_npc function."""
        mock_interactor = MagicMock()
        mock_interactor.interact_with_npc.return_value = True
        mock_get_interactor.return_value = mock_interactor
        
        success = interact_with_npc("John")
        assert success is True
        mock_interactor.interact_with_npc.assert_called_once_with("John", None)
    
    @patch('chatbox_scanner.get_chatbox_scanner')
    def test_scan_chatbox(self, mock_get_scanner):
        """Test global scan_chatbox function."""
        mock_scanner = MagicMock()
        mock_scanner.scan_chatbox.return_value = []
        mock_get_scanner.return_value = mock_scanner
        
        messages = scan_chatbox()
        assert isinstance(messages, list)
        mock_scanner.scan_chatbox.assert_called_once()
    
    @patch('npc_interactor.get_npc_interactor')
    def test_get_interaction_statistics(self, mock_get_interactor):
        """Test global get_interaction_statistics function."""
        mock_interactor = MagicMock()
        mock_interactor.get_interaction_statistics.return_value = {"total": 0}
        mock_get_interactor.return_value = mock_interactor
        
        stats = get_interaction_statistics()
        assert isinstance(stats, dict)
        mock_interactor.get_interaction_statistics.assert_called_once()
    
    @patch('chatbox_scanner.get_chatbox_scanner')
    def test_get_chat_statistics(self, mock_get_scanner):
        """Test global get_chat_statistics function."""
        mock_scanner = MagicMock()
        mock_scanner.get_chat_statistics.return_value = {"total": 0}
        mock_get_scanner.return_value = mock_scanner
        
        stats = get_chat_statistics()
        assert isinstance(stats, dict)
        mock_scanner.get_chat_statistics.assert_called_once()


class TestDataStructures:
    """Test data structures and enums."""
    
    def test_interaction_type_enum(self):
        """Test InteractionType enum."""
        assert InteractionType.QUEST_GIVER.value == "quest_giver"
        assert InteractionType.TRAINER.value == "trainer"
        assert InteractionType.TERMINAL.value == "terminal"
        assert InteractionType.VENDOR.value == "vendor"
        assert InteractionType.UNKNOWN.value == "unknown"
    
    def test_response_type_enum(self):
        """Test ResponseType enum."""
        assert ResponseType.ACCEPT.value == "accept"
        assert ResponseType.DECLINE.value == "decline"
        assert ResponseType.TRAIN.value == "train"
        assert ResponseType.BUY.value == "buy"
        assert ResponseType.SELL.value == "sell"
        assert ResponseType.CONTINUE.value == "continue"
        assert ResponseType.EXIT.value == "exit"
        assert ResponseType.CUSTOM.value == "custom"
    
    def test_message_type_enum(self):
        """Test MessageType enum."""
        assert MessageType.NPC_SPEECH.value == "npc_speech"
        assert MessageType.QUEST_MESSAGE.value == "quest_message"
        assert MessageType.TRAINER_MESSAGE.value == "trainer_message"
        assert MessageType.TERMINAL_MESSAGE.value == "terminal_message"
        assert MessageType.VENDOR_MESSAGE.value == "vendor_message"
        assert MessageType.SYSTEM_MESSAGE.value == "system_message"
        assert MessageType.PLAYER_MESSAGE.value == "player_message"
        assert MessageType.UNKNOWN.value == "unknown"
    
    def test_npc_dialogue_dataclass(self):
        """Test NPCDialogue dataclass."""
        dialogue = NPCDialogue(
            npc_name="John",
            dialogue_text="Hello there!",
            response_options=["Accept", "Decline"],
            interaction_type=InteractionType.QUEST_GIVER,
            confidence=0.8
        )
        
        assert dialogue.npc_name == "John"
        assert dialogue.dialogue_text == "Hello there!"
        assert len(dialogue.response_options) == 2
        assert dialogue.interaction_type == InteractionType.QUEST_GIVER
        assert dialogue.confidence == 0.8
    
    def test_chat_message_dataclass(self):
        """Test ChatMessage dataclass."""
        message = ChatMessage(
            sender="John",
            message_type=MessageType.NPC_SPEECH,
            content="Hello there!",
            timestamp=time.time(),
            confidence=0.8,
            requires_response=True
        )
        
        assert message.sender == "John"
        assert message.message_type == MessageType.NPC_SPEECH
        assert message.content == "Hello there!"
        assert message.requires_response is True
        assert message.confidence == 0.8
    
    def test_interaction_attempt_dataclass(self):
        """Test InteractionAttempt dataclass."""
        attempt = InteractionAttempt(
            npc_name="John",
            interaction_type=InteractionType.QUEST_GIVER,
            ocr_text="Test dialogue",
            detected_response=ResponseType.ACCEPT,
            success=True,
            timestamp=time.time(),
            fallback_used=False,
            response_time=1.0
        )
        
        assert attempt.npc_name == "John"
        assert attempt.interaction_type == InteractionType.QUEST_GIVER
        assert attempt.detected_response == ResponseType.ACCEPT
        assert attempt.success is True
        assert attempt.fallback_used is False
        assert attempt.response_time == 1.0


if __name__ == "__main__":
    pytest.main([__file__]) 