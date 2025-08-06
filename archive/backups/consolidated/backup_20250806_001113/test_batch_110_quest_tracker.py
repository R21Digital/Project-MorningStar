#!/usr/bin/env python3
"""
Batch 110 - Public Quest Tracker Widget Tests

This test suite verifies the functionality of the quest tracker system,
including quest management, filtering, progress tracking, and widget features.

Author: SWG Bot Development Team
"""

import json
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

# Import quest tracker components
from core.quest_tracker import (
    QuestTracker, QuestDefinition, QuestProgress, QuestStatistics,
    QuestCategory, QuestDifficulty, QuestStatus, Planet, RewardType,
    QuestStep, QuestReward
)

class TestQuestTracker(unittest.TestCase):
    """Test cases for the Quest Tracker system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.tracker = QuestTracker(
            data_dir="data/quest_tracker",
            quests_file="quests.json",
            progress_file="progress.json",
            stats_file="statistics.json"
        )
        self.tracker.load_data()
    
    def test_quest_loading(self):
        """Test quest data loading."""
        print("🧪 Testing quest data loading...")
        
        # Check that quests were loaded
        self.assertGreater(len(self.tracker.quests), 0, "No quests loaded")
        
        # Check that progress was loaded
        self.assertGreater(len(self.tracker.progress), 0, "No progress data loaded")
        
        # Check that statistics were loaded
        self.assertGreater(len(self.tracker.statistics), 0, "No statistics loaded")
        
        print(f"✅ Loaded {len(self.tracker.quests)} quests, {len(self.tracker.progress)} progress entries, {len(self.tracker.statistics)} statistics")
    
    def test_quest_filtering(self):
        """Test quest filtering functionality."""
        print("🧪 Testing quest filtering...")
        
        # Test category filtering
        legacy_quests = self.tracker.filter_quests(
            self.tracker.QuestFilter(categories=[QuestCategory.LEGACY])
        )
        self.assertGreater(len(legacy_quests), 0, "No legacy quests found")
        
        # Test difficulty filtering
        heroic_quests = self.tracker.filter_quests(
            self.tracker.QuestFilter(difficulties=[QuestDifficulty.HEROIC])
        )
        self.assertGreater(len(heroic_quests), 0, "No heroic quests found")
        
        # Test planet filtering
        tatooine_quests = self.tracker.filter_quests(
            self.tracker.QuestFilter(planets=[Planet.TATOOINE])
        )
        self.assertGreater(len(tatooine_quests), 0, "No Tatooine quests found")
        
        # Test reward type filtering
        xp_quests = self.tracker.filter_quests(
            self.tracker.QuestFilter(reward_types=[RewardType.XP])
        )
        self.assertGreater(len(xp_quests), 0, "No XP reward quests found")
        
        print(f"✅ Filtering tests passed: {len(legacy_quests)} legacy, {len(heroic_quests)} heroic, {len(tatooine_quests)} Tatooine, {len(xp_quests)} XP quests")
    
    def test_quest_progress_tracking(self):
        """Test quest progress tracking."""
        print("🧪 Testing quest progress tracking...")
        
        # Test getting user progress
        user_progress = self.tracker.get_user_progress("player_001")
        self.assertGreater(len(user_progress), 0, "No user progress found")
        
        # Test getting quest progress
        quest_progress = self.tracker.get_quest_progress("legacy_001")
        self.assertGreater(len(quest_progress), 0, "No quest progress found")
        
        # Test progress update
        test_progress = QuestProgress(
            quest_id="test_quest",
            user_id="test_user",
            status=QuestStatus.IN_PROGRESS,
            current_step=1,
            steps_completed=["step1"],
            start_time=datetime.now(),
            notes="Test progress"
        )
        
        success = self.tracker.update_progress("test_user", "test_quest", test_progress)
        self.assertTrue(success, "Failed to update progress")
        
        # Verify the update
        updated_progress = self.tracker.get_user_progress("test_user")
        self.assertGreater(len(updated_progress), 0, "Progress update not found")
        
        print(f"✅ Progress tracking tests passed: {len(user_progress)} user progress, {len(quest_progress)} quest progress")
    
    def test_popular_quests(self):
        """Test popular quests functionality."""
        print("🧪 Testing popular quests...")
        
        popular_quests = self.tracker.get_popular_quests(5)
        self.assertGreater(len(popular_quests), 0, "No popular quests found")
        
        # Check that quests have statistics
        for quest, stats in popular_quests:
            self.assertIsNotNone(stats, "Quest statistics missing")
            self.assertGreaterEqual(stats.popularity_score, 0, "Invalid popularity score")
            self.assertGreaterEqual(stats.current_players, 0, "Invalid current players count")
        
        print(f"✅ Popular quests test passed: {len(popular_quests)} popular quests")
    
    def test_recent_activity(self):
        """Test recent activity functionality."""
        print("🧪 Testing recent activity...")
        
        recent_activity = self.tracker.get_recent_activity(24)
        self.assertIsInstance(recent_activity, list, "Recent activity should be a list")
        
        # Check activity structure
        for activity in recent_activity:
            self.assertIn('quest_id', activity, "Activity missing quest_id")
            self.assertIn('user_id', activity, "Activity missing user_id")
            self.assertIn('completion_time', activity, "Activity missing completion_time")
        
        print(f"✅ Recent activity test passed: {len(recent_activity)} activities")
    
    def test_quest_statistics(self):
        """Test quest statistics functionality."""
        print("🧪 Testing quest statistics...")
        
        overall_stats = self.tracker.get_overall_statistics()
        
        # Check required statistics fields
        required_fields = ['total_quests', 'total_attempts', 'total_completions', 'active_players']
        for field in required_fields:
            self.assertIn(field, overall_stats, f"Missing statistics field: {field}")
            self.assertIsInstance(overall_stats[field], (int, float), f"Invalid statistics field type: {field}")
        
        # Test individual quest statistics
        if self.tracker.quests:
            quest_id = self.tracker.quests[0].quest_id
            quest_stats = self.tracker.get_quest_statistics(quest_id)
            self.assertIsNotNone(quest_stats, "Quest statistics should not be None")
        
        print(f"✅ Statistics test passed: {overall_stats['total_quests']} total quests, {overall_stats['active_players']} active players")
    
    def test_widget_data_generation(self):
        """Test widget data generation."""
        print("🧪 Testing widget data generation...")
        
        # Get widget data components
        popular_quests = self.tracker.get_popular_quests(5)
        recent_activity = self.tracker.get_recent_activity(6)
        stats = self.tracker.get_overall_statistics()
        
        # Verify widget data structure
        widget_data = {
            'popular_quests': [],
            'recent_activity': [],
            'statistics': stats
        }
        
        # Format popular quests for widget
        for quest, quest_stats in popular_quests:
            widget_data['popular_quests'].append({
                'id': quest.quest_id,
                'name': quest.name,
                'category': quest.category.value,
                'difficulty': quest.difficulty.value,
                'planet': quest.planet.value,
                'popularity_score': quest_stats.popularity_score,
                'current_players': quest_stats.current_players
            })
        
        # Format recent activity for widget
        for activity in recent_activity[:5]:
            quest = self.tracker.get_quest(activity['quest_id'])
            if quest:
                widget_data['recent_activity'].append({
                    'user_id': activity['user_id'],
                    'quest_name': quest.name,
                    'category': quest.category.value,
                    'completion_time': activity['completion_time'].isoformat()
                })
        
        # Verify widget data
        self.assertIsInstance(widget_data['popular_quests'], list, "Popular quests should be a list")
        self.assertIsInstance(widget_data['recent_activity'], list, "Recent activity should be a list")
        self.assertIsInstance(widget_data['statistics'], dict, "Statistics should be a dict")
        
        print(f"✅ Widget data test passed: {len(widget_data['popular_quests'])} popular quests, {len(widget_data['recent_activity'])} recent activities")
    
    def test_quest_categories(self):
        """Test quest category functionality."""
        print("🧪 Testing quest categories...")
        
        # Test all categories
        categories = [QuestCategory.LEGACY, QuestCategory.THEME_PARK, QuestCategory.SPACE, 
                     QuestCategory.KASHYYYK, QuestCategory.MUSTAFAR, QuestCategory.HEROIC,
                     QuestCategory.DAILY, QuestCategory.WEEKLY]
        
        for category in categories:
            filtered_quests = self.tracker.filter_quests(
                self.tracker.QuestFilter(categories=[category])
            )
            print(f"  {category.value}: {len(filtered_quests)} quests")
        
        print("✅ Quest categories test passed")
    
    def test_quest_difficulties(self):
        """Test quest difficulty functionality."""
        print("🧪 Testing quest difficulties...")
        
        # Test all difficulties
        difficulties = [QuestDifficulty.EASY, QuestDifficulty.NORMAL, QuestDifficulty.HARD,
                      QuestDifficulty.HEROIC, QuestDifficulty.LEGENDARY]
        
        for difficulty in difficulties:
            filtered_quests = self.tracker.filter_quests(
                self.tracker.QuestFilter(difficulties=[difficulty])
            )
            print(f"  {difficulty.value}: {len(filtered_quests)} quests")
        
        print("✅ Quest difficulties test passed")
    
    def test_quest_planets(self):
        """Test quest planet functionality."""
        print("🧪 Testing quest planets...")
        
        # Test all planets
        planets = [Planet.TATOOINE, Planet.NABOO, Planet.CORELLIA, Planet.RORI, Planet.TALUS,
                  Planet.DATHOMIR, Planet.LOK, Planet.ENDOR, Planet.DANTOOINE, Planet.YAVIN4,
                  Planet.KASHYYYK, Planet.MUSTAFAR, Planet.SPACE]
        
        for planet in planets:
            filtered_quests = self.tracker.filter_quests(
                self.tracker.QuestFilter(planets=[planet])
            )
            if filtered_quests:
                print(f"  {planet.value}: {len(filtered_quests)} quests")
        
        print("✅ Quest planets test passed")
    
    def test_quest_rewards(self):
        """Test quest reward functionality."""
        print("🧪 Testing quest rewards...")
        
        # Test all reward types
        reward_types = [RewardType.XP, RewardType.CREDITS, RewardType.ITEMS, 
                       RewardType.TITLES, RewardType.DECORATIONS, RewardType.VEHICLES]
        
        for reward_type in reward_types:
            filtered_quests = self.tracker.filter_quests(
                self.tracker.QuestFilter(reward_types=[reward_type])
            )
            print(f"  {reward_type.value}: {len(filtered_quests)} quests")
        
        print("✅ Quest rewards test passed")
    
    def test_quest_search(self):
        """Test quest search functionality."""
        print("🧪 Testing quest search...")
        
        # Test search by quest name
        search_results = self.tracker.filter_quests(
            self.tracker.QuestFilter(search_term="Jedi")
        )
        self.assertIsInstance(search_results, list, "Search results should be a list")
        
        # Test search by description
        search_results = self.tracker.filter_quests(
            self.tracker.QuestFilter(search_term="Palace")
        )
        self.assertIsInstance(search_results, list, "Search results should be a list")
        
        print(f"✅ Quest search test passed: {len(search_results)} search results")
    
    def test_quest_combinations(self):
        """Test quest filter combinations."""
        print("🧪 Testing quest filter combinations...")
        
        # Test multiple categories
        multi_category_filter = self.tracker.QuestFilter(
            categories=[QuestCategory.LEGACY, QuestCategory.THEME_PARK]
        )
        multi_category_results = self.tracker.filter_quests(multi_category_filter)
        self.assertIsInstance(multi_category_results, list, "Multi-category results should be a list")
        
        # Test multiple difficulties
        multi_difficulty_filter = self.tracker.QuestFilter(
            difficulties=[QuestDifficulty.HARD, QuestDifficulty.HEROIC]
        )
        multi_difficulty_results = self.tracker.filter_quests(multi_difficulty_filter)
        self.assertIsInstance(multi_difficulty_results, list, "Multi-difficulty results should be a list")
        
        # Test complex filter
        complex_filter = self.tracker.QuestFilter(
            categories=[QuestCategory.SPACE],
            difficulties=[QuestDifficulty.HEROIC],
            planets=[Planet.SPACE]
        )
        complex_results = self.tracker.filter_quests(complex_filter)
        self.assertIsInstance(complex_results, list, "Complex filter results should be a list")
        
        print(f"✅ Filter combinations test passed: {len(multi_category_results)} multi-category, {len(multi_difficulty_results)} multi-difficulty, {len(complex_results)} complex")
    
    def test_data_persistence(self):
        """Test data persistence functionality."""
        print("🧪 Testing data persistence...")
        
        # Save data
        self.tracker.save_data()
        
        # Check that files exist
        data_dir = Path("data/quest_tracker")
        self.assertTrue(data_dir.exists(), "Data directory should exist")
        
        quests_file = data_dir / "quests.json"
        progress_file = data_dir / "progress.json"
        stats_file = data_dir / "statistics.json"
        
        self.assertTrue(quests_file.exists(), "Quests file should exist")
        self.assertTrue(progress_file.exists(), "Progress file should exist")
        self.assertTrue(stats_file.exists(), "Statistics file should exist")
        
        # Check file sizes
        self.assertGreater(quests_file.stat().st_size, 0, "Quests file should not be empty")
        self.assertGreater(progress_file.stat().st_size, 0, "Progress file should not be empty")
        self.assertGreater(stats_file.stat().st_size, 0, "Statistics file should not be empty")
        
        print("✅ Data persistence test passed")
    
    def test_web_interface_endpoints(self):
        """Test web interface endpoint functionality."""
        print("🧪 Testing web interface endpoints...")
        
        # Test that we can get all quests
        all_quests = self.tracker.get_all_quests()
        self.assertGreater(len(all_quests), 0, "Should have quests available")
        
        # Test that we can get specific quest
        if all_quests:
            quest = self.tracker.get_quest(all_quests[0].quest_id)
            self.assertIsNotNone(quest, "Should be able to get specific quest")
        
        # Test that we can get categories
        categories = [cat.value for cat in QuestCategory]
        self.assertGreater(len(categories), 0, "Should have categories available")
        
        # Test that we can get difficulties
        difficulties = [diff.value for diff in QuestDifficulty]
        self.assertGreater(len(difficulties), 0, "Should have difficulties available")
        
        # Test that we can get planets
        planets = [planet.value for planet in Planet]
        self.assertGreater(len(planets), 0, "Should have planets available")
        
        print(f"✅ Web interface endpoints test passed: {len(all_quests)} quests, {len(categories)} categories, {len(difficulties)} difficulties, {len(planets)} planets")

def run_performance_tests():
    """Run performance tests for the quest tracker."""
    print("\n🚀 Running performance tests...")
    
    tracker = QuestTracker()
    tracker.load_data()
    
    import time
    
    # Test filtering performance
    start_time = time.time()
    for _ in range(100):
        tracker.filter_quests(tracker.QuestFilter(categories=[QuestCategory.LEGACY]))
    filter_time = time.time() - start_time
    
    # Test statistics performance
    start_time = time.time()
    for _ in range(100):
        tracker.get_overall_statistics()
    stats_time = time.time() - start_time
    
    # Test popular quests performance
    start_time = time.time()
    for _ in range(100):
        tracker.get_popular_quests(5)
    popular_time = time.time() - start_time
    
    print(f"✅ Performance test results:")
    print(f"  Filtering: {filter_time:.3f}s for 100 operations")
    print(f"  Statistics: {stats_time:.3f}s for 100 operations")
    print(f"  Popular quests: {popular_time:.3f}s for 100 operations")

def run_integration_tests():
    """Run integration tests for the quest tracker."""
    print("\n🔗 Running integration tests...")
    
    tracker = QuestTracker()
    tracker.load_data()
    
    # Test full workflow
    print("  Testing quest discovery workflow...")
    all_quests = tracker.get_all_quests()
    self.assertGreater(len(all_quests), 0, "Should have quests to discover")
    
    print("  Testing quest filtering workflow...")
    filtered_quests = tracker.filter_quests(tracker.QuestFilter(categories=[QuestCategory.LEGACY]))
    self.assertGreater(len(filtered_quests), 0, "Should have legacy quests")
    
    print("  Testing progress tracking workflow...")
    if filtered_quests:
        quest = filtered_quests[0]
        progress = QuestProgress(
            quest_id=quest.quest_id,
            user_id="integration_test_user",
            status=QuestStatus.IN_PROGRESS,
            current_step=1,
            steps_completed=[],
            start_time=datetime.now(),
            notes="Integration test"
        )
        success = tracker.update_progress("integration_test_user", quest.quest_id, progress)
        self.assertTrue(success, "Should be able to update progress")
    
    print("  Testing statistics workflow...")
    stats = tracker.get_overall_statistics()
    self.assertIsInstance(stats, dict, "Should get statistics")
    
    print("  Testing widget data workflow...")
    popular_quests = tracker.get_popular_quests(5)
    recent_activity = tracker.get_recent_activity(6)
    self.assertGreater(len(popular_quests), 0, "Should have popular quests")
    self.assertIsInstance(recent_activity, list, "Should have recent activity")
    
    print("✅ Integration tests passed")

def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 BATCH 110 - PUBLIC QUEST TRACKER WIDGET TESTS")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestQuestTracker)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Run additional tests
    run_performance_tests()
    run_integration_tests()
    
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ ALL TESTS PASSED!")
        print("🎯 Quest Tracker is ready for production use")
    else:
        print("❌ SOME TESTS FAILED!")
        print("🔧 Please check the implementation")
    print("=" * 60)
    
    # Print summary
    print("\n📊 Test Summary:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100:.1f}%")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 