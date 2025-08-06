#!/usr/bin/env python3
"""Demo script for Batch 045 - Smart Quest To-Do List + Completion Tracker."""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from ui.todo_tracker import (
    QuestMaster, QuestData, QuestStatus, QuestPriority,
    TodoManager, TodoItem, TodoCategory,
    ProgressTracker, ProgressData, CompletionStats,
    TodoDashboard, generate_html_dashboard,
    TodoCLI, display_quest_list, display_todo_list, display_progress_summary,
    QuestPlanner, QuestChain, PrerequisiteAnalyzer
)


def demo_quest_master():
    """Demo the QuestMaster functionality."""
    print("🎯 Demo: Quest Master")
    print("=" * 50)
    
    # Create sample quest data
    sample_quests = [
        QuestData(
            id="quest_001",
            name="Tatooine Trade Route",
            planet="tatooine",
            npc="Mos Eisley Merchant",
            description="Establish a trade route between Mos Eisley and Anchorhead",
            objectives=["Talk to merchant", "Deliver goods", "Return to merchant"],
            prerequisites=[],
            xp_reward=500,
            credit_reward=2000,
            difficulty="easy",
            status=QuestStatus.NOT_STARTED,
            priority=QuestPriority.MEDIUM,
            tags=["trade", "tatooine"]
        ),
        QuestData(
            id="quest_002",
            name="Naboo Palace Security",
            planet="naboo",
            npc="Palace Guard",
            description="Help secure the Naboo palace from threats",
            objectives=["Patrol palace grounds", "Report suspicious activity", "Complete security check"],
            prerequisites=["quest_001"],
            xp_reward=800,
            credit_reward=3500,
            difficulty="medium",
            status=QuestStatus.NOT_STARTED,
            priority=QuestPriority.HIGH,
            tags=["security", "naboo", "palace"]
        ),
        QuestData(
            id="quest_003",
            name="Corellia Artifact Hunt",
            planet="corellia",
            npc="Archaeologist",
            description="Search for ancient artifacts in Corellia's ruins",
            objectives=["Explore ruins", "Find artifacts", "Return to archaeologist"],
            prerequisites=["quest_002"],
            xp_reward=1200,
            credit_reward=5000,
            difficulty="hard",
            status=QuestStatus.COMPLETED,
            priority=QuestPriority.CRITICAL,
            tags=["archaeology", "corellia", "artifacts"]
        )
    ]
    
    # Initialize QuestMaster
    quest_master = QuestMaster()
    
    # Add sample quests
    for quest in sample_quests:
        quest_master.quests[quest.id] = quest
    
    print(f"✅ Loaded {len(quest_master.quests)} quests")
    
    # Demo quest operations
    print(f"\n📋 Quest Statistics:")
    print(f"Total quests: {quest_master.get_total_quests()}")
    print(f"Completed quests: {quest_master.get_completed_quests()}")
    print(f"Completion percentage: {quest_master.get_completion_percentage():.1f}%")
    
    # Demo quest filtering
    print(f"\n🌍 Quests by planet:")
    for planet in ["tatooine", "naboo", "corellia"]:
        planet_quests = quest_master.get_quests_by_planet(planet)
        print(f"  {planet.title()}: {len(planet_quests)} quests")
    
    # Demo available quests
    available_quests = quest_master.get_available_quests()
    print(f"\n🚀 Available quests: {len(available_quests)}")
    for quest in available_quests:
        print(f"  - {quest.name} ({quest.planet})")
    
    # Demo quest status updates
    quest_master.update_quest_status("quest_001", QuestStatus.IN_PROGRESS)
    print(f"\n✅ Updated quest_001 status to in_progress")
    
    return quest_master


