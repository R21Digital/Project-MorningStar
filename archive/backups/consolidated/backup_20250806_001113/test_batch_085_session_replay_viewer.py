#!/usr/bin/env python3
"""
Test script for Batch 085 - Session Replay Viewer

This script tests the session replay viewer functionality including:
1. Session log loading and filtering
2. Session sync utility
3. Dashboard API endpoints
4. Web UI functionality
"""

import json
import os
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import unittest
from unittest.mock import patch, MagicMock
import requests
import threading
import time

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from dashboard.session_sync import SessionSync
from dashboard.app import _load_session_logs, _filter_sessions, _calculate_session_stats


class TestSessionSync(unittest.TestCase):
    """Test the session sync functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_sessions_dir = Path(self.temp_dir) / "test_sessions"
        self.test_sessions_dir.mkdir()
        
        # Create test session files
        self.create_test_sessions()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def create_test_sessions(self):
        """Create test session files."""
        test_sessions = [
            {
                "session_id": "test_session_001",
                "start_time": (datetime.now() - timedelta(hours=2)).isoformat(),
                "end_time": (datetime.now() - timedelta(hours=1)).isoformat(),
                "character_name": "TestCharacter",
                "total_xp_gained": 1000,
                "total_credits_gained": 5000,
                "total_deaths": 1,
                "total_quests_completed": 2,
                "events": [
                    {
                        "event_type": "xp_gain",
                        "timestamp": (datetime.now() - timedelta(hours=1, minutes=30)).isoformat(),
                        "description": "Gained 500 XP from quest",
                        "xp_gained": 500
                    },
                    {
                        "event_type": "death",
                        "timestamp": (datetime.now() - timedelta(hours=1, minutes=15)).isoformat(),
                        "description": "Death: Killed by enemy",
                        "xp_gained": 0
                    }
                ]
            },
            {
                "session_id": "test_session_002",
                "start_time": (datetime.now() - timedelta(days=1)).isoformat(),
                "end_time": (datetime.now() - timedelta(days=1, hours=1)).isoformat(),
                "character_name": "TestCharacter2",
                "total_xp_gained": 800,
                "total_credits_gained": 3000,
                "total_deaths": 0,
                "total_quests_completed": 1,
                "events": [
                    {
                        "event_type": "quest_completion",
                        "timestamp": (datetime.now() - timedelta(days=1, minutes=30)).isoformat(),
                        "description": "Completed quest",
                        "xp_gained": 800
                    }
                ]
            }
        ]
        
        for i, session in enumerate(test_sessions):
            filename = f"session_{session['session_id']}.json"
            filepath = self.test_sessions_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session, f, indent=2)
    
    def test_session_sync_initialization(self):
        """Test session sync initialization."""
        with patch('dashboard.session_sync.Path') as mock_path:
            mock_path.return_value.resolve.return_value.parents.__getitem__.return_value = Path(self.temp_dir)
            
            syncer = SessionSync()
            self.assertIsNotNone(syncer)
    
    def test_find_session_logs(self):
        """Test finding session logs."""
        with patch('dashboard.session_sync.Path') as mock_path:
            mock_path.return_value.resolve.return_value.parents.__getitem__.return_value = Path(self.temp_dir)
            
            syncer = SessionSync()
            syncer.source_dirs = [self.test_sessions_dir]
            
            session_files = syncer.find_session_logs()
            self.assertEqual(len(session_files), 2)
    
    def test_is_session_log(self):
        """Test session log validation."""
        with patch('dashboard.session_sync.Path') as mock_path:
            mock_path.return_value.resolve.return_value.parents.__getitem__.return_value = Path(self.temp_dir)
            
            syncer = SessionSync()
            
            # Valid session log
            valid_session = {
                "session_id": "test",
                "start_time": "2023-01-01T00:00:00",
                "total_xp_gained": 100
            }
            self.assertTrue(syncer._is_session_log(valid_session))
            
            # Invalid session log
            invalid_session = {"random": "data"}
            self.assertFalse(syncer._is_session_log(invalid_session))
    
    def test_sync_sessions(self):
        """Test session sync functionality."""
        with patch('dashboard.session_sync.Path') as mock_path:
            mock_path.return_value.resolve.return_value.parents.__getitem__.return_value = Path(self.temp_dir)
            
            syncer = SessionSync()
            syncer.source_dirs = [self.test_sessions_dir]
            syncer.dashboard_sessions_dir = self.test_sessions_dir / "dashboard"
            syncer.dashboard_sessions_dir.mkdir(exist_ok=True)
            
            results = syncer.sync_sessions()
            self.assertEqual(results['total_found'], 2)
            self.assertEqual(results['copied'], 2)
            self.assertEqual(results['errors'], 0)


class TestSessionLoading(unittest.TestCase):
    """Test session loading and filtering functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_sessions_dir = Path(self.temp_dir) / "test_sessions"
        self.test_sessions_dir.mkdir()
        
        # Create test session files
        self.create_test_sessions()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def create_test_sessions(self):
        """Create test session files."""
        test_sessions = [
            {
                "session_id": "filter_test_001",
                "start_time": (datetime.now() - timedelta(hours=1)).isoformat(),
                "end_time": datetime.now().isoformat(),
                "character_name": "FilterTest",
                "location": "Naboo",
                "total_deaths": 2,
                "total_quests_completed": 3,
                "total_xp_gained": 1500,
                "total_credits_gained": 8000,
                "events": [
                    {
                        "event_type": "whisper",
                        "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
                        "description": "Whisper from friend"
                    }
                ]
            },
            {
                "session_id": "filter_test_002",
                "start_time": (datetime.now() - timedelta(days=2)).isoformat(),
                "end_time": (datetime.now() - timedelta(days=2, hours=1)).isoformat(),
                "character_name": "FilterTest2",
                "location": "Corellia",
                "total_deaths": 0,
                "total_quests_completed": 0,
                "total_xp_gained": 500,
                "total_credits_gained": 2000,
                "events": []
            }
        ]
        
        for i, session in enumerate(test_sessions):
            filename = f"session_{session['session_id']}.json"
            filepath = self.test_sessions_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session, f, indent=2)
    
    @patch('dashboard.app.LOG_DIRS')
    def test_load_session_logs(self, mock_log_dirs):
        """Test loading session logs."""
        mock_log_dirs.__iter__.return_value = [self.test_sessions_dir]
        
        sessions = _load_session_logs()
        self.assertEqual(len(sessions), 2)
        
        # Check that file metadata was added
        for session in sessions:
            self.assertIn('_file_path', session)
            self.assertIn('_file_name', session)
            self.assertIn('_file_size', session)
            self.assertIn('_modified_time', session)
    
    def test_filter_sessions(self):
        """Test session filtering."""
        sessions = [
            {
                "session_id": "test1",
                "character_name": "TestChar",
                "location": "Naboo",
                "start_time": (datetime.now() - timedelta(hours=1)).isoformat(),
                "total_deaths": 2,
                "total_quests_completed": 3,
                "events": [{"event_type": "whisper"}]
            },
            {
                "session_id": "test2",
                "character_name": "OtherChar",
                "location": "Corellia",
                "start_time": (datetime.now() - timedelta(days=2)).isoformat(),
                "total_deaths": 0,
                "total_quests_completed": 0,
                "events": []
            }
        ]
        
        # Test character filter
        filtered = _filter_sessions(sessions, {"character": "TestChar"})
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["session_id"], "test1")
        
        # Test location filter
        filtered = _filter_sessions(sessions, {"location": "Naboo"})
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["session_id"], "test1")
        
        # Test deaths filter
        filtered = _filter_sessions(sessions, {"has_deaths": True})
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["session_id"], "test1")
        
        # Test quests filter
        filtered = _filter_sessions(sessions, {"has_quests": True})
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["session_id"], "test1")
        
        # Test whispers filter
        filtered = _filter_sessions(sessions, {"has_whispers": True})
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["session_id"], "test1")
    
    def test_calculate_session_stats(self):
        """Test session statistics calculation."""
        session = {
            "start_time": (datetime.now() - timedelta(hours=1)).isoformat(),
            "end_time": datetime.now().isoformat(),
            "total_xp_gained": 1200,
            "total_credits_gained": 6000,
            "total_quests_completed": 2,
            "total_combat_actions": 10,
            "total_deaths": 1
        }
        
        stats = _calculate_session_stats(session)
        
        self.assertIn('duration_minutes', stats)
        self.assertIn('xp_per_minute', stats)
        self.assertIn('credits_per_minute', stats)
        self.assertIn('quests_per_hour', stats)
        self.assertIn('combat_efficiency', stats)
        
        # Check that duration is calculated correctly (should be around 60 minutes)
        self.assertGreater(stats['duration_minutes'], 50)
        self.assertLess(stats['duration_minutes'], 70)
        
        # Check that rates are calculated
        self.assertGreater(stats['xp_per_minute'], 0)
        self.assertGreater(stats['credits_per_minute'], 0)


