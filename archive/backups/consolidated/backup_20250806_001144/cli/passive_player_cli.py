#!/usr/bin/env python3
"""
Batch 149 - Passive Player Data Collection CLI

This module provides a command-line interface for managing passive player data collection,
viewing statistics, searching players, and exporting data for SWGDB integration.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add core directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.passive_player_integration import (
    get_passive_player_integration,
    start_passive_collection,
    stop_passive_collection,
    update_passive_collection_location,
    get_passive_collection_statistics,
    add_passive_player_encounter,
    search_passive_players,
    get_passive_player_profile,
    export_passive_data_for_swgdb
)
from core.passive_player_collector import PlayerProfile
from profession_logic.utils.logger import logger


def print_banner():
    """Print CLI banner."""
    print("=" * 80)
    print("MS11 - Batch 149: Passive Player Data Collection System")
    print("=" * 80)
    print("Commands: start, stop, status, add, search, profile, export, location")
    print("=" * 80)


def cmd_start_collection(args):
    """Start automatic passive player data collection."""
    print("🔄 Starting automatic passive player data collection...")
    
    try:
        start_passive_collection()
        print("✅ Automatic collection started successfully")
        print("   Collection will run in background and save data automatically")
        
    except Exception as e:
        print(f"❌ Error starting collection: {e}")
        return False
    
    return True


def cmd_stop_collection(args):
    """Stop automatic passive player data collection."""
    print("🛑 Stopping automatic passive player data collection...")
    
    try:
        stop_passive_collection()
        print("✅ Automatic collection stopped successfully")
        
    except Exception as e:
        print(f"❌ Error stopping collection: {e}")
        return False
    
    return True


def cmd_status(args):
    """Show collection status and statistics."""
    print("📊 Passive Player Data Collection Status")
    print("-" * 50)
    
    try:
        stats = get_passive_collection_statistics()
        
        print(f"Collection Enabled: {'✅ Yes' if stats.get('collection_enabled') else '❌ No'}")
        print(f"Total Players: {stats.get('total_players', 0)}")
        print(f"Total Encounters: {stats.get('total_encounters', 0)}")
        print(f"Possible NPCs: {stats.get('possible_npcs', 0)}")
        
        current_location = stats.get('current_location', {})
        print(f"Current Location: {current_location.get('zone', 'Unknown')}, {current_location.get('planet', 'Unknown')}")
        
        # Show top guilds
        guilds = stats.get('guilds', {})
        if guilds:
            print("\nTop Guilds:")
            sorted_guilds = sorted(guilds.items(), key=lambda x: x[1], reverse=True)[:5]
            for guild, count in sorted_guilds:
                print(f"   {guild}: {count} players")
        
        # Show top factions
        factions = stats.get('factions', {})
        if factions:
            print("\nTop Factions:")
            sorted_factions = sorted(factions.items(), key=lambda x: x[1], reverse=True)[:5]
            for faction, count in sorted_factions:
                print(f"   {faction}: {count} players")
        
        # Show recent activity
        recent = stats.get('recent_activity', [])
        if recent:
            print(f"\nRecent Activity (Last 24h): {len(recent)} encounters")
            for encounter in recent[:3]:  # Show last 3
                print(f"   {encounter['name']} in {encounter.get('zone', 'Unknown')}, {encounter.get('planet', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Error getting status: {e}")
        return False
    
    return True


def cmd_add_encounter(args):
    """Add a manual player encounter."""
    print("➕ Adding Player Encounter")
    print("-" * 30)
    
    try:
        # Get player details
        name = input("Player Name: ").strip()
        if not name:
            print("❌ Player name is required")
            return False
        
        guild = input("Guild (optional): ").strip() or None
        faction = input("Faction (optional): ").strip() or None
        title = input("Title (optional): ").strip() or None
        zone = input("Zone (optional): ").strip() or None
        planet = input("Planet (optional): ").strip() or None
        
        # Add encounter
        success = add_passive_player_encounter(
            name=name,
            guild=guild,
            faction=faction,
            title=title,
            zone=zone,
            planet=planet
        )
        
        if success:
            print(f"✅ Added encounter for {name}")
        else:
            print(f"❌ Failed to add encounter for {name}")
            return False
        
    except Exception as e:
        print(f"❌ Error adding encounter: {e}")
        return False
    
    return True


def cmd_search_players(args):
    """Search for players in collected data."""
    print("🔍 Player Search")
    print("-" * 20)
    
    try:
        query = input("Search Query: ").strip()
        if not query:
            print("❌ Search query is required")
            return False
        
        search_type = input("Search Type (name/guild/faction/title) [name]: ").strip() or "name"
        
        results = search_passive_players(query, search_type)
        
        if results:
            print(f"\nFound {len(results)} players:")
            print("-" * 60)
            
            for i, player in enumerate(results[:10], 1):  # Show first 10
                print(f"{i}. {player.name}")
                if player.guild:
                    print(f"   Guild: {player.guild}")
                if player.faction:
                    print(f"   Faction: {player.faction}")
                if player.title:
                    print(f"   Title: {player.title}")
                print(f"   Encounters: {player.total_encounters}")
                print(f"   Zones: {len(player.zones_seen)}")
                print(f"   Planets: {len(player.planets_seen)}")
                if player.possible_npc:
                    print("   ⚠️  Possible NPC")
                print()
        else:
            print("No players found matching the query")
        
    except Exception as e:
        print(f"❌ Error searching players: {e}")
        return False
    
    return True


def cmd_player_profile(args):
    """Show detailed profile for a specific player."""
    print("👤 Player Profile")
    print("-" * 20)
    
    try:
        name = input("Player Name: ").strip()
        if not name:
            print("❌ Player name is required")
            return False
        
        player = get_passive_player_profile(name)
        
        if player:
            print(f"\nProfile for: {player.name}")
            print("=" * 40)
            print(f"Guild: {player.guild or 'Unknown'}")
            print(f"Faction: {player.faction or 'Unknown'}")
            print(f"Title: {player.title or 'Unknown'}")
            print(f"First Seen: {player.first_seen}")
            print(f"Last Seen: {player.last_seen}")
            print(f"Total Encounters: {player.total_encounters}")
            print(f"Zones Seen: {', '.join(player.zones_seen) if player.zones_seen else 'None'}")
            print(f"Planets Seen: {', '.join(player.planets_seen) if player.planets_seen else 'None'}")
            print(f"Possible NPC: {'Yes' if player.possible_npc else 'No'}")
            
            if player.encounter_history:
                print(f"\nRecent Encounters:")
                for encounter in player.encounter_history[-5:]:  # Last 5
                    print(f"   {encounter.timestamp}: {encounter.zone}, {encounter.planet}")
        else:
            print(f"Player '{name}' not found in collected data")
        
    except Exception as e:
        print(f"❌ Error getting player profile: {e}")
        return False
    
    return True


def cmd_export_data(args):
    """Export data for SWGDB integration."""
    print("📤 Exporting Data for SWGDB")
    print("-" * 35)
    
    try:
        output_file = input("Output file (optional): ").strip()
        if not output_file:
            output_file = "passive_player_data_export.json"
        
        # Export data
        data = export_passive_data_for_swgdb()
        
        if "error" in data:
            print(f"❌ Export error: {data['error']}")
            return False
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Data exported to {output_file}")
        print(f"   Players: {len(data.get('players', []))}")
        print(f"   Encounters: {len(data.get('encounters', []))}")
        print(f"   Export timestamp: {data.get('export_timestamp', 'Unknown')}")
        
    except Exception as e:
        print(f"❌ Error exporting data: {e}")
        return False
    
    return True


def cmd_update_location(args):
    """Update current location for data collection."""
    print("📍 Update Collection Location")
    print("-" * 35)
    
    try:
        zone = input("Current Zone: ").strip()
        planet = input("Current Planet: ").strip()
        
        if not zone or not planet:
            print("❌ Both zone and planet are required")
            return False
        
        update_passive_collection_location(zone, planet)
        print(f"✅ Location updated: {zone}, {planet}")
        
    except Exception as e:
        print(f"❌ Error updating location: {e}")
        return False
    
    return True


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="MS11 Batch 149 - Passive Player Data Collection CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  start       Start automatic passive player data collection
  stop        Stop automatic passive player data collection
  status      Show collection status and statistics
  add         Add a manual player encounter
  search      Search for players in collected data
  profile     Show detailed profile for a specific player
  export      Export data for SWGDB integration
  location    Update current location for data collection
        """
    )
    
    parser.add_argument('command', nargs='?', help='Command to execute')
    parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Interactive mode
    if args.interactive or not args.command:
        while True:
            try:
                print("\nAvailable commands: start, stop, status, add, search, profile, export, location, quit")
                command = input("\nEnter command: ").strip().lower()
                
                if command == 'quit' or command == 'exit':
                    break
                elif command == 'start':
                    cmd_start_collection(args)
                elif command == 'stop':
                    cmd_stop_collection(args)
                elif command == 'status':
                    cmd_status(args)
                elif command == 'add':
                    cmd_add_encounter(args)
                elif command == 'search':
                    cmd_search_players(args)
                elif command == 'profile':
                    cmd_player_profile(args)
                elif command == 'export':
                    cmd_export_data(args)
                elif command == 'location':
                    cmd_update_location(args)
                else:
                    print("❌ Unknown command. Type 'quit' to exit.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    # Command mode
    else:
        command = args.command.lower()
        
        if command == 'start':
            success = cmd_start_collection(args)
        elif command == 'stop':
            success = cmd_stop_collection(args)
        elif command == 'status':
            success = cmd_status(args)
        elif command == 'add':
            success = cmd_add_encounter(args)
        elif command == 'search':
            success = cmd_search_players(args)
        elif command == 'profile':
            success = cmd_player_profile(args)
        elif command == 'export':
            success = cmd_export_data(args)
        elif command == 'location':
            success = cmd_update_location(args)
        else:
            print(f"❌ Unknown command: {command}")
            parser.print_help()
            sys.exit(1)
        
        if not success:
            sys.exit(1)


if __name__ == "__main__":
    main() 