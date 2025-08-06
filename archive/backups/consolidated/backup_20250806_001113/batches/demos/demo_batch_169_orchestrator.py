#!/usr/bin/env python3
"""
Batch 169 - Multi-Client Orchestrator & Scheduler Demo

This demo showcases the complete orchestrator functionality including:
- Agent registration and health monitoring
- Task scheduling with constraints and anti-patterns
- Fleet plan management
- Real-time status tracking
"""

import json
import time
import threading
from datetime import datetime, timedelta, time as dt_time
from pathlib import Path

from orchestrator.agent_registry import (
    AgentRegistry, Agent, AgentStatus, AgentHealth, AgentCapability,
    register_agent, unregister_agent, update_agent_heartbeat, check_agent_health
)

from orchestrator.scheduler import (
    FleetScheduler, ScheduleTask, SchedulePriority, ScheduleStatus, ScheduleConstraint,
    create_schedule_task, get_next_scheduled_task, update_task_status,
    ScheduleWindow
)

def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_section(title: str):
    """Print a formatted section."""
    print(f"\n--- {title} ---")

def demo_agent_registry():
    """Demonstrate agent registry functionality."""
    print_header("Agent Registry Demo")
    
    # Initialize registry
    registry = AgentRegistry()
    
    # Register agents
    print_section("Registering Agents")
    
    # Main agent (quest mode)
    main_agent = register_agent(
        name="Main",
        machine_id="DESKTOP-ABC123",
        window_id="SWG_MAIN_01",
        capabilities={
            AgentCapability.QUEST,
            AgentCapability.COMBAT,
            AgentCapability.EXPLORATION,
            AgentCapability.SOCIAL
        },
        config_path="config/agent_main.json"
    )
    print(f"✓ Registered Main agent: {main_agent.name}")
    
    # Heals agent (medic follow mode)
    heals_agent = register_agent(
        name="Heals",
        machine_id="DESKTOP-ABC123",
        window_id="SWG_HEALS_01",
        capabilities={
            AgentCapability.MEDIC_FOLLOW,
            AgentCapability.COMBAT,
            AgentCapability.SOCIAL
        },
        config_path="config/agent_heals.json"
    )
    print(f"✓ Registered Heals agent: {heals_agent.name}")
    
    # Craft agent (crafting mode)
    craft_agent = register_agent(
        name="Craft",
        machine_id="DESKTOP-DEF456",
        window_id="SWG_CRAFT_01",
        capabilities={
            AgentCapability.CRAFTING,
            AgentCapability.TRADING,
            AgentCapability.SOCIAL
        },
        config_path="config/agent_craft.json"
    )
    print(f"✓ Registered Craft agent: {craft_agent.name}")
    
    # Farm agent (farming mode)
    farm_agent = register_agent(
        name="Farm",
        machine_id="DESKTOP-GHI789",
        window_id="SWG_FARM_01",
        capabilities={
            AgentCapability.FARMING,
            AgentCapability.COMBAT,
            AgentCapability.EXPLORATION
        },
        config_path="config/agent_farm.json"
    )
    print(f"✓ Registered Farm agent: {farm_agent.name}")
    
    # Update heartbeats
    print_section("Updating Agent Heartbeats")
    
    update_agent_heartbeat("Main", AgentStatus.ONLINE, "quest")
    update_agent_heartbeat("Heals", AgentStatus.ONLINE, "medic_follow")
    update_agent_heartbeat("Craft", AgentStatus.IDLE, None)
    update_agent_heartbeat("Farm", AgentStatus.OFFLINE, None)
    
    print("✓ Updated agent heartbeats")
    
    # Display agent status
    print_section("Agent Status")
    agents = registry.get_all_agents()
    for agent in agents:
        health = check_agent_health(agent.name)
        print(f"• {agent.name}: {agent.status.value} | {health.value} | {agent.current_mode or 'idle'}")
    
    # Get registry summary
    print_section("Registry Summary")
    summary = registry.get_registry_summary()
    print(f"Total agents: {summary['total_agents']}")
    print(f"Online agents: {summary['online_agents']}")
    print(f"Busy agents: {summary['busy_agents']}")
    print(f"Healthy agents: {summary['healthy_agents']}")
    
    return registry

