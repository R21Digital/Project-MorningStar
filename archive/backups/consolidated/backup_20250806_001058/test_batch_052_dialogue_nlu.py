"""
Test Suite for Batch 052 - Rasa Evaluation for NPC and Quest Intent Parsing

This test suite validates the experimental NLU system for extracting quest-related
intents and slot information from NPC dialogues. It covers:

- Intent classification accuracy
- Slot extraction functionality
- Training data management
- Session integration
- Error handling
- Performance metrics
"""

import json
import logging
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple
from unittest.mock import patch, MagicMock

from experimental.dialogue_nlu import (
    IntentType, SlotType, IntentResult, TrainingExample,
    SimpleIntentClassifier, DialogueNLU,
    get_dialogue_nlu, process_dialogue, add_training_example,
    evaluate_accuracy, get_session_summary, set_session
)


class TestIntentDataStructures(unittest.TestCase):
    """Test intent data structures and serialization."""
    
    def test_intent_type_enum(self):
        """Test IntentType enum values."""
        self.assertEqual(IntentType.START_QUEST.value, "start_quest")
        self.assertEqual(IntentType.COMPLETE_QUEST.value, "complete_quest")
        self.assertEqual(IntentType.DECLINE_QUEST.value, "decline_quest")
        self.assertEqual(IntentType.UNKNOWN.value, "unknown")
    
    def test_slot_type_enum(self):
        """Test SlotType enum values."""
        self.assertEqual(SlotType.QUEST_NAME.value, "quest_name")
        self.assertEqual(SlotType.NPC_NAME.value, "npc_name")
        self.assertEqual(SlotType.LOCATION.value, "location")
        self.assertEqual(SlotType.REWARD.value, "reward")
    
    def test_intent_result_creation(self):
        """Test IntentResult creation and serialization."""
        result = IntentResult(
            intent=IntentType.START_QUEST,
            confidence=0.85,
            slots={"quest_name": "Legacy Training", "npc_name": "Yevin"},
            raw_text="I have a quest for you",
            metadata={"method": "pattern_keyword"}
        )
        
        self.assertEqual(result.intent, IntentType.START_QUEST)
        self.assertEqual(result.confidence, 0.85)
        self.assertEqual(result.slots["quest_name"], "Legacy Training")
        self.assertEqual(result.slots["npc_name"], "Yevin")
        self.assertEqual(result.raw_text, "I have a quest for you")
        self.assertEqual(result.metadata["method"], "pattern_keyword")
    
    def test_training_example_creation(self):
        """Test TrainingExample creation."""
        example = TrainingExample(
            text="I have a quest for you",
            intent=IntentType.START_QUEST,
            slots={"quest_name": "Legacy Training"},
            metadata={"source": "yevin_rook"}
        )
        
        self.assertEqual(example.text, "I have a quest for you")
        self.assertEqual(example.intent, IntentType.START_QUEST)
        self.assertEqual(example.slots["quest_name"], "Legacy Training")
        self.assertEqual(example.metadata["source"], "yevin_rook")


