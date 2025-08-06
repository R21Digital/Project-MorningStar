<template>
  <div class="performance-dashboard">
    <!-- Header -->
    <div class="header">
      <h2>Performance Dashboard</h2>
      <div class="header-controls">
        <button @click="refreshData" :disabled="loading">
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
          Refresh
        </button>
        <button @click="toggleMonitoring" :class="{ active: monitoringActive }">
          <i class="fas fa-play" v-if="!monitoringActive"></i>
          <i class="fas fa-pause" v-else></i>
          {{ monitoringActive ? 'Stop' : 'Start' }} Monitoring
        </button>
        <button @click="exportProfile" :disabled="!hasData">
          <i class="fas fa-download"></i>
          Export Profile
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
      <p>Loading performance data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error">
      <i class="fas fa-exclamation-triangle"></i>
      <p>{{ error }}</p>
      <button @click="refreshData">Try Again</button>
    </div>

    <!-- Main Content -->
    <div v-else class="content">
      <!-- System Metrics Overview -->
      <div class="metrics-overview">
        <div class="metric-card" :class="getCpuClass()">
          <div class="metric-icon">
            <i class="fas fa-microchip"></i>
          </div>
          <div class="metric-content">
            <h3>{{ systemMetrics.cpu_percent?.toFixed(1) || '0.0' }}%</h3>
            <p>CPU Usage</p>
          </div>
        </div>

        <div class="metric-card" :class="getMemoryClass()">
          <div class="metric-icon">
            <i class="fas fa-memory"></i>
          </div>
          <div class="metric-content">
            <h3>{{ systemMetrics.memory_percent?.toFixed(1) || '0.0' }}%</h3>
            <p>Memory Usage</p>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon">
            <i class="fas fa-eye"></i>
          </div>
          <div class="metric-content">
            <h3>{{ performanceMetrics.ocr_calls_per_minute || 0 }}</h3>
            <p>OCR Calls/min</p>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon">
            <i class="fas fa-film"></i>
          </div>
          <div class="metric-content">
            <h3>{{ performanceMetrics.frames_analyzed_per_minute || 0 }}</h3>
            <p>Frames/min</p>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon">
            <i class="fas fa-hdd"></i>
          </div>
          <div class="metric-content">
            <h3>{{ systemMetrics.io_wait_percent?.toFixed(1) || '0.0' }}%</h3>
            <p>IO Wait</p>
          </div>
        </div>

        <div class="metric-card">
          <div class="metric-icon">
            <i class="fas fa-network-wired"></i>
          </div>
          <div class="metric-content">
            <h3>{{ formatBytes(systemMetrics.network_io_bytes || 0) }}</h3>
            <p>Network IO</p>
          </div>
        </div>
      </div>

      <!-- Module Performance -->
      <div class="module-performance">
        <h3>Module Performance</h3>
        <div class="module-grid">
          <div 
            v-for="(module, name) in modulePerformance" 
            :key="name"
            class="module-card"
            :class="getModuleClass(module.load_level)"
          >
            <div class="module-header">
              <h4>{{ formatModuleName(name) }}</h4>
              <span class="load-badge" :class="module.load_level">
                {{ module.load_level.toUpperCase() }}
              </span>
            </div>
            <div class="module-metrics">
              <div class="metric">
                <span class="label">CPU:</span>
                <span class="value">{{ module.cpu_usage?.toFixed(1) || '0.0' }}%</span>
              </div>
              <div class="metric">
                <span class="label">Memory:</span>
                <span class="value">{{ module.memory_usage?.toFixed(1) || '0.0' }}MB</span>
              </div>
              <div class="metric">
                <span class="label">Calls:</span>
                <span class="value">{{ module.call_count || 0 }}</span>
              </div>
            </div>
            <div v-if="module.recommendations && module.recommendations.length > 0" class="recommendations">
              <div class="recommendation" v-for="rec in module.recommendations.slice(0, 2)" :key="rec">
                <i class="fas fa-lightbulb"></i>
                {{ rec }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Performance Recommendations -->
      <div class="recommendations-section">
        <h3>Performance Recommendations</h3>
        <div class="recommendations-list">
          <div 
            v-for="(rec, index) in recommendations" 
            :key="index"
            class="recommendation-card"
            :class="getRecommendationClass(rec.priority)"
          >
            <div class="recommendation-header">
              <div class="priority-badge" :class="rec.priority">
                {{ rec.priority.toUpperCase() }}
              </div>
              <h4>{{ rec.category }}</h4>
            </div>
            <div class="recommendation-content">
              <p class="description">{{ rec.description }}</p>
              <div class="details">
                <div class="detail">
                  <strong>Impact:</strong> {{ rec.impact }}
                </div>
                <div class="detail">
                  <strong>Action:</strong> {{ rec.action }}
                </div>
                <div class="detail">
                  <strong>Estimated Savings:</strong> {{ rec.estimated_savings }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Detailed Information -->
      <div v-if="showDetails" class="details-section">
        <!-- System Metrics Chart -->
        <div class="chart-section">
          <h3>System Metrics History</h3>
          <div class="chart-container">
            <canvas ref="systemMetricsChart"></canvas>
          </div>
        </div>

        <!-- Performance Statistics -->
        <div class="statistics-section">
          <h3>Performance Statistics</h3>
          <div class="stats-grid">
            <div class="stat-item">
              <label>Active Modules:</label>
              <span>{{ performanceMetrics.active_modules || 0 }}</span>
            </div>
            <div class="stat-item">
              <label>Heavy Modules:</label>
              <span class="heavy">{{ performanceMetrics.heavy_modules || 0 }}</span>
            </div>
            <div class="stat-item">
              <label>Medium Modules:</label>
              <span class="medium">{{ performanceMetrics.medium_modules || 0 }}</span>
            </div>
            <div class="stat-item">
              <label>Light Modules:</label>
              <span class="light">{{ performanceMetrics.light_modules || 0 }}</span>
            </div>
            <div class="stat-item">
              <label>Available Memory:</label>
              <span>{{ systemMetrics.memory_available_gb?.toFixed(1) || '0.0' }}GB</span>
            </div>
            <div class="stat-item">
              <label>Disk Usage:</label>
              <span>{{ systemMetrics.disk_usage_percent?.toFixed(1) || '0.0' }}%</span>
            </div>
          </div>
        </div>

        <!-- Monitoring Status -->
        <div class="status-section">
          <h3>Monitoring Status</h3>
          <div class="status-grid">
            <div class="status-item">
              <label>Monitoring Active:</label>
              <span :class="{ active: monitoringActive, inactive: !monitoringActive }">
                {{ monitoringActive ? 'Yes' : 'No' }}
              </span>
            </div>
            <div class="status-item">
              <label>Last Update:</label>
              <span>{{ formatTime(lastUpdate) }}</span>
            </div>
            <div class="status-item">
              <label>Data Points:</label>
              <span>{{ systemMetricsHistory.length }}</span>
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
import Chart from 'chart.js/auto';

export default {
  name: 'PerformanceDashboard',
  data() {
    return {
      loading: false,
      error: null,
      showDetails: false,
      monitoringActive: false,
      hasData: false,
      dashboardData: null,
      systemMetrics: {},
      performanceMetrics: {},
      modulePerformance: {},
      recommendations: [],
      systemMetricsHistory: [],
      lastUpdate: null,
      alertMessage: null,
      alertType: 'info',
      autoRefreshInterval: null,
      systemMetricsChart: null
    }
  },
  computed: {
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
    this.loadDashboardData()
    this.startAutoRefresh()
  },
  beforeDestroy() {
    this.stopAutoRefresh()
    if (this.systemMetricsChart) {
      this.systemMetricsChart.destroy()
    }
  },
  methods: {
    async loadDashboardData() {
      this.loading = true
      this.error = null
      
      try {
        // Simulate API call - replace with actual endpoint
        const response = await fetch('/api/performance/dashboard')
        if (!response.ok) {
          throw new Error('Failed to load performance dashboard data')
        }
        
        const data = await response.json()
        this.dashboardData = data
        this.systemMetrics = data.system_metrics || {}
        this.performanceMetrics = data.performance_metrics || {}
        this.modulePerformance = data.module_performance || {}
        this.recommendations = data.recommendations || []
        this.monitoringActive = data.monitoring_active || false
        this.lastUpdate = data.last_update ? new Date(data.last_update) : null
        this.hasData = true
        
        this.checkForAlerts()
        this.$nextTick(() => {
          this.updateChart()
        })
      } catch (error) {
        this.error = error.message
        console.error('Failed to load dashboard data:', error)
      } finally {
        this.loading = false
      }
    },
    refreshData() {
      this.loadDashboardData()
    },
    toggleMonitoring() {
      this.monitoringActive = !this.monitoringActive
      // In a real implementation, this would call the API to start/stop monitoring
      this.showAlert(
        `Performance monitoring ${this.monitoringActive ? 'started' : 'stopped'}`,
        this.monitoringActive ? 'success' : 'info'
      )
    },
    toggleDetails() {
      this.showDetails = !this.showDetails
    },
    startAutoRefresh() {
      this.autoRefreshInterval = setInterval(() => {
        this.loadDashboardData()
      }, 10000) // Refresh every 10 seconds
    },
    stopAutoRefresh() {
      if (this.autoRefreshInterval) {
        clearInterval(this.autoRefreshInterval)
        this.autoRefreshInterval = null
      }
    },
    updateChart() {
      if (!this.showDetails || !this.$refs.systemMetricsChart) {
        return
      }
      
      if (this.systemMetricsChart) {
        this.systemMetricsChart.destroy()
      }
      
      const ctx = this.$refs.systemMetricsChart
      this.systemMetricsChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels: this.systemMetricsHistory.map((_, index) => `T${index}`),
          datasets: [
            {
              label: 'CPU %',
              data: this.systemMetricsHistory.map(m => m.cpu_percent),
              borderColor: '#ff6b6b',
              backgroundColor: 'rgba(255, 107, 107, 0.1)',
              tension: 0.4
            },
            {
              label: 'Memory %',
              data: this.systemMetricsHistory.map(m => m.memory_percent),
              borderColor: '#4ecdc4',
              backgroundColor: 'rgba(78, 205, 196, 0.1)',
              tension: 0.4
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              max: 100
            }
          }
        }
      })
    },
    getCpuClass() {
      const cpu = this.systemMetrics.cpu_percent || 0
      if (cpu > 80) return 'critical'
      if (cpu > 60) return 'warning'
      return 'normal'
    },
    getMemoryClass() {
      const memory = this.systemMetrics.memory_percent || 0
      if (memory > 85) return 'critical'
      if (memory > 70) return 'warning'
      return 'normal'
    },
    getModuleClass(loadLevel) {
      return `module-${loadLevel}`
    },
    getRecommendationClass(priority) {
      return `recommendation-${priority}`
    },
    formatModuleName(name) {
      return name.replace(/\./g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    },
    formatBytes(bytes) {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    },
    formatTime(timestamp) {
      if (!timestamp) return 'Never'
      const date = new Date(timestamp)
      return date.toLocaleTimeString()
    },
    async exportProfile() {
      try {
        const response = await fetch('/api/performance/export', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            session_id: 'current_session'
          })
        })
        
        if (response.ok) {
          const blob = await response.blob()
          const url = window.URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = `performance_profile_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`
          document.body.appendChild(a)
          a.click()
          window.URL.revokeObjectURL(url)
          document.body.removeChild(a)
          
          this.showAlert('Performance profile exported successfully', 'success')
        } else {
          throw new Error('Failed to export profile')
        }
      } catch (error) {
        this.showAlert('Failed to export profile: ' + error.message, 'error')
      }
    },
    checkForAlerts() {
      if (!this.systemMetrics) return
      
      const cpu = this.systemMetrics.cpu_percent || 0
      const memory = this.systemMetrics.memory_percent || 0
      const heavyModules = this.performanceMetrics.heavy_modules || 0
      
      if (cpu > 90) {
        this.showAlert('Critical CPU usage detected!', 'error')
      } else if (cpu > 80) {
        this.showAlert('High CPU usage detected', 'warning')
      } else if (memory > 95) {
        this.showAlert('Critical memory usage detected!', 'error')
      } else if (memory > 85) {
        this.showAlert('High memory usage detected', 'warning')
      } else if (heavyModules > 3) {
        this.showAlert('Multiple heavy modules active', 'warning')
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
.performance-dashboard {
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
  display: flex;
  align-items: center;
  gap: 5px;
}

.header-controls button:hover {
  background: #3a3a3a;
  border-color: #555;
}

.header-controls button.active {
  background: #28a745;
  border-color: #28a745;
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

.metrics-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
}

.metric-card {
  background: #2a2a2a;
  border: 1px solid #444;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
  transition: all 0.2s ease;
}

.metric-card.normal {
  border-color: #28a745;
}

.metric-card.warning {
  border-color: #ffc107;
}

.metric-card.critical {
  border-color: #dc3545;
}

.metric-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #007bff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
}

.metric-content h3 {
  margin: 0 0 5px 0;
  font-size: 1.5rem;
  font-weight: 700;
  color: #ffffff;
}

.metric-content p {
  margin: 0;
  color: #cccccc;
  font-size: 0.9rem;
}

.module-performance {
  margin-bottom: 30px;
}

.module-performance h3 {
  margin: 0 0 20px 0;
  color: #ffffff;
  font-size: 1.2rem;
  font-weight: 600;
}

.module-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
}

