<template>
  <div class="recovery-timeline">
    <!-- Header -->
    <div class="timeline-header">
      <h3 class="timeline-title">
        <i class="fas fa-history"></i>
        Recovery Timeline
      </h3>
      <div class="timeline-controls">
        <button 
          @click="refreshTimeline" 
          :disabled="isLoading"
          class="refresh-btn"
          :title="'Refresh timeline'"
        >
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': isLoading }"></i>
        </button>
        <button 
          @click="toggleAutoRefresh" 
          :class="{ 'active': autoRefresh }"
          class="auto-refresh-btn"
          :title="autoRefresh ? 'Disable auto-refresh' : 'Enable auto-refresh'"
        >
          <i class="fas fa-clock"></i>
        </button>
        <button 
          @click="toggleDetails" 
          class="details-btn"
          :title="showDetails ? 'Hide details' : 'Show details'"
        >
          <i class="fas fa-info-circle"></i>
        </button>
      </div>
    </div>

    <!-- Status Summary -->
    <div class="status-summary" v-if="recoveryStatus">
      <div class="status-indicator" :class="statusClass">
        <i :class="statusIcon"></i>
        <span class="status-text">{{ statusText }}</span>
      </div>
      <div class="statistics" v-if="showDetails">
        <div class="stat-item">
          <span class="stat-label">Total Attempts:</span>
          <span class="stat-value">{{ recoveryStatus.statistics?.total_attempts || 0 }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Successful:</span>
          <span class="stat-value success">{{ recoveryStatus.statistics?.successful_attempts || 0 }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Failed:</span>
          <span class="stat-value failed">{{ recoveryStatus.statistics?.failed_attempts || 0 }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Skipped:</span>
          <span class="stat-value skipped">{{ recoveryStatus.statistics?.skipped_attempts || 0 }}</span>
        </div>
      </div>
    </div>

    <!-- Current Recovery -->
    <div class="current-recovery" v-if="recoveryStatus?.current_attempt">
      <div class="current-header">
        <h4>Current Recovery</h4>
        <span class="progress-indicator">
          <i class="fas fa-cog fa-spin"></i>
          In Progress
        </span>
      </div>
      <div class="current-details">
        <div class="action-info">
          <strong>Action:</strong> {{ getActionDisplayName(recoveryStatus.current_attempt.action) }}
        </div>
        <div class="duration-info">
          <strong>Duration:</strong> {{ formatDuration(recoveryStatus.current_attempt.start_time) }}
        </div>
        <div class="cooldown-info" v-if="recoveryStatus.current_attempt.cooldown_until">
          <strong>Cooldown Until:</strong> {{ formatTime(recoveryStatus.current_attempt.cooldown_until) }}
        </div>
      </div>
    </div>

    <!-- Timeline -->
    <div class="timeline-container">
      <div class="timeline" v-if="timeline.length > 0">
        <div 
          v-for="(event, index) in timeline" 
          :key="index"
          class="timeline-event"
          :class="getEventClass(event)"
        >
          <!-- Timeline Line -->
          <div class="timeline-line" v-if="index < timeline.length - 1"></div>
          
          <!-- Event Icon -->
          <div class="event-icon">
            <i :class="getEventIcon(event)"></i>
          </div>
          
          <!-- Event Content -->
          <div class="event-content">
            <div class="event-header">
              <h5 class="event-title">{{ event.title }}</h5>
              <span class="event-time">{{ formatTime(event.timestamp) }}</span>
            </div>
            <p class="event-description">{{ event.description }}</p>
            
            <!-- Event Details -->
            <div class="event-details" v-if="showDetails && event.details">
              <div class="details-toggle" @click="toggleEventDetails(index)">
                <span>Details</span>
                <i class="fas fa-chevron-down" :class="{ 'rotated': expandedEvents[index] }"></i>
              </div>
              <div class="details-content" v-if="expandedEvents[index]">
                <pre class="details-json">{{ formatDetails(event.details) }}</pre>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Empty State -->
      <div class="empty-timeline" v-else>
        <i class="fas fa-history"></i>
        <p>No recovery events yet</p>
        <small>Recovery events will appear here when stuck states are detected and recovery actions are taken.</small>
      </div>
    </div>

    <!-- Cooldowns -->
    <div class="cooldowns-section" v-if="showDetails && recoveryStatus?.cooldowns">
      <h4>Action Cooldowns</h4>
      <div class="cooldown-list">
        <div 
          v-for="(until, action) in recoveryStatus.cooldowns" 
          :key="action"
          class="cooldown-item"
        >
          <span class="action-name">{{ getActionDisplayName(action) }}</span>
          <span class="cooldown-time">{{ formatTime(until) }}</span>
          <span class="cooldown-status" :class="getCooldownStatusClass(until)">
            {{ getCooldownStatusText(until) }}
          </span>
        </div>
      </div>
    </div>

    <!-- Alert Messages -->
    <div v-if="alertMessage" class="alert-message" :class="alertClass">
      <i :class="alertIcon"></i>
      <span>{{ alertMessage }}</span>
      <button @click="dismissAlert" class="dismiss-btn">
        <i class="fas fa-times"></i>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RecoveryTimeline',
  data() {
    return {
      recoveryStatus: null,
      timeline: [],
      isLoading: false,
      autoRefresh: true,
      showDetails: false,
      expandedEvents: {},
      alertMessage: null,
      alertType: 'info',
      refreshInterval: null
    }
  },
  computed: {
    statusClass() {
      if (!this.recoveryStatus) return 'idle'
      if (this.recoveryStatus.is_recovering) return 'recovering'
      if (this.recoveryStatus.stuck_detection) return 'stuck'
      return 'idle'
    },
    statusIcon() {
      const icons = {
        idle: 'fas fa-check-circle',
        recovering: 'fas fa-cog fa-spin',
        stuck: 'fas fa-exclamation-triangle'
      }
      return icons[this.statusClass] || 'fas fa-info-circle'
    },
    statusText() {
      if (!this.recoveryStatus) return 'No Recovery Data'
      if (this.recoveryStatus.is_recovering) return 'Recovery in Progress'
      if (this.recoveryStatus.stuck_detection) return 'Stuck State Detected'
      return 'System Idle'
    },
    alertClass() {
      return `alert-${this.alertType}`
    },
    alertIcon() {
      const icons = {
        info: 'fas fa-info-circle',
        success: 'fas fa-check-circle',
        warning: 'fas fa-exclamation-triangle',
        error: 'fas fa-times-circle'
      }
      return icons[this.alertType] || 'fas fa-info-circle'
    }
  },
  mounted() {
    this.loadRecoveryData()
    this.startAutoRefresh()
  },
  beforeDestroy() {
    this.stopAutoRefresh()
  },
  methods: {
    async loadRecoveryData() {
      try {
        this.isLoading = true
        
        // Load recovery status
        const statusResponse = await fetch('/api/recovery/status')
        if (statusResponse.ok) {
          this.recoveryStatus = await statusResponse.json()
        }
        
        // Load timeline
        const timelineResponse = await fetch('/api/recovery/timeline')
        if (timelineResponse.ok) {
          this.timeline = await timelineResponse.json()
        }
        
        this.checkForAlerts()
      } catch (error) {
        console.error('Failed to load recovery data:', error)
        this.showAlert('Failed to load recovery data', 'error')
      } finally {
        this.isLoading = false
      }
    },
    
    async refreshTimeline() {
      await this.loadRecoveryData()
    },
    
    toggleAutoRefresh() {
      this.autoRefresh = !this.autoRefresh
      if (this.autoRefresh) {
        this.startAutoRefresh()
      } else {
        this.stopAutoRefresh()
      }
    },
    
    startAutoRefresh() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval)
      }
      this.refreshInterval = setInterval(() => {
        this.loadRecoveryData()
      }, 5000) // Refresh every 5 seconds
    },
    
    stopAutoRefresh() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval)
        this.refreshInterval = null
      }
    },
    
    toggleDetails() {
      this.showDetails = !this.showDetails
    },
    
    toggleEventDetails(index) {
      this.$set(this.expandedEvents, index, !this.expandedEvents[index])
    },
    
    getEventClass(event) {
      const classes = {
        'stuck_detected': 'event-stuck',
        'recovery_attempt': 'event-recovery',
        'recovery_completed': 'event-completed'
      }
      return classes[event.type] || 'event-default'
    },
    
    getEventIcon(event) {
      const icons = {
        'stuck_detected': 'fas fa-exclamation-triangle',
        'recovery_attempt': 'fas fa-tools',
        'recovery_completed': 'fas fa-check-circle'
      }
      return icons[event.type] || 'fas fa-info-circle'
    },
    
    getActionDisplayName(action) {
      const actionNames = {
        'micro_path_jitter': 'Micro Path Jitter',
        'mount_toggle': 'Mount Toggle',
        'face_camera_rescan': 'Face Camera & Re-scan',
        'nearest_navmesh_waypoint': 'Nearest Navmesh Waypoint',
        'shuttle_fallback': 'Shuttle Fallback',
        'safe_logout': 'Safe Logout'
      }
      return actionNames[action] || action
    },
    
    formatTime(timestamp) {
      if (!timestamp) return 'N/A'
      const date = new Date(timestamp * 1000)
      return date.toLocaleTimeString()
    },
    
    formatDuration(startTime) {
      if (!startTime) return 'N/A'
      const duration = (Date.now() / 1000) - startTime
      return `${Math.floor(duration)}s`
    },
    
    formatDetails(details) {
      return JSON.stringify(details, null, 2)
    },
    
    getCooldownStatusClass(until) {
      const now = Date.now() / 1000
      if (until <= now) return 'available'
      if (until - now < 60) return 'soon'
      return 'cooldown'
    },
    
    getCooldownStatusText(until) {
      const now = Date.now() / 1000
      if (until <= now) return 'Available'
      const remaining = until - now
      if (remaining < 60) return `${Math.floor(remaining)}s`
      if (remaining < 3600) return `${Math.floor(remaining / 60)}m`
      return `${Math.floor(remaining / 3600)}h`
    },
    
    checkForAlerts() {
      if (this.recoveryStatus?.is_recovering) {
        this.showAlert('Recovery in progress', 'warning')
      } else if (this.recoveryStatus?.stuck_detection) {
        this.showAlert('Stuck state detected', 'error')
      } else if (this.recoveryStatus?.statistics?.failed_attempts > 0) {
        this.showAlert(`${this.recoveryStatus.statistics.failed_attempts} recovery attempts failed`, 'warning')
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
    }
  }
}
</script>

