import React, { useState, useEffect, useCallback } from 'react';
import './SessionControlPanel.css';

// Types
interface SessionStatus {
  session_id: string;
  status: 'running' | 'paused' | 'stopped' | 'error' | 'not_found';
  mode: string;
  start_time: string;
  uptime_seconds: number;
  current_task: string;
  stuck_detected: boolean;
  stuck_duration?: number;
  last_activity: string;
  performance_metrics: Record<string, any>;
  error_message?: string;
}

interface SessionParameters {
  heal_range?: number;
  auto_revive?: boolean;
  quest_types?: string[];
  auto_accept?: boolean;
  resource_types?: string[];
  auto_loot?: boolean;
  target_level?: number;
  xp_threshold?: number;
  recipe_types?: string[];
  auto_craft?: boolean;
}

interface AlertData {
  type: string;
  message: string;
  session_id?: string;
}

interface BridgeStatus {
  status: string;
  active_sessions: number;
  total_commands: number;
  last_heartbeat: string;
}

interface AuthStatus {
  authenticated: boolean;
  user_id: string;
  permissions: Record<string, boolean>;
}

// API Service
class SessionControlAPI {
  private apiBaseUrl: string;
  private authToken: string | null;

  constructor() {
    this.apiBaseUrl = '/api/session-bridge';
    this.authToken = this.getStoredAuthToken();
  }

  private getStoredAuthToken(): string | null {
    try {
      const authData = localStorage.getItem('ms11_auth_data');
      return authData ? JSON.parse(authData).token : null;
    } catch {
      return null;
    }
  }

