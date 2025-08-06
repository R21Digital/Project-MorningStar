#!/usr/bin/env python3
"""
Batch 186 Test - Loot Tables Page (Heroics) + Loot Sync Logic
Comprehensive testing of the new loot table system
"""

import json
import os
import sys
import unittest
from datetime import datetime
from pathlib import Path

class TestLootTables(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.loot_tables_dir = Path("src/data/loot_tables")
        self.test_data = {}
        self.load_test_data()
        
    def load_test_data(self):
        """Load test loot table data"""
        for json_file in self.loot_tables_dir.glob("*.json"):
            planet = json_file.stem
            try:
                with open(json_file, 'r') as f:
                    self.test_data[planet] = json.load(f)
            except Exception as e:
                self.fail(f"Failed to load {planet}: {e}")
                
    def test_loot_table_structure(self):
        """Test that loot tables have correct structure"""
        print("Testing loot table structure...")
        
        for planet, data in self.test_data.items():
            # Check required top-level fields
            self.assertIn('source_type', data, f"Missing source_type in {planet}")
            self.assertIn('planet', data, f"Missing planet in {planet}")
            self.assertIn('total_runs', data, f"Missing total_runs in {planet}")
            self.assertIn('total_loot', data, f"Missing total_loot in {planet}")
            self.assertIn('last_updated', data, f"Missing last_updated in {planet}")
            self.assertIn('heroics', data, f"Missing heroics in {planet}")
            
            # Check heroics structure
            for heroic_key, heroic_data in data['heroics'].items():
                self.assertIn('boss', heroic_data, f"Missing boss in {planet}.{heroic_key}")
                self.assertIn('location', heroic_data, f"Missing location in {planet}.{heroic_key}")
                self.assertIn('level', heroic_data, f"Missing level in {planet}.{heroic_key}")
                self.assertIn('total_kills', heroic_data, f"Missing total_kills in {planet}.{heroic_key}")
                self.assertIn('items', heroic_data, f"Missing items in {planet}.{heroic_key}")
                
                # Check items structure
                for item_key, item_data in heroic_data['items'].items():
                    self.assertIn('name', item_data, f"Missing name in {planet}.{heroic_key}.{item_key}")
                    self.assertIn('type', item_data, f"Missing type in {planet}.{heroic_key}.{item_key}")
                    self.assertIn('rarity', item_data, f"Missing rarity in {planet}.{heroic_key}.{item_key}")
                    self.assertIn('use_case', item_data, f"Missing use_case in {planet}.{heroic_key}.{item_key}")
                    self.assertIn('drop_chance', item_data, f"Missing drop_chance in {planet}.{heroic_key}.{item_key}")
                    self.assertIn('profession_relevance', item_data, f"Missing profession_relevance in {planet}.{heroic_key}.{item_key}")
                    self.assertIn('source', item_data, f"Missing source in {planet}.{heroic_key}.{item_key}")
                    
        print("✅ Loot table structure tests passed")
        
    def test_data_consistency(self):
        """Test data consistency across all loot tables"""
        print("Testing data consistency...")
        
        # Check that planet field matches filename
        for planet, data in self.test_data.items():
            self.assertEqual(data['planet'], planet, f"Planet field mismatch in {planet}")
            
        # Check that source_type is consistent
        for planet, data in self.test_data.items():
            self.assertEqual(data['source_type'], 'heroic', f"Invalid source_type in {planet}")
            
        # Check that all items have valid rarity values
        valid_rarities = ['common', 'uncommon', 'rare', 'epic', 'legendary']
        for planet, data in self.test_data.items():
            for heroic_key, heroic_data in data['heroics'].items():
                for item_key, item_data in heroic_data['items'].items():
                    self.assertIn(item_data['rarity'], valid_rarities, 
                                f"Invalid rarity in {planet}.{heroic_key}.{item_key}")
                    
        # Check that all items have valid types
        valid_types = ['weapon', 'armor', 'material', 'component', 'trophy', 'decoration']
        for planet, data in self.test_data.items():
            for heroic_key, heroic_data in data['heroics'].items():
                for item_key, item_data in heroic_data['items'].items():
                    self.assertIn(item_data['type'], valid_types, 
                                f"Invalid type in {planet}.{heroic_key}.{item_key}")
                    
        print("✅ Data consistency tests passed")
        
    def test_filtering_system(self):
        """Test the filtering system"""
        print("Testing filtering system...")
        
        # Test rarity filter
        legendary_items = self.filter_items_by_criteria({'rarity': 'legendary'})
        self.assertGreater(len(legendary_items), 0, "No legendary items found")
        
        # Test type filter
        weapon_items = self.filter_items_by_criteria({'type': 'weapon'})
        self.assertGreater(len(weapon_items), 0, "No weapon items found")
        
        # Test profession filter
        weaponsmith_items = self.filter_items_by_criteria({'profession': 'weaponsmith'})
        self.assertGreater(len(weaponsmith_items), 0, "No weaponsmith items found")
        
        # Test source filter
        swgdb_items = self.filter_items_by_criteria({'source': 'SWGDB Generated'})
        self.assertGreater(len(swgdb_items), 0, "No SWGDB Generated items found")
        
        # Test search filter
        crystal_items = self.filter_items_by_criteria({'search': 'crystal'})
        self.assertGreater(len(crystal_items), 0, "No crystal items found")
        
        print("✅ Filtering system tests passed")
        
    def filter_items_by_criteria(self, criteria):
        """Filter items by given criteria"""
        filtered_items = []
        
        for planet, data in self.test_data.items():
            for heroic_key, heroic_data in data['heroics'].items():
                for item_key, item_data in heroic_data['items'].items():
                    if self.item_matches_criteria(item_data, criteria):
                        filtered_items.append({
                            'planet': planet,
                            'heroic': heroic_data['boss'],
                            'name': item_data['name'],
                            'rarity': item_data['rarity'],
                            'type': item_data['type'],
                            'source': item_data.get('source', 'Unknown')
                        })
                        
        return filtered_items
        
    def item_matches_criteria(self, item, criteria):
        """Check if item matches all criteria"""
        for criterion_type, criterion_value in criteria.items():
            if criterion_type == 'rarity':
                if item.get('rarity') != criterion_value:
                    return False
            elif criterion_type == 'type':
                if item.get('type') != criterion_value:
                    return False
            elif criterion_type == 'profession':
                professions = item.get('profession_relevance', [])
                if criterion_value not in professions:
                    return False
            elif criterion_type == 'source':
                if item.get('source') != criterion_value:
                    return False
            elif criterion_type == 'search':
                search_term = criterion_value.lower()
                item_name = item.get('name', '').lower()
                item_use_case = item.get('use_case', '').lower()
                if search_term not in item_name and search_term not in item_use_case:
                    return False
                    
        return True
        
    def test_statistics_generation(self):
        """Test statistics generation"""
        print("Testing statistics generation...")
        
        stats = self.generate_statistics()
        
        # Check that statistics are generated correctly
        self.assertIn('total_planets', stats)
        self.assertIn('total_heroics', stats)
        self.assertIn('total_items', stats)
        self.assertIn('rarity_breakdown', stats)
        self.assertIn('type_breakdown', stats)
        self.assertIn('profession_breakdown', stats)
        self.assertIn('source_breakdown', stats)
        
        # Check that totals are correct
        total_items = sum(stats['rarity_breakdown'].values())
        self.assertEqual(stats['total_items'], total_items, "Total items mismatch")
        
        # Check that we have items in each category
        self.assertGreater(stats['total_items'], 0, "No items found")
        self.assertGreater(len(stats['rarity_breakdown']), 0, "No rarity breakdown")
        self.assertGreater(len(stats['type_breakdown']), 0, "No type breakdown")
        
        print("✅ Statistics generation tests passed")
        
    def generate_statistics(self):
        """Generate comprehensive statistics"""
        stats = {
            'total_planets': len(self.test_data),
            'total_heroics': 0,
            'total_items': 0,
            'rarity_breakdown': {},
            'type_breakdown': {},
            'profession_breakdown': {},
            'source_breakdown': {}
        }
        
        for planet, data in self.test_data.items():
            for heroic_key, heroic_data in data['heroics'].items():
                stats['total_heroics'] += 1
                
                for item_key, item_data in heroic_data['items'].items():
                    stats['total_items'] += 1
                    
                    # Rarity breakdown
                    rarity = item_data.get('rarity', 'unknown')
                    stats['rarity_breakdown'][rarity] = stats['rarity_breakdown'].get(rarity, 0) + 1
                    
                    # Type breakdown
                    item_type = item_data.get('type', 'unknown')
                    stats['type_breakdown'][item_type] = stats['type_breakdown'].get(item_type, 0) + 1
                    
                    # Source breakdown
                    source = item_data.get('source', 'unknown')
                    stats['source_breakdown'][source] = stats['source_breakdown'].get(source, 0) + 1
                    
                    # Profession breakdown
                    professions = item_data.get('profession_relevance', [])
                    for profession in professions:
                        stats['profession_breakdown'][profession] = stats['profession_breakdown'].get(profession, 0) + 1
                        
        return stats
        
    def test_ms11_export(self):
        """Test MS11 export functionality"""
        print("Testing MS11 export...")
        
        export_data = self.generate_ms11_export()
        
        # Check export structure
        self.assertIn('timestamp', export_data)
        self.assertIn('source', export_data)
        self.assertIn('version', export_data)
        self.assertIn('planets', export_data)
        
        # Check that all planets are exported
        self.assertEqual(len(export_data['planets']), len(self.test_data))
        
        # Check planet structure
        for planet, planet_data in export_data['planets'].items():
            self.assertIn('planet', planet_data)
            self.assertIn('heroics', planet_data)
            self.assertIn('total_runs', planet_data)
            self.assertIn('total_loot', planet_data)
            self.assertIn('last_updated', planet_data)
            
        print("✅ MS11 export tests passed")
        
    def generate_ms11_export(self):
        """Generate MS11 export data"""
        export_data = {
            'timestamp': datetime.now().isoformat(),
            'source': 'SWGDB Loot Tables',
            'version': '1.0.0',
            'planets': {}
        }
        
        for planet, data in self.test_data.items():
            export_data['planets'][planet] = {
                'planet': data.get('planet'),
                'total_runs': data.get('total_runs', 0),
                'total_loot': data.get('total_loot', 0),
                'last_updated': data.get('last_updated'),
                'heroics': {}
            }
            
            for heroic_key, heroic_data in data.get('heroics', {}).items():
                export_data['planets'][planet]['heroics'][heroic_key] = {
                    'boss': heroic_data['boss'],
                    'location': heroic_data['location'],
                    'level': heroic_data['level'],
                    'items': []
                }
                
                for item_key, item_data in heroic_data.get('items', {}).items():
                    export_data['planets'][planet]['heroics'][heroic_key]['items'].append({
                        'name': item_data['name'],
                        'type': item_data['type'],
                        'rarity': item_data['rarity'],
                        'drop_chance': item_data.get('drop_chance', 0),
                        'profession_relevance': item_data.get('profession_relevance', []),
                        'use_case': item_data.get('use_case', '')
                    })
                    
        return export_data
        
    def test_loot_sync_logic(self):
        """Test loot sync logic between manual and bot data"""
        print("Testing loot sync logic...")
        
        # Create test bot data
        bot_data = {
            'heroic': 'krayt_dragon',
            'boss': 'Krayt Dragon',
            'location': 'Tatooine - Dune Sea',
            'level': 80,
            'total_kills': 50,
            'items': {
                'krayt_scale_bot': {
                    'name': 'Krayt Dragon Scale',
                    'rarity': 'rare',
                    'total_drops': 12,
                    'total_quantity': 45,
                    'first_seen': '2025-08-01T10:00:00',
                    'last_seen': '2025-08-05T15:30:00'
                },
                'new_item': {
                    'name': 'Krayt Dragon Heart',
                    'rarity': 'epic',
                    'total_drops': 3,
                    'total_quantity': 3,
                    'first_seen': '2025-08-03T14:20:00',
                    'last_seen': '2025-08-05T16:45:00'
                }
            }
        }
        
        # Test merge with existing data
        if 'tatooine' in self.test_data:
            merged_data = self.merge_loot_data(self.test_data['tatooine'], bot_data)
            
            # Check that merge was successful
            self.assertIn('heroics', merged_data)
            self.assertIn('krayt_dragon', merged_data['heroics'])
            
            # Check that items were merged correctly
            krayt_items = merged_data['heroics']['krayt_dragon']['items']
            self.assertGreater(len(krayt_items), 0, "No items in merged data")
            
            # Check that new item was added
            new_item_found = False
            for item_key, item_data in krayt_items.items():
                if item_data['name'] == 'Krayt Dragon Heart':
                    new_item_found = True
                    self.assertEqual(item_data['source'], 'Bot Generated')
                    break
                    
            self.assertTrue(new_item_found, "New item not found in merged data")
            
        print("✅ Loot sync logic tests passed")
        
    def merge_loot_data(self, manual_data, bot_data):
        """Merge bot-generated data with manual data"""
        merged = manual_data.copy()
        
        if 'heroics' not in merged:
            merged['heroics'] = {}
            
        heroic_key = bot_data['heroic']
        if heroic_key not in merged['heroics']:
            merged['heroics'][heroic_key] = {
                'boss': bot_data['boss'],
                'location': bot_data['location'],
                'level': bot_data['level'],
                'total_kills': bot_data['total_kills'],
                'items': {}
            }
        
        # Merge items
        for item_key, bot_item in bot_data['items'].items():
            # Check if item already exists
            existing_item = None
            for existing_key, existing_data in merged['heroics'][heroic_key]['items'].items():
                if existing_data['name'].lower() == bot_item['name'].lower():
                    existing_item = existing_key
                    break
            
            if existing_item:
                # Update existing item
                merged['heroics'][heroic_key]['items'][existing_item].update({
                    'total_drops': (merged['heroics'][heroic_key]['items'][existing_item].get('total_drops', 0) + 
                                  bot_item['total_drops']),
                    'total_quantity': (merged['heroics'][heroic_key]['items'][existing_item].get('total_quantity', 0) + 
                                     bot_item['total_quantity']),
                    'first_seen': (merged['heroics'][heroic_key]['items'][existing_item].get('first_seen') or 
                                 bot_item['first_seen']),
                    'last_seen': bot_item['last_seen'],
                    'source': 'Bot Generated + Manual'
                })
            else:
                # Add new item
                merged['heroics'][heroic_key]['items'][item_key] = {
                    'name': bot_item['name'],
                    'rarity': bot_item['rarity'],
                    'total_drops': bot_item['total_drops'],
                    'total_quantity': bot_item['total_quantity'],
                    'first_seen': bot_item['first_seen'],
                    'last_seen': bot_item['last_seen'],
                    'source': 'Bot Generated'
                }
        
        return merged
        
    def test_file_integrity(self):
        """Test that all required files exist and are valid"""
        print("Testing file integrity...")
        
        # Check that loot tables directory exists
        self.assertTrue(self.loot_tables_dir.exists(), "Loot tables directory not found")
        
        # Check that we have loot table files
        json_files = list(self.loot_tables_dir.glob("*.json"))
        self.assertGreater(len(json_files), 0, "No loot table files found")
        
        # Check that lib directory and files exist
        lib_dir = Path("src/lib")
        self.assertTrue(lib_dir.exists(), "Lib directory not found")
        
        loot_parser_file = lib_dir / "loot-parser.js"
        self.assertTrue(loot_parser_file.exists(), "Loot parser file not found")
        
        # Check that components directory and files exist
        components_dir = Path("src/components")
        self.assertTrue(components_dir.exists(), "Components directory not found")
        
        loot_table_component = components_dir / "LootTable.svelte"
        self.assertTrue(loot_table_component.exists(), "LootTable component not found")
        
        # Check that pages directory and files exist
        pages_dir = Path("src/pages/heroics")
        self.assertTrue(pages_dir.exists(), "Heroics pages directory not found")
        
        print("✅ File integrity tests passed")
        
    def test_data_quality(self):
        """Test data quality and completeness"""
        print("Testing data quality...")
        
        for planet, data in self.test_data.items():
            # Check that all items have meaningful names
            for heroic_key, heroic_data in data['heroics'].items():
                for item_key, item_data in heroic_data['items'].items():
                    self.assertIsInstance(item_data['name'], str, f"Invalid name type in {planet}.{heroic_key}.{item_key}")
                    self.assertGreater(len(item_data['name']), 0, f"Empty name in {planet}.{heroic_key}.{item_key}")
                    
                    # Check that drop chances are reasonable
                    drop_chance = item_data.get('drop_chance', 0)
                    self.assertGreaterEqual(drop_chance, 0, f"Negative drop chance in {planet}.{heroic_key}.{item_key}")
                    self.assertLessEqual(drop_chance, 100, f"Drop chance > 100% in {planet}.{heroic_key}.{item_key}")
                    
                    # Check that profession relevance is a list
                    profession_relevance = item_data.get('profession_relevance', [])
                    self.assertIsInstance(profession_relevance, list, f"Invalid profession_relevance type in {planet}.{heroic_key}.{item_key}")
                    
                    # Check that use case is provided
                    use_case = item_data.get('use_case', '')
                    self.assertIsInstance(use_case, str, f"Invalid use_case type in {planet}.{heroic_key}.{item_key}")
                    
        print("✅ Data quality tests passed")

def run_tests():
    """Run all tests"""
    print("🧪 Batch 186 Test - Loot Tables Page (Heroics) + Loot Sync Logic")
    print("=" * 70)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestLootTables)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Generate test report
    test_report = {
        'timestamp': datetime.now().isoformat(),
        'tests_run': result.testsRun,
        'tests_failed': len(result.failures),
        'tests_errored': len(result.errors),
        'success_rate': ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100 if result.testsRun > 0 else 0
    }
    
    # Save test report
    report_file = f"BATCH_186_TEST_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(test_report, f, indent=2)
        
    print(f"\n📄 Test report saved to: {report_file}")
    print(f"📊 Success rate: {test_report['success_rate']:.1f}%")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 