def demo_todo_manager():
    """Demo the TodoManager functionality."""
    print("\n✅ Demo: Todo Manager")
    print("=" * 50)
    
    # Initialize TodoManager
    todo_manager = TodoManager()
    
    # Add sample todo items
    todo_items = [
        {
            'title': "Complete Tatooine Trade Route",
            'description': "Finish the trade route quest for XP and credits",
            'category': TodoCategory.QUEST,
            'priority': QuestPriority.MEDIUM,
            'planet': "tatooine",
            'estimated_time': 30,
            'tags': ["quest", "tatooine"]
        },
        {
            'title': "Collect 100 Credits",
            'description': "Save up credits for better equipment",
            'category': TodoCategory.COLLECTION,
            'priority': QuestPriority.LOW,
            'estimated_time': 60,
            'tags': ["credits", "saving"]
        },
        {
            'title': "Visit All Planets",
            'description': "Travel to each planet to unlock new content",
            'category': TodoCategory.EXPLORATION,
            'priority': QuestPriority.HIGH,
            'estimated_time': 120,
            'tags': ["exploration", "travel"]
        }
    ]
    
    for item_data in todo_items:
        todo_id = todo_manager.add_todo_item(**item_data)
        print(f"✅ Added todo: {item_data['title']} (ID: {todo_id})")
    
    print(f"\n📊 Todo Statistics:")
    print(f"Total todos: {todo_manager.get_total_todos()}")
    print(f"Completed todos: {todo_manager.get_completed_todos()}")
    print(f"Completion percentage: {todo_manager.get_completion_percentage():.1f}%")
    
    # Demo category stats
    category_stats = todo_manager.get_category_stats()
    print(f"\n📂 Category Statistics:")
    for category, stats in category_stats.items():
        if stats['total'] > 0:
            print(f"  {category.value}: {stats['completed']}/{stats['total']} completed")
    
    # Demo search functionality
    search_results = todo_manager.search_todos("credits")
    print(f"\n🔍 Search results for 'credits': {len(search_results)} items")
    
    return todo_manager


def demo_progress_tracker(quest_master, todo_manager):
    """Demo the ProgressTracker functionality."""
    print("\n📊 Demo: Progress Tracker")
    print("=" * 50)
    
    # Initialize ProgressTracker
    progress_tracker = ProgressTracker()
    
    # Update progress with current data
    quests = list(quest_master.quests.values())
    todos = list(todo_manager.todos.values())
    progress_tracker.update_progress(quests, todos)
    
    # Get progress summary
    summary = progress_tracker.get_progress_summary()
    print(f"📈 Progress Summary:")
    print(f"  Total items: {summary['total_items']}")
    print(f"  Completed: {summary['completed_items']}")
    print(f"  Completion: {summary['completion_percentage']:.1f}%")
    print(f"  XP gained: {summary['xp_gained']:,}")
    print(f"  Credits earned: {summary['credits_gained']:,}")
    print(f"  Planets visited: {summary['planets_visited']}")
    print(f"  Current streak: {summary['completion_streak']} days")
    
    # Record some completion events
    progress_tracker.record_completion("quest_003", "quest", 45, "corellia", "quest")
    progress_tracker.record_completion("todo_1", "todo", 30, "tatooine", "quest")
    
    # Get completion trends
    trends = progress_tracker.get_completion_trends(7)
    print(f"\n📅 Recent completion trends:")
    for date, count in trends['daily'][-3:]:
        print(f"  {date}: {count} completions")
    
    # Get recent completions
    recent = progress_tracker.get_recent_completions(5)
    print(f"\n🕒 Recent completions:")
    for completion in recent:
        date = completion['completion_date'][:10]
        print(f"  {date}: {completion['item_type']} {completion['item_id']}")
    
    return progress_tracker


def demo_dashboard(quest_master, todo_manager, progress_tracker):
    """Demo the dashboard functionality."""
    print("\n🌐 Demo: HTML Dashboard")
    print("=" * 50)
    
    # Generate dashboard
    quests = list(quest_master.quests.values())
    todos = list(todo_manager.todos.values())
    
    dashboard_file = generate_html_dashboard(quests, todos, progress_tracker)
    print(f"✅ Dashboard generated: {dashboard_file}")
    
    # Check if file was created
    if Path(dashboard_file).exists():
        file_size = Path(dashboard_file).stat().st_size
        print(f"📁 Dashboard file size: {file_size:,} bytes")
    else:
        print("❌ Dashboard file not found")


