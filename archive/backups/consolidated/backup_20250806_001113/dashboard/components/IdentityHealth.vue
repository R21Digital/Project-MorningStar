<template>
  <div class="identity-health">
    <!-- Header -->
    <div class="header">
      <h2>Identity Protection Health</h2>
      <div class="header-controls">
        <button @click="refreshData" :disabled="loading">
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
          Refresh
        </button>
        <button @click="toggleDetails" class="details-toggle">
          <i class="fas" :class="showDetails ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
          {{ showDetails ? 'Hide' : 'Show' }} Details
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Loading identity protection status...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error">
      <i class="fas fa-exclamation-triangle"></i>
      <p>{{ error }}</p>
      <button @click="refreshData">Try Again</button>
    </div>

    <!-- Main Content -->
    <div v-else class="content">
      <!-- Risk Level Indicator -->
      <div class="risk-indicator" :class="riskLevelClass">
        <div class="risk-icon">
          <i :class="riskLevelIcon"></i>
        </div>
        <div class="risk-info">
          <h3>{{ riskLevelText }}</h3>
          <p>{{ riskLevelDescription }}</p>
        </div>
      </div>

      <!-- Protection Status Cards -->
      <div class="protection-cards">
        <div class="card" :class="{ active: protectionStatus.idle_emotes }">
          <div class="card-icon">
            <i class="fas fa-smile"></i>
          </div>
          <div class="card-content">
            <h4>Idle Emotes</h4>
            <p>{{ protectionStatus.idle_emotes ? 'Enabled' : 'Disabled' }}</p>
          </div>
        </div>

        <div class="card" :class="{ active: protectionStatus.chat_rate_limit }">
          <div class="card-icon">
            <i class="fas fa-comments"></i>
          </div>
          <div class="card-content">
            <h4>Chat Rate Limit</h4>
            <p>{{ protectionStatus.chat_rate_limit ? 'Enabled' : 'Disabled' }}</p>
          </div>
        </div>

        <div class="card" :class="{ active: protectionStatus.sanitize_logs }">
          <div class="card-icon">
            <i class="fas fa-shield-alt"></i>
          </div>
          <div class="card-content">
            <h4>Log Sanitization</h4>
            <p>{{ protectionStatus.sanitize_logs ? 'Enabled' : 'Disabled' }}</p>
          </div>
        </div>

        <div class="card" :class="{ active: protectionStatus.randomize_movement }">
          <div class="card-icon">
            <i class="fas fa-random"></i>
          </div>
          <div class="card-content">
            <h4>Movement Randomization</h4>
            <p>{{ protectionStatus.randomize_movement ? 'Enabled' : 'Disabled' }}</p>
          </div>
        </div>

        <div class="card" :class="{ active: protectionStatus.randomize_mood }">
          <div class="card-icon">
            <i class="fas fa-heart"></i>
          </div>
          <div class="card-content">
            <h4>Mood Randomization</h4>
            <p>{{ protectionStatus.randomize_mood ? 'Enabled' : 'Disabled' }}</p>
          </div>
        </div>

        <div class="card" :class="{ active: protectionStatus.camera_wiggles }">
          <div class="card-icon">
            <i class="fas fa-eye"></i>
          </div>
          <div class="card-content">
            <h4>Camera Wiggles</h4>
            <p>{{ protectionStatus.camera_wiggles ? 'Enabled' : 'Disabled' }}</p>
          </div>
        </div>
      </div>

      <!-- Statistics -->
      <div class="statistics">
        <div class="stat-card">
          <div class="stat-value">{{ statistics.total_events }}</div>
          <div class="stat-label">Total Events</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ statistics.risk_events }}</div>
          <div class="stat-label">Risk Events</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ statistics.sanitized_logs }}</div>
          <div class="stat-label">Sanitized Logs</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ statistics.rate_limited_messages }}</div>
          <div class="stat-label">Rate Limited</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ statistics.randomization_actions }}</div>
          <div class="stat-label">Randomization Actions</div>
        </div>
      </div>

      <!-- Detailed Information -->
      <div v-if="showDetails" class="details-section">
        <!-- Recent Activities -->
        <div class="activities-section">
          <h3>Recent Activities</h3>
          <div class="activities-list">
            <div 
              v-for="(activity, index) in recentActivities" 
              :key="index"
              class="activity-item"
              :class="getActivityClass(activity)"
            >
              <div class="activity-icon">
                <i :class="getActivityIcon(activity)"></i>
              </div>
              <div class="activity-content">
                <div class="activity-type">{{ formatActivityType(activity.event_type) }}</div>
                <div class="activity-time">{{ formatTime(activity.timestamp) }}</div>
                <div class="activity-action">{{ activity.action_taken }}</div>
              </div>
              <div class="activity-risk" :class="getRiskClass(activity.risk_level)">
                {{ activity.risk_level }}
              </div>
            </div>
          </div>
        </div>

        <!-- Protection Metrics -->
        <div class="metrics-section">
          <h3>Protection Metrics</h3>
          <div class="metrics-grid">
            <div class="metric-item">
              <label>Chat History Size:</label>
              <span>{{ statistics.chat_history_size }}</span>
            </div>
            <div class="metric-item">
              <label>Movement History Size:</label>
              <span>{{ statistics.movement_history_size }}</span>
            </div>
            <div class="metric-item">
              <label>Recent Activity Count:</label>
              <span>{{ statistics.recent_activity }}</span>
            </div>
            <div class="metric-item">
              <label>Last Risk Event:</label>
              <span>{{ formatLastRiskEvent() }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Alert Messages -->
      <div v-if="alertMessage" class="alert-message" :class="alertClass">
        <i :class="alertIcon"></i>
        <span>{{ alertMessage }}</span>
        <button @click="dismissAlert" class="alert-dismiss">
          <i class="fas fa-times"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'IdentityHealth',
  data() {
    return {
      loading: false,
      error: null,
      showDetails: false,
      identityHealth: null,
      statistics: {
        total_events: 0,
        risk_events: 0,
        sanitized_logs: 0,
        rate_limited_messages: 0,
        randomization_actions: 0,
        chat_history_size: 0,
        movement_history_size: 0,
        recent_activity: 0
      },
      protectionStatus: {
        idle_emotes: false,
        chat_rate_limit: false,
        sanitize_logs: false,
        randomize_movement: false,
        randomize_mood: false,
        camera_wiggles: false
      },
      recentActivities: [],
      alertMessage: null,
      alertType: 'info',
      autoRefreshInterval: null
    }
  },
  computed: {
    riskLevelClass() {
      if (!this.identityHealth) return 'risk-low'
      const riskLevel = this.identityHealth.current_risk_level
      return `risk-${riskLevel}`
    },
    riskLevelText() {
      if (!this.identityHealth) return 'Unknown'
      const riskLevel = this.identityHealth.current_risk_level
      return riskLevel.charAt(0).toUpperCase() + riskLevel.slice(1)
    },
    riskLevelDescription() {
      if (!this.identityHealth) return 'No data available'
      const riskLevel = this.identityHealth.current_risk_level
      const descriptions = {
        low: 'Normal protection level',
        medium: 'Elevated risk detected',
        high: 'High risk - increased monitoring',
        critical: 'Critical risk - immediate attention required'
      }
      return descriptions[riskLevel] || 'Unknown risk level'
    },
    riskLevelIcon() {
      if (!this.identityHealth) return 'fas fa-question-circle'
      const riskLevel = this.identityHealth.current_risk_level
      const icons = {
        low: 'fas fa-check-circle',
        medium: 'fas fa-exclamation-triangle',
        high: 'fas fa-exclamation-circle',
        critical: 'fas fa-radiation'
      }
      return icons[riskLevel] || 'fas fa-question-circle'
    },
    alertClass() {
      return `alert-${this.alertType}`
    },
    alertIcon() {
      const icons = {
        info: 'fas fa-info-circle',
        warning: 'fas fa-exclamation-triangle',
        error: 'fas fa-times-circle',
        success: 'fas fa-check-circle'
      }
      return icons[this.alertType] || icons.info
    }
  },
  mounted() {
    this.loadIdentityHealth()
    this.startAutoRefresh()
  },
  beforeDestroy() {
    this.stopAutoRefresh()
  },
  methods: {
    async loadIdentityHealth() {
      this.loading = true
      this.error = null
      
      try {
        // Simulate API call - replace with actual endpoint
        const response = await fetch('/api/identity/health')
        if (!response.ok) {
          throw new Error('Failed to load identity health data')
        }
        
        const data = await response.json()
        this.identityHealth = data
        this.statistics = data.statistics || {}
        this.protectionStatus = data.protection_enabled || {}
        this.recentActivities = data.recent_activities || []
        
        this.checkForAlerts()
      } catch (error) {
        this.error = error.message
        console.error('Failed to load identity health:', error)
      } finally {
        this.loading = false
      }
    },
    refreshData() {
      this.loadIdentityHealth()
    },
    toggleDetails() {
      this.showDetails = !this.showDetails
    },
    startAutoRefresh() {
      this.autoRefreshInterval = setInterval(() => {
        this.loadIdentityHealth()
      }, 10000) // Refresh every 10 seconds
    },
    stopAutoRefresh() {
      if (this.autoRefreshInterval) {
        clearInterval(this.autoRefreshInterval)
        this.autoRefreshInterval = null
      }
    },
    getActivityClass(activity) {
      const riskLevel = activity.risk_level
      return `activity-${riskLevel}`
    },
    getActivityIcon(activity) {
      const eventType = activity.event_type
      const icons = {
        'rate_limit_exceeded': 'fas fa-ban',
        'repetitive_message': 'fas fa-redo',
        'sensitive_data_detected': 'fas fa-shield-alt',
        'mood_randomized': 'fas fa-heart',
        'emote_randomized': 'fas fa-smile',
        'movement_randomized': 'fas fa-random',
        'log_sanitized': 'fas fa-eraser',
        'repetitive_action_detected': 'fas fa-exclamation-triangle'
      }
      return icons[eventType] || 'fas fa-info-circle'
    },
    formatActivityType(eventType) {
      return eventType.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    },
    formatTime(timestamp) {
      if (!timestamp) return 'Unknown'
      const date = new Date(timestamp * 1000)
      return date.toLocaleTimeString()
    },
    getRiskClass(riskLevel) {
      return `risk-${riskLevel}`
    },
    formatLastRiskEvent() {
      if (!this.identityHealth?.last_risk_event) return 'None'
      return this.formatTime(this.identityHealth.last_risk_event)
    },
    checkForAlerts() {
      if (!this.identityHealth) return
      
      const riskLevel = this.identityHealth.current_risk_level
      const riskEvents = this.statistics.risk_events
      
      if (riskLevel === 'critical') {
        this.showAlert('Critical risk level detected! Immediate attention required.', 'error')
      } else if (riskLevel === 'high') {
        this.showAlert('High risk level detected. Monitor closely.', 'warning')
      } else if (riskEvents > 10) {
        this.showAlert('Multiple risk events detected. Review protection settings.', 'warning')
      }
    },
    showAlert(message, type = 'info') {
      this.alertMessage = message
      this.alertType = type
      
      // Auto-dismiss after 5 seconds
      setTimeout(() => {
        this.dismissAlert()
      }, 5000)
    },
    dismissAlert() {
      this.alertMessage = null
      this.alertType = 'info'
    }
  }
}
</script>

