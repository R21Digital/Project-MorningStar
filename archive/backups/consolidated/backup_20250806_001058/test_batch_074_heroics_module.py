#!/usr/bin/env python3
"""
Test suite for Batch 074 - Heroics Module: Prerequisites + Lockout Logic

This test suite validates all components of the heroics management system including:
- Lockout tracker functionality
- Heroics manager functionality
- Prerequisite checking
- Data persistence
- Integration between components
"""

import unittest
import tempfile
import shutil
import time
import json
from pathlib import Path
from datetime import datetime, timedelta

# Add the project root to the path
import sys
sys.path.insert(0, '.')

from utils.lockout_tracker import LockoutTracker, create_lockout_tracker
from core.heroics_manager import HeroicsManager, create_heroics_manager
from android_ms11.utils.logging_utils import log_event


class TestLockoutTracker(unittest.TestCase):
    """Test the lockout tracker functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.lockout_tracker = LockoutTracker(data_dir=self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_record_heroic_completion(self):
        """Test recording heroic completions."""
        character_name = "TestCharacter"
        heroic_id = "axkva_min"
        difficulty = "normal"
        
        # Record completion
        success = self.lockout_tracker.record_heroic_completion(character_name, heroic_id, difficulty)
        self.assertTrue(success)
        
        # Verify lockout was created
        lockout_key = f"{character_name}_{heroic_id}_{difficulty}"
        self.assertIn(lockout_key, self.lockout_tracker.lockout_data)
        
        # Verify character and instance tracking
        self.assertIn(character_name, self.lockout_tracker.character_lockouts)
        self.assertIn(heroic_id, self.lockout_tracker.instance_lockouts)

    def test_check_lockout_status(self):
        """Test checking lockout status."""
        character_name = "TestCharacter"
        heroic_id = "axkva_min"
        difficulty = "normal"
        
        # Check status before completion (should be available)
        status = self.lockout_tracker.check_lockout_status(character_name, heroic_id, difficulty)
        self.assertFalse(status["locked_out"])
        self.assertTrue(status["can_enter"])
        
        # Record completion
        self.lockout_tracker.record_heroic_completion(character_name, heroic_id, difficulty)
        
        # Check status after completion (should be locked out)
        status = self.lockout_tracker.check_lockout_status(character_name, heroic_id, difficulty)
        self.assertTrue(status["locked_out"])
        self.assertFalse(status["can_enter"])
        self.assertGreater(status["time_remaining"], 0)

    def test_get_character_lockouts(self):
        """Test getting character lockouts."""
        character_name = "TestCharacter"
        heroic_id = "axkva_min"
        
        # Record completions for different difficulties
        self.lockout_tracker.record_heroic_completion(character_name, heroic_id, "normal")
        self.lockout_tracker.record_heroic_completion(character_name, heroic_id, "hard")
        
        # Get character lockouts
        lockouts = self.lockout_tracker.get_character_lockouts(character_name)
        
        self.assertEqual(lockouts["character_name"], character_name)
        self.assertEqual(lockouts["total_lockouts"], 2)
        self.assertEqual(len(lockouts["active_lockouts"]), 2)
        
        # Verify both difficulties are present
        difficulties = [lockout["difficulty"] for lockout in lockouts["active_lockouts"]]
        self.assertIn("normal", difficulties)
        self.assertIn("hard", difficulties)

    def test_get_instance_lockouts(self):
        """Test getting instance lockouts."""
        heroic_id = "axkva_min"
        characters = ["Player1", "Player2", "Player3"]
        
        # Record completions for multiple characters
        for character in characters:
            self.lockout_tracker.record_heroic_completion(character, heroic_id, "normal")
        
        # Get instance lockouts
        lockouts = self.lockout_tracker.get_instance_lockouts(heroic_id)
        
        self.assertEqual(lockouts["heroic_id"], heroic_id)
        self.assertEqual(lockouts["total_lockouts"], 3)
        self.assertEqual(len(lockouts["active_lockouts"]), 3)
        
        # Verify all characters are present
        character_names = [lockout["character_name"] for lockout in lockouts["active_lockouts"]]
        for character in characters:
            self.assertIn(character, character_names)

    def test_clear_expired_lockouts(self):
        """Test clearing expired lockouts."""
        character_name = "TestCharacter"
        heroic_id = "axkva_min"
        
        # Record completion
        self.lockout_tracker.record_heroic_completion(character_name, heroic_id, "normal")
        
        # Manually expire the lockout by modifying the timestamp
        lockout_key = f"{character_name}_{heroic_id}_normal"
        self.lockout_tracker.lockout_data[lockout_key]["lockout_until"] = time.time() - 3600  # 1 hour ago
        
        # Clear expired lockouts
        cleared_count = self.lockout_tracker.clear_expired_lockouts()
        
        self.assertEqual(cleared_count, 1)
        self.assertNotIn(lockout_key, self.lockout_tracker.lockout_data)

    def test_export_lockout_data(self):
        """Test exporting lockout data."""
        character_name = "TestCharacter"
        heroic_id = "axkva_min"
        
        # Record completion
        self.lockout_tracker.record_heroic_completion(character_name, heroic_id, "normal")
        
        # Export data
        export_path = self.lockout_tracker.export_lockout_data()
        
        self.assertIsNotNone(export_path)
        self.assertTrue(Path(export_path).exists())
        
        # Verify export content
        with open(export_path, 'r', encoding='utf-8') as f:
            export_data = json.load(f)
        
        self.assertIn("lockout_data", export_data)
        self.assertIn("character_lockouts", export_data)
        self.assertIn("instance_lockouts", export_data)


class TestHeroicsManager(unittest.TestCase):
    """Test the heroics manager functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.heroics_manager = HeroicsManager(data_dir=self.temp_dir)
        
        # Create test heroics data
        self._create_test_heroics_data()

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def _create_test_heroics_data(self):
        """Create test heroics data files."""
        import yaml
        
        # Create heroics index
        index_data = {
            "metadata": {
                "description": "Test heroics index",
                "last_updated": "2025-01-27 12:00:00",
                "version": "1.0",
                "total_heroics": 1
            },
            "heroics": {
                "axkva_min": {
                    "name": "Axkva Min",
                    "planet": "dantooine",
                    "location": "dantooine_ruins",
                    "coordinates": [5000, -3000],
                    "difficulty_tiers": ["normal", "hard"],
                    "level_requirement": 80,
                    "group_size": "4-16 players",
                    "status": "active",
                    "last_updated": "2025-01-27"
                }
            }
        }
        
        index_file = Path(self.temp_dir) / "heroics_index.yml"
        with open(index_file, 'w', encoding='utf-8') as f:
            yaml.dump(index_data, f)
        
        # Create Axkva Min data
        axkva_data = {
            "heroic_id": "axkva_min",
            "name": "Axkva Min",
            "planet": "dantooine",
            "location": "dantooine_ruins",
            "coordinates": [5000, -3000],
            "instance_type": "heroic",
            "difficulty_tiers": {
                "normal": {
                    "level_requirement": 80,
                    "group_size": "4-8 players",
                    "lockout_timer": 86400,
                    "reset_time": "daily",
                    "description": "Standard difficulty"
                },
                "hard": {
                    "level_requirement": 90,
                    "group_size": "8-16 players",
                    "lockout_timer": 604800,
                    "reset_time": "weekly",
                    "description": "High difficulty"
                }
            },
            "prerequisites": {
                "quests": [
                    {
                        "quest_id": "dantooine_ruins_exploration",
                        "name": "Dantooine Ruins Exploration",
                        "status": "required",
                        "description": "Must complete the initial ruins exploration quest"
                    }
                ],
                "skills": [
                    {
                        "skill_name": "combat_skills",
                        "level_requirement": 4000,
                        "description": "Combat skills at master level"
                    }
                ],
                "items": [
                    {
                        "item_name": "ancient_key_fragment",
                        "quantity": 3,
                        "description": "Key fragments from previous quests"
                    }
                ],
                "reputation": [
                    {
                        "faction": "dantooine_locals",
                        "level": "friendly",
                        "description": "Friendly reputation with local inhabitants"
                    }
                ]
            }
        }
        
        axkva_file = Path(self.temp_dir) / "axkva_min.yml"
        with open(axkva_file, 'w', encoding='utf-8') as f:
            yaml.dump(axkva_data, f)
        
        # Reload the heroics manager to pick up the new data
        self.heroics_manager._load_heroics_data()

    def test_get_heroic_info(self):
        """Test getting heroic information."""
        heroic_info = self.heroics_manager.get_heroic_info("axkva_min")
        
        self.assertNotIn("error", heroic_info)
        self.assertEqual(heroic_info["name"], "Axkva Min")
        self.assertEqual(heroic_info["planet"], "dantooine")
        self.assertIn("difficulty_tiers", heroic_info)
        self.assertIn("prerequisites", heroic_info)

    def test_check_prerequisites(self):
        """Test checking prerequisites."""
        character_name = "TestCharacter"
        heroic_id = "axkva_min"
        difficulty = "normal"
        
        prerequisite_check = self.heroics_manager.check_prerequisites(character_name, heroic_id, difficulty)
        
        self.assertIn("can_enter", prerequisite_check)
        self.assertIn("prerequisites_met", prerequisite_check)
        
        # Check if it's a lockout or full prerequisite check
        if "reason" in prerequisite_check and prerequisite_check["reason"] == "lockout":
            # This is a lockout response, which is valid
            self.assertIn("lockout_info", prerequisite_check)
        else:
            # This is a full prerequisite check
            self.assertIn("quest_prerequisites", prerequisite_check)
            self.assertIn("skill_prerequisites", prerequisite_check)
            self.assertIn("item_prerequisites", prerequisite_check)
            self.assertIn("reputation_prerequisites", prerequisite_check)

    def test_record_heroic_completion(self):
        """Test recording heroic completion."""
        character_name = "TestCharacter"
        heroic_id = "axkva_min"
        difficulty = "normal"
        completion_data = {
            "loot": ["axkva_min_crystal"],
            "experience": 50000,
            "credits": 100000
        }
        
        success = self.heroics_manager.record_heroic_completion(
            character_name, heroic_id, difficulty, completion_data
        )
        
        self.assertTrue(success)

    def test_get_available_heroics(self):
        """Test getting available heroics for a character."""
        character_name = "TestCharacter"
        available_heroics = self.heroics_manager.get_available_heroics(character_name)
        
        self.assertEqual(available_heroics["character_name"], character_name)
        self.assertIn("available_heroics", available_heroics)
        self.assertIn("unavailable_heroics", available_heroics)
        self.assertIn("total_available", available_heroics)
        self.assertIn("total_unavailable", available_heroics)

    def test_get_axkva_min_info(self):
        """Test getting Axkva Min specific information."""
        axkva_info = self.heroics_manager.get_axkva_min_info()
        
        self.assertNotIn("error", axkva_info)
        self.assertEqual(axkva_info["name"], "Axkva Min")
        self.assertIn("special_handling", axkva_info)
        
        # Check special mechanics
        special_handling = axkva_info["special_handling"]
        self.assertIn("dark_side_corruption", special_handling)
        self.assertIn("force_storm", special_handling)
        self.assertIn("mind_control", special_handling)

    def test_get_heroics_summary(self):
        """Test getting heroics summary."""
        summary = self.heroics_manager.get_heroics_summary()
        
        self.assertEqual(summary["total_heroics"], 1)
        self.assertIn("heroics_by_planet", summary)
        self.assertIn("heroics_by_difficulty", summary)
        self.assertIn("heroics_list", summary)
        
        # Check planet grouping
        self.assertIn("dantooine", summary["heroics_by_planet"])
        self.assertEqual(len(summary["heroics_by_planet"]["dantooine"]), 1)