def demo_planner(quest_master, todo_manager):
    """Demo the QuestPlanner functionality."""
    print("\n📋 Demo: Quest Planner")
    print("=" * 50)
    
    # Initialize planner
    planner = QuestPlanner(quest_master, todo_manager)
    
    # Create optimization plan
    plan = planner.create_optimization_plan()
    print(f"📊 Optimization Plan:")
    print(f"  Target quests: {len(plan['target_quests'])}")
    print(f"  Estimated time: {plan['estimated_time']} minutes")
    print(f"  Total XP: {plan['total_xp']:,}")
    print(f"  Total credits: {plan['total_credits']:,}")
    print(f"  Efficiency score: {plan['efficiency_score']:.2f}")
    
    # Create planet completion plan
    tatooine_plan = planner.create_planet_completion_plan("tatooine")
    print(f"\n🌍 Tatooine Completion Plan:")
    print(f"  Quests in plan: {len(tatooine_plan['quest_order'])}")
    print(f"  Prerequisites needed: {len(tatooine_plan['prerequisites'])}")
    print(f"  Blocked quests: {len(tatooine_plan['blockers'])}")
    
    # Get quest recommendations
    recommendations = planner.get_quest_recommendations(
        preferred_planets=["tatooine", "naboo"]
    )
    print(f"\n🎯 Top Quest Recommendations:")
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"  {i}. {rec['quest_name']} ({rec['planet']}) - Score: {rec['score']}")
        print(f"     Reasons: {', '.join(rec['reasons'])}")
    
    # Save a plan
    planner.save_plan("demo_plan", plan)
    print(f"\n💾 Saved demo plan")
    
    return planner


def demo_prerequisite_analyzer(quest_master):
    """Demo the PrerequisiteAnalyzer functionality."""
    print("\n🔗 Demo: Prerequisite Analyzer")
    print("=" * 50)
    
    # Initialize analyzer
    analyzer = PrerequisiteAnalyzer(quest_master)
    
    # Analyze quest dependencies
    quest_id = "quest_002"
    direct_prereqs = analyzer.get_direct_prerequisites(quest_id)
    all_prereqs = analyzer.get_all_prerequisites(quest_id)
    dependents = analyzer.get_dependents(quest_id)
    
    print(f"📋 Quest Analysis for {quest_id}:")
    print(f"  Direct prerequisites: {len(direct_prereqs)}")
    print(f"  All prerequisites: {len(all_prereqs)}")
    print(f"  Dependents: {len(dependents)}")
    
    # Check if prerequisites are met
    prereqs_met = analyzer.check_prerequisites_met(quest_id)
    print(f"  Prerequisites met: {prereqs_met}")
    
    # Get blocking quests
    blockers = analyzer.get_blocking_quests(quest_id)
    print(f"  Blocking quests: {len(blockers)}")
    
    # Get quest chain
    chain = analyzer.get_quest_chain(quest_id)
    if chain:
        print(f"\n🔗 Quest Chain for {quest_id}:")
        print(f"  Total quests: {len(chain.quests)}")
        print(f"  Total XP: {chain.total_xp:,}")
        print(f"  Total credits: {chain.total_credits:,}")
        print(f"  Estimated time: {chain.estimated_time} minutes")
        print(f"  Difficulty: {chain.difficulty}")
    
    # Check for circular dependencies
    cycles = analyzer.find_circular_dependencies()
    if cycles:
        print(f"\n⚠️  Circular dependencies found: {len(cycles)}")
        for cycle in cycles:
            print(f"  Cycle: {' -> '.join(cycle)}")
    else:
        print(f"\n✅ No circular dependencies found")


