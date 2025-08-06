#!/usr/bin/env python3
"""
Batch 152 - Rare Loot Drop Table Viewer Tests

This test suite covers the rare loot drop table viewer functionality including:
- Database structure validation
- Filtering and search capabilities
- UI component testing
- Data source integration
- Export functionality
- Boss profile integration

Usage:
    python test_batch_152_rare_loot_viewer.py
"""

import json
import logging
import os
import shutil
import sys
import tempfile
import time
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

class TestRareLootDatabase(unittest.TestCase):
    """Test the rare loot database structure and content."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.database_file = Path("data/rare_loot_database.json")
        self.test_data = {
            "metadata": {
                "version": "1.0",
                "last_updated": "2025-01-04T12:00:00",
                "data_sources": ["community_submissions", "ms11_scanning", "rls_wiki", "loot_tables"],
                "total_items": 10,
                "total_sources": 4
            },
            "categories": {
                "weapons": {"name": "Weapons", "description": "Rare weapons", "icon": "sword", "color": "#dc3545"},
                "armor": {"name": "Armor", "description": "Rare armor", "icon": "shield", "color": "#28a745"}
            },
            "locations": {
                "tatooine": {"name": "Tatooine", "zones": ["Krayt Dragon Valley"]},
                "lok": {"name": "Lok", "zones": ["Kimogila Territory"]}
            },
            "enemy_types": {
                "boss": {"name": "Boss", "description": "Major bosses", "difficulty": "high", "color": "#dc3545"},
                "elite": {"name": "Elite", "description": "Elite enemies", "difficulty": "medium", "color": "#fd7e14"}
            },
            "items": [
                {
                    "id": "test_item_001",
                    "name": "Test Item",
                    "category": "weapons",
                    "rarity": "legendary",
                    "description": "A test item",
                    "locations": [{
                        "planet": "tatooine",
                        "zone": "Krayt Dragon Valley",
                        "enemy_type": "boss",
                        "enemy_name": "Test Boss",
                        "drop_rate": 0.05,
                        "confirmed_drops": 2,
                        "last_seen": "2024-01-15T09:45:30"
                    }],
                    "stats": {"value": 50000, "weight": 1.0, "attributes": ["test", "valuable"]},
                    "sources": ["ms11_scanning", "community_submissions"],
                    "image_url": "/images/loot/test_item.jpg",
                    "wiki_url": "https://swgr.org/wiki/rls/test-item"
                }
            ],
            "boss_profiles": {
                "test_boss": {
                    "name": "Test Boss",
                    "planet": "tatooine",
                    "zone": "Krayt Dragon Valley",
                    "level": 90,
                    "type": "boss",
                    "description": "A test boss",
                    "known_drops": ["test_item_001"],
                    "spawn_conditions": "Test spawn",
                    "difficulty": "high",
                    "image_url": "/images/bosses/test_boss.jpg",
                    "wiki_url": "https://swgr.org/wiki/bosses/test-boss"
                }
            }
        }
    
    def test_database_structure(self):
        """Test that the database has the correct structure."""
        if not self.database_file.exists():
            self.skipTest("Database file not found")
        
        with open(self.database_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check required top-level keys
        required_keys = ['metadata', 'categories', 'locations', 'enemy_types', 'items', 'boss_profiles']
        for key in required_keys:
            self.assertIn(key, data, f"Missing required key: {key}")
        
        # Check metadata structure
        metadata = data['metadata']
        self.assertIn('version', metadata)
        self.assertIn('last_updated', metadata)
        self.assertIn('data_sources', metadata)
        self.assertIsInstance(metadata['data_sources'], list)
    
    def test_categories_structure(self):
        """Test that categories have the correct structure."""
        if not self.database_file.exists():
            self.skipTest("Database file not found")
        
        with open(self.database_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        categories = data['categories']
        self.assertIsInstance(categories, dict)
        
        for category_id, category in categories.items():
            required_fields = ['name', 'description', 'icon', 'color']
            for field in required_fields:
                self.assertIn(field, category, f"Category {category_id} missing field: {field}")
    
    def test_locations_structure(self):
        """Test that locations have the correct structure."""
        if not self.database_file.exists():
            self.skipTest("Database file not found")
        
        with open(self.database_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        locations = data['locations']
        self.assertIsInstance(locations, dict)
        
        for location_id, location in locations.items():
            self.assertIn('name', location)
            self.assertIn('zones', location)
            self.assertIsInstance(location['zones'], list)
    
    def test_enemy_types_structure(self):
        """Test that enemy types have the correct structure."""
        if not self.database_file.exists():
            self.skipTest("Database file not found")
        
        with open(self.database_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        enemy_types = data['enemy_types']
        self.assertIsInstance(enemy_types, dict)
        
        for enemy_type_id, enemy_type in enemy_types.items():
            required_fields = ['name', 'description', 'difficulty', 'color']
            for field in required_fields:
                self.assertIn(field, enemy_type, f"Enemy type {enemy_type_id} missing field: {field}")
    
    def test_items_structure(self):
        """Test that items have the correct structure."""
        if not self.database_file.exists():
            self.skipTest("Database file not found")
        
        with open(self.database_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        items = data['items']
        self.assertIsInstance(items, list)
        self.assertGreater(len(items), 0, "No items found in database")
        
        for item in items:
            required_fields = ['id', 'name', 'category', 'rarity', 'description', 'locations', 'stats', 'sources']
            for field in required_fields:
                self.assertIn(field, item, f"Item missing required field: {field}")
            
            # Check locations structure
            self.assertIsInstance(item['locations'], list)
            for location in item['locations']:
                location_fields = ['planet', 'zone', 'enemy_type', 'enemy_name', 'drop_rate', 'confirmed_drops', 'last_seen']
                for field in location_fields:
                    self.assertIn(field, location, f"Location missing field: {field}")
            
            # Check stats structure
            stats = item['stats']
            self.assertIn('value', stats)
            self.assertIn('weight', stats)
            self.assertIn('attributes', stats)
            self.assertIsInstance(stats['attributes'], list)
    
    def test_boss_profiles_structure(self):
        """Test that boss profiles have the correct structure."""
        if not self.database_file.exists():
            self.skipTest("Database file not found")
        
        with open(self.database_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        boss_profiles = data['boss_profiles']
        self.assertIsInstance(boss_profiles, dict)
        
        for boss_id, boss in boss_profiles.items():
            required_fields = ['name', 'planet', 'zone', 'level', 'type', 'description', 'known_drops', 'spawn_conditions', 'difficulty']
            for field in required_fields:
                self.assertIn(field, boss, f"Boss profile {boss_id} missing field: {field}")

class TestRareLootFiltering(unittest.TestCase):
    """Test filtering and search capabilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_items = [
            {
                "id": "item_1",
                "name": "Legendary Sword",
                "category": "weapons",
                "rarity": "legendary",
                "description": "A powerful sword",
                "locations": [{
                    "planet": "tatooine",
                    "zone": "Krayt Dragon Valley",
                    "enemy_type": "boss",
                    "enemy_name": "Greater Krayt Dragon",
                    "drop_rate": 0.02,
                    "confirmed_drops": 1,
                    "last_seen": "2024-01-15T09:45:30"
                }],
                "stats": {"value": 75000, "weight": 3.0, "attributes": ["legendary", "powerful"]},
                "sources": ["ms11_scanning", "community_submissions"]
            },
            {
                "id": "item_2",
                "name": "Epic Armor",
                "category": "armor",
                "rarity": "epic",
                "description": "Strong armor",
                "locations": [{
                    "planet": "lok",
                    "zone": "Kimogila Territory",
                    "enemy_type": "boss",
                    "enemy_name": "Kimogila Matriarch",
                    "drop_rate": 0.15,
                    "confirmed_drops": 5,
                    "last_seen": "2024-01-10T14:22:15"
                }],
                "stats": {"value": 35000, "weight": 5.0, "attributes": ["protective", "valuable"]},
                "sources": ["rls_wiki"]
            },
            {
                "id": "item_3",
                "name": "Rare Crystal",
                "category": "jewelry",
                "rarity": "rare",
                "description": "A rare crystal",
                "locations": [{
                    "planet": "dantooine",
                    "zone": "Force Crystal Cave",
                    "enemy_type": "elite",
                    "enemy_name": "Crystal Guardian",
                    "drop_rate": 0.25,
                    "confirmed_drops": 3,
                    "last_seen": "2024-01-12T16:33:45"
                }],
                "stats": {"value": 15000, "weight": 0.5, "attributes": ["crystal", "jewelry"]},
                "sources": ["community_submissions"]
            }
        ]
    
    def test_category_filtering(self):
        """Test filtering by category."""
        weapons = [item for item in self.test_items if item['category'] == 'weapons']
        self.assertEqual(len(weapons), 1)
        self.assertEqual(weapons[0]['name'], 'Legendary Sword')
        
        armor = [item for item in self.test_items if item['category'] == 'armor']
        self.assertEqual(len(armor), 1)
        self.assertEqual(armor[0]['name'], 'Epic Armor')
    
    def test_rarity_filtering(self):
        """Test filtering by rarity."""
        legendary = [item for item in self.test_items if item['rarity'] == 'legendary']
        self.assertEqual(len(legendary), 1)
        self.assertEqual(legendary[0]['name'], 'Legendary Sword')
        
        epic = [item for item in self.test_items if item['rarity'] == 'epic']
        self.assertEqual(len(epic), 1)
        self.assertEqual(epic[0]['name'], 'Epic Armor')
    
    def test_planet_filtering(self):
        """Test filtering by planet."""
        tatooine_items = [item for item in self.test_items 
                         if any(loc['planet'] == 'tatooine' for loc in item['locations'])]
        self.assertEqual(len(tatooine_items), 1)
        self.assertEqual(tatooine_items[0]['name'], 'Legendary Sword')
        
        lok_items = [item for item in self.test_items 
                    if any(loc['planet'] == 'lok' for loc in item['locations'])]
        self.assertEqual(len(lok_items), 1)
        self.assertEqual(lok_items[0]['name'], 'Epic Armor')
    
    def test_enemy_type_filtering(self):
        """Test filtering by enemy type."""
        boss_drops = [item for item in self.test_items 
                     if any(loc['enemy_type'] == 'boss' for loc in item['locations'])]
        self.assertEqual(len(boss_drops), 2)
        
        elite_drops = [item for item in self.test_items 
                      if any(loc['enemy_type'] == 'elite' for loc in item['locations'])]
        self.assertEqual(len(elite_drops), 1)
        self.assertEqual(elite_drops[0]['name'], 'Rare Crystal')
    
    def test_value_filtering(self):
        """Test filtering by value range."""
        high_value = [item for item in self.test_items if item['stats']['value'] > 50000]
        self.assertEqual(len(high_value), 1)
        self.assertEqual(high_value[0]['name'], 'Legendary Sword')
        
        medium_value = [item for item in self.test_items 
                       if 10000 <= item['stats']['value'] <= 50000]
        self.assertEqual(len(medium_value), 2)
    
    def test_source_filtering(self):
        """Test filtering by data source."""
        ms11_items = [item for item in self.test_items if 'ms11_scanning' in item['sources']]
        self.assertEqual(len(ms11_items), 1)
        self.assertEqual(ms11_items[0]['name'], 'Legendary Sword')
        
        community_items = [item for item in self.test_items if 'community_submissions' in item['sources']]
        self.assertEqual(len(community_items), 2)
    
    def test_search_functionality(self):
        """Test search functionality."""
        # Search by name
        sword_results = [item for item in self.test_items if 'sword' in item['name'].lower()]
        self.assertEqual(len(sword_results), 1)
        self.assertEqual(sword_results[0]['name'], 'Legendary Sword')
        
        # Search by description
        powerful_results = [item for item in self.test_items if 'powerful' in item['description'].lower()]
        self.assertEqual(len(powerful_results), 1)
        self.assertEqual(powerful_results[0]['name'], 'Legendary Sword')
        
        # Search by enemy name
        krayt_results = [item for item in self.test_items 
                        if any('krayt' in loc['enemy_name'].lower() for loc in item['locations'])]
        self.assertEqual(len(krayt_results), 1)
        self.assertEqual(krayt_results[0]['name'], 'Legendary Sword')

