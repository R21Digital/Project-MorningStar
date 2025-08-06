#!/usr/bin/env python3
"""
MS11 Batch 091 - AI Assistant Tests

This module provides comprehensive tests for the AI assistant
functionality, including data ingestion, content filtering, and response generation.
"""

import json
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import patch, MagicMock

from core.ai_assistant import (
    AIAssistant,
    AIDataIngestion,
    ContentFilter,
    AIDroidPersonality,
    ChatMessage,
    ChatSession
)
from core.chat_session_manager import ChatSessionManager

class TestAIDataIngestion(unittest.TestCase):
    """Test cases for AI data ingestion."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.test_dir, "data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create test data files
        self._create_test_data_files()
        
        self.ingestion = AIDataIngestion(self.data_dir)

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)

    def _create_test_data_files(self):
        """Create test data files."""
        # Quest database
        quest_data = {
            "test_quest": {
                "quest_id": "test_quest",
                "name": "Test Quest",
                "location": "test_location",
                "planet": "test_planet",
                "difficulty": "easy",
                "level_requirement": 1
            }
        }
        
        with open(os.path.join(self.data_dir, "quest_database.json"), 'w') as f:
            json.dump(quest_data, f)
        
        # Trainer data
        trainer_data = {
            "marksman": {
                "tatooine": {
                    "mos_eisley": {
                        "name": "Marksman Trainer",
                        "x": 3500,
                        "y": -4800,
                        "skills_taught": ["ranged_weapons"]
                    }
                }
            }
        }
        
        with open(os.path.join(self.data_dir, "trainers.yaml"), 'w') as f:
            import yaml
            yaml.dump(trainer_data, f)
        
        # Conversation logs
        conversation_dir = os.path.join(self.data_dir, "conversation_logs")
        os.makedirs(conversation_dir, exist_ok=True)
        
        conversation_data = {
            "session_id": "test_session",
            "user_id": "test_user",
            "messages": [
                {
                    "role": "user",
                    "content": "Where can I find a trainer?",
                    "timestamp": "2025-01-01T00:00:00"
                },
                {
                    "role": "assistant",
                    "content": "I can help you find trainers!",
                    "timestamp": "2025-01-01T00:00:01"
                }
            ]
        }
        
        with open(os.path.join(conversation_dir, "test_session.json"), 'w') as f:
            json.dump(conversation_data, f)

    def test_ingest_all_data(self):
        """Test complete data ingestion."""
        data = self.ingestion.ingest_all_data()
        
        self.assertIn('quests', data)
        self.assertIn('trainers', data)
        self.assertIn('lore', data)
        self.assertIn('conversations', data)
        
        self.assertEqual(len(data['quests']), 1)
        self.assertEqual(len(data['trainers']), 1)

    def test_ingest_quest_data(self):
        """Test quest data ingestion."""
        quest_data = self.ingestion._ingest_quest_data()
        
        self.assertIn('test_quest', quest_data)
        self.assertEqual(quest_data['test_quest']['name'], 'Test Quest')

    def test_ingest_trainer_data(self):
        """Test trainer data ingestion."""
        trainer_data = self.ingestion._ingest_trainer_data()
        
        self.assertIn('marksman', trainer_data)
        self.assertIn('tatooine', trainer_data['marksman'])

    def test_ingest_lore_data(self):
        """Test lore data ingestion."""
        lore_data = self.ingestion._ingest_lore_data()
        
        self.assertIn('factions', lore_data)
        self.assertIn('planets', lore_data)
        self.assertIn('races', lore_data)

    def test_anonymize_conversation(self):
        """Test conversation anonymization."""
        session_data = {
            "session_id": "test_session",
            "user_id": "test_user",
            "messages": [
                {
                    "role": "user",
                    "content": "Where can I find a trainer?",
                    "timestamp": "2025-01-01T00:00:00"
                }
            ]
        }
        
        anonymized = self.ingestion._anonymize_conversation(session_data)
        
        self.assertIn('session_id', anonymized)
        self.assertIn('messages', anonymized)
        self.assertTrue(anonymized['session_id'].startswith('anon_'))

    def test_contains_sensitive_content(self):
        """Test sensitive content detection."""
        # Test sensitive content
        sensitive_content = "How do I configure my MS11 bot?"
        self.assertTrue(self.ingestion._contains_sensitive_content(sensitive_content))
        
        # Test safe content
        safe_content = "Where can I find a trainer?"
        self.assertFalse(self.ingestion._contains_sensitive_content(safe_content))

    def test_sanitize_content(self):
        """Test content sanitization."""
        sensitive_content = "How do I configure my MS11 bot?"
        sanitized = self.ingestion._sanitize_content(sensitive_content)
        
        self.assertNotIn('MS11', sanitized)
        self.assertIn('game assistant', sanitized)

class TestContentFilter(unittest.TestCase):
    """Test cases for content filtering."""

    def setUp(self):
        """Set up test environment."""
        self.filter = ContentFilter()

    def test_contains_sensitive_content(self):
        """Test sensitive content detection."""
        # Test various sensitive terms
        sensitive_messages = [
            "How do I configure my MS11 bot?",
            "What automation settings should I use?",
            "Tell me about third-party tools",
            "My bot is stuck",
            "How do I use macros?"
        ]
        
        for message in sensitive_messages:
            self.assertTrue(self.filter.contains_sensitive_content(message))
        
        # Test safe messages
        safe_messages = [
            "Where can I find a trainer?",
            "Tell me about quests on Tatooine",
            "What professions are available?",
            "How do I travel between planets?"
        ]
        
        for message in safe_messages:
            self.assertFalse(self.filter.contains_sensitive_content(message))

    def test_sanitize_content(self):
        """Test content sanitization."""
        test_cases = [
            ("How do I configure my MS11 bot?", "game assistant"),
            ("What automation settings should I use?", "gameplay"),
            ("Tell me about third-party tools", "external"),
            ("My bot is stuck", "character"),
            ("How do I use macros?", "routine")
        ]
        
        for original, expected_replacement in test_cases:
            sanitized = self.filter.sanitize_content(original)
            self.assertIn(expected_replacement, sanitized)
            self.assertNotIn("MS11", sanitized)
            self.assertNotIn("bot", sanitized)

class TestAIDroidPersonality(unittest.TestCase):
    """Test cases for droid personality."""

    def setUp(self):
        """Set up test environment."""
        self.personality = AIDroidPersonality()

    def test_personality_attributes(self):
        """Test personality attributes."""
        self.assertEqual(self.personality.name, "AZ-L0N")
        self.assertEqual(self.personality.title, "Protocol Droid")
        self.assertIsInstance(self.personality.personality_traits, list)
        self.assertGreater(len(self.personality.personality_traits), 0)

    def test_greetings(self):
        """Test greeting generation."""
        greetings = []
        for _ in range(10):
            greeting = self.personality.get_greeting()
            greetings.append(greeting)
            self.assertIn("AZ-L0N", greeting)
        
        # Should have some variety
        unique_greetings = set(greetings)
        self.assertGreater(len(unique_greetings), 1)

    def test_farewells(self):
        """Test farewell generation."""
        farewells = []
        for _ in range(10):
            farewell = self.personality.get_farewell()
            farewells.append(farewell)
            self.assertIn("AZ-L0N", farewell)
        
        # Should have some variety
        unique_farewells = set(farewells)
        self.assertGreater(len(unique_farewells), 1)

    def test_confused_responses(self):
        """Test confused response generation."""
        responses = []
        for _ in range(10):
            response = self.personality.get_confused_response()
            responses.append(response)
            self.assertIn("I", response)  # Should be first person
        
        # Should have some variety
        unique_responses = set(responses)
        self.assertGreater(len(unique_responses), 1)

    def test_format_response(self):
        """Test response formatting."""
        content = "This is a test response."
        
        # Test without greeting
        formatted = self.personality.format_response(content, include_greeting=False)
        self.assertEqual(formatted, content)
        
        # Test with greeting (may or may not include greeting based on random)
        formatted = self.personality.format_response(content, include_greeting=True)
        self.assertIn(content, formatted)

class TestAIAssistant(unittest.TestCase):
    """Test cases for main AI assistant."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = os.path.join(self.test_dir, "data")
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create minimal test data
        self._create_minimal_test_data()
        
        self.assistant = AIAssistant(self.data_dir)

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)

    def _create_minimal_test_data(self):
        """Create minimal test data."""
        # Basic quest data
        quest_data = {
            "test_quest": {
                "name": "Test Quest",
                "location": "test_location",
                "planet": "test_planet",
                "difficulty": "easy",
                "level_requirement": 1
            }
        }
        
        with open(os.path.join(self.data_dir, "quest_database.json"), 'w') as f:
            json.dump(quest_data, f)
        
        # Basic trainer data
        trainer_data = {
            "marksman": {
                "tatooine": {
                    "mos_eisley": {
                        "name": "Marksman Trainer",
                        "skills_taught": ["ranged_weapons"]
                    }
                }
            }
        }
        
        with open(os.path.join(self.data_dir, "trainers.yaml"), 'w') as f:
            import yaml
            yaml.dump(trainer_data, f)

    def test_process_message_safe(self):
        """Test processing safe messages."""
        safe_messages = [
            "Where can I find a trainer?",
            "Tell me about quests",
            "What professions are available?",
            "How do I travel between planets?"
        ]
        
        for message in safe_messages:
            response = self.assistant.process_message(message)
            self.assertIsInstance(response, str)
            self.assertGreater(len(response), 0)

    def test_process_message_sensitive(self):
        """Test processing sensitive messages."""
        sensitive_messages = [
            "How do I configure my MS11 bot?",
            "What automation settings should I use?",
            "Tell me about third-party tools"
        ]
        
        for message in sensitive_messages:
            response = self.assistant.process_message(message)
            # Should return a confused response
            self.assertIn("I apologize", response)
            self.assertIn("not quite sure", response)

    def test_handle_quest_question(self):
        """Test quest question handling."""
        response = self.assistant._handle_quest_question("Tell me about quests")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

    def test_handle_trainer_question(self):
        """Test trainer question handling."""
        response = self.assistant._handle_trainer_question("Where can I find a trainer?")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

    def test_handle_profession_question(self):
        """Test profession question handling."""
        response = self.assistant._handle_profession_question("What professions are available?")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

    def test_handle_location_question(self):
        """Test location question handling."""
        response = self.assistant._handle_location_question("Where can I find Tatooine?")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

    def test_handle_lore_question(self):
        """Test lore question handling."""
        response = self.assistant._handle_lore_question("Tell me about the Rebel Alliance")
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)