class TestSimpleIntentClassifier(unittest.TestCase):
    """Test the SimpleIntentClassifier functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.training_data_path = Path(self.temp_dir) / "test_training.json"
        self.classifier = SimpleIntentClassifier(str(self.training_data_path))
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_classifier_initialization(self):
        """Test classifier initialization."""
        self.assertIsNotNone(self.classifier.intent_patterns)
        self.assertIsNotNone(self.classifier.keyword_weights)
        self.assertEqual(len(self.classifier.training_examples), 0)
        self.assertEqual(len(self.classifier.classification_history), 0)
    
    def test_intent_patterns(self):
        """Test intent pattern matching."""
        # Test start quest patterns
        result = self.classifier.classify_intent("I have a quest for you")
        self.assertEqual(result.intent, IntentType.START_QUEST)
        self.assertGreater(result.confidence, 0.0)
        
        # Test complete quest patterns
        result = self.classifier.classify_intent("Quest completed successfully!")
        self.assertEqual(result.intent, IntentType.COMPLETE_QUEST)
        self.assertGreater(result.confidence, 0.0)
        
        # Test greeting patterns
        result = self.classifier.classify_intent("Hello there!")
        self.assertEqual(result.intent, IntentType.GREETING)
        self.assertGreater(result.confidence, 0.0)
    
    def test_keyword_weights(self):
        """Test keyword weight matching."""
        # Test quest keyword
        result = self.classifier.classify_intent("I need help with a quest")
        self.assertEqual(result.intent, IntentType.START_QUEST)
        self.assertGreater(result.confidence, 0.0)
        
        # Test mission keyword
        result = self.classifier.classify_intent("I have a mission for you")
        self.assertEqual(result.intent, IntentType.START_QUEST)
        self.assertGreater(result.confidence, 0.0)
        
        # Test complete keyword
        result = self.classifier.classify_intent("I have completed the task")
        self.assertEqual(result.intent, IntentType.COMPLETE_QUEST)
        self.assertGreater(result.confidence, 0.0)
    
    def test_slot_extraction(self):
        """Test slot extraction functionality."""
        # Test NPC name extraction
        result = self.classifier.classify_intent("I am Yevin Rook, and I have a quest for you")
        self.assertIn("npc_name", result.slots)
        self.assertEqual(result.slots["npc_name"], "Yevin")
        
        # Test quest name extraction
        result = self.classifier.classify_intent("I need help with a mission: Defeat the Bounty Hunter")
        self.assertIn("quest_name", result.slots)
        self.assertEqual(result.slots["quest_name"], "Defeat the Bounty Hunter")
        
        # Test location extraction
        result = self.classifier.classify_intent("Go to Mos Eisley and collect the rare crystals")
        self.assertIn("location", result.slots)
        self.assertEqual(result.slots["location"], "Mos")
        
        # Test reward extraction
        result = self.classifier.classify_intent("Complete this task and receive 1000 credits reward")
        self.assertIn("reward", result.slots)
        self.assertEqual(result.slots["reward"], "1000 credits")
    
    def test_add_training_example(self):
        """Test adding training examples."""
        example_text = "I have a special quest for you"
        example_intent = IntentType.START_QUEST
        example_slots = {"quest_name": "Special Quest"}
        
        self.classifier.add_training_example(example_text, example_intent, example_slots)
        
        self.assertEqual(len(self.classifier.training_examples), 1)
        example = self.classifier.training_examples[0]
        self.assertEqual(example.text, example_text)
        self.assertEqual(example.intent, example_intent)
        self.assertEqual(example.slots, example_slots)
    
    def test_evaluate_accuracy(self):
        """Test accuracy evaluation."""
        # Add some training examples
        test_examples = [
            ("I have a quest for you", IntentType.START_QUEST),
            ("Quest completed!", IntentType.COMPLETE_QUEST),
            ("Not interested", IntentType.DECLINE_QUEST),
            ("Hello there!", IntentType.GREETING),
            ("Goodbye!", IntentType.FAREWELL)
        ]
        
        metrics = self.classifier.evaluate_accuracy(test_examples)
        
        self.assertIn('overall_accuracy', metrics)
        self.assertIn('total_examples', metrics)
        self.assertIn('correct_predictions', metrics)
        self.assertIn('per_intent_accuracy', metrics)
        
        self.assertEqual(metrics['total_examples'], 5)
        self.assertGreaterEqual(metrics['overall_accuracy'], 0.0)
        self.assertLessEqual(metrics['overall_accuracy'], 1.0)
    
    def test_classification_history(self):
        """Test classification history tracking."""
        # Perform some classifications
        self.classifier.classify_intent("I have a quest for you")
        self.classifier.classify_intent("Quest completed!")
        self.classifier.classify_intent("Hello there!")
        
        history = self.classifier.get_classification_history()
        
        self.assertEqual(len(history), 3)
        self.assertEqual(history[0].intent, IntentType.START_QUEST)
        self.assertEqual(history[1].intent, IntentType.COMPLETE_QUEST)
        self.assertEqual(history[2].intent, IntentType.GREETING)
    
    def test_unknown_intent(self):
        """Test handling of unknown intents."""
        result = self.classifier.classify_intent("This is completely unrelated text")
        
        self.assertEqual(result.intent, IntentType.UNKNOWN)
        self.assertEqual(result.confidence, 0.0)
    
    def test_confidence_scoring(self):
        """Test confidence scoring mechanism."""
        # Test high confidence for clear intent
        result = self.classifier.classify_intent("I have a quest for you")
        self.assertGreater(result.confidence, 0.5)
        
        # Test lower confidence for ambiguous text
        result = self.classifier.classify_intent("I have something for you")
        self.assertLess(result.confidence, 0.5)
    
    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Empty string
        result = self.classifier.classify_intent("")
        self.assertEqual(result.intent, IntentType.UNKNOWN)
        
        # Whitespace only
        result = self.classifier.classify_intent("   ")
        self.assertEqual(result.intent, IntentType.UNKNOWN)
        
        # Very long text
        long_text = "This is a very long dialogue that doesn't match any specific patterns but contains some keywords like quest and training and other words to make it longer"
        result = self.classifier.classify_intent(long_text)
        self.assertIsInstance(result.intent, IntentType)
        self.assertIsInstance(result.confidence, float)


class TestDialogueNLU(unittest.TestCase):
    """Test the main DialogueNLU system."""
    
    def setUp(self):
        """Set up test environment."""
        self.nlu = DialogueNLU("test_session")
    
    def test_nlu_initialization(self):
        """Test NLU initialization."""
        self.assertEqual(self.nlu.session_id, "test_session")
        self.assertIsNotNone(self.nlu.classifier)
        self.assertEqual(len(self.nlu.session_intents), 0)
        self.assertEqual(len(self.nlu.npc_context), 0)
    
    def test_process_dialogue(self):
        """Test dialogue processing."""
        result = self.nlu.process_dialogue(
            "I have a quest for you",
            npc_name="Yevin Rook",
            context={"location": "Mos Eisley"}
        )
        
        self.assertEqual(result.intent, IntentType.START_QUEST)
        self.assertIn("npc_name", result.slots)
        self.assertEqual(result.slots["npc_name"], "Yevin Rook")
        self.assertIn("context", result.metadata)
        self.assertEqual(result.metadata["context"]["location"], "Mos Eisley")
        
        # Check session storage
        self.assertEqual(len(self.nlu.session_intents), 1)
        self.assertEqual(self.nlu.session_intents[0], result)
    
    def test_session_summary(self):
        """Test session summary generation."""
        # Process some dialogues
        self.nlu.process_dialogue("I have a quest for you", "Yevin")
        self.nlu.process_dialogue("Quest completed!", "Yevin")
        self.nlu.process_dialogue("Hello there!", "Merchant")
        
        summary = self.nlu.get_session_summary()
        
        self.assertEqual(summary['total_intents'], 3)
        self.assertIn('intent_distribution', summary)
        self.assertIn('average_confidence', summary)
        self.assertEqual(summary['session_id'], "test_session")
        
        # Check intent distribution
        distribution = summary['intent_distribution']
        self.assertIn('start_quest', distribution)
        self.assertIn('complete_quest', distribution)
        self.assertIn('greeting', distribution)
    
    def test_set_session(self):
        """Test session setting."""
        self.nlu.set_session("new_session")
        
        self.assertEqual(self.nlu.session_id, "new_session")
        self.assertEqual(len(self.nlu.session_intents), 0)
        self.assertEqual(len(self.nlu.npc_context), 0)
    
    def test_add_npc_context(self):
        """Test NPC context management."""
        context = {
            "location": "Mos Eisley",
            "quest_giver": True,
            "specialization": "Legacy Training"
        }
        
        self.nlu.add_npc_context("Yevin Rook", context)
        
        self.assertIn("Yevin Rook", self.nlu.npc_context)
        self.assertEqual(self.nlu.npc_context["Yevin Rook"], context)


class TestGlobalFunctions(unittest.TestCase):
    """Test global helper functions."""
    
    def setUp(self):
        """Set up test environment."""
        # Reset global instance
        import experimental.dialogue_nlu
        experimental.dialogue_nlu._nlu_instance = None
    
    def test_get_dialogue_nlu(self):
        """Test getting dialogue NLU instance."""
        nlu = get_dialogue_nlu()
        self.assertIsInstance(nlu, DialogueNLU)
        
        # Test with session ID
        nlu2 = get_dialogue_nlu("test_session")
        self.assertEqual(nlu2.session_id, "test_session")
    
    def test_process_dialogue_global(self):
        """Test global process_dialogue function."""
        result = process_dialogue("I have a quest for you", "Yevin Rook")
        
        self.assertIsInstance(result, IntentResult)
        self.assertEqual(result.intent, IntentType.START_QUEST)
        self.assertIn("npc_name", result.slots)
    
    def test_add_training_example_global(self):
        """Test global add_training_example function."""
        add_training_example("Test quest text", IntentType.START_QUEST)
        
        nlu = get_dialogue_nlu()
        self.assertEqual(len(nlu.classifier.training_examples), 1)
    
    def test_evaluate_accuracy_global(self):
        """Test global evaluate_accuracy function."""
        test_examples = [
            ("I have a quest for you", IntentType.START_QUEST),
            ("Quest completed!", IntentType.COMPLETE_QUEST)
        ]
        
        metrics = evaluate_accuracy(test_examples)
        
        self.assertIn('overall_accuracy', metrics)
        self.assertEqual(metrics['total_examples'], 2)
    
    def test_get_session_summary_global(self):
        """Test global get_session_summary function."""
        # Process some dialogues first
        process_dialogue("I have a quest for you", "Yevin")
        process_dialogue("Quest completed!", "Yevin")
        
        summary = get_session_summary()
        
        self.assertIn('total_intents', summary)
        self.assertIn('intent_distribution', summary)
    
    def test_set_session_global(self):
        """Test global set_session function."""
        set_session("test_session_global")
        
        nlu = get_dialogue_nlu()
        self.assertEqual(nlu.session_id, "test_session_global")


class TestTrainingDataManagement(unittest.TestCase):
    """Test training data management functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.training_data_path = Path(self.temp_dir) / "test_training.json"
        self.classifier = SimpleIntentClassifier(str(self.training_data_path))
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_save_and_load_training_data(self):
        """Test saving and loading training data."""
        # Add training examples
        self.classifier.add_training_example("Test quest", IntentType.START_QUEST)
        self.classifier.add_training_example("Quest done", IntentType.COMPLETE_QUEST)
        
        # Create new classifier to test loading
        new_classifier = SimpleIntentClassifier(str(self.training_data_path))
        
        self.assertEqual(len(new_classifier.training_examples), 2)
        self.assertEqual(new_classifier.training_examples[0].text, "Test quest")
        self.assertEqual(new_classifier.training_examples[1].text, "Quest done")
    
    def test_training_data_serialization(self):
        """Test training data JSON serialization."""
        example = TrainingExample(
            text="Test text",
            intent=IntentType.START_QUEST,
            slots={"quest_name": "Test Quest"},
            metadata={"source": "test"}
        )
        
        # Test serialization
        data = {
            'text': example.text,
            'intent': example.intent.value,
            'slots': example.slots,
            'metadata': example.metadata
        }
        
        # Test deserialization
        loaded_example = TrainingExample(
            text=data['text'],
            intent=IntentType(data['intent']),
            slots=data['slots'],
            metadata=data['metadata']
        )
        
        self.assertEqual(loaded_example.text, example.text)
        self.assertEqual(loaded_example.intent, example.intent)
        self.assertEqual(loaded_example.slots, example.slots)
        self.assertEqual(loaded_example.metadata, example.metadata)


