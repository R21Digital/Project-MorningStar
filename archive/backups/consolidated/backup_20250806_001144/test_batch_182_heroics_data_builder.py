#!/usr/bin/env python3
"""
Test suite for Batch 182 - Public-Side Heroics Page Data Builder (Phase 1)
Objective: Test the heroics data structure, YAML files, and website integration
"""

import unittest
import yaml
import json
import os
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import patch, mock_open, MagicMock

class TestHeroicsDataStructure(unittest.TestCase):
    """Test the heroics data structure and YAML files"""
    
    def setUp(self):
        self.website_data_dir = Path("website/data/heroics")
        self.required_fields = [
            'name', 'slug', 'location', 'planet', 'level_requirement',
            'faction', 'group_size', 'difficulty', 'description',
            'bosses', 'loot_tables', 'strategies', 'requirements',
            'tips', 'related_content', 'last_updated', 'data_source'
        ]
        
    def test_directory_structure_exists(self):
        """Test that the heroics data directory exists"""
        self.assertTrue(self.website_data_dir.exists(), 
                       "Heroics data directory should exist")
        
    def test_yaml_files_exist(self):
        """Test that the required YAML files exist"""
        expected_files = ["axkva-min.yml", "ig-88.yml", "tusken-army.yml"]
        
        for filename in expected_files:
            file_path = self.website_data_dir / filename
            self.assertTrue(file_path.exists(), 
                          f"YAML file {filename} should exist")
            
    def test_yaml_structure_validation(self):
        """Test that all YAML files have the required structure"""
        for yaml_file in self.website_data_dir.glob("*.yml"):
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                
            # Check required fields
            for field in self.required_fields:
                self.assertIn(field, data, 
                            f"Field '{field}' missing in {yaml_file.name}")
                
            # Check data types
            self.assertIsInstance(data['name'], str)
            self.assertIsInstance(data['slug'], str)
            self.assertIsInstance(data['level_requirement'], int)
            self.assertIsInstance(data['bosses'], list)
            self.assertIsInstance(data['loot_tables'], dict)
            self.assertIsInstance(data['strategies'], dict)
            self.assertIsInstance(data['requirements'], list)
            self.assertIsInstance(data['tips'], list)
            
    def test_boss_structure_validation(self):
        """Test that boss data has the correct structure"""
        boss_required_fields = ['name', 'level', 'type', 'health', 'abilities', 'tactics', 'loot_table']
        
        for yaml_file in self.website_data_dir.glob("*.yml"):
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                
            for boss in data['bosses']:
                for field in boss_required_fields:
                    self.assertIn(field, boss, 
                                f"Boss field '{field}' missing in {yaml_file.name}")
                    
                # Check data types
                self.assertIsInstance(boss['name'], str)
                self.assertIsInstance(boss['level'], int)
                self.assertIsInstance(boss['abilities'], list)
                self.assertIsInstance(boss['tactics'], list)
                
    def test_loot_table_structure_validation(self):
        """Test that loot table data has the correct structure"""
        for yaml_file in self.website_data_dir.glob("*.yml"):
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                
            for table_name, table_data in data['loot_tables'].items():
                self.assertIn('guaranteed', table_data)
                self.assertIn('random', table_data)
                self.assertIsInstance(table_data['guaranteed'], list)
                self.assertIsInstance(table_data['random'], list)
                
                # Check item structure
                for item in table_data['guaranteed'] + table_data['random']:
                    self.assertIn('item', item)
                    self.assertIn('rarity', item)
                    self.assertIn('slot', item)
                    
                    if 'drop_rate' in item:
                        self.assertIsInstance(item['drop_rate'], (int, float))
                        self.assertGreaterEqual(item['drop_rate'], 0)
                        self.assertLessEqual(item['drop_rate'], 1)

