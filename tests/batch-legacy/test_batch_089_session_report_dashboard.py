#!/usr/bin/env python3
"""
MS11 Batch 089 - Session Report Dashboard Tests

Comprehensive test suite for the enhanced session reporting system.

Tests cover:
- Enhanced SessionManager functionality
- Location visit tracking
- Player encounter detection
- Communication event tracking
- Quest completion tracking
- AFK detection and duration tracking
- Stuck event detection
- Session dashboard functionality
- Data export and import
- Discord summary generation
- Dashboard API endpoints

Usage:
    python test_batch_089_session_report_dashboard.py
"""

import json
import os
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import patch, MagicMock

import pytest

# Import the modules to test
from core.session_manager import SessionManager, LocationVisit, PlayerEncounter, CommunicationEvent
from core.session_report_dashboard import SessionReportDashboard, SessionSummary


class TestSessionManager:
    """Test the enhanced SessionManager functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.sessions_dir = Path(self.temp_dir) / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # Patch the logs directory
        with patch('core.session_manager.os.makedirs'):
            with patch('core.session_manager.logger'):
                self.session = SessionManager(mode="test")
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_session_initialization(self):
        """Test session initialization with enhanced tracking."""
        assert self.session.session_id is not None
        assert self.session.mode == "test"
        assert self.session.start_time is not None
        assert self.session.locations_visited == []
        assert self.session.player_encounters == []
        assert self.session.communication_events == []
        assert self.session.quests_completed == []
        assert self.session.afk_periods == []
        assert self.session.stuck_events == []
        assert self.session.performance_metrics == {}
    
    def test_location_visit_tracking(self):
        """Test location visit tracking functionality."""
        # Record location visits
        self.session.record_location_visit("Tatooine", "Mos Eisley", (3520, -4800))
        self.session.record_location_visit("Corellia", "Coronet", (123, 456))
        
        assert len(self.session.locations_visited) == 2
        
        # Check first location
        first_location = self.session.locations_visited[0]
        assert first_location.planet == "Tatooine"
        assert first_location.city == "Mos Eisley"
        assert first_location.coordinates == (3520, -4800)
        assert first_location.arrival_time is not None
        assert first_location.departure_time is not None
        assert first_location.duration_minutes is not None
        
        # Check second location
        second_location = self.session.locations_visited[1]
        assert second_location.planet == "Corellia"
        assert second_location.city == "Coronet"
        assert second_location.coordinates == (123, 456)
    
    def test_player_encounter_tracking(self):
        """Test player encounter tracking functionality."""
        # Record player encounters
        self.session.record_player_encounter("Player1", "Mos Eisley", 50.0, "detected")
        self.session.record_player_encounter("Player2", "Coronet", 25.0, "whispered")
        
        assert len(self.session.player_encounters) == 2
        
        # Check first encounter
        first_encounter = self.session.player_encounters[0]
        assert first_encounter.player_name == "Player1"
        assert first_encounter.location == "Mos Eisley"
        assert first_encounter.distance == 50.0
        assert first_encounter.interaction_type == "detected"
        assert first_encounter.timestamp is not None
        
        # Check second encounter
        second_encounter = self.session.player_encounters[1]
        assert second_encounter.player_name == "Player2"
        assert second_encounter.location == "Coronet"
        assert second_encounter.distance == 25.0
        assert second_encounter.interaction_type == "whispered"
    
    def test_communication_event_tracking(self):
        """Test communication event tracking functionality."""
        # Record communication events
        self.session.record_communication("whisper", "Player1", "Hello", True)
        self.session.record_communication("tell", "Player2", "Need help", False)
        
        assert len(self.session.communication_events) == 2
        
        # Check first communication
        first_comm = self.session.communication_events[0]
        assert first_comm.event_type == "whisper"
        assert first_comm.sender == "Player1"
        assert first_comm.message == "Hello"
        assert first_comm.response_sent is True
        assert first_comm.timestamp is not None
        
        # Check second communication
        second_comm = self.session.communication_events[1]
        assert second_comm.event_type == "tell"
        assert second_comm.sender == "Player2"
        assert second_comm.message == "Need help"
        assert second_comm.response_sent is False
    
    def test_quest_completion_tracking(self):
        """Test quest completion tracking functionality."""
        # Record quest completions
        self.session.record_quest_completion("Quest1")
        self.session.record_quest_completion("Quest2")
        
        assert len(self.session.quests_completed) == 2
        assert "Quest1" in self.session.quests_completed
        assert "Quest2" in self.session.quests_completed
    
    def test_stuck_event_detection(self):
        """Test stuck event detection functionality."""
        # Simulate being stuck at the same position
        self.session.update_position((100, 100))
        self.session.update_position((100, 100))  # Same position
        self.session.update_position((100, 100))  # Still stuck
        self.session.update_position((100, 100))  # Still stuck
        self.session.update_position((100, 100))  # Should trigger stuck event
        
        # Should have recorded a stuck event
        assert len(self.session.stuck_events) > 0
        
        stuck_event = self.session.stuck_events[0]
        assert stuck_event["location"] == "(100, 100)"
        assert stuck_event["reason"] == "Position unchanged"
        assert stuck_event["duration_seconds"] > 0
    
    def test_afk_detection(self):
        """Test AFK detection functionality."""
        # Initially should not be AFK
        assert not self.session.check_afk_status()
        
        # Simulate inactivity by manipulating the last activity time
        self.session.last_activity_time = datetime.now() - timedelta(minutes=10)
        
        # Should now be AFK
        assert self.session.check_afk_status()
        
        # Add activity to reset AFK
        self.session.add_action("Test action")
        assert not self.session.check_afk_status()
    
    def test_session_end_with_enhanced_data(self):
        """Test session ending with enhanced data collection."""
        # Add some test data
        self.session.set_start_credits(10000)
        self.session.set_start_xp(50000)
        
        self.session.record_location_visit("Tatooine", "Mos Eisley", (3520, -4800))
        self.session.record_player_encounter("Player1", "Mos Eisley", 50.0, "detected")
        self.session.record_communication("whisper", "Player1", "Hello", True)
        self.session.record_quest_completion("Test Quest")
        
        self.session.set_end_credits(15000)
        self.session.set_end_xp(60000)
        
        # End session
        with patch('core.session_manager.logger'):
            with patch('builtins.open', create=True) as mock_open:
                mock_file = MagicMock()
                mock_open.return_value.__enter__.return_value = mock_file
                self.session.end_session()
        
        # Check that performance metrics were calculated
        assert self.session.performance_metrics is not None
        assert "total_duration_minutes" in self.session.performance_metrics
        assert "locations_visited_count" in self.session.performance_metrics
        assert "unique_players_encountered" in self.session.performance_metrics
        assert "communication_events_count" in self.session.performance_metrics
        assert "quests_completed_count" in self.session.performance_metrics
        assert "stuck_events_count" in self.session.performance_metrics
        assert "credits_per_hour" in self.session.performance_metrics
        assert "xp_per_hour" in self.session.performance_metrics


class TestSessionReportDashboard:
    """Test the SessionReportDashboard functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.sessions_dir = Path(self.temp_dir) / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        self.dashboard = SessionReportDashboard(str(self.sessions_dir))
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def create_test_session_data(self) -> Dict[str, Any]:
        """Create test session data."""
        return {
            "session_id": "test123",
            "mode": "combat",
            "start_time": "2025-01-01T10:00:00",
            "end_time": "2025-01-01T11:00:00",
            "duration_minutes": 60.0,
            "start_credits": 10000,
            "end_credits": 15000,
            "start_xp": 50000,
            "end_xp": 60000,
            "xp_gained": 10000,
            "actions": [],
            "locations_visited": [
                {
                    "planet": "Tatooine",
                    "city": "Mos Eisley",
                    "coordinates": [3520, -4800],
                    "arrival_time": "2025-01-01T10:00:00",
                    "departure_time": "2025-01-01T10:30:00",
                    "duration_minutes": 30.0
                }
            ],
            "player_encounters": [
                {
                    "player_name": "Player1",
                    "timestamp": "2025-01-01T10:15:00",
                    "location": "Mos Eisley",
                    "distance": 50.0,
                    "interaction_type": "detected"
                }
            ],
            "communication_events": [
                {
                    "timestamp": "2025-01-01T10:20:00",
                    "event_type": "whisper",
                    "sender": "Player1",
                    "message": "Hello",
                    "response_sent": True
                }
            ],
            "quests_completed": ["Quest1", "Quest2"],
            "afk_periods": [
                {
                    "start_time": "2025-01-01T10:45:00",
                    "end_time": "2025-01-01T10:50:00",
                    "duration_minutes": 5.0
                }
            ],
            "stuck_events": [
                {
                    "timestamp": "2025-01-01T10:25:00",
                    "location": "(100, 100)",
                    "reason": "Position unchanged",
                    "duration_seconds": 30.0
                }
            ],
            "performance_metrics": {
                "total_duration_minutes": 60.0,
                "active_time_minutes": 55.0,
                "afk_time_minutes": 5.0,
                "afk_percentage": 8.33,
                "locations_visited_count": 1,
                "unique_players_encountered": 1,
                "communication_events_count": 1,
                "quests_completed_count": 2,
                "stuck_events_count": 1,
                "credits_per_hour": 5000.0,
                "xp_per_hour": 10000.0
            },
            "summary": {
                "total_credits_earned": 5000,
                "total_xp_gained": 10000,
                "total_quests_completed": 2,
                "total_locations_visited": 1,
                "total_player_encounters": 1,
                "total_communication_events": 1,
                "total_afk_time_minutes": 5.0,
                "total_stuck_events": 1,
                "active_time_minutes": 55.0,
                "credits_per_hour": 5000.0,
                "xp_per_hour": 10000.0
            }
        }
    
    def test_load_session_data(self):
        """Test loading session data by ID."""
        # Create test session file
        session_data = self.create_test_session_data()
        session_file = self.sessions_dir / "session_test123.json"
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        # Test loading
        loaded_data = self.dashboard.load_session_data("test123")
        assert loaded_data is not None
        assert loaded_data["session_id"] == "test123"
        assert loaded_data["mode"] == "combat"
    
    def test_load_all_sessions(self):
        """Test loading all sessions."""
        # Create multiple test session files
        for i in range(3):
            session_data = self.create_test_session_data()
            session_data["session_id"] = f"test{i}"
            session_file = self.sessions_dir / f"session_test{i}.json"
            
            with open(session_file, 'w') as f:
                json.dump(session_data, f)
        
        # Test loading all sessions
        sessions = self.dashboard.load_all_sessions()
        assert len(sessions) == 3
        
        # Should be sorted by modification time (newest first)
        session_ids = [s["session_id"] for s in sessions]
        assert "test0" in session_ids
        assert "test1" in session_ids
        assert "test2" in session_ids
    
    def test_get_session_summary(self):
        """Test creating session summary from data."""
        session_data = self.create_test_session_data()
        summary = self.dashboard.get_session_summary(session_data)
        
        assert isinstance(summary, SessionSummary)
        assert summary.session_id == "test123"
        assert summary.mode == "combat"
        assert summary.duration_minutes == 60.0
        assert summary.credits_earned == 5000
        assert summary.xp_gained == 10000
        assert summary.quests_completed == 2
        assert summary.locations_visited == 1
        assert summary.player_encounters == 1
        assert summary.communication_events == 1
        assert summary.afk_time_minutes == 5.0
        assert summary.stuck_events == 1
        assert summary.active_time_minutes == 55.0
        assert summary.credits_per_hour == 5000.0
        assert summary.xp_per_hour == 10000.0
    
    def test_filter_sessions(self):
        """Test session filtering functionality."""
        # Create test sessions with different characteristics
        sessions = []
        for i in range(3):
            session_data = self.create_test_session_data()
            session_data["session_id"] = f"test{i}"
            session_data["mode"] = ["combat", "questing", "crafting"][i]
            session_data["duration_minutes"] = [30.0, 60.0, 90.0][i]
            session_data["summary"]["total_credits_earned"] = [1000, 5000, 10000][i]
            sessions.append(session_data)
        
        # Test mode filter
        filtered = self.dashboard.filter_sessions(sessions, {"mode": "combat"})
        assert len(filtered) == 1
        assert filtered[0]["session_id"] == "test0"
        
        # Test duration filter
        filtered = self.dashboard.filter_sessions(sessions, {"min_duration": 60.0})
        assert len(filtered) == 2
        assert filtered[0]["session_id"] == "test1"
        assert filtered[1]["session_id"] == "test2"
        
        # Test credits filter
        filtered = self.dashboard.filter_sessions(sessions, {"min_credits": 5000})
        assert len(filtered) == 2
        assert filtered[0]["session_id"] == "test1"
        assert filtered[1]["session_id"] == "test2"
    
    def test_calculate_aggregate_stats(self):
        """Test aggregate statistics calculation."""
        sessions = []
        for i in range(3):
            session_data = self.create_test_session_data()
            session_data["session_id"] = f"test{i}"
            session_data["mode"] = ["combat", "questing", "combat"][i]
            session_data["duration_minutes"] = 60.0
            session_data["summary"]["total_credits_earned"] = 5000
            session_data["summary"]["total_xp_gained"] = 10000
            sessions.append(session_data)
        
        stats = self.dashboard.calculate_aggregate_stats(sessions)
        
        assert stats["total_sessions"] == 3
        assert stats["total_duration_hours"] == 3.0
        assert stats["total_credits_earned"] == 15000
        assert stats["total_xp_gained"] == 30000
        assert stats["avg_duration_minutes"] == 60.0
        assert stats["avg_credits_per_session"] == 5000
        assert stats["avg_xp_per_session"] == 10000
        assert stats["credits_per_hour"] == 5000.0
        assert stats["xp_per_hour"] == 10000.0
        assert stats["mode_distribution"]["combat"] == 2
        assert stats["mode_distribution"]["questing"] == 1
    
    def test_get_recent_sessions(self):
        """Test getting recent sessions."""
        # Create test sessions with different timestamps
        sessions = []
        for i in range(3):
            session_data = self.create_test_session_data()
            session_data["session_id"] = f"test{i}"
            # Create sessions at different times
            base_time = datetime.now() - timedelta(hours=i*2)
            session_data["start_time"] = base_time.isoformat()
            sessions.append(session_data)
        
        # Save sessions to files
        for session in sessions:
            session_file = self.sessions_dir / f"session_{session['session_id']}.json"
            with open(session_file, 'w') as f:
                json.dump(session, f)
        
        # Test getting recent sessions (last 4 hours)
        recent = self.dashboard.get_recent_sessions(hours=4)
        assert len(recent) == 2  # Should get 2 sessions (0 and 2 hours ago)
    
    def test_get_session_details(self):
        """Test getting detailed session information."""
        session_data = self.create_test_session_data()
        session_file = self.sessions_dir / "session_test123.json"
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        details = self.dashboard.get_session_details("test123")
        assert details is not None
        assert details["session_id"] == "test123"
        assert "summary_stats" in details
        assert "start_time_formatted" in details
        assert "end_time_formatted" in details
    
    def test_export_session_report(self):
        """Test session export functionality."""
        session_data = self.create_test_session_data()
        session_file = self.sessions_dir / "session_test123.json"
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        # Test JSON export
        export_data = self.dashboard.export_session_report("test123", "json")
        assert export_data is not None
        assert "test123" in export_data
        
        # Test YAML export
        export_data = self.dashboard.export_session_report("test123", "yaml")
        assert export_data is not None
        assert "test123" in export_data
    
    def test_generate_discord_summary(self):
        """Test Discord summary generation."""
        session_data = self.create_test_session_data()
        session_file = self.sessions_dir / "session_test123.json"
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f)
        
        summary = self.dashboard.generate_discord_summary("test123")
        assert summary is not None
        assert "Session Report" in summary
        assert "test123" in summary
        assert "combat" in summary
        assert "Credits:" in summary
        assert "XP:" in summary


