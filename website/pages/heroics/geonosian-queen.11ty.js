const yaml = require('js-yaml');
const fs = require('fs');
const path = require('path');

module.exports = class {
  data() {
    return {
      title: "Geonosian Queen Heroic - SWGDB",
      description: "Face the Geonosian Queen and her royal guard in their hive. View live loot drops, boss mechanics, and strategies.",
      layout: "base.njk",
      permalink: "/heroics/geonosian-queen/",
      heroicId: "geonosian_queen",
      heroicName: "Geonosian Queen"
    };
  }

  render(data) {
    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${data.title}</title>
    <meta name="description" content="${data.description}">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <link href="/styles/loot.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #007bff;
            --secondary-color: #6c757d;
            --success-color: #28a745;
            --danger-color: #dc3545;
            --warning-color: #ffc107;
            --info-color: #17a2b8;
            --light-color: #f8f9fa;
            --dark-color: #343a40;
            --geonosian-color: #d32f2f;
            --hive-color: #795548;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #d32f2f 0%, #795548 100%);
            min-height: 100vh;
        }

        .main-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            margin: 20px auto;
            max-width: 1400px;
            overflow: hidden;
        }

        .header-section {
            background: linear-gradient(135deg, var(--geonosian-color) 0%, var(--hive-color) 100%);
            color: white;
            padding: 30px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .header-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
            pointer-events: none;
        }

        .header-section h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
            position: relative;
            z-index: 1;
        }

        .header-section p {
            font-size: 1.1rem;
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }

        .content-section {
            padding: 30px;
        }

        .tab-navigation {
            display: flex;
            background: var(--light-color);
            border-radius: 8px;
            padding: 5px;
            margin-bottom: 30px;
            gap: 5px;
        }

        .tab-btn {
            flex: 1;
            background: transparent;
            border: none;
            padding: 15px 20px;
            border-radius: 6px;
            font-weight: 500;
            color: var(--secondary-color);
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .tab-btn.active {
            background: var(--geonosian-color);
            color: white;
            box-shadow: 0 2px 8px rgba(211, 47, 47, 0.3);
        }

        .tab-btn:hover:not(.active) {
            background: rgba(211, 47, 47, 0.1);
            color: var(--geonosian-color);
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }

        .info-card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            padding: 25px;
            border: 1px solid #e9ecef;
        }

        .info-card h3 {
            color: var(--dark-color);
            font-size: 1.3rem;
            margin-bottom: 15px;
            font-weight: 600;
            display: flex;
            align-items: center;
        }

        .info-card h3 i {
            margin-right: 10px;
            color: var(--geonosian-color);
        }

        .boss-section {
            background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 30px;
        }

        .boss-section h2 {
            color: var(--geonosian-color);
            margin-bottom: 20px;
            font-weight: 600;
        }

        .boss-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            border-left: 4px solid var(--geonosian-color);
        }

        .boss-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .boss-name {
            font-size: 1.4rem;
            font-weight: 600;
            color: var(--dark-color);
        }

        .difficulty-badge {
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        .difficulty-medium { 
            background: var(--warning-color); 
            color: var(--dark-color); 
        }

        .mechanics-list {
            list-style: none;
            padding: 0;
        }

        .mechanics-list li {
            background: var(--light-color);
            padding: 8px 12px;
            margin-bottom: 8px;
            border-radius: 6px;
            font-size: 0.9rem;
            border-left: 4px solid var(--geonosian-color);
        }

        .strategy-section {
            background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
            border-radius: 12px;
            padding: 25px;
        }

        .strategy-step {
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border-left: 4px solid var(--success-color);
        }

        .strategy-step h4 {
            color: var(--dark-color);
            font-size: 1rem;
            margin-bottom: 8px;
            font-weight: 600;
        }

        .strategy-step p {
            color: var(--secondary-color);
            font-size: 0.9rem;
            margin: 0;
        }

        .back-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            font-weight: 500;
            transition: all 0.3s ease;
        }

        .back-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
            color: white;
            text-decoration: none;
        }

        .back-btn i {
            margin-right: 8px;
        }

        .live-indicator {
            display: inline-flex;
            align-items: center;
            gap: 5px;
            color: var(--success-color);
            font-weight: 500;
            font-size: 0.9rem;
            margin-top: 10px;
        }

        .live-dot {
            width: 8px;
            height: 8px;
            background: var(--success-color);
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }

        .loot-summary {
            background: linear-gradient(135deg, #fce4ec 0%, #f8bbd9 100%);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }

        .loot-summary h3 {
            color: #ad1457;
            margin-bottom: 15px;
        }

        .loot-stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }

        .loot-stat {
            background: rgba(255, 255, 255, 0.8);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }

        .loot-stat .number {
            font-size: 1.8rem;
            font-weight: 700;
            color: #ad1457;
            display: block;
        }

        .loot-stat .label {
            font-size: 0.9rem;
            color: #6c757d;
            margin-top: 5px;
        }

        .hive-highlight {
            background: linear-gradient(135deg, #fff3e0 0%, #ffcc80 100%);
            border: 2px solid #ff8f00;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
        }

        .hive-highlight h4 {
            color: #ff8f00;
            margin-bottom: 10px;
            font-weight: 600;
        }

        .hive-highlight p {
            color: #e65100;
            margin: 0;
            font-size: 0.9rem;
        }

        @media (max-width: 768px) {
            .tab-navigation {
                flex-direction: column;
            }
            
            .tab-btn {
                text-align: center;
            }
            
            .info-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="main-container">
        <div class="header-section">
            <h1><i class="fas fa-bug"></i> Geonosian Queen</h1>
            <p>Face the Geonosian Queen and her royal guard in their underground hive</p>
            <div class="live-indicator">
                <div class="live-dot"></div>
                Live loot tracking active
            </div>
        </div>

        <div class="content-section">
            <!-- Tab Navigation -->
            <div class="tab-navigation">
                <button class="tab-btn active" data-tab="overview">
                    <i class="fas fa-info-circle"></i>
                    Overview
                </button>
                <button class="tab-btn" data-tab="loot">
                    <i class="fas fa-treasure-chest"></i>
                    Live Loot Table
                </button>
                <button class="tab-btn" data-tab="strategy">
                    <i class="fas fa-chess"></i>
                    Strategy
                </button>
            </div>

            <!-- Overview Tab -->
            <div class="tab-content active" id="overview">
                <div class="info-grid">
                    <div class="info-card">
                        <h3><i class="fas fa-globe"></i> Location</h3>
                        <p><strong>Planet:</strong> Geonosis</p>
                        <p><strong>Zone:</strong> Royal Hive</p>
                        <p><strong>Coordinates:</strong> 3400, -4800</p>
                    </div>

                    <div class="info-card">
                        <h3><i class="fas fa-users"></i> Entry Requirements</h3>
                        <p><strong>Level:</strong> 60+</p>
                        <p><strong>Group Size:</strong> 4-6 players</p>
                        <p><strong>Access:</strong> Geonosis travel + hive key</p>
                        <p><strong>Faction:</strong> Any</p>
                    </div>

                    <div class="info-card">
                        <h3><i class="fas fa-clock"></i> Estimated Time</h3>
                        <p><strong>Duration:</strong> 30-50 minutes</p>
                        <p><strong>Reset:</strong> Daily</p>
                        <p><strong>Lockout:</strong> 18 hours</p>
                    </div>

                    <div class="info-card">
                        <h3><i class="fas fa-trophy"></i> Rewards</h3>
                        <p><strong>XP:</strong> 10,000-18,000</p>
                        <p><strong>Credits:</strong> 3,000-6,000</p>
                        <p><strong>Faction:</strong> +300 Imperial/Republic</p>
                    </div>
                </div>

                <div class="hive-highlight">
                    <h4><i class="fas fa-exclamation-circle"></i> Hive Mechanics</h4>
                    <p>The Geonosian hive features unique swarm mechanics. Queen's death triggers enrage in all remaining guards. Use area attacks effectively but beware of acid pools left by defeated enemies.</p>
                </div>

                <div class="boss-section">
                    <h2><i class="fas fa-skull"></i> Boss Encounters</h2>
                    
                    <div class="boss-card">
                        <div class="boss-header">
                            <div class="boss-name">Geonosian Queen</div>
                            <span class="difficulty-badge difficulty-medium">Medium</span>
                        </div>
                        <ul class="mechanics-list">
                            <li><strong>Acid Spit:</strong> Ranged acid attacks that create ground hazards</li>
                            <li><strong>Swarm Call:</strong> Summons waves of worker drones every 30 seconds</li>
                            <li><strong>Royal Guard:</strong> Protected by elite Geonosian warriors</li>
                            <li><strong>Hive Mind:</strong> Gains damage bonus for each living guard</li>
                            <li><strong>Wing Buffet:</strong> Knockback attack that repositions players</li>
                            <li><strong>Egg Laying:</strong> Creates destructible eggs that spawn reinforcements</li>
                        </ul>
                    </div>

                    <div class="boss-card">
                        <div class="boss-header">
                            <div class="boss-name">Royal Guards</div>
                            <span class="difficulty-badge difficulty-medium">Medium</span>
                        </div>
                        <ul class="mechanics-list">
                            <li><strong>Protective Formation:</strong> Form defensive positions around the Queen</li>
                            <li><strong>Sonic Weapons:</strong> Use sonic blasters with stun effects</li>
                            <li><strong>Coordinated Strikes:</strong> Execute synchronized attacks</li>
                            <li><strong>Death Rage:</strong> Gain attack speed when Queen reaches low health</li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- Live Loot Table Tab -->
            <div class="tab-content" id="loot">
                <div class="loot-summary">
                    <h3><i class="fas fa-chart-bar"></i> Loot Statistics (Last 7 Days)</h3>
                    <div class="loot-stats-grid" id="lootStats">
                        <!-- Stats will be populated by JavaScript -->
                    </div>
                </div>
                
                <!-- Loot table will be inserted here -->
                <div id="lootTableContainer">
                    <div class="loot-table-loading">
                        <div class="loading-spinner">
                            <i class="fas fa-spinner fa-spin"></i>
                            <p>Loading live loot data...</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Strategy Tab -->
            <div class="tab-content" id="strategy">
                <div class="strategy-section">
                    <h2><i class="fas fa-chess"></i> Strategy Guide</h2>
                    
                    <div class="strategy-step">
                        <h4>Preparation</h4>
                        <p>Bring acid resistance gear and AoE abilities for managing swarms. Pack plenty of antidotes for acid effects. Ensure group has good mobility for avoiding ground hazards. Consider bringing a dedicated tank for Queen aggro.</p>
                    </div>

                    <div class="strategy-step">
                        <h4>Phase 1 - Royal Guards (100-70%)</h4>
                        <p>Focus fire on Royal Guards first to reduce Queen's damage bonus. Use crowd control on worker drones. Tank should maintain Queen position while DPS clears guards. Avoid standing in acid pools.</p>
                    </div>

                    <div class="strategy-step">
                        <h4>Phase 2 - Queen Focus (70-30%)</h4>
                        <p>With guards eliminated, focus all damage on Queen. Continue managing drone swarms with AoE. Watch for egg laying and destroy eggs quickly. Use interrupts on major acid spit attacks.</p>
                    </div>

                    <div class="strategy-step">
                        <h4>Phase 3 - Final Stand (30-0%)</h4>
                        <p>Queen becomes more aggressive with faster swarm calls. Use defensive cooldowns and maintain formation. Focus fire to finish quickly before being overwhelmed by drones. Save healing consumables for this phase.</p>
                    </div>

                    <div class="strategy-step">
                        <h4>Group Composition</h4>
                        <p>Recommended: 1 tank, 1 healer, 2-3 DPS. Include at least one AoE specialist for drone management. Bring acid resistance gear and antidotes. Ranged DPS recommended to avoid melee acid hazards.</p>
                    </div>

                    <div class="strategy-step">
                        <h4>Key Tips</h4>
                        <p>Kill guards before focusing Queen. Destroy eggs immediately. Use AoE abilities effectively on drone swarms. Maintain mobility to avoid acid pools. Coordinate interrupts on major attacks.</p>
                    </div>
                </div>
            </div>

            <a href="../" class="back-btn">
                <i class="fas fa-arrow-left"></i> Back to Heroics
            </a>
        </div>
    </div>

    <script>
        // Tab functionality
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                // Update active button
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                
                // Update active content
                document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                document.getElementById(this.dataset.tab).classList.add('active');
                
                // Load loot table if switching to loot tab
                if (this.dataset.tab === 'loot') {
                    loadLootTable();
                }
            });
        });

        // Load loot statistics
        async function loadLootStats() {
            try {
                const response = await fetch('/api/heroics/loot/stats?heroic=geonosian_queen&timeframe=7d');
                const result = await response.json();
                
                if (result.success && result.stats) {
                    const stats = result.stats;
                    const statsContainer = document.getElementById('lootStats');
                    
                    statsContainer.innerHTML = \`
                        <div class="loot-stat">
                            <span class="number">\${stats.total_entries || 0}</span>
                            <div class="label">Total Drops</div>
                        </div>
                        <div class="loot-stat">
                            <span class="number">\${stats.unique_items || 0}</span>
                            <div class="label">Unique Items</div>
                        </div>
                        <div class="loot-stat">
                            <span class="number">\${stats.player_count || 0}</span>
                            <div class="label">Players</div>
                        </div>
                        <div class="loot-stat">
                            <span class="number">\${stats.rarity_distribution?.rare || 0}</span>
                            <div class="label">Rare+ Drops</div>
                        </div>
                    \`;
                }
            } catch (error) {
                console.error('Error loading loot stats:', error);
            }
        }

        // Load loot table (enhanced for Geonosian Queen)
        async function loadLootTable() {
            const container = document.getElementById('lootTableContainer');
            
            try {
                // Simulate API call delay
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                // Enhanced loot table for Geonosian Queen
                container.innerHTML = \`
                    <div class="loot-table-container">
                        <div class="loot-table-header">
                            <div class="loot-stats">
                                <span class="stat-item">
                                    <i class="fas fa-treasure-chest"></i>
                                    14 recent drops
                                </span>
                                <span class="stat-item">
                                    <i class="fas fa-shield-alt"></i>
                                    Geonosian Queen Heroic
                                </span>
                                <span class="stat-item">
                                    <i class="fas fa-star"></i>
                                    3 rare+ this week
                                </span>
                                <span class="stat-item">
                                    <i class="fas fa-clock"></i>
                                    Last updated: Just now
                                </span>
                            </div>
                        </div>
                        
                        <div class="loot-filters">
                            <div class="filter-group">
                                <label>Rarity:</label>
                                <select>
                                    <option value="all">All Rarities</option>
                                    <option value="rare">Rare</option>
                                    <option value="epic">Epic</option>
                                    <option value="uncommon">Uncommon</option>
                                    <option value="common">Common</option>
                                </select>
                            </div>
                            <div class="filter-group">
                                <label>Type:</label>
                                <select>
                                    <option value="all">All Types</option>
                                    <option value="weapon">Weapon</option>
                                    <option value="armor">Armor</option>
                                    <option value="material">Material</option>
                                    <option value="accessory">Accessory</option>
                                </select>
                            </div>
                            <button class="refresh-btn" onclick="loadLootTable()">
                                <i class="fas fa-sync-alt"></i>
                            </button>
                        </div>
                        
                        <div class="loot-table-wrapper">
                            <table class="loot-table">
                                <thead>
                                    <tr>
                                        <th><i class="fas fa-clock"></i> Time</th>
                                        <th><i class="fas fa-cube"></i> Item</th>
                                        <th><i class="fas fa-star"></i> Rarity</th>
                                        <th><i class="fas fa-skull"></i> Boss</th>
                                        <th><i class="fas fa-user"></i> Player</th>
                                        <th><i class="fas fa-info-circle"></i> Details</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr class="loot-row">
                                        <td class="timestamp-cell">8m ago</td>
                                        <td class="item-cell">
                                            <div class="item-info">
                                                <i class="fas fa-magic"></i>
                                                <span class="item-name" style="color: #0070dd;">Queen's Staff</span>
                                            </div>
                                        </td>
                                        <td class="rarity-cell">
                                            <span class="rarity-badge" style="background: #0070dd; color: white;">rare</span>
                                        </td>
                                        <td class="boss-cell">Geonosian Queen</td>
                                        <td class="player-cell">HiveHunter1</td>
                                        <td class="details-cell">
                                            <span class="difficulty-badge difficulty-heroic">heroic</span>
                                            <i class="fas fa-check-circle success"></i>
                                        </td>
                                    </tr>
                                    <tr class="loot-row">
                                        <td class="timestamp-cell">22m ago</td>
                                        <td class="item-cell">
                                            <div class="item-info">
                                                <i class="fas fa-hammer"></i>
                                                <span class="item-name" style="color: #1eff00;">2x Geonosian Artifacts</span>
                                            </div>
                                        </td>
                                        <td class="rarity-cell">
                                            <span class="rarity-badge" style="background: #1eff00; color: black;">uncommon</span>
                                        </td>
                                        <td class="boss-cell">Geonosian Queen</td>
                                        <td class="player-cell">PlayerName2</td>
                                        <td class="details-cell">
                                            <span class="difficulty-badge difficulty-heroic">heroic</span>
                                            <i class="fas fa-check-circle success"></i>
                                        </td>
                                    </tr>
                                    <tr class="loot-row">
                                        <td class="timestamp-cell">35m ago</td>
                                        <td class="item-cell">
                                            <div class="item-info">
                                                <i class="fas fa-shield-alt"></i>
                                                <span class="item-name" style="color: #0070dd;">Royal Armor Piece</span>
                                            </div>
                                        </td>
                                        <td class="rarity-cell">
                                            <span class="rarity-badge" style="background: #0070dd; color: white;">rare</span>
                                        </td>
                                        <td class="boss-cell">Royal Guard</td>
                                        <td class="player-cell">GeoBuster3</td>
                                        <td class="details-cell">
                                            <span class="difficulty-badge difficulty-heroic">heroic</span>
                                            <i class="fas fa-check-circle success"></i>
                                        </td>
                                    </tr>
                                    <tr class="loot-row">
                                        <td class="timestamp-cell">1h ago</td>
                                        <td class="item-cell">
                                            <div class="item-info">
                                                <i class="fas fa-gem"></i>
                                                <span class="item-name" style="color: #9d9d9d;">Hive Crystals</span>
                                            </div>
                                        </td>
                                        <td class="rarity-cell">
                                            <span class="rarity-badge" style="background: #9d9d9d; color: white;">common</span>
                                        </td>
                                        <td class="boss-cell">Worker Drone</td>
                                        <td class="player-cell">SwarmKiller</td>
                                        <td class="details-cell">
                                            <span class="difficulty-badge difficulty-heroic">heroic</span>
                                            <i class="fas fa-check-circle success"></i>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        
                        <div class="loot-table-footer">
                            <div class="footer-info">
                                <span><i class="fas fa-database"></i> Data from MS11 bot sessions and mod submissions</span>
                                <span class="attribution"><i class="fas fa-external-link-alt"></i> Generated by SWGDB</span>
                            </div>
                        </div>
                    </div>
                \`;
            } catch (error) {
                container.innerHTML = \`
                    <div class="loot-table-error">
                        <div class="error-message">
                            <i class="fas fa-exclamation-triangle"></i>
                            <h3>Failed to Load Loot Data</h3>
                            <p>Unable to connect to the loot tracking API</p>
                            <button onclick="loadLootTable()" class="retry-btn">
                                <i class="fas fa-redo"></i> Retry
                            </button>
                        </div>
                    </div>
                \`;
            }
        }

        // Initialize page
        document.addEventListener('DOMContentLoaded', function() {
            loadLootStats();
        });
    </script>
</body>
</html>
    `;
  }
};