"""CLI Interface - Command-line interface for Batch 045."""

import sys
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

from .quest_master import QuestData, QuestStatus, QuestPriority
from .todo_manager import TodoItem, TodoCategory
from .progress_tracker import ProgressTracker

logger = logging.getLogger(__name__)


class TodoCLI:
    """Command-line interface for todo tracker."""
    
    def __init__(self, quest_master, todo_manager, progress_tracker):
        """Initialize CLI with managers."""
        self.quest_master = quest_master
        self.todo_manager = todo_manager
        self.progress_tracker = progress_tracker
    
    def run(self):
        """Run the CLI interface."""
        print("🎯 SWGR Todo Tracker CLI")
        print("=" * 50)
        
        while True:
            self._show_main_menu()
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == '1':
                self._show_quest_list()
            elif choice == '2':
                self._show_todo_list()
            elif choice == '3':
                self._show_progress_summary()
            elif choice == '4':
                self._add_todo_item()
            elif choice == '5':
                self._update_item_status()
            elif choice == '6':
                self._search_items()
            elif choice == '7':
                self._show_available_items()
            elif choice == '8':
                print("Goodbye! 🚀")
                break
            else:
                print("❌ Invalid choice. Please try again.")
    
    def _show_main_menu(self):
        """Display the main menu."""
        print("\n📋 Main Menu:")
        print("1. View Quest List")
        print("2. View Todo List")
        print("3. Show Progress Summary")
        print("4. Add Todo Item")
        print("5. Update Item Status")
        print("6. Search Items")
        print("7. Show Available Items")
        print("8. Exit")
    
    def _show_quest_list(self):
        """Display quest list with filtering options."""
        print("\n📋 Quest List")
        print("-" * 30)
        
        filter_choice = input("Filter by:\n1. All\n2. Planet\n3. Status\n4. Priority\nChoice: ").strip()
        
        quests = []
        if filter_choice == '1':
            quests = list(self.quest_master.quests.values())
        elif filter_choice == '2':
            planet = input("Enter planet name: ").strip()
            quests = self.quest_master.get_quests_by_planet(planet)
        elif filter_choice == '3':
            status_choice = input("Status (not_started/in_progress/completed/skipped/failed): ").strip()
            try:
                status = QuestStatus(status_choice)
                quests = self.quest_master.get_quests_by_status(status)
            except ValueError:
                print("❌ Invalid status")
                return
        elif filter_choice == '4':
            priority_choice = input("Priority (low/medium/high/critical): ").strip()
            try:
                priority = QuestPriority(priority_choice)
                quests = self.quest_master.get_quests_by_priority(priority)
            except ValueError:
                print("❌ Invalid priority")
                return
        
        if not quests:
            print("No quests found.")
            return
        
        display_quest_list(quests)
    
    def _show_todo_list(self):
        """Display todo list with filtering options."""
        print("\n✅ Todo List")
        print("-" * 30)
        
        filter_choice = input("Filter by:\n1. All\n2. Category\n3. Status\n4. Priority\nChoice: ").strip()
        
        todos = []
        if filter_choice == '1':
            todos = list(self.todo_manager.todos.values())
        elif filter_choice == '2':
            category_choice = input("Category (quest/collection/achievement/crafting/combat/exploration/social/other): ").strip()
            try:
                category = TodoCategory(category_choice)
                todos = self.todo_manager.get_todos_by_category(category)
            except ValueError:
                print("❌ Invalid category")
                return
        elif filter_choice == '3':
            status_choice = input("Status (not_started/in_progress/completed/skipped/failed): ").strip()
            try:
                status = QuestStatus(status_choice)
                todos = self.todo_manager.get_todos_by_status(status)
            except ValueError:
                print("❌ Invalid status")
                return
        elif filter_choice == '4':
            priority_choice = input("Priority (low/medium/high/critical): ").strip()
            try:
                priority = QuestPriority(priority_choice)
                todos = self.todo_manager.get_todos_by_priority(priority)
            except ValueError:
                print("❌ Invalid priority")
                return
        
        if not todos:
            print("No todos found.")
            return
        
        display_todo_list(todos)
    
    def _show_progress_summary(self):
        """Display progress summary."""
        print("\n📊 Progress Summary")
        print("-" * 30)
        
        # Update progress with current data
        quests = list(self.quest_master.quests.values())
        todos = list(self.todo_manager.todos.values())
        self.progress_tracker.update_progress(quests, todos)
        
        display_progress_summary(self.progress_tracker)
    
    def _add_todo_item(self):
        """Add a new todo item."""
        print("\n➕ Add Todo Item")
        print("-" * 30)
        
        title = input("Title: ").strip()
        if not title:
            print("❌ Title is required")
            return
        
        description = input("Description (optional): ").strip()
        
        print("\nCategories:")
        for i, category in enumerate(TodoCategory, 1):
            print(f"{i}. {category.value}")
        category_choice = input("Category (1-8): ").strip()
        
        try:
            category = list(TodoCategory)[int(category_choice) - 1]
        except (ValueError, IndexError):
            print("❌ Invalid category choice")
            return
        
        print("\nPriorities:")
        for i, priority in enumerate(QuestPriority, 1):
            print(f"{i}. {priority.value}")
        priority_choice = input("Priority (1-4): ").strip()
        
        try:
            priority = list(QuestPriority)[int(priority_choice) - 1]
        except (ValueError, IndexError):
            print("❌ Invalid priority choice")
            return
        
        planet = input("Planet (optional): ").strip() or None
        estimated_time = input("Estimated time in minutes (optional): ").strip()
        estimated_time = int(estimated_time) if estimated_time.isdigit() else None
        
        tags_input = input("Tags (comma-separated, optional): ").strip()
        tags = [tag.strip() for tag in tags_input.split(',')] if tags_input else []
        
        todo_id = self.todo_manager.add_todo_item(
            title=title,
            description=description,
            category=category,
            priority=priority,
            planet=planet,
            estimated_time=estimated_time,
            tags=tags
        )
        
        print(f"✅ Todo item added with ID: {todo_id}")
    
    def _update_item_status(self):
        """Update item status."""
        print("\n🔄 Update Item Status")
        print("-" * 30)
        
        item_type = input("Item type (quest/todo): ").strip().lower()
        
        if item_type == 'quest':
            quest_id = input("Quest ID: ").strip()
            quest = self.quest_master.get_quest(quest_id)
            if not quest:
                print("❌ Quest not found")
                return
            
            print(f"Current status: {quest.status.value}")
            print("Available statuses: not_started, in_progress, completed, skipped, failed")
            new_status = input("New status: ").strip()
            
            try:
                status = QuestStatus(new_status)
                self.quest_master.update_quest_status(quest_id, status)
                print(f"✅ Updated quest {quest_id} status to {status.value}")
            except ValueError:
                print("❌ Invalid status")
        
        elif item_type == 'todo':
            todo_id = input("Todo ID: ").strip()
            todo = self.todo_manager.get_todo_item(todo_id)
            if not todo:
                print("❌ Todo not found")
                return
            
            print(f"Current status: {todo.status.value}")
            print("Available statuses: not_started, in_progress, completed, skipped, failed")
            new_status = input("New status: ").strip()
            
            try:
                status = QuestStatus(new_status)
                self.todo_manager.update_todo_status(todo_id, status)
                print(f"✅ Updated todo {todo_id} status to {status.value}")
            except ValueError:
                print("❌ Invalid status")
        
        else:
            print("❌ Invalid item type")
    
    def _search_items(self):
        """Search for items."""
        print("\n🔍 Search Items")
        print("-" * 30)
        
        query = input("Search query: ").strip()
        if not query:
            print("❌ Search query is required")
            return
        
        # Search in quests
        quest_results = []
        for quest in self.quest_master.quests.values():
            if (query.lower() in quest.name.lower() or
                (quest.description and query.lower() in quest.description.lower()) or
                any(query.lower() in tag.lower() for tag in quest.tags)):
                quest_results.append(quest)
        
        # Search in todos
        todo_results = self.todo_manager.search_todos(query)
        
        print(f"\nFound {len(quest_results)} quests and {len(todo_results)} todos")
        
        if quest_results:
            print("\n📋 Matching Quests:")
            display_quest_list(quest_results)
        
        if todo_results:
            print("\n✅ Matching Todos:")
            display_todo_list(todo_results)
    
    def _show_available_items(self):
        """Show items that can be started."""
        print("\n🚀 Available Items")
        print("-" * 30)
        
        available_quests = self.quest_master.get_available_quests()
        available_todos = self.todo_manager.get_available_todos()
        
        print(f"Available quests: {len(available_quests)}")
        print(f"Available todos: {len(available_todos)}")
        
        if available_quests:
            print("\n📋 Available Quests:")
            display_quest_list(available_quests)
        
        if available_todos:
            print("\n✅ Available Todos:")
            display_todo_list(available_todos)


