<template>
  <div class="multi-char-stats">
    <!-- Header -->
    <div class="header">
      <h2>Multi-Character Statistics</h2>
      <div class="header-controls">
        <select v-model="selectedTimeframe" @change="updateStats">
          <option value="7">Last 7 Days</option>
          <option value="30">Last 30 Days</option>
          <option value="90">Last 90 Days</option>
          <option value="all">All Time</option>
        </select>
        <button @click="refreshData" :disabled="loading">
          <i class="fas fa-sync-alt" :class="{ 'fa-spin': loading }"></i>
          Refresh
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>Loading character statistics...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error">
      <i class="fas fa-exclamation-triangle"></i>
      <p>{{ error }}</p>
      <button @click="refreshData">Try Again</button>
    </div>

    <!-- Stats Content -->
    <div v-else class="stats-content">
      <!-- Summary Cards -->
      <div class="summary-cards">
        <div class="card">
          <div class="card-icon">
            <i class="fas fa-users"></i>
          </div>
          <div class="card-content">
            <h3>{{ totalCharacters }}</h3>
            <p>Total Characters</p>
          </div>
        </div>

        <div class="card">
          <div class="card-icon">
            <i class="fas fa-clock"></i>
          </div>
          <div class="card-content">
            <h3>{{ formatPlaytime(totalPlaytime) }}</h3>
            <p>Total Playtime</p>
          </div>
        </div>

        <div class="card">
          <div class="card-icon">
            <i class="fas fa-trophy"></i>
          </div>
          <div class="card-content">
            <h3>{{ formatCredits(totalXpGained) }}</h3>
            <p>Total XP Gained</p>
          </div>
        </div>

        <div class="card">
          <div class="card-icon">
            <i class="fas fa-coins"></i>
          </div>
          <div class="card-content">
            <h3>{{ formatCredits(totalCreditsEarned) }}</h3>
            <p>Total Credits Earned</p>
          </div>
        </div>
      </div>

      <!-- Character Performance Chart -->
      <div class="chart-section">
        <h3>Character Performance</h3>
        <div class="chart-container">
          <canvas ref="performanceChart"></canvas>
        </div>
      </div>

      <!-- Character Comparison Table -->
      <div class="comparison-section">
        <h3>Character Comparison</h3>
        <div class="table-container">
          <table class="comparison-table">
            <thead>
              <tr>
                <th>Character</th>
                <th>Level</th>
                <th>Profession</th>
                <th>Playtime</th>
                <th>Sessions</th>
                <th>XP Gained</th>
                <th>Credits Earned</th>
                <th>Status</th>
                <th>Last Session</th>
                <th>Quests</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="character in sortedCharacters" :key="character.character_id">
                <td>
                  <div class="character-info">
                    <span class="character-name">{{ character.name }}</span>
                    <span v-if="character.is_main_character" class="main-badge">★</span>
                  </div>
                </td>
                <td>{{ character.level }}</td>
                <td>
                  <span class="profession-badge" :class="character.profession.toLowerCase()">
                    {{ character.profession }}
                  </span>
                </td>
                <td>{{ formatPlaytime(character.total_playtime_hours) }}</td>
                <td>{{ character.total_sessions }}</td>
                <td>{{ formatCredits(character.total_xp_gained) }}</td>
                <td>{{ formatCredits(character.total_credits_earned) }}</td>
                <td>{{ getCharacterStats(character.character_id, 'combat_kills') }}</td>
                <td>{{ getCharacterStats(character.character_id, 'quests_completed') }}</td>
                <td>
                  <span class="status-badge" :class="character.status">
                    {{ character.status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Activity Breakdown -->
      <div class="activity-section">
        <h3>Activity Breakdown</h3>
        <div class="activity-grid">
          <div class="activity-card">
            <h4>Session Types</h4>
            <div class="chart-container">
              <canvas ref="sessionTypeChart"></canvas>
            </div>
          </div>

          <div class="activity-card">
            <h4>Profession Distribution</h4>
            <div class="chart-container">
              <canvas ref="professionChart"></canvas>
            </div>
          </div>

          <div class="activity-card">
            <h4>Server Distribution</h4>
            <div class="chart-container">
              <canvas ref="serverChart"></canvas>
            </div>
          </div>

          <div class="activity-card">
            <h4>Recent Activity</h4>
            <div class="recent-activity">
              <div v-for="activity in recentActivities" :key="activity.id" class="activity-item">
                <div class="activity-icon">
                  <i :class="getActivityIcon(activity.type)"></i>
                </div>
                <div class="activity-details">
                  <div class="activity-title">{{ activity.title }}</div>
                  <div class="activity-meta">
                    {{ activity.character }} • {{ formatTime(activity.timestamp) }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Auto-Launch Status -->
      <div class="auto-launch-section">
        <h3>Auto-Launch Status</h3>
        <div class="auto-launch-grid">
          <div v-for="character in charactersWithAutoLaunch" :key="character.character_id" class="auto-launch-card">
            <div class="card-header">
              <h4>{{ character.name }}</h4>
              <div class="auto-launch-status" :class="{ enabled: character.auto_launch_enabled }">
                <i class="fas fa-power-off"></i>
                {{ character.auto_launch_enabled ? 'Enabled' : 'Disabled' }}
              </div>
            </div>
            <div class="card-content">
              <div class="profile-count">
                {{ getAutoLaunchProfiles(character.character_id).length }} Profile(s)
              </div>
              <div class="last-launch">
                Last Launch: {{ formatTime(character.last_session_at) }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Chart from 'chart.js/auto';

export default {
  name: 'MultiCharStats',
  props: {
    discordUserId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      loading: true,
      error: null,
      selectedTimeframe: '30',
      characters: [],
      characterStats: {},
      characterSessions: {},
      autoLaunchProfiles: {},
      performanceChart: null,
      sessionTypeChart: null,
      professionChart: null,
      serverChart: null
    };
  },
  computed: {
    totalCharacters() {
      return this.characters.length;
    },
    totalPlaytime() {
      return this.characters.reduce((total, char) => total + char.total_playtime_hours, 0);
    },
    totalXpGained() {
      return this.characters.reduce((total, char) => total + char.total_xp_gained, 0);
    },
    totalCreditsEarned() {
      return this.characters.reduce((total, char) => total + char.total_credits_earned, 0);
    },
    sortedCharacters() {
      return [...this.characters].sort((a, b) => {
        // Sort by main character first, then by playtime
        if (a.is_main_character && !b.is_main_character) return -1;
        if (!a.is_main_character && b.is_main_character) return 1;
        return b.total_playtime_hours - a.total_playtime_hours;
      });
    },
    charactersWithAutoLaunch() {
      return this.characters.filter(char => char.auto_launch_enabled);
    },
    recentActivities() {
      const activities = [];
      this.characters.forEach(character => {
        const sessions = this.characterSessions[character.character_id] || [];
        sessions.forEach(session => {
          activities.push({
            id: session.session_id,
            type: session.session_type,
            title: `${session.session_type} Session`,
            character: character.name,
            timestamp: session.start_time,
            duration: session.duration_minutes,
            xp: session.xp_gained,
            credits: session.credits_earned
          });
        });
      });
      return activities
        .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
        .slice(0, 10);
    }
  },
  mounted() {
    this.loadData();
  },
  methods: {
    async loadData() {
      try {
        this.loading = true;
        this.error = null;

        // Simulate API calls
        const [charactersData, statsData, sessionsData, autoLaunchData] = await Promise.all([
          this.fetchCharactersData(),
          this.fetchCharacterStatsData(),
          this.fetchCharacterSessionsData(),
          this.fetchAutoLaunchProfilesData()
        ]);

        this.characters = charactersData;
        this.characterStats = statsData;
        this.characterSessions = sessionsData;
        this.autoLaunchProfiles = autoLaunchData;

        this.$nextTick(() => {
          this.initializeCharts();
        });
      } catch (err) {
        this.error = 'Failed to load character statistics. Please try again.';
        console.error('Error loading data:', err);
      } finally {
        this.loading = false;
      }
    },

    async fetchCharactersData() {
      try {
        // Fetch character data from the character registry API
        const response = await fetch('/api/character-registry/characters', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ discord_user_id: this.discordUserId }),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data.characters || [];
      } catch (error) {
        console.error('Error fetching character data:', error);
        // Return mock data for development
        return [
          {
            character_id: 'char_001',
            discord_user_id: this.discordUserId,
            name: 'DemoMarksman',
            server: 'Basilisk',
            race: 'Human',
            profession: 'Marksman',
            level: 80,
            faction: 'Rebel',
            city: 'Coronet',
            guild: 'Demo Guild',
            guild_tag: '[DEMO]',
            planet: 'Corellia',
            location: 'Coronet City',
            coordinates: [0.0, 0.0],
            status: 'active',
            role: 'main',
            is_main_character: true,
            auto_launch_enabled: false,
            created_at: '2024-01-15T10:30:00',
            updated_at: '2024-01-15T14:45:00',
            last_session_at: '2024-01-15T14:45:00',
            total_playtime_hours: 150.5,
            total_sessions: 45,
            total_xp_gained: 2500000,
            total_credits_earned: 5000000,
            notes: 'Main character for testing'
          },
          {
            character_id: 'char_002',
            discord_user_id: this.discordUserId,
            name: 'DemoCrafter',
            server: 'Basilisk',
            race: 'Human',
            profession: 'Artisan',
            level: 60,
            faction: 'Neutral',
            city: 'Theed',
            guild: 'Demo Guild',
            guild_tag: '[DEMO]',
            planet: 'Naboo',
            location: 'Theed Palace',
            coordinates: [0.0, 0.0],
            status: 'active',
            role: 'alt',
            is_main_character: false,
            auto_launch_enabled: true,
            created_at: '2024-01-10T09:15:00',
            updated_at: '2024-01-15T12:30:00',
            last_session_at: '2024-01-15T12:30:00',
            total_playtime_hours: 75.2,
            total_sessions: 22,
            total_xp_gained: 1200000,
            total_credits_earned: 2500000,
            notes: 'Crafting alt character'
          },
          {
            character_id: 'char_003',
            discord_user_id: this.discordUserId,
            name: 'DemoBoxer',
            server: 'Basilisk',
            race: 'Wookiee',
            profession: 'Brawler',
            level: 40,
            faction: 'Imperial',
            city: 'Mos Eisley',
            guild: 'Demo Guild',
            guild_tag: '[DEMO]',
            planet: 'Tatooine',
            location: 'Mos Eisley',
            coordinates: [0.0, 0.0],
            status: 'active',
            role: 'boxer',
            is_main_character: false,
            auto_launch_enabled: true,
            created_at: '2024-01-05T11:00:00',
            updated_at: '2024-01-15T13:20:00',
            last_session_at: '2024-01-15T13:20:00',
            total_playtime_hours: 45.8,
            total_sessions: 15,
            total_xp_gained: 800000,
            total_credits_earned: 1500000,
            notes: 'Boxing character for multi-account play'
          }
        ];
      }
    },

    async fetchCharacterStatsData() {
      // Simulate API call
      return {
        'char_001': {
          character_id: 'char_001',
          combat_kills: 1250,
          combat_deaths: 45,
          quests_completed: 85,
          items_crafted: 0,
          items_sold: 0,
          credits_spent: 2000000,
          distance_traveled: 1500.5,
          planets_visited: ['Corellia', 'Naboo', 'Tatooine', 'Dantooine'],
          skills_mastered: 12,
          achievements_earned: 25,
          last_updated: '2024-01-15T14:45:00'
        },
        'char_002': {
          character_id: 'char_002',
          combat_kills: 0,
          combat_deaths: 0,
          quests_completed: 15,
          items_crafted: 150,
          items_sold: 75,
          credits_spent: 500000,
          distance_traveled: 800.2,
          planets_visited: ['Naboo', 'Corellia', 'Tatooine'],
          skills_mastered: 8,
          achievements_earned: 12,
          last_updated: '2024-01-15T12:30:00'
        },
        'char_003': {
          character_id: 'char_003',
          combat_kills: 300,
          combat_deaths: 25,
          quests_completed: 30,
          items_crafted: 0,
          items_sold: 0,
          credits_spent: 800000,
          distance_traveled: 600.8,
          planets_visited: ['Tatooine', 'Corellia'],
          skills_mastered: 6,
          achievements_earned: 8,
          last_updated: '2024-01-15T13:20:00'
        }
      };
    },

    async fetchCharacterSessionsData() {
      // Simulate API call
      return {
        'char_001': [
          {
            session_id: 'session_001',
            character_id: 'char_001',
            session_type: 'combat',
            start_time: '2024-01-15T10:30:00',
            end_time: '2024-01-15T14:45:00',
            duration_minutes: 255,
            xp_gained: 25000,
            credits_earned: 50000,
            activities: ['PvP combat', 'Quest completion', 'Travel'],
            location_start: 'Coronet City',
            location_end: 'Tyrena',
            planet_start: 'Corellia',
            planet_end: 'Corellia',
            coordinates_start: [0.0, 0.0],
            coordinates_end: [0.0, 0.0],
            notes: 'Successful combat session'
          }
        ],
        'char_002': [
          {
            session_id: 'session_002',
            character_id: 'char_002',
            session_type: 'crafting',
            start_time: '2024-01-15T09:00:00',
            end_time: '2024-01-15T12:30:00',
            duration_minutes: 210,
            xp_gained: 15000,
            credits_earned: 75000,
            activities: ['Item crafting', 'Resource gathering', 'Trading'],
            location_start: 'Theed Palace',
            location_end: 'Theed Palace',
            planet_start: 'Naboo',
            planet_end: 'Naboo',
            coordinates_start: [0.0, 0.0],
            coordinates_end: [0.0, 0.0],
            notes: 'Productive crafting session'
          }
        ],
        'char_003': [
          {
            session_id: 'session_003',
            character_id: 'char_003',
            session_type: 'combat',
            start_time: '2024-01-15T11:00:00',
            end_time: '2024-01-15T13:20:00',
            duration_minutes: 140,
            xp_gained: 18000,
            credits_earned: 35000,
            activities: ['PvE combat', 'Quest completion'],
            location_start: 'Mos Eisley',
            location_end: 'Mos Eisley',
            planet_start: 'Tatooine',
            planet_end: 'Tatooine',
            coordinates_start: [0.0, 0.0],
            coordinates_end: [0.0, 0.0],
            notes: 'Boxing session with main character'
          }
        ]
      };
    },

    async fetchAutoLaunchProfilesData() {
      // Simulate API call
      return {
        'char_002': [
          {
            profile_id: 'profile_001',
            character_id: 'char_002',
            profile_name: 'Crafting Session',
            launch_order: 1,
            auto_connect: true,
            auto_login: true,
            auto_launch_macros: ['/macro craft', '/macro gather'],
            startup_commands: ['/waypoint Theed Palace'],
            window_position: [100, 100],
            window_size: [800, 600],
            is_enabled: true,
            created_at: '2024-01-10T09:00:00'
          }
        ],
        'char_003': [
          {
            profile_id: 'profile_002',
            character_id: 'char_003',
            profile_name: 'Boxing Session',
            launch_order: 2,
            auto_connect: true,
            auto_login: true,
            auto_launch_macros: ['/macro support', '/macro heal'],
            startup_commands: ['/waypoint Mos Eisley'],
            window_position: [900, 100],
            window_size: [800, 600],
            is_enabled: true,
            created_at: '2024-01-05T11:00:00'
          }
        ]
      };
    },

    initializeCharts() {
      this.createPerformanceChart();
      this.createSessionTypeChart();
      this.createProfessionChart();
      this.createServerChart();
    },

    createPerformanceChart() {
      const ctx = this.$refs.performanceChart;
      if (!ctx) return;

      this.performanceChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: this.characters.map(char => char.name),
          datasets: [
            {
              label: 'Playtime (Hours)',
              data: this.characters.map(char => char.total_playtime_hours),
              backgroundColor: 'rgba(54, 162, 235, 0.8)',
              borderColor: 'rgba(54, 162, 235, 1)',
              borderWidth: 1
            },
            {
              label: 'XP Gained (K)',
              data: this.characters.map(char => char.total_xp_gained / 1000),
              backgroundColor: 'rgba(255, 206, 86, 0.8)',
              borderColor: 'rgba(255, 206, 86, 1)',
              borderWidth: 1
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true
            }
          }
        }
      });
    },

    createSessionTypeChart() {
      const ctx = this.$refs.sessionTypeChart;
      if (!ctx) return;

      const sessionTypes = {};
      Object.values(this.characterSessions).flat().forEach(session => {
        sessionTypes[session.session_type] = (sessionTypes[session.session_type] || 0) + 1;
      });

      this.sessionTypeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: Object.keys(sessionTypes),
          datasets: [{
            data: Object.values(sessionTypes),
            backgroundColor: [
              'rgba(255, 99, 132, 0.8)',
              'rgba(54, 162, 235, 0.8)',
              'rgba(255, 206, 86, 0.8)',
              'rgba(75, 192, 192, 0.8)',
              'rgba(153, 102, 255, 0.8)'
            ]
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      });
    },

    createProfessionChart() {
      const ctx = this.$refs.professionChart;
      if (!ctx) return;

      const professions = {};
      this.characters.forEach(char => {
        professions[char.profession] = (professions[char.profession] || 0) + 1;
      });

      this.professionChart = new Chart(ctx, {
        type: 'pie',
        data: {
          labels: Object.keys(professions),
          datasets: [{
            data: Object.values(professions),
            backgroundColor: [
              'rgba(255, 99, 132, 0.8)',
              'rgba(54, 162, 235, 0.8)',
              'rgba(255, 206, 86, 0.8)',
              'rgba(75, 192, 192, 0.8)',
              'rgba(153, 102, 255, 0.8)'
            ]
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false
        }
      });
    },

    createServerChart() {
      const ctx = this.$refs.serverChart;
      if (!ctx) return;

      const servers = {};
      this.characters.forEach(char => {
        servers[char.server] = (servers[char.server] || 0) + 1;
      });

      this.serverChart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: Object.keys(servers),
          datasets: [{
            label: 'Characters',
            data: Object.values(servers),
            backgroundColor: 'rgba(75, 192, 192, 0.8)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1
              }
            }
          }
        }
      });
    },

    getCharacterStats(characterId, statName) {
      const stats = this.characterStats[characterId];
      return stats ? stats[statName] || 0 : 0;
    },

    getAutoLaunchProfiles(characterId) {
      return this.autoLaunchProfiles[characterId] || [];
    },

    getActivityIcon(type) {
      const icons = {
        combat: 'fas fa-sword',
        crafting: 'fas fa-hammer',
        questing: 'fas fa-map',
        farming: 'fas fa-seedling',
        exploration: 'fas fa-compass',
        social: 'fas fa-users',
        trading: 'fas fa-coins'
      };
      return icons[type] || 'fas fa-gamepad';
    },

    formatPlaytime(hours) {
      const days = Math.floor(hours / 24);
      const remainingHours = hours % 24;
      if (days > 0) {
        return `${days}d ${remainingHours.toFixed(1)}h`;
      }
      return `${hours.toFixed(1)}h`;
    },

    formatCredits(credits) {
      if (credits >= 1000000) {
        return `${(credits / 1000000).toFixed(1)}M`;
      } else if (credits >= 1000) {
        return `${(credits / 1000).toFixed(1)}K`;
      }
      return credits.toString();
    },

    formatTime(timestamp) {
      if (!timestamp) return 'Never';
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now - date;
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
      
      if (diffDays === 0) {
        return 'Today';
      } else if (diffDays === 1) {
        return 'Yesterday';
      } else if (diffDays < 7) {
        return `${diffDays} days ago`;
      } else {
        return date.toLocaleDateString();
      }
    },

    updateStats() {
      // In a real implementation, this would filter data based on timeframe
      this.refreshData();
    },

    refreshData() {
      this.loadData();
    }
  }
};
</script>

