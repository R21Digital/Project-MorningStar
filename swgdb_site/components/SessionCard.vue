<template>
  <div class="session-card" :class="{ 'has-alerts': hasAlerts, 'has-stuck': hasStuckEvents }">
    <!-- Session Header -->
    <div class="session-header">
      <div class="session-id">
        <h3>{{ session.session_id }}</h3>
        <span class="character-name">{{ session.character_name }}</span>
      </div>
      <div class="session-status">
        <span class="status-indicator" :class="statusClass"></span>
        <span class="status-text">{{ statusText }}</span>
      </div>
    </div>

    <!-- Session Metrics -->
    <div class="session-metrics">
      <div class="metric-item">
        <div class="metric-icon">⏱️</div>
        <div class="metric-content">
          <span class="metric-label">Duration</span>
          <span class="metric-value">{{ formatDuration(session.duration_minutes) }}</span>
        </div>
      </div>

      <div class="metric-item">
        <div class="metric-icon">⭐</div>
        <div class="metric-content">
          <span class="metric-label">XP Gained</span>
          <span class="metric-value">{{ formatNumber(session.xp_data.total_xp_gained) }}</span>
        </div>
      </div>

      <div class="metric-item">
        <div class="metric-icon">💰</div>
        <div class="metric-content">
          <span class="metric-label">Credits</span>
          <span class="metric-value">{{ formatNumber(session.credit_data.total_credits_gained) }}</span>
        </div>
      </div>

      <div class="metric-item">
        <div class="metric-icon">📋</div>
        <div class="metric-content">
          <span class="metric-label">Quests</span>
          <span class="metric-value">{{ session.quest_data.total_quests_completed }}</span>
        </div>
      </div>
    </div>

    <!-- Session Details -->
    <div class="session-details">
      <div class="detail-row">
        <span class="detail-label">Start Time:</span>
        <span class="detail-value">{{ formatDateTime(session.start_time) }}</span>
      </div>
      <div class="detail-row">
        <span class="detail-label">End Time:</span>
        <span class="detail-value">{{ formatDateTime(session.end_time) }}</span>
      </div>
      <div class="detail-row">
        <span class="detail-label">Locations:</span>
        <span class="detail-value">{{ session.location_data.total_locations_visited }}</span>
      </div>
      <div class="detail-row">
        <span class="detail-label">Events:</span>
        <span class="detail-value">{{ session.event_data.total_events }}</span>
      </div>
    </div>

    <!-- Alerts and Issues -->
    <div class="session-alerts" v-if="hasAlerts || hasStuckEvents">
      <div class="alert-section" v-if="hasStuckEvents">
        <div class="alert-header">
          <span class="alert-icon">⚠️</span>
          <span class="alert-title">Stuck Events</span>
          <span class="alert-count">{{ session.event_data.stuck_events.length }}</span>
        </div>
        <div class="alert-items">
          <div 
            v-for="event in session.event_data.stuck_events.slice(0, 2)" 
            :key="event.timestamp"
            class="alert-item"
          >
            <span class="alert-location">{{ event.location }}</span>
            <span class="alert-duration">{{ formatDuration(event.duration_seconds / 60) }}</span>
          </div>
          <div v-if="session.event_data.stuck_events.length > 2" class="alert-more">
            +{{ session.event_data.stuck_events.length - 2 }} more
          </div>
        </div>
      </div>

      <div class="alert-section" v-if="hasAlerts">
        <div class="alert-header">
          <span class="alert-icon">📢</span>
          <span class="alert-title">Communication Alerts</span>
          <span class="alert-count">{{ session.event_data.communication_events.length }}</span>
        </div>
        <div class="alert-items">
          <div 
            v-for="event in session.event_data.communication_events.slice(0, 2)" 
            :key="event.timestamp"
            class="alert-item"
            :class="{ 'whisper-alert': event.event_type === 'whisper' }"
          >
            <span class="alert-type">{{ event.event_type }}</span>
            <span class="alert-sender">{{ event.sender }}</span>
            <span class="alert-response" v-if="event.response_sent">✓</span>
          </div>
          <div v-if="session.event_data.communication_events.length > 2" class="alert-more">
            +{{ session.event_data.communication_events.length - 2 }} more
          </div>
        </div>
      </div>

      <div class="alert-section" v-if="hasGuildAlerts">
        <div class="alert-header">
          <span class="alert-icon">⚔️</span>
          <span class="alert-title">Guild Alerts</span>
          <span class="alert-count">{{ session.event_data.guild_alerts.length }}</span>
        </div>
        <div class="alert-items">
          <div 
            v-for="alert in session.event_data.guild_alerts.slice(0, 2)" 
            :key="alert.timestamp"
            class="alert-item"
            :class="alert.priority"
          >
            <span class="alert-type">{{ alert.alert_type }}</span>
            <span class="alert-sender">{{ alert.sender }}</span>
            <span class="alert-priority-badge">{{ alert.priority }}</span>
          </div>
          <div v-if="session.event_data.guild_alerts.length > 2" class="alert-more">
            +{{ session.event_data.guild_alerts.length - 2 }} more
          </div>
        </div>
      </div>
    </div>

    <!-- Top Quests -->
    <div class="session-quests" v-if="session.quest_data.quest_events.length > 0">
      <div class="quests-header">
        <span class="quests-icon">📋</span>
        <span class="quests-title">Recent Quests</span>
        <span class="quests-count">{{ session.quest_data.total_quests_completed }}</span>
      </div>
      <div class="quests-list">
        <div 
          v-for="quest in session.quest_data.quest_events.slice(0, 3)" 
          :key="quest.timestamp"
          class="quest-item"
        >
          <div class="quest-info">
            <span class="quest-name">{{ quest.quest_name }}</span>
            <span class="quest-type" v-if="quest.quest_type">{{ quest.quest_type }}</span>
          </div>
          <div class="quest-details">
            <span class="quest-zone" v-if="quest.zone">{{ quest.zone }}</span>
            <span class="quest-reward" v-if="quest.reward_amount">{{ formatNumber(quest.reward_amount) }}</span>
          </div>
        </div>
        <div v-if="session.quest_data.quest_events.length > 3" class="quests-more">
          +{{ session.quest_data.quest_events.length - 3 }} more quests
        </div>
      </div>
    </div>

    <!-- Top Locations -->
    <div class="session-locations" v-if="session.location_data.location_events.length > 0">
      <div class="locations-header">
        <span class="locations-icon">🗺️</span>
        <span class="locations-title">Locations Visited</span>
      </div>
      <div class="locations-list">
        <div 
          v-for="location in session.location_data.location_events.slice(0, 3)" 
          :key="location.timestamp"
          class="location-item"
        >
          <span class="location-name">{{ location.city }}, {{ location.planet }}</span>
          <span class="location-duration" v-if="location.duration_minutes">
            {{ formatDuration(location.duration_minutes) }}
          </span>
        </div>
        <div v-if="session.location_data.location_events.length > 3" class="locations-more">
          +{{ session.location_data.location_events.length - 3 }} more locations
        </div>
      </div>
    </div>

    <!-- Performance Indicators -->
    <div class="session-performance">
      <div class="performance-indicators">
        <div class="indicator" :class="{ 'good': xpPerHour > 1000, 'warning': xpPerHour <= 1000 }">
          <span class="indicator-label">XP/Hour</span>
          <span class="indicator-value">{{ Math.round(xpPerHour) }}</span>
        </div>
        <div class="indicator" :class="{ 'good': creditsPerHour > 5000, 'warning': creditsPerHour <= 5000 }">
          <span class="indicator-label">Credits/Hour</span>
          <span class="indicator-value">{{ Math.round(creditsPerHour) }}</span>
        </div>
        <div class="indicator" :class="{ 'good': questsPerHour > 2, 'warning': questsPerHour <= 2 }">
          <span class="indicator-label">Quests/Hour</span>
          <span class="indicator-value">{{ questsPerHour.toFixed(1) }}</span>
        </div>
      </div>
    </div>

    <!-- Session Actions -->
    <div class="session-actions">
      <button class="btn btn-primary btn-sm" @click="$emit('view', session)">
        <span class="btn-icon">👁️</span>
        View Details
      </button>
      <button class="btn btn-secondary btn-sm" @click="$emit('download', session)">
        <span class="btn-icon">📥</span>
        Download
      </button>
      <button class="btn btn-outline btn-sm" @click="exportPDF">
        <span class="btn-icon">📄</span>
        PDF
      </button>
    </div>

    <!-- Session Tags -->
    <div class="session-tags">
      <span class="tag tag-character">{{ session.character_name }}</span>
      <span class="tag tag-duration">{{ formatDuration(session.duration_minutes) }}</span>
      <span v-if="hasStuckEvents" class="tag tag-warning">Stuck Events</span>
      <span v-if="hasAlerts" class="tag tag-alert">Alerts</span>
      <span v-if="session.quest_data.total_quests_completed > 5" class="tag tag-success">High Activity</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SessionCard',
  props: {
    session: {
      type: Object,
      required: true
    }
  },
  computed: {
    hasStuckEvents() {
      return this.session.event_data.stuck_events.length > 0;
    },
    hasAlerts() {
      return this.session.event_data.communication_events.length > 0;
    },
    hasGuildAlerts() {
      return this.session.event_data.guild_alerts && this.session.event_data.guild_alerts.length > 0;
    },
    statusClass() {
      if (this.hasStuckEvents) return 'status-warning';
      if (this.hasAlerts) return 'status-info';
      return 'status-success';
    },
    statusText() {
      if (this.hasStuckEvents) return 'Issues Detected';
      if (this.hasAlerts) return 'Alerts';
      return 'Normal';
    },
    xpPerHour() {
      const hours = this.session.duration_minutes / 60;
      return hours > 0 ? this.session.xp_data.total_xp_gained / hours : 0;
    },
    creditsPerHour() {
      const hours = this.session.duration_minutes / 60;
      return hours > 0 ? this.session.credit_data.total_credits_gained / hours : 0;
    },
    questsPerHour() {
      const hours = this.session.duration_minutes / 60;
      return hours > 0 ? this.session.quest_data.total_quests_completed / hours : 0;
    }
  },
  methods: {
    formatNumber(num) {
      return new Intl.NumberFormat().format(num);
    },
    formatDuration(minutes) {
      const hours = Math.floor(minutes / 60);
      const mins = Math.round(minutes % 60);
      if (hours > 0) {
        return `${hours}h ${mins}m`;
      }
      return `${mins}m`;
    },
    formatDateTime(dateString) {
      return new Date(dateString).toLocaleString();
    },
    async exportPDF() {
      const { jsPDF } = window.jspdf;
      const doc = new jsPDF();
      
      // Add session title
      doc.setFontSize(18);
      doc.text(`Session Report: ${this.session.session_id}`, 20, 20);
      
      // Add basic info
      doc.setFontSize(12);
      doc.text(`Character: ${this.session.character_name}`, 20, 40);
      doc.text(`Duration: ${this.formatDuration(this.session.duration_minutes)}`, 20, 50);
      doc.text(`XP Gained: ${this.formatNumber(this.session.xp_data.total_xp_gained)}`, 20, 60);
      doc.text(`Credits Gained: ${this.formatNumber(this.session.credit_data.total_credits_gained)}`, 20, 70);
      doc.text(`Quests Completed: ${this.session.quest_data.total_quests_completed}`, 20, 80);
      
      // Add quests table
      if (this.session.quest_data.quest_events.length > 0) {
        doc.text('Quests Completed:', 20, 100);
        const questData = this.session.quest_data.quest_events.map(q => [
          q.quest_name,
          this.formatDateTime(q.timestamp),
          q.zone || 'N/A'
        ]);
        doc.autoTable({
          startY: 105,
          head: [['Quest', 'Time', 'Zone']],
          body: questData
        });
      }
      
      doc.save(`${this.session.session_id}_card.pdf`);
    }
  }
};
</script>