class TestIntegration:
    """Integration tests for the complete session reporting system."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.sessions_dir = Path(self.temp_dir) / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_complete_session_lifecycle(self):
        """Test a complete session lifecycle with all features."""
        # Create session
        with patch('core.session_manager.logger'):
            session = SessionManager(mode="integration_test")
        
        # Add comprehensive test data
        session.set_start_credits(10000)
        session.set_start_xp(50000)
        
        # Record locations
        session.record_location_visit("Tatooine", "Mos Eisley", (3520, -4800))
        session.record_location_visit("Corellia", "Coronet", (123, 456))
        
        # Record player encounters
        session.record_player_encounter("Player1", "Mos Eisley", 50.0, "detected")
        session.record_player_encounter("Player2", "Coronet", 25.0, "whispered")
        
        # Record communications
        session.record_communication("whisper", "Player1", "Hello", True)
        session.record_communication("tell", "Player2", "Need help", False)
        
        # Record quests
        session.record_quest_completion("Quest1")
        session.record_quest_completion("Quest2")
        
        # Simulate stuck events
        session.update_position((100, 100))
        session.update_position((100, 100))
        session.update_position((100, 100))
        session.update_position((100, 100))
        session.update_position((100, 100))
        
        # End session
        session.set_end_credits(15000)
        session.set_end_xp(60000)
        
        with patch('core.session_manager.logger'):
            with patch('builtins.open', create=True) as mock_open:
                mock_file = MagicMock()
                mock_open.return_value.__enter__.return_value = mock_file
                session.end_session()
        
        # Test dashboard integration
        dashboard = SessionReportDashboard(str(self.sessions_dir))
        
        # Load sessions
        sessions = dashboard.load_all_sessions()
        assert len(sessions) > 0
        
        # Get session details
        session_details = dashboard.get_session_details(session.session_id)
        assert session_details is not None
        
        # Test filtering
        filtered = dashboard.filter_sessions(sessions, {"mode": "integration_test"})
        assert len(filtered) > 0
        
        # Test aggregate stats
        stats = dashboard.calculate_aggregate_stats(sessions)
        assert stats["total_sessions"] > 0
        
        # Test export
        export_data = dashboard.export_session_report(session.session_id, "json")
        assert export_data is not None
        
        # Test Discord summary
        discord_summary = dashboard.generate_discord_summary(session.session_id)
        assert discord_summary is not None


def run_tests():
    """Run all tests."""
    print("Running MS11 Batch 089 Session Report Dashboard Tests...")
    print("=" * 60)
    
    # Create test instances
    test_classes = [
        TestSessionManager,
        TestSessionReportDashboard,
        TestIntegration
    ]
    
    total_tests = 0
    passed_tests = 0
    
    for test_class in test_classes:
        print(f"\nTesting {test_class.__name__}...")
        
        test_instance = test_class()
        
        # Get all test methods
        test_methods = [method for method in dir(test_instance) 
                       if method.startswith('test_')]
        
        for method_name in test_methods:
            total_tests += 1
            try:
                # Run setup
                if hasattr(test_instance, 'setup_method'):
                    test_instance.setup_method()
                
                # Run test
                method = getattr(test_instance, method_name)
                method()
                
                # Run teardown
                if hasattr(test_instance, 'teardown_method'):
                    test_instance.teardown_method()
                
                print(f"  ✓ {method_name}")
                passed_tests += 1
                
            except Exception as e:
                print(f"  ✗ {method_name}: {e}")
                
                # Run teardown even if test failed
                if hasattr(test_instance, 'teardown_method'):
                    try:
                        test_instance.teardown_method()
                    except:
                        pass
    
    print(f"\n" + "=" * 60)
    print(f"Test Results: {passed_tests}/{total_tests} tests passed")
    print("=" * 60)
    
    if passed_tests == total_tests:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed.")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1) 