<template>
  <div class="pvp-status-badge" :class="statusClass">
    <!-- Main Status Display -->
    <div class="status-header">
      <div class="status-icon">
        <i :class="statusIcon"></i>
      </div>
      <div class="status-content">
        <h3 class="status-title">PvP Status</h3>
        <div class="risk-indicator">
          <span class="risk-level">{{ riskLevel }}</span>
          <span class="risk-score">{{ (riskScore * 100).toFixed(0) }}%</span>
        </div>
      </div>
      <div class="status-actions">
        <button 
          @click="refreshStatus" 
          :disabled="loading"
          class="refresh-btn"
          :title="loading ? 'Refreshing...' : 'Refresh Status'"
        >
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
        </button>
        <button 
          @click="toggleDetails" 
          class="details-btn"
          :title="showDetails ? 'Hide Details' : 'Show Details'"
        >
          <i class="fas" :class="showDetails ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
        </button>
      </div>
    </div>

    <!-- Risk Progress Bar -->
    <div class="risk-progress">
      <div class="progress-bar">
        <div 
          class="progress-fill" 
          :style="{ width: (riskScore * 100) + '%' }"
          :class="progressClass"
        ></div>
      </div>
      <div class="progress-labels">
        <span class="label">Safe</span>
        <span class="label">Medium</span>
        <span class="label">High</span>
        <span class="label">Critical</span>
      </div>
    </div>

    <!-- Detailed Information -->
    <div v-if="showDetails" class="status-details">
      <!-- Current Strategy -->
      <div class="detail-section">
        <h4>Current Strategy</h4>
        <div class="strategy-info">
          <span class="strategy-name">{{ strategy }}</span>
          <span class="strategy-description">{{ strategyDescription }}</span>
        </div>
      </div>

      <!-- Nearby Players -->
      <div class="detail-section">
        <h4>Nearby Players</h4>
        <div class="player-count">
          <span class="count">{{ nearbyPlayers }}</span>
          <span class="label">players detected</span>
        </div>
        <div v-if="nearbyPlayers > 0" class="player-list">
          <div 
            v-for="player in recentPlayers" 
            :key="player.name"
            class="player-item"
            :class="player.risk_level"
          >
            <span class="player-name">{{ player.name }}</span>
            <span class="player-faction">{{ player.faction }}</span>
            <span class="player-risk">{{ player.risk_type }}</span>
            <span class="player-distance">{{ player.distance }}m</span>
          </div>
        </div>
      </div>

      <!-- Active Zones -->
      <div class="detail-section">
        <h4>Active Zones</h4>
        <div class="zone-count">
          <span class="count">{{ activeZones }}</span>
          <span class="label">zones monitored</span>
        </div>
        <div v-if="activeZones > 0" class="zone-list">
          <div 
            v-for="zone in recentZones" 
            :key="zone.zone_name"
            class="zone-item"
            :class="zone.risk_level"
          >
            <span class="zone-name">{{ zone.zone_name }}</span>
            <span class="zone-planet">{{ zone.planet }}</span>
            <span class="zone-risk">{{ zone.risk_level }}</span>
            <span class="zone-players">{{ zone.player_count }} players</span>
          </div>
        </div>
      </div>

      <!-- Recent Events -->
      <div class="detail-section">
        <h4>Recent Events</h4>
        <div class="event-count">
          <span class="count">{{ recentEvents }}</span>
          <span class="label">events in last hour</span>
        </div>
        <div v-if="recentEvents > 0" class="event-list">
          <div 
            v-for="event in recentEventList" 
            :key="event.event_id"
            class="event-item"
            :class="event.risk_level"
          >
            <span class="event-time">{{ formatTime(event.timestamp) }}</span>
            <span class="event-type">{{ event.event_type }}</span>
            <span class="event-description">{{ event.description }}</span>
          </div>
        </div>
      </div>

      <!-- Statistics -->
      <div class="detail-section">
        <h4>Statistics</h4>
        <div class="stats-grid">
          <div class="stat-item">
            <span class="stat-label">Average Risk</span>
            <span class="stat-value">{{ (averageRiskScore * 100).toFixed(1) }}%</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Risk Trend</span>
            <span class="stat-value" :class="trendClass">{{ riskTrend }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Last Assessment</span>
            <span class="stat-value">{{ formatTime(lastAssessment) }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Total Events</span>
            <span class="stat-value">{{ totalEvents }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Alert Messages -->
    <div v-if="alertMessage" class="alert-message" :class="alertClass">
      <i class="fas" :class="alertIcon"></i>
      <span>{{ alertMessage }}</span>
      <button @click="dismissAlert" class="alert-dismiss">
        <i class="fas fa-times"></i>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PvPStatusBadge',
  data() {
    return {
      loading: false,
      showDetails: false,
      alertMessage: '',
      alertClass: '',
      statusData: {
        risk_score: 0.0,
        risk_level: 'low',
        strategy: 'log_only',
        nearby_players: 0,
        active_zones: 0,
        last_assessment: new Date().toISOString(),
        recent_events: 0
      },
      recentPlayers: [],
      recentZones: [],
      recentEventList: [],
      statistics: {
        average_risk_score: 0.0,
        risk_trend: 'stable',
        total_events: 0
      },
      updateInterval: null
    }
  },
  computed: {
    riskScore() {
      return this.statusData.risk_score || 0.0
    },
    riskLevel() {
      return this.statusData.risk_level || 'low'
    },
    strategy() {
      return this.statusData.strategy || 'log_only'
    },
    nearbyPlayers() {
      return this.statusData.nearby_players || 0
    },
    activeZones() {
      return this.statusData.active_zones || 0
    },
    recentEvents() {
      return this.statusData.recent_events || 0
    },
    lastAssessment() {
      return this.statusData.last_assessment || new Date().toISOString()
    },
    averageRiskScore() {
      return this.statistics.average_risk_score || 0.0
    },
    riskTrend() {
      return this.statistics.risk_trend || 'stable'
    },
    totalEvents() {
      return this.statistics.total_events || 0
    },
    statusClass() {
      return {
        'status-low': this.riskLevel === 'low',
        'status-medium': this.riskLevel === 'medium',
        'status-high': this.riskLevel === 'high',
        'status-critical': this.riskLevel === 'critical'
      }
    },
    statusIcon() {
      const icons = {
        low: 'fas fa-shield-alt',
        medium: 'fas fa-exclamation-triangle',
        high: 'fas fa-exclamation-circle',
        critical: 'fas fa-radiation'
      }
      return icons[this.riskLevel] || 'fas fa-shield-alt'
    },
    progressClass() {
      return {
        'progress-low': this.riskLevel === 'low',
        'progress-medium': this.riskLevel === 'medium',
        'progress-high': this.riskLevel === 'high',
        'progress-critical': this.riskLevel === 'critical'
      }
    },
    strategyDescription() {
      const descriptions = {
        log_only: 'Logging PvP activity only',
        soft_path_deviation: 'Deviating from current path',
        safe_spot_wait: 'Moving to safe spot',
        mount_escape: 'Mounting for rapid escape',
        zone_change: 'Changing to safer zone',
        session_pause: 'Pausing session for safety'
      }
      return descriptions[this.strategy] || 'Unknown strategy'
    },
    trendClass() {
      return {
        'trend-increasing': this.riskTrend === 'increasing',
        'trend-decreasing': this.riskTrend === 'decreasing',
        'trend-stable': this.riskTrend === 'stable'
      }
    },
    alertIcon() {
      return this.alertClass.includes('error') ? 'fa-exclamation-triangle' : 'fa-info-circle'
    }
  },
  mounted() {
    this.loadStatus()
    this.startAutoUpdate()
  },
  beforeDestroy() {
    this.stopAutoUpdate()
  },
  methods: {
    async loadStatus() {
      this.loading = true
      try {
        const response = await fetch('/api/pvp/status')
        if (response.ok) {
          const data = await response.json()
          this.statusData = data.status
          this.recentPlayers = data.recent_players || []
          this.recentZones = data.recent_zones || []
          this.recentEventList = data.recent_events || []
          this.statistics = data.statistics || {}
          
          // Check for alerts
          this.checkForAlerts()
        } else {
          throw new Error('Failed to load PvP status')
        }
      } catch (error) {
        console.error('Error loading PvP status:', error)
        this.showAlert('Failed to load PvP status', 'error')
      } finally {
        this.loading = false
      }
    },
    async refreshStatus() {
      await this.loadStatus()
    },
    toggleDetails() {
      this.showDetails = !this.showDetails
    },
    startAutoUpdate() {
      this.updateInterval = setInterval(() => {
        this.loadStatus()
      }, 5000) // Update every 5 seconds
    },
    stopAutoUpdate() {
      if (this.updateInterval) {
        clearInterval(this.updateInterval)
        this.updateInterval = null
      }
    },
    checkForAlerts() {
      if (this.riskLevel === 'critical') {
        this.showAlert('Critical PvP risk detected!', 'error')
      } else if (this.riskLevel === 'high') {
        this.showAlert('High PvP risk detected', 'warning')
      } else if (this.nearbyPlayers > 5) {
        this.showAlert(`${this.nearbyPlayers} nearby players detected`, 'info')
      }
    },
    showAlert(message, type = 'info') {
      this.alertMessage = message
      this.alertClass = `alert-${type}`
      
      // Auto-dismiss after 5 seconds
      setTimeout(() => {
        this.dismissAlert()
      }, 5000)
    },
    dismissAlert() {
      this.alertMessage = ''
      this.alertClass = ''
    },
    formatTime(timestamp) {
      if (!timestamp) return 'Unknown'
      
      const date = new Date(timestamp)
      const now = new Date()
      const diff = now - date
      
      if (diff < 60000) { // Less than 1 minute
        return 'Just now'
      } else if (diff < 3600000) { // Less than 1 hour
        const minutes = Math.floor(diff / 60000)
        return `${minutes}m ago`
      } else if (diff < 86400000) { // Less than 1 day
        const hours = Math.floor(diff / 3600000)
        return `${hours}h ago`
      } else {
        return date.toLocaleDateString()
      }
    }
  }
}
</script>

<style scoped>
.pvp-status-badge {
  background: #1a1a1a;
  border: 1px solid #333;
  border-radius: 8px;
  padding: 16px;
  margin: 8px;
  min-width: 300px;
  transition: all 0.3s ease;
}

.pvp-status-badge:hover {
  border-color: #555;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

/* Status Classes */
.status-low {
  border-left: 4px solid #28a745;
}

.status-medium {
  border-left: 4px solid #ffc107;
}

.status-high {
  border-left: 4px solid #fd7e14;
}

.status-critical {
  border-left: 4px solid #dc3545;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(220, 53, 69, 0.7); }
  70% { box-shadow: 0 0 0 10px rgba(220, 53, 69, 0); }
  100% { box-shadow: 0 0 0 0 rgba(220, 53, 69, 0); }
}

/* Header */
.status-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.status-icon {
  font-size: 24px;
  margin-right: 12px;
  width: 40px;
  text-align: center;
}

.status-content {
  flex: 1;
}

.status-title {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

.risk-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
}

.risk-level {
  font-size: 14px;
  font-weight: 500;
  text-transform: uppercase;
  color: #ccc;
}

.risk-score {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
}

.status-actions {
  display: flex;
  gap: 4px;
}

.refresh-btn,
.details-btn {
  background: #333;
  border: none;
  border-radius: 4px;
  padding: 6px 8px;
  color: #ccc;
  cursor: pointer;
  transition: all 0.2s ease;
}

.refresh-btn:hover,
.details-btn:hover {
  background: #555;
  color: #fff;
}

.refresh-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Progress Bar */
.risk-progress {
  margin-bottom: 12px;
}

.progress-bar {
  height: 8px;
  background: #333;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 4px;
}

.progress-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.progress-low {
  background: linear-gradient(90deg, #28a745, #20c997);
}

.progress-medium {
  background: linear-gradient(90deg, #ffc107, #fd7e14);
}

.progress-high {
  background: linear-gradient(90deg, #fd7e14, #dc3545);
}

.progress-critical {
  background: linear-gradient(90deg, #dc3545, #6f42c1);
  animation: pulse 2s infinite;
}

.progress-labels {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: #666;
}

/* Details */
.status-details {
  border-top: 1px solid #333;
  padding-top: 12px;
  margin-top: 12px;
}

.detail-section {
  margin-bottom: 16px;
}

.detail-section h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: #ccc;
  text-transform: uppercase;
}

.strategy-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.strategy-name {
  font-size: 16px;
  font-weight: 600;
  color: #fff;
  text-transform: capitalize;
}

.strategy-description {
  font-size: 12px;
  color: #999;
}

.player-count,
.zone-count,
.event-count {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.count {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
}

.label {
  font-size: 12px;
  color: #999;
}

.player-list,
.zone-list,
.event-list {
  max-height: 120px;
  overflow-y: auto;
}

.player-item,
.zone-item,
.event-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 8px;
  margin-bottom: 2px;
  border-radius: 4px;
  font-size: 12px;
  background: #222;
}

.player-item.low,
.zone-item.low,
.event-item.low {
  border-left: 3px solid #28a745;
}

.player-item.medium,
.zone-item.medium,
.event-item.medium {
  border-left: 3px solid #ffc107;
}

.player-item.high,
.zone-item.high,
.event-item.high {
  border-left: 3px solid #fd7e14;
}

.player-item.critical,
.zone-item.critical,
.event-item.critical {
  border-left: 3px solid #dc3545;
}

.player-name,
.zone-name {
  font-weight: 600;
  color: #fff;
}

.player-faction,
.zone-planet {
  color: #999;
}

.player-risk,
.zone-risk {
  color: #ccc;
  text-transform: capitalize;
}

.player-distance,
.zone-players {
  color: #666;
}

.event-time {
  color: #999;
  font-size: 10px;
}

.event-type {
  color: #ccc;
  text-transform: capitalize;
}

.event-description {
  color: #999;
  font-size: 11px;
}

/* Statistics */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-label {
  font-size: 10px;
  color: #666;
  text-transform: uppercase;
}

.stat-value {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
}

.trend-increasing {
  color: #dc3545;
}

.trend-decreasing {
  color: #28a745;
}

.trend-stable {
  color: #ffc107;
}

/* Alerts */
.alert-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 4px;
  margin-top: 8px;
  font-size: 12px;
}

.alert-info {
  background: rgba(13, 202, 240, 0.1);
  border: 1px solid rgba(13, 202, 240, 0.3);
  color: #0dcaf0;
}

.alert-warning {
  background: rgba(255, 193, 7, 0.1);
  border: 1px solid rgba(255, 193, 7, 0.3);
  color: #ffc107;
}

.alert-error {
  background: rgba(220, 53, 69, 0.1);
  border: 1px solid rgba(220, 53, 69, 0.3);
  color: #dc3545;
}

.alert-dismiss {
  background: none;
  border: none;
  color: inherit;
  cursor: pointer;
  margin-left: auto;
  padding: 2px 4px;
  border-radius: 2px;
  transition: background 0.2s ease;
}

.alert-dismiss:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* Scrollbar */
.player-list::-webkit-scrollbar,
.zone-list::-webkit-scrollbar,
.event-list::-webkit-scrollbar {
  width: 4px;
}

.player-list::-webkit-scrollbar-track,
.zone-list::-webkit-scrollbar-track,
.event-list::-webkit-scrollbar-track {
  background: #222;
}

.player-list::-webkit-scrollbar-thumb,
.zone-list::-webkit-scrollbar-thumb,
.event-list::-webkit-scrollbar-thumb {
  background: #555;
  border-radius: 2px;
}

.player-list::-webkit-scrollbar-thumb:hover,
.zone-list::-webkit-scrollbar-thumb:hover,
.event-list::-webkit-scrollbar-thumb:hover {
  background: #777;
}
</style> 