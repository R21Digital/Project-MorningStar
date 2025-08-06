#!/usr/bin/env python3
"""
Player Notes CLI Tool for Batch 160.

This command-line interface provides tools for managing player notes
and encounters observed during MS11 sessions.
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Optional, Dict, Any

from core.player_notes_collector import get_player_notes_collector, PlayerNotesCollector
from core.player_notes_integration import get_player_notes_integration

def add_player_command(args):
    """Add a player encounter."""
    collector = get_player_notes_collector()
    
    # Parse location if coordinates provided
    location = None
    if args.planet or args.city or args.coordinates:
        location = {}
        if args.planet:
            location["planet"] = args.planet
        if args.city:
            location["city"] = args.city
        if args.coordinates:
            try:
                coords = [float(x.strip()) for x in args.coordinates.split(",")]
                if len(coords) == 2:
                    location["coordinates"] = coords
                else:
                    print("❌ Coordinates must be in format 'x,y'")
                    return
            except ValueError:
                print("❌ Invalid coordinates format. Use 'x,y'")
                return
    
    success = collector.add_player_encounter(
        player_name=args.name,
        guild_tag=args.guild,
        race=args.race,
        faction=args.faction,
        title=args.title,
        location=location,
        notes=args.notes
    )
    
    if success:
        print(f"✅ Added player encounter: {args.name}")
    else:
        print(f"❌ Failed to add player encounter: {args.name}")

def list_players_command(args):
    """List all players."""
    collector = get_player_notes_collector()
    players = collector.get_all_players()
    
    if not players:
        print("📝 No players recorded yet.")
        return
    
    print(f"📋 Found {len(players)} players:")
    print("-" * 80)
    
    for player_name, player in players.items():
        guild_info = f" [{player.guild_tag}]" if player.guild_tag else ""
        faction_info = f" ({player.faction})" if player.faction else ""
        race_info = f" - {player.race}" if player.race else ""
        title_info = f" '{player.title}'" if player.title else ""
        
        print(f"👤 {player_name}{guild_info}{faction_info}{race_info}{title_info}")
        print(f"   📍 Encounters: {player.encounter_count}")
        print(f"   📅 First seen: {player.first_seen}")
        print(f"   📅 Last seen: {player.last_seen}")
        if player.notes:
            print(f"   📝 Notes: {player.notes}")
        print()

def search_players_command(args):
    """Search for players by various criteria."""
    collector = get_player_notes_collector()
    
    if args.guild:
        players = collector.get_players_by_guild(args.guild)
        print(f"🔍 Found {len(players)} players in guild '{args.guild}':")
    elif args.faction:
        players = collector.get_players_by_faction(args.faction)
        print(f"🔍 Found {len(players)} players in faction '{args.faction}':")
    elif args.race:
        players = collector.get_players_by_race(args.race)
        print(f"🔍 Found {len(players)} players of race '{args.race}':")
    else:
        print("❌ Please specify --guild, --faction, or --race")
        return
    
    if not players:
        print("📝 No players found matching criteria.")
        return
    
    for player in players:
        guild_info = f" [{player.guild_tag}]" if player.guild_tag else ""
        faction_info = f" ({player.faction})" if player.faction else ""
        race_info = f" - {player.race}" if player.race else ""
        title_info = f" '{player.title}'" if player.title else ""
        
        print(f"👤 {player.player_name}{guild_info}{faction_info}{race_info}{title_info}")
        print(f"   📍 Encounters: {player.encounter_count}")
        print(f"   📅 Last seen: {player.last_seen}")

def stats_command(args):
    """Show player statistics."""
    collector = get_player_notes_collector()
    stats = collector.get_statistics()
    
    print("📊 Player Notes Statistics:")
    print("=" * 40)
    print(f"👥 Total Players: {stats['total_players']}")
    print(f"🤝 Total Encounters: {stats['total_encounters']}")
    print(f"🕐 Recent Encounters (24h): {stats['recent_encounters']}")
    
    if stats['guilds']:
        print(f"\n🏛️  Guilds ({len(stats['guilds'])}):")
        for guild, count in sorted(stats['guilds'].items(), key=lambda x: x[1], reverse=True):
            print(f"   {guild}: {count} players")
    
    if stats['factions']:
        print(f"\n⚔️  Factions ({len(stats['factions'])}):")
        for faction, count in sorted(stats['factions'].items(), key=lambda x: x[1], reverse=True):
            print(f"   {faction}: {count} players")
    
    if stats['races']:
        print(f"\n👽 Races ({len(stats['races'])}):")
        for race, count in sorted(stats['races'].items(), key=lambda x: x[1], reverse=True):
            print(f"   {race}: {count} players")

def export_command(args):
    """Export player data."""
    collector = get_player_notes_collector()
    
    try:
        export_file = collector.export_data(format=args.format)
        print(f"✅ Exported {args.format.upper()} data to: {export_file}")
    except Exception as e:
        print(f"❌ Export failed: {e}")

def cleanup_command(args):
    """Clean up old player data."""
    collector = get_player_notes_collector()
    
    removed_count = collector.cleanup_old_data(days_old=args.days)
    print(f"🧹 Removed {removed_count} old player records (older than {args.days} days)")

def session_stats_command(args):
    """Show session-specific statistics."""
    integration = get_player_notes_integration()
    stats = integration.get_session_statistics()
    
    print("📊 Session Statistics:")
    print("=" * 30)
    print(f"🤝 Session Encounters: {stats['session_encounters']}")
    print(f"👥 Unique Players: {stats['unique_players']}")
    
    if stats['guilds_encountered']:
        print(f"🏛️  Guilds Encountered: {', '.join(stats['guilds_encountered'])}")
    
    if stats['factions_encountered']:
        print(f"⚔️  Factions Encountered: {', '.join(stats['factions_encountered'])}")
    
    if stats['races_encountered']:
        print(f"👽 Races Encountered: {', '.join(stats['races_encountered'])}")
    
    if stats['session_id']:
        print(f"🆔 Session ID: {stats['session_id']}")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Batch 160 - Player Notes CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add a player encounter
  python player_notes_cli.py add --name "ZabrakWarrior" --guild "Mandalorian" --race "zabrak" --faction "mandalorian"
  
  # List all players
  python player_notes_cli.py list
  
  # Search for players by guild
  python player_notes_cli.py search --guild "Mandalorian"
  
  # Show statistics
  python player_notes_cli.py stats
  
  # Export data
  python player_notes_cli.py export --format json --output players_export.json
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add player command
    add_parser = subparsers.add_parser('add', help='Add a player encounter')
    add_parser.add_argument('--name', required=True, help='Player name')
    add_parser.add_argument('--guild', help='Guild tag')
    add_parser.add_argument('--race', help='Player race')
    add_parser.add_argument('--faction', help='Faction')
    add_parser.add_argument('--title', help='Player title')
    add_parser.add_argument('--planet', help='Planet location')
    add_parser.add_argument('--city', help='City location')
    add_parser.add_argument('--coordinates', help='Coordinates (x,y format)')
    add_parser.add_argument('--notes', help='Additional notes')
    add_parser.set_defaults(func=add_player_command)
    
    # List players command
    list_parser = subparsers.add_parser('list', help='List all players')
    list_parser.set_defaults(func=list_players_command)
    
    # Search players command
    search_parser = subparsers.add_parser('search', help='Search for players')
    search_group = search_parser.add_mutually_exclusive_group(required=True)
    search_group.add_argument('--guild', help='Search by guild tag')
    search_group.add_argument('--faction', help='Search by faction')
    search_group.add_argument('--race', help='Search by race')
    search_parser.set_defaults(func=search_players_command)
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    stats_parser.set_defaults(func=stats_command)
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export player data')
    export_parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Export format')
    export_parser.set_defaults(func=export_command)
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old data')
    cleanup_parser.add_argument('--days', type=int, default=30, help='Remove data older than N days')
    cleanup_parser.set_defaults(func=cleanup_command)
    
    # Session stats command
    session_stats_parser = subparsers.add_parser('session-stats', help='Show session statistics')
    session_stats_parser.set_defaults(func=session_stats_command)
    
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