<style scoped>
.identity-health {
  background: #1a1a1a;
  border-radius: 8px;
  padding: 20px;
  color: #ffffff;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #333;
}

.header h2 {
  margin: 0;
  color: #ffffff;
  font-size: 1.5rem;
  font-weight: 600;
}

.header-controls {
  display: flex;
  gap: 10px;
}

.header-controls button {
  background: #2a2a2a;
  border: 1px solid #444;
  color: #ffffff;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 0.9rem;
}

.header-controls button:hover {
  background: #3a3a3a;
  border-color: #555;
}

.header-controls button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading, .error {
  text-align: center;
  padding: 40px;
  color: #cccccc;
}

.spinner {
  border: 3px solid #333;
  border-top: 3px solid #007bff;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
  margin: 0 auto 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  color: #ff6b6b;
}

.error button {
  background: #ff6b6b;
  border: none;
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}

.risk-indicator {
  display: flex;
  align-items: center;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  background: #2a2a2a;
}

.risk-low {
  border-left: 4px solid #28a745;
}

.risk-medium {
  border-left: 4px solid #ffc107;
}

.risk-high {
  border-left: 4px solid #fd7e14;
}

.risk-critical {
  border-left: 4px solid #dc3545;
}

.risk-icon {
  margin-right: 15px;
  font-size: 1.5rem;
}

