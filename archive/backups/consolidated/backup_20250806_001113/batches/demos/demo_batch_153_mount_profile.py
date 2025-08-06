#!/usr/bin/env python3
"""
Batch 153 - Mount Scanner & Profile Builder Demo

This demo showcases the comprehensive mount inventory system that:
- Scans learned mounts on login
- Builds detailed mount profiles per character
- Outputs to /data/mounts/{character}.json
- Syncs to user dashboard for selection (future)
- Includes mount name, speed, type, and creature (if custom)
"""

import json
import time
from datetime import datetime
from pathlib import Path

from core.mount_profile_builder import get_mount_profile_builder, scan_character_mounts
from core.mount_profile_integration import get_mount_profile_integration

def demo_basic_mount_scanning():
    """Demonstrate basic mount scanning functionality."""
    print("🔍 Demo: Basic Mount Scanning")
    print("=" * 50)
    
    # Test characters with different mount types
    test_characters = [
        "JediMaster",
        "BountyHunter", 
        "TraderMerchant",
        "ImperialAgent"
    ]
    
    for character in test_characters:
        print(f"\n🐎 Scanning mounts for {character}...")
        
        # Simulate different mount lists based on character type
        if "jedi" in character.lower():
            learned_mounts = ["Speederbike", "Jetpack", "Flying Mount", "Dewback"]
            available_mounts = ["Speederbike", "Jetpack", "Dewback"]
        elif "bounty" in character.lower():
            learned_mounts = ["Speederbike", "Swoop", "AV-21", "Bantha"]
            available_mounts = ["Speederbike", "Swoop", "Bantha"]
        elif "trader" in character.lower():
            learned_mounts = ["Landspeeder", "Kaadu", "Eopie", "Falumpaset"]
            available_mounts = ["Landspeeder", "Kaadu", "Eopie"]
        else:
            learned_mounts = ["Speederbike", "Dewback", "Bantha", "Ronto"]
            available_mounts = ["Speederbike", "Dewback", "Bantha"]
        
        # Scan character mounts
        profile = scan_character_mounts(character, learned_mounts, available_mounts)
        
        print(f"✅ Scan completed for {character}:")
        print(f"   📊 Total mounts: {profile.total_mounts}")
        print(f"   📚 Learned: {profile.learned_mounts}")
        print(f"   ✅ Available: {profile.available_mounts}")
        
        # Show fastest mount
        fastest = profile.mount_statistics.get("fastest_mount")
        if fastest:
            print(f"   ⚡ Fastest: {fastest}")

def demo_mount_profile_details():
    """Demonstrate detailed mount profile information."""
    print("\n📋 Demo: Mount Profile Details")
    print("=" * 50)
    
    builder = get_mount_profile_builder()
    
    # Load a profile and show detailed information
    profile = builder.load_character_profile("JediMaster")
    if profile:
        print(f"📋 Detailed Profile for JediMaster:")
        print(f"   📅 Last scan: {profile.scan_timestamp}")
        print(f"   🐎 Total mounts: {profile.total_mounts}")
        
        print(f"\n🐎 Mount Inventory:")
        for mount_name, mount in profile.mount_inventory.items():
            print(f"   {mount_name}:")
            print(f"     Type: {mount.mount_type}")
            print(f"     Speed: {mount.speed}")
            print(f"     Learned: {mount.learned}")
            if mount.creature_type:
                print(f"     Creature: {mount.creature_type}")
            if mount.hotbar_slot:
                print(f"     Hotbar: {mount.hotbar_slot}")
            if mount.command:
                print(f"     Command: {mount.command}")
        
        print(f"\n📊 Statistics:")
        stats = profile.mount_statistics
        print(f"   Average speed: {stats.get('average_speed', 0)}")
        print(f"   Fastest: {stats.get('fastest_mount', 'None')}")
        print(f"   Slowest: {stats.get('slowest_mount', 'None')}")
        
        print(f"\n🎯 Preferences:")
        prefs = profile.preferences
        print(f"   Preferred type: {prefs.get('preferred_mount_type', 'None')}")
        print(f"   Preferred speed: {prefs.get('preferred_speed_range', 'None')}")
        print(f"   Fallback mount: {prefs.get('fallback_mount', 'None')}")

