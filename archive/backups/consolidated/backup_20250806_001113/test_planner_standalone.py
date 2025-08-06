"""
Standalone test for the task planner module.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import directly from the planner module
import core.planner as planner_module

def test_basic_functionality():
    """Test basic task planner functionality."""
    print("Testing basic task planner functionality...")
    
    # Create a simple task
    task = planner_module.Task(
        id="test_task_001",
        type=planner_module.TaskType.QUEST,
        title="Test Quest",
        description="A simple test quest",
        priority=planner_module.TaskPriority.HIGH
    )
    
    # Get planner instance
    planner = planner_module.get_task_planner()
    
    # Add task to planner
    task_id = planner.add_task(task)
    print(f"Added task: {task_id}")
    
    # Get next task
    next_task = planner.get_next_task()
    if next_task:
        print(f"Next task: {next_task.title}")
        
        # Complete the task
        result = planner_module.TaskResult(
            success=True,
            duration=60,
            xp_gained=100,
            credits_gained=200
        )
        
        success = planner.complete_task(task_id, result)
        print(f"Task completed: {success}")
    else:
        print("No tasks available")
    
    # Get summary
    summary = planner.get_task_summary()
    print(f"Summary: {summary['active_tasks']} active, {summary['completed_tasks']} completed")

if __name__ == "__main__":
    test_basic_functionality() 