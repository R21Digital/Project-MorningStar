#!/usr/bin/env python3
"""
MS11 Batch 057 - SWGTracker Integration Tests

Comprehensive test suite for the SWGTracker integration system.
Tests data fetching, caching, analysis, and export functionality.
"""

import json
import os
import tempfile
import unittest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
from datetime import datetime, timedelta

# Add the project root to the path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from core.swgtracker_integration import (
    SWGTrackerIntegration,
    get_swgtracker_integration,
    get_top_cities,
    get_active_resources,
    get_guild_territories,
    get_rare_materials,
    ResourceData,
    GuildData,
    CityData,
    PulseData,
    SWGTrackerCache,
    DataType,
    ResourceCategory
)


class TestSWGTrackerIntegration(unittest.TestCase):
    """Test cases for the SWGTrackerIntegration class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_directory = tempfile.mkdtemp()
        self.integration = SWGTrackerIntegration(self.test_directory)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_directory)
    
    def test_init_with_cache_dir(self):
        """Test initialization with custom cache directory."""
        integration = SWGTrackerIntegration("/test/cache")
        self.assertEqual(integration.cache_dir, Path("/test/cache"))
    
    def test_load_cache_empty(self):
        """Test loading cache when no cache file exists."""
        # Remove any existing cache
        cache_file = self.integration.cache_dir / "swgtracker_cache.json"
        if cache_file.exists():
            cache_file.unlink()
        
        cache = self.integration._load_cache()
        self.assertEqual(len(cache.resources), 0)
        self.assertEqual(len(cache.guilds), 0)
        self.assertEqual(len(cache.cities), 0)
        self.assertIsNone(cache.pulse)
    
    def test_save_cache(self):
        """Test cache saving functionality."""
        # Create test data
        test_resource = ResourceData(
            name="Test Resource",
            type="mineral",
            rating=850,
            cpu=2,
            oq=800,
            cr=750,
            planet="Tatooine",
            date="2024-01-01",
            status="active",
            source="SA"
        )
        
        test_guild = GuildData(
            name="Test Guild",
            tag="TEST",
            faction="None",
            leader="Test Leader",
            members_total=50,
            members_active=25,
            active_percentage=50.0
        )
        
        test_city = CityData(
            name="Test City",
            planet="Naboo",
            mayor="Test Mayor",
            population=1000,
            status="active",
            last_updated="2024-01-01"
        )
        
        # Add to cache
        self.integration.cache.resources = [test_resource]
        self.integration.cache.guilds = [test_guild]
        self.integration.cache.cities = [test_city]
        self.integration.cache.last_updated = datetime.now().isoformat()
        
        # Save cache
        self.integration._save_cache()
        
        # Verify file was created
        cache_file = self.integration.cache_dir / "swgtracker_cache.json"
        self.assertTrue(cache_file.exists())
        
        # Load and verify
        with open(cache_file, 'r') as f:
            data = json.load(f)
        
        self.assertEqual(len(data['resources']), 1)
        self.assertEqual(len(data['guilds']), 1)
        self.assertEqual(len(data['cities']), 1)
        self.assertEqual(data['resources'][0]['name'], "Test Resource")
    
    def test_is_cache_valid(self):
        """Test cache validity checking."""
        # Test with no last_updated
        self.integration.cache.last_updated = ""
        self.assertFalse(self.integration._is_cache_valid())
        
        # Test with recent timestamp
        self.integration.cache.last_updated = datetime.now().isoformat()
        self.assertTrue(self.integration._is_cache_valid())
        
        # Test with old timestamp
        old_time = (datetime.now() - timedelta(hours=2)).isoformat()
        self.integration.cache.last_updated = old_time
        self.assertFalse(self.integration._is_cache_valid())
    
    def test_extract_row_data(self):
        """Test table row data extraction."""
        test_line = '<tr><td>Test Resource</td><td>mineral</td><td>850</td></tr>'
        data = self.integration._extract_row_data(test_line)
        
        self.assertEqual(len(data), 3)
        self.assertEqual(data[0], "Test Resource")
        self.assertEqual(data[1], "mineral")
        self.assertEqual(data[2], "850")
    
    def test_parse_resources_table(self):
        """Test resource table parsing."""
        test_html = """
        <table>
        <tr><td>Resource1</td><td>mineral</td><td>850</td><td>2</td><td>800</td><td>750</td><td>700</td><td>650</td><td>600</td><td>550</td><td>500</td><td>450</td><td>400</td><td>350</td><td>Tatooine</td><td>2024-01-01</td><td>active</td><td>SA</td></tr>
        <tr><td>Resource2</td><td>gas</td><td>900</td><td>2</td><td>850</td><td>800</td><td>750</td><td>700</td><td>650</td><td>600</td><td>550</td><td>500</td><td>450</td><td>400</td><td>Naboo</td><td>2024-01-01</td><td>active</td><td>SA</td></tr>
        </table>
        """
        
        resources = self.integration._parse_resources_table(test_html)
        
        self.assertEqual(len(resources), 2)
        self.assertEqual(resources[0].name, "Resource1")
        self.assertEqual(resources[0].type, "mineral")
        self.assertEqual(resources[0].rating, 850)
        self.assertEqual(resources[0].planet, "Tatooine")
        
        self.assertEqual(resources[1].name, "Resource2")
        self.assertEqual(resources[1].type, "gas")
        self.assertEqual(resources[1].rating, 900)
        self.assertEqual(resources[1].planet, "Naboo")
    
    def test_parse_guilds_table(self):
        """Test guilds table parsing."""
        test_html = """
        <table>
        <tr><td>Test Guild</td><td>TEST</td><td>None</td><td>Test Leader</td><td>50</td><td>25 50%</td></tr>
        <tr><td>Another Guild</td><td>ANOT</td><td>Imperial</td><td>Another Leader</td><td>30</td><td>15 50%</td></tr>
        </table>
        """
        
        guilds = self.integration._parse_guilds_table(test_html)
        
        self.assertEqual(len(guilds), 2)
        self.assertEqual(guilds[0].name, "Test Guild")
        self.assertEqual(guilds[0].tag, "TEST")
        self.assertEqual(guilds[0].leader, "Test Leader")
        self.assertEqual(guilds[0].members_total, 50)
        self.assertEqual(guilds[0].members_active, 25)
        self.assertEqual(guilds[0].active_percentage, 50.0)
    
    def test_parse_cities_table(self):
        """Test cities table parsing."""
        test_html = """
        <table>
        <tr><td>Test City</td><td>Naboo</td><td>Test Mayor</td><td>1000</td><td>active</td><td>2024-01-01</td></tr>
        <tr><td>Another City</td><td>Tatooine</td><td>Another Mayor</td><td>500</td><td>active</td><td>2024-01-01</td></tr>
        </table>
        """
        
        cities = self.integration._parse_cities_table(test_html)
        
        self.assertEqual(len(cities), 2)
        self.assertEqual(cities[0].name, "Test City")
        self.assertEqual(cities[0].planet, "Naboo")
        self.assertEqual(cities[0].mayor, "Test Mayor")
        self.assertEqual(cities[0].population, 1000)
        self.assertEqual(cities[0].status, "active")
    
    def test_parse_pulse_data(self):
        """Test pulse data parsing."""
        test_html = """
        <div>Online players: 1250</div>
        <div>Server status: Online</div>
        <div>Uptime: 24 hours</div>
        """
        
        pulse = self.integration._parse_pulse_data(test_html)
        
        self.assertIsNotNone(pulse)
        self.assertEqual(pulse.online_players, 1250)
        self.assertEqual(pulse.server_status, "Online")
        self.assertEqual(pulse.uptime, "Unknown")  # Default value
    
    @patch('requests.Session.get')
    def test_fetch_resources(self, mock_get):
        """Test resource fetching with mocked response."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = """
        <table>
        <tr><td>Test Resource</td><td>mineral</td><td>850</td><td>2</td><td>800</td><td>750</td><td>700</td><td>650</td><td>600</td><td>550</td><td>500</td><td>450</td><td>400</td><td>350</td><td>Tatooine</td><td>2024-01-01</td><td>active</td><td>SA</td></tr>
        </table>
        """
        mock_get.return_value = mock_response
        
        resources = self.integration.fetch_resources()
        
        self.assertEqual(len(resources), 1)
        self.assertEqual(resources[0].name, "Test Resource")
        mock_get.assert_called_once_with("https://swgtracker.com/")
    
    @patch('requests.Session.get')
    def test_fetch_guilds(self, mock_get):
        """Test guild fetching with mocked response."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = """
        <table>
        <tr><td>Test Guild</td><td>TEST</td><td>None</td><td>Test Leader</td><td>50</td><td>25 50%</td></tr>
        </table>
        """
        mock_get.return_value = mock_response
        
        guilds = self.integration.fetch_guilds()
        
        self.assertEqual(len(guilds), 1)
        self.assertEqual(guilds[0].name, "Test Guild")
        mock_get.assert_called_once_with("https://swgtracker.com/guilds.php")
    
    @patch('requests.Session.get')
    def test_fetch_cities(self, mock_get):
        """Test city fetching with mocked response."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = """
        <table>
        <tr><td>Test City</td><td>Naboo</td><td>Test Mayor</td><td>1000</td><td>active</td><td>2024-01-01</td></tr>
        </table>
        """
        mock_get.return_value = mock_response
        
        cities = self.integration.fetch_cities()
        
        self.assertEqual(len(cities), 1)
        self.assertEqual(cities[0].name, "Test City")
        mock_get.assert_called_once_with("https://swgtracker.com/cities.php")
    
    @patch('requests.Session.get')
    def test_fetch_pulse(self, mock_get):
        """Test pulse fetching with mocked response."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = """
        <div>Online players: 1250</div>
        <div>Server status: Online</div>
        """
        mock_get.return_value = mock_response
        
        pulse = self.integration.fetch_pulse()
        
        self.assertIsNotNone(pulse)
        self.assertEqual(pulse.online_players, 1250)
        mock_get.assert_called_once_with("https://swgtracker.com/pulse.php")
    
    def test_get_top_cities(self):
        """Test getting top cities."""
        # Add test cities to cache
        test_cities = [
            CityData("City1", "Naboo", "Mayor1", 1000, "active", "2024-01-01"),
            CityData("City2", "Tatooine", "Mayor2", 2000, "active", "2024-01-01"),
            CityData("City3", "Corellia", "Mayor3", 500, "active", "2024-01-01")
        ]
        self.integration.cache.cities = test_cities
        
        top_cities = self.integration.get_top_cities(limit=2)
        
        self.assertEqual(len(top_cities), 2)
        self.assertEqual(top_cities[0].name, "City2")  # Highest population
        self.assertEqual(top_cities[1].name, "City1")
    
    def test_get_active_resources(self):
        """Test getting active resources."""
        # Add test resources to cache
        test_resources = [
            ResourceData("Resource1", "mineral", 850, 2, planet="Tatooine", status="active", date="2024-01-01", source="SA"),
            ResourceData("Resource2", "gas", 900, 2, planet="Naboo", status="inactive", date="2024-01-01", source="SA"),
            ResourceData("Resource3", "mineral", 800, 2, planet="Corellia", status="active", date="2024-01-01", source="SA")
        ]
        self.integration.cache.resources = test_resources
        
        active_resources = self.integration.get_active_resources()
        self.assertEqual(len(active_resources), 2)
        
        # Test with category filter
        mineral_resources = self.integration.get_active_resources(category="mineral")
        self.assertEqual(len(mineral_resources), 2)
    
    def test_get_guild_territories(self):
        """Test getting guild territories."""
        # Add test cities with guild mayors
        test_cities = [
            CityData("City1", "Naboo", "Player1 (Guild1)", 1000, "active", "2024-01-01"),
            CityData("City2", "Tatooine", "Player2 (Guild1)", 2000, "active", "2024-01-01"),
            CityData("City3", "Corellia", "Player3 (Guild2)", 500, "active", "2024-01-01"),
            CityData("City4", "Naboo", "Player4 (Unknown)", 300, "active", "2024-01-01")
        ]
        self.integration.cache.cities = test_cities
        
        territories = self.integration.get_guild_territories()
        
        self.assertEqual(len(territories), 2)
        self.assertIn("Guild1", territories)
        self.assertIn("Guild2", territories)
        self.assertEqual(len(territories["Guild1"]), 2)
        self.assertEqual(len(territories["Guild2"]), 1)
    
    def test_get_rare_materials(self):
        """Test getting rare materials."""
        # Add test resources to cache
        test_resources = [
            ResourceData("Resource1", "mineral", 850, 2, planet="Tatooine", status="active", date="2024-01-01", source="SA"),
            ResourceData("Resource2", "gas", 900, 2, planet="Naboo", status="active", date="2024-01-01", source="SA"),
            ResourceData("Resource3", "mineral", 700, 2, planet="Corellia", status="active", date="2024-01-01", source="SA")
        ]
        self.integration.cache.resources = test_resources
        
        rare_materials = self.integration.get_rare_materials(min_rating=800)
        self.assertEqual(len(rare_materials), 2)
        
        # Test with higher threshold
        very_rare = self.integration.get_rare_materials(min_rating=900)
        self.assertEqual(len(very_rare), 1)
    
    def test_refresh_all_data(self):
        """Test refreshing all data."""
        with patch.object(self.integration, 'fetch_resources') as mock_resources, \
             patch.object(self.integration, 'fetch_guilds') as mock_guilds, \
             patch.object(self.integration, 'fetch_cities') as mock_cities, \
             patch.object(self.integration, 'fetch_pulse') as mock_pulse:
            
            self.integration.refresh_all_data()
            
            mock_resources.assert_called_once_with(force_refresh=True)
            mock_guilds.assert_called_once_with(force_refresh=True)
            mock_cities.assert_called_once_with(force_refresh=True)
            mock_pulse.assert_called_once_with(force_refresh=True)


class TestDataStructures(unittest.TestCase):
    """Test cases for data structures."""
    
    def test_resource_data(self):
        """Test ResourceData dataclass."""
        resource = ResourceData(
            name="Test Resource",
            type="mineral",
            rating=850,
            cpu=2,
            oq=800,
            cr=750,
            planet="Tatooine",
            date="2024-01-01",
            status="active",
            source="SA"
        )
        
        self.assertEqual(resource.name, "Test Resource")
        self.assertEqual(resource.type, "mineral")
        self.assertEqual(resource.rating, 850)
        self.assertEqual(resource.oq, 800)
        self.assertEqual(resource.planet, "Tatooine")
    
    def test_guild_data(self):
        """Test GuildData dataclass."""
        guild = GuildData(
            name="Test Guild",
            tag="TEST",
            faction="None",
            leader="Test Leader",
            members_total=50,
            members_active=25,
            active_percentage=50.0
        )
        
        self.assertEqual(guild.name, "Test Guild")
        self.assertEqual(guild.tag, "TEST")
        self.assertEqual(guild.members_total, 50)
        self.assertEqual(guild.active_percentage, 50.0)
    
    def test_city_data(self):
        """Test CityData dataclass."""
        city = CityData(
            name="Test City",
            planet="Naboo",
            mayor="Test Mayor",
            population=1000,
            status="active",
            last_updated="2024-01-01"
        )
        
        self.assertEqual(city.name, "Test City")
        self.assertEqual(city.planet, "Naboo")
        self.assertEqual(city.population, 1000)
        self.assertEqual(city.status, "active")
    
    def test_pulse_data(self):
        """Test PulseData dataclass."""
        pulse = PulseData(
            timestamp="2024-01-01T12:00:00",
            online_players=1250,
            server_status="Online",
            uptime="24 hours",
            performance_metrics={"cpu": 50, "memory": 75}
        )
        
        self.assertEqual(pulse.timestamp, "2024-01-01T12:00:00")
        self.assertEqual(pulse.online_players, 1250)
        self.assertEqual(pulse.server_status, "Online")
        self.assertEqual(pulse.performance_metrics["cpu"], 50)


class TestGlobalFunctions(unittest.TestCase):
    """Test cases for global convenience functions."""
    
    def test_get_swgtracker_integration(self):
        """Test get_swgtracker_integration function."""
        integration1 = get_swgtracker_integration()
        integration2 = get_swgtracker_integration()
        
        # Should return the same instance (singleton)
        self.assertIs(integration1, integration2)
    
    def test_get_top_cities(self):
        """Test get_top_cities function."""
        with patch('core.swgtracker_integration.get_swgtracker_integration') as mock_get:
            mock_integration = MagicMock()
            mock_integration.get_top_cities.return_value = [
                CityData("City1", "Naboo", "Mayor1", 1000, "active", "2024-01-01"),
                CityData("City2", "Tatooine", "Mayor2", 2000, "active", "2024-01-01")
            ]
            mock_get.return_value = mock_integration
            
            cities = get_top_cities(limit=5)
            
            self.assertEqual(len(cities), 2)
            mock_integration.get_top_cities.assert_called_once_with(5)
    
    def test_get_active_resources(self):
        """Test get_active_resources function."""
        with patch('core.swgtracker_integration.get_swgtracker_integration') as mock_get:
            mock_integration = MagicMock()
            mock_integration.get_active_resources.return_value = [
                ResourceData("Resource1", "mineral", 850, 2, planet="Tatooine", status="active", date="2024-01-01", source="SA")
            ]
            mock_get.return_value = mock_integration
            
            resources = get_active_resources(category="mineral")
            
            self.assertEqual(len(resources), 1)
            mock_integration.get_active_resources.assert_called_once_with("mineral")
    
    def test_get_guild_territories(self):
        """Test get_guild_territories function."""
        with patch('core.swgtracker_integration.get_swgtracker_integration') as mock_get:
            mock_integration = MagicMock()
            mock_integration.get_guild_territories.return_value = {
                "Guild1": ["City1", "City2"],
                "Guild2": ["City3"]
            }
            mock_get.return_value = mock_integration
            
            territories = get_guild_territories()
            
            self.assertEqual(len(territories), 2)
            mock_integration.get_guild_territories.assert_called_once()
    
    def test_get_rare_materials(self):
        """Test get_rare_materials function."""
        with patch('core.swgtracker_integration.get_swgtracker_integration') as mock_get:
            mock_integration = MagicMock()
            mock_integration.get_rare_materials.return_value = [
                ResourceData("Resource1", "mineral", 900, 2, planet="Tatooine", status="active", date="2024-01-01", source="SA")
            ]
            mock_get.return_value = mock_integration
            
            materials = get_rare_materials(min_rating=850)
            
            self.assertEqual(len(materials), 1)
            mock_integration.get_rare_materials.assert_called_once_with(850)


class TestEnums(unittest.TestCase):
    """Test cases for enums."""
    
    def test_data_type_enum(self):
        """Test DataType enum values."""
        self.assertEqual(DataType.RESOURCES.value, "resources")
        self.assertEqual(DataType.GUILDS.value, "guilds")
        self.assertEqual(DataType.CITIES.value, "cities")
        self.assertEqual(DataType.PULSE.value, "pulse")
    
    def test_resource_category_enum(self):
        """Test ResourceCategory enum values."""
        categories = {
            ResourceCategory.MINERAL: "mineral",
            ResourceCategory.GAS: "gas",
            ResourceCategory.METAL: "metal",
            ResourceCategory.ORGANIC: "organic",
            ResourceCategory.ENERGY: "energy"
        }
        
        for category, expected_value in categories.items():
            self.assertEqual(category.value, expected_value)


class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling."""
    
    def test_fetch_resources_error(self):
        """Test error handling in resource fetching."""
        integration = SWGTrackerIntegration()
        
        with patch('requests.Session.get', side_effect=Exception("Network error")):
            # Should return cached data (empty in this case)
            resources = integration.fetch_resources()
            self.assertEqual(len(resources), 0)
    
    def test_parse_invalid_html(self):
        """Test parsing invalid HTML."""
        integration = SWGTrackerIntegration()
        
        # Test with invalid HTML
        resources = integration._parse_resources_table("invalid html content")
        self.assertEqual(len(resources), 0)
    
    def test_cache_load_error(self):
        """Test cache loading error handling."""
        integration = SWGTrackerIntegration()
        
        # Create invalid cache file
        cache_file = integration.cache_dir / "swgtracker_cache.json"
        with open(cache_file, 'w') as f:
            f.write("invalid json content")
        
        # Should handle error gracefully
        cache = integration._load_cache()
        self.assertEqual(len(cache.resources), 0)


if __name__ == '__main__':
    unittest.main() 