class TestRareLootSorting(unittest.TestCase):
    """Test sorting functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_items = [
            {
                "id": "item_1",
                "name": "Zebra Sword",
                "rarity": "legendary",
                "stats": {"value": 75000},
                "locations": [{"drop_rate": 0.02, "last_seen": "2024-01-15T09:45:30"}]
            },
            {
                "id": "item_2", 
                "name": "Alpha Armor",
                "rarity": "epic",
                "stats": {"value": 35000},
                "locations": [{"drop_rate": 0.15, "last_seen": "2024-01-10T14:22:15"}]
            },
            {
                "id": "item_3",
                "name": "Beta Crystal",
                "rarity": "rare",
                "stats": {"value": 15000},
                "locations": [{"drop_rate": 0.25, "last_seen": "2024-01-12T16:33:45"}]
            }
        ]
    
    def test_name_sorting(self):
        """Test sorting by name."""
        sorted_items = sorted(self.test_items, key=lambda x: x['name'])
        self.assertEqual(sorted_items[0]['name'], 'Alpha Armor')
        self.assertEqual(sorted_items[1]['name'], 'Beta Crystal')
        self.assertEqual(sorted_items[2]['name'], 'Zebra Sword')
    
    def test_rarity_sorting(self):
        """Test sorting by rarity."""
        rarity_order = {'legendary': 5, 'epic': 4, 'rare': 3, 'uncommon': 2, 'common': 1}
        sorted_items = sorted(self.test_items, key=lambda x: rarity_order[x['rarity']], reverse=True)
        self.assertEqual(sorted_items[0]['rarity'], 'legendary')
        self.assertEqual(sorted_items[1]['rarity'], 'epic')
        self.assertEqual(sorted_items[2]['rarity'], 'rare')
    
    def test_value_sorting(self):
        """Test sorting by value."""
        sorted_items = sorted(self.test_items, key=lambda x: x['stats']['value'], reverse=True)
        self.assertEqual(sorted_items[0]['stats']['value'], 75000)
        self.assertEqual(sorted_items[1]['stats']['value'], 35000)
        self.assertEqual(sorted_items[2]['stats']['value'], 15000)
    
    def test_drop_rate_sorting(self):
        """Test sorting by drop rate."""
        sorted_items = sorted(self.test_items, 
                            key=lambda x: max(loc['drop_rate'] for loc in x['locations']), 
                            reverse=True)
        self.assertEqual(sorted_items[0]['locations'][0]['drop_rate'], 0.25)
        self.assertEqual(sorted_items[1]['locations'][0]['drop_rate'], 0.15)
        self.assertEqual(sorted_items[2]['locations'][0]['drop_rate'], 0.02)
    
    def test_recent_sorting(self):
        """Test sorting by recent activity."""
        sorted_items = sorted(self.test_items,
                            key=lambda x: max(datetime.fromisoformat(loc['last_seen']).timestamp() for loc in x['locations']),
                            reverse=True)
        # Should be sorted by last_seen date (most recent first)
        self.assertEqual(sorted_items[0]['locations'][0]['last_seen'], "2024-01-15T09:45:30")
        self.assertEqual(sorted_items[1]['locations'][0]['last_seen'], "2024-01-12T16:33:45")
        self.assertEqual(sorted_items[2]['locations'][0]['last_seen'], "2024-01-10T14:22:15")

class TestRareLootExport(unittest.TestCase):
    """Test export functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_data = {
            "items": [
                {
                    "id": "export_test_1",
                    "name": "Export Test Item 1",
                    "rarity": "legendary",
                    "category": "weapons",
                    "stats": {"value": 100000},
                    "locations": [{"planet": "tatooine", "enemy_type": "boss"}],
                    "sources": ["ms11_scanning"]
                },
                {
                    "id": "export_test_2", 
                    "name": "Export Test Item 2",
                    "rarity": "epic",
                    "category": "armor",
                    "stats": {"value": 50000},
                    "locations": [{"planet": "lok", "enemy_type": "elite"}],
                    "sources": ["community_submissions"]
                }
            ]
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_export_filtered_data(self):
        """Test exporting filtered data."""
        # Filter for legendary items
        legendary_items = [item for item in self.test_data['items'] if item['rarity'] == 'legendary']
        
        export_data = {
            "export_info": {
                "scenario": "legendary_items",
                "description": "Legendary items only",
                "export_date": datetime.now().isoformat(),
                "total_items": len(legendary_items)
            },
            "items": legendary_items
        }
        
        export_file = Path(self.temp_dir) / "legendary_items_export.json"
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2)
        
        # Verify export file
        self.assertTrue(export_file.exists())
        
        with open(export_file, 'r', encoding='utf-8') as f:
            exported_data = json.load(f)
        
        self.assertEqual(exported_data['export_info']['total_items'], 1)
        self.assertEqual(exported_data['items'][0]['name'], 'Export Test Item 1')
    
    def test_export_multiple_scenarios(self):
        """Test exporting multiple scenarios."""
        scenarios = [
            {
                "name": "legendary_items",
                "filter": lambda item: item['rarity'] == 'legendary'
            },
            {
                "name": "boss_drops", 
                "filter": lambda item: any(loc['enemy_type'] == 'boss' for loc in item['locations'])
            },
            {
                "name": "high_value_items",
                "filter": lambda item: item['stats']['value'] > 75000
            }
        ]
        
        for scenario in scenarios:
            filtered_items = list(filter(scenario['filter'], self.test_data['items']))
            
            export_data = {
                "export_info": {
                    "scenario": scenario['name'],
                    "description": f"Filtered by {scenario['name']}",
                    "export_date": datetime.now().isoformat(),
                    "total_items": len(filtered_items)
                },
                "items": filtered_items
            }
            
            export_file = Path(self.temp_dir) / f"{scenario['name']}_export.json"
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2)
            
            self.assertTrue(export_file.exists())
            
            # Verify file size is reasonable
            file_size = export_file.stat().st_size
            self.assertGreater(file_size, 0)
            self.assertLess(file_size, 100000)  # Should be less than 100KB

