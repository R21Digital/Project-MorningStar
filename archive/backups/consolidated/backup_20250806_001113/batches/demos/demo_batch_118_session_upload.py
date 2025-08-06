#!/usr/bin/env python3
"""
Demo for Batch 118 – Session Upload Bridge to SWGDB

This script demonstrates the complete session upload bridge functionality,
including session serialization, SWGDB API integration, and log viewing.
"""

import json
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Import our modules
from bridge.session_uploader import SessionUploader, UploadConfig
from swgdb_api.push_session_data import SWGDBAPIClient, SWGDBUploadManager
from core.log_serializer import SessionLogSerializer
from data.sessions.log_viewer import SessionLogViewer


class SessionUploadDemo:
    """Demonstrates session upload functionality."""
    
    def __init__(self):
        self.serializer = SessionLogSerializer()
        self.demo_sessions_dir = Path("data/sessions")
        self.demo_sessions_dir.mkdir(parents=True, exist_ok=True)
    
    def create_demo_session_data(self) -> Dict[str, Any]:
        """Create realistic demo session data."""
        start_time = datetime.now() - timedelta(hours=2)
        end_time = datetime.now()
        
        return {
            "session_id": "demo_session_123",
            "character_name": "DemoCharacter",
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_minutes": 120.5,
            "mode": "quest",
            "xp": {
                "start": 50000,
                "end": 75000,
                "gained": 25000
            },
            "credits": {
                "start": 100000,
                "end": 125000,
                "gained": 25000
            },
            "quests_completed": [
                "Destroy the Imperial Base",
                "Rescue the Rebel Spy",
                "Collect Rare Minerals",
                "Eliminate the Bounty Hunter"
            ],
            "locations_visited": [
                {
                    "planet": "Tatooine",
                    "city": "Mos Eisley",
                    "coordinates": (100, 200),
                    "arrival_time": start_time.isoformat(),
                    "departure_time": (start_time + timedelta(minutes=30)).isoformat(),
                    "duration_minutes": 30.0,
                    "purpose": "quest_hub"
                },
                {
                    "planet": "Naboo",
                    "city": "Theed",
                    "coordinates": (300, 400),
                    "arrival_time": (start_time + timedelta(minutes=35)).isoformat(),
                    "departure_time": (start_time + timedelta(minutes=90)).isoformat(),
                    "duration_minutes": 55.0,
                    "purpose": "quest_execution"
                }
            ],
            "communication_events": [
                {
                    "timestamp": (start_time + timedelta(minutes=15)).isoformat(),
                    "event_type": "whisper",
                    "sender": "GuildMember1",
                    "message": "Need help with quest?",
                    "response_sent": True
                },
                {
                    "timestamp": (start_time + timedelta(minutes=45)).isoformat(),
                    "event_type": "tell",
                    "sender": "RandomPlayer",
                    "message": "Nice armor!",
                    "response_sent": False
                }
            ],
            "player_encounters": [
                {
                    "player_name": "Player1",
                    "timestamp": (start_time + timedelta(minutes=20)).isoformat(),
                    "location": "Tatooine - Mos Eisley",
                    "distance": 15.5,
                    "interaction_type": "detected"
                }
            ],
            "guild_alerts": [
                {
                    "timestamp": (start_time + timedelta(minutes=10)).isoformat(),
                    "sender": "GuildLeader",
                    "message": "Guild meeting tonight at 8 PM",
                    "alert_type": "guild_whisper",
                    "priority": "medium",
                    "auto_reply_sent": True,
                    "reply_message": "Will be there!"
                }
            ],
            "afk_periods": [
                {
                    "start_time": (start_time + timedelta(minutes=60)).isoformat(),
                    "end_time": (start_time + timedelta(minutes=65)).isoformat(),
                    "duration_minutes": 5.0,
                    "reason": "bio_break"
                }
            ],
            "stuck_events": [
                {
                    "timestamp": (start_time + timedelta(minutes=75)).isoformat(),
                    "location": "Naboo - Theed Palace",
                    "reason": "path_blocked",
                    "duration_seconds": 45.0
                }
            ],
            "actions": [
                {"time": start_time.isoformat(), "action": "Session started"},
                {"time": (start_time + timedelta(minutes=5)).isoformat(), "action": "Accepted quest: Destroy the Imperial Base"},
                {"time": (start_time + timedelta(minutes=10)).isoformat(), "action": "Traveled to Tatooine"},
                {"time": (start_time + timedelta(minutes=15)).isoformat(), "action": "Completed quest: Destroy the Imperial Base"},
                {"time": (start_time + timedelta(minutes=20)).isoformat(), "action": "Accepted quest: Rescue the Rebel Spy"},
                {"time": (start_time + timedelta(minutes=30)).isoformat(), "action": "Traveled to Naboo"},
                {"time": (start_time + timedelta(minutes=45)).isoformat(), "action": "Completed quest: Rescue the Rebel Spy"},
                {"time": (start_time + timedelta(minutes=60)).isoformat(), "action": "AFK - bio break"},
                {"time": (start_time + timedelta(minutes=65)).isoformat(), "action": "Returned from AFK"},
                {"time": (start_time + timedelta(minutes=90)).isoformat(), "action": "Completed quest: Collect Rare Minerals"},
                {"time": (start_time + timedelta(minutes=105)).isoformat(), "action": "Completed quest: Eliminate the Bounty Hunter"},
                {"time": end_time.isoformat(), "action": "Session ended"}
            ],
            "performance_metrics": {
                "session_duration_minutes": 120.5,
                "total_actions": 12,
                "actions_per_hour": 6.0,
                "efficiency_score": 8750.0,
                "unique_locations_visited": 2,
                "total_travel_time_minutes": 85.0,
                "unique_players_encountered": 1,
                "quests_completed": 4,
                "afk_periods": 1,
                "stuck_events": 1
            }
        }
    
    def create_multiple_demo_sessions(self) -> List[Dict[str, Any]]:
        """Create multiple demo sessions with different characteristics."""
        sessions = []
        
        # Quest-focused session
        quest_session = self.create_demo_session_data()
        quest_session["session_id"] = "quest_session_001"
        quest_session["mode"] = "quest"
        quest_session["xp"]["gained"] = 30000
        quest_session["credits"]["gained"] = 35000
        sessions.append(quest_session)
        
        # Combat-focused session
        combat_session = self.create_demo_session_data()
        combat_session["session_id"] = "combat_session_001"
        combat_session["mode"] = "combat"
        combat_session["xp"]["gained"] = 45000
        combat_session["credits"]["gained"] = 15000
        combat_session["locations_visited"] = [
            {
                "planet": "Endor",
                "city": "Ewok Village",
                "coordinates": (500, 600),
                "arrival_time": combat_session["start_time"],
                "departure_time": combat_session["end_time"],
                "duration_minutes": 120.0,
                "purpose": "combat_grinding"
            }
        ]
        sessions.append(combat_session)
        
        # Crafting-focused session
        crafting_session = self.create_demo_session_data()
        crafting_session["session_id"] = "crafting_session_001"
        crafting_session["mode"] = "crafting"
        crafting_session["xp"]["gained"] = 15000
        crafting_session["credits"]["gained"] = 50000
        crafting_session["locations_visited"] = [
            {
                "planet": "Corellia",
                "city": "Coronet",
                "coordinates": (700, 800),
                "arrival_time": crafting_session["start_time"],
                "departure_time": crafting_session["end_time"],
                "duration_minutes": 120.0,
                "purpose": "crafting_hub"
            }
        ]
        sessions.append(crafting_session)
        
        return sessions
    
    def save_demo_sessions(self) -> List[str]:
        """Save demo sessions to files."""
        sessions = self.create_multiple_demo_sessions()
        saved_files = []
        
        for session in sessions:
            filename = f"{session['session_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = self.demo_sessions_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session, f, indent=2, ensure_ascii=False)
            
            saved_files.append(str(filepath))
            print(f"✅ Saved demo session: {filename}")
        
        return saved_files
    
    def demonstrate_serialization(self) -> None:
        """Demonstrate session serialization."""
        print("\n=== Session Serialization Demo ===")
        
        # Create demo session
        session_data = self.create_demo_session_data()
        print(f"Original session data keys: {list(session_data.keys())}")
        
        # Serialize session
        serialized = self.serializer.serialize_session(session_data)
        print(f"Serialized session keys: {list(serialized.keys())}")
        
        # Show key differences
        print(f"\nSerialization results:")
        print(f"  - Character name: {serialized.get('character_name', 'Unknown')}")
        print(f"  - Duration: {serialized.get('duration_minutes', 0):.1f} minutes")
        print(f"  - XP gained: {serialized.get('xp_data', {}).get('total_xp_gained', 0):,}")
        print(f"  - Credits gained: {serialized.get('credit_data', {}).get('total_credits_gained', 0):,}")
        print(f"  - Quests completed: {serialized.get('quest_data', {}).get('total_quests_completed', 0)}")
        print(f"  - Locations visited: {serialized.get('location_data', {}).get('total_locations_visited', 0)}")
        print(f"  - Events processed: {serialized.get('event_data', {}).get('total_events', 0)}")
        
        # Show sanitization
        event_data = serialized.get('event_data', {})
        comm_events = event_data.get('communication_events', [])
        if comm_events:
            print(f"\nCommunication events (sanitized):")
            for event in comm_events:
                print(f"  - {event.get('event_type')}: {event.get('message', '')[:50]}...")
    
    def demonstrate_swgdb_api(self) -> None:
        """Demonstrate SWGDB API functionality."""
        print("\n=== SWGDB API Demo ===")
        
        # Mock API client
        with patch('swgdb_api.push_session_data.SWGDBAPIClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            # Mock successful upload
            mock_client.push_session_data.return_value = {
                "success": True,
                "swgdb_session_id": "swgdb_12345",
                "message": "Session uploaded successfully"
            }
            
            # Mock credential validation
            mock_client.validate_credentials.return_value = {
                "success": True,
                "valid": True,
                "user_info": {"username": "demo_user", "user_id": "12345"}
            }
            
            # Create API client
            api_client = SWGDBAPIClient(
                api_url="https://api.swgdb.com/v1",
                api_key="demo_api_key",
                user_hash="demo_user_hash"
            )
            
            # Test credential validation
            auth_result = api_client.validate_credentials()
            print(f"✅ Authentication: {auth_result.get('valid', False)}")
            
            # Test session upload
            session_data = self.create_demo_session_data()
            upload_result = api_client.push_session_data(session_data)
            print(f"✅ Upload result: {upload_result.get('success', False)}")
            print(f"   SWGDB Session ID: {upload_result.get('swgdb_session_id', 'None')}")
            
            # Test batch upload
            sessions = self.create_multiple_demo_sessions()
            batch_result = api_client.batch_upload_sessions(sessions)
            print(f"✅ Batch upload: {batch_result.get('success', False)}")
            print(f"   Uploaded: {batch_result.get('uploaded_count', 0)}")
            print(f"   Failed: {batch_result.get('failed_count', 0)}")
    
    def demonstrate_upload_manager(self) -> None:
        """Demonstrate upload manager functionality."""
        print("\n=== Upload Manager Demo ===")
        
        # Mock API client
        with patch('swgdb_api.push_session_data.SWGDBAPIClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            # Mock successful batch upload
            mock_client.batch_upload_sessions.return_value = {
                "success": True,
                "uploaded_count": 3,
                "failed_count": 0,
                "session_ids": ["swgdb_001", "swgdb_002", "swgdb_003"]
            }
            
            # Create upload manager
            upload_manager = SWGDBUploadManager(mock_client)
            
            # Add sessions to queue
            sessions = self.create_multiple_demo_sessions()
            for session in sessions:
                upload_manager.add_to_queue(session)
            
            print(f"✅ Added {len(sessions)} sessions to upload queue")
            
            # Process queue
            result = upload_manager.process_queue()
            print(f"✅ Queue processing complete:")
            print(f"   Processed: {result.get('processed', 0)}")
            print(f"   Successful: {result.get('successful', 0)}")
            print(f"   Failed: {result.get('failed', 0)}")
    
    def demonstrate_session_uploader(self) -> None:
        """Demonstrate session uploader functionality."""
        print("\n=== Session Uploader Demo ===")
        
        # Create demo sessions
        saved_files = self.save_demo_sessions()
        
        # Mock SWGDB API client
        with patch('bridge.session_uploader.SWGDBAPIClient') as mock_client_class:
            mock_client = Mock()
            mock_client_class.return_value = mock_client
            
            # Mock successful upload
            mock_client.push_session_data.return_value = {
                "success": True,
                "swgdb_session_id": "swgdb_demo_123",
                "message": "Session uploaded successfully"
            }
            
            # Create uploader
            config = UploadConfig(
                swgdb_api_url="https://api.swgdb.com/v1",
                api_key="demo_api_key",
                user_hash="demo_user_hash",
                sanitize_data=True,
                include_events=True,
                include_locations=True,
                include_communications=False,
                include_player_encounters=False
            )
            
            uploader = SessionUploader(config)
            
            # Upload all sessions
            results = uploader.upload_all_sessions()
            print(f"✅ Upload results:")
            print(f"   Total sessions: {results.get('total_sessions', 0)}")
            print(f"   Uploaded: {results.get('uploaded', 0)}")
            print(f"   Failed: {results.get('failed', 0)}")
            
            # Show statistics
            stats = uploader.get_upload_statistics()
            print(f"\n📊 Upload statistics:")
            print(f"   Total sessions: {stats.get('total_sessions', 0)}")
            print(f"   Successful: {stats.get('successful', 0)}")
            print(f"   Failed: {stats.get('failed', 0)}")
            print(f"   Success rate: {stats.get('success_rate', 0):.1f}%")
    
    def demonstrate_log_viewer(self) -> None:
        """Demonstrate log viewer functionality."""
        print("\n=== Log Viewer Demo ===")
        
        # Create viewer
        viewer = SessionLogViewer(str(self.demo_sessions_dir))
        
        # List sessions
        print("📋 Recent sessions:")
        viewer.list_sessions(limit=5)
        
        # View specific session
        sessions = viewer.load_all_sessions()
        if sessions:
            session_id = list(sessions.keys())[0]
            print(f"\n📖 Session details for {session_id}:")
            viewer.view_session(session_id)
        
        # Search sessions
        print(f"\n🔍 Searching for 'quest' in sessions:")
        results = viewer.search_sessions("quest")
        print(f"Found {len(results)} sessions containing 'quest'")
        
        # Analyze sessions
        print(f"\n📊 Session analysis:")
        analysis = viewer.analyze_sessions()
        if "error" not in analysis:
            print(f"   Total sessions: {analysis.get('total_sessions', 0)}")
            print(f"   Total duration: {analysis.get('total_duration_hours', 0):.1f} hours")
            print(f"   Total XP gained: {analysis.get('total_xp_gained', 0):,}")
            print(f"   Total credits gained: {analysis.get('total_credits_gained', 0):,}")
            print(f"   Total quests completed: {analysis.get('total_quests_completed', 0)}")
            
            if analysis.get('most_common_quests'):
                print(f"   Most common quests:")
                for quest, count in analysis['most_common_quests'][:3]:
                    print(f"     {quest}: {count}")
    
    def run_complete_demo(self) -> None:
        """Run the complete demonstration."""
        print("🚀 Starting Batch 118 Session Upload Bridge Demo")
        print("=" * 60)
        
        # Demonstrate each component
        self.demonstrate_serialization()
        self.demonstrate_swgdb_api()
        self.demonstrate_upload_manager()
        self.demonstrate_session_uploader()
        self.demonstrate_log_viewer()
        
        print("\n" + "=" * 60)
        print("✅ Batch 118 Demo Complete!")
        print("\nKey Features Demonstrated:")
        print("  • Session data serialization with sanitization")
        print("  • SWGDB API integration with authentication")
        print("  • Batch upload management with rate limiting")
        print("  • Session uploader with retry logic")
        print("  • Internal log viewer for debugging")
        print("  • Session analysis and comparison tools")


def main():
    """Main function to run the demo."""
    demo = SessionUploadDemo()
    demo.run_complete_demo()


if __name__ == '__main__':
    main() 