#!/usr/bin/env python3
"""
Batch 140 - Quest Completion Verifier Tests

Comprehensive test suite for the quest completion verification system.
Tests OCR functionality, memory-based verification, caching, and integration.
"""

import json
import logging
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List

# Import the quest completion verifier
from core.quest_completion_verifier import (
    QuestCompletionVerifier,
    QuestVerificationResult,
    QuestChainVerificationResult,
    get_quest_verifier,
    verify_quest_completion,
    verify_quest_chain_completion,
    should_skip_quest,
    should_skip_chain,
    get_next_pending_quest
)


class TestQuestCompletionVerifier(unittest.TestCase):
    """Test cases for QuestCompletionVerifier class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'min_confidence': 70.0,
            'retry_attempts': 2,
            'retry_delay': 0.1,
            'cache_duration': 60,
            'quest_log_regions': {
                'main_quest_area': (100, 200, 800, 600),
                'quest_status_area': (900, 200, 300, 600)
            },
            'completion_keywords': [
                'completed', 'finished', 'done', 'accomplished'
            ]
        }
        
        # Create temporary quest log file
        self.temp_dir = tempfile.mkdtemp()
        self.quest_log_path = Path(self.temp_dir) / "quest_log.txt"
        
        # Mock OCR engine
        self.mock_ocr_engine = Mock()
        self.mock_ocr_result = Mock()
        self.mock_ocr_result.text = "Legacy Quest 1: Introduction - Completed"
        self.mock_ocr_result.confidence = 85.0
        self.mock_ocr_engine.extract_text.return_value = self.mock_ocr_result
        
        # Initialize verifier with mocked components
        with patch('core.quest_completion_verifier.get_ocr_engine', return_value=self.mock_ocr_engine):
            with patch('core.quest_completion_verifier.capture_screen', return_value=Mock()):
                with patch('core.quest_completion_verifier.read_saved_quest_log', return_value=[]):
                    self.verifier = QuestCompletionVerifier(self.config)
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temporary files
        if self.quest_log_path.exists():
            self.quest_log_path.unlink()
        Path(self.temp_dir).rmdir()
    
    def test_verifier_initialization(self):
        """Test verifier initialization with configuration."""
        self.assertIsNotNone(self.verifier)
        self.assertEqual(self.verifier.config, self.config)
        self.assertEqual(self.verifier.min_confidence, 70.0)
        self.assertEqual(self.verifier.retry_attempts, 2)
        self.assertEqual(self.verifier.cache_duration, 60)
    
    def test_verify_quest_completion_ocr_success(self):
        """Test OCR-based quest completion verification with success."""
        quest_name = "Legacy Quest 1: Introduction"
        
        # Mock OCR to return completion result
        self.mock_ocr_result.text = f"{quest_name} - Completed"
        self.mock_ocr_result.confidence = 85.0
        
        result = self.verifier.verify_quest_completion(quest_name)
        
        self.assertIsInstance(result, QuestVerificationResult)
        self.assertEqual(result.quest_name, quest_name)
        self.assertTrue(result.is_completed)
        self.assertEqual(result.confidence, 85.0)
        self.assertIn("ocr", result.method)
    
    def test_verify_quest_completion_ocr_failure(self):
        """Test OCR-based quest completion verification with failure."""
        quest_name = "Non-existent Quest"
        
        # Mock OCR to return no completion
        self.mock_ocr_result.text = "Some other quest text"
        self.mock_ocr_result.confidence = 50.0
        
        result = self.verifier.verify_quest_completion(quest_name)
        
        self.assertIsInstance(result, QuestVerificationResult)
        self.assertEqual(result.quest_name, quest_name)
        self.assertFalse(result.is_completed)
        self.assertEqual(result.confidence, 0.0)
    
    def test_verify_quest_completion_memory_success(self):
        """Test memory-based quest completion verification with success."""
        quest_name = "Legacy Quest 1: Introduction"
        
        # Mock quest log with completion
        quest_log_lines = [
            f"{quest_name} - Completed",
            "Some other quest - In Progress"
        ]
        
        with patch('core.quest_completion_verifier.read_saved_quest_log', return_value=quest_log_lines):
            result = self.verifier.verify_quest_completion(quest_name)
        
        self.assertIsInstance(result, QuestVerificationResult)
        self.assertEqual(result.quest_name, quest_name)
        self.assertTrue(result.is_completed)
        self.assertEqual(result.confidence, 80.0)
        self.assertEqual(result.method, "memory_based")
    
    def test_verify_quest_completion_memory_failure(self):
        """Test memory-based quest completion verification with failure."""
        quest_name = "Non-existent Quest"
        
        # Mock quest log without completion
        quest_log_lines = [
            "Some other quest - Completed",
            "Another quest - In Progress"
        ]
        
        with patch('core.quest_completion_verifier.read_saved_quest_log', return_value=quest_log_lines):
            result = self.verifier.verify_quest_completion(quest_name)
        
        self.assertIsInstance(result, QuestVerificationResult)
        self.assertEqual(result.quest_name, quest_name)
        self.assertFalse(result.is_completed)
        self.assertEqual(result.confidence, 0.0)
    
    def test_verify_quest_chain_completion(self):
        """Test quest chain completion verification."""
        chain_id = "legacy"
        quest_names = [
            "Legacy Quest 1: Introduction",
            "Legacy Quest 2: Training",
            "Legacy Quest 3: Final Test"
        ]
        
        # Mock individual quest verifications
        with patch.object(self.verifier, 'verify_quest_completion') as mock_verify:
            mock_verify.side_effect = [
                QuestVerificationResult(
                    quest_name=quest_names[0],
                    is_completed=True,
                    confidence=85.0,
                    method="ocr",
                    verification_time=0.1,
                    quest_log_text="Completed",
                    matched_keywords=["completed"],
                    chain_id=chain_id
                ),
                QuestVerificationResult(
                    quest_name=quest_names[1],
                    is_completed=False,
                    confidence=0.0,
                    method="ocr",
                    verification_time=0.1,
                    quest_log_text="In Progress",
                    matched_keywords=[],
                    chain_id=chain_id
                ),
                QuestVerificationResult(
                    quest_name=quest_names[2],
                    is_completed=True,
                    confidence=90.0,
                    method="ocr",
                    verification_time=0.1,
                    quest_log_text="Completed",
                    matched_keywords=["completed"],
                    chain_id=chain_id
                )
            ]
            
            result = self.verifier.verify_quest_chain_completion(chain_id, quest_names)
        
        self.assertIsInstance(result, QuestChainVerificationResult)
        self.assertEqual(result.chain_id, chain_id)
        self.assertEqual(result.total_quests, 3)
        self.assertEqual(result.completed_quests, 2)
        self.assertEqual(result.completion_percentage, 66.67)
        self.assertFalse(result.is_fully_completed)
        self.assertEqual(len(result.completed_quests_list), 2)
        self.assertEqual(len(result.pending_quests), 1)
    
    def test_verify_quest_chain_completion_fully_completed(self):
        """Test quest chain completion verification when fully completed."""
        chain_id = "daily"
        quest_names = ["Daily Quest 1", "Daily Quest 2"]
        
        # Mock all quests as completed
        with patch.object(self.verifier, 'verify_quest_completion') as mock_verify:
            mock_verify.side_effect = [
                QuestVerificationResult(
                    quest_name=quest_names[0],
                    is_completed=True,
                    confidence=85.0,
                    method="ocr",
                    verification_time=0.1,
                    quest_log_text="Completed",
                    matched_keywords=["completed"],
                    chain_id=chain_id
                ),
                QuestVerificationResult(
                    quest_name=quest_names[1],
                    is_completed=True,
                    confidence=90.0,
                    method="ocr",
                    verification_time=0.1,
                    quest_log_text="Completed",
                    matched_keywords=["completed"],
                    chain_id=chain_id
                )
            ]
            
            result = self.verifier.verify_quest_chain_completion(chain_id, quest_names)
        
        self.assertTrue(result.is_fully_completed)
        self.assertEqual(result.completion_percentage, 100.0)
        self.assertEqual(len(result.pending_quests), 0)
    
    def test_caching_system(self):
        """Test the caching system for performance."""
        quest_name = "Test Quest"
        
        # First verification (cache miss)
        with patch.object(self.verifier, '_verify_quest_completion_ocr') as mock_ocr:
            mock_ocr.return_value = QuestVerificationResult(
                quest_name=quest_name,
                is_completed=True,
                confidence=85.0,
                method="ocr",
                verification_time=0.1,
                quest_log_text="Completed",
                matched_keywords=["completed"]
            )
            
            result1 = self.verifier.verify_quest_completion(quest_name)
        
        # Second verification (should use cache)
        result2 = self.verifier.verify_quest_completion(quest_name)
        
        # Results should be identical
        self.assertEqual(result1.quest_name, result2.quest_name)
        self.assertEqual(result1.is_completed, result2.is_completed)
        self.assertEqual(result1.confidence, result2.confidence)
        
        # Clear cache
        self.verifier.clear_cache()
        self.assertEqual(len(self.verifier.verification_cache), 0)
    
    def test_should_skip_quest(self):
        """Test quest skip logic."""
        quest_name = "Test Quest"
        
        # Mock completed quest
        with patch.object(self.verifier, 'verify_quest_completion') as mock_verify:
            mock_verify.return_value = QuestVerificationResult(
                quest_name=quest_name,
                is_completed=True,
                confidence=85.0,
                method="ocr",
                verification_time=0.1,
                quest_log_text="Completed",
                matched_keywords=["completed"]
            )
            
            should_skip = self.verifier.should_skip_quest(quest_name, prompt_user=False)
            self.assertTrue(should_skip)
        
        # Mock incomplete quest
        with patch.object(self.verifier, 'verify_quest_completion') as mock_verify:
            mock_verify.return_value = QuestVerificationResult(
                quest_name=quest_name,
                is_completed=False,
                confidence=0.0,
                method="ocr",
                verification_time=0.1,
                quest_log_text="In Progress",
                matched_keywords=[]
            )
            
            should_skip = self.verifier.should_skip_quest(quest_name, prompt_user=False)
            self.assertFalse(should_skip)
    
    def test_should_skip_chain(self):
        """Test chain skip logic."""
        chain_id = "test_chain"
        
        # Mock fully completed chain
        with patch.object(self.verifier, 'verify_quest_chain_completion') as mock_verify:
            mock_verify.return_value = QuestChainVerificationResult(
                chain_id=chain_id,
                total_quests=3,
                completed_quests=3,
                completion_percentage=100.0,
                is_fully_completed=True,
                pending_quests=[],
                completed_quests_list=["Quest 1", "Quest 2", "Quest 3"],
                verification_time=0.1
            )
            
            should_skip = self.verifier.should_skip_chain(chain_id, prompt_user=False)
            self.assertTrue(should_skip)
        
        # Mock incomplete chain
        with patch.object(self.verifier, 'verify_quest_chain_completion') as mock_verify:
            mock_verify.return_value = QuestChainVerificationResult(
                chain_id=chain_id,
                total_quests=3,
                completed_quests=1,
                completion_percentage=33.33,
                is_fully_completed=False,
                pending_quests=["Quest 2", "Quest 3"],
                completed_quests_list=["Quest 1"],
                verification_time=0.1
            )
            
            should_skip = self.verifier.should_skip_chain(chain_id, prompt_user=False)
            self.assertFalse(should_skip)
    
    def test_get_next_pending_quest(self):
        """Test getting next pending quest in chain."""
        chain_id = "test_chain"
        
        # Mock chain with pending quests
        with patch.object(self.verifier, 'verify_quest_chain_completion') as mock_verify:
            mock_verify.return_value = QuestChainVerificationResult(
                chain_id=chain_id,
                total_quests=3,
                completed_quests=1,
                completion_percentage=33.33,
                is_fully_completed=False,
                pending_quests=["Quest 2", "Quest 3"],
                completed_quests_list=["Quest 1"],
                verification_time=0.1
            )
            
            next_quest = self.verifier.get_next_pending_quest(chain_id)
            self.assertEqual(next_quest, "Quest 2")
        
        # Mock fully completed chain
        with patch.object(self.verifier, 'verify_quest_chain_completion') as mock_verify:
            mock_verify.return_value = QuestChainVerificationResult(
                chain_id=chain_id,
                total_quests=3,
                completed_quests=3,
                completion_percentage=100.0,
                is_fully_completed=True,
                pending_quests=[],
                completed_quests_list=["Quest 1", "Quest 2", "Quest 3"],
                verification_time=0.1
            )
            
            next_quest = self.verifier.get_next_pending_quest(chain_id)
            self.assertIsNone(next_quest)
    
    def test_check_quest_completion_in_text(self):
        """Test quest completion detection in text."""
        quest_name = "Test Quest"
        
        # Test completion detection
        completion_text = f"{quest_name} - Completed successfully"
        self.assertTrue(self.verifier._check_quest_completion_in_text(completion_text, quest_name))
        
        # Test no completion
        incomplete_text = f"{quest_name} - In Progress"
        self.assertFalse(self.verifier._check_quest_completion_in_text(incomplete_text, quest_name))
        
        # Test quest name not found
        other_text = "Some other quest - Completed"
        self.assertFalse(self.verifier._check_quest_completion_in_text(other_text, quest_name))
    
    def test_infer_chain_quests(self):
        """Test chain quest inference."""
        # Test known chain
        legacy_quests = self.verifier._infer_chain_quests("legacy")
        self.assertIsInstance(legacy_quests, list)
        self.assertGreater(len(legacy_quests), 0)
        
        # Test unknown chain
        unknown_quests = self.verifier._infer_chain_quests("unknown_chain")
        self.assertEqual(unknown_quests, [])
    
    def test_error_handling(self):
        """Test error handling in verification."""
        quest_name = "Test Quest"
        
        # Mock OCR error
        with patch.object(self.verifier.ocr_engine, 'extract_text', side_effect=Exception("OCR Error")):
            result = self.verifier.verify_quest_completion(quest_name)
            
            self.assertIsInstance(result, QuestVerificationResult)
            self.assertEqual(result.quest_name, quest_name)
            self.assertFalse(result.is_completed)
            self.assertEqual(result.confidence, 0.0)
    
    def test_force_refresh_cache(self):
        """Test force refresh of verification cache."""
        quest_name = "Test Quest"
        
        # First verification
        with patch.object(self.verifier, '_verify_quest_completion_ocr') as mock_ocr:
            mock_ocr.return_value = QuestVerificationResult(
                quest_name=quest_name,
                is_completed=True,
                confidence=85.0,
                method="ocr",
                verification_time=0.1,
                quest_log_text="Completed",
                matched_keywords=["completed"]
            )
            
            result1 = self.verifier.verify_quest_completion(quest_name)
        
        # Force refresh verification
        with patch.object(self.verifier, '_verify_quest_completion_ocr') as mock_ocr:
            mock_ocr.return_value = QuestVerificationResult(
                quest_name=quest_name,
                is_completed=False,
                confidence=0.0,
                method="ocr",
                verification_time=0.1,
                quest_log_text="In Progress",
                matched_keywords=[]
            )
            
            result2 = self.verifier.verify_quest_completion(quest_name, force_refresh=True)
        
        # Results should be different due to force refresh
        self.assertNotEqual(result1.is_completed, result2.is_completed)


class TestQuestCompletionVerifierIntegration(unittest.TestCase):
    """Integration tests for quest completion verifier."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        self.config = {
            'min_confidence': 70.0,
            'retry_attempts': 2,
            'retry_delay': 0.1,
            'cache_duration': 60
        }
    
    @patch('core.quest_completion_verifier.get_ocr_engine')
    @patch('core.quest_completion_verifier.capture_screen')
    @patch('core.quest_completion_verifier.read_saved_quest_log')
    def test_integration_with_quest_system(self, mock_read_log, mock_capture, mock_ocr):
        """Test integration with existing quest system."""
        # Mock OCR engine
        mock_ocr_engine = Mock()
        mock_ocr_result = Mock()
        mock_ocr_result.text = "Legacy Quest 1: Introduction - Completed"
        mock_ocr_result.confidence = 85.0
        mock_ocr_engine.extract_text.return_value = mock_ocr_result
        mock_ocr.return_value = mock_ocr_engine
        
        # Mock screen capture
        mock_capture.return_value = Mock()
        
        # Mock quest log
        mock_read_log.return_value = []
        
        # Test integration
        verifier = QuestCompletionVerifier(self.config)
        
        # Test quest verification
        result = verifier.verify_quest_completion("Legacy Quest 1: Introduction")
        self.assertIsInstance(result, QuestVerificationResult)
        
        # Test chain verification
        chain_result = verifier.verify_quest_chain_completion("legacy")
        self.assertIsInstance(chain_result, QuestChainVerificationResult)
    
    def test_global_functions(self):
        """Test global convenience functions."""
        # Test get_quest_verifier
        verifier1 = get_quest_verifier()
        verifier2 = get_quest_verifier()
        self.assertIs(verifier1, verifier2)  # Should be singleton
        
        # Test convenience functions with mocked verifier
        with patch('core.quest_completion_verifier.get_quest_verifier') as mock_get:
            mock_verifier = Mock()
            mock_get.return_value = mock_verifier
            
            # Test verify_quest_completion
            verify_quest_completion("Test Quest")
            mock_verifier.verify_quest_completion.assert_called_once_with("Test Quest", None)
            
            # Test verify_quest_chain_completion
            verify_quest_chain_completion("test_chain")
            mock_verifier.verify_quest_chain_completion.assert_called_once_with("test_chain", None)
            
            # Test should_skip_quest
            should_skip_quest("Test Quest")
            mock_verifier.should_skip_quest.assert_called_once_with("Test Quest", None, False)
            
            # Test should_skip_chain
            should_skip_chain("test_chain")
            mock_verifier.should_skip_chain.assert_called_once_with("test_chain", False)
            
            # Test get_next_pending_quest
            get_next_pending_quest("test_chain")
            mock_verifier.get_next_pending_quest.assert_called_once_with("test_chain")


def run_tests():
    """Run all tests."""
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)
    
    # Run tests
    unittest.main(verbosity=2)


if __name__ == "__main__":
    run_tests() 