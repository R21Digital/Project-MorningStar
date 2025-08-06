#!/usr/bin/env python3
"""
Batch 151 - Rare Loot System (RLS) Farming Mode Tests

This test suite covers all RLS farming functionality:
- Data model validation and creation
- Session management and tracking
- Zone and target configuration
- Loot acquisition and verification
- Error handling and edge cases
- Integration with MS11 session management
"""

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import Mock, patch

from core.rare_loot_farming import (
    get_rare_loot_farmer,
    RareLootFarmer,
    DropZone,
    EnemyInfo,
    LootTarget,
    FarmingSession,
    LootAcquisition,
    DropRarity,
    EnemyType
)
from android_ms11.modes.rare_loot_farm import (
    list_available_zones,
    list_target_items,
    get_farming_recommendations,
    get_session_statistics
)


class TestDataModels(unittest.TestCase):
    """Test data model creation and validation."""
    
    def test_drop_zone_creation(self):
        """Test DropZone dataclass creation."""
        zone = DropZone(
            name="Test Zone",
            planet="tatooine",
            coordinates=(1000, 1000),
            patrol_radius=300,
            enemy_types=["Test Enemy"],
            spawn_rate=0.5,
            respawn_time=60,
            difficulty="rare",
            notes="Test zone"
        )
        
        self.assertEqual(zone.name, "Test Zone")
        self.assertEqual(zone.planet, "tatooine")
        self.assertEqual(zone.coordinates, (1000, 1000))
        self.assertEqual(zone.patrol_radius, 300)
        self.assertEqual(zone.enemy_types, ["Test Enemy"])
        self.assertEqual(zone.spawn_rate, 0.5)
        self.assertEqual(zone.respawn_time, 60)
        self.assertEqual(zone.difficulty, "rare")
        self.assertEqual(zone.notes, "Test zone")
    
    def test_enemy_info_creation(self):
        """Test EnemyInfo dataclass creation."""
        enemy = EnemyInfo(
            name="Test Enemy",
            type=EnemyType.MONSTER,
            level=50,
            health=10000,
            drops=[
                {"name": "Test Item", "rarity": "rare", "drop_rate": 0.1}
            ],
            drop_percentage=0.8,
            respawn_time=90,
            spawn_locations=[(1000, 1000), (1100, 1100)]
        )
        
        self.assertEqual(enemy.name, "Test Enemy")
        self.assertEqual(enemy.type, EnemyType.MONSTER)
        self.assertEqual(enemy.level, 50)
        self.assertEqual(enemy.health, 10000)
        self.assertEqual(len(enemy.drops), 1)
        self.assertEqual(enemy.drop_percentage, 0.8)
        self.assertEqual(enemy.respawn_time, 90)
        self.assertEqual(len(enemy.spawn_locations), 2)
    
    def test_loot_target_creation(self):
        """Test LootTarget dataclass creation."""
        target = LootTarget(
            name="Test Item",
            rarity=DropRarity.RARE,
            drop_zones=["test_zone"],
            enemy_types=["Test Enemy"],
            drop_percentage=0.1,
            value=5000,
            notes="Test target",
            priority=3
        )
        
        self.assertEqual(target.name, "Test Item")
        self.assertEqual(target.rarity, DropRarity.RARE)
        self.assertEqual(target.drop_zones, ["test_zone"])
        self.assertEqual(target.enemy_types, ["Test Enemy"])
        self.assertEqual(target.drop_percentage, 0.1)
        self.assertEqual(target.value, 5000)
        self.assertEqual(target.notes, "Test target")
        self.assertEqual(target.priority, 3)
    
    def test_farming_session_creation(self):
        """Test FarmingSession dataclass creation."""
        session = FarmingSession(
            session_id="test_session",
            start_time="2025-01-17T10:00:00",
            target_zone="test_zone",
            target_items=["Test Item"],
            loot_found=[],
            enemies_killed=0,
            session_duration=0,
            status="active"
        )
        
        self.assertEqual(session.session_id, "test_session")
        self.assertEqual(session.target_zone, "test_zone")
        self.assertEqual(session.target_items, ["Test Item"])
        self.assertEqual(session.status, "active")
    
    def test_loot_acquisition_creation(self):
        """Test LootAcquisition dataclass creation."""
        acquisition = LootAcquisition(
            item_name="Test Item",
            rarity=DropRarity.RARE,
            drop_zone="test_zone",
            enemy_name="Test Enemy",
            coordinates=(1000, 1000),
            timestamp="2025-01-17T10:00:00",
            session_id="test_session",
            verified=True
        )
        
        self.assertEqual(acquisition.item_name, "Test Item")
        self.assertEqual(acquisition.rarity, DropRarity.RARE)
        self.assertEqual(acquisition.drop_zone, "test_zone")
        self.assertEqual(acquisition.enemy_name, "Test Enemy")
        self.assertEqual(acquisition.coordinates, (1000, 1000))
        self.assertEqual(acquisition.session_id, "test_session")
        self.assertTrue(acquisition.verified)


