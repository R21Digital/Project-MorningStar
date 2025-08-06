#!/usr/bin/env python3
"""
Batch 169 - Multi-Client Orchestrator & Scheduler Tests

Comprehensive test suite for the orchestrator functionality including:
- Agent registry tests
- Scheduler tests
- Fleet plan tests
- Integration tests
"""

import unittest
import json
import tempfile
import shutil
import time
from datetime import datetime, timedelta, time as dt_time
from pathlib import Path
from unittest.mock import patch, MagicMock

from orchestrator.agent_registry import (
    AgentRegistry, Agent, AgentStatus, AgentHealth, AgentCapability,
    register_agent, unregister_agent, update_agent_heartbeat, check_agent_health,
    get_agent_status, get_all_agents, get_agent_capabilities
)

from orchestrator.scheduler import (
    FleetScheduler, ScheduleTask, SchedulePriority, ScheduleStatus, ScheduleConstraint,
    create_schedule_task, get_next_scheduled_task, update_task_status,
    get_schedule_summary, validate_schedule_constraints, apply_anti_pattern_rules,
    ScheduleWindow
)

class TestAgentRegistry(unittest.TestCase):
    """Test cases for Agent Registry functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.registry_file = Path(self.temp_dir) / "test_agent_registry.json"
        self.registry = AgentRegistry(str(self.registry_file))
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_register_agent(self):
        """Test agent registration."""
        agent = register_agent(
            name="TestAgent",
            machine_id="TEST-MACHINE",
            window_id="TEST-WINDOW",
            capabilities={AgentCapability.QUEST, AgentCapability.COMBAT},
            config_path="config/test_agent.json"
        )
        
        self.assertEqual(agent.name, "TestAgent")
        self.assertEqual(agent.machine_id, "TEST-MACHINE")
        self.assertEqual(agent.window_id, "TEST-WINDOW")
        self.assertEqual(agent.status, AgentStatus.ONLINE)
        self.assertEqual(agent.health, AgentHealth.HEALTHY)
        self.assertEqual(agent.capabilities, {AgentCapability.QUEST, AgentCapability.COMBAT})
        self.assertIsNone(agent.current_mode)
        self.assertEqual(agent.error_count, 0)
        self.assertIsNone(agent.last_error)
    
    def test_register_duplicate_agent(self):
        """Test registering duplicate agent raises error."""
        register_agent(
            name="TestAgent",
            machine_id="TEST-MACHINE",
            window_id="TEST-WINDOW",
            capabilities={AgentCapability.QUEST}
        )
        
        with self.assertRaises(ValueError):
            register_agent(
                name="TestAgent",
                machine_id="TEST-MACHINE",
                window_id="TEST-WINDOW",
                capabilities={AgentCapability.QUEST}
            )
    
    def test_unregister_agent(self):
        """Test agent unregistration."""
        register_agent(
            name="TestAgent",
            machine_id="TEST-MACHINE",
            window_id="TEST-WINDOW",
            capabilities={AgentCapability.QUEST}
        )
        
        result = unregister_agent("TestAgent")
        self.assertTrue(result)
        
        # Try to unregister again
        result = unregister_agent("TestAgent")
        self.assertFalse(result)
    
    def test_update_heartbeat(self):
        """Test heartbeat updates."""
        register_agent(
            name="TestAgent",
            machine_id="TEST-MACHINE",
            window_id="TEST-WINDOW",
            capabilities={AgentCapability.QUEST}
        )
        
        # Update heartbeat
        result = update_agent_heartbeat(
            "TestAgent",
            AgentStatus.BUSY,
            "quest",
            {"cpu_usage": 50.0}
        )
        self.assertTrue(result)
        
        agent = self.registry.get_agent("TestAgent")
        self.assertEqual(agent.status, AgentStatus.BUSY)
        self.assertEqual(agent.current_mode, "quest")
        self.assertEqual(agent.performance_metrics["cpu_usage"], 50.0)
    
    def test_update_nonexistent_agent_heartbeat(self):
        """Test updating heartbeat for nonexistent agent."""
        result = update_agent_heartbeat("NonexistentAgent", AgentStatus.ONLINE)
        self.assertFalse(result)
    
    def test_check_agent_health(self):
        """Test agent health checking."""
        register_agent(
            name="TestAgent",
            machine_id="TEST-MACHINE",
            window_id="TEST-WINDOW",
            capabilities={AgentCapability.QUEST}
        )
        
        # Check healthy agent
        health = check_agent_health("TestAgent")
        self.assertEqual(health, AgentHealth.HEALTHY)
        
        # Report errors to make agent unhealthy
        self.registry.report_error("TestAgent", "Test error 1")
        self.registry.report_error("TestAgent", "Test error 2")
        self.registry.report_error("TestAgent", "Test error 3")
        self.registry.report_error("TestAgent", "Test error 4")
        self.registry.report_error("TestAgent", "Test error 5")
        
        health = check_agent_health("TestAgent")
        self.assertEqual(health, AgentHealth.WARNING)
        
        # Add more errors to make critical
        for i in range(6, 12):
            self.registry.report_error("TestAgent", f"Test error {i}")
        
        health = check_agent_health("TestAgent")
        self.assertEqual(health, AgentHealth.CRITICAL)
    
    def test_agent_heartbeat_timeout(self):
        """Test agent heartbeat timeout detection."""
        agent = register_agent(
            name="TestAgent",
            machine_id="TEST-MACHINE",
            window_id="TEST-WINDOW",
            capabilities={AgentCapability.QUEST}
        )
        
        # Set heartbeat to old time
        agent.last_heartbeat = datetime.now() - timedelta(seconds=40)
        self.registry._save_registry()
        
        health = check_agent_health("TestAgent")
        self.assertEqual(health, AgentHealth.CRITICAL)
        
        agent = self.registry.get_agent("TestAgent")
        self.assertEqual(agent.status, AgentStatus.OFFLINE)
    
    def test_get_agents_by_status(self):
        """Test getting agents by status."""
        register_agent("Agent1", "MACHINE1", "WINDOW1", {AgentCapability.QUEST})
        register_agent("Agent2", "MACHINE2", "WINDOW2", {AgentCapability.COMBAT})
        
        update_agent_heartbeat("Agent1", AgentStatus.ONLINE)
        update_agent_heartbeat("Agent2", AgentStatus.BUSY)
        
        online_agents = self.registry.get_agents_by_status(AgentStatus.ONLINE)
        self.assertEqual(len(online_agents), 1)
        self.assertEqual(online_agents[0].name, "Agent1")
        
        busy_agents = self.registry.get_agents_by_status(AgentStatus.BUSY)
        self.assertEqual(len(busy_agents), 1)
        self.assertEqual(busy_agents[0].name, "Agent2")
    
    def test_get_agents_by_capability(self):
        """Test getting agents by capability."""
        register_agent("Agent1", "MACHINE1", "WINDOW1", {AgentCapability.QUEST})
        register_agent("Agent2", "MACHINE2", "WINDOW2", {AgentCapability.COMBAT})
        register_agent("Agent3", "MACHINE3", "WINDOW3", {AgentCapability.QUEST, AgentCapability.COMBAT})
        
        quest_agents = self.registry.get_agents_by_capability(AgentCapability.QUEST)
        self.assertEqual(len(quest_agents), 2)
        
        combat_agents = self.registry.get_agents_by_capability(AgentCapability.COMBAT)
        self.assertEqual(len(combat_agents), 2)
        
        crafting_agents = self.registry.get_agents_by_capability(AgentCapability.CRAFTING)
        self.assertEqual(len(crafting_agents), 0)
    
    def test_registry_summary(self):
        """Test registry summary generation."""
        register_agent("Agent1", "MACHINE1", "WINDOW1", {AgentCapability.QUEST})
        register_agent("Agent2", "MACHINE2", "WINDOW2", {AgentCapability.COMBAT})
        
        update_agent_heartbeat("Agent1", AgentStatus.ONLINE)
        update_agent_heartbeat("Agent2", AgentStatus.BUSY)
        
        summary = self.registry.get_registry_summary()
        
        self.assertEqual(summary["total_agents"], 2)
        self.assertEqual(summary["online_agents"], 1)
        self.assertEqual(summary["busy_agents"], 1)
        self.assertEqual(summary["healthy_agents"], 2)
        
        self.assertIn("agents_by_status", summary)
        self.assertIn("agents_by_health", summary)
    
    def test_agent_serialization(self):
        """Test agent serialization and deserialization."""
        agent = register_agent(
            name="TestAgent",
            machine_id="TEST-MACHINE",
            window_id="TEST-WINDOW",
            capabilities={AgentCapability.QUEST, AgentCapability.COMBAT}
        )
        
        # Serialize
        serialized = self.registry._serialize_agent(agent)
        
        # Deserialize
        deserialized = self.registry._deserialize_agent(serialized)
        
        self.assertEqual(deserialized.name, agent.name)
        self.assertEqual(deserialized.machine_id, agent.machine_id)
        self.assertEqual(deserialized.capabilities, agent.capabilities)
        self.assertEqual(deserialized.status, agent.status)
        self.assertEqual(deserialized.health, agent.health)

class TestFleetScheduler(unittest.TestCase):
    """Test cases for Fleet Scheduler functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.schedule_file = Path(self.temp_dir) / "test_fleet_schedule.json"
        self.scheduler = FleetScheduler(str(self.schedule_file))
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_create_task(self):
        """Test task creation."""
        task = create_schedule_task(
            name="Test Task",
            mode="quest",
            agent_name="TestAgent",
            priority=SchedulePriority.HIGH,
            scheduled_for=datetime.now() + timedelta(hours=1),
            estimated_duration=timedelta(hours=2),
            constraints={ScheduleConstraint.DAILY_CAP: 3},
            daily_cap=3,
            metadata={"test": "data"}
        )
        
        self.assertEqual(task.name, "Test Task")
        self.assertEqual(task.mode, "quest")
        self.assertEqual(task.agent_name, "TestAgent")
        self.assertEqual(task.priority, SchedulePriority.HIGH)
        self.assertEqual(task.status, ScheduleStatus.PENDING)
        self.assertEqual(task.daily_cap, 3)
        self.assertEqual(task.metadata["test"], "data")
    
    def test_get_next_task(self):
        """Test getting next task."""
        # Create task scheduled for now
        task = create_schedule_task(
            name="Test Task",
            mode="quest",
            agent_name="TestAgent",
            scheduled_for=datetime.now(),
            estimated_duration=timedelta(hours=1)
        )
        
        next_task = get_next_scheduled_task("TestAgent")
        self.assertIsNotNone(next_task)
        self.assertEqual(next_task.id, task.id)
        
        # Test with different agent
        next_task = get_next_scheduled_task("DifferentAgent")
        self.assertIsNone(next_task)
    
    def test_task_constraints(self):
        """Test task constraint validation."""
        # Create task with daily cap
        task = create_schedule_task(
            name="Test Task",
            mode="quest",
            agent_name="TestAgent",
            constraints={ScheduleConstraint.DAILY_CAP: 1},
            daily_cap=1,
            current_daily_count=1  # Already at cap
        )
        
        # Task should not be available due to daily cap
        next_task = get_next_scheduled_task("TestAgent")
        self.assertIsNone(next_task)
    
    def test_anti_pattern_rules(self):
        """Test anti-pattern rule application."""
        # Create task with anti-pattern rule
        task = create_schedule_task(
            name="Test Task",
            mode="quest",
            agent_name="TestAgent",
            anti_pattern_rules=[
                {
                    "type": "idle_block",
                    "idle_start": "00:00",
                    "idle_end": "23:59"
                }
            ]
        )
        
        # Task should be blocked by idle block rule
        next_task = get_next_scheduled_task("TestAgent")
        self.assertIsNone(next_task)
    
    def test_task_status_updates(self):
        """Test task status updates."""
        task = create_schedule_task(
            name="Test Task",
            mode="quest",
            agent_name="TestAgent",
            scheduled_for=datetime.now()
        )
        
        # Start task
        update_task_status(task.id, ScheduleStatus.RUNNING)
        updated_task = self.scheduler.tasks[task.id]
        self.assertEqual(updated_task.status, ScheduleStatus.RUNNING)
        self.assertIsNotNone(updated_task.started_at)
        
        # Complete task
        update_task_status(task.id, ScheduleStatus.COMPLETED, success=True)
        updated_task = self.scheduler.tasks[task.id]
        self.assertEqual(updated_task.status, ScheduleStatus.COMPLETED)
        self.assertIsNotNone(updated_task.completed_at)
        self.assertEqual(updated_task.current_daily_count, 1)
        self.assertEqual(updated_task.current_weekly_count, 1)
        
        # Fail task
        task2 = create_schedule_task(
            name="Test Task 2",
            mode="quest",
            agent_name="TestAgent",
            scheduled_for=datetime.now()
        )
        
        update_task_status(task2.id, ScheduleStatus.FAILED, success=False, error_message="Test error")
        updated_task2 = self.scheduler.tasks[task2.id]
        self.assertEqual(updated_task2.status, ScheduleStatus.FAILED)
        self.assertEqual(updated_task2.error_count, 1)
        self.assertEqual(updated_task2.last_error, "Test error")
    
    def test_schedule_windows(self):
        """Test schedule window functionality."""
        # Create schedule window
        window = ScheduleWindow(
            start_time=dt_time(9, 0),
            end_time=dt_time(17, 0),
            days_of_week={0, 1, 2, 3, 4, 5, 6},
            priority_boost=1.5
        )
        
        self.scheduler.add_schedule_window("work_hours", window)
        
        # Verify window was added
        self.assertIn("work_hours", self.scheduler.schedule_windows)
        stored_window = self.scheduler.schedule_windows["work_hours"]
        self.assertEqual(stored_window.start_time, dt_time(9, 0))
        self.assertEqual(stored_window.end_time, dt_time(17, 0))
        self.assertEqual(stored_window.priority_boost, 1.5)
    
    def test_anti_pattern_rules(self):
        """Test anti-pattern rule management."""
        rule = {
            "type": "recent_failure",
            "timeout": 3600,
            "max_failures": 3,
            "description": "Test rule"
        }
        
        self.scheduler.add_anti_pattern_rule("test_rule", rule)
        
        # Verify rule was added
        self.assertIn("test_rule", self.scheduler.anti_patterns)
        stored_rule = self.scheduler.anti_patterns["test_rule"]
        self.assertEqual(stored_rule["type"], "recent_failure")
        self.assertEqual(stored_rule["timeout"], 3600)
    
    def test_schedule_summary(self):
        """Test schedule summary generation."""
        # Create tasks in different states
        create_schedule_task("Task1", "quest", "Agent1", scheduled_for=datetime.now())
        create_schedule_task("Task2", "quest", "Agent2", scheduled_for=datetime.now())
        
        # Start one task
        tasks = list(self.scheduler.tasks.values())
        update_task_status(tasks[0].id, ScheduleStatus.RUNNING)
        
        summary = get_schedule_summary()
        
        self.assertEqual(summary["total_tasks"], 2)
        self.assertEqual(summary["pending_tasks"], 1)
        self.assertEqual(summary["running_tasks"], 1)
        self.assertEqual(summary["completed_tasks"], 0)
        self.assertEqual(summary["failed_tasks"], 0)
        
        self.assertIn("tasks_by_priority", summary)
        self.assertIn("tasks_by_status", summary)
    
    def test_task_serialization(self):
        """Test task serialization and deserialization."""
        task = create_schedule_task(
            name="Test Task",
            mode="quest",
            agent_name="TestAgent",
            priority=SchedulePriority.HIGH,
            scheduled_for=datetime.now(),
            estimated_duration=timedelta(hours=1),
            constraints={ScheduleConstraint.DAILY_CAP: 3},
            daily_cap=3
        )
        
        # Serialize
        serialized = self.scheduler._serialize_task(task)
        
        # Deserialize
        deserialized = self.scheduler._deserialize_task(serialized)
        
        self.assertEqual(deserialized.name, task.name)
        self.assertEqual(deserialized.mode, task.mode)
        self.assertEqual(deserialized.priority, task.priority)
        self.assertEqual(deserialized.status, task.status)
        self.assertEqual(deserialized.daily_cap, task.daily_cap)

