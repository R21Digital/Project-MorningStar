/**
 * Heroic Boss Tracker Leaderboard - Eleventy Generator
 * Generates dynamic leaderboard pages for heroic boss statistics and kill tracking
 */

const fs = require('fs');
const path = require('path');

class HeroicLeaderboardGenerator {
  data() {
    return {
      title: "Heroic Boss Leaderboards - MorningStar",
      description: "Track heroic boss kills, participation stats, and first-kill achievements across all seasons",
      layout: "base.11ty.js",
      permalink: "/heroics/leaderboard/",
      tags: ["heroics", "leaderboard", "stats"],
      eleventyNavigation: {
        key: "Heroic Leaderboards",
        parent: "Heroics",
        order: 1
      }
    };
  }

  async render(data) {
    // Load boss kills data
    const bossKillsPath = path.join(__dirname, '../../data/heroics/boss_kills.json');
    let bossData = {};
    
    try {
      const rawData = fs.readFileSync(bossKillsPath, 'utf8');
      bossData = JSON.parse(rawData);
    } catch (error) {
      console.warn('Could not load boss kills data:', error.message);
      bossData = this.getDefaultBossData();
    }

    const { metadata, bosses, leaderboards, analytics } = bossData;
    const currentSeason = metadata?.currentSeason || 'Season 15';

    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${data.title}</title>
    <meta name="description" content="${data.description}">
    
    <!-- Custom CSS for leaderboards -->
    <style>
        .heroic-dashboard {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .dashboard-header {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            padding: 40px 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        }
        
        .dashboard-header h1 {
            margin: 0 0 10px 0;
            font-size: 3em;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        
        .dashboard-header .subtitle {
            font-size: 1.2em;
            opacity: 0.9;
            margin-bottom: 20px;
        }
        
        .stats-overview {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border-left: 4px solid #007bff;
            transition: transform 0.2s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-5px);
        }
        
        .stat-card .number {
            font-size: 2.5em;
            font-weight: bold;
            color: #007bff;
            margin-bottom: 10px;
        }
        
        .stat-card .label {
            color: #666;
            font-size: 1.1em;
            font-weight: 500;
        }
        
        .section-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        @media (max-width: 768px) {
            .section-grid {
                grid-template-columns: 1fr;
            }
        }
        
        .leaderboard-section {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .section-title {
            font-size: 1.8em;
            font-weight: 600;
            margin-bottom: 20px;
            color: #333;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }
        
        .leaderboard-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .leaderboard-table th {
            background: #f8f9fa;
            padding: 15px 12px;
            text-align: left;
            font-weight: 600;
            color: #555;
            border-bottom: 2px solid #dee2e6;
        }
        
        .leaderboard-table td {
            padding: 12px;
            border-bottom: 1px solid #dee2e6;
            vertical-align: middle;
        }
        
        .leaderboard-table tr:hover {
            background: #f8f9fa;
        }
        
        .rank {
            font-weight: bold;
            color: #007bff;
            font-size: 1.1em;
            width: 60px;
        }
        
        .player-name {
            font-weight: 600;
            color: #333;
        }
        
        .discord-hash {
            font-family: monospace;
            font-size: 0.8em;
            color: #666;
            background: #f1f3f4;
            padding: 2px 6px;
            border-radius: 3px;
        }
        
        .boss-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }
        
        .boss-card {
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border-top: 4px solid;
            transition: transform 0.2s ease;
        }
        
        .boss-card:hover {
            transform: translateY(-3px);
        }
        
        .boss-card.legendary { border-top-color: #ff6b35; }
        .boss-card.hard { border-top-color: #f39c12; }
        .boss-card.medium { border-top-color: #27ae60; }
        
        .boss-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .boss-name {
            font-size: 1.4em;
            font-weight: 700;
            color: #333;
        }
        
        .boss-location {
            color: #666;
            font-size: 0.9em;
        }
        
        .difficulty-badge {
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .difficulty-badge.legendary {
            background: #ff6b35;
            color: white;
        }
        
        .difficulty-badge.hard {
            background: #f39c12;
            color: white;
        }
        
        .difficulty-badge.medium {
            background: #27ae60;
            color: white;
        }
        
        .boss-stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin: 20px 0;
        }
        
        .boss-stat {
            text-align: center;
        }
        
        .boss-stat .value {
            font-size: 1.3em;
            font-weight: bold;
            color: #007bff;
        }
        
        .boss-stat .label {
            font-size: 0.9em;
            color: #666;
        }
        
        .first-kill-banner {
            background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
            color: #333;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            border-left: 4px solid #f39c12;
        }
        
        .first-kill-banner .title {
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .first-kill-banner .team {
            font-size: 0.9em;
        }
        
        .recent-kills {
            margin-top: 15px;
        }
        
        .recent-kill {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 6px;
            margin-bottom: 8px;
            font-size: 0.9em;
        }
        
        .kill-time {
            font-weight: 600;
            color: #007bff;
        }
        
        .season-selector {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .season-btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            margin: 0 5px;
            border-radius: 5px;
            cursor: pointer;
            font-weight: 600;
            transition: background 0.2s ease;
        }
        
        .season-btn:hover {
            background: #0056b3;
        }
        
        .season-btn.active {
            background: #28a745;
        }
        
        .analytics-section {
            background: white;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .chart-container {
            height: 300px;
            background: #f8f9fa;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #666;
            font-style: italic;
        }
        
        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            border-top: 1px solid #dee2e6;
            margin-top: 30px;
        }
        
        .update-time {
            font-size: 0.9em;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="heroic-dashboard">
        <!-- Dashboard Header -->
        <div class="dashboard-header">
            <h1>🏆 Heroic Boss Leaderboards</h1>
            <div class="subtitle">Track the galaxy's greatest heroes and their legendary achievements</div>
            <div class="update-time">
                Last Updated: ${new Date(metadata?.lastUpdated || Date.now()).toLocaleString()}
                | Current Season: ${currentSeason}
            </div>
        </div>

        <!-- Stats Overview -->
        <div class="stats-overview">
            <div class="stat-card">
                <div class="number">${this.formatNumber(metadata?.totalKills || 0)}</div>
                <div class="label">Total Boss Kills</div>
            </div>
            <div class="stat-card">
                <div class="number">${this.formatNumber(metadata?.totalPlayers || 0)}</div>
                <div class="label">Active Hunters</div>
            </div>
            <div class="stat-card">
                <div class="number">${metadata?.averageTeamSize || 4.2}</div>
                <div class="label">Avg Team Size</div>
            </div>
            <div class="stat-card">
                <div class="number">${Object.keys(bosses || {}).length}</div>
                <div class="label">Heroic Bosses</div>
            </div>
        </div>

        <!-- Boss Cards Grid -->
        <div class="boss-grid">
            ${this.renderBossCards(bosses || {})}
        </div>

        <!-- Leaderboards Section -->
        <div class="section-grid">
            <!-- Most Kills Leaderboard -->
            <div class="leaderboard-section">
                <h2 class="section-title">🥇 Top Killers</h2>
                <table class="leaderboard-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Hunter</th>
                            <th>Total Kills</th>
                            <th>Avg Time</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${this.renderLeaderboardRows(leaderboards?.mostKills || [])}
                    </tbody>
                </table>
            </div>

            <!-- Fastest Killers Leaderboard -->
            <div class="leaderboard-section">
                <h2 class="section-title">⚡ Speed Demons</h2>
                <table class="leaderboard-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Hunter</th>
                            <th>Best Time</th>
                            <th>Boss</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${this.renderFastestKillersRows(leaderboards?.fastestKillers || [])}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Team Players and Season Stats -->
        <div class="section-grid">
            <!-- Team Players -->
            <div class="leaderboard-section">
                <h2 class="section-title">🤝 Team Players</h2>
                <table class="leaderboard-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Hunter</th>
                            <th>Teams Joined</th>
                            <th>Avg Team Size</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${this.renderTeamPlayersRows(leaderboards?.teamPlayers || [])}
                    </tbody>
                </table>
            </div>

            <!-- Current Season Top Players -->
            <div class="leaderboard-section">
                <h2 class="section-title">👑 ${currentSeason} Champions</h2>
                <table class="leaderboard-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Hunter</th>
                            <th>Kills</th>
                            <th>First Kills</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${this.renderSeasonPlayersRows(leaderboards?.seasonStats?.season_15?.topPlayers || [])}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Analytics Section -->
        <div class="analytics-section">
            <h2 class="section-title">📊 Analytics & Trends</h2>
            <div class="section-grid">
                <div>
                    <h3>Boss Popularity</h3>
                    ${this.renderBossPopularity(analytics?.popularityRanking || [])}
                </div>
                <div>
                    <h3>Team Size Distribution</h3>
                    ${this.renderTeamSizeDistribution(analytics?.teamSizeDistribution || {})}
                </div>
            </div>
            <div class="chart-container">
                📈 Interactive charts would be rendered here with Chart.js or similar
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>Part of the MorningStar SWG Enhancement Suite</p>
            <p class="update-time">Data auto-updates every 15 minutes | Season resets quarterly</p>
        </div>
    </div>

    <!-- JavaScript for interactivity -->
    <script>
        // Season selector functionality
        function switchSeason(seasonId) {
            // This would reload data for the selected season
            console.log('Switching to season:', seasonId);
            // In a real implementation, this would make an API call
        }

        // Real-time updates
        function refreshData() {
            // This would fetch latest boss kill data
            console.log('Refreshing leaderboard data...');
            // In a real implementation, this would update the displays
        }

        // Auto-refresh every 5 minutes
        setInterval(refreshData, 300000);

        // Initialize any interactive elements
        document.addEventListener('DOMContentLoaded', function() {
            console.log('Heroic Boss Leaderboard loaded');
            
            // Add hover effects for better UX
            const cards = document.querySelectorAll('.boss-card, .stat-card');
            cards.forEach(card => {
                card.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-5px)';
                });
                card.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0)';
                });
            });
        });
    </script>
</body>
</html>`;
  }

  renderBossCards(bosses) {
    return Object.values(bosses).map(boss => {
      const difficultyClass = boss.difficulty.toLowerCase();
      const firstKill = boss.stats?.firstKillThisSeason;
      
      return `
        <div class="boss-card ${difficultyClass}">
            <div class="boss-header">
                <div>
                    <div class="boss-name">${boss.displayName}</div>
                    <div class="boss-location">${boss.location}</div>
                </div>
                <div class="difficulty-badge ${difficultyClass}">${boss.difficulty}</div>
            </div>
            
            <div class="boss-stats">
                <div class="boss-stat">
                    <div class="value">${this.formatNumber(boss.stats?.totalKills || 0)}</div>
                    <div class="label">Total Kills</div>
                </div>
                <div class="boss-stat">
                    <div class="value">${boss.stats?.uniqueKillers || 0}</div>
                    <div class="label">Unique Killers</div>
                </div>
                <div class="boss-stat">
                    <div class="value">${this.formatTime(boss.stats?.fastestKill || 0)}</div>
                    <div class="label">Fastest Kill</div>
                </div>
                <div class="boss-stat">
                    <div class="value">${boss.stats?.averageTeamSize || 0}</div>
                    <div class="label">Avg Team Size</div>
                </div>
            </div>

            ${firstKill ? `
            <div class="first-kill-banner">
                <div class="title">🥇 First Kill This Season</div>
                <div class="team">
                    ${firstKill.team?.map(member => member.alias).join(', ') || 'Unknown Team'}
                </div>
                <div>Time: ${this.formatTime(firstKill.killTime)} | ${new Date(firstKill.timestamp).toLocaleDateString()}</div>
            </div>
            ` : ''}

            <div class="recent-kills">
                <strong>Recent Kills:</strong>
                ${(boss.stats?.recentKills || []).slice(0, 2).map(kill => `
                    <div class="recent-kill">
                        <span class="kill-time">${this.formatTime(kill.killTime)}</span> - 
                        ${kill.team?.map(member => member.alias).join(', ') || 'Unknown'}
                        <br><small>${new Date(kill.timestamp).toLocaleDateString()}</small>
                    </div>
                `).join('')}
            </div>
        </div>
      `;
    }).join('');
  }

  renderLeaderboardRows(players) {
    return players.slice(0, 10).map((player, index) => `
      <tr>
        <td class="rank">#${index + 1}</td>
        <td class="player-name">${player.alias}</td>
        <td>${player.totalKills}</td>
        <td>${this.formatTime(player.averageKillTime)}</td>
      </tr>
    `).join('');
  }

  renderFastestKillersRows(players) {
    return players.slice(0, 10).map((player, index) => `
      <tr>
        <td class="rank">#${index + 1}</td>
        <td class="player-name">${player.alias}</td>
        <td class="kill-time">${this.formatTime(player.fastestKill)}</td>
        <td>${this.formatBossName(player.boss)}</td>
      </tr>
    `).join('');
  }

  renderTeamPlayersRows(players) {
    return players.slice(0, 10).map((player, index) => `
      <tr>
        <td class="rank">#${index + 1}</td>
        <td class="player-name">${player.alias}</td>
        <td>${player.teamsJoined}</td>
        <td>${player.averageTeamSize}</td>
      </tr>
    `).join('');
  }

  renderSeasonPlayersRows(players) {
    return players.slice(0, 10).map((player, index) => `
      <tr>
        <td class="rank">#${index + 1}</td>
        <td class="player-name">${player.alias}</td>
        <td>${player.kills}</td>
        <td>${player.firstKills}</td>
      </tr>
    `).join('');
  }

  renderBossPopularity(popularity) {
    return `
      <div class="popularity-list">
        ${popularity.map((boss, index) => `
          <div class="popularity-item" style="margin-bottom: 10px;">
            <strong>#${index + 1}</strong> ${this.formatBossName(boss.boss)} - 
            <span style="color: #007bff;">${boss.killPercentage}%</span>
            <small>(${boss.averageWaitTime}min avg wait)</small>
          </div>
        `).join('')}
      </div>
    `;
  }

  renderTeamSizeDistribution(distribution) {
    const total = Object.values(distribution).reduce((sum, count) => sum + count, 0);
    return `
      <div class="distribution-list">
        ${Object.entries(distribution).map(([size, count]) => {
          const percentage = ((count / total) * 100).toFixed(1);
          return `
            <div style="margin-bottom: 8px;">
              <strong>${this.formatTeamSizeLabel(size)}:</strong> 
              ${count} <small>(${percentage}%)</small>
            </div>
          `;
        }).join('')}
      </div>
    `;
  }

  formatNumber(num) {
    return new Intl.NumberFormat().format(num);
  }

  formatTime(seconds) {
    if (!seconds) return '0:00';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  }

  formatBossName(bossId) {
    const bossNames = {
      'exar_kun': 'Exar Kun',
      'ig88': 'IG-88',
      'tusken_king': 'Tusken King',
      'lord_nyax': 'Lord Nyax',
      'axkva_min': 'Axkva Min'
    };
    return bossNames[bossId] || bossId;
  }

  formatTeamSizeLabel(size) {
    const labels = {
      'solo': 'Solo (1)',
      'duo': 'Duo (2)',
      'trio': 'Trio (3)',
      'quad': 'Quad (4)',
      'quintet': 'Quintet (5)',
      'sextet': 'Sextet (6)',
      'larger': 'Large (7+)'
    };
    return labels[size] || size;
  }

  getDefaultBossData() {
    return {
      metadata: {
        currentSeason: "Season 15",
        totalKills: 0,
        totalPlayers: 0,
        averageTeamSize: 4.0,
        lastUpdated: new Date().toISOString()
      },
      bosses: {},
      leaderboards: {
        mostKills: [],
        fastestKillers: [],
        teamPlayers: [],
        seasonStats: {}
      },
      analytics: {
        popularityRanking: [],
        teamSizeDistribution: {}
      }
    };
  }
}

module.exports = HeroicLeaderboardGenerator;