<style scoped>
.multi-char-stats {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.header h2 {
  margin: 0;
  color: #333;
}

.header-controls {
  display: flex;
  gap: 10px;
}

.header-controls select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
}

.header-controls button {
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.header-controls button:hover {
  background: #0056b3;
}

.header-controls button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.loading {
  text-align: center;
  padding: 50px;
}

.spinner {
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  text-align: center;
  padding: 50px;
  color: #dc3545;
}

.error i {
  font-size: 48px;
  margin-bottom: 20px;
}

.error button {
  margin-top: 20px;
  padding: 10px 20px;
  background: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  align-items: center;
  gap: 15px;
}

.card-icon {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #007bff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.card-content h3 {
  margin: 0 0 5px 0;
  font-size: 24px;
  color: #333;
}

.card-content p {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.chart-section, .comparison-section, .activity-section, .auto-launch-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.chart-section h3, .comparison-section h3, .activity-section h3, .auto-launch-section h3 {
  margin: 0 0 20px 0;
  color: #333;
}

.chart-container {
  height: 300px;
  position: relative;
}

.table-container {
  overflow-x: auto;
}

.comparison-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.comparison-table th,
.comparison-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.comparison-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #333;
}

.character-info {
  display: flex;
  align-items: center;
  gap: 5px;
}

.character-name {
  font-weight: 500;
}

.main-badge {
  color: #ffc107;
  font-size: 16px;
}

.profession-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
}

