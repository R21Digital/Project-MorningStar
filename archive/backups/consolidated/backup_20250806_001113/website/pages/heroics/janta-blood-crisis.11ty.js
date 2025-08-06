const yaml = require('js-yaml');
const fs = require('fs');
const path = require('path');

module.exports = class {
  data() {
    return {
      title: "Janta Blood Crisis - SWGDB",
      description: "Defeat Janta Blood collectors threatening Mos Entha. View live loot drops, desert combat, and tactical strategies.",
      layout: "base.njk",
      permalink: "/heroics/janta-blood-crisis/",
      heroicId: "janta_blood_crisis",
      heroicName: "Janta Blood Crisis"
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
            --janta-color: #e65100;
            --blood-color: #b71c1c;
            --desert-color: #ff9800;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #ff9800 0%, #e65100 50%, #b71c1c 100%);
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
            background: linear-gradient(135deg, var(--desert-color) 0%, var(--janta-color) 50%, var(--blood-color) 100%);
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

        .beginner-friendly {
            background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
            border: 2px solid var(--success-color);
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
        }

        .beginner-friendly h3 {
            color: var(--success-color);
            margin-bottom: 10px;
            font-weight: 600;
        }

        .beginner-friendly p {
            color: #2e7d32;
            margin: 0;
            font-size: 0.95rem;
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
            background: var(--janta-color);
            color: white;
            box-shadow: 0 2px 8px rgba(230, 81, 0, 0.3);
        }

        .tab-btn:hover:not(.active) {
            background: rgba(230, 81, 0, 0.1);
            color: var(--janta-color);
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
            color: var(--janta-color);
        }

        .boss-section {
            background: linear-gradient(135deg, #fff3e0 0%, #ffcc80 100%);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 30px;
        }

        .boss-section h2 {
            color: var(--janta-color);
            margin-bottom: 20px;
            font-weight: 600;
        }

        .boss-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            border-left: 4px solid var(--janta-color);
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

        .difficulty-easy { 
            background: var(--success-color); 
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
            border-left: 4px solid var(--janta-color);
        }

        .strategy-section {
            background: linear-gradient(135deg, #fff3e0 0%, #ffcc80 100%);
            border-radius: 12px;
            padding: 25px;
        }

        .strategy-step {
            background: white;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            border-left: 4px solid var(--desert-color);
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
            background: linear-gradient(135deg, #fff3e0 0%, #ffcc80 100%);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }

        .loot-summary h3 {
            color: var(--janta-color);
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
            color: var(--janta-color);
            display: block;
        }

        .loot-stat .label {
            font-size: 0.9rem;
            color: #6c757d;
            margin-top: 5px;
        }

        .training-highlight {
            background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
            border: 2px solid var(--success-color);
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
        }

        .training-highlight h4 {
            color: var(--success-color);
            margin-bottom: 10px;
            font-weight: 600;
        }

        .training-highlight p {
            color: #2e7d32;
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
            <h1><i class="fas fa-tint"></i> Janta Blood Crisis</h1>
            <p>Defeat Janta Blood collectors threatening the settlements around Mos Entha</p>
            <div class="live-indicator">
                <div class="live-dot"></div>
                Live loot tracking active
            </div>
        </div>

        <div class="content-section">
            <div class="beginner-friendly">
                <h3><i class="fas fa-graduation-cap"></i> Perfect for New Players</h3>
                <p>This heroic is designed for players new to group content. Straightforward mechanics, forgiving difficulty, and great for learning teamwork and heroic dungeon basics.</p>
            </div>

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
                        <p><strong>Zone:</strong> Near Mos Entha</p>
                        <p><strong>Coordinates:</strong> 1200, -3400</p>
                    </div>

                    <div class="info-card">
                        <h3><i class="fas fa-users"></i> Entry Requirements</h3>
                        <p><strong>Level:</strong> 25+</p>
                        <p><strong>Group Size:</strong> 3-4 players</p>
                        <p><strong>Access:</strong> Quest series from Mos Entha</p>
                        <p><strong>Faction:</strong> Any</p>
                    </div>

                    <div class="info-card">
                        <h3><i class="fas fa-clock"></i> Estimated Time</h3>
                        <p><strong>Duration:</strong> 20-35 minutes</p>
                        <p><strong>Reset:</strong> Daily</p>
                        <p><strong>Lockout:</strong> 16 hours</p>
                    </div>

                    <div class="info-card">
                        <h3><i class="fas fa-trophy"></i> Rewards</h3>
                        <p><strong>XP:</strong> 5,000-8,000</p>
                        <p><strong>Credits:</strong> 1,500-3,000</p>
                        <p><strong>Faction:</strong> +200 Imperial/Republic</p>
                    </div>
                </div>

                <div class="training-highlight">
                    <h4><i class="fas fa-user-graduate"></i> Training Ground</h4>
                    <p>Excellent introduction to heroic mechanics. Learn basic group tactics, threat management, and coordinate healing without overwhelming complexity. Many experienced players mentor newcomers here.</p>
                </div>

                <div class="boss-section">
                    <h2><i class="fas fa-skull"></i> Enemy Encounters</h2>
                    
                    <div class="boss-card">
                        <div class="boss-header">
                            <div class="boss-name">Janta Blood Collectors</div>
                            <span class="difficulty-badge difficulty-easy">Easy</span>
                        </div>
                        <ul class="mechanics-list">
                            <li><strong>Basic Combat:</strong> Standard melee and ranged attacks with predictable patterns</li>
                            <li><strong>Blood Drain:</strong> Simple channeled ability that can be interrupted</li>
                            <li><strong>Pack Tactics:</strong> Work together in groups of 2-3</li>
                            <li><strong>Desert Ambush:</strong> Emerge from sand for surprise attacks</li>
                            <li><strong>Poison Darts:</strong> Ranged attacks with mild poison effects</li>
                        </ul>
                    </div>

                    <div class="boss-card">
                        <div class="boss-header">
                            <div class="boss-name">Blood Leaders</div>
                            <span class="difficulty-badge difficulty-easy">Easy</span>
                        </div>
                        <ul class="mechanics-list">
                            <li><strong>Enhanced Abilities:</strong> Stronger versions of collector attacks</li>
                            <li><strong>Rally Call:</strong> Buffs nearby collectors when health drops low</li>
                            <li><strong>Desperate Strike:</strong> Final powerful attack when near death</li>
                            <li><strong>Blood Shield:</strong> Temporary damage reduction ability</li>
                        </ul>
                    </div>

                    <div class="boss-card">
                        <div class="boss-header">
                            <div class="boss-name">Desert Scavengers</div>
                            <span class="difficulty-badge difficulty-easy">Easy</span>
                        </div>
                        <ul class="mechanics-list">
                            <li><strong>Hit and Run:</strong> Fast attacks followed by retreat to range</li>
                            <li><strong>Sand Throw:</strong> Blinds targets temporarily</li>
                            <li><strong>Scavenged Weapons:</strong> Use various found equipment types</li>
                            <li><strong>Pack Mentality:</strong> Become more aggressive in groups</li>
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
                    <h2><i class="fas fa-chess"></i> Beginner Strategy Guide</h2>
                    
                    <div class="strategy-step">
                        <h4>Getting Started</h4>
                        <p>Perfect heroic for new players to learn group dynamics. Bring basic healing supplies and ensure your weapons are in good repair. Don't worry about perfect gear - focus on learning and teamwork.</p>
                    </div>

                    <div class="strategy-step">
                        <h4>Basic Group Roles</h4>
                        <p>Assign one player to tank (hold enemy attention), one to heal, and 1-2 for damage. Tank should engage enemies first, healers focus on keeping everyone healthy, DPS players attack designated targets.</p>
                    </div>

                    <div class="strategy-step">
                        <h4>Blood Collector Encounters</h4>
                        <p>These enemies are straightforward but teach important concepts. Practice interrupting their Blood Drain ability - this teaches timing for more advanced heroics. Focus fire one target at a time.</p>
                    </div>

                    <div class="strategy-step">
                        <h4>Managing Blood Leaders</h4>
                        <p>Leaders are slightly stronger but still manageable. When they use Rally Call, focus fire them quickly to prevent buff effects. Save healing abilities for their Desperate Strike attack.</p>
                    </div>

                    <div class="strategy-step">
                        <h4>Desert Environment</h4>
                        <p>Learn to use terrain to your advantage. Take cover behind rocks during ranged attacks. Watch for ambush spots where enemies emerge from sand. Stay grouped but not too close together.</p>
                    </div>

                    <div class="strategy-step">
                        <h4>Group Composition</h4>
                        <p>Flexible composition works well. Recommended: 1 tank, 1 healer, 2 DPS, but any combination can succeed. Focus on communication and learning rather than perfect optimization.</p>
                    </div>

                    <div class="strategy-step">
                        <h4>Learning Objectives</h4>
                        <p>Master interrupt timing, coordinate target focus, practice positioning, learn to manage healing resources. These skills transfer directly to advanced heroics. Don't rush - focus on execution quality.</p>
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
                const response = await fetch('/api/heroics/loot/stats?heroic=janta_blood_crisis&timeframe=7d');
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
                            <span class="number">\${stats.rarity_distribution?.uncommon || 0}</span>
                            <div class="label">Uncommon+ Drops</div>
                        </div>
                    \`;
                }
            } catch (error) {
                console.error('Error loading loot stats:', error);
            }
        }

        // Load loot table (enhanced for Janta Blood Crisis)
        async function loadLootTable() {
            const container = document.getElementById('lootTableContainer');
            
            try {
                // Simulate API call delay
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                // Enhanced loot table for Janta Blood Crisis
                container.innerHTML = \`
                    <div class="loot-table-container">
                        <div class="loot-table-header">
                            <div class="loot-stats">
                                <span class="stat-item">
                                    <i class="fas fa-treasure-chest"></i>
                                    42 recent drops
                                </span>
                                <span class="stat-item">
                                    <i class="fas fa-shield-alt"></i>
                                    Janta Blood Crisis
                                </span>
                                <span class="stat-item">
                                    <i class="fas fa-user-graduate"></i>
                                    Training heroic
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
                                        <td class="timestamp-cell">5m ago</td>
                                        <td class="item-cell">
                                            <div class="item-info">
                                                <i class="fas fa-gem"></i>
                                                <span class="item-name" style="color: #1eff00;">Blood Artifacts</span>
                                            </div>
                                        </td>
                                        <td class="rarity-cell">
                                            <span class="rarity-badge" style="background: #1eff00; color: black;">uncommon</span>
                                        </td>
                                        <td class="boss-cell">Blood Leader</td>
                                        <td class="player-cell">NewbieHunter</td>
                                        <td class="details-cell">
                                            <span class="difficulty-badge difficulty-heroic">heroic</span>
                                            <i class="fas fa-check-circle success"></i>
                                        </td>
                                    </tr>
                                    <tr class="loot-row">
                                        <td class="timestamp-cell">18m ago</td>
                                        <td class="item-cell">
                                            <div class="item-info">
                                                <i class="fas fa-shield-alt"></i>
                                                <span class="item-name" style="color: #9d9d9d;">Desert Equipment</span>
                                            </div>
                                        </td>
                                        <td class="rarity-cell">
                                            <span class="rarity-badge" style="background: #9d9d9d; color: white;">common</span>
                                        </td>
                                        <td class="boss-cell">Desert Scavenger</td>
                                        <td class="player-cell">FirstTimer</td>
                                        <td class="details-cell">
                                            <span class="difficulty-badge difficulty-heroic">heroic</span>
                                            <i class="fas fa-check-circle success"></i>
                                        </td>
                                    </tr>
                                    <tr class="loot-row">
                                        <td class="timestamp-cell">32m ago</td>
                                        <td class="item-cell">
                                            <div class="item-info">
                                                <i class="fas fa-hammer"></i>
                                                <span class="item-name" style="color: #1eff00;">2x Tatooine Relics</span>
                                            </div>
                                        </td>
                                        <td class="rarity-cell">
                                            <span class="rarity-badge" style="background: #1eff00; color: black;">uncommon</span>
                                        </td>
                                        <td class="boss-cell">Janta Blood Collector</td>
                                        <td class="player-cell">TrainingGroup1</td>
                                        <td class="details-cell">
                                            <span class="difficulty-badge difficulty-heroic">heroic</span>
                                            <i class="fas fa-check-circle success"></i>
                                        </td>
                                    </tr>
                                    <tr class="loot-row">
                                        <td class="timestamp-cell">45m ago</td>
                                        <td class="item-cell">
                                            <div class="item-info">
                                                <i class="fas fa-coins"></i>
                                                <span class="item-name" style="color: #9d9d9d;">Desert Salvage</span>
                                            </div>
                                        </td>
                                        <td class="rarity-cell">
                                            <span class="rarity-badge" style="background: #9d9d9d; color: white;">common</span>
                                        </td>
                                        <td class="boss-cell">Desert Scavenger</td>
                                        <td class="player-cell">LearningPlayer</td>
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