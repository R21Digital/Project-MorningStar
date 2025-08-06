#!/usr/bin/env python3
"""
MS11 Batch 084 - Combat Role Engine Test Suite

This test suite verifies the combat role engine functionality including:
- Role-based combat logic and triggers
- Automatic role switching based on group composition
- Role-aware ability prioritization
- Integration with existing combat profiles
"""

import unittest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the project root to the path
import sys
sys.path.insert(0, str(Path(__file__).parent))

def log_event(message: str):
    """Simple logging function for tests."""
    print(f"[TEST] {message}")

# Import the combat role engine components
from core.combat_role_engine import CombatRoleEngine
from core.combat_role_profile_manager import CombatRoleProfileManager

class TestCombatRoleEngine(unittest.TestCase):
    """Test cases for the CombatRoleEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary roles config file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.roles_config_path = os.path.join(self.temp_dir, "roles.json")
        
        # Create test roles configuration
        test_roles_config = {
            "combat_roles": {
                "version": "1.0",
                "roles": {
                    "solo_dps": {
                        "name": "Solo DPS",
                        "description": "Optimized for solo combat",
                        "enabled": True,
                        "behaviors": {
                            "damage_optimization": {"enabled": True, "priority": "high"},
                            "survival": {"enabled": True, "priority": "medium"}
                        },
                        "triggers": {
                            "use_taunt": False,
                            "maintain_aggro": False,
                            "use_group_healing": False,
                            "use_crowd_control": True,
                            "use_escape_abilities": True
                        },
                        "ability_priorities": ["highest_damage_ability", "damage_buff", "defensive_cooldown"]
                    },
                    "healer": {
                        "name": "Healer",
                        "description": "Focused on healing",
                        "enabled": True,
                        "behaviors": {
                            "healing_optimization": {"enabled": True, "priority": "critical"},
                            "survival": {"enabled": True, "priority": "high"}
                        },
                        "triggers": {
                            "use_taunt": False,
                            "maintain_aggro": False,
                            "use_group_healing": True,
                            "use_crowd_control": False,
                            "use_escape_abilities": True
                        },
                        "ability_priorities": ["emergency_heal", "group_heal", "healing_buff"]
                    },
                    "tank": {
                        "name": "Tank",
                        "description": "Focused on aggro management",
                        "enabled": True,
                        "behaviors": {
                            "aggro_management": {"enabled": True, "priority": "critical"},
                            "survival": {"enabled": True, "priority": "high"}
                        },
                        "triggers": {
                            "use_taunt": True,
                            "maintain_aggro": True,
                            "use_group_healing": False,
                            "use_crowd_control": True,
                            "use_escape_abilities": False
                        },
                        "ability_priorities": ["taunt_ability", "aggro_generating_ability", "defensive_cooldown"]
                    }
                },
                "role_switching": {
                    "enabled": True,
                    "auto_switch_to_healer": {"enabled": True, "group_size_threshold": 3},
                    "auto_switch_to_tank": {"enabled": True, "group_size_threshold": 4}
                },
                "logic_triggers": {
                    "tank_triggers": {"use_taunt_if_tank": True, "maintain_aggro": True},
                    "healer_triggers": {"prioritize_group_healing": True, "heal_tank_first": True}
                }
            }
        }
        
        with open(self.roles_config_path, 'w') as f:
            json.dump(test_roles_config, f)
        
        self.role_engine = CombatRoleEngine(self.roles_config_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test role engine initialization."""
        self.assertIsNotNone(self.role_engine)
        self.assertEqual(len(self.role_engine.get_available_roles()), 3)
        self.assertIsNone(self.role_engine.current_role)
    
    def test_get_available_roles(self):
        """Test getting available roles."""
        roles = self.role_engine.get_available_roles()
        self.assertEqual(len(roles), 3)
        self.assertIn("solo_dps", roles)
        self.assertIn("healer", roles)
        self.assertIn("tank", roles)
    
    def test_set_current_role(self):
        """Test setting current role."""
        # Test valid role
        success = self.role_engine.set_current_role("solo_dps")
        self.assertTrue(success)
        self.assertEqual(self.role_engine.current_role, "solo_dps")
        
        # Test invalid role
        success = self.role_engine.set_current_role("invalid_role")
        self.assertFalse(success)
    
    def test_get_role_info(self):
        """Test getting role information."""
        role_info = self.role_engine.get_role_info("solo_dps")
        self.assertIsNotNone(role_info)
        self.assertEqual(role_info["name"], "Solo DPS")
        self.assertEqual(role_info["description"], "Optimized for solo combat")
        
        # Test invalid role
        role_info = self.role_engine.get_role_info("invalid_role")
        self.assertIsNone(role_info)
    
    def test_get_current_role_info(self):
        """Test getting current role information."""
        # No role set
        role_info = self.role_engine.get_current_role_info()
        self.assertIsNone(role_info)
        
        # Set role and test
        self.role_engine.set_current_role("healer")
        role_info = self.role_engine.get_current_role_info()
        self.assertIsNotNone(role_info)
        self.assertEqual(role_info["name"], "Healer")
    
    def test_should_use_taunt(self):
        """Test taunt usage logic."""
        # Tank should use taunt
        self.role_engine.set_current_role("tank")
        self.assertTrue(self.role_engine.should_use_taunt())
        
        # Solo DPS should not use taunt
        self.role_engine.set_current_role("solo_dps")
        self.assertFalse(self.role_engine.should_use_taunt())
        
        # Healer should not use taunt
        self.role_engine.set_current_role("healer")
        self.assertFalse(self.role_engine.should_use_taunt())
    
    def test_should_maintain_aggro(self):
        """Test aggro maintenance logic."""
        # Tank should maintain aggro
        self.role_engine.set_current_role("tank")
        self.assertTrue(self.role_engine.should_maintain_aggro())
        
        # Solo DPS should not maintain aggro
        self.role_engine.set_current_role("solo_dps")
        self.assertFalse(self.role_engine.should_maintain_aggro())
    
    def test_should_use_group_healing(self):
        """Test group healing logic."""
        # Healer should use group healing
        self.role_engine.set_current_role("healer")
        self.assertTrue(self.role_engine.should_use_group_healing())
        
        # Solo DPS should not use group healing
        self.role_engine.set_current_role("solo_dps")
        self.assertFalse(self.role_engine.should_use_group_healing())
    
    def test_get_ability_priorities(self):
        """Test getting ability priorities."""
        self.role_engine.set_current_role("solo_dps")
        priorities = self.role_engine.get_ability_priorities()
        self.assertEqual(priorities, ["highest_damage_ability", "damage_buff", "defensive_cooldown"])
        
        self.role_engine.set_current_role("healer")
        priorities = self.role_engine.get_ability_priorities()
        self.assertEqual(priorities, ["emergency_heal", "group_heal", "healing_buff"])
    
    def test_get_role_behaviors(self):
        """Test getting role behaviors."""
        self.role_engine.set_current_role("solo_dps")
        behaviors = self.role_engine.get_role_behaviors()
        self.assertIn("damage_optimization", behaviors)
        self.assertIn("survival", behaviors)
        
        # Test specific behavior type
        damage_behavior = self.role_engine.get_role_behaviors("damage_optimization")
        self.assertEqual(damage_behavior["priority"], "high")
    
    def test_auto_detect_role(self):
        """Test automatic role detection."""
        # Solo player
        group = [{"name": "Player1", "role": "dps"}]
        suggested_role = self.role_engine.auto_detect_role(group)
        self.assertEqual(suggested_role, "solo_dps")
        
        # Group without healer
        group = [
            {"name": "Player1", "role": "dps"},
            {"name": "Player2", "role": "dps"},
            {"name": "Player3", "role": "dps"}
        ]
        suggested_role = self.role_engine.auto_detect_role(group)
        self.assertEqual(suggested_role, "healer")
        
        # Group without tank
        group = [
            {"name": "Player1", "role": "dps"},
            {"name": "Player2", "role": "dps"},
            {"name": "Player3", "role": "dps"},
            {"name": "Player4", "role": "dps"}
        ]
        suggested_role = self.role_engine.auto_detect_role(group)
        self.assertEqual(suggested_role, "healer")  # Healer takes priority over tank for 4-person group
    
    def test_update_group_composition(self):
        """Test group composition updates."""
        group = [
            {"name": "Player1", "role": "dps"},
            {"name": "Player2", "role": "dps"},
            {"name": "Player3", "role": "dps"}
        ]
        
        self.role_engine.update_group_composition(group)
        self.assertEqual(len(self.role_engine.group_composition), 3)
        # Should auto-switch to healer
        self.assertEqual(self.role_engine.current_role, "healer")
    
    def test_get_role_specific_triggers(self):
        """Test getting role-specific triggers."""
        tank_triggers = self.role_engine.get_role_specific_triggers("tank_triggers")
        self.assertIn("use_taunt_if_tank", tank_triggers)
        self.assertIn("maintain_aggro", tank_triggers)
        
        healer_triggers = self.role_engine.get_role_specific_triggers("healer_triggers")
        self.assertIn("prioritize_group_healing", healer_triggers)
        self.assertIn("heal_tank_first", healer_triggers)
    
    def test_evaluate_combat_decision(self):
        """Test combat decision evaluation."""
        combat_context = {"player_health": 75, "target_health": 50}
        
        # Test tank decisions
        self.role_engine.set_current_role("tank")
        self.assertTrue(self.role_engine.evaluate_combat_decision("use_taunt", combat_context))
        self.assertTrue(self.role_engine.evaluate_combat_decision("maintain_aggro", combat_context))
        self.assertFalse(self.role_engine.evaluate_combat_decision("use_group_healing", combat_context))
        
        # Test healer decisions
        self.role_engine.set_current_role("healer")
        self.assertFalse(self.role_engine.evaluate_combat_decision("use_taunt", combat_context))
        self.assertTrue(self.role_engine.evaluate_combat_decision("use_group_healing", combat_context))
    
    def test_role_performance_metrics(self):
        """Test role performance metrics."""
        self.role_engine.set_current_role("solo_dps")
        self.role_engine.update_role_performance({
            "damage_dealt": 1500,
            "abilities_used": 15
        })
        
        metrics = self.role_engine.get_role_performance_metrics()
        self.assertEqual(metrics["damage_dealt"], 1500)
        self.assertEqual(metrics["abilities_used"], 15)
    
    def test_get_role_suggestions(self):
        """Test role suggestions."""
        combat_context = {"player_health": 75, "target_health": 50}
        suggestions = self.role_engine.get_role_suggestions(combat_context)
        
        self.assertEqual(len(suggestions), 3)
        role_names = [s["name"] for s in suggestions]
        self.assertIn("Solo DPS", role_names)
        self.assertIn("Healer", role_names)
        self.assertIn("Tank", role_names)
    
    def test_validate_role_configuration(self):
        """Test role configuration validation."""
        is_valid, errors = self.role_engine.validate_role_configuration()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_get_statistics(self):
        """Test getting statistics."""
        stats = self.role_engine.get_statistics()
        self.assertIn("current_role", stats)
        self.assertIn("available_roles", stats)
        self.assertIn("role_switching_enabled", stats)
        self.assertIn("group_size", stats)
        self.assertIn("role_performance", stats)
        self.assertIn("config_loaded", stats)
        
        self.assertEqual(stats["available_roles"], 3)
        self.assertTrue(stats["role_switching_enabled"])
        self.assertEqual(stats["group_size"], 0)