.profession-badge.marksman {
  background: #e3f2fd;
  color: #1976d2;
}

.profession-badge.artisan {
  background: #fff3e0;
  color: #f57c00;
}

.profession-badge.brawler {
  background: #ffebee;
  color: #d32f2f;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
}

.status-badge.active {
  background: #e8f5e8;
  color: #2e7d32;
}

.status-badge.inactive {
  background: #fff3e0;
  color: #f57c00;
}

.status-badge.suspended {
  background: #ffebee;
  color: #d32f2f;
}

.activity-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.activity-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
}

.activity-card h4 {
  margin: 0 0 15px 0;
  color: #333;
}

.recent-activity {
  max-height: 300px;
  overflow-y: auto;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-icon {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #007bff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}

.activity-details {
  flex: 1;
}

.activity-title {
  font-weight: 500;
  color: #333;
  margin-bottom: 2px;
}

.activity-meta {
  font-size: 12px;
  color: #666;
}

.auto-launch-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.auto-launch-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  border-left: 4px solid #007bff;
}

.auto-launch-card .card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.auto-launch-card h4 {
  margin: 0;
  color: #333;
}

.auto-launch-status {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #666;
}

.auto-launch-status.enabled {
  color: #2e7d32;
}

.auto-launch-status i {
  font-size: 14px;
}

.card-content {
  font-size: 12px;
  color: #666;
}

.profile-count {
  margin-bottom: 5px;
}

.last-launch {
  font-style: italic;
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }

  .summary-cards {
    grid-template-columns: 1fr;
  }

  .activity-grid {
    grid-template-columns: 1fr;
  }

  .auto-launch-grid {
    grid-template-columns: 1fr;
  }

  .comparison-table {
    font-size: 12px;
  }

  .comparison-table th,
  .comparison-table td {
    padding: 8px;
  }
}
</style> 