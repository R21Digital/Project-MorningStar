"""Agent Registry for Multi-Client Orchestration.

This module manages the registration, health monitoring, and status tracking
of multiple SWG client instances across different machines/windows.
"""

import json
import logging
import threading
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, List, Optional, Any, Set
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class AgentStatus(Enum):
    """Agent operational status."""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    IDLE = "idle"
    ERROR = "error"
    MAINTENANCE = "maintenance"

class AgentHealth(Enum):
    """Agent health status."""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"

class AgentCapability(Enum):
    """Agent capabilities."""
    QUEST = "quest"
    COMBAT = "combat"
    CRAFTING = "crafting"
    FARMING = "farming"
    MEDIC_FOLLOW = "medic_follow"
    PVP = "pvp"
    TRADING = "trading"
    EXPLORATION = "exploration"
    SOCIAL = "social"

@dataclass
class Agent:
    """Represents a registered SWG client agent."""
    name: str
    machine_id: str
    window_id: str
    status: AgentStatus
    health: AgentHealth
    capabilities: Set[AgentCapability]
    current_mode: Optional[str]
    last_heartbeat: datetime
    uptime: timedelta
    performance_metrics: Dict[str, Any]
    error_count: int
    last_error: Optional[str]
    registration_time: datetime
    config_path: Optional[str]
    session_data: Dict[str, Any]

