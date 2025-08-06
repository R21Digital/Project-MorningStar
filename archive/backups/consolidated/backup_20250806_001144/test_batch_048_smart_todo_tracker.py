"""
Test Suite for Batch 048 - Smart Todo Tracker

This test suite provides comprehensive testing for the Smart Todo Tracker system,
including unit tests, integration tests, and performance tests.
"""

import json
import logging
import unittest
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Import the smart todo tracker components
from core.todo_tracker import (
    get_smart_tracker, SmartGoal, GoalStatus, GoalPriority, GoalCategory,
    GoalType, SmartSuggestion, CompletionScore, GoalLocation, GoalReward,
    GoalPrerequisite, add_goal, update_goal_progress, complete_goal,
    get_smart_suggestions, get_completion_scores, get_statistics,
    SmartTodoTracker
)

# Configure logging for tests
logging.basicConfig(level=logging.WARNING)


class TestSmartGoal(unittest.TestCase):
    """Test SmartGoal dataclass functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sample_goal = SmartGoal(
            id="test_goal_001",
            title="Test Goal",
            description="A test goal for unit testing",
            goal_type=GoalType.QUEST,
            category=GoalCategory.MAIN_QUEST,
            priority=GoalPriority.HIGH,
            location=GoalLocation(planet="tatooine", city="mos_eisley"),
            estimated_time=30,
            difficulty="easy",
            rewards=[
                GoalReward(type="experience", value=1000, description="Experience points"),
                GoalReward(type="credits", value=500, description="Credits")
            ],
            tags=["test", "unit_test"]
        )
    
    def test_goal_creation(self):
        """Test goal creation with all fields."""
        self.assertEqual(self.sample_goal.id, "test_goal_001")
        self.assertEqual(self.sample_goal.title, "Test Goal")
        self.assertEqual(self.sample_goal.goal_type, GoalType.QUEST)
        self.assertEqual(self.sample_goal.priority, GoalPriority.HIGH)
        self.assertEqual(self.sample_goal.status, GoalStatus.NOT_STARTED)
        self.assertEqual(len(self.sample_goal.rewards), 2)
        self.assertEqual(len(self.sample_goal.tags), 2)
    
    def test_goal_serialization(self):
        """Test goal serialization to dictionary."""
        goal_dict = self.sample_goal.to_dict()
        
        self.assertIn('id', goal_dict)
        self.assertIn('title', goal_dict)
        self.assertIn('goal_type', goal_dict)
        self.assertIn('rewards', goal_dict)
        self.assertIn('tags', goal_dict)
        
        self.assertEqual(goal_dict['id'], "test_goal_001")
        self.assertEqual(goal_dict['goal_type'], "quest")
        self.assertEqual(len(goal_dict['rewards']), 2)
    
    def test_goal_deserialization(self):
        """Test goal deserialization from dictionary."""
        goal_dict = self.sample_goal.to_dict()
        reconstructed_goal = SmartGoal.from_dict(goal_dict)
        
        self.assertEqual(reconstructed_goal.id, self.sample_goal.id)
        self.assertEqual(reconstructed_goal.title, self.sample_goal.title)
        self.assertEqual(reconstructed_goal.goal_type, self.sample_goal.goal_type)
        self.assertEqual(len(reconstructed_goal.rewards), len(self.sample_goal.rewards))
        self.assertEqual(len(reconstructed_goal.tags), len(self.sample_goal.tags))
    
    def test_goal_progress_calculation(self):
        """Test goal progress percentage calculation."""
        goal = SmartGoal(
            id="progress_test",
            title="Progress Test Goal",
            progress_current=3,
            progress_total=5
        )
        
        self.assertEqual(goal.progress_percentage, 60.0)
    
    def test_goal_with_prerequisites(self):
        """Test goal with prerequisites."""
        goal = SmartGoal(
            id="prereq_test",
            title="Prerequisite Test Goal",
            prerequisites=[
                GoalPrerequisite(
                    goal_id="test_goal_001",
                    goal_type=GoalType.QUEST,
                    description="Requires test goal completion"
                )
            ]
        )
        
        self.assertEqual(len(goal.prerequisites), 1)
        self.assertEqual(goal.prerequisites[0].goal_id, "test_goal_001")


class TestSmartTodoTracker(unittest.TestCase):
    """Test SmartTodoTracker class functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.test_data_file = Path(self.test_dir) / "test_smart_goals.json"
        
        # Create tracker with test data file
        self.tracker = SmartTodoTracker(str(self.test_data_file))
        
        # Create test goals
        self.test_goals = [
            SmartGoal(
                id="test_quest_001",
                title="Test Quest 1",
                goal_type=GoalType.QUEST,
                category=GoalCategory.MAIN_QUEST,
                priority=GoalPriority.HIGH,
                location=GoalLocation(planet="tatooine", city="mos_eisley"),
                estimated_time=30
            ),
            SmartGoal(
                id="test_collection_001",
                title="Test Collection 1",
                goal_type=GoalType.COLLECTION,
                category=GoalCategory.COLLECTION_ITEM,
                priority=GoalPriority.MEDIUM,
                location=GoalLocation(planet="naboo", city="theed"),
                estimated_time=20
            ),
            SmartGoal(
                id="test_faction_001",
                title="Test Faction 1",
                goal_type=GoalType.FACTION,
                category=GoalCategory.FACTION_QUEST,
                priority=GoalPriority.HIGH,
                location=GoalLocation(planet="corellia", city="coronet"),
                estimated_time=45
            )
        ]
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_tracker_initialization(self):
        """Test tracker initialization."""
        self.assertIsNotNone(self.tracker)
        self.assertEqual(len(self.tracker.goals), 0)
        self.assertIsInstance(self.tracker.completion_scores, dict)
    
    def test_add_goal(self):
        """Test adding goals to tracker."""
        goal = self.test_goals[0]
        goal_id = self.tracker.add_goal(goal)
        
        self.assertEqual(goal_id, goal.id)
        self.assertIn(goal.id, self.tracker.goals)
        self.assertEqual(self.tracker.goals[goal.id], goal)
    
    def test_update_goal_progress(self):
        """Test updating goal progress."""
        goal = self.test_goals[0]
        self.tracker.add_goal(goal)
        
        # Update progress
        self.tracker.update_goal_progress(goal.id, 2, 5)
        updated_goal = self.tracker.goals[goal.id]
        
        self.assertEqual(updated_goal.progress_current, 2)
        self.assertEqual(updated_goal.progress_total, 5)
        self.assertEqual(updated_goal.progress_percentage, 40.0)
        self.assertEqual(updated_goal.status, GoalStatus.IN_PROGRESS)
    
    def test_complete_goal(self):
        """Test completing a goal."""
        goal = self.test_goals[0]
        self.tracker.add_goal(goal)
        
        self.tracker.complete_goal(goal.id)
        completed_goal = self.tracker.goals[goal.id]
        
        self.assertEqual(completed_goal.status, GoalStatus.COMPLETED)
        self.assertEqual(completed_goal.progress_percentage, 100.0)
        self.assertIsNotNone(completed_goal.completed_date)
    
    def test_get_available_goals(self):
        """Test getting available goals."""
        # Add goals
        for goal in self.test_goals:
            self.tracker.add_goal(goal)
        
        available_goals = self.tracker.get_available_goals()
        
        # All goals should be available initially
        self.assertEqual(len(available_goals), len(self.test_goals))
        
        # Complete one goal
        self.tracker.complete_goal(self.test_goals[0].id)
        
        available_goals = self.tracker.get_available_goals()
        # Should have one less available goal
        self.assertEqual(len(available_goals), len(self.test_goals) - 1)
    
    def test_get_smart_suggestions(self):
        """Test smart suggestions."""
        # Add goals
        for goal in self.test_goals:
            self.tracker.add_goal(goal)
        
        # Test suggestions for different locations
        suggestions = self.tracker.get_smart_suggestions(("tatooine", "mos_eisley"))
        self.assertGreater(len(suggestions), 0)
        
        # Test suggestions without location
        suggestions = self.tracker.get_smart_suggestions()
        self.assertGreater(len(suggestions), 0)
    
    def test_goal_filtering(self):
        """Test goal filtering by various criteria."""
        # Add goals
        for goal in self.test_goals:
            self.tracker.add_goal(goal)
        
        # Filter by category
        quest_goals = self.tracker.get_goals_by_category(GoalCategory.MAIN_QUEST)
        self.assertEqual(len(quest_goals), 1)
        
        # Filter by status
        not_started_goals = self.tracker.get_goals_by_status(GoalStatus.NOT_STARTED)
        self.assertEqual(len(not_started_goals), len(self.test_goals))
        
        # Filter by priority
        high_priority_goals = self.tracker.get_goals_by_priority(GoalPriority.HIGH)
        self.assertEqual(len(high_priority_goals), 2)
    
    def test_goal_search(self):
        """Test goal search functionality."""
        # Add goals
        for goal in self.test_goals:
            self.tracker.add_goal(goal)
        
        # Search by title
        results = self.tracker.search_goals("Quest")
        self.assertEqual(len(results), 1)
        
        # Search by tag
        results = self.tracker.search_goals("test")
        self.assertEqual(len(results), 0)  # No tags in test goals
        
        # Search with no results
        results = self.tracker.search_goals("nonexistent")
        self.assertEqual(len(results), 0)
    
    def test_completion_scoring(self):
        """Test completion scoring system."""
        # Add goals
        for goal in self.test_goals:
            self.tracker.add_goal(goal)
        
        # Complete one goal
        self.tracker.complete_goal(self.test_goals[0].id)
        
        # Update completion scores
        self.tracker._update_completion_scores()
        
        scores = self.tracker.get_completion_scores()
        self.assertGreater(len(scores), 0)
        
        # Check that main_quest category has completion
        main_quest_score = scores.get("main_quest")
        if main_quest_score:
            self.assertEqual(main_quest_score.completed_goals, 1)
            self.assertEqual(main_quest_score.total_goals, 1)
            self.assertEqual(main_quest_score.completion_percentage, 100.0)
    
    def test_planet_completion(self):
        """Test planet-specific completion tracking."""
        # Add goals
        for goal in self.test_goals:
            self.tracker.add_goal(goal)
        
        # Complete a goal on Tatooine
        self.tracker.complete_goal(self.test_goals[0].id)
        
        # Check Tatooine completion
        tatooine_completion = self.tracker.get_planet_completion("tatooine")
        self.assertEqual(tatooine_completion['planet'], "tatooine")
        self.assertEqual(tatooine_completion['completed_goals'], 1)
        self.assertEqual(tatooine_completion['total_goals'], 1)
        self.assertEqual(tatooine_completion['completion_percentage'], 100.0)
    
    def test_goal_path(self):
        """Test goal path calculation."""
        # Create goals with prerequisites
        prereq_goal = SmartGoal(
            id="prereq_goal",
            title="Prerequisite Goal",
            goal_type=GoalType.QUEST,
            category=GoalCategory.MAIN_QUEST
        )
        
        dependent_goal = SmartGoal(
            id="dependent_goal",
            title="Dependent Goal",
            goal_type=GoalType.QUEST,
            category=GoalCategory.SIDE_QUEST,
            prerequisites=[
                GoalPrerequisite(
                    goal_id="prereq_goal",
                    goal_type=GoalType.QUEST,
                    description="Requires prerequisite"
                )
            ]
        )
        
        self.tracker.add_goal(prereq_goal)
        self.tracker.add_goal(dependent_goal)
        
        # Get path for dependent goal
        path = self.tracker.get_goal_path("dependent_goal")
        self.assertEqual(len(path), 2)  # Should include both goals
        self.assertEqual(path[0].id, "prereq_goal")
        self.assertEqual(path[1].id, "dependent_goal")
    
    def test_prerequisites_checking(self):
        """Test prerequisite checking logic."""
        # Create goals with prerequisites
        prereq_goal = SmartGoal(
            id="prereq_goal",
            title="Prerequisite Goal",
            goal_type=GoalType.QUEST,
            category=GoalCategory.MAIN_QUEST
        )
        
        dependent_goal = SmartGoal(
            id="dependent_goal",
            title="Dependent Goal",
            goal_type=GoalType.QUEST,
            category=GoalCategory.SIDE_QUEST,
            prerequisites=[
                GoalPrerequisite(
                    goal_id="prereq_goal",
                    goal_type=GoalType.QUEST,
                    description="Requires prerequisite"
                )
            ]
        )
        
        self.tracker.add_goal(prereq_goal)
        self.tracker.add_goal(dependent_goal)
        
        # Initially, dependent goal should not be available
        available_goals = self.tracker.get_available_goals()
        dependent_available = any(g.id == "dependent_goal" for g in available_goals)
        self.assertFalse(dependent_available)
        
        # Complete prerequisite
        self.tracker.complete_goal("prereq_goal")
        
        # Now dependent goal should be available
        available_goals = self.tracker.get_available_goals()
        dependent_available = any(g.id == "dependent_goal" for g in available_goals)
        self.assertTrue(dependent_available)
    
    def test_statistics_generation(self):
        """Test statistics generation."""
        # Add goals
        for goal in self.test_goals:
            self.tracker.add_goal(goal)
        
        # Complete one goal
        self.tracker.complete_goal(self.test_goals[0].id)
        
        stats = self.tracker.get_statistics()
        
        self.assertIn('total_goals', stats)
        self.assertIn('completed_goals', stats)
        self.assertIn('in_progress_goals', stats)
        self.assertIn('overall_completion_percentage', stats)
        self.assertIn('category_stats', stats)
        self.assertIn('priority_stats', stats)
        
        self.assertEqual(stats['total_goals'], len(self.test_goals))
        self.assertEqual(stats['completed_goals'], 1)
        self.assertEqual(stats['overall_completion_percentage'], 33.33333333333333)


