import React, { useState, useEffect, useCallback } from 'react';
import './OrchestratorPanel.css';

interface Agent {
  name: string;
  machine_id: string;
  window_id: string;
  status: 'online' | 'offline' | 'busy' | 'idle' | 'error' | 'maintenance';
  health: 'healthy' | 'warning' | 'critical' | 'unknown';
  capabilities: string[];
  current_mode: string | null;
  last_heartbeat: string;
  uptime: string;
  performance_metrics: Record<string, any>;
  error_count: number;
  last_error: string | null;
  registration_time: string;
  config_path: string | null;
  session_data: Record<string, any>;
}

interface ScheduleTask {
  id: string;
  name: string;
  mode: string;
  agent_name: string | null;
  priority: 'critical' | 'high' | 'normal' | 'low' | 'maintenance';
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled' | 'paused';
  created_at: string;
  scheduled_for: string;
  started_at: string | null;
  completed_at: string | null;
  estimated_duration: string;
  actual_duration: string | null;
  constraints: Record<string, any>;
  anti_pattern_rules: any[];
  daily_cap: number | null;
  weekly_cap: number | null;
  current_daily_count: number;
  current_weekly_count: number;
  error_count: number;
  last_error: string | null;
  metadata: Record<string, any>;
}

interface FleetPlan {
  fleet_name: string;
  description: string;
  version: string;
  agents: Array<{
    name: string;
    machine_id: string;
    window_id: string;
    mode: string;
    capabilities: string[];
    config_path: string;
    priority: string;
    auto_start: boolean;
    heartbeat_interval: number;
    performance_thresholds: Record<string, number>;
    schedule_preferences: {
      preferred_hours: number[];
      avoid_hours: number[];
      max_daily_runtime: number;
      cooldown_periods: Array<{
        start: string;
        end: string;
        reason: string;
      }>;
    };
  }>;
  schedule_windows: Record<string, any>;
  anti_pattern_rules: Record<string, any>;
  global_constraints: Record<string, any>;
  monitoring: Record<string, any>;
  notifications: Record<string, any>;
  backup: Record<string, any>;
}

interface OrchestratorPanelProps {
  className?: string;
}

