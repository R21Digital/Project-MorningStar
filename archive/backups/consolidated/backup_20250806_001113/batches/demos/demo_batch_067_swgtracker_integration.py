#!/usr/bin/env python3
"""Demo script for Batch 067 - SWGTracker.com Data Integration Layer.

This script demonstrates all features of the SWGTracker integration:
- Material Tracker data sync
- Guilds & Cities data sync
- Population Pulse data sync
- Local cache storage
- Dashboard panels for rare mats, travel hubs, and guild territory heatmaps
"""

import asyncio
import json
import logging
import tempfile
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import SWGTracker integration modules
from modules.swgtracker_integration import (
    MaterialTracker,
    GuildsCitiesTracker,
    PopulationPulseTracker,
    DataSyncManager,
    DashboardPanels
)


def create_mock_material_data():
    """Create mock material data for demonstration."""
    return [
        {
            "name": "Durasteel",
            "rarity": "rare",
            "location": "Tatooine, Anchorhead",
            "price": 5000.0,
            "last_seen": "2024-01-15T10:30:00Z",
            "quantity": 10
        },
        {
            "name": "Titanium",
            "rarity": "very_rare",
            "location": "Naboo, Theed",
            "price": 15000.0,
            "last_seen": "2024-01-15T09:15:00Z",
            "quantity": 5
        },
        {
            "name": "Carbonite",
            "rarity": "legendary",
            "location": "Hoth, Echo Base",
            "price": 50000.0,
            "last_seen": "2024-01-15T08:45:00Z",
            "quantity": 2
        },
        {
            "name": "Iron",
            "rarity": "common",
            "location": "Corellia, Coronet",
            "price": 100.0,
            "last_seen": "2024-01-15T11:20:00Z",
            "quantity": 50
        }
    ]


def create_mock_guilds_cities_data():
    """Create mock guilds and cities data for demonstration."""
    return {
        "guilds": [
            {
                "name": "Jedi Order",
                "faction": "rebel",
                "member_count": 150,
                "territory_count": 8,
                "influence": 0.85,
                "headquarters": "Coruscant, Jedi Temple",
                "leader": "Master Yoda"
            },
            {
                "name": "Sith Empire",
                "faction": "imperial",
                "member_count": 200,
                "territory_count": 12,
                "influence": 0.92,
                "headquarters": "Korriban, Sith Academy",
                "leader": "Darth Vader"
            },
            {
                "name": "Smugglers Guild",
                "faction": "neutral",
                "member_count": 75,
                "territory_count": 3,
                "influence": 0.45,
                "headquarters": "Nar Shaddaa, Smuggler's Den",
                "leader": "Han Solo"
            }
        ],
        "cities": [
            {
                "name": "Mos Eisley",
                "planet": "Tatooine",
                "coordinates": [100, 200],
                "population": 500,
                "mayor": "Jabba the Hutt",
                "guild_controlled": True,
                "controlling_guild": "Smugglers Guild",
                "travel_hub": True
            },
            {
                "name": "Theed",
                "planet": "Naboo",
                "coordinates": [300, 400],
                "population": 800,
                "mayor": "Queen Amidala",
                "guild_controlled": False,
                "controlling_guild": None,
                "travel_hub": True
            },
            {
                "name": "Coronet",
                "planet": "Corellia",
                "coordinates": [500, 600],
                "population": 1200,
                "mayor": "Governor Tarkin",
                "guild_controlled": True,
                "controlling_guild": "Sith Empire",
                "travel_hub": True
            }
        ]
    }


def create_mock_population_data():
    """Create mock population data for demonstration."""
    return [
        {
            "planet": "Tatooine",
            "city": "Mos Eisley",
            "population": 500,
            "change_24h": 25,
            "change_7d": 150,
            "activity_level": "high",
            "peak_hours": ["18:00", "19:00", "20:00"]
        },
        {
            "planet": "Naboo",
            "city": "Theed",
            "population": 800,
            "change_24h": 50,
            "change_7d": 300,
            "activity_level": "medium",
            "peak_hours": ["19:00", "20:00", "21:00"]
        },
        {
            "planet": "Corellia",
            "city": "Coronet",
            "population": 1200,
            "change_24h": 75,
            "change_7d": 450,
            "activity_level": "high",
            "peak_hours": ["17:00", "18:00", "19:00", "20:00"]
        }
    ]


