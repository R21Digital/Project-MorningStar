#!/usr/bin/env python3
"""
Batch 160 - Player Notes System Demo

This script demonstrates the comprehensive player notes system including:
- Adding player encounters (new and duplicates)
- Searching and filtering by various criteria
- Generating statistics
- Session integration
- Data export capabilities
"""

import json
from datetime import datetime
from core.player_notes_collector import get_player_notes_collector, add_player_encounter
from core.player_notes_integration import get_player_notes_integration, PlayerNotesIntegration

def demo_basic_functionality():
    """Demonstrate basic player notes functionality."""
    print("🎯 Demo: Basic Player Notes Functionality")
    print("=" * 50)
    
    collector = get_player_notes_collector()
    
    # Add some sample player encounters
    sample_players = [
        {
            "player_name": "ZabrakWarrior",
            "guild_tag": "Mandalorian",
            "race": "zabrak",
            "faction": "mandalorian",
            "title": "Warrior",
            "location": {"planet": "Corellia", "city": "Coronet", "coordinates": [200, 400]},
            "notes": "Skilled combatant, often seen in PvP areas"
        },
        {
            "player_name": "TwilekDancer",
            "guild_tag": "Entertainers Guild",
            "race": "twilek",
            "faction": "neutral",
            "title": "Dancer",
            "location": {"planet": "Tatooine", "city": "Mos Eisley", "coordinates": [150, 300]},
            "notes": "Professional entertainer, performs regularly"
        },
        {
            "player_name": "IthorianSage",
            "guild_tag": "Sages Guild",
            "race": "ithorian",
            "faction": "neutral",
            "title": "Sage",
            "location": {"planet": "Corellia", "city": "Coronet", "coordinates": [200, 400]},
            "notes": "Wise scholar, often helps new players"
        },
        {
            "player_name": "WookieeWarrior",
            "guild_tag": "Rebel Alliance",
            "race": "wookiee",
            "faction": "rebel",
            "title": "Warrior",
            "location": {"planet": "Alderaan", "city": "Aldera", "coordinates": [250, 500]},
            "notes": "Loyal rebel fighter, strong in combat"
        },
        {
            "player_name": "JediMaster",
            "guild_tag": "Jedi Order",
            "race": "human",
            "faction": "jedi",
            "title": "Jedi Master",
            "location": {"planet": "Alderaan", "city": "Aldera", "coordinates": [250, 500]},
            "notes": "Experienced Jedi, mentors young padawans"
        }
    ]
    
    print("📝 Adding sample player encounters...")
    for player_data in sample_players:
        success = collector.add_player_encounter(**player_data)
        if success:
            print(f"✅ Added: {player_data['player_name']}")
        else:
            print(f"❌ Failed: {player_data['player_name']}")
    
    print(f"\n📊 Current Statistics:")
    stats = collector.get_statistics()
    print(f"   Total Players: {stats['total_players']}")
    print(f"   Total Encounters: {stats['total_encounters']}")
    print(f"   Recent Encounters (24h): {stats['recent_encounters']}")

def demo_duplicate_encounters():
    """Demonstrate handling of duplicate encounters."""
    print("\n🔄 Demo: Duplicate Encounter Handling")
    print("=" * 50)
    
    collector = get_player_notes_collector()
    
    # Add the same player multiple times with different information
    print("📝 Adding multiple encounters for the same player...")
    
    # First encounter
    collector.add_player_encounter(
        player_name="ZabrakWarrior",
        guild_tag="Mandalorian",
        race="zabrak",
        faction="mandalorian",
        location={"planet": "Corellia", "city": "Coronet"}
    )
    
    # Second encounter (same player, different location)
    collector.add_player_encounter(
        player_name="ZabrakWarrior",
        guild_tag="Mandalorian",
        race="zabrak",
        faction="mandalorian",
        title="Warrior",  # New information
        location={"planet": "Tatooine", "city": "Mos Eisley"},
        notes="Updated notes"
    )
    
    # Third encounter (same player, new location)
    collector.add_player_encounter(
        player_name="ZabrakWarrior",
        guild_tag="Mandalorian",
        race="zabrak",
        faction="mandalorian",
        title="Warrior",
        location={"planet": "Alderaan", "city": "Aldera"},
        notes="Final encounter notes"
    )
    
    # Check the player's updated information
    player_info = collector.get_player_info("ZabrakWarrior")
    if player_info:
        print(f"\n👤 Updated Player Info for ZabrakWarrior:")
        print(f"   Encounters: {player_info.encounter_count}")
        print(f"   Title: {player_info.title}")
        print(f"   Notes: {player_info.notes}")
        print(f"   Locations: {len(player_info.locations)} recorded")
        print(f"   First Seen: {player_info.first_seen}")
        print(f"   Last Seen: {player_info.last_seen}")