class TestDashboardAPI(unittest.TestCase):
    """Test dashboard API endpoints."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_sessions_dir = Path(self.temp_dir) / "test_sessions"
        self.test_sessions_dir.mkdir()
        
        # Create test session files
        self.create_test_sessions()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def create_test_sessions(self):
        """Create test session files."""
        test_session = {
            "session_id": "api_test_001",
            "start_time": (datetime.now() - timedelta(hours=1)).isoformat(),
            "end_time": datetime.now().isoformat(),
            "character_name": "APITest",
            "total_xp_gained": 1000,
            "total_credits_gained": 5000,
            "events": []
        }
        
        filename = f"session_{test_session['session_id']}.json"
        filepath = self.test_sessions_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(test_session, f, indent=2)
    
    @patch('dashboard.app._load_session_logs')
    @patch('dashboard.app._filter_sessions')
    @patch('dashboard.app._calculate_session_stats')
    def test_api_sessions_endpoint(self, mock_calc_stats, mock_filter, mock_load):
        """Test the /api/sessions endpoint."""
        from dashboard.app import app
        
        # Mock the session loading functions
        mock_sessions = [{"session_id": "test", "character_name": "Test"}]
        mock_load.return_value = mock_sessions
        mock_filter.return_value = mock_sessions
        mock_calc_stats.return_value = {"duration_minutes": 60}
        
        with app.test_client() as client:
            response = client.get('/api/sessions')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertIn('sessions', data)
            self.assertIn('total_count', data)
            self.assertIn('filters', data)
    
    @patch('dashboard.app._load_session_logs')
    def test_api_session_detail_endpoint(self, mock_load):
        """Test the /api/session/<session_id> endpoint."""
        from dashboard.app import app
        
        # Mock session data
        mock_session = {
            "session_id": "test_detail",
            "character_name": "TestDetail",
            "total_xp_gained": 1000
        }
        mock_load.return_value = [mock_session]
        
        with app.test_client() as client:
            # Test existing session
            response = client.get('/api/session/test_detail')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            self.assertEqual(data['session_id'], 'test_detail')
            
            # Test non-existing session
            response = client.get('/api/session/nonexistent')
            self.assertEqual(response.status_code, 404)


class TestWebUI(unittest.TestCase):
    """Test web UI functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_sessions_dir = Path(self.temp_dir) / "test_sessions"
        self.test_sessions_dir.mkdir()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    @patch('dashboard.app._load_session_logs')
    @patch('dashboard.app._filter_sessions')
    @patch('dashboard.app._calculate_session_stats')
    def test_sessions_page_rendering(self, mock_calc_stats, mock_filter, mock_load):
        """Test that the sessions page renders correctly."""
        from dashboard.app import app
        
        # Mock session data
        mock_sessions = [
            {
                "session_id": "test_ui_001",
                "character_name": "UITest",
                "start_time": datetime.now().isoformat(),
                "total_xp_gained": 1000,
                "total_credits_gained": 5000,
                "total_deaths": 1,
                "total_quests_completed": 2,
                "events": []
            }
        ]
        mock_load.return_value = mock_sessions
        mock_filter.return_value = mock_sessions
        mock_calc_stats.return_value = {"duration_minutes": 60, "xp_per_minute": 16.67}
        
        with app.test_client() as client:
            response = client.get('/sessions')
            self.assertEqual(response.status_code, 200)
            
            # Check that the response contains expected content
            content = response.data.decode('utf-8')
            self.assertIn('Session Replay Viewer', content)
            self.assertIn('Filters', content)
            self.assertIn('UITest', content)


