"""
Demo for Batch 051 - Lightweight AI Task Planner (BabyAGI-Inspired)

This demo showcases the task planner's capabilities including:
- Adding tasks with different priorities
- Task queue management
- Task completion and result tracking
- Session integration
- Replanning based on goals
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

from core.planner import (
    Task, TaskType, TaskStatus, TaskPriority, TaskRequirement, TaskResult,
    get_task_planner, add_task, get_next_task, complete_task, replan,
    set_session, get_task_summary
)


def setup_logging():
    """Setup logging for the demo."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('demo_batch_051_task_planner.log'),
            logging.StreamHandler()
        ]
    )


def create_sample_tasks() -> List[Task]:
    """Create sample tasks for demonstration."""
    tasks = []
    
    # Emergency task (healing)
    healing_task = Task(
        id="heal_001",
        type=TaskType.HEALING,
        title="Emergency Healing",
        description="Heal character due to low health",
        priority=TaskPriority.CRITICAL,
        location="current_location",
        estimated_duration=2,
        executor="healing_system"
    )
    tasks.append(healing_task)
    
    # High priority quest
    quest_task = Task(
        id="quest_main_001",
        type=TaskType.QUEST,
        title="Complete Main Quest: The Beginning",
        description="Complete the main storyline quest",
        priority=TaskPriority.HIGH,
        location="Naboo",
        estimated_duration=30,
        executor="quest_system",
        parameters={"quest_id": "main_001", "npc_name": "Quest Giver"}
    )
    tasks.append(quest_task)
    
    # Travel task
    travel_task = Task(
        id="travel_naboo_001",
        type=TaskType.TRAVEL,
        title="Travel to Naboo",
        description="Travel to Naboo for quest completion",
        priority=TaskPriority.HIGH,
        location="Naboo",
        estimated_duration=5,
        executor="travel_system",
        dependencies=["heal_001"]  # Must heal first
    )
    tasks.append(travel_task)
    
    # Combat task
    combat_task = Task(
        id="combat_bounty_001",
        type=TaskType.COMBAT,
        title="Defeat Bounty Target",
        description="Defeat the bounty target for credits",
        priority=TaskPriority.MEDIUM,
        location="Naboo",
        estimated_duration=15,
        executor="combat_system",
        parameters={"target_name": "Bounty Target", "bounty_amount": 5000}
    )
    tasks.append(combat_task)
    
    # Training task
    training_task = Task(
        id="training_skill_001",
        type=TaskType.TRAINING,
        title="Train Combat Skills",
        description="Train combat skills at the trainer",
        priority=TaskPriority.MEDIUM,
        location="Naboo",
        estimated_duration=10,
        executor="training_system",
        parameters={"skill_name": "Combat", "target_level": 5}
    )
    tasks.append(training_task)
    
    # Collection task
    collection_task = Task(
        id="collection_item_001",
        type=TaskType.COLLECTION,
        title="Collect Rare Items",
        description="Collect rare items for collection",
        priority=TaskPriority.LOW,
        location="Naboo",
        estimated_duration=20,
        executor="collection_system",
        parameters={"item_name": "Rare Crystal", "quantity": 5}
    )
    tasks.append(collection_task)
    
    # Background maintenance task
    maintenance_task = Task(
        id="maintenance_inventory_001",
        type=TaskType.MAINTENANCE,
        title="Organize Inventory",
        description="Organize and clean up inventory",
        priority=TaskPriority.BACKGROUND,
        location="current_location",
        estimated_duration=5,
        executor="inventory_system"
    )
    tasks.append(maintenance_task)
    
    return tasks


def simulate_task_execution(task: Task) -> TaskResult:
    """Simulate task execution and return results."""
    print(f"  Executing task: {task.title}")
    
    # Simulate execution time
    execution_time = task.estimated_duration or 5
    time.sleep(0.1)  # Simulate some processing time
    
    # Generate realistic results based on task type
    if task.type == TaskType.HEALING:
        return TaskResult(
            success=True,
            duration=execution_time * 60,
            xp_gained=0,
            credits_gained=0,
            items_gained=[],
            notes="Character fully healed"
        )
    elif task.type == TaskType.QUEST:
        return TaskResult(
            success=True,
            duration=execution_time * 60,
            xp_gained=500,
            credits_gained=1000,
            items_gained=["Quest Reward Item"],
            notes="Quest completed successfully"
        )
    elif task.type == TaskType.TRAVEL:
        return TaskResult(
            success=True,
            duration=execution_time * 60,
            xp_gained=50,
            credits_gained=100,
            items_gained=[],
            notes="Successfully traveled to destination"
        )
    elif task.type == TaskType.COMBAT:
        return TaskResult(
            success=True,
            duration=execution_time * 60,
            xp_gained=300,
            credits_gained=5000,
            items_gained=["Bounty Reward", "Combat Loot"],
            notes="Bounty target defeated"
        )
    elif task.type == TaskType.TRAINING:
        return TaskResult(
            success=True,
            duration=execution_time * 60,
            xp_gained=200,
            credits_gained=500,
            items_gained=[],
            notes="Skills trained successfully"
        )
    elif task.type == TaskType.COLLECTION:
        return TaskResult(
            success=True,
            duration=execution_time * 60,
            xp_gained=100,
            credits_gained=200,
            items_gained=["Rare Crystal", "Rare Crystal", "Rare Crystal"],
            notes="Collection items gathered"
        )
    elif task.type == TaskType.MAINTENANCE:
        return TaskResult(
            success=True,
            duration=execution_time * 60,
            xp_gained=0,
            credits_gained=0,
            items_gained=[],
            notes="Inventory organized"
        )
    else:
        return TaskResult(
            success=True,
            duration=execution_time * 60,
            xp_gained=50,
            credits_gained=100,
            items_gained=[],
            notes="Task completed"
        )