def demo_scheduler():
    """Demonstrate scheduler functionality."""
    print_header("Fleet Scheduler Demo")
    
    scheduler = FleetScheduler()
    
    # Add schedule windows
    print_section("Setting Up Schedule Windows")
    
    peak_window = ScheduleWindow(
        start_time=dt_time(9, 0),
        end_time=dt_time(22, 0),
        days_of_week={0, 1, 2, 3, 4, 5, 6},
        priority_boost=1.5
    )
    scheduler.add_schedule_window("peak_hours", peak_window)
    print("✓ Added peak hours window (9:00-22:00)")
    
    off_peak_window = ScheduleWindow(
        start_time=dt_time(22, 0),
        end_time=dt_time(9, 0),
        days_of_week={0, 1, 2, 3, 4, 5, 6},
        priority_boost=0.7
    )
    scheduler.add_schedule_window("off_peak_hours", off_peak_window)
    print("✓ Added off-peak hours window (22:00-9:00)")
    
    # Add anti-pattern rules
    print_section("Setting Up Anti-Pattern Rules")
    
    scheduler.add_anti_pattern_rule("recent_failure_cooldown", {
        "type": "recent_failure",
        "timeout": 3600,
        "max_failures": 3,
        "description": "Cooldown after recent task failures"
    })
    print("✓ Added recent failure cooldown rule")
    
    scheduler.add_anti_pattern_rule("idle_block_night", {
        "type": "idle_block",
        "idle_start": "23:00",
        "idle_end": "06:00",
        "description": "Night idle block"
    })
    print("✓ Added night idle block rule")
    
    # Create scheduled tasks
    print_section("Creating Scheduled Tasks")
    
    # Quest task for Main agent
    quest_task = create_schedule_task(
        name="Daily Quest Run",
        mode="quest",
        agent_name="Main",
        priority=SchedulePriority.HIGH,
        scheduled_for=datetime.now() + timedelta(minutes=5),
        estimated_duration=timedelta(hours=2),
        constraints={
            ScheduleConstraint.DAILY_CAP: 3,
            ScheduleConstraint.TIME_WINDOW: "peak_hours",
            ScheduleConstraint.AGENT_CAPABILITY: AgentCapability.QUEST.value
        },
        anti_pattern_rules=[
            {
                "type": "recent_failure",
                "timeout": 3600,
                "max_failures": 2
            }
        ],
        daily_cap=3,
        metadata={"quest_type": "daily", "difficulty": "normal"}
    )
    print(f"✓ Created quest task: {quest_task.name}")
    
    # Medic follow task for Heals agent
    medic_task = create_schedule_task(
        name="Medic Support",
        mode="medic_follow",
        agent_name="Heals",
        priority=SchedulePriority.NORMAL,
        scheduled_for=datetime.now() + timedelta(minutes=10),
        estimated_duration=timedelta(hours=4),
        constraints={
            ScheduleConstraint.WEEKLY_CAP: 20,
            ScheduleConstraint.AGENT_CAPABILITY: AgentCapability.MEDIC_FOLLOW.value
        },
        weekly_cap=20,
        metadata={"support_type": "healing", "target_agent": "Main"}
    )
    print(f"✓ Created medic task: {medic_task.name}")
    
    # Crafting task for Craft agent
    craft_task = create_schedule_task(
        name="Crafting Session",
        mode="crafting",
        agent_name="Craft",
        priority=SchedulePriority.NORMAL,
        scheduled_for=datetime.now() + timedelta(minutes=15),
        estimated_duration=timedelta(hours=3),
        constraints={
            ScheduleConstraint.DAILY_CAP: 2,
            ScheduleConstraint.TIME_WINDOW: "peak_hours"
        },
        daily_cap=2,
        metadata={"craft_type": "weapons", "quality": "high"}
    )
    print(f"✓ Created crafting task: {craft_task.name}")
    
    # Farming task for Farm agent
    farm_task = create_schedule_task(
        name="Resource Farming",
        mode="farming",
        agent_name="Farm",
        priority=SchedulePriority.LOW,
        scheduled_for=datetime.now() + timedelta(minutes=20),
        estimated_duration=timedelta(hours=6),
        constraints={
            ScheduleConstraint.DAILY_CAP: 1,
            ScheduleConstraint.AGENT_CAPABILITY: AgentCapability.FARMING.value
        },
        daily_cap=1,
        metadata={"resource_type": "ore", "location": "Naboo"}
    )
    print(f"✓ Created farming task: {farm_task.name}")
    
    # Display schedule summary
    print_section("Schedule Summary")
    summary = scheduler.get_schedule_summary()
    print(f"Total tasks: {summary['total_tasks']}")
    print(f"Pending tasks: {summary['pending_tasks']}")
    print(f"Running tasks: {summary['running_tasks']}")
    print(f"Completed tasks: {summary['completed_tasks']}")
    print(f"Failed tasks: {summary['failed_tasks']}")
    
    return scheduler