<style scoped>
.recovery-timeline {
  background: #1a1a1a;
  border-radius: 8px;
  padding: 20px;
  color: #ffffff;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #333;
}

.timeline-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
  display: flex;
  align-items: center;
  gap: 8px;
}

.timeline-controls {
  display: flex;
  gap: 8px;
}

.timeline-controls button {
  background: #333;
  border: none;
  color: #ffffff;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.timeline-controls button:hover {
  background: #444;
}

.timeline-controls button.active {
  background: #007bff;
}

.timeline-controls button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.status-summary {
  background: #2a2a2a;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 20px;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 500;
}

.status-indicator.idle {
  color: #28a745;
}

.status-indicator.recovering {
  color: #ffc107;
}

.status-indicator.stuck {
  color: #dc3545;
}

.statistics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #444;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  color: #aaa;
  font-size: 14px;
}

.stat-value {
  font-weight: 600;
  font-size: 16px;
}

.stat-value.success {
  color: #28a745;
}

.stat-value.failed {
  color: #dc3545;
}

.stat-value.skipped {
  color: #ffc107;
}

.current-recovery {
  background: #2a2a2a;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 20px;
  border-left: 4px solid #007bff;
}

.current-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.current-header h4 {
  margin: 0;
  color: #ffffff;
}

