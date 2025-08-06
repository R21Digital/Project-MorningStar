#!/usr/bin/env python3
"""
MS11 Batch 057 - SWGTracker Integration Demo

This demo showcases the SWGTracker integration functionality including:
- Data fetching from SWGTracker.com
- Caching and cache management
- Resource analysis and filtering
- Guild territory mapping
- Server pulse monitoring
"""

import json
import time
from pathlib import Path

# Add the project root to the path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from core.swgtracker_integration import (
    get_swgtracker_integration,
    get_top_cities,
    get_active_resources,
    get_guild_territories,
    get_rare_materials,
    DataType,
    ResourceCategory
)


def demo_data_fetching():
    """Demo basic data fetching functionality."""
    print("=" * 60)
    print("DEMO: Data Fetching")
    print("=" * 60)
    
    integration = get_swgtracker_integration()
    
    print("Fetching data from SWGTracker.com...")
    
    # Fetch resources
    try:
        resources = integration.fetch_resources()
        print(f"✓ Fetched {len(resources)} resources")
        
        active_resources = [r for r in resources if r.status.lower() == 'active']
        print(f"  - Active resources: {len(active_resources)}")
        
        rare_resources = [r for r in active_resources if r.rating >= 800]
        print(f"  - Rare resources (800+): {len(rare_resources)}")
        
    except Exception as e:
        print(f"✗ Failed to fetch resources: {e}")
    
    # Fetch guilds
    try:
        guilds = integration.fetch_guilds()
        print(f"✓ Fetched {len(guilds)} guilds")
        
        active_guilds = [g for g in guilds if g.active_percentage > 0]
        print(f"  - Active guilds: {len(active_guilds)}")
        
    except Exception as e:
        print(f"✗ Failed to fetch guilds: {e}")
    
    # Fetch cities
    try:
        cities = integration.fetch_cities()
        print(f"✓ Fetched {len(cities)} cities")
        
        total_population = sum(c.population for c in cities)
        print(f"  - Total population: {total_population:,}")
        
    except Exception as e:
        print(f"✗ Failed to fetch cities: {e}")
    
    # Fetch pulse
    try:
        pulse = integration.fetch_pulse()
        if pulse:
            print(f"✓ Fetched pulse data")
            print(f"  - Online players: {pulse.online_players:,}")
        else:
            print("⚠ No pulse data available")
            
    except Exception as e:
        print(f"✗ Failed to fetch pulse: {e}")


def demo_cache_management():
    """Demo cache management functionality."""
    print("\n" + "=" * 60)
    print("DEMO: Cache Management")
    print("=" * 60)
    
    integration = get_swgtracker_integration()
    
    # Show cache status
    cache = integration.cache
    print(f"Cache Status:")
    print(f"  Last Updated: {cache.last_updated}")
    print(f"  Cache Duration: {cache.cache_duration} seconds")
    print(f"  Resources Cached: {len(cache.resources)}")
    print(f"  Guilds Cached: {len(cache.guilds)}")
    print(f"  Cities Cached: {len(cache.cities)}")
    print(f"  Pulse Cached: {cache.pulse is not None}")
    
    # Check cache validity
    is_valid = integration._is_cache_valid()
    print(f"  Cache Valid: {'Yes' if is_valid else 'No'}")
    
    # Demo cache refresh
    print(f"\nRefreshing cache...")
    try:
        integration.refresh_all_data()
        print("✓ Cache refreshed successfully")
        
        # Show updated status
        cache = integration.cache
        print(f"  Updated: {cache.last_updated}")
        print(f"  Resources: {len(cache.resources)}")
        print(f"  Guilds: {len(cache.guilds)}")
        print(f"  Cities: {len(cache.cities)}")
        
    except Exception as e:
        print(f"✗ Failed to refresh cache: {e}")


