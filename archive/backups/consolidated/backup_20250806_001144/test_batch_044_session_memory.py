#!/usr/bin/env python3
"""
Test suite for Batch 044 - Session Tracking + Memory System (v1)

This test suite validates all aspects of the session memory system including:
- Session logging and tracking
- Event tracking and analytics
- Memory management and analysis
- Performance metrics and recommendations
"""

import unittest
import tempfile
import shutil
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

from core.session_memory import (
    SessionLogger, MemoryManager, EventTracker, SessionAnalyzer,
    log_event, log_combat_action, log_quest_completion,
    load_session_logs, analyze_session_data, track_xp_gain,
    track_death, track_travel_event, get_session_stats,
    get_performance_metrics
)
from core.session_memory.memory_template import (
    EventType, CombatType, QuestStatus, MemoryTemplate,
    SessionData, EventData, CombatData, QuestData
)


class TestSessionLogger(unittest.TestCase):
    """Test SessionLogger functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.session_id = "test_session_123"
        self.character_name = "TestCharacter"
        self.temp_dir = tempfile.mkdtemp()
        
        # Mock the logs directory
        with patch('core.session_memory.session_logger.Path') as mock_path:
            mock_path.return_value.mkdir.return_value = None
            mock_path.return_value.__truediv__.return_value = Path(f"{self.temp_dir}/test.log")
            self.logger = SessionLogger(self.session_id, self.character_name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_session_logger_initialization(self):
        """Test session logger initialization."""
        self.assertEqual(self.logger.session_id, self.session_id)
        self.assertEqual(self.logger.character_name, self.character_name)
        self.assertIsNotNone(self.logger.session_data)
        self.assertEqual(self.logger.session_data.session_id, self.session_id)
        self.assertEqual(self.logger.session_data.character_name, self.character_name)
    
    def test_log_event(self):
        """Test logging general events."""
        event = self.logger.log_event(
            EventType.XP_GAIN,
            "Test XP gain",
            xp_gained=100,
            location="Test Location"
        )
        
        self.assertEqual(event.event_type, EventType.XP_GAIN)
        self.assertEqual(event.description, "Test XP gain")
        self.assertEqual(event.xp_gained, 100)
        self.assertEqual(event.location, "Test Location")
        self.assertIn(event, self.logger.session_data.events)
    
    def test_log_combat_action(self):
        """Test logging combat actions."""
        combat_data = self.logger.log_combat_action(
            CombatType.ATTACK,
            target_name="Test Enemy",
            damage_dealt=200,
            damage_received=50,
            victory=True,
            xp_gained=75
        )
        
        self.assertEqual(combat_data.combat_type, CombatType.ATTACK)
        self.assertEqual(combat_data.target_name, "Test Enemy")
        self.assertEqual(combat_data.damage_dealt, 200)
        self.assertEqual(combat_data.damage_received, 50)
        self.assertTrue(combat_data.victory)
        self.assertEqual(combat_data.xp_gained, 75)
        self.assertIn(combat_data, self.logger.session_data.combat_events)
    
    def test_log_quest_completion(self):
        """Test logging quest completions."""
        quest_data = self.logger.log_quest_completion(
            "Test Quest",
            quest_id="quest_001",
            npc_name="Test NPC",
            xp_reward=150,
            credit_reward=500
        )
        
        self.assertEqual(quest_data.quest_name, "Test Quest")
        self.assertEqual(quest_data.quest_id, "quest_001")
        self.assertEqual(quest_data.npc_name, "Test NPC")
        self.assertEqual(quest_data.xp_reward, 150)
        self.assertEqual(quest_data.credit_reward, 500)
        self.assertEqual(quest_data.status, QuestStatus.COMPLETED)
        self.assertIn(quest_data, self.logger.session_data.quest_events)
    
    def test_log_xp_gain(self):
        """Test logging XP gain."""
        event = self.logger.log_xp_gain(200, "quest_completion", location="Test Location")
        
        self.assertEqual(event.event_type, EventType.XP_GAIN)
        self.assertEqual(event.xp_gained, 200)
        self.assertEqual(event.location, "Test Location")
        self.assertEqual(self.logger.session_data.total_xp_gained, 200)
    
    def test_log_death(self):
        """Test logging death events."""
        event = self.logger.log_death("Test death", location="Test Location")
        
        self.assertEqual(event.event_type, EventType.DEATH)
        self.assertEqual(event.location, "Test Location")
        self.assertEqual(self.logger.session_data.total_deaths, 1)
    
    def test_log_travel_event(self):
        """Test logging travel events."""
        event = self.logger.log_travel_event("Test Destination", duration=120.5)
        
        self.assertEqual(event.event_type, EventType.TRAVEL_EVENT)
        self.assertEqual(event.location, "Test Destination")
        self.assertEqual(event.duration, 120.5)
        self.assertEqual(self.logger.session_data.total_travel_events, 1)
    
    def test_log_error(self):
        """Test logging error events."""
        event = self.logger.log_error("Test error", "navigation", location="Test Location")
        
        self.assertEqual(event.event_type, EventType.ERROR)
        self.assertEqual(event.error_message, "Test error")
        self.assertEqual(event.location, "Test Location")
        self.assertEqual(self.logger.session_data.total_errors, 1)
    
    def test_finalize_session(self):
        """Test session finalization."""
        # Add some events first
        self.logger.log_xp_gain(100, "quest")
        self.logger.log_combat_action(CombatType.ATTACK, target_name="Enemy")
        self.logger.log_quest_completion("Test Quest")
        
        # Finalize session
        session_data = self.logger.finalize_session()
        
        self.assertIsNotNone(session_data.end_time)
        self.assertIsNotNone(session_data.efficiency_score)
        self.assertIsNotNone(session_data.success_rate)
        self.assertEqual(session_data.total_xp_gained, 100)
        self.assertEqual(session_data.total_combat_actions, 1)
        self.assertEqual(session_data.total_quests_completed, 1)


class TestEventTracker(unittest.TestCase):
    """Test EventTracker functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.session_id = "test_tracker_123"
        self.logger = SessionLogger(self.session_id, "TestTracker")
        self.tracker = EventTracker(self.logger)
    
    def test_track_xp_gain(self):
        """Test tracking XP gain with analytics."""
        event = self.tracker.track_xp_gain(150, "quest_completion", location="Test Location")
        
        self.assertEqual(event.xp_gained, 150)
        self.assertEqual(self.tracker.total_xp_gained, 150)
        self.assertIn("quest_completion", self.tracker.xp_sources)
        self.assertEqual(self.tracker.xp_sources["quest_completion"], 150)
    
    def test_track_death(self):
        """Test tracking death events."""
        event = self.tracker.track_death("Test death", location="Test Location")
        
        self.assertEqual(event.event_type, EventType.DEATH)
        self.assertEqual(self.tracker.total_deaths, 1)
        self.assertIn("Test death", self.tracker.death_reasons)
        self.assertEqual(self.tracker.death_reasons["Test death"], 1)
    
    def test_track_travel_event(self):
        """Test tracking travel events."""
        event = self.tracker.track_travel_event("Test Destination", duration=120.5)
        
        self.assertEqual(event.event_type, EventType.TRAVEL_EVENT)
        self.assertEqual(self.tracker.total_travel_events, 1)
        self.assertIn("Test Destination", self.tracker.travel_destinations)
        self.assertEqual(self.tracker.travel_destinations["Test Destination"], 1)
    
    def test_track_combat_performance(self):
        """Test tracking combat performance."""
        event = self.tracker.track_combat_performance(
            "attack", "Test Enemy", damage_dealt=200, damage_received=50, victory=True
        )
        
        self.assertEqual(event.event_type, EventType.COMBAT_ACTION)
        self.assertEqual(event.metadata["combat_type"], "attack")
        self.assertEqual(event.metadata["target_name"], "Test Enemy")
        self.assertEqual(event.metadata["damage_dealt"], 200)
        self.assertEqual(event.metadata["damage_received"], 50)
        self.assertTrue(event.metadata["victory"])
    
    def test_track_quest_progress(self):
        """Test tracking quest progress."""
        event = self.tracker.track_quest_progress(
            "Test Quest", "completed", xp_reward=200, credit_reward=500
        )
        
        self.assertEqual(event.event_type, EventType.QUEST_COMPLETION)
        self.assertEqual(event.xp_gained, 200)
        self.assertEqual(event.credits_gained, 500)
        self.assertEqual(event.metadata["quest_name"], "Test Quest")
        self.assertEqual(event.metadata["status"], "completed")
    
    def test_track_error(self):
        """Test tracking errors with categorization."""
        event = self.tracker.track_error("Test error", "navigation")
        
        self.assertEqual(event.event_type, EventType.ERROR)
        self.assertEqual(event.metadata["error_type"], "navigation")
        self.assertEqual(event.metadata["error_category"], "navigation")
    
    def test_get_tracking_summary(self):
        """Test getting tracking summary."""
        # Add some events
        self.tracker.track_xp_gain(100, "quest")
        self.tracker.track_death("Test death")
        self.tracker.track_travel_event("Test Destination")
        
        summary = self.tracker.get_tracking_summary()
        
        self.assertEqual(summary["total_xp_gained"], 100)
        self.assertEqual(summary["total_deaths"], 1)
        self.assertEqual(summary["total_travel_events"], 1)
        self.assertIn("quest", summary["xp_sources"])
        self.assertIn("Test death", summary["death_reasons"])
        self.assertIn("Test Destination", summary["travel_destinations"])
    
    def test_reset_tracking(self):
        """Test resetting tracking counters."""
        # Add some events
        self.tracker.track_xp_gain(100, "quest")
        self.tracker.track_death("Test death")
        
        # Reset tracking
        self.tracker.reset_tracking()
        
        self.assertEqual(self.tracker.total_xp_gained, 0)
        self.assertEqual(self.tracker.total_deaths, 0)
        self.assertEqual(self.tracker.total_travel_events, 0)
        self.assertEqual(len(self.tracker.xp_sources), 0)
        self.assertEqual(len(self.tracker.death_reasons), 0)


