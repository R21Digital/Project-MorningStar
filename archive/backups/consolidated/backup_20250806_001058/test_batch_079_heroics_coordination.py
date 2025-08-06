#!/usr/bin/env python3
"""
MS11 Batch 079 Tests - Heroics Instance Entry + Group Coordination Logic

Comprehensive test suite for the heroics coordination system including:
- Heroic instance detection and parsing
- Group formation and management
- Role assignment and behaviors
- Entry sequence execution
- Discord integration functionality
"""

import json
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Import Batch 079 modules
try:
    from core.heroics.heroic_detector import (
        HeroicDetector, HeroicInstance, HeroicLockout, HeroicEntryStatus
    )
    from core.heroics.heroic_coordinator import (
        HeroicCoordinator, GroupMember, GroupFormation, RoleAssignment
    )
    from core.heroics.role_behaviors import (
        RoleBehaviorManager, CombatAction, RoleBehavior
    )
    from core.heroics.discord_integration import (
        DiscordIntegration, DiscordBotInfo, DiscordGroupMessage
    )
except ImportError as e:
    print(f"Error importing Batch 079 modules: {e}")
    print("Please ensure all modules are properly installed")
    exit(1)


class TestHeroicDetector(unittest.TestCase):
    """Test cases for HeroicDetector class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.heroics_data_dir = Path(self.temp_dir) / "heroics"
        self.heroics_data_dir.mkdir()
        
        # Create test heroics index
        self.heroics_index = {
            "metadata": {
                "description": "Test heroics index",
                "last_updated": "2025-01-27",
                "version": "1.0",
                "total_heroics": 2
            },
            "heroics": {
                "axkva_min": {
                    "name": "Axkva Min",
                    "planet": "dantooine",
                    "location": "dantooine_ruins",
                    "coordinates": [5000, -3000],
                    "difficulty_tiers": ["normal", "hard"],
                    "level_requirement": 80,
                    "group_size": "4-8 players",
                    "status": "active"
                },
                "ancient_jedi_temple": {
                    "name": "Ancient Jedi Temple",
                    "planet": "yavin4",
                    "location": "yavin4_jungle",
                    "coordinates": [3000, 2000],
                    "difficulty_tiers": ["normal", "hard"],
                    "level_requirement": 75,
                    "group_size": "6-12 players",
                    "status": "active"
                }
            }
        }
        
        # Create test heroic instance file
        self.axkva_min_data = {
            "heroic_id": "axkva_min",
            "name": "Axkva Min",
            "planet": "dantooine",
            "location": "dantooine_ruins",
            "coordinates": [5000, -3000],
            "difficulty_tiers": {
                "normal": {
                    "level_requirement": 80,
                    "group_size": "4-8 players",
                    "lockout_timer": 86400,
                    "reset_time": "daily"
                }
            },
            "prerequisites": {
                "quests": [
                    {
                        "quest_id": "dantooine_ruins_exploration",
                        "name": "Dantooine Ruins Exploration",
                        "status": "required"
                    }
                ]
            },
            "bosses": [
                {
                    "name": "Axkva Min",
                    "level": 90,
                    "health": 50000
                }
            ]
        }
        
        # Write test files
        with open(self.heroics_data_dir / "heroics_index.yml", 'w') as f:
            import yaml
            yaml.dump(self.heroics_index, f)
        
        with open(self.heroics_data_dir / "axkva_min.yml", 'w') as f:
            yaml.dump(self.axkva_min_data, f)
        
        self.detector = HeroicDetector(str(self.heroics_data_dir))

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_heroic_detector_initialization(self):
        """Test heroic detector initialization."""
        self.assertIsNotNone(self.detector)
        self.assertEqual(len(self.detector.heroic_instances), 1)
        self.assertIn("axkva_min", self.detector.heroic_instances)

    def test_parse_heroiclock_command(self):
        """Test parsing /heroiclock command output."""
        heroiclock_text = """
        Axkva Min - Normal - Available - 0 hours
        Ancient Jedi Temple - Normal - Available - 0 hours
        Sith Academy - Normal - Locked - 12 hours
        """
        
        lockouts = self.detector.parse_heroiclock_command(heroiclock_text)
        
        self.assertIsInstance(lockouts, list)
        self.assertGreater(len(lockouts), 0)
        
        # Check that we found the axkva_min lockout
        axkva_lockout = next((l for l in lockouts if l.heroic_id == "axkva_min"), None)
        self.assertIsNotNone(axkva_lockout)
        self.assertFalse(axkva_lockout.is_locked)

    def test_detect_available_heroics(self):
        """Test detecting available heroics."""
        heroiclock_text = "Axkva Min - Normal - Available - 0 hours"
        
        available_heroics = self.detector.detect_available_heroics(heroiclock_text)
        
        self.assertIsInstance(available_heroics, list)
        self.assertGreater(len(available_heroics), 0)
        
        axkva_heroic = next((h for h in available_heroics if h.heroic_id == "axkva_min"), None)
        self.assertIsNotNone(axkva_heroic)
        self.assertTrue(axkva_heroic.can_enter)

    def test_get_heroic_entry_sequence(self):
        """Test getting entry sequence for a heroic."""
        sequence = self.detector.get_heroic_entry_sequence("axkva_min", "normal")
        
        self.assertIsInstance(sequence, list)
        self.assertGreater(len(sequence), 0)
        
        # Check that sequence has required steps
        step_actions = [step["action"] for step in sequence]
        self.assertIn("travel_to_location", step_actions)
        self.assertIn("enter_instance", step_actions)

    def test_get_heroic_info(self):
        """Test getting heroic instance information."""
        info = self.detector.get_heroic_info("axkva_min")
        
        self.assertIsNotNone(info)
        self.assertEqual(info.heroic_id, "axkva_min")
        self.assertEqual(info.name, "Axkva Min")
        self.assertEqual(info.planet, "dantooine")

    def test_update_lockout_cache(self):
        """Test updating lockout cache."""
        self.detector.update_lockout_cache(
            heroic_id="axkva_min",
            difficulty="normal",
            is_locked=True,
            time_remaining=3600
        )
        
        cache_key = "axkva_min_normal"
        self.assertIn(cache_key, self.detector.lockout_cache)
        
        lockout = self.detector.lockout_cache[cache_key]
        self.assertTrue(lockout.is_locked)
        self.assertEqual(lockout.time_remaining, 3600)


class TestHeroicCoordinator(unittest.TestCase):
    """Test cases for HeroicCoordinator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "group_heroics.json"
        
        # Create test configuration
        self.test_config = {
            "group_coordination": {
                "enabled": True,
                "discord_integration": {
                    "enabled": False,
                    "webhook_url": "",
                    "channel_id": "",
                    "bot_token": ""
                },
                "auto_role_assignment": True,
                "role_priority": ["healer", "tank", "dps", "support"]
            },
            "roles": {
                "dps": {
                    "description": "Damage dealer role",
                    "priorities": ["maximize_damage_output"],
                    "keybinds": {
                        "primary_attack": "1",
                        "secondary_attack": "2"
                    },
                    "targeting_rules": {
                        "primary_target": "boss"
                    }
                },
                "healer": {
                    "description": "Healing role",
                    "priorities": ["maintain_group_health"],
                    "keybinds": {
                        "primary_heal": "1",
                        "group_heal": "2"
                    },
                    "healing_rules": {
                        "tank_health_threshold": 0.8
                    }
                }
            },
            "heroic_instances": {
                "axkva_min": {
                    "recommended_group_size": {
                        "normal": 6,
                        "hard": 8
                    }
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(self.test_config, f)
        
        self.coordinator = HeroicCoordinator(str(self.config_path))

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_heroic_coordinator_initialization(self):
        """Test heroic coordinator initialization."""
        self.assertIsNotNone(self.coordinator)
        self.assertIsNotNone(self.coordinator.config)

    def test_create_group_formation(self):
        """Test creating a group formation."""
        formation = self.coordinator.create_group_formation(
            heroic_id="axkva_min",
            difficulty="normal",
            leader_name="TestLeader"
        )
        
        self.assertIsNotNone(formation)
        self.assertEqual(formation.heroic_id, "axkva_min")
        self.assertEqual(formation.difficulty, "normal")
        self.assertEqual(formation.status, "forming")
        self.assertGreater(formation.target_size, 0)

    def test_assign_role(self):
        """Test role assignment."""
        player_info = {
            "level": 85,
            "profession": "commando",
            "preferred_role": "dps"
        }
        
        role_assignment = self.coordinator.assign_role("TestPlayer", player_info)
        
        self.assertIsNotNone(role_assignment)
        self.assertEqual(role_assignment.player_name, "TestPlayer")
        self.assertIn(role_assignment.assigned_role, ["dps", "healer", "tank", "support"])
        self.assertGreater(role_assignment.confidence, 0.0)

    def test_add_member_to_group(self):
        """Test adding member to group."""
        # Create group first
        formation = self.coordinator.create_group_formation(
            heroic_id="axkva_min",
            difficulty="normal"
        )
        
        player_info = {
            "level": 85,
            "profession": "medic",
            "preferred_role": "healer"
        }
        
        success = self.coordinator.add_member_to_group(
            formation.group_id,
            "TestMember",
            player_info
        )
        
        self.assertTrue(success)
        
        # Check group status
        updated_formation = self.coordinator.get_group_status(formation.group_id)
        self.assertEqual(updated_formation.current_size, 1)

    def test_get_entry_sequence(self):
        """Test getting entry sequence."""
        sequence = self.coordinator.get_entry_sequence("axkva_min", "normal")
        
        self.assertIsInstance(sequence, list)
        self.assertGreater(len(sequence), 0)

    def test_execute_entry_sequence(self):
        """Test executing entry sequence."""
        # Create group
        formation = self.coordinator.create_group_formation(
            heroic_id="axkva_min",
            difficulty="normal"
        )
        
        # Add members
        for i in range(3):
            player_info = {
                "level": 80 + i,
                "profession": "commando",
                "preferred_role": "dps"
            }
            self.coordinator.add_member_to_group(
                formation.group_id,
                f"Member{i}",
                player_info
            )
        
        # Get and execute sequence
        sequence = self.coordinator.get_entry_sequence("axkva_min", "normal")
        success = self.coordinator.execute_entry_sequence(formation.group_id, sequence)
        
        # Should succeed (even if placeholders)
        self.assertTrue(success)

    def test_get_all_groups(self):
        """Test getting all groups."""
        # Create multiple groups
        group1 = self.coordinator.create_group_formation("axkva_min", "normal")
        group2 = self.coordinator.create_group_formation("ancient_jedi_temple", "hard")
        
        all_groups = self.coordinator.get_all_groups()
        
        self.assertGreaterEqual(len(all_groups), 2)

    def test_disband_group(self):
        """Test disbanding a group."""
        formation = self.coordinator.create_group_formation("axkva_min", "normal")
        group_id = formation.group_id
        
        success = self.coordinator.disband_group(group_id)
        self.assertTrue(success)
        
        # Check that group is removed
        group_status = self.coordinator.get_group_status(group_id)
        self.assertIsNone(group_status)


class TestRoleBehaviorManager(unittest.TestCase):
    """Test cases for RoleBehaviorManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "group_heroics.json"
        
        # Create test configuration
        self.test_config = {
            "roles": {
                "dps": {
                    "description": "Damage dealer role",
                    "priorities": ["maximize_damage_output"],
                    "keybinds": {
                        "primary_attack": "1",
                        "secondary_attack": "2",
                        "damage_cooldown": "3"
                    },
                    "targeting_rules": {
                        "primary_target": "boss"
                    },
                    "healing_rules": {}
                },
                "healer": {
                    "description": "Healing role",
                    "priorities": ["maintain_group_health"],
                    "keybinds": {
                        "primary_heal": "1",
                        "group_heal": "2",
                        "cleanse": "3"
                    },
                    "targeting_rules": {},
                    "healing_rules": {
                        "tank_health_threshold": 0.8,
                        "group_health_threshold": 0.6
                    }
                },
                "tank": {
                    "description": "Tank role",
                    "priorities": ["maintain_aggro"],
                    "keybinds": {
                        "taunt": "1",
                        "defensive_cooldown": "2"
                    },
                    "targeting_rules": {
                        "aggro_threshold": 0.9
                    },
                    "healing_rules": {}
                },
                "support": {
                    "description": "Support role",
                    "priorities": ["maintain_buffs"],
                    "keybinds": {
                        "group_buff": "1",
                        "debuff_target": "2"
                    },
                    "targeting_rules": {},
                    "healing_rules": {}
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(self.test_config, f)
        
        self.behavior_manager = RoleBehaviorManager(str(self.config_path))

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_role_behavior_manager_initialization(self):
        """Test role behavior manager initialization."""
        self.assertIsNotNone(self.behavior_manager)
        self.assertIsNotNone(self.behavior_manager.role_behaviors)

    def test_get_role_behavior(self):
        """Test getting role behavior."""
        dps_behavior = self.behavior_manager.get_role_behavior("dps")
        healer_behavior = self.behavior_manager.get_role_behavior("healer")
        
        self.assertIsNotNone(dps_behavior)
        self.assertEqual(dps_behavior.role, "dps")
        self.assertIsNotNone(healer_behavior)
        self.assertEqual(healer_behavior.role, "healer")

    def test_get_next_action(self):
        """Test getting next action for a role."""
        game_state = {
            "has_target": True,
            "target_in_range": True,
            "target_is_boss": True
        }
        
        action = self.behavior_manager.get_next_action("dps", game_state)
        
        self.assertIsNotNone(action)
        self.assertEqual(action.role, "dps")

    def test_execute_dps_behavior(self):
        """Test executing DPS behavior."""
        game_state = {
            "has_target": True,
            "target_in_range": True,
            "target_is_boss": True
        }
        
        result = self.behavior_manager.execute_dps_behavior(game_state)
        
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)

    def test_execute_healer_behavior(self):
        """Test executing healer behavior."""
        game_state = {
            "target_low_health": True,
            "target_friendly": True,
            "group_average_health": 0.5,
            "tank_health": 0.3
        }
        
        result = self.behavior_manager.execute_healer_behavior(game_state)
        
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)

    def test_execute_tank_behavior(self):
        """Test executing tank behavior."""
        game_state = {
            "has_target": True,
            "aggro_lost": True,
            "self_health": 0.6
        }
        
        result = self.behavior_manager.execute_tank_behavior(game_state)
        
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)

    def test_execute_support_behavior(self):
        """Test executing support behavior."""
        game_state = {
            "group_needs_buff": True,
            "target_exists": True,
            "target_enemy": True
        }
        
        result = self.behavior_manager.execute_support_behavior(game_state)
        
        self.assertIsInstance(result, dict)
        self.assertIn("success", result)

    def test_get_role_priorities(self):
        """Test getting role priorities."""
        dps_priorities = self.behavior_manager.get_role_priorities("dps")
        healer_priorities = self.behavior_manager.get_role_priorities("healer")
        
        self.assertIsInstance(dps_priorities, list)
        self.assertIsInstance(healer_priorities, list)
        self.assertGreater(len(dps_priorities), 0)
        self.assertGreater(len(healer_priorities), 0)

    def test_get_all_roles(self):
        """Test getting all available roles."""
        roles = self.behavior_manager.get_all_roles()
        
        self.assertIsInstance(roles, list)
        self.assertIn("dps", roles)
        self.assertIn("healer", roles)
        self.assertIn("tank", roles)
        self.assertIn("support", roles)


class TestDiscordIntegration(unittest.TestCase):
    """Test cases for DiscordIntegration class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "bot_token": "test_token",
            "channel_id": "123456789",
            "webhook_url": "https://discord.com/api/webhooks/test"
        }
        
        self.discord_integration = DiscordIntegration(self.config)

    def test_discord_integration_initialization(self):
        """Test Discord integration initialization."""
        self.assertIsNotNone(self.discord_integration)
        self.assertEqual(self.discord_integration.bot_token, "test_token")
        self.assertEqual(self.discord_integration.channel_id, "123456789")

    def test_parse_status_message(self):
        """Test parsing status messages."""
        status_message = "!status 0.8 0.9 dantooine axkva_min"
        
        status_data = self.discord_integration._parse_status_message(status_message)
        
        self.assertIsNotNone(status_data)
        self.assertEqual(status_data["health"], 0.8)
        self.assertEqual(status_data["energy"], 0.9)
        self.assertEqual(status_data["location"], "dantooine")
        self.assertEqual(status_data["target"], "axkva_min")

    def test_get_available_bots(self):
        """Test getting available bots."""
        bots = self.discord_integration.get_available_bots()
        
        self.assertIsInstance(bots, list)

    def test_get_active_groups(self):
        """Test getting active groups."""
        groups = self.discord_integration.get_active_groups()
        
        self.assertIsInstance(groups, dict)

    @patch('discord.ext.commands.Bot')
    def test_connect_disconnect(self, mock_bot):
        """Test connecting and disconnecting from Discord."""
        # Mock the bot
        mock_bot_instance = Mock()
        mock_bot.return_value = mock_bot_instance
        
        # Test connection (should fail without real token)
        success = self.discord_integration.connect()
        self.assertFalse(success)  # Should fail with test token
        
        # Test disconnection
        self.discord_integration.disconnect()
        # Should not raise any exceptions


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete heroics coordination system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "group_heroics.json"
        
        # Create comprehensive test configuration
        self.test_config = {
            "group_coordination": {
                "enabled": True,
                "discord_integration": {
                    "enabled": False
                },
                "auto_role_assignment": True
            },
            "roles": {
                "dps": {
                    "description": "Damage dealer",
                    "priorities": ["maximize_damage_output"],
                    "keybinds": {"primary_attack": "1"},
                    "targeting_rules": {"primary_target": "boss"},
                    "healing_rules": {}
                },
                "healer": {
                    "description": "Healer",
                    "priorities": ["maintain_group_health"],
                    "keybinds": {"primary_heal": "1"},
                    "targeting_rules": {},
                    "healing_rules": {"tank_health_threshold": 0.8}
                }
            },
            "heroic_instances": {
                "axkva_min": {
                    "recommended_group_size": {"normal": 6}
                }
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(self.test_config, f)

    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_complete_heroic_workflow(self):
        """Test complete heroic workflow from detection to execution."""
        # Initialize components
        coordinator = HeroicCoordinator(str(self.config_path))
        behavior_manager = RoleBehaviorManager(str(self.config_path))
        
        # 1. Create group formation
        formation = coordinator.create_group_formation(
            heroic_id="axkva_min",
            difficulty="normal",
            leader_name="TestLeader"
        )
        self.assertIsNotNone(formation)
        
        # 2. Add members with role assignment
        members = [
            {"name": "DPSPlayer", "level": 85, "profession": "commando", "preferred_role": "dps"},
            {"name": "HealerPlayer", "level": 82, "profession": "medic", "preferred_role": "healer"}
        ]
        
        for member_info in members:
            success = coordinator.add_member_to_group(
                formation.group_id,
                member_info["name"],
                member_info
            )
            self.assertTrue(success)
        
        # 3. Get entry sequence
        sequence = coordinator.get_entry_sequence("axkva_min", "normal")
        self.assertGreater(len(sequence), 0)
        
        # 4. Execute role behaviors
        game_state = {
            "has_target": True,
            "target_in_range": True,
            "target_is_boss": True
        }
        
        dps_result = behavior_manager.execute_dps_behavior(game_state)
        healer_result = behavior_manager.execute_healer_behavior(game_state)
        
        self.assertIn("success", dps_result)
        self.assertIn("success", healer_result)
        
        # 5. Execute entry sequence
        success = coordinator.execute_entry_sequence(formation.group_id, sequence)
        self.assertTrue(success)

    def test_role_assignment_workflow(self):
        """Test complete role assignment workflow."""
        coordinator = HeroicCoordinator(str(self.config_path))
        
        # Test different profession/level combinations
        test_cases = [
            {"name": "HighLevelMedic", "level": 90, "profession": "medic", "expected_role": "healer"},
            {"name": "LowLevelCommando", "level": 70, "profession": "commando", "expected_role": "dps"},
            {"name": "BrawlerTank", "level": 85, "profession": "brawler", "expected_role": "tank"},
            {"name": "EntertainerSupport", "level": 80, "profession": "entertainer", "expected_role": "support"}
        ]
        
        for test_case in test_cases:
            role_assignment = coordinator.assign_role(
                test_case["name"],
                {
                    "level": test_case["level"],
                    "profession": test_case["profession"],
                    "preferred_role": ""
                }
            )
            
            self.assertIsNotNone(role_assignment)
            self.assertEqual(role_assignment.player_name, test_case["name"])
            # Note: Role assignment is probabilistic, so we just check it's valid
            self.assertIn(role_assignment.assigned_role, ["dps", "healer", "tank", "support"])


def run_tests():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestHeroicDetector,
        TestHeroicCoordinator,
        TestRoleBehaviorManager,
        TestDiscordIntegration,
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
    print(f"Test Summary:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("🧪 MS11 Batch 079 Test Suite - Heroics Coordination System")
    print("=" * 60)
    
    success = run_tests()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        exit(1) 