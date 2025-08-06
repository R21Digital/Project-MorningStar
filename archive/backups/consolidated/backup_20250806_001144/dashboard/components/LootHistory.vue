<template>
  <div class="loot-history">
    <div class="header">
      <h2>📦 Loot History</h2>
      <div class="controls">
        <div class="search-box">
          <input 
            v-model="searchQuery" 
            placeholder="Search items or sources..."
            class="search-input"
          />
          <button @click="clearSearch" class="clear-btn">×</button>
        </div>
        <select v-model="selectedSource" class="source-filter">
          <option value="">All Sources</option>
          <option v-for="source in availableSources" :key="source" :value="source">
            {{ source }}
          </option>
        </select>
        <select v-model="selectedRarity" class="rarity-filter">
          <option value="">All Rarities</option>
          <option value="common">Common</option>
          <option value="uncommon">Uncommon</option>
          <option value="rare">Rare</option>
          <option value="epic">Epic</option>
          <option value="legendary">Legendary</option>
        </select>
      </div>
    </div>

    <!-- Statistics Cards -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-value">{{ statistics.total_items || 0 }}</div>
        <div class="stat-label">Total Items</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ statistics.total_sources || 0 }}</div>
        <div class="stat-label">Sources</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ statistics.total_sessions || 0 }}</div>
        <div class="stat-label">Sessions</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ formatValue(statistics.total_value || 0) }}</div>
        <div class="stat-label">Total Value</div>
      </div>
    </div>

    <!-- Recent Loot Section -->
    <div class="recent-loot-section">
      <h3>Last 20 Items Looted</h3>
      <div class="loot-grid">
        <div 
          v-for="item in filteredRecentLoot" 
          :key="`${item.item_id}-${item.timestamp}`"
          class="loot-card"
          :class="getRarityClass(item.rarity)"
        >
          <div class="loot-header">
            <div class="item-info">
              <h4>{{ item.item_name }}</h4>
              <span class="quantity">×{{ item.quantity }}</span>
            </div>
            <div class="rarity-badge" :class="item.rarity">
              {{ item.rarity.toUpperCase() }}
            </div>
          </div>
          <div class="loot-details">
            <div class="source">From: {{ item.source_name }}</div>
            <div class="timestamp">{{ formatTimestamp(item.timestamp) }}</div>
            <div class="detection">
              <span class="detection-method">{{ item.macro_detected ? 'Macro' : 'OCR' }}</span>
              <span v-if="item.ocr_confidence" class="confidence">
                {{ (item.ocr_confidence * 100).toFixed(1) }}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loot Tables Section -->
    <div class="loot-tables-section">
      <h3>Loot Tables</h3>
      <div class="tables-grid">
        <div 
          v-for="(table, sourceName) in lootTables" 
          :key="sourceName"
          class="table-card"
        >
          <div class="table-header">
            <h4>{{ sourceName }}</h4>
            <div class="table-stats">
              <span>{{ table.total_loot }} items</span>
              <span>{{ table.total_kills }} kills</span>
            </div>
          </div>
          <div class="table-content">
            <div class="rarity-distribution">
              <div 
                v-for="(count, rarity) in table.rarity_distribution" 
                :key="rarity"
                class="rarity-item"
                :class="rarity"
              >
                <span class="rarity-name">{{ rarity }}</span>
                <span class="rarity-count">{{ count }}</span>
              </div>
            </div>
            <div class="top-items">
              <h5>Top Items</h5>
              <div 
                v-for="(itemData, itemId) in getTopItems(table, 3)" 
                :key="itemId"
                class="top-item"
              >
                <span class="item-name">{{ itemData.name }}</span>
                <span class="drop-rate">{{ table.drop_rates[itemId] }}%</span>
              </div>
            </div>
          </div>
          <div class="table-footer">
            <span class="last-updated">
              Updated: {{ formatTimestamp(table.last_updated) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Krayt Loot Memory Section -->
    <div v-if="kraytTable" class="krayt-section">
      <h3>🐉 Krayt Loot Memory</h3>
      <div class="krayt-stats">
        <div class="krayt-stat">
          <span class="stat-label">Total Kills:</span>
          <span class="stat-value">{{ kraytTable.total_kills }}</span>
        </div>
        <div class="krayt-stat">
          <span class="stat-label">Total Loot:</span>
          <span class="stat-value">{{ kraytTable.total_loot }}</span>
        </div>
        <div class="krayt-stat">
          <span class="stat-label">Pearls Found:</span>
          <span class="stat-value">{{ getKraytPearlCount() }}</span>
        </div>
      </div>
      <div class="krayt-items">
        <div 
          v-for="(itemData, itemId) in kraytTable.items" 
          :key="itemId"
          class="krayt-item"
          :class="itemData.rarity"
        >
          <div class="item-header">
            <span class="item-name">{{ itemData.name }}</span>
            <span class="drop-rate">{{ kraytTable.drop_rates[itemId] }}%</span>
          </div>
          <div class="item-stats">
            <span>Drops: {{ itemData.total_drops }}</span>
            <span>Total: {{ itemData.total_quantity }}</span>
            <span>Last: {{ formatTimestamp(itemData.last_seen) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading and Error States -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading loot data...</p>
    </div>

    <div v-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <p>{{ error }}</p>
      <button @click="loadData" class="retry-btn">Retry</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LootHistory',
  data() {
    return {
      recentLoot: [],
      lootTables: {},
      statistics: {},
      loading: true,
      error: null,
      searchQuery: '',
      selectedSource: '',
      selectedRarity: '',
      refreshInterval: null
    }
  },
  computed: {
    filteredRecentLoot() {
      let filtered = this.recentLoot

      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        filtered = filtered.filter(item => 
          item.item_name.toLowerCase().includes(query) ||
          item.source_name.toLowerCase().includes(query)
        )
      }

      if (this.selectedSource) {
        filtered = filtered.filter(item => 
          item.source_name.toLowerCase() === this.selectedSource.toLowerCase()
        )
      }

      if (this.selectedRarity) {
        filtered = filtered.filter(item => 
          item.rarity.toLowerCase() === this.selectedRarity.toLowerCase()
        )
      }

      return filtered.slice(-20) // Last 20 items
    },
    availableSources() {
      const sources = new Set()
      this.recentLoot.forEach(item => sources.add(item.source_name))
      return Array.from(sources).sort()
    },
    kraytTable() {
      return this.lootTables['Krayt Dragon'] || null
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
      try {
        this.loading = true
        this.error = null

        // Load recent loot
        const lootResponse = await fetch('/api/loot/recent')
        if (lootResponse.ok) {
          const lootData = await lootResponse.json()
          this.recentLoot = lootData.items || []
        }

        // Load loot tables
        const tablesResponse = await fetch('/api/loot/tables')
        if (tablesResponse.ok) {
          const tablesData = await tablesResponse.json()
          this.lootTables = tablesData.tables || {}
        }

        // Load statistics
        const statsResponse = await fetch('/api/loot/statistics')
        if (statsResponse.ok) {
          const statsData = await statsResponse.json()
          this.statistics = statsData
        }

      } catch (err) {
        this.error = err.message || 'Failed to load loot data'
      } finally {
        this.loading = false
      }
    },
    startAutoRefresh() {
      this.refreshInterval = setInterval(this.loadData, 30000) // Refresh every 30 seconds
    },
    stopAutoRefresh() {
      if (this.refreshInterval) {
        clearInterval(this.refreshInterval)
        this.refreshInterval = null
      }
    },
    clearSearch() {
      this.searchQuery = ''
    },
    formatTimestamp(timestamp) {
      const date = new Date(timestamp)
      return date.toLocaleString()
    },
    formatValue(value) {
      if (value >= 1000000) {
        return `${(value / 1000000).toFixed(1)}M`
      } else if (value >= 1000) {
        return `${(value / 1000).toFixed(1)}K`
      }
      return value.toString()
    },
    getRarityClass(rarity) {
      return `rarity-${rarity.toLowerCase()}`
    },
    getTopItems(table, limit = 3) {
      const items = Object.entries(table.items)
        .sort(([, a], [, b]) => b.total_drops - a.total_drops)
        .slice(0, limit)
        .reduce((obj, [id, data]) => {
          obj[id] = data
          return obj
        }, {})
      return items
    },
    getKraytPearlCount() {
      if (!this.kraytTable) return 0
      
      const pearlItem = Object.values(this.kraytTable.items)
        .find(item => item.name.includes('Pearl'))
      
      return pearlItem ? pearlItem.total_drops : 0
    }
  }
}
</script>

<style scoped>
.loot-history {
  padding: 24px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  border-radius: 12px;
  color: #ffffff;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.1);
}

.header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  background: linear-gradient(135deg, #00aaff 0%, #0088cc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input {
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  font-size: 14px;
  width: 200px;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.6);
}

.clear-btn {
  position: absolute;
  right: 8px;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.6);
  cursor: pointer;
  font-size: 16px;
}