def display_quest_list(quests: List[QuestData]):
    """Display a list of quests."""
    if not quests:
        print("No quests to display.")
        return
    
    print(f"\n{'ID':<15} {'Name':<30} {'Planet':<12} {'Status':<12} {'Priority':<10} {'XP':<6}")
    print("-" * 100)
    
    for quest in quests:
        print(f"{quest.id:<15} {quest.name[:29]:<30} {quest.planet:<12} "
              f"{quest.status.value:<12} {quest.priority.value:<10} {quest.xp_reward:<6}")


def display_todo_list(todos: List[TodoItem]):
    """Display a list of todos."""
    if not todos:
        print("No todos to display.")
        return
    
    print(f"\n{'ID':<15} {'Title':<30} {'Category':<12} {'Status':<12} {'Priority':<10} {'Planet':<12}")
    print("-" * 100)
    
    for todo in todos:
        print(f"{todo.id:<15} {todo.title[:29]:<30} {todo.category.value:<12} "
              f"{todo.status.value:<12} {todo.priority.value:<10} {todo.planet or 'Any':<12}")


def display_progress_summary(progress_tracker: ProgressTracker):
    """Display progress summary."""
    summary = progress_tracker.get_progress_summary()
    
    print(f"Total Items: {summary['total_items']}")
    print(f"Completed: {summary['completed_items']}")
    print(f"Completion Percentage: {summary['completion_percentage']:.1f}%")
    print(f"XP Gained: {summary['xp_gained']:,}")
    print(f"Credits Earned: {summary['credits_gained']:,}")
    print(f"Planets Visited: {summary['planets_visited']}")
    print(f"Current Streak: {summary['completion_streak']} days")
    print(f"Longest Streak: {summary['longest_streak']} days")
    print(f"Last Updated: {summary['last_updated']}")
    
    # Show recent completions
    recent = progress_tracker.get_recent_completions(5)
    if recent:
        print(f"\n📅 Recent Completions:")
        for completion in recent:
            date = completion['completion_date'][:10]  # Just the date part
            print(f"  {date}: {completion['item_type']} {completion['item_id']}")


def main():
    """Main function to run the CLI."""
    try:
        from .quest_master import QuestMaster
        from .todo_manager import TodoManager
        from .progress_tracker import ProgressTracker
        
        # Initialize managers
        quest_master = QuestMaster()
        todo_manager = TodoManager()
        progress_tracker = ProgressTracker()
        
        # Run CLI
        cli = TodoCLI(quest_master, todo_manager, progress_tracker)
        cli.run()
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"CLI error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 