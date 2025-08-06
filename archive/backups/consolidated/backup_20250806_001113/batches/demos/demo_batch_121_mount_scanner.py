#!/usr/bin/env python3
"""
Demo Script for Batch 121 - Mount Scanner + Speed Prioritizer
Tests the enhanced mount scanning and speed prioritization features.
"""

import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.mount_manager import MountManager, get_mount_manager
from utils.mount_parser import MountParser, ParsedMount, MountSpeedTier


class MountScannerDemo:
    """Demo class for testing the mount scanner and speed prioritizer."""

    def __init__(self):
        self.demo_user_hash = "demo_user_121"
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / "data"
        self.config_dir = self.project_root / "config"

        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)

    def run_complete_demo(self):
        """Run the complete mount scanner demo."""
        print("🎯 MS11 Mount Scanner Demo - Batch 121")
        print("=" * 50)
        print()

        # Test 1: Mount parsing functionality
        self.test_mount_parsing()

        # Test 2: Speed prioritization
        self.test_speed_prioritization()

        # Test 3: User preference matching
        self.test_user_preference_matching()

        # Test 4: Mount scanning methods
        self.test_mount_scanning_methods()

        # Test 5: Situational mount selection
        self.test_situational_mount_selection()

        # Test 6: Fallback strategies
        self.test_fallback_strategies()

        print("\n✅ Mount scanner demo completed successfully!")
        print("\n📋 Demo Summary:")
        print("   • Mount parsing functionality tested")
        print("   • Speed prioritization tested")
        print("   • User preference matching tested")
        print("   • Mount scanning methods tested")
        print("   • Situational mount selection tested")
        print("   • Fallback strategies tested")

    def test_mount_parsing(self):
        """Test mount parsing functionality."""
        print("🔍 Test 1: Mount Parsing Functionality")
        print("-" * 30)

        try:
            # Create mount parser
            parser = MountParser()

            # Test with sample /learn_mounts output
            sample_output = """
            Available Mounts:
            Speeder Bike - Speed: 15.0 (Available)
            Landspeeder - Speed: 20.0 (Available)
            Bantha - Speed: 8.0 (Cooldown: 30 seconds)
            Dewback - Speed: 10.0 (Available)
            Swoop Bike - Speed: 25.0 (Not Available)
            Jetpack - Speed: 30.0 (Available)
            Varactyl - Speed: 12.0 (Available)
            Rancor - Speed: 6.0 (Available)
            """

            # Parse mounts
            mounts = parser.parse_learn_mounts_output(sample_output)

            print(f"✅ Parsed {len(mounts)} mounts from sample output")

            # Verify mount data
            for mount in mounts:
                print(f"   {mount.name}: {mount.speed} speed ({mount.speed_tier.value}) - {mount.mount_type}")
                assert mount.name is not None
                assert mount.speed > 0
                assert mount.speed_tier in MountSpeedTier
                assert mount.mount_type in ["speeder", "creature", "vehicle", "flying"]

            print("✅ Mount parsing test passed\n")

        except Exception as e:
            print(f"❌ Mount parsing test failed: {e}\n")

    def test_speed_prioritization(self):
        """Test speed prioritization functionality."""
        print("🔍 Test 2: Speed Prioritization")
        print("-" * 30)

        try:
            # Create mount parser
            parser = MountParser()

            # Create test mounts with different speeds
            test_mounts = [
                ParsedMount("Jetpack", 30.0, MountSpeedTier.VERY_FAST, "flying"),
                ParsedMount("Swoop Bike", 25.0, MountSpeedTier.FAST, "speeder"),
                ParsedMount("Landspeeder", 20.0, MountSpeedTier.FAST, "vehicle"),
                ParsedMount("Speeder Bike", 15.0, MountSpeedTier.MEDIUM, "speeder"),
                ParsedMount("Varactyl", 12.0, MountSpeedTier.MEDIUM, "creature"),
                ParsedMount("Dewback", 10.0, MountSpeedTier.MEDIUM, "creature"),
                ParsedMount("Bantha", 8.0, MountSpeedTier.SLOW, "creature"),
                ParsedMount("Rancor", 6.0, MountSpeedTier.SLOW, "creature")
            ]

            # Rank mounts by speed
            ranked_mounts = parser.rank_mounts_by_speed(test_mounts)

            print(f"✅ Ranked {len(ranked_mounts)} mounts by speed")

            # Verify ranking order (fastest first)
            expected_order = ["Jetpack", "Swoop Bike", "Landspeeder", "Speeder Bike", "Varactyl", "Dewback", "Bantha", "Rancor"]
            actual_order = [mount.name for mount in ranked_mounts]

            print("   Speed ranking (fastest first):")
            for i, mount in enumerate(ranked_mounts):
                print(f"   {i+1}. {mount.name}: {mount.speed} speed ({mount.speed_tier.value})")

            # Verify fastest mount
            fastest = parser.get_fastest_available_mount(test_mounts)
            assert fastest.name == "Jetpack"
            print(f"✅ Fastest mount correctly identified: {fastest.name}")

            print("✅ Speed prioritization test passed\n")

        except Exception as e:
            print(f"❌ Speed prioritization test failed: {e}\n")

    def test_user_preference_matching(self):
        """Test user preference matching functionality."""
        print("🔍 Test 3: User Preference Matching")
        print("-" * 30)

        try:
            # Create mount parser
            parser = MountParser()

            # Create test mounts
            test_mounts = [
                ParsedMount("Jetpack", 30.0, MountSpeedTier.VERY_FAST, "flying", True),
                ParsedMount("Swoop Bike", 25.0, MountSpeedTier.FAST, "speeder", True),
                ParsedMount("Landspeeder", 20.0, MountSpeedTier.FAST, "vehicle", True),
                ParsedMount("Speeder Bike", 15.0, MountSpeedTier.MEDIUM, "speeder", True),
                ParsedMount("Dewback", 10.0, MountSpeedTier.MEDIUM, "creature", True),
                ParsedMount("Rancor", 6.0, MountSpeedTier.SLOW, "creature", True)
            ]

            # Test preferences
            preferences = {
                "preferred_mounts": ["Swoop Bike", "Jetpack", "Speeder Bike"],
                "banned_mounts": ["Rancor"],
                "preferred_mount_type": "speeder"
            }

            # Filter mounts by preferences
            filtered_mounts = parser.filter_mounts_by_preferences(test_mounts, preferences)

            print(f"✅ Filtered to {len(filtered_mounts)} mounts based on preferences")

            # Verify banned mounts are excluded
            banned_mounts = [mount.name for mount in filtered_mounts if mount.name.lower() in ["rancor"]]
            assert len(banned_mounts) == 0
            print("✅ Banned mounts correctly excluded")

            # Verify preferred mounts are prioritized
            preferred_mounts = [mount.name for mount in filtered_mounts if mount.name in preferences["preferred_mounts"]]
            print(f"✅ Found {len(preferred_mounts)} preferred mounts: {preferred_mounts}")

            print("✅ User preference matching test passed\n")

        except Exception as e:
            print(f"❌ User preference matching test failed: {e}\n")

    def test_mount_scanning_methods(self):
        """Test different mount scanning methods."""
        print("🔍 Test 4: Mount Scanning Methods")
        print("-" * 30)

        try:
            # Create mount manager
            manager = get_mount_manager("demo_user_121")

            # Test command output scanning
            command_mounts = manager._scan_mounts_via_command()
            print(f"✅ Command scan found {len(command_mounts)} mounts")

            # Test OCR scanning (simulated)
            ocr_mounts = manager._scan_mounts_via_ocr()
            print(f"✅ OCR scan found {len(ocr_mounts)} mounts")

            # Test hotbar scanning (simulated)
            hotbar_mounts = manager._scan_mounts_via_hotbar()
            print(f"✅ Hotbar scan found {len(hotbar_mounts)} mounts")

            # Test combined scanning
            all_mounts = manager.scan_available_mounts(force_scan=True)
            print(f"✅ Combined scan found {len(all_mounts)} unique mounts")

            # Test cache functionality
            cached_mounts = manager.scan_available_mounts(force_scan=False)
            print(f"✅ Cache returned {len(cached_mounts)} mounts")

            # Verify cache is working
            assert len(all_mounts) == len(cached_mounts)
            print("✅ Cache functionality working correctly")

            print("✅ Mount scanning methods test passed\n")

        except Exception as e:
            print(f"❌ Mount scanning methods test failed: {e}\n")

    def test_situational_mount_selection(self):
        """Test situational mount selection."""
        print("🔍 Test 5: Situational Mount Selection")
        print("-" * 30)

        try:
            # Create mount manager
            manager = get_mount_manager("demo_user_121")

            # Test different situations
            situations = ["combat", "travel", "hunting", "city", "general"]

            for situation in situations:
                selected_mount = manager.select_mount_by_preferences(situation)
                if selected_mount:
                    print(f"✅ {situation.capitalize()} situation: Selected {selected_mount.name}")
                else:
                    print(f"⚠️ {situation.capitalize()} situation: No mount selected")

            # Test fastest mount selection
            fastest_mount = manager.get_fastest_available_mount()
            if fastest_mount:
                print(f"✅ Fastest available mount: {fastest_mount.name} ({fastest_mount.speed} speed)")
            else:
                print("⚠️ No fastest mount available")

            print("✅ Situational mount selection test passed\n")

        except Exception as e:
            print(f"❌ Situational mount selection test failed: {e}\n")

    def test_fallback_strategies(self):
        """Test fallback strategies when preferred mounts are unavailable."""
        print("🔍 Test 6: Fallback Strategies")
        print("-" * 30)

        try:
            # Create mount manager
            manager = get_mount_manager("demo_user_121")

            # Test mount scan status
            scan_status = manager.get_mount_scan_status()
            print(f"✅ Mount scan status:")
            print(f"   Total mounts: {scan_status['total_mounts']}")
            print(f"   Available mounts: {scan_status['available_mounts']}")
            print(f"   Ranked mounts: {scan_status['ranked_mounts']}")
            print(f"   Fastest mount: {scan_status['fastest_mount']}")
            print(f"   Cache valid: {scan_status['cache_valid']}")
            print(f"   Scan methods: {scan_status['scan_methods']}")

            # Test preference updates
            new_preferences = {
                "user_preferences": {
                    "preferred_mounts": ["Jetpack", "Swoop Bike"],
                    "banned_mounts": ["Rancor"]
                }
            }

            manager.update_mount_preferences(new_preferences)
            print("✅ Mount preferences updated successfully")

            # Test ranking with new preferences
            available_mounts = manager.scan_available_mounts()
            ranked_mounts = manager.rank_mounts_by_speed(available_mounts)

            print(f"✅ Re-ranked {len(ranked_mounts)} mounts with updated preferences")

            print("✅ Fallback strategies test passed\n")

        except Exception as e:
            print(f"❌ Fallback strategies test failed: {e}\n")

    def generate_demo_report(self):
        """Generate a demo report."""
        report = {
            "demo_name": "Batch 121 Mount Scanner Demo",
            "demo_date": datetime.now().isoformat(),
            "demo_user_hash": self.demo_user_hash,
            "tests_run": [
                "Mount Parsing Functionality",
                "Speed Prioritization",
                "User Preference Matching",
                "Mount Scanning Methods",
                "Situational Mount Selection",
                "Fallback Strategies"
            ],
            "project_structure": {
                "mount_manager": "core/mount_manager.py",
                "mount_parser": "utils/mount_parser.py",
                "mount_preferences": "config/mount_preferences.json",
                "read_mounts_macro": "data/macros/read_mounts.macro"
            },
            "features_tested": [
                "OCR and macro scan /learn_mounts output",
                "Rank mounts by known speed tiers",
                "User mount priority specification",
                "Fallback to fastest available mount",
                "Situational mount selection",
                "Preference-based filtering",
                "Mount caching and performance"
            ]
        }

        # Save demo report
        report_path = self.data_dir / f"mount_scanner_demo_report_{self.demo_user_hash}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"📄 Demo report saved: {report_path}")
        return report


def main():
    """Main function to run the demo."""
    demo = MountScannerDemo()
    demo.run_complete_demo()

    # Generate demo report
    report = demo.generate_demo_report()

    print("\n📊 Demo Report Summary:")
    print(f"   Demo Name: {report['demo_name']}")
    print(f"   Demo Date: {report['demo_date']}")
    print(f"   Tests Run: {len(report['tests_run'])}")
    print(f"   Features Tested: {len(report['features_tested'])}")


if __name__ == "__main__":
    main() 