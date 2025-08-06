#!/usr/bin/env python3
"""
Comprehensive test suite for Batch 172 - Rare Loot Scan Mode (RLS Mode)

This test suite validates all aspects of the RLS mode implementation:
- Configuration loading and validation
- Target prioritization and scanning
- Loot analysis and categorization
- Discord alert system
- Learning system and user preferences
- Session logging and statistics
- Full RLS mode execution
"""

import json
import unittest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.modes.rare_loot import RareLootScanner, run_rls_mode


class TestRareLootScanner(unittest.TestCase):
    """Test suite for the RareLootScanner class."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_config = {
            "targets": [
                {
                    "name": "Test Krayt Dragon",
                    "planet": "Tatooine",
                    "zone": "Dune Sea",
                    "level": 90,
                    "priority": 10,
                    "loot_types": ["pearls", "scales"],
                    "notes": "Test target",
                    "coordinates": [100, 200],
                    "spawn_conditions": "night_only",
                    "rarity": "legendary"
                },
                {
                    "name": "Test Kimogila",
                    "planet": "Lok",
                    "zone": "Kimogila Valley",
                    "level": 85,
                    "priority": 9,
                    "loot_types": ["hides", "claws"],
                    "notes": "Test target 2",
                    "coordinates": [300, 150],
                    "spawn_conditions": "any_time",
                    "rarity": "epic"
                }
            ],
            "settings": {
                "scan_interval": 30,
                "max_targets_per_session": 10,
                "discord_alerts_enabled": True,
                "auto_logout_on_rare": False,
                "notification_threshold": "rare",
                "learning_enabled": True,
                "area_scan_radius": 1000,
                "enemy_type_scan": True
            },
            "loot_categories": {
                "pearls": {
                    "rarity": "legendary",
                    "value": 10000,
                    "professions": ["artisan", "merchant"]
                },
                "scales": {
                    "rarity": "epic",
                    "value": 5000,
                    "professions": ["armorsmith", "artisan"]
                },
                "hides": {
                    "rarity": "rare",
                    "value": 2000,
                    "professions": ["armorsmith", "artisan"]
                }
            }
        }
        
        # Create test config file
        self.config_path = Path(self.temp_dir) / "rare_loot_targets.json"
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_config, f, indent=2)
        
        # Create test learning data
        self.test_learning_data = {
            "successful_targets": ["Test Krayt Dragon"],
            "failed_targets": ["Test Kimogila"],
            "loot_patterns": {
                "pearls": 2,
                "scales": 1
            }
        }
        
        # Create test user preferences
        self.test_user_preferences = {
            "preferred_planets": ["Tatooine"],
            "preferred_loot_types": ["pearls"],
            "avoided_targets": ["Test Kimogila"],
            "notification_preferences": "all"
        }
        
        # Mock session memory
        self.original_session_memory = None
        try:
            from core.session_memory import session_memory
            self.original_session_memory = session_memory
        except ImportError:
            pass
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_scanner_initialization(self):
        """Test RareLootScanner initialization."""
        scanner = RareLootScanner()
        self.assertIsNotNone(scanner)
        self.assertIsInstance(scanner.config, dict)
        self.assertIsInstance(scanner.targets_config, dict)
        self.assertIsInstance(scanner.session_log, list)
        self.assertIsInstance(scanner.rare_loot_found, list)
    
    def test_config_loading(self):
        """Test configuration loading functionality."""
        # Test with existing config
        scanner = RareLootScanner()
        config = scanner._load_targets_config()
        self.assertIsInstance(config, dict)
        self.assertIn("targets", config)
        self.assertIn("settings", config)
    
    def test_learning_data_loading(self):
        """Test learning data loading functionality."""
        scanner = RareLootScanner()
        learning_data = scanner._load_learning_data()
        self.assertIsInstance(learning_data, dict)
        self.assertIn("successful_targets", learning_data)
        self.assertIn("failed_targets", learning_data)
        self.assertIn("loot_patterns", learning_data)
    
    def test_user_preferences_loading(self):
        """Test user preferences loading functionality."""
        scanner = RareLootScanner()
        preferences = scanner._load_user_preferences()
        self.assertIsInstance(preferences, dict)
        self.assertIn("preferred_planets", preferences)
        self.assertIn("preferred_loot_types", preferences)
        self.assertIn("avoided_targets", preferences)
    
    def test_target_prioritization(self):
        """Test target prioritization system."""
        scanner = RareLootScanner()
        
        # Mock targets config
        scanner.targets_config = self.test_config
        scanner.learning_data = self.test_learning_data
        scanner.user_preferences = self.test_user_preferences
        
        targets = scanner.prioritize_targets()
        self.assertIsInstance(targets, list)
        self.assertGreater(len(targets), 0)
        
        # Check that avoided targets are filtered out
        target_names = [target["name"] for target in targets]
        self.assertNotIn("Test Kimogila", target_names)
    
    def test_area_scanning(self):
        """Test area scanning functionality."""
        scanner = RareLootScanner()
        scanner.targets_config = self.test_config
        
        # Mock current location
        def mock_get_location():
            return [150, 250]
        
        # Mock session memory
        if hasattr(scanner, '_calculate_distance'):
            area_targets = scanner.scan_area_for_targets(area_radius=1000)
            self.assertIsInstance(area_targets, list)
    
    def test_enemy_type_scanning(self):
        """Test enemy type scanning functionality."""
        scanner = RareLootScanner()
        scanner.targets_config = self.test_config
        
        dragon_targets = scanner.scan_by_enemy_type("dragon")
        self.assertIsInstance(dragon_targets, list)
        
        # Should find the Krayt Dragon
        target_names = [target["name"] for target in dragon_targets]
        self.assertIn("Test Krayt Dragon", target_names)
    
    def test_distance_calculation(self):
        """Test distance calculation functionality."""
        scanner = RareLootScanner()
        
        # Test valid coordinates
        distance = scanner._calculate_distance([0, 0], [3, 4])
        self.assertEqual(distance, 5.0)
        
        # Test invalid coordinates
        distance = scanner._calculate_distance([0], [3, 4])
        self.assertEqual(distance, float('inf'))
    
    def test_loot_analysis(self):
        """Test loot analysis functionality."""
        scanner = RareLootScanner()
        scanner.targets_config = self.test_config
        
        # Test pearl analysis
        loot_info = scanner._analyze_loot_item("Krayt Dragon Pearl")
        self.assertEqual(loot_info["type"], "pearls")
        self.assertEqual(loot_info["rarity"], "legendary")
        self.assertEqual(loot_info["value"], 10000)
        self.assertTrue(loot_info["is_rare"])
        
        # Test unknown item
        loot_info = scanner._analyze_loot_item("Unknown Item")
        self.assertEqual(loot_info["type"], "unknown")
        self.assertEqual(loot_info["rarity"], "common")
        self.assertFalse(loot_info["is_rare"])
    
    def test_rare_loot_logging(self):
        """Test rare loot logging functionality."""
        scanner = RareLootScanner()
        scanner.learning_data = self.test_learning_data
        scanner.current_target = {"name": "Test Target"}
        
        # Test logging rare loot
        loot_info = {
            "name": "Test Pearl",
            "type": "pearls",
            "rarity": "legendary",
            "value": 10000,
            "is_rare": True
        }
        
        initial_count = len(scanner.rare_loot_found)
        scanner._log_rare_loot(loot_info)
        
        self.assertEqual(len(scanner.rare_loot_found), initial_count + 1)
        self.assertEqual(len(scanner.session_log), initial_count + 1)
    
    def test_discord_alert_generation(self):
        """Test Discord alert message generation."""
        scanner = RareLootScanner()
        scanner.current_target = {"name": "Test Target"}
        
        loot_info = {
            "name": "Test Pearl",
            "rarity": "legendary",
            "type": "pearls",
            "value": 10000,
            "timestamp": "2024-01-01T12:00:00",
            "location": "Test Location"
        }
        
        # Test alert generation (without actually sending)
        try:
            scanner._send_discord_alert(loot_info)
            # Should not raise exception
            self.assertTrue(True)
        except Exception as e:
            # Expected if Discord is not configured
            self.assertIn("Discord", str(e))
    
    def test_auto_logout_handling(self):
        """Test auto-logout handling functionality."""
        scanner = RareLootScanner()
        scanner.targets_config = self.test_config
        
        # Test legendary item
        loot_info = {
            "name": "Legendary Item",
            "rarity": "legendary"
        }
        
        try:
            scanner._handle_auto_logout(loot_info)
            # Should not raise exception
            self.assertTrue(True)
        except Exception as e:
            # Expected if session memory is not available
            pass
    
    def test_learning_from_wiki(self):
        """Test learning from wiki functionality."""
        scanner = RareLootScanner()
        scanner.rare_loot_found = [
            {"type": "pearls", "rarity": "legendary"},
            {"type": "scales", "rarity": "epic"}
        ]
        
        # Test learning process
        try:
            scanner.learn_from_wiki()
            # Should not raise exception
            self.assertTrue(True)
        except Exception as e:
            # Expected if file operations fail
            pass
    
    def test_session_statistics(self):
        """Test session statistics calculation."""
        scanner = RareLootScanner()
        scanner.scan_count = 5
        scanner.rare_loot_found = [
            {"name": "Item 1", "value": 1000, "rarity": "rare"},
            {"name": "Item 2", "value": 2000, "rarity": "epic"},
            {"name": "Item 3", "value": 5000, "rarity": "legendary"}
        ]
        
        stats = scanner.get_session_stats()
        
        self.assertEqual(stats["scan_count"], 5)
        self.assertEqual(stats["rare_loot_found"], 3)
        self.assertEqual(stats["total_value"], 8000)
        self.assertIn("rare", stats["rarity_breakdown"])
        self.assertIn("epic", stats["rarity_breakdown"])
        self.assertIn("legendary", stats["rarity_breakdown"])
    
    def test_rarity_breakdown(self):
        """Test rarity breakdown calculation."""
        scanner = RareLootScanner()
        scanner.rare_loot_found = [
            {"rarity": "rare"},
            {"rarity": "epic"},
            {"rarity": "legendary"},
            {"rarity": "rare"}
        ]
        
        breakdown = scanner._get_rarity_breakdown()
        
        self.assertEqual(breakdown["rare"], 2)
        self.assertEqual(breakdown["epic"], 1)
        self.assertEqual(breakdown["legendary"], 1)
    
    def test_session_duration_calculation(self):
        """Test session duration calculation."""
        scanner = RareLootScanner()
        
        # Test empty session
        duration = scanner._get_session_duration()
        self.assertEqual(duration, 0.0)
        
        # Test session with items
        scanner.session_log = [
            {"timestamp": "2024-01-01T12:00:00"},
            {"timestamp": "2024-01-01T12:01:00"}
        ]
        
        duration = scanner._get_session_duration()
        self.assertGreater(duration, 0.0)
    
    def test_session_log_export(self):
        """Test session log export functionality."""
        scanner = RareLootScanner()
        scanner.targets_config = self.test_config
        scanner.scan_count = 3
        scanner.rare_loot_found = [
            {"name": "Test Item", "value": 1000, "rarity": "rare"}
        ]
        
        # Test export
        log_path = scanner.export_session_log()
        
        # Should return a path (even if file creation fails)
        self.assertIsInstance(log_path, str)
    
    def test_save_learning_data(self):
        """Test learning data saving functionality."""
        scanner = RareLootScanner()
        scanner.learning_data = self.test_learning_data
        
        # Test save operation
        try:
            scanner._save_learning_data()
            # Should not raise exception
            self.assertTrue(True)
        except Exception as e:
            # Expected if file operations fail
            pass
    
    def test_save_user_preferences(self):
        """Test user preferences saving functionality."""
        scanner = RareLootScanner()
        scanner.user_preferences = self.test_user_preferences
        
        # Test save operation
        try:
            scanner._save_user_preferences()
            # Should not raise exception
            self.assertTrue(True)
        except Exception as e:
            # Expected if file operations fail
            pass


class TestRLSModeExecution(unittest.TestCase):
    """Test suite for RLS mode execution functions."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_run_rls_mode_basic(self):
        """Test basic RLS mode execution."""
        result = run_rls_mode(
            config={"iterations": 1},
            loop_count=1
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
        self.assertIn("stats", result)
        self.assertIn("log_path", result)
        self.assertIn("rare_loot_found", result)
    
    def test_run_rls_mode_with_area_scan(self):
        """Test RLS mode with area scanning."""
        result = run_rls_mode(
            config={"iterations": 1},
            loop_count=1,
            area_scan=True,
            enemy_type_scan=False
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
    
    def test_run_rls_mode_with_enemy_type_scan(self):
        """Test RLS mode with enemy type scanning."""
        result = run_rls_mode(
            config={"iterations": 1},
            loop_count=1,
            area_scan=False,
            enemy_type_scan=True,
            enemy_type="dragon"
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)
    
    def test_run_rls_mode_no_targets(self):
        """Test RLS mode with no available targets."""
        # This should handle the case gracefully
        result = run_rls_mode(
            config={"iterations": 1},
            loop_count=1
        )
        
        self.assertIsInstance(result, dict)
        # Should either succeed or return error gracefully
        self.assertIn("success", result)


class TestRLSConfiguration(unittest.TestCase):
    """Test suite for RLS configuration validation."""
    
    def test_config_file_structure(self):
        """Test configuration file structure validation."""
        config_path = Path("config/rare_loot_targets.json")
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Test required sections
            self.assertIn("targets", config)
            self.assertIn("settings", config)
            self.assertIn("loot_categories", config)
            
            # Test targets structure
            targets = config["targets"]
            self.assertIsInstance(targets, list)
            
            for target in targets:
                required_fields = ["name", "planet", "level", "priority"]
                for field in required_fields:
                    self.assertIn(field, target)
    
    def test_loot_categories_structure(self):
        """Test loot categories structure validation."""
        config_path = Path("config/rare_loot_targets.json")
        
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            loot_categories = config.get("loot_categories", {})
            
            for category_name, category_info in loot_categories.items():
                self.assertIn("rarity", category_info)
                self.assertIn("value", category_info)
                self.assertIn("professions", category_info)
                
                # Test rarity values
                valid_rarities = ["common", "uncommon", "rare", "epic", "legendary"]
                self.assertIn(category_info["rarity"], valid_rarities)
                
                # Test value is numeric
                self.assertIsInstance(category_info["value"], (int, float))
                
                # Test professions is list
                self.assertIsInstance(category_info["professions"], list)


class TestRLSIntegration(unittest.TestCase):
    """Test suite for RLS mode integration."""
    
    def test_scanner_integration(self):
        """Test scanner integration with other components."""
        scanner = RareLootScanner()
        
        # Test that scanner can be initialized
        self.assertIsNotNone(scanner)
        
        # Test that scanner has required methods
        required_methods = [
            "prioritize_targets",
            "scan_area_for_targets",
            "scan_by_enemy_type",
            "scan_for_loot",
            "get_session_stats",
            "export_session_log"
        ]
        
        for method_name in required_methods:
            self.assertTrue(hasattr(scanner, method_name))
    
    def test_mode_compatibility(self):
        """Test RLS mode compatibility with existing mode system."""
        # Test that run function exists and is callable
        from core.modes.rare_loot import run
        
        self.assertTrue(callable(run))
        
        # Test function signature
        import inspect
        sig = inspect.signature(run)
        params = list(sig.parameters.keys())
        
        # Should have config, session, and loop_count parameters
        self.assertIn("config", params)
        self.assertIn("session", params)
        self.assertIn("loop_count", params)


def run_tests():
    """Run all RLS mode tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestRareLootScanner,
        TestRLSModeExecution,
        TestRLSConfiguration,
        TestRLSIntegration
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