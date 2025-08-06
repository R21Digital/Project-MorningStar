#!/usr/bin/env python3
"""Test suite for Batch 045 - Smart Quest To-Do List + Completion Tracker."""

import unittest
import tempfile
import json
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import sys
import os

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


class TestQuestData(unittest.TestCase):
    """Test QuestData dataclass."""
    
    def test_quest_data_creation(self):
        """Test creating QuestData instance."""
        quest = QuestData(
            id="test_quest",
            name="Test Quest",
            planet="tatooine",
            npc="Test NPC",
            description="A test quest",
            objectives=["Objective 1", "Objective 2"],
            prerequisites=["prereq_1"],
            xp_reward=500,
            credit_reward=1000,
            difficulty="medium",
            status=QuestStatus.NOT_STARTED,
            priority=QuestPriority.MEDIUM,
            tags=["test", "demo"]
        )
        
        self.assertEqual(quest.id, "test_quest")
        self.assertEqual(quest.name, "Test Quest")
        self.assertEqual(quest.planet, "tatooine")
        self.assertEqual(quest.npc, "Test NPC")
        self.assertEqual(quest.xp_reward, 500)
        self.assertEqual(quest.credit_reward, 1000)
        self.assertEqual(quest.status, QuestStatus.NOT_STARTED)
        self.assertEqual(quest.priority, QuestPriority.MEDIUM)
    
    def test_quest_data_to_dict(self):
        """Test QuestData to_dict method."""
        quest = QuestData(
            id="test_quest",
            name="Test Quest",
            planet="tatooine",
            xp_reward=500,
            credit_reward=1000
        )
        
        data = quest.to_dict()
        self.assertEqual(data['id'], "test_quest")
        self.assertEqual(data['name'], "Test Quest")
        self.assertEqual(data['planet'], "tatooine")
        self.assertEqual(data['xp_reward'], 500)
        self.assertEqual(data['credit_reward'], 1000)
        self.assertEqual(data['status'], "not_started")
        self.assertEqual(data['priority'], "medium")
    
    def test_quest_data_from_dict(self):
        """Test QuestData from_dict method."""
        data = {
            'id': 'test_quest',
            'name': 'Test Quest',
            'planet': 'tatooine',
            'xp_reward': 500,
            'credit_reward': 1000,
            'status': 'completed',
            'priority': 'high',
            'completion_date': '2023-01-01T12:00:00'
        }
        
        quest = QuestData.from_dict(data)
        self.assertEqual(quest.id, "test_quest")
        self.assertEqual(quest.name, "Test Quest")
        self.assertEqual(quest.status, QuestStatus.COMPLETED)
        self.assertEqual(quest.priority, QuestPriority.HIGH)
        self.assertIsInstance(quest.completion_date, datetime)


class TestQuestMaster(unittest.TestCase):
    """Test QuestMaster class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.quest_master = QuestMaster(self.temp_dir)
        
        # Create sample quest data
        self.sample_quest = QuestData(
            id="test_quest",
            name="Test Quest",
            planet="tatooine",
            xp_reward=500,
            credit_reward=1000
        )
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_quest_master_initialization(self):
        """Test QuestMaster initialization."""
        self.assertIsInstance(self.quest_master.quests, dict)
        self.assertIsInstance(self.quest_master.quest_chains, dict)
        self.assertIsInstance(self.quest_master.planet_quests, dict)
    
    def test_add_quest(self):
        """Test adding quest to QuestMaster."""
        self.quest_master.quests["test_quest"] = self.sample_quest
        self.assertIn("test_quest", self.quest_master.quests)
        self.assertEqual(self.quest_master.quests["test_quest"], self.sample_quest)
    
    def test_get_quest(self):
        """Test getting quest by ID."""
        self.quest_master.quests["test_quest"] = self.sample_quest
        quest = self.quest_master.get_quest("test_quest")
        self.assertEqual(quest, self.sample_quest)
        
        # Test non-existent quest
        quest = self.quest_master.get_quest("non_existent")
        self.assertIsNone(quest)
    
    def test_get_quests_by_planet(self):
        """Test getting quests by planet."""
        quest1 = QuestData(id="q1", name="Quest 1", planet="tatooine")
        quest2 = QuestData(id="q2", name="Quest 2", planet="naboo")
        quest3 = QuestData(id="q3", name="Quest 3", planet="tatooine")
        
        self.quest_master.quests = {"q1": quest1, "q2": quest2, "q3": quest3}
        self.quest_master.planet_quests = {
            "tatooine": ["q1", "q3"],
            "naboo": ["q2"]
        }
        
        tatooine_quests = self.quest_master.get_quests_by_planet("tatooine")
        self.assertEqual(len(tatooine_quests), 2)
        self.assertIn(quest1, tatooine_quests)
        self.assertIn(quest3, tatooine_quests)
    
    def test_get_quests_by_status(self):
        """Test getting quests by status."""
        quest1 = QuestData(id="q1", name="Quest 1", planet="tatooine", status=QuestStatus.COMPLETED)
        quest2 = QuestData(id="q2", name="Quest 2", planet="naboo", status=QuestStatus.NOT_STARTED)
        quest3 = QuestData(id="q3", name="Quest 3", planet="tatooine", status=QuestStatus.COMPLETED)
        
        self.quest_master.quests = {"q1": quest1, "q2": quest2, "q3": quest3}
        
        completed_quests = self.quest_master.get_quests_by_status(QuestStatus.COMPLETED)
        self.assertEqual(len(completed_quests), 2)
        self.assertIn(quest1, completed_quests)
        self.assertIn(quest3, completed_quests)
    
    def test_update_quest_status(self):
        """Test updating quest status."""
        self.quest_master.quests["test_quest"] = self.sample_quest
        
        self.quest_master.update_quest_status("test_quest", QuestStatus.COMPLETED)
        self.assertEqual(self.quest_master.quests["test_quest"].status, QuestStatus.COMPLETED)
    
    def test_get_completion_percentage(self):
        """Test completion percentage calculation."""
        quest1 = QuestData(id="q1", name="Quest 1", planet="tatooine", status=QuestStatus.COMPLETED)
        quest2 = QuestData(id="q2", name="Quest 2", planet="naboo", status=QuestStatus.NOT_STARTED)
        quest3 = QuestData(id="q3", name="Quest 3", planet="tatooine", status=QuestStatus.COMPLETED)
        
        self.quest_master.quests = {"q1": quest1, "q2": quest2, "q3": quest3}
        
        percentage = self.quest_master.get_completion_percentage()
        self.assertAlmostEqual(percentage, 66.66666666666667, places=10)  # 2/3 * 100
    
    def test_get_available_quests(self):
        """Test getting available quests."""
        quest1 = QuestData(id="q1", name="Quest 1", planet="tatooine", status=QuestStatus.NOT_STARTED)
        quest2 = QuestData(id="q2", name="Quest 2", planet="naboo", status=QuestStatus.NOT_STARTED, prerequisites=["q1"])
        quest3 = QuestData(id="q3", name="Quest 3", planet="tatooine", status=QuestStatus.NOT_STARTED)
        
        self.quest_master.quests = {"q1": quest1, "q2": quest2, "q3": quest3}
        
        # Initially, only quest1 and quest3 should be available (no prerequisites)
        available = self.quest_master.get_available_quests()
        self.assertEqual(len(available), 2)
        self.assertIn(quest1, available)
        self.assertIn(quest3, available)
        
        # After completing quest1, quest2 should become available
        quest1.status = QuestStatus.COMPLETED
        available = self.quest_master.get_available_quests()
        self.assertEqual(len(available), 2)  # quest1 is completed, quest2 and quest3 available
        self.assertIn(quest2, available)
        self.assertIn(quest3, available)


class TestTodoItem(unittest.TestCase):
    """Test TodoItem dataclass."""
    
    def test_todo_item_creation(self):
        """Test creating TodoItem instance."""
        todo = TodoItem(
            id="test_todo",
            title="Test Todo",
            description="A test todo item",
            category=TodoCategory.QUEST,
            priority=QuestPriority.HIGH,
            planet="tatooine",
            estimated_time=30,
            tags=["test", "demo"]
        )
        
        self.assertEqual(todo.id, "test_todo")
        self.assertEqual(todo.title, "Test Todo")
        self.assertEqual(todo.category, TodoCategory.QUEST)
        self.assertEqual(todo.priority, QuestPriority.HIGH)
        self.assertEqual(todo.planet, "tatooine")
        self.assertEqual(todo.estimated_time, 30)
    
    def test_todo_item_to_dict(self):
        """Test TodoItem to_dict method."""
        todo = TodoItem(
            id="test_todo",
            title="Test Todo",
            category=TodoCategory.QUEST,
            priority=QuestPriority.HIGH
        )
        
        data = todo.to_dict()
        self.assertEqual(data['id'], "test_todo")
        self.assertEqual(data['title'], "Test Todo")
        self.assertEqual(data['category'], "quest")
        self.assertEqual(data['priority'], "high")
    
    def test_todo_item_from_dict(self):
        """Test TodoItem from_dict method."""
        data = {
            'id': 'test_todo',
            'title': 'Test Todo',
            'category': 'quest',
            'priority': 'high',
            'status': 'completed',
            'completion_date': '2023-01-01T12:00:00'
        }
        
        todo = TodoItem.from_dict(data)
        self.assertEqual(todo.id, "test_todo")
        self.assertEqual(todo.title, "Test Todo")
        self.assertEqual(todo.category, TodoCategory.QUEST)
        self.assertEqual(todo.priority, QuestPriority.HIGH)
        self.assertEqual(todo.status, QuestStatus.COMPLETED)


class TestTodoManager(unittest.TestCase):
    """Test TodoManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.todo_manager = TodoManager(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.unlink(self.temp_file.name)
    
    def test_todo_manager_initialization(self):
        """Test TodoManager initialization."""
        self.assertIsInstance(self.todo_manager.todos, dict)
        self.assertIsInstance(self.todo_manager.categories, dict)
    
    def test_add_todo_item(self):
        """Test adding todo item."""
        todo_id = self.todo_manager.add_todo_item(
            title="Test Todo",
            description="A test todo",
            category=TodoCategory.QUEST,
            priority=QuestPriority.HIGH,
            planet="tatooine"
        )
        
        self.assertIn(todo_id, self.todo_manager.todos)
        todo = self.todo_manager.todos[todo_id]
        self.assertEqual(todo.title, "Test Todo")
        self.assertEqual(todo.category, TodoCategory.QUEST)
        self.assertEqual(todo.priority, QuestPriority.HIGH)
    
    def test_get_todo_item(self):
        """Test getting todo item by ID."""
        todo_id = self.todo_manager.add_todo_item(title="Test Todo")
        todo = self.todo_manager.get_todo_item(todo_id)
        self.assertIsNotNone(todo)
        self.assertEqual(todo.title, "Test Todo")
        
        # Test non-existent todo
        todo = self.todo_manager.get_todo_item("non_existent")
        self.assertIsNone(todo)
    
    def test_get_todos_by_category(self):
        """Test getting todos by category."""
        self.todo_manager.add_todo_item(title="Quest Todo", category=TodoCategory.QUEST)
        self.todo_manager.add_todo_item(title="Collection Todo", category=TodoCategory.COLLECTION)
        self.todo_manager.add_todo_item(title="Another Quest", category=TodoCategory.QUEST)
        
        quest_todos = self.todo_manager.get_todos_by_category(TodoCategory.QUEST)
        self.assertEqual(len(quest_todos), 2)
        
        collection_todos = self.todo_manager.get_todos_by_category(TodoCategory.COLLECTION)
        self.assertEqual(len(collection_todos), 1)
    
    def test_update_todo_status(self):
        """Test updating todo status."""
        todo_id = self.todo_manager.add_todo_item(title="Test Todo")
        
        self.todo_manager.update_todo_status(todo_id, QuestStatus.COMPLETED)
        todo = self.todo_manager.get_todo_item(todo_id)
        self.assertEqual(todo.status, QuestStatus.COMPLETED)
        self.assertIsNotNone(todo.completed_date)
    
    def test_search_todos(self):
        """Test searching todos."""
        self.todo_manager.add_todo_item(title="Test Todo", description="A test todo")
        self.todo_manager.add_todo_item(title="Another Todo", description="Different description")
        self.todo_manager.add_todo_item(title="Third Todo", tags=["test"])
        
        results = self.todo_manager.search_todos("test")
        self.assertEqual(len(results), 2)  # "Test Todo" and "Third Todo"
    
    def test_get_completion_percentage(self):
        """Test completion percentage calculation."""
        todo1_id = self.todo_manager.add_todo_item(title="Todo 1")
        todo2_id = self.todo_manager.add_todo_item(title="Todo 2")
        todo3_id = self.todo_manager.add_todo_item(title="Todo 3")
        
        # Update status after creation
        self.todo_manager.update_todo_status(todo1_id, QuestStatus.COMPLETED)
        self.todo_manager.update_todo_status(todo3_id, QuestStatus.COMPLETED)
        
        percentage = self.todo_manager.get_completion_percentage()
        self.assertAlmostEqual(percentage, 66.66666666666667, places=10)  # 2/3 * 100


class TestProgressTracker(unittest.TestCase):
    """Test ProgressTracker class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.progress_tracker = ProgressTracker(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.unlink(self.temp_file.name)
    
    def test_progress_tracker_initialization(self):
        """Test ProgressTracker initialization."""
        self.assertIsInstance(self.progress_tracker.progress_data, ProgressData)
        self.assertIsInstance(self.progress_tracker.completion_stats, CompletionStats)
        self.assertIsInstance(self.progress_tracker.completion_history, list)
    
    def test_update_progress(self):
        """Test updating progress."""
        quests = [
            QuestData(id="q1", name="Quest 1", planet="tatooine", status=QuestStatus.COMPLETED, xp_reward=500),
            QuestData(id="q2", name="Quest 2", planet="naboo", status=QuestStatus.NOT_STARTED, xp_reward=300)
        ]
        
        todos = [
            TodoItem(id="t1", title="Todo 1", status=QuestStatus.COMPLETED),
            TodoItem(id="t2", title="Todo 2", status=QuestStatus.NOT_STARTED)
        ]
        
        self.progress_tracker.update_progress(quests, todos)
        
        self.assertEqual(self.progress_tracker.progress_data.total_items, 4)
        self.assertEqual(self.progress_tracker.progress_data.completed_items, 2)
        self.assertEqual(self.progress_tracker.progress_data.completion_percentage, 50.0)
        self.assertEqual(self.progress_tracker.progress_data.xp_gained, 500)
    
    def test_record_completion(self):
        """Test recording completion events."""
        self.progress_tracker.record_completion("test_item", "quest", 30, "tatooine", "quest")
        
        self.assertEqual(len(self.progress_tracker.completion_history), 1)
        event = self.progress_tracker.completion_history[0]
        self.assertEqual(event['item_id'], "test_item")
        self.assertEqual(event['item_type'], "quest")
        self.assertEqual(event['planet'], "tatooine")
        self.assertEqual(event['category'], "quest")
    
    def test_get_progress_summary(self):
        """Test getting progress summary."""
        quests = [
            QuestData(id="q1", name="Quest 1", planet="tatooine", status=QuestStatus.COMPLETED, xp_reward=500)
        ]
        todos = [
            TodoItem(id="t1", title="Todo 1", status=QuestStatus.COMPLETED)
        ]
        
        self.progress_tracker.update_progress(quests, todos)
        summary = self.progress_tracker.get_progress_summary()
        
        self.assertEqual(summary['total_items'], 2)
        self.assertEqual(summary['completed_items'], 2)
        self.assertEqual(summary['completion_percentage'], 100.0)
        self.assertEqual(summary['xp_gained'], 500)
    
    def test_get_completion_trends(self):
        """Test getting completion trends."""
        # Record some completions
        self.progress_tracker.record_completion("item1", "quest")
        self.progress_tracker.record_completion("item2", "todo")
        
        trends = self.progress_tracker.get_completion_trends(7)
        
        self.assertIn('daily', trends)
        self.assertIn('weekly', trends)
        self.assertIsInstance(trends['daily'], list)
        self.assertIsInstance(trends['weekly'], list)


class TestQuestPlanner(unittest.TestCase):
    """Test QuestPlanner class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.quest_master = QuestMaster()
        self.todo_manager = TodoManager()
        
        # Add sample quests
        quest1 = QuestData(id="q1", name="Quest 1", planet="tatooine", status=QuestStatus.NOT_STARTED, xp_reward=500)
        quest2 = QuestData(id="q2", name="Quest 2", planet="naboo", status=QuestStatus.NOT_STARTED, xp_reward=800, prerequisites=["q1"])
        
        self.quest_master.quests = {"q1": quest1, "q2": quest2}
        
        self.planner = QuestPlanner(self.quest_master, self.todo_manager)
    
    def test_planner_initialization(self):
        """Test QuestPlanner initialization."""
        self.assertEqual(self.planner.quest_master, self.quest_master)
        self.assertEqual(self.planner.todo_manager, self.todo_manager)
        self.assertIsInstance(self.planner.prerequisite_analyzer, PrerequisiteAnalyzer)
        self.assertIsInstance(self.planner.plans, dict)
    
    def test_create_optimization_plan(self):
        """Test creating optimization plan."""
        plan = self.planner.create_optimization_plan()
        
        self.assertIn('target_quests', plan)
        self.assertIn('estimated_time', plan)
        self.assertIn('total_xp', plan)
        self.assertIn('quest_order', plan)
        self.assertIn('efficiency_score', plan)
    
    def test_create_planet_completion_plan(self):
        """Test creating planet completion plan."""
        plan = self.planner.create_planet_completion_plan("tatooine")
        
        self.assertIn('target_quests', plan)
        self.assertIn('quest_order', plan)
        self.assertIn('prerequisites', plan)
    
    def test_get_quest_recommendations(self):
        """Test getting quest recommendations."""
        recommendations = self.planner.get_quest_recommendations(
            preferred_planets=["tatooine"]
        )
        
        self.assertIsInstance(recommendations, list)
        if recommendations:
            self.assertIn('quest_id', recommendations[0])
            self.assertIn('quest_name', recommendations[0])
            self.assertIn('score', recommendations[0])
            self.assertIn('reasons', recommendations[0])
    
    def test_save_and_load_plan(self):
        """Test saving and loading plans."""
        plan = {"test": "data"}
        
        self.planner.save_plan("test_plan", plan)
        self.assertIn("test_plan", self.planner.plans)
        
        loaded_plan = self.planner.load_plan("test_plan")
        self.assertEqual(loaded_plan, plan)
        
        # Test non-existent plan
        loaded_plan = self.planner.load_plan("non_existent")
        self.assertIsNone(loaded_plan)


class TestPrerequisiteAnalyzer(unittest.TestCase):
    """Test PrerequisiteAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.quest_master = QuestMaster()
        
        # Create quests with dependencies
        quest1 = QuestData(id="q1", name="Quest 1", planet="tatooine", prerequisites=[])
        quest2 = QuestData(id="q2", name="Quest 2", planet="naboo", prerequisites=["q1"])
        quest3 = QuestData(id="q3", name="Quest 3", planet="corellia", prerequisites=["q2"])
        
        self.quest_master.quests = {"q1": quest1, "q2": quest2, "q3": quest3}
        
        self.analyzer = PrerequisiteAnalyzer(self.quest_master)
    
    def test_analyzer_initialization(self):
        """Test PrerequisiteAnalyzer initialization."""
        self.assertEqual(self.analyzer.quest_master, self.quest_master)
        self.assertIsInstance(self.analyzer.dependency_graph, dict)
        self.assertIsInstance(self.analyzer.reverse_dependencies, dict)
    
    def test_get_direct_prerequisites(self):
        """Test getting direct prerequisites."""
        prereqs = self.analyzer.get_direct_prerequisites("q2")
        self.assertEqual(len(prereqs), 1)
        self.assertEqual(prereqs[0].id, "q1")
    
    def test_get_all_prerequisites(self):
        """Test getting all prerequisites."""
        prereqs = self.analyzer.get_all_prerequisites("q3")
        self.assertEqual(len(prereqs), 2)  # q1 and q2
        prereq_ids = [p.id for p in prereqs]
        self.assertIn("q1", prereq_ids)
        self.assertIn("q2", prereq_ids)
    
    def test_get_dependents(self):
        """Test getting dependents."""
        dependents = self.analyzer.get_dependents("q1")
        self.assertEqual(len(dependents), 1)
        self.assertEqual(dependents[0].id, "q2")
    
    def test_check_prerequisites_met(self):
        """Test checking if prerequisites are met."""
        # Initially, q2 prerequisites are not met
        self.assertFalse(self.analyzer.check_prerequisites_met("q2"))
        
        # After completing q1, prerequisites should be met
        self.quest_master.quests["q1"].status = QuestStatus.COMPLETED
        self.assertTrue(self.analyzer.check_prerequisites_met("q2"))
    
    def test_get_blocking_quests(self):
        """Test getting blocking quests."""
        blockers = self.analyzer.get_blocking_quests("q2")
        self.assertEqual(len(blockers), 1)
        self.assertEqual(blockers[0].id, "q1")
    
    def test_get_quest_chain(self):
        """Test getting quest chain."""
        chain = self.analyzer.get_quest_chain("q3")
        
        self.assertIsNotNone(chain)
        self.assertEqual(chain.id, "chain_q3")
        self.assertEqual(len(chain.quests), 3)  # q1, q2, q3
        self.assertEqual(chain.total_xp, 0)  # No XP set in test quests
        self.assertIsInstance(chain.estimated_time, int)


class TestTodoDashboard(unittest.TestCase):
    """Test TodoDashboard class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.dashboard = TodoDashboard(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_dashboard_initialization(self):
        """Test TodoDashboard initialization."""
        self.assertEqual(self.dashboard.output_dir, Path(self.temp_dir))
        self.assertTrue(self.dashboard.output_dir.exists())
    
    def test_generate_dashboard(self):
        """Test dashboard generation."""
        quests = [
            QuestData(id="q1", name="Test Quest", planet="tatooine", xp_reward=500)
        ]
        todos = [
            TodoItem(id="t1", title="Test Todo", category=TodoCategory.QUEST)
        ]
        progress_tracker = ProgressTracker()
        
        html = self.dashboard.generate_dashboard(quests, todos, progress_tracker)
        
        self.assertIsInstance(html, str)
        self.assertIn("SWGR Todo Tracker", html)
        self.assertIn("Test Quest", html)
        self.assertIn("Test Todo", html)
    
    def test_save_dashboard(self):
        """Test saving dashboard."""
        quests = [QuestData(id="q1", name="Test Quest", planet="tatooine")]
        todos = [TodoItem(id="t1", title="Test Todo")]
        progress_tracker = ProgressTracker()
        
        output_file = self.dashboard.save_dashboard(quests, todos, progress_tracker)
        
        self.assertTrue(Path(output_file).exists())
        self.assertTrue(Path(output_file).stat().st_size > 0)


class TestCLIInterface(unittest.TestCase):
    """Test CLI interface functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.quest_master = QuestMaster()
        self.todo_manager = TodoManager()
        self.progress_tracker = ProgressTracker()
        
        # Add sample data
        quest1 = QuestData(id="q1", name="Test Quest", planet="tatooine", xp_reward=500)
        quest2 = QuestData(id="q2", name="Another Quest", planet="naboo", xp_reward=800)
        self.quest_master.quests = {"q1": quest1, "q2": quest2}
        
        todo1 = TodoItem(id="t1", title="Test Todo", category=TodoCategory.QUEST)
        todo2 = TodoItem(id="t2", title="Another Todo", category=TodoCategory.COLLECTION)
        self.todo_manager.todos = {"t1": todo1, "t2": todo2}
    
    def test_display_quest_list(self):
        """Test displaying quest list."""
        quests = list(self.quest_master.quests.values())
        
        # This should not raise any exceptions
        display_quest_list(quests)
    
    def test_display_todo_list(self):
        """Test displaying todo list."""
        todos = list(self.todo_manager.todos.values())
        
        # This should not raise any exceptions
        display_todo_list(todos)
    
    def test_display_progress_summary(self):
        """Test displaying progress summary."""
        # Update progress first
        quests = list(self.quest_master.quests.values())
        todos = list(self.todo_manager.todos.values())
        self.progress_tracker.update_progress(quests, todos)
        
        # This should not raise any exceptions
        display_progress_summary(self.progress_tracker)


class TestIntegration(unittest.TestCase):
    """Test integration between components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.quest_master = QuestMaster()
        self.todo_manager = TodoManager()
        self.progress_tracker = ProgressTracker()
        self.planner = QuestPlanner(self.quest_master, self.todo_manager)
    
    def test_full_workflow(self):
        """Test complete workflow from quest creation to completion tracking."""
        # 1. Create quests
        quest1 = QuestData(id="q1", name="Quest 1", planet="tatooine", xp_reward=500)
        quest2 = QuestData(id="q2", name="Quest 2", planet="naboo", xp_reward=800, prerequisites=["q1"])
        
        self.quest_master.quests = {"q1": quest1, "q2": quest2}
        
        # 2. Add todos
        todo_id = self.todo_manager.add_todo_item(
            title="Complete Quest 1",
            category=TodoCategory.QUEST,
            priority=QuestPriority.HIGH
        )
        
        # 3. Update progress
        quests = list(self.quest_master.quests.values())
        todos = list(self.todo_manager.todos.values())
        self.progress_tracker.update_progress(quests, todos)
        
        # 4. Record completion
        self.progress_tracker.record_completion("q1", "quest", 30, "tatooine", "quest")
        
        # 5. Update quest status
        self.quest_master.update_quest_status("q1", QuestStatus.COMPLETED)
        
        # 6. Check available quests
        available = self.quest_master.get_available_quests()
        self.assertEqual(len(available), 1)  # Only q2 should be available now
        self.assertEqual(available[0].id, "q2")
        
        # 7. Create plan
        plan = self.planner.create_optimization_plan()
        self.assertIn('target_quests', plan)
        self.assertIn('quest_order', plan)
        
        # 8. Generate dashboard
        dashboard = TodoDashboard()
        html = dashboard.generate_dashboard(quests, todos, self.progress_tracker)
        self.assertIn("SWGR Todo Tracker", html)
    
    def test_error_handling(self):
        """Test error handling scenarios."""
        # Test with invalid quest status
        with self.assertRaises(ValueError):
            QuestStatus("invalid_status")
        
        # Test with invalid priority
        with self.assertRaises(ValueError):
            QuestPriority("invalid_priority")
        
        # Test with invalid category
        with self.assertRaises(ValueError):
            TodoCategory("invalid_category")


def main():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestQuestData,
        TestQuestMaster,
        TestTodoItem,
        TestTodoManager,
        TestProgressTracker,
        TestQuestPlanner,
        TestPrerequisiteAnalyzer,
        TestTodoDashboard,
        TestCLIInterface,
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
    print(f"Test Summary:")
    print(f"  Tests run: {result.testsRun}")
    print(f"  Failures: {len(result.failures)}")
    print(f"  Errors: {len(result.errors)}")
    print(f"  Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print(f"{'='*60}")
    
    return len(result.failures) + len(result.errors)


if __name__ == "__main__":
    exit(main()) 