class TestChatSessionManager(unittest.TestCase):
    """Test cases for chat session management."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.sessions_dir = os.path.join(self.test_dir, "sessions")
        os.makedirs(self.sessions_dir, exist_ok=True)
        
        self.session_manager = ChatSessionManager(self.sessions_dir)

    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)

    def test_create_session(self):
        """Test session creation."""
        session_id = self.session_manager.create_session("test_user", "general")
        
        self.assertIsInstance(session_id, str)
        self.assertGreater(len(session_id), 0)
        
        session = self.session_manager.get_session(session_id)
        self.assertIsNotNone(session)
        self.assertEqual(session.user_id, "test_user")
        self.assertEqual(session.mode, "general")

    def test_add_message(self):
        """Test message addition."""
        session_id = self.session_manager.create_session("test_user")
        
        success = self.session_manager.add_message(session_id, "user", "Hello")
        self.assertTrue(success)
        
        session = self.session_manager.get_session(session_id)
        self.assertEqual(len(session.messages), 1)
        self.assertEqual(session.messages[0].content, "Hello")

    def test_process_user_message(self):
        """Test user message processing."""
        session_id = self.session_manager.create_session("test_user")
        
        response = self.session_manager.process_user_message(session_id, "Where can I find a trainer?")
        
        self.assertIsInstance(response, str)
        self.assertGreater(len(response), 0)
        
        session = self.session_manager.get_session(session_id)
        self.assertEqual(len(session.messages), 2)  # User message + AI response

    def test_get_session_history(self):
        """Test session history retrieval."""
        session_id = self.session_manager.create_session("test_user")
        self.session_manager.add_message(session_id, "user", "Hello")
        self.session_manager.add_message(session_id, "assistant", "Hi there!")
        
        history = self.session_manager.get_session_history(session_id)
        
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]['role'], 'user')
        self.assertEqual(history[1]['role'], 'assistant')

    def test_list_sessions(self):
        """Test session listing."""
        # Create multiple sessions
        session_ids = []
        for i in range(3):
            session_id = self.session_manager.create_session(f"user_{i}")
            session_ids.append(session_id)
        
        sessions = self.session_manager.list_sessions()
        
        self.assertGreaterEqual(len(sessions), 3)
        for session in sessions:
            self.assertIn('session_id', session)
            self.assertIn('user_id', session)
            self.assertIn('start_time', session)

    def test_delete_session(self):
        """Test session deletion."""
        session_id = self.session_manager.create_session("test_user")
        
        # Verify session exists
        session = self.session_manager.get_session(session_id)
        self.assertIsNotNone(session)
        
        # Delete session
        success = self.session_manager.delete_session(session_id)
        self.assertTrue(success)
        
        # Verify session is gone
        session = self.session_manager.get_session(session_id)
        self.assertIsNone(session)

    def test_get_session_stats(self):
        """Test session statistics."""
        # Create some sessions
        for i in range(3):
            session_id = self.session_manager.create_session(f"user_{i}")
            self.session_manager.add_message(session_id, "user", f"Message {i}")
        
        stats = self.session_manager.get_session_stats()
        
        self.assertIn('active_sessions', stats)
        self.assertIn('total_sessions', stats)
        self.assertIn('total_messages', stats)
        self.assertGreaterEqual(stats['active_sessions'], 3)

def run_tests():
    """Run all tests and provide summary."""
    print("MS11 Batch 091 - AI Assistant Tests")
    print("=" * 50)

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestAIDataIngestion,
        TestContentFilter,
        TestAIDroidPersonality,
        TestAIAssistant,
        TestChatSessionManager
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")

    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")

    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall result: {'PASSED' if success else 'FAILED'}")

    return success

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1) 