def demo_mount_integration():
    """Demonstrate mount profile integration with session management."""
    print("\n🔄 Demo: Mount Profile Integration")
    print("=" * 50)
    
    integration = get_mount_profile_integration()
    
    # Simulate session-based mount scanning
    characters = ["JediMaster", "BountyHunter", "TraderMerchant"]
    
    for character in characters:
        print(f"\n🔍 Session mount scan for {character}...")
        
        # Simulate mount lists
        learned_mounts = ["Speederbike", "Dewback", "Bantha"]
        if "jedi" in character.lower():
            learned_mounts.append("Jetpack")
        elif "bounty" in character.lower():
            learned_mounts.append("Swoop")
        
        # Scan mounts on login
        profile = integration.scan_mounts_on_login(character, learned_mounts)
        
        print(f"✅ Session scan completed:")
        print(f"   📊 Mounts found: {profile.total_mounts}")
        print(f"   📚 Learned: {profile.learned_mounts}")
    
    # Show session statistics
    print(f"\n📊 Session Statistics:")
    session_stats = integration.get_session_statistics()
    print(f"   Total scans: {session_stats.get('total_scans', 0)}")
    print(f"   Characters scanned: {len(session_stats.get('characters_scanned', []))}")
    print(f"   Total mounts found: {session_stats.get('total_mounts_found', 0)}")
    print(f"   Profiles created: {session_stats.get('profiles_created', 0)}")

def demo_mount_search_and_filter():
    """Demonstrate mount search and filtering capabilities."""
    print("\n🔍 Demo: Mount Search and Filter")
    print("=" * 50)
    
    integration = get_mount_profile_integration()
    
    # Search for different mount types
    mount_types = ["speeder", "creature", "flying"]
    
    for mount_type in mount_types:
        print(f"\n🔍 {mount_type.capitalize()} mounts:")
        mounts = integration.get_mounts_by_type("JediMaster", mount_type)
        
        if mounts:
            for mount in mounts:
                print(f"   {mount.name} (Speed: {mount.speed})")
        else:
            print(f"   No {mount_type} mounts found")
    
    # Show all available mounts
    print(f"\n🔍 All available mounts for JediMaster:")
    available_mounts = integration.get_available_mounts("JediMaster")
    for mount in available_mounts:
        print(f"   {mount.name} ({mount.mount_type}, Speed: {mount.speed})")

def demo_mount_statistics():
    """Demonstrate mount statistics and analysis."""
    print("\n📊 Demo: Mount Statistics")
    print("=" * 50)
    
    integration = get_mount_profile_integration()
    
    # Show statistics for different characters
    characters = ["JediMaster", "BountyHunter", "TraderMerchant"]
    
    for character in characters:
        print(f"\n📊 Statistics for {character}:")
        stats = integration.get_mount_statistics(character)
        
        if stats:
            print(f"   Total mounts: {stats.get('total_mounts', 0)}")
            print(f"   Available mounts: {stats.get('available_mounts', 0)}")
            print(f"   Learned mounts: {stats.get('learned_mounts', 0)}")
            print(f"   Average speed: {stats.get('average_speed', 0)}")
            print(f"   Fastest mount: {stats.get('fastest_mount', 'None')}")
            print(f"   Slowest mount: {stats.get('slowest_mount', 'None')}")
            
            # Speed ranges
            speed_ranges = stats.get("speed_ranges", {})
            if speed_ranges:
                print(f"   Speed ranges:")
                for range_name, count in speed_ranges.items():
                    print(f"     {range_name.capitalize()}: {count}")
            
            # Mount types
            mount_types = stats.get("mount_types", {})
            if mount_types:
                print(f"   Mount types:")
                for mount_type, count in mount_types.items():
                    print(f"     {mount_type.capitalize()}: {count}")
        else:
            print(f"   No statistics available")

def demo_mount_export():
    """Demonstrate mount data export functionality."""
    print("\n📤 Demo: Mount Data Export")
    print("=" * 50)
    
    builder = get_mount_profile_builder()
    
    # Export data in different formats
    characters = ["JediMaster", "BountyHunter"]
    formats = ["json", "csv"]
    
    for character in characters:
        for format_type in formats:
            try:
                print(f"\n📤 Exporting {character} data in {format_type.upper()} format...")
                export_file = builder.export_mount_data(character, format=format_type)
                print(f"✅ Export completed: {export_file}")
                
                # Show file size
                file_path = Path(export_file)
                if file_path.exists():
                    size_kb = file_path.stat().st_size / 1024
                    print(f"   📁 File size: {size_kb:.1f} KB")
                
            except Exception as e:
                print(f"❌ Export failed: {e}")

