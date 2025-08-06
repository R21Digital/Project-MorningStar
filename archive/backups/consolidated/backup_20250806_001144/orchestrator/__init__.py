"""Multi-Client Orchestrator & Scheduler Module.

This module provides centralized control for managing multiple SWG client instances
across different machines/windows with coordinated scheduling and health monitoring.
"""

from .agent_registry import (
    AgentRegistry,
    Agent,
    AgentStatus,
    AgentHealth,
    AgentCapability,
    register_agent,
    unregister_agent,
    get_agent_status,
    get_all_agents,
    update_agent_heartbeat,
    check_agent_health,
    get_agent_capabilities
)

from .scheduler import (
    FleetScheduler,
    ScheduleTask,
    SchedulePriority,
    ScheduleStatus,
    ScheduleConstraint,
    ScheduleWindow,
    create_schedule_task,
    get_next_scheduled_task,
    update_task_status,
    get_schedule_summary,
    validate_schedule_constraints,
    apply_anti_pattern_rules
)

__all__ = [
    # Agent Registry
    "AgentRegistry",
    "Agent", 
    "AgentStatus",
    "AgentHealth",
    "AgentCapability",
    "register_agent",
    "unregister_agent", 
    "get_agent_status",
    "get_all_agents",
    "update_agent_heartbeat",
    "check_agent_health",
    "get_agent_capabilities",
    
    # Scheduler
    "FleetScheduler",
    "ScheduleTask",
    "SchedulePriority", 
    "ScheduleStatus",
    "ScheduleConstraint",
    "ScheduleWindow",
    "create_schedule_task",
    "get_next_scheduled_task",
    "update_task_status",
    "get_schedule_summary",
    "validate_schedule_constraints",
    "apply_anti_pattern_rules"
] 