class TestRareLootFarmer(unittest.TestCase):
    """Test the main RareLootFarmer class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.test_dir) / "data" / "rls_farming"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Mock session manager
        self.mock_session_manager = Mock()
        
        # Create farmer instance
        with patch('core.rare_loot_farming.Path') as mock_path:
            mock_path.return_value = self.data_dir
            self.farmer = RareLootFarmer(self.mock_session_manager)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test farmer initialization."""
        self.assertIsNotNone(self.farmer)
        self.assertEqual(self.farmer.session_manager, self.mock_session_manager)
        self.assertIsInstance(self.farmer.drop_zones, dict)
        self.assertIsInstance(self.farmer.enemy_types, dict)
        self.assertIsInstance(self.farmer.loot_targets, dict)
        self.assertIsInstance(self.farmer.farming_sessions, dict)
    
    def test_start_farming_session(self):
        """Test starting a farming session."""
        # Add a test zone
        test_zone = DropZone(
            name="test_zone",
            planet="tatooine",
            coordinates=(1000, 1000),
            patrol_radius=300,
            enemy_types=["Test Enemy"],
            spawn_rate=0.5,
            respawn_time=60,
            difficulty="rare"
        )
        self.farmer.drop_zones["test_zone"] = test_zone
        
        # Start session
        session = self.farmer.start_farming_session("test_zone", ["Test Item"])
        
        self.assertIsNotNone(session)
        self.assertEqual(session.target_zone, "test_zone")
        self.assertEqual(session.target_items, ["Test Item"])
        self.assertEqual(session.status, "active")
        self.assertIsNotNone(session.session_id)
        
        # Check that session is stored
        self.assertIn(session.session_id, self.farmer.farming_sessions)
        self.assertEqual(self.farmer.current_session, session)
    
    def test_start_farming_session_invalid_zone(self):
        """Test starting session with invalid zone."""
        with self.assertRaises(ValueError):
            self.farmer.start_farming_session("invalid_zone", ["Test Item"])
    
    def test_end_farming_session(self):
        """Test ending a farming session."""
        # Start a session first
        test_zone = DropZone(
            name="test_zone",
            planet="tatooine",
            coordinates=(1000, 1000),
            patrol_radius=300,
            enemy_types=["Test Enemy"],
            spawn_rate=0.5,
            respawn_time=60,
            difficulty="rare"
        )
        self.farmer.drop_zones["test_zone"] = test_zone
        
        session = self.farmer.start_farming_session("test_zone", ["Test Item"])
        
        # End session
        completed_session = self.farmer.end_farming_session()
        
        self.assertIsNotNone(completed_session)
        self.assertEqual(completed_session.status, "completed")
        self.assertIsNone(self.farmer.current_session)
        self.assertIsNone(self.farmer.current_zone)
    
    def test_end_farming_session_no_active(self):
        """Test ending session when no active session."""
        result = self.farmer.end_farming_session()
        self.assertIsNone(result)
    
    def test_record_loot_acquisition(self):
        """Test recording loot acquisition."""
        # Start a session first
        test_zone = DropZone(
            name="test_zone",
            planet="tatooine",
            coordinates=(1000, 1000),
            patrol_radius=300,
            enemy_types=["Test Enemy"],
            spawn_rate=0.5,
            respawn_time=60,
            difficulty="rare"
        )
        self.farmer.drop_zones["test_zone"] = test_zone
        
        session = self.farmer.start_farming_session("test_zone", ["Test Item"])
        
        # Record loot acquisition
        acquisition = self.farmer.record_loot_acquisition(
            item_name="Test Item",
            enemy_name="Test Enemy",
            coordinates=(1000, 1000)
        )
        
        self.assertIsNotNone(acquisition)
        self.assertEqual(acquisition.item_name, "Test Item")
        self.assertEqual(acquisition.enemy_name, "Test Enemy")
        self.assertEqual(acquisition.coordinates, (1000, 1000))
        self.assertEqual(acquisition.session_id, session.session_id)
        self.assertTrue(acquisition.verified)
        
        # Check that it's added to session
        self.assertIn(acquisition.item_name, [item.get('item_name') for item in session.loot_found])
    
    def test_record_loot_acquisition_no_session(self):
        """Test recording loot when no active session."""
        with self.assertRaises(RuntimeError):
            self.farmer.record_loot_acquisition("Test Item", "Test Enemy", (1000, 1000))
    
    def test_get_optimal_farming_route(self):
        """Test optimal farming route calculation."""
        # Add test zones and targets
        test_zone = DropZone(
            name="test_zone",
            planet="tatooine",
            coordinates=(1000, 1000),
            patrol_radius=300,
            enemy_types=["Test Enemy"],
            spawn_rate=0.5,
            respawn_time=60,
            difficulty="rare"
        )
        self.farmer.drop_zones["test_zone"] = test_zone
        
        test_target = LootTarget(
            name="Test Item",
            rarity=DropRarity.RARE,
            drop_zones=["test_zone"],
            enemy_types=["Test Enemy"],
            drop_percentage=0.1,
            value=5000,
            priority=3
        )
        self.farmer.loot_targets["test_item"] = test_target
        
        # Get optimal route
        route = self.farmer.get_optimal_farming_route(["Test Item"])
        
        self.assertIsInstance(route, list)
        self.assertEqual(len(route), 1)
        self.assertEqual(route[0].name, "test_zone")
    
    def test_get_session_statistics(self):
        """Test session statistics calculation."""
        # Create a test session
        session = FarmingSession(
            session_id="test_session",
            start_time="2025-01-17T10:00:00",
            target_zone="test_zone",
            target_items=["Test Item"],
            loot_found=[
                {"item_name": "Test Item", "rarity": "rare", "value": 5000}
            ],
            enemies_killed=5,
            session_duration=30,
            status="completed"
        )
        
        self.farmer.farming_sessions["test_session"] = session
        
        # Add test target for value calculation
        test_target = LootTarget(
            name="Test Item",
            rarity=DropRarity.RARE,
            drop_zones=["test_zone"],
            enemy_types=["Test Enemy"],
            drop_percentage=0.1,
            value=5000,
            priority=3
        )
        self.farmer.loot_targets["test_item"] = test_target
        
        # Get statistics
        stats = self.farmer.get_session_statistics("test_session")
        
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats.get("session_id"), "test_session")
        self.assertEqual(stats.get("items_found"), 1)
        self.assertEqual(stats.get("total_value"), 5000)
        self.assertEqual(stats.get("enemies_killed"), 5)
        self.assertEqual(stats.get("duration_minutes"), 30)
    
    def test_get_session_statistics_invalid_session(self):
        """Test statistics for invalid session."""
        stats = self.farmer.get_session_statistics("invalid_session")
        self.assertEqual(stats, {})
    
    def test_export_session_data(self):
        """Test session data export."""
        # Create a test session
        session = FarmingSession(
            session_id="test_session",
            start_time="2025-01-17T10:00:00",
            target_zone="test_zone",
            target_items=["Test Item"],
            loot_found=[],
            enemies_killed=0,
            session_duration=0,
            status="completed"
        )
        
        self.farmer.farming_sessions["test_session"] = session
        
        # Export data
        export_path = self.farmer.export_session_data("test_session")
        
        self.assertIsInstance(export_path, str)
        self.assertTrue(Path(export_path).exists())
        
        # Check export content
        with open(export_path, 'r') as f:
            export_data = json.load(f)
        
        self.assertIn("session", export_data)
        self.assertIn("statistics", export_data)
        self.assertIn("loot_acquisitions", export_data)
    
    def test_export_session_data_invalid_session(self):
        """Test export for invalid session."""
        with self.assertRaises(ValueError):
            self.farmer.export_session_data("invalid_session")
    
    def test_export_session_data_invalid_format(self):
        """Test export with invalid format."""
        session = FarmingSession(
            session_id="test_session",
            start_time="2025-01-17T10:00:00",
            target_zone="test_zone",
            target_items=["Test Item"],
            loot_found=[],
            enemies_killed=0,
            session_duration=0,
            status="completed"
        )
        
        self.farmer.farming_sessions["test_session"] = session
        
        with self.assertRaises(ValueError):
            self.farmer.export_session_data("test_session", "invalid_format")