class MockSWGTrackerAPI:
    """Mock SWGTracker API for demonstration purposes."""
    
    def __init__(self):
        self.material_data = create_mock_material_data()
        self.guilds_cities_data = create_mock_guilds_cities_data()
        self.population_data = create_mock_population_data()
    
    async def get_materials(self):
        """Mock material data endpoint."""
        await asyncio.sleep(0.1)  # Simulate API delay
        return self.material_data
    
    async def get_guilds_cities(self):
        """Mock guilds and cities data endpoint."""
        await asyncio.sleep(0.1)  # Simulate API delay
        return self.guilds_cities_data
    
    async def get_population(self):
        """Mock population data endpoint."""
        await asyncio.sleep(0.1)  # Simulate API delay
        return self.population_data


async def demo_material_tracker():
    """Demonstrate Material Tracker functionality."""
    print("\n" + "="*60)
    print("MATERIAL TRACKER DEMO")
    print("="*60)
    
    # Create mock API
    mock_api = MockSWGTrackerAPI()
    
    # Initialize material tracker
    material_tracker = MaterialTracker()
    
    # Simulate API call
    print("📡 Syncing material data from SWGTracker.com...")
    material_data = await mock_api.get_materials()
    
    # Process the data
    await material_tracker._process_material_data(material_data)
    material_tracker.last_sync = datetime.now()
    await material_tracker._save_to_cache()
    
    print(f"✅ Material sync completed: {len(material_tracker.materials)} materials")
    
    # Demonstrate material queries
    print("\n📊 Material Analysis:")
    print(f"  • Total materials: {len(material_tracker.materials)}")
    
    rare_materials = material_tracker.get_rare_materials("rare")
    print(f"  • Rare materials: {len(rare_materials)}")
    
    price_data = material_tracker.get_price_data()
    print(f"  • Materials with prices: {len(price_data)}")
    
    # Show some rare materials
    print("\n💎 Rare Materials:")
    for material in rare_materials:
        print(f"  • {material.name} ({material.rarity}) - {material.location}")
        if material.price:
            print(f"    Price: {material.price:,} credits")
    
    # Cache status
    status = material_tracker.get_sync_status()
    print(f"\n📋 Cache Status:")
    print(f"  • Last sync: {status['last_sync']}")
    print(f"  • Cache stale: {status['cache_stale']}")


async def demo_guilds_cities_tracker():
    """Demonstrate Guilds & Cities Tracker functionality."""
    print("\n" + "="*60)
    print("GUILDS & CITIES TRACKER DEMO")
    print("="*60)
    
    # Create mock API
    mock_api = MockSWGTrackerAPI()
    
    # Initialize guilds and cities tracker
    guilds_cities_tracker = GuildsCitiesTracker()
    
    # Simulate API call
    print("📡 Syncing guilds and cities data from SWGTracker.com...")
    guilds_cities_data = await mock_api.get_guilds_cities()
    
    # Process the data
    await guilds_cities_tracker._process_guilds_cities_data(guilds_cities_data)
    guilds_cities_tracker.last_sync = datetime.now()
    await guilds_cities_tracker._save_to_cache()
    
    print(f"✅ Guilds/Cities sync completed: {len(guilds_cities_tracker.guilds)} guilds, {len(guilds_cities_tracker.cities)} cities")
    
    # Demonstrate queries
    print("\n🏛️ Guild Analysis:")
    print(f"  • Total guilds: {len(guilds_cities_tracker.guilds)}")
    
    large_guilds = guilds_cities_tracker.get_large_guilds(100)
    print(f"  • Large guilds (100+ members): {len(large_guilds)}")
    
    rebel_guilds = guilds_cities_tracker.get_faction_guilds("rebel")
    print(f"  • Rebel guilds: {len(rebel_guilds)}")
    
    # Show top guilds
    print("\n👑 Top Guilds by Territory:")
    top_guilds = sorted(
        guilds_cities_tracker.guilds.values(),
        key=lambda g: g.territory_count,
        reverse=True
    )[:3]
    
    for guild in top_guilds:
        print(f"  • {guild.name} ({guild.faction}) - {guild.territory_count} territories")
    
    # Travel hubs
    print("\n🚀 Travel Hubs:")
    travel_hubs = guilds_cities_tracker.get_travel_hubs()
    for city in travel_hubs:
        print(f"  • {city.name}, {city.planet} (Pop: {city.population})")
        if city.guild_controlled:
            print(f"    Controlled by: {city.controlling_guild}")
    
    # Territory heatmap data
    heatmap_data = guilds_cities_tracker.get_territory_heatmap_data()
    print(f"\n🗺️ Territory Control:")
    for guild_name, territory_count in heatmap_data.items():
        print(f"  • {guild_name}: {territory_count} territories")


