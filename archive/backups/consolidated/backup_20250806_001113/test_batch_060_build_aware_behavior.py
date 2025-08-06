"""Test suite for Batch 060 - Build-Aware Behavior System.

This test suite validates the functionality of the build-aware behavior system,
including skill calculator link parsing and combat behavior adaptation.
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

from core.skill_calculator_parser import SkillCalculatorParser
from core.build_aware_behavior import BuildAwareBehavior, create_build_aware_behavior
from android_ms11.core.combat_profile_engine import CombatProfileEngine


class TestSkillCalculatorParser(unittest.TestCase):
    """Test the skill calculator parser functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = SkillCalculatorParser()
        self.temp_dir = tempfile.mkdtemp()
        self.test_build_data = {
            "profession_boxes": ["rifleman", "medic"],
            "weapons_supported": ["rifle", "pistol"],
            "abilities_granted": ["Rifle Shot", "Heal", "Cure Poison"],
            "combat_style": "hybrid",
            "minimum_attack_distance": 3,
            "build_summary": "Rifleman + Medic | Weapons: rifle, pistol | Combat Style: Hybrid",
            "parsed_at": datetime.now().isoformat(),
            "source_url": "https://swgr.org/skill-calculator/rifleman_medic"
        }
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_parser_initialization(self):
        """Test that the parser initializes correctly."""
        self.assertIsNotNone(self.parser)
        self.assertEqual(self.parser.base_url, "https://swgr.org/skill-calculator/")
        self.assertIsNotNone(self.parser.session)
    
    def test_valid_skill_calculator_url(self):
        """Test URL validation for skill calculator links."""
        valid_urls = [
            "https://swgr.org/skill-calculator/rifleman",
            "https://swgr.org/skill-calculator/pistoleer?skills=shot",
            "https://swgr.org/skill-calculator/medic/advanced"
        ]
        
        invalid_urls = [
            "https://swgr.org/wiki/rifleman",
            "https://google.com/skill-calculator",
            "https://swgr.org/skill-calculator",
            "invalid-url"
        ]
        
        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(self.parser._is_valid_skill_calculator_url(url))
        
        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(self.parser._is_valid_skill_calculator_url(url))
    
    def test_extract_build_data_from_url(self):
        """Test extracting build data from URL parameters."""
        url = "https://swgr.org/skill-calculator/rifleman?skills=rifle_shot,marksman_shot&professions=rifleman"
        
        build_data = self.parser._extract_build_data_from_url(url)
        
        self.assertIn("profession", build_data)
        self.assertEqual(build_data["profession"], "rifleman")
        self.assertIn("skills", build_data)
        self.assertIn("professions", build_data)
    
    def test_parse_profession_boxes(self):
        """Test parsing profession boxes from build data."""
        build_data = {
            "profession": "rifleman",
            "professions": ["medic"],
            "skills": ["rifle_shot", "heal"]
        }
        
        profession_boxes = self.parser._parse_profession_boxes(build_data)
        
        self.assertIn("rifleman", profession_boxes)
        self.assertIn("medic", profession_boxes)
    
    def test_infer_professions_from_skills(self):
        """Test inferring professions from skill names."""
        skills = ["rifle_shot", "marksman_shot", "heal", "cure_poison"]
        
        professions = self.parser._infer_professions_from_skills(skills)
        
        self.assertIn("rifleman", professions)
        self.assertIn("medic", professions)
    
    def test_determine_weapons_supported(self):
        """Test determining weapons supported by profession boxes."""
        profession_boxes = ["rifleman", "pistoleer"]
        
        weapons = self.parser._determine_weapons_supported(profession_boxes)
        
        self.assertIn("rifle", weapons)
        self.assertIn("pistol", weapons)
    
    def test_extract_abilities_granted(self):
        """Test extracting abilities granted by profession boxes."""
        profession_boxes = ["rifleman", "medic"]
        
        abilities = self.parser._extract_abilities_granted(profession_boxes)
        
        self.assertIn("Rifle Shot", abilities)
        self.assertIn("Heal", abilities)
    
    def test_determine_combat_style(self):
        """Test determining combat style from profession boxes."""
        # Test melee style
        melee_professions = ["brawler", "swordsman"]
        style = self.parser._determine_combat_style(melee_professions)
        self.assertEqual(style, "melee")
        
        # Test ranged style
        ranged_professions = ["rifleman", "pistoleer"]
        style = self.parser._determine_combat_style(ranged_professions)
        self.assertEqual(style, "ranged")
        
        # Test support style
        support_professions = ["medic", "doctor"]
        style = self.parser._determine_combat_style(support_professions)
        self.assertEqual(style, "support")
    
    def test_calculate_minimum_attack_distance(self):
        """Test calculating minimum attack distance."""
        # Test melee distance
        distance = self.parser._calculate_minimum_attack_distance("melee", ["sword"])
        self.assertEqual(distance, 1)
        
        # Test ranged distance
        distance = self.parser._calculate_minimum_attack_distance("ranged", ["rifle"])
        self.assertEqual(distance, 5)
        
        # Test support distance
        distance = self.parser._calculate_minimum_attack_distance("support", ["pistol"])
        self.assertEqual(distance, 3)
    
    def test_generate_build_summary(self):
        """Test generating build summary."""
        profession_boxes = ["rifleman", "medic"]
        weapons_supported = ["rifle", "pistol"]
        abilities_granted = ["Rifle Shot", "Heal", "Cure Poison"]
        combat_style = "hybrid"
        
        summary = self.parser._generate_build_summary(
            profession_boxes, weapons_supported, abilities_granted, combat_style
        )
        
        self.assertIn("rifleman", summary)
        self.assertIn("medic", summary)
        self.assertIn("rifle", summary)
        self.assertIn("pistol", summary)
        self.assertIn("Hybrid", summary)
    
    def test_save_and_load_build(self):
        """Test saving and loading build data."""
        filename = "test_build.json"
        filepath = self.parser.save_build_to_file(self.test_build_data, filename)
        
        # Verify file was created
        self.assertTrue(Path(filepath).exists())
        
        # Load the build data
        loaded_data = self.parser.load_build_from_file(filepath)
        
        # Verify data matches
        self.assertEqual(loaded_data["profession_boxes"], self.test_build_data["profession_boxes"])
        self.assertEqual(loaded_data["weapons_supported"], self.test_build_data["weapons_supported"])
        self.assertEqual(loaded_data["abilities_granted"], self.test_build_data["abilities_granted"])
        
        # Clean up
        Path(filepath).unlink()
    
    @patch('core.skill_calculator_parser.SkillCalculatorParser._extract_build_data_from_url')
    def test_parse_skill_calculator_link(self, mock_extract):
        """Test parsing a complete skill calculator link."""
        # Mock the build data extraction
        mock_extract.return_value = {
            "profession": "rifleman",
            "skills": ["rifle_shot", "marksman_shot"]
        }
        
        url = "https://swgr.org/skill-calculator/rifleman?skills=rifle_shot,marksman_shot"
        
        result = self.parser.parse_skill_calculator_link(url)
        
        self.assertIn("profession_boxes", result)
        self.assertIn("weapons_supported", result)
        self.assertIn("abilities_granted", result)
        self.assertIn("combat_style", result)
        self.assertIn("minimum_attack_distance", result)
        self.assertIn("build_summary", result)
        self.assertIn("parsed_at", result)
        self.assertIn("source_url", result)


