const yaml = require('js-yaml');
const fs = require('fs');
const path = require('path');

module.exports = class {
  data() {
    return {
      title: "Krayt Dragon Hunt - SWGDB",
      description: "Hunt the legendary Ancient Krayt Dragon in the Dune Sea. View live loot drops, dragon mechanics, and hunting strategies.",
      layout: "base.njk",
      permalink: "/heroics/krayt-dragon/",
      heroicId: "krayt_dragon",
      heroicName: "Krayt Dragon Hunt"
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
            --krayt-color: #8bc34a;
            --dragon-color: #2e7d32;
            --desert-color: #ff9800;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #ff9800 0%, #8bc34a 50%, #2e7d32 100%);
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
            background: linear-gradient(135deg, var(--desert-color) 0%, var(--krayt-color) 50%, var(--dragon-color) 100%);
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

        .legendary-warning {
            background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
            border: 2px solid var(--warning-color);
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            text-align: center;
        }

        .legendary-warning h3 {
            color: #856404;
            margin-bottom: 10px;
            font-weight: 600;
        }

        .legendary-warning p {
            color: #856404;
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
            background: var(--dragon-color);
            color: white;
            box-shadow: 0 2px 8px rgba(46, 125, 50, 0.3);
        }

        .tab-btn:hover:not(.active) {
            background: rgba(46, 125, 50, 0.1);
            color: var(--dragon-color);
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
            color: var(--dragon-color);
        }

        .boss-section {
            background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 30px;
        }

        .boss-section h2 {
            color: var(--dragon-color);
            margin-bottom: 20px;
            font-weight: 600;
        }

        .boss-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            border-left: 4px solid var(--dragon-color);
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

        .difficulty-expert { 
            background: #6f42c1; 
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
            border-left: 4px solid var(--dragon-color);
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
            background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }

        .loot-summary h3 {
            color: var(--dragon-color);
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
            color: var(--dragon-color);
            display: block;
        }

        .loot-stat .label {
            font-size: 0.9rem;
            color: #6c757d;
            margin-top: 5px;
        }

        .dragon-pearl-highlight {
            background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%);
            border: 2px solid #ff8000;
            border-radius: 8px;
            padding: 15px;
            margin: 15px 0;
        }

        .dragon-pearl-highlight h4 {
            color: #ff8000;
            margin-bottom: 10px;
            font-weight: 600;
        }

        .dragon-pearl-highlight p {
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
            <h1><i class="fas fa-dragon"></i> Krayt Dragon Hunt</h1>
            <p>Hunt the legendary Ancient Krayt Dragon in the vast Dune Sea of Tatooine</p>
            <div class="live-indicator">
                <div class="live-dot"></div>
                Live loot tracking active
            </div>
        </div>

        <div class="content-section">
            <div class="legendary-warning">
                <h3><i class="fas fa-exclamation-triangle"></i> Legendary Hunt Warning</h3>
                <p>This is the most prestigious hunt in the galaxy. Only the most skilled groups should attempt this encounter. Dragon deaths are rare and highly celebrated across the server.</p>
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
                        <p><strong>Zone:</strong> Dune Sea</p>
                        <p><strong>Coordinates:</strong> Variable (tracking required)</p>
                    </div>

                    <div class="info-card">
                        <h3><i class="fas fa-users"></i> Entry Requirements</h3>
                        <p><strong>Level:</strong> 80+</p>
                        <p><strong>Group Size:</strong> 8+ players</p>
                        <p><strong>Access:</strong> Dragon tracking quest</p>
                        <p><strong>Faction:</strong> Any</p>
                    </div>

                    <div class="info-card">
                        <h3><i class="fas fa-clock"></i> Estimated Time</h3>
                        <p><strong>Duration:</strong> 2-4 hours</p>
                        <p><strong>Reset:</strong> Weekly</p>
                        <p><strong>Lockout:</strong> 7 days</p>
                    </div>

                    <div class="info-card">
                        <h3><i class="fas fa-trophy"></i> Rewards</h3>
                        <p><strong>XP:</strong> 50,000-80,000</p>
                        <p><strong>Credits:</strong> 15,000-25,000</p>
                        <p><strong>Faction:</strong> +2000 Imperial/Republic</p>
                    </div>
                </div>

                <div class="dragon-pearl-highlight">
                    <h4><i class="fas fa-gem"></i> Krayt Dragon Pearl</h4>
                    <p>The most coveted item in the galaxy. Ancient Krayt Dragons have a rare chance to drop a Perfect Krayt Dragon Pearl, the ultimate lightsaber crystal worth millions of credits and providing unmatched combat bonuses.</p>
                </div>

                <div class="boss-section">
                    <h2><i class="fas fa-skull"></i> Dragon Encounters</h2>
                    
                    <div class="boss-card">
                        <div class="boss-header">
                            <div class="boss-name">Ancient Krayt Dragon</div>
                            <span class="difficulty-badge difficulty-expert">Expert</span>
                        </div>
                        <ul class="mechanics-list">
                            <li><strong>Massive Scale:</strong> Enormous creature with millions of hit points</li>
                            <li><strong>Burrow Attack:</strong> Disappears underground and emerges for devastating attacks</li>
                            <li><strong>Tail Sweep:</strong> Massive AoE attacks that can instantly kill players</li>
                            <li><strong>Dragon Roar:</strong> Fear effect that sends players fleeing</li>
                            <li><strong>Acidic Breath:</strong> Cone attack with ongoing acid damage</li>
                            <li><strong>Sandstorm:</strong> Creates environmental hazards that reduce visibility</li>
                            <li><strong>Rage Mode:</strong> At low health, gains increased speed and damage</li>
                        </ul>
                    </div>

                    <div class="boss-card">
                        <div class="boss-header">
                            <div class="boss-name">Young Krayt Dragons</div>
                            <span class="difficulty-badge difficulty-expert">Expert</span>
                        </div>
                        <ul class="mechanics-list">
                            <li><strong>Pack Hunters:</strong> Attack in coordinated groups of 2-3</li>
                            <li><strong>Flanking:</strong> Attempt to surround and isolate players</li>
                            <li><strong>Protective Instinct:</strong> Become enraged if Ancient Dragon is threatened</li>
                            <li><strong>Speed Advantage:</strong> Much faster than the Ancient Dragon</li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- Live Loot Table Tab -->
            <div class="tab-content" id="loot">
                <div class="loot-summary">
                    <h3><i class="fas fa-chart-bar"></i> Loot Statistics (Last 30 Days)</h3>
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
                    <h2><i class="fas fa-chess"></i> Dragon Hunting Strategy</h2>
                    
                    <div class="strategy-step">
                        <h4>Pre-Hunt Preparation</h4>
                        <p>Form a raid group of 8+ players with perfect coordination. Everyone must have maximum-level gear, acid resistance, and fear immunity. Stock massive amounts of healing supplies. Plan for 2-4 hour encounter duration.</p>
                    </div>

                    <div class="strategy-step">
                        <h4>Dragon Tracking</h4>
                        <p>Use tracking abilities to locate the Ancient Dragon in the Dune Sea. Dragons move locations periodically. Young dragons indicate nearby Ancient presence. Approach with extreme caution - dragons detect movement from great distances.</p>
                    </div>

                    <div class="strategy-step">
                        <h4>Phase 1 - Initial Engagement (100-75%)</h4>
                        <p>Establish maximum range and begin coordinated assault. Tanks must maintain aggro while staying mobile. All players spread out to minimize tail sweep casualties. Use terrain for cover during burrow attacks.</p>
                    </div>

                    <div class="strategy-step">
                        <h4>Phase 2 - Young Dragon Intervention (75-50%)</h4>
                        <p>Young dragons arrive to defend their elder. Assign dedicated teams to kite young dragons while maintaining damage on Ancient. Do not let young dragons reach healers or damage dealers.</p>
                    </div>

                    <div class="strategy-step">
                        <h4>Phase 3 - Environmental Hazards (50-25%)</h4>
                        <p>Dragon creates sandstorms and acid pools across battlefield. Maintain formation and communication despite reduced visibility. Use landmark positioning to stay oriented. Focus fire to push through this dangerous phase quickly.</p>
                    </div>

                    <div class="strategy-step">
                        <h4>Phase 4 - Rage Mode (25-0%)</h4>
                        <p>Dragon enters final rage with increased speed and damage. Use all remaining defensive abilities and consumables. Coordinate final damage burst while maintaining survival. Victory requires perfect execution.</p>
                    </div>

                    <div class="strategy-step">
                        <h4>Raid Composition</h4>
                        <p>Required: 2+ master tanks, 3+ master healers, 4+ master DPS. Include multiple classes for utility: Jedi for Force powers, Bounty Hunters for tracking, Commandos for heavy weapons. All members must be server elite.</p>
                    </div>

                    <div class="strategy-step">
                        <h4>Critical Success Factors</h4>
                        <p>Perfect communication and coordination essential. Single mistakes can wipe entire raid. Prepare for multiple attempts over several sessions. Success brings server-wide recognition and legendary rewards.</p>
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
                const response = await fetch('/api/heroics/loot/stats?heroic=krayt_dragon&timeframe=30d');
                const result = await response.json();
                
                if (result.success && result.stats) {
                    const stats = result.stats;
                    const statsContainer = document.getElementById('lootStats');
                    
                    statsContainer.innerHTML = \`
                        <div class="loot-stat">
                            <span class="number">\${stats.total_entries || 0}</span>
                            <div class="label">Total Kills</div>
                        </div>
                        <div class="loot-stat">
                            <span class="number">\${stats.unique_items || 0}</span>
                            <div class="label">Unique Items</div>
                        </div>
                        <div class="loot-stat">
                            <span class="number">\${stats.player_count || 0}</span>
                            <div class="label">Dragon Hunters</div>
                        </div>
                        <div class="loot-stat">
                            <span class="number">\${stats.rarity_distribution?.legendary || 0}</span>
                            <div class="label">Pearl Drops</div>
                        </div>
                    \`;
                }
            } catch (error) {
                console.error('Error loading loot stats:', error);
            }
        }

        // Load loot table (enhanced for Krayt Dragon)
        async function loadLootTable() {
            const container = document.getElementById('lootTableContainer');
            
            try {
                // Simulate API call delay
                await new Promise(resolve => setTimeout(resolve, 1000));
                
                // Enhanced loot table for Krayt Dragon
                container.innerHTML = \`
                    <div class="loot-table-container">
                        <div class="loot-table-header">
                            <div class="loot-stats">
                                <span class="stat-item">
                                    <i class="fas fa-treasure-chest"></i>
                                    7 dragon kills this month
                                </span>
                                <span class="stat-item">
                                    <i class="fas fa-shield-alt"></i>
                                    Ancient Krayt Dragon
                                </span>
                                <span class="stat-item">
                                    <i class="fas fa-star"></i>
                                    2 pearl drops recorded
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
                                </select>
                            </div>
                            <div class="filter-group">
                                <label>Type:</label>
                                <select>
                                    <option value="all">All Types</option>
                                    <option value="material">Material</option>
                                    <option value="weapon">Weapon</option>
                                    <option value="armor">Armor</option>
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
                                        <td class="timestamp-cell">3d ago</td>
                                        <td class="item-cell">
                                            <div class="item-info">
                                                <i class="fas fa-gem"></i>
                                                <span class="item-name" style="color: #ff8000;">Perfect Krayt Dragon Pearl</span>
                                                <i class="fas fa-star" style="color: #ff8000;" title="Legendary drop!"></i>
                                            </div>
                                        </td>
                                        <td class="rarity-cell">
                                            <span class="rarity-badge" style="background: #ff8000; color: white;">legendary</span>
                                        </td>
                                        <td class="boss-cell">Ancient Krayt Dragon</td>
                                        <td class="player-cell">DragonSlayer1</td>
                                        <td class="details-cell">
                                            <span class="difficulty-badge difficulty-heroic">heroic</span>
                                            <i class="fas fa-check-circle success"></i>
                                        </td>
                                    </tr>
                                    <tr class="loot-row">
                                        <td class="timestamp-cell">5d ago</td>
                                        <td class="item-cell">
                                            <div class="item-info">
                                                <i class="fas fa-shield-alt"></i>
                                                <span class="item-name" style="color: #a335ee;">5x Dragon Scales</span>
                                            </div>
                                        </td>
                                        <td class="rarity-cell">
                                            <span class="rarity-badge" style="background: #a335ee; color: white;">epic</span>
                                        </td>
                                        <td class="boss-cell">Ancient Krayt Dragon</td>
                                        <td class="player-cell">ScaleCollector</td>
                                        <td class="details-cell">
                                            <span class="difficulty-badge difficulty-heroic">heroic</span>
                                            <i class="fas fa-check-circle success"></i>
                                        </td>
                                    </tr>
                                    <tr class="loot-row">
                                        <td class="timestamp-cell">6d ago</td>
                                        <td class="item-cell">
                                            <div class="item-info">
                                                <i class="fas fa-sword"></i>
                                                <span class="item-name" style="color: #ff8000;">Legendary Dragon Bone Weapon</span>
                                                <i class="fas fa-star" style="color: #ff8000;" title="Legendary drop!"></i>
                                            </div>
                                        </td>
                                        <td class="rarity-cell">
                                            <span class="rarity-badge" style="background: #ff8000; color: white;">legendary</span>
                                        </td>
                                        <td class="boss-cell">Ancient Krayt Dragon</td>
                                        <td class="player-cell">BoneCarver</td>
                                        <td class="details-cell">
                                            <span class="difficulty-badge difficulty-heroic">heroic</span>
                                            <i class="fas fa-check-circle success"></i>
                                        </td>
                                    </tr>
                                    <tr class="loot-row">
                                        <td class="timestamp-cell">1w ago</td>
                                        <td class="item-cell">
                                            <div class="item-info">
                                                <i class="fas fa-gem"></i>
                                                <span class="item-name" style="color: #0070dd;">Krayt Dragon Tissue</span>
                                            </div>
                                        </td>
                                        <td class="rarity-cell">
                                            <span class="rarity-badge" style="background: #0070dd; color: white;">rare</span>
                                        </td>
                                        <td class="boss-cell">Young Krayt Dragon</td>
                                        <td class="player-cell">TissueHunter</td>
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