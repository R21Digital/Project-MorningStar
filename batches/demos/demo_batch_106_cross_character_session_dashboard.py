#!/usr/bin/env python3
"""
Demo for Batch 106 - Cross-Character Session Dashboard

This demo showcases the cross-character session dashboard functionality:
- Discord authentication integration
- Session sync management
- Cross-character data aggregation
- Dashboard visualization
- Export functionality

Usage:
    python demo_batch_106_cross_character_session_dashboard.py
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from core.cross_character_session_dashboard import (
    CrossCharacterSessionDashboard, 
    CrossCharacterSessionSummary,
    CharacterSessionData
)
from core.steam_discord_bridge import IdentityBridge, AuthStatus


def create_sample_session_data() -> Dict[str, Any]:
    """Create sample session data for demonstration."""
    return {
        "session_id": "demo_session_001",
        "character_name": "DemoCharacter",
        "server": "Argent",
        "start_time": datetime.now().isoformat(),
        "end_time": (datetime.now() + timedelta(hours=2)).isoformat(),
        "duration_minutes": 120.0,
        "mode": "medic",
        "summary": {
            "total_xp_gained": 15000,
            "total_credits_earned": 50000,
            "total_quests_completed": 5,
            "total_locations_visited": 8,
            "total_player_encounters": 3,
            "total_communication_events": 2,
            "total_afk_time_minutes": 10.0,
            "total_stuck_events": 1,
            "active_time_minutes": 110.0,
            "credits_per_hour": 25000.0,
            "xp_per_hour": 7500.0
        },
        "events": [
            {
                "event_type": "whisper",
                "timestamp": datetime.now().isoformat(),
                "sender": "Player1",
                "message": "Hello there!"
            },
            {
                "event_type": "quest_complete",
                "timestamp": datetime.now().isoformat(),
                "quest_name": "Sample Quest",
                "xp_reward": 3000
            }
        ]
    }


def create_sample_multi_character_data():
    """Create sample multi-character data for demonstration."""
    # Create directories
    data_dir = Path("data/multi_character")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Sample accounts data
    accounts_data = [
        {
            "account_id": "acc_001",
            "discord_id": "123456789",
            "account_name": "DemoAccount",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
    ]
    
    # Sample characters data
    characters_data = [
        {
            "character_id": "char_001",
            "account_id": "acc_001",
            "character_name": "DemoCharacter",
            "server": "Argent",
            "profession": "Medic",
            "level": 45,
            "is_main": True,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        },
        {
            "character_id": "char_002",
            "account_id": "acc_001",
            "character_name": "DemoCharacter2",
            "server": "Argent",
            "profession": "Rifleman",
            "level": 32,
            "is_main": False,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
    ]
    
    # Save accounts data
    with open(data_dir / "accounts.json", 'w', encoding='utf-8') as f:
        json.dump(accounts_data, f, indent=2)
    
    # Save characters data
    with open(data_dir / "characters.json", 'w', encoding='utf-8') as f:
        json.dump(characters_data, f, indent=2)
    
    # Create sync settings
    sync_settings = {
        "123456789": {
            "session_sync_enabled": True,
            "enabled_at": datetime.now().isoformat()
        }
    }
    
    with open(data_dir / "sync_settings.json", 'w', encoding='utf-8') as f:
        json.dump(sync_settings, f, indent=2)


def create_sample_session_logs():
    """Create sample session log files for demonstration."""
    sessions_dir = Path("logs/sessions")
    sessions_dir.mkdir(parents=True, exist_ok=True)
    
    # Create multiple session files for different characters
    sessions = [
        {
            "session_id": "session_001",
            "character_name": "DemoCharacter",
            "server": "Argent",
            "start_time": (datetime.now() - timedelta(days=1)).isoformat(),
            "end_time": (datetime.now() - timedelta(days=1) + timedelta(hours=2)).isoformat(),
            "duration_minutes": 120.0,
            "mode": "medic",
            "summary": {
                "total_xp_gained": 15000,
                "total_credits_earned": 50000,
                "total_quests_completed": 5,
                "total_locations_visited": 8,
                "total_player_encounters": 3,
                "total_communication_events": 2,
                "total_afk_time_minutes": 10.0,
                "total_stuck_events": 1,
                "active_time_minutes": 110.0,
                "credits_per_hour": 25000.0,
                "xp_per_hour": 7500.0
            },
            "events": [
                {
                    "event_type": "whisper",
                    "timestamp": (datetime.now() - timedelta(days=1)).isoformat(),
                    "sender": "Player1",
                    "message": "Hello there!"
                }
            ]
        },
        {
            "session_id": "session_002",
            "character_name": "DemoCharacter",
            "server": "Argent",
            "start_time": (datetime.now() - timedelta(days=2)).isoformat(),
            "end_time": (datetime.now() - timedelta(days=2) + timedelta(hours=1.5)).isoformat(),
            "duration_minutes": 90.0,
            "mode": "quest",
            "summary": {
                "total_xp_gained": 12000,
                "total_credits_earned": 35000,
                "total_quests_completed": 8,
                "total_locations_visited": 12,
                "total_player_encounters": 1,
                "total_communication_events": 0,
                "total_afk_time_minutes": 5.0,
                "total_stuck_events": 0,
                "active_time_minutes": 85.0,
                "credits_per_hour": 23333.0,
                "xp_per_hour": 8000.0
            },
            "events": []
        },
        {
            "session_id": "session_003",
            "character_name": "DemoCharacter2",
            "server": "Argent",
            "start_time": (datetime.now() - timedelta(days=3)).isoformat(),
            "end_time": (datetime.now() - timedelta(days=3) + timedelta(hours=3)).isoformat(),
            "duration_minutes": 180.0,
            "mode": "combat",
            "summary": {
                "total_xp_gained": 25000,
                "total_credits_earned": 75000,
                "total_quests_completed": 3,
                "total_locations_visited": 5,
                "total_player_encounters": 5,
                "total_communication_events": 3,
                "total_afk_time_minutes": 15.0,
                "total_stuck_events": 2,
                "active_time_minutes": 165.0,
                "credits_per_hour": 25000.0,
                "xp_per_hour": 8333.0
            },
            "events": [
                {
                    "event_type": "whisper",
                    "timestamp": (datetime.now() - timedelta(days=3)).isoformat(),
                    "sender": "Player2",
                    "message": "Great combat session!"
                },
                {
                    "event_type": "whisper",
                    "timestamp": (datetime.now() - timedelta(days=3) + timedelta(minutes=30)).isoformat(),
                    "sender": "Player3",
                    "message": "Thanks for the help!"
                }
            ]
        }
    ]
    
    # Save session files
    for i, session in enumerate(sessions, 1):
        filename = f"session_{i:03d}.json"
        with open(sessions_dir / filename, 'w', encoding='utf-8') as f:
            json.dump(session, f, indent=2)


def demo_authentication_check():
    """Demonstrate authentication checking functionality."""
    print("\n" + "="*60)
    print("DEMO: Authentication Check")
    print("="*60)
    
    dashboard = CrossCharacterSessionDashboard()
    
    # Test with sample Discord ID
    discord_id = "123456789"
    
    print(f"Checking authentication for Discord ID: {discord_id}")
    
    # Check Discord auth (will be False in demo since no real auth)
    auth_status = dashboard.check_discord_auth(discord_id)
    print(f"Discord Authentication: {'✓' if auth_status else '✗'}")
    
    # Check session sync status
    sync_status = dashboard.check_session_sync_enabled(discord_id)
    print(f"Session Sync Enabled: {'✓' if sync_status else '✗'}")
    
    if not auth_status:
        print("Note: Authentication is False because this is a demo without real Discord integration")
    
    return auth_status, sync_status


def demo_character_loading():
    """Demonstrate character loading functionality."""
    print("\n" + "="*60)
    print("DEMO: Character Loading")
    print("="*60)
    
    dashboard = CrossCharacterSessionDashboard()
    discord_id = "123456789"
    
    print(f"Loading characters for Discord ID: {discord_id}")
    
    characters = dashboard.get_user_characters(discord_id)
    print(f"Found {len(characters)} characters:")
    
    for char in characters:
        print(f"  - {char['character_name']} ({char['server']}) - {char['profession']} Lv.{char['level']}")
    
    return characters


def demo_session_loading():
    """Demonstrate session loading functionality."""
    print("\n" + "="*60)
    print("DEMO: Session Loading")
    print("="*60)
    
    dashboard = CrossCharacterSessionDashboard()
    
    # Load sessions for each character
    characters = [
        ("DemoCharacter", "Argent"),
        ("DemoCharacter2", "Argent")
    ]
    
    for char_name, server in characters:
        print(f"\nLoading sessions for {char_name} ({server}):")
        sessions = dashboard.load_character_sessions(char_name, server)
        print(f"  Found {len(sessions)} sessions")
        
        for session in sessions:
            session_id = session.get('session_id', 'Unknown')
            mode = session.get('mode', 'Unknown')
            duration = session.get('duration_minutes', 0)
            xp_gained = session.get('summary', {}).get('total_xp_gained', 0)
            print(f"    - {session_id}: {mode} mode, {duration:.1f} min, {xp_gained:,} XP")


def demo_cross_character_summary():
    """Demonstrate cross-character summary generation."""
    print("\n" + "="*60)
    print("DEMO: Cross-Character Summary")
    print("="*60)
    
    dashboard = CrossCharacterSessionDashboard()
    discord_id = "123456789"
    
    print(f"Generating cross-character summary for Discord ID: {discord_id}")
    
    # Get the summary
    summary = dashboard.get_cross_character_summary(discord_id)
    
    if summary:
        print("\n📊 CROSS-CHARACTER SUMMARY:")
        print(f"  Total Sessions: {summary.total_sessions}")
        print(f"  Total XP Gained: {summary.total_xp_gained:,}")
        print(f"  Total Credits Earned: {summary.total_credits_earned:,}")
        print(f"  Total Quests Completed: {summary.total_quests_completed}")
        print(f"  Total Locations Visited: {summary.total_locations_visited}")
        print(f"  Total Whisper Encounters: {summary.total_whisper_encounters}")
        print(f"  Total Duration: {summary.total_duration_hours:.1f} hours")
        print(f"  Average XP/Hour: {summary.average_xp_per_hour:.1f}")
        print(f"  Average Credits/Hour: {summary.average_credits_per_hour:.1f}")
        print(f"  Characters Played: {', '.join(summary.characters_played)}")
        
        print("\n🎮 MODE HISTORY:")
        for mode, count in summary.mode_history.items():
            print(f"  {mode}: {count} sessions")
        
        print("\n📈 RECENT ACTIVITY (Last 5):")
        for activity in summary.recent_activity[:5]:
            print(f"  {activity['character_name']} ({activity['server']}): "
                  f"{activity['mode']} mode, {activity['xp_gained']:,} XP, "
                  f"{activity['credits_earned']:,} credits")
    
    else:
        print("❌ No summary available (likely due to authentication requirements)")
    
    return summary


def demo_export_functionality():
    """Demonstrate export functionality."""
    print("\n" + "="*60)
    print("DEMO: Export Functionality")
    print("="*60)
    
    dashboard = CrossCharacterSessionDashboard()
    discord_id = "123456789"
    
    print(f"Testing export functionality for Discord ID: {discord_id}")
    
    # Test JSON export
    json_export = dashboard.export_summary(discord_id, 'json')
    if json_export:
        print("✓ JSON export successful")
        print(f"  Export size: {len(json_export)} characters")
    else:
        print("✗ JSON export failed")
    
    # Test CSV export
    csv_export = dashboard.export_summary(discord_id, 'csv')
    if csv_export:
        print("✓ CSV export successful")
        print(f"  Export size: {len(csv_export)} characters")
        print("  CSV Preview:")
        lines = csv_export.split('\n')[:5]
        for line in lines:
            print(f"    {line}")
    else:
        print("✗ CSV export failed")


def demo_sync_management():
    """Demonstrate session sync management."""
    print("\n" + "="*60)
    print("DEMO: Session Sync Management")
    print("="*60)
    
    dashboard = CrossCharacterSessionDashboard()
    discord_id = "123456789"
    
    print(f"Testing sync management for Discord ID: {discord_id}")
    
    # Check current status
    current_status = dashboard.check_session_sync_enabled(discord_id)
    print(f"Current sync status: {'Enabled' if current_status else 'Disabled'}")
    
    # Test disable
    print("\nTesting disable functionality...")
    success = dashboard.disable_session_sync(discord_id)
    print(f"Disable result: {'✓ Success' if success else '✗ Failed'}")
    
    # Check status after disable
    status_after_disable = dashboard.check_session_sync_enabled(discord_id)
    print(f"Status after disable: {'Enabled' if status_after_disable else 'Disabled'}")
    
    # Test enable
    print("\nTesting enable functionality...")
    success = dashboard.enable_session_sync(discord_id)
    print(f"Enable result: {'✓ Success' if success else '✗ Failed'}")
    
    # Check status after enable
    status_after_enable = dashboard.check_session_sync_enabled(discord_id)
    print(f"Status after enable: {'Enabled' if status_after_enable else 'Disabled'}")


def demo_dashboard_integration():
    """Demonstrate dashboard integration features."""
    print("\n" + "="*60)
    print("DEMO: Dashboard Integration")
    print("="*60)
    
    print("🎯 FEATURES IMPLEMENTED:")
    print("  ✓ Discord authentication requirement")
    print("  ✓ Session sync management")
    print("  ✓ Cross-character data aggregation")
    print("  ✓ XP and credits tracking")
    print("  ✓ Quest completion tracking")
    print("  ✓ Location visit tracking")
    print("  ✓ Whisper encounter tracking")
    print("  ✓ Mode history tracking")
    print("  ✓ Recent activity display")
    print("  ✓ Export functionality (JSON/CSV)")
    print("  ✓ Real-time data updates")
    
    print("\n🌐 WEB DASHBOARD:")
    print("  URL: /my-dashboard/sessions")
    print("  Requirements:")
    print("    - Discord account linked")
    print("    - Session sync enabled")
    print("    - Multi-character profiles configured")
    
    print("\n📊 DASHBOARD FEATURES:")
    print("  - Summary statistics cards")
    print("  - Character and mode breakdowns")
    print("  - Recent activity timeline")
    print("  - Performance metrics")
    print("  - Export buttons")
    print("  - Auto-refresh functionality")


def main():
    """Run the complete demo."""
    print("🚀 BATCH 106 DEMO: Cross-Character Session Dashboard")
    print("="*60)
    
    # Create sample data
    print("\n📁 Creating sample data...")
    create_sample_multi_character_data()
    create_sample_session_logs()
    print("✓ Sample data created successfully")
    
    # Run demos
    demo_authentication_check()
    demo_character_loading()
    demo_session_loading()
    demo_cross_character_summary()
    demo_export_functionality()
    demo_sync_management()
    demo_dashboard_integration()
    
    print("\n" + "="*60)
    print("✅ DEMO COMPLETE!")
    print("="*60)
    print("\n🎯 NEXT STEPS:")
    print("  1. Link your Discord account via /identity-bridge")
    print("  2. Enable session sync in your account settings")
    print("  3. Configure multi-character profiles")
    print("  4. Visit /my-dashboard/sessions to view your data")
    print("  5. Export your data using the dashboard buttons")
    
    print("\n📚 IMPLEMENTATION DETAILS:")
    print("  - Core module: core/cross_character_session_dashboard.py")
    print("  - Dashboard routes: dashboard/app.py")
    print("  - Template: dashboard/templates/my_dashboard_sessions.html")
    print("  - Integration: Discord auth + multi-character system")


if __name__ == "__main__":
    main() 