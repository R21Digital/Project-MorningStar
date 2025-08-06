const yaml = require('js-yaml');
const fs = require('fs');
const path = require('path');

module.exports = class {
  data() {
    return {
      title: "IG-88 Heroic - SWGDB",
      description: "Fight the infamous bounty hunter droid IG-88 in his lair. View live loot drops, strategies, and boss mechanics.",
      layout: "base.njk",
      permalink: "/heroics/ig-88/",
      heroicId: "ig_88",
      heroicName: "IG-88"
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
            --ig88-color: #ff6b35;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }

        .main-container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            margin: 20px auto;
            max-width: 1400px;
            overflow: hidden;
        }

        .header-section {
            background: linear-gradient(135deg, var(--ig88-color) 0%, #e55100 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header-section h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
        }

        .header-section p {
            font-size: 1.1rem;
            opacity: 0.9;
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
            background: var(--ig88-color);
            color: white;
            box-shadow: 0 2px 8px rgba(255, 107, 53, 0.3);
        }

        .tab-btn:hover:not(.active) {
            background: rgba(255, 107, 53, 0.1);
            color: var(--ig88-color);
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
            color: var(--ig88-color);
        }

        .boss-section {
            background: linear-gradient(135deg, #fff3e0 0%, #ffcc80 100%);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 30px;
        }

        .boss-section h2 {
            color: #e65100;
            margin-bottom: 20px;
            font-weight: 600;
        }

        .boss-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
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

        .difficulty-hard { 
            background: var(--danger-color); 
            color: white; 
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
            border-left: 4px solid var(--ig88-color);
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
            background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }

        .loot-summary h3 {
            color: #6a1b9a;
            margin-bottom: 15px;
        }

        .loot-stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }

        .loot-stat {
            background: rgba(255, 255, 255, 0.7);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }

        .loot-stat .number {
            font-size: 1.8rem;
            font-weight: 700;
            color: #6a1b9a;
            display: block;
        }

        .loot-stat .label {
            font-size: 0.9rem;
            color: #6c757d;
            margin-top: 5px;
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
            <h1><i class="fas fa-robot"></i> IG-88</h1>
            <p>Face the infamous bounty hunter droid in his Tatooine lair</p>
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
                        <p><strong>Planet:</strong> Tatooine</p>
                        <p><strong>Zone:</strong> IG-88's Lair</p>
                        <p><strong>Coordinates:</strong> -6200, 2700</p>
                    </div>

                    <div class="info-card">
                        <h3><i class="fas fa-users"></i> Entry Requirements</h3>
                        <p><strong>Level:</strong> 70+</p>
                        <p><strong>Group Size:</strong> 4-6 players</p>
                        <p><strong>Access:</strong> Quest series completion</p>
                        <p><strong>Faction:</strong> Any</p>
                    </div>

                    <div class="info-card">
                        <h3><i class="fas fa-clock"></i> Estimated Time</h3>
                        <p><strong>Duration:</strong> 45-75 minutes</p>
                        <p><strong>Reset:</strong> Daily</p>
                        <p><strong>Lockout:</strong> 20 hours</p>
                    </div>

                    <div class="info-card">
                        <h3><i class="fas fa-trophy"></i> Rewards</h3>
                        <p><strong>XP:</strong> 15,000-25,000</p>
                        <p><strong>Credits:</strong> 5,000-8,000</p>
                        <p><strong>Faction:</strong> +500 Imperial/Republic</p>
                    </div>
                </div>

                <div class="boss-section">
                    <h2><i class="fas fa-skull"></i> Boss Encounters</h2>
                    
                    <div class="boss-card">
                        <div class="boss-header">
                            <div class="boss-name">IG-88</div>
                            <span class="difficulty-badge difficulty-hard">Hard</span>
                        </div>
                        <ul class="mechanics-list">
                            <li><strong>Precise Targeting:</strong> IG-88 has extremely high accuracy and critical hit chance</li>
                            <li><strong>Weapon Systems:</strong> Switches between rifle, flamethrower, and rocket launcher</li>
                            <li><strong>Droid Reinforcements:</strong> Calls in security droids every 25% health</li>
                            <li><strong>System Overload:</strong> At low health, gains increased attack speed and damage</li>
                            <li><strong>Area Denial:</strong> Creates hazardous zones with explosives and fire</li>
                            <li><strong>Combat Protocols:</strong> Adapts tactics based on group composition</li>
                        </ul>
                    </div>

                    <div class="boss-card">
                        <div class="boss-header">
                            <div class="boss-name">Security Droids</div>
                            <span class="difficulty-badge difficulty-hard">Hard</span>
                        </div>
                        <ul class="mechanics-list">
                            <li><strong>Shield Generators:</strong> Droids create protective barriers</li>
                            <li><strong>Coordinated Attacks:</strong> Work together with synchronized abilities</li>
                            <li><strong>Self-Destruct:</strong> Explode when destroyed, dealing AoE damage</li>
                            <li><strong>Electronic Warfare:</strong> Can disable player equipment temporarily</li>
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
                        <p>Bring ranged DPS and crowd control abilities. IG-88 is vulnerable to ion damage and electronic warfare. Ensure your group has good mobility for avoiding area attacks. Stock up on healing supplies and equipment repair kits.</p>
                    </div>

                    <div class="strategy-step">
                        <h4>Phase 1 - Initial Engagement (100-75%)</h4>
                        <p>Start with careful positioning at maximum range. Tank should maintain threat while avoiding direct line of sight during weapon swaps. Focus fire on IG-88 while managing the first wave of security droids.</p>
                    </div>

                    <div class="strategy-step">
                        <h4>Phase 2 - Droid Reinforcements (75-50%)</h4>
                        <p>Priority target the shield generator droids first, then focus on the combat units. Use AoE abilities carefully to avoid triggering multiple self-destructs. Maintain spread formation to minimize explosive damage.</p>
                    </div>

                    <div class="strategy-step">
                        <h4>Phase 3 - System Overload (50-25%)</h4>
                        <p>IG-88 becomes more aggressive and calls reinforcements more frequently. Use defensive cooldowns and crowd control to manage the increased threat. Focus on survival while maintaining steady DPS.</p>
                    </div>

                    <div class="strategy-step">
                        <h4>Final Phase - Critical Systems (25-0%)</h4>
                        <p>IG-88 enters berserker mode with maximum attack speed. Use all remaining defensive abilities and healing consumables. Coordinate burst damage to finish quickly before the group is overwhelmed.</p>
                    </div>

                    <div class="strategy-step">
                        <h4>Group Composition</h4>
                        <p>Recommended: 1 tank, 2 healers, 2-3 DPS. Include at least one ranged DPS for safe positioning. Bring crowd control abilities for managing droid adds. Ion weapons and electronic warfare specialists are highly effective.</p>
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
                const response = await fetch('/api/heroics/loot/stats?heroic=ig_88&timeframe=7d');
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
                            <span class="number">\${Object.keys(stats.rarity_distribution || {}).length}</span>
                            <div class="label">Rarity Types</div>
                        </div>
                    \`;
                }
            } catch (error) {
                console.error('Error loading loot stats:', error);
            }
        }

        // Load loot table (simulated for demo)
        async function loadLootTable() {
            const container = document.getElementById('lootTableContainer');
            
            try {
                // Simulate API call delay
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                // For demo purposes, create a mock loot table
                container.innerHTML = \`
                    <div class="loot-table-container">
                        <div class="loot-table-header">
                            <div class="loot-stats">
                                <span class="stat-item">
                                    <i class="fas fa-treasure-chest"></i>
                                    24 recent drops
                                </span>
                                <span class="stat-item">
                                    <i class="fas fa-shield-alt"></i>
                                    IG-88 Heroic
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
                                    <option value="legendary">Legendary</option>
                                    <option value="epic">Epic</option>
                                    <option value="rare">Rare</option>
                                    <option value="uncommon">Uncommon</option>
                                </select>
                            </div>
                            <div class="filter-group">
                                <label>Type:</label>
                                <select>
                                    <option value="all">All Types</option>
                                    <option value="weapon">Weapon</option>
                                    <option value="armor">Armor</option>
                                    <option value="material">Material</option>
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
                                        <td class="timestamp-cell">2m ago</td>
                                        <td class="item-cell">
                                            <div class="item-info">
                                                <i class="fas fa-sword"></i>
                                                <span class="item-name" style="color: #ff8000;">IG-88's Rifle</span>
                                            </div>
                                        </td>
                                        <td class="rarity-cell">
                                            <span class="rarity-badge" style="background: #ff8000; color: white;">legendary</span>
                                        </td>
                                        <td class="boss-cell">IG-88</td>
                                        <td class="player-cell">PlayerName1</td>
                                        <td class="details-cell">
                                            <span class="difficulty-badge difficulty-heroic">heroic</span>
                                            <i class="fas fa-check-circle success"></i>
                                        </td>
                                    </tr>
                                    <tr class="loot-row">
                                        <td class="timestamp-cell">15m ago</td>
                                        <td class="item-cell">
                                            <div class="item-info">
                                                <i class="fas fa-hammer"></i>
                                                <span class="item-name" style="color: #a335ee;">Advanced Droid Parts</span>
                                            </div>
                                        </td>
                                        <td class="rarity-cell">
                                            <span class="rarity-badge" style="background: #a335ee; color: white;">epic</span>
                                        </td>
                                        <td class="boss-cell">IG-88</td>
                                        <td class="player-cell">PlayerName2</td>
                                        <td class="details-cell">
                                            <span class="difficulty-badge difficulty-heroic">heroic</span>
                                            <i class="fas fa-check-circle success"></i>
                                        </td>
                                    </tr>
                                    <tr class="loot-row">
                                        <td class="timestamp-cell">32m ago</td>
                                        <td class="item-cell">
                                            <div class="item-info">
                                                <i class="fas fa-shield-alt"></i>
                                                <span class="item-name" style="color: #0070dd;">Targeting Computer</span>
                                            </div>
                                        </td>
                                        <td class="rarity-cell">
                                            <span class="rarity-badge" style="background: #0070dd; color: white;">rare</span>
                                        </td>
                                        <td class="boss-cell">Security Droid</td>
                                        <td class="player-cell">PlayerName3</td>
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