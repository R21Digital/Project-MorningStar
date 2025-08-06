#!/usr/bin/env python3
"""
Test Script for Batch 126 - GCW/Faction Rank Tracker + Strategy Advisor

This script provides comprehensive testing of the GCW tracking and strategy advisory system,
validating all functionality including faction detection, battle logging, gear recommendations,
strategy guides, and data persistence.

Author: SWG Bot Development Team
"""

import json
import time
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import tempfile
import shutil

# Import the GCW Tracker
from core.gcw_tracker import (
    GCWTracker, FactionType, BattleType, GearCategory, StrategyType,
    GCWBattle, FactionProfile, GearRecommendation, StrategyGuide, GCWEvent
)

class TestGCWTracker(unittest.TestCase):
    """Test suite for GCW Tracker functionality."""
    
    def setUp(self):
        """Set up test environment with temporary data directory."""
        # Create temporary directory for test data
        self.test_dir = Path(tempfile.mkdtemp())
        self.tracker = GCWTracker(
            data_dir=str(self.test_dir),
            profiles_file="test_profiles.json",
            battles_file="test_battles.json",
            events_file="test_events.json",
            gear_file="test_gear.json",
            strategies_file="test_strategies.json"
        )
        
        # Test data
        self.test_characters = ["TestRebel", "TestImperial", "TestNeutral"]
        self.test_battles = [
            {
                'battle_type': 'pvp',
                'location': 'TestLocation1',
                'faction': 'rebel',
                'rank_at_time': 4,
                'outcome': 'victory',
                'duration': 15,
                'participants': 8,
                'rewards': {'points': 150, 'credits': 5000},
                'timestamp': datetime.now().isoformat()
            },
            {
                'battle_type': 'zone_control',
                'location': 'TestLocation2',
                'faction': 'imperial',
                'rank_at_time': 5,
                'outcome': 'victory',
                'duration': 45,
                'participants': 20,
                'rewards': {'points': 300, 'credits': 10000},
                'timestamp': datetime.now().isoformat()
            }
        ]
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary directory
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)
    
    def test_faction_detection(self):
        """Test faction detection functionality."""
        print("\nTesting Faction Detection...")
        
        # Test Rebel detection
        rebel_indicators = {
            'faction': 'rebel',
            'rank': 4,
            'rank_points': 4500,
            'items': ['rebel_armor', 'rebel_weapon'],
            'abilities': ['rebel_tactics']
        }
        
        profile = self.tracker.detect_faction_status("TestRebel", rebel_indicators)
        self.assertEqual(profile.faction, FactionType.REBEL)
        self.assertEqual(profile.current_rank, 4)
        self.assertEqual(profile.rank_points, 4500)
        print("✓ Rebel faction detection passed")
        
        # Test Imperial detection
        imperial_indicators = {
            'faction': 'imperial',
            'rank': 5,
            'rank_points': 6000,
            'items': ['imperial_armor', 'imperial_weapon'],
            'abilities': ['imperial_tactics']
        }
        
        profile = self.tracker.detect_faction_status("TestImperial", imperial_indicators)
        self.assertEqual(profile.faction, FactionType.IMPERIAL)
        self.assertEqual(profile.current_rank, 5)
        self.assertEqual(profile.rank_points, 6000)
        print("✓ Imperial faction detection passed")
        
        # Test Neutral detection
        neutral_indicators = {
            'faction': 'neutral',
            'rank': 0,
            'rank_points': 0,
            'items': ['civilian_clothing'],
            'abilities': []
        }
        
        profile = self.tracker.detect_faction_status("TestNeutral", neutral_indicators)
        self.assertEqual(profile.faction, FactionType.NEUTRAL)
        self.assertEqual(profile.current_rank, 0)
        self.assertEqual(profile.rank_points, 0)
        print("✓ Neutral faction detection passed")
    
    def test_battle_logging(self):
        """Test battle logging functionality."""
        print("\nTesting Battle Logging...")
        
        # Create test profiles first
        self.tracker.detect_faction_status("TestRebel", {
            'faction': 'rebel', 'rank': 4, 'rank_points': 4500
        })
        self.tracker.detect_faction_status("TestImperial", {
            'faction': 'imperial', 'rank': 5, 'rank_points': 6000
        })
        
        # Log battles
        for i, battle_data in enumerate(self.test_battles):
            character = "TestRebel" if battle_data['faction'] == 'rebel' else "TestImperial"
            battle = self.tracker.log_battle(character, battle_data)
            
            self.assertIsInstance(battle, GCWBattle)
            self.assertEqual(battle.battle_type.value, battle_data['battle_type'])
            self.assertEqual(battle.location, battle_data['location'])
            self.assertEqual(battle.outcome, battle_data['outcome'])
            print(f"✓ Battle {i+1} logging passed")
        
        # Verify battle statistics
        rebel_profile = self.tracker.profiles.get("TestRebel")
        self.assertIsNotNone(rebel_profile)
        self.assertEqual(rebel_profile.total_battles, 1)
        self.assertEqual(rebel_profile.victories, 1)
        self.assertEqual(rebel_profile.win_rate, 1.0)
        print("✓ Battle statistics calculation passed")
    
    def test_gear_recommendations(self):
        """Test gear recommendations functionality."""
        print("\nTesting Gear Recommendations...")
        
        # Create test profiles
        self.tracker.detect_faction_status("TestRebel", {
            'faction': 'rebel', 'rank': 4, 'rank_points': 4500
        })
        self.tracker.detect_faction_status("TestImperial", {
            'faction': 'imperial', 'rank': 5, 'rank_points': 6000
        })
        
        # Test gear recommendations for Rebel
        rebel_gear = self.tracker.get_gear_recommendations("TestRebel")
        self.assertGreater(len(rebel_gear), 0)
        
        # Check that Rebel-specific gear is included
        rebel_gear_names = [gear.item_name for gear in rebel_gear]
        self.assertTrue(any("Rebel" in name for name in rebel_gear_names))
        print("✓ Rebel gear recommendations passed")
        
        # Test gear recommendations for Imperial
        imperial_gear = self.tracker.get_gear_recommendations("TestImperial")
        self.assertGreater(len(imperial_gear), 0)
        
        # Check that Imperial-specific gear is included
        imperial_gear_names = [gear.item_name for gear in imperial_gear]
        self.assertTrue(any("Imperial" in name for name in imperial_gear_names))
        print("✓ Imperial gear recommendations passed")
        
        # Test gear filtering by rank
        high_rank_gear = self.tracker.get_gear_recommendations("TestRebel", rank=6)
        for gear in high_rank_gear:
            self.assertLessEqual(gear.rank_requirement, 6)
        print("✓ Gear rank filtering passed")
    
    def test_strategy_guides(self):
        """Test strategy guides functionality."""
        print("\nTesting Strategy Guides...")
        
        # Create test profiles
        self.tracker.detect_faction_status("TestRebel", {
            'faction': 'rebel', 'rank': 4, 'rank_points': 4500
        })
        self.tracker.detect_faction_status("TestImperial", {
            'faction': 'imperial', 'rank': 5, 'rank_points': 6000
        })
        
        # Test strategy guides for Rebel
        rebel_strategies = self.tracker.get_strategy_guides("TestRebel")
        self.assertGreater(len(rebel_strategies), 0)
        
        # Check that Rebel strategies are included
        rebel_strategy_titles = [guide.title for guide in rebel_strategies]
        self.assertTrue(any("Rebel" in title for title in rebel_strategy_titles))
        print("✓ Rebel strategy guides passed")
        
        # Test strategy guides for Imperial
        imperial_strategies = self.tracker.get_strategy_guides("TestImperial")
        self.assertGreater(len(imperial_strategies), 0)
        
        # Check that Imperial strategies are included
        imperial_strategy_titles = [guide.title for guide in imperial_strategies]
        self.assertTrue(any("Imperial" in title for title in imperial_strategy_titles))
        print("✓ Imperial strategy guides passed")
        
        # Test strategy filtering by type
        offensive_strategies = self.tracker.get_strategy_guides(
            "TestRebel", strategy_type=StrategyType.OFFENSIVE
        )
        for strategy in offensive_strategies:
            self.assertEqual(strategy.strategy_type, StrategyType.OFFENSIVE)
        print("✓ Strategy type filtering passed")
    
    def test_rank_progression(self):
        """Test rank progression analysis."""
        print("\nTesting Rank Progression...")
        
        # Create test profile and log battles
        self.tracker.detect_faction_status("TestRebel", {
            'faction': 'rebel', 'rank': 4, 'rank_points': 4500
        })
        
        # Log some battles to generate progression data
        for battle_data in self.test_battles[:1]:  # Just one battle
            self.tracker.log_battle("TestRebel", battle_data)
        
        # Test rank progression analysis
        progression = self.tracker.get_rank_progression("TestRebel")
        self.assertIsNotNone(progression)
        self.assertEqual(progression['current_rank'], 4)
        self.assertGreater(progression['current_points'], 0)
        self.assertEqual(progression['next_rank'], 5)
        self.assertGreater(progression['points_needed'], 0)
        print("✓ Rank progression analysis passed")
    
    def test_faction_statistics(self):
        """Test faction statistics functionality."""
        print("\nTesting Faction Statistics...")
        
        # Create test profiles and log battles
        self.tracker.detect_faction_status("TestRebel", {
            'faction': 'rebel', 'rank': 4, 'rank_points': 4500
        })
        self.tracker.detect_faction_status("TestImperial", {
            'faction': 'imperial', 'rank': 5, 'rank_points': 6000
        })
        
        # Log battles for both factions
        for battle_data in self.test_battles:
            character = "TestRebel" if battle_data['faction'] == 'rebel' else "TestImperial"
            self.tracker.log_battle(character, battle_data)
        
        # Test Rebel statistics
        rebel_stats = self.tracker.get_faction_statistics(FactionType.REBEL)
        self.assertEqual(rebel_stats['total_characters'], 1)
        self.assertGreater(rebel_stats['battle_statistics']['total_battles'], 0)
        print("✓ Rebel faction statistics passed")
        
        # Test Imperial statistics
        imperial_stats = self.tracker.get_faction_statistics(FactionType.IMPERIAL)
        self.assertEqual(imperial_stats['total_characters'], 1)
        self.assertGreater(imperial_stats['battle_statistics']['total_battles'], 0)
        print("✓ Imperial faction statistics passed")
        
        # Test overall statistics
        overall_stats = self.tracker.get_faction_statistics()
        self.assertEqual(overall_stats['total_characters'], 2)
        self.assertGreater(overall_stats['battle_statistics']['total_battles'], 0)
        print("✓ Overall faction statistics passed")
    
    def test_gcw_events(self):
        """Test GCW events functionality."""
        print("\nTesting GCW Events...")
        
        # Create test event
        event_data = {
            'event_id': 'test_event_001',
            'name': 'Test Battle Event',
            'description': 'A test GCW event',
            'start_time': datetime.now().isoformat(),
            'end_time': (datetime.now() + timedelta(hours=2)).isoformat(),
            'location': 'TestLocation',
            'faction_restriction': None,
            'rank_requirement': 4,
            'rewards': {'points': 300, 'credits': 15000},
            'participants': []
        }
        
        # Add event
        event = self.tracker.add_gcw_event(event_data)
        self.assertIsInstance(event, GCWEvent)
        self.assertEqual(event.name, 'Test Battle Event')
        self.assertEqual(event.location, 'TestLocation')
        print("✓ GCW event creation passed")
        
        # Test active events
        self.tracker.detect_faction_status("TestRebel", {
            'faction': 'rebel', 'rank': 4, 'rank_points': 4500
        })
        
        active_events = self.tracker.get_active_events("TestRebel")
        self.assertGreater(len(active_events), 0)
        print("✓ Active events retrieval passed")
    
    def test_data_persistence(self):
        """Test data persistence functionality."""
        print("\nTesting Data Persistence...")
        
        # Create test data
        self.tracker.detect_faction_status("TestRebel", {
            'faction': 'rebel', 'rank': 4, 'rank_points': 4500
        })
        
        self.tracker.log_battle("TestRebel", self.test_battles[0])
        
        # Add test gear and strategy
        test_gear = GearRecommendation(
            item_name="Test Gear",
            category=GearCategory.ARMOR,
            rank_requirement=4,
            faction_requirement=None,
            stats={"constitution": 20},
            resists={"energy": 25},
            cost="medium",
            priority="high",
            reasoning="Test gear for testing"
        )
        self.tracker.gear_recommendations["test_gear_4"] = test_gear
        
        test_strategy = StrategyGuide(
            rank=4,
            faction=FactionType.REBEL,
            strategy_type=StrategyType.OFFENSIVE,
            title="Test Strategy",
            description="A test strategy guide",
            tactics=["Test tactic 1", "Test tactic 2"],
            gear_requirements=["Test Gear"],
            skill_requirements=["Test Skill"],
            difficulty="medium",
            estimated_success_rate=0.75
        )
        self.tracker.strategy_guides["test_strategy_4"] = test_strategy
        
        # Save data
        self.tracker.save_data()
        
        # Verify files were created
        self.assertTrue(self.tracker.profiles_file.exists())
        self.assertTrue(self.tracker.battles_file.exists())
        self.assertTrue(self.tracker.gear_file.exists())
        self.assertTrue(self.tracker.strategies_file.exists())
        print("✓ Data persistence passed")
        
        # Test data loading
        new_tracker = GCWTracker(
            data_dir=str(self.test_dir),
            profiles_file="test_profiles.json",
            battles_file="test_battles.json",
            events_file="test_events.json",
            gear_file="test_gear.json",
            strategies_file="test_strategies.json"
        )
        
        # Verify data was loaded correctly
        self.assertIn("TestRebel", new_tracker.profiles)
        self.assertIn("test_gear_4", new_tracker.gear_recommendations)
        self.assertIn("test_strategy_4", new_tracker.strategy_guides)
        print("✓ Data loading passed")
    
    def test_advanced_features(self):
        """Test advanced GCW tracker features."""
        print("\nTesting Advanced Features...")
        
        # Test custom gear creation
        custom_gear = GearRecommendation(
            item_name="Experimental Combat Suit",
            category=GearCategory.ARMOR,
            rank_requirement=7,
            faction_requirement=None,
            stats={"constitution": 35, "stamina": 30},
            resists={"energy": 45, "kinetic": 40, "stun": 30},
            cost="very_high",
            priority="critical",
            reasoning="Experimental armor with advanced protection"
        )
        
        self.tracker.gear_recommendations["experimental_suit_7"] = custom_gear
        self.assertIn("experimental_suit_7", self.tracker.gear_recommendations)
        print("✓ Custom gear creation passed")
        
        # Test custom strategy creation
        custom_strategy = StrategyGuide(
            rank=10,
            faction=FactionType.REBEL,
            strategy_type=StrategyType.STEALTH,
            title="Elite Stealth Operations",
            description="Ultimate stealth tactics for Rebel Marshals",
            tactics=[
                "Infiltrate enemy bases undetected",
                "Execute precision strikes",
                "Maintain operational security"
            ],
            gear_requirements=[
                "Stealth Combat Suit",
                "Advanced Cloaking Device"
            ],
            skill_requirements=[
                "Stealth: 4/4",
                "Tactics: 4/4"
            ],
            difficulty="expert",
            estimated_success_rate=0.90
        )
        
        self.tracker.strategy_guides["elite_stealth_10"] = custom_strategy
        self.assertIn("elite_stealth_10", self.tracker.strategy_guides)
        print("✓ Custom strategy creation passed")
        
        # Test gear recommendations with custom gear
        recommendations = self.tracker.get_gear_recommendations("TestRebel", rank=7)
        gear_names = [gear.item_name for gear in recommendations]
        self.assertIn("Experimental Combat Suit", gear_names)
        print("✓ Advanced gear recommendations passed")
    
    def test_error_handling(self):
        """Test error handling functionality."""
        print("\nTesting Error Handling...")
        
        # Test invalid faction detection
        invalid_indicators = {
            'faction': 'invalid_faction',
            'rank': 4,
            'rank_points': 4500
        }
        
        # This should handle the error gracefully
        try:
            profile = self.tracker.detect_faction_status("TestInvalid", invalid_indicators)
            # Should default to neutral
            self.assertEqual(profile.faction, FactionType.NEUTRAL)
            print("✓ Invalid faction handling passed")
        except Exception as e:
            self.fail(f"Faction detection should handle invalid faction gracefully: {e}")
        
        # Test invalid battle data
        invalid_battle = {
            'battle_type': 'invalid_type',
            'location': 'TestLocation',
            'faction': 'rebel',
            'rank_at_time': 4,
            'outcome': 'invalid_outcome',
            'duration': -5,  # Invalid duration
            'participants': 0,
            'rewards': {},
            'timestamp': 'invalid_timestamp'
        }
        
        # This should handle the error gracefully
        try:
            battle = self.tracker.log_battle("TestRebel", invalid_battle)
            self.assertIsInstance(battle, GCWBattle)
            print("✓ Invalid battle data handling passed")
        except Exception as e:
            self.fail(f"Battle logging should handle invalid data gracefully: {e}")
    
    def test_performance(self):
        """Test performance with large datasets."""
        print("\nTesting Performance...")
        
        # Create multiple profiles
        start_time = time.time()
        for i in range(100):
            char_name = f"TestChar{i}"
            faction = 'rebel' if i % 2 == 0 else 'imperial'
            self.tracker.detect_faction_status(char_name, {
                'faction': faction,
                'rank': i % 10,
                'rank_points': i * 100
            })
        
        profile_time = time.time() - start_time
        self.assertLess(profile_time, 5.0)  # Should complete within 5 seconds
        print(f"✓ Profile creation performance: {profile_time:.2f}s")
        
        # Log multiple battles
        start_time = time.time()
        for i in range(50):
            char_name = f"TestChar{i % 10}"
            battle_data = {
                'battle_type': 'pvp',
                'location': f'Location{i}',
                'faction': 'rebel' if i % 2 == 0 else 'imperial',
                'rank_at_time': i % 10,
                'outcome': 'victory' if i % 3 == 0 else 'defeat',
                'duration': 15 + (i % 30),
                'participants': 5 + (i % 10),
                'rewards': {'points': 100 + (i * 10), 'credits': 5000 + (i * 100)},
                'timestamp': datetime.now().isoformat()
            }
            self.tracker.log_battle(char_name, battle_data)
        
        battle_time = time.time() - start_time
        self.assertLess(battle_time, 10.0)  # Should complete within 10 seconds
        print(f"✓ Battle logging performance: {battle_time:.2f}s")
        
        # Test statistics calculation
        start_time = time.time()
        stats = self.tracker.get_faction_statistics()
        stats_time = time.time() - start_time
        self.assertLess(stats_time, 2.0)  # Should complete within 2 seconds
        print(f"✓ Statistics calculation performance: {stats_time:.2f}s")