.risk-low .risk-icon {
  color: #28a745;
}

.risk-medium .risk-icon {
  color: #ffc107;
}

.risk-high .risk-icon {
  color: #fd7e14;
}

.risk-critical .risk-icon {
  color: #dc3545;
}

.risk-info h3 {
  margin: 0 0 5px 0;
  font-size: 1.2rem;
  font-weight: 600;
}

.risk-info p {
  margin: 0;
  color: #cccccc;
  font-size: 0.9rem;
}

.protection-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.card {
  background: #2a2a2a;
  border: 1px solid #444;
  border-radius: 6px;
  padding: 15px;
  transition: all 0.2s ease;
}

.card.active {
  border-color: #28a745;
  background: #1e3a1e;
}

.card-icon {
  font-size: 1.5rem;
  margin-bottom: 10px;
  color: #007bff;
}

.card.active .card-icon {
  color: #28a745;
}

.card-content h4 {
  margin: 0 0 5px 0;
  font-size: 1rem;
  font-weight: 600;
}

.card-content p {
  margin: 0;
  color: #cccccc;
  font-size: 0.9rem;
}

.statistics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  background: #2a2a2a;
  border: 1px solid #444;
  border-radius: 6px;
  padding: 15px;
  text-align: center;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #007bff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 0.8rem;
  color: #cccccc;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.details-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #333;
}