def demo_cli_interface(quest_master, todo_manager, progress_tracker):
    """Demo the CLI interface."""
    print("\n💻 Demo: CLI Interface")
    print("=" * 50)
    
    # Initialize CLI
    cli = TodoCLI(quest_master, todo_manager, progress_tracker)
    
    print("🎯 CLI Interface Features:")
    print("  - View quest and todo lists")
    print("  - Filter by planet, status, priority, category")
    print("  - Add new todo items")
    print("  - Update item status")
    print("  - Search items")
    print("  - Show available items")
    print("  - Display progress summary")
    
    # Demo display functions
    print(f"\n📋 Sample Quest List:")
    quests = list(quest_master.quests.values())
    display_quest_list(quests)
    
    print(f"\n✅ Sample Todo List:")
    todos = list(todo_manager.todos.values())
    display_todo_list(todos)
    
    print(f"\n📊 Progress Summary:")
    display_progress_summary(progress_tracker)


def demo_integration():
    """Demo the full integration of all components."""
    print("\n🔗 Demo: Full Integration")
    print("=" * 50)
    
    # Initialize all components
    quest_master = demo_quest_master()
    todo_manager = demo_todo_manager()
    progress_tracker = demo_progress_tracker(quest_master, todo_manager)
    
    # Generate dashboard
    demo_dashboard(quest_master, todo_manager, progress_tracker)
    
    # Test planner
    planner = demo_planner(quest_master, todo_manager)
    
    # Test prerequisite analyzer
    demo_prerequisite_analyzer(quest_master)
    
    # Test CLI interface
    demo_cli_interface(quest_master, todo_manager, progress_tracker)
    
    print(f"\n🎉 Integration demo completed successfully!")
    print(f"📁 Generated files:")
    print(f"  - Dashboard: dashboard/index.html")
    print(f"  - Progress data: data/progress_tracker.json")
    print(f"  - Todo data: data/todo_list.json")


def demo_error_handling():
    """Demo error handling scenarios."""
    print("\n⚠️  Demo: Error Handling")
    print("=" * 50)
    
    # Test with non-existent quest directory
    quest_master = QuestMaster("non_existent_directory")
    print(f"✅ QuestMaster initialized with non-existent directory")
    print(f"  Loaded quests: {len(quest_master.quests)}")
    
    # Test with non-existent todo file
    todo_manager = TodoManager("non_existent_file.json")
    print(f"✅ TodoManager initialized with non-existent file")
    print(f"  Loaded todos: {len(todo_manager.todos)}")
    
    # Test with non-existent progress file
    progress_tracker = ProgressTracker("non_existent_progress.json")
    print(f"✅ ProgressTracker initialized with non-existent file")
    
    # Test invalid quest status
    try:
        invalid_status = QuestStatus("invalid_status")
    except ValueError as e:
        print(f"✅ Caught invalid status error: {e}")
    
    # Test invalid priority
    try:
        invalid_priority = QuestPriority("invalid_priority")
    except ValueError as e:
        print(f"✅ Caught invalid priority error: {e}")


def main():
    """Run all demos."""
    print("🎯 Batch 045 - Smart Quest To-Do List + Completion Tracker Demo")
    print("=" * 70)
    print("This demo showcases all features of the todo tracker system.")
    print()
    
    try:
        # Run individual component demos
        demo_quest_master()
        demo_todo_manager()
        
        # Run integration demo
        demo_integration()
        
        # Run error handling demo
        demo_error_handling()
        
        print(f"\n🎉 All demos completed successfully!")
        print(f"📋 Features demonstrated:")
        print(f"  ✅ Quest management and filtering")
        print(f"  ✅ Todo item management")
        print(f"  ✅ Progress tracking and statistics")
        print(f"  ✅ HTML dashboard generation")
        print(f"  ✅ Quest planning and optimization")
        print(f"  ✅ Prerequisite analysis")
        print(f"  ✅ CLI interface")
        print(f"  ✅ Error handling")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 