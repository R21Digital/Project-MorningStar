import React, { useState, useEffect } from 'react';
import './MacroHealthStatus.css';

interface MacroHealth {
  macro_id: string;
  macro_name: string;
  state: string;
  risk_level: string;
  risk_score: number;
  last_event: string;
  pattern_matches: string[];
  memory_usage: number;
  cpu_usage: number;
  warnings: string[];
  is_safe: boolean;
}

interface MacroEvent {
  macro_id: string;
  macro_name: string;
  event_type: string;
  timestamp: string;
  data: Record<string, any>;
  risk_score: number;
}

interface MacroHealthStatusProps {
  refreshInterval?: number;
  showDetails?: boolean;
  onMacroAction?: (macroId: string, action: string) => void;
}

const MacroHealthStatus: React.FC<MacroHealthStatusProps> = ({
  refreshInterval = 5000,
  showDetails = true,
  onMacroAction
}) => {
  const [macroHealth, setMacroHealth] = useState<MacroHealth[]>([]);
  const [recentEvents, setRecentEvents] = useState<MacroEvent[]>([]);
  const [statistics, setStatistics] = useState<any>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedMacro, setSelectedMacro] = useState<string | null>(null);

  useEffect(() => {
    loadMacroHealth();
    const interval = setInterval(loadMacroHealth, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  const loadMacroHealth = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch macro health data
      const healthResponse = await fetch('/api/safety/macro-health');
      if (!healthResponse.ok) {
        throw new Error('Failed to load macro health data');
      }
      const healthData = await healthResponse.json();
      setMacroHealth(healthData.macros || []);

      // Fetch recent events
      const eventsResponse = await fetch('/api/safety/recent-events');
      if (eventsResponse.ok) {
        const eventsData = await eventsResponse.json();
        setRecentEvents(eventsData.events || []);
      }

      // Fetch statistics
      const statsResponse = await fetch('/api/safety/statistics');
      if (statsResponse.ok) {
        const statsData = await statsResponse.json();
        setStatistics(statsData);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  const handleMacroAction = async (macroId: string, action: string) => {
    try {
      const response = await fetch(`/api/safety/macro/${macroId}/${action}`, {
        method: 'POST',
      });

      if (response.ok) {
        // Reload data after action
        await loadMacroHealth();
        onMacroAction?.(macroId, action);
      } else {
        throw new Error(`Failed to ${action} macro`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Action failed');
    }
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel.toLowerCase()) {
      case 'critical':
        return '#ff4444';
      case 'high':
        return '#ff8800';
      case 'medium':
        return '#ffaa00';
      case 'low':
        return '#00aa00';
      default:
        return '#888888';
    }
  };

  const getStateColor = (state: string) => {
    switch (state.toLowerCase()) {
      case 'running':
        return '#00aa00';
      case 'paused':
        return '#ffaa00';
      case 'stopped':
        return '#ff4444';
      case 'crashed':
        return '#880000';
      default:
        return '#888888';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const getRiskScoreColor = (score: number) => {
    if (score >= 0.8) return '#ff4444';
    if (score >= 0.6) return '#ff8800';
    if (score >= 0.4) return '#ffaa00';
    return '#00aa00';
  };

  if (loading && macroHealth.length === 0) {
    return (
      <div className="macro-health-status loading">
        <div className="loading-spinner"></div>
        <p>Loading macro health data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="macro-health-status error">
        <div className="error-icon">⚠️</div>
        <p>Error: {error}</p>
        <button onClick={loadMacroHealth} className="retry-button">
          Retry
        </button>
      </div>
    );
  }

  const safeMacros = macroHealth.filter(m => m.is_safe);
  const unsafeMacros = macroHealth.filter(m => !m.is_safe);
  const criticalMacros = macroHealth.filter(m => m.risk_level === 'critical');

  return (
    <div className="macro-health-status">
      <div className="header">
        <h2>🔒 Macro Health Status</h2>
        <div className="status-summary">
          <span className={`status-indicator ${statistics.monitoring_active ? 'active' : 'inactive'}`}>
            {statistics.monitoring_active ? '🟢 Active' : '🔴 Inactive'}
          </span>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="statistics-grid">
        <div className="stat-card">
          <div className="stat-value">{statistics.total_macros || 0}</div>
          <div className="stat-label">Total Macros</div>
        </div>
        <div className="stat-card safe">
          <div className="stat-value">{safeMacros.length}</div>
          <div className="stat-label">Safe</div>
        </div>
        <div className="stat-card warning">
          <div className="stat-value">{unsafeMacros.length}</div>
          <div className="stat-label">Unsafe</div>
        </div>
        <div className="stat-card critical">
          <div className="stat-value">{criticalMacros.length}</div>
          <div className="stat-label">Critical</div>
        </div>
      </div>

      {/* Macro Health List */}
      <div className="macro-list">
        <h3>Active Macros</h3>
        {macroHealth.length === 0 ? (
          <div className="no-macros">
            <p>No active macros found</p>
          </div>
        ) : (
          macroHealth.map((macro) => (
            <div
              key={macro.macro_id}
              className={`macro-card ${macro.is_safe ? 'safe' : 'unsafe'} ${selectedMacro === macro.macro_id ? 'selected' : ''}`}
              onClick={() => setSelectedMacro(selectedMacro === macro.macro_id ? null : macro.macro_id)}
            >
              <div className="macro-header">
                <div className="macro-info">
                  <h4>{macro.macro_name}</h4>
                  <span className="macro-id">ID: {macro.macro_id}</span>
                </div>
                <div className="macro-status">
                  <span
                    className="state-badge"
                    style={{ backgroundColor: getStateColor(macro.state) }}
                  >
                    {macro.state.toUpperCase()}
                  </span>
                  <span
                    className="risk-badge"
                    style={{ backgroundColor: getRiskLevelColor(macro.risk_level) }}
                  >
                    {macro.risk_level.toUpperCase()}
                  </span>
                </div>
              </div>

              <div className="macro-metrics">
                <div className="metric">
                  <span className="metric-label">Risk Score:</span>
                  <span
                    className="metric-value"
                    style={{ color: getRiskScoreColor(macro.risk_score) }}
                  >
                    {(macro.risk_score * 100).toFixed(1)}%
                  </span>
                </div>
                <div className="metric">
                  <span className="metric-label">Memory:</span>
                  <span className="metric-value">{macro.memory_usage.toFixed(1)}%</span>
                </div>
                <div className="metric">
                  <span className="metric-label">CPU:</span>
                  <span className="metric-value">{macro.cpu_usage.toFixed(1)}%</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Patterns:</span>
                  <span className="metric-value">{macro.pattern_matches.length}</span>
                </div>
              </div>

              {selectedMacro === macro.macro_id && showDetails && (
                <div className="macro-details">
                  <div className="details-section">
                    <h5>Warnings ({macro.warnings.length})</h5>
                    {macro.warnings.length > 0 ? (
                      <ul className="warnings-list">
                        {macro.warnings.map((warning, index) => (
                          <li key={index} className="warning-item">
                            ⚠️ {warning}
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="no-warnings">No warnings</p>
                    )}
                  </div>

                  <div className="details-section">
                    <h5>Pattern Matches</h5>
                    {macro.pattern_matches.length > 0 ? (
                      <div className="pattern-matches">
                        {macro.pattern_matches.map((pattern, index) => (
                          <span key={index} className="pattern-tag">
                            {pattern}
                          </span>
                        ))}
                      </div>
                    ) : (
                      <p className="no-patterns">No dangerous patterns detected</p>
                    )}
                  </div>

                  <div className="macro-actions">
                    {macro.state === 'running' && (
                      <>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleMacroAction(macro.macro_id, 'pause');
                          }}
                          className="action-button pause"
                        >
                          ⏸️ Pause
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleMacroAction(macro.macro_id, 'stop');
                          }}
                          className="action-button stop"
                        >
                          ⏹️ Stop
                        </button>
                      </>
                    )}
                    {macro.state === 'paused' && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleMacroAction(macro.macro_id, 'resume');
                        }}
                        className="action-button resume"
                      >
                        ▶️ Resume
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Recent Events */}
      {showDetails && recentEvents.length > 0 && (
        <div className="recent-events">
          <h3>Recent Events</h3>
          <div className="events-list">
            {recentEvents.slice(0, 10).map((event, index) => (
              <div key={index} className="event-item">
                <div className="event-header">
                  <span className="event-type">{event.event_type}</span>
                  <span className="event-time">{formatTimestamp(event.timestamp)}</span>
                </div>
                <div className="event-details">
                  <span className="event-macro">{event.macro_name}</span>
                  <span className="event-risk">Risk: {(event.risk_score * 100).toFixed(1)}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* System Status */}
      {showDetails && (
        <div className="system-status">
          <h3>System Status</h3>
          <div className="status-grid">
            <div className="status-item">
              <span className="status-label">Guard Level:</span>
              <span className="status-value">{statistics.guard_level || 'medium'}</span>
            </div>
            <div className="status-item">
              <span className="status-label">Patterns Loaded:</span>
              <span className="status-value">{statistics.patterns_loaded || 0}</span>
            </div>
            <div className="status-item">
              <span className="status-label">Recent Events:</span>
              <span className="status-value">{recentEvents.length}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MacroHealthStatus; 