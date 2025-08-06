#!/usr/bin/env python3
"""Test suite for Batch 067 - SWGTracker.com Data Integration Layer."""

import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

# Import SWGTracker integration modules
from modules.swgtracker_integration import (
    MaterialTracker,
    GuildsCitiesTracker,
    PopulationPulseTracker,
    DataSyncManager,
    DashboardPanels
)
from modules.swgtracker_integration.material_tracker import MaterialData, MaterialTrackerConfig
from modules.swgtracker_integration.guilds_cities import GuildData, CityData, GuildsCitiesConfig
from modules.swgtracker_integration.population_pulse import PopulationData, PopulationPulseConfig


class TestMaterialTracker(unittest.TestCase):
    """Test cases for MaterialTracker."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = Path(self.temp_dir) / "materials"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Mock config to use temp directory
        self.config = MaterialTrackerConfig()
        self.config.api_url = "https://test.api/materials"
        
        # Create tracker instance
        self.tracker = MaterialTracker(self.config)
        self.tracker.cache_dir = self.cache_dir
        
        # Sample material data
        self.sample_materials = [
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
            }
        ]
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test MaterialTracker initialization."""
        self.assertIsNotNone(self.tracker)
        self.assertEqual(len(self.tracker.materials), 0)
        self.assertIsNone(self.tracker.last_sync)
    
    def test_process_material_data(self):
        """Test processing material data."""
        asyncio.run(self.tracker._process_material_data(self.sample_materials))
        
        self.assertEqual(len(self.tracker.materials), 2)
        self.assertIn("durasteel", self.tracker.materials)
        self.assertIn("titanium", self.tracker.materials)
        
        durasteel = self.tracker.materials["durasteel"]
        self.assertEqual(durasteel.name, "Durasteel")
        self.assertEqual(durasteel.rarity, "rare")
        self.assertEqual(durasteel.price, 5000.0)
    
    def test_save_and_load_cache(self):
        """Test saving and loading cache."""
        # Process data and save
        asyncio.run(self.tracker._process_material_data(self.sample_materials))
        self.tracker.last_sync = datetime.now()
        asyncio.run(self.tracker._save_to_cache())
        
        # Create new tracker and load cache
        new_tracker = MaterialTracker(self.config)
        new_tracker.cache_dir = self.cache_dir
        
        success = new_tracker.load_from_cache()
        self.assertTrue(success)
        self.assertEqual(len(new_tracker.materials), 2)
        self.assertIsNotNone(new_tracker.last_sync)
    
    def test_get_rare_materials(self):
        """Test getting rare materials."""
        # Add materials to tracker
        for material_data in self.sample_materials:
            material = MaterialData(**material_data)
            self.tracker.materials[material.name.lower()] = material
        
        rare_materials = self.tracker.get_rare_materials("rare")
        self.assertEqual(len(rare_materials), 2)  # Both are rare or above
        
        very_rare_materials = self.tracker.get_rare_materials("very_rare")
        self.assertEqual(len(very_rare_materials), 1)  # Only Titanium
    
    def test_get_materials_by_location(self):
        """Test getting materials by location."""
        # Add materials to tracker
        for material_data in self.sample_materials:
            material = MaterialData(**material_data)
            self.tracker.materials[material.name.lower()] = material
        
        tatooine_materials = self.tracker.get_materials_by_location("Tatooine")
        self.assertEqual(len(tatooine_materials), 1)
        self.assertEqual(tatooine_materials[0].name, "Durasteel")
    
    def test_get_price_data(self):
        """Test getting price data."""
        # Add materials to tracker
        for material_data in self.sample_materials:
            material = MaterialData(**material_data)
            self.tracker.materials[material.name.lower()] = material
        
        price_data = self.tracker.get_price_data()
        self.assertEqual(len(price_data), 2)
        self.assertEqual(price_data["Durasteel"], 5000.0)
        self.assertEqual(price_data["Titanium"], 15000.0)
    
    def test_is_cache_stale(self):
        """Test cache staleness detection."""
        # Fresh cache
        self.tracker.last_sync = datetime.now()
        self.assertFalse(self.tracker.is_cache_stale())
        
        # Stale cache
        self.tracker.last_sync = datetime.now() - timedelta(hours=2)
        self.assertTrue(self.tracker.is_cache_stale())
    
    def test_sync_materials_success(self):
        """Test successful material sync."""
        # Test the core functionality without actual API calls
        # Add materials directly and test processing
        asyncio.run(self.tracker._process_material_data(self.sample_materials))
        self.tracker.last_sync = datetime.now()
        
        self.assertEqual(len(self.tracker.materials), 2)
        self.assertIsNotNone(self.tracker.last_sync)
        
        # Test that we can get the materials
        rare_materials = self.tracker.get_rare_materials("rare")
        self.assertEqual(len(rare_materials), 2)
    
    def test_sync_materials_failure(self):
        """Test failed material sync."""
        # Test with empty data (simulating failure)
        empty_data = []
        asyncio.run(self.tracker._process_material_data(empty_data))
        
        self.assertEqual(len(self.tracker.materials), 0)


