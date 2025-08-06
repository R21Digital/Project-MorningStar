#!/usr/bin/env python3
"""
Batch 153 - Mount Profile CLI Tool

This command-line interface provides tools for managing mount profiles
and character mount inventories.
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Optional, Dict, Any

from core.mount_profile_builder import get_mount_profile_builder, CharacterMountProfile
from core.mount_profile_integration import get_mount_profile_integration

def scan_character_command(args):
    """Scan mounts for a character."""
    builder = get_mount_profile_builder()
    
    print(f"🔍 Scanning mounts for character: {args.character}")
    
    # Use provided mount lists if specified
    learned_mounts = None
    available_mounts = None
    
    if args.learned_mounts:
        learned_mounts = [mount.strip() for mount in args.learned_mounts.split(",")]
        print(f"📝 Learned mounts: {', '.join(learned_mounts)}")
    
    if args.available_mounts:
        available_mounts = [mount.strip() for mount in args.available_mounts.split(",")]
        print(f"✅ Available mounts: {', '.join(available_mounts)}")
    
    # Scan character mounts
    profile = builder.scan_character_mounts(args.character, learned_mounts, available_mounts)
    
    print(f"✅ Mount scan completed!")
    print(f"📊 Results:")
    print(f"   Total mounts: {profile.total_mounts}")
    print(f"   Learned mounts: {profile.learned_mounts}")
    print(f"   Available mounts: {profile.available_mounts}")
    print(f"   Profile saved to: data/mounts/{args.character}.json")

def list_profiles_command(args):
    """List all character mount profiles."""
    builder = get_mount_profile_builder()
    profiles = builder.get_all_profiles()
    
    if not profiles:
        print("📝 No mount profiles found.")
        return
    
    print(f"📋 Found {len(profiles)} character mount profiles:")
    print("-" * 60)
    
    for character_name, profile in profiles.items():
        print(f"👤 {character_name}")
        print(f"   📅 Last scan: {profile.scan_timestamp}")
        print(f"   🐎 Total mounts: {profile.total_mounts}")
        print(f"   📚 Learned: {profile.learned_mounts}")
        print(f"   ✅ Available: {profile.available_mounts}")
        
        # Show fastest mount
        fastest = profile.mount_statistics.get("fastest_mount")
        if fastest:
            print(f"   ⚡ Fastest: {fastest}")
        
        print()

def view_profile_command(args):
    """View detailed mount profile for a character."""
    builder = get_mount_profile_builder()
    profile = builder.load_character_profile(args.character)
    
    if not profile:
        print(f"❌ No profile found for character: {args.character}")
        return
    
    print(f"📋 Mount Profile for {args.character}")
    print("=" * 60)
    print(f"📅 Last scan: {profile.scan_timestamp}")
    print(f"🐎 Total mounts: {profile.total_mounts}")
    print(f"📚 Learned mounts: {profile.learned_mounts}")
    print(f"✅ Available mounts: {profile.available_mounts}")
    print()
    
    # Show mount inventory
    print("🐎 Mount Inventory:")
    print("-" * 40)
    for mount_name, mount in profile.mount_inventory.items():
        print(f"   {mount_name}")
        print(f"     Type: {mount.mount_type}")
        print(f"     Speed: {mount.speed}")
        print(f"     Learned: {mount.learned}")
        if mount.creature_type:
            print(f"     Creature: {mount.creature_type}")
        if mount.hotbar_slot:
            print(f"     Hotbar: {mount.hotbar_slot}")
        if mount.command:
            print(f"     Command: {mount.command}")
        if mount.description:
            print(f"     Description: {mount.description}")
        print()
    
    # Show statistics
    print("📊 Statistics:")
    print("-" * 20)
    stats = profile.mount_statistics
    print(f"   Average speed: {stats.get('average_speed', 0)}")
    print(f"   Fastest mount: {stats.get('fastest_mount', 'None')}")
    print(f"   Slowest mount: {stats.get('slowest_mount', 'None')}")
    
    print("\n   Speed ranges:")
    speed_ranges = stats.get("speed_ranges", {})
    for range_name, count in speed_ranges.items():
        print(f"     {range_name.capitalize()}: {count}")
    
    print("\n   Mount types:")
    mount_types = stats.get("mount_types", {})
    for mount_type, count in mount_types.items():
        print(f"     {mount_type.capitalize()}: {count}")
    
    # Show preferences
    print("\n🎯 Preferences:")
    print("-" * 20)
    prefs = profile.preferences
    print(f"   Preferred type: {prefs.get('preferred_mount_type', 'None')}")
    print(f"   Preferred speed: {prefs.get('preferred_speed_range', 'None')}")
    print(f"   Auto-select: {prefs.get('auto_select', False)}")
    print(f"   Fallback mount: {prefs.get('fallback_mount', 'None')}")
    
    favorites = prefs.get("favorite_mounts", [])
    if favorites:
        print(f"   Favorite mounts: {', '.join(favorites)}")

def stats_command(args):
    """Show mount statistics."""
    integration = get_mount_profile_integration()
    
    if args.character:
        # Character-specific stats
        stats = integration.get_mount_statistics(args.character)
        if not stats:
            print(f"❌ No statistics found for character: {args.character}")
            return
        
        print(f"📊 Mount Statistics for {args.character}:")
        print("=" * 50)
        print(f"Total mounts: {stats.get('total_mounts', 0)}")
        print(f"Available mounts: {stats.get('available_mounts', 0)}")
        print(f"Learned mounts: {stats.get('learned_mounts', 0)}")
        print(f"Average speed: {stats.get('average_speed', 0)}")
        print(f"Fastest mount: {stats.get('fastest_mount', 'None')}")
        print(f"Slowest mount: {stats.get('slowest_mount', 'None')}")
        
        # Speed ranges
        print("\nSpeed ranges:")
        speed_ranges = stats.get("speed_ranges", {})
        for range_name, count in speed_ranges.items():
            print(f"  {range_name.capitalize()}: {count}")
        
        # Mount types
        print("\nMount types:")
        mount_types = stats.get("mount_types", {})
        for mount_type, count in mount_types.items():
            print(f"  {mount_type.capitalize()}: {count}")
    
    else:
        # Session statistics
        session_stats = integration.get_session_statistics()
        print("📊 Session Mount Scan Statistics:")
        print("=" * 40)
        print(f"Total scans: {session_stats.get('total_scans', 0)}")
        print(f"Characters scanned: {len(session_stats.get('characters_scanned', []))}")
        print(f"Total mounts found: {session_stats.get('total_mounts_found', 0)}")
        print(f"Profiles created: {session_stats.get('profiles_created', 0)}")
        
        characters = session_stats.get('characters_scanned', [])
        if characters:
            print(f"\nCharacters scanned: {', '.join(characters)}")

def export_command(args):
    """Export mount data."""
    builder = get_mount_profile_builder()
    
    try:
        export_file = builder.export_mount_data(args.character, format=args.format)
        print(f"✅ Mount data exported to: {export_file}")
    except Exception as e:
        print(f"❌ Export failed: {e}")

def search_command(args):
    """Search for mounts by criteria."""
    integration = get_mount_profile_integration()
    
    if args.character:
        if args.type:
            # Search by mount type
            mounts = integration.get_mounts_by_type(args.character, args.type)
            print(f"🔍 {args.type.capitalize()} mounts for {args.character}:")
            for mount in mounts:
                print(f"   {mount.name} (Speed: {mount.speed})")
        else:
            # Show all available mounts
            mounts = integration.get_available_mounts(args.character)
            print(f"🔍 Available mounts for {args.character}:")
            for mount in mounts:
                print(f"   {mount.name} ({mount.mount_type}, Speed: {mount.speed})")
    else:
        print("❌ Please specify a character name")

def sync_command(args):
    """Sync mount data to dashboard."""
    integration = get_mount_profile_integration()
    
    dashboard_data = integration.sync_to_dashboard(args.character)
    
    if "error" in dashboard_data:
        print(f"❌ {dashboard_data['error']}")
        return
    
    print(f"🔄 Dashboard sync data for {args.character}:")
    print(f"   Total mounts: {dashboard_data.get('total_mounts', 0)}")
    print(f"   Available mounts: {dashboard_data.get('available_mounts', 0)}")
    print(f"   Last scan: {dashboard_data.get('last_scan', 'Unknown')}")
    
    mounts = dashboard_data.get('mounts', [])
    if mounts:
        print(f"\n   Mounts:")
        for mount in mounts[:5]:  # Show first 5
            print(f"     {mount['name']} ({mount['type']}, Speed: {mount['speed']})")
        if len(mounts) > 5:
            print(f"     ... and {len(mounts) - 5} more")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Batch 153 - Mount Profile CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan mounts for a character
  python mount_profile_cli.py scan --character "JediMaster"
  
  # Scan with specific mount lists
  python mount_profile_cli.py scan --character "BountyHunter" --learned-mounts "Speederbike,Swoop,AV-21"
  
  # View detailed profile
  python mount_profile_cli.py view --character "JediMaster"
  
  # Show statistics
  python mount_profile_cli.py stats --character "JediMaster"
  
  # Export data
  python mount_profile_cli.py export --character "JediMaster" --format json
  
  # Search by mount type
  python mount_profile_cli.py search --character "JediMaster" --type speeder
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scan command
    scan_parser = subparsers.add_parser('scan', help='Scan mounts for a character')
    scan_parser.add_argument('--character', required=True, help='Character name')
    scan_parser.add_argument('--learned-mounts', help='Comma-separated list of learned mounts')
    scan_parser.add_argument('--available-mounts', help='Comma-separated list of available mounts')
    scan_parser.set_defaults(func=scan_character_command)
    
    # List profiles command
    list_parser = subparsers.add_parser('list', help='List all character profiles')
    list_parser.set_defaults(func=list_profiles_command)
    
    # View profile command
    view_parser = subparsers.add_parser('view', help='View detailed mount profile')
    view_parser.add_argument('--character', required=True, help='Character name')
    view_parser.set_defaults(func=view_profile_command)
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show mount statistics')
    stats_parser.add_argument('--character', help='Character name (optional for session stats)')
    stats_parser.set_defaults(func=stats_command)
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export mount data')
    export_parser.add_argument('--character', required=True, help='Character name')
    export_parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Export format')
    export_parser.set_defaults(func=export_command)
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for mounts')
    search_parser.add_argument('--character', required=True, help='Character name')
    search_parser.add_argument('--type', help='Mount type to search for')
    search_parser.set_defaults(func=search_command)
    
    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Sync to dashboard')
    sync_parser.add_argument('--character', required=True, help='Character name')
    sync_parser.set_defaults(func=sync_command)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 