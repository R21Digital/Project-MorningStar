"""
Test suite for Batch 053 - Smart Inventory Whitelist & Exclusion System

Tests cover:
- InventoryManager class functionality
- StorageLocation and InventorySettings dataclasses
- Exclusion checking logic
- Storage location management
- Inventory warnings
- Configuration persistence
- Global convenience functions
"""

import json
import tempfile
import unittest
from pathlib import Path
from typing import Dict, Any
from unittest.mock import patch, MagicMock

# Add the project root to the path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from core.inventory_manager import (
    InventoryManager, StorageLocation, InventorySettings,
    get_inventory_manager, should_keep, get_storage_location, check_inventory_full
)

class TestStorageLocation(unittest.TestCase):
    """Test StorageLocation dataclass."""
    
    def test_storage_location_creation(self):
        """Test creating a StorageLocation."""
        location = StorageLocation(
            planet="Tatooine",
            city="Mos Entha",
            structure_name="Storage Shed A",
            coordinates={"x": 1234, "y": 5678}
        )
        
        self.assertEqual(location.planet, "Tatooine")
        self.assertEqual(location.city, "Mos Entha")
        self.assertEqual(location.structure_name, "Storage Shed A")
        self.assertEqual(location.coordinates, {"x": 1234, "y": 5678})
    
    def test_storage_location_without_coordinates(self):
        """Test creating a StorageLocation without coordinates."""
        location = StorageLocation(
            planet="Naboo",
            city="Theed",
            structure_name="Player House"
        )
        
        self.assertEqual(location.planet, "Naboo")
        self.assertEqual(location.city, "Theed")
        self.assertEqual(location.structure_name, "Player House")
        self.assertIsNone(location.coordinates)
    
    def test_storage_location_string_representation(self):
        """Test string representation of StorageLocation."""
        # With coordinates
        location_with_coords = StorageLocation(
            planet="Tatooine",
            city="Mos Entha",
            structure_name="Storage Shed A",
            coordinates={"x": 1234, "y": 5678}
        )
        expected_with_coords = "Storage Shed A in Mos Entha, Tatooine (1234, 5678)"
        self.assertEqual(str(location_with_coords), expected_with_coords)
        
        # Without coordinates
        location_without_coords = StorageLocation(
            planet="Naboo",
            city="Theed",
            structure_name="Player House"
        )
        expected_without_coords = "Player House in Theed, Naboo"
        self.assertEqual(str(location_without_coords), expected_without_coords)

class TestInventorySettings(unittest.TestCase):
    """Test InventorySettings dataclass."""
    
    def test_inventory_settings_defaults(self):
        """Test InventorySettings default values."""
        settings = InventorySettings()
        
        self.assertEqual(settings.max_inventory_warning_threshold, 80)
        self.assertTrue(settings.auto_storage_enabled)
        self.assertEqual(settings.storage_check_interval, 300)
        self.assertFalse(settings.exclusion_case_sensitive)
    
    def test_inventory_settings_custom_values(self):
        """Test InventorySettings with custom values."""
        settings = InventorySettings(
            max_inventory_warning_threshold=90,
            auto_storage_enabled=False,
            storage_check_interval=600,
            exclusion_case_sensitive=True
        )
        
        self.assertEqual(settings.max_inventory_warning_threshold, 90)
        self.assertFalse(settings.auto_storage_enabled)
        self.assertEqual(settings.storage_check_interval, 600)
        self.assertTrue(settings.exclusion_case_sensitive)