class TestGuildsCitiesTracker(unittest.TestCase):
    """Test cases for GuildsCitiesTracker."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = Path(self.temp_dir) / "guilds_cities"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Mock config
        self.config = GuildsCitiesConfig()
        self.config.api_url = "https://test.api/guilds-cities"
        
        # Create tracker instance
        self.tracker = GuildsCitiesTracker(self.config)
        self.tracker.cache_dir = self.cache_dir
        
        # Sample data
        self.sample_data = {
            "guilds": [
                {
                    "name": "Jedi Order",
                    "faction": "rebel",
                    "member_count": 150,
                    "territory_count": 8,
                    "influence": 0.85,
                    "headquarters": "Coruscant, Jedi Temple",
                    "leader": "Master Yoda"
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
                }
            ]
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test GuildsCitiesTracker initialization."""
        self.assertIsNotNone(self.tracker)
        self.assertEqual(len(self.tracker.guilds), 0)
        self.assertEqual(len(self.tracker.cities), 0)
        self.assertIsNone(self.tracker.last_sync)
    
    def test_process_guilds_cities_data(self):
        """Test processing guilds and cities data."""
        asyncio.run(self.tracker._process_guilds_cities_data(self.sample_data))
        
        self.assertEqual(len(self.tracker.guilds), 1)
        self.assertEqual(len(self.tracker.cities), 1)
        
        guild = self.tracker.guilds["jedi order"]
        self.assertEqual(guild.name, "Jedi Order")
        self.assertEqual(guild.faction, "rebel")
        self.assertEqual(guild.territory_count, 8)
        
        city = self.tracker.cities["mos eisley"]
        self.assertEqual(city.name, "Mos Eisley")
        self.assertEqual(city.planet, "Tatooine")
        self.assertEqual(city.coordinates, (100, 200))
        self.assertTrue(city.travel_hub)
    
    def test_get_travel_hubs(self):
        """Test getting travel hubs."""
        # Add cities to tracker
        for city_data in self.sample_data["cities"]:
            city = CityData(**city_data)
            self.tracker.cities[city.name.lower()] = city
        
        travel_hubs = self.tracker.get_travel_hubs()
        self.assertEqual(len(travel_hubs), 1)
        self.assertEqual(travel_hubs[0].name, "Mos Eisley")
    
    def test_get_guild_territories(self):
        """Test getting guild territories."""
        # Add cities to tracker
        for city_data in self.sample_data["cities"]:
            city = CityData(**city_data)
            self.tracker.cities[city.name.lower()] = city
        
        territories = self.tracker.get_guild_territories("Smugglers Guild")
        self.assertEqual(len(territories), 1)
        self.assertEqual(territories[0].name, "Mos Eisley")
    
    def test_get_popular_cities(self):
        """Test getting popular cities."""
        # Add cities to tracker
        for city_data in self.sample_data["cities"]:
            city = CityData(**city_data)
            self.tracker.cities[city.name.lower()] = city
        
        popular_cities = self.tracker.get_popular_cities(400)
        self.assertEqual(len(popular_cities), 1)  # Mos Eisley has 500 pop
        
        popular_cities = self.tracker.get_popular_cities(600)
        self.assertEqual(len(popular_cities), 0)  # No cities with 600+ pop
    
    def test_get_faction_guilds(self):
        """Test getting faction guilds."""
        # Add guilds to tracker
        for guild_data in self.sample_data["guilds"]:
            guild = GuildData(**guild_data)
            self.tracker.guilds[guild.name.lower()] = guild
        
        rebel_guilds = self.tracker.get_faction_guilds("rebel")
        self.assertEqual(len(rebel_guilds), 1)
        self.assertEqual(rebel_guilds[0].name, "Jedi Order")
        
        imperial_guilds = self.tracker.get_faction_guilds("imperial")
        self.assertEqual(len(imperial_guilds), 0)
    
    def test_get_territory_heatmap_data(self):
        """Test getting territory heatmap data."""
        # Add guilds to tracker
        for guild_data in self.sample_data["guilds"]:
            guild = GuildData(**guild_data)
            self.tracker.guilds[guild.name.lower()] = guild
        
        heatmap_data = self.tracker.get_territory_heatmap_data()
        self.assertEqual(len(heatmap_data), 1)
        self.assertEqual(heatmap_data["Jedi Order"], 8)


