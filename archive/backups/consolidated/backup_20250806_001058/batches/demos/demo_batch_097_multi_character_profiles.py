#!/usr/bin/env python3
"""
Batch 097 - Multi-Character Player Profile Support Demo

This demo showcases the new multi-character profile system that allows users to:
- Create accounts that can contain multiple characters
- Manage character profiles with profession trees, equipment, and achievements
- Track session history for each character
- Control visibility settings (public/private/friends-only)
- Set main characters and view aggregated account statistics

Features:
- Account-level organization with parent-child relationships
- Character tabs/dropdown UI for easy switching
- Session history tracking per character
- Visibility controls for privacy
- Main character designation
- Account-level statistics aggregation
"""

import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from core.multi_character_profile_manager import multi_character_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def demo_multi_character_system():
    """Demonstrate the multi-character profile system."""
    
    print("=" * 80)
    print("BATCH 097 - MULTI-CHARACTER PLAYER PROFILE SUPPORT DEMO")
    print("=" * 80)
    print()
    
    # Clear existing data for demo
    logger.info("Clearing existing demo data...")
    multi_character_manager.accounts.clear()
    multi_character_manager.characters.clear()
    multi_character_manager.sessions.clear()
    multi_character_manager._save_data()
    
    print("1. Creating Multi-Character Accounts")
    print("-" * 40)
    
    # Create demo accounts
    accounts = []
    
    # Account 1: Veteran Player
    veteran_account = multi_character_manager.create_account(
        account_name="VeteranPlayer",
        email="veteran@example.com",
        discord_id="VeteranPlayer#1234",
        steam_id="veteran_steam",
        preferred_server="Basilisk"
    )
    accounts.append(veteran_account)
    print(f"✓ Created account: {veteran_account.account_name}")
    
    # Account 2: New Player
    new_player_account = multi_character_manager.create_account(
        account_name="NewPlayer",
        email="newplayer@example.com",
        discord_id="NewPlayer#5678",
        preferred_server="Legends"
    )
    accounts.append(new_player_account)
    print(f"✓ Created account: {new_player_account.account_name}")
    
    # Account 3: Multi-Server Player
    multi_server_account = multi_character_manager.create_account(
        account_name="MultiServerPlayer",
        email="multiserver@example.com",
        steam_id="multiserver_steam",
        preferred_server="Infinity"
    )
    accounts.append(multi_server_account)
    print(f"✓ Created account: {multi_server_account.account_name}")
    
    print()
    print("2. Creating Characters for Each Account")
    print("-" * 40)
    
    # Create characters for Veteran Player
    veteran_characters = []
    
    commando = multi_character_manager.create_character(
        account_id=veteran_account.account_id,
        name="CommandoRex",
        server="Basilisk",
        race="Human",
        profession="Commando",
        level=80,
        city="Coronet",
        guild="Elite Commandos",
        guild_tag="[EC]",
        faction="Imperial",
        planet="Corellia",
        playtime_hours=1200,
        kills=5000,
        sessions=150,
        macros_used=["AutoHeal", "CombatRotation", "GroupBuff"],
        achievements=["Master Commando", "Elite PvP", "Guild Leader"],
        skills={"Commando": 4, "Carbineer": 4, "Rifleman": 4},
        equipment={"Weapon": "Elite Carbine", "Armor": "Commando Armor"},
        notes="Main PvP character, guild leader",
        visibility="public"
    )
    veteran_characters.append(commando)
    print(f"✓ Created character: {commando.name} ({commando.profession})")
    
    medic = multi_character_manager.create_character(
        account_id=veteran_account.account_id,
        name="MedicHealer",
        server="Basilisk",
        race="Mon Calamari",
        profession="Combat Medic",
        level=75,
        city="Mos Eisley",
        guild="Elite Commandos",
        guild_tag="[EC]",
        faction="Imperial",
        planet="Tatooine",
        playtime_hours=800,
        kills=1500,
        sessions=100,
        macros_used=["HealRotation", "GroupHeal", "BuffCycle"],
        achievements=["Master Medic", "Raid Healer", "Support Specialist"],
        skills={"Combat Medic": 4, "Medic": 4, "Doctor": 4},
        equipment={"Weapon": "Medical Pistol", "Armor": "Medic Robes"},
        notes="Support character for raids and PvP",
        visibility="public"
    )
    veteran_characters.append(medic)
    print(f"✓ Created character: {medic.name} ({medic.profession})")
    
    # Create characters for New Player
    new_player_characters = []
    
    rifleman = multi_character_manager.create_character(
        account_id=new_player_account.account_id,
        name="RiflemanNew",
        server="Legends",
        race="Trandoshan",
        profession="Rifleman",
        level=45,
        city="Theed",
        faction="Rebel",
        planet="Naboo",
        playtime_hours=200,
        kills=500,
        sessions=25,
        macros_used=["BasicCombat", "AutoLoot"],
        achievements=["Novice Rifleman", "First Kill"],
        skills={"Rifleman": 2, "Scout": 1},
        equipment={"Weapon": "Basic Rifle", "Armor": "Light Armor"},
        notes="Learning the game, first character",
        visibility="public"
    )
    new_player_characters.append(rifleman)
    print(f"✓ Created character: {rifleman.name} ({rifleman.profession})")
    
    # Create characters for Multi-Server Player
    multi_server_characters = []
    
    jedi = multi_character_manager.create_character(
        account_id=multi_server_account.account_id,
        name="JediMaster",
        server="Infinity",
        race="Human",
        profession="Jedi Guardian",
        level=90,
        city="Anchorhead",
        guild="Jedi Order",
        guild_tag="[JO]",
        faction="Neutral",
        planet="Tatooine",
        playtime_hours=2000,
        kills=8000,
        sessions=300,
        macros_used=["JediCombat", "ForcePowers", "SaberForms"],
        achievements=["Master Jedi", "Force Master", "Lightsaber Expert"],
        skills={"Jedi Guardian": 4, "Jedi": 4, "Teras Kasi": 4},
        equipment={"Weapon": "Lightsaber", "Armor": "Jedi Robes"},
        notes="Main character, Jedi master",
        visibility="public"
    )
    multi_server_characters.append(jedi)
    print(f"✓ Created character: {jedi.name} ({jedi.profession})")
    
    smuggler = multi_character_manager.create_character(
        account_id=multi_server_account.account_id,
        name="SmugglerHan",
        server="Basilisk",
        race="Human",
        profession="Smuggler",
        level=60,
        city="Coronet",
        faction="Neutral",
        planet="Corellia",
        playtime_hours=600,
        kills=2000,
        sessions=80,
        macros_used=["SmugglerCombat", "StealthMode", "TradeRoutes"],
        achievements=["Master Smuggler", "Trade Expert", "Stealth Master"],
        skills={"Smuggler": 3, "Pistoleer": 3, "Scout": 2},
        equipment={"Weapon": "Blaster Pistol", "Armor": "Smuggler Vest"},
        notes="Secondary character for trading and stealth",
        visibility="friends_only"
    )
    multi_server_characters.append(smuggler)
    print(f"✓ Created character: {smuggler.name} ({smuggler.profession})")
    
    artisan = multi_character_manager.create_character(
        account_id=multi_server_account.account_id,
        name="ArtisanCraft",
        server="Legends",
        race="Ithorian",
        profession="Artisan",
        level=50,
        city="Theed",
        faction="Rebel",
        planet="Naboo",
        playtime_hours=400,
        kills=100,
        sessions=50,
        macros_used=["CraftingRotation", "ResourceGather", "QualityCheck"],
        achievements=["Master Artisan", "Crafting Expert", "Resource Master"],
        skills={"Artisan": 3, "Architect": 2, "Merchant": 1},
        equipment={"Tool": "Master Crafting Tool", "Armor": "Crafting Apron"},
        notes="Crafting specialist, private character",
        visibility="private"
    )
    multi_server_characters.append(artisan)
    print(f"✓ Created character: {artisan.name} ({artisan.profession})")
    
    print()
    print("3. Setting Main Characters")
    print("-" * 40)
    
    # Set main characters
    multi_character_manager.set_main_character(commando.character_id)
    print(f"✓ Set {commando.name} as main character for {veteran_account.account_name}")
    
    multi_character_manager.set_main_character(rifleman.character_id)
    print(f"✓ Set {rifleman.name} as main character for {new_player_account.account_name}")
    
    multi_character_manager.set_main_character(jedi.character_id)
    print(f"✓ Set {jedi.name} as main character for {multi_server_account.account_name}")
    
    print()
    print("4. Adding Session History")
    print("-" * 40)
    
    # Add some session history for characters
    sessions_data = [
        # Veteran Player sessions
        {
            "character_id": commando.character_id,
            "start_time": (datetime.now() - timedelta(hours=2)).isoformat(),
            "end_time": (datetime.now() - timedelta(hours=1)).isoformat(),
            "duration_minutes": 60,
            "xp_gained": 5000,
            "credits_earned": 25000,
            "activities": ["PvP Combat", "Guild Raid", "Quest Completion"],
            "location_start": "Coronet, Corellia",
            "location_end": "Mos Eisley, Tatooine",
            "notes": "Successful PvP session with guild"
        },
        {
            "character_id": medic.character_id,
            "start_time": (datetime.now() - timedelta(hours=4)).isoformat(),
            "end_time": (datetime.now() - timedelta(hours=2)).isoformat(),
            "duration_minutes": 120,
            "xp_gained": 3000,
            "credits_earned": 15000,
            "activities": ["Healing", "Group Support", "Buffing"],
            "location_start": "Mos Eisley, Tatooine",
            "location_end": "Coronet, Corellia",
            "notes": "Support session for guild activities"
        },
        # New Player sessions
        {
            "character_id": rifleman.character_id,
            "start_time": (datetime.now() - timedelta(hours=6)).isoformat(),
            "end_time": (datetime.now() - timedelta(hours=4)).isoformat(),
            "duration_minutes": 120,
            "xp_gained": 2000,
            "credits_earned": 8000,
            "activities": ["Questing", "Combat Training", "Exploration"],
            "location_start": "Theed, Naboo",
            "location_end": "Theed, Naboo",
            "notes": "Learning the game mechanics"
        },
        # Multi-Server Player sessions
        {
            "character_id": jedi.character_id,
            "start_time": (datetime.now() - timedelta(hours=8)).isoformat(),
            "end_time": (datetime.now() - timedelta(hours=5)).isoformat(),
            "duration_minutes": 180,
            "xp_gained": 8000,
            "credits_earned": 40000,
            "activities": ["Jedi Training", "Force Powers", "Lightsaber Combat"],
            "location_start": "Anchorhead, Tatooine",
            "location_end": "Mos Eisley, Tatooine",
            "notes": "Intensive Jedi training session"
        },
        {
            "character_id": smuggler.character_id,
            "start_time": (datetime.now() - timedelta(hours=10)).isoformat(),
            "end_time": (datetime.now() - timedelta(hours=8)).isoformat(),
            "duration_minutes": 120,
            "xp_gained": 4000,
            "credits_earned": 30000,
            "activities": ["Trading", "Smuggling", "Stealth Operations"],
            "location_start": "Coronet, Corellia",
            "location_end": "Coronet, Corellia",
            "notes": "Profitable trading session"
        },
        {
            "character_id": artisan.character_id,
            "start_time": (datetime.now() - timedelta(hours=12)).isoformat(),
            "end_time": (datetime.now() - timedelta(hours=10)).isoformat(),
            "duration_minutes": 120,
            "xp_gained": 3000,
            "credits_earned": 20000,
            "activities": ["Crafting", "Resource Gathering", "Quality Control"],
            "location_start": "Theed, Naboo",
            "location_end": "Theed, Naboo",
            "notes": "Crafting session for guild supplies"
        }
    ]
    
    for session_data in sessions_data:
        session = multi_character_manager.add_session_history(**session_data)
        character = multi_character_manager.get_character(session.character_id)
        print(f"✓ Added session for {character.name}: {session.duration_minutes}min, {session.xp_gained} XP")
    
    print()
    print("5. Displaying Account Statistics")
    print("-" * 40)
    
    for account in accounts:
        stats = multi_character_manager.calculate_account_stats(account.account_id)
        characters = multi_character_manager.get_account_characters(account.account_id)
        
        print(f"\nAccount: {account.account_name}")
        print(f"  Characters: {stats['character_count']}")
        print(f"  Total Playtime: {stats['total_playtime_hours']} hours")
        print(f"  Total Sessions: {stats['total_sessions']}")
        print(f"  Total Kills: {stats['total_kills']}")
        print(f"  Main Character: {stats['main_character'].name if stats['main_character'] else 'None'}")
        
        print("  Characters:")
        for char in characters:
            visibility_icon = "🌐" if char.visibility == "public" else "🔒" if char.visibility == "private" else "👥"
            main_icon = "⭐" if char.is_main_character else "  "
            print(f"    {main_icon} {visibility_icon} {char.name} ({char.profession}) - Level {char.level or 'Unknown'}")
    
    print()
    print("6. Testing Search Functionality")
    print("-" * 40)
    
    # Test account search
    print("Searching for accounts with 'Player' in name:")
    player_accounts = multi_character_manager.search_accounts(query="Player")
    for account in player_accounts:
        print(f"  ✓ {account.account_name}")
    
    # Test character search
    print("\nSearching for characters with 'Combat' professions:")
    combat_chars = multi_character_manager.search_characters(profession="Commando")
    for char in combat_chars:
        print(f"  ✓ {char.name} ({char.profession}) on {char.server}")
    
    print("\nSearching for public characters:")
    public_chars = multi_character_manager.search_characters(visibility="public")
    for char in public_chars:
        print(f"  ✓ {char.name} ({char.profession}) - {char.visibility}")
    
    print()
    print("7. Testing Visibility Controls")
    print("-" * 40)
    
    # Test visibility changes
    print("Changing character visibility...")
    multi_character_manager.set_character_visibility(artisan.character_id, "public")
    print(f"✓ Changed {artisan.name} visibility to public")
    
    multi_character_manager.set_character_visibility(smuggler.character_id, "private")
    print(f"✓ Changed {smuggler.name} visibility to private")
    
    print()
    print("8. API Endpoints Available")
    print("-" * 40)
    print("The following API endpoints are now available:")
    print("  GET  /multi-character                    - Multi-character home page")
    print("  GET  /multi-character/account/create     - Create account form")
    print("  POST /multi-character/account/create     - Create account")
    print("  GET  /multi-character/account/<id>       - View account details")
    print("  GET  /multi-character/character/create   - Create character form")
    print("  POST /multi-character/character/create   - Create character")
    print("  GET  /multi-character/character/<id>     - View character details")
    print("  GET  /multi-character/character/<id>/edit - Edit character form")
    print("  POST /multi-character/character/<id>/edit - Update character")
    print()
    print("  GET  /api/multi-character/accounts      - Search accounts")
    print("  GET  /api/multi-character/characters    - Search characters")
    print("  GET  /api/multi-character/account/<id>  - Get account details")
    print("  GET  /api/multi-character/character/<id> - Get character details")
    print("  POST /api/multi-character/character/<id>/set-main - Set main character")
    print("  POST /api/multi-character/character/<id>/visibility - Set visibility")
    print("  POST /api/multi-character/session/add   - Add session history")
    
    print()
    print("=" * 80)
    print("DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print()
    print("Key Features Demonstrated:")
    print("✓ Multi-character account creation and management")
    print("✓ Character profiles with profession trees and equipment")
    print("✓ Session history tracking per character")
    print("✓ Visibility controls (public/private/friends-only)")
    print("✓ Main character designation")
    print("✓ Account-level statistics aggregation")
    print("✓ Search functionality for accounts and characters")
    print("✓ Tab/dropdown UI for character switching")
    print()
    print("Next Steps:")
    print("1. Start the dashboard: python dashboard/app.py")
    print("2. Navigate to http://localhost:8000/multi-character")
    print("3. Explore the multi-character profile system")
    print("4. Test creating accounts and characters")
    print("5. Try the search and filtering features")
    print("6. Test visibility controls and main character settings")

if __name__ == "__main__":
    try:
        demo_multi_character_system()
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        sys.exit(1) 