def demo_resource_analysis():
    """Demo resource analysis functionality."""
    print("\n" + "=" * 60)
    print("DEMO: Resource Analysis")
    print("=" * 60)
    
    # Get active resources
    try:
        active_resources = get_active_resources()
        print(f"Active Resources: {len(active_resources)}")
        
        if active_resources:
            # Show top 5 by rating
            top_resources = sorted(active_resources, key=lambda x: x.rating, reverse=True)[:5]
            print(f"\nTop 5 Resources by Rating:")
            for i, resource in enumerate(top_resources, 1):
                print(f"  {i}. {resource.name}")
                print(f"     Type: {resource.type}")
                print(f"     Rating: {resource.rating}")
                print(f"     Planet: {resource.planet}")
                print()
        
        # Get rare materials
        rare_materials = get_rare_materials(min_rating=800)
        print(f"Rare Materials (800+): {len(rare_materials)}")
        
        if rare_materials:
            print(f"\nTop 3 Rare Materials:")
            for i, resource in enumerate(rare_materials[:3], 1):
                print(f"  {i}. {resource.name}")
                print(f"     Rating: {resource.rating}")
                print(f"     Type: {resource.type}")
                print(f"     Planet: {resource.planet}")
                print()
        
        # Analyze by category
        categories = {}
        for resource in active_resources:
            category = resource.type.lower()
            if category not in categories:
                categories[category] = []
            categories[category].append(resource)
        
        print(f"Resources by Category:")
        for category, resources in sorted(categories.items(), key=lambda x: len(x[1]), reverse=True)[:5]:
            print(f"  {category}: {len(resources)} resources")
        
    except Exception as e:
        print(f"✗ Failed to analyze resources: {e}")


def demo_guild_territories():
    """Demo guild territory analysis."""
    print("\n" + "=" * 60)
    print("DEMO: Guild Territory Analysis")
    print("=" * 60)
    
    try:
        territories = get_guild_territories()
        print(f"Guild Territories: {len(territories)} guilds")
        
        if territories:
            # Show top guilds by city count
            sorted_guilds = sorted(territories.items(), key=lambda x: len(x[1]), reverse=True)
            
            print(f"\nTop 5 Guilds by City Control:")
            for i, (guild_name, cities) in enumerate(sorted_guilds[:5], 1):
                print(f"  {i}. {guild_name}")
                print(f"     Cities: {len(cities)}")
                print(f"     Cities: {', '.join(cities[:3])}{'...' if len(cities) > 3 else ''}")
                print()
        
        # Show total cities controlled
        total_controlled = sum(len(cities) for cities in territories.values())
        print(f"Total Cities Controlled: {total_controlled}")
        
    except Exception as e:
        print(f"✗ Failed to analyze guild territories: {e}")


def demo_top_cities():
    """Demo top cities analysis."""
    print("\n" + "=" * 60)
    print("DEMO: Top Cities Analysis")
    print("=" * 60)
    
    try:
        top_cities = get_top_cities(limit=10)
        print(f"Top 10 Cities by Population:")
        
        for i, city in enumerate(top_cities, 1):
            print(f"  {i:2d}. {city.name}")
            print(f"       Planet: {city.planet}")
            print(f"       Mayor: {city.mayor}")
            print(f"       Population: {city.population:,}")
            print(f"       Status: {city.status}")
            print()
        
        # Calculate statistics
        total_population = sum(c.population for c in top_cities)
        avg_population = total_population / len(top_cities) if top_cities else 0
        
        print(f"Statistics:")
        print(f"  Total Population (Top 10): {total_population:,}")
        print(f"  Average Population: {avg_population:,.0f}")
        print(f"  Largest City: {top_cities[0].name} ({top_cities[0].population:,})")
        
    except Exception as e:
        print(f"✗ Failed to analyze top cities: {e}")