class TestIntegration(unittest.TestCase):
    """Test integration between components."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.lockout_tracker = LockoutTracker(data_dir=self.temp_dir)
        self.heroics_manager = HeroicsManager(data_dir=self.temp_dir)
        
        # Ensure heroics manager uses the same lockout tracker
        self.heroics_manager.lockout_tracker = self.lockout_tracker
        
        # Create test data
        self._create_test_data()

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def _create_test_data(self):
        """Create test data for integration tests."""
        import yaml
        
        # Create heroics index
        index_data = {
            "metadata": {"description": "Test index", "total_heroics": 1},
            "heroics": {
                "test_heroic": {
                    "name": "Test Heroic",
                    "planet": "test_planet",
                    "difficulty_tiers": ["normal"],
                    "level_requirement": 50,
                    "status": "active"
                }
            }
        }
        
        index_file = Path(self.temp_dir) / "heroics_index.yml"
        with open(index_file, 'w', encoding='utf-8') as f:
            yaml.dump(index_data, f)
        
        # Create test heroic
        heroic_data = {
            "heroic_id": "test_heroic",
            "name": "Test Heroic",
            "planet": "test_planet",
            "difficulty_tiers": {
                "normal": {
                    "level_requirement": 50,
                    "lockout_timer": 86400,  # 24 hours for testing
                    "reset_time": "daily"
                }
            },
            "prerequisites": {
                "quests": [],
                "skills": [],
                "items": [],
                "reputation": []
            }
        }
        
        heroic_file = Path(self.temp_dir) / "test_heroic.yml"
        with open(heroic_file, 'w', encoding='utf-8') as f:
            yaml.dump(heroic_data, f)
        
        # Reload the heroics manager to pick up the new data
        self.heroics_manager._load_heroics_data()

    def test_complete_workflow(self):
        """Test complete heroic workflow."""
        import time as time_module
        character_name = f"IntegrationTest_{int(time_module.time())}"  # Unique name
        heroic_id = "test_heroic"
        difficulty = "normal"
        
        # Step 1: Check prerequisites
        prerequisite_check = self.heroics_manager.check_prerequisites(character_name, heroic_id, difficulty)
        self.assertTrue(prerequisite_check["can_enter"])
        
        # Step 2: Record completion
        completion_data = {"loot": ["test_item"], "experience": 1000}
        success = self.heroics_manager.record_heroic_completion(character_name, heroic_id, difficulty, completion_data)
        self.assertTrue(success)
        
        # Step 3: Check lockout status
        lockout_status = self.lockout_tracker.check_lockout_status(character_name, heroic_id, difficulty)
        self.assertTrue(lockout_status["locked_out"])
        self.assertFalse(lockout_status["can_enter"])
        
        # Step 4: Check prerequisites again (should be locked out)
        prerequisite_check_after = self.heroics_manager.check_prerequisites(character_name, heroic_id, difficulty)
        self.assertFalse(prerequisite_check_after["can_enter"])
        self.assertEqual(prerequisite_check_after["reason"], "lockout")
        
        # Step 5: Wait a moment and check again to ensure lockout is properly set
        time_module.sleep(0.1)  # Small delay to ensure timestamps are different
        
        # Verify the lockout is still active
        final_lockout_status = self.lockout_tracker.check_lockout_status(character_name, heroic_id, difficulty)
        self.assertTrue(final_lockout_status["locked_out"])

    def test_multiple_characters(self):
        """Test multiple character support."""
        characters = ["Player1", "Player2", "Player3"]
        heroic_id = "test_heroic"
        difficulty = "normal"
        
        # Record completions for all characters
        for character in characters:
            success = self.lockout_tracker.record_heroic_completion(character, heroic_id, difficulty)
            self.assertTrue(success)
        
        # Check instance lockouts
        instance_lockouts = self.lockout_tracker.get_instance_lockouts(heroic_id)
        self.assertEqual(instance_lockouts["total_lockouts"], 3)
        
        # Check character lockouts
        for character in characters:
            character_lockouts = self.lockout_tracker.get_character_lockouts(character)
            self.assertEqual(character_lockouts["total_lockouts"], 1)

    def test_difficulty_tiers(self):
        """Test different difficulty tiers."""
        character_name = "DifficultyTest"
        heroic_id = "test_heroic"
        
        # Record normal difficulty completion
        self.lockout_tracker.record_heroic_completion(character_name, heroic_id, "normal")
        
        # Check lockout status for both difficulties
        normal_status = self.lockout_tracker.check_lockout_status(character_name, heroic_id, "normal")
        hard_status = self.lockout_tracker.check_lockout_status(character_name, heroic_id, "hard")
        
        # Normal should be locked out, hard should be available
        self.assertTrue(normal_status["locked_out"])
        self.assertFalse(hard_status["locked_out"])


class TestDataPersistence(unittest.TestCase):
    """Test data persistence functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.lockout_tracker = LockoutTracker(data_dir=self.temp_dir)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_data_persistence(self):
        """Test that data persists between instances."""
        character_name = "PersistenceTest"
        heroic_id = "test_heroic"
        
        # Record completion
        self.lockout_tracker.record_heroic_completion(character_name, heroic_id, "normal")
        
        # Create new instance
        new_tracker = LockoutTracker(data_dir=self.temp_dir)
        
        # Check that data was loaded
        lockout_status = new_tracker.check_lockout_status(character_name, heroic_id, "normal")
        self.assertTrue(lockout_status["locked_out"])

    def test_export_import(self):
        """Test export and import functionality."""
        character_name = "ExportTest"
        heroic_id = "test_heroic"
        
        # Record completion
        self.lockout_tracker.record_heroic_completion(character_name, heroic_id, "normal")
        
        # Export data
        export_path = self.lockout_tracker.export_lockout_data()
        
        # Verify export file exists and contains data
        self.assertTrue(Path(export_path).exists())
        
        with open(export_path, 'r', encoding='utf-8') as f:
            export_data = json.load(f)
        
        self.assertIn("lockout_data", export_data)
        self.assertIn("character_lockouts", export_data)
        self.assertIn("instance_lockouts", export_data)


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2) 