.module-card {
  background: #2a2a2a;
  border: 1px solid #444;
  border-radius: 8px;
  padding: 15px;
  transition: all 0.2s ease;
}

.module-card.module-green {
  border-left: 4px solid #28a745;
}

.module-card.module-yellow {
  border-left: 4px solid #ffc107;
}

.module-card.module-red {
  border-left: 4px solid #dc3545;
}

.module-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.module-header h4 {
  margin: 0;
  color: #ffffff;
  font-size: 1rem;
  font-weight: 600;
}

.load-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
}

.load-badge.green {
  background: #28a745;
  color: white;
}

.load-badge.yellow {
  background: #ffc107;
  color: #212529;
}

.load-badge.red {
  background: #dc3545;
  color: white;
}

.module-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-bottom: 10px;
}

.metric {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
}

.metric .label {
  color: #cccccc;
}

.metric .value {
  color: #007bff;
  font-weight: 600;
}

.recommendations {
  border-top: 1px solid #444;
  padding-top: 10px;
}

.recommendation {
  font-size: 0.8rem;
  color: #ffc107;
  margin-bottom: 5px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.recommendation:last-child {
  margin-bottom: 0;
}

.recommendations-section {
  margin-bottom: 30px;
}

.recommendations-section h3 {
  margin: 0 0 20px 0;
  color: #ffffff;
  font-size: 1.2rem;
  font-weight: 600;
}

.recommendations-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 15px;
}

