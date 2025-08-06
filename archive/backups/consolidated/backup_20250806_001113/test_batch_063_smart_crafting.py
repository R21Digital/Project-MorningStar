"""Test Suite for Batch 063 - Smart Crafting Integration.

This test suite validates:
- Crafting mode toggle functionality
- Schematic loop execution
- Crafting validation (inventory, resources, power)
- Profession training integration
- Support for Artisan, Chef, and Structures professions
"""

import unittest
import json
import time
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

# Import the modules to test
from modules.crafting.crafting_manager import CraftingManager, CraftingStation, CraftingSession
from modules.crafting.schematic_looper import SchematicLooper, Schematic, CraftingResult
from modules.crafting.crafting_validator import CraftingValidator, ValidationResult
from modules.crafting.profession_trainer import ProfessionTrainer, TrainingLocation, TrainingSession


class TestCraftingManager(unittest.TestCase):
    """Test cases for CraftingManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary config file
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_config.write(json.dumps({
            "crafting_mode": {
                "enabled": False,
                "auto_detect_stations": True,
                "preferred_station_types": ["artisan", "chef", "structures"]
            },
            "profiles": {
                "default": {
                    "station_type": "artisan",
                    "schematics": ["Basic Tool", "Survey Device"],
                    "max_quantity": 10,
                    "resource_check": True,
                    "power_check": True
                }
            },
            "validation": {
                "min_inventory_space": 5,
                "min_power": 100,
                "required_resources": ["metal", "chemical", "fiber"]
            }
        }))
        self.temp_config.close()
        
        # Mock dependencies
        self.mock_ocr = Mock()
        self.mock_screenshot = Mock()
        self.mock_state_tracker = Mock()
        
        with patch('modules.crafting.crafting_manager.OCREngine', return_value=self.mock_ocr), \
             patch('modules.crafting.crafting_manager.capture_screen', return_value=self.mock_screenshot), \
             patch('modules.crafting.crafting_manager.update_state', side_effect=self.mock_state_tracker), \
             patch('modules.crafting.crafting_manager.get_state', return_value="Unknown"):
            
            self.manager = CraftingManager(self.temp_config.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.unlink(self.temp_config.name)
    
    def test_crafting_manager_initialization(self):
        """Test CraftingManager initialization."""
        self.assertIsNotNone(self.manager)
        self.assertFalse(self.manager.config["crafting_mode"]["enabled"])
        self.assertEqual(len(self.manager.known_stations), 3)
    
    def test_toggle_crafting_mode(self):
        """Test crafting mode toggle functionality."""
        # Test enabling
        result = self.manager.toggle_crafting_mode(True)
        self.assertTrue(result)
        self.assertTrue(self.manager.config["crafting_mode"]["enabled"])
        
        # Test disabling
        result = self.manager.toggle_crafting_mode(False)
        self.assertFalse(result)
        self.assertFalse(self.manager.config["crafting_mode"]["enabled"])
        
        # Test toggle
        result = self.manager.toggle_crafting_mode()
        self.assertTrue(result)
        self.assertTrue(self.manager.config["crafting_mode"]["enabled"])
    
    def test_detect_crafting_stations(self):
        """Test crafting station detection."""
        # Mock OCR results
        mock_result = Mock()
        mock_result.text = "Artisan Workbench"
        mock_result.x = 100
        mock_result.y = 200
        self.mock_ocr.scan_text.return_value = [mock_result]
        
        stations = self.manager.detect_crafting_stations()
        
        self.assertEqual(len(stations), 1)
        self.assertEqual(stations[0].name, "Artisan Workbench")
        self.assertEqual(stations[0].station_type, "artisan")
        self.assertEqual(stations[0].coords, (100, 200))
    
    def test_start_crafting_session(self):
        """Test starting a crafting session."""
        # Enable crafting mode
        self.manager.toggle_crafting_mode(True)
        
        # Mock station detection
        mock_station = CraftingStation(
            name="Artisan Workbench",
            station_type="artisan",
            location="Test Location",
            coords=(100, 200),
            ui_elements=["craft", "create"]
        )
        
        with patch.object(self.manager, 'detect_crafting_stations', return_value=[mock_station]), \
             patch.object(self.manager.validator, 'validate_crafting_requirements', return_value=True):
            
            result = self.manager.start_crafting_session("default")
            self.assertTrue(result)
            self.assertIsNotNone(self.manager.active_session)
            self.assertEqual(self.manager.active_session.profile_name, "default")
    
    def test_run_crafting_loop(self):
        """Test running the crafting loop."""
        # Set up active session
        mock_station = CraftingStation(
            name="Artisan Workbench",
            station_type="artisan",
            location="Test Location",
            coords=(100, 200),
            ui_elements=["craft", "create"]
        )
        
        self.manager.active_session = CraftingSession(
            station=mock_station,
            profile_name="default",
            start_time=time.time(),
            session_id="test_session"
        )
        
        # Mock schematic looper
        mock_results = {
            "items_crafted": 5,
            "schematics_completed": ["Basic Tool", "Survey Device"],
            "total_experience": 125,
            "errors": []
        }
        
        with patch.object(self.manager.schematic_looper, 'run_schematic_loop', return_value=mock_results):
            results = self.manager.run_crafting_loop()
            
            self.assertEqual(results["items_crafted"], 5)
            self.assertEqual(len(results["schematics_completed"]), 2)
            self.assertEqual(results["total_experience"], 125)
    
    def test_stop_crafting_session(self):
        """Test stopping a crafting session."""
        # Set up active session
        mock_station = CraftingStation(
            name="Artisan Workbench",
            station_type="artisan",
            location="Test Location",
            coords=(100, 200),
            ui_elements=["craft", "create"]
        )
        
        self.manager.active_session = CraftingSession(
            station=mock_station,
            profile_name="default",
            start_time=time.time() - 60,  # 1 minute ago
            session_id="test_session"
        )
        
        summary = self.manager.stop_crafting_session()
        
        self.assertTrue(summary["success"])
        self.assertEqual(summary["profile_name"], "default")
        self.assertIsNone(self.manager.active_session)
    
    def test_get_crafting_status(self):
        """Test getting crafting status."""
        status = self.manager.get_crafting_status()
        
        self.assertIn("mode_enabled", status)
        self.assertIn("active_session", status)
        self.assertIn("available_profiles", status)
        self.assertIn("known_stations", status)


class TestSchematicLooper(unittest.TestCase):
    """Test cases for SchematicLooper."""
    
    def setUp(self):
        """Set up test fixtures."""
        with patch('modules.crafting.schematic_looper.OCREngine'), \
             patch('modules.crafting.schematic_looper.capture_screen'), \
             patch('modules.crafting.schematic_looper.update_state'):
            
            self.looper = SchematicLooper()
    
    def test_schematic_looper_initialization(self):
        """Test SchematicLooper initialization."""
        self.assertIsNotNone(self.looper)
        self.assertGreater(len(self.looper.known_schematics), 0)
        self.assertEqual(len(self.looper.ui_mappings), 3)
    
    def test_load_known_schematics(self):
        """Test loading known schematics."""
        schematics = self.looper._load_known_schematics()
        
        # Check that schematics are loaded for each profession
        self.assertIn("Basic Tool", schematics)
        self.assertIn("Basic Meal", schematics)
        self.assertIn("Basic Structure", schematics)
        
        # Check schematic properties
        basic_tool = schematics["Basic Tool"]
        self.assertEqual(basic_tool.profession, "artisan")
        self.assertEqual(basic_tool.difficulty, 1)
        self.assertIn("metal", basic_tool.materials)
    
    def test_run_schematic_loop(self):
        """Test running schematic loop."""
        schematic_names = ["Basic Tool", "Survey Device"]
        
        with patch.object(self.looper, '_craft_schematic') as mock_craft:
            # Mock successful crafting
            mock_result = CraftingResult(
                schematic_name="Basic Tool",
                success=True,
                quantity=1,
                experience_gained=50,
                materials_used=["metal", "chemical"],
                crafting_time=30.0,
                timestamp=time.time()
            )
            mock_craft.return_value = mock_result
            
            results = self.looper.run_schematic_loop(schematic_names, max_quantity=5)
            
            self.assertEqual(results["items_crafted"], 2)
            self.assertEqual(len(results["schematics_completed"]), 2)
            self.assertEqual(results["total_experience"], 100)
    
    def test_craft_schematic_success(self):
        """Test successful schematic crafting."""
        schematic = Schematic(
            name="Basic Tool",
            profession="artisan",
            difficulty=1,
            materials=["metal", "chemical"],
            crafting_time=30,
            experience_gain=50,
            ui_elements=["craft", "create"]
        )
        
        with patch.object(self.looper, '_detect_crafting_ui', return_value=True), \
             patch.object(self.looper, '_select_schematic', return_value=True), \
             patch.object(self.looper, '_start_crafting', return_value=True), \
             patch.object(self.looper, '_complete_crafting', return_value=True):
            
            result = self.looper._craft_schematic(schematic, 1)
            
            self.assertTrue(result.success)
            self.assertEqual(result.quantity, 1)
            self.assertEqual(result.experience_gained, 50)
            self.assertEqual(result.schematic_name, "Basic Tool")
    
    def test_craft_schematic_failure(self):
        """Test failed schematic crafting."""
        schematic = Schematic(
            name="Basic Tool",
            profession="artisan",
            difficulty=1,
            materials=["metal", "chemical"],
            crafting_time=30,
            experience_gain=50,
            ui_elements=["craft", "create"]
        )
        
        with patch.object(self.looper, '_detect_crafting_ui', return_value=False):
            result = self.looper._craft_schematic(schematic, 1)
            
            self.assertFalse(result.success)
            self.assertEqual(result.quantity, 0)
            self.assertEqual(result.experience_gained, 0)
    
    def test_get_crafting_history(self):
        """Test getting crafting history."""
        # Add some test results
        test_result = CraftingResult(
            schematic_name="Basic Tool",
            success=True,
            quantity=1,
            experience_gained=50,
            materials_used=["metal", "chemical"],
            crafting_time=30.0,
            timestamp=time.time()
        )
        self.looper.crafting_history.append(test_result)
        
        history = self.looper.get_crafting_history()
        
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["schematic_name"], "Basic Tool")
        self.assertTrue(history[0]["success"])
    
    def test_get_schematic_stats(self):
        """Test getting schematic statistics."""
        # Add test results
        for i in range(5):
            result = CraftingResult(
                schematic_name="Basic Tool",
                success=i < 4,  # 4 successful, 1 failed
                quantity=1 if i < 4 else 0,
                experience_gained=50 if i < 4 else 0,
                materials_used=["metal", "chemical"] if i < 4 else [],
                crafting_time=30.0,
                timestamp=time.time()
            )
            self.looper.crafting_history.append(result)
        
        stats = self.looper.get_schematic_stats("Basic Tool")
        
        self.assertEqual(stats["total_crafted"], 4)
        self.assertEqual(stats["success_rate"], 0.8)
        self.assertEqual(stats["total_experience"], 200)
        self.assertEqual(stats["average_crafting_time"], 30.0)


class TestCraftingValidator(unittest.TestCase):
    """Test cases for CraftingValidator."""
    
    def setUp(self):
        """Set up test fixtures."""
        with patch('modules.crafting.crafting_validator.OCREngine'), \
             patch('modules.crafting.crafting_validator.capture_screen'), \
             patch('modules.crafting.crafting_validator.get_state', return_value=100):
            
            self.validator = CraftingValidator()
    
    def test_validator_initialization(self):
        """Test CraftingValidator initialization."""
        self.assertIsNotNone(self.validator)
        self.assertEqual(self.validator.default_thresholds["min_inventory_space"], 5)
        self.assertEqual(self.validator.default_thresholds["min_power"], 100)
    
    def test_validate_crafting_requirements_success(self):
        """Test successful crafting requirements validation."""
        profile = {
            "min_inventory_space": 3,
            "min_power": 80,
            "required_resources": ["metal", "chemical"]
        }
        
        with patch.object(self.validator, '_validate_inventory_space', return_value=True), \
             patch.object(self.validator, '_validate_power_level', return_value=True), \
             patch.object(self.validator, '_validate_resources', return_value=[]), \
             patch.object(self.validator, '_validate_character_status', return_value=True):
            
            result = self.validator.validate_crafting_requirements(profile)
            self.assertTrue(result)
    
    def test_validate_crafting_requirements_failure(self):
        """Test failed crafting requirements validation."""
        profile = {
            "min_inventory_space": 10,
            "min_power": 200,
            "required_resources": ["metal", "chemical", "fiber"]
        }
        
        with patch.object(self.validator, '_validate_inventory_space', return_value=False), \
             patch.object(self.validator, '_validate_power_level', return_value=True), \
             patch.object(self.validator, '_validate_resources', return_value=[]), \
             patch.object(self.validator, '_validate_character_status', return_value=True):
            
            result = self.validator.validate_crafting_requirements(profile)
            self.assertFalse(result)
    
    def test_validate_inventory_space(self):
        """Test inventory space validation."""
        profile = {"min_inventory_space": 5}
        
        with patch('modules.crafting.crafting_validator.get_state', return_value=10):
            result = self.validator._validate_inventory_space(profile)
            self.assertTrue(result)
        
        with patch('modules.crafting.crafting_validator.get_state', return_value=3):
            result = self.validator._validate_inventory_space(profile)
            self.assertFalse(result)
    
    def test_validate_power_level(self):
        """Test power level validation."""
        profile = {"min_power": 100}
        
        with patch('modules.crafting.crafting_validator.get_state', return_value=200):
            result = self.validator._validate_power_level(profile)
            self.assertTrue(result)
        
        with patch('modules.crafting.crafting_validator.get_state', return_value=50):
            result = self.validator._validate_power_level(profile)
            self.assertFalse(result)
    
    def test_validate_resources(self):
        """Test resource validation."""
        profile = {"required_resources": ["metal", "chemical"]}
        
        # Mock inventory with all required resources
        mock_inventory = {"metal": 5, "chemical": 3, "fiber": 1}
        with patch('modules.crafting.crafting_validator.get_state', return_value=mock_inventory):
            missing = self.validator._validate_resources(profile)
            self.assertEqual(len(missing), 0)
        
        # Mock inventory missing some resources
        mock_inventory = {"metal": 5, "fiber": 1}
        with patch('modules.crafting.crafting_validator.get_state', return_value=mock_inventory):
            missing = self.validator._validate_resources(profile)
            self.assertIn("chemical", missing)
    
    def test_scan_inventory_for_resources(self):
        """Test inventory resource scanning."""
        # Mock OCR results
        mock_result1 = Mock()
        mock_result1.text = "metal 5"
        mock_result2 = Mock()
        mock_result2.text = "chemical 3"
        
        with patch.object(self.validator.ocr_engine, 'scan_text', return_value=[mock_result1, mock_result2]):
            resources = self.validator.scan_inventory_for_resources()
            
            self.assertIn("metal", resources)
            self.assertIn("chemical", resources)
            self.assertEqual(resources["metal"], 5)
            self.assertEqual(resources["chemical"], 3)
    
    def test_get_validation_summary(self):
        """Test getting validation summary."""
        profile = {
            "min_inventory_space": 5,
            "min_power": 100,
            "required_resources": ["metal", "chemical"]
        }
        
        with patch.object(self.validator, '_validate_inventory_space', return_value=True), \
             patch.object(self.validator, '_validate_power_level', return_value=True), \
             patch.object(self.validator, '_validate_resources', return_value=[]), \
             patch.object(self.validator, '_validate_character_status', return_value=True), \
             patch.object(self.validator, 'scan_inventory_for_resources', return_value={"metal": 5, "chemical": 3}):
            
            summary = self.validator.get_validation_summary(profile)
            
            self.assertTrue(summary["overall_valid"])
            self.assertTrue(summary["inventory_space"]["valid"])
            self.assertTrue(summary["power_level"]["valid"])
            self.assertEqual(len(summary["resources"]["missing"]), 0)
            self.assertTrue(summary["character_status"]["valid"])


class TestProfessionTrainer(unittest.TestCase):
    """Test cases for ProfessionTrainer."""
    
    def setUp(self):
        """Set up test fixtures."""
        with patch('modules.crafting.profession_trainer.OCREngine'), \
             patch('modules.crafting.profession_trainer.capture_screen'), \
             patch('modules.crafting.profession_trainer.update_state'), \
             patch('modules.crafting.profession_trainer.TravelManager'):
            
            self.trainer = ProfessionTrainer()
    
    def test_trainer_initialization(self):
        """Test ProfessionTrainer initialization."""
        self.assertIsNotNone(self.trainer)
        self.assertEqual(len(self.trainer.training_locations), 3)
        self.assertEqual(len(self.trainer.skill_trees), 3)
    
    def test_get_available_skills(self):
        """Test getting available skills."""
        artisan_skills = self.trainer.get_available_skills("artisan")
        self.assertEqual(artisan_skills, ["crafting_artisan_novice"])
        
        chef_skills = self.trainer.get_available_skills("chef")
        self.assertEqual(chef_skills, ["crafting_chef_novice"])
    
    def test_get_current_skills(self):
        """Test getting current skills."""
        current_skills = self.trainer.get_current_skills()
        
        self.assertIn("artisan", current_skills)
        self.assertIn("chef", current_skills)
        self.assertIn("structures", current_skills)
        self.assertIn("crafting_artisan_novice", current_skills["artisan"])
    
    def test_get_missing_skills(self):
        """Test getting missing skills."""
        missing_artisan = self.trainer.get_missing_skills("artisan")
        self.assertEqual(len(missing_artisan), 0)  # Already has novice
        
        missing_chef = self.trainer.get_missing_skills("chef")
        self.assertIn("crafting_chef_novice", missing_chef)
    
    def test_find_training_location(self):
        """Test finding training location."""
        location = self.trainer.find_training_location("artisan", "crafting_artisan_novice")
        self.assertIsNotNone(location)
        self.assertEqual(location.profession, "artisan")
        self.assertIn("crafting_artisan_novice", location.available_skills)
        
        # Test non-existent skill
        location = self.trainer.find_training_location("artisan", "non_existent_skill")
        self.assertIsNone(location)
    
    def test_start_training_session(self):
        """Test starting a training session."""
        with patch.object(self.trainer, '_travel_to_training_location', return_value=True):
            result = self.trainer.start_training_session("chef")
            
            self.assertTrue(result)
            self.assertIsNotNone(self.trainer.active_session)
            self.assertEqual(self.trainer.active_session.profession, "chef")
    
    def test_run_training_loop(self):
        """Test running training loop."""
        # Set up active session
        mock_location = TrainingLocation(
            name="Chef Trainer - Corellia",
            profession="chef",
            planet="Corellia",
            city="Coronet",
            coords=(120, 180),
            trainer_name="Master Chef",
            available_skills=["crafting_chef_novice", "crafting_chef_apprentice"]
        )
        
        self.trainer.active_session = TrainingSession(
            profession="chef",
            location=mock_location,
            skills_to_learn=["crafting_chef_novice"],
            start_time=time.time()
        )
        
        with patch.object(self.trainer, '_interact_with_trainer', return_value=True), \
             patch.object(self.trainer, '_learn_skill', return_value=True):
            
            results = self.trainer.run_training_loop()
            
            self.assertEqual(results["skills_learned"], 1)
            self.assertIn("crafting_chef_novice", results["skills_completed"])
    
    def test_stop_training_session(self):
        """Test stopping training session."""
        # Set up active session
        mock_location = TrainingLocation(
            name="Chef Trainer - Corellia",
            profession="chef",
            planet="Corellia",
            city="Coronet",
            coords=(120, 180),
            trainer_name="Master Chef",
            available_skills=["crafting_chef_novice"]
        )
        
        self.trainer.active_session = TrainingSession(
            profession="chef",
            location=mock_location,
            skills_to_learn=["crafting_chef_novice"],
            start_time=time.time() - 60,
            skills_learned=1
        )
        
        summary = self.trainer.stop_training_session()
        
        self.assertTrue(summary["success"])
        self.assertEqual(summary["skills_learned"], 1)
        self.assertIsNone(self.trainer.active_session)
    
    def test_get_training_status(self):
        """Test getting training status."""
        status = self.trainer.get_training_status()
        
        self.assertIn("active_session", status)
        self.assertIn("current_skills", status)
        self.assertIn("available_locations", status)
        self.assertIn("missing_skills", status)
    
    def test_get_profession_progress(self):
        """Test getting profession progress."""
        progress = self.trainer.get_profession_progress("artisan")
        
        self.assertEqual(progress["profession"], "artisan")
        self.assertIn("learned_skills", progress)
        self.assertIn("total_skills", progress)
        self.assertIn("progress_percentage", progress)


class TestCraftingIntegration(unittest.TestCase):
    """Integration tests for the complete crafting system."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary config
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_config.write(json.dumps({
            "crafting_mode": {"enabled": True},
            "profiles": {
                "test_profile": {
                    "station_type": "artisan",
                    "schematics": ["Basic Tool"],
                    "max_quantity": 2,
                    "resource_check": True,
                    "power_check": True
                }
            },
            "validation": {
                "min_inventory_space": 3,
                "min_power": 80
            }
        }))
        self.temp_config.close()
        
        # Mock all dependencies
        self.patches = [
            patch('modules.crafting.crafting_manager.OCREngine'),
            patch('modules.crafting.crafting_manager.capture_screen'),
            patch('modules.crafting.crafting_manager.update_state'),
            patch('modules.crafting.crafting_manager.get_state', return_value=100),
            patch('modules.crafting.schematic_looper.OCREngine'),
            patch('modules.crafting.schematic_looper.capture_screen'),
            patch('modules.crafting.schematic_looper.update_state'),
            patch('modules.crafting.crafting_validator.OCREngine'),
            patch('modules.crafting.crafting_validator.capture_screen'),
            patch('modules.crafting.crafting_validator.get_state', return_value=100),
            patch('modules.crafting.profession_trainer.OCREngine'),
            patch('modules.crafting.profession_trainer.capture_screen'),
            patch('modules.crafting.profession_trainer.update_state'),
            patch('modules.crafting.profession_trainer.TravelManager')
        ]
        
        for p in self.patches:
            p.start()
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.unlink(self.temp_config.name)
        for p in self.patches:
            p.stop()
    
    def test_complete_crafting_workflow(self):
        """Test complete crafting workflow from start to finish."""
        # Initialize manager
        manager = CraftingManager(self.temp_config.name)
        
        # Enable crafting mode
        manager.toggle_crafting_mode(True)
        self.assertTrue(manager.config["crafting_mode"]["enabled"])
        
        # Mock station detection
        mock_station = CraftingStation(
            name="Artisan Workbench",
            station_type="artisan",
            location="Test Location",
            coords=(100, 200),
            ui_elements=["craft", "create"]
        )
        
        with patch.object(manager, 'detect_crafting_stations', return_value=[mock_station]), \
             patch.object(manager.validator, 'validate_crafting_requirements', return_value=True), \
             patch.object(manager.schematic_looper, 'run_schematic_loop', return_value={
                 "items_crafted": 2,
                 "schematics_completed": ["Basic Tool"],
                 "total_experience": 100,
                 "errors": []
             }):
            
            # Start crafting session
            result = manager.start_crafting_session("test_profile")
            self.assertTrue(result)
            self.assertIsNotNone(manager.active_session)
            
            # Run crafting loop
            results = manager.run_crafting_loop()
            self.assertEqual(results["items_crafted"], 2)
            self.assertEqual(len(results["schematics_completed"]), 1)
            
            # Stop session
            summary = manager.stop_crafting_session()
            self.assertTrue(summary["success"])
            self.assertEqual(summary["items_crafted"], 2)
    
    def test_profession_training_workflow(self):
        """Test complete profession training workflow."""
        trainer = ProfessionTrainer()
        
        # Mock travel and training
        with patch.object(trainer, '_travel_to_training_location', return_value=True), \
             patch.object(trainer, '_interact_with_trainer', return_value=True), \
             patch.object(trainer, '_learn_skill', return_value=True):
            
            # Start training session
            result = trainer.start_training_session("chef")
            self.assertTrue(result)
            self.assertIsNotNone(trainer.active_session)
            
            # Run training loop
            results = trainer.run_training_loop()
            self.assertGreaterEqual(results["skills_learned"], 0)
            
            # Stop session
            summary = trainer.stop_training_session()
            self.assertTrue(summary["success"])


def run_crafting_tests():
    """Run all crafting tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestCraftingManager,
        TestSchematicLooper,
        TestCraftingValidator,
        TestProfessionTrainer,
        TestCraftingIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"CRAFTING SYSTEM TEST RESULTS")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    print("🧪 Running Batch 063 - Smart Crafting Integration Tests")
    print("=" * 60)
    
    success = run_crafting_tests()
    
    if success:
        print("\n✅ All crafting tests passed!")
    else:
        print("\n❌ Some crafting tests failed!")
    
    print("\n" + "=" * 60) 