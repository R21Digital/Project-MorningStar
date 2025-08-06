#!/usr/bin/env python3
"""
Test Suite for Batch 118 – Session Upload Bridge to SWGDB

This file contains comprehensive unit and integration tests for all components
developed in Batch 118, including session serialization, SWGDB API integration,
upload management, and log viewing functionality.
"""

import json
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
import unittest

# Import our modules
from bridge.session_uploader import SessionUploader, UploadConfig
from swgdb_api.push_session_data import SWGDBAPIClient, SWGDBUploadManager
from core.log_serializer import SessionLogSerializer
from data.sessions.log_viewer import SessionLogViewer


class TestSessionLogSerializer(unittest.TestCase):
    """Test the session log serializer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.serializer = SessionLogSerializer()
        self.sample_session = {
            "session_id": "test_session_123",
            "start_time": "2025-01-01T10:00:00",
            "end_time": "2025-01-01T12:00:00",
            "duration_minutes": 120,
            "character_name": "TestCharacter",
            "mode": "quest",
            "xp": {
                "start": 1000,
                "end": 1500,
                "gained": 500
            },
            "credits": {
                "start": 10000,
                "end": 12000,
                "gained": 2000
            },
            "quests_completed": ["Quest1", "Quest2"],
            "locations_visited": [
                {
                    "planet": "Tatooine",
                    "city": "Mos Eisley",
                    "arrival_time": "2025-01-01T10:00:00",
                    "duration_minutes": 30
                }
            ],
            "communication_events": [
                {
                    "timestamp": "2025-01-01T10:30:00",
                    "event_type": "whisper",
                    "sender": "Player1",
                    "message": "Hello there!",
                    "response_sent": True
                }
            ],
            "player_encounters": [
                {
                    "player_name": "Player2",
                    "timestamp": "2025-01-01T10:45:00",
                    "location": "Tatooine - Mos Eisley",
                    "distance": 15.5,
                    "interaction_type": "detected"
                }
            ],
            "guild_alerts": [
                {
                    "timestamp": "2025-01-01T11:00:00",
                    "sender": "GuildLeader",
                    "message": "Guild meeting tonight",
                    "alert_type": "guild_whisper",
                    "priority": "medium",
                    "auto_reply_sent": True
                }
            ],
            "actions": [
                {"time": "2025-01-01T10:00:00", "action": "Session started"},
                {"time": "2025-01-01T10:15:00", "action": "Completed quest: Quest1"},
                {"time": "2025-01-01T11:30:00", "action": "Completed quest: Quest2"}
            ],
            "performance_metrics": {
                "session_duration_minutes": 120,
                "total_actions": 3
            }
        }
    
    def test_serialize_session_basic(self):
        """Test basic session serialization."""
        serialized = self.serializer.serialize_session(self.sample_session)
        
        # Check basic structure
        self.assertIn("session_id", serialized)
        self.assertIn("character_name", serialized)
        self.assertIn("duration_minutes", serialized)
        self.assertIn("xp_data", serialized)
        self.assertIn("credit_data", serialized)
        self.assertIn("quest_data", serialized)
        self.assertIn("location_data", serialized)
        self.assertIn("event_data", serialized)
        self.assertIn("performance_metrics", serialized)
        self.assertIn("metadata", serialized)
        
        # Check values
        self.assertEqual(serialized["session_id"], "test_session_123")
        self.assertEqual(serialized["character_name"], "TestCharacter")
        self.assertEqual(serialized["duration_minutes"], 120.0)
    
    def test_serialize_xp_data(self):
        """Test XP data serialization."""
        serialized = self.serializer.serialize_session(self.sample_session)
        xp_data = serialized["xp_data"]
        
        self.assertEqual(xp_data["total_xp_gained"], 500)
        self.assertEqual(xp_data["xp_per_hour"], 250.0)  # 500 XP / 2 hours
        self.assertIn("xp_events", xp_data)
        self.assertIn("profession_breakdown", xp_data)
        self.assertIn("skill_breakdown", xp_data)
        self.assertIn("source_breakdown", xp_data)
    
    def test_serialize_credit_data(self):
        """Test credit data serialization."""
        serialized = self.serializer.serialize_session(self.sample_session)
        credit_data = serialized["credit_data"]
        
        self.assertEqual(credit_data["total_credits_gained"], 2000)
        self.assertEqual(credit_data["credits_per_hour"], 1000.0)  # 2000 credits / 2 hours
        self.assertIn("credit_events", credit_data)
        self.assertIn("balance_history", credit_data)
    
    def test_serialize_quest_data(self):
        """Test quest data serialization."""
        serialized = self.serializer.serialize_session(self.sample_session)
        quest_data = serialized["quest_data"]
        
        self.assertEqual(quest_data["total_quests_completed"], 2)
        self.assertEqual(quest_data["quests_per_hour"], 1.0)  # 2 quests / 2 hours
        self.assertIn("quest_events", quest_data)
        self.assertIn("quest_types", quest_data)
        self.assertIn("reward_types", quest_data)
    
    def test_serialize_location_data(self):
        """Test location data serialization."""
        serialized = self.serializer.serialize_session(self.sample_session)
        location_data = serialized["location_data"]
        
        self.assertEqual(location_data["total_locations_visited"], 1)
        self.assertIn("Tatooine", location_data["unique_planets"])
        self.assertIn("Mos Eisley", location_data["unique_cities"])
        self.assertEqual(location_data["travel_time_minutes"], 30.0)
        self.assertIn("location_events", location_data)
    
    def test_serialize_event_data(self):
        """Test event data serialization."""
        serialized = self.serializer.serialize_session(self.sample_session)
        event_data = serialized["event_data"]
        
        self.assertGreater(event_data["total_events"], 0)
        self.assertIn("communication_events", event_data)
        self.assertIn("player_encounters", event_data)
        self.assertIn("guild_alerts", event_data)
        self.assertIn("afk_periods", event_data)
        self.assertIn("stuck_events", event_data)
        self.assertIn("event_types", event_data)
    
    def test_sanitize_communication_events(self):
        """Test communication event sanitization."""
        sensitive_session = self.sample_session.copy()
        sensitive_session["communication_events"] = [
            {
                "timestamp": "2025-01-01T10:30:00",
                "event_type": "whisper",
                "sender": "Player1",
                "message": "My password is secret123",
                "response_sent": True
            }
        ]
        
        serialized = self.serializer.serialize_session(sensitive_session)
        event_data = serialized["event_data"]
        comm_events = event_data["communication_events"]
        
        self.assertEqual(len(comm_events), 1)
        self.assertIn("SENSITIVE", comm_events[0]["message"])
    
    def test_sanitize_player_encounters(self):
        """Test player encounter sanitization."""
        serialized = self.serializer.serialize_session(self.sample_session)
        event_data = serialized["event_data"]
        encounters = event_data["player_encounters"]
        
        self.assertEqual(len(encounters), 1)
        self.assertNotIn("player_name", encounters[0])
        self.assertIn("_player_name_removed", encounters[0])
    
    def test_serialize_performance_metrics(self):
        """Test performance metrics serialization."""
        serialized = self.serializer.serialize_session(self.sample_session)
        metrics = serialized["performance_metrics"]
        
        self.assertEqual(metrics["session_duration_minutes"], 120)
        self.assertEqual(metrics["total_actions"], 3)
        self.assertEqual(metrics["actions_per_hour"], 1.5)  # 3 actions / 2 hours
        self.assertGreater(metrics["efficiency_score"], 0)
    
    def test_serialize_metadata(self):
        """Test metadata serialization."""
        serialized = self.serializer.serialize_session(self.sample_session)
        metadata = serialized["metadata"]
        
        self.assertIn("serialization_timestamp", metadata)
        self.assertEqual(metadata["serializer_version"], "1.0.0")
        self.assertEqual(metadata["data_source"], "ms11_bot")
        self.assertTrue(metadata["sanitization_applied"])
        self.assertIn("original_session_keys", metadata)
    
    def test_error_handling(self):
        """Test error handling in serialization."""
        invalid_session = {"invalid": "data"}
        serialized = self.serializer.serialize_session(invalid_session)
        
        self.assertIn("session_id", serialized)
        self.assertIn("metadata", serialized)
        self.assertIn("serialization_error", serialized["metadata"])


class TestSWGDBAPIClient(unittest.TestCase):
    """Test the SWGDB API client."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_client = SWGDBAPIClient(
            api_url="https://api.swgdb.com/v1",
            api_key="test_api_key",
            user_hash="test_user_hash"
        )
        self.sample_session = {
            "session_id": "test_session_123",
            "character_name": "TestCharacter",
            "start_time": "2025-01-01T10:00:00",
            "end_time": "2025-01-01T12:00:00",
            "duration_minutes": 120,
            "xp_data": {"total_xp_gained": 500},
            "credit_data": {"total_credits_gained": 2000},
            "quest_data": {"total_quests_completed": 2},
            "location_data": {"total_locations_visited": 1},
            "event_data": {"total_events": 3},
            "performance_metrics": {"session_duration_minutes": 120},
            "metadata": {"serializer_version": "1.0.0"}
        }
    
    @patch('swgdb_api.push_session_data.requests.Session')
    def test_push_session_data_success(self, mock_session_class):
        """Test successful session upload."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"session_id": "swgdb_12345"}
        mock_session.post.return_value = mock_response
        
        result = self.api_client.push_session_data(self.sample_session)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["swgdb_session_id"], "swgdb_12345")
        self.assertEqual(result["message"], "Session uploaded successfully")
    
    @patch('swgdb_api.push_session_data.requests.Session')
    def test_push_session_data_authentication_failure(self, mock_session_class):
        """Test authentication failure."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock 401 response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_session.post.return_value = mock_response
        
        result = self.api_client.push_session_data(self.sample_session)
        
        self.assertFalse(result["success"])
        self.assertIn("Authentication failed", result["error"])
    
    @patch('swgdb_api.push_session_data.requests.Session')
    def test_push_session_data_rate_limit(self, mock_session_class):
        """Test rate limit handling."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock 429 response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_session.post.return_value = mock_response
        
        result = self.api_client.push_session_data(self.sample_session)
        
        self.assertFalse(result["success"])
        self.assertIn("Rate limit exceeded", result["error"])
    
    @patch('swgdb_api.push_session_data.requests.Session')
    def test_batch_upload_sessions_success(self, mock_session_class):
        """Test successful batch upload."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "uploaded_count": 2,
            "failed_count": 0,
            "session_ids": ["swgdb_001", "swgdb_002"]
        }
        mock_session.post.return_value = mock_response
        
        sessions = [self.sample_session, self.sample_session]
        result = self.api_client.batch_upload_sessions(sessions)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["uploaded_count"], 2)
        self.assertEqual(result["failed_count"], 0)
        self.assertEqual(len(result["session_ids"]), 2)
    
    @patch('swgdb_api.push_session_data.requests.Session')
    def test_validate_credentials_success(self, mock_session_class):
        """Test successful credential validation."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"username": "test_user", "user_id": "12345"}
        mock_session.get.return_value = mock_response
        
        result = self.api_client.validate_credentials()
        
        self.assertTrue(result["success"])
        self.assertTrue(result["valid"])
        self.assertIn("user_info", result)
    
    @patch('swgdb_api.push_session_data.requests.Session')
    def test_validate_credentials_failure(self, mock_session_class):
        """Test failed credential validation."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        # Mock 401 response
        mock_response = Mock()
        mock_response.status_code = 401
        mock_session.get.return_value = mock_response
        
        result = self.api_client.validate_credentials()
        
        self.assertTrue(result["success"])
        self.assertFalse(result["valid"])
        self.assertIn("Invalid credentials", result["error"])
    
    def test_generate_signature(self):
        """Test HMAC signature generation."""
        data = '{"test": "data"}'
        timestamp = "1234567890"
        signature = self.api_client._generate_signature(data, timestamp)
        
        self.assertIsInstance(signature, str)
        self.assertEqual(len(signature), 64)  # SHA256 hex digest length
    
    def test_prepare_headers(self):
        """Test header preparation."""
        data = {"test": "data"}
        headers = self.api_client._prepare_headers(data)
        
        required_headers = [
            "Content-Type",
            "X-SWGDB-API-Key",
            "X-SWGDB-User-Hash",
            "X-SWGDB-Timestamp",
            "X-SWGDB-Signature",
            "User-Agent"
        ]
        
        for header in required_headers:
            self.assertIn(header, headers)