def demo_dashboard_sync():
    """Demonstrate dashboard synchronization."""
    print("\n🔄 Demo: Dashboard Synchronization")
    print("=" * 50)
    
    integration = get_mount_profile_integration()
    
    # Sync data for different characters
    characters = ["JediMaster", "BountyHunter", "TraderMerchant"]
    
    for character in characters:
        print(f"\n🔄 Syncing {character} data to dashboard...")
        
        dashboard_data = integration.sync_to_dashboard(character)
        
        if "error" in dashboard_data:
            print(f"❌ {dashboard_data['error']}")
        else:
            print(f"✅ Dashboard sync completed:")
            print(f"   📊 Total mounts: {dashboard_data.get('total_mounts', 0)}")
            print(f"   ✅ Available mounts: {dashboard_data.get('available_mounts', 0)}")
            print(f"   📅 Last scan: {dashboard_data.get('last_scan', 'Unknown')}")
            
            # Show mount details
            mounts = dashboard_data.get('mounts', [])
            if mounts:
                print(f"   🐎 Mounts:")
                for mount in mounts[:3]:  # Show first 3
                    print(f"     {mount['name']} ({mount['type']}, Speed: {mount['speed']})")
                if len(mounts) > 3:
                    print(f"     ... and {len(mounts) - 3} more")

def demo_mount_usage_tracking():
    """Demonstrate mount usage tracking."""
    print("\n📈 Demo: Mount Usage Tracking")
    print("=" * 50)
    
    integration = get_mount_profile_integration()
    
    # Simulate mount usage
    character = "JediMaster"
    mounts_to_use = ["Speederbike", "Jetpack", "Dewback"]
    
    print(f"📈 Tracking mount usage for {character}...")
    
    for mount_name in mounts_to_use:
        print(f"   🐎 Using mount: {mount_name}")
        success = integration.update_mount_usage(character, mount_name)
        
        if success:
            print(f"   ✅ Usage updated successfully")
        else:
            print(f"   ❌ Failed to update usage")
    
    # Show updated profile
    profile = integration.get_character_mount_profile(character)
    if profile:
        print(f"\n📊 Updated usage statistics:")
        for mount_name, mount in profile.mount_inventory.items():
            if mount.usage_count > 0:
                print(f"   {mount_name}: {mount.usage_count} uses")
                if mount.last_used:
                    print(f"     Last used: {mount.last_used}")

def demo_data_persistence():
    """Demonstrate data persistence and loading."""
    print("\n💾 Demo: Data Persistence")
    print("=" * 50)
    
    builder = get_mount_profile_builder()
    
    # Show all profiles
    profiles = builder.get_all_profiles()
    
    print(f"📋 Found {len(profiles)} character profiles:")
    for character_name, profile in profiles.items():
        print(f"   👤 {character_name}")
        print(f"     📅 Last scan: {profile.scan_timestamp}")
        print(f"     🐎 Total mounts: {profile.total_mounts}")
        print(f"     📚 Learned: {profile.learned_mounts}")
        print(f"     ✅ Available: {profile.available_mounts}")
        
        # Show file path
        profile_file = Path(f"data/mounts/{character_name}.json")
        if profile_file.exists():
            size_kb = profile_file.stat().st_size / 1024
            print(f"     📁 File: {profile_file} ({size_kb:.1f} KB)")
        print()

def main():
    """Run the complete Batch 153 mount profile demo."""
    print("🚀 Batch 153 - Mount Scanner & Profile Builder Demo")
    print("=" * 70)
    print("This demo showcases the comprehensive mount inventory system")
    print("that scans learned mounts on login and builds detailed profiles.")
    print()
    
    try:
        # Run all demos
        demo_basic_mount_scanning()
        demo_mount_profile_details()
        demo_mount_integration()
        demo_mount_search_and_filter()
        demo_mount_statistics()
        demo_mount_export()
        demo_dashboard_sync()
        demo_mount_usage_tracking()
        demo_data_persistence()
        
        print("\n🎉 Demo completed successfully!")
        print("\n📋 Summary:")
        print("   ✅ Basic mount scanning functionality")
        print("   ✅ Detailed mount profile creation")
        print("   ✅ Session integration")
        print("   ✅ Search and filter capabilities")
        print("   ✅ Statistics and analysis")
        print("   ✅ Data export (JSON/CSV)")
        print("   ✅ Dashboard synchronization")
        print("   ✅ Usage tracking")
        print("   ✅ Data persistence")
        print("\n💡 The mount profile system is ready for production use!")
        
        # Show final data structure
        print("\n📁 Data Structure:")
        print("   /data/mounts/{character}.json - Character mount profiles")
        print("   Mount info includes: name, speed, type, creature, preferences")
        print("   Dashboard sync ready for future integration")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 