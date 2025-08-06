#!/usr/bin/env python3
"""
Batch 153 - Mount Profile Builder Test Suite

This test suite validates the mount scanner and profile builder functionality,
ensuring all components work correctly and data is properly persisted.
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

from core.mount_profile_builder import (
    MountProfileBuilder, MountInfo, CharacterMountProfile,
    get_mount_profile_builder, scan_character_mounts
)
from core.mount_profile_integration import (
    MountProfileIntegration, MountScanEvent,
    get_mount_profile_integration, scan_mounts_on_login
)

class TestMountInfo(unittest.TestCase):
    """Test the MountInfo dataclass."""
    
    def test_mount_info_creation(self):
        """Test creating a MountInfo instance."""
        mount = MountInfo(
            name="Speederbike",
            mount_type="speeder",
            speed=2.5,
            learned=True,
            hotbar_slot=1,
            command="/mount speederbike",
            description="Fast speeder bike",
            creature_type=None,
            indoor_allowed=False,
            city_allowed=True,
            combat_allowed=False
        )
        
        self.assertEqual(mount.name, "Speederbike")
        self.assertEqual(mount.mount_type, "speeder")
        self.assertEqual(mount.speed, 2.5)
        self.assertTrue(mount.learned)
        self.assertEqual(mount.hotbar_slot, 1)
        self.assertEqual(mount.command, "/mount speederbike")
        self.assertEqual(mount.description, "Fast speeder bike")
        self.assertIsNone(mount.creature_type)
        self.assertFalse(mount.indoor_allowed)
        self.assertTrue(mount.city_allowed)
        self.assertFalse(mount.combat_allowed)
    
    def test_mount_info_with_creature(self):
        """Test MountInfo with creature type."""
        mount = MountInfo(
            name="Dewback",
            mount_type="creature",
            speed=1.5,
            learned=True,
            creature_type="dewback"
        )
        
        self.assertEqual(mount.name, "Dewback")
        self.assertEqual(mount.mount_type, "creature")
        self.assertEqual(mount.creature_type, "dewback")
        self.assertEqual(mount.speed, 1.5)

class TestMountProfileBuilder(unittest.TestCase):
    """Test the MountProfileBuilder class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.builder = MountProfileBuilder(str(self.test_dir))
        
        # Create test mount database
        self.test_mount_db = {
            "mounts": {
                "Speederbike": {
                    "name": "Speederbike",
                    "type": "speeder",
                    "speed": 2.5,
                    "learned": True,
                    "hotbar_slot": 1,
                    "command": "/mount speederbike",
                    "description": "Fast speeder bike"
                },
                "Dewback": {
                    "name": "Dewback",
                    "type": "creature",
                    "speed": 1.5,
                    "learned": True,
                    "creature_type": "dewback",
                    "description": "Desert creature"
                }
            }
        }
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    @patch('core.mount_profile_builder.Path')
    def test_load_mount_database(self, mock_path):
        """Test loading mount database."""
        # Mock the mount database file
        mock_yaml_file = MagicMock()
        mock_yaml_file.exists.return_value = True
        mock_path.return_value = mock_yaml_file
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = """
            mounts:
              Speederbike:
                name: "Speederbike"
                type: "speeder"
                speed: 2.5
            """
            
            builder = MountProfileBuilder()
            self.assertIn("mounts", builder.mount_database)
    
    def test_determine_mount_type(self):
        """Test mount type determination."""
        self.assertEqual(self.builder._determine_mount_type("Speederbike"), "speeder")
        self.assertEqual(self.builder._determine_mount_type("Dewback"), "creature")
        self.assertEqual(self.builder._determine_mount_type("Jetpack"), "flying")
        self.assertEqual(self.builder._determine_mount_type("Unknown"), "unknown")
    
    def test_estimate_mount_speed(self):
        """Test mount speed estimation."""
        # Test with known types
        speed = self.builder._estimate_mount_speed("Speederbike")
        self.assertGreaterEqual(speed, 2.0)
        self.assertLessEqual(speed, 3.5)
        
        speed = self.builder._estimate_mount_speed("Dewback")
        self.assertGreaterEqual(speed, 1.0)
        self.assertLessEqual(speed, 2.0)
    
    def test_build_mount_preferences_for_type(self):
        """Test building mount preferences by type."""
        prefs = self.builder._build_mount_preferences_for_type("speeder")
        self.assertIn("desert", prefs["terrain"])
        self.assertIn("grassland", prefs["terrain"])
        self.assertIn("urban", prefs["terrain"])
        
        prefs = self.builder._build_mount_preferences_for_type("creature")
        self.assertIn("desert", prefs["terrain"])
        self.assertIn("grassland", prefs["terrain"])
        self.assertIn("sandstorm", prefs["weather"])
    
    def test_calculate_mount_statistics(self):
        """Test mount statistics calculation."""
        mount_inventory = {
            "Speederbike": MountInfo("Speederbike", "speeder", 2.5, True),
            "Dewback": MountInfo("Dewback", "creature", 1.5, True),
            "Jetpack": MountInfo("Jetpack", "flying", 3.0, True)
        }
        available_mounts = ["Speederbike", "Dewback", "Jetpack"]
        
        stats = self.builder._calculate_mount_statistics(mount_inventory, available_mounts)
        
        self.assertEqual(stats["total_mounts"], 3)
        self.assertEqual(stats["available_mounts"], 3)
        self.assertEqual(stats["learned_mounts"], 3)
        self.assertEqual(stats["fastest_mount"], "Jetpack")
        self.assertEqual(stats["slowest_mount"], "Dewback")
        self.assertIn("speeder", stats["mount_types"])
        self.assertIn("creature", stats["mount_types"])
        self.assertIn("flying", stats["mount_types"])
    
    def test_build_mount_preferences(self):
        """Test building character mount preferences."""
        mount_inventory = {
            "Speederbike": MountInfo("Speederbike", "speeder", 2.5, True),
            "Dewback": MountInfo("Dewback", "creature", 1.5, True)
        }
        
        # Test Jedi character
        prefs = self.builder._build_mount_preferences("JediMaster", mount_inventory)
        self.assertEqual(prefs["preferred_mount_type"], "flying")
        self.assertEqual(prefs["preferred_speed_range"], "fast")
        
        # Test Bounty Hunter character
        prefs = self.builder._build_mount_preferences("BountyHunter", mount_inventory)
        self.assertEqual(prefs["preferred_mount_type"], "speeder")
        self.assertEqual(prefs["preferred_speed_range"], "fast")
        
        # Test Trader character
        prefs = self.builder._build_mount_preferences("TraderMerchant", mount_inventory)
        self.assertEqual(prefs["preferred_mount_type"], "creature")
        self.assertEqual(prefs["preferred_speed_range"], "medium")
    
    def test_scan_character_mounts(self):
        """Test scanning character mounts."""
        learned_mounts = ["Speederbike", "Dewback"]
        available_mounts = ["Speederbike", "Dewback"]
        
        profile = self.builder.scan_character_mounts("TestCharacter", learned_mounts, available_mounts)
        
        self.assertEqual(profile.character_name, "TestCharacter")
        self.assertEqual(profile.total_mounts, 2)
        self.assertEqual(profile.learned_mounts, 2)
        self.assertEqual(profile.available_mounts, 2)
        self.assertIn("Speederbike", profile.mount_inventory)
        self.assertIn("Dewback", profile.mount_inventory)
    
    def test_save_and_load_character_profile(self):
        """Test saving and loading character profiles."""
        # Create a test profile
        mount_inventory = {
            "Speederbike": MountInfo("Speederbike", "speeder", 2.5, True)
        }
        
        profile = CharacterMountProfile(
            character_name="TestCharacter",
            scan_timestamp=datetime.now().isoformat(),
            total_mounts=1,
            learned_mounts=1,
            available_mounts=1,
            mount_inventory=mount_inventory,
            mount_statistics={"total_mounts": 1},
            preferences={"preferred_mount_type": "speeder"}
        )
        
        # Save profile
        success = self.builder._save_character_profile(profile)
        self.assertTrue(success)
        
        # Load profile
        loaded_profile = self.builder.load_character_profile("TestCharacter")
        self.assertIsNotNone(loaded_profile)
        self.assertEqual(loaded_profile.character_name, "TestCharacter")
        self.assertEqual(loaded_profile.total_mounts, 1)
        self.assertIn("Speederbike", loaded_profile.mount_inventory)
    
    def test_export_mount_data(self):
        """Test mount data export."""
        # Create a test profile first
        mount_inventory = {
            "Speederbike": MountInfo("Speederbike", "speeder", 2.5, True)
        }
        
        profile = CharacterMountProfile(
            character_name="TestCharacter",
            scan_timestamp=datetime.now().isoformat(),
            total_mounts=1,
            learned_mounts=1,
            available_mounts=1,
            mount_inventory=mount_inventory,
            mount_statistics={"total_mounts": 1},
            preferences={"preferred_mount_type": "speeder"}
        )
        
        self.builder._save_character_profile(profile)
        
        # Test JSON export
        export_file = self.builder.export_mount_data("TestCharacter", "json")
        self.assertTrue(Path(export_file).exists())
        
        # Test CSV export
        export_file = self.builder.export_mount_data("TestCharacter", "csv")
        self.assertTrue(Path(export_file).exists())
    
    def test_export_invalid_format(self):
        """Test export with invalid format."""
        with self.assertRaises(ValueError):
            self.builder.export_mount_data("TestCharacter", "invalid")

