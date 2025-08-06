#!/usr/bin/env python3
"""
Demo Script for Batch 119 - SWGDB Private Session Viewer
Tests the enhanced session viewer with comprehensive session data.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from api.get_sessions_by_user import SessionAPI


class SessionViewerDemo:
    """Demo class for testing the enhanced session viewer."""
    
    def __init__(self):
        self.api = SessionAPI()
        self.demo_user_hash = "demo_user_119"
    
    def create_sample_sessions(self):
        """Create sample session data for testing."""
        sessions = []
        
        # Sample session 1 - Quest-focused session
        session1 = {
            "session_id": "demo_session_001",
            "character_name": "DemoCharacter",
            "start_time": (datetime.now() - timedelta(hours=3)).isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_minutes": 180,
            "xp_data": {
                "total_xp_gained": 15000,
                "xp_per_hour": 5000,
                "xp_events": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=2, minutes=30)).isoformat(),
                        "amount": 5000,
                        "profession": "combat",
                        "skill": "marksman",
                        "source": "quest",
                        "quest_name": "Bounty Hunt",
                        "zone": "Tatooine"
                    }
                ],
                "profession_breakdown": {
                    "combat": 10000,
                    "marksman": 5000
                },
                "skill_breakdown": {
                    "marksman": 8000,
                    "pistol": 7000
                },
                "source_breakdown": {
                    "quest": 12000,
                    "combat": 3000
                }
            },
            "credit_data": {
                "total_credits_gained": 25000,
                "credits_per_hour": 8333,
                "credit_events": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=2, minutes=30)).isoformat(),
                        "amount": 25000,
                        "source": "quest",
                        "balance_after": 75000,
                        "transaction_type": "gain"
                    }
                ],
                "balance_history": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=3)).isoformat(),
                        "balance": 50000
                    },
                    {
                        "timestamp": datetime.now().isoformat(),
                        "balance": 75000
                    }
                ]
            },
            "quest_data": {
                "total_quests_completed": 8,
                "quests_per_hour": 2.67,
                "quest_events": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=2, minutes=45)).isoformat(),
                        "quest_name": "Bounty Hunt",
                        "quest_type": "hunt",
                        "reward_type": "credits",
                        "reward_amount": 5000,
                        "zone": "Tatooine"
                    },
                    {
                        "timestamp": (datetime.now() - timedelta(hours=2, minutes=30)).isoformat(),
                        "quest_name": "Delivery Mission",
                        "quest_type": "delivery",
                        "reward_type": "xp",
                        "reward_amount": 2000,
                        "zone": "Naboo"
                    },
                    {
                        "timestamp": (datetime.now() - timedelta(hours=2, minutes=15)).isoformat(),
                        "quest_name": "Crafting Task",
                        "quest_type": "craft",
                        "reward_type": "items",
                        "reward_amount": 1000,
                        "zone": "Corellia"
                    }
                ],
                "quest_types": {
                    "hunt": 3,
                    "delivery": 3,
                    "craft": 2
                },
                "reward_types": {
                    "credits": 4,
                    "xp": 2,
                    "items": 2
                }
            },
            "location_data": {
                "total_locations_visited": 5,
                "unique_planets": ["Tatooine", "Naboo", "Corellia"],
                "unique_cities": ["Mos Eisley", "Theed", "Coronet"],
                "location_events": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=2, minutes=45)).isoformat(),
                        "planet": "Tatooine",
                        "city": "Mos Eisley",
                        "coordinates": [100, 200],
                        "duration_minutes": 45,
                        "purpose": "quest_hub"
                    },
                    {
                        "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                        "planet": "Naboo",
                        "city": "Theed",
                        "coordinates": [150, 300],
                        "duration_minutes": 30,
                        "purpose": "quest_hub"
                    }
                ],
                "travel_time_minutes": 15,
                "zone_efficiency": {
                    "Tatooine": 0.8,
                    "Naboo": 0.7,
                    "Corellia": 0.6
                }
            },
            "event_data": {
                "total_events": 12,
                "event_types": {
                    "communication": 3,
                    "stuck": 1,
                    "player_encounter": 2,
                    "guild_alert": 1
                },
                "communication_events": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=2, minutes=30)).isoformat(),
                        "event_type": "whisper",
                        "sender": "Player123",
                        "message": "Hey, are you available for a group quest?",
                        "response_sent": True,
                        "_sanitized": True
                    },
                    {
                        "timestamp": (datetime.now() - timedelta(hours=2, minutes=15)).isoformat(),
                        "event_type": "tell",
                        "sender": "GuildMate",
                        "message": "Thanks for the help with the quest!",
                        "response_sent": True,
                        "_sanitized": True
                    }
                ],
                "player_encounters": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=2, minutes=30)).isoformat(),
                        "location": "Mos Eisley, Tatooine",
                        "distance": 50,
                        "interaction_type": "detected",
                        "_player_name_removed": True
                    }
                ],
                "guild_alerts": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=2, minutes=45)).isoformat(),
                        "sender": "GuildLeader",
                        "message": "Guild meeting in 30 minutes",
                        "alert_type": "leader_message",
                        "priority": "medium",
                        "auto_reply_sent": True,
                        "reply_message": "Will be there!",
                        "_sanitized": True
                    }
                ],
                "afk_periods": [
                    {
                        "start_time": (datetime.now() - timedelta(hours=2, minutes=30)).isoformat(),
                        "end_time": (datetime.now() - timedelta(hours=2, minutes=25)).isoformat(),
                        "duration_minutes": 5,
                        "reason": "Bathroom break"
                    }
                ],
                "stuck_events": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=1, minutes=30)).isoformat(),
                        "location": "Mos Eisley Cantina",
                        "reason": "NPC not spawning",
                        "duration_seconds": 300
                    }
                ]
            },
            "performance_metrics": {
                "session_duration_minutes": 180,
                "total_actions": 150,
                "actions_per_hour": 50,
                "efficiency_score": 0.85,
                "unique_locations_visited": 5,
                "total_travel_time_minutes": 15,
                "unique_players_encountered": 2,
                "quests_completed": 8,
                "afk_periods": 1,
                "stuck_events": 1
            },
            "metadata": {
                "serialization_timestamp": datetime.now().isoformat(),
                "serializer_version": "1.0.0",
                "data_source": "ms11_bot",
                "original_session_keys": ["session_id", "character_name", "start_time"],
                "sanitization_applied": True,
                "session_mode": "quest",
                "character_name": "DemoCharacter",
                "serialization_error": False
            }
        }
        
        # Sample session 2 - Combat-focused session
        session2 = {
            "session_id": "demo_session_002",
            "character_name": "CombatChar",
            "start_time": (datetime.now() - timedelta(hours=6)).isoformat(),
            "end_time": (datetime.now() - timedelta(hours=4)).isoformat(),
            "duration_minutes": 120,
            "xp_data": {
                "total_xp_gained": 25000,
                "xp_per_hour": 12500,
                "xp_events": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=5, minutes=30)).isoformat(),
                        "amount": 15000,
                        "profession": "combat",
                        "skill": "marksman",
                        "source": "combat",
                        "zone": "Dantooine"
                    }
                ],
                "profession_breakdown": {
                    "combat": 20000,
                    "marksman": 5000
                },
                "skill_breakdown": {
                    "marksman": 15000,
                    "pistol": 10000
                },
                "source_breakdown": {
                    "combat": 20000,
                    "quest": 5000
                }
            },
            "credit_data": {
                "total_credits_gained": 15000,
                "credits_per_hour": 7500,
                "credit_events": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=5, minutes=30)).isoformat(),
                        "amount": 15000,
                        "source": "combat",
                        "balance_after": 90000,
                        "transaction_type": "gain"
                    }
                ],
                "balance_history": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=6)).isoformat(),
                        "balance": 75000
                    },
                    {
                        "timestamp": (datetime.now() - timedelta(hours=4)).isoformat(),
                        "balance": 90000
                    }
                ]
            },
            "quest_data": {
                "total_quests_completed": 3,
                "quests_per_hour": 1.5,
                "quest_events": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=5, minutes=45)).isoformat(),
                        "quest_name": "Combat Training",
                        "quest_type": "hunt",
                        "reward_type": "xp",
                        "reward_amount": 5000,
                        "zone": "Dantooine"
                    }
                ],
                "quest_types": {
                    "hunt": 3
                },
                "reward_types": {
                    "xp": 2,
                    "credits": 1
                }
            },
            "location_data": {
                "total_locations_visited": 3,
                "unique_planets": ["Dantooine"],
                "unique_cities": ["Khoonda"],
                "location_events": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=5, minutes=45)).isoformat(),
                        "planet": "Dantooine",
                        "city": "Khoonda",
                        "coordinates": [200, 400],
                        "duration_minutes": 120,
                        "purpose": "combat_grinding"
                    }
                ],
                "travel_time_minutes": 5,
                "zone_efficiency": {
                    "Dantooine": 0.9
                }
            },
            "event_data": {
                "total_events": 8,
                "event_types": {
                    "communication": 2,
                    "stuck": 0,
                    "player_encounter": 1,
                    "guild_alert": 0
                },
                "communication_events": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=5, minutes=30)).isoformat(),
                        "event_type": "whisper",
                        "sender": "CombatBuddy",
                        "message": "Great combat session!",
                        "response_sent": True,
                        "_sanitized": True
                    }
                ],
                "player_encounters": [
                    {
                        "timestamp": (datetime.now() - timedelta(hours=5, minutes=30)).isoformat(),
                        "location": "Dantooine Plains",
                        "distance": 100,
                        "interaction_type": "detected",
                        "_player_name_removed": True
                    }
                ],
                "guild_alerts": [],
                "afk_periods": [],
                "stuck_events": []
            },
            "performance_metrics": {
                "session_duration_minutes": 120,
                "total_actions": 200,
                "actions_per_hour": 100,
                "efficiency_score": 0.95,
                "unique_locations_visited": 3,
                "total_travel_time_minutes": 5,
                "unique_players_encountered": 1,
                "quests_completed": 3,
                "afk_periods": 0,
                "stuck_events": 0
            },
            "metadata": {
                "serialization_timestamp": datetime.now().isoformat(),
                "serializer_version": "1.0.0",
                "data_source": "ms11_bot",
                "original_session_keys": ["session_id", "character_name", "start_time"],
                "sanitization_applied": True,
                "session_mode": "combat",
                "character_name": "CombatChar",
                "serialization_error": False
            }
        }
        
        sessions = [session1, session2]
        return sessions
    
    def insert_demo_sessions(self):
        """Insert demo sessions into the database."""
        sessions = self.create_sample_sessions()
        
        print("Inserting demo sessions...")
        for session in sessions:
            success = self.api.insert_session(self.demo_user_hash, session)
            if success:
                print(f"✓ Inserted session: {session['session_id']}")
            else:
                print(f"✗ Failed to insert session: {session['session_id']}")
    
    def test_session_retrieval(self):
        """Test session retrieval with filters."""
        print("\nTesting session retrieval...")
        
        # Test basic retrieval
        sessions = self.api.get_sessions_by_user(self.demo_user_hash)
        print(f"✓ Retrieved {len(sessions)} sessions")
        
        # Test with character filter
        sessions = self.api.get_sessions_by_user(
            self.demo_user_hash, 
            {"character": "DemoCharacter"}
        )
        print(f"✓ Retrieved {len(sessions)} sessions for DemoCharacter")
        
        # Test with planet filter
        sessions = self.api.get_sessions_by_user(
            self.demo_user_hash, 
            {"planet": "Tatooine"}
        )
        print(f"✓ Retrieved {len(sessions)} sessions on Tatooine")
        
        # Test with profession filter
        sessions = self.api.get_sessions_by_user(
            self.demo_user_hash, 
            {"profession": "combat"}
        )
        print(f"✓ Retrieved {len(sessions)} sessions with combat profession")
    
    def test_statistics(self):
        """Test statistics generation."""
        print("\nTesting statistics generation...")
        
        stats = self.api.get_session_statistics(self.demo_user_hash)
        print(f"✓ Total sessions: {stats['total_sessions']}")
        print(f"✓ Total XP gained: {stats['total_xp_gained']}")
        print(f"✓ Total credits gained: {stats['total_credits_gained']}")
        print(f"✓ Total quests completed: {stats['total_quests_completed']}")
        print(f"✓ Total stuck events: {stats['total_stuck_events']}")
        print(f"✓ Total communication events: {stats['total_communication_events']}")
        print(f"✓ Characters: {stats['characters']}")
        print(f"✓ Planets: {stats['planets']}")
        print(f"✓ Professions: {stats['professions']}")
    
    def test_individual_session(self):
        """Test individual session retrieval."""
        print("\nTesting individual session retrieval...")
        
        session = self.api.get_session_by_id(self.demo_user_hash, "demo_session_001")
        if session:
            print(f"✓ Retrieved session: {session['session_id']}")
            print(f"  Character: {session['character_name']}")
            print(f"  Duration: {session['duration_minutes']} minutes")
            print(f"  XP Gained: {session['xp_data']['total_xp_gained']}")
            print(f"  Credits Gained: {session['credit_data']['total_credits_gained']}")
            print(f"  Quests Completed: {session['quest_data']['total_quests_completed']}")
            print(f"  Stuck Events: {len(session['event_data']['stuck_events'])}")
            print(f"  Communication Events: {len(session['event_data']['communication_events'])}")
        else:
            print("✗ Failed to retrieve session")
    
    def run_demo(self):
        """Run the complete demo."""
        print("=== SWGDB Private Session Viewer Demo ===")
        print("Batch 119 - Enhanced Session Viewer")
        print("=" * 50)
        
        # Insert demo sessions
        self.insert_demo_sessions()
        
        # Test various functionality
        self.test_session_retrieval()
        self.test_statistics()
        self.test_individual_session()
        
        print("\n" + "=" * 50)
        print("Demo completed successfully!")
        print("\nTo test the web interface:")
        print("1. Start the web server")
        print("2. Navigate to /my-sessions")
        print("3. Use the demo user token for authentication")
        print("4. Explore the enhanced features:")
        print("   - Quest breakdowns")
        print("   - Whisper alerts")
        print("   - Guild alerts")
        print("   - Player encounters")
        print("   - Enhanced filtering")
        print("   - PDF export functionality")


def main():
    """Main function to run the demo."""
    demo = SessionViewerDemo()
    demo.run_demo()


if __name__ == "__main__":
    main() 