class TestSWGDBUploadManager(unittest.TestCase):
    """Test the SWGDB upload manager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_api_client = Mock()
        self.upload_manager = SWGDBUploadManager(self.mock_api_client)
        self.sample_session = {
            "session_id": "test_session_123",
            "character_name": "TestCharacter",
            "duration_minutes": 120
        }
    
    def test_add_to_queue(self):
        """Test adding sessions to queue."""
        self.assertEqual(len(self.upload_manager.upload_queue), 0)
        
        self.upload_manager.add_to_queue(self.sample_session)
        
        self.assertEqual(len(self.upload_manager.upload_queue), 1)
        self.assertEqual(self.upload_manager.upload_queue[0]["data"], self.sample_session)
        self.assertIn("added_timestamp", self.upload_manager.upload_queue[0])
        self.assertEqual(self.upload_manager.upload_queue[0]["retry_count"], 0)
    
    def test_process_queue_empty(self):
        """Test processing empty queue."""
        result = self.upload_manager.process_queue()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["processed"], 0)
        self.assertIn("Queue is empty", result["message"])
    
    def test_process_queue_success(self):
        """Test successful queue processing."""
        # Add sessions to queue
        self.upload_manager.add_to_queue(self.sample_session)
        self.upload_manager.add_to_queue(self.sample_session)
        
        # Mock successful batch upload
        self.mock_api_client.batch_upload_sessions.return_value = {
            "success": True,
            "uploaded_count": 2,
            "failed_count": 0
        }
        
        result = self.upload_manager.process_queue()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["processed"], 2)
        self.assertEqual(result["successful"], 2)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(len(self.upload_manager.upload_queue), 0)
    
    def test_process_queue_failure(self):
        """Test queue processing with failures."""
        # Add sessions to queue
        self.upload_manager.add_to_queue(self.sample_session)
        
        # Mock failed batch upload
        self.mock_api_client.batch_upload_sessions.return_value = {
            "success": False,
            "error": "API error"
        }
        
        result = self.upload_manager.process_queue()
        
        self.assertTrue(result["success"])
        self.assertEqual(result["processed"], 1)
        self.assertEqual(result["successful"], 0)
        self.assertEqual(result["failed"], 1)
        self.assertIn("API error", result["errors"])
    
    def test_retry_failed_uploads(self):
        """Test retrying failed uploads."""
        # Add sessions to queue with retry count
        self.upload_manager.add_to_queue(self.sample_session)
        self.upload_manager.upload_queue[0]["retry_count"] = 1
        
        # Mock successful individual upload
        self.mock_api_client.push_session_data.return_value = {
            "success": True,
            "swgdb_session_id": "swgdb_123"
        }
        
        result = self.upload_manager.retry_failed_uploads(max_retries=3)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["retried"], 1)
        self.assertEqual(result["successful"], 1)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(len(self.upload_manager.upload_queue), 0)
    
    def test_retry_failed_uploads_max_retries(self):
        """Test retry with max retries exceeded."""
        # Add sessions to queue with max retry count
        self.upload_manager.add_to_queue(self.sample_session)
        self.upload_manager.upload_queue[0]["retry_count"] = 3
        
        result = self.upload_manager.retry_failed_uploads(max_retries=3)
        
        self.assertTrue(result["success"])
        self.assertEqual(result["retried"], 0)
        self.assertIn("No failed uploads to retry", result["message"])


class TestSessionUploader(unittest.TestCase):
    """Test the session uploader."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config = UploadConfig(
            swgdb_api_url="https://api.swgdb.com/v1",
            api_key="test_api_key",
            user_hash="test_user_hash",
            sanitize_data=True,
            include_events=True,
            include_locations=True,
            include_communications=False,
            include_player_encounters=False
        )
        
        # Create test session files
        self.session_files = []
        for i in range(3):
            session_data = {
                "session_id": f"test_session_{i}",
                "start_time": "2025-01-01T10:00:00",
                "end_time": "2025-01-01T12:00:00",
                "duration_minutes": 120,
                "xp": {"gained": 1000 * (i + 1)},
                "credits": {"gained": 2000 * (i + 1)},
                "quests_completed": [f"Quest{i}"],
                "locations_visited": [],
                "actions": []
            }
            
            filepath = os.path.join(self.temp_dir, f"session_{i}.json")
            with open(filepath, 'w') as f:
                json.dump(session_data, f)
            self.session_files.append(filepath)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    @patch('bridge.session_uploader.SWGDBAPIClient')
    def test_upload_all_sessions_success(self, mock_client_class):
        """Test successful upload of all sessions."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.push_session_data.return_value = {
            "success": True,
            "swgdb_session_id": "swgdb_123"
        }
        
        uploader = SessionUploader(self.config)
        uploader.sessions_dir = Path(self.temp_dir)
        
        result = uploader.upload_all_sessions()
        
        self.assertEqual(result["total_sessions"], 3)
        self.assertEqual(result["uploaded"], 3)
        self.assertEqual(result["failed"], 0)
        self.assertEqual(len(result["sessions"]), 3)
    
    @patch('bridge.session_uploader.SWGDBAPIClient')
    def test_upload_all_sessions_failure(self, mock_client_class):
        """Test upload with some failures."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.push_session_data.return_value = {
            "success": False,
            "error": "API error"
        }
        
        uploader = SessionUploader(self.config)
        uploader.sessions_dir = Path(self.temp_dir)
        
        result = uploader.upload_all_sessions()
        
        self.assertEqual(result["total_sessions"], 3)
        self.assertEqual(result["uploaded"], 0)
        self.assertEqual(result["failed"], 3)
        self.assertEqual(len(result["sessions"]), 3)
    
    def test_find_session_logs(self):
        """Test finding session log files."""
        uploader = SessionUploader(self.config)
        uploader.sessions_dir = Path(self.temp_dir)
        
        session_files = uploader.find_session_logs()
        
        self.assertEqual(len(session_files), 3)
        for file_path in session_files:
            self.assertTrue(file_path.exists())
            self.assertTrue(file_path.suffix == '.json')
    
    def test_load_session_data(self):
        """Test loading session data from file."""
        uploader = SessionUploader(self.config)
        
        session_data = uploader.load_session_data(Path(self.session_files[0]))
        
        self.assertIsNotNone(session_data)
        self.assertEqual(session_data["session_id"], "test_session_0")
        self.assertIn("_file_path", session_data)
        self.assertIn("_file_name", session_data)
        self.assertIn("_file_size", session_data)
        self.assertIn("_modified_time", session_data)
    
    def test_sanitize_session_data(self):
        """Test session data sanitization."""
        uploader = SessionUploader(self.config)
        
        session_data = {
            "session_id": "test",
            "communication_events": [{"message": "secret info"}],
            "player_encounters": [{"player_name": "Player1"}],
            "locations_visited": [{"planet": "Tatooine"}]
        }
        
        sanitized = uploader.sanitize_session_data(session_data)
        
        # Check that sensitive data is removed
        self.assertNotIn("communication_events", sanitized)
        self.assertNotIn("player_encounters", sanitized)
        self.assertIn("locations_visited", sanitized)  # Should be included
        self.assertIn("_sanitized", sanitized)
        self.assertIn("_sanitization_timestamp", sanitized)
    
    def test_get_upload_statistics(self):
        """Test upload statistics."""
        uploader = SessionUploader(self.config)
        
        # Add some mock uploaded sessions
        uploader.uploaded_sessions = [
            Mock(upload_status="success", upload_timestamp="2025-01-01T10:00:00"),
            Mock(upload_status="success", upload_timestamp="2025-01-01T11:00:00"),
            Mock(upload_status="failed", upload_timestamp="2025-01-01T12:00:00")
        ]
        
        stats = uploader.get_upload_statistics()
        
        self.assertEqual(stats["total_sessions"], 3)
        self.assertEqual(stats["successful"], 2)
        self.assertEqual(stats["failed"], 1)
        self.assertEqual(stats["success_rate"], 66.7)
        self.assertIsNotNone(stats["last_upload"])