.recommendation-card {
  background: #2a2a2a;
  border: 1px solid #444;
  border-radius: 8px;
  padding: 15px;
  transition: all 0.2s ease;
}

.recommendation-card.recommendation-high {
  border-left: 4px solid #dc3545;
}

.recommendation-card.recommendation-medium {
  border-left: 4px solid #ffc107;
}

.recommendation-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.priority-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
}

.priority-badge.high {
  background: #dc3545;
  color: white;
}

.priority-badge.medium {
  background: #ffc107;
  color: #212529;
}

.recommendation-header h4 {
  margin: 0;
  color: #ffffff;
  font-size: 1rem;
  font-weight: 600;
}

.recommendation-content .description {
  color: #ffffff;
  margin: 0 0 10px 0;
  font-size: 0.9rem;
}

.details {
  font-size: 0.8rem;
}

.detail {
  margin-bottom: 5px;
  color: #cccccc;
}

.detail strong {
  color: #007bff;
}

.details-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #333;
}

.chart-section, .statistics-section, .status-section {
  margin-bottom: 30px;
}

.chart-section h3, .statistics-section h3, .status-section h3 {
  margin: 0 0 15px 0;
  color: #ffffff;
  font-size: 1.1rem;
  font-weight: 600;
}

.chart-container {
  height: 300px;
  background: #2a2a2a;
  border-radius: 8px;
  padding: 15px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background: #2a2a2a;
  border-radius: 4px;
  border: 1px solid #444;
}

.stat-item label {
  color: #cccccc;
  font-size: 0.9rem;
}

.stat-item span {
  color: #007bff;
  font-weight: 600;
}

.stat-item span.heavy {
  color: #dc3545;
}

.stat-item span.medium {
  color: #ffc107;
}

.stat-item span.light {
  color: #28a745;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background: #2a2a2a;
  border-radius: 4px;
  border: 1px solid #444;
}

.status-item label {
  color: #cccccc;
  font-size: 0.9rem;
}

.status-item span {
  color: #007bff;
  font-weight: 600;
}

.status-item span.active {
  color: #28a745;
}

.status-item span.inactive {
  color: #dc3545;
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
  
  .header-controls {
    flex-wrap: wrap;
  }
  
  .metrics-overview {
    grid-template-columns: 1fr;
  }
  
  .module-grid {
    grid-template-columns: 1fr;
  }
  
  .recommendations-list {
    grid-template-columns: 1fr;
  }
  
  .stats-grid, .status-grid {
    grid-template-columns: 1fr;
  }
}
</style> 