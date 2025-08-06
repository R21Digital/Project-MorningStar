#!/usr/bin/env python3
"""
MS11 Batch 090 - Public Player Profiles Demo

This script demonstrates the new public player profile functionality,
including profile creation, data upload, and profile management.
"""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

from core.player_profile_manager import profile_manager, PublicPlayerProfile

def create_sample_profiles():
    """Create sample player profiles for demonstration."""
    print("Creating sample player profiles...")
    
    # Sample profile 1 - Manual entry
    try:
        profile1 = profile_manager.create_profile(
            name="DarthVader",
            server="Basilisk",
            race="Human",
            profession="Swordsman",
            level=80,
            city="Mos Eisley",
            guild="Empire",
            guild_tag="EMP",
            faction="Imperial",
            planet="Tatooine",
            location="Mos Eisley Cantina",
            playtime_hours=1500,
            kills=2500,
            sessions=500,
            macros_used=["combat_macro", "heal_macro", "travel_macro"],
            achievements=["Master Swordsman", "Elite Warrior", "Legendary Fighter"],
            skills={"swordsman_novice": 4, "swordsman_master": 4},
            equipment={"weapon": "Lightsaber", "armor": "Imperial Armor"},
            notes="Dark Lord of the Sith, master of the Force."
        )
        print(f"✓ Created profile for {profile1.name}")
    except Exception as e:
        print(f"✗ Failed to create profile 1: {e}")
    
    # Sample profile 2 - JSON upload simulation
    try:
        json_data = {
            "name": "LukeSkywalker",
            "server": "Legends",
            "race": "Human",
            "profession": "Jedi Guardian",
            "level": 90,
            "city": "Anchorhead",
            "guild": "Rebel Alliance",
            "guild_tag": "REB",
            "faction": "Rebel",
            "planet": "Tatooine",
            "location": "Anchorhead Outpost",
            "playtime_hours": 2000,
            "kills": 1800,
            "sessions": 750,
            "macros_used": ["force_macro", "heal_macro", "travel_macro", "combat_macro"],
            "achievements": ["Jedi Master", "Force Adept", "Rebel Hero"],
            "skills": {"jedi_guardian_novice": 4, "jedi_guardian_master": 4},
            "equipment": {"weapon": "Lightsaber", "armor": "Jedi Robes"}
        }
        
        profile2 = profile_manager.create_profile(
            name="LukeSkywalker",
            server="Legends",
            race="Human",
            profession="Jedi Guardian",
            **json_data
        )
        print(f"✓ Created profile for {profile2.name}")
    except Exception as e:
        print(f"✗ Failed to create profile 2: {e}")
    
    # Sample profile 3 - Basic profile
    try:
        profile3 = profile_manager.create_profile(
            name="HanSolo",
            server="Infinity",
            race="Human",
            profession="Smuggler",
            level=75,
            city="Coronet",
            guild="Smugglers Guild",
            guild_tag="SMG",
            faction="Neutral",
            planet="Corellia",
            macros_used=["pilot_macro", "smuggle_macro"],
            achievements=["Master Smuggler", "Elite Pilot"],
            notes="Captain of the Millennium Falcon."
        )
        print(f"✓ Created profile for {profile3.name}")
    except Exception as e:
        print(f"✗ Failed to create profile 3: {e}")

def demonstrate_profile_management():
    """Demonstrate profile management functionality."""
    print("\nDemonstrating profile management...")
    
    # List all profiles
    profiles = profile_manager.list_profiles()
    print(f"✓ Found {len(profiles)} profiles")
    
    for profile in profiles:
        print(f"  - {profile.name} ({profile.server}) - {profile.profession}")
    
    # Test profile retrieval
    if profiles:
        test_profile = profiles[0]
        retrieved = profile_manager.get_profile(test_profile.name, test_profile.server)
        if retrieved:
            print(f"✓ Successfully retrieved profile for {retrieved.name}")
        else:
            print(f"✗ Failed to retrieve profile for {test_profile.name}")
    
    # Test profile update
    if profiles:
        test_profile = profiles[0]
        updated = profile_manager.update_profile(
            test_profile.name, 
            test_profile.server,
            notes="Updated via demo script"
        )
        if updated:
            print(f"✓ Successfully updated profile for {updated.name}")
        else:
            print(f"✗ Failed to update profile for {test_profile.name}")

