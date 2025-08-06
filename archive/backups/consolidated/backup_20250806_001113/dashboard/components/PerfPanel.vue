<template>
  <div class="perf-panel">
    <!-- Panel Header -->
    <div class="panel-header">
      <h3>Performance Monitor</h3>
      <div class="header-controls">
        <button @click="refreshData" :disabled="loading" class="refresh-btn">
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
        </button>
        <button @click="toggleMonitoring" :class="{ active: monitoringActive }" class="monitor-btn">
          <i class="fas" :class="monitoringActive ? 'fa-pause' : 'fa-play'"></i>
        </button>
        <button @click="exportProfile" :disabled="!hasData" class="export-btn">
          <i class="fas fa-download"></i>
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading performance data...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <i class="fas fa-exclamation-triangle"></i>
      <p>{{ error }}</p>
      <button @click="refreshData" class="retry-btn">Retry</button>
    </div>

    <!-- Main Content -->
    <div v-else class="panel-content">
      <!-- Real-time Metrics -->
      <div class="metrics-section">
        <h4>Real-time Metrics</h4>
        <div class="metrics-grid">
          <div class="metric-item" :class="getCpuClass()">
            <div class="metric-icon">
              <i class="fas fa-microchip"></i>
            </div>
            <div class="metric-content">
              <div class="metric-value">{{ systemMetrics.cpu_percent?.toFixed(1) || '0.0' }}%</div>
              <div class="metric-label">CPU</div>
            </div>
          </div>

          <div class="metric-item" :class="getMemoryClass()">
            <div class="metric-icon">
              <i class="fas fa-memory"></i>
            </div>
            <div class="metric-content">
              <div class="metric-value">{{ systemMetrics.memory_percent?.toFixed(1) || '0.0' }}%</div>
              <div class="metric-label">RAM</div>
            </div>
          </div>

          <div class="metric-item">
            <div class="metric-icon">
              <i class="fas fa-eye"></i>
            </div>
            <div class="metric-content">
              <div class="metric-value">{{ performanceMetrics.ocr_calls_per_minute || 0 }}</div>
              <div class="metric-label">OCR/min</div>
            </div>
          </div>

          <div class="metric-item">
            <div class="metric-icon">
              <i class="fas fa-film"></i>
            </div>
            <div class="metric-content">
              <div class="metric-value">{{ performanceMetrics.frames_analyzed_per_minute || 0 }}</div>
              <div class="metric-label">Frames/min</div>
            </div>
          </div>

          <div class="metric-item">
            <div class="metric-icon">
              <i class="fas fa-hdd"></i>
            </div>
            <div class="metric-content">
              <div class="metric-value">{{ systemMetrics.io_wait_percent?.toFixed(1) || '0.0' }}%</div>
              <div class="metric-label">IO Wait</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Load Level Indicators -->
      <div class="load-levels-section">
        <h4>Module Load Levels</h4>
        <div class="load-indicators">
          <div class="load-indicator green">
            <div class="indicator-dot"></div>
            <span class="indicator-label">Green</span>
            <span class="indicator-count">{{ loadLevels.green || 0 }}</span>
          </div>
          <div class="load-indicator yellow">
            <div class="indicator-dot"></div>
            <span class="indicator-label">Yellow</span>
            <span class="indicator-count">{{ loadLevels.yellow || 0 }}</span>
          </div>
          <div class="load-indicator red">
            <div class="indicator-dot"></div>
            <span class="indicator-label">Red</span>
            <span class="indicator-count">{{ loadLevels.red || 0 }}</span>
          </div>
        </div>
      </div>

      <!-- Heavy Modules Alert -->
      <div v-if="heavyModules.length > 0" class="heavy-modules-alert">
        <div class="alert-header">
          <i class="fas fa-exclamation-triangle"></i>
          <h4>Heavy Modules Detected</h4>
        </div>
        <div class="heavy-modules-list">
          <div 
            v-for="module in heavyModules" 
            :key="module.name"
            class="heavy-module-item"
          >
            <span class="module-name">{{ formatModuleName(module.name) }}</span>
            <span class="module-impact">{{ module.cpu_usage?.toFixed(1) || '0.0' }}% CPU</span>
          </div>
        </div>
      </div>

      <!-- Performance Recommendations -->
      <div class="recommendations-section">
        <h4>Optimization Recommendations</h4>
        <div class="recommendations-list">
          <div 
            v-for="(rec, index) in recommendations" 
            :key="index"
            class="recommendation-item"
            :class="getRecommendationPriority(rec.priority)"
          >
            <div class="recommendation-icon">
              <i class="fas fa-lightbulb"></i>
            </div>
            <div class="recommendation-content">
              <div class="recommendation-title">{{ rec.category }}</div>
              <div class="recommendation-description">{{ rec.description }}</div>
              <div class="recommendation-impact">
                <strong>Impact:</strong> {{ rec.impact }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Quick Actions -->
      <div class="quick-actions-section">
        <h4>Quick Actions</h4>
        <div class="actions-grid">
          <button @click="reduceOcrFrequency" class="action-btn">
            <i class="fas fa-eye-slash"></i>
            Lower OCR Cadence
          </button>
          <button @click="disableVerboseCapture" class="action-btn">
            <i class="fas fa-camera-slash"></i>
            Disable Verbose Capture
          </button>
          <button @click="reduceHeatmaps" class="action-btn">
            <i class="fas fa-fire-extinguisher"></i>
            Reduce Heatmaps
          </button>
          <button @click="optimizeMemory" class="action-btn">
            <i class="fas fa-memory"></i>
            Optimize Memory
          </button>
        </div>
      </div>

      <!-- Performance Summary -->
      <div class="summary-section">
        <h4>Performance Summary</h4>
        <div class="summary-content">
          <div class="summary-item">
            <span class="summary-label">Overall Status:</span>
            <span class="summary-value" :class="getOverallStatusClass()">
              {{ overallStatus }}
            </span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Active Modules:</span>
            <span class="summary-value">{{ performanceMetrics.active_modules || 0 }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Sampling Duration:</span>
            <span class="summary-value">{{ formatDuration(samplingDuration) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PerfPanel',
  data() {
    return {
      loading: false,
      error: null,
      monitoringActive: false,
      hasData: false,
      systemMetrics: {},
      performanceMetrics: {},
      loadLevels: { green: 0, yellow: 0, red: 0 },
      heavyModules: [],
      recommendations: [],
      overallStatus: 'Unknown',
      samplingDuration: 0,
      refreshInterval: null
    }
  },
  mounted() {
    this.loadData()
    this.startAutoRefresh()
  },
  beforeDestroy() {
    this.stopAutoRefresh()
  },
  methods: {
    async loadData() {
      this.loading = true
      this.error = null
      
      try {
        const response = await fetch('/api/performance/dashboard')
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }
        
        const data = await response.json()
        this.updateData(data)
        this.hasData = true
      } catch (err) {
        this.error = `Failed to load performance data: ${err.message}`
        console.error('Performance data load error:', err)
      } finally {
        this.loading = false
      }
    },
    
    updateData(data) {
      this.systemMetrics = data.system_metrics || {}
      this.performanceMetrics = data.performance_metrics || {}
      this.loadLevels = data.load_levels || { green: 0, yellow: 0, red: 0 }
      this.heavyModules = data.heavy_modules || []
      this.recommendations = data.recommendations || []
      this.overallStatus = data.overall_status || 'Unknown'
      this.samplingDuration = data.sampling_duration || 0
      this.monitoringActive = data.monitoring_active || false
    },
    
    async refreshData() {
      await this.loadData()
    },
    
    async toggleMonitoring() {
      try {
        const action = this.monitoringActive ? 'stop' : 'start'
        const response = await fetch(`/api/performance/monitoring/${action}`, {
          method: 'POST'
        })
        
        if (response.ok) {
          this.monitoringActive = !this.monitoringActive
          await this.loadData()
        }
      } catch (err) {
        console.error('Failed to toggle monitoring:', err)
      }
    },
    
    async exportProfile() {
      try {
        const response = await fetch('/api/performance/export', {
          method: 'POST'
        })
        
        if (response.ok) {
          const blob = await response.blob()
          const url = window.URL.createObjectURL(blob)
          const a = document.createElement('a')
          a.href = url
          a.download = `performance_profile_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.json`
          document.body.appendChild(a)
          a.click()
          document.body.removeChild(a)
          window.URL.revokeObjectURL(url)
        }
      } catch (err) {
        console.error('Failed to export profile:', err)
      }
    },
    
    startAutoRefresh() {
      this.refreshInterval = setInterval(() => {
        if (this.monitoringActive && !this.loading) {
          this.loadData()
        }
      }, 5000) // Refresh every 5 seconds when monitoring
    },
    
    stopAutoRefresh() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval)
        this.refreshInterval = null
      }
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
    
    getOverallStatusClass() {
      switch (this.overallStatus.toLowerCase()) {
        case 'critical': return 'critical'
        case 'warning': return 'warning'
        case 'normal': return 'normal'
        default: return 'unknown'
      }
    },
    
    getRecommendationPriority(priority) {
      switch (priority.toLowerCase()) {
        case 'high': return 'high-priority'
        case 'medium': return 'medium-priority'
        case 'low': return 'low-priority'
        default: return 'normal-priority'
      }
    },
    
    formatModuleName(name) {
      return name.replace(/\./g, ' ').replace(/\b\w/g, l => l.toUpperCase())
    },
    
    formatDuration(seconds) {
      if (!seconds) return '0s'
      const hours = Math.floor(seconds / 3600)
      const minutes = Math.floor((seconds % 3600) / 60)
      const secs = Math.floor(seconds % 60)
      
      if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`
      } else if (minutes > 0) {
        return `${minutes}m ${secs}s`
      } else {
        return `${secs}s`
      }
    },
    
    async reduceOcrFrequency() {
      try {
        await fetch('/api/performance/optimize/ocr-frequency', { method: 'POST' })
        await this.loadData()
      } catch (err) {
        console.error('Failed to reduce OCR frequency:', err)
      }
    },
    
    async disableVerboseCapture() {
      try {
        await fetch('/api/performance/optimize/disable-verbose', { method: 'POST' })
        await this.loadData()
      } catch (err) {
        console.error('Failed to disable verbose capture:', err)
      }
    },
    
    async reduceHeatmaps() {
      try {
        await fetch('/api/performance/optimize/reduce-heatmaps', { method: 'POST' })
        await this.loadData()
      } catch (err) {
        console.error('Failed to reduce heatmaps:', err)
      }
    },
    
    async optimizeMemory() {
      try {
        await fetch('/api/performance/optimize/memory', { method: 'POST' })
        await this.loadData()
      } catch (err) {
        console.error('Failed to optimize memory:', err)
      }
    }
  }
}
</script>

<style scoped>
.perf-panel {
  background: #1a1a1a;
  border-radius: 8px;
  padding: 16px;
  color: #ffffff;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #333;
}

.panel-header h3 {
  margin: 0;
  color: #00d4ff;
  font-size: 18px;
  font-weight: 600;
}

.header-controls {
  display: flex;
  gap: 8px;
}

.header-controls button {
  background: #2a2a2a;
  border: 1px solid #444;
  color: #ccc;
  padding: 6px 10px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.header-controls button:hover {
  background: #3a3a3a;
  border-color: #555;
}

.header-controls button.active {
  background: #0066cc;
  border-color: #0088ff;
  color: #ffffff;
}

.header-controls button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.loading-state, .error-state {
  text-align: center;
  padding: 40px 20px;
}

.spinner {
  border: 3px solid #333;
  border-top: 3px solid #00d4ff;
  border-radius: 50%;
  width: 30px;
  height: 30px;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state i {
  color: #ff6b6b;
  font-size: 24px;
  margin-bottom: 12px;
}

.retry-btn {
  background: #0066cc;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 12px;
}

.panel-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.metrics-section h4,
.load-levels-section h4,
.recommendations-section h4,
.quick-actions-section h4,
.summary-section h4 {
  margin: 0 0 12px 0;
  color: #00d4ff;
  font-size: 14px;
  font-weight: 600;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
}

.metric-item {
  background: #2a2a2a;
  border-radius: 6px;
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-left: 3px solid #444;
  transition: all 0.2s ease;
}

.metric-item.normal {
  border-left-color: #4caf50;
}

.metric-item.warning {
  border-left-color: #ff9800;
}

.metric-item.critical {
  border-left-color: #f44336;
}

.metric-icon {
  color: #00d4ff;
  font-size: 16px;
  width: 20px;
  text-align: center;
}

.metric-content {
  flex: 1;
}

.metric-value {
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
}

.metric-label {
  font-size: 11px;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.load-indicators {
  display: flex;
  gap: 16px;
}

.load-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #2a2a2a;
  border-radius: 6px;
}

.indicator-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.load-indicator.green .indicator-dot {
  background: #4caf50;
}

.load-indicator.yellow .indicator-dot {
  background: #ff9800;
}

.load-indicator.red .indicator-dot {
  background: #f44336;
}

.indicator-label {
  font-size: 12px;
  color: #ccc;
}

.indicator-count {
  font-weight: 600;
  color: #ffffff;
}

.heavy-modules-alert {
  background: #2d1b1b;
  border: 1px solid #f44336;
  border-radius: 6px;
  padding: 12px;
}

.alert-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.alert-header i {
  color: #f44336;
}

.alert-header h4 {
  margin: 0;
  color: #f44336;
  font-size: 14px;
}

.heavy-modules-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.heavy-module-item {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.module-name {
  color: #ccc;
}

.module-impact {
  color: #f44336;
  font-weight: 600;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.recommendation-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #2a2a2a;
  border-radius: 6px;
  border-left: 3px solid #444;
}

.recommendation-item.high-priority {
  border-left-color: #f44336;
}

.recommendation-item.medium-priority {
  border-left-color: #ff9800;
}

.recommendation-item.low-priority {
  border-left-color: #4caf50;
}

.recommendation-icon {
  color: #00d4ff;
  font-size: 14px;
  margin-top: 2px;
}

.recommendation-content {
  flex: 1;
}

.recommendation-title {
  font-weight: 600;
  color: #ffffff;
  margin-bottom: 4px;
}

.recommendation-description {
  font-size: 12px;
  color: #ccc;
  margin-bottom: 6px;
}

.recommendation-impact {
  font-size: 11px;
  color: #888;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 8px;
}

.action-btn {
  background: #2a2a2a;
  border: 1px solid #444;
  color: #ccc;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: #3a3a3a;
  border-color: #555;
  color: #ffffff;
}

.summary-content {
  background: #2a2a2a;
  border-radius: 6px;
  padding: 12px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.summary-item:last-child {
  margin-bottom: 0;
}

.summary-label {
  color: #888;
  font-size: 12px;
}

.summary-value {
  font-weight: 600;
  font-size: 12px;
}

.summary-value.normal {
  color: #4caf50;
}

.summary-value.warning {
  color: #ff9800;
}

.summary-value.critical {
  color: #f44336;
}

.summary-value.unknown {
  color: #888;
}
</style> 