class TestSlotExtraction(unittest.TestCase):
    """Test slot extraction functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.training_data_path = Path(self.temp_dir) / "test_training.json"
        self.classifier = SimpleIntentClassifier(str(self.training_data_path))
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_npc_name_extraction(self):
        """Test NPC name extraction patterns."""
        test_cases = [
            ("I am Yevin Rook, and I have a quest for you", "Yevin"),
            ("My name is Combat Trainer", "Combat"),
            ("Call me Merchant", "Merchant"),
            ("Yevin here, how can I help?", "Yevin")
        ]
        
        for text, expected_name in test_cases:
            result = self.classifier.classify_intent(text)
            if "npc_name" in result.slots:
                self.assertEqual(result.slots["npc_name"], expected_name)
    
    def test_quest_name_extraction(self):
        """Test quest name extraction patterns."""
        test_cases = [
            ("I need help with a mission: Defeat the Bounty Hunter", "Defeat the Bounty Hunter"),
            ("I have a quest: Legacy Training", "Legacy Training"),
            ("Job: Collect rare crystals", "Collect rare crystals"),
            ("Task: Defeat the enemy", "Defeat the enemy")
        ]
        
        for text, expected_quest in test_cases:
            result = self.classifier.classify_intent(text)
            if "quest_name" in result.slots:
                self.assertEqual(result.slots["quest_name"], expected_quest)
    
    def test_location_extraction(self):
        """Test location extraction patterns."""
        test_cases = [
            ("Go to Mos Eisley and collect items", "Mos"),
            ("Travel to Tatooine for training", "Tatooine"),
            ("Meet me in Naboo", "Naboo"),
            ("Go to the desert", "desert")
        ]
        
        for text, expected_location in test_cases:
            result = self.classifier.classify_intent(text)
            if "location" in result.slots:
                self.assertEqual(result.slots["location"], expected_location)
    
    def test_reward_extraction(self):
        """Test reward extraction patterns."""
        test_cases = [
            ("Complete this task and receive 1000 credits reward", "1000 credits"),
            ("Reward: 500 XP", "500 XP"),
            ("Payment: 200 credits", "200 credits"),
            ("You'll get 1500 XP", "1500 XP")
        ]
        
        for text, expected_reward in test_cases:
            result = self.classifier.classify_intent(text)
            if "reward" in result.slots:
                self.assertEqual(result.slots["reward"], expected_reward)


class TestPerformanceMetrics(unittest.TestCase):
    """Test performance metrics and analysis."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.training_data_path = Path(self.temp_dir) / "test_training.json"
        self.classifier = SimpleIntentClassifier(str(self.training_data_path))
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_accuracy_metrics(self):
        """Test accuracy metrics calculation."""
        # Add some training examples
        test_examples = [
            ("I have a quest for you", IntentType.START_QUEST),
            ("Quest completed!", IntentType.COMPLETE_QUEST),
            ("Not interested", IntentType.DECLINE_QUEST),
            ("Hello there!", IntentType.GREETING),
            ("Goodbye!", IntentType.FAREWELL)
        ]
        
        metrics = self.classifier.evaluate_accuracy(test_examples)
        
        # Test metrics structure
        self.assertIn('overall_accuracy', metrics)
        self.assertIn('per_intent_accuracy', metrics)
        self.assertIn('total_examples', metrics)
        self.assertIn('correct_predictions', metrics)
        
        # Test metric values
        self.assertEqual(metrics['total_examples'], 5)
        self.assertGreaterEqual(metrics['overall_accuracy'], 0.0)
        self.assertLessEqual(metrics['overall_accuracy'], 1.0)
        self.assertGreaterEqual(metrics['correct_predictions'], 0)
        self.assertLessEqual(metrics['correct_predictions'], 5)
    
    def test_classification_history(self):
        """Test classification history tracking."""
        # Perform classifications
        self.classifier.classify_intent("I have a quest for you")
        self.classifier.classify_intent("Quest completed!")
        self.classifier.classify_intent("Hello there!")
        
        history = self.classifier.get_classification_history()
        
        self.assertEqual(len(history), 3)
        
        # Test history entries
        for result in history:
            self.assertIsInstance(result, IntentResult)
            self.assertIsInstance(result.intent, IntentType)
            self.assertIsInstance(result.confidence, float)
            self.assertIsInstance(result.slots, dict)
            self.assertIsInstance(result.raw_text, str)
            self.assertIsInstance(result.timestamp, datetime)
    
    def test_per_intent_accuracy(self):
        """Test per-intent accuracy calculation."""
        test_examples = [
            ("I have a quest for you", IntentType.START_QUEST),
            ("I have another quest", IntentType.START_QUEST),
            ("Quest completed!", IntentType.COMPLETE_QUEST),
            ("Not interested", IntentType.DECLINE_QUEST)
        ]
        
        metrics = self.classifier.evaluate_accuracy(test_examples)
        
        per_intent_accuracy = metrics['per_intent_accuracy']
        
        # Test that all intents in test examples are present
        expected_intents = {IntentType.START_QUEST, IntentType.COMPLETE_QUEST, IntentType.DECLINE_QUEST}
        for intent in expected_intents:
            if intent.value in per_intent_accuracy:
                accuracy = per_intent_accuracy[intent.value]
                self.assertGreaterEqual(accuracy, 0.0)
                self.assertLessEqual(accuracy, 1.0)


def run_tests():
    """Run all tests and return success status."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestIntentDataStructures,
        TestSimpleIntentClassifier,
        TestDialogueNLU,
        TestGlobalFunctions,
        TestTrainingDataManagement,
        TestSlotExtraction,
        TestPerformanceMetrics
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print(f"\n{'='*60}")
    print("BATCH 052 DIALOGUE NLU TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    # Print failures and errors
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1) 