class TestWebsiteIntegration(unittest.TestCase):
    """Test the website integration files"""
    
    def setUp(self):
        self.heroics_page = Path("website/pages/heroics.11ty.js")
        self.heroic_detail = Path("website/components/HeroicDetail.tsx")
        
    def test_heroics_page_exists(self):
        """Test that the heroics page exists"""
        self.assertTrue(self.heroics_page.exists(), 
                       "Heroics page should exist")
        
    def test_heroics_page_structure(self):
        """Test that the heroics page has the correct structure"""
        with open(self.heroics_page, 'r') as f:
            content = f.read()
            
        # Check for required elements
        self.assertIn("layout", content)
        self.assertIn("title", content)
        self.assertIn("heroics", content)
        self.assertIn("eleventyComputed", content)
        
    def test_heroic_detail_component_exists(self):
        """Test that the HeroicDetail component exists"""
        self.assertTrue(self.heroic_detail.exists(), 
                       "HeroicDetail component should exist")
        
    def test_heroic_detail_typescript_interfaces(self):
        """Test that the HeroicDetail component has TypeScript interfaces"""
        with open(self.heroic_detail, 'r') as f:
            content = f.read()
            
        # Check for TypeScript interfaces
        self.assertIn("interface", content)
        self.assertIn("HeroicData", content)
        self.assertIn("Boss", content)
        self.assertIn("LootItem", content)
        
    def test_heroic_detail_functionality(self):
        """Test that the HeroicDetail component has required functionality"""
        with open(self.heroic_detail, 'r') as f:
            content = f.read()
            
        # Check for required functions
        self.assertIn("getRarityColor", content)
        self.assertIn("loot_tables", content)
        self.assertIn("bosses", content)
        self.assertIn("strategies", content)

class TestDataValidation(unittest.TestCase):
    """Test data validation and integrity"""
    
    def setUp(self):
        self.website_data_dir = Path("website/data/heroics")
        
    def test_yaml_syntax_validity(self):
        """Test that all YAML files have valid syntax"""
        for yaml_file in self.website_data_dir.glob("*.yml"):
            with open(yaml_file, 'r') as f:
                try:
                    yaml.safe_load(f)
                except yaml.YAMLError as e:
                    self.fail(f"Invalid YAML syntax in {yaml_file.name}: {e}")
                    
    def test_data_consistency(self):
        """Test data consistency across files"""
        heroic_names = set()
        slugs = set()
        
        for yaml_file in self.website_data_dir.glob("*.yml"):
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                
            # Check for unique names and slugs
            self.assertNotIn(data['name'], heroic_names, 
                           f"Duplicate heroic name: {data['name']}")
            self.assertNotIn(data['slug'], slugs, 
                           f"Duplicate slug: {data['slug']}")
            
            heroic_names.add(data['name'])
            slugs.add(data['slug'])
            
    def test_level_requirements_validity(self):
        """Test that level requirements are reasonable"""
        for yaml_file in self.website_data_dir.glob("*.yml"):
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                
            level = data['level_requirement']
            self.assertGreaterEqual(level, 1, 
                                  f"Level requirement should be >= 1 in {yaml_file.name}")
            self.assertLessEqual(level, 90, 
                               f"Level requirement should be <= 90 in {yaml_file.name}")
            
    def test_difficulty_values(self):
        """Test that difficulty values are valid"""
        valid_difficulties = ['Easy', 'Medium', 'Hard', 'Very Hard']
        
        for yaml_file in self.website_data_dir.glob("*.yml"):
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                
            difficulty = data['difficulty']
            self.assertIn(difficulty, valid_difficulties, 
                         f"Invalid difficulty '{difficulty}' in {yaml_file.name}")