  private async makeRequest(endpoint: string, options: RequestInit = {}): Promise<Response> {
    const url = `${this.apiBaseUrl}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...(this.authToken && { Authorization: `Bearer ${this.authToken}` }),
      ...options.headers,
    };

    return fetch(url, { ...options, headers });
  }

  async getBridgeStatus(): Promise<BridgeStatus> {
    const response = await this.makeRequest('/status');
    if (!response.ok) throw new Error('Failed to get bridge status');
    return response.json();
  }

  async verifyAuth(): Promise<AuthStatus> {
    const authData = this.getStoredAuthToken();
    if (!authData) throw new Error('No auth token found');

    const response = await this.makeRequest('/auth/verify', {
      method: 'POST',
      body: JSON.stringify({
        token: authData,
        user_id: 'current_user', // This would come from auth data
      }),
    });

    if (!response.ok) throw new Error('Auth verification failed');
    return response.json();
  }

  async getSessions(): Promise<SessionStatus[]> {
    const response = await this.makeRequest('/sessions');
    if (!response.ok) throw new Error('Failed to get sessions');
    const data = await response.json();
    return data.sessions;
  }

  async getSession(sessionId: string): Promise<SessionStatus> {
    const response = await this.makeRequest(`/session/${sessionId}`);
    if (!response.ok) throw new Error('Failed to get session');
    return response.json();
  }

  async startSession(mode: string, parameters: SessionParameters): Promise<{ session_id: string }> {
    const response = await this.makeRequest('/session/start', {
      method: 'POST',
      body: JSON.stringify({ mode, parameters }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to start session');
    }

    return response.json();
  }

  async controlSession(sessionId: string, command: string): Promise<void> {
    const response = await this.makeRequest(`/session/${sessionId}/control`, {
      method: 'POST',
      body: JSON.stringify({ command }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || `Failed to ${command} session`);
    }
  }

  async sendDiscordAlert(alertData: AlertData): Promise<void> {
    const response = await this.makeRequest('/alerts/discord', {
      method: 'POST',
      body: JSON.stringify(alertData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Failed to send Discord alert');
    }
  }
}

// Main Component
const SessionControlPanel: React.FC = () => {
  const [api] = useState(() => new SessionControlAPI());
  const [sessions, setSessions] = useState<SessionStatus[]>([]);
  const [selectedSession, setSelectedSession] = useState<SessionStatus | null>(null);
  const [bridgeStatus, setBridgeStatus] = useState<BridgeStatus | null>(null);
  const [authStatus, setAuthStatus] = useState<AuthStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'error' | 'warning' } | null>(null);

  // Form states
  const [newSessionMode, setNewSessionMode] = useState('medic');
  const [newSessionParams, setNewSessionParams] = useState('');
  const [alertType, setAlertType] = useState('session_start');
  const [alertMessage, setAlertMessage] = useState('');

  // Load initial data
  useEffect(() => {
    loadInitialData();
    const interval = setInterval(loadInitialData, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadInitialData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Load bridge status
      const status = await api.getBridgeStatus();
      setBridgeStatus(status);

      // Verify auth
      const auth = await api.verifyAuth();
      setAuthStatus(auth);

      // Load sessions
      const sessionList = await api.getSessions();
      setSessions(sessionList);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }, [api]);

  const showNotification = useCallback((message: string, type: 'success' | 'error' | 'warning') => {
    setNotification({ message, type });
    setTimeout(() => setNotification(null), 5000);
  }, []);

  const handleStartSession = async () => {
    try {
      let parameters: SessionParameters = {};
      
      if (newSessionParams.trim()) {
        try {
          parameters = JSON.parse(newSessionParams);
        } catch {
          showNotification('Invalid JSON parameters', 'error');
          return;
        }
      }

      const result = await api.startSession(newSessionMode, parameters);
      showNotification(`Session started: ${result.session_id}`, 'success');
      
      // Reset form
      setNewSessionParams('');
      await loadInitialData();
    } catch (err) {
      showNotification(err instanceof Error ? err.message : 'Failed to start session', 'error');
    }
  };

  const handleControlSession = async (sessionId: string, command: string) => {
    try {
      await api.controlSession(sessionId, command);
      showNotification(`Session ${command} command executed`, 'success');
      await loadInitialData();
    } catch (err) {
      showNotification(err instanceof Error ? err.message : `Failed to ${command} session`, 'error');
    }
  };

  const handleSelectSession = async (sessionId: string) => {
    try {
      const session = await api.getSession(sessionId);
      setSelectedSession(session);
    } catch (err) {
      showNotification('Failed to load session details', 'error');
    }
  };

  const handleSendAlert = async () => {
    try {
      if (!alertMessage.trim()) {
        showNotification('Please enter an alert message', 'error');
        return;
      }

      await api.sendDiscordAlert({
        type: alertType,
        message: alertMessage,
        session_id: selectedSession?.session_id,
      });

      showNotification('Discord alert sent successfully', 'success');
      setAlertMessage('');
    } catch (err) {
      showNotification(err instanceof Error ? err.message : 'Failed to send Discord alert', 'error');
    }
  };

  const formatUptime = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  if (loading && !bridgeStatus) {
    return <div className="session-control-loading">Loading session controls...</div>;
  }

  if (error) {
    return (
      <div className="session-control-error">
        <h3>Error</h3>
        <p>{error}</p>
        <button onClick={loadInitialData}>Retry</button>
      </div>
    );
  }

  return (
    <div className="session-control-panel">
      {/* Notification */}
      {notification && (
        <div className={`notification notification-${notification.type}`}>
          {notification.message}
        </div>
      )}

      {/* Header */}
      <div className="control-header">
        <h2>Bot Session Control</h2>
        <div className="status-indicators">
          <span className={`status-indicator ${bridgeStatus?.status === 'active' ? 'active' : 'error'}`}>
            Bridge: {bridgeStatus?.status || 'Unknown'} ({bridgeStatus?.active_sessions || 0} sessions)
          </span>
          <span className={`status-indicator ${authStatus?.authenticated ? 'active' : 'error'}`}>
            Auth: {authStatus?.authenticated ? `Valid (${authStatus.user_id})` : 'Invalid'}
          </span>
        </div>
      </div>

      {/* Start Session Panel */}
      <div className="session-controls">
        <div className="start-session-panel">
          <h3>Start New Session</h3>
          <div className="session-form">
            <div className="form-group">
              <label htmlFor="session-mode">Mode:</label>
              <select
                id="session-mode"
                value={newSessionMode}
                onChange={(e) => setNewSessionMode(e.target.value)}
                className="form-control"
              >
                <option value="medic">Medic</option>
                <option value="quest">Quest</option>
                <option value="farming">Farming</option>
                <option value="grinding">Grinding</option>
                <option value="crafting">Crafting</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="session-parameters">Parameters (JSON):</label>
              <textarea
                id="session-parameters"
                value={newSessionParams}
                onChange={(e) => setNewSessionParams(e.target.value)}
                className="form-control"
                placeholder='{"heal_range": 75, "auto_revive": true}'
                rows={3}
              />
            </div>

            <button
              onClick={handleStartSession}
              disabled={loading}
              className="btn btn-primary"
            >
              {loading ? 'Starting...' : 'Start Session'}
            </button>
          </div>
        </div>

        {/* Active Sessions Panel */}
        <div className="active-sessions-panel">
          <h3>Active Sessions</h3>
          <div className="sessions-list">
            {sessions.length === 0 ? (
              <div className="no-sessions">No active sessions</div>
            ) : (
              sessions.map((session) => (
                <div key={session.session_id} className="session-item">
                  <div className="session-header">
                    <span className="session-id">{session.session_id}</span>
                    <span className={`session-status ${session.status}`}>
                      {session.status}
                    </span>
                  </div>
                  <div className="session-info">
                    <div className="session-mode">Mode: {session.mode}</div>
                    <div className="session-uptime">
                      Uptime: {formatUptime(session.uptime_seconds)}
                    </div>
                    <div className="session-task">Task: {session.current_task}</div>
                    {session.stuck_detected && (
                      <div className="stuck-warning">⚠️ Stuck Detected</div>
                    )}
                  </div>
                  <div className="session-controls">
                    <button
                      onClick={() => handleSelectSession(session.session_id)}
                      className="btn btn-sm btn-info"
                    >
                      Details
                    </button>
                    <button
                      onClick={() => handleControlSession(session.session_id, 'pause')}
                      className="btn btn-sm btn-warning"
                      disabled={session.status !== 'running'}
                    >
                      Pause
                    </button>
                    <button
                      onClick={() => handleControlSession(session.session_id, 'stop')}
                      className="btn btn-sm btn-danger"
                    >
                      Stop
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Session Details */}
      {selectedSession && (
        <div className="session-details">
          <h3>Session Details</h3>
          <div className="session-info">
            <div className="session-detail-item">
              <strong>Session ID:</strong> {selectedSession.session_id}
            </div>
            <div className="session-detail-item">
              <strong>Status:</strong>{' '}
              <span className={`status-${selectedSession.status}`}>
                {selectedSession.status}
              </span>
            </div>
            <div className="session-detail-item">
              <strong>Mode:</strong> {selectedSession.mode}
            </div>
            <div className="session-detail-item">
              <strong>Uptime:</strong> {formatUptime(selectedSession.uptime_seconds)}
            </div>
            <div className="session-detail-item">
              <strong>Current Task:</strong> {selectedSession.current_task}
            </div>
            <div className="session-detail-item">
              <strong>Last Activity:</strong>{' '}
              {new Date(selectedSession.last_activity).toLocaleString()}
            </div>
            {selectedSession.stuck_detected && (
              <div className="session-detail-item stuck-warning">
                <strong>⚠️ Stuck Detected:</strong>{' '}
                {selectedSession.stuck_duration
                  ? Math.round(selectedSession.stuck_duration)
                  : 'Unknown'}s
              </div>
            )}
            <div className="session-detail-item">
              <strong>Performance Metrics:</strong>
              <pre>{JSON.stringify(selectedSession.performance_metrics, null, 2)}</pre>
            </div>
          </div>
          <div className="session-controls">
            <button
              onClick={() => handleControlSession(selectedSession.session_id, 'pause')}
              className="btn btn-warning"
              disabled={selectedSession.status !== 'running'}
            >
              Pause
            </button>
            <button
              onClick={() => handleControlSession(selectedSession.session_id, 'resume')}
              className="btn btn-info"
              disabled={selectedSession.status !== 'paused'}
            >
              Resume
            </button>
            <button
              onClick={() => handleControlSession(selectedSession.session_id, 'reset')}
              className="btn btn-secondary"
            >
              Reset
            </button>
            <button
              onClick={() => handleControlSession(selectedSession.session_id, 'stop')}
              className="btn btn-danger"
            >
              Stop
            </button>
          </div>
        </div>
      )}

      {/* Discord Alerts Panel */}
      <div className="alert-panel">
        <h3>Discord Alerts</h3>
        <div className="alert-form">
          <div className="form-group">
            <label htmlFor="alert-type">Alert Type:</label>
            <select
              id="alert-type"
              value={alertType}
              onChange={(e) => setAlertType(e.target.value)}
              className="form-control"
            >
              <option value="session_start">Session Start</option>
              <option value="session_stop">Session Stop</option>
              <option value="session_pause">Session Pause</option>
              <option value="session_resume">Session Resume</option>
              <option value="session_reset">Session Reset</option>
              <option value="stuck_detected">Stuck Detected</option>
              <option value="error">Error</option>
              <option value="custom">Custom</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="alert-message">Message:</label>
            <textarea
              id="alert-message"
              value={alertMessage}
              onChange={(e) => setAlertMessage(e.target.value)}
              className="form-control"
              placeholder="Enter alert message..."
              rows={2}
            />
          </div>

          <button onClick={handleSendAlert} className="btn btn-success">
            Send Discord Alert
          </button>
        </div>
      </div>
    </div>
  );
};

export default SessionControlPanel; 