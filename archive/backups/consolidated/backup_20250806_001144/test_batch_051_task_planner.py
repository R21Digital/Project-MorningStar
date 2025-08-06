"""
Test Suite for Batch 051 - Lightweight AI Task Planner (BabyAGI-Inspired)

This test suite validates the task planner's functionality including:
- Task creation and management
- Priority queue ordering
- Task execution lifecycle
- Session integration
- Performance tracking
- Error handling
"""

import json
import logging
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import patch, MagicMock

from core.planner import (
    Task, TaskType, TaskStatus, TaskPriority, TaskRequirement, TaskResult,
    TaskPlanner, get_task_planner, add_task, get_next_task, complete_task,
    replan, set_session, get_task_summary
)


class TestTaskDataStructures(unittest.TestCase):
    """Test the data structures used by the task planner."""
    
    def test_task_creation(self):
        """Test creating a basic task."""
        task = Task(
            id="test_task_001",
            type=TaskType.QUEST,
            title="Test Quest",
            description="A test quest task",
            priority=TaskPriority.HIGH
        )
        
        self.assertEqual(task.id, "test_task_001")
        self.assertEqual(task.type, TaskType.QUEST)
        self.assertEqual(task.title, "Test Quest")
        self.assertEqual(task.priority, TaskPriority.HIGH)
        self.assertEqual(task.status, TaskStatus.PENDING)
    
    def test_task_serialization(self):
        """Test task serialization to/from dictionary."""
        task = Task(
            id="serialization_test",
            type=TaskType.COMBAT,
            title="Combat Test",
            description="Test combat task",
            priority=TaskPriority.MEDIUM,
            location="Test Location",
            estimated_duration=10,
            requirements=[
                TaskRequirement(
                    type="level",
                    value=5,
                    description="Level 5 required",
                    current_value=3,
                    satisfied=False
                )
            ]
        )
        
        # Serialize
        task_dict = task.to_dict()
        
        # Deserialize
        reconstructed_task = Task.from_dict(task_dict)
        
        # Verify
        self.assertEqual(reconstructed_task.id, task.id)
        self.assertEqual(reconstructed_task.type, task.type)
        self.assertEqual(reconstructed_task.title, task.title)
        self.assertEqual(reconstructed_task.priority, task.priority)
        self.assertEqual(reconstructed_task.location, task.location)
        self.assertEqual(len(reconstructed_task.requirements), len(task.requirements))
    
    def test_task_result_creation(self):
        """Test creating task results."""
        result = TaskResult(
            success=True,
            duration=300.5,
            xp_gained=500,
            credits_gained=1000,
            items_gained=["Item1", "Item2"],
            notes="Test completion"
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.duration, 300.5)
        self.assertEqual(result.xp_gained, 500)
        self.assertEqual(result.credits_gained, 1000)
        self.assertEqual(len(result.items_gained), 2)
        self.assertEqual(result.notes, "Test completion")


