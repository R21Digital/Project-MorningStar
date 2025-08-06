#!/usr/bin/env python3
"""
Test Script for Batch 121 - Mount Scanner + Speed Prioritizer
Comprehensive testing of the enhanced mount scanning and speed prioritization features.
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

from core.mount_manager import (
    MountManager,
    MountType,
    MountStatus,
    ZoneType,
    Mount,
    MountState,
    MountPreferences,
    get_mount_manager
)
from utils.mount_parser import (
    MountParser,
    ParsedMount,
    MountSpeedTier,
    get_mount_parser,
    parse_learn_mounts_output,
    scan_mount_interface,
    get_fastest_mount
)


class TestMountParser(unittest.TestCase):
    """Test class for the mount parser functionality."""

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

    def test_mount_parser_initialization(self):
        """Test mount parser initialization."""
        parser = MountParser()

        self.assertIsNotNone(parser.speed_tiers)
        self.assertIsNotNone(parser.mount_patterns)
        self.assertIsNotNone(parser.speed_patterns)
        self.assertIsNotNone(parser.mount_name_patterns)

        # Check speed tiers
        self.assertIn(MountSpeedTier.SLOW, parser.speed_tiers)
        self.assertIn(MountSpeedTier.MEDIUM, parser.speed_tiers)
        self.assertIn(MountSpeedTier.FAST, parser.speed_tiers)
        self.assertIn(MountSpeedTier.VERY_FAST, parser.speed_tiers)

    def test_parse_learn_mounts_output(self):
        """Test parsing /learn_mounts command output."""
        parser = MountParser()

        sample_output = """
        Available Mounts:
        Speeder Bike - Speed: 15.0 (Available)
        Landspeeder - Speed: 20.0 (Available)
        Bantha - Speed: 8.0 (Cooldown: 30 seconds)
        Dewback - Speed: 10.0 (Available)
        Swoop Bike - Speed: 25.0 (Not Available)
        Jetpack - Speed: 30.0 (Available)
        """

        mounts = parser.parse_learn_mounts_output(sample_output)

        self.assertEqual(len(mounts), 6)

        # Check specific mounts
        mount_names = [mount.name for mount in mounts]
        self.assertIn("Speeder Bike", mount_names)
        self.assertIn("Landspeeder", mount_names)
        self.assertIn("Bantha", mount_names)
        self.assertIn("Dewback", mount_names)
        self.assertIn("Swoop Bike", mount_names)
        self.assertIn("Jetpack", mount_names)

        # Check speed values
        for mount in mounts:
            self.assertGreater(mount.speed, 0)
            self.assertIsInstance(mount.speed_tier, MountSpeedTier)
            self.assertIsInstance(mount.mount_type, str)

    def test_extract_mount_name(self):
        """Test mount name extraction."""
        parser = MountParser()

        test_cases = [
            ("Speeder Bike - Speed: 15.0", "Speeder Bike"),
            ("Landspeeder Mount Available", "Landspeeder"),
            ("Bantha Vehicle Ready", "Bantha"),
            ("Jetpack Speed 30.0", "Jetpack"),
            ("Dewback Available", "Dewback")
        ]

        for line, expected_name in test_cases:
            extracted_name = parser._extract_mount_name(line)
            self.assertEqual(extracted_name, expected_name)

    def test_extract_speed(self):
        """Test speed extraction."""
        parser = MountParser()

        test_cases = [
            ("Speed: 15.0", 15.0),
            ("20.0 speed", 20.0),
            ("velocity: 25.5", 25.5),
            ("30.0 velocity", 30.0),
            ("No speed info", None)
        ]

        for line, expected_speed in test_cases:
            extracted_speed = parser._extract_speed(line)
            if expected_speed is None:
                self.assertIsNone(extracted_speed)
            else:
                self.assertEqual(extracted_speed, expected_speed)

    def test_classify_speed_tier(self):
        """Test speed tier classification."""
        parser = MountParser()

        test_cases = [
            (5.0, MountSpeedTier.SLOW),
            (8.0, MountSpeedTier.SLOW),
            (9.0, MountSpeedTier.MEDIUM),
            (15.0, MountSpeedTier.MEDIUM),
            (16.0, MountSpeedTier.FAST),
            (25.0, MountSpeedTier.FAST),
            (26.0, MountSpeedTier.VERY_FAST),
            (50.0, MountSpeedTier.VERY_FAST)
        ]

        for speed, expected_tier in test_cases:
            classified_tier = parser._classify_speed_tier(speed)
            self.assertEqual(classified_tier, expected_tier)

    def test_classify_mount_type(self):
        """Test mount type classification."""
        parser = MountParser()

        test_cases = [
            ("Speeder Bike", "speeder"),
            ("Landspeeder", "vehicle"),
            ("Swoop Bike", "speeder"),
            ("Jetpack", "flying"),
            ("Bantha", "creature"),
            ("Dewback", "creature"),
            ("Varactyl", "creature"),
            ("Unknown Mount", "vehicle")  # Default fallback
        ]

        for mount_name, expected_type in test_cases:
            classified_type = parser._classify_mount_type(mount_name)
            self.assertEqual(classified_type, expected_type)

    def test_check_availability(self):
        """Test mount availability checking."""
        parser = MountParser()

        available_lines = [
            "Speeder Bike - Available",
            "Landspeeder Ready",
            "Jetpack Active",
            "Dewback Summoned"
        ]

        unavailable_lines = [
            "Bantha - Unavailable",
            "Swoop Bike Not Available",
            "Jetpack Cooldown",
            "Landspeeder Disabled",
            "Dewback In Use"
        ]

        for line in available_lines:
            self.assertTrue(parser._check_availability(line))

        for line in unavailable_lines:
            self.assertFalse(parser._check_availability(line))

    def test_rank_mounts_by_speed(self):
        """Test mount ranking by speed."""
        parser = MountParser()

        test_mounts = [
            ParsedMount("Slow Mount", 8.0, MountSpeedTier.SLOW, "creature"),
            ParsedMount("Fast Mount", 25.0, MountSpeedTier.FAST, "speeder"),
            ParsedMount("Medium Mount", 12.0, MountSpeedTier.MEDIUM, "vehicle"),
            ParsedMount("Very Fast Mount", 30.0, MountSpeedTier.VERY_FAST, "flying")
        ]

        ranked_mounts = parser.rank_mounts_by_speed(test_mounts)

        # Should be ranked by speed tier and speed value
        expected_order = ["Very Fast Mount", "Fast Mount", "Medium Mount", "Slow Mount"]
        actual_order = [mount.name for mount in ranked_mounts]

        self.assertEqual(actual_order, expected_order)

    def test_filter_mounts_by_preferences(self):
        """Test mount filtering by preferences."""
        parser = MountParser()

        test_mounts = [
            ParsedMount("Jetpack", 30.0, MountSpeedTier.VERY_FAST, "flying", True),
            ParsedMount("Swoop Bike", 25.0, MountSpeedTier.FAST, "speeder", True),
            ParsedMount("Landspeeder", 20.0, MountSpeedTier.FAST, "vehicle", True),
            ParsedMount("Speeder Bike", 15.0, MountSpeedTier.MEDIUM, "speeder", True),
            ParsedMount("Dewback", 10.0, MountSpeedTier.MEDIUM, "creature", True),
            ParsedMount("Rancor", 6.0, MountSpeedTier.SLOW, "creature", False)  # Unavailable
        ]

        preferences = {
            "preferred_mounts": ["Swoop Bike", "Jetpack"],
            "banned_mounts": ["Rancor"],
            "preferred_mount_type": "speeder"
        }

        filtered_mounts = parser.filter_mounts_by_preferences(test_mounts, preferences)

        # Should exclude banned and unavailable mounts
        self.assertEqual(len(filtered_mounts), 4)

        mount_names = [mount.name for mount in filtered_mounts]
        self.assertIn("Jetpack", mount_names)
        self.assertIn("Swoop Bike", mount_names)
        self.assertIn("Landspeeder", mount_names)
        self.assertIn("Speeder Bike", mount_names)
        self.assertNotIn("Rancor", mount_names)

    def test_get_fastest_available_mount(self):
        """Test getting fastest available mount."""
        parser = MountParser()

        test_mounts = [
            ParsedMount("Jetpack", 30.0, MountSpeedTier.VERY_FAST, "flying", True),
            ParsedMount("Swoop Bike", 25.0, MountSpeedTier.FAST, "speeder", True),
            ParsedMount("Landspeeder", 20.0, MountSpeedTier.FAST, "vehicle", False),  # Unavailable
            ParsedMount("Speeder Bike", 15.0, MountSpeedTier.MEDIUM, "speeder", True),
            ParsedMount("Dewback", 10.0, MountSpeedTier.MEDIUM, "creature", True)
        ]

        fastest = parser.get_fastest_available_mount(test_mounts)

        self.assertIsNotNone(fastest)
        self.assertEqual(fastest.name, "Jetpack")
        self.assertEqual(fastest.speed, 30.0)

    def test_save_and_load_mount_data(self):
        """Test saving and loading mount data."""
        parser = MountParser()

        test_mounts = [
            ParsedMount("Jetpack", 30.0, MountSpeedTier.VERY_FAST, "flying", True),
            ParsedMount("Swoop Bike", 25.0, MountSpeedTier.FAST, "speeder", True)
        ]

        file_path = str(self.data_dir / "test_mounts.json")

        # Save mount data
        parser.save_mount_data(test_mounts, file_path)

        # Load mount data
        loaded_mounts = parser.load_mount_data(file_path)

        self.assertEqual(len(loaded_mounts), 2)

        for original, loaded in zip(test_mounts, loaded_mounts):
            self.assertEqual(original.name, loaded.name)
            self.assertEqual(original.speed, loaded.speed)
            self.assertEqual(original.speed_tier, loaded.speed_tier)
            self.assertEqual(original.mount_type, loaded.mount_type)
            self.assertEqual(original.is_available, loaded.is_available)


class TestMountManager(unittest.TestCase):
    """Test class for the enhanced mount manager functionality."""

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

    @patch('core.mount_manager.Path')
    def test_mount_manager_initialization(self, mock_path):
        """Test mount manager initialization."""
        mock_path.return_value.parent.parent = self.project_root

        manager = MountManager("test_profile")

        self.assertEqual(manager.profile_name, "test_profile")
        self.assertIsNotNone(manager.mount_parser)
        self.assertIsNotNone(manager.enhanced_preferences)
        self.assertIsNotNone(manager.mount_cache)
        self.assertEqual(manager.last_scan_time, 0.0)

    def test_scan_available_mounts(self):
        """Test scanning available mounts."""
        manager = MountManager("test_profile")

        # Test with force scan
        mounts = manager.scan_available_mounts(force_scan=True)

        self.assertIsInstance(mounts, list)
        self.assertGreater(len(mounts), 0)

        # Test cache functionality
        cached_mounts = manager.scan_available_mounts(force_scan=False)
        self.assertEqual(len(mounts), len(cached_mounts))

    def test_scan_mounts_via_command(self):
        """Test command-based mount scanning."""
        manager = MountManager("test_profile")

        mounts = manager._scan_mounts_via_command()

        self.assertIsInstance(mounts, list)
        self.assertGreater(len(mounts), 0)

        for mount in mounts:
            self.assertIsInstance(mount, ParsedMount)
            self.assertIsNotNone(mount.name)
            self.assertGreater(mount.speed, 0)

    @patch('core.mount_manager.MountParser.scan_mount_interface')
    def test_scan_mounts_via_ocr(self, mock_scan):
        """Test OCR-based mount scanning."""
        # Mock OCR scan results
        mock_mounts = [
            ParsedMount("Jetpack", 30.0, MountSpeedTier.VERY_FAST, "flying"),
            ParsedMount("Swoop Bike", 25.0, MountSpeedTier.FAST, "speeder")
        ]
        mock_scan.return_value = mock_mounts

        manager = MountManager("test_profile")

        mounts = manager._scan_mounts_via_ocr()

        self.assertEqual(len(mounts), 2)
        self.assertEqual(mounts[0].name, "Jetpack")
        self.assertEqual(mounts[1].name, "Swoop Bike")

    def test_deduplicate_mounts(self):
        """Test mount deduplication."""
        manager = MountManager("test_profile")

        test_mounts = [
            ParsedMount("Jetpack", 30.0, MountSpeedTier.VERY_FAST, "flying"),
            ParsedMount("Jetpack", 30.0, MountSpeedTier.VERY_FAST, "flying"),  # Duplicate
            ParsedMount("Swoop Bike", 25.0, MountSpeedTier.FAST, "speeder"),
            ParsedMount("Swoop Bike", 25.0, MountSpeedTier.FAST, "speeder"),  # Duplicate
            ParsedMount("Landspeeder", 20.0, MountSpeedTier.FAST, "vehicle")
        ]

        unique_mounts = manager._deduplicate_mounts(test_mounts)

        self.assertEqual(len(unique_mounts), 3)

        mount_names = [mount.name for mount in unique_mounts]
        self.assertIn("Jetpack", mount_names)
        self.assertIn("Swoop Bike", mount_names)
        self.assertIn("Landspeeder", mount_names)

    def test_cache_functionality(self):
        """Test mount cache functionality."""
        manager = MountManager("test_profile")

        # Initially cache should be invalid
        self.assertFalse(manager._is_cache_valid())

        # Scan mounts to populate cache
        mounts = manager.scan_available_mounts(force_scan=True)
        self.assertGreater(len(mounts), 0)

        # Cache should now be valid
        self.assertTrue(manager._is_cache_valid())

        # Update cache
        test_mounts = [
            ParsedMount("Test Mount", 15.0, MountSpeedTier.MEDIUM, "speeder")
        ]
        manager._update_mount_cache(test_mounts)

        self.assertEqual(len(manager.mount_cache), 1)
        self.assertIn("Test Mount", manager.mount_cache)

    def test_rank_mounts_by_speed(self):
        """Test ranking mounts by speed."""
        manager = MountManager("test_profile")

        test_mounts = [
            ParsedMount("Slow Mount", 8.0, MountSpeedTier.SLOW, "creature"),
            ParsedMount("Fast Mount", 25.0, MountSpeedTier.FAST, "speeder"),
            ParsedMount("Medium Mount", 12.0, MountSpeedTier.MEDIUM, "vehicle"),
            ParsedMount("Very Fast Mount", 30.0, MountSpeedTier.VERY_FAST, "flying")
        ]

        ranked_mounts = manager.rank_mounts_by_speed(test_mounts)

        # Should be ranked by speed tier and speed value
        expected_order = ["Very Fast Mount", "Fast Mount", "Medium Mount", "Slow Mount"]
        actual_order = [mount.name for mount in ranked_mounts]

        self.assertEqual(actual_order, expected_order)

    def test_select_mount_by_preferences(self):
        """Test selecting mount by preferences."""
        manager = MountManager("test_profile")

        # Test different situations
        situations = ["combat", "travel", "hunting", "city", "general"]

        for situation in situations:
            selected_mount = manager.select_mount_by_preferences(situation)
            # Should return a mount or None, but not raise an exception
            if selected_mount is not None:
                self.assertIsInstance(selected_mount, ParsedMount)
                self.assertIsNotNone(selected_mount.name)

    def test_get_fastest_available_mount(self):
        """Test getting fastest available mount."""
        manager = MountManager("test_profile")

        fastest_mount = manager.get_fastest_available_mount()

        # Should return a mount or None, but not raise an exception
        if fastest_mount is not None:
            self.assertIsInstance(fastest_mount, ParsedMount)
            self.assertIsNotNone(fastest_mount.name)
            self.assertGreater(fastest_mount.speed, 0)

    def test_update_mount_preferences(self):
        """Test updating mount preferences."""
        manager = MountManager("test_profile")

        new_preferences = {
            "user_preferences": {
                "preferred_mounts": ["Jetpack", "Swoop Bike"],
                "banned_mounts": ["Rancor"]
            }
        }

        # Should not raise an exception
        manager.update_mount_preferences(new_preferences)

    def test_get_mount_scan_status(self):
        """Test getting mount scan status."""
        manager = MountManager("test_profile")

        status = manager.get_mount_scan_status()

        self.assertIsInstance(status, dict)
        self.assertIn("total_mounts", status)
        self.assertIn("available_mounts", status)
        self.assertIn("ranked_mounts", status)
        self.assertIn("fastest_mount", status)
        self.assertIn("cache_valid", status)
        self.assertIn("last_scan_time", status)
        self.assertIn("scan_methods", status)


class TestMountParserFunctions(unittest.TestCase):
    """Test class for mount parser utility functions."""

    def test_get_mount_parser(self):
        """Test getting mount parser instance."""
        parser = get_mount_parser()

        self.assertIsInstance(parser, MountParser)

    def test_parse_learn_mounts_output(self):
        """Test parsing learn mounts output function."""
        sample_output = """
        Available Mounts:
        Speeder Bike - Speed: 15.0 (Available)
        Landspeeder - Speed: 20.0 (Available)
        """

        mounts = parse_learn_mounts_output(sample_output)

        self.assertIsInstance(mounts, list)
        self.assertEqual(len(mounts), 2)

        for mount in mounts:
            self.assertIsInstance(mount, ParsedMount)

    @patch('utils.mount_parser.MountParser.scan_mount_interface')
    def test_scan_mount_interface(self, mock_scan):
        """Test scanning mount interface function."""
        # Mock scan results
        mock_mounts = [
            ParsedMount("Jetpack", 30.0, MountSpeedTier.VERY_FAST, "flying"),
            ParsedMount("Swoop Bike", 25.0, MountSpeedTier.FAST, "speeder")
        ]
        mock_scan.return_value = mock_mounts

        mounts = scan_mount_interface()

        self.assertEqual(len(mounts), 2)
        self.assertEqual(mounts[0].name, "Jetpack")
        self.assertEqual(mounts[1].name, "Swoop Bike")

    def test_get_fastest_mount(self):
        """Test getting fastest mount function."""
        test_mounts = [
            ParsedMount("Slow Mount", 8.0, MountSpeedTier.SLOW, "creature", True),
            ParsedMount("Fast Mount", 25.0, MountSpeedTier.FAST, "speeder", True),
            ParsedMount("Very Fast Mount", 30.0, MountSpeedTier.VERY_FAST, "flying", True)
        ]

        fastest = get_fastest_mount(test_mounts)

        self.assertIsNotNone(fastest)
        self.assertEqual(fastest.name, "Very Fast Mount")
        self.assertEqual(fastest.speed, 30.0)


def run_tests():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()

    # Add test classes
    test_classes = [
        TestMountParser,
        TestMountManager,
        TestMountParserFunctions
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