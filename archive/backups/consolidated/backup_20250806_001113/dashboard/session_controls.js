/**
 * Session Controls for Dashboard Bot Control
 * 
 * This module provides the frontend functionality for controlling and monitoring
 * bot sessions from the web dashboard on swgdb.com.
 */

class SessionControlPanel {
    constructor() {
        this.apiBaseUrl = '/api/session-bridge';
        this.authToken = null;
        this.userId = null;
        this.activeSessions = new Map();
        this.statusUpdateInterval = null;
        this.websocket = null;
        
        this.init();
    }
    
    async init() {
        try {
            // Initialize authentication
            await this.initializeAuth();
            
            // Setup UI components
            this.setupUI();
            
            // Start real-time updates
            this.startRealTimeUpdates();
            
            // Load initial session data
            await this.loadSessions();
            
            console.log('Session Control Panel initialized');
        } catch (error) {
            console.error('Error initializing Session Control Panel:', error);
            this.showError('Failed to initialize session controls');
        }
    }
    
    async initializeAuth() {
        try {
            // Check if user is authenticated
            const authData = this.getStoredAuthData();
            if (authData && authData.token && authData.userId) {
                this.authToken = authData.token;
                this.userId = authData.userId;
                
                // Verify token is still valid
                const isValid = await this.verifyAuth();
                if (!isValid) {
                    throw new Error('Authentication token expired');
                }
            } else {
                throw new Error('No authentication data found');
            }
        } catch (error) {
            console.error('Authentication error:', error);
            this.showLoginPrompt();
        }
    }
    
    getStoredAuthData() {
        try {
            const authData = localStorage.getItem('ms11_auth_data');
            return authData ? JSON.parse(authData) : null;
        } catch (error) {
            console.error('Error reading auth data:', error);
            return null;
        }
    }
    