.progress-indicator {
  color: #007bff;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 5px;
}

.current-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}

.action-info, .duration-info, .cooldown-info {
  font-size: 14px;
}

.timeline-container {
  max-height: 400px;
  overflow-y: auto;
}

.timeline {
  position: relative;
  padding-left: 30px;
}

.timeline-event {
  position: relative;
  margin-bottom: 20px;
}

.timeline-line {
  position: absolute;
  left: 15px;
  top: 30px;
  bottom: -20px;
  width: 2px;
  background: #444;
}

.event-icon {
  position: absolute;
  left: -15px;
  top: 5px;
  width: 30px;
  height: 30px;
  background: #333;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  z-index: 2;
}

.event-stuck .event-icon {
  background: #dc3545;
}

.event-recovery .event-icon {
  background: #007bff;
}

.event-completed .event-icon {
  background: #28a745;
}

.event-content {
  background: #2a2a2a;
  border-radius: 6px;
  padding: 15px;
  margin-left: 20px;
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.event-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
}

.event-time {
  color: #aaa;
  font-size: 12px;
}

.event-description {
  margin: 0 0 10px 0;
  color: #ccc;
  font-size: 14px;
}

.event-details {
  border-top: 1px solid #444;
  padding-top: 10px;
}

.details-toggle {
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  color: #007bff;
  font-size: 14px;
  font-weight: 500;
}

