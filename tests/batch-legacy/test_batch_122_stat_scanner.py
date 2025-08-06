#!/usr/bin/env python3
"""
Test Script for Batch 122 - Stat Scanner + Attribute Parser
Comprehensive testing of the enhanced stat scanning and attribute parsing features.
"""

import json
import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ocr.stat_extractor import (
    StatExtractor, CharacterProfile, CharacterStat, StatType,
    get_stat_extractor, extract_character_stats, save_character_stats, load_character_stats
)
from core.attribute_profile import (
    AttributeProfileManager, OptimizationType, OptimizationProfile, OptimizationTarget,
    get_attribute_profile_manager, create_optimization_profile, analyze_optimization,
    establish_character_baseline
)
from swgdb_api.push_stat_data import (
    SWGDBStatAPIClient, SWGDBStatUploadManager,
    test_api_connection
)


class TestStatExtractor(unittest.TestCase):
    """Test class for the stat extractor functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)

        # Create test directory structure
        self.data_dir = self.project_root / "data"
        self.config_dir = self.project_root / "config"

        for directory in [self.data_dir, self.config_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir)

    def test_stat_extractor_initialization(self):
        """Test stat extractor initialization."""
        extractor = StatExtractor()

        self.assertIsNotNone(extractor.ocr_engine)
        self.assertIsNotNone(extractor.stat_patterns)
        self.assertIsNotNone(extractor.resistance_patterns)
        self.assertIsNotNone(extractor.tape_patterns)
        self.assertIsNotNone(extractor.panel_regions)

        # Check stat patterns
        self.assertIn(StatType.HEALTH, extractor.stat_patterns)
        self.assertIn(StatType.ACTION, extractor.stat_patterns)
        self.assertIn(StatType.MIND, extractor.stat_patterns)
        self.assertIn(StatType.LUCK, extractor.stat_patterns)

    def test_parse_stats_from_text(self):
        """Test parsing stats from text."""
        extractor = StatExtractor()

        test_text = """
        Character Stats:
        Health: 1500/1500
        Action: 800/800
        Mind: 600/600
        Luck: 25
        
        Armor Stats:
        Energy Resistance: 45
        Blast Resistance: 30
        Kinetic Resistance: 25
        Heat Resistance: 20
        
        Tapes:
        Energy Tape: 15
        Blast Tape: 10
        Kinetic Tape: 8
        """

        stats = extractor._parse_stats_from_text(test_text, "test_source", 85.0)

        self.assertGreater(len(stats), 0)

        # Check specific stats
        health_stat = stats.get(StatType.HEALTH)
        if health_stat:
            self.assertEqual(health_stat.current_value, 1500)
            self.assertEqual(health_stat.max_value, 1500)
            self.assertEqual(health_stat.percentage, 100.0)

        action_stat = stats.get(StatType.ACTION)
        if action_stat:
            self.assertEqual(action_stat.current_value, 800)
            self.assertEqual(action_stat.max_value, 800)

        luck_stat = stats.get(StatType.LUCK)
        if luck_stat:
            self.assertEqual(luck_stat.current_value, 25)
            self.assertEqual(luck_stat.max_value, 25)

    def test_extract_stats_via_macro(self):
        """Test extracting stats via macro."""
        extractor = StatExtractor()

        stats = extractor.extract_stats_via_macro()

        self.assertIsInstance(stats, dict)
        self.assertGreater(len(stats), 0)

        for stat_type, stat in stats.items():
            self.assertIsInstance(stat, CharacterStat)
            self.assertIsInstance(stat_type, StatType)
            self.assertGreaterEqual(stat.current_value, 0)
            self.assertGreaterEqual(stat.max_value, 0)
            self.assertGreaterEqual(stat.confidence, 0)
            self.assertLessEqual(stat.confidence, 100)

    def test_create_character_profile(self):
        """Test creating character profile."""
        extractor = StatExtractor()

        profile = extractor.create_character_profile("TestCharacter", "Rifleman", 50)

        self.assertIsInstance(profile, CharacterProfile)
        self.assertEqual(profile.character_name, "TestCharacter")
        self.assertEqual(profile.profession, "Rifleman")
        self.assertEqual(profile.level, 50)
        self.assertIsInstance(profile.stats, dict)
        self.assertIsInstance(profile.resistances, dict)
        self.assertIsInstance(profile.tapes, dict)
        self.assertGreaterEqual(profile.confidence_score, 0)
        self.assertLessEqual(profile.confidence_score, 100)

    def test_validate_stat_data(self):
        """Test stat data validation."""
        extractor = StatExtractor()

        # Create test profile
        profile = extractor.create_character_profile("TestCharacter", "Rifleman", 50)

        validation = extractor.validate_stat_data(profile)

        self.assertIsInstance(validation, dict)
        self.assertIn("valid", validation)
        self.assertIn("warnings", validation)
        self.assertIn("errors", validation)
        self.assertIn("confidence_score", validation)

    def test_save_and_load_character_profile(self):
        """Test saving and loading character profile."""
        extractor = StatExtractor()

        # Create test profile
        profile = extractor.create_character_profile("TestCharacter", "Rifleman", 50)

        # Save profile
        saved = extractor.save_character_profile(profile)
        self.assertTrue(saved)

        # Load profile
        loaded = extractor.load_character_profile("TestCharacter")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.character_name, profile.character_name)
        self.assertEqual(loaded.profession, profile.profession)
        self.assertEqual(loaded.level, profile.level)

        # Compare stats
        for stat_type, original_stat in profile.stats.items():
            loaded_stat = loaded.stats.get(stat_type)
            if loaded_stat:
                self.assertEqual(original_stat.current_value, loaded_stat.current_value)
                self.assertEqual(original_stat.max_value, loaded_stat.max_value)


class TestAttributeProfileManager(unittest.TestCase):
    """Test class for the attribute profile manager functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)

        # Create test directory structure
        self.data_dir = self.project_root / "data"
        self.config_dir = self.project_root / "config"

        for directory in [self.data_dir, self.config_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir)

    def test_attribute_profile_manager_initialization(self):
        """Test attribute profile manager initialization."""
        manager = AttributeProfileManager()

        self.assertIsNotNone(manager.profession_targets)
        self.assertIsNotNone(manager.default_targets)

        # Check profession targets
        self.assertIn("rifleman", manager.profession_targets)
        self.assertIn("medic", manager.profession_targets)
        self.assertIn("pistoleer", manager.profession_targets)

    def test_create_optimization_profile(self):
        """Test creating optimization profile."""
        manager = AttributeProfileManager()

        # Create test character profile
        from ocr.stat_extractor import get_stat_extractor
        extractor = get_stat_extractor()
        char_profile = extractor.create_character_profile("TestCharacter", "Rifleman", 50)

        # Create optimization profile
        opt_profile = manager.create_optimization_profile(char_profile, OptimizationType.COMBAT)

        self.assertIsInstance(opt_profile, OptimizationProfile)
        self.assertEqual(opt_profile.character_name, "TestCharacter")
        self.assertEqual(opt_profile.profession, "Rifleman")
        self.assertEqual(opt_profile.optimization_type, OptimizationType.COMBAT)
        self.assertIsInstance(opt_profile.targets, list)
        self.assertGreaterEqual(opt_profile.optimization_score, 0)
        self.assertLessEqual(opt_profile.optimization_score, 100)

    def test_analyze_stat_gaps(self):
        """Test analyzing stat gaps."""
        manager = AttributeProfileManager()

        # Create test optimization profile
        from ocr.stat_extractor import get_stat_extractor
        extractor = get_stat_extractor()
        char_profile = extractor.create_character_profile("TestCharacter", "Rifleman", 50)
        opt_profile = manager.create_optimization_profile(char_profile, OptimizationType.COMBAT)

        analysis = manager.analyze_stat_gaps(opt_profile)

        self.assertIsInstance(analysis, dict)
        self.assertIn("character_name", analysis)
        self.assertIn("profession", analysis)
        self.assertIn("optimization_type", analysis)
        self.assertIn("overall_score", analysis)
        self.assertIn("stat_gaps", analysis)
        self.assertIn("recommendations", analysis)
        self.assertIn("priority_improvements", analysis)
        self.assertIn("easy_wins", analysis)

    def test_establish_and_load_baseline(self):
        """Test establishing and loading baseline."""
        manager = AttributeProfileManager()

        # Create test character profile
        from ocr.stat_extractor import get_stat_extractor
        extractor = get_stat_extractor()
        char_profile = extractor.create_character_profile("TestCharacter", "Rifleman", 50)

        # Establish baseline
        baseline_established = manager.establish_baseline("TestCharacter", char_profile)
        self.assertTrue(baseline_established)

        # Load baseline
        loaded_baseline = manager.load_baseline("TestCharacter")
        self.assertIsNotNone(loaded_baseline)
        self.assertEqual(loaded_baseline.character_name, "TestCharacter")
        self.assertEqual(loaded_baseline.profession, "Rifleman")

    def test_compare_with_baseline(self):
        """Test comparing with baseline."""
        manager = AttributeProfileManager()

        # Create baseline profile
        from ocr.stat_extractor import get_stat_extractor
        extractor = get_stat_extractor()
        baseline_profile = extractor.create_character_profile("TestCharacter", "Rifleman", 50)

        # Create current profile (simulating improvement)
        current_profile = extractor.create_character_profile("TestCharacter", "Rifleman", 55)

        # Compare with baseline
        comparison = manager.compare_with_baseline(current_profile, baseline_profile)

        self.assertIsInstance(comparison, dict)
        self.assertIn("character_name", comparison)
        self.assertIn("baseline_date", comparison)
        self.assertIn("current_date", comparison)
        self.assertIn("time_elapsed_days", comparison)
        self.assertIn("stat_changes", comparison)
        self.assertIn("overall_improvement", comparison)
        self.assertIn("improvements", comparison)
        self.assertIn("regressions", comparison)
        self.assertIn("unchanged", comparison)

    def test_get_optimization_recommendations(self):
        """Test getting optimization recommendations."""
        manager = AttributeProfileManager()

        # Create test optimization profile
        from ocr.stat_extractor import get_stat_extractor
        extractor = get_stat_extractor()
        char_profile = extractor.create_character_profile("TestCharacter", "Rifleman", 50)
        opt_profile = manager.create_optimization_profile(char_profile, OptimizationType.COMBAT)

        recommendations = manager.get_optimization_recommendations(opt_profile)

        self.assertIsInstance(recommendations, list)
        self.assertGreaterEqual(len(recommendations), 0)

        for recommendation in recommendations:
            self.assertIsInstance(recommendation, str)
            self.assertGreater(len(recommendation), 0)

    def test_save_optimization_profile(self):
        """Test saving optimization profile."""
        manager = AttributeProfileManager()

        # Create test optimization profile
        from ocr.stat_extractor import get_stat_extractor
        extractor = get_stat_extractor()
        char_profile = extractor.create_character_profile("TestCharacter", "Rifleman", 50)
        opt_profile = manager.create_optimization_profile(char_profile, OptimizationType.COMBAT)

        # Save profile
        saved = manager.save_optimization_profile(opt_profile)
        self.assertTrue(saved)