class TestCombatRoleProfileManager(unittest.TestCase):
    """Test cases for the CombatRoleProfileManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary roles config file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.roles_config_path = os.path.join(self.temp_dir, "roles.json")
        
        # Create test roles configuration
        test_roles_config = {
            "combat_roles": {
                "version": "1.0",
                "roles": {
                    "healer": {
                        "name": "Healer",
                        "description": "Focused on healing",
                        "enabled": True,
                        "behaviors": {
                            "healing_optimization": {"enabled": True, "priority": "critical"}
                        },
                        "triggers": {
                            "use_group_healing": True,
                            "use_escape_abilities": True
                        },
                        "ability_priorities": ["emergency_heal", "group_heal", "healing_buff"]
                    },
                    "solo_dps": {
                        "name": "Solo DPS",
                        "description": "Optimized for solo combat",
                        "enabled": True,
                        "behaviors": {
                            "damage_optimization": {"enabled": True, "priority": "high"}
                        },
                        "triggers": {
                            "use_escape_abilities": True
                        },
                        "ability_priorities": ["highest_damage_ability", "damage_buff"]
                    }
                }
            }
        }
        
        with open(self.roles_config_path, 'w') as f:
            json.dump(test_roles_config, f)
        
        self.profile_manager = CombatRoleProfileManager(self.roles_config_path)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_initialization(self):
        """Test profile manager initialization."""
        self.assertIsNotNone(self.profile_manager)
        self.assertIsNotNone(self.profile_manager.role_engine)
        self.assertEqual(len(self.profile_manager.base_profiles), 0)
        self.assertEqual(len(self.profile_manager.role_modified_profiles), 0)
        self.assertIsNone(self.profile_manager.active_profile)
    
    def test_load_base_profile(self):
        """Test loading base profiles."""
        profile_data = {
            "name": "Test Profile",
            "description": "Test description",
            "rotation": ["ability1", "ability2"],
            "cooldowns": {"ability1": 5, "ability2": 10}
        }
        
        success = self.profile_manager.load_base_profile("test_profile", profile_data)
        self.assertTrue(success)
        self.assertIn("test_profile", self.profile_manager.base_profiles)
        self.assertEqual(self.profile_manager.base_profiles["test_profile"]["name"], "Test Profile")
    
    def test_create_role_modified_profile(self):
        """Test creating role-modified profiles."""
        # Load base profile first
        profile_data = {
            "name": "Test Profile",
            "description": "Test description",
            "rotation": ["ability1", "ability2", "heal_self"],
            "cooldowns": {"ability1": 5, "ability2": 10, "heal_self": 30},
            "emergency_abilities": {"critical_heal": "heal_self"}
        }
        self.profile_manager.load_base_profile("test_profile", profile_data)
        
        # Create healer-modified profile
        modified_profile = self.profile_manager.create_role_modified_profile("test_profile", "healer")
        self.assertIsNotNone(modified_profile)
        self.assertEqual(modified_profile["role"], "Healer")
        self.assertIn("role_ability_priorities", modified_profile)
        self.assertIn("role_behaviors", modified_profile)
        self.assertIn("role_triggers", modified_profile)
    
    def test_get_profile_for_role(self):
        """Test getting profiles for specific roles."""
        # Load base profile
        profile_data = {
            "name": "Test Profile",
            "description": "Test description",
            "rotation": ["ability1", "ability2"],
            "cooldowns": {"ability1": 5, "ability2": 10}
        }
        self.profile_manager.load_base_profile("test_profile", profile_data)
        
        # Get healer profile
        healer_profile = self.profile_manager.get_profile_for_role("test_profile", "healer")
        self.assertIsNotNone(healer_profile)
        self.assertEqual(healer_profile["role"], "Healer")
        
        # Test caching
        cached_profile = self.profile_manager.get_profile_for_role("test_profile", "healer")
        self.assertEqual(healer_profile, cached_profile)
    
    def test_set_active_profile(self):
        """Test setting active profile."""
        # Load base profile
        profile_data = {
            "name": "Test Profile",
            "description": "Test description",
            "rotation": ["ability1", "ability2"],
            "cooldowns": {"ability1": 5, "ability2": 10}
        }
        self.profile_manager.load_base_profile("test_profile", profile_data)
        
        # Set active profile with role
        self.profile_manager.role_engine.set_current_role("healer")
        success = self.profile_manager.set_active_profile("test_profile")
        self.assertTrue(success)
        self.assertIsNotNone(self.profile_manager.active_profile)
        self.assertEqual(self.profile_manager.active_profile["role"], "Healer")
    
    def test_get_next_ability(self):
        """Test getting next ability."""
        # Load base profile and set as active
        profile_data = {
            "name": "Test Profile",
            "description": "Test description",
            "rotation": ["ability1", "ability2"],
            "cooldowns": {"ability1": 5, "ability2": 10},
            "emergency_abilities": {"group_heal_emergency": "heal_other"}
        }
        self.profile_manager.load_base_profile("test_profile", profile_data)
        self.profile_manager.role_engine.set_current_role("healer")
        self.profile_manager.set_active_profile("test_profile")
        
        # Test next ability selection
        next_ability = self.profile_manager.get_next_ability()
        self.assertIsNotNone(next_ability)
        self.assertIn(next_ability, ["ability1", "ability2", "heal_other", "Heal Other"])
    
    def test_get_available_profiles(self):
        """Test getting available profiles."""
        # Load some profiles
        profile_data = {"name": "Test Profile", "description": "Test description"}
        self.profile_manager.load_base_profile("profile1", profile_data)
        self.profile_manager.load_base_profile("profile2", profile_data)
        
        available_profiles = self.profile_manager.get_available_profiles()
        self.assertEqual(len(available_profiles), 2)
        self.assertIn("profile1", available_profiles)
        self.assertIn("profile2", available_profiles)
    
    def test_get_available_roles(self):
        """Test getting available roles."""
        roles = self.profile_manager.get_available_roles()
        self.assertEqual(len(roles), 2)
        self.assertIn("healer", roles)
        self.assertIn("solo_dps", roles)
    
    def test_get_profile_suggestions(self):
        """Test getting profile suggestions."""
        # Load some profiles
        profile_data = {"name": "Test Profile", "description": "Test description"}
        self.profile_manager.load_base_profile("profile1", profile_data)
        self.profile_manager.load_base_profile("profile2", profile_data)
        
        suggestions = self.profile_manager.get_profile_suggestions()
        self.assertEqual(len(suggestions), 4)  # 2 profiles × 2 roles
        
        # Check that all combinations are present
        profile_roles = [(s["profile"], s["role"]) for s in suggestions]
        self.assertIn(("profile1", "healer"), profile_roles)
        self.assertIn(("profile1", "solo_dps"), profile_roles)
        self.assertIn(("profile2", "healer"), profile_roles)
        self.assertIn(("profile2", "solo_dps"), profile_roles)
    
    def test_validate_profile_configuration(self):
        """Test profile configuration validation."""
        is_valid, errors = self.profile_manager.validate_profile_configuration()
        self.assertTrue(is_valid)
        self.assertEqual(len(errors), 0)
    
    def test_get_statistics(self):
        """Test getting statistics."""
        stats = self.profile_manager.get_statistics()
        self.assertIn("base_profiles_count", stats)
        self.assertIn("role_modified_profiles_count", stats)
        self.assertIn("profile_cache_size", stats)
        self.assertIn("active_profile", stats)
        self.assertIn("role_engine_stats", stats)
        
        self.assertEqual(stats["base_profiles_count"], 0)
        self.assertEqual(stats["role_modified_profiles_count"], 0)
        self.assertEqual(stats["profile_cache_size"], 0)
        self.assertIsNone(stats["active_profile"])

def main():
    """Run the test suite."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestCombatRoleEngine))
    test_suite.addTest(unittest.TestLoader().loadTestsFromTestCase(TestCombatRoleProfileManager))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n" + "=" * 60)
    print("MS11 Batch 084 - Combat Role Engine Test Results")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    print("=" * 60)
    
    return len(result.failures) + len(result.errors)

if __name__ == "__main__":
    exit(main()) 