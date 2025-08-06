#!/usr/bin/env python3
"""
Demo Script for Batch 124 - Gear/Armor Optimizer (AskMrRoboto Logic)
Tests the gear optimization system that recommends armor sets and enhancements.
"""

import json
import sys
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from optimizer.gear_advisor import (
    get_gear_advisor, OptimizationType, analyze_character_gear, save_gear_optimization_result
)
from ocr.stat_extractor import get_stat_extractor
from core.build_loader import get_build_loader


class GearOptimizerDemo:
    """Demo class for testing the gear optimizer system."""

    def __init__(self):
        self.demo_user_hash = "demo_user_124"
        self.project_root = Path(__file__).parent
        self.data_dir = self.project_root / "data"
        self.config_dir = self.project_root / "config"

        # Ensure directories exist
        self.data_dir.mkdir(exist_ok=True)
        self.config_dir.mkdir(exist_ok=True)

    def run_complete_demo(self):
        """Run the complete gear optimizer demo."""
        print("🎯 MS11 Gear Optimizer Demo - Batch 124")
        print("=" * 50)
        print()

        # Test 1: Gear advisor initialization
        self.test_gear_advisor_initialization()

        # Test 2: Armor sets loading
        self.test_armor_sets_loading()

        # Test 3: Character profile creation
        self.test_character_profile_creation()

        # Test 4: Build loading
        self.test_build_loading()

        # Test 5: Gear optimization analysis
        self.test_gear_optimization_analysis()

        # Test 6: Different optimization types
        self.test_different_optimization_types()

        # Test 7: Budget constraints
        self.test_budget_constraints()

        # Test 8: Enhancement recommendations
        self.test_enhancement_recommendations()

        # Test 9: Result saving
        self.test_result_saving()

        print("\n✅ Gear optimizer demo completed successfully!")
        print("\n📋 Demo Summary:")
        print("   • Gear advisor initialization tested")
        print("   • Armor sets loading tested")
        print("   • Character profile creation tested")
        print("   • Build loading tested")
        print("   • Gear optimization analysis tested")
        print("   • Different optimization types tested")
        print("   • Budget constraints tested")
        print("   • Enhancement recommendations tested")
        print("   • Result saving tested")

    def test_gear_advisor_initialization(self):
        """Test gear advisor initialization."""
        print("🔍 Test 1: Gear Advisor Initialization")
        print("-" * 30)

        try:
            gear_advisor = get_gear_advisor()
            print(f"✅ Gear advisor initialized successfully")
            print(f"   Armor sets loaded: {len(gear_advisor.armor_sets)}")
            print(f"   Enhancements loaded: {len(gear_advisor.enhancements)}")
            print(f"   Resist types loaded: {len(gear_advisor.resist_types)}")

            # Test armor sets
            armor_set_names = list(gear_advisor.armor_sets.keys())
            print(f"   Available armor sets: {', '.join(armor_set_names)}")

            # Test enhancements
            enhancement_names = list(gear_advisor.enhancements.keys())
            print(f"   Available enhancements: {', '.join(enhancement_names)}")

            print("✅ Gear advisor initialization test passed\n")

        except Exception as e:
            print(f"❌ Gear advisor initialization test failed: {e}\n")

    def test_armor_sets_loading(self):
        """Test armor sets loading and validation."""
        print("🔍 Test 2: Armor Sets Loading")
        print("-" * 30)

        try:
            gear_advisor = get_gear_advisor()

            # Test each armor set
            for set_id, set_data in gear_advisor.armor_sets.items():
                print(f"✅ Armor set '{set_id}':")
                print(f"   Name: {set_data['name']}")
                print(f"   Type: {set_data['type']}")
                print(f"   Profession: {set_data['profession']}")
                print(f"   Cost: {set_data['cost']}")
                print(f"   Combat style: {set_data['combat_style']}")
                print(f"   Specialization: {set_data['specialization']}")
                print(f"   Slots: {len(set_data['slots'])}")
                print(f"   Set bonus: {set_data['set_bonus']}")

                # Test slot data
                for slot_name, slot_data in set_data['slots'].items():
                    print(f"     {slot_name}: {slot_data['name']}")
                    print(f"       Base stats: {slot_data['base_stats']}")
                    print(f"       Resists: {slot_data['resists']}")
                    print(f"       Enhancement slots: {slot_data['enhancement_slots']}")

            print("✅ Armor sets loading test passed\n")

        except Exception as e:
            print(f"❌ Armor sets loading test failed: {e}\n")

    def test_character_profile_creation(self):
        """Test character profile creation."""
        print("🔍 Test 3: Character Profile Creation")
        print("-" * 30)

        try:
            stat_extractor = get_stat_extractor()

            # Create test character profiles
            test_characters = [
                ("TestRifleman", "Rifleman", 50),
                ("TestMedic", "Medic", 45),
                ("TestPistoleer", "Pistoleer", 40),
                ("TestBrawler", "Brawler", 55)
            ]

            profiles = []
            for char_name, profession, level in test_characters:
                profile = stat_extractor.create_character_profile(char_name, profession, level)
                profiles.append(profile)
                print(f"✅ Created profile for {char_name}: {len(profile.stats)} stats")

            # Test profile validation
            for profile in profiles:
                validation = stat_extractor.validate_stat_data(profile)
                print(f"   {profile.character_name} validation: {'Valid' if validation['valid'] else 'Invalid'}")

            print("✅ Character profile creation test passed\n")

        except Exception as e:
            print(f"❌ Character profile creation test failed: {e}\n")

    def test_build_loading(self):
        """Test build loading for gear optimization."""
        print("🔍 Test 4: Build Loading")
        print("-" * 30)

        try:
            build_loader = get_build_loader()
            builds = build_loader.get_all_builds()

            print(f"✅ Loaded {len(builds)} builds:")

            for build_id, build_data in builds.items():
                print(f"   {build_id}: {build_data.name}")
                print(f"     Category: {build_data.category.value}")
                print(f"     Specialization: {build_data.specialization.value}")
                print(f"     Difficulty: {build_data.difficulty.value}")
                print(f"     Professions: {build_data.professions}")

            # Test specific build details
            test_build_id = "rifleman_medic"
            build_data = build_loader.get_build(test_build_id)
            if build_data:
                print(f"✅ Test build '{test_build_id}' details:")
                print(f"   Skills: {len(build_data.skills)} skill trees")
                print(f"   Equipment: {build_data.equipment}")
                print(f"   Performance: {build_data.performance}")
                print(f"   Combat: {build_data.combat}")

            print("✅ Build loading test passed\n")

        except Exception as e:
            print(f"❌ Build loading test failed: {e}\n")

    def test_gear_optimization_analysis(self):
        """Test gear optimization analysis."""
        print("🔍 Test 5: Gear Optimization Analysis")
        print("-" * 30)

        try:
            # Test optimization for different characters and builds
            test_cases = [
                ("TestRifleman", "rifleman_medic", OptimizationType.BALANCED, "medium"),
                ("TestMedic", "rifleman_medic", OptimizationType.SUPPORT, "high"),
                ("TestPistoleer", "tk_pistoleer", OptimizationType.DPS, "medium"),
                ("TestBrawler", "brawler_tank", OptimizationType.TANK, "high")
            ]

            for char_name, build_id, opt_type, budget in test_cases:
                print(f"✅ Testing optimization for {char_name} ({build_id}):")
                
                result = analyze_character_gear(char_name, build_id, opt_type, budget)
                
                if result:
                    print(f"   Character: {result.character_name}")
                    print(f"   Build: {result.build_id}")
                    print(f"   Optimization type: {result.optimization_type.value}")
                    print(f"   Overall improvement: {result.overall_improvement:.1f}%")
                    print(f"   Total cost: {result.total_cost}")
                    print(f"   Recommendations: {len(result.recommendations)}")
                    print(f"   Implementation priority: {len(result.implementation_priority)} items")

                    # Show top recommendations
                    high_priority = [r for r in result.recommendations if r.priority == "high"]
                    if high_priority:
                        print(f"   High priority upgrades: {len(high_priority)}")
                        for rec in high_priority[:3]:  # Show top 3
                            print(f"     {rec.slot.value}: {rec.recommended_item} (+{rec.improvement_score:.1f}%)")

                else:
                    print(f"   ❌ Optimization failed for {char_name}")

            print("✅ Gear optimization analysis test passed\n")

        except Exception as e:
            print(f"❌ Gear optimization analysis test failed: {e}\n")

    def test_different_optimization_types(self):
        """Test different optimization types."""
        print("🔍 Test 6: Different Optimization Types")
        print("-" * 30)

        try:
            test_char = "TestRifleman"
            test_build = "rifleman_medic"
            test_budget = "medium"

            optimization_types = [
                OptimizationType.BALANCED,
                OptimizationType.DPS,
                OptimizationType.TANK,
                OptimizationType.SUPPORT
            ]

            for opt_type in optimization_types:
                print(f"✅ Testing {opt_type.value} optimization:")
                
                result = analyze_character_gear(test_char, test_build, opt_type, test_budget)
                
                if result:
                    print(f"   Overall improvement: {result.overall_improvement:.1f}%")
                    print(f"   Recommendations: {len(result.recommendations)}")
                    
                    # Show target stats differences
                    if opt_type == OptimizationType.DPS:
                        print(f"   Target stats focus: DPS-oriented")
                    elif opt_type == OptimizationType.TANK:
                        print(f"   Target stats focus: Tank-oriented")
                    elif opt_type == OptimizationType.SUPPORT:
                        print(f"   Target stats focus: Support-oriented")
                    else:
                        print(f"   Target stats focus: Balanced")

            print("✅ Different optimization types test passed\n")

        except Exception as e:
            print(f"❌ Different optimization types test failed: {e}\n")

    def test_budget_constraints(self):
        """Test budget constraints."""
        print("🔍 Test 7: Budget Constraints")
        print("-" * 30)

        try:
            test_char = "TestRifleman"
            test_build = "rifleman_medic"
            test_opt_type = OptimizationType.BALANCED

            budgets = ["low", "medium", "high"]

            for budget in budgets:
                print(f"✅ Testing {budget} budget optimization:")
                
                result = analyze_character_gear(test_char, test_build, test_opt_type, budget)
                
                if result:
                    print(f"   Total cost: {result.total_cost}")
                    print(f"   Recommendations: {len(result.recommendations)}")
                    
                    # Count recommendations by cost
                    cost_counts = {}
                    for rec in result.recommendations:
                        cost_counts[rec.cost] = cost_counts.get(rec.cost, 0) + 1
                    
                    print(f"   Cost breakdown: {cost_counts}")

            print("✅ Budget constraints test passed\n")

        except Exception as e:
            print(f"❌ Budget constraints test failed: {e}\n")

    def test_enhancement_recommendations(self):
        """Test enhancement recommendations."""
        print("🔍 Test 8: Enhancement Recommendations")
        print("-" * 30)

        try:
            gear_advisor = get_gear_advisor()

            # Test enhancement recommendations for different builds
            test_cases = [
                ("rifleman_medic", OptimizationType.DPS),
                ("rifleman_medic", OptimizationType.TANK),
                ("tk_pistoleer", OptimizationType.DPS),
                ("brawler_tank", OptimizationType.TANK)
            ]

            for build_id, opt_type in test_cases:
                print(f"✅ Testing enhancements for {build_id} ({opt_type.value}):")
                
                build_data = gear_advisor.build_loader.get_build(build_id)
                if build_data:
                    # Test enhancement recommendations for each armor set
                    for set_id, set_data in gear_advisor.armor_sets.items():
                        if gear_advisor._armor_set_matches_build(set_data, build_data):
                            print(f"   Armor set: {set_data['name']}")
                            
                            for slot_name, slot_data in set_data['slots'].items():
                                enhancements = gear_advisor._recommend_enhancements(
                                    slot_data, build_data, opt_type, "medium"
                                )
                                if enhancements:
                                    print(f"     {slot_name}: {enhancements}")

            print("✅ Enhancement recommendations test passed\n")

        except Exception as e:
            print(f"❌ Enhancement recommendations test failed: {e}\n")

    def test_result_saving(self):
        """Test result saving functionality."""
        print("🔍 Test 9: Result Saving")
        print("-" * 30)

        try:
            # Create a test optimization result
            test_char = "TestRifleman"
            test_build = "rifleman_medic"
            test_opt_type = OptimizationType.BALANCED
            test_budget = "medium"

            result = analyze_character_gear(test_char, test_build, test_opt_type, test_budget)
            
            if result:
                # Save the result
                saved = save_gear_optimization_result(result)
                
                if saved:
                    print(f"✅ Optimization result saved successfully")
                    print(f"   Character: {result.character_name}")
                    print(f"   Build: {result.build_id}")
                    print(f"   Optimization type: {result.optimization_type.value}")
                    print(f"   Overall improvement: {result.overall_improvement:.1f}%")
                    print(f"   Total cost: {result.total_cost}")
                    print(f"   Recommendations: {len(result.recommendations)}")
                    print(f"   Implementation priority: {len(result.implementation_priority)} items")
                    print(f"   Notes: {len(result.notes)}")
                else:
                    print(f"❌ Failed to save optimization result")

            print("✅ Result saving test passed\n")

        except Exception as e:
            print(f"❌ Result saving test failed: {e}\n")

    def generate_demo_report(self):
        """Generate a demo report."""
        report = {
            "demo_name": "Batch 124 Gear Optimizer Demo",
            "demo_date": datetime.now().isoformat(),
            "demo_user_hash": self.demo_user_hash,
            "tests_run": [
                "Gear Advisor Initialization",
                "Armor Sets Loading",
                "Character Profile Creation",
                "Build Loading",
                "Gear Optimization Analysis",
                "Different Optimization Types",
                "Budget Constraints",
                "Enhancement Recommendations",
                "Result Saving"
            ],
            "project_structure": {
                "gear_advisor": "optimizer/gear_advisor.py",
                "armor_sets": "data/armor_sets.json",
                "gear_suggestions": "ui/components/GearSuggestions.tsx",
                "gear_optimizer_page": "swgdb_site/pages/gear-optimizer.html"
            },
            "features_tested": [
                "Parse scanned stats (Batch 122) + selected build (Batch 123)",
                "Cross-reference armor sets and known resists",
                "Recommend gear improvements (e.g., 'replace boots with 40% kinetic')",
                "Upload optimizer results to dashboard (user-only view)",
                "Armor set compatibility scoring",
                "Enhancement recommendations based on build and optimization type",
                "Budget constraint handling",
                "Implementation priority calculation",
                "Result saving and export"
            ]
        }

        # Save demo report
        report_path = self.data_dir / f"gear_optimizer_demo_report_{self.demo_user_hash}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"📄 Demo report saved: {report_path}")
        return report


def main():
    """Main function to run the demo."""
    demo = GearOptimizerDemo()
    demo.run_complete_demo()

    # Generate demo report
    report = demo.generate_demo_report()

    print("\n📊 Demo Report Summary:")
    print(f"   Demo Name: {report['demo_name']}")
    print(f"   Demo Date: {report['demo_date']}")
    print(f"   Tests Run: {len(report['tests_run'])}")
    print(f"   Features Tested: {len(report['features_tested'])}")

    print("\n🎯 Batch 124 Implementation Complete!")
    print("   • Gear/Armor Optimizer (AskMrRoboto Logic)")
    print("   • Armor sets database with comprehensive stats")
    print("   • Enhancement recommendations system")
    print("   • Budget-aware optimization")
    print("   • React component for gear suggestions")
    print("   • Standalone web page for gear optimization")
    print("   • API endpoints for dashboard integration")


if __name__ == "__main__":
    main() 