class TestIntegration(unittest.TestCase):
    """Test integration with MS11 session management."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.test_dir) / "data" / "rls_farming"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Mock session manager
        self.mock_session_manager = Mock()
        self.mock_session_manager.add_action = Mock()
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_session_manager_integration(self):
        """Test integration with session manager."""
        with patch('core.rare_loot_farming.Path') as mock_path:
            mock_path.return_value = self.data_dir
            farmer = RareLootFarmer(self.mock_session_manager)
        
        # Add test zone
        test_zone = DropZone(
            name="test_zone",
            planet="tatooine",
            coordinates=(1000, 1000),
            patrol_radius=300,
            enemy_types=["Test Enemy"],
            spawn_rate=0.5,
            respawn_time=60,
            difficulty="rare"
        )
        farmer.drop_zones["test_zone"] = test_zone
        
        # Start session
        session = farmer.start_farming_session("test_zone", ["Test Item"])
        
        # Check that session manager was called
        self.mock_session_manager.add_action.assert_called_with(
            "Started RLS farming in test_zone"
        )
        
        # Record loot
        acquisition = farmer.record_loot_acquisition(
            item_name="Test Item",
            enemy_name="Test Enemy",
            coordinates=(1000, 1000)
        )
        
        # Check that session manager was called for loot
        self.mock_session_manager.add_action.assert_called_with(
            "Found rare loot: Test Item"
        )
        
        # End session
        completed_session = farmer.end_farming_session()
        
        # Check that session manager was called for completion
        self.mock_session_manager.add_action.assert_called_with(
            "Completed RLS farming session: 1 items found"
        )


class TestErrorHandling(unittest.TestCase):
    """Test error handling and edge cases."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.test_dir) / "data" / "rls_farming"
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.test_dir)
    
    def test_corrupted_config_files(self):
        """Test handling of corrupted configuration files."""
        # Create corrupted JSON files
        zones_file = self.data_dir / "drop_zones.json"
        with open(zones_file, 'w') as f:
            f.write("invalid json content")
        
        enemies_file = self.data_dir / "enemy_types.json"
        with open(enemies_file, 'w') as f:
            f.write("invalid json content")
        
        targets_file = self.data_dir / "target_items.json"
        with open(targets_file, 'w') as f:
            f.write("invalid json content")
        
        # Should not raise exception, should create defaults
        with patch('core.rare_loot_farming.Path') as mock_path:
            mock_path.return_value = self.data_dir
            farmer = RareLootFarmer()
        
        # Should have default data
        self.assertGreater(len(farmer.drop_zones), 0)
        self.assertGreater(len(farmer.enemy_types), 0)
        self.assertGreater(len(farmer.loot_targets), 0)
    
    def test_missing_config_files(self):
        """Test handling of missing configuration files."""
        # Don't create any config files
        with patch('core.rare_loot_farming.Path') as mock_path:
            mock_path.return_value = self.data_dir
            farmer = RareLootFarmer()
        
        # Should create default data
        self.assertGreater(len(farmer.drop_zones), 0)
        self.assertGreater(len(farmer.enemy_types), 0)
        self.assertGreater(len(farmer.loot_targets), 0)
    
    def test_invalid_coordinates(self):
        """Test handling of invalid coordinates."""
        with patch('core.rare_loot_farming.Path') as mock_path:
            mock_path.return_value = self.data_dir
            farmer = RareLootFarmer()
        
        # Add test zone
        test_zone = DropZone(
            name="test_zone",
            planet="tatooine",
            coordinates=(1000, 1000),
            patrol_radius=300,
            enemy_types=["Test Enemy"],
            spawn_rate=0.5,
            respawn_time=60,
            difficulty="rare"
        )
        farmer.drop_zones["test_zone"] = test_zone
        
        session = farmer.start_farming_session("test_zone", ["Test Item"])
        
        # Test with invalid coordinates
        with self.assertRaises(TypeError):
            farmer.record_loot_acquisition("Test Item", "Test Enemy", "invalid_coords")