<style scoped>
.session-card {
  background: #ffffff;
  border: 1px solid #e1e5e9;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.session-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.session-card.has-alerts {
  border-left: 4px solid #ff9800;
}

.session-card.has-stuck {
  border-left: 4px solid #f44336;
}

.session-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.session-id h3 {
  margin: 0 0 5px 0;
  font-size: 18px;
  font-weight: 600;
  color: #2c3e50;
}

.character-name {
  font-size: 14px;
  color: #7f8c8d;
  font-weight: 500;
}

.session-status {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-success {
  background-color: #4caf50;
}

.status-warning {
  background-color: #ff9800;
}

.status-info {
  background-color: #2196f3;
}

.status-text {
  font-size: 12px;
  font-weight: 500;
  color: #7f8c8d;
}

.session-metrics {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  margin-bottom: 20px;
}

.metric-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.metric-icon {
  font-size: 20px;
  width: 30px;
  text-align: center;
}

.metric-content {
  display: flex;
  flex-direction: column;
}

.metric-label {
  font-size: 12px;
  color: #7f8c8d;
  font-weight: 500;
}

.metric-value {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
}

.session-details {
  margin-bottom: 20px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.detail-label {
  font-size: 12px;
  color: #7f8c8d;
}

.detail-value {
  font-size: 12px;
  color: #2c3e50;
  font-weight: 500;
}

.session-alerts {
  margin-bottom: 20px;
}

.alert-section {
  margin-bottom: 15px;
}

.alert-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.alert-icon {
  font-size: 16px;
}

.alert-title {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}

.alert-count {
  background: #e74c3c;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.alert-items {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.alert-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 10px;
  background: #fff3cd;
  border-radius: 4px;
  font-size: 12px;
}

.alert-location,
.alert-type {
  color: #856404;
  font-weight: 500;
}

.alert-duration,
.alert-sender {
  color: #856404;
  font-size: 11px;
}

.alert-response {
  color: #27ae60;
  font-weight: 600;
  font-size: 12px;
}

.alert-priority-badge {
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 9px;
  font-weight: 600;
  text-transform: uppercase;
}

.alert-priority-badge.high {
  background: #e74c3c;
  color: white;
}

.alert-priority-badge.medium {
  background: #f39c12;
  color: white;
}

.alert-priority-badge.low {
  background: #95a5a6;
  color: white;
}

.alert-item.whisper-alert {
  border-left: 3px solid #e74c3c;
  background: #fff5f5;
}

.alert-item.high {
  border-left: 3px solid #e74c3c;
  background: #fff5f5;
}

.alert-item.medium {
  border-left: 3px solid #f39c12;
  background: #fffbf0;
}

.alert-item.low {
  border-left: 3px solid #95a5a6;
  background: #f8f9fa;
}

.alert-more {
  font-size: 11px;
  color: #856404;
  font-style: italic;
  text-align: center;
  padding: 5px;
}

.session-quests,
.session-locations {
  margin-bottom: 20px;
}

.quests-header,
.locations-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.quests-icon,
.locations-icon {
  font-size: 16px;
}

.quests-title,
.locations-title {
  font-size: 14px;
  font-weight: 600;
  color: #2c3e50;
}

.quests-count {
  background: #3498db;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.quests-list,
.locations-list {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.quest-item,
.location-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 5px 10px;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 12px;
}

.quest-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.quest-name {
  color: #2c3e50;
  font-weight: 500;
  font-size: 12px;
}

.quest-type {
  color: #3498db;
  font-size: 10px;
  font-weight: 500;
  text-transform: capitalize;
}

.quest-details {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.quest-zone {
  color: #7f8c8d;
  font-size: 10px;
}

.quest-reward {
  color: #27ae60;
  font-size: 10px;
  font-weight: 600;
}

.location-name {
  color: #2c3e50;
  font-weight: 500;
}

.location-duration {
  color: #7f8c8d;
  font-size: 11px;
}

.quests-more,
.locations-more {
  font-size: 11px;
  color: #7f8c8d;
  font-style: italic;
  text-align: center;
  padding: 5px;
}

.session-performance {
  margin-bottom: 20px;
}

.performance-indicators {
  display: flex;
  gap: 15px;
}

.indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px;
  border-radius: 6px;
  min-width: 60px;
}

.indicator.good {
  background: #d4edda;
  color: #155724;
}

.indicator.warning {
  background: #fff3cd;
  color: #856404;
}

.indicator-label {
  font-size: 10px;
  font-weight: 500;
  margin-bottom: 2px;
}

.indicator-value {
  font-size: 14px;
  font-weight: 600;
}

.session-actions {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-primary:hover {
  background: #0056b3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #545b62;
}

.btn-outline {
  background: transparent;
  color: #007bff;
  border: 1px solid #007bff;
}

.btn-outline:hover {
  background: #007bff;
  color: white;
}

.btn-sm {
  padding: 6px 10px;
  font-size: 11px;
}

.btn-icon {
  font-size: 12px;
}

.session-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.tag {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 500;
}

.tag-character {
  background: #e3f2fd;
  color: #1976d2;
}

.tag-duration {
  background: #f3e5f5;
  color: #7b1fa2;
}

.tag-warning {
  background: #fff3cd;
  color: #856404;
}

.tag-alert {
  background: #f8d7da;
  color: #721c24;
}

.tag-success {
  background: #d4edda;
  color: #155724;
}

@media (max-width: 768px) {
  .session-metrics {
    grid-template-columns: 1fr;
  }
  
  .performance-indicators {
    flex-direction: column;
    gap: 10px;
  }
  
  .session-actions {
    flex-direction: column;
  }
  
  .session-tags {
    justify-content: center;
  }
}
</style> 