const OrchestratorPanel: React.FC<OrchestratorPanelProps> = ({ className = '' }) => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [tasks, setTasks] = useState<ScheduleTask[]>([]);
  const [fleetPlan, setFleetPlan] = useState<FleetPlan | null>(null);
  const [selectedTab, setSelectedTab] = useState<'agents' | 'tasks' | 'fleet' | 'monitoring'>('agents');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshInterval, setRefreshInterval] = useState(30000); // 30 seconds

  // Fetch data from backend
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch agents
      const agentsResponse = await fetch('/api/orchestrator/agents');
      if (agentsResponse.ok) {
        const agentsData = await agentsResponse.json();
        setAgents(agentsData.agents || []);
      }

      // Fetch tasks
      const tasksResponse = await fetch('/api/orchestrator/tasks');
      if (tasksResponse.ok) {
        const tasksData = await tasksResponse.json();
        setTasks(tasksData.tasks || []);
      }

      // Fetch fleet plan
      const fleetResponse = await fetch('/api/orchestrator/fleet-plan');
      if (fleetResponse.ok) {
        const fleetData = await fleetResponse.json();
        setFleetPlan(fleetData);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch data');
    } finally {
      setLoading(false);
    }
  }, []);

  // Auto-refresh data
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, refreshInterval);
    return () => clearInterval(interval);
  }, [fetchData, refreshInterval]);

  // Agent management functions
  const registerAgent = async (agentData: Partial<Agent>) => {
    try {
      const response = await fetch('/api/orchestrator/agents', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(agentData),
      });
      if (response.ok) {
        await fetchData();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to register agent');
    }
  };

  const unregisterAgent = async (agentName: string) => {
    try {
      const response = await fetch(`/api/orchestrator/agents/${agentName}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        await fetchData();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to unregister agent');
    }
  };

  const updateAgentHeartbeat = async (agentName: string, status?: string, mode?: string) => {
    try {
      const response = await fetch(`/api/orchestrator/agents/${agentName}/heartbeat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status, current_mode: mode }),
      });
      if (response.ok) {
        await fetchData();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update heartbeat');
    }
  };

  // Task management functions
  const createTask = async (taskData: Partial<ScheduleTask>) => {
    try {
      const response = await fetch('/api/orchestrator/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(taskData),
      });
      if (response.ok) {
        await fetchData();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create task');
    }
  };

  const updateTaskStatus = async (taskId: string, status: string, success?: boolean, errorMessage?: string) => {
    try {
      const response = await fetch(`/api/orchestrator/tasks/${taskId}/status`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status, success, error_message: errorMessage }),
      });
      if (response.ok) {
        await fetchData();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task status');
    }
  };

  // Utility functions
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return '#4CAF50';
      case 'busy': return '#FF9800';
      case 'offline': return '#F44336';
      case 'error': return '#D32F2F';
      case 'maintenance': return '#9C27B0';
      default: return '#757575';
    }
  };

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'healthy': return '#4CAF50';
      case 'warning': return '#FF9800';
      case 'critical': return '#F44336';
      default: return '#757575';
    }
  };

  const formatDuration = (duration: string) => {
    const seconds = parseInt(duration);
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  const formatDateTime = (dateTime: string) => {
    return new Date(dateTime).toLocaleString();
  };

  if (loading && agents.length === 0) {
    return (
      <div className={`orchestrator-panel ${className}`}>
        <div className="loading">Loading orchestrator data...</div>
      </div>
    );
  }

  return (
    <div className={`orchestrator-panel ${className}`}>
      <div className="orchestrator-header">
        <h2>Fleet Orchestrator</h2>
        <div className="header-controls">
          <button onClick={fetchData} className="refresh-btn">
            Refresh
          </button>
          <select 
            value={refreshInterval} 
            onChange={(e) => setRefreshInterval(Number(e.target.value))}
            className="refresh-interval"
          >
            <option value={10000}>10s</option>
            <option value={30000}>30s</option>
            <option value={60000}>1m</option>
            <option value={300000}>5m</option>
          </select>
        </div>
      </div>

      {error && (
        <div className="error-message">
          Error: {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      <div className="orchestrator-tabs">
        <button 
          className={`tab ${selectedTab === 'agents' ? 'active' : ''}`}
          onClick={() => setSelectedTab('agents')}
        >
          Agents ({agents.length})
        </button>
        <button 
          className={`tab ${selectedTab === 'tasks' ? 'active' : ''}`}
          onClick={() => setSelectedTab('tasks')}
        >
          Tasks ({tasks.length})
        </button>
        <button 
          className={`tab ${selectedTab === 'fleet' ? 'active' : ''}`}
          onClick={() => setSelectedTab('fleet')}
        >
          Fleet Plan
        </button>
        <button 
          className={`tab ${selectedTab === 'monitoring' ? 'active' : ''}`}
          onClick={() => setSelectedTab('monitoring')}
        >
          Monitoring
        </button>
      </div>

      <div className="orchestrator-content">
        {selectedTab === 'agents' && (
          <div className="agents-tab">
            <div className="agents-header">
              <h3>Registered Agents</h3>
              <button className="add-agent-btn">Add Agent</button>
            </div>
            
            <div className="agents-grid">
              {agents.map((agent) => (
                <div key={agent.name} className="agent-card">
                  <div className="agent-header">
                    <h4>{agent.name}</h4>
                    <div className="agent-status">
                      <span 
                        className="status-indicator" 
                        style={{ backgroundColor: getStatusColor(agent.status) }}
                      />
                      <span className="status-text">{agent.status}</span>
                    </div>
                  </div>
                  
                  <div className="agent-details">
                    <div className="detail-row">
                      <span className="label">Machine:</span>
                      <span className="value">{agent.machine_id}</span>
                    </div>
                    <div className="detail-row">
                      <span className="label">Window:</span>
                      <span className="value">{agent.window_id}</span>
                    </div>
                    <div className="detail-row">
                      <span className="label">Health:</span>
                      <span 
                        className="value health-indicator"
                        style={{ color: getHealthColor(agent.health) }}
                      >
                        {agent.health}
                      </span>
                    </div>
                    <div className="detail-row">
                      <span className="label">Mode:</span>
                      <span className="value">{agent.current_mode || 'idle'}</span>
                    </div>
                    <div className="detail-row">
                      <span className="label">Uptime:</span>
                      <span className="value">{formatDuration(agent.uptime)}</span>
                    </div>
                    <div className="detail-row">
                      <span className="label">Errors:</span>
                      <span className="value">{agent.error_count}</span>
                    </div>
                  </div>
                  
                  <div className="agent-capabilities">
                    <span className="label">Capabilities:</span>
                    <div className="capabilities-list">
                      {agent.capabilities.map((cap) => (
                        <span key={cap} className="capability-tag">{cap}</span>
                      ))}
                    </div>
                  </div>
                  
                  <div className="agent-actions">
                    <button 
                      onClick={() => updateAgentHeartbeat(agent.name, 'online')}
                      className="action-btn"
                    >
                      Online
                    </button>
                    <button 
                      onClick={() => updateAgentHeartbeat(agent.name, 'offline')}
                      className="action-btn"
                    >
                      Offline
                    </button>
                    <button 
                      onClick={() => unregisterAgent(agent.name)}
                      className="action-btn danger"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {selectedTab === 'tasks' && (
          <div className="tasks-tab">
            <div className="tasks-header">
              <h3>Scheduled Tasks</h3>
              <button className="add-task-btn">Add Task</button>
            </div>
            
            <div className="tasks-table">
              <table>
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Mode</th>
                    <th>Agent</th>
                    <th>Priority</th>
                    <th>Status</th>
                    <th>Scheduled For</th>
                    <th>Duration</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {tasks.map((task) => (
                    <tr key={task.id}>
                      <td>{task.name}</td>
                      <td>{task.mode}</td>
                      <td>{task.agent_name || 'Any'}</td>
                      <td>
                        <span className={`priority-badge priority-${task.priority}`}>
                          {task.priority}
                        </span>
                      </td>
                      <td>
                        <span 
                          className={`status-badge status-${task.status}`}
                          style={{ backgroundColor: getStatusColor(task.status) }}
                        >
                          {task.status}
                        </span>
                      </td>
                      <td>{formatDateTime(task.scheduled_for)}</td>
                      <td>{formatDuration(task.estimated_duration)}</td>
                      <td>
                        <div className="task-actions">
                          {task.status === 'pending' && (
                            <button 
                              onClick={() => updateTaskStatus(task.id, 'running')}
                              className="action-btn small"
                            >
                              Start
                            </button>
                          )}
                          {task.status === 'running' && (
                            <button 
                              onClick={() => updateTaskStatus(task.id, 'completed', true)}
                              className="action-btn small success"
                            >
                              Complete
                            </button>
                          )}
                          <button 
                            onClick={() => updateTaskStatus(task.id, 'cancelled')}
                            className="action-btn small danger"
                          >
                            Cancel
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {selectedTab === 'fleet' && fleetPlan && (
          <div className="fleet-tab">
            <div className="fleet-header">
              <h3>{fleetPlan.fleet_name}</h3>
              <p>{fleetPlan.description}</p>
            </div>
            
            <div className="fleet-overview">
              <div className="overview-card">
                <h4>Agents</h4>
                <div className="overview-stats">
                  <div className="stat">
                    <span className="stat-value">{fleetPlan.agents.length}</span>
                    <span className="stat-label">Total</span>
                  </div>
                  <div className="stat">
                    <span className="stat-value">
                      {fleetPlan.agents.filter(a => a.auto_start).length}
                    </span>
                    <span className="stat-label">Auto-start</span>
                  </div>
                </div>
              </div>
              
              <div className="overview-card">
                <h4>Global Constraints</h4>
                <div className="constraints-list">
                  {Object.entries(fleetPlan.global_constraints).map(([key, value]) => (
                    <div key={key} className="constraint-item">
                      <span className="constraint-key">{key}:</span>
                      <span className="constraint-value">{String(value)}</span>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="overview-card">
                <h4>Schedule Windows</h4>
                <div className="windows-list">
                  {Object.entries(fleetPlan.schedule_windows).map(([name, window]) => (
                    <div key={name} className="window-item">
                      <span className="window-name">{name}</span>
                      <span className="window-time">
                        {window.start_time} - {window.end_time}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="fleet-agents">
              <h4>Fleet Agents</h4>
              <div className="fleet-agents-grid">
                {fleetPlan.agents.map((agent) => (
                  <div key={agent.name} className="fleet-agent-card">
                    <div className="fleet-agent-header">
                      <h5>{agent.name}</h5>
                      <span className={`priority-badge priority-${agent.priority}`}>
                        {agent.priority}
                      </span>
                    </div>
                    
                    <div className="fleet-agent-details">
                      <div className="detail-row">
                        <span className="label">Mode:</span>
                        <span className="value">{agent.mode}</span>
                      </div>
                      <div className="detail-row">
                        <span className="label">Machine:</span>
                        <span className="value">{agent.machine_id}</span>
                      </div>
                      <div className="detail-row">
                        <span className="label">Auto-start:</span>
                        <span className="value">{agent.auto_start ? 'Yes' : 'No'}</span>
                      </div>
                      <div className="detail-row">
                        <span className="label">Max Runtime:</span>
                        <span className="value">{agent.schedule_preferences.max_daily_runtime}h</span>
                      </div>
                    </div>
                    
                    <div className="fleet-agent-capabilities">
                      {agent.capabilities.map((cap) => (
                        <span key={cap} className="capability-tag">{cap}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {selectedTab === 'monitoring' && (
          <div className="monitoring-tab">
            <div className="monitoring-header">
              <h3>Fleet Monitoring</h3>
            </div>
            
            <div className="monitoring-stats">
              <div className="stat-card">
                <h4>Agent Health</h4>
                <div className="stat-content">
                  <div className="stat-item">
                    <span className="stat-label">Healthy:</span>
                    <span className="stat-value">
                      {agents.filter(a => a.health === 'healthy').length}
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Warning:</span>
                    <span className="stat-value">
                      {agents.filter(a => a.health === 'warning').length}
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Critical:</span>
                    <span className="stat-value">
                      {agents.filter(a => a.health === 'critical').length}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="stat-card">
                <h4>Task Status</h4>
                <div className="stat-content">
                  <div className="stat-item">
                    <span className="stat-label">Pending:</span>
                    <span className="stat-value">
                      {tasks.filter(t => t.status === 'pending').length}
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Running:</span>
                    <span className="stat-value">
                      {tasks.filter(t => t.status === 'running').length}
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Completed:</span>
                    <span className="stat-value">
                      {tasks.filter(t => t.status === 'completed').length}
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Failed:</span>
                    <span className="stat-value">
                      {tasks.filter(t => t.status === 'failed').length}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="stat-card">
                <h4>Performance</h4>
                <div className="stat-content">
                  <div className="stat-item">
                    <span className="stat-label">Avg Response:</span>
                    <span className="stat-value">
                      {agents.length > 0 
                        ? Math.round(agents.reduce((sum, a) => sum + (a.performance_metrics.response_time || 0), 0) / agents.length)
                        : 0}ms
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Total Errors:</span>
                    <span className="stat-value">
                      {agents.reduce((sum, a) => sum + a.error_count, 0)}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default OrchestratorPanel; 