class TestBuildAwareBehavior(unittest.TestCase):
    """Test the build-aware behavior system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.combat_engine = Mock(spec=CombatProfileEngine)
        # Add profiles attribute to mock
        self.combat_engine.profiles = {}
        self.build_aware = BuildAwareBehavior(self.combat_engine)
        self.test_build_data = {
            "profession_boxes": ["rifleman", "medic"],
            "weapons_supported": ["rifle", "pistol"],
            "abilities_granted": ["Rifle Shot", "Heal", "Cure Poison"],
            "combat_style": "hybrid",
            "minimum_attack_distance": 3,
            "build_summary": "Rifleman + Medic | Weapons: rifle, pistol | Combat Style: Hybrid"
        }
    
    def test_initialization(self):
        """Test that the build-aware behavior system initializes correctly."""
        self.assertIsNotNone(self.build_aware)
        self.assertEqual(self.build_aware.combat_engine, self.combat_engine)
        self.assertIsNotNone(self.build_aware.skill_parser)
        self.assertIsNone(self.build_aware.current_build)
        self.assertEqual(self.build_aware.build_config, {})
    
    def test_create_build_config(self):
        """Test creating build configuration from parsed data."""
        config = self.build_aware._create_build_config(self.test_build_data)
        
        self.assertEqual(config["combat_style"], "hybrid")
        self.assertEqual(config["weapons_supported"], ["rifle", "pistol"])
        self.assertEqual(config["abilities_granted"], ["Rifle Shot", "Heal", "Cure Poison"])
        self.assertEqual(config["minimum_attack_distance"], 3)
        self.assertIn("preferred_distance", config)
        self.assertIn("movement_style", config)
        self.assertIn("ability_priorities", config)
        self.assertIn("targeting_style", config)
    
    def test_adapt_combat_behavior(self):
        """Test adapting combat behavior based on build configuration."""
        # Set up build config
        self.build_aware.build_config = self.build_aware._create_build_config(self.test_build_data)
        
        # Mock the adaptation methods
        with patch.object(self.build_aware, '_update_combat_profile') as mock_update:
            with patch.object(self.build_aware, '_adjust_ability_priorities') as mock_adjust:
                with patch.object(self.build_aware, '_set_combat_distance_preferences') as mock_set:
                    self.build_aware._adapt_combat_behavior()
                    
                    mock_update.assert_called_once()
                    mock_adjust.assert_called_once()
                    mock_set.assert_called_once()
    
    def test_generate_ability_rotation(self):
        """Test generating ability rotation based on build."""
        self.build_aware.build_config = {
            "abilities_granted": ["Rifle Shot", "Heal", "Cure Poison"],
            "combat_style": "hybrid"
        }
        
        rotation = self.build_aware._generate_ability_rotation()
        
        self.assertIn("Rifle Shot", rotation)
        self.assertIn("Heal", rotation)
        self.assertIn("Cure Poison", rotation)
    
    def test_generate_combat_strategy(self):
        """Test generating combat strategy based on build."""
        self.build_aware.build_config = {
            "combat_style": "ranged",
            "movement_style": "tactical",
            "targeting_style": "long_range",
            "preferred_distance": 5,
            "minimum_attack_distance": 3,
            "ability_priorities": ["ranged_attack", "sniper_shot"]
        }
        
        strategy = self.build_aware._generate_combat_strategy()
        
        self.assertEqual(strategy["primary_style"], "ranged")
        self.assertEqual(strategy["movement_approach"], "tactical")
        self.assertEqual(strategy["targeting_approach"], "long_range")
        self.assertIn("distance_management", strategy)
        self.assertIn("ability_usage", strategy)
    
    def test_adjust_ability_priorities(self):
        """Test adjusting ability priorities based on build."""
        abilities_granted = ["Melee Hit", "Rifle Shot", "Heal"]
        
        # Mock the combat engine to have ability_priorities attribute
        self.combat_engine.ability_priorities = {}
        
        self.build_aware._adjust_ability_priorities(abilities_granted)
        
        # Verify priorities were set
        self.assertIn("Melee Hit", self.combat_engine.ability_priorities)
        self.assertIn("Rifle Shot", self.combat_engine.ability_priorities)
        self.assertIn("Heal", self.combat_engine.ability_priorities)
    
    def test_set_combat_distance_preferences(self):
        """Test setting combat distance preferences."""
        self.build_aware.build_config = {
            "minimum_attack_distance": 3,
            "preferred_distance": 5
        }
        
        # Mock the combat engine to have distance_preferences attribute
        self.combat_engine.distance_preferences = {}
        
        self.build_aware._set_combat_distance_preferences()
        
        # Verify preferences were set
        self.assertEqual(self.combat_engine.distance_preferences["minimum_attack_distance"], 3)
        self.assertEqual(self.combat_engine.distance_preferences["preferred_distance"], 5)
        self.assertIn("maximum_effective_distance", self.combat_engine.distance_preferences)
    
    def test_calculate_maximum_distance(self):
        """Test calculating maximum effective distance."""
        # Test melee
        self.build_aware.build_config = {"combat_style": "melee"}
        max_distance = self.build_aware._calculate_maximum_distance()
        self.assertEqual(max_distance, 2)
        
        # Test ranged with heavy weapons
        self.build_aware.build_config = {
            "combat_style": "ranged",
            "weapons_supported": ["heavy_weapon", "grenade"]
        }
        max_distance = self.build_aware._calculate_maximum_distance()
        self.assertEqual(max_distance, 15)
        
        # Test ranged with rifles
        self.build_aware.build_config = {
            "combat_style": "ranged",
            "weapons_supported": ["rifle", "carbine"]
        }
        max_distance = self.build_aware._calculate_maximum_distance()
        self.assertEqual(max_distance, 12)
    
    def test_get_build_summary(self):
        """Test getting build summary."""
        # Test with no build loaded
        summary = self.build_aware.get_build_summary()
        self.assertEqual(summary, "No build loaded")
        
        # Test with build loaded
        self.build_aware.build_config = {"build_summary": "Test Build Summary"}
        summary = self.build_aware.get_build_summary()
        self.assertEqual(summary, "Test Build Summary")
    
    def test_get_combat_recommendations(self):
        """Test getting combat recommendations."""
        # Test with no build loaded
        recommendations = self.build_aware.get_combat_recommendations()
        self.assertIn("error", recommendations)
        
        # Test with build loaded
        self.build_aware.build_config = {
            "combat_style": "ranged",
            "weapons_supported": ["rifle", "pistol"],
            "abilities_granted": ["Rifle Shot", "Marksman Shot", "Sniper Shot"],
            "minimum_attack_distance": 5,
            "preferred_distance": 8,
            "movement_style": "tactical"
        }
        
        recommendations = self.build_aware.get_combat_recommendations()
        
        self.assertEqual(recommendations["combat_style"], "ranged")
        self.assertEqual(recommendations["recommended_weapons"], ["rifle", "pistol"])
        self.assertEqual(len(recommendations["priority_abilities"]), 3)
        self.assertIn("tactical_advice", recommendations)
    
    def test_generate_tactical_advice(self):
        """Test generating tactical advice."""
        # Test melee advice
        advice = self.build_aware._generate_tactical_advice("melee", ["sword"])
        self.assertIn("close range", advice[0].lower())
        
        # Test ranged advice
        advice = self.build_aware._generate_tactical_advice("ranged", ["rifle"])
        self.assertIn("optimal distance", advice[0].lower())
        
        # Test support advice
        advice = self.build_aware._generate_tactical_advice("support", ["pistol"])
        self.assertIn("medium range", advice[0].lower())
    
    @patch('core.build_aware_behavior.SkillCalculatorParser.parse_skill_calculator_link')
    def test_load_build_from_link(self, mock_parse):
        """Test loading build from skill calculator link."""
        # Mock the parser response
        mock_parse.return_value = self.test_build_data
        
        url = "https://swgr.org/skill-calculator/rifleman_medic"
        
        result = self.build_aware.load_build_from_link(url)
        
        self.assertEqual(result, self.test_build_data)
        self.assertEqual(self.build_aware.current_build, self.test_build_data)
        self.assertIsNotNone(self.build_aware.build_config)
    
    def test_save_and_load_build_config(self):
        """Test saving and loading build configuration."""
        # Set up build config
        self.build_aware.build_config = self.build_aware._create_build_config(self.test_build_data)
        
        # Save config
        config_file = self.build_aware.save_build_config("test_config.json")
        
        # Verify file was created
        self.assertTrue(Path(config_file).exists())
        
        # Load config
        loaded_config = self.build_aware.load_build_config(config_file)
        
        # Verify config matches
        self.assertEqual(loaded_config["combat_style"], "hybrid")
        self.assertEqual(loaded_config["weapons_supported"], ["rifle", "pistol"])
        
        # Clean up
        Path(config_file).unlink()


class TestIntegration(unittest.TestCase):
    """Test integration between components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_end_to_end_workflow(self):
        """Test the complete end-to-end workflow."""
        # Create parser and build-aware system
        parser = SkillCalculatorParser()
        build_aware = create_build_aware_behavior()
        
        # Mock the parsing to avoid actual network calls
        with patch.object(parser, 'parse_skill_calculator_link') as mock_parse:
            mock_parse.return_value = {
                "profession_boxes": ["rifleman"],
                "weapons_supported": ["rifle"],
                "abilities_granted": ["Rifle Shot", "Marksman Shot"],
                "combat_style": "ranged",
                "minimum_attack_distance": 5,
                "build_summary": "Rifleman | Weapons: rifle | Combat Style: Ranged"
            }
            
            # Test the complete workflow
            url = "https://swgr.org/skill-calculator/rifleman"
            
            # Parse the build
            build_data = parser.parse_skill_calculator_link(url)
            
            # Load into build-aware system
            result = build_aware.load_build_from_link(url)
            
            # Verify results
            self.assertEqual(build_data["combat_style"], "ranged")
            self.assertEqual(result["combat_style"], "ranged")
            
            # Get recommendations
            recommendations = build_aware.get_combat_recommendations()
            self.assertEqual(recommendations["combat_style"], "ranged")
    
    def test_create_build_aware_behavior(self):
        """Test the convenience function for creating build-aware behavior."""
        combat_engine = Mock(spec=CombatProfileEngine)
        
        build_aware = create_build_aware_behavior(combat_engine)
        
        self.assertIsInstance(build_aware, BuildAwareBehavior)
        self.assertEqual(build_aware.combat_engine, combat_engine)


def run_tests():
    """Run all tests and return results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSkillCalculatorParser))
    suite.addTests(loader.loadTestsFromTestCase(TestBuildAwareBehavior))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == "__main__":
    # Run tests
    result = run_tests()
    
    # Print summary
    print(f"\n=== Test Summary ===")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n=== Failures ===")
        for test, traceback in result.failures:
            print(f"FAIL: {test}")
            print(traceback)
    
    if result.errors:
        print(f"\n=== Errors ===")
        for test, traceback in result.errors:
            print(f"ERROR: {test}")
            print(traceback)
    
    # Exit with appropriate code
    exit_code = 0 if result.wasSuccessful() else 1
    exit(exit_code) 