class TestMountProfileIntegration(unittest.TestCase):
    """Test the MountProfileIntegration class."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.integration = MountProfileIntegration()
        self.integration.mount_profile_builder.data_dir = self.test_dir
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_scan_mounts_on_login(self):
        """Test scanning mounts on login."""
        learned_mounts = ["Speederbike", "Dewback"]
        available_mounts = ["Speederbike", "Dewback"]
        
        profile = self.integration.scan_mounts_on_login("TestCharacter", learned_mounts, available_mounts)
        
        self.assertEqual(profile.character_name, "TestCharacter")
        self.assertEqual(profile.total_mounts, 2)
        self.assertEqual(len(self.integration.scan_events), 1)
        
        # Check scan event
        event = self.integration.scan_events[0]
        self.assertEqual(event.character_name, "TestCharacter")
        self.assertEqual(event.mount_count, 2)
        self.assertTrue(event.profile_created)
    
    def test_get_character_mount_profile(self):
        """Test getting character mount profile."""
        # Create a test profile first
        learned_mounts = ["Speederbike"]
        self.integration.scan_mounts_on_login("TestCharacter", learned_mounts)
        
        profile = self.integration.get_character_mount_profile("TestCharacter")
        self.assertIsNotNone(profile)
        self.assertEqual(profile.character_name, "TestCharacter")
    
    def test_get_mount_statistics(self):
        """Test getting mount statistics."""
        # Create a test profile first
        learned_mounts = ["Speederbike", "Dewback"]
        self.integration.scan_mounts_on_login("TestCharacter", learned_mounts)
        
        stats = self.integration.get_mount_statistics("TestCharacter")
        self.assertIsNotNone(stats)
        self.assertEqual(stats["total_mounts"], 2)
    
    def test_get_mount_preferences(self):
        """Test getting mount preferences."""
        # Create a test profile first
        learned_mounts = ["Speederbike"]
        self.integration.scan_mounts_on_login("TestCharacter", learned_mounts)
        
        prefs = self.integration.get_mount_preferences("TestCharacter")
        self.assertIsNotNone(prefs)
        self.assertIn("preferred_mount_type", prefs)
    
    def test_get_fastest_mount(self):
        """Test getting fastest mount."""
        # Create a test profile first
        learned_mounts = ["Speederbike", "Dewback"]
        self.integration.scan_mounts_on_login("TestCharacter", learned_mounts)
        
        fastest = self.integration.get_fastest_mount("TestCharacter")
        self.assertIsNotNone(fastest)
    
    def test_get_mounts_by_type(self):
        """Test getting mounts by type."""
        # Create a test profile first
        learned_mounts = ["Speederbike", "Dewback"]
        self.integration.scan_mounts_on_login("TestCharacter", learned_mounts)
        
        speeder_mounts = self.integration.get_mounts_by_type("TestCharacter", "speeder")
        self.assertGreater(len(speeder_mounts), 0)
        
        creature_mounts = self.integration.get_mounts_by_type("TestCharacter", "creature")
        self.assertGreater(len(creature_mounts), 0)
    
    def test_get_available_mounts(self):
        """Test getting available mounts."""
        # Create a test profile first
        learned_mounts = ["Speederbike", "Dewback"]
        self.integration.scan_mounts_on_login("TestCharacter", learned_mounts)
        
        available_mounts = self.integration.get_available_mounts("TestCharacter")
        self.assertEqual(len(available_mounts), 2)
    
    def test_get_session_statistics(self):
        """Test getting session statistics."""
        # Create some scan events
        learned_mounts = ["Speederbike"]
        self.integration.scan_mounts_on_login("Character1", learned_mounts)
        self.integration.scan_mounts_on_login("Character2", learned_mounts)
        
        stats = self.integration.get_session_statistics()
        self.assertEqual(stats["total_scans"], 2)
        self.assertEqual(len(stats["characters_scanned"]), 2)
        self.assertEqual(stats["total_mounts_found"], 2)
        self.assertEqual(stats["profiles_created"], 2)
    
    def test_export_session_data(self):
        """Test exporting session data."""
        # Create some scan events
        learned_mounts = ["Speederbike"]
        self.integration.scan_mounts_on_login("TestCharacter", learned_mounts)
        
        session_data = self.integration.export_session_data()
        self.assertIn("scan_events", session_data)
        self.assertIn("statistics", session_data)
        self.assertEqual(len(session_data["scan_events"]), 1)
    
    def test_clear_session_data(self):
        """Test clearing session data."""
        # Create some scan events
        learned_mounts = ["Speederbike"]
        self.integration.scan_mounts_on_login("TestCharacter", learned_mounts)
        
        self.assertEqual(len(self.integration.scan_events), 1)
        
        self.integration.clear_session_data()
        self.assertEqual(len(self.integration.scan_events), 0)
    
    def test_sync_to_dashboard(self):
        """Test dashboard synchronization."""
        # Create a test profile first
        learned_mounts = ["Speederbike", "Dewback"]
        self.integration.scan_mounts_on_login("TestCharacter", learned_mounts)
        
        dashboard_data = self.integration.sync_to_dashboard("TestCharacter")
        
        self.assertNotIn("error", dashboard_data)
        self.assertEqual(dashboard_data["character_name"], "TestCharacter")
        self.assertEqual(dashboard_data["total_mounts"], 2)
        self.assertIn("mounts", dashboard_data)
        self.assertIn("statistics", dashboard_data)
        self.assertIn("preferences", dashboard_data)
    
    def test_sync_to_dashboard_no_profile(self):
        """Test dashboard sync with non-existent profile."""
        dashboard_data = self.integration.sync_to_dashboard("NonExistentCharacter")
        
        self.assertIn("error", dashboard_data)
    
    def test_update_mount_usage(self):
        """Test updating mount usage."""
        # Create a test profile first
        learned_mounts = ["Speederbike"]
        self.integration.scan_mounts_on_login("TestCharacter", learned_mounts)
        
        # Update usage
        success = self.integration.update_mount_usage("TestCharacter", "Speederbike")
        self.assertTrue(success)
        
        # Check updated profile
        profile = self.integration.get_character_mount_profile("TestCharacter")
        mount = profile.mount_inventory["Speederbike"]
        self.assertEqual(mount.usage_count, 1)
        self.assertIsNotNone(mount.last_used)

class TestGlobalFunctions(unittest.TestCase):
    """Test global helper functions."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_get_mount_profile_builder(self):
        """Test getting global mount profile builder."""
        builder1 = get_mount_profile_builder()
        builder2 = get_mount_profile_builder()
        
        # Should return the same instance
        self.assertIs(builder1, builder2)
    
    def test_get_mount_profile_integration(self):
        """Test getting global mount profile integration."""
        integration1 = get_mount_profile_integration()
        integration2 = get_mount_profile_integration()
        
        # Should return the same instance
        self.assertIs(integration1, integration2)
    
    def test_scan_character_mounts(self):
        """Test global scan_character_mounts function."""
        with patch('core.mount_profile_builder.get_mount_profile_builder') as mock_get_builder:
            mock_builder = MagicMock()
            mock_get_builder.return_value = mock_builder
            
            # Mock the scan result
            mock_profile = MagicMock()
            mock_builder.scan_character_mounts.return_value = mock_profile
            
            result = scan_character_mounts("TestCharacter", ["Speederbike"])
            
            mock_builder.scan_character_mounts.assert_called_once_with("TestCharacter", ["Speederbike"], None)
            self.assertEqual(result, mock_profile)
    
    def test_scan_mounts_on_login(self):
        """Test global scan_mounts_on_login function."""
        with patch('core.mount_profile_integration.get_mount_profile_integration') as mock_get_integration:
            mock_integration = MagicMock()
            mock_get_integration.return_value = mock_integration
            
            # Mock the scan result
            mock_profile = MagicMock()
            mock_integration.scan_mounts_on_login.return_value = mock_profile
            
            result = scan_mounts_on_login("TestCharacter", ["Speederbike"])
            
            mock_integration.scan_mounts_on_login.assert_called_once_with("TestCharacter", ["Speederbike"], None)
            self.assertEqual(result, mock_profile)

class TestDataPersistence(unittest.TestCase):
    """Test data persistence and error handling."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.builder = MountProfileBuilder(str(self.test_dir))
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    
    def test_corrupted_json_handling(self):
        """Test handling of corrupted JSON files."""
        # Create a corrupted JSON file
        profile_file = self.test_dir / "TestCharacter.json"
        with open(profile_file, 'w') as f:
            f.write("{ invalid json content")
        
        # Should handle gracefully
        profile = self.builder.load_character_profile("TestCharacter")
        self.assertIsNone(profile)
    
    def test_missing_file_handling(self):
        """Test handling of missing files."""
        profile = self.builder.load_character_profile("NonExistentCharacter")
        self.assertIsNone(profile)
    
    def test_empty_mount_database(self):
        """Test handling of empty mount database."""
        with patch('core.mount_profile_builder.Path') as mock_path:
            mock_yaml_file = MagicMock()
            mock_yaml_file.exists.return_value = False
            mock_json_file = MagicMock()
            mock_json_file.exists.return_value = False
            mock_path.side_effect = [mock_yaml_file, mock_json_file]
            
            builder = MountProfileBuilder()
            self.assertEqual(builder.mount_database, {"mounts": {}})

if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2) 