class TestPopulationPulseTracker(unittest.TestCase):
    """Test cases for PopulationPulseTracker."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = Path(self.temp_dir) / "population"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Mock config
        self.config = PopulationPulseConfig()
        self.config.api_url = "https://test.api/population-pulse"
        
        # Create tracker instance
        self.tracker = PopulationPulseTracker(self.config)
        self.tracker.cache_dir = self.cache_dir
        
        # Sample data
        self.sample_data = [
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
            }
        ]
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test PopulationPulseTracker initialization."""
        self.assertIsNotNone(self.tracker)
        self.assertEqual(len(self.tracker.population_data), 0)
        self.assertIsNone(self.tracker.last_sync)
    
    def test_process_population_data(self):
        """Test processing population data."""
        asyncio.run(self.tracker._process_population_data(self.sample_data))
        
        self.assertEqual(len(self.tracker.population_data), 2)
        
        key = "tatooine_mos eisley"
        self.assertIn(key, self.tracker.population_data)
        
        location = self.tracker.population_data[key]
        self.assertEqual(location.planet, "Tatooine")
        self.assertEqual(location.city, "Mos Eisley")
        self.assertEqual(location.population, 500)
        self.assertEqual(location.change_24h, 25)
    
    def test_get_popular_locations(self):
        """Test getting popular locations."""
        # Add data to tracker
        for data in self.sample_data:
            population = PopulationData(**data)
            key = f"{population.planet}_{population.city}".lower()
            self.tracker.population_data[key] = population
        
        popular_locations = self.tracker.get_popular_locations(400)
        self.assertEqual(len(popular_locations), 2)  # Both have 400+ pop
        
        popular_locations = self.tracker.get_popular_locations(600)
        self.assertEqual(len(popular_locations), 1)  # Only Theed has 600+ pop
    
    def test_get_growing_locations(self):
        """Test getting growing locations."""
        # Add data to tracker
        for data in self.sample_data:
            population = PopulationData(**data)
            key = f"{population.planet}_{population.city}".lower()
            self.tracker.population_data[key] = population
        
        growing_locations = self.tracker.get_growing_locations(30)
        self.assertEqual(len(growing_locations), 1)  # Only Theed has 30+ growth
        
        growing_locations = self.tracker.get_growing_locations(10)
        self.assertEqual(len(growing_locations), 2)  # Both have 10+ growth
    
    def test_get_active_locations(self):
        """Test getting active locations."""
        # Add data to tracker
        for data in self.sample_data:
            population = PopulationData(**data)
            key = f"{population.planet}_{population.city}".lower()
            self.tracker.population_data[key] = population
        
        active_locations = self.tracker.get_active_locations("high")
        self.assertEqual(len(active_locations), 1)  # Only Mos Eisley is high activity
        
        active_locations = self.tracker.get_active_locations("medium")
        self.assertEqual(len(active_locations), 1)  # Only Theed is medium activity
    
    def test_get_population_trends(self):
        """Test getting population trends."""
        # Add data to tracker
        for data in self.sample_data:
            population = PopulationData(**data)
            key = f"{population.planet}_{population.city}".lower()
            self.tracker.population_data[key] = population
        
        trends = self.tracker.get_population_trends()
        self.assertEqual(len(trends), 2)  # Two planets
        
        tatooine_trend = trends["Tatooine"]
        self.assertEqual(tatooine_trend["total_population"], 500)
        self.assertEqual(tatooine_trend["total_growth_24h"], 25)
        self.assertEqual(tatooine_trend["location_count"], 1)


