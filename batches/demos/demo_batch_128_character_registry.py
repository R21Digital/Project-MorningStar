#!/usr/bin/env python3
"""
Batch 128 - Character Registry Demo

This demo showcases the multi-character tracker and character switcher functionality.
It demonstrates character creation, switching, session management, and statistics.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

from core.character_registry import get_registry, CharacterProfile, CharacterSession


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)


def print_section(title: str):
    """Print a formatted section header."""
    print(f"\n--- {title} ---")


def demo_character_creation():
    """Demo character creation functionality."""
    print_header("Character Creation Demo")
    
    registry = get_registry()
    discord_user_id = "user_123456789"
    
    # Create main character
    print_section("Creating Main Character")
    main_char = registry.create_character(
        discord_user_id=discord_user_id,
        name="DemoMarksman",
        server="Basilisk",
        race="Human",
        profession="Marksman",
        level=80,
        faction="Rebel",
        city="Coronet",
        guild="Demo Guild",
        guild_tag="[DEMO]",
        planet="Corellia",
        location="Coronet City",
        coordinates=(0.0, 0.0),
        role="main",
        is_main_character=True,
        auto_launch_enabled=False,
        notes="Main character for testing and development"
    )
    print(f"✅ Created main character: {main_char.name} (ID: {main_char.character_id})")
    
    # Create crafting alt
    print_section("Creating Crafting Alt")
    crafter_char = registry.create_character(
        discord_user_id=discord_user_id,
        name="DemoCrafter",
        server="Basilisk",
        race="Human",
        profession="Artisan",
        level=60,
        faction="Neutral",
        city="Theed",
        guild="Demo Guild",
        guild_tag="[DEMO]",
        planet="Naboo",
        location="Theed Palace",
        coordinates=(0.0, 0.0),
        role="alt",
        is_main_character=False,
        auto_launch_enabled=True,
        notes="Crafting alt character for resource gathering and item creation"
    )
    print(f"✅ Created crafting alt: {crafter_char.name} (ID: {crafter_char.character_id})")
    
    # Create boxing character
    print_section("Creating Boxing Character")
    boxer_char = registry.create_character(
        discord_user_id=discord_user_id,
        name="DemoBoxer",
        server="Basilisk",
        race="Wookiee",
        profession="Brawler",
        level=40,
        faction="Imperial",
        city="Mos Eisley",
        guild="Demo Guild",
        guild_tag="[DEMO]",
        planet="Tatooine",
        location="Mos Eisley",
        coordinates=(0.0, 0.0),
        role="boxer",
        is_main_character=False,
        auto_launch_enabled=True,
        notes="Boxing character for multi-account play and support roles"
    )
    print(f"✅ Created boxing character: {boxer_char.name} (ID: {boxer_char.character_id})")
    
    # Create support character
    print_section("Creating Support Character")
    support_char = registry.create_character(
        discord_user_id=discord_user_id,
        name="DemoMedic",
        server="Basilisk",
        race="Human",
        profession="Medic",
        level=35,
        faction="Rebel",
        city="Coronet",
        guild="Demo Guild",
        guild_tag="[DEMO]",
        planet="Corellia",
        location="Coronet City",
        coordinates=(0.0, 0.0),
        role="alt",
        is_main_character=False,
        auto_launch_enabled=False,
        notes="Support character for healing and buffing during group activities"
    )
    print(f"✅ Created support character: {support_char.name} (ID: {support_char.character_id})")
    
    return [main_char, crafter_char, boxer_char, support_char]


def demo_character_switching():
    """Demo character switching functionality."""
    print_header("Character Switching Demo")
    
    registry = get_registry()
    discord_user_id = "user_123456789"
    
    # Get all characters for the user
    characters = registry.get_characters_by_user(discord_user_id)
    print(f"📋 Found {len(characters)} characters for user {discord_user_id}")
    
    # Switch between characters
    for char in characters:
        print_section(f"Switching to {char.name}")
        switched_char = registry.switch_character(discord_user_id, char.name)
        if switched_char:
            print(f"✅ Switched to {switched_char.name}")
            print(f"   Level: {switched_char.level}")
            print(f"   Profession: {switched_char.profession}")
            print(f"   Faction: {switched_char.faction}")
            print(f"   Location: {switched_char.city}, {switched_char.planet}")
            print(f"   Last session: {switched_char.last_session_at or 'Never'}")
        else:
            print(f"❌ Failed to switch to {char.name}")
    
    # Get main character
    main_char = registry.get_main_character(discord_user_id)
    if main_char:
        print_section("Main Character")
        print(f"👑 Main character: {main_char.name}")
        print(f"   Role: {main_char.role}")
        print(f"   Auto-launch: {'Enabled' if main_char.auto_launch_enabled else 'Disabled'}")


def demo_session_management():
    """Demo session management functionality."""
    print_header("Session Management Demo")
    
    registry = get_registry()
    discord_user_id = "user_123456789"
    characters = registry.get_characters_by_user(discord_user_id)
    
    if not characters:
        print("❌ No characters found for session demo")
        return
    
    # Start sessions for each character
    sessions = []
    for char in characters[:2]:  # Demo with first 2 characters
        print_section(f"Starting Session for {char.name}")
        
        # Start session
        session = registry.start_session(
            character_id=char.character_id,
            mode="combat" if char.profession in ["Marksman", "Brawler"] else "crafting",
            session_config={
                "location": char.location,
                "planet": char.planet,
                "target_activities": ["questing", "combat"] if char.profession in ["Marksman", "Brawler"] else ["crafting", "gathering"]
            }
        )
        
        if session:
            print(f"✅ Started session {session.session_id}")
            print(f"   Mode: {session.mode}")
            print(f"   Start time: {session.start_time}")
            sessions.append((char, session))
        else:
            print(f"❌ Failed to start session for {char.name}")
    
    # Simulate some time passing
    print_section("Simulating Session Activity")
    time.sleep(2)  # Simulate 2 seconds of activity
    
    # End sessions with some metrics
    for char, session in sessions:
        print_section(f"Ending Session for {char.name}")
        
        # Generate some realistic metrics based on character type
        if char.profession in ["Marksman", "Brawler"]:
            xp_gained = 80000 if char.name == "DemoMarksman" else 40000
            credits_gained = 40000 if char.name == "DemoMarksman" else 20000
            actions = ["Combat", "Quest completion", "Travel"]
        else:
            xp_gained = 60000 if char.name == "DemoCrafter" else 35000
            credits_gained = 30000 if char.name == "DemoCrafter" else 17500
            actions = ["Crafting", "Resource gathering", "Trading"]
        
        playtime_minutes = 45.0  # 45 minutes session
        
        ended_session = registry.end_session(
            character_id=char.character_id,
            session_id=session.session_id,
            xp_gained=xp_gained,
            credits_gained=credits_gained,
            playtime_minutes=playtime_minutes,
            actions_completed=actions,
            notes=f"Successful {session.mode} session for {char.name}"
        )
        
        if ended_session:
            print(f"✅ Ended session {ended_session.session_id}")
            print(f"   XP gained: {ended_session.xp_gained:,}")
            print(f"   Credits earned: {ended_session.credits_gained:,}")
            print(f"   Playtime: {ended_session.playtime_minutes:.1f} minutes")
            print(f"   Actions: {', '.join(ended_session.actions_completed)}")
        else:
            print(f"❌ Failed to end session for {char.name}")


def demo_auto_launch_management():
    """Demo auto-launch functionality."""
    print_header("Auto-Launch Management Demo")
    
    registry = get_registry()
    discord_user_id = "user_123456789"
    
    # Get characters with auto-launch enabled
    auto_launch_chars = registry.get_auto_launch_characters(discord_user_id)
    print(f"🚀 Found {len(auto_launch_chars)} characters with auto-launch enabled")
    
    for char in auto_launch_chars:
        print(f"   - {char.name} ({char.profession}) - Auto-launch: {'✅' if char.auto_launch_enabled else '❌'}")
    
    # Toggle auto-launch for a character
    if auto_launch_chars:
        char_to_toggle = auto_launch_chars[0]
        print_section(f"Toggling Auto-Launch for {char_to_toggle.name}")
        
        new_state = registry.toggle_auto_launch(char_to_toggle.character_id)
        print(f"✅ Auto-launch {'enabled' if new_state else 'disabled'} for {char_to_toggle.name}")
        
        # Toggle back
        registry.toggle_auto_launch(char_to_toggle.character_id)
        print(f"✅ Auto-launch toggled back for {char_to_toggle.name}")


def demo_statistics():
    """Demo statistics functionality."""
    print_header("Statistics Demo")
    
    registry = get_registry()
    discord_user_id = "user_123456789"
    
    # Get user statistics
    stats = registry.get_user_statistics(discord_user_id)
    
    print_section("User Statistics")
    print(f"📊 Total characters: {stats['total_characters']}")
    print(f"📊 Active characters: {stats['active_characters']}")
    print(f"📊 Total playtime: {stats['total_playtime_hours']:.1f} hours")
    print(f"📊 Total XP gained: {stats['total_xp_gained']:,}")
    print(f"📊 Total credits earned: {stats['total_credits_earned']:,}")
    print(f"📊 Total sessions: {stats['total_sessions']}")
    
    if stats['main_character']:
        print(f"👑 Main character: {stats['main_character'].name}")
    
    print_section("Character Details")
    for char in stats['characters']:
        print(f"   {char.name} (Lv.{char.level} {char.profession})")
        print(f"     Role: {char.role}")
        print(f"     Faction: {char.faction}")
        print(f"     Playtime: {char.total_playtime_hours:.1f}h")
        print(f"     Sessions: {char.total_sessions}")
        print(f"     XP: {char.total_xp_gained:,}")
        print(f"     Credits: {char.total_credits_earned:,}")
        print(f"     Auto-launch: {'✅' if char.auto_launch_enabled else '❌'}")
        print()
    
    print_section("Recent Sessions")
    for session in stats['recent_sessions'][:3]:  # Show last 3 sessions
        char = next((c for c in stats['characters'] if c.character_id == session.character_id), None)
        char_name = char.name if char else "Unknown"
        print(f"   {char_name} - {session.mode} session")
        print(f"     XP: {session.xp_gained:,}")
        print(f"     Credits: {session.credits_gained:,}")
        print(f"     Duration: {session.playtime_minutes:.1f} minutes")
        print()


def demo_character_sessions():
    """Demo character session retrieval."""
    print_header("Character Sessions Demo")
    
    registry = get_registry()
    discord_user_id = "user_123456789"
    characters = registry.get_characters_by_user(discord_user_id)
    
    for char in characters[:2]:  # Demo with first 2 characters
        print_section(f"Sessions for {char.name}")
        
        # Get all sessions
        all_sessions = registry.get_character_sessions(char.character_id)
        print(f"📋 Total sessions: {len(all_sessions)}")
        
        # Get recent sessions (last 7 days)
        recent_sessions = registry.get_character_sessions(char.character_id, days=7)
        print(f"📋 Recent sessions (7 days): {len(recent_sessions)}")
        
        if all_sessions:
            latest_session = all_sessions[0]  # Most recent first
            print(f"📋 Latest session:")
            print(f"   Mode: {latest_session.mode}")
            print(f"   Start: {latest_session.start_time}")
            print(f"   End: {latest_session.end_time or 'Active'}")
            print(f"   XP: {latest_session.xp_gained:,}")
            print(f"   Credits: {latest_session.credits_gained:,}")
            print(f"   Duration: {latest_session.playtime_minutes:.1f} minutes")
            print(f"   Actions: {', '.join(latest_session.actions_completed)}")


def demo_data_export_import():
    """Demo data export and import functionality."""
    print_header("Data Export/Import Demo")
    
    registry = get_registry()
    discord_user_id = "user_123456789"
    characters = registry.get_characters_by_user(discord_user_id)
    
    if not characters:
        print("❌ No characters found for export demo")
        return
    
    # Export character data
    char_to_export = characters[0]
    print_section(f"Exporting {char_to_export.name}")
    
    export_data = registry.export_character_data(char_to_export.character_id)
    if export_data:
        print(f"✅ Exported data for {char_to_export.name}")
        print(f"   Character data: {len(export_data['character'])} fields")
        print(f"   Sessions: {len(export_data['sessions'])}")
        print(f"   Exported at: {export_data['exported_at']}")
        
        # Save to file for demonstration
        export_file = f"export_{char_to_export.name}_{int(time.time())}.json"
        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2)
        print(f"💾 Saved export to: {export_file}")
        
        # Import the data back (simulating transfer to another user)
        print_section("Importing Character Data")
        new_discord_user_id = "user_987654321"
        
        # Modify the export data for import
        import_data = export_data.copy()
        import_data['character']['discord_user_id'] = new_discord_user_id
        import_data['character']['name'] = f"{char_to_export.name}_Imported"
        
        imported_char = registry.import_character_data(import_data, new_discord_user_id)
        if imported_char:
            print(f"✅ Imported character: {imported_char.name}")
            print(f"   New ID: {imported_char.character_id}")
            print(f"   User ID: {imported_char.discord_user_id}")
            print(f"   Sessions imported: {len(import_data['sessions'])}")
        else:
            print("❌ Failed to import character data")
    else:
        print(f"❌ Failed to export data for {char_to_export.name}")


def demo_character_updates():
    """Demo character update functionality."""
    print_header("Character Updates Demo")
    
    registry = get_registry()
    discord_user_id = "user_123456789"
    characters = registry.get_characters_by_user(discord_user_id)
    
    if not characters:
        print("❌ No characters found for update demo")
        return
    
    char_to_update = characters[0]
    print_section(f"Updating {char_to_update.name}")
    
    print(f"📋 Current level: {char_to_update.level}")
    print(f"📋 Current location: {char_to_update.location}, {char_to_update.planet}")
    print(f"📋 Current notes: {char_to_update.notes}")
    
    # Update character
    updated_char = registry.update_character(
        char_to_update.character_id,
        level=char_to_update.level + 1,
        location="Updated Location",
        notes="Updated via demo script"
    )
    
    if updated_char:
        print(f"✅ Updated {updated_char.name}")
        print(f"   New level: {updated_char.level}")
        print(f"   New location: {updated_char.location}")
        print(f"   New notes: {updated_char.notes}")
        print(f"   Updated at: {updated_char.updated_at}")
    else:
        print(f"❌ Failed to update {char_to_update.name}")


def main():
    """Run the complete character registry demo."""
    print_header("Batch 128 - Character Registry Demo")
    print("This demo showcases the multi-character tracker and character switcher functionality.")
    
    try:
        # Run all demos
        demo_character_creation()
        demo_character_switching()
        demo_session_management()
        demo_auto_launch_management()
        demo_statistics()
        demo_character_sessions()
        demo_data_export_import()
        demo_character_updates()
        
        print_header("Demo Complete")
        print("✅ All character registry functionality demonstrated successfully!")
        print("\nKey Features Demonstrated:")
        print("  • Multi-character creation and management")
        print("  • Character switching and selection")
        print("  • Session tracking and metrics")
        print("  • Auto-launch profile management")
        print("  • Comprehensive statistics and reporting")
        print("  • Data export and import capabilities")
        print("  • Character updates and modifications")
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 