class TestTaskPlanner(unittest.TestCase):
    """Test the main TaskPlanner class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary data file
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = Path(self.temp_dir) / "test_task_planner.json"
        
        # Create planner instance
        self.planner = TaskPlanner(str(self.data_file))
    
    def tearDown(self):
        """Clean up test environment."""
        # Remove temporary files
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_planner_initialization(self):
        """Test planner initialization."""
        self.assertIsNotNone(self.planner)
        self.assertEqual(len(self.planner.tasks), 0)
        self.assertEqual(len(self.planner.completed_tasks), 0)
        self.assertTrue(self.planner.task_queue.empty())
    
    def test_add_task(self):
        """Test adding tasks to the planner."""
        task = Task(
            id="test_add_001",
            type=TaskType.QUEST,
            title="Test Add Task",
            description="Testing task addition",
            priority=TaskPriority.HIGH
        )
        
        task_id = self.planner.add_task(task)
        
        self.assertEqual(task_id, "test_add_001")
        self.assertIn("test_add_001", self.planner.tasks)
        self.assertEqual(len(self.planner.tasks), 1)
    
    def test_add_duplicate_task(self):
        """Test adding a duplicate task raises error."""
        task = Task(
            id="duplicate_test",
            type=TaskType.QUEST,
            title="Duplicate Test",
            description="Testing duplicate handling",
            priority=TaskPriority.MEDIUM
        )
        
        # Add first time
        self.planner.add_task(task)
        
        # Try to add again
        with self.assertRaises(ValueError):
            self.planner.add_task(task)
    
    def test_get_next_task_priority_order(self):
        """Test that tasks are returned in priority order."""
        # Create tasks with different priorities
        critical_task = Task(
            id="critical_001",
            type=TaskType.HEALING,
            title="Critical Task",
            description="Critical priority task",
            priority=TaskPriority.CRITICAL
        )
        
        high_task = Task(
            id="high_001",
            type=TaskType.QUEST,
            title="High Task",
            description="High priority task",
            priority=TaskPriority.HIGH
        )
        
        medium_task = Task(
            id="medium_001",
            type=TaskType.COMBAT,
            title="Medium Task",
            description="Medium priority task",
            priority=TaskPriority.MEDIUM
        )
        
        # Add tasks in reverse priority order
        self.planner.add_task(medium_task)
        self.planner.add_task(high_task)
        self.planner.add_task(critical_task)
        
        # Get next task (should be critical)
        next_task = self.planner.get_next_task()
        self.assertEqual(next_task.priority, TaskPriority.CRITICAL)
        self.assertEqual(next_task.id, "critical_001")
    
    def test_task_dependencies(self):
        """Test task dependency handling."""
        # Create dependent task
        dependent_task = Task(
            id="dependent_001",
            type=TaskType.QUEST,
            title="Dependent Task",
            description="Task with dependencies",
            priority=TaskPriority.HIGH,
            dependencies=["prerequisite_001"]
        )
        
        # Create prerequisite task
        prerequisite_task = Task(
            id="prerequisite_001",
            type=TaskType.TRAVEL,
            title="Prerequisite Task",
            description="Task that must be completed first",
            priority=TaskPriority.HIGH
        )
        
        # Add tasks
        self.planner.add_task(dependent_task)
        self.planner.add_task(prerequisite_task)
        
        # Get next task (should be prerequisite, not dependent)
        next_task = self.planner.get_next_task()
        self.assertEqual(next_task.id, "prerequisite_001")
        
        # Complete prerequisite
        result = TaskResult(success=True, duration=60)
        self.planner.complete_task("prerequisite_001", result)
        
        # Now dependent task should be available
        next_task = self.planner.get_next_task()
        self.assertEqual(next_task.id, "dependent_001")
    
    def test_task_lifecycle(self):
        """Test complete task lifecycle."""
        task = Task(
            id="lifecycle_test",
            type=TaskType.QUEST,
            title="Lifecycle Test",
            description="Testing task lifecycle",
            priority=TaskPriority.MEDIUM
        )
        
        # Add task
        self.planner.add_task(task)
        
        # Start task
        self.assertTrue(self.planner.start_task("lifecycle_test"))
        self.assertEqual(self.planner.tasks["lifecycle_test"].status, TaskStatus.IN_PROGRESS)
        self.assertIsNotNone(self.planner.tasks["lifecycle_test"].started_at)
        
        # Complete task
        result = TaskResult(
            success=True,
            duration=120,
            xp_gained=200,
            credits_gained=500
        )
        
        self.assertTrue(self.planner.complete_task("lifecycle_test", result))
        
        # Verify task moved to completed
        self.assertNotIn("lifecycle_test", self.planner.tasks)
        self.assertIn("lifecycle_test", self.planner.completed_tasks)
        
        completed_task = self.planner.completed_tasks["lifecycle_test"]
        self.assertEqual(completed_task.status, TaskStatus.COMPLETED)
        self.assertIsNotNone(completed_task.completed_at)
        self.assertEqual(completed_task.result.xp_gained, 200)
    
    def test_task_failure(self):
        """Test task failure handling."""
        task = Task(
            id="failure_test",
            type=TaskType.COMBAT,
            title="Failure Test",
            description="Testing task failure",
            priority=TaskPriority.MEDIUM
        )
        
        self.planner.add_task(task)
        self.planner.start_task("failure_test")
        
        # Fail the task
        self.assertTrue(self.planner.fail_task("failure_test", "Combat failure"))
        
        failed_task = self.planner.completed_tasks["failure_test"]
        self.assertEqual(failed_task.status, TaskStatus.FAILED)
        self.assertFalse(failed_task.result.success)
        self.assertIn("Combat failure", failed_task.result.errors)
    
    def test_performance_tracking(self):
        """Test performance metrics tracking."""
        # Create and complete several tasks
        task_types = [TaskType.QUEST, TaskType.COMBAT, TaskType.TRAVEL]
        
        for i, task_type in enumerate(task_types):
            task = Task(
                id=f"perf_test_{i}",
                type=task_type,
                title=f"Performance Test {i}",
                description=f"Testing performance tracking for {task_type.value}",
                priority=TaskPriority.MEDIUM
            )
            
            self.planner.add_task(task)
            self.planner.start_task(task.id)
            
            result = TaskResult(
                success=True,
                duration=(i + 1) * 60,
                xp_gained=(i + 1) * 100,
                credits_gained=(i + 1) * 200
            )
            
            self.planner.complete_task(task.id, result)
        
        # Check performance metrics
        metrics = self.planner.performance_metrics
        
        for task_type in task_types:
            self.assertIn(task_type.value, metrics)
            task_metrics = metrics[task_type.value]
            self.assertEqual(task_metrics['total_tasks'], 1)
            self.assertEqual(task_metrics['successful_tasks'], 1)
            self.assertEqual(task_metrics['success_rate'], 1.0)
    
    def test_session_integration(self):
        """Test session integration."""
        session_id = "test_session_001"
        goals = ["goal_1", "goal_2", "goal_3"]
        
        self.planner.set_session(session_id, goals)
        
        self.assertEqual(self.planner.current_session_id, session_id)
        self.assertEqual(self.planner.session_goals, goals)
    
    def test_replanning(self):
        """Test task replanning."""
        # Set up session
        self.planner.set_session("replan_test", ["goal_1", "goal_2"])
        
        # Add some existing tasks
        existing_task = Task(
            id="existing_001",
            type=TaskType.QUEST,
            title="Existing Task",
            description="Task that should remain after replanning",
            priority=TaskPriority.HIGH
        )
        self.planner.add_task(existing_task)
        
        # Replan
        new_tasks = self.planner.replan(
            current_location="Test Location",
            current_goals=["goal_1", "goal_2"]
        )
        
        # Should have generated new tasks from goals
        self.assertGreater(len(new_tasks), 0)
        
        # Existing task should still be there
        self.assertIn("existing_001", self.planner.tasks)


class TestGlobalFunctions(unittest.TestCase):
    """Test the global convenience functions."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary data file
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = Path(self.temp_dir) / "test_global_planner.json"
        
        # Patch the global planner to use our test file
        with patch('core.planner._planner_instance', None):
            with patch('core.planner.TaskPlanner') as mock_planner_class:
                mock_planner = MagicMock()
                mock_planner_class.return_value = mock_planner
                self.mock_planner = mock_planner
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_get_task_planner(self):
        """Test getting the global planner instance."""
        with patch('core.planner._planner_instance', None):
            planner = get_task_planner()
            self.assertIsNotNone(planner)
    
    def test_add_task_global(self):
        """Test global add_task function."""
        task = Task(
            id="global_test",
            type=TaskType.QUEST,
            title="Global Test",
            description="Testing global function",
            priority=TaskPriority.MEDIUM
        )
        
        self.mock_planner.add_task.return_value = "global_test"
        
        task_id = add_task(task)
        
        self.assertEqual(task_id, "global_test")
        self.mock_planner.add_task.assert_called_once_with(task)
    
    def test_get_next_task_global(self):
        """Test global get_next_task function."""
        mock_task = MagicMock()
        self.mock_planner.get_next_task.return_value = mock_task
        
        result = get_next_task()
        
        self.assertEqual(result, mock_task)
        self.mock_planner.get_next_task.assert_called_once()
    
    def test_complete_task_global(self):
        """Test global complete_task function."""
        result = TaskResult(success=True, duration=60)
        self.mock_planner.complete_task.return_value = True
        
        success = complete_task("test_task", result)
        
        self.assertTrue(success)
        self.mock_planner.complete_task.assert_called_once_with("test_task", result)
    
    def test_replan_global(self):
        """Test global replan function."""
        mock_tasks = [MagicMock(), MagicMock()]
        self.mock_planner.replan.return_value = mock_tasks
        
        result = replan(current_location="Test Location", current_goals=["goal1"])
        
        self.assertEqual(result, mock_tasks)
        self.mock_planner.replan.assert_called_once_with(
            current_location="Test Location",
            current_goals=["goal1"]
        )
    
    def test_set_session_global(self):
        """Test global set_session function."""
        set_session("test_session", ["goal1", "goal2"])
        
        self.mock_planner.set_session.assert_called_once_with("test_session", ["goal1", "goal2"])
    
    def test_get_task_summary_global(self):
        """Test global get_task_summary function."""
        mock_summary = {"active_tasks": 5, "completed_tasks": 10}
        self.mock_planner.get_task_summary.return_value = mock_summary
        
        result = get_task_summary()
        
        self.assertEqual(result, mock_summary)
        self.mock_planner.get_task_summary.assert_called_once()