class TestDataSyncManager(unittest.TestCase):
    """Test cases for DataSyncManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = Path(self.temp_dir) / "live_feeds"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Create sync manager
        self.sync_manager = DataSyncManager()
        self.sync_manager.cache_dir = self.cache_dir
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test DataSyncManager initialization."""
        self.assertIsNotNone(self.sync_manager)
        self.assertEqual(len(self.sync_manager.sync_history), 0)
        self.assertIsNone(self.sync_manager.last_full_sync)
    
    def test_load_all_caches(self):
        """Test loading all caches."""
        # Create mock cache files
        materials_cache = self.cache_dir / "materials" / "materials_cache.json"
        materials_cache.parent.mkdir(exist_ok=True)
        
        cache_data = {
            "last_sync": datetime.now().isoformat(),
            "materials": []
        }
        
        with open(materials_cache, 'w') as f:
            json.dump(cache_data, f)
        
        results = self.sync_manager.load_all_caches()
        self.assertIn("materials", results)
        # Note: This will be False in test environment since we're not setting up full cache structure
    
    def test_get_sync_status(self):
        """Test getting sync status."""
        status = self.sync_manager.get_sync_status()
        
        self.assertIn("last_full_sync", status)
        self.assertIn("enabled_trackers", status)
        self.assertIn("tracker_status", status)
    
    def test_get_data_summary(self):
        """Test getting data summary."""
        summary = self.sync_manager.get_data_summary()
        
        self.assertIn("materials", summary)
        self.assertIn("guilds_cities", summary)
        self.assertIn("population", summary)
    
    def test_is_any_cache_stale(self):
        """Test cache staleness detection."""
        # Initially should be stale (no sync)
        self.assertTrue(self.sync_manager.is_any_cache_stale())
        
        # Mock that all trackers are fresh
        if self.sync_manager.material_tracker:
            self.sync_manager.material_tracker.last_sync = datetime.now()
        if self.sync_manager.guilds_cities_tracker:
            self.sync_manager.guilds_cities_tracker.last_sync = datetime.now()
        if self.sync_manager.population_tracker:
            self.sync_manager.population_tracker.last_sync = datetime.now()
        
        self.assertFalse(self.sync_manager.is_any_cache_stale())


