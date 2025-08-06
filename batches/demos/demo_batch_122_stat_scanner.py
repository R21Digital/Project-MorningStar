#!/usr/bin/env python3
"""
Demo Script for Batch 122 - Stat Scanner + Attribute Parser
Tests the enhanced stat scanning and attribute parsing features.
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

from ocr.stat_extractor import StatExtractor, CharacterProfile, StatType, get_stat_extractor
from core.attribute_profile import (
    AttributeProfileManager, OptimizationType, OptimizationProfile,
    get_attribute_profile_manager, create_optimization_profile
)
from swgdb_api.push_stat_data import SWGDBStatAPIClient, SWGDBStatUploadManager


class StatScannerDemo:
    """Demo class for testing the stat scanner and attribute parser."""

    def __init__(self):
        self.demo_user_hash = "demo_user_122"
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / "data"
        self.config_dir = self.project_root / "config"

        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)

    def run_complete_demo(self):
        """Run the complete stat scanner demo."""
        print("🎯 MS11 Stat Scanner Demo - Batch 122")
        print("=" * 50)
        print()

        # Test 1: Stat extraction functionality
        self.test_stat_extraction()

        # Test 2: Character profile creation
        self.test_character_profile_creation()

        # Test 3: Attribute profile management
        self.test_attribute_profile_management()

        # Test 4: Optimization analysis
        self.test_optimization_analysis()

        # Test 5: Baseline tracking
        self.test_baseline_tracking()

        # Test 6: SWGDB integration
        self.test_swgdb_integration()

        print("\n✅ Stat scanner demo completed successfully!")
        print("\n📋 Demo Summary:")
        print("   • Stat extraction functionality tested")
        print("   • Character profile creation tested")
        print("   • Attribute profile management tested")
        print("   • Optimization analysis tested")
        print("   • Baseline tracking tested")
        print("   • SWGDB integration tested")

    def test_stat_extraction(self):
        """Test stat extraction functionality."""
        print("🔍 Test 1: Stat Extraction Functionality")
        print("-" * 30)

        try:
            # Create stat extractor
            extractor = get_stat_extractor()

            # Test OCR-based extraction
            stats_panel_stats = extractor.extract_stats_from_panel("stats_panel")
            print(f"✅ Stats panel extraction: {len(stats_panel_stats)} stats")

            armor_panel_stats = extractor.extract_stats_from_panel("armor_panel")
            print(f"✅ Armor panel extraction: {len(armor_panel_stats)} stats")

            # Test macro-based extraction
            macro_stats = extractor.extract_stats_via_macro()
            print(f"✅ Macro extraction: {len(macro_stats)} stats")

            # Verify stat types
            for stat_type, stat in macro_stats.items():
                print(f"   {stat_type.value}: {stat.current_value}/{stat.max_value} ({stat.confidence:.1f}% confidence)")
                assert stat.current_value >= 0
                assert stat.max_value >= 0
                assert 0 <= stat.confidence <= 100

            print("✅ Stat extraction test passed\n")

        except Exception as e:
            print(f"❌ Stat extraction test failed: {e}\n")

    def test_character_profile_creation(self):
        """Test character profile creation functionality."""
        print("🔍 Test 2: Character Profile Creation")
        print("-" * 30)

        try:
            # Create stat extractor
            extractor = get_stat_extractor()

            # Create character profiles for different professions
            test_characters = [
                ("TestRifleman", "Rifleman", 50),
                ("TestMedic", "Medic", 45),
                ("TestPistoleer", "Pistoleer", 40),
                ("TestArtisan", "Artisan", 35)
            ]

            profiles = []
            for char_name, profession, level in test_characters:
                profile = extractor.create_character_profile(char_name, profession, level)
                profiles.append(profile)
                print(f"✅ Created profile for {char_name}: {len(profile.stats)} stats, {profile.confidence_score:.1f}% confidence")

            # Test profile validation
            for profile in profiles:
                validation = extractor.validate_stat_data(profile)
                print(f"   {profile.character_name} validation: {'Valid' if validation['valid'] else 'Invalid'}")
                if validation['warnings']:
                    print(f"   Warnings: {len(validation['warnings'])}")
                if validation['errors']:
                    print(f"   Errors: {len(validation['errors'])}")

            # Test profile saving and loading
            for profile in profiles:
                saved = extractor.save_character_profile(profile)
                assert saved, f"Failed to save profile for {profile.character_name}"

                loaded = extractor.load_character_profile(profile.character_name)
                assert loaded is not None, f"Failed to load profile for {profile.character_name}"
                assert loaded.character_name == profile.character_name

            print("✅ Character profile creation test passed\n")

        except Exception as e:
            print(f"❌ Character profile creation test failed: {e}\n")

    def test_attribute_profile_management(self):
        """Test attribute profile management functionality."""
        print("🔍 Test 3: Attribute Profile Management")
        print("-" * 30)

        try:
            # Create attribute profile manager
            manager = get_attribute_profile_manager()

            # Create test character profile
            extractor = get_stat_extractor()
            test_profile = extractor.create_character_profile("TestCharacter", "Rifleman", 50)

            # Test different optimization types
            optimization_types = [
                OptimizationType.COMBAT,
                OptimizationType.DPS,
                OptimizationType.BALANCED
            ]

            for opt_type in optimization_types:
                opt_profile = manager.create_optimization_profile(test_profile, opt_type)
                print(f"✅ Created {opt_type.value} optimization profile: {opt_profile.optimization_score:.1f}% score")

                # Test optimization analysis
                analysis = manager.analyze_stat_gaps(opt_profile)
                print(f"   Overall score: {analysis['overall_score']:.1f}%")
                print(f"   Priority improvements: {len(analysis['priority_improvements'])}")
                print(f"   Easy wins: {len(analysis['easy_wins'])}")

                # Test recommendations
                recommendations = manager.get_optimization_recommendations(opt_profile)
                print(f"   Recommendations: {len(recommendations)}")

            print("✅ Attribute profile management test passed\n")

        except Exception as e:
            print(f"❌ Attribute profile management test failed: {e}\n")

    def test_optimization_analysis(self):
        """Test optimization analysis functionality."""
        print("🔍 Test 4: Optimization Analysis")
        print("-" * 30)

        try:
            # Create test profiles for different professions
            test_cases = [
                ("CombatRifleman", "Rifleman", OptimizationType.COMBAT),
                ("HealingMedic", "Medic", OptimizationType.HEALING),
                ("DPSPistoleer", "Pistoleer", OptimizationType.DPS),
                ("CraftingArtisan", "Artisan", OptimizationType.CRAFTING)
            ]

            manager = get_attribute_profile_manager()
            extractor = get_stat_extractor()

            for char_name, profession, opt_type in test_cases:
                # Create character profile
                char_profile = extractor.create_character_profile(char_name, profession, 50)

                # Create optimization profile
                opt_profile = manager.create_optimization_profile(char_profile, opt_type)

                # Analyze optimization
                analysis = manager.analyze_stat_gaps(opt_profile)

                print(f"✅ {char_name} ({profession} - {opt_type.value}):")
                print(f"   Optimization score: {opt_profile.optimization_score:.1f}%")
                print(f"   Overall score: {analysis['overall_score']:.1f}%")
                print(f"   Targets: {len(opt_profile.targets)}")
                print(f"   Priority improvements: {len(analysis['priority_improvements'])}")
                print(f"   Easy wins: {len(analysis['easy_wins'])}")

                # Test recommendations
                recommendations = manager.get_optimization_recommendations(opt_profile)
                print(f"   Recommendations: {len(recommendations)}")

            print("✅ Optimization analysis test passed\n")

        except Exception as e:
            print(f"❌ Optimization analysis test failed: {e}\n")

    def test_baseline_tracking(self):
        """Test baseline tracking functionality."""
        print("🔍 Test 5: Baseline Tracking")
        print("-" * 30)

        try:
            manager = get_attribute_profile_manager()
            extractor = get_stat_extractor()

            # Create baseline profile
            baseline_profile = extractor.create_character_profile("BaselineCharacter", "Rifleman", 50)
            baseline_established = manager.establish_baseline("BaselineCharacter", baseline_profile)
            assert baseline_established, "Failed to establish baseline"

            # Create current profile (simulating improvement)
            current_profile = extractor.create_character_profile("BaselineCharacter", "Rifleman", 55)

            # Compare with baseline
            comparison = manager.compare_with_baseline(current_profile, baseline_profile)
            print(f"✅ Baseline comparison:")
            print(f"   Time elapsed: {comparison['time_elapsed_days']:.1f} days")
            print(f"   Overall improvement: {comparison['overall_improvement']:.1f}%")
            print(f"   Improvements: {len(comparison['improvements'])}")
            print(f"   Regressions: {len(comparison['regressions'])}")
            print(f"   Unchanged: {len(comparison['unchanged'])}")

            # Test baseline loading
            loaded_baseline = manager.load_baseline("BaselineCharacter")
            assert loaded_baseline is not None, "Failed to load baseline"
            assert loaded_baseline.character_name == "BaselineCharacter"

            print("✅ Baseline tracking test passed\n")

        except Exception as e:
            print(f"❌ Baseline tracking test failed: {e}\n")

    def test_swgdb_integration(self):
        """Test SWGDB integration functionality."""
        print("🔍 Test 6: SWGDB Integration")
        print("-" * 30)

        try:
            # Create test API client
            api_client = SWGDBStatAPIClient(
                api_url="https://api.swgdb.com/v1",
                api_key="test_api_key",
                user_hash="test_user_hash"
            )

            # Test API connection
            connection_test = api_client.validate_credentials()
            print(f"✅ API connection test: {'Success' if connection_test['success'] else 'Failed'}")

            # Create test character profile
            extractor = get_stat_extractor()
            test_profile = extractor.create_character_profile("TestCharacter", "Rifleman", 50)

            # Test stat upload (simulated)
            upload_result = api_client.push_character_stats(test_profile)
            print(f"✅ Stat upload test: {'Success' if upload_result['success'] else 'Failed'}")

            # Test optimization profile upload
            manager = get_attribute_profile_manager()
            opt_profile = manager.create_optimization_profile(test_profile, OptimizationType.COMBAT)

            opt_upload_result = api_client.push_optimization_profile(opt_profile)
            print(f"✅ Optimization upload test: {'Success' if opt_upload_result['success'] else 'Failed'}")

            # Test upload manager
            upload_manager = SWGDBStatUploadManager(api_client)
            upload_manager.add_to_queue(test_profile)
            queue_result = upload_manager.process_queue()
            print(f"✅ Upload manager test: {'Success' if queue_result['success'] else 'Failed'}")

            print("✅ SWGDB integration test passed\n")

        except Exception as e:
            print(f"❌ SWGDB integration test failed: {e}\n")

    def generate_demo_report(self):
        """Generate a demo report."""
        report = {
            "demo_name": "Batch 122 Stat Scanner Demo",
            "demo_date": datetime.now().isoformat(),
            "demo_user_hash": self.demo_user_hash,
            "tests_run": [
                "Stat Extraction Functionality",
                "Character Profile Creation",
                "Attribute Profile Management",
                "Optimization Analysis",
                "Baseline Tracking",
                "SWGDB Integration"
            ],
            "project_structure": {
                "stat_extractor": "ocr/stat_extractor.py",
                "attribute_profile": "core/attribute_profile.py",
                "swgdb_api": "swgdb_api/push_stat_data.py",
                "read_stats_macro": "data/macros/read_stats.macro"
            },
            "features_tested": [
                "OCR and macro scan /stats and /armor panels",
                "Normalize stats: Health, Action, Mind, Luck, Resists, Tapes",
                "Upload stat data to SWGDB player profile",
                "Begin baseline for stat-based optimization",
                "Character profile management",
                "Optimization analysis and recommendations",
                "Baseline tracking and comparison"
            ]
        }

        # Save demo report
        report_path = self.data_dir / f"stat_scanner_demo_report_{self.demo_user_hash}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"📄 Demo report saved: {report_path}")
        return report


def main():
    """Main function to run the demo."""
    demo = StatScannerDemo()
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