async def demo_population_tracker():
    """Demonstrate Population Pulse Tracker functionality."""
    print("\n" + "="*60)
    print("POPULATION PULSE TRACKER DEMO")
    print("="*60)
    
    # Create mock API
    mock_api = MockSWGTrackerAPI()
    
    # Initialize population tracker
    population_tracker = PopulationPulseTracker()
    
    # Simulate API call
    print("📡 Syncing population data from SWGTracker.com...")
    population_data = await mock_api.get_population()
    
    # Process the data
    await population_tracker._process_population_data(population_data)
    population_tracker.last_sync = datetime.now()
    await population_tracker._save_to_cache()
    
    print(f"✅ Population sync completed: {len(population_tracker.population_data)} locations")
    
    # Demonstrate queries
    print("\n👥 Population Analysis:")
    print(f"  • Total locations: {len(population_tracker.population_data)}")
    
    popular_locations = population_tracker.get_popular_locations(500)
    print(f"  • Popular locations (500+ pop): {len(popular_locations)}")
    
    growing_locations = population_tracker.get_growing_locations(25)
    print(f"  • Growing locations (25+ growth): {len(growing_locations)}")
    
    # Show population trends
    print("\n📈 Population Trends by Planet:")
    trends = population_tracker.get_population_trends()
    for planet, data in trends.items():
        print(f"  • {planet}:")
        print(f"    - Total population: {data['total_population']:,}")
        print(f"    - 24h growth: {data['total_growth_24h']:+}")
        print(f"    - Locations: {data['location_count']}")
    
    # Show growing locations
    print("\n🌱 Fastest Growing Locations:")
    top_growing = sorted(
        population_tracker.population_data.values(),
        key=lambda loc: loc.change_24h,
        reverse=True
    )[:3]
    
    for location in top_growing:
        print(f"  • {location.city}, {location.planet}: +{location.change_24h} (24h)")


async def demo_data_sync_manager():
    """Demonstrate Data Sync Manager functionality."""
    print("\n" + "="*60)
    print("DATA SYNC MANAGER DEMO")
    print("="*60)
    
    # Initialize sync manager
    sync_manager = DataSyncManager()
    
    # Load from cache first
    print("📂 Loading data from cache...")
    cache_results = sync_manager.load_all_caches()
    for tracker, success in cache_results.items():
        status = "✅" if success else "❌"
        print(f"  {status} {tracker}: {'Loaded' if success else 'Failed'}")
    
    # Get sync status
    print("\n📊 Sync Status:")
    status = sync_manager.get_sync_status()
    print(f"  • Last full sync: {status['last_full_sync']}")
    print(f"  • Enabled trackers: {', '.join(status['enabled_trackers'])}")
    
    # Check if cache is stale
    is_stale = sync_manager.is_any_cache_stale()
    print(f"  • Cache stale: {'Yes' if is_stale else 'No'}")
    
    # Get data summary
    print("\n📈 Data Summary:")
    summary = sync_manager.get_data_summary()
    for category, data in summary.items():
        if data:  # Only show categories with data
            print(f"  • {category.replace('_', ' ').title()}:")
            for key, value in data.items():
                print(f"    - {key.replace('_', ' ').title()}: {value}")