class TestTaskRequirements(unittest.TestCase):
    """Test task requirements and validation."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = Path(self.temp_dir) / "test_requirements.json"
        self.planner = TaskPlanner(str(self.data_file))
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_task_requirements_validation(self):
        """Test task requirements validation."""
        task = Task(
            id="requirements_test",
            type=TaskType.QUEST,
            title="Requirements Test",
            description="Testing task requirements",
            priority=TaskPriority.HIGH,
            requirements=[
                TaskRequirement(
                    type="level",
                    value=10,
                    description="Level 10 required",
                    current_value=8,
                    satisfied=False
                ),
                TaskRequirement(
                    type="location",
                    value="Naboo",
                    description="Must be on Naboo",
                    current_value="Naboo",
                    satisfied=True
                )
            ]
        )
        
        # Add task (should not raise error)
        self.planner.add_task(task)
        
        # Verify requirements are stored
        stored_task = self.planner.tasks["requirements_test"]
        self.assertEqual(len(stored_task.requirements), 2)
        self.assertFalse(stored_task.requirements[0].satisfied)
        self.assertTrue(stored_task.requirements[1].satisfied)
    
    def test_requirement_update(self):
        """Test updating task requirements based on current state."""
        task = Task(
            id="update_test",
            type=TaskType.QUEST,
            title="Update Test",
            description="Testing requirement updates",
            priority=TaskPriority.MEDIUM,
            requirements=[
                TaskRequirement(
                    type="location",
                    value="Naboo",
                    description="Must be on Naboo",
                    current_value=None,
                    satisfied=False
                )
            ]
        )
        
        self.planner.add_task(task)
        
        # Update requirements based on current location
        self.planner._update_task_requirements(task, "Naboo")
        
        # Verify requirement was updated
        self.assertEqual(task.requirements[0].current_value, "Naboo")
        self.assertTrue(task.requirements[0].satisfied)


class TestDataPersistence(unittest.TestCase):
    """Test data persistence and loading."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = Path(self.temp_dir) / "test_persistence.json"
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_save_and_load_data(self):
        """Test saving and loading planner data."""
        # Create planner and add tasks
        planner1 = TaskPlanner(str(self.data_file))
        
        task = Task(
            id="persistence_test",
            type=TaskType.QUEST,
            title="Persistence Test",
            description="Testing data persistence",
            priority=TaskPriority.MEDIUM
        )
        
        planner1.add_task(task)
        
        # Complete the task
        result = TaskResult(success=True, duration=60)
        planner1.complete_task("persistence_test", result)
        
        # Create new planner instance (should load data)
        planner2 = TaskPlanner(str(self.data_file))
        
        # Verify data was loaded
        self.assertEqual(len(planner2.tasks), 0)  # No active tasks
        self.assertEqual(len(planner2.completed_tasks), 1)  # One completed task
        self.assertIn("persistence_test", planner2.completed_tasks)
    
    def test_corrupted_data_handling(self):
        """Test handling of corrupted data files."""
        # Create corrupted data file
        with open(self.data_file, 'w') as f:
            f.write("invalid json content")
        
        # Should not raise exception, should create new planner
        planner = TaskPlanner(str(self.data_file))
        self.assertIsNotNone(planner)
        self.assertEqual(len(planner.tasks), 0)


