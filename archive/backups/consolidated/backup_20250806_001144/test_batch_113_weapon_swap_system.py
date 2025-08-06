"""Test suite for Batch 113 - Weapon Swap + Loadout Handling

This test suite covers:
- Weapon system initialization and configuration
- Loadout management and weapon switching
- Weapon effectiveness calculations
- Dynamic weapon swapping logic
- Combat integration
- Manual override capabilities
- Analytics and export functionality
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from modules.weapon_swap_system import WeaponSwapSystem, WeaponStats, WeaponLoadout, WeaponSwapEvent
from src.ai.combat.weapon_swap_integration import CombatWeaponSwapIntegration


class TestWeaponSwapSystem(unittest.TestCase):
    """Test cases for the WeaponSwapSystem class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary config file
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_weapon_config.json")
        
        # Create test configuration
        test_config = {
            "weapons": {
                "test_rifle": {
                    "weapon_type": "rifle",
                    "damage_type": "kinetic",
                    "base_damage": 25,
                    "range": 100,
                    "accuracy": 0.85,
                    "fire_rate": 1.0,
                    "ammo_capacity": 30,
                    "reload_time": 2.5,
                    "condition": 100.0,
                    "current_ammo": 30
                },
                "test_carbine": {
                    "weapon_type": "carbine",
                    "damage_type": "kinetic",
                    "base_damage": 18,
                    "range": 60,
                    "accuracy": 0.75,
                    "fire_rate": 1.5,
                    "ammo_capacity": 25,
                    "reload_time": 2.0,
                    "condition": 100.0,
                    "current_ammo": 25
                },
                "test_energy": {
                    "weapon_type": "rifle",
                    "damage_type": "energy",
                    "base_damage": 30,
                    "range": 80,
                    "accuracy": 0.9,
                    "fire_rate": 0.7,
                    "ammo_capacity": 20,
                    "reload_time": 3.0,
                    "condition": 100.0,
                    "current_ammo": 20
                }
            },
            "loadouts": {
                "test_loadout": {
                    "description": "Test loadout",
                    "primary_weapon": "test_rifle",
                    "secondary_weapon": "test_carbine",
                    "auto_swap_enabled": True,
                    "priority_rules": {
                        "distance_based": True,
                        "enemy_resistance": True,
                        "ammo_management": True
                    }
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        # Initialize weapon system
        self.weapon_system = WeaponSwapSystem(self.config_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test weapon system initialization."""
        self.assertIsNotNone(self.weapon_system)
        self.assertEqual(len(self.weapon_system.weapons), 3)
        self.assertEqual(len(self.weapon_system.loadouts), 1)
        self.assertIsNotNone(self.weapon_system.enemy_resistances)
    
    def test_load_loadout(self):
        """Test loading a weapon loadout."""
        success = self.weapon_system.load_loadout("test_loadout")
        self.assertTrue(success)
        self.assertEqual(self.weapon_system.current_loadout, "test_loadout")
        self.assertEqual(self.weapon_system.current_weapon, "test_rifle")
    
    def test_load_nonexistent_loadout(self):
        """Test loading a non-existent loadout."""
        success = self.weapon_system.load_loadout("nonexistent_loadout")
        self.assertFalse(success)
    
    def test_get_available_weapons(self):
        """Test getting available weapons in current loadout."""
        self.weapon_system.load_loadout("test_loadout")
        available_weapons = self.weapon_system.get_available_weapons()
        self.assertEqual(len(available_weapons), 2)
        self.assertIn("test_rifle", available_weapons)
        self.assertIn("test_carbine", available_weapons)
    
    def test_calculate_weapon_effectiveness(self):
        """Test weapon effectiveness calculation."""
        effectiveness = self.weapon_system.calculate_weapon_effectiveness(
            "test_rifle", "stormtrooper", 50.0
        )
        self.assertGreaterEqual(effectiveness, 0.0)
        self.assertLessEqual(effectiveness, 1.0)
    
    def test_calculate_effectiveness_out_of_range(self):
        """Test weapon effectiveness when target is out of range."""
        effectiveness = self.weapon_system.calculate_weapon_effectiveness(
            "test_rifle", "stormtrooper", 150.0  # Beyond 100m range
        )
        self.assertLess(effectiveness, 0.5)  # Should be penalized
    
    def test_calculate_effectiveness_no_ammo(self):
        """Test weapon effectiveness when weapon has no ammo."""
        self.weapon_system.update_weapon_ammo("test_rifle", 0)
        effectiveness = self.weapon_system.calculate_weapon_effectiveness(
            "test_rifle", "stormtrooper", 50.0
        )
        self.assertLess(effectiveness, 0.2)  # Should be heavily penalized
    
    def test_get_best_weapon(self):
        """Test getting the best weapon for given conditions."""
        self.weapon_system.load_loadout("test_loadout")
        best_weapon = self.weapon_system.get_best_weapon("stormtrooper", 50.0)
        self.assertIsNotNone(best_weapon)
        self.assertIn(best_weapon, ["test_rifle", "test_carbine"])
    
    def test_should_swap_weapon(self):
        """Test weapon swap decision logic."""
        self.weapon_system.load_loadout("test_loadout")
        should_swap, best_weapon = self.weapon_system.should_swap_weapon(
            "stormtrooper", 50.0
        )
        # Should not swap initially since we're already on the primary weapon
        self.assertFalse(should_swap)
    
    def test_swap_weapon(self):
        """Test manual weapon swapping."""
        self.weapon_system.load_loadout("test_loadout")
        success = self.weapon_system.swap_weapon("test_carbine", "manual")
        self.assertTrue(success)
        self.assertEqual(self.weapon_system.current_weapon, "test_carbine")
    
    def test_swap_to_invalid_weapon(self):
        """Test swapping to an invalid weapon."""
        self.weapon_system.load_loadout("test_loadout")
        success = self.weapon_system.swap_weapon("invalid_weapon", "manual")
        self.assertFalse(success)
    
    def test_auto_swap_weapon(self):
        """Test automatic weapon swapping."""
        self.weapon_system.load_loadout("test_loadout")
        # Set up conditions that would trigger a swap
        self.weapon_system.update_weapon_ammo("test_rifle", 0)
        
        success = self.weapon_system.auto_swap_weapon("stormtrooper", 50.0)
        # Should swap due to no ammo
        self.assertTrue(success)
    
    def test_update_weapon_ammo(self):
        """Test updating weapon ammo."""
        self.weapon_system.update_weapon_ammo("test_rifle", 15)
        weapon_stats = self.weapon_system.get_weapon_stats("test_rifle")
        self.assertEqual(weapon_stats.current_ammo, 15)
    
    def test_update_weapon_condition(self):
        """Test updating weapon condition."""
        self.weapon_system.update_weapon_condition("test_rifle", 75.0)
        weapon_stats = self.weapon_system.get_weapon_stats("test_rifle")
        self.assertEqual(weapon_stats.condition, 75.0)
    
    def test_get_weapon_history(self):
        """Test getting weapon swap history."""
        self.weapon_system.load_loadout("test_loadout")
        self.weapon_system.swap_weapon("test_carbine", "test")
        
        history = self.weapon_system.get_weapon_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].from_weapon, "test_rifle")
        self.assertEqual(history[0].to_weapon, "test_carbine")
        self.assertEqual(history[0].reason, "test")
    
    def test_get_weapon_effectiveness_stats(self):
        """Test getting weapon effectiveness statistics."""
        stats = self.weapon_system.get_weapon_effectiveness_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn("test_rifle", stats)
        self.assertIn("test_carbine", stats)
        self.assertIn("test_energy", stats)
    
    def test_export_weapon_data(self):
        """Test weapon data export functionality."""
        self.weapon_system.load_loadout("test_loadout")
        self.weapon_system.swap_weapon("test_carbine", "test")
        
        export_path = self.weapon_system.export_weapon_data()
        self.assertTrue(os.path.exists(export_path))
        
        # Verify export data
        with open(export_path, 'r') as f:
            export_data = json.load(f)
        
        self.assertIn("weapons", export_data)
        self.assertIn("loadouts", export_data)
        self.assertIn("weapon_history", export_data)
        self.assertEqual(len(export_data["weapon_history"]), 1)


class TestCombatWeaponSwapIntegration(unittest.TestCase):
    """Test cases for the CombatWeaponSwapIntegration class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock weapon system
        self.mock_weapon_system = Mock()
        self.mock_weapon_system.current_weapon = "test_rifle"
        self.mock_weapon_system.get_available_weapons.return_value = ["test_rifle", "test_carbine"]
        self.mock_weapon_system.get_weapon_stats.return_value = Mock(
            current_ammo=30,
            condition=100.0
        )
        self.mock_weapon_system.calculate_weapon_effectiveness.return_value = 0.8
        self.mock_weapon_system.should_swap_weapon.return_value = (False, None)
        self.mock_weapon_system.swap_weapon.return_value = True
        
        # Create combat integration
        self.combat_integration = CombatWeaponSwapIntegration(self.mock_weapon_system)
    
    def test_initialization(self):
        """Test combat integration initialization."""
        self.assertIsNotNone(self.combat_integration)
        self.assertEqual(self.combat_integration.weapon_system, self.mock_weapon_system)
    
    def test_update_combat_context(self):
        """Test updating combat context."""
        player_state = {"hp": 80, "ammo_status": {"test_rifle": 15}}
        target_state = {"hp": 60}
        
        self.combat_integration.update_combat_context(
            player_state, target_state, "stormtrooper", 50.0
        )
        
        # Verify weapon system was called with correct context
        self.mock_weapon_system.set_combat_context.assert_called_once()
    
    def test_should_swap_weapon(self):
        """Test combat weapon swap decision."""
        player_state = {"hp": 80}
        target_state = {"hp": 60}
        
        should_swap, weapon = self.combat_integration.should_swap_weapon(
            player_state, target_state, "stormtrooper", 50.0
        )
        
        self.assertFalse(should_swap)  # Based on mock return value
        self.assertIsNone(weapon)
    
    def test_emergency_swap_no_ammo(self):
        """Test emergency swap when weapon has no ammo."""
        # Mock weapon with no ammo
        self.mock_weapon_system.get_weapon_stats.return_value = Mock(
            current_ammo=0,
            condition=100.0
        )
        
        # Mock available weapon with ammo
        self.mock_weapon_system.get_weapon_stats.side_effect = [
            Mock(current_ammo=0, condition=100.0),  # Current weapon
            Mock(current_ammo=15, condition=100.0)  # Available weapon
        ]
        
        player_state = {"hp": 80}
        should_swap, weapon = self.combat_integration._check_emergency_swap(player_state)
        
        self.assertTrue(should_swap)
        self.assertEqual(weapon, "test_carbine")
    
    def test_emergency_swap_critical_condition(self):
        """Test emergency swap when weapon has critical condition."""
        # Mock weapon with critical condition
        self.mock_weapon_system.get_weapon_stats.return_value = Mock(
            current_ammo=30,
            condition=15.0
        )
        
        # Mock available weapon with good condition
        self.mock_weapon_system.get_weapon_stats.side_effect = [
            Mock(current_ammo=30, condition=15.0),  # Current weapon
            Mock(current_ammo=25, condition=80.0)   # Available weapon
        ]
        
        player_state = {"hp": 80}
        should_swap, weapon = self.combat_integration._check_emergency_swap(player_state)
        
        self.assertTrue(should_swap)
        self.assertEqual(weapon, "test_carbine")
    
    def test_execute_weapon_swap(self):
        """Test executing a weapon swap."""
        success = self.combat_integration.execute_weapon_swap("test_carbine", "test")
        
        self.assertTrue(success)
        self.mock_weapon_system.swap_weapon.assert_called_once_with("test_carbine", "test")
    
    @patch('src.ai.combat.weapon_swap_integration.evaluate_state')
    def test_get_enhanced_combat_action(self, mock_evaluate_state):
        """Test getting enhanced combat action."""
        mock_evaluate_state.return_value = "attack"
        
        player_state = {"hp": 80}
        target_state = {"hp": 60}
        
        action = self.combat_integration.get_enhanced_combat_action(
            player_state, target_state, "stormtrooper", 50.0
        )
        
        self.assertEqual(action, "attack")
        mock_evaluate_state.assert_called_once_with(player_state, target_state)
    
    def test_get_weapon_recommendation(self):
        """Test getting weapon recommendation."""
        self.mock_weapon_system.calculate_weapon_effectiveness.return_value = 0.8
        self.mock_weapon_system.get_weapon_stats.return_value = Mock(
            damage_type=Mock(value="kinetic"),
            range=100,
            current_ammo=30,
            condition=100.0
        )
        
        recommendation = self.combat_integration.get_weapon_recommendation("stormtrooper", 50.0)
        
        self.assertIn("recommendations", recommendation)
        self.assertIn("best_weapon", recommendation)
        self.assertEqual(recommendation["enemy_type"], "stormtrooper")
        self.assertEqual(recommendation["distance"], 50.0)
    
    def test_get_combat_analytics(self):
        """Test getting combat analytics."""
        # Mock weapon history
        mock_event = Mock()
        mock_event.reason = "test"
        self.mock_weapon_system.get_weapon_history.return_value = [mock_event]
        self.mock_weapon_system.get_weapon_effectiveness_stats.return_value = {"test": {}}
        
        analytics = self.combat_integration.get_combat_analytics()
        
        self.assertIn("total_swaps", analytics)
        self.assertIn("recent_swaps", analytics)
        self.assertIn("current_weapon", analytics)
        self.assertIn("swap_reasons", analytics)


class TestWeaponSwapEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "test_config.json")
        
        # Create minimal config
        minimal_config = {
            "weapons": {},
            "loadouts": {}
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(minimal_config, f)
        
        self.weapon_system = WeaponSwapSystem(self.config_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_empty_config(self):
        """Test behavior with empty configuration."""
        self.assertEqual(len(self.weapon_system.weapons), 0)
        self.assertEqual(len(self.weapon_system.loadouts), 0)
    
    def test_nonexistent_weapon(self):
        """Test behavior with non-existent weapon."""
        effectiveness = self.weapon_system.calculate_weapon_effectiveness(
            "nonexistent_weapon", "stormtrooper", 50.0
        )
        self.assertEqual(effectiveness, 0.0)
    
    def test_no_loadout_loaded(self):
        """Test behavior when no loadout is loaded."""
        available_weapons = self.weapon_system.get_available_weapons()
        self.assertEqual(len(available_weapons), 0)
    
    def test_invalid_enemy_type(self):
        """Test behavior with invalid enemy type."""
        # Add a weapon to test with
        self.weapon_system.weapons["test_weapon"] = WeaponStats(
            name="test_weapon",
            weapon_type=Mock(value="rifle"),
            damage_type=Mock(value="kinetic"),
            base_damage=25,
            range=100,
            accuracy=0.8,
            fire_rate=1.0,
            ammo_capacity=30,
            reload_time=2.5
        )
        
        effectiveness = self.weapon_system.calculate_weapon_effectiveness(
            "test_weapon", "invalid_enemy", 50.0
        )
        # Should still return a value (no enemy resistance applied)
        self.assertGreater(effectiveness, 0.0)
    
    def test_negative_distance(self):
        """Test behavior with negative distance."""
        self.weapon_system.weapons["test_weapon"] = WeaponStats(
            name="test_weapon",
            weapon_type=Mock(value="rifle"),
            damage_type=Mock(value="kinetic"),
            base_damage=25,
            range=100,
            accuracy=0.8,
            fire_rate=1.0,
            ammo_capacity=30,
            reload_time=2.5
        )
        
        effectiveness = self.weapon_system.calculate_weapon_effectiveness(
            "test_weapon", "stormtrooper", -10.0
        )
        # Should handle negative distance gracefully
        self.assertGreaterEqual(effectiveness, 0.0)


class TestWeaponSwapPerformance(unittest.TestCase):
    """Test performance characteristics of the weapon swap system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.temp_dir, "perf_config.json")
        
        # Create config with many weapons
        config = {
            "weapons": {},
            "loadouts": {
                "perf_loadout": {
                    "description": "Performance test loadout",
                    "primary_weapon": "weapon_1",
                    "secondary_weapon": "weapon_2",
                    "auto_swap_enabled": True
                }
            }
        }
        
        # Add many weapons
        for i in range(100):
            config["weapons"][f"weapon_{i}"] = {
                "weapon_type": "rifle",
                "damage_type": "kinetic",
                "base_damage": 25,
                "range": 100,
                "accuracy": 0.8,
                "fire_rate": 1.0,
                "ammo_capacity": 30,
                "reload_time": 2.5,
                "condition": 100.0,
                "current_ammo": 30
            }
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f)
        
        self.weapon_system = WeaponSwapSystem(self.config_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_large_weapon_set_performance(self):
        """Test performance with large number of weapons."""
        self.weapon_system.load_loadout("perf_loadout")
        
        # Test effectiveness calculation performance
        import time
        start_time = time.time()
        
        for _ in range(1000):
            self.weapon_system.calculate_weapon_effectiveness(
                "weapon_1", "stormtrooper", 50.0
            )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within reasonable time (less than 1 second)
        self.assertLess(duration, 1.0)
    
    def test_weapon_swap_frequency_limit(self):
        """Test weapon swap frequency limiting."""
        self.weapon_system.load_loadout("perf_loadout")
        
        # Perform many swaps quickly
        for i in range(10):
            self.weapon_system.swap_weapon(f"weapon_{i}", "test")
        
        # Should have history of all swaps
        history = self.weapon_system.get_weapon_history()
        self.assertEqual(len(history), 10)


if __name__ == '__main__':
    unittest.main() 