def demo_basic_task_management():
    """Demo basic task management functionality."""
    print("\n" + "="*60)
    print("DEMO: Basic Task Management")
    print("="*60)
    
    # Get planner instance
    planner = get_task_planner()
    
    # Create sample tasks
    tasks = create_sample_tasks()
    
    # Add tasks to planner
    print("Adding tasks to planner...")
    for task in tasks:
        task_id = add_task(task)
        print(f"  Added task: {task.title} (ID: {task_id})")
    
    # Show initial summary
    summary = get_task_summary()
    print(f"\nInitial task summary:")
    print(f"  Active tasks: {summary['active_tasks']}")
    print(f"  Queue size: {summary['queue_size']}")
    print(f"  Task types: {summary['task_types']}")
    print(f"  Task priorities: {summary['task_priorities']}")


def demo_task_execution():
    """Demo task execution and completion."""
    print("\n" + "="*60)
    print("DEMO: Task Execution")
    print("="*60)
    
    planner = get_task_planner()
    
    # Execute tasks in priority order
    print("Executing tasks in priority order...")
    completed_count = 0
    
    while completed_count < 5:  # Execute 5 tasks for demo
        next_task = get_next_task()
        if not next_task:
            print("  No more tasks in queue")
            break
        
        print(f"\n  Next task: {next_task.title}")
        print(f"    Type: {next_task.type.value}")
        print(f"    Priority: {next_task.priority.name}")
        print(f"    Location: {next_task.location}")
        
        # Start the task
        if planner.start_task(next_task.id):
            print(f"    Started task: {next_task.id}")
            
            # Simulate execution
            result = simulate_task_execution(next_task)
            
            # Complete the task
            if complete_task(next_task.id, result):
                print(f"    Completed task: {next_task.id}")
                print(f"    Success: {result.success}")
                print(f"    XP gained: {result.xp_gained}")
                print(f"    Credits gained: {result.credits_gained}")
                print(f"    Items gained: {result.items_gained}")
                completed_count += 1
            else:
                print(f"    Failed to complete task: {next_task.id}")
        else:
            print(f"    Failed to start task: {next_task.id}")
    
    # Show updated summary
    summary = get_task_summary()
    print(f"\nUpdated task summary:")
    print(f"  Active tasks: {summary['active_tasks']}")
    print(f"  Completed tasks: {summary['completed_tasks']}")
    print(f"  Queue size: {summary['queue_size']}")


def demo_session_integration():
    """Demo session integration and goal-based planning."""
    print("\n" + "="*60)
    print("DEMO: Session Integration")
    print("="*60)
    
    # Set up a session with goals
    session_id = "demo_session_001"
    goals = ["goal_quest_main", "goal_combat_training", "goal_collection_complete"]
    
    set_session(session_id, goals)
    print(f"Set session: {session_id}")
    print(f"Session goals: {goals}")
    
    # Replan based on session goals
    print("\nReplanning based on session goals...")
    new_tasks = replan(current_location="Naboo", current_goals=goals)
    
    print(f"Generated {len(new_tasks)} new tasks from goals:")
    for task in new_tasks:
        print(f"  - {task.title} (Priority: {task.priority.name})")
    
    # Show session summary
    summary = get_task_summary()
    print(f"\nSession summary:")
    print(f"  Current session: {summary['current_session']}")
    print(f"  Session goals: {summary['session_goals']}")
    print(f"  Active tasks: {summary['active_tasks']}")


def demo_performance_tracking():
    """Demo performance tracking and metrics."""
    print("\n" + "="*60)
    print("DEMO: Performance Tracking")
    print("="*60)
    
    summary = get_task_summary()
    metrics = summary['performance_metrics']
    
    print("Performance metrics by task type:")
    for task_type, task_metrics in metrics.items():
        if task_metrics['total_tasks'] > 0:
            print(f"  {task_type}:")
            print(f"    Total tasks: {task_metrics['total_tasks']}")
            print(f"    Success rate: {task_metrics['success_rate']:.2%}")
            print(f"    Average duration: {task_metrics['average_duration']:.1f} seconds")
            print(f"    Total XP gained: {task_metrics['total_xp_gained']}")
            print(f"    Total credits gained: {task_metrics['total_credits_gained']}")