class AgentRegistry:
    """Central registry for managing multiple SWG client agents."""
    
    def __init__(self, registry_file: str = "data/agent_registry.json"):
        self.registry_file = Path(registry_file)
        self.agents: Dict[str, Agent] = {}
        self.heartbeat_timeout = 30  # seconds
        self.health_check_interval = 60  # seconds
        self.lock = threading.RLock()
        
        # Ensure data directory exists
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing registry
        self._load_registry()
        
        # Start health monitoring thread
        self._start_health_monitor()
    
    def _load_registry(self):
        """Load agent registry from file."""
        try:
            if self.registry_file.exists():
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)
                    for agent_data in data.get('agents', []):
                        agent = self._deserialize_agent(agent_data)
                        self.agents[agent.name] = agent
                logger.info(f"Loaded {len(self.agents)} agents from registry")
        except Exception as e:
            logger.error(f"Failed to load agent registry: {e}")
    
    def _save_registry(self):
        """Save agent registry to file."""
        try:
            with self.lock:
                data = {
                    'agents': [self._serialize_agent(agent) for agent in self.agents.values()],
                    'last_updated': datetime.now().isoformat()
                }
                with open(self.registry_file, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save agent registry: {e}")
    
    def _serialize_agent(self, agent: Agent) -> Dict[str, Any]:
        """Serialize agent to dictionary."""
        data = asdict(agent)
        data['capabilities'] = [cap.value for cap in agent.capabilities]
        data['status'] = agent.status.value
        data['health'] = agent.health.value
        return data
    
    def _deserialize_agent(self, data: Dict[str, Any]) -> Agent:
        """Deserialize agent from dictionary."""
        data['capabilities'] = {AgentCapability(cap) for cap in data['capabilities']}
        data['status'] = AgentStatus(data['status'])
        data['health'] = AgentHealth(data['health'])
        data['last_heartbeat'] = datetime.fromisoformat(data['last_heartbeat'])
        data['registration_time'] = datetime.fromisoformat(data['registration_time'])
        data['uptime'] = timedelta(seconds=data['uptime'])
        return Agent(**data)
    
    def register_agent(self, name: str, machine_id: str, window_id: str, 
                      capabilities: Set[AgentCapability], config_path: Optional[str] = None) -> Agent:
        """Register a new agent."""
        with self.lock:
            if name in self.agents:
                raise ValueError(f"Agent '{name}' already registered")
            
            agent = Agent(
                name=name,
                machine_id=machine_id,
                window_id=window_id,
                status=AgentStatus.ONLINE,
                health=AgentHealth.HEALTHY,
                capabilities=capabilities,
                current_mode=None,
                last_heartbeat=datetime.now(),
                uptime=timedelta(),
                performance_metrics={},
                error_count=0,
                last_error=None,
                registration_time=datetime.now(),
                config_path=config_path,
                session_data={}
            )
            
            self.agents[name] = agent
            self._save_registry()
            logger.info(f"Registered agent: {name} on {machine_id}")
            return agent
    
    def unregister_agent(self, name: str) -> bool:
        """Unregister an agent."""
        with self.lock:
            if name in self.agents:
                del self.agents[name]
                self._save_registry()
                logger.info(f"Unregistered agent: {name}")
                return True
            return False
    
    def update_heartbeat(self, name: str, status: Optional[AgentStatus] = None,
                        current_mode: Optional[str] = None, 
                        performance_metrics: Optional[Dict[str, Any]] = None) -> bool:
        """Update agent heartbeat and status."""
        with self.lock:
            if name not in self.agents:
                return False
            
            agent = self.agents[name]
            agent.last_heartbeat = datetime.now()
            
            if status:
                agent.status = status
            
            if current_mode:
                agent.current_mode = current_mode
            
            if performance_metrics:
                agent.performance_metrics.update(performance_metrics)
            
            # Update uptime
            agent.uptime = datetime.now() - agent.registration_time
            
            self._save_registry()
            return True
    
    def get_agent(self, name: str) -> Optional[Agent]:
        """Get agent by name."""
        return self.agents.get(name)
    
    def get_all_agents(self) -> List[Agent]:
        """Get all registered agents."""
        return list(self.agents.values())
    
    def get_agents_by_status(self, status: AgentStatus) -> List[Agent]:
        """Get agents by status."""
        return [agent for agent in self.agents.values() if agent.status == status]
    
    def get_agents_by_capability(self, capability: AgentCapability) -> List[Agent]:
        """Get agents with specific capability."""
        return [agent for agent in self.agents.values() if capability in agent.capabilities]
    
    def check_agent_health(self, name: str) -> AgentHealth:
        """Check agent health status."""
        agent = self.get_agent(name)
        if not agent:
            return AgentHealth.UNKNOWN
        
        # Check heartbeat timeout
        time_since_heartbeat = datetime.now() - agent.last_heartbeat
        if time_since_heartbeat.total_seconds() > self.heartbeat_timeout:
            agent.health = AgentHealth.CRITICAL
            agent.status = AgentStatus.OFFLINE
            return AgentHealth.CRITICAL
        
        # Check error count
        if agent.error_count > 10:
            agent.health = AgentHealth.CRITICAL
        elif agent.error_count > 5:
            agent.health = AgentHealth.WARNING
        else:
            agent.health = AgentHealth.HEALTHY
        
        return agent.health
    
    def report_error(self, name: str, error_message: str):
        """Report an error for an agent."""
        with self.lock:
            agent = self.get_agent(name)
            if agent:
                agent.error_count += 1
                agent.last_error = error_message
                agent.health = AgentHealth.WARNING
                self._save_registry()
                logger.warning(f"Agent {name} error: {error_message}")
    
    def _start_health_monitor(self):
        """Start background health monitoring thread."""
        def monitor_health():
            while True:
                try:
                    with self.lock:
                        for agent in self.agents.values():
                            self.check_agent_health(agent.name)
                    self._save_registry()
                except Exception as e:
                    logger.error(f"Health monitor error: {e}")
                
                time.sleep(self.health_check_interval)
        
        monitor_thread = threading.Thread(target=monitor_health, daemon=True)
        monitor_thread.start()
    
    def get_registry_summary(self) -> Dict[str, Any]:
        """Get registry summary statistics."""
        with self.lock:
            total_agents = len(self.agents)
            online_agents = len(self.get_agents_by_status(AgentStatus.ONLINE))
            busy_agents = len(self.get_agents_by_status(AgentStatus.BUSY))
            healthy_agents = len([a for a in self.agents.values() if a.health == AgentHealth.HEALTHY])
            
            return {
                'total_agents': total_agents,
                'online_agents': online_agents,
                'busy_agents': busy_agents,
                'healthy_agents': healthy_agents,
                'agents_by_status': {
                    status.value: len(self.get_agents_by_status(status))
                    for status in AgentStatus
                },
                'agents_by_health': {
                    health.value: len([a for a in self.agents.values() if a.health == health])
                    for health in AgentHealth
                }
            }

# Global registry instance
_registry: Optional[AgentRegistry] = None

def get_agent_registry() -> AgentRegistry:
    """Get global agent registry instance."""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry

# Convenience functions
def register_agent(name: str, machine_id: str, window_id: str, 
                  capabilities: Set[AgentCapability], config_path: Optional[str] = None) -> Agent:
    """Register a new agent."""
    return get_agent_registry().register_agent(name, machine_id, window_id, capabilities, config_path)

def unregister_agent(name: str) -> bool:
    """Unregister an agent."""
    return get_agent_registry().unregister_agent(name)

def get_agent_status(name: str) -> Optional[AgentStatus]:
    """Get agent status."""
    agent = get_agent_registry().get_agent(name)
    return agent.status if agent else None

def get_all_agents() -> List[Agent]:
    """Get all registered agents."""
    return get_agent_registry().get_all_agents()

def update_agent_heartbeat(name: str, status: Optional[AgentStatus] = None,
                          current_mode: Optional[str] = None,
                          performance_metrics: Optional[Dict[str, Any]] = None) -> bool:
    """Update agent heartbeat."""
    return get_agent_registry().update_heartbeat(name, status, current_mode, performance_metrics)

def check_agent_health(name: str) -> AgentHealth:
    """Check agent health."""
    return get_agent_registry().check_agent_health(name)

def get_agent_capabilities(name: str) -> Set[AgentCapability]:
    """Get agent capabilities."""
    agent = get_agent_registry().get_agent(name)
    return agent.capabilities if agent else set() 