class TestSmartSuggestions(unittest.TestCase):
    """Test smart suggestion functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_data_file = Path(self.test_dir) / "test_suggestions.json"
        self.tracker = SmartTodoTracker(str(self.test_data_file))
        
        # Create diverse test goals
        self.test_goals = [
            SmartGoal(
                id="quick_quest",
                title="Quick Quest",
                goal_type=GoalType.QUEST,
                category=GoalCategory.SIDE_QUEST,
                priority=GoalPriority.MEDIUM,
                location=GoalLocation(planet="tatooine", city="mos_eisley"),
                estimated_time=10,
                difficulty="easy"
            ),
            SmartGoal(
                id="long_quest",
                title="Long Quest",
                goal_type=GoalType.QUEST,
                category=GoalCategory.MAIN_QUEST,
                priority=GoalPriority.HIGH,
                location=GoalLocation(planet="naboo", city="theed"),
                estimated_time=60,
                difficulty="hard"
            ),
            SmartGoal(
                id="critical_quest",
                title="Critical Quest",
                goal_type=GoalType.QUEST,
                category=GoalCategory.MAIN_QUEST,
                priority=GoalPriority.CRITICAL,
                location=GoalLocation(planet="tatooine", city="mos_eisley"),
                estimated_time=30,
                difficulty="medium"
            )
        ]
        
        for goal in self.test_goals:
            self.tracker.add_goal(goal)
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_suggestion_priority_scoring(self):
        """Test suggestion priority scoring."""
        suggestions = self.tracker.get_smart_suggestions(("tatooine", "mos_eisley"))
        
        # Should have suggestions
        self.assertGreater(len(suggestions), 0)
        
        # Suggestions should be sorted by priority score
        for i in range(len(suggestions) - 1):
            self.assertGreaterEqual(suggestions[i].priority_score, suggestions[i + 1].priority_score)
    
    def test_location_convenience(self):
        """Test location convenience scoring."""
        # Test suggestions for Tatooine location
        tatooine_suggestions = self.tracker.get_smart_suggestions(("tatooine", "mos_eisley"))
        
        # Test suggestions for different location
        naboo_suggestions = self.tracker.get_smart_suggestions(("naboo", "theed"))
        
        # Should have different suggestions based on location
        self.assertNotEqual(len(tatooine_suggestions), len(naboo_suggestions))
    
    def test_suggestion_reasons(self):
        """Test suggestion reason generation."""
        suggestions = self.tracker.get_smart_suggestions(("tatooine", "mos_eisley"))
        
        for suggestion in suggestions:
            self.assertIsNotNone(suggestion.reason)
            self.assertIsInstance(suggestion.reason, str)
            self.assertGreater(len(suggestion.reason), 0)
    
    def test_suggestion_metadata(self):
        """Test suggestion metadata."""
        suggestions = self.tracker.get_smart_suggestions(("tatooine", "mos_eisley"))
        
        for suggestion in suggestions:
            self.assertIsNotNone(suggestion.goal_id)
            self.assertIsInstance(suggestion.priority_score, float)
            self.assertIsInstance(suggestion.prerequisites_met, bool)
            self.assertIsInstance(suggestion.location_convenient, bool)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_data_file = Path(self.test_dir) / "test_integration.json"
        self.tracker = SmartTodoTracker(str(self.test_data_file))
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_complete_workflow(self):
        """Test complete workflow from goal creation to completion."""
        # Create a goal
        goal = SmartGoal(
            id="workflow_test",
            title="Workflow Test Goal",
            goal_type=GoalType.QUEST,
            category=GoalCategory.MAIN_QUEST,
            priority=GoalPriority.HIGH,
            location=GoalLocation(planet="tatooine", city="mos_eisley"),
            estimated_time=30
        )
        
        # Add goal
        goal_id = add_goal(goal)
        self.assertEqual(goal_id, goal.id)
        
        # Check it's available
        available_goals = self.tracker.get_available_goals()
        self.assertIn(goal, available_goals)
        
        # Update progress
        update_goal_progress(goal.id, 2, 5)
        updated_goal = self.tracker.goals[goal.id]
        self.assertEqual(updated_goal.progress_percentage, 40.0)
        self.assertEqual(updated_goal.status, GoalStatus.IN_PROGRESS)
        
        # Complete goal
        complete_goal(goal.id)
        completed_goal = self.tracker.goals[goal.id]
        self.assertEqual(completed_goal.status, GoalStatus.COMPLETED)
        self.assertEqual(completed_goal.progress_percentage, 100.0)
        
        # Check statistics
        stats = get_statistics()
        self.assertEqual(stats['completed_goals'], 1)
        self.assertEqual(stats['overall_completion_percentage'], 100.0)
    
    def test_global_functions(self):
        """Test global convenience functions."""
        # Test get_smart_suggestions
        suggestions = get_smart_suggestions(("tatooine", "mos_eisley"))
        self.assertIsInstance(suggestions, list)
        
        # Test get_completion_scores
        scores = get_completion_scores()
        self.assertIsInstance(scores, dict)
        
        # Test get_statistics
        stats = get_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_goals', stats)
    
    def test_data_persistence(self):
        """Test data persistence across tracker instances."""
        # Create goal in first tracker
        goal = SmartGoal(
            id="persistence_test",
            title="Persistence Test Goal",
            goal_type=GoalType.QUEST,
            category=GoalCategory.MAIN_QUEST
        )
        
        self.tracker.add_goal(goal)
        
        # Create new tracker instance with same data file
        new_tracker = SmartTodoTracker(str(self.test_data_file))
        
        # Goal should be loaded
        self.assertIn(goal.id, new_tracker.goals)
        loaded_goal = new_tracker.goals[goal.id]
        self.assertEqual(loaded_goal.title, goal.title)
        self.assertEqual(loaded_goal.goal_type, goal.goal_type)


class TestPerformance(unittest.TestCase):
    """Performance tests for the system."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.mkdtemp()
        self.test_data_file = Path(self.test_dir) / "test_performance.json"
        self.tracker = SmartTodoTracker(str(self.test_data_file))
    
    def tearDown(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_large_goal_set(self):
        """Test performance with large number of goals."""
        import time
        
        # Create many goals
        start_time = time.time()
        
        for i in range(100):
            goal = SmartGoal(
                id=f"perf_test_{i:03d}",
                title=f"Performance Test Goal {i}",
                goal_type=GoalType.QUEST,
                category=GoalCategory.SIDE_QUEST,
                priority=GoalPriority.MEDIUM,
                location=GoalLocation(planet="tatooine", city="mos_eisley"),
                estimated_time=30
            )
            self.tracker.add_goal(goal)
        
        creation_time = time.time() - start_time
        
        # Test suggestion generation performance
        start_time = time.time()
        suggestions = self.tracker.get_smart_suggestions(("tatooine", "mos_eisley"))
        suggestion_time = time.time() - start_time
        
        # Test statistics generation performance
        start_time = time.time()
        stats = self.tracker.get_statistics()
        stats_time = time.time() - start_time
        
        # Performance assertions
        self.assertLess(creation_time, 5.0)  # Should create 100 goals in under 5 seconds
        self.assertLess(suggestion_time, 1.0)  # Should generate suggestions in under 1 second
        self.assertLess(stats_time, 1.0)  # Should generate stats in under 1 second
        
        self.assertEqual(len(self.tracker.goals), 100)
        self.assertGreater(len(suggestions), 0)
    
    def test_completion_scoring_performance(self):
        """Test completion scoring performance."""
        import time
        
        # Create goals in different categories
        categories = [GoalCategory.MAIN_QUEST, GoalCategory.SIDE_QUEST, GoalCategory.COLLECTION_ITEM]
        
        for i, category in enumerate(categories):
            for j in range(10):
                goal = SmartGoal(
                    id=f"scoring_test_{i}_{j}",
                    title=f"Scoring Test Goal {i}_{j}",
                    goal_type=GoalType.QUEST,
                    category=category,
                    priority=GoalPriority.MEDIUM
                )
                self.tracker.add_goal(goal)
        
        # Complete some goals
        goals = list(self.tracker.goals.values())
        for i in range(0, len(goals), 3):  # Complete every third goal
            self.tracker.complete_goal(goals[i].id)
        
        # Test completion scoring performance
        start_time = time.time()
        self.tracker._update_completion_scores()
        scoring_time = time.time() - start_time
        
        self.assertLess(scoring_time, 1.0)  # Should update scores in under 1 second
        
        scores = self.tracker.get_completion_scores()
        self.assertGreater(len(scores), 0)


def run_tests():
    """Run all tests and generate a test report."""
    print("🧪 Running Batch 048 - Smart Todo Tracker Tests")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    test_classes = [
        TestSmartGoal,
        TestSmartTodoTracker,
        TestSmartSuggestions,
        TestIntegration,
        TestPerformance
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Generate test report
    report = {
        "test_info": {
            "name": "Batch 048 - Smart Todo Tracker Tests",
            "timestamp": datetime.now().isoformat(),
            "total_tests": result.testsRun,
            "failures": len(result.failures),
            "errors": len(result.errors),
            "success_rate": ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
        },
        "test_results": {
            "passed": result.testsRun - len(result.failures) - len(result.errors),
            "failed": len(result.failures),
            "errors": len(result.errors)
        },
        "failure_details": [
            {
                "test": str(failure[0]),
                "error": failure[1]
            }
            for failure in result.failures
        ],
        "error_details": [
            {
                "test": str(error[0]),
                "error": error[1]
            }
            for error in result.errors
        ]
    }
    
    # Save test report
    report_file = f"test_batch_048_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📋 Test report saved to: {report_file}")
    print(f"✅ Tests passed: {report['test_results']['passed']}")
    print(f"❌ Tests failed: {report['test_results']['failed']}")
    print(f"⚠️  Tests with errors: {report['test_results']['errors']}")
    print(f"📊 Success rate: {report['test_info']['success_rate']:.1f}%")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1) 