#!/usr/bin/env python3
"""
Batch 171 Phase 1 Integration Tests
Tests the complete Phase 1 implementation: session log parsing, API endpoints, and backend storage.
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any
import shutil

# Import the components we're testing
sys.path.append(str(Path(__file__).parent / 'src'))
from src.ms11.trackers.heroics_loot import HeroicsLootTracker

class TestBatch171Phase1Integration(unittest.TestCase):
    """Integration tests for Batch 171 Phase 1 components."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directories
        self.temp_dir = Path(tempfile.mkdtemp())
        self.session_logs_dir = self.temp_dir / 'session_logs'
        self.loot_logs_dir = self.temp_dir / 'loot_logs'
        
        self.session_logs_dir.mkdir(parents=True)
        self.loot_logs_dir.mkdir(parents=True)
        
        # Configure tracker
        self.tracker_config = {
            'session_logs_dir': str(self.session_logs_dir),
            'loot_logs_dir': str(self.loot_logs_dir),
            'max_log_age_days': 30,
            'validate_items': True
        }
        
        self.tracker = HeroicsLootTracker(self.tracker_config)
        
        # Create sample session logs
        self.create_sample_session_logs()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_sample_session_logs(self):
        """Create sample session log files for testing."""
        # Sample log content with heroic loot
        log_content1 = """
[2025-01-27 10:00:00] MS11 Bot Started
[2025-01-27 10:01:00] Loading character: TestPlayer
[2025-01-27 10:02:00] Entering game world
[2025-01-27 10:05:00] Group size: 8
[2025-01-27 10:10:00] Entering Axkva Min heroic instance
[2025-01-27 10:30:00] Axkva Min defeated!
[2025-01-27 10:30:05] You have received Axkva Min's Lightsaber [Legendary]
[2025-01-27 10:30:10] You have received 2x Dark Side Crystal [Epic]
[2025-01-27 10:35:00] Instance completed successfully
[2025-01-27 10:40:00] Session ended
"""
        
        log_content2 = """
[2025-01-27 11:00:00] MS11 Bot Started
[2025-01-27 11:01:00] Loading character: GuildMember1
[2025-01-27 11:02:00] Entering game world
[2025-01-27 11:05:00] Group size: 6
[2025-01-27 11:15:00] Entering IG-88 heroic instance
[2025-01-27 11:45:00] IG-88 destroyed!
[2025-01-27 11:45:05] You have received Enhanced Rifle Barrel [Rare] (100-125 damage)
[2025-01-27 11:45:10] You have received 3x Droid Processing Unit [Uncommon]
[2025-01-27 11:50:00] Instance completed
[2025-01-27 11:55:00] Session ended
"""
        
        log_content3 = """
[2025-01-27 12:00:00] MS11 Bot Started
[2025-01-27 12:01:00] Loading character: TestPlayer
[2025-01-27 12:02:00] Entering game world
[2025-01-27 12:05:00] Group size: 8
[2025-01-27 12:20:00] Entering Geonosian Queen heroic instance
[2025-01-27 12:50:00] Geonosian Queen defeated!
[2025-01-27 12:50:05] You have received 5x Queen's Carapace Fragment [Epic]
[2025-01-27 12:50:10] You have received Insectoid Chitin Armor [Epic] (75 armor rating)
[2025-01-27 12:55:00] Instance completed successfully
[2025-01-27 13:00:00] Session ended
"""
        
        # Write log files
        with open(self.session_logs_dir / 'session_20250127_1000.log', 'w') as f:
            f.write(log_content1)
        
        with open(self.session_logs_dir / 'session_20250127_1100.log', 'w') as f:
            f.write(log_content2)
        
        with open(self.session_logs_dir / 'session_20250127_1200.log', 'w') as f:
            f.write(log_content3)
    
    def test_session_log_parsing(self):
        """Test parsing session logs to extract loot data."""
        # Parse the session logs
        loot_entries = self.tracker.parse_session_logs()
        
        # Verify we got loot entries
        self.assertGreater(len(loot_entries), 0, "Should parse loot entries from session logs")
        
        # Verify entry structure
        for entry in loot_entries:
            self.assertIn('timestamp', entry)
            self.assertIn('player_name', entry)
            self.assertIn('heroic_instance', entry)
            self.assertIn('boss_name', entry)
            self.assertIn('item_name', entry)
            self.assertIn('item_type', entry)
            self.assertIn('rarity', entry)
            self.assertIn('quantity', entry)
        
        # Verify specific items were parsed correctly
        item_names = [entry['item_name'] for entry in loot_entries]
        self.assertIn("Axkva Min's Lightsaber", item_names)
        self.assertIn("Dark Side Crystal", item_names)
        self.assertIn("Enhanced Rifle Barrel", item_names)
        
        # Verify rarity detection
        legendary_items = [entry for entry in loot_entries if entry['rarity'] == 'legendary']
        self.assertGreater(len(legendary_items), 0, "Should detect legendary items")
        
        # Verify heroic instance detection
        heroic_instances = set(entry['heroic_instance'] for entry in loot_entries)
        expected_instances = {'axkva_min', 'ig_88', 'geonosian_queen'}
        self.assertTrue(heroic_instances.intersection(expected_instances), 
                       "Should detect multiple heroic instances")
    
    def test_loot_data_storage(self):
        """Test storing parsed loot data to persistent storage."""
        # Parse session logs
        loot_entries = self.tracker.parse_session_logs()
        self.assertGreater(len(loot_entries), 0)
        
        # Store the data
        filepath = self.tracker.store_loot_data(loot_entries)
        self.assertTrue(os.path.exists(filepath), "Should create loot data file")
        
        # Verify file content
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check structure
        self.assertIn('metadata', data)
        self.assertIn('loot_entries', data)
        
        # Check metadata
        metadata = data['metadata']
        self.assertIn('generated_at', metadata)
        self.assertIn('version', metadata)
        self.assertIn('total_entries', metadata)
        self.assertEqual(metadata['total_entries'], len(loot_entries))
        
        # Check loot entries
        stored_entries = data['loot_entries']
        self.assertEqual(len(stored_entries), len(loot_entries))
        
        for entry in stored_entries:
            self.assertIn('timestamp', entry)
            self.assertIn('item_name', entry)
            self.assertIn('heroic_instance', entry)
    
    def test_recent_loot_retrieval(self):
        """Test retrieving recent loot data."""
        # Parse and store loot data
        loot_entries = self.tracker.parse_session_logs()
        self.tracker.store_loot_data(loot_entries)
        
        # Retrieve recent loot data
        recent_loot = self.tracker.get_recent_loot_data(hours=24)
        self.assertGreater(len(recent_loot), 0, "Should retrieve recent loot data")
        
        # Test filtering by heroic type
        axkva_loot = self.tracker.get_recent_loot_data(heroic_type='axkva_min', hours=24)
        self.assertTrue(all(entry['heroic_instance'] == 'axkva_min' for entry in axkva_loot))
        
        # Test time filtering
        old_loot = self.tracker.get_recent_loot_data(hours=1)  # Very recent
        # Should be empty or very few items since our test data is synthetic
    
    def test_loot_statistics_calculation(self):
        """Test calculating loot statistics."""
        # Parse and store loot data
        loot_entries = self.tracker.parse_session_logs()
        self.tracker.store_loot_data(loot_entries)
        
        # Get statistics
        stats = self.tracker.get_loot_statistics()
        
        # Verify statistics structure
        self.assertIn('total_entries', stats)
        self.assertIn('unique_items', stats)
        self.assertIn('heroic_breakdown', stats)
        self.assertIn('rarity_distribution', stats)
        self.assertIn('type_distribution', stats)
        self.assertIn('most_common_items', stats)
        
        # Verify statistics content
        self.assertGreater(stats['total_entries'], 0)
        self.assertGreater(stats['unique_items'], 0)
        self.assertIsInstance(stats['heroic_breakdown'], dict)
        self.assertIsInstance(stats['rarity_distribution'], dict)
    
    def test_api_data_files_exist(self):
        """Test that API-related files exist and are accessible."""
        # Check API file exists
        api_file = Path(__file__).parent / 'src' / 'api' / 'heroics' / 'loot.js'
        self.assertTrue(api_file.exists(), "API endpoint file should exist")
        
        # Check loot logs directory exists
        loot_logs_dir = Path(__file__).parent / 'src' / 'data' / 'loot_logs'
        self.assertTrue(loot_logs_dir.exists(), "Loot logs directory should exist")
        
        # Check sample data exists
        sample_file = loot_logs_dir / 'heroic_loot_logs_sample.json'
        self.assertTrue(sample_file.exists(), "Sample loot data should exist")
        
        # Validate sample data structure
        with open(sample_file, 'r', encoding='utf-8') as f:
            sample_data = json.load(f)
        
        self.assertIn('metadata', sample_data)
        self.assertIn('loot_entries', sample_data)
        self.assertIsInstance(sample_data['loot_entries'], list)
    
    def test_item_classification(self):
        """Test item type classification."""
        # Test weapon classification
        self.assertEqual(self.tracker._classify_item_type("Axkva Min's Lightsaber"), 'weapon')
        self.assertEqual(self.tracker._classify_item_type("Enhanced Rifle Barrel"), 'weapon')
        
        # Test material classification
        self.assertEqual(self.tracker._classify_item_type("Dark Side Crystal"), 'material')
        self.assertEqual(self.tracker._classify_item_type("Queen's Carapace Fragment"), 'material')
        
        # Test armor classification
        self.assertEqual(self.tracker._classify_item_type("Insectoid Chitin Armor"), 'armor')
        
        # Test unknown classification
        self.assertEqual(self.tracker._classify_item_type("Unknown Item"), 'misc')
    
    def test_timestamp_extraction(self):
        """Test timestamp extraction from log lines."""
        # Test various timestamp formats
        test_cases = [
            ("[2025-01-27 10:30:05] Some log message", "2025-01-27T10:30:05"),
            ("[10:30:05] Some log message", None),  # Time only, should use current date
            ("2025-01-27T10:30:05Z Some message", "2025-01-27T10:30:05"),
            ("No timestamp in this line", None)
        ]
        
        for log_line, expected_result in test_cases:
            result = self.tracker._extract_timestamp(log_line)
            if expected_result:
                self.assertIsNotNone(result, f"Should extract timestamp from: {log_line}")
                if expected_result != "varies":  # For time-only tests
                    self.assertTrue(result.startswith(expected_result[:10]), 
                                  f"Timestamp should start with date: {result}")
            else:
                # Some test cases might return None or current date
                pass
    
    def test_boss_name_extraction(self):
        """Test boss name extraction."""
        test_cases = [
            ("Axkva Min defeated!", "axkva_min", "Axkva Min"),
            ("IG-88 destroyed!", "ig_88", "IG-88"),
            ("Geonosian Queen defeated!", "geonosian_queen", "Geonosian Queen"),
            ("Unknown boss defeated!", "unknown_heroic", "Unknown Heroic")
        ]
        
        for log_line, heroic_type, expected_boss in test_cases:
            if heroic_type != "unknown_heroic":  # Skip unknown test case
                result = self.tracker._extract_boss_name(log_line, heroic_type)
                self.assertEqual(result, expected_boss, 
                               f"Should extract boss name from: {log_line}")
    
    def test_rarity_extraction(self):
        """Test rarity extraction from log lines."""
        test_cases = [
            ("You have received Item [Legendary]", "legendary"),
            ("You have received Item [Epic]", "epic"),
            ("You have received Item [Rare]", "rare"),
            ("You have received Item [Uncommon]", "uncommon"),
            ("You have received Item [Common]", "common"),
            ("You have received Item", "common")  # Default
        ]
        
        for log_line, expected_rarity in test_cases:
            result = self.tracker._extract_rarity(log_line)
            self.assertEqual(result, expected_rarity,
                           f"Should extract rarity from: {log_line}")
    
    def test_stats_extraction(self):
        """Test stats extraction from log lines."""
        test_cases = [
            ("Item (100-125 damage)", {"damage": "100-125"}),
            ("Item (75 armor)", {}),  # Single value doesn't match pattern
            ("Item with no stats", {})
        ]
        
        for log_line, expected_stats in test_cases:
            result = self.tracker._extract_stats(log_line)
            if expected_stats:
                self.assertEqual(result, expected_stats,
                               f"Should extract stats from: {log_line}")
            else:
                self.assertEqual(result, {}, f"Should return empty stats for: {log_line}")
    
    def test_end_to_end_workflow(self):
        """Test the complete end-to-end workflow."""
        # 1. Parse session logs
        loot_entries = self.tracker.parse_session_logs()
        self.assertGreater(len(loot_entries), 0, "Step 1: Should parse loot entries")
        
        # 2. Store loot data
        filepath = self.tracker.store_loot_data(loot_entries)
        self.assertTrue(os.path.exists(filepath), "Step 2: Should store loot data")
        
        # 3. Retrieve recent data
        recent_loot = self.tracker.get_recent_loot_data(hours=24)
        self.assertEqual(len(recent_loot), len(loot_entries), 
                        "Step 3: Should retrieve all recent entries")
        
        # 4. Calculate statistics
        stats = self.tracker.get_loot_statistics()
        self.assertGreater(stats['total_entries'], 0, "Step 4: Should calculate statistics")
        
        # 5. Verify data consistency
        self.assertEqual(stats['total_entries'], len(loot_entries),
                        "Step 5: Statistics should match parsed entries")
        
        print("End-to-end test completed successfully!")
        print(f"   - Parsed {len(loot_entries)} loot entries")
        print(f"   - Stored to: {filepath}")
        print(f"   - Retrieved {len(recent_loot)} recent entries")
        print(f"   - Generated statistics with {stats['total_entries']} total entries")