    async verifyAuth() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/auth/verify`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.authToken}`
                },
                body: JSON.stringify({
                    token: this.authToken,
                    user_id: this.userId
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                return data.authenticated;
            }
            return false;
        } catch (error) {
            console.error('Auth verification error:', error);
            return false;
        }
    }
    
    setupUI() {
        // Create main control panel
        this.createControlPanel();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Setup status indicators
        this.setupStatusIndicators();
    }
    
    createControlPanel() {
        const container = document.getElementById('session-control-panel') || 
                         this.createContainer();
        
        container.innerHTML = `
            <div class="session-control-container">
                <div class="control-header">
                    <h2>Bot Session Control</h2>
                    <div class="status-indicators">
                        <span class="status-indicator" id="bridge-status">Bridge: Connecting...</span>
                        <span class="status-indicator" id="auth-status">Auth: Checking...</span>
                    </div>
                </div>
                
                <div class="session-controls">
                    <div class="start-session-panel">
                        <h3>Start New Session</h3>
                        <div class="session-form">
                            <div class="form-group">
                                <label for="session-mode">Mode:</label>
                                <select id="session-mode" class="form-control">
                                    <option value="medic">Medic</option>
                                    <option value="quest">Quest</option>
                                    <option value="farming">Farming</option>
                                    <option value="grinding">Grinding</option>
                                    <option value="crafting">Crafting</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label for="session-parameters">Parameters (JSON):</label>
                                <textarea id="session-parameters" class="form-control" 
                                          placeholder='{"heal_range": 75, "auto_revive": true}'
                                          rows="3"></textarea>
                            </div>
                            
                            <button id="start-session-btn" class="btn btn-primary">
                                Start Session
                            </button>
                        </div>
                    </div>
                    
                    <div class="active-sessions-panel">
                        <h3>Active Sessions</h3>
                        <div id="sessions-list" class="sessions-list">
                            <div class="no-sessions">No active sessions</div>
                        </div>
                    </div>
                </div>
                
                <div class="session-details" id="session-details" style="display: none;">
                    <h3>Session Details</h3>
                    <div id="session-info"></div>
                    <div class="session-controls">
                        <button id="pause-session-btn" class="btn btn-warning">Pause</button>
                        <button id="resume-session-btn" class="btn btn-info">Resume</button>
                        <button id="reset-session-btn" class="btn btn-secondary">Reset</button>
                        <button id="stop-session-btn" class="btn btn-danger">Stop</button>
                    </div>
                </div>
                
                <div class="alert-panel">
                    <h3>Discord Alerts</h3>
                    <div class="alert-form">
                        <div class="form-group">
                            <label for="alert-type">Alert Type:</label>
                            <select id="alert-type" class="form-control">
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
                        
                        <div class="form-group">
                            <label for="alert-message">Message:</label>
                            <textarea id="alert-message" class="form-control" 
                                      placeholder="Enter alert message..."
                                      rows="2"></textarea>
                        </div>
                        
                        <button id="send-alert-btn" class="btn btn-success">
                            Send Discord Alert
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    createContainer() {
        const container = document.createElement('div');
        container.id = 'session-control-panel';
        container.className = 'session-control-panel';
        document.body.appendChild(container);
        return container;
    }
    
    setupEventListeners() {
        // Start session button
        const startBtn = document.getElementById('start-session-btn');
        if (startBtn) {
            startBtn.addEventListener('click', () => this.startSession());
        }
        
        // Session control buttons
        const pauseBtn = document.getElementById('pause-session-btn');
        const resumeBtn = document.getElementById('resume-session-btn');
        const resetBtn = document.getElementById('reset-session-btn');
        const stopBtn = document.getElementById('stop-session-btn');
        
        if (pauseBtn) pauseBtn.addEventListener('click', () => this.controlSession('pause'));
        if (resumeBtn) resumeBtn.addEventListener('click', () => this.controlSession('resume'));
        if (resetBtn) resetBtn.addEventListener('click', () => this.controlSession('reset'));
        if (stopBtn) stopBtn.addEventListener('click', () => this.controlSession('stop'));
        
        // Discord alert button
        const alertBtn = document.getElementById('send-alert-btn');
        if (alertBtn) {
            alertBtn.addEventListener('click', () => this.sendDiscordAlert());
        }
    }
    
    setupStatusIndicators() {
        // Update bridge status
        this.updateBridgeStatus();
        
        // Update auth status
        this.updateAuthStatus();
    }
    
    async updateBridgeStatus() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/status`);
            if (response.ok) {
                const data = await response.json();
                const statusEl = document.getElementById('bridge-status');
                if (statusEl) {
                    statusEl.textContent = `Bridge: Active (${data.active_sessions} sessions)`;
                    statusEl.className = 'status-indicator active';
                }
            } else {
                const statusEl = document.getElementById('bridge-status');
                if (statusEl) {
                    statusEl.textContent = 'Bridge: Disconnected';
                    statusEl.className = 'status-indicator error';
                }
            }
        } catch (error) {
            console.error('Error updating bridge status:', error);
            const statusEl = document.getElementById('bridge-status');
            if (statusEl) {
                statusEl.textContent = 'Bridge: Error';
                statusEl.className = 'status-indicator error';
            }
        }
    }
    
    async updateAuthStatus() {
        const isValid = await this.verifyAuth();
        const statusEl = document.getElementById('auth-status');
        if (statusEl) {
            if (isValid) {
                statusEl.textContent = `Auth: Valid (${this.userId})`;
                statusEl.className = 'status-indicator active';
            } else {
                statusEl.textContent = 'Auth: Invalid';
                statusEl.className = 'status-indicator error';
            }
        }
    }
    
    async loadSessions() {
        try {
            const response = await fetch(`${this.apiBaseUrl}/sessions`, {
                headers: {
                    'Authorization': `Bearer ${this.authToken}`
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.updateSessionsList(data.sessions);
            } else {
                console.error('Failed to load sessions');
            }
        } catch (error) {
            console.error('Error loading sessions:', error);
        }
    }
    
    updateSessionsList(sessions) {
        const sessionsList = document.getElementById('sessions-list');
        if (!sessionsList) return;
        
        if (sessions.length === 0) {
            sessionsList.innerHTML = '<div class="no-sessions">No active sessions</div>';
            return;
        }
        
        const sessionsHtml = sessions.map(session => `
            <div class="session-item" data-session-id="${session.session_id}">
                <div class="session-header">
                    <span class="session-id">${session.session_id}</span>
                    <span class="session-status ${session.status}">${session.status}</span>
                </div>
                <div class="session-info">
                    <div class="session-mode">Mode: ${session.mode}</div>
                    <div class="session-uptime">Uptime: ${this.formatUptime(session.uptime_seconds)}</div>
                    <div class="session-task">Task: ${session.current_task}</div>
                    ${session.stuck_detected ? '<div class="stuck-warning">⚠️ Stuck Detected</div>' : ''}
                </div>
                <div class="session-controls">
                    <button class="btn btn-sm btn-info" onclick="sessionControlPanel.selectSession('${session.session_id}')">
                        Details
                    </button>
                    <button class="btn btn-sm btn-warning" onclick="sessionControlPanel.controlSession('${session.session_id}', 'pause')">
                        Pause
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="sessionControlPanel.controlSession('${session.session_id}', 'stop')">
                        Stop
                    </button>
                </div>
            </div>
        `).join('');
        
        sessionsList.innerHTML = sessionsHtml;
    }
    
    async startSession() {
        try {
            const modeSelect = document.getElementById('session-mode');
            const paramsTextarea = document.getElementById('session-parameters');
            
            const mode = modeSelect.value;
            let parameters = {};
            
            try {
                if (paramsTextarea.value.trim()) {
                    parameters = JSON.parse(paramsTextarea.value);
                }
            } catch (error) {
                this.showError('Invalid JSON parameters');
                return;
            }
            
            const response = await fetch(`${this.apiBaseUrl}/session/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.authToken}`
                },
                body: JSON.stringify({
                    mode: mode,
                    parameters: parameters
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.showSuccess(`Session started: ${data.session_id}`);
                await this.loadSessions();
            } else {
                const errorData = await response.json();
                this.showError(`Failed to start session: ${errorData.error}`);
            }
        } catch (error) {
            console.error('Error starting session:', error);
            this.showError('Failed to start session');
        }
    }
    
    async controlSession(sessionId, command) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/session/${sessionId}/control`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.authToken}`
                },
                body: JSON.stringify({
                    command: command
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.showSuccess(`Session ${command} command executed`);
                await this.loadSessions();
            } else {
                const errorData = await response.json();
                this.showError(`Failed to ${command} session: ${errorData.error}`);
            }
        } catch (error) {
            console.error(`Error ${command}ing session:`, error);
            this.showError(`Failed to ${command} session`);
        }
    }
    
    async selectSession(sessionId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}/session/${sessionId}`, {
                headers: {
                    'Authorization': `Bearer ${this.authToken}`
                }
            });
            
            if (response.ok) {
                const session = await response.json();
                this.showSessionDetails(session);
            } else {
                this.showError('Failed to load session details');
            }
        } catch (error) {
            console.error('Error loading session details:', error);
            this.showError('Failed to load session details');
        }
    }
    
    showSessionDetails(session) {
        const detailsPanel = document.getElementById('session-details');
        const sessionInfo = document.getElementById('session-info');
        
        if (detailsPanel && sessionInfo) {
            detailsPanel.style.display = 'block';
            
            sessionInfo.innerHTML = `
                <div class="session-detail-item">
                    <strong>Session ID:</strong> ${session.session_id}
                </div>
                <div class="session-detail-item">
                    <strong>Status:</strong> <span class="status-${session.status}">${session.status}</span>
                </div>
                <div class="session-detail-item">
                    <strong>Mode:</strong> ${session.mode}
                </div>
                <div class="session-detail-item">
                    <strong>Uptime:</strong> ${this.formatUptime(session.uptime_seconds)}
                </div>
                <div class="session-detail-item">
                    <strong>Current Task:</strong> ${session.current_task}
                </div>
                <div class="session-detail-item">
                    <strong>Last Activity:</strong> ${new Date(session.last_activity).toLocaleString()}
                </div>
                ${session.stuck_detected ? `
                <div class="session-detail-item stuck-warning">
                    <strong>⚠️ Stuck Detected:</strong> ${session.stuck_duration ? Math.round(session.stuck_duration)}s
                </div>
                ` : ''}
                <div class="session-detail-item">
                    <strong>Performance Metrics:</strong>
                    <pre>${JSON.stringify(session.performance_metrics, null, 2)}</pre>
                </div>
            `;
            
            // Store current session ID for control buttons
            detailsPanel.dataset.sessionId = session.session_id;
        }
    }
    
    async sendDiscordAlert() {
        try {
            const alertType = document.getElementById('alert-type').value;
            const alertMessage = document.getElementById('alert-message').value;
            const sessionId = document.getElementById('session-details')?.dataset.sessionId;
            
            if (!alertMessage.trim()) {
                this.showError('Please enter an alert message');
                return;
            }
            
            const response = await fetch(`${this.apiBaseUrl}/alerts/discord`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.authToken}`
                },
                body: JSON.stringify({
                    type: alertType,
                    message: alertMessage,
                    session_id: sessionId
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                this.showSuccess('Discord alert sent successfully');
                document.getElementById('alert-message').value = '';
            } else {
                const errorData = await response.json();
                this.showError(`Failed to send alert: ${errorData.error}`);
            }
        } catch (error) {
            console.error('Error sending Discord alert:', error);
            this.showError('Failed to send Discord alert');
        }
    }
    
    startRealTimeUpdates() {
        // Update sessions every 5 seconds
        this.statusUpdateInterval = setInterval(() => {
            this.loadSessions();
            this.updateBridgeStatus();
        }, 5000);
        
        // Setup WebSocket for real-time updates (if available)
        this.setupWebSocket();
    }
    
    setupWebSocket() {
        try {
            const wsUrl = this.apiBaseUrl.replace('http', 'ws') + '/ws';
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected for real-time updates');
            };
            
            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
            this.websocket.onclose = () => {
                console.log('WebSocket disconnected');
                // Attempt to reconnect after 5 seconds
                setTimeout(() => this.setupWebSocket(), 5000);
            };
        } catch (error) {
            console.error('Error setting up WebSocket:', error);
        }
    }
    
    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'session_update':
                this.updateSessionInList(data.session);
                break;
            case 'session_start':
                this.showSuccess(`Session started: ${data.session_id}`);
                this.loadSessions();
                break;
            case 'session_stop':
                this.showSuccess(`Session stopped: ${data.session_id}`);
                this.loadSessions();
                break;
            case 'stuck_detected':
                this.showWarning(`Session ${data.session_id} is stuck!`);
                break;
            default:
                console.log('Unknown WebSocket message type:', data.type);
        }
    }
    
    updateSessionInList(session) {
        const sessionItem = document.querySelector(`[data-session-id="${session.session_id}"]`);
        if (sessionItem) {
            // Update session display
            const statusEl = sessionItem.querySelector('.session-status');
            const uptimeEl = sessionItem.querySelector('.session-uptime');
            const taskEl = sessionItem.querySelector('.session-task');
            
            if (statusEl) statusEl.textContent = session.status;
            if (uptimeEl) uptimeEl.textContent = `Uptime: ${this.formatUptime(session.uptime_seconds)}`;
            if (taskEl) taskEl.textContent = `Task: ${session.current_task}`;
            
            // Update stuck warning
            const stuckWarning = sessionItem.querySelector('.stuck-warning');
            if (session.stuck_detected) {
                if (!stuckWarning) {
                    const warning = document.createElement('div');
                    warning.className = 'stuck-warning';
                    warning.textContent = '⚠️ Stuck Detected';
                    sessionItem.querySelector('.session-info').appendChild(warning);
                }
            } else if (stuckWarning) {
                stuckWarning.remove();
            }
        }
    }
    
    formatUptime(seconds) {
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
    }
    
    showSuccess(message) {
        this.showNotification(message, 'success');
    }
    
    showError(message) {
        this.showNotification(message, 'error');
    }
    
    showWarning(message) {
        this.showNotification(message, 'warning');
    }
    
    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }
    
    showLoginPrompt() {
        const loginPrompt = document.createElement('div');
        loginPrompt.className = 'login-prompt';
        loginPrompt.innerHTML = `
            <div class="login-modal">
                <h3>Authentication Required</h3>
                <p>Please log in to access bot session controls.</p>
                <button onclick="window.location.href='/auth/discord'">Login with Discord</button>
            </div>
        `;
        document.body.appendChild(loginPrompt);
    }
    
    destroy() {
        if (this.statusUpdateInterval) {
            clearInterval(this.statusUpdateInterval);
        }
        
        if (this.websocket) {
            this.websocket.close();
        }
    }
}

// Initialize the session control panel when the page loads
let sessionControlPanel;

document.addEventListener('DOMContentLoaded', () => {
    sessionControlPanel = new SessionControlPanel();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (sessionControlPanel) {
        sessionControlPanel.destroy();
    }
});

// Export for global access
window.sessionControlPanel = sessionControlPanel; 