class TestIntegration(unittest.TestCase):
    """Integration tests for the task planner."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = Path(self.temp_dir) / "test_integration.json"
        self.planner = TaskPlanner(str(self.data_file))
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complex_workflow(self):
        """Test a complex workflow with multiple tasks and dependencies."""
        # Set up session
        self.planner.set_session("complex_test", ["main_quest", "side_quest"])
        
        # Create complex task hierarchy
        tasks = [
            Task(
                id="heal_emergency",
                type=TaskType.HEALING,
                title="Emergency Healing",
                description="Heal character",
                priority=TaskPriority.CRITICAL
            ),
            Task(
                id="travel_to_quest",
                type=TaskType.TRAVEL,
                title="Travel to Quest Location",
                description="Travel to quest location",
                priority=TaskPriority.HIGH,
                dependencies=["heal_emergency"]
            ),
            Task(
                id="complete_quest",
                type=TaskType.QUEST,
                title="Complete Main Quest",
                description="Complete the main quest",
                priority=TaskPriority.HIGH,
                dependencies=["travel_to_quest"]
            ),
            Task(
                id="train_skills",
                type=TaskType.TRAINING,
                title="Train Skills",
                description="Train character skills",
                priority=TaskPriority.MEDIUM,
                dependencies=["complete_quest"]
            )
        ]
        
        # Add all tasks
        for task in tasks:
            self.planner.add_task(task)
        
        # Execute workflow
        execution_order = []
        
        while len(execution_order) < len(tasks):
            next_task = self.planner.get_next_task()
            if not next_task:
                break
            
            execution_order.append(next_task.id)
            
            # Start and complete task
            self.planner.start_task(next_task.id)
            result = TaskResult(success=True, duration=60)
            self.planner.complete_task(next_task.id, result)
        
        # Verify execution order (should follow dependencies)
        expected_order = ["heal_emergency", "travel_to_quest", "complete_quest", "train_skills"]
        self.assertEqual(execution_order, expected_order)
        
        # Verify all tasks completed
        self.assertEqual(len(self.planner.completed_tasks), len(tasks))
        self.assertEqual(len(self.planner.tasks), 0)
    
    def test_performance_metrics_integration(self):
        """Test performance metrics integration with task execution."""
        # Execute various task types
        task_types = [TaskType.QUEST, TaskType.COMBAT, TaskType.TRAVEL, TaskType.TRAINING]
        
        for task_type in task_types:
            task = Task(
                id=f"perf_integration_{task_type.value}",
                type=task_type,
                title=f"Performance Integration {task_type.value}",
                description=f"Testing performance integration for {task_type.value}",
                priority=TaskPriority.MEDIUM
            )
            
            self.planner.add_task(task)
            
            # Execute task
            next_task = self.planner.get_next_task()
            self.planner.start_task(next_task.id)
            
            result = TaskResult(
                success=True,
                duration=120,
                xp_gained=200,
                credits_gained=500
            )
            
            self.planner.complete_task(next_task.id, result)
        
        # Verify performance metrics
        summary = self.planner.get_task_summary()
        metrics = summary['performance_metrics']
        
        for task_type in task_types:
            self.assertIn(task_type.value, metrics)
            task_metrics = metrics[task_type.value]
            self.assertEqual(task_metrics['total_tasks'], 1)
            self.assertEqual(task_metrics['successful_tasks'], 1)
            self.assertEqual(task_metrics['success_rate'], 1.0)
            self.assertEqual(task_metrics['total_xp_gained'], 200)
            self.assertEqual(task_metrics['total_credits_gained'], 500)


def run_tests():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestTaskDataStructures,
        TestTaskPlanner,
        TestGlobalFunctions,
        TestTaskRequirements,
        TestDataPersistence,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1) 