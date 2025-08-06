"""
Minimal test for the task planner module.
"""

import json
import tempfile
import unittest
from pathlib import Path
from datetime import datetime

# Import the planner module directly
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock the problematic imports
import unittest.mock as mock

# Mock the session_memory and todo_tracker imports
with mock.patch.dict('sys.modules', {
    'core.session_memory.memory_template': mock.MagicMock(),
    'core.todo_tracker': mock.MagicMock()
}):
    from core.planner import (
        Task, TaskType, TaskStatus, TaskPriority, TaskRequirement, TaskResult,
        TaskPlanner
    )

class TestTaskPlannerMinimal(unittest.TestCase):
    """Minimal test for task planner functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.data_file = Path(self.temp_dir) / "test_planner.json"
        self.planner = TaskPlanner(str(self.data_file))
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_task_creation(self):
        """Test creating a basic task."""
        task = Task(
            id="test_task_001",
            type=TaskType.QUEST,
            title="Test Quest",
            description="A test quest",
            priority=TaskPriority.HIGH
        )
        
        self.assertEqual(task.id, "test_task_001")
        self.assertEqual(task.type, TaskType.QUEST)
        self.assertEqual(task.title, "Test Quest")
        self.assertEqual(task.priority, TaskPriority.HIGH)
        self.assertEqual(task.status, TaskStatus.PENDING)
    
    def test_add_task(self):
        """Test adding a task to the planner."""
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
    
    def test_get_next_task(self):
        """Test getting the next task."""
        task = Task(
            id="test_next_001",
            type=TaskType.QUEST,
            title="Test Next Task",
            description="Testing next task retrieval",
            priority=TaskPriority.HIGH
        )
        
        self.planner.add_task(task)
        next_task = self.planner.get_next_task()
        
        self.assertIsNotNone(next_task)
        self.assertEqual(next_task.id, "test_next_001")
    
    def test_complete_task(self):
        """Test completing a task."""
        task = Task(
            id="test_complete_001",
            type=TaskType.QUEST,
            title="Test Complete Task",
            description="Testing task completion",
            priority=TaskPriority.HIGH
        )
        
        self.planner.add_task(task)
        
        result = TaskResult(
            success=True,
            duration=60,
            xp_gained=100,
            credits_gained=200
        )
        
        success = self.planner.complete_task("test_complete_001", result)
        
        self.assertTrue(success)
        self.assertNotIn("test_complete_001", self.planner.tasks)
        self.assertIn("test_complete_001", self.planner.completed_tasks)
    
    def test_priority_ordering(self):
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
        
        # Add tasks in reverse priority order
        self.planner.add_task(high_task)
        self.planner.add_task(critical_task)
        
        # Get next task (should be critical)
        next_task = self.planner.get_next_task()
        self.assertEqual(next_task.priority, TaskPriority.CRITICAL)
        self.assertEqual(next_task.id, "critical_001")

def run_minimal_tests():
    """Run the minimal tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    tests = unittest.TestLoader().loadTestsFromTestCase(TestTaskPlannerMinimal)
    test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    print(f"\n{'='*60}")
    print("MINIMAL TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_minimal_tests()
    exit(0 if success else 1) 