class TestSWGDBStatAPI(unittest.TestCase):
    """Test class for the SWGDB Stat API functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)

        # Create test directory structure
        self.data_dir = self.project_root / "data"
        self.config_dir = self.project_root / "config"

        for directory in [self.data_dir, self.config_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        """Clean up after tests."""
        shutil.rmtree(self.temp_dir)

    def test_swgdb_stat_api_client_initialization(self):
        """Test SWGDB Stat API client initialization."""
        client = SWGDBStatAPIClient(
            api_url="https://api.swgdb.com/v1",
            api_key="test_api_key",
            user_hash="test_user_hash"
        )

        self.assertEqual(client.api_url, "https://api.swgdb.com/v1")
        self.assertEqual(client.api_key, "test_api_key")
        self.assertEqual(client.user_hash, "test_user_hash")
        self.assertIsNotNone(client.session)

    def test_prepare_stat_data(self):
        """Test preparing stat data for API upload."""
        client = SWGDBStatAPIClient(
            api_url="https://api.swgdb.com/v1",
            api_key="test_api_key",
            user_hash="test_user_hash"
        )

        # Create test character profile
        from ocr.stat_extractor import get_stat_extractor
        extractor = get_stat_extractor()
        char_profile = extractor.create_character_profile("TestCharacter", "Rifleman", 50)

        stat_data = client._prepare_stat_data(char_profile)

        self.assertIsInstance(stat_data, dict)
        self.assertIn("character_name", stat_data)
        self.assertIn("profession", stat_data)
        self.assertIn("level", stat_data)
        self.assertIn("scan_timestamp", stat_data)
        self.assertIn("scan_method", stat_data)
        self.assertIn("confidence_score", stat_data)
        self.assertIn("stats", stat_data)
        self.assertIn("resistances", stat_data)
        self.assertIn("tapes", stat_data)
        self.assertIn("upload_timestamp", stat_data)
        self.assertIn("data_version", stat_data)

    def test_prepare_optimization_data(self):
        """Test preparing optimization data for API upload."""
        client = SWGDBStatAPIClient(
            api_url="https://api.swgdb.com/v1",
            api_key="test_api_key",
            user_hash="test_user_hash"
        )

        # Create test optimization profile
        from ocr.stat_extractor import get_stat_extractor
        from core.attribute_profile import get_attribute_profile_manager
        extractor = get_stat_extractor()
        manager = get_attribute_profile_manager()
        char_profile = extractor.create_character_profile("TestCharacter", "Rifleman", 50)
        opt_profile = manager.create_optimization_profile(char_profile, OptimizationType.COMBAT)

        opt_data = client._prepare_optimization_data(opt_profile)

        self.assertIsInstance(opt_data, dict)
        self.assertIn("character_name", opt_data)
        self.assertIn("profession", opt_data)
        self.assertIn("optimization_type", opt_data)
        self.assertIn("optimization_score", opt_data)
        self.assertIn("targets", opt_data)
        self.assertIn("created_timestamp", opt_data)
        self.assertIn("last_updated", opt_data)
        self.assertIn("upload_timestamp", opt_data)
        self.assertIn("data_version", opt_data)

    def test_swgdb_stat_upload_manager(self):
        """Test SWGDB Stat Upload Manager."""
        client = SWGDBStatAPIClient(
            api_url="https://api.swgdb.com/v1",
            api_key="test_api_key",
            user_hash="test_user_hash"
        )

        upload_manager = SWGDBStatUploadManager(client)

        self.assertIsNotNone(upload_manager.api_client)
        self.assertEqual(upload_manager.rate_limit_delay, 2.0)
        self.assertEqual(upload_manager.max_batch_size, 5)
        self.assertIsInstance(upload_manager.upload_queue, list)

        # Test adding to queue
        from ocr.stat_extractor import get_stat_extractor
        extractor = get_stat_extractor()
        char_profile = extractor.create_character_profile("TestCharacter", "Rifleman", 50)

        upload_manager.add_to_queue(char_profile)
        self.assertEqual(len(upload_manager.upload_queue), 1)


class TestStatExtractorFunctions(unittest.TestCase):
    """Test class for stat extractor utility functions."""

    def test_get_stat_extractor(self):
        """Test getting stat extractor instance."""
        extractor = get_stat_extractor()

        self.assertIsInstance(extractor, StatExtractor)

    def test_extract_character_stats(self):
        """Test extracting character stats function."""
        profile = extract_character_stats("TestCharacter", "Rifleman", 50)

        self.assertIsInstance(profile, CharacterProfile)
        self.assertEqual(profile.character_name, "TestCharacter")
        self.assertEqual(profile.profession, "Rifleman")
        self.assertEqual(profile.level, 50)

    def test_save_and_load_character_stats(self):
        """Test saving and loading character stats functions."""
        # Create test profile
        profile = extract_character_stats("TestCharacter", "Rifleman", 50)

        # Save profile
        saved = save_character_stats(profile)
        self.assertTrue(saved)

        # Load profile
        loaded = load_character_stats("TestCharacter")
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.character_name, "TestCharacter")


class TestAttributeProfileFunctions(unittest.TestCase):
    """Test class for attribute profile utility functions."""

    def test_get_attribute_profile_manager(self):
        """Test getting attribute profile manager instance."""
        manager = get_attribute_profile_manager()

        self.assertIsInstance(manager, AttributeProfileManager)

    def test_create_optimization_profile(self):
        """Test creating optimization profile function."""
        # Create test character profile
        from ocr.stat_extractor import get_stat_extractor
        extractor = get_stat_extractor()
        char_profile = extractor.create_character_profile("TestCharacter", "Rifleman", 50)

        opt_profile = create_optimization_profile(char_profile, OptimizationType.COMBAT)

        self.assertIsInstance(opt_profile, OptimizationProfile)
        self.assertEqual(opt_profile.character_name, "TestCharacter")
        self.assertEqual(opt_profile.optimization_type, OptimizationType.COMBAT)

    def test_analyze_optimization(self):
        """Test analyzing optimization function."""
        # Create test optimization profile
        from ocr.stat_extractor import get_stat_extractor
        from core.attribute_profile import get_attribute_profile_manager
        extractor = get_stat_extractor()
        manager = get_attribute_profile_manager()
        char_profile = extractor.create_character_profile("TestCharacter", "Rifleman", 50)
        opt_profile = manager.create_optimization_profile(char_profile, OptimizationType.COMBAT)

        analysis = analyze_optimization(opt_profile)

        self.assertIsInstance(analysis, dict)
        self.assertIn("character_name", analysis)
        self.assertIn("profession", analysis)
        self.assertIn("optimization_type", analysis)
        self.assertIn("overall_score", analysis)

    def test_establish_character_baseline(self):
        """Test establishing character baseline function."""
        # Create test character profile
        from ocr.stat_extractor import get_stat_extractor
        extractor = get_stat_extractor()
        char_profile = extractor.create_character_profile("TestCharacter", "Rifleman", 50)

        baseline_established = establish_character_baseline("TestCharacter", char_profile)
        self.assertTrue(baseline_established)


def run_tests():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestStatExtractor,
        TestAttributeProfileManager,
        TestSWGDBStatAPI,
        TestStatExtractorFunctions,
        TestAttributeProfileFunctions
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Print summary
    print(f"\n📊 Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

    if result.failures:
        print(f"\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback}")

    if result.errors:
        print(f"\n❌ Errors:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback}")

    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1) 