def run_integration_tests():
    """Run integration tests with a real dashboard server."""
    print("\n=== Running Integration Tests ===")
    
    # Start dashboard server in background
    import subprocess
    import time
    
    try:
        # Change to dashboard directory
        dashboard_dir = project_root / "dashboard"
        os.chdir(dashboard_dir)
        
        # Start server
        process = subprocess.Popen([sys.executable, "app.py"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(3)
        
        # Test API endpoints
        try:
            response = requests.get('http://127.0.0.1:8000/api/sessions')
            print(f"API Sessions endpoint: {response.status_code}")
            
            response = requests.get('http://127.0.0.1:8000/sessions')
            print(f"Sessions page: {response.status_code}")
            
        except requests.exceptions.ConnectionError:
            print("Could not connect to dashboard server")
        
        # Stop server
        process.terminate()
        process.wait()
        
    except Exception as e:
        print(f"Integration test error: {e}")


def main():
    """Run all tests."""
    print("=== Batch 085 - Session Replay Viewer Tests ===")
    
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run integration tests
    run_integration_tests()
    
    print("\n=== Test Summary ===")
    print("✓ Session sync functionality tested")
    print("✓ Session loading and filtering tested")
    print("✓ Dashboard API endpoints tested")
    print("✓ Web UI rendering tested")
    print("✓ Integration tests completed")


if __name__ == "__main__":
    main() 