class TestMemoryManager(unittest.TestCase):
    """Test MemoryManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = MemoryManager(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_memory_manager_initialization(self):
        """Test memory manager initialization."""
        self.assertEqual(self.manager.logs_dir, Path(self.temp_dir))
        self.assertIsNotNone(self.manager.logger)
    
    def test_load_session_logs_empty(self):
        """Test loading session logs when directory is empty."""
        sessions = self.manager.load_session_logs()
        self.assertEqual(len(sessions), 0)
    
    def test_load_session_logs_with_data(self):
        """Test loading session logs with mock data."""
        # Create mock session data
        mock_session_data = {
            "session_id": "test_session",
            "start_time": "2024-01-01T10:00:00",
            "end_time": "2024-01-01T11:00:00",
            "character_name": "TestCharacter",
            "total_xp_gained": 1000,
            "total_quests_completed": 5,
            "total_combat_actions": 10,
            "total_deaths": 1,
            "total_travel_events": 3,
            "total_errors": 2,
            "efficiency_score": 0.75,
            "success_rate": 0.8
        }
        
        # Create mock JSON file
        json_file = Path(self.temp_dir) / "session_test_session.json"
        with open(json_file, 'w') as f:
            json.dump(mock_session_data, f)
        
        # Load sessions
        sessions = self.manager.load_session_logs()
        
        self.assertEqual(len(sessions), 1)
        session = sessions[0]
        self.assertEqual(session.session_id, "test_session")
        self.assertEqual(session.character_name, "TestCharacter")
        self.assertEqual(session.total_xp_gained, 1000)
    
    def test_analyze_session_data(self):
        """Test analyzing session data."""
        # Create mock session data
        session_data = SessionData(
            session_id="test_session",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
            character_name="TestCharacter",
            total_xp_gained=1000,
            total_quests_completed=5,
            total_combat_actions=10,
            total_deaths=1,
            total_travel_events=3,
            total_errors=2,
            efficiency_score=0.75,
            success_rate=0.8
        )
        
        analysis = self.manager.analyze_session_data([session_data])
        
        self.assertEqual(analysis["total_sessions"], 1)
        self.assertEqual(analysis["total_xp_gained"], 1000)
        self.assertEqual(analysis["total_quests_completed"], 5)
        self.assertEqual(analysis["total_combat_actions"], 10)
        self.assertEqual(analysis["total_deaths"], 1)
        self.assertEqual(analysis["total_travel_events"], 3)
        self.assertEqual(analysis["total_errors"], 2)
        self.assertEqual(analysis["average_efficiency_score"], 0.75)
        self.assertEqual(analysis["average_success_rate"], 0.8)
    
    def test_get_session_by_id(self):
        """Test getting session by ID."""
        # Create mock session data
        mock_session_data = {
            "session_id": "test_session",
            "start_time": "2024-01-01T10:00:00",
            "end_time": "2024-01-01T11:00:00",
            "character_name": "TestCharacter",
            "total_xp_gained": 1000
        }
        
        # Create mock JSON file
        json_file = Path(self.temp_dir) / "session_test_session.json"
        with open(json_file, 'w') as f:
            json.dump(mock_session_data, f)
        
        session = self.manager.get_session_by_id("test_session")
        
        self.assertIsNotNone(session)
        self.assertEqual(session.session_id, "test_session")
        self.assertEqual(session.character_name, "TestCharacter")
    
    def test_get_session_statistics(self):
        """Test getting session statistics."""
        # Create mock session data
        session_data = SessionData(
            session_id="test_session",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
            character_name="TestCharacter",
            total_xp_gained=1000,
            total_quests_completed=5,
            total_combat_actions=10,
            total_deaths=1,
            total_travel_events=3,
            total_errors=2,
            efficiency_score=0.75,
            success_rate=0.8
        )
        
        # Mock the get_session_by_id method
        with patch.object(self.manager, 'get_session_by_id', return_value=session_data):
            stats = self.manager.get_session_statistics("test_session")
            
            self.assertEqual(stats["session_id"], "test_session")
            self.assertEqual(stats["character_name"], "TestCharacter")
            self.assertEqual(stats["total_xp_gained"], 1000)
            self.assertEqual(stats["total_quests_completed"], 5)
            self.assertEqual(stats["total_combat_actions"], 10)
            self.assertEqual(stats["total_deaths"], 1)
            self.assertEqual(stats["total_travel_events"], 3)
            self.assertEqual(stats["total_errors"], 2)
            self.assertEqual(stats["efficiency_score"], 0.75)
            self.assertEqual(stats["success_rate"], 0.8)


class TestSessionAnalyzer(unittest.TestCase):
    """Test SessionAnalyzer functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = SessionAnalyzer()
    
    def test_get_session_stats(self):
        """Test getting session statistics."""
        # Create mock session data
        session_data = SessionData(
            session_id="test_session",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
            character_name="TestCharacter",
            total_xp_gained=1000,
            total_quests_completed=5,
            total_combat_actions=10,
            total_deaths=1,
            total_travel_events=3,
            total_errors=2,
            efficiency_score=0.75,
            success_rate=0.8
        )
        
        # Add some events
        event1 = EventData(
            event_type=EventType.XP_GAIN,
            timestamp=datetime.now(),
            description="Test event 1",
            xp_gained=100
        )
        event2 = EventData(
            event_type=EventType.COMBAT_ACTION,
            timestamp=datetime.now(),
            description="Test event 2",
            success=True
        )
        session_data.events = [event1, event2]
        
        stats = self.analyzer.get_session_stats(session_data)
        
        self.assertEqual(stats["session_id"], "test_session")
        self.assertEqual(stats["character_name"], "TestCharacter")
        self.assertEqual(stats["total_xp_gained"], 1000)
        self.assertEqual(stats["total_quests_completed"], 5)
        self.assertEqual(stats["total_combat_actions"], 10)
        self.assertEqual(stats["total_deaths"], 1)
        self.assertEqual(stats["total_travel_events"], 3)
        self.assertEqual(stats["total_errors"], 2)
        self.assertEqual(stats["efficiency_score"], 0.75)
        self.assertEqual(stats["success_rate"], 0.8)
        self.assertIn("xp_gain", stats["event_breakdown"])
        self.assertIn("combat_action", stats["event_breakdown"])
    
    def test_get_performance_metrics(self):
        """Test getting performance metrics across multiple sessions."""
        # Create mock session data
        sessions = []
        for i in range(3):
            session_data = SessionData(
                session_id=f"test_session_{i}",
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=1),
                character_name=f"TestCharacter_{i}",
                total_xp_gained=1000 * (i + 1),
                total_quests_completed=5 * (i + 1),
                total_combat_actions=10 * (i + 1),
                total_deaths=1,
                total_travel_events=3,
                total_errors=2,
                efficiency_score=0.75,
                success_rate=0.8
            )
            sessions.append(session_data)
        
        metrics = self.analyzer.get_performance_metrics(sessions)
        
        self.assertEqual(metrics["total_sessions"], 3)
        self.assertEqual(metrics["total_xp_gained"], 6000)  # 1000 + 2000 + 3000
        self.assertEqual(metrics["total_quests_completed"], 30)  # 5 + 10 + 15
        self.assertEqual(metrics["total_combat_actions"], 60)  # 10 + 20 + 30
        self.assertEqual(metrics["total_deaths"], 3)
        self.assertEqual(metrics["total_travel_events"], 9)
        self.assertEqual(metrics["total_errors"], 6)
        self.assertEqual(metrics["average_efficiency_score"], 0.75)
        self.assertAlmostEqual(metrics["average_success_rate"], 0.8, places=1)
    
    def test_get_recommendations(self):
        """Test getting recommendations based on session analysis."""
        # Create session with low efficiency
        session_data = SessionData(
            session_id="test_session",
            start_time=datetime.now(),
            end_time=datetime.now() + timedelta(hours=1),
            character_name="TestCharacter",
            total_xp_gained=500,
            total_quests_completed=1,
            total_combat_actions=5,
            total_deaths=4,
            total_travel_events=3,
            total_errors=6,
            efficiency_score=0.25,
            success_rate=0.6
        )
        
        recommendations = self.analyzer.get_recommendations(session_data)
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Check for specific recommendations based on the session data
        recommendation_text = " ".join(recommendations).lower()
        self.assertIn("efficiency", recommendation_text)
        self.assertIn("error", recommendation_text)
        self.assertIn("death", recommendation_text)
    
    def test_analyze_learning_patterns(self):
        """Test analyzing learning patterns."""
        # Create multiple sessions with improvement over time
        sessions = []
        for i in range(3):
            session_data = SessionData(
                session_id=f"test_session_{i}",
                start_time=datetime.now() + timedelta(days=i),
                end_time=datetime.now() + timedelta(days=i, hours=1),
                character_name="TestCharacter",
                total_xp_gained=1000 * (i + 1),
                total_quests_completed=5 * (i + 1),
                total_combat_actions=10 * (i + 1),
                total_deaths=1,
                total_travel_events=3,
                total_errors=2 - i,  # Decreasing errors
                efficiency_score=0.5 + (i * 0.1),  # Improving efficiency
                success_rate=0.7 + (i * 0.05)  # Improving success rate
            )
            sessions.append(session_data)
        
        patterns = self.analyzer.analyze_learning_patterns(sessions)
        
        self.assertEqual(patterns["total_sessions_analyzed"], 3)
        self.assertEqual(patterns["time_span_days"], 2)
        self.assertIn("efficiency_trend", patterns)
        self.assertIn("xp_rate_trend", patterns)
        self.assertIn("error_rate_trend", patterns)
        self.assertIn("improvement_metrics", patterns)