class TestLootTableValidation(unittest.TestCase):
    """Test loot table validation and structure"""
    
    def setUp(self):
        self.website_data_dir = Path("website/data/heroics")
        self.valid_rarities = ['Common', 'Uncommon', 'Rare', 'Epic', 'Legendary']
        self.valid_slots = ['Weapon', 'Armor', 'Head', 'Chest', 'Legs', 'Feet', 
                           'Hands', 'Neck', 'Back', 'Utility', 'Material', 'Consumable', 'Schematic']
        
    def test_loot_table_rarity_validation(self):
        """Test that loot table rarities are valid"""
        for yaml_file in self.website_data_dir.glob("*.yml"):
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                
            for table_name, table_data in data['loot_tables'].items():
                for item in table_data['guaranteed'] + table_data['random']:
                    rarity = item['rarity']
                    self.assertIn(rarity, self.valid_rarities, 
                                f"Invalid rarity '{rarity}' in {yaml_file.name}")
                    
    def test_loot_table_slot_validation(self):
        """Test that loot table slots are valid"""
        for yaml_file in self.website_data_dir.glob("*.yml"):
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                
            for table_name, table_data in data['loot_tables'].items():
                for item in table_data['guaranteed'] + table_data['random']:
                    slot = item['slot']
                    self.assertIn(slot, self.valid_slots, 
                                f"Invalid slot '{slot}' in {yaml_file.name}")
                    
    def test_drop_rate_validation(self):
        """Test that drop rates are valid percentages"""
        for yaml_file in self.website_data_dir.glob("*.yml"):
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                
            for table_name, table_data in data['loot_tables'].items():
                for item in table_data['random']:
                    if 'drop_rate' in item:
                        drop_rate = item['drop_rate']
                        self.assertGreaterEqual(drop_rate, 0, 
                                             f"Drop rate should be >= 0 in {yaml_file.name}")
                        self.assertLessEqual(drop_rate, 1, 
                                          f"Drop rate should be <= 1 in {yaml_file.name}")

class TestStrategyValidation(unittest.TestCase):
    """Test strategy validation and structure"""
    
    def setUp(self):
        self.website_data_dir = Path("website/data/heroics")
        
    def test_strategy_structure_validation(self):
        """Test that strategy data has the correct structure"""
        for yaml_file in self.website_data_dir.glob("*.yml"):
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                
            strategies = data['strategies']
            
            # Check for general strategies
            self.assertIn('general', strategies)
            self.assertIsInstance(strategies['general'], list)
            self.assertGreater(len(strategies['general']), 0)
            
            # Check for phase strategies
            phase_strategies = {k: v for k, v in strategies.items() if k.startswith('phase_')}
            self.assertGreater(len(phase_strategies), 0)
            
            for phase_name, phase_data in phase_strategies.items():
                self.assertIn('name', phase_data)
                self.assertIn('description', phase_data)
                self.assertIn('tactics', phase_data)
                self.assertIsInstance(phase_data['tactics'], list)
                self.assertGreater(len(phase_data['tactics']), 0)
                
    def test_tactics_content_validation(self):
        """Test that tactics have meaningful content"""
        for yaml_file in self.website_data_dir.glob("*.yml"):
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                
            strategies = data['strategies']
            
            # Check general tactics
            for tactic in strategies['general']:
                self.assertIsInstance(tactic, str)
                self.assertGreater(len(tactic.strip()), 0)
                
            # Check phase tactics
            phase_strategies = {k: v for k, v in strategies.items() if k.startswith('phase_')}
            for phase_data in phase_strategies.values():
                for tactic in phase_data['tactics']:
                    self.assertIsInstance(tactic, str)
                    self.assertGreater(len(tactic.strip()), 0)

class TestBossValidation(unittest.TestCase):
    """Test boss validation and structure"""
    
    def setUp(self):
        self.website_data_dir = Path("website/data/heroics")
        
    def test_boss_level_validation(self):
        """Test that boss levels are reasonable"""
        for yaml_file in self.website_data_dir.glob("*.yml"):
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                
            for boss in data['bosses']:
                level = boss['level']
                self.assertGreaterEqual(level, 1, 
                                      f"Boss level should be >= 1 in {yaml_file.name}")
                self.assertLessEqual(level, 90, 
                                   f"Boss level should be <= 90 in {yaml_file.name}")
                
    def test_boss_abilities_validation(self):
        """Test that boss abilities have meaningful content"""
        for yaml_file in self.website_data_dir.glob("*.yml"):
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                
            for boss in data['bosses']:
                abilities = boss['abilities']
                self.assertGreater(len(abilities), 0, 
                                 f"Boss should have at least one ability in {yaml_file.name}")
                
                for ability in abilities:
                    self.assertIsInstance(ability, str)
                    self.assertGreater(len(ability.strip()), 0)
                    
    def test_boss_tactics_validation(self):
        """Test that boss tactics have meaningful content"""
        for yaml_file in self.website_data_dir.glob("*.yml"):
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                
            for boss in data['bosses']:
                tactics = boss['tactics']
                self.assertGreater(len(tactics), 0, 
                                 f"Boss should have at least one tactic in {yaml_file.name}")
                
                for tactic in tactics:
                    self.assertIsInstance(tactic, str)
                    self.assertGreater(len(tactic.strip()), 0)

class TestIntegration(unittest.TestCase):
    """Test overall integration and functionality"""
    
    def setUp(self):
        self.website_data_dir = Path("website/data/heroics")
        
    def test_phase_1_completion(self):
        """Test that Phase 1 requirements are met"""
        # Check directory structure
        self.assertTrue(self.website_data_dir.exists())
        
        # Check YAML files
        yaml_files = list(self.website_data_dir.glob("*.yml"))
        self.assertGreaterEqual(len(yaml_files), 3)
        
        # Check specific files
        expected_files = ["axkva-min.yml", "ig-88.yml", "tusken-army.yml"]
        for filename in expected_files:
            file_path = self.website_data_dir / filename
            self.assertTrue(file_path.exists())
            
        # Check website files
        heroics_page = Path("website/pages/heroics.11ty.js")
        heroic_detail = Path("website/components/HeroicDetail.tsx")
        
        self.assertTrue(heroics_page.exists())
        self.assertTrue(heroic_detail.exists())
        
    def test_data_quality(self):
        """Test overall data quality"""
        total_bosses = 0
        total_loot_tables = 0
        total_strategies = 0
        
        for yaml_file in self.website_data_dir.glob("*.yml"):
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
                
            total_bosses += len(data['bosses'])
            total_loot_tables += len(data['loot_tables'])
            total_strategies += len(data['strategies'])
            
        # Ensure we have substantial content
        self.assertGreaterEqual(total_bosses, 3)
        self.assertGreaterEqual(total_loot_tables, 3)
        self.assertGreaterEqual(total_strategies, 3)
        
    def test_future_ms11_integration_points(self):
        """Test that integration points for future MS11 data exist"""
        # Check for MS11 data directories
        ms11_dirs = [
            Path("data/heroics"),
            Path("data/loot_tables"),
            Path("data/combat_feedback")
        ]
        
        # At least some MS11 data should exist
        existing_dirs = [d for d in ms11_dirs if d.exists()]
        self.assertGreater(len(existing_dirs), 0, 
                          "At least one MS11 data directory should exist")
        
    def test_website_component_functionality(self):
        """Test that website components are functional"""
        heroic_detail = Path("website/components/HeroicDetail.tsx")
        
        with open(heroic_detail, 'r') as f:
            content = f.read()
            
        # Check for essential functionality
        self.assertIn("interface HeroicData", content)
        self.assertIn("getRarityColor", content)
        self.assertIn("loot_tables", content)
        self.assertIn("bosses", content)
        self.assertIn("strategies", content)
        
        # Check for React component structure
        self.assertIn("React.FC", content)
        self.assertIn("export default", content)

if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestHeroicsDataStructure,
        TestWebsiteIntegration,
        TestDataValidation,
        TestLootTableValidation,
        TestStrategyValidation,
        TestBossValidation,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
        
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print("BATCH 182 TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.wasSuccessful():
        print("🎉 All tests passed! Batch 182 implementation is successful.")
    else:
        print("❌ Some tests failed. Please review the implementation.")
        
    print(f"{'='*60}") 