def demonstrate_upload_functionality():
    """Demonstrate file upload functionality."""
    print("\nDemonstrating upload functionality...")
    
    # Create temporary JSON file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        upload_data = {
            "level": 85,
            "city": "Theed",
            "guild": "Royal Guard",
            "guild_tag": "RG",
            "faction": "Neutral",
            "planet": "Naboo",
            "playtime_hours": 1200,
            "kills": 1500,
            "sessions": 300,
            "macros_used": ["guard_macro", "patrol_macro"],
            "achievements": ["Royal Guard", "Protector of Naboo"],
            "skills": {"commando_novice": 4, "commando_master": 4},
            "equipment": {"weapon": "Blaster Rifle", "armor": "Royal Guard Armor"}
        }
        json.dump(upload_data, f, indent=2)
        temp_file_path = f.name
    
    try:
        # Simulate file upload
        from werkzeug.datastructures import FileStorage
        
        with open(temp_file_path, 'rb') as f:
            file_storage = FileStorage(
                stream=f,
                filename="character_data.json",
                content_type="application/json"
            )
            
            upload = profile_manager.upload_profile_data(
                profile_name="QueenAmidala",
                server="Basilisk",
                upload_type="json_data",
                file=file_storage
            )
            
            if upload.processed:
                print(f"✓ Successfully processed upload for QueenAmidala")
            else:
                print(f"✗ Upload processing failed: {upload.error_message}")
    
    except Exception as e:
        print(f"✗ Upload demonstration failed: {e}")
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

def demonstrate_api_endpoints():
    """Demonstrate API endpoint functionality."""
    print("\nDemonstrating API endpoints...")
    
    # Test profile listing
    profiles = profile_manager.list_profiles()
    print(f"✓ API: Found {len(profiles)} profiles")
    
    # Test server filtering
    basilisk_profiles = profile_manager.list_profiles(server="Basilisk")
    print(f"✓ API: Found {len(basilisk_profiles)} profiles on Basilisk")
    
    # Test status filtering
    pending_profiles = profile_manager.list_profiles(status="pending")
    print(f"✓ API: Found {len(pending_profiles)} pending profiles")
    
    # Test profile verification
    if profiles:
        test_profile = profiles[0]
        success = profile_manager.verify_profile(test_profile.name, test_profile.server)
        if success:
            print(f"✓ API: Successfully verified profile for {test_profile.name}")
        else:
            print(f"✗ API: Failed to verify profile for {test_profile.name}")

def demonstrate_supported_options():
    """Demonstrate supported options."""
    print("\nDemonstrating supported options...")
    
    servers = profile_manager.get_supported_servers()
    print(f"✓ Supported servers: {len(servers)}")
    print(f"  Sample servers: {servers[:3]}")
    
    races = profile_manager.get_supported_races()
    print(f"✓ Supported races: {len(races)}")
    print(f"  Sample races: {races[:3]}")
    
    professions = profile_manager.get_supported_professions()
    print(f"✓ Supported professions: {len(professions)}")
    print(f"  Sample professions: {professions[:3]}")

def main():
    """Main demonstration function."""
    print("MS11 Batch 090 - Public Player Profiles Demo")
    print("=" * 50)
    
    # Ensure data directories exist
    os.makedirs("data/public_profiles", exist_ok=True)
    os.makedirs("data/uploads", exist_ok=True)
    os.makedirs("data/internal", exist_ok=True)
    
    # Run demonstrations
    create_sample_profiles()
    demonstrate_profile_management()
    demonstrate_upload_functionality()
    demonstrate_api_endpoints()
    demonstrate_supported_options()
    
    print("\n" + "=" * 50)
    print("Demo completed!")
    print("\nNext steps:")
    print("1. Start the dashboard: python dashboard/app.py")
    print("2. Visit http://localhost:8000/profile/create")
    print("3. Create your own player profile")
    print("4. View profiles at http://localhost:8000/players")
    print("\nAPI Endpoints:")
    print("- GET /api/profiles - List all profiles")
    print("- GET /api/profile/<name>/<server> - Get specific profile")
    print("- POST /api/profile/<name>/<server>/verify - Verify profile")

if __name__ == "__main__":
    main() 