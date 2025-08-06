"""
Simple test for the task planner module.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.planner import (
    Task, TaskType, TaskStatus, TaskPriority, TaskRequirement, TaskResult,
    get_task_planner, add_task, get_next_task, complete_task
)

def test_basic_functionality():
    """Test basic task planner functionality."""
    print("Testing basic task planner functionality...")
    
    # Create a simple task
    task = Task(
        id="test_task_001",
        type=TaskType.QUEST,
        title="Test Quest",
        description="A simple test quest",
        priority=TaskPriority.HIGH
    )
    
    # Add task to planner
    task_id = add_task(task)
    print(f"Added task: {task_id}")
    
    # Get next task
    next_task = get_next_task()
    if next_task:
        print(f"Next task: {next_task.title}")
        
        # Complete the task
        result = TaskResult(
            success=True,
            duration=60,
            xp_gained=100,
            credits_gained=200
        )
        
        success = complete_task(task_id, result)
        print(f"Task completed: {success}")
    else:
        print("No tasks available")
    
    # Get summary
    from core.planner import get_task_summary
    summary = get_task_summary()
    print(f"Summary: {summary['active_tasks']} active, {summary['completed_tasks']} completed")

if __name__ == "__main__":
    test_basic_functionality() 