.source-filter,
.rarity-filter {
  padding: 8px 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  font-size: 14px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
  color: #ffffff;
}

.stat-label {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: rgba(255, 255, 255, 0.7);
}

.recent-loot-section h3,
.loot-tables-section h3,
.krayt-section h3 {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
  color: #ffffff;
}

.loot-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  margin-bottom: 32px;
}

.loot-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.loot-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.loot-card.rarity-legendary {
  border-color: #ffd700;
  background: rgba(255, 215, 0, 0.1);
}

.loot-card.rarity-epic {
  border-color: #ff6b6b;
  background: rgba(255, 107, 107, 0.1);
}

.loot-card.rarity-rare {
  border-color: #4ecdc4;
  background: rgba(78, 205, 196, 0.1);
}

.loot-card.rarity-uncommon {
  border-color: #45b7d1;
  background: rgba(69, 183, 209, 0.1);
}

.loot-card.rarity-common {
  border-color: #96ceb4;
  background: rgba(150, 206, 180, 0.1);
}

.loot-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.item-info h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
}

.quantity {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.rarity-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.rarity-badge.legendary {
  background: #ffd700;
  color: #000;
}

.rarity-badge.epic {
  background: #ff6b6b;
  color: #fff;
}

.rarity-badge.rare {
  background: #4ecdc4;
  color: #fff;
}

.rarity-badge.uncommon {
  background: #45b7d1;
  color: #fff;
}

.rarity-badge.common {
  background: #96ceb4;
  color: #fff;
}

.loot-details {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.source {
  margin-bottom: 4px;
}

.timestamp {
  margin-bottom: 4px;
}

.detection {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detection-method {
  font-weight: 600;
  color: #00aaff;
}

.confidence {
  color: rgba(255, 255, 255, 0.5);
}

.tables-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
  margin-bottom: 32px;
}

.table-card {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #ffffff;
}

.table-stats {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.rarity-distribution {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.rarity-item {
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  gap: 4px;
}

.rarity-item.legendary {
  background: rgba(255, 215, 0, 0.2);
  color: #ffd700;
}

.rarity-item.epic {
  background: rgba(255, 107, 107, 0.2);
  color: #ff6b6b;
}

.rarity-item.rare {
  background: rgba(78, 205, 196, 0.2);
  color: #4ecdc4;
}

.rarity-item.uncommon {
  background: rgba(69, 183, 209, 0.2);
  color: #45b7d1;
}

.rarity-item.common {
  background: rgba(150, 206, 180, 0.2);
  color: #96ceb4;
}

.top-items h5 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
}

.top-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 0;
  font-size: 12px;
}

.item-name {
  color: #ffffff;
}

.drop-rate {
  color: #00aaff;
  font-weight: 600;
}

.table-footer {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 11px;
  color: rgba(255, 255, 255, 0.5);
}

.krayt-section {
  background: rgba(255, 215, 0, 0.1);
  border: 1px solid rgba(255, 215, 0, 0.3);
  border-radius: 12px;
  padding: 20px;
  margin-top: 32px;
}

.krayt-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.krayt-stat {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
}

.stat-label {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.7);
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: #ffd700;
}

.krayt-items {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 12px;
}

.krayt-item {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.krayt-item.legendary {
  border-color: #ffd700;
  background: rgba(255, 215, 0, 0.1);
}

.krayt-item.epic {
  border-color: #ff6b6b;
  background: rgba(255, 107, 107, 0.1);
}

.krayt-item.rare {
  border-color: #4ecdc4;
  background: rgba(78, 205, 196, 0.1);
}

.krayt-item.uncommon {
  border-color: #45b7d1;
  background: rgba(69, 183, 209, 0.1);
}

.krayt-item.common {
  border-color: #96ceb4;
  background: rgba(150, 206, 180, 0.1);
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.item-name {
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
}

.drop-rate {
  font-size: 12px;
  color: #00aaff;
  font-weight: 600;
}

.item-stats {
  display: flex;
  gap: 12px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.7);
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #333;
  border-top: 4px solid #00aaff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.retry-btn {
  background: linear-gradient(135deg, #ff4444 0%, #cc0000 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  margin-top: 16px;
}

.retry-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 68, 68, 0.3);
}

@media (max-width: 768px) {
  .loot-history {
    padding: 16px;
  }

  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .controls {
    flex-direction: column;
    width: 100%;
  }

  .search-input {
    width: 100%;
  }

  .loot-grid {
    grid-template-columns: 1fr;
  }

  .tables-grid {
    grid-template-columns: 1fr;
  }

  .krayt-items {
    grid-template-columns: 1fr;
  }
}
</style> 