class TestSessionLogViewer(unittest.TestCase):
    """Test the session log viewer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.viewer = SessionLogViewer(self.temp_dir)
        
        # Create test session files
        self.session_files = []
        for i in range(3):
            session_data = {
                "session_id": f"test_session_{i}",
                "start_time": "2025-01-01T10:00:00",
                "end_time": "2025-01-01T12:00:00",
                "duration_minutes": 120,
                "xp": {"gained": 1000 * (i + 1)},
                "credits": {"gained": 2000 * (i + 1)},
                "quests_completed": [f"Quest{i}"],
                "locations_visited": [
                    {"planet": f"Planet{i}", "city": f"City{i}"}
                ],
                "actions": [
                    {"time": "2025-01-01T10:00:00", "action": f"Action{i}"}
                ]
            }
            
            filepath = os.path.join(self.temp_dir, f"session_{i}.json")
            with open(filepath, 'w') as f:
                json.dump(session_data, f)
            self.session_files.append(filepath)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_find_session_files(self):
        """Test finding session files."""
        session_files = self.viewer.find_session_files()
        
        self.assertEqual(len(session_files), 3)
        for file_path in session_files:
            self.assertTrue(file_path.exists())
            self.assertTrue(file_path.suffix == '.json')
    
    def test_load_session(self):
        """Test loading a single session."""
        session_files = self.viewer.find_session_files()
        session_data = self.viewer.load_session(session_files[0])
        
        self.assertIsNotNone(session_data)
        self.assertEqual(session_data["session_id"], "test_session_0")
        self.assertIn("_file_path", session_data)
        self.assertIn("_file_name", session_data)
        self.assertIn("_file_size", session_data)
        self.assertIn("_modified_time", session_data)
    
    def test_load_all_sessions(self):
        """Test loading all sessions."""
        sessions = self.viewer.load_all_sessions()
        
        self.assertEqual(len(sessions), 3)
        for session_id, session_data in sessions.items():
            self.assertIn("session_id", session_data)
            self.assertIn("_file_path", session_data)
    
    def test_list_sessions(self):
        """Test listing sessions."""
        # This test captures output, so we'll just verify it doesn't raise an exception
        try:
            self.viewer.list_sessions(limit=2)
        except Exception as e:
            self.fail(f"list_sessions raised an exception: {e}")
    
    def test_view_session(self):
        """Test viewing a specific session."""
        sessions = self.viewer.load_all_sessions()
        session_id = list(sessions.keys())[0]
        
        # This test captures output, so we'll just verify it doesn't raise an exception
        try:
            self.viewer.view_session(session_id)
        except Exception as e:
            self.fail(f"view_session raised an exception: {e}")
    
    def test_search_sessions(self):
        """Test searching sessions."""
        sessions = self.viewer.load_all_sessions()
        
        # Search for "Quest"
        results = self.viewer.search_sessions("Quest")
        self.assertEqual(len(results), 3)  # All sessions contain "Quest"
        
        # Search for "Planet"
        results = self.viewer.search_sessions("Planet")
        self.assertEqual(len(results), 3)  # All sessions contain "Planet"
        
        # Search for non-existent term
        results = self.viewer.search_sessions("NonExistent")
        self.assertEqual(len(results), 0)
    
    def test_analyze_sessions(self):
        """Test session analysis."""
        analysis = self.viewer.analyze_sessions()
        
        self.assertEqual(analysis["total_sessions"], 3)
        self.assertEqual(analysis["total_xp_gained"], 6000)  # 1000 + 2000 + 3000
        self.assertEqual(analysis["total_credits_gained"], 12000)  # 2000 + 4000 + 6000
        self.assertEqual(analysis["total_quests_completed"], 3)
        self.assertGreater(analysis["average_session_duration"], 0)
        self.assertGreater(analysis["average_xp_per_session"], 0)
        self.assertGreater(analysis["average_credits_per_session"], 0)
    
    def test_export_session(self):
        """Test session export."""
        sessions = self.viewer.load_all_sessions()
        session_id = list(sessions.keys())[0]
        
        export_file = os.path.join(self.temp_dir, "exported_session.json")
        success = self.viewer.export_session(session_id, export_file)
        
        self.assertTrue(success)
        self.assertTrue(os.path.exists(export_file))
        
        # Verify exported content
        with open(export_file, 'r') as f:
            exported_data = json.load(f)
        self.assertEqual(exported_data["session_id"], session_id)
    
    def test_compare_sessions(self):
        """Test session comparison."""
        sessions = self.viewer.load_all_sessions()
        session_ids = list(sessions.keys())[:2]
        
        comparison = self.viewer.compare_sessions(session_ids)
        
        self.assertEqual(len(comparison["sessions_compared"]), 2)
        self.assertIn("comparison_data", comparison)
        self.assertEqual(len(comparison["comparison_data"]), 2)
        
        for session_id in session_ids:
            self.assertIn(session_id, comparison["comparison_data"])
            session_data = comparison["comparison_data"][session_id]
            self.assertIn("duration_minutes", session_data)
            self.assertIn("xp_gained", session_data)
            self.assertIn("credits_gained", session_data)
            self.assertIn("quests_completed", session_data)


def run_tests():
    """Run all tests and provide a summary."""
    print("🧪 Running Batch 118 Session Upload Bridge Tests")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestSessionLogSerializer,
        TestSWGDBAPIClient,
        TestSWGDBUploadManager,
        TestSessionUploader,
        TestSessionLogViewer
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print(f"Total Tests: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print("\n❌ Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    if not result.failures and not result.errors:
        print("\n✅ All tests passed!")
    
    return result


if __name__ == '__main__':
    run_tests() 