def demo_task_requirements():
    """Demo task requirements and dependencies."""
    print("\n" + "="*60)
    print("DEMO: Task Requirements")
    print("="*60)
    
    # Create a task with requirements
    requirement_task = Task(
        id="requirement_demo_001",
        type=TaskType.QUEST,
        title="Advanced Quest with Requirements",
        description="Quest that requires specific conditions",
        priority=TaskPriority.HIGH,
        location="Naboo",
        requirements=[
            TaskRequirement(
                type="level",
                value=10,
                description="Character level 10 or higher",
                current_value=8,
                satisfied=False
            ),
            TaskRequirement(
                type="location",
                value="Naboo",
                description="Must be on Naboo",
                current_value="Naboo",
                satisfied=True
            ),
            TaskRequirement(
                type="item",
                value="Quest Item",
                description="Must have quest item",
                current_value=None,
                satisfied=False
            )
        ]
    )
    
    add_task(requirement_task)
    print(f"Added task with requirements: {requirement_task.title}")
    
    # Show requirements
    for i, req in enumerate(requirement_task.requirements, 1):
        status = "✓" if req.satisfied else "✗"
        print(f"  Requirement {i}: {req.description} {status}")
        print(f"    Required: {req.value}, Current: {req.current_value}")


def demo_error_handling():
    """Demo error handling and task failure."""
    print("\n" + "="*60)
    print("DEMO: Error Handling")
    print("="*60)
    
    planner = get_task_planner()
    
    # Create a task that might fail
    risky_task = Task(
        id="risky_task_001",
        type=TaskType.COMBAT,
        title="Risky Combat Task",
        description="Combat task that might fail",
        priority=TaskPriority.MEDIUM,
        location="Dangerous Zone",
        estimated_duration=10
    )
    
    task_id = add_task(risky_task)
    print(f"Added risky task: {risky_task.title}")
    
    # Simulate task failure
    if planner.start_task(task_id):
        print("  Started risky task...")
        
        # Simulate failure
        failure_result = TaskResult(
            success=False,
            duration=300,  # 5 minutes
            xp_gained=0,
            credits_gained=0,
            items_gained=[],
            errors=["Character died during combat", "Target was too strong"],
            notes="Task failed due to insufficient combat skills"
        )
        
        if planner.fail_task(task_id, "Combat failure"):
            print("  Task failed as expected")
            print(f"    Errors: {failure_result.errors}")
            print(f"    Notes: {failure_result.notes}")
        else:
            print("  Failed to mark task as failed")


def demo_replanning():
    """Demo task replanning based on changing conditions."""
    print("\n" + "="*60)
    print("DEMO: Task Replanning")
    print("="*60)
    
    # Get current state
    summary_before = get_task_summary()
    print(f"Tasks before replanning: {summary_before['active_tasks']}")
    
    # Replan with new location and goals
    print("\nReplanning with new conditions...")
    new_tasks = replan(
        current_location="Tatooine",  # Changed location
        current_goals=["goal_exploration", "goal_combat_advanced"]  # New goals
    )
    
    print(f"Generated {len(new_tasks)} new tasks during replanning:")
    for task in new_tasks:
        print(f"  - {task.title} (Location: {task.location})")
    
    # Show updated state
    summary_after = get_task_summary()
    print(f"\nTasks after replanning: {summary_after['active_tasks']}")


def main():
    """Run the complete demo."""
    print("MS11 Batch 051 - Lightweight AI Task Planner Demo")
    print("="*60)
    
    setup_logging()
    
    try:
        # Run all demos
        demo_basic_task_management()
        demo_task_execution()
        demo_session_integration()
        demo_task_requirements()
        demo_error_handling()
        demo_performance_tracking()
        demo_replanning()
        
        print("\n" + "="*60)
        print("DEMO COMPLETE")
        print("="*60)
        
        # Final summary
        final_summary = get_task_summary()
        print(f"Final Summary:")
        print(f"  Active tasks: {final_summary['active_tasks']}")
        print(f"  Completed tasks: {final_summary['completed_tasks']}")
        print(f"  Performance metrics: {len(final_summary['performance_metrics'])} task types tracked")
        
        # Save demo results
        with open('demo_batch_051_results.json', 'w') as f:
            json.dump(final_summary, f, indent=2)
        print(f"\nDemo results saved to: demo_batch_051_results.json")
        
    except Exception as e:
        print(f"Demo failed with error: {e}")
        logging.error(f"Demo error: {e}", exc_info=True)


if __name__ == "__main__":
    main() 