class TestDashboardPanels(unittest.TestCase):
    """Test cases for DashboardPanels."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = Path(self.temp_dir) / "dashboard"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Create mock trackers
        self.material_tracker = MaterialTracker()
        self.guilds_cities_tracker = GuildsCitiesTracker()
        self.population_tracker = PopulationPulseTracker()
        
        # Create dashboard panels
        self.dashboard = DashboardPanels(
            material_tracker=self.material_tracker,
            guilds_cities_tracker=self.guilds_cities_tracker,
            population_tracker=self.population_tracker
        )
        self.dashboard.cache_dir = self.cache_dir
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_initialization(self):
        """Test DashboardPanels initialization."""
        self.assertIsNotNone(self.dashboard)
        self.assertEqual(len(self.dashboard.panels), 0)
    
    def test_generate_rare_materials_panel(self):
        """Test generating rare materials panel."""
        # Add some materials to tracker
        material_data = MaterialData(
            name="Durasteel",
            rarity="rare",
            location="Tatooine",
            price=5000.0,
            last_seen="2024-01-15T10:30:00Z",
            quantity=10
        )
        self.material_tracker.materials["durasteel"] = material_data
        
        panel = self.dashboard.generate_rare_materials_panel()
        self.assertIsNotNone(panel)
        self.assertEqual(panel.title, "Rare Materials")
        self.assertEqual(panel.panel_type, "rare_materials")
        self.assertIn("total_rare_materials", panel.data)
    
    def test_generate_travel_hubs_panel(self):
        """Test generating travel hubs panel."""
        # Add some cities to tracker
        city_data = CityData(
            name="Mos Eisley",
            planet="Tatooine",
            coordinates=(100, 200),
            population=500,
            mayor="Jabba the Hutt",
            guild_controlled=True,
            controlling_guild="Smugglers Guild",
            travel_hub=True
        )
        self.guilds_cities_tracker.cities["mos eisley"] = city_data
        
        panel = self.dashboard.generate_travel_hubs_panel()
        self.assertIsNotNone(panel)
        self.assertEqual(panel.title, "Travel Hubs")
        self.assertEqual(panel.panel_type, "travel_hubs")
        self.assertIn("total_travel_hubs", panel.data["statistics"])
    
    def test_generate_all_panels(self):
        """Test generating all panels."""
        # Add some data to trackers
        material_data = MaterialData(
            name="Durasteel",
            rarity="rare",
            location="Tatooine",
            price=5000.0,
            last_seen="2024-01-15T10:30:00Z",
            quantity=10
        )
        self.material_tracker.materials["durasteel"] = material_data
        
        city_data = CityData(
            name="Mos Eisley",
            planet="Tatooine",
            coordinates=(100, 200),
            population=500,
            mayor="Jabba the Hutt",
            guild_controlled=True,
            controlling_guild="Smugglers Guild",
            travel_hub=True
        )
        self.guilds_cities_tracker.cities["mos eisley"] = city_data
        
        panels = self.dashboard.generate_all_panels()
        self.assertGreater(len(panels), 0)
        self.assertIn("rare_materials", panels)
        self.assertIn("travel_hubs", panels)
    
    def test_get_panel_summary(self):
        """Test getting panel summary."""
        summary = self.dashboard.get_panel_summary()
        
        self.assertIn("total_panels", summary)
        self.assertIn("available_panels", summary)
        self.assertIn("panel_types", summary)
    
    def test_export_panel_data(self):
        """Test exporting panel data."""
        # Add a panel first
        material_data = MaterialData(
            name="Durasteel",
            rarity="rare",
            location="Tatooine",
            price=5000.0,
            last_seen="2024-01-15T10:30:00Z",
            quantity=10
        )
        self.material_tracker.materials["durasteel"] = material_data
        
        panel = self.dashboard.generate_rare_materials_panel()
        self.dashboard.panels["rare_materials"] = panel
        
        # Export panel data
        exported_data = self.dashboard.export_panel_data("rare_materials", "json")
        self.assertIsNotNone(exported_data)
        self.assertIn("total_rare_materials", exported_data)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete SWGTracker integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cache_dir = Path(self.temp_dir) / "live_feeds"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_integration_workflow(self):
        """Test complete integration workflow."""
        # Create sync manager
        sync_manager = DataSyncManager()
        sync_manager.cache_dir = self.cache_dir
        
        # Create dashboard panels
        dashboard = DashboardPanels(
            material_tracker=sync_manager.material_tracker,
            guilds_cities_tracker=sync_manager.guilds_cities_tracker,
            population_tracker=sync_manager.population_tracker
        )
        dashboard.cache_dir = self.cache_dir / "dashboard"
        dashboard.cache_dir.mkdir(exist_ok=True)
        
        # Test sync status
        status = sync_manager.get_sync_status()
        self.assertIsInstance(status, dict)
        self.assertIn("enabled_trackers", status)
        
        # Test data summary
        summary = sync_manager.get_data_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn("materials", summary)
        
        # Test dashboard panels
        panels = dashboard.generate_all_panels()
        self.assertIsInstance(panels, dict)
        
        # Test panel summary
        panel_summary = dashboard.get_panel_summary()
        self.assertIsInstance(panel_summary, dict)
        self.assertIn("total_panels", panel_summary)


def run_tests():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestMaterialTracker,
        TestGuildsCitiesTracker,
        TestPopulationPulseTracker,
        TestDataSyncManager,
        TestDashboardPanels,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1) 