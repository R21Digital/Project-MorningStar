#!/usr/bin/env python3
"""
Batch 098 - Quest Heatmap & Popular Paths Tracker Tests

This script tests the quest heatmap and popular paths tracking functionality
to ensure all features work correctly and data is properly anonymized.
"""

import json
import logging
import sys
import time
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import unittest

sys.path.insert(0, str(Path(__file__).parent))
from core.quest_heatmap_tracker import (
    quest_heatmap_tracker, QuestEvent, LocationVisit, StuckEvent, TravelPath
)

logger = logging.getLogger(__name__)

class QuestHeatmapTrackerTest(unittest.TestCase):
    """Test suite for QuestHeatmapTracker."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directories
        self.temp_logs_dir = Path(tempfile.mkdtemp())
        self.temp_data_dir = Path(tempfile.mkdtemp())
        
        # Create test tracker instance
        self.test_tracker = type(quest_heatmap_tracker)(
            logs_dir=str(self.temp_logs_dir),
            data_dir=str(self.temp_data_dir),
            anonymize=True
        )
        
        # Create test session data
        self.create_test_session_data()
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directories
        shutil.rmtree(self.temp_logs_dir, ignore_errors=True)
        shutil.rmtree(self.temp_data_dir, ignore_errors=True)
    
    def create_test_session_data(self):
        """Create test session data files."""
        # Test session log
        session_data = {
            "start_time": datetime.now().isoformat(),
            "quests_completed": 2,
            "total_xp": 1000,
            "time_spent": 1800.0,
            "activity_breakdown": {"quest": 3, "move": 4, "stuck": 1},
            "steps": [
                {
                    "time": (datetime.now() - timedelta(hours=1)).isoformat(),
                    "type": "quest",
                    "id": "test_quest_1",
                    "name": "Test Quest 1",
                    "action": "start",
                    "to": {"planet": "Tatooine", "city": "Mos Eisley", "x": 3600, "y": -4850}
                },
                {
                    "time": (datetime.now() - timedelta(minutes=45)).isoformat(),
                    "type": "quest",
                    "id": "test_quest_1",
                    "name": "Test Quest 1",
                    "action": "complete",
                    "xp": 500,
                    "to": {"planet": "Tatooine", "city": "Mos Eisley", "x": 3600, "y": -4850}
                },
                {
                    "time": (datetime.now() - timedelta(minutes=30)).isoformat(),
                    "type": "move",
                    "to": {"planet": "Tatooine", "city": "Mos Espa", "x": 3520, "y": -4800}
                },
                {
                    "time": (datetime.now() - timedelta(minutes=15)).isoformat(),
                    "type": "quest",
                    "id": "test_quest_2",
                    "name": "Test Quest 2",
                    "action": "start",
                    "to": {"planet": "Tatooine", "city": "Mos Espa", "x": 3520, "y": -4800}
                },
                {
                    "time": (datetime.now() - timedelta(minutes=10)).isoformat(),
                    "type": "stuck",
                    "location": {"planet": "Tatooine", "city": "Mos Espa", "zone": "mos_espa", "x": 3520, "y": -4800},
                    "duration_minutes": 10,
                    "attempts": 3,
                    "reason": "navigation_failed"
                },
                {
                    "time": (datetime.now() - timedelta(minutes=5)).isoformat(),
                    "type": "quest",
                    "id": "test_quest_2",
                    "name": "Test Quest 2",
                    "action": "complete",
                    "xp": 500,
                    "to": {"planet": "Tatooine", "city": "Mos Espa", "x": 3520, "y": -4800}
                }
            ]
        }
        
        # Write test session file
        session_file = self.temp_logs_dir / "session_test_123.json"
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)
        
        # Test navigation events
        nav_events = [
            {
                "timestamp": time.time() - 3600,
                "event_type": "path_progression",
                "details": {
                    "current_position": {"x": 3600, "y": -4850, "zone": "mos_eisley", "planet": "tatooine"},
                    "target_position": {"x": 3520, "y": -4800, "zone": "mos_espa", "planet": "tatooine"},
                    "distance": 94.34,
                    "status": "moving",
                    "attempts": 0,
                    "path_length": 2
                }
            },
            {
                "timestamp": time.time() - 1800,
                "event_type": "path_progression",
                "details": {
                    "current_position": {"x": 3520, "y": -4800, "zone": "mos_espa", "planet": "tatooine"},
                    "target_position": {"x": 3500, "y": -4780, "zone": "mos_espa", "planet": "tatooine"},
                    "distance": 25.0,
                    "status": "stuck",
                    "attempts": 3,
                    "path_length": 5
                }
            }
        ]
        
        nav_file = self.temp_logs_dir / "navigation_events_test.json"
        with open(nav_file, 'w') as f:
            for event in nav_events:
                f.write(json.dumps(event) + '\n')
    
    def test_initialization(self):
        """Test tracker initialization."""
        self.assertIsNotNone(self.test_tracker)
        self.assertEqual(self.test_tracker.logs_dir, self.temp_logs_dir)
        self.assertEqual(self.test_tracker.data_dir, self.temp_data_dir)
        self.assertTrue(self.test_tracker.anonymize)
    
    def test_anonymization(self):
        """Test session anonymization."""
        original_session_id = "test_session_12345"
        anonymized = self.test_tracker._anonymize_session(original_session_id)
        
        self.assertNotEqual(original_session_id, anonymized)
        self.assertEqual(len(anonymized), 8)  # MD5 hash truncated to 8 chars
        self.assertIsInstance(anonymized, str)
    
    def test_coordinate_extraction(self):
        """Test coordinate extraction from location data."""
        # Test dict format
        location_dict = {"x": 100, "y": 200}
        coords = self.test_tracker._extract_coordinates(location_dict)
        self.assertEqual(coords, (100, 200))
        
        # Test list format
        location_list = [300, 400]
        coords = self.test_tracker._extract_coordinates(location_list)
        self.assertEqual(coords, (300, 400))
        
        # Test tuple format
        location_tuple = (500, 600)
        coords = self.test_tracker._extract_coordinates(location_tuple)
        self.assertEqual(coords, (500, 600))
        
        # Test invalid format
        invalid_location = "invalid"
        coords = self.test_tracker._extract_coordinates(invalid_location)
        self.assertEqual(coords, (0, 0))
    
    def test_session_processing(self):
        """Test session log processing."""
        self.test_tracker.process_session_logs()
        
        # Check that quest events were created
        self.assertGreater(len(self.test_tracker.quest_events), 0)
        
        # Check that location visits were created
        self.assertGreater(len(self.test_tracker.location_visits), 0)
        
        # Check that stuck events were created
        self.assertGreater(len(self.test_tracker.stuck_events), 0)
        
        # Verify data structure
        for event in self.test_tracker.quest_events:
            self.assertIsInstance(event, QuestEvent)
            self.assertIsInstance(event.session_hash, str)
            self.assertIsInstance(event.coordinates, tuple)
            self.assertEqual(len(event.coordinates), 2)
    
    def test_quest_heatmap(self):
        """Test quest heatmap generation."""
        self.test_tracker.process_session_logs()
        
        quest_data = self.test_tracker.get_quest_heatmap(days=7)
        
        self.assertIn('period_days', quest_data)
        self.assertIn('total_quests', quest_data)
        self.assertIn('top_quests', quest_data)
        
        self.assertEqual(quest_data['period_days'], 7)
        self.assertGreaterEqual(quest_data['total_quests'], 0)
        self.assertIsInstance(quest_data['top_quests'], list)
    
    def test_city_heatmap(self):
        """Test city heatmap generation."""
        self.test_tracker.process_session_logs()
        
        city_data = self.test_tracker.get_city_heatmap(days=7)
        
        self.assertIn('period_days', city_data)
        self.assertIn('total_visits', city_data)
        self.assertIn('top_cities', city_data)
        
        self.assertEqual(city_data['period_days'], 7)
        self.assertGreaterEqual(city_data['total_visits'], 0)
        self.assertIsInstance(city_data['top_cities'], list)
    
    def test_danger_zones(self):
        """Test danger zones detection."""
        self.test_tracker.process_session_logs()
        
        danger_data = self.test_tracker.get_danger_zones(days=7)
        
        self.assertIn('period_days', danger_data)
        self.assertIn('total_stuck_events', danger_data)
        self.assertIn('danger_zones', danger_data)
        
        self.assertEqual(danger_data['period_days'], 7)
        self.assertGreaterEqual(danger_data['total_stuck_events'], 0)
        self.assertIsInstance(danger_data['danger_zones'], list)
    
    def test_popular_paths(self):
        """Test popular paths detection."""
        self.test_tracker.process_session_logs()
        
        paths_data = self.test_tracker.get_popular_paths(days=7)
        
        self.assertIn('period_days', paths_data)
        self.assertIn('total_paths', paths_data)
        self.assertIn('popular_paths', paths_data)
        
        self.assertEqual(paths_data['period_days'], 7)
        self.assertGreaterEqual(paths_data['total_paths'], 0)
        self.assertIsInstance(paths_data['popular_paths'], list)
    
    def test_coordinate_heatmap(self):
        """Test coordinate heatmap generation."""
        self.test_tracker.process_session_logs()
        
        coord_data = self.test_tracker.get_coordinate_heatmap("Tatooine", days=7)
        
        self.assertIsInstance(coord_data, list)
        
        if coord_data:
            for point in coord_data:
                self.assertIn('x', point)
                self.assertIn('y', point)
                self.assertIn('count', point)
                self.assertIn('intensity', point)
                self.assertIsInstance(point['x'], int)
                self.assertIsInstance(point['y'], int)
                self.assertIsInstance(point['count'], int)
                self.assertIsInstance(point['intensity'], float)
    
    def test_weekly_stats(self):
        """Test weekly statistics generation."""
        self.test_tracker.process_session_logs()
        
        stats = self.test_tracker.get_weekly_stats()
        
        self.assertIn('period', stats)
        self.assertIn('quest_stats', stats)
        self.assertIn('city_stats', stats)
        self.assertIn('danger_stats', stats)
        self.assertIn('path_stats', stats)
        
        self.assertEqual(stats['period'], '7 days')
        self.assertIsInstance(stats['quest_stats'], dict)
        self.assertIsInstance(stats['city_stats'], dict)
        self.assertIsInstance(stats['danger_stats'], dict)
        self.assertIsInstance(stats['path_stats'], dict)
    
    def test_manual_data_addition(self):
        """Test manual data addition methods."""
        # Test adding travel path
        from_location = {"planet": "Tatooine", "city": "Mos Eisley", "x": 3600, "y": -4850}
        to_location = {"planet": "Naboo", "city": "Theed", "x": 5000, "y": -3000}
        
        initial_path_count = len(self.test_tracker.travel_paths)
        
        self.test_tracker.add_travel_path(
            from_location=from_location,
            to_location=to_location,
            session_hash="test_session",
            duration_minutes=30,
            method="shuttle"
        )
        
        self.assertEqual(len(self.test_tracker.travel_paths), initial_path_count + 1)
        
        # Test adding stuck event
        stuck_location = {"planet": "Corellia", "city": "Coronet", "zone": "coronet_city", "x": 4000, "y": -2000}
        
        initial_stuck_count = len(self.test_tracker.stuck_events)
        
        self.test_tracker.add_stuck_event(
            location=stuck_location,
            session_hash="test_session",
            duration_minutes=15,
            attempts=3,
            reason="quest_blocked"
        )
        
        self.assertEqual(len(self.test_tracker.stuck_events), initial_stuck_count + 1)
    
    def test_data_persistence(self):
        """Test data persistence and loading."""
        self.test_tracker.process_session_logs()
        
        # Add some manual data
        self.test_tracker.add_travel_path(
            from_location={"planet": "Test", "city": "City1", "x": 100, "y": 200},
            to_location={"planet": "Test", "city": "City2", "x": 300, "y": 400},
            session_hash="test_persistence",
            duration_minutes=20,
            method="direct"
        )
        
        # Save data
        self.test_tracker._save_data()
        
        # Create new tracker instance to test loading
        new_tracker = type(quest_heatmap_tracker)(
            logs_dir=str(self.temp_logs_dir),
            data_dir=str(self.test_tracker.data_dir),
            anonymize=True
        )
        
        # Load data
        new_tracker._load_data()
        
        # Verify data was loaded correctly
        self.assertGreater(len(new_tracker.travel_paths), 0)
        self.assertGreater(len(new_tracker.quest_events), 0)
    
    def test_data_filtering(self):
        """Test data filtering by time period."""
        # Create old data
        old_event = QuestEvent(
            quest_id="old_quest",
            quest_name="Old Quest",
            planet="Tatooine",
            city="Mos Eisley",
            coordinates=(3600, -4850),
            timestamp=(datetime.now() - timedelta(days=10)).isoformat(),
            action="start",
            session_hash="old_session"
        )
        
        # Create recent data
        recent_event = QuestEvent(
            quest_id="recent_quest",
            quest_name="Recent Quest",
            planet="Tatooine",
            city="Mos Espa",
            coordinates=(3520, -4800),
            timestamp=datetime.now().isoformat(),
            action="start",
            session_hash="recent_session"
        )
        
        self.test_tracker.quest_events = [old_event, recent_event]
        
        # Test filtering for last 7 days
        quest_data = self.test_tracker.get_quest_heatmap(days=7)
        
        # Should only include recent quest
        self.assertEqual(quest_data['total_quests'], 1)
        self.assertEqual(quest_data['top_quests'][0]['quest_id'], 'recent_quest')
    
    def test_error_handling(self):
        """Test error handling in data processing."""
        # Test with invalid session data
        invalid_session = {"invalid": "data"}
        
        # Should not raise exception
        try:
            self.test_tracker._process_session_data(invalid_session, "test_hash")
        except Exception as e:
            self.fail(f"Should handle invalid session data gracefully: {e}")
        
        # Test with invalid navigation event
        invalid_nav_event = {"invalid": "navigation_data"}
        
        try:
            self.test_tracker._process_navigation_event(invalid_nav_event)
        except Exception as e:
            self.fail(f"Should handle invalid navigation data gracefully: {e}")
    
    def test_clear_old_data(self):
        """Test clearing old data."""
        # Add some old data
        old_event = QuestEvent(
            quest_id="old_quest",
            quest_name="Old Quest",
            planet="Tatooine",
            city="Mos Eisley",
            coordinates=(3600, -4850),
            timestamp=(datetime.now() - timedelta(days=40)).isoformat(),
            action="start",
            session_hash="old_session"
        )
        
        # Add some recent data
        recent_event = QuestEvent(
            quest_id="recent_quest",
            quest_name="Recent Quest",
            planet="Tatooine",
            city="Mos Espa",
            coordinates=(3520, -4800),
            timestamp=datetime.now().isoformat(),
            action="start",
            session_hash="recent_session"
        )
        
        self.test_tracker.quest_events = [old_event, recent_event]
        
        # Clear data older than 30 days
        self.test_tracker.clear_old_data(days=30)
        
        # Should only have recent data
        self.assertEqual(len(self.test_tracker.quest_events), 1)
        self.assertEqual(self.test_tracker.quest_events[0].quest_id, "recent_quest")

class QuestHeatmapIntegrationTest(unittest.TestCase):
    """Integration tests for quest heatmap functionality."""
    
    def setUp(self):
        """Set up integration test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.test_tracker = type(quest_heatmap_tracker)(
            logs_dir=str(self.temp_dir),
            data_dir=str(self.temp_dir / "data"),
            anonymize=True
        )
    
    def tearDown(self):
        """Clean up integration test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_workflow(self):
        """Test complete workflow from session processing to dashboard data."""
        # Create comprehensive test data
        self.create_comprehensive_test_data()
        
        # Process session logs
        self.test_tracker.process_session_logs()
        
        # Test all dashboard endpoints
        self.test_dashboard_endpoints()
    
    def create_comprehensive_test_data(self):
        """Create comprehensive test data for integration testing."""
        # Create multiple session files with different scenarios
        sessions = [
            {
                "start_time": (datetime.now() - timedelta(days=1)).isoformat(),
                "quests_completed": 3,
                "total_xp": 1500,
                "time_spent": 3600.0,
                "activity_breakdown": {"quest": 5, "move": 8, "stuck": 1},
                "steps": [
                    {
                        "time": (datetime.now() - timedelta(hours=2)).isoformat(),
                        "type": "quest",
                        "id": "intro_quest",
                        "name": "Introduction Quest",
                        "action": "start",
                        "to": {"planet": "Tatooine", "city": "Mos Eisley", "x": 3600, "y": -4850}
                    },
                    {
                        "time": (datetime.now() - timedelta(hours=1, minutes=45)).isoformat(),
                        "type": "quest",
                        "id": "intro_quest",
                        "name": "Introduction Quest",
                        "action": "complete",
                        "xp": 500,
                        "to": {"planet": "Tatooine", "city": "Mos Eisley", "x": 3600, "y": -4850}
                    },
                    {
                        "time": (datetime.now() - timedelta(hours=1, minutes=30)).isoformat(),
                        "type": "move",
                        "to": {"planet": "Tatooine", "city": "Mos Espa", "x": 3520, "y": -4800}
                    },
                    {
                        "time": (datetime.now() - timedelta(hours=1, minutes=15)).isoformat(),
                        "type": "stuck",
                        "location": {"planet": "Tatooine", "city": "Mos Espa", "zone": "mos_espa", "x": 3520, "y": -4800},
                        "duration_minutes": 15,
                        "attempts": 3,
                        "reason": "navigation_failed"
                    }
                ]
            },
            {
                "start_time": (datetime.now() - timedelta(days=2)).isoformat(),
                "quests_completed": 2,
                "total_xp": 800,
                "time_spent": 2400.0,
                "activity_breakdown": {"quest": 3, "move": 5, "stuck": 2},
                "steps": [
                    {
                        "time": (datetime.now() - timedelta(days=2, hours=1)).isoformat(),
                        "type": "quest",
                        "id": "hunting_quest",
                        "name": "Hunting Quest",
                        "action": "start",
                        "to": {"planet": "Naboo", "city": "Theed", "x": 5000, "y": -3000}
                    },
                    {
                        "time": (datetime.now() - timedelta(days=2, minutes=30)).isoformat(),
                        "type": "stuck",
                        "location": {"planet": "Naboo", "city": "Theed", "zone": "theed_palace", "x": 5000, "y": -3000},
                        "duration_minutes": 20,
                        "attempts": 5,
                        "reason": "quest_blocked"
                    }
                ]
            }
        ]
        
        # Write session files
        for i, session_data in enumerate(sessions):
            session_file = self.temp_dir / f"session_integration_{i+1}.json"
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
    
    def test_dashboard_endpoints(self):
        """Test all dashboard data endpoints."""
        # Test weekly stats
        stats = self.test_tracker.get_weekly_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn('quest_stats', stats)
        self.assertIn('city_stats', stats)
        self.assertIn('danger_stats', stats)
        self.assertIn('path_stats', stats)
        
        # Test quest data
        quest_data = self.test_tracker.get_quest_heatmap(days=7)
        self.assertIsInstance(quest_data, dict)
        self.assertIn('top_quests', quest_data)
        
        # Test city data
        city_data = self.test_tracker.get_city_heatmap(days=7)
        self.assertIsInstance(city_data, dict)
        self.assertIn('top_cities', city_data)
        
        # Test danger zones
        danger_data = self.test_tracker.get_danger_zones(days=7)
        self.assertIsInstance(danger_data, dict)
        self.assertIn('danger_zones', danger_data)
        
        # Test popular paths
        paths_data = self.test_tracker.get_popular_paths(days=7)
        self.assertIsInstance(paths_data, dict)
        self.assertIn('popular_paths', paths_data)
        
        # Test coordinate heatmap
        coord_data = self.test_tracker.get_coordinate_heatmap("Tatooine", days=7)
        self.assertIsInstance(coord_data, list)

def run_tests():
    """Run all tests."""
    print("=" * 80)
    print("BATCH 098 - QUEST HEATMAP & POPULAR PATHS TRACKER TESTS")
    print("=" * 80)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add unit tests
    test_suite.addTest(unittest.makeSuite(QuestHeatmapTrackerTest))
    
    # Add integration tests
    test_suite.addTest(unittest.makeSuite(QuestHeatmapIntegrationTest))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✓ All tests passed!")
        return True
    else:
        print("\n✗ Some tests failed!")
        return False

def main():
    """Main test function."""
    success = run_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 