def demo_data_export():
    """Demo data export functionality."""
    print("\n" + "=" * 60)
    print("DEMO: Data Export")
    print("=" * 60)
    
    integration = get_swgtracker_integration()
    
    # Export different data types
    export_types = [
        ("resources", integration.fetch_resources()),
        ("guilds", integration.fetch_guilds()),
        ("cities", integration.fetch_cities()),
        ("pulse", integration.fetch_pulse())
    ]
    
    for data_type, data in export_types:
        if data:
            try:
                # Convert to JSON-serializable format
                if hasattr(data, '__iter__') and not isinstance(data, (str, bytes)):
                    json_data = []
                    for item in data:
                        if hasattr(item, '__dict__'):
                            json_data.append(item.__dict__)
                        else:
                            json_data.append(item)
                else:
                    json_data = data.__dict__ if hasattr(data, '__dict__') else data
                
                # Save to file
                filename = f"demo_{data_type}_export.json"
                with open(filename, 'w') as f:
                    json.dump({
                        'data_type': data_type,
                        'timestamp': integration.cache.last_updated,
                        'count': len(data) if hasattr(data, '__len__') else 1,
                        'data': json_data
                    }, f, indent=2)
                
                print(f"✓ Exported {data_type} to {filename}")
                
            except Exception as e:
                print(f"✗ Failed to export {data_type}: {e}")


def demo_integration_scenarios():
    """Demo real-world integration scenarios."""
    print("\n" + "=" * 60)
    print("DEMO: Integration Scenarios")
    print("=" * 60)
    
    integration = get_swgtracker_integration()
    
    # Scenario 1: Finding rare materials for crafting
    print("Scenario 1: Rare Materials for Crafting")
    try:
        rare_materials = get_rare_materials(min_rating=900)
        print(f"Found {len(rare_materials)} rare materials (900+ rating)")
        
        if rare_materials:
            print("Top materials for crafting:")
            for i, resource in enumerate(rare_materials[:3], 1):
                print(f"  {i}. {resource.name} (Rating: {resource.rating})")
                print(f"     Planet: {resource.planet}")
                print(f"     Type: {resource.type}")
                print()
        
    except Exception as e:
        print(f"✗ Scenario 1 failed: {e}")
    
    # Scenario 2: Guild territory analysis for travel decisions
    print("Scenario 2: Guild Territory Analysis")
    try:
        territories = get_guild_territories()
        print(f"Analyzing {len(territories)} guild territories")
        
        if territories:
            # Find guilds with most cities
            top_guilds = sorted(territories.items(), key=lambda x: len(x[1]), reverse=True)[:3]
            print("Top guilds for travel planning:")
            for guild_name, cities in top_guilds:
                print(f"  {guild_name}: {len(cities)} cities")
                print(f"    Cities: {', '.join(cities[:5])}{'...' if len(cities) > 5 else ''}")
                print()
        
    except Exception as e:
        print(f"✗ Scenario 2 failed: {e}")
    
    # Scenario 3: Server activity monitoring
    print("Scenario 3: Server Activity Monitoring")
    try:
        pulse = integration.fetch_pulse()
        if pulse:
            print(f"Server Status: {pulse.server_status}")
            print(f"Online Players: {pulse.online_players:,}")
            print(f"Last Updated: {pulse.timestamp}")
            
            # Determine activity level
            if pulse.online_players > 1000:
                activity_level = "High"
            elif pulse.online_players > 500:
                activity_level = "Medium"
            else:
                activity_level = "Low"
            
            print(f"Activity Level: {activity_level}")
        else:
            print("No pulse data available")
        
    except Exception as e:
        print(f"✗ Scenario 3 failed: {e}")


def main():
    """Run all demos."""
    print("MS11 Batch 057 - SWGTracker Integration Demo")
    print("=" * 60)
    
    try:
        demo_data_fetching()
        demo_cache_management()
        demo_resource_analysis()
        demo_guild_territories()
        demo_top_cities()
        demo_data_export()
        demo_integration_scenarios()
        
        print("\n" + "=" * 60)
        print("DEMO COMPLETE")
        print("=" * 60)
        print("The SWGTracker integration provides:")
        print("✅ Live data fetching from SWGTracker.com")
        print("✅ Intelligent caching with automatic refresh")
        print("✅ Resource analysis and filtering")
        print("✅ Guild territory mapping")
        print("✅ Server pulse monitoring")
        print("✅ Data export capabilities")
        print("✅ Real-world integration scenarios")
        
    except Exception as e:
        print(f"Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 