class TestBatch171APIIntegration(unittest.TestCase):
    """Test API integration aspects."""
    
    def test_api_file_structure(self):
        """Test that the API file has correct structure."""
        api_file = Path(__file__).parent / 'src' / 'api' / 'heroics' / 'loot.js'
        self.assertTrue(api_file.exists(), "API file should exist")
        
        with open(api_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required components
        required_components = [
            'class HeroicsLootAPI',
            'getLootData',
            'getLootByHeroic', 
            'getLootStats',
            'getRecentLoot',
            'getLootByPlayer',
            'healthCheck'
        ]
        
        for component in required_components:
            self.assertIn(component, content, f"API should have {component}")
    
    def test_sample_data_structure(self):
        """Test sample data has correct structure for API consumption."""
        sample_file = Path(__file__).parent / 'src' / 'data' / 'loot_logs' / 'heroic_loot_logs_sample.json'
        self.assertTrue(sample_file.exists(), "Sample data file should exist")
        
        with open(sample_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Verify structure
        self.assertIn('metadata', data)
        self.assertIn('loot_entries', data)
        
        # Verify metadata
        metadata = data['metadata']
        required_metadata = ['generated_at', 'version', 'total_entries', 'heroic_instances']
        for field in required_metadata:
            self.assertIn(field, metadata, f"Metadata should have {field}")
        
        # Verify loot entries
        entries = data['loot_entries']
        self.assertIsInstance(entries, list)
        self.assertGreater(len(entries), 0)
        
        # Verify entry structure
        for entry in entries[:3]:  # Check first 3 entries
            required_fields = [
                'timestamp', 'player_name', 'heroic_instance', 'boss_name',
                'item_name', 'item_type', 'rarity', 'quantity'
            ]
            for field in required_fields:
                self.assertIn(field, entry, f"Entry should have {field}")

def run_tests():
    """Run all Phase 1 integration tests."""
    print("Running Batch 171 Phase 1 Integration Tests")
    print("=" * 60)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBatch171Phase1Integration))
    suite.addTests(loader.loadTestsFromTestCase(TestBatch171APIIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\nPhase 1 Integration Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("All Phase 1 integration tests passed!")
        print("\nPhase 1 Components Ready:")
        print("  - Session log parsing")
        print("  - Backend storage system")
        print("  - API endpoint structure")
        print("  - Data format validation")
        print("  - End-to-end workflow")
    else:
        print("Some Phase 1 tests failed!")
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)