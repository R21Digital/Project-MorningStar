#!/usr/bin/env python3
"""
MS11 Batch 089 - Session Report Dashboard Demo

This demo showcases the comprehensive session reporting system with:
- Enhanced session tracking with detailed metrics
- Location visit tracking with coordinates
- Player encounter detection and logging
- Communication event tracking (whispers, tells)
- Quest completion tracking
- AFK detection and duration tracking
- Stuck event detection and logging
- Dashboard integration with filtering and statistics
- Export functionality (JSON/YAML)
- Discord summary generation

Usage:
    python demo_batch_089_session_report_dashboard.py
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Import the new session reporting modules
from core.session_manager import SessionManager
from core.session_report_dashboard import session_dashboard


def create_mock_session_data() -> Dict[str, Any]:
    """Create realistic mock session data for demonstration."""
    
    # Create a session manager instance
    session = SessionManager(mode="combat")
    
    # Set initial values
    session.set_start_credits(50000)
    session.set_start_xp(150000)
    
    # Simulate location visits
    locations = [
        ("Tatooine", "Mos Eisley", (3520, -4800)),
        ("Tatooine", "Anchorhead", (-100, 200)),
        ("Corellia", "Coronet", (123, 456)),
        ("Naboo", "Theed", (789, -123)),
    ]
    
    for planet, city, coords in locations:
        session.record_location_visit(planet, city, coords)
        time.sleep(0.1)  # Simulate time passing
    
    # Simulate player encounters
    players = [
        ("DarthVader", "Mos Eisley Cantina", 50.0, "detected"),
        ("LukeSkywalker", "Anchorhead Market", 25.0, "whispered"),
        ("HanSolo", "Coronet Spaceport", 100.0, "grouped"),
        ("LeiaOrgana", "Theed Palace", 75.0, "detected"),
    ]
    
    for player, location, distance, interaction in players:
        session.record_player_encounter(player, location, distance, interaction)
        time.sleep(0.1)
    
    # Simulate communication events
    communications = [
        ("whisper", "DarthVader", "Looking for a pilot", True),
        ("tell", "LukeSkywalker", "Need help with quest", False),
        ("group_chat", "HanSolo", "Anyone want to group up?", True),
        ("whisper", "LeiaOrgana", "Thanks for the buff", True),
    ]
    
    for comm_type, sender, message, response in communications:
        session.record_communication(comm_type, sender, message, response)
        time.sleep(0.1)
    
    # Simulate quest completions
    quests = [
        "Eliminate Tusken Raiders",
        "Deliver Package to Coronet",
        "Collect Water Samples",
        "Defend Theed Palace",
    ]
    
    for quest in quests:
        session.record_quest_completion(quest)
        time.sleep(0.1)
    
    # Simulate position updates and stuck events
    positions = [
        (3520, -4800),  # Normal movement
        (3520, -4800),  # Stuck - same position
        (3520, -4800),  # Still stuck
        (3520, -4800),  # Still stuck - should trigger stuck event
        (3521, -4801),  # Moved - unstuck
        (3522, -4802),  # Normal movement
    ]
    
    for pos in positions:
        session.update_position(pos)
        time.sleep(0.1)
    
    # Simulate AFK periods
    session.check_afk_status()  # Should not trigger AFK
    time.sleep(0.1)
    
    # Simulate some activity
    session.add_action("Combat action")
    session.add_action("Loot collection")
    session.add_action("Skill training")
    
    # Set final values
    session.set_end_credits(75000)
    session.set_end_xp(180000)
    
    # End session
    session.end_session()
    
    return session


def demonstrate_session_dashboard():
    """Demonstrate the session dashboard functionality."""
    
    print("=" * 60)
    print("MS11 Batch 089 - Session Report Dashboard Demo")
    print("=" * 60)
    
    # Create mock session data
    print("\n1. Creating mock session data...")
    session = create_mock_session_data()
    print(f"✓ Session created: {session.session_id}")
    
    # Test session dashboard functionality
    print("\n2. Testing session dashboard functionality...")
    
    # Load all sessions
    all_sessions = session_dashboard.load_all_sessions()
    print(f"✓ Loaded {len(all_sessions)} sessions")
    
    # Get session details
    session_details = session_dashboard.get_session_details(session.session_id)
    if session_details:
        print(f"✓ Session details loaded for {session.session_id}")
        print(f"  - Mode: {session_details.get('mode')}")
        print(f"  - Duration: {session_details.get('duration_minutes', 0):.1f} minutes")
        print(f"  - Credits earned: {session_details.get('summary', {}).get('total_credits_earned', 0):,}")
        print(f"  - XP gained: {session_details.get('summary', {}).get('total_xp_gained', 0):,}")
    else:
        print("✗ Failed to load session details")
    
    # Test filtering
    print("\n3. Testing session filtering...")
    filters = {
        'mode': 'combat',
        'min_duration': 0.1,
        'min_credits': 1000
    }
    
    filtered_sessions = session_dashboard.filter_sessions(all_sessions, filters)
    print(f"✓ Filtered to {len(filtered_sessions)} sessions")
    
    # Test aggregate statistics
    print("\n4. Testing aggregate statistics...")
    aggregate_stats = session_dashboard.calculate_aggregate_stats(all_sessions)
    if aggregate_stats:
        print("✓ Aggregate statistics calculated:")
        print(f"  - Total sessions: {aggregate_stats.get('total_sessions', 0)}")
        print(f"  - Total credits: {aggregate_stats.get('total_credits_earned', 0):,}")
        print(f"  - Total XP: {aggregate_stats.get('total_xp_gained', 0):,}")
        print(f"  - Average duration: {aggregate_stats.get('avg_duration_minutes', 0):.1f} minutes")
        print(f"  - Credits per hour: {aggregate_stats.get('credits_per_hour', 0):,.0f}")
        print(f"  - XP per hour: {aggregate_stats.get('xp_per_hour', 0):,.0f}")
    else:
        print("✗ Failed to calculate aggregate statistics")
    
    # Test recent sessions
    print("\n5. Testing recent sessions...")
    recent_sessions = session_dashboard.get_recent_sessions(hours=24)
    print(f"✓ Found {len(recent_sessions)} recent sessions")
    
    # Test export functionality
    print("\n6. Testing export functionality...")
    export_json = session_dashboard.export_session_report(session.session_id, 'json')
    if export_json:
        print("✓ JSON export successful")
        
        # Save to file for inspection
        export_file = f"demo_session_export_{session.session_id}.json"
        with open(export_file, 'w') as f:
            f.write(export_json)
        print(f"  - Saved to: {export_file}")
    else:
        print("✗ JSON export failed")
    
    # Test Discord summary
    print("\n7. Testing Discord summary generation...")
    discord_summary = session_dashboard.generate_discord_summary(session.session_id)
    if discord_summary:
        print("✓ Discord summary generated:")
        print("-" * 40)
        print(discord_summary)
        print("-" * 40)
    else:
        print("✗ Discord summary generation failed")
    
    # Test session summary object
    print("\n8. Testing session summary object...")
    if all_sessions:
        session_data = all_sessions[0]
        summary = session_dashboard.get_session_summary(session_data)
        print("✓ Session summary created:")
        print(f"  - Session ID: {summary.session_id}")
        print(f"  - Mode: {summary.mode}")
        print(f"  - Duration: {summary.duration_minutes:.1f} minutes")
        print(f"  - Credits earned: {summary.credits_earned:,}")
        print(f"  - XP gained: {summary.xp_gained:,}")
        print(f"  - Quests completed: {summary.quests_completed}")
        print(f"  - Locations visited: {summary.locations_visited}")
        print(f"  - Player encounters: {summary.player_encounters}")
        print(f"  - Communication events: {summary.communication_events}")
        print(f"  - AFK time: {summary.afk_time_minutes:.1f} minutes")
        print(f"  - Stuck events: {summary.stuck_events}")
    else:
        print("✗ No sessions available for summary test")
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)
    
    # Print dashboard access information
    print("\nDashboard Access:")
    print("- Start the dashboard: python dashboard/app.py")
    print("- View sessions: http://localhost:5000/sessions")
    print("- API endpoints:")
    print("  - GET /api/sessions - List all sessions")
    print("  - GET /api/session/<id> - Get session details")
    print("  - GET /api/session/<id>/export - Export session")
    print("  - GET /api/session/<id>/discord-summary - Generate Discord summary")
    print("  - GET /api/sessions/recent - Get recent sessions")
    print("  - GET /api/sessions/stats - Get aggregate statistics")


def demonstrate_enhanced_features():
    """Demonstrate the enhanced session tracking features."""
    
    print("\n" + "=" * 60)
    print("Enhanced Session Tracking Features Demo")
    print("=" * 60)
    
    # Create a new session to demonstrate real-time tracking
    print("\n1. Creating session with enhanced tracking...")
    session = SessionManager(mode="questing")
    
    # Demonstrate location tracking
    print("\n2. Location tracking demonstration:")
    locations = [
        ("Tatooine", "Mos Eisley", (3520, -4800)),
        ("Tatooine", "Anchorhead", (-100, 200)),
        ("Corellia", "Coronet", (123, 456)),
    ]
    
    for planet, city, coords in locations:
        session.record_location_visit(planet, city, coords)
        print(f"  ✓ Visited {city}, {planet} at {coords}")
        time.sleep(0.1)
    
    # Demonstrate player encounter tracking
    print("\n3. Player encounter tracking:")
    encounters = [
        ("ObiWan", "Mos Eisley Cantina", 30.0, "detected"),
        ("Anakin", "Anchorhead Market", 45.0, "whispered"),
        ("Padme", "Coronet Spaceport", 60.0, "grouped"),
    ]
    
    for player, location, distance, interaction in encounters:
        session.record_player_encounter(player, location, distance, interaction)
        print(f"  ✓ {interaction.title()} {player} at {location} (distance: {distance})")
        time.sleep(0.1)
    
    # Demonstrate communication tracking
    print("\n4. Communication tracking:")
    communications = [
        ("whisper", "ObiWan", "Need help with quest", True),
        ("tell", "Anakin", "Can you buff me?", False),
        ("group_chat", "Padme", "Great group!", True),
    ]
    
    for comm_type, sender, message, response in communications:
        session.record_communication(comm_type, sender, message, response)
        print(f"  ✓ {comm_type.title()} from {sender}: {message} (response: {response})")
        time.sleep(0.1)
    
    # Demonstrate quest completion tracking
    print("\n5. Quest completion tracking:")
    quests = [
        "Defeat Tusken Raiders",
        "Deliver Package",
        "Collect Resources",
    ]
    
    for quest in quests:
        session.record_quest_completion(quest)
        print(f"  ✓ Completed: {quest}")
        time.sleep(0.1)
    
    # Demonstrate stuck detection
    print("\n6. Stuck detection:")
    positions = [
        (100, 100),  # Normal movement
        (100, 100),  # Same position
        (100, 100),  # Still stuck
        (100, 100),  # Still stuck
        (100, 100),  # Should trigger stuck event
        (101, 101),  # Moved - unstuck
    ]
    
    for i, pos in enumerate(positions):
        session.update_position(pos)
        print(f"  Position {i+1}: {pos}")
        time.sleep(0.1)
    
    # Demonstrate AFK detection
    print("\n7. AFK detection:")
    print("  Checking AFK status...")
    is_afk = session.check_afk_status()
    print(f"  Currently AFK: {is_afk}")
    
    # Add some activity to reset AFK
    session.add_action("Combat action")
    session.add_action("Loot collection")
    print("  Added activity to reset AFK timer")
    
    # End session
    print("\n8. Ending session...")
    session.set_start_credits(10000)
    session.set_end_credits(15000)
    session.set_start_xp(50000)
    session.set_end_xp(60000)
    session.end_session()
    
    print(f"  ✓ Session ended: {session.session_id}")
    print(f"  ✓ Duration: {session.duration:.1f} minutes")
    print(f"  ✓ Credits earned: {session.end_credits - session.start_credits:,}")
    print(f"  ✓ XP gained: {session.xp_gained:,}")
    
    # Show performance metrics
    print("\n9. Performance metrics:")
    metrics = session.performance_metrics
    print(f"  - Total duration: {metrics.get('total_duration_minutes', 0):.1f} minutes")
    print(f"  - Active time: {metrics.get('active_time_minutes', 0):.1f} minutes")
    print(f"  - AFK time: {metrics.get('afk_time_minutes', 0):.1f} minutes")
    print(f"  - AFK percentage: {metrics.get('afk_percentage', 0):.1f}%")
    print(f"  - Locations visited: {metrics.get('locations_visited_count', 0)}")
    print(f"  - Unique players: {metrics.get('unique_players_encountered', 0)}")
    print(f"  - Communication events: {metrics.get('communication_events_count', 0)}")
    print(f"  - Quests completed: {metrics.get('quests_completed_count', 0)}")
    print(f"  - Stuck events: {metrics.get('stuck_events_count', 0)}")
    print(f"  - Credits per hour: {metrics.get('credits_per_hour', 0):,.0f}")
    print(f"  - XP per hour: {metrics.get('xp_per_hour', 0):,.0f}")


def main():
    """Main demo function."""
    
    print("MS11 Batch 089 - Session Report Dashboard Demo")
    print("=" * 60)
    
    # Ensure logs directory exists
    os.makedirs("logs/sessions", exist_ok=True)
    
    # Run demonstrations
    demonstrate_enhanced_features()
    demonstrate_session_dashboard()
    
    print("\nDemo completed! Check the logs/sessions/ directory for generated session files.")
    print("You can also start the dashboard to view the sessions in the web interface.")


if __name__ == "__main__":
    main() 