class TestCLIFunctions(unittest.TestCase):
    """Test CLI helper functions."""
    
    def test_list_available_zones(self):
        """Test list_available_zones function."""
        zones = list_available_zones()
        self.assertIsInstance(zones, list)
        
        if zones:
            zone = zones[0]
            self.assertIn('name', zone)
            self.assertIn('display_name', zone)
            self.assertIn('planet', zone)
            self.assertIn('coordinates', zone)
    
    def test_list_target_items(self):
        """Test list_target_items function."""
        items = list_target_items()
        self.assertIsInstance(items, list)
        
        if items:
            item = items[0]
            self.assertIn('name', item)
            self.assertIn('display_name', item)
            self.assertIn('rarity', item)
            self.assertIn('value', item)
    
    def test_get_farming_recommendations(self):
        """Test get_farming_recommendations function."""
        recommendations = get_farming_recommendations()
        self.assertIsInstance(recommendations, list)
        
        if recommendations:
            rec = recommendations[0]
            self.assertIn('target_item', rec)
            self.assertIn('drop_zone', rec)
            self.assertIn('efficiency_score', rec)
    
    def test_get_session_statistics(self):
        """Test get_session_statistics function."""
        # Test with invalid session
        stats = get_session_statistics("invalid_session")
        self.assertEqual(stats, {})


if __name__ == "__main__":
    unittest.main() 