.activities-section, .metrics-section {
  margin-bottom: 20px;
}

.activities-section h3, .metrics-section h3 {
  margin: 0 0 15px 0;
  color: #ffffff;
  font-size: 1.1rem;
  font-weight: 600;
}

.activities-list {
  max-height: 300px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: center;
  padding: 10px;
  background: #2a2a2a;
  border-radius: 4px;
  margin-bottom: 8px;
  border-left: 3px solid #444;
}

.activity-low {
  border-left-color: #28a745;
}

.activity-medium {
  border-left-color: #ffc107;
}

.activity-high {
  border-left-color: #fd7e14;
}

.activity-critical {
  border-left-color: #dc3545;
}

.activity-icon {
  margin-right: 12px;
  font-size: 1.1rem;
  color: #007bff;
}

.activity-content {
  flex: 1;
}

.activity-type {
  font-weight: 600;
  color: #ffffff;
  font-size: 0.9rem;
}

.activity-time {
  color: #888;
  font-size: 0.8rem;
  margin-top: 2px;
}

.activity-action {
  color: #007bff;
  font-size: 0.8rem;
  margin-top: 2px;
}

.activity-risk {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
}

.risk-low {
  background: #28a745;
  color: white;
}

.risk-medium {
  background: #ffc107;
  color: #212529;
}

.risk-high {
  background: #fd7e14;
  color: white;
}

.risk-critical {
  background: #dc3545;
  color: white;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.metric-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background: #2a2a2a;
  border-radius: 4px;
  border: 1px solid #444;
}

.metric-item label {
  color: #cccccc;
  font-size: 0.9rem;
}

.metric-item span {
  color: #007bff;
  font-weight: 600;
}

.alert-message {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  border-radius: 6px;
  margin-top: 15px;
  font-size: 0.9rem;
}

.alert-info {
  background: #1e3a5f;
  border: 1px solid #0056b3;
  color: #b3d9ff;
}

.alert-warning {
  background: #3d2c1e;
  border: 1px solid #856404;
  color: #ffeaa7;
}

.alert-error {
  background: #3d1e1e;
  border: 1px solid #721c24;
  color: #f5c6cb;
}

.alert-success {
  background: #1e3d1e;
  border: 1px solid #155724;
  color: #c3e6cb;
}

.alert-message i {
  margin-right: 10px;
  font-size: 1.1rem;
}

.alert-dismiss {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  margin-left: auto;
  padding: 0;
  font-size: 1rem;
}

.alert-dismiss:hover {
  opacity: 0.7;
}

/* Responsive Design */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .protection-cards {
    grid-template-columns: 1fr;
  }
  
  .statistics {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .metrics-grid {
    grid-template-columns: 1fr;
  }
}
</style> 