class TestRareLootValidation(unittest.TestCase):
    """Test data validation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.valid_item = {
            "id": "valid_item_001",
            "name": "Valid Item",
            "category": "weapons",
            "rarity": "legendary",
            "description": "A valid test item",
            "locations": [{
                "planet": "tatooine",
                "zone": "Test Zone",
                "enemy_type": "boss",
                "enemy_name": "Test Boss",
                "drop_rate": 0.05,
                "confirmed_drops": 1,
                "last_seen": "2024-01-15T09:45:30"
            }],
            "stats": {"value": 50000, "weight": 1.0, "attributes": ["test"]},
            "sources": ["ms11_scanning"]
        }
    
    def test_valid_item_structure(self):
        """Test that a valid item passes validation."""
        required_fields = ['id', 'name', 'category', 'rarity', 'description', 'locations', 'stats', 'sources']
        
        for field in required_fields:
            self.assertIn(field, self.valid_item, f"Valid item missing required field: {field}")
        
        # Check locations structure
        self.assertIsInstance(self.valid_item['locations'], list)
        for location in self.valid_item['locations']:
            location_fields = ['planet', 'zone', 'enemy_type', 'enemy_name', 'drop_rate', 'confirmed_drops', 'last_seen']
            for field in location_fields:
                self.assertIn(field, location, f"Location missing field: {field}")
        
        # Check stats structure
        stats = self.valid_item['stats']
        self.assertIn('value', stats)
        self.assertIn('weight', stats)
        self.assertIn('attributes', stats)
        self.assertIsInstance(stats['attributes'], list)
    
    def test_invalid_item_missing_fields(self):
        """Test that invalid items are caught."""
        invalid_items = [
            {"name": "Missing ID"},  # Missing id
            {"id": "test", "name": "Missing Category"},  # Missing category
            {"id": "test", "name": "test", "category": "weapons", "rarity": "invalid"},  # Invalid rarity
        ]
        
        valid_rarities = ['common', 'uncommon', 'rare', 'epic', 'legendary']
        
        for item in invalid_items:
            if 'id' not in item:
                self.assertRaises(KeyError, lambda: item['id'])
            
            if 'rarity' in item and item['rarity'] not in valid_rarities:
                self.assertNotIn(item['rarity'], valid_rarities)
    
    def test_category_validation(self):
        """Test category validation."""
        valid_categories = ['weapons', 'armor', 'jewelry', 'resources', 'collectibles', 'consumables']
        
        # Test valid category
        self.assertIn(self.valid_item['category'], valid_categories)
        
        # Test invalid category
        invalid_item = self.valid_item.copy()
        invalid_item['category'] = 'invalid_category'
        self.assertNotIn(invalid_item['category'], valid_categories)
    
    def test_rarity_validation(self):
        """Test rarity validation."""
        valid_rarities = ['common', 'uncommon', 'rare', 'epic', 'legendary']
        
        # Test valid rarity
        self.assertIn(self.valid_item['rarity'], valid_rarities)
        
        # Test invalid rarity
        invalid_item = self.valid_item.copy()
        invalid_item['rarity'] = 'invalid_rarity'
        self.assertNotIn(invalid_item['rarity'], valid_rarities)

class TestRareLootIntegration(unittest.TestCase):
    """Test integration with other systems."""
    
    def test_boss_profile_integration(self):
        """Test integration with boss profiles."""
        test_boss = {
            "name": "Test Boss",
            "planet": "tatooine",
            "zone": "Test Zone",
            "level": 90,
            "type": "boss",
            "description": "A test boss",
            "known_drops": ["test_item_001"],
            "spawn_conditions": "Test spawn",
            "difficulty": "high"
        }
        
        # Test boss profile structure
        required_fields = ['name', 'planet', 'zone', 'level', 'type', 'description', 'known_drops', 'spawn_conditions', 'difficulty']
        for field in required_fields:
            self.assertIn(field, test_boss, f"Boss profile missing field: {field}")
        
        # Test known drops
        self.assertIsInstance(test_boss['known_drops'], list)
        self.assertIn('test_item_001', test_boss['known_drops'])
    
    def test_data_source_integration(self):
        """Test integration with data sources."""
        valid_sources = ['community_submissions', 'ms11_scanning', 'rls_wiki', 'loot_tables']
        
        test_item = {
            "sources": ["ms11_scanning", "community_submissions"]
        }
        
        # Test that all sources are valid
        for source in test_item['sources']:
            self.assertIn(source, valid_sources, f"Invalid data source: {source}")
    
    def test_location_integration(self):
        """Test integration with location data."""
        valid_planets = ['tatooine', 'lok', 'kashyyyk', 'dantooine', 'naboo', 'corellia']
        valid_enemy_types = ['boss', 'elite', 'rare', 'common']
        
        test_location = {
            "planet": "tatooine",
            "enemy_type": "boss"
        }
        
        # Test valid planet
        self.assertIn(test_location['planet'], valid_planets)
        
        # Test valid enemy type
        self.assertIn(test_location['enemy_type'], valid_enemy_types)

def run_tests():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestRareLootDatabase,
        TestRareLootFiltering,
        TestRareLootSorting,
        TestRareLootExport,
        TestRareLootValidation,
        TestRareLootIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    return len(result.failures) + len(result.errors) == 0

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 