class TestFleetPlan(unittest.TestCase):
    """Test cases for Fleet Plan functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.fleet_plan_file = Path(self.temp_dir) / "test_fleet_plan.json"
        
        # Create test fleet plan
        self.fleet_plan = {
            "fleet_name": "Test Fleet",
            "description": "Test fleet for unit testing",
            "version": "1.0.0",
            "agents": [
                {
                    "name": "TestAgent",
                    "machine_id": "TEST-MACHINE",
                    "window_id": "TEST-WINDOW",
                    "mode": "quest",
                    "capabilities": ["quest", "combat"],
                    "config_path": "config/test_agent.json",
                    "priority": "high",
                    "auto_start": True,
                    "heartbeat_interval": 30,
                    "performance_thresholds": {
                        "cpu_max": 80.0,
                        "memory_max": 85.0,
                        "response_time_max": 5000
                    },
                    "schedule_preferences": {
                        "preferred_hours": [9, 10, 11, 12],
                        "avoid_hours": [0, 1, 2, 3],
                        "max_daily_runtime": 8,
                        "cooldown_periods": [
                            {
                                "start": "12:00",
                                "end": "13:00",
                                "reason": "lunch_break"
                            }
                        ]
                    }
                }
            ],
            "schedule_windows": {
                "peak_hours": {
                    "start_time": "09:00",
                    "end_time": "17:00",
                    "days_of_week": [0, 1, 2, 3, 4],
                    "priority_boost": 1.5,
                    "description": "Peak activity hours"
                }
            },
            "anti_pattern_rules": {
                "recent_failure_cooldown": {
                    "type": "recent_failure",
                    "timeout": 3600,
                    "max_failures": 3,
                    "description": "Cooldown after recent task failures"
                }
            },
            "global_constraints": {
                "max_concurrent_agents": 4,
                "max_concurrent_combat": 2,
                "min_agent_health": "healthy"
            },
            "monitoring": {
                "health_check_interval": 60,
                "performance_monitoring": True,
                "error_tracking": True
            },
            "notifications": {
                "discord_webhook": "",
                "alert_channels": ["health", "performance"]
            },
            "backup": {
                "enabled": True,
                "backup_interval_hours": 6,
                "retention_days": 7
            }
        }
        
        with open(self.fleet_plan_file, 'w') as f:
            json.dump(self.fleet_plan, f, indent=2)
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_fleet_plan_loading(self):
        """Test fleet plan loading."""
        with open(self.fleet_plan_file, 'r') as f:
            loaded_plan = json.load(f)
        
        self.assertEqual(loaded_plan["fleet_name"], "Test Fleet")
        self.assertEqual(loaded_plan["description"], "Test fleet for unit testing")
        self.assertEqual(loaded_plan["version"], "1.0.0")
        
        # Check agents
        self.assertEqual(len(loaded_plan["agents"]), 1)
        agent = loaded_plan["agents"][0]
        self.assertEqual(agent["name"], "TestAgent")
        self.assertEqual(agent["mode"], "quest")
        self.assertEqual(agent["priority"], "high")
        self.assertTrue(agent["auto_start"])
        
        # Check capabilities
        self.assertEqual(agent["capabilities"], ["quest", "combat"])
        
        # Check schedule preferences
        prefs = agent["schedule_preferences"]
        self.assertEqual(prefs["max_daily_runtime"], 8)
        self.assertEqual(prefs["preferred_hours"], [9, 10, 11, 12])
        self.assertEqual(prefs["avoid_hours"], [0, 1, 2, 3])
        
        # Check global constraints
        constraints = loaded_plan["global_constraints"]
        self.assertEqual(constraints["max_concurrent_agents"], 4)
        self.assertEqual(constraints["max_concurrent_combat"], 2)
        self.assertEqual(constraints["min_agent_health"], "healthy")
    
    def test_fleet_plan_validation(self):
        """Test fleet plan validation."""
        # Test valid plan
        self.assertIsInstance(self.fleet_plan["agents"], list)
        self.assertIsInstance(self.fleet_plan["schedule_windows"], dict)
        self.assertIsInstance(self.fleet_plan["anti_pattern_rules"], dict)
        self.assertIsInstance(self.fleet_plan["global_constraints"], dict)
        
        # Test required fields
        required_fields = ["fleet_name", "description", "version", "agents"]
        for field in required_fields:
            self.assertIn(field, self.fleet_plan)
        
        # Test agent structure
        for agent in self.fleet_plan["agents"]:
            required_agent_fields = ["name", "machine_id", "window_id", "mode", "capabilities"]
            for field in required_agent_fields:
                self.assertIn(field, agent)

class TestIntegration(unittest.TestCase):
    """Integration tests for orchestrator components."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.registry_file = Path(self.temp_dir) / "test_agent_registry.json"
        self.schedule_file = Path(self.temp_dir) / "test_fleet_schedule.json"
        
        self.registry = AgentRegistry(str(self.registry_file))
        self.scheduler = FleetScheduler(str(self.schedule_file))
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_agent_scheduler_integration(self):
        """Test integration between agent registry and scheduler."""
        # Register agent
        agent = register_agent(
            name="TestAgent",
            machine_id="TEST-MACHINE",
            window_id="TEST-WINDOW",
            capabilities={AgentCapability.QUEST, AgentCapability.COMBAT}
        )
        
        # Create task for agent
        task = create_schedule_task(
            name="Test Task",
            mode="quest",
            agent_name="TestAgent",
            scheduled_for=datetime.now(),
            estimated_duration=timedelta(hours=1)
        )
        
        # Update agent status
        update_agent_heartbeat("TestAgent", AgentStatus.ONLINE, "quest")
        
        # Get next task for agent
        next_task = get_next_scheduled_task("TestAgent")
        self.assertIsNotNone(next_task)
        self.assertEqual(next_task.name, "Test Task")
        
        # Start task
        update_task_status(next_task.id, ScheduleStatus.RUNNING)
        
        # Update agent status to busy
        update_agent_heartbeat("TestAgent", AgentStatus.BUSY, "quest")
        
        # Verify agent is busy
        agent = self.registry.get_agent("TestAgent")
        self.assertEqual(agent.status, AgentStatus.BUSY)
        self.assertEqual(agent.current_mode, "quest")
    
    def test_health_monitoring_integration(self):
        """Test health monitoring integration."""
        # Register agent
        register_agent(
            name="TestAgent",
            machine_id="TEST-MACHINE",
            window_id="TEST-WINDOW",
            capabilities={AgentCapability.QUEST}
        )
        
        # Report errors
        self.registry.report_error("TestAgent", "Error 1")
        self.registry.report_error("TestAgent", "Error 2")
        self.registry.report_error("TestAgent", "Error 3")
        
        # Check health
        health = check_agent_health("TestAgent")
        self.assertEqual(health, AgentHealth.WARNING)
        
        # Create task with health constraint
        task = create_schedule_task(
            name="Test Task",
            mode="quest",
            agent_name="TestAgent",
            scheduled_for=datetime.now(),
            constraints={ScheduleConstraint.AGENT_CAPABILITY: AgentCapability.QUEST.value}
        )
        
        # Task should still be available despite health warning
        next_task = get_next_scheduled_task("TestAgent")
        self.assertIsNotNone(next_task)
    
    def test_schedule_constraints_integration(self):
        """Test schedule constraints integration."""
        # Register agent
        register_agent(
            name="TestAgent",
            machine_id="TEST-MACHINE",
            window_id="TEST-WINDOW",
            capabilities={AgentCapability.QUEST}
        )
        
        # Create task with daily cap
        task = create_schedule_task(
            name="Test Task",
            mode="quest",
            agent_name="TestAgent",
            scheduled_for=datetime.now(),
            daily_cap=2,
            current_daily_count=2  # At cap
        )
        
        # Task should not be available due to daily cap
        next_task = get_next_scheduled_task("TestAgent")
        self.assertIsNone(next_task)
        
        # Create task with capability constraint
        task2 = create_schedule_task(
            name="Test Task 2",
            mode="crafting",
            agent_name="TestAgent",
            scheduled_for=datetime.now(),
            constraints={ScheduleConstraint.AGENT_CAPABILITY: AgentCapability.CRAFTING.value}
        )
        
        # Task should not be available due to capability constraint
        next_task = get_next_scheduled_task("TestAgent")
        self.assertIsNone(next_task)