class TestInventoryManager(unittest.TestCase):
    """Test InventoryManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary config file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_inventory_rules.json"
        
        # Create test config
        test_config = {
            "exclusions": ["Janta Blood", "Robe of the Benevolent", "Ancient Artifact"],
            "storage_target": {
                "planet": "Tatooine",
                "city": "Mos Entha",
                "structure_name": "Storage Shed A",
                "coordinates": {"x": 1234, "y": 5678}
            },
            "settings": {
                "max_inventory_warning_threshold": 85,
                "auto_storage_enabled": True,
                "storage_check_interval": 300,
                "exclusion_case_sensitive": False
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_inventory_manager_initialization(self):
        """Test InventoryManager initialization."""
        manager = InventoryManager(str(self.config_file))
        
        self.assertEqual(len(manager.exclusions), 3)
        self.assertIn("Janta Blood", manager.exclusions)
        self.assertIn("Robe of the Benevolent", manager.exclusions)
        self.assertIn("Ancient Artifact", manager.exclusions)
        
        self.assertIsNotNone(manager.storage_location)
        self.assertEqual(manager.storage_location.planet, "Tatooine")
        self.assertEqual(manager.storage_location.city, "Mos Entha")
        self.assertEqual(manager.storage_location.structure_name, "Storage Shed A")
        
        self.assertEqual(manager.settings.max_inventory_warning_threshold, 85)
        self.assertTrue(manager.settings.auto_storage_enabled)
    
    def test_inventory_manager_missing_config(self):
        """Test InventoryManager with missing config file."""
        manager = InventoryManager("nonexistent_file.json")
        
        self.assertEqual(len(manager.exclusions), 0)
        self.assertIsNone(manager.storage_location)
        self.assertEqual(manager.settings.max_inventory_warning_threshold, 80)  # Default
    
    def test_should_keep_excluded_items(self):
        """Test should_keep with excluded items."""
        manager = InventoryManager(str(self.config_file))
        
        # Test exact matches
        self.assertTrue(manager.should_keep("Janta Blood"))
        self.assertTrue(manager.should_keep("Robe of the Benevolent"))
        self.assertTrue(manager.should_keep("Ancient Artifact"))
        
        # Test partial matches (case-insensitive)
        self.assertTrue(manager.should_keep("janta blood"))
        self.assertTrue(manager.should_keep("JANTA BLOOD"))
        self.assertTrue(manager.should_keep("Robe of the"))
        self.assertTrue(manager.should_keep("ancient"))
    
    def test_should_keep_non_excluded_items(self):
        """Test should_keep with non-excluded items."""
        manager = InventoryManager(str(self.config_file))
        
        # Test non-excluded items
        self.assertFalse(manager.should_keep("Common Sword"))
        self.assertFalse(manager.should_keep("Basic Armor"))
        self.assertFalse(manager.should_keep("Simple Potion"))
        self.assertFalse(manager.should_keep(""))
        self.assertFalse(manager.should_keep(None))
    
    def test_should_keep_case_sensitive(self):
        """Test should_keep with case-sensitive setting."""
        manager = InventoryManager(str(self.config_file))
        
        # Test case-insensitive (default)
        self.assertTrue(manager.should_keep("janta blood"))
        
        # Change to case-sensitive
        manager.update_settings(exclusion_case_sensitive=True)
        self.assertFalse(manager.should_keep("janta blood"))
        self.assertTrue(manager.should_keep("Janta Blood"))
    
    def test_get_storage_location(self):
        """Test get_storage_location."""
        manager = InventoryManager(str(self.config_file))
        storage = manager.get_storage_location()
        
        self.assertIsNotNone(storage)
        self.assertEqual(storage.planet, "Tatooine")
        self.assertEqual(storage.city, "Mos Entha")
        self.assertEqual(storage.structure_name, "Storage Shed A")
        self.assertEqual(storage.coordinates, {"x": 1234, "y": 5678})
    
    def test_check_inventory_full(self):
        """Test check_inventory_full."""
        manager = InventoryManager(str(self.config_file))
        
        # Test below threshold
        is_full, warning = manager.check_inventory_full(50)
        self.assertFalse(is_full)
        self.assertIsNone(warning)
        
        # Test at threshold
        is_full, warning = manager.check_inventory_full(85)
        self.assertTrue(is_full)
        self.assertIn("85% full", warning)
        self.assertIn("Consider storing items", warning)
        
        # Test above threshold
        is_full, warning = manager.check_inventory_full(95)
        self.assertTrue(is_full)
        self.assertIn("95% full", warning)
    
    def test_check_inventory_full_no_storage(self):
        """Test check_inventory_full with no storage location."""
        manager = InventoryManager(str(self.config_file))
        manager.storage_location = None
        
        is_full, warning = manager.check_inventory_full(90)
        self.assertTrue(is_full)
        self.assertIn("No storage location configured", warning)
    
    def test_check_inventory_full_auto_storage_disabled(self):
        """Test check_inventory_full with auto-storage disabled."""
        manager = InventoryManager(str(self.config_file))
        manager.update_settings(auto_storage_enabled=False)
        
        is_full, warning = manager.check_inventory_full(90)
        self.assertTrue(is_full)
        self.assertIn("Auto-storage is disabled", warning)
    
    def test_add_exclusion(self):
        """Test add_exclusion."""
        manager = InventoryManager(str(self.config_file))
        original_count = len(manager.exclusions)
        
        # Add new exclusion
        result = manager.add_exclusion("New Test Item")
        self.assertTrue(result)
        self.assertEqual(len(manager.exclusions), original_count + 1)
        self.assertIn("New Test Item", manager.exclusions)
        
        # Try to add duplicate
        result = manager.add_exclusion("New Test Item")
        self.assertFalse(result)
        self.assertEqual(len(manager.exclusions), original_count + 1)
    
    def test_remove_exclusion(self):
        """Test remove_exclusion."""
        manager = InventoryManager(str(self.config_file))
        original_count = len(manager.exclusions)
        
        # Remove existing exclusion
        result = manager.remove_exclusion("Janta Blood")
        self.assertTrue(result)
        self.assertEqual(len(manager.exclusions), original_count - 1)
        self.assertNotIn("Janta Blood", manager.exclusions)
        
        # Try to remove non-existent exclusion
        result = manager.remove_exclusion("Non-existent Item")
        self.assertFalse(result)
        self.assertEqual(len(manager.exclusions), original_count - 1)
    
    def test_set_storage_location(self):
        """Test set_storage_location."""
        manager = InventoryManager(str(self.config_file))
        
        # Set new storage location
        manager.set_storage_location(
            planet="Naboo",
            city="Theed",
            structure_name="Player House",
            coordinates={"x": 2000, "y": 3000}
        )
        
        storage = manager.get_storage_location()
        self.assertEqual(storage.planet, "Naboo")
        self.assertEqual(storage.city, "Theed")
        self.assertEqual(storage.structure_name, "Player House")
        self.assertEqual(storage.coordinates, {"x": 2000, "y": 3000})
    
    def test_get_exclusions(self):
        """Test get_exclusions."""
        manager = InventoryManager(str(self.config_file))
        exclusions = manager.get_exclusions()
        
        self.assertEqual(len(exclusions), 3)
        self.assertIn("Janta Blood", exclusions)
        self.assertIn("Robe of the Benevolent", exclusions)
        self.assertIn("Ancient Artifact", exclusions)
        
        # Test that returned list is a copy
        exclusions.append("Test Item")
        self.assertNotIn("Test Item", manager.exclusions)
    
    def test_get_settings(self):
        """Test get_settings."""
        manager = InventoryManager(str(self.config_file))
        settings = manager.get_settings()
        
        self.assertEqual(settings.max_inventory_warning_threshold, 85)
        self.assertTrue(settings.auto_storage_enabled)
        self.assertEqual(settings.storage_check_interval, 300)
        self.assertFalse(settings.exclusion_case_sensitive)
    
    def test_update_settings(self):
        """Test update_settings."""
        manager = InventoryManager(str(self.config_file))
        
        # Update settings
        manager.update_settings(
            max_inventory_warning_threshold=90,
            auto_storage_enabled=False,
            storage_check_interval=600
        )
        
        settings = manager.get_settings()
        self.assertEqual(settings.max_inventory_warning_threshold, 90)
        self.assertFalse(settings.auto_storage_enabled)
        self.assertEqual(settings.storage_check_interval, 600)
    
    def test_get_summary(self):
        """Test get_summary."""
        manager = InventoryManager(str(self.config_file))
        summary = manager.get_summary()
        
        self.assertEqual(summary["exclusions_count"], 3)
        self.assertEqual(len(summary["exclusions"]), 3)
        self.assertIn("Storage Shed A in Mos Entha, Tatooine", summary["storage_location"])
        self.assertTrue(summary["auto_storage_enabled"])
        self.assertEqual(summary["max_inventory_warning_threshold"], 85)
        self.assertFalse(summary["exclusion_case_sensitive"])
    
    def test_configuration_persistence(self):
        """Test that configuration changes are persisted."""
        manager = InventoryManager(str(self.config_file))
        
        # Make changes
        manager.add_exclusion("Persistent Test Item")
        manager.set_storage_location("Corellia", "Coronet", "Test Storage")
        
        # Create new manager instance to test persistence
        new_manager = InventoryManager(str(self.config_file))
        
        # Verify persistence
        self.assertIn("Persistent Test Item", new_manager.exclusions)
        self.assertEqual(new_manager.storage_location.planet, "Corellia")
        self.assertEqual(new_manager.storage_location.city, "Coronet")
        self.assertEqual(new_manager.storage_location.structure_name, "Test Storage")

class TestGlobalFunctions(unittest.TestCase):
    """Test global convenience functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary config file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_inventory_rules.json"
        
        # Create test config
        test_config = {
            "exclusions": ["Janta Blood", "Robe of the Benevolent"],
            "storage_target": {
                "planet": "Tatooine",
                "city": "Mos Entha",
                "structure_name": "Storage Shed A",
                "coordinates": {"x": 1234, "y": 5678}
            },
            "settings": {
                "max_inventory_warning_threshold": 80,
                "auto_storage_enabled": True,
                "storage_check_interval": 300,
                "exclusion_case_sensitive": False
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    @patch('core.inventory_manager._inventory_manager', None)
    def test_get_inventory_manager(self):
        """Test get_inventory_manager global function."""
        # Reset global instance
        import core.inventory_manager
        core.inventory_manager._inventory_manager = None
        
        manager = get_inventory_manager()
        self.assertIsInstance(manager, InventoryManager)
        
        # Test singleton behavior
        manager2 = get_inventory_manager()
        self.assertIs(manager, manager2)
    
    def test_should_keep_global(self):
        """Test should_keep global function."""
        with patch('core.inventory_manager.get_inventory_manager') as mock_get_manager:
            mock_manager = MagicMock()
            mock_manager.should_keep.return_value = True
            mock_get_manager.return_value = mock_manager
            
            result = should_keep("Test Item")
            
            mock_manager.should_keep.assert_called_once_with("Test Item")
            self.assertTrue(result)
    
    def test_get_storage_location_global(self):
        """Test get_storage_location global function."""
        with patch('core.inventory_manager.get_inventory_manager') as mock_get_manager:
            mock_manager = MagicMock()
            mock_storage = StorageLocation("Tatooine", "Mos Entha", "Test Storage")
            mock_manager.get_storage_location.return_value = mock_storage
            mock_get_manager.return_value = mock_manager
            
            result = get_storage_location()
            
            mock_manager.get_storage_location.assert_called_once()
            self.assertEqual(result, mock_storage)
    
    def test_check_inventory_full_global(self):
        """Test check_inventory_full global function."""
        with patch('core.inventory_manager.get_inventory_manager') as mock_get_manager:
            mock_manager = MagicMock()
            mock_manager.check_inventory_full.return_value = (True, "Warning message")
            mock_get_manager.return_value = mock_manager
            
            is_full, warning = check_inventory_full(90)
            
            mock_manager.check_inventory_full.assert_called_once_with(90)
            self.assertTrue(is_full)
            self.assertEqual(warning, "Warning message")

class TestIntegration(unittest.TestCase):
    """Integration tests for the inventory management system."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary config file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = Path(self.temp_dir) / "test_inventory_rules.json"
        
        # Create test config
        test_config = {
            "exclusions": ["Janta Blood", "Robe of the Benevolent", "Ancient Artifact"],
            "storage_target": {
                "planet": "Tatooine",
                "city": "Mos Entha",
                "structure_name": "Storage Shed A",
                "coordinates": {"x": 1234, "y": 5678}
            },
            "settings": {
                "max_inventory_warning_threshold": 80,
                "auto_storage_enabled": True,
                "storage_check_interval": 300,
                "exclusion_case_sensitive": False
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(test_config, f)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_integration_workflow(self):
        """Test a complete inventory management workflow."""
        manager = InventoryManager(str(self.config_file))
        
        # Test initial state
        self.assertEqual(len(manager.exclusions), 3)
        self.assertIsNotNone(manager.storage_location)
        
        # Test exclusion checking
        self.assertTrue(manager.should_keep("Janta Blood"))
        self.assertFalse(manager.should_keep("Common Sword"))
        
        # Test inventory warnings
        is_full, warning = manager.check_inventory_full(85)
        self.assertTrue(is_full)
        self.assertIn("85% full", warning)
        
        # Test adding exclusion
        manager.add_exclusion("New Valuable Item")
        self.assertTrue(manager.should_keep("New Valuable Item"))
        
        # Test removing exclusion
        manager.remove_exclusion("Janta Blood")
        self.assertFalse(manager.should_keep("Janta Blood"))
        
        # Test storage location update
        manager.set_storage_location("Naboo", "Theed", "Player House")
        storage = manager.get_storage_location()
        self.assertEqual(storage.planet, "Naboo")
        
        # Test settings update
        manager.update_settings(max_inventory_warning_threshold=90)
        is_full, warning = manager.check_inventory_full(85)
        self.assertFalse(is_full)  # Now below threshold
        
        # Test persistence
        new_manager = InventoryManager(str(self.config_file))
        self.assertIn("New Valuable Item", new_manager.exclusions)
        self.assertNotIn("Janta Blood", new_manager.exclusions)
        self.assertEqual(new_manager.storage_location.planet, "Naboo")
        self.assertEqual(new_manager.settings.max_inventory_warning_threshold, 90)

def run_tests():
    """Run all tests and return results."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestStorageLocation,
        TestInventorySettings,
        TestInventoryManager,
        TestGlobalFunctions,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result

if __name__ == "__main__":
    result = run_tests()
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Test Results Summary:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*60}")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1) 