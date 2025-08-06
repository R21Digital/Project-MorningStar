#!/usr/bin/env python3
"""
Demo script for Batch 085 - Session Replay Viewer

This script demonstrates the session replay viewer functionality by:
1. Creating sample session logs
2. Testing the session sync utility
3. Starting the dashboard server
"""

import json
import os
import time
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from dashboard.session_sync import SessionSync


def create_sample_session_logs():
    """Create sample session logs for testing."""
    sample_sessions = [
        {
            "session_id": "demo_combat_session_001",
            "start_time": (datetime.now() - timedelta(hours=2)).isoformat(),
            "end_time": (datetime.now() - timedelta(hours=1)).isoformat(),
            "character_name": "DemoCombat",
            "character_level": 45,
            "profession": "Rifleman",
            "location": "Naboo - Theed Palace",
            "total_xp_gained": 2500,
            "total_credits_gained": 15000,
            "total_deaths": 2,
            "total_quests_completed": 3,
            "total_combat_actions": 25,
            "total_travel_events": 5,
            "total_errors": 1,
            "average_combat_duration": 45.5,
            "success_rate": 92.0,
            "efficiency_score": 0.85,
            "session_goals": "Combat training and quest completion",
            "session_mode": "combat",
            "notes": "Good session with some deaths but overall progress",
            "events": [
                {
                    "event_type": "xp_gain",
                    "timestamp": (datetime.now() - timedelta(hours=1, minutes=45)).isoformat(),
                    "description": "Gained 800 XP from quest completion",
                    "location": "Theed Palace",
                    "coordinates": None,
                    "metadata": {"source": "quest_completion"},
                    "success": True,
                    "error_message": None,
                    "duration": 120,
                    "xp_gained": 800,
                    "credits_gained": 5000,
                    "items_gained": ["Rifle Scope"],
                    "items_lost": None
                },
                {
                    "event_type": "combat",
                    "timestamp": (datetime.now() - timedelta(hours=1, minutes=30)).isoformat(),
                    "description": "Combat with Imperial Trooper",
                    "location": "Theed Palace",
                    "coordinates": None,
                    "metadata": {"enemy_type": "Imperial Trooper"},
                    "success": True,
                    "error_message": None,
                    "duration": 45,
                    "xp_gained": 300,
                    "credits_gained": 2000,
                    "items_gained": ["Blaster Rifle"],
                    "items_lost": None
                },
                {
                    "event_type": "death",
                    "timestamp": (datetime.now() - timedelta(hours=1, minutes=15)).isoformat(),
                    "description": "Death: Overwhelmed by multiple enemies",
                    "location": "Theed Palace",
                    "coordinates": None,
                    "metadata": {"reason": "Multiple enemies"},
                    "success": False,
                    "error_message": "Overwhelmed by multiple enemies",
                    "duration": 30,
                    "xp_gained": 0,
                    "credits_gained": 0,
                    "items_gained": None,
                    "items_lost": ["Medpack"]
                },
                {
                    "event_type": "whisper",
                    "timestamp": (datetime.now() - timedelta(hours=1, minutes=10)).isoformat(),
                    "description": "Whisper from GuildMaster: 'Need help with quest?'",
                    "location": "Theed Palace",
                    "coordinates": None,
                    "metadata": {"sender": "GuildMaster", "message": "Need help with quest?"},
                    "success": True,
                    "error_message": None,
                    "duration": None,
                    "xp_gained": None,
                    "credits_gained": None,
                    "items_gained": None,
                    "items_lost": None
                }
            ],
            "combat_events": [
                {
                    "combat_type": "attack",
                    "target_name": "Imperial Trooper",
                    "damage_dealt": 150,
                    "damage_received": 25,
                    "ability_used": "Rifle Shot",
                    "weapon_used": "Blaster Rifle",
                    "combat_duration": 45,
                    "victory": True,
                    "loot_gained": ["Blaster Rifle", "Credits"],
                    "xp_gained": 300,
                    "location": "Theed Palace",
                    "coordinates": None
                }
            ],
            "quest_events": [
                {
                    "quest_name": "Imperial Infiltration",
                    "quest_id": "quest_001",
                    "status": "completed",
                    "npc_name": "Captain Solo",
                    "location": "Theed Palace",
                    "objectives_completed": ["Defeat Imperial Troopers", "Retrieve Documents"],
                    "rewards_gained": ["Credits", "Rifle Scope"],
                    "xp_reward": 800,
                    "credit_reward": 5000,
                    "time_spent": 120,
                    "difficulty": "medium"
                }
            ]
        },
        {
            "session_id": "demo_quest_session_002",
            "start_time": (datetime.now() - timedelta(days=1)).isoformat(),
            "end_time": (datetime.now() - timedelta(days=1, hours=1)).isoformat(),
            "character_name": "DemoQuest",
            "character_level": 32,
            "profession": "Medic",
            "location": "Corellia - Coronet City",
            "total_xp_gained": 1800,
            "total_credits_gained": 8000,
            "total_deaths": 0,
            "total_quests_completed": 5,
            "total_combat_actions": 8,
            "total_travel_events": 12,
            "total_errors": 0,
            "average_combat_duration": 20.0,
            "success_rate": 100.0,
            "efficiency_score": 0.95,
            "session_goals": "Quest completion and exploration",
            "session_mode": "questing",
            "notes": "Excellent questing session with no deaths",
            "events": [
                {
                    "event_type": "quest_completion",
                    "timestamp": (datetime.now() - timedelta(days=1, minutes=30)).isoformat(),
                    "description": "Completed quest: Medical Supplies",
                    "location": "Coronet City",
                    "coordinates": None,
                    "metadata": {"quest_name": "Medical Supplies"},
                    "success": True,
                    "error_message": None,
                    "duration": 180,
                    "xp_gained": 400,
                    "credits_gained": 2000,
                    "items_gained": ["Medpack", "Stimpack"],
                    "items_lost": None
                },
                {
                    "event_type": "travel",
                    "timestamp": (datetime.now() - timedelta(days=1, minutes=45)).isoformat(),
                    "description": "Traveled to Coronet City",
                    "location": "Coronet City",
                    "coordinates": None,
                    "metadata": {"transport": "shuttle"},
                    "success": True,
                    "error_message": None,
                    "duration": 60,
                    "xp_gained": 0,
                    "credits_gained": -500,
                    "items_gained": None,
                    "items_lost": None
                }
            ],
            "combat_events": [],
            "quest_events": [
                {
                    "quest_name": "Medical Supplies",
                    "quest_id": "quest_002",
                    "status": "completed",
                    "npc_name": "Dr. Smith",
                    "location": "Coronet City",
                    "objectives_completed": ["Collect Medical Supplies", "Deliver to Doctor"],
                    "rewards_gained": ["Credits", "Medpack"],
                    "xp_reward": 400,
                    "credit_reward": 2000,
                    "time_spent": 180,
                    "difficulty": "easy"
                }
            ]
        },
        {
            "session_id": "demo_error_session_003",
            "start_time": (datetime.now() - timedelta(days=2)).isoformat(),
            "end_time": (datetime.now() - timedelta(days=2, hours=30)).isoformat(),
            "character_name": "DemoError",
            "character_level": 28,
            "profession": "Pistoleer",
            "location": "Tatooine - Mos Eisley",
            "total_xp_gained": 500,
            "total_credits_gained": 2000,
            "total_deaths": 3,
            "total_quests_completed": 1,
            "total_combat_actions": 15,
            "total_travel_events": 3,
            "total_errors": 5,
            "average_combat_duration": 15.0,
            "success_rate": 60.0,
            "efficiency_score": 0.40,
            "session_goals": "Combat training",
            "session_mode": "combat",
            "notes": "Difficult session with many errors and deaths",
            "events": [
                {
                    "event_type": "error",
                    "timestamp": (datetime.now() - timedelta(days=2, minutes=45)).isoformat(),
                    "description": "Error: Connection lost",
                    "location": "Mos Eisley",
                    "coordinates": None,
                    "metadata": {"error_type": "connection"},
                    "success": False,
                    "error_message": "Connection lost to server",
                    "duration": None,
                    "xp_gained": None,
                    "credits_gained": None,
                    "items_gained": None,
                    "items_lost": None
                },
                {
                    "event_type": "death",
                    "timestamp": (datetime.now() - timedelta(days=2, minutes=30)).isoformat(),
                    "description": "Death: Killed by Tusken Raider",
                    "location": "Mos Eisley",
                    "coordinates": None,
                    "metadata": {"reason": "Tusken Raider attack"},
                    "success": False,
                    "error_message": "Killed by Tusken Raider",
                    "duration": 20,
                    "xp_gained": 0,
                    "credits_gained": 0,
                    "items_gained": None,
                    "items_lost": ["Blaster Pistol"]
                }
            ],
            "combat_events": [
                {
                    "combat_type": "attack",
                    "target_name": "Tusken Raider",
                    "damage_dealt": 80,
                    "damage_received": 120,
                    "ability_used": "Pistol Shot",
                    "weapon_used": "Blaster Pistol",
                    "combat_duration": 20,
                    "victory": False,
                    "loot_gained": None,
                    "xp_gained": 0,
                    "location": "Mos Eisley",
                    "coordinates": None
                }
            ],
            "quest_events": [
                {
                    "quest_name": "Tusken Threat",
                    "quest_id": "quest_003",
                    "status": "failed",
                    "npc_name": "Mayor",
                    "location": "Mos Eisley",
                    "objectives_completed": [],
                    "rewards_gained": None,
                    "xp_reward": 0,
                    "credit_reward": 0,
                    "time_spent": 30,
                    "difficulty": "hard"
                }
            ]
        }
    ]
    
    # Create session_logs directory if it doesn't exist
    session_logs_dir = project_root / "session_logs"
    session_logs_dir.mkdir(exist_ok=True)
    
    # Write sample session logs
    for i, session in enumerate(sample_sessions):
        filename = f"session_{session['session_id']}.json"
        filepath = session_logs_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2)
        
        print(f"Created sample session log: {filename}")
    
    return len(sample_sessions)