def demo_task_execution():
    """Demonstrate task execution workflow."""
    print_header("Task Execution Demo")
    
    scheduler = FleetScheduler()
    
    # Simulate task execution
    print_section("Simulating Task Execution")
    
    # Get next task for Main agent
    next_task = get_next_scheduled_task("Main")
    if next_task:
        print(f"Next task for Main: {next_task.name} ({next_task.mode})")
        
        # Start task
        update_task_status(next_task.id, ScheduleStatus.RUNNING)
        print(f"✓ Started task: {next_task.name}")
        
        # Simulate task running
        time.sleep(2)
        
        # Complete task
        update_task_status(next_task.id, ScheduleStatus.COMPLETED, success=True)
        print(f"✓ Completed task: {next_task.name}")
    
    # Get next task for Heals agent
    next_task = get_next_scheduled_task("Heals")
    if next_task:
        print(f"Next task for Heals: {next_task.name} ({next_task.mode})")
        
        # Start task
        update_task_status(next_task.id, ScheduleStatus.RUNNING)
        print(f"✓ Started task: {next_task.name}")
        
        # Simulate task failure
        time.sleep(1)
        update_task_status(next_task.id, ScheduleStatus.FAILED, success=False, error_message="Connection timeout")
        print(f"✗ Failed task: {next_task.name}")
    
    # Display updated summary
    print_section("Updated Schedule Summary")
    summary = scheduler.get_schedule_summary()
    print(f"Total tasks: {summary['total_tasks']}")
    print(f"Pending tasks: {summary['pending_tasks']}")
    print(f"Running tasks: {summary['running_tasks']}")
    print(f"Completed tasks: {summary['completed_tasks']}")
    print(f"Failed tasks: {summary['failed_tasks']}")

def demo_fleet_plan():
    """Demonstrate fleet plan management."""
    print_header("Fleet Plan Demo")
    
    # Load fleet plan
    fleet_plan_path = Path("config/fleet_plan.json")
    if fleet_plan_path.exists():
        with open(fleet_plan_path, 'r') as f:
            fleet_plan = json.load(f)
        
        print_section("Fleet Plan Overview")
        print(f"Fleet Name: {fleet_plan['fleet_name']}")
        print(f"Description: {fleet_plan['description']}")
        print(f"Version: {fleet_plan['version']}")
        
        print_section("Agents Configuration")
        for agent in fleet_plan['agents']:
            print(f"• {agent['name']}: {agent['mode']} on {agent['machine_id']}")
            print(f"  Capabilities: {', '.join(agent['capabilities'])}")
            print(f"  Priority: {agent['priority']}")
            print(f"  Auto-start: {agent['auto_start']}")
            print(f"  Max daily runtime: {agent['schedule_preferences']['max_daily_runtime']}h")
            print()
        
        print_section("Global Constraints")
        for key, value in fleet_plan['global_constraints'].items():
            print(f"• {key}: {value}")
        
        print_section("Schedule Windows")
        for name, window in fleet_plan['schedule_windows'].items():
            print(f"• {name}: {window['start_time']} - {window['end_time']}")
            print(f"  Priority boost: {window['priority_boost']}")
            print(f"  Description: {window['description']}")
            print()
        
        print_section("Anti-Pattern Rules")
        for name, rule in fleet_plan['anti_pattern_rules'].items():
            print(f"• {name}: {rule['description']}")
            print(f"  Type: {rule['type']}")
            if 'timeout' in rule:
                print(f"  Timeout: {rule['timeout']}s")
            print()
    else:
        print("✗ Fleet plan file not found")