.details-toggle:hover {
  color: #0056b3;
}

.details-toggle .fa-chevron-down {
  transition: transform 0.2s ease;
}

.details-toggle .fa-chevron-down.rotated {
  transform: rotate(180deg);
}

.details-content {
  margin-top: 10px;
  padding: 10px;
  background: #1a1a1a;
  border-radius: 4px;
}

.details-json {
  margin: 0;
  font-size: 12px;
  color: #ccc;
  white-space: pre-wrap;
  word-break: break-all;
}

.empty-timeline {
  text-align: center;
  padding: 40px 20px;
  color: #aaa;
}

.empty-timeline i {
  font-size: 48px;
  margin-bottom: 15px;
  opacity: 0.5;
}

.empty-timeline p {
  margin: 0 0 10px 0;
  font-size: 16px;
  font-weight: 500;
}

.empty-timeline small {
  font-size: 14px;
  opacity: 0.7;
}

.cooldowns-section {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #333;
}

.cooldowns-section h4 {
  margin: 0 0 15px 0;
  color: #ffffff;
}

.cooldown-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.cooldown-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #2a2a2a;
  border-radius: 4px;
  font-size: 14px;
}

.action-name {
  color: #ffffff;
  font-weight: 500;
}

.cooldown-time {
  color: #aaa;
}

.cooldown-status {
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 3px;
  font-size: 12px;
}

.cooldown-status.available {
  background: #28a745;
  color: #ffffff;
}

.cooldown-status.soon {
  background: #ffc107;
  color: #000000;
}

.cooldown-status.cooldown {
  background: #6c757d;
  color: #ffffff;
}

.alert-message {
  position: fixed;
  top: 20px;
  right: 20px;
  background: #2a2a2a;
  border-radius: 6px;
  padding: 15px 20px;
  color: #ffffff;
  display: flex;
  align-items: center;
  gap: 10px;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  animation: slideIn 0.3s ease;
}

.alert-info {
  border-left: 4px solid #007bff;
}

.alert-success {
  border-left: 4px solid #28a745;
}

.alert-warning {
  border-left: 4px solid #ffc107;
}

.alert-error {
  border-left: 4px solid #dc3545;
}

.dismiss-btn {
  background: none;
  border: none;
  color: #aaa;
  cursor: pointer;
  padding: 0;
  margin-left: 10px;
}

.dismiss-btn:hover {
  color: #ffffff;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Scrollbar styling */
.timeline-container::-webkit-scrollbar {
  width: 8px;
}

.timeline-container::-webkit-scrollbar-track {
  background: #1a1a1a;
}

.timeline-container::-webkit-scrollbar-thumb {
  background: #444;
  border-radius: 4px;
}

.timeline-container::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style> 