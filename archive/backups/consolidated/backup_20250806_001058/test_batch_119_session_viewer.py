#!/usr/bin/env python3
"""
Test Script for Batch 119 - SWGDB Private Session Viewer
Comprehensive testing of the enhanced session viewer features.
"""

import json
import os
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from api.get_sessions_by_user import SessionAPI


class TestSessionViewer(unittest.TestCase):
    """Test class for the enhanced session viewer."""
    
    def setUp(self):
        """Set up test environment."""
        self.api = SessionAPI()
        self.test_user_hash = "test_user_119"
        
        # Clean up any existing test data
        self.cleanup_test_data()
        
        # Create test sessions
        self.create_test_sessions()
    
    def tearDown(self):
        """Clean up after tests."""
        self.cleanup_test_data()
    
    def cleanup_test_data(self):
        """Clean up test session data."""
        try:
            # Delete test sessions
            sessions = self.api.get_sessions_by_user(self.test_user_hash)
            for session in sessions:
                self.api.delete_session(self.test_user_hash, session['session_id'])
        except Exception as e:
            print(f"Cleanup warning: {e}")
    
    def create_test_sessions(self):
        """Create comprehensive test session data."""
        sessions = []
        
        # Test session with all features
        session1 = {
            "session_id": "test_session_001",
            "character_name": "TestCharacter",
            "start_time": (datetime.now() - timedelta(hours=4)).isoformat(),
            "end_time": (datetime.now() - timedelta(hours=2)).isoformat(),
            "duration_minutes": 120,
            "xp_data": {
                "total_xp_gained": 20000,
                "xp_per_hour": 10000,
                "xp_events": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=3, minutes=30)).isoformat(),
                        "amount": 10000,
                        "profession": "combat",
                        "skill": "marksman",
                        "source": "quest",
                        "quest_name": "Test Quest",
                        "zone": "Tatooine"
                    }
                ],
                "profession_breakdown": {
                    "combat": 15000,
                    "marksman": 5000
                },
                "skill_breakdown": {
                    "marksman": 12000,
                    "pistol": 8000
                },
                "source_breakdown": {
                    "quest": 15000,
                    "combat": 5000
                }
            },
            "credit_data": {
                "total_credits_gained": 30000,
                "credits_per_hour": 15000,
                "credit_events": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=3, minutes=30)).isoformat(),
                        "amount": 30000,
                        "source": "quest",
                        "balance_after": 80000,
                        "transaction_type": "gain"
                    }
                ],
                "balance_history": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=4)).isoformat(),
                        "balance": 50000
                    },
                    {
                        "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                        "balance": 80000
                    }
                ]
            },
            "quest_data": {
                "total_quests_completed": 10,
                "quests_per_hour": 5.0,
                "quest_events": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=3, minutes=45)).isoformat(),
                        "quest_name": "Bounty Hunt",
                        "quest_type": "hunt",
                        "reward_type": "credits",
                        "reward_amount": 5000,
                        "zone": "Tatooine"
                    },
                    {
                        "timestamp": (datetime.now() - timedelta(hours=3, minutes=30)).isoformat(),
                        "quest_name": "Delivery Mission",
                        "quest_type": "delivery",
                        "reward_type": "xp",
                        "reward_amount": 2000,
                        "zone": "Naboo"
                    },
                    {
                        "timestamp": (datetime.now() - timedelta(hours=3, minutes=15)).isoformat(),
                        "quest_name": "Crafting Task",
                        "quest_type": "craft",
                        "reward_type": "items",
                        "reward_amount": 1000,
                        "zone": "Corellia"
                    }
                ],
                "quest_types": {
                    "hunt": 4,
                    "delivery": 3,
                    "craft": 3
                },
                "reward_types": {
                    "credits": 5,
                    "xp": 3,
                    "items": 2
                }
            },
            "location_data": {
                "total_locations_visited": 6,
                "unique_planets": ["Tatooine", "Naboo", "Corellia"],
                "unique_cities": ["Mos Eisley", "Theed", "Coronet"],
                "location_events": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=3, minutes=45)).isoformat(),
                        "planet": "Tatooine",
                        "city": "Mos Eisley",
                        "coordinates": [100, 200],
                        "duration_minutes": 60,
                        "purpose": "quest_hub"
                    },
                    {
                        "timestamp": (datetime.now() - timedelta(hours=3)).isoformat(),
                        "planet": "Naboo",
                        "city": "Theed",
                        "coordinates": [150, 300],
                        "duration_minutes": 45,
                        "purpose": "quest_hub"
                    }
                ],
                "travel_time_minutes": 15,
                "zone_efficiency": {
                    "Tatooine": 0.85,
                    "Naboo": 0.75,
                    "Corellia": 0.65
                }
            },
            "event_data": {
                "total_events": 15,
                "event_types": {
                    "communication": 4,
                    "stuck": 2,
                    "player_encounter": 3,
                    "guild_alert": 2
                },
                "communication_events": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=3, minutes=30)).isoformat(),
                        "event_type": "whisper",
                        "sender": "Player123",
                        "message": "Hey, are you available for a group quest?",
                        "response_sent": True,
                        "_sanitized": True
                    },
                    {
                        "timestamp": (datetime.now() - timedelta(hours=3, minutes=15)).isoformat(),
                        "event_type": "tell",
                        "sender": "GuildMate",
                        "message": "Thanks for the help with the quest!",
                        "response_sent": True,
                        "_sanitized": True
                    },
                    {
                        "timestamp": (datetime.now() - timedelta(hours=3)).isoformat(),
                        "event_type": "whisper",
                        "sender": "RandomPlayer",
                        "message": "Can you help me with this quest?",
                        "response_sent": False,
                        "_sanitized": True
                    }
                ],
                "player_encounters": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=3, minutes=30)).isoformat(),
                        "location": "Mos Eisley, Tatooine",
                        "distance": 50,
                        "interaction_type": "detected",
                        "_player_name_removed": True
                    },
                    {
                        "timestamp": (datetime.now() - timedelta(hours=3, minutes=15)).isoformat(),
                        "location": "Theed, Naboo",
                        "distance": 75,
                        "interaction_type": "whispered",
                        "_player_name_removed": True
                    }
                ],
                "guild_alerts": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=3, minutes=45)).isoformat(),
                        "sender": "GuildLeader",
                        "message": "Guild meeting in 30 minutes",
                        "alert_type": "leader_message",
                        "priority": "medium",
                        "auto_reply_sent": True,
                        "reply_message": "Will be there!",
                        "_sanitized": True
                    },
                    {
                        "timestamp": (datetime.now() - timedelta(hours=3, minutes=30)).isoformat(),
                        "sender": "GuildOfficer",
                        "message": "Urgent: Need help with raid",
                        "alert_type": "officer_message",
                        "priority": "high",
                        "auto_reply_sent": False,
                        "reply_message": "",
                        "_sanitized": True
                    }
                ],
                "afk_periods": [
                    {
                        "start_time": (datetime.now() - timedelta(hours=3, minutes=30)).isoformat(),
                        "end_time": (datetime.now() - timedelta(hours=3, minutes=25)).isoformat(),
                        "duration_minutes": 5,
                        "reason": "Bathroom break"
                    }
                ],
                "stuck_events": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=3, minutes=15)).isoformat(),
                        "location": "Mos Eisley Cantina",
                        "reason": "NPC not spawning",
                        "duration_seconds": 300
                    },
                    {
                        "timestamp": (datetime.now() - timedelta(hours=3)).isoformat(),
                        "location": "Theed Palace",
                        "reason": "Path blocked",
                        "duration_seconds": 180
                    }
                ]
            },
            "performance_metrics": {
                "session_duration_minutes": 120,
                "total_actions": 200,
                "actions_per_hour": 100,
                "efficiency_score": 0.9,
                "unique_locations_visited": 6,
                "total_travel_time_minutes": 15,
                "unique_players_encountered": 3,
                "quests_completed": 10,
                "afk_periods": 1,
                "stuck_events": 2
            },
            "metadata": {
                "serialization_timestamp": datetime.now().isoformat(),
                "serializer_version": "1.0.0",
                "data_source": "ms11_bot",
                "original_session_keys": ["session_id", "character_name", "start_time"],
                "sanitization_applied": True,
                "session_mode": "quest",
                "character_name": "TestCharacter",
                "serialization_error": False
            }
        }
        
        sessions.append(session1)
        
        # Insert test sessions
        for session in sessions:
            success = self.api.insert_session(self.test_user_hash, session)
            if not success:
                raise Exception(f"Failed to insert test session: {session['session_id']}")
    
    def test_basic_session_retrieval(self):
        """Test basic session retrieval functionality."""
        sessions = self.api.get_sessions_by_user(self.test_user_hash)
        
        self.assertIsInstance(sessions, list)
        self.assertGreater(len(sessions), 0)
        
        session = sessions[0]
        self.assertIn('session_id', session)
        self.assertIn('character_name', session)
        self.assertIn('xp_data', session)
        self.assertIn('credit_data', session)
        self.assertIn('quest_data', session)
        self.assertIn('event_data', session)
    
    def test_session_filtering(self):
        """Test session filtering by various criteria."""
        # Test character filter
        sessions = self.api.get_sessions_by_user(
            self.test_user_hash, 
            {"character": "TestCharacter"}
        )
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0]['character_name'], "TestCharacter")
        
        # Test planet filter
        sessions = self.api.get_sessions_by_user(
            self.test_user_hash, 
            {"planet": "Tatooine"}
        )
        self.assertEqual(len(sessions), 1)
        
        # Test profession filter
        sessions = self.api.get_sessions_by_user(
            self.test_user_hash, 
            {"profession": "combat"}
        )
        self.assertEqual(len(sessions), 1)
        
        # Test non-existent filters
        sessions = self.api.get_sessions_by_user(
            self.test_user_hash, 
            {"character": "NonExistentCharacter"}
        )
        self.assertEqual(len(sessions), 0)
    
    def test_session_statistics(self):
        """Test session statistics generation."""
        stats = self.api.get_session_statistics(self.test_user_hash)
        
        self.assertIsInstance(stats, dict)
        self.assertIn('total_sessions', stats)
        self.assertIn('total_xp_gained', stats)
        self.assertIn('total_credits_gained', stats)
        self.assertIn('total_quests_completed', stats)
        self.assertIn('total_stuck_events', stats)
        self.assertIn('total_communication_events', stats)
        self.assertIn('characters', stats)
        self.assertIn('planets', stats)
        self.assertIn('professions', stats)
        
        self.assertEqual(stats['total_sessions'], 1)
        self.assertEqual(stats['total_xp_gained'], 20000)
        self.assertEqual(stats['total_credits_gained'], 30000)
        self.assertEqual(stats['total_quests_completed'], 10)
        self.assertEqual(stats['total_stuck_events'], 2)
        self.assertEqual(stats['total_communication_events'], 4)
    
    def test_individual_session_retrieval(self):
        """Test individual session retrieval by ID."""
        session = self.api.get_session_by_id(self.test_user_hash, "test_session_001")
        
        self.assertIsNotNone(session)
        self.assertEqual(session['session_id'], "test_session_001")
        self.assertEqual(session['character_name'], "TestCharacter")
        
        # Test non-existent session
        session = self.api.get_session_by_id(self.test_user_hash, "non_existent_session")
        self.assertIsNone(session)
    
    def test_quest_data_structure(self):
        """Test quest data structure and breakdowns."""
        sessions = self.api.get_sessions_by_user(self.test_user_hash)
        session = sessions[0]
        
        quest_data = session['quest_data']
        self.assertEqual(quest_data['total_quests_completed'], 10)
        self.assertEqual(quest_data['quests_per_hour'], 5.0)
        
        # Test quest events
        quest_events = quest_data['quest_events']
        self.assertEqual(len(quest_events), 3)
        
        # Test quest types breakdown
        quest_types = quest_data['quest_types']
        self.assertEqual(quest_types['hunt'], 4)
        self.assertEqual(quest_types['delivery'], 3)
        self.assertEqual(quest_types['craft'], 3)
        
        # Test reward types breakdown
        reward_types = quest_data['reward_types']
        self.assertEqual(reward_types['credits'], 5)
        self.assertEqual(reward_types['xp'], 3)
        self.assertEqual(reward_types['items'], 2)
    
    def test_communication_events(self):
        """Test communication events and whisper alerts."""
        sessions = self.api.get_sessions_by_user(self.test_user_hash)
        session = sessions[0]
        
        comm_events = session['event_data']['communication_events']
        self.assertEqual(len(comm_events), 4)
        
        # Test whisper events
        whisper_events = [e for e in comm_events if e['event_type'] == 'whisper']
        self.assertEqual(len(whisper_events), 2)
        
        # Test response tracking
        responded_events = [e for e in comm_events if e.get('response_sent')]
        self.assertEqual(len(responded_events), 2)
        
        # Test sanitization
        sanitized_events = [e for e in comm_events if e.get('_sanitized')]
        self.assertEqual(len(sanitized_events), 4)
    
    def test_guild_alerts(self):
        """Test guild alerts functionality."""
        sessions = self.api.get_sessions_by_user(self.test_user_hash)
        session = sessions[0]
        
        guild_alerts = session['event_data']['guild_alerts']
        self.assertEqual(len(guild_alerts), 2)
        
        # Test priority levels
        high_priority = [a for a in guild_alerts if a['priority'] == 'high']
        medium_priority = [a for a in guild_alerts if a['priority'] == 'medium']
        
        self.assertEqual(len(high_priority), 1)
        self.assertEqual(len(medium_priority), 1)
        
        # Test auto-reply functionality
        auto_replied = [a for a in guild_alerts if a.get('auto_reply_sent')]
        self.assertEqual(len(auto_replied), 1)
    
    def test_player_encounters(self):
        """Test player encounters data."""
        sessions = self.api.get_sessions_by_user(self.test_user_hash)
        session = sessions[0]
        
        encounters = session['event_data']['player_encounters']
        self.assertEqual(len(encounters), 3)
        
        # Test privacy protection
        for encounter in encounters:
            self.assertTrue(encounter.get('_player_name_removed'))
    
    def test_stuck_events(self):
        """Test stuck events tracking."""
        sessions = self.api.get_sessions_by_user(self.test_user_hash)
        session = sessions[0]
        
        stuck_events = session['event_data']['stuck_events']
        self.assertEqual(len(stuck_events), 2)
        
        for event in stuck_events:
            self.assertIn('location', event)
            self.assertIn('reason', event)
            self.assertIn('duration_seconds', event)
            self.assertGreater(event['duration_seconds'], 0)
    
    def test_location_data(self):
        """Test location data and travel tracking."""
        sessions = self.api.get_sessions_by_user(self.test_user_hash)
        session = sessions[0]
        
        location_data = session['location_data']
        self.assertEqual(location_data['total_locations_visited'], 6)
        self.assertEqual(len(location_data['unique_planets']), 3)
        self.assertEqual(len(location_data['unique_cities']), 3)
        
        # Test location events
        location_events = location_data['location_events']
        self.assertEqual(len(location_events), 2)
        
        for event in location_events:
            self.assertIn('planet', event)
            self.assertIn('city', event)
            self.assertIn('coordinates', event)
            self.assertIn('duration_minutes', event)
            self.assertIn('purpose', event)
    
    def test_performance_metrics(self):
        """Test performance metrics calculation."""
        sessions = self.api.get_sessions_by_user(self.test_user_hash)
        session = sessions[0]
        
        metrics = session['performance_metrics']
        self.assertEqual(metrics['session_duration_minutes'], 120)
        self.assertEqual(metrics['total_actions'], 200)
        self.assertEqual(metrics['actions_per_hour'], 100)
        self.assertGreater(metrics['efficiency_score'], 0)
        self.assertLessEqual(metrics['efficiency_score'], 1)
    
    def test_session_deletion(self):
        """Test session deletion functionality."""
        # Insert a test session for deletion
        test_session = {
            "session_id": "delete_test_session",
            "character_name": "DeleteTest",
            "start_time": datetime.now().isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_minutes": 60,
            "xp_data": {"total_xp_gained": 1000},
            "credit_data": {"total_credits_gained": 1000},
            "quest_data": {"total_quests_completed": 1, "quest_events": []},
            "location_data": {"total_locations_visited": 1, "location_events": []},
            "event_data": {"total_events": 0, "communication_events": [], "stuck_events": []},
            "performance_metrics": {"session_duration_minutes": 60},
            "metadata": {"serialization_timestamp": datetime.now().isoformat()}
        }
        
        # Insert session
        success = self.api.insert_session(self.test_user_hash, test_session)
        self.assertTrue(success)
        
        # Verify session exists
        session = self.api.get_session_by_id(self.test_user_hash, "delete_test_session")
        self.assertIsNotNone(session)
        
        # Delete session
        success = self.api.delete_session(self.test_user_hash, "delete_test_session")
        self.assertTrue(success)
        
        # Verify session is deleted
        session = self.api.get_session_by_id(self.test_user_hash, "delete_test_session")
        self.assertIsNone(session)
    
    def test_data_sanitization(self):
        """Test data sanitization features."""
        sessions = self.api.get_sessions_by_user(self.test_user_hash)
        session = sessions[0]
        
        # Test communication event sanitization
        comm_events = session['event_data']['communication_events']
        for event in comm_events:
            self.assertTrue(event.get('_sanitized'))
        
        # Test player encounter sanitization
        encounters = session['event_data']['player_encounters']
        for encounter in encounters:
            self.assertTrue(encounter.get('_player_name_removed'))
        
        # Test guild alert sanitization
        guild_alerts = session['event_data']['guild_alerts']
        for alert in guild_alerts:
            self.assertTrue(alert.get('_sanitized'))


def run_tests():
    """Run all tests."""
    print("=== SWGDB Private Session Viewer Tests ===")
    print("Batch 119 - Enhanced Session Viewer")
    print("=" * 50)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSessionViewer)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print("Test Summary:")
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
    
    if result.wasSuccessful():
        print("\n✓ All tests passed!")
    else:
        print("\n✗ Some tests failed!")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 