def demo_health_monitoring():
    """Demonstrate health monitoring functionality."""
    print_header("Health Monitoring Demo")
    
    registry = AgentRegistry()
    
    # Simulate agent health issues
    print_section("Simulating Health Issues")
    
    # Report errors for Main agent
    registry.report_error("Main", "Quest NPC not found")
    registry.report_error("Main", "Inventory full")
    registry.report_error("Main", "Connection lost")
    
    print("✓ Reported 3 errors for Main agent")
    
    # Check health status
    print_section("Health Status Check")
    agents = registry.get_all_agents()
    for agent in agents:
        health = check_agent_health(agent.name)
        print(f"• {agent.name}: {health.value} (errors: {agent.error_count})")
    
    # Simulate agent going offline
    print_section("Simulating Agent Offline")
    
    # Update Main agent heartbeat to simulate going offline
    main_agent = registry.get_agent("Main")
    if main_agent:
        # Set last heartbeat to 40 seconds ago (beyond timeout)
        main_agent.last_heartbeat = datetime.now() - timedelta(seconds=40)
        registry._save_registry()
        print("✓ Set Main agent heartbeat to 40 seconds ago")
        
        # Check health again
        health = check_agent_health("Main")
        print(f"• Main agent health: {health.value}")
        print(f"• Main agent status: {registry.get_agent('Main').status.value}")

def demo_performance_metrics():
    """Demonstrate performance metrics tracking."""
    print_header("Performance Metrics Demo")
    
    registry = AgentRegistry()
    
    # Update agents with performance metrics
    print_section("Updating Performance Metrics")
    
    update_agent_heartbeat(
        "Main",
        AgentStatus.BUSY,
        "quest",
        {
            "cpu_usage": 45.2,
            "memory_usage": 67.8,
            "response_time": 1200,
            "fps": 60,
            "network_latency": 85
        }
    )
    
    update_agent_heartbeat(
        "Heals",
        AgentStatus.ONLINE,
        "medic_follow",
        {
            "cpu_usage": 32.1,
            "memory_usage": 54.3,
            "response_time": 950,
            "fps": 60,
            "network_latency": 92
        }
    )
    
    update_agent_heartbeat(
        "Craft",
        AgentStatus.IDLE,
        None,
        {
            "cpu_usage": 28.7,
            "memory_usage": 48.9,
            "response_time": 1100,
            "fps": 60,
            "network_latency": 78
        }
    )
    
    print("✓ Updated performance metrics for all agents")
    
    # Display performance summary
    print_section("Performance Summary")
    agents = registry.get_all_agents()
    total_cpu = 0
    total_memory = 0
    total_response = 0
    
    for agent in agents:
        metrics = agent.performance_metrics
        if metrics:
            cpu = metrics.get('cpu_usage', 0)
            memory = metrics.get('memory_usage', 0)
            response = metrics.get('response_time', 0)
            
            total_cpu += cpu
            total_memory += memory
            total_response += response
            
            print(f"• {agent.name}:")
            print(f"  CPU: {cpu:.1f}%")
            print(f"  Memory: {memory:.1f}%")
            print(f"  Response: {response}ms")
            print()
    
    if agents:
        avg_cpu = total_cpu / len(agents)
        avg_memory = total_memory / len(agents)
        avg_response = total_response / len(agents)
        
        print(f"Average Performance:")
        print(f"• CPU Usage: {avg_cpu:.1f}%")
        print(f"• Memory Usage: {avg_memory:.1f}%")
        print(f"• Response Time: {avg_response:.0f}ms")

def main():
    """Run the complete orchestrator demo."""
    print_header("Batch 169 - Multi-Client Orchestrator & Scheduler Demo")
    print("This demo showcases the complete orchestrator functionality")
    print("including agent registration, task scheduling, and fleet management.")
    
    try:
        # Run all demos
        registry = demo_agent_registry()
        scheduler = demo_scheduler()
        demo_task_execution()
        demo_fleet_plan()
        demo_health_monitoring()
        demo_performance_metrics()
        
        print_header("Demo Complete")
        print("✓ All orchestrator features demonstrated successfully!")
        print("\nKey Features Demonstrated:")
        print("• Agent registration and health monitoring")
        print("• Task scheduling with constraints and anti-patterns")
        print("• Fleet plan management and configuration")
        print("• Performance metrics tracking")
        print("• Real-time status updates")
        print("• Error handling and recovery")
        
    except Exception as e:
        print(f"\n✗ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 