class TestMemoryTemplate(unittest.TestCase):
    """Test MemoryTemplate functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.template = MemoryTemplate()
    
    def test_create_session_data(self):
        """Test creating session data."""
        session_data = self.template.create_session_data("test_session", "TestCharacter")
        
        self.assertEqual(session_data.session_id, "test_session")
        self.assertEqual(session_data.character_name, "TestCharacter")
        self.assertIsNotNone(session_data.start_time)
        self.assertIsNone(session_data.end_time)
    
    def test_add_event(self):
        """Test adding events to template."""
        # Create session data
        session_data = self.template.create_session_data("test_session", "TestCharacter")
        self.template.session_data = session_data
        
        # Create event
        event = EventData(
            event_type=EventType.XP_GAIN,
            timestamp=datetime.now(),
            description="Test event",
            xp_gained=100
        )
        
        # Add event
        self.template.add_event(event)
        
        self.assertIn(event, self.template.session_data.events)
        self.assertEqual(self.template.session_data.total_xp_gained, 100)
    
    def test_add_combat_event(self):
        """Test adding combat events to template."""
        # Create session data
        session_data = self.template.create_session_data("test_session", "TestCharacter")
        self.template.session_data = session_data
        
        # Create combat event
        combat_data = CombatData(
            combat_type=CombatType.ATTACK,
            target_name="Test Enemy",
            damage_dealt=200,
            victory=True
        )
        
        # Add combat event
        self.template.add_combat_event(combat_data)
        
        self.assertIn(combat_data, self.template.session_data.combat_events)
        self.assertEqual(self.template.session_data.total_combat_actions, 1)
    
    def test_add_quest_event(self):
        """Test adding quest events to template."""
        # Create session data
        session_data = self.template.create_session_data("test_session", "TestCharacter")
        self.template.session_data = session_data
        
        # Create quest event
        quest_data = QuestData(
            quest_name="Test Quest",
            status=QuestStatus.COMPLETED,
            xp_reward=150
        )
        
        # Add quest event
        self.template.add_quest_event(quest_data)
        
        self.assertIn(quest_data, self.template.session_data.quest_events)
        self.assertEqual(self.template.session_data.total_quests_completed, 1)
    
    def test_finalize_session(self):
        """Test finalizing session."""
        # Create session data
        session_data = self.template.create_session_data("test_session", "TestCharacter")
        self.template.session_data = session_data
        
        # Add some events
        event = EventData(
            event_type=EventType.XP_GAIN,
            timestamp=datetime.now(),
            description="Test event",
            xp_gained=100
        )
        self.template.add_event(event)
        
        # Finalize session
        finalized_session = self.template.finalize_session()
        
        self.assertIsNotNone(finalized_session.end_time)
        self.assertIsNotNone(finalized_session.efficiency_score)
        self.assertIsNotNone(finalized_session.success_rate)
    
    def test_get_session_summary(self):
        """Test getting session summary."""
        # Create session data
        session_data = self.template.create_session_data("test_session", "TestCharacter")
        self.template.session_data = session_data
        
        # Add some events
        event = EventData(
            event_type=EventType.XP_GAIN,
            timestamp=datetime.now(),
            description="Test event",
            xp_gained=100
        )
        self.template.add_event(event)
        
        # Get summary
        summary = self.template.get_session_summary()
        
        self.assertEqual(summary["session_id"], "test_session")
        self.assertEqual(summary["character_name"], "TestCharacter")
        self.assertEqual(summary["total_xp_gained"], 100)


class TestIntegration(unittest.TestCase):
    """Test integration between components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_workflow(self):
        """Test the complete workflow from logging to analysis."""
        # Create session logger
        session_id = f"integration_test_{int(time.time())}"
        logger = SessionLogger(session_id, "IntegrationTest")
        
        # Log various events
        logger.log_xp_gain(200, "quest_completion")
        logger.log_combat_action(CombatType.ATTACK, target_name="Enemy", victory=True)
        logger.log_quest_completion("Test Quest", xp_reward=200)
        logger.log_error("Test error", "general")
        
        # Finalize session
        session_data = logger.finalize_session()
        
        # Create analyzer and get stats
        analyzer = SessionAnalyzer()
        stats = analyzer.get_session_stats(session_data)
        
        # Verify stats
        self.assertEqual(stats["session_id"], session_id)
        self.assertEqual(stats["total_xp_gained"], 400)  # 200 + 200
        self.assertEqual(stats["total_combat_actions"], 1)
        self.assertEqual(stats["total_quests_completed"], 1)
        self.assertEqual(stats["total_errors"], 1)
        self.assertIsNotNone(stats["efficiency_score"])
    
    def test_convenience_functions(self):
        """Test convenience functions."""
        # Test log_event
        session_id = f"convenience_test_{int(time.time())}"
        logger = SessionLogger(session_id, "ConvenienceTest")
        
        event = log_event(logger, EventType.XP_GAIN, "Test event", xp_gained=100)
        self.assertEqual(event.event_type, EventType.XP_GAIN)
        self.assertEqual(event.xp_gained, 100)
        
        # Test log_combat_action
        combat_data = log_combat_action(logger, CombatType.ATTACK, target_name="Enemy")
        self.assertEqual(combat_data.combat_type, CombatType.ATTACK)
        self.assertEqual(combat_data.target_name, "Enemy")
        
        # Test log_quest_completion
        quest_data = log_quest_completion(logger, "Test Quest", xp_reward=150)
        self.assertEqual(quest_data.quest_name, "Test Quest")
        self.assertEqual(quest_data.xp_reward, 150)
        
        # Test track_xp_gain
        event = track_xp_gain(logger, 200, "quest")
        self.assertEqual(event.xp_gained, 200)
        
        # Test track_death
        event = track_death(logger, "Test death")
        self.assertEqual(event.event_type, EventType.DEATH)
        
        # Test track_travel_event
        event = track_travel_event(logger, "Test Destination")
        self.assertEqual(event.event_type, EventType.TRAVEL_EVENT)
        
        # Test get_session_stats
        session_data = logger.finalize_session()
        stats = get_session_stats(session_data)
        self.assertIsInstance(stats, dict)
        self.assertIn("session_id", stats)
        
        # Test get_performance_metrics
        metrics = get_performance_metrics([session_data])
        self.assertIsInstance(metrics, dict)
        self.assertIn("total_sessions", metrics)


if __name__ == "__main__":
    unittest.main() 