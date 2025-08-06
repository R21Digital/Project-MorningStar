#!/usr/bin/env python3
"""
MS11 Batch 057 - SWGTracker Manager CLI

Command-line interface for the SWGTracker integration system.
Provides data fetching, reporting, and cache management functionality.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.swgtracker_integration import (
    get_swgtracker_integration,
    get_top_cities,
    get_active_resources,
    get_guild_territories,
    get_rare_materials,
    DataType,
    ResourceCategory
)


def print_top_cities(cities, limit: int = 10) -> None:
    """Print top populated cities.
    
    Args:
        cities: List of city data
        limit: Maximum number to display
    """
    print(f"\nTop {min(len(cities), limit)} Populated Cities")
    print("=" * 60)
    
    for i, city in enumerate(cities[:limit], 1):
        print(f"{i:2d}. {city.name}")
        print(f"     Planet: {city.planet}")
        print(f"     Mayor: {city.mayor}")
        print(f"     Population: {city.population:,}")
        print(f"     Status: {city.status}")
        print()


def print_active_resources(resources, category: Optional[str] = None) -> None:
    """Print active resources.
    
    Args:
        resources: List of resource data
        category: Optional category filter
    """
    title = "Active Resources"
    if category:
        title += f" - {category.title()}"
    
    print(f"\n{title}")
    print("=" * 60)
    
    if not resources:
        print("No active resources found.")
        return
    
    for i, resource in enumerate(resources[:20], 1):  # Show first 20
        print(f"{i:2d}. {resource.name}")
        print(f"     Type: {resource.type}")
        print(f"     Rating: {resource.rating}")
        print(f"     Planet: {resource.planet}")
        print(f"     Status: {resource.status}")
        print(f"     Date: {resource.date}")
        if resource.oq:
            print(f"     OQ: {resource.oq}")
        if resource.sr:
            print(f"     SR: {resource.sr}")
        print()


def print_guild_territories(territories) -> None:
    """Print guild-controlled territories.
    
    Args:
        territories: Dictionary of guild territories
    """
    print(f"\nGuild-Controlled Territories")
    print("=" * 60)
    
    if not territories:
        print("No guild territories found.")
        return
    
    for guild_name, cities in territories.items():
        print(f"Guild: {guild_name}")
        print(f"  Controlled Cities ({len(cities)}):")
        for city in cities:
            print(f"    - {city}")
        print()


def print_rare_materials(resources, min_rating: int = 800) -> None:
    """Print rare materials.
    
    Args:
        resources: List of resource data
        min_rating: Minimum rating threshold
    """
    print(f"\nRare Materials (Rating >= {min_rating})")
    print("=" * 60)
    
    if not resources:
        print("No rare materials found.")
        return
    
    for i, resource in enumerate(resources[:15], 1):  # Show first 15
        print(f"{i:2d}. {resource.name}")
        print(f"     Type: {resource.type}")
        print(f"     Rating: {resource.rating}")
        print(f"     Planet: {resource.planet}")
        print(f"     Status: {resource.status}")
        if resource.oq:
            print(f"     OQ: {resource.oq}")
        if resource.sr:
            print(f"     SR: {resource.sr}")
        print()


def print_server_pulse(pulse) -> None:
    """Print server pulse data.
    
    Args:
        pulse: Pulse data object
    """
    print(f"\nServer Pulse")
    print("=" * 60)
    
    if not pulse:
        print("No pulse data available.")
        return
    
    print(f"Timestamp: {pulse.timestamp}")
    print(f"Online Players: {pulse.online_players:,}")
    print(f"Server Status: {pulse.server_status}")
    print(f"Uptime: {pulse.uptime}")
    
    if pulse.performance_metrics:
        print(f"Performance Metrics:")
        for metric, value in pulse.performance_metrics.items():
            print(f"  {metric}: {value}")


def print_cache_status(integration) -> None:
    """Print cache status information.
    
    Args:
        integration: SWGTracker integration instance
    """
    print(f"\nCache Status")
    print("=" * 60)
    
    cache = integration.cache
    print(f"Last Updated: {cache.last_updated}")
    print(f"Cache Duration: {cache.cache_duration} seconds")
    print(f"Resources Cached: {len(cache.resources)}")
    print(f"Guilds Cached: {len(cache.guilds)}")
    print(f"Cities Cached: {len(cache.cities)}")
    print(f"Pulse Cached: {cache.pulse is not None}")
    
    # Check if cache is valid
    is_valid = integration._is_cache_valid()
    print(f"Cache Valid: {'Yes' if is_valid else 'No'}")


def print_data_summary(integration) -> None:
    """Print a summary of all data.
    
    Args:
        integration: SWGTracker integration instance
    """
    print(f"\nSWGTracker Data Summary")
    print("=" * 60)
    
    # Resources summary
    resources = integration.fetch_resources()
    active_resources = [r for r in resources if r.status.lower() == 'active']
    rare_resources = [r for r in active_resources if r.rating >= 800]
    
    print(f"Total Resources: {len(resources)}")
    print(f"Active Resources: {len(active_resources)}")
    print(f"Rare Resources (800+): {len(rare_resources)}")
    
    # Guilds summary
    guilds = integration.fetch_guilds()
    active_guilds = [g for g in guilds if g.active_percentage > 0]
    
    print(f"Total Guilds: {len(guilds)}")
    print(f"Active Guilds: {len(active_guilds)}")
    
    # Cities summary
    cities = integration.fetch_cities()
    top_cities = sorted(cities, key=lambda x: x.population, reverse=True)[:5]
    
    print(f"Total Cities: {len(cities)}")
    print(f"Top 5 Cities by Population:")
    for i, city in enumerate(top_cities, 1):
        print(f"  {i}. {city.name} ({city.planet}): {city.population:,}")
    
    # Pulse summary
    pulse = integration.fetch_pulse()
    if pulse:
        print(f"Online Players: {pulse.online_players:,}")
        print(f"Server Status: {pulse.server_status}")


def save_report(filepath: str, data_type: str, data) -> None:
    """Save data report to JSON file.
    
    Args:
        filepath: Path to save the report
        data_type: Type of data being saved
        data: Data to save
    """
    try:
        # Convert dataclass objects to dictionaries
        if hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
            json_data = []
            for item in data:
                if hasattr(item, '__dict__'):
                    json_data.append(item.__dict__)
                else:
                    json_data.append(item)
        else:
            json_data = data.__dict__ if hasattr(data, '__dict__') else data
        
        report = {
            'data_type': data_type,
            'timestamp': integration.cache.last_updated,
            'data': json_data
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✓ Saved {data_type} report to {filepath}")
        
    except Exception as e:
        print(f"Error saving report: {e}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="MS11 SWGTracker Manager - Fetch and manage SWGTracker.com data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli/swgtracker_manager.py --summary
  python cli/swgtracker_manager.py --top-cities 5
  python cli/swgtracker_manager.py --active-resources
  python cli/swgtracker_manager.py --active-resources --category mineral
  python cli/swgtracker_manager.py --guild-territories
  python cli/swgtracker_manager.py --rare-materials --min-rating 900
  python cli/swgtracker_manager.py --server-pulse
  python cli/swgtracker_manager.py --cache-status
  python cli/swgtracker_manager.py --refresh-all
  python cli/swgtracker_manager.py --save-report resources.json --data-type resources
        """
    )
    
    parser.add_argument(
        '--summary',
        action='store_true',
        help='Show data summary'
    )
    
    parser.add_argument(
        '--top-cities',
        type=int,
        metavar='LIMIT',
        help='Show top populated cities (default: 10)'
    )
    
    parser.add_argument(
        '--active-resources',
        action='store_true',
        help='Show active resources'
    )
    
    parser.add_argument(
        '--category',
        choices=[cat.value for cat in ResourceCategory],
        help='Filter resources by category'
    )
    
    parser.add_argument(
        '--guild-territories',
        action='store_true',
        help='Show guild-controlled territories'
    )
    
    parser.add_argument(
        '--rare-materials',
        action='store_true',
        help='Show rare materials'
    )
    
    parser.add_argument(
        '--min-rating',
        type=int,
        default=800,
        help='Minimum rating for rare materials (default: 800)'
    )
    
    parser.add_argument(
        '--server-pulse',
        action='store_true',
        help='Show server pulse data'
    )
    
    parser.add_argument(
        '--cache-status',
        action='store_true',
        help='Show cache status'
    )
    
    parser.add_argument(
        '--refresh-all',
        action='store_true',
        help='Force refresh all cached data'
    )
    
    parser.add_argument(
        '--save-report',
        metavar='FILE',
        help='Save data report to JSON file'
    )
    
    parser.add_argument(
        '--data-type',
        choices=[dt.value for dt in DataType],
        help='Data type for report saving'
    )
    
    args = parser.parse_args()
    
    # Get integration instance
    try:
        integration = get_swgtracker_integration()
    except Exception as e:
        print(f"Error initializing SWGTracker integration: {e}")
        return 1
    
    # Handle refresh command first
    if args.refresh_all:
        try:
            integration.refresh_all_data()
            print("✓ All data refreshed successfully")
        except Exception as e:
            print(f"Error refreshing data: {e}")
            return 1
    
    # Handle commands
    try:
        if args.summary:
            print_data_summary(integration)
        
        if args.top_cities is not None:
            cities = get_top_cities(args.top_cities)
            print_top_cities(cities, args.top_cities)
        
        if args.active_resources:
            resources = get_active_resources(args.category)
            print_active_resources(resources, args.category)
        
        if args.guild_territories:
            territories = get_guild_territories()
            print_guild_territories(territories)
        
        if args.rare_materials:
            resources = get_rare_materials(args.min_rating)
            print_rare_materials(resources, args.min_rating)
        
        if args.server_pulse:
            pulse = integration.fetch_pulse()
            print_server_pulse(pulse)
        
        if args.cache_status:
            print_cache_status(integration)
        
        # Handle report saving
        if args.save_report and args.data_type:
            data = None
            if args.data_type == DataType.RESOURCES.value:
                data = get_active_resources()
            elif args.data_type == DataType.GUILDS.value:
                data = integration.fetch_guilds()
            elif args.data_type == DataType.CITIES.value:
                data = get_top_cities()
            elif args.data_type == DataType.PULSE.value:
                data = integration.fetch_pulse()
            
            if data:
                save_report(args.save_report, args.data_type, data)
        
        # If no specific command, show summary
        if not any([args.summary, args.top_cities is not None, args.active_resources,
                   args.guild_territories, args.rare_materials, args.server_pulse,
                   args.cache_status, args.refresh_all, args.save_report]):
            print_data_summary(integration)
        
    except Exception as e:
        print(f"Error executing command: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 