async def demo_dashboard_panels():
    """Demonstrate Dashboard Panels functionality."""
    print("\n" + "="*60)
    print("DASHBOARD PANELS DEMO")
    print("="*60)
    
    # Create mock data first
    mock_api = MockSWGTrackerAPI()
    
    # Initialize trackers with mock data
    material_tracker = MaterialTracker()
    guilds_cities_tracker = GuildsCitiesTracker()
    population_tracker = PopulationPulseTracker()
    
    # Load mock data
    material_data = await mock_api.get_materials()
    await material_tracker._process_material_data(material_data)
    
    guilds_cities_data = await mock_api.get_guilds_cities()
    await guilds_cities_tracker._process_guilds_cities_data(guilds_cities_data)
    
    population_data = await mock_api.get_population()
    await population_tracker._process_population_data(population_data)
    
    # Initialize dashboard panels
    dashboard = DashboardPanels(
        material_tracker=material_tracker,
        guilds_cities_tracker=guilds_cities_tracker,
        population_tracker=population_tracker
    )
    
    # Generate all panels
    print("🎛️ Generating dashboard panels...")
    panels = dashboard.generate_all_panels()
    
    print(f"✅ Generated {len(panels)} dashboard panels")
    
    # Show panel summary
    print("\n📋 Panel Summary:")
    summary = dashboard.get_panel_summary()
    print(f"  • Total panels: {summary['total_panels']}")
    print(f"  • Available panels: {', '.join(summary['available_panels'])}")
    
    # Show details for each panel
    for panel_name, panel in panels.items():
        print(f"\n📊 {panel.title}:")
        print(f"  • Type: {panel.panel_type}")
        print(f"  • Last updated: {panel.last_updated}")
        
        # Show some key data from each panel
        if panel_name == "rare_materials":
            data = panel.data
            print(f"  • Total rare materials: {data['total_rare_materials']}")
            print(f"  • Price stats: Avg {data['price_statistics']['average_price']:.0f} credits")
            
        elif panel_name == "travel_hubs":
            data = panel.data
            print(f"  • Total travel hubs: {data['statistics']['total_travel_hubs']}")
            print(f"  • Total population: {data['statistics']['total_population']:,}")
            
        elif panel_name == "guild_heatmap":
            data = panel.data
            print(f"  • Total guilds: {data['statistics']['total_guilds']}")
            print(f"  • Total territories: {data['statistics']['total_territories']}")
            
        elif panel_name == "population_trends":
            data = panel.data
            print(f"  • Total locations: {data['statistics']['total_locations']}")
            print(f"  • Growing locations: {data['statistics']['growing_locations']}")
    
    # Save panels to cache
    dashboard.save_panels_to_cache()
    print("\n💾 Dashboard panels saved to cache")


async def main():
    """Run the complete SWGTracker integration demo."""
    print("🚀 SWGTracker.com Data Integration Layer Demo")
    print("="*60)
    print("This demo showcases all features of Batch 067:")
    print("• Material Tracker data sync")
    print("• Guilds & Cities data sync") 
    print("• Population Pulse data sync")
    print("• Local cache storage in data/live_feeds/")
    print("• Dashboard panels for rare mats, travel hubs, and guild territory heatmaps")
    print("="*60)
    
    # Create temporary directory for demo
    with tempfile.TemporaryDirectory() as temp_dir:
        # Change to temp directory
        original_cwd = Path.cwd()
        os.chdir(temp_dir)
        
        try:
            # Run all demos
            await demo_material_tracker()
            await demo_guilds_cities_tracker()
            await demo_population_tracker()
            await demo_data_sync_manager()
            await demo_dashboard_panels()
            
            print("\n" + "="*60)
            print("✅ DEMO COMPLETED SUCCESSFULLY!")
            print("="*60)
            print("All SWGTracker.com integration features demonstrated:")
            print("• Material tracking with rarity filtering and price analysis")
            print("• Guild and city management with territory control")
            print("• Population monitoring with trend analysis")
            print("• Coordinated data synchronization")
            print("• Dashboard panels for data visualization")
            print("\nData cached in: data/live_feeds/")
            
        finally:
            # Restore original directory
            os.chdir(original_cwd)


if __name__ == "__main__":
    import os
    asyncio.run(main()) 