def test_session_sync():
    """Test the session sync functionality."""
    print("\n=== Testing Session Sync ===")
    
    syncer = SessionSync()
    
    # Test sync status
    status = syncer.get_sync_status()
    print(f"Sync Status:")
    print(f"  Source files: {status['source_files']}")
    print(f"  Dashboard files: {status['dest_files']}")
    print(f"  Dashboard directory: {status['dashboard_dir']}")
    
    # Test session sync
    results = syncer.sync_sessions()
    print(f"\nSync Results:")
    print(f"  Found: {results['total_found']} files")
    print(f"  Copied: {results['copied']} files")
    print(f"  Skipped: {results['skipped']} files")
    print(f"  Errors: {results['errors']}")
    
    return results


def start_dashboard_server():
    """Start the dashboard server."""
    print("\n=== Starting Dashboard Server ===")
    print("Dashboard will be available at: http://127.0.0.1:8000")
    print("Session Replay Viewer: http://127.0.0.1:8000/sessions")
    print("Press Ctrl+C to stop the server")
    
    try:
        # Change to dashboard directory
        dashboard_dir = project_root / "dashboard"
        os.chdir(dashboard_dir)
        
        # Start the Flask server
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\nDashboard server stopped.")
    except Exception as e:
        print(f"Error starting dashboard server: {e}")


def main():
    """Main demo function."""
    print("=== Batch 085 - Session Replay Viewer Demo ===")
    print("This demo will:")
    print("1. Create sample session logs")
    print("2. Test session sync functionality")
    print("3. Start the dashboard server")
    print()
    
    # Create sample session logs
    print("Creating sample session logs...")
    num_sessions = create_sample_session_logs()
    print(f"Created {num_sessions} sample session logs")
    
    # Test session sync
    sync_results = test_session_sync()
    
    if sync_results['errors'] > 0:
        print(f"Warning: {sync_results['errors']} errors during sync")
    
    # Start dashboard server
    print("\nStarting dashboard server...")
    start_dashboard_server()


if __name__ == "__main__":
    main() 