def run_comprehensive_tests():
    """Run comprehensive tests for GCW Tracker."""
    print("=" * 80)
    print("BATCH 126 COMPREHENSIVE TEST SUITE")
    print("GCW/Faction Rank Tracker + Strategy Advisor")
    print("=" * 80)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test methods
    test_methods = [
        'test_faction_detection',
        'test_battle_logging',
        'test_gear_recommendations',
        'test_strategy_guides',
        'test_rank_progression',
        'test_faction_statistics',
        'test_gcw_events',
        'test_data_persistence',
        'test_advanced_features',
        'test_error_handling',
        'test_performance'
    ]
    
    for method_name in test_methods:
        test_suite.addTest(TestGCWTracker(method_name))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED!")
        print("✓ GCW Tracker is fully functional")
        print("✓ All features are working correctly")
        print("✓ Data persistence is reliable")
        print("✓ Performance is acceptable")
    else:
        print("\n✗ SOME TESTS FAILED!")
        print("Please review the failures and errors above")
    
    return result.wasSuccessful()

def main():
    """Main test function."""
    try:
        success = run_comprehensive_tests()
        
        if success:
            print("\n" + "=" * 80)
            print("BATCH 126 IMPLEMENTATION VALIDATION")
            print("=" * 80)
            print("✓ Faction Detection: Working correctly")
            print("✓ Battle Logging: Working correctly")
            print("✓ Gear Recommendations: Working correctly")
            print("✓ Strategy Guides: Working correctly")
            print("✓ Rank Progression: Working correctly")
            print("✓ Faction Statistics: Working correctly")
            print("✓ GCW Events: Working correctly")
            print("✓ Data Persistence: Working correctly")
            print("✓ Advanced Features: Working correctly")
            print("✓ Error Handling: Working correctly")
            print("✓ Performance: Acceptable")
            print("✓ All components validated successfully!")
        
        return success
        
    except Exception as e:
        print(f"Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 