def demo_search_and_filter():
    """Demonstrate search and filter functionality."""
    print("\n🔍 Demo: Search and Filter Functionality")
    print("=" * 50)
    
    collector = get_player_notes_collector()
    
    # Search by guild
    print("🏛️  Searching for players in 'Mandalorian' guild:")
    mandalorian_players = collector.get_players_by_guild("Mandalorian")
    for player in mandalorian_players:
        print(f"   👤 {player.player_name} - {player.race} {player.faction}")
    
    # Search by faction
    print("\n⚔️  Searching for 'rebel' faction players:")
    rebel_players = collector.get_players_by_faction("rebel")
    for player in rebel_players:
        print(f"   👤 {player.player_name} [{player.guild_tag}] - {player.race}")
    
    # Search by race
    print("\n👽 Searching for 'zabrak' race players:")
    zabrak_players = collector.get_players_by_race("zabrak")
    for player in zabrak_players:
        print(f"   👤 {player.player_name} [{player.guild_tag}] - {player.faction}")

def demo_session_integration():
    """Demonstrate session integration functionality."""
    print("\n🎮 Demo: Session Integration")
    print("=" * 50)
    
    # Create integration instance
    integration = get_player_notes_integration()
    
    # Record some session encounters
    print("📝 Recording session encounters...")
    
    session_encounters = [
        {
            "player_name": "SessionPlayer1",
            "guild_tag": "Test Guild",
            "race": "human",
            "faction": "neutral",
            "location": {"planet": "Corellia", "city": "Coronet"},
            "notes": "Session encounter 1"
        },
        {
            "player_name": "SessionPlayer2",
            "guild_tag": "Test Guild",
            "race": "twilek",
            "faction": "rebel",
            "location": {"planet": "Tatooine", "city": "Mos Eisley"},
            "notes": "Session encounter 2"
        },
        {
            "player_name": "SessionPlayer3",
            "guild_tag": "Another Guild",
            "race": "wookiee",
            "faction": "imperial",
            "location": {"planet": "Alderaan", "city": "Aldera"},
            "notes": "Session encounter 3"
        }
    ]
    
    for encounter_data in session_encounters:
        success = integration.record_player_encounter(**encounter_data)
        if success:
            print(f"✅ Session encounter: {encounter_data['player_name']}")
        else:
            print(f"❌ Failed session encounter: {encounter_data['player_name']}")
    
    # Show session statistics
    print(f"\n📊 Session Statistics:")
    session_stats = integration.get_session_statistics()
    print(f"   Session Encounters: {session_stats['session_encounters']}")
    print(f"   Unique Players: {session_stats['unique_players']}")
    print(f"   Guilds Encountered: {session_stats['guilds_encountered']}")
    print(f"   Factions Encountered: {session_stats['factions_encountered']}")
    print(f"   Races Encountered: {session_stats['races_encountered']}")
    
    # Show session-specific filtering
    print(f"\n🏛️  Session players in 'Test Guild':")
    test_guild_players = integration.get_players_by_guild_in_session("Test Guild")
    for encounter in test_guild_players:
        print(f"   👤 {encounter.player_name} - {encounter.race} {encounter.faction}")

def demo_data_export():
    """Demonstrate data export functionality."""
    print("\n📤 Demo: Data Export Functionality")
    print("=" * 50)
    
    collector = get_player_notes_collector()
    
    # Export to JSON
    print("📄 Exporting to JSON format...")
    try:
        json_file = collector.export_data(format="json")
        print(f"✅ JSON export successful: {json_file}")
    except Exception as e:
        print(f"❌ JSON export failed: {e}")
    
    # Export to CSV
    print("\n📄 Exporting to CSV format...")
    try:
        csv_file = collector.export_data(format="csv")
        print(f"✅ CSV export successful: {csv_file}")
    except Exception as e:
        print(f"❌ CSV export failed: {e}")

def demo_cleanup():
    """Demonstrate data cleanup functionality."""
    print("\n🧹 Demo: Data Cleanup Functionality")
    print("=" * 50)
    
    collector = get_player_notes_collector()
    
    # Show current player count
    all_players = collector.get_all_players()
    print(f"📊 Current players: {len(all_players)}")
    
    # Cleanup old data (simulate by using a very short time period)
    print("🧹 Cleaning up old data...")
    removed_count = collector.cleanup_old_data(days_old=1)  # Remove data older than 1 day
    print(f"✅ Removed {removed_count} old player records")
    
    # Show updated player count
    all_players_after = collector.get_all_players()
    print(f"📊 Players after cleanup: {len(all_players_after)}")

def main():
    """Run the complete demo."""
    print("🚀 Batch 160 - Player Notes System Demo")
    print("=" * 60)
    print("This demo showcases the comprehensive player tracking system")
    print("that logs observed player data during MS11 sessions.")
    print()
    
    try:
        # Run all demo sections
        demo_basic_functionality()
        demo_duplicate_encounters()
        demo_search_and_filter()
        demo_session_integration()
        demo_data_export()
        demo_cleanup()
        
        print("\n🎉 Demo completed successfully!")
        print("\n📋 Summary:")
        print("   ✅ Basic player encounter recording")
        print("   ✅ Duplicate encounter handling")
        print("   ✅ Search and filter functionality")
        print("   ✅ Session integration")
        print("   ✅ Data export (JSON/CSV)")
        print("   ✅ Data cleanup")
        print("\n💡 The system is ready for production use!")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 