class TestPerformance(unittest.TestCase):
    """Performance tests for orchestrator components."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.registry_file = Path(self.temp_dir) / "test_agent_registry.json"
        self.schedule_file = Path(self.temp_dir) / "test_fleet_schedule.json"
        
        self.registry = AgentRegistry(str(self.registry_file))
        self.scheduler = FleetScheduler(str(self.schedule_file))
    
    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_bulk_agent_registration(self):
        """Test bulk agent registration performance."""
        start_time = time.time()
        
        # Register 100 agents
        for i in range(100):
            register_agent(
                name=f"Agent{i}",
                machine_id=f"MACHINE{i}",
                window_id=f"WINDOW{i}",
                capabilities={AgentCapability.QUEST, AgentCapability.COMBAT}
            )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within 5 seconds
        self.assertLess(duration, 5.0)
        
        # Verify all agents registered
        agents = get_all_agents()
        self.assertEqual(len(agents), 100)
    
    def test_bulk_task_creation(self):
        """Test bulk task creation performance."""
        # Register agent first
        register_agent(
            name="TestAgent",
            machine_id="TEST-MACHINE",
            window_id="TEST-WINDOW",
            capabilities={AgentCapability.QUEST}
        )
        
        start_time = time.time()
        
        # Create 100 tasks
        for i in range(100):
            create_schedule_task(
                name=f"Task{i}",
                mode="quest",
                agent_name="TestAgent",
                scheduled_for=datetime.now() + timedelta(minutes=i),
                estimated_duration=timedelta(hours=1)
            )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within 5 seconds
        self.assertLess(duration, 5.0)
        
        # Verify all tasks created
        summary = get_schedule_summary()
        self.assertEqual(summary["total_tasks"], 100)
    
    def test_heartbeat_update_performance(self):
        """Test heartbeat update performance."""
        # Register agent
        register_agent(
            name="TestAgent",
            machine_id="TEST-MACHINE",
            window_id="TEST-WINDOW",
            capabilities={AgentCapability.QUEST}
        )
        
        start_time = time.time()
        
        # Update heartbeat 1000 times
        for i in range(1000):
            update_agent_heartbeat(
                "TestAgent",
                AgentStatus.ONLINE,
                "quest",
                {"cpu_usage": i % 100}
            )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within 10 seconds
        self.assertLess(duration, 10.0)

def run_tests():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestAgentRegistry,
        TestFleetScheduler,
        TestFleetPlan,
        TestIntegration,
        TestPerformance
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
            print(f"• {test}: {traceback}")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"• {test}: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1) 