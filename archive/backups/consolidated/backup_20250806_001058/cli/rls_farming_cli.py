"""
Rare Loot System (RLS) Farming CLI Tool

This CLI provides comprehensive management for the RLS farming system:
- Session management (start, stop, list, stats)
- Zone configuration and management
- Target item management
- Loot tracking and verification
- Farming recommendations
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from core.rare_loot_farming import get_rare_loot_farmer
from android_ms11.modes.rare_loot_farm import (
    list_available_zones,
    list_target_items,
    get_farming_recommendations,
    get_session_statistics
)


def start_session_command(args):
    """Start a new RLS farming session."""
    farmer = get_rare_loot_farmer()
    
    try:
        session = farmer.start_farming_session(args.zone, args.targets)
        
        print(f"✅ Started RLS farming session: {session.session_id}")
        print(f"📍 Target Zone: {session.target_zone}")
        print(f"🎯 Target Items: {', '.join(session.target_items)}")
        print(f"⏰ Start Time: {session.start_time}")
        
        # Show optimal route
        optimal_route = farmer.get_optimal_farming_route(session.target_items)
        print(f"\n🗺️  Optimal Route ({len(optimal_route)} zones):")
        for zone in optimal_route:
            print(f"   • {zone.name} at {zone.coordinates}")
        
    except Exception as e:
        print(f"❌ Failed to start session: {e}")
        sys.exit(1)


def stop_session_command(args):
    """Stop the current RLS farming session."""
    farmer = get_rare_loot_farmer()
    
    if not farmer.current_session:
        print("❌ No active farming session to stop")
        return
    
    try:
        session = farmer.end_farming_session()
        if session:
            stats = farmer.get_session_statistics(session.session_id)
            
            print(f"✅ Stopped RLS farming session: {session.session_id}")
            print(f"⏱️  Duration: {stats.get('duration_minutes', 0)} minutes")
            print(f"⚔️  Enemies Killed: {stats.get('enemies_killed', 0)}")
            print(f"📦 Items Found: {stats.get('items_found', 0)}")
            print(f"💰 Total Value: {stats.get('total_value', 0):,} credits")
            
            # Show rarity breakdown
            rarity_breakdown = stats.get('rarity_breakdown', {})
            if rarity_breakdown:
                print(f"\n📊 Rarity Breakdown:")
                for rarity, count in rarity_breakdown.items():
                    print(f"   • {rarity.title()}: {count}")
        
    except Exception as e:
        print(f"❌ Failed to stop session: {e}")
        sys.exit(1)


def list_sessions_command(args):
    """List all RLS farming sessions."""
    farmer = get_rare_loot_farmer()
    
    if not farmer.farming_sessions:
        print("📋 No farming sessions found")
        return
    
    print(f"📋 RLS Farming Sessions ({len(farmer.farming_sessions)}):")
    print("-" * 80)
    
    for session_id, session in farmer.farming_sessions.items():
        stats = farmer.get_session_statistics(session_id)
        
        print(f"🆔 Session ID: {session_id}")
        print(f"📍 Zone: {session.target_zone}")
        print(f"🎯 Targets: {', '.join(session.target_items)}")
        print(f"📦 Items Found: {stats.get('items_found', 0)}")
        print(f"💰 Value: {stats.get('total_value', 0):,} credits")
        print(f"⏱️  Duration: {stats.get('duration_minutes', 0)} minutes")
        print(f"📊 Status: {session.status}")
        print("-" * 80)


def session_stats_command(args):
    """Show detailed statistics for a specific session."""
    farmer = get_rare_loot_farmer()
    
    if args.session_id not in farmer.farming_sessions:
        print(f"❌ Session {args.session_id} not found")
        return
    
    stats = farmer.get_session_statistics(args.session_id)
    session = farmer.farming_sessions[args.session_id]
    
    print(f"📊 Session Statistics: {args.session_id}")
    print("=" * 50)
    print(f"📍 Target Zone: {stats.get('target_zone', 'Unknown')}")
    print(f"🎯 Target Items: {', '.join(stats.get('target_items', []))}")
    print(f"⏱️  Duration: {stats.get('duration_minutes', 0)} minutes")
    print(f"⚔️  Enemies Killed: {stats.get('enemies_killed', 0)}")
    print(f"📦 Items Found: {stats.get('items_found', 0)}")
    print(f"💰 Total Value: {stats.get('total_value', 0):,} credits")
    
    # Rarity breakdown
    rarity_breakdown = stats.get('rarity_breakdown', {})
    if rarity_breakdown:
        print(f"\n📊 Rarity Breakdown:")
        for rarity, count in rarity_breakdown.items():
            print(f"   • {rarity.title()}: {count}")
    
    # Show loot found
    if session.loot_found:
        print(f"\n📦 Loot Found:")
        for item in session.loot_found:
            print(f"   • {item.get('item_name', 'Unknown')} ({item.get('rarity', 'common')})")


def list_zones_command(args):
    """List all available drop zones."""
    zones = list_available_zones()
    
    if not zones:
        print("🗺️  No drop zones configured")
        return
    
    print(f"🗺️  Available Drop Zones ({len(zones)}):")
    print("-" * 80)
    
    for zone in zones:
        print(f"📍 {zone['display_name']}")
        print(f"   Planet: {zone['planet']}")
        print(f"   Coordinates: {zone['coordinates']}")
        print(f"   Patrol Radius: {zone['patrol_radius']}")
        print(f"   Difficulty: {zone['difficulty']}")
        print(f"   Spawn Rate: {zone['spawn_rate']:.1%}")
        print(f"   Respawn Time: {zone['respawn_time']} minutes")
        print(f"   Enemy Types: {', '.join(zone['enemy_types'])}")
        if zone['notes']:
            print(f"   Notes: {zone['notes']}")
        print("-" * 80)


def list_targets_command(args):
    """List all available target items."""
    items = list_target_items()
    
    if not items:
        print("🎯 No target items configured")
        return
    
    print(f"🎯 Available Target Items ({len(items)}):")
    print("-" * 80)
    
    for item in items:
        print(f"📦 {item['display_name']}")
        print(f"   Rarity: {item['rarity'].title()}")
        print(f"   Value: {item['value']:,} credits")
        print(f"   Drop Rate: {item['drop_percentage']:.1%}")
        print(f"   Priority: {item['priority']}/5")
        print(f"   Drop Zones: {', '.join(item['drop_zones'])}")
        print(f"   Enemy Types: {', '.join(item['enemy_types'])}")
        if item['notes']:
            print(f"   Notes: {item['notes']}")
        print("-" * 80)


def recommendations_command(args):
    """Show farming recommendations."""
    recommendations = get_farming_recommendations()
    
    if not recommendations:
        print("💡 No farming recommendations available")
        return
    
    print(f"💡 Farming Recommendations ({len(recommendations)}):")
    print("-" * 80)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['target_item']}")
        print(f"   Zone: {rec['drop_zone']}")
        print(f"   Planet: {rec['planet']}")
        print(f"   Coordinates: {rec['coordinates']}")
        print(f"   Efficiency Score: {rec['efficiency_score']:.2f}")
        print(f"   Estimated Time: {rec['estimated_time']} minutes")
        print(f"   Difficulty: {rec['difficulty']}")
        print(f"   Value: {rec['value']:,} credits")
        print("-" * 80)


def add_loot_command(args):
    """Manually add loot acquisition to current session."""
    farmer = get_rare_loot_farmer()
    
    if not farmer.current_session:
        print("❌ No active farming session")
        return
    
    try:
        coordinates = tuple(map(int, args.coordinates.split(',')))
        
        acquisition = farmer.record_loot_acquisition(
            item_name=args.item,
            enemy_name=args.enemy,
            coordinates=coordinates
        )
        
        print(f"✅ Added loot acquisition:")
        print(f"   Item: {acquisition.item_name}")
        print(f"   Enemy: {acquisition.enemy_name}")
        print(f"   Coordinates: {acquisition.coordinates}")
        print(f"   Rarity: {acquisition.rarity.value}")
        print(f"   Verified: {acquisition.verified}")
        
    except Exception as e:
        print(f"❌ Failed to add loot: {e}")
        sys.exit(1)


def export_session_command(args):
    """Export session data to file."""
    farmer = get_rare_loot_farmer()
    
    try:
        export_path = farmer.export_session_data(args.session_id, args.format)
        print(f"✅ Session data exported to: {export_path}")
        
    except Exception as e:
        print(f"❌ Failed to export session: {e}")
        sys.exit(1)


def configure_zone_command(args):
    """Configure a drop zone."""
    farmer = get_rare_loot_farmer()
    
    # Create new zone configuration
    zone_config = {
        "name": args.name,
        "planet": args.planet,
        "coordinates": tuple(map(int, args.coordinates.split(','))),
        "patrol_radius": args.radius,
        "enemy_types": args.enemies.split(','),
        "spawn_rate": args.spawn_rate,
        "respawn_time": args.respawn_time,
        "difficulty": args.difficulty,
        "notes": args.notes
    }
    
    # Add to farmer's drop zones
    from core.rare_loot_farming import DropZone
    zone = DropZone(**zone_config)
    farmer.drop_zones[args.name] = zone
    
    # Save to file
    farmer._save_drop_zones(farmer.drop_zones)
    
    print(f"✅ Configured drop zone: {args.name}")
    print(f"   Planet: {zone.planet}")
    print(f"   Coordinates: {zone.coordinates}")
    print(f"   Patrol Radius: {zone.patrol_radius}")
    print(f"   Enemy Types: {', '.join(zone.enemy_types)}")


def configure_target_command(args):
    """Configure a target item."""
    farmer = get_rare_loot_farmer()
    
    # Create new target configuration
    target_config = {
        "name": args.name,
        "rarity": args.rarity,
        "drop_zones": args.zones.split(','),
        "enemy_types": args.enemies.split(','),
        "drop_percentage": args.drop_rate,
        "value": args.value,
        "priority": args.priority,
        "notes": args.notes
    }
    
    # Add to farmer's loot targets
    from core.rare_loot_farming import LootTarget, DropRarity
    target = LootTarget(
        name=target_config["name"],
        rarity=DropRarity(target_config["rarity"]),
        drop_zones=target_config["drop_zones"],
        enemy_types=target_config["enemy_types"],
        drop_percentage=target_config["drop_percentage"],
        value=target_config["value"],
        priority=target_config["priority"],
        notes=target_config["notes"]
    )
    farmer.loot_targets[args.name] = target
    
    # Save to file
    farmer._save_loot_targets(farmer.loot_targets)
    
    print(f"✅ Configured target item: {args.name}")
    print(f"   Rarity: {target.rarity.value}")
    print(f"   Value: {target.value:,} credits")
    print(f"   Drop Rate: {target.drop_percentage:.1%}")
    print(f"   Priority: {target.priority}/5")
    print(f"   Drop Zones: {', '.join(target.drop_zones)}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Rare Loot System (RLS) Farming CLI Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start a farming session
  python cli/rls_farming_cli.py start-session --zone krayt_dragon_zone --targets "Krayt Dragon Pearl"

  # List all zones
  python cli/rls_farming_cli.py list-zones

  # Show recommendations
  python cli/rls_farming_cli.py recommendations

  # Add loot manually
  python cli/rls_farming_cli.py add-loot --item "Krayt Dragon Pearl" --enemy "Greater Krayt Dragon" --coordinates "2000,1500"
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Start session command
    start_parser = subparsers.add_parser('start-session', help='Start a new RLS farming session')
    start_parser.add_argument('--zone', required=True, help='Target zone name')
    start_parser.add_argument('--targets', required=True, nargs='+', help='Target items to farm for')
    start_parser.set_defaults(func=start_session_command)
    
    # Stop session command
    stop_parser = subparsers.add_parser('stop-session', help='Stop the current RLS farming session')
    stop_parser.set_defaults(func=stop_session_command)
    
    # List sessions command
    list_parser = subparsers.add_parser('list-sessions', help='List all RLS farming sessions')
    list_parser.set_defaults(func=list_sessions_command)
    
    # Session stats command
    stats_parser = subparsers.add_parser('session-stats', help='Show statistics for a specific session')
    stats_parser.add_argument('session_id', help='Session ID to show stats for')
    stats_parser.set_defaults(func=session_stats_command)
    
    # List zones command
    zones_parser = subparsers.add_parser('list-zones', help='List all available drop zones')
    zones_parser.set_defaults(func=list_zones_command)
    
    # List targets command
    targets_parser = subparsers.add_parser('list-targets', help='List all available target items')
    targets_parser.set_defaults(func=list_targets_command)
    
    # Recommendations command
    rec_parser = subparsers.add_parser('recommendations', help='Show farming recommendations')
    rec_parser.set_defaults(func=recommendations_command)
    
    # Add loot command
    add_parser = subparsers.add_parser('add-loot', help='Manually add loot acquisition')
    add_parser.add_argument('--item', required=True, help='Item name')
    add_parser.add_argument('--enemy', required=True, help='Enemy name')
    add_parser.add_argument('--coordinates', required=True, help='Coordinates (x,y)')
    add_parser.set_defaults(func=add_loot_command)
    
    # Export session command
    export_parser = subparsers.add_parser('export-session', help='Export session data')
    export_parser.add_argument('session_id', help='Session ID to export')
    export_parser.add_argument('--format', default='json', help='Export format (default: json)')
    export_parser.set_defaults(func=export_session_command)
    
    # Configure zone command
    zone_config_parser = subparsers.add_parser('configure-zone', help='Configure a drop zone')
    zone_config_parser.add_argument('--name', required=True, help='Zone name')
    zone_config_parser.add_argument('--planet', required=True, help='Planet name')
    zone_config_parser.add_argument('--coordinates', required=True, help='Coordinates (x,y)')
    zone_config_parser.add_argument('--radius', type=int, required=True, help='Patrol radius')
    zone_config_parser.add_argument('--enemies', required=True, help='Comma-separated enemy types')
    zone_config_parser.add_argument('--spawn-rate', type=float, required=True, help='Spawn rate (0.0-1.0)')
    zone_config_parser.add_argument('--respawn-time', type=int, required=True, help='Respawn time in minutes')
    zone_config_parser.add_argument('--difficulty', required=True, help='Difficulty level')
    zone_config_parser.add_argument('--notes', help='Additional notes')
    zone_config_parser.set_defaults(func=configure_zone_command)
    
    # Configure target command
    target_config_parser = subparsers.add_parser('configure-target', help='Configure a target item')
    target_config_parser.add_argument('--name', required=True, help='Item name')
    target_config_parser.add_argument('--rarity', required=True, help='Rarity level')
    target_config_parser.add_argument('--zones', required=True, help='Comma-separated drop zones')
    target_config_parser.add_argument('--enemies', required=True, help='Comma-separated enemy types')
    target_config_parser.add_argument('--drop-rate', type=float, required=True, help='Drop rate (0.0-1.0)')
    target_config_parser.add_argument('--value', type=int, required=True, help='Item value in credits')
    target_config_parser.add_argument('--priority', type=int, default=1, help='Priority (1-5, default: 1)')
    target_config_parser.add_argument('--notes', help='Additional notes')
    target_config_parser.set_defaults(func=configure_target_command)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 