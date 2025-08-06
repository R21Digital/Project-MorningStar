#!/usr/bin/env python3
"""
Test suite for Batch 183 - Heroics Loot Table Integration with MS11
Objective: Test the loot tracking system for rare item drops and SWGDB integration
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime
from typing import Dict, List, Any

# Mock imports for testing
class MockLogger:
    def info(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): pass

class MockLicenseHook:
    def __call__(self, func):
        return func

# Mock the imports
import sys
sys.modules['utils.license_hooks'] = type('MockModule', (), {'requires_license': MockLicenseHook()})
sys.modules['profession_logic.utils.logger'] = type('MockModule', (), {'logger': MockLogger()})

from src.ms11.combat.loot_tracker import LootTracker, LootDrop, LootRarity, LootDrop, HeroicLootData

class TestLootRarity(unittest.TestCase):
    """Test loot rarity enumeration"""
    
    def test_rarity_values(self):
        """Test that rarity values are correct"""
        self.assertEqual(LootRarity.COMMON.value, "common")
        self.assertEqual(LootRarity.UNCOMMON.value, "uncommon")
        self.assertEqual(LootRarity.RARE.value, "rare")
        self.assertEqual(LootRarity.EPIC.value, "epic")
        self.assertEqual(LootRarity.LEGENDARY.value, "legendary")
    
    def test_rarity_count(self):
        """Test that all rarity levels are defined"""
        self.assertEqual(len(LootRarity), 5)

class TestLootDrop(unittest.TestCase):
    """Test loot drop data structure"""
    
    def test_loot_drop_creation(self):
        """Test creating a loot drop"""
        drop = LootDrop(
            item_name="Test Item",
            rarity="rare",
            heroic_name="Test Heroic",
            boss_name="Test Boss",
            character_name="TestPlayer",
            timestamp="2024-01-01T00:00:00Z",
            location="Test Location"
        )
        
        self.assertEqual(drop.item_name, "Test Item")
        self.assertEqual(drop.rarity, "rare")
        self.assertEqual(drop.heroic_name, "Test Heroic")
        self.assertEqual(drop.boss_name, "Test Boss")
        self.assertEqual(drop.character_name, "TestPlayer")
        self.assertEqual(drop.location, "Test Location")
    
    def test_loot_drop_optional_fields(self):
        """Test loot drop with optional fields"""
        drop = LootDrop(
            item_name="Test Item",
            rarity="rare",
            heroic_name="Test Heroic",
            boss_name="Test Boss",
            character_name="TestPlayer",
            timestamp="2024-01-01T00:00:00Z",
            location="Test Location",
            instance_id="test-instance-123",
            drop_rate=0.05
        )
        
        self.assertEqual(drop.instance_id, "test-instance-123")
        self.assertEqual(drop.drop_rate, 0.05)

class TestLootTracker(unittest.TestCase):
    """Test the main loot tracker class"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "loot_targets.json"
        self.loot_file_path = Path(self.temp_dir) / "heroics_loot.json"
        
        # Create test config
        self.test_config = {
            "tracking_enabled": True,
            "specific_items": ["Test Item", "Rare Item"],
            "excluded_items": ["Common Item"],
            "rarity_levels": {
                "common": False,
                "uncommon": True,
                "rare": True,
                "epic": True,
                "legendary": True
            },
            "tracking_settings": {
                "log_all_drops": False,
                "log_rare_only": True,
                "include_timestamp": True,
                "include_character": True,
                "include_location": True,
                "include_boss": True
            }
        }
        
        # Create test loot data
        self.test_loot_data = {
            "metadata": {
                "version": "1.0",
                "last_updated": "2024-01-01T00:00:00Z",
                "total_drops": 0,
                "data_source": "MS11 Loot Tracker"
            },
            "heroics": {
                "test-heroic": {
                    "name": "Test Heroic",
                    "location": "Test Location",
                    "bosses": {
                        "test-boss": {
                            "name": "Test Boss",
                            "drops": []
                        }
                    },
                    "total_drops": 0,
                    "last_drop": None
                }
            },
            "characters": {},
            "statistics": {
                "total_drops": 0,
                "unique_items": 0,
                "rarest_drops": [],
                "most_active_heroic": None,
                "most_active_character": None
            }
        }
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('builtins.open', new_callable=mock_open)
    def test_loot_tracker_initialization(self, mock_file):
        """Test loot tracker initialization"""
        # Mock file reading
        mock_file.return_value.__enter__.return_value.read.return_value = json.dumps(self.test_config)
        
        tracker = LootTracker(str(self.config_path), str(self.loot_file_path))
        
        self.assertIsNotNone(tracker)
        self.assertEqual(tracker.config_path, self.config_path)
        self.assertEqual(tracker.loot_file, self.loot_file_path)
        self.assertTrue(tracker.config.get("tracking_enabled"))
    
    def test_parse_loot_message_success(self):
        """Test successful loot message parsing"""
        tracker = LootTracker()
        tracker.config = self.test_config
        
        message = "You loot Test Item from Test Boss."
        loot_drop = tracker.parse_loot_message(message)
        
        self.assertIsNotNone(loot_drop)
        self.assertEqual(loot_drop.item_name, "Test Item")
        self.assertEqual(loot_drop.boss_name, "Test Boss")
    
    def test_parse_loot_message_failure(self):
        """Test loot message parsing failure"""
        tracker = LootTracker()
        tracker.config = self.test_config
        
        message = "You receive Common Item from Test Boss."
        loot_drop = tracker.parse_loot_message(message)
        
        # Should not track excluded items
        self.assertIsNone(loot_drop)
    
    def test_parse_loot_message_patterns(self):
        """Test different loot message patterns"""
        tracker = LootTracker()
        tracker.config = self.test_config
        
        patterns = [
            "You loot Test Item from Test Boss.",
            "You receive Test Item from Test Boss.",
            "You found Test Item in Test Boss.",
            "Test Item was added to your inventory from Test Boss."
        ]
        
        for pattern in patterns:
            loot_drop = tracker.parse_loot_message(pattern)
            self.assertIsNotNone(loot_drop, f"Failed to parse: {pattern}")
            self.assertEqual(loot_drop.item_name, "Test Item")
    
    def test_should_track_item(self):
        """Test item tracking logic"""
        tracker = LootTracker()
        tracker.config = self.test_config
        
        # Test specific items
        self.assertTrue(tracker._should_track_item("Test Item"))
        self.assertTrue(tracker._should_track_item("Rare Item"))
        
        # Test excluded items
        self.assertFalse(tracker._should_track_item("Common Item"))
        
        # Test rare keywords
        self.assertTrue(tracker._should_track_item("Rare Crystal"))
        self.assertTrue(tracker._should_track_item("Epic Robe"))
        self.assertTrue(tracker._should_track_item("Legendary Artifact"))
    
    def test_determine_rarity(self):
        """Test rarity determination"""
        tracker = LootTracker()
        
        self.assertEqual(tracker._determine_rarity("Legendary Artifact"), "legendary")
        self.assertEqual(tracker._determine_rarity("Epic Crystal"), "epic")
        self.assertEqual(tracker._determine_rarity("Rare Robe"), "rare")
        self.assertEqual(tracker._determine_rarity("Uncommon Item"), "uncommon")
        self.assertEqual(tracker._determine_rarity("Common Item"), "common")
    
    def test_extract_heroic_from_source(self):
        """Test heroic extraction from source"""
        tracker = LootTracker()
        
        self.assertEqual(tracker._extract_heroic_from_source("Axkva Min"), "axkva-min")
        self.assertEqual(tracker._extract_heroic_from_source("IG-88"), "ig-88")
        self.assertEqual(tracker._extract_heroic_from_source("Tusken Chieftain"), "tusken-army")
        self.assertEqual(tracker._extract_heroic_from_source("Unknown Boss"), "unknown")
    
    def test_extract_boss_from_source(self):
        """Test boss extraction from source"""
        tracker = LootTracker()
        
        self.assertEqual(tracker._extract_boss_from_source("Axkva Min"), "axkva-min")
        self.assertEqual(tracker._extract_boss_from_source("IG-88"), "ig-88")
        self.assertEqual(tracker._extract_boss_from_source("Tusken Chieftain"), "tusken-chieftain")
        self.assertEqual(tracker._extract_boss_from_source("Unknown Boss"), "unknown")
    
    def test_set_current_context(self):
        """Test setting current context"""
        tracker = LootTracker()
        
        tracker.set_current_context(
            heroic="Test Heroic",
            boss="Test Boss",
            character="TestPlayer",
            location="Test Location"
        )
        
        self.assertEqual(tracker.current_heroic, "Test Heroic")
        self.assertEqual(tracker.current_boss, "Test Boss")
        self.assertEqual(tracker.current_character, "TestPlayer")
        self.assertEqual(tracker.current_location, "Test Location")
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.exists')
    def test_record_loot_drop(self, mock_exists, mock_file):
        """Test recording a loot drop"""
        mock_exists.return_value = True
        mock_file.return_value.__enter__.return_value.read.return_value = json.dumps(self.test_loot_data)
        
        tracker = LootTracker(str(self.config_path), str(self.loot_file_path))
        tracker.loot_data = self.test_loot_data
        
        loot_drop = LootDrop(
            item_name="Test Item",
            rarity="rare",
            heroic_name="Test Heroic",
            boss_name="Test Boss",
            character_name="TestPlayer",
            timestamp="2024-01-01T00:00:00Z",
            location="Test Location"
        )
        
        tracker.record_loot_drop(loot_drop)
        
        # Check that drop was recorded
        heroic_key = "test-heroic"
        boss_key = "test-boss"
        
        self.assertIn(heroic_key, tracker.loot_data["heroics"])
        self.assertIn(boss_key, tracker.loot_data["heroics"][heroic_key]["bosses"])
        self.assertEqual(tracker.loot_data["heroics"][heroic_key]["total_drops"], 1)
        self.assertEqual(tracker.loot_data["statistics"]["total_drops"], 1)
    
    def test_process_loot_message(self):
        """Test processing loot messages"""
        tracker = LootTracker()
        tracker.config = self.test_config
        
        # Test successful processing
        message = "You loot Test Item from Test Boss."
        success = tracker.process_loot_message(message)
        self.assertTrue(success)
        
        # Test unsuccessful processing
        message = "You loot Common Item from Test Boss."
        success = tracker.process_loot_message(message)
        self.assertFalse(success)
    
    def test_get_loot_statistics(self):
        """Test getting loot statistics"""
        tracker = LootTracker()
        tracker.loot_data = self.test_loot_data
        
        stats = tracker.get_loot_statistics()
        
        self.assertIn("total_drops", stats)
        self.assertIn("unique_items", stats)
        self.assertIn("most_active_heroic", stats)
        self.assertIn("most_active_character", stats)
        self.assertIn("heroics_count", stats)
        self.assertIn("characters_count", stats)
    
    def test_get_heroic_drops(self):
        """Test getting drops for a specific heroic"""
        tracker = LootTracker()
        tracker.loot_data = self.test_loot_data
        
        # Add a test drop
        test_drop = {
            "item_name": "Test Item",
            "rarity": "rare",
            "heroic_name": "Test Heroic",
            "boss_name": "Test Boss",
            "character_name": "TestPlayer",
            "timestamp": "2024-01-01T00:00:00Z",
            "location": "Test Location"
        }
        
        tracker.loot_data["heroics"]["test-heroic"]["bosses"]["test-boss"]["drops"].append(test_drop)
        
        drops = tracker.get_heroic_drops("Test Heroic")
        self.assertEqual(len(drops), 1)
        self.assertEqual(drops[0]["item_name"], "Test Item")
    
    def test_get_character_drops(self):
        """Test getting drops for a specific character"""
        tracker = LootTracker()
        tracker.loot_data = self.test_loot_data
        
        # Add character data
        tracker.loot_data["characters"]["TestPlayer"] = {
            "drops": [],
            "total_drops": 0,
            "last_drop": None
        }
        
        # Add a test drop
        test_drop = {
            "item_name": "Test Item",
            "rarity": "rare",
            "heroic_name": "Test Heroic",
            "boss_name": "Test Boss",
            "character_name": "TestPlayer",
            "timestamp": "2024-01-01T00:00:00Z",
            "location": "Test Location"
        }
        
        tracker.loot_data["characters"]["TestPlayer"]["drops"].append(test_drop)
        
        drops = tracker.get_character_drops("TestPlayer")
        self.assertEqual(len(drops), 1)
        self.assertEqual(drops[0]["item_name"], "Test Item")

class TestGlobalFunctions(unittest.TestCase):
    """Test global functions"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "loot_targets.json"
        self.loot_file_path = Path(self.temp_dir) / "heroics_loot.json"
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('src.ms11.combat.loot_tracker.loot_tracker')
    def test_process_loot_message_global(self, mock_tracker):
        """Test global process_loot_message function"""
        from src.ms11.combat.loot_tracker import process_loot_message
        
        mock_tracker.process_loot_message.return_value = True
        
        result = process_loot_message("You loot Test Item from Test Boss.")
        self.assertTrue(result)
        mock_tracker.process_loot_message.assert_called_once_with("You loot Test Item from Test Boss.")
    
    @patch('src.ms11.combat.loot_tracker.loot_tracker')
    def test_set_loot_context_global(self, mock_tracker):
        """Test global set_loot_context function"""
        from src.ms11.combat.loot_tracker import set_loot_context
        
        set_loot_context(heroic="Test Heroic", boss="Test Boss")
        mock_tracker.set_current_context.assert_called_once_with(heroic="Test Heroic", boss="Test Boss")
    
    @patch('src.ms11.combat.loot_tracker.loot_tracker')
    def test_get_loot_statistics_global(self, mock_tracker):
        """Test global get_loot_statistics function"""
        from src.ms11.combat.loot_tracker import get_loot_statistics
        
        expected_stats = {"total_drops": 10, "unique_items": 5}
        mock_tracker.get_loot_statistics.return_value = expected_stats
        
        stats = get_loot_statistics()
        self.assertEqual(stats, expected_stats)
        mock_tracker.get_loot_statistics.assert_called_once()

class TestIntegration(unittest.TestCase):
    """Test integration scenarios"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "loot_targets.json"
        self.loot_file_path = Path(self.temp_dir) / "heroics_loot.json"
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.exists')
    def test_full_loot_tracking_workflow(self, mock_exists, mock_file):
        """Test complete loot tracking workflow"""
        # Mock file operations
        mock_exists.return_value = True
        mock_file.return_value.__enter__.return_value.read.return_value = "{}"
        
        tracker = LootTracker(str(self.config_path), str(self.loot_file_path))
        
        # Set context
        tracker.set_current_context(
            heroic="Axkva Min",
            boss="Axkva Min",
            character="TestPlayer",
            location="Dathomir"
        )
        
        # Process loot messages
        messages = [
            "You loot Nightsister Robe from Axkva Min.",
            "You receive Force Crystal from Axkva Min.",
            "You found Dark Side Artifact from Axkva Min."
        ]
        
        for message in messages:
            success = tracker.process_loot_message(message)
            self.assertTrue(success)
        
        # Check statistics
        stats = tracker.get_loot_statistics()
        self.assertEqual(stats["total_drops"], 3)
        self.assertEqual(stats["unique_items"], 3)
        self.assertEqual(stats["heroics_count"], 1)
        self.assertEqual(stats["characters_count"], 1)
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.exists')
    def test_multiple_heroics_tracking(self, mock_exists, mock_file):
        """Test tracking across multiple heroics"""
        # Mock file operations
        mock_exists.return_value = True
        mock_file.return_value.__enter__.return_value.read.return_value = "{}"
        
        tracker = LootTracker(str(self.config_path), str(self.loot_file_path))
        
        # Test Axkva Min
        tracker.set_current_context(heroic="Axkva Min", boss="Axkva Min", character="Player1")
        tracker.process_loot_message("You loot Nightsister Robe from Axkva Min.")
        
        # Test IG-88
        tracker.set_current_context(heroic="IG-88", boss="IG-88", character="Player2")
        tracker.process_loot_message("You loot Bounty Hunter Rifle from IG-88.")
        
        # Test Tusken Army
        tracker.set_current_context(heroic="Tusken Army", boss="Tusken Chieftain", character="Player3")
        tracker.process_loot_message("You loot Tusken Raider Armor from Tusken Chieftain.")
        
        # Check statistics
        stats = tracker.get_loot_statistics()
        self.assertEqual(stats["total_drops"], 3)
        self.assertEqual(stats["heroics_count"], 3)
        self.assertEqual(stats["characters_count"], 3)

if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestLootRarity,
        TestLootDrop,
        TestLootTracker,
        TestGlobalFunctions,
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
    print(f"BATCH 183 TEST RESULTS")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    if result.wasSuccessful():
        print(f"\n✅ ALL TESTS PASSED!")
        print(f"🎉 Batch 183 loot tracking system is working correctly!")
    else:
        print(f"\n❌ SOME TESTS FAILED!")
        print(f"🔧 Please review and fix the failing tests.") 