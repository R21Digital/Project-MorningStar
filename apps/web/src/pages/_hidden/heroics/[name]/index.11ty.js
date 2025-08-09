const yaml = require('js-yaml');
const fs = require('fs');
const path = require('path');

module.exports = class {
  data() {
    return {
      // Enable pagination for dynamic routes
      pagination: {
        data: 'heroics',
        size: 1,
        alias: 'heroic',
        generatePageOnEmptyData: false
      },
      
      // Computed data for heroics
      eleventyComputed: {
        heroics: () => {
          try {
            // Load heroics index
            const indexPath = path.join(__dirname, '../../../data/heroics/heroics_index.yml');
            const indexContent = fs.readFileSync(indexPath, 'utf8');
            const indexData = yaml.load(indexContent);
            
            // Convert heroics object to array for pagination
            return Object.entries(indexData.heroics || {}).map(([id, data]) => ({
              id,
              ...data
            }));
          } catch (error) {
            console.error('Error loading heroics index:', error);
            return [];
          }
        },
        
        heroicData: (data) => {
          try {
            const heroicId = data.heroic?.id;
            if (!heroicId) return null;
            
            // Load individual heroic data file
            const heroicPath = path.join(__dirname, `../../../data/heroics/${heroicId}.yml`);
            if (fs.existsSync(heroicPath)) {
              const fileContents = fs.readFileSync(heroicPath, 'utf8');
              return yaml.load(fileContents);
            }
            
            return null;
          } catch (error) {
            console.error(`Error loading heroic data for ${data.heroic?.id}:`, error);
            return null;
          }
        },
        
        mapData: (data) => {
          try {
            const heroicId = data.heroic?.id;
            if (!heroicId) return null;
            
            // Load map data if exists
            const mapPath = path.join(__dirname, `../../../data/maps/${heroicId}.json`);
            if (fs.existsSync(mapPath)) {
              const fileContents = fs.readFileSync(mapPath, 'utf8');
              return JSON.parse(fileContents);
            }
            
            return null;
          } catch (error) {
            console.error(`Error loading map data for ${data.heroic?.id}:`, error);
            return null;
          }
        },
        
        lootTables: (data) => {
          try {
            const heroicId = data.heroic?.id;
            if (!heroicId) return null;
            
            // Load loot table data
            const lootPath = path.join(__dirname, `../../../data/loot_tables/${heroicId}.json`);
            if (fs.existsSync(lootPath)) {
              const fileContents = fs.readFileSync(lootPath, 'utf8');
              return JSON.parse(fileContents);
            }
            
            return null;
          } catch (error) {
            console.error(`Error loading loot data for ${data.heroic?.id}:`, error);
            return null;
          }
        }
      },
      
      // Permalink pattern for dynamic routes
      permalink: (data) => {
        return `/heroics/${data.heroic.id}/`;
      },
      
      // Page metadata
      title: (data) => `${data.heroic?.name || 'Heroic'} - Complete Guide`,
      description: (data) => `Complete guide for ${data.heroic?.name || 'heroic instance'} including tactics, maps, loot tables, and boss strategies.`,
      layout: 'base.11ty.js'
    };
  }

  render(data) {
    const { heroic, heroicData, mapData, lootTables } = data;
    
    if (!heroic || !heroicData) {
      return '<div class="error">Heroic data not found</div>';
    }

    // Generate boss phase navigation
    const bossPhases = heroicData.encounters?.map(encounter => ({
      id: encounter.boss_id,
      name: encounter.boss_name,
      phase: encounter.phase || 1,
      difficulty: encounter.difficulty || 'normal'
    })) || [];

    // Generate loot summary
    const lootSummary = lootTables ? {
      totalItems: Object.keys(lootTables.drops || {}).length,
      rareItems: Object.values(lootTables.drops || {}).filter(item => 
        item.rarity === 'legendary' || item.rarity === 'epic').length,
      categories: [...new Set(Object.values(lootTables.drops || {}).map(item => item.category))]
    } : null;

    return `
      <div class="heroic-guide-container" data-heroic-id="${heroic.id}">
        <!-- Header Section -->
        <header class="heroic-header">
          <div class="heroic-header-content">
            <div class="heroic-title-section">
              <h1 class="heroic-title">${heroic.name}</h1>
              <div class="heroic-subtitle">
                <span class="planet-badge">${heroic.planet.charAt(0).toUpperCase() + heroic.planet.slice(1)}</span>
                <span class="location-badge">${heroic.location}</span>
              </div>
            </div>
            
            <div class="heroic-meta">
              <div class="meta-item">
                <strong>Level Requirement:</strong> ${heroic.level_requirement}+
              </div>
              <div class="meta-item">
                <strong>Group Size:</strong> ${heroic.group_size}
              </div>
              <div class="meta-item">
                <strong>Coordinates:</strong> ${heroic.coordinates.join(', ')}
              </div>
            </div>
          </div>
        </header>

        <!-- Navigation Tabs -->
        <nav class="heroic-nav">
          <div class="nav-tabs">
            <button class="nav-tab active" data-tab="overview">Overview</button>
            <button class="nav-tab" data-tab="map">Map & Location</button>
            <button class="nav-tab" data-tab="encounters">Boss Encounters</button>
            <button class="nav-tab" data-tab="loot">Loot Tables</button>
            <button class="nav-tab" data-tab="tactics">Tactics</button>
            <button class="nav-tab" data-tab="stats">Kill Stats</button>
          </div>
        </nav>

        <!-- Tab Content -->
        <main class="heroic-content">
          <!-- Overview Tab -->
          <section class="tab-content active" id="overview-tab">
            <div class="overview-grid">
              <div class="overview-main">
                <h2>Instance Overview</h2>
                <div class="description">
                  ${heroicData.description || 'Complete guide and tactics for this heroic instance.'}
                </div>
                
                ${heroicData.prerequisites ? `
                  <div class="prerequisites">
                    <h3>Prerequisites</h3>
                    <ul class="prereq-list">
                      ${heroicData.prerequisites.quests?.map(quest => `
                        <li class="prereq-item ${quest.status}">
                          <span class="prereq-name">${quest.name}</span>
                          <span class="prereq-status">${quest.status}</span>
                        </li>
                      `).join('') || ''}
                    </ul>
                  </div>
                ` : ''}
                
                <div class="difficulty-tiers">
                  <h3>Difficulty Tiers</h3>
                  <div class="tier-grid">
                    ${Object.entries(heroicData.difficulty_tiers || {}).map(([tier, data]) => `
                      <div class="tier-card ${tier}">
                        <h4>${tier.charAt(0).toUpperCase() + tier.slice(1)}</h4>
                        <p>Level: ${data.level_requirement}+</p>
                        <p>Group: ${data.group_size}</p>
                        <p>Lockout: ${data.reset_time}</p>
                        <p class="tier-desc">${data.description}</p>
                      </div>
                    `).join('')}
                  </div>
                </div>
              </div>
              
              <div class="overview-sidebar">
                <div class="quick-stats">
                  <h3>Quick Stats</h3>
                  <dl class="stats-list">
                    <dt>Location</dt>
                    <dd>${heroic.planet} - ${heroic.location}</dd>
                    <dt>Coordinates</dt>
                    <dd>${heroic.coordinates.join(', ')}</dd>
                    <dt>Status</dt>
                    <dd class="status ${heroic.status}">${heroic.status}</dd>
                    ${lootSummary ? `
                      <dt>Loot Items</dt>
                      <dd>${lootSummary.totalItems} total (${lootSummary.rareItems} rare)</dd>
                      <dt>Categories</dt>
                      <dd>${lootSummary.categories.slice(0, 3).join(', ')}${lootSummary.categories.length > 3 ? '...' : ''}</dd>
                    ` : ''}
                  </dl>
                </div>
              </div>
            </div>
          </section>

          <!-- Map & Location Tab -->
          <section class="tab-content" id="map-tab">
            <div class="map-container">
              <h2>Instance Map & Location</h2>
              ${mapData ? `
                <div class="map-viewer-container">
                  <div id="map-viewer" class="map-viewer" 
                       data-map-data='${JSON.stringify(mapData)}'
                       data-coordinates='${JSON.stringify(heroic.coordinates)}'>
                    <!-- Map will be rendered here by MapViewer component -->
                    <div class="map-placeholder">
                      <p>Loading interactive map...</p>
                    </div>
                  </div>
                </div>
              ` : `
                <div class="map-fallback">
                  <div class="coordinates-display">
                    <h3>Location Information</h3>
                    <p><strong>Planet:</strong> ${heroic.planet}</p>
                    <p><strong>Zone:</strong> ${heroic.location}</p>
                    <p><strong>Coordinates:</strong> ${heroic.coordinates.join(', ')}</p>
                  </div>
                </div>
              `}
              
              <div class="location-details">
                <h3>Getting There</h3>
                <div class="travel-info">
                  <p>Travel to ${heroic.planet} and navigate to coordinates ${heroic.coordinates.join(', ')} in the ${heroic.location} area.</p>
                  ${heroicData.travel_notes ? `<p class="travel-notes">${heroicData.travel_notes}</p>` : ''}
                </div>
              </div>
            </div>
          </section>

          <!-- Boss Encounters Tab -->
          <section class="tab-content" id="encounters-tab">
            <div class="encounters-container">
              <h2>Boss Encounters</h2>
              
              ${bossPhases.length > 0 ? `
                <div class="boss-phase-nav">
                  <h3>Select Boss Phase:</h3>
                  <div class="phase-buttons">
                    ${bossPhases.map((boss, index) => `
                      <button class="phase-btn ${index === 0 ? 'active' : ''}" 
                              data-boss-id="${boss.id}" 
                              data-phase="${boss.phase}">
                        ${boss.name} ${boss.phase > 1 ? `(Phase ${boss.phase})` : ''}
                      </button>
                    `).join('')}
                  </div>
                </div>
                
                <div class="boss-encounters">
                  ${heroicData.encounters?.map((encounter, index) => `
                    <div class="boss-encounter ${index === 0 ? 'active' : ''}" 
                         data-boss-id="${encounter.boss_id}">
                      <div class="boss-header">
                        <h3>${encounter.boss_name}</h3>
                        <div class="boss-meta">
                          <span class="boss-level">Level ${encounter.level}</span>
                          <span class="boss-health">HP: ${encounter.health || 'Unknown'}</span>
                          ${encounter.phase ? `<span class="boss-phase">Phase ${encounter.phase}</span>` : ''}
                        </div>
                      </div>
                      
                      <div class="boss-content">
                        <div class="boss-description">
                          ${encounter.description || 'No description available.'}
                        </div>
                        
                        ${encounter.abilities ? `
                          <div class="boss-abilities">
                            <h4>Special Abilities</h4>
                            <ul class="abilities-list">
                              ${encounter.abilities.map(ability => `
                                <li class="ability-item">
                                  <strong>${ability.name}:</strong> ${ability.description}
                                  ${ability.damage ? `<span class="damage">(${ability.damage} damage)</span>` : ''}
                                </li>
                              `).join('')}
                            </ul>
                          </div>
                        ` : ''}
                        
                        ${encounter.tactics ? `
                          <div class="boss-tactics">
                            <h4>Tactics & Strategy</h4>
                            <div class="tactics-content">
                              ${encounter.tactics}
                            </div>
                          </div>
                        ` : ''}
                      </div>
                    </div>
                  `).join('')}
                </div>
              ` : `
                <div class="no-encounters">
                  <p>Boss encounter data not available for this heroic.</p>
                </div>
              `}
            </div>
          </section>

          <!-- Loot Tables Tab -->
          <section class="tab-content" id="loot-tab">
            <div class="loot-container">
              <h2>Loot Tables</h2>
              ${lootTables ? `
                <div class="loot-tables-container">
                  <div id="loot-table-component" 
                       data-loot-data='${JSON.stringify(lootTables)}'>
                    <!-- Loot table will be rendered here by LootTable component -->
                  </div>
                </div>
              ` : `
                <div class="loot-fallback">
                  <p>Loot table data not available for this heroic.</p>
                  <p>Check back later as we continue to update our database.</p>
                </div>
              `}
            </div>
          </section>

          <!-- Tactics Tab -->
          <section class="tab-content" id="tactics-tab">
            <div class="tactics-container">
              <h2>General Tactics & Strategy</h2>
              ${heroicData.general_tactics ? `
                <div class="tactics-content">
                  ${heroicData.general_tactics}
                </div>
              ` : `
                <div class="tactics-placeholder">
                  <h3>Basic Strategy</h3>
                  <ul class="basic-tactics">
                    <li>Ensure all group members meet the level requirement (${heroic.level_requirement}+)</li>
                    <li>Bring appropriate healing and buffing classes</li>
                    <li>Study boss abilities and plan counter-strategies</li>
                    <li>Coordinate group composition for optimal damage and survivability</li>
                  </ul>
                </div>
              `}
              
              ${heroicData.recommended_group ? `
                <div class="group-composition">
                  <h3>Recommended Group Composition</h3>
                  <div class="composition-grid">
                    ${Object.entries(heroicData.recommended_group).map(([role, count]) => `
                      <div class="role-item">
                        <span class="role-name">${role}</span>
                        <span class="role-count">${count}</span>
                      </div>
                    `).join('')}
                  </div>
                </div>
              ` : ''}
            </div>
          </section>

          <!-- Kill Stats Tab -->
          <section class="tab-content" id="stats-tab">
            <div class="stats-container">
              <h2>Kill Statistics</h2>
              <div class="stats-placeholder">
                <p>Kill statistics and completion data will be displayed here.</p>
                <p>This feature requires integration with player tracking systems.</p>
              </div>
            </div>
          </section>
        </main>
      </div>

      <!-- Include component scripts -->
      <script type="module">
        // Initialize tab switching
        document.addEventListener('DOMContentLoaded', () => {
          const tabs = document.querySelectorAll('.nav-tab');
          const contents = document.querySelectorAll('.tab-content');
          
          tabs.forEach(tab => {
            tab.addEventListener('click', () => {
              const targetTab = tab.dataset.tab;
              
              // Remove active from all tabs and contents
              tabs.forEach(t => t.classList.remove('active'));
              contents.forEach(c => c.classList.remove('active'));
              
              // Add active to clicked tab and corresponding content
              tab.classList.add('active');
              document.getElementById(targetTab + '-tab').classList.add('active');
            });
          });
          
          // Initialize boss phase switching
          const phaseButtons = document.querySelectorAll('.phase-btn');
          const bossEncounters = document.querySelectorAll('.boss-encounter');
          
          phaseButtons.forEach(btn => {
            btn.addEventListener('click', () => {
              const bossId = btn.dataset.bossId;
              
              // Remove active from all buttons and encounters
              phaseButtons.forEach(b => b.classList.remove('active'));
              bossEncounters.forEach(e => e.classList.remove('active'));
              
              // Add active to clicked button and corresponding encounter
              btn.classList.add('active');
              const targetEncounter = document.querySelector(\`[data-boss-id="\${bossId}"]\`);
              if (targetEncounter) {
                targetEncounter.classList.add('active');
              }
            });
          });
          
          // Initialize map viewer if map data exists
          const mapContainer = document.getElementById('map-viewer');
          if (mapContainer && mapContainer.dataset.mapData) {
            // Map viewer component will be initialized here
            console.log('Initializing map viewer for ${heroic.id}');
          }
          
          // Initialize loot table component if loot data exists
          const lootContainer = document.getElementById('loot-table-component');
          if (lootContainer && lootContainer.dataset.lootData) {
            // Loot table component will be initialized here
            console.log('Initializing loot table for ${heroic.id}');
          }
        });
      </script>
      
      <style>
        .heroic-guide-container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 20px;
        }
        
        .heroic-header {
          background: linear-gradient(135deg, #2c3e50, #34495e);
          color: white;
          padding: 30px;
          border-radius: 10px;
          margin-bottom: 20px;
        }
        
        .heroic-header-content {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          flex-wrap: wrap;
          gap: 20px;
        }
        
        .heroic-title {
          font-size: 2.5rem;
          margin: 0 0 10px 0;
          font-weight: bold;
        }
        
        .heroic-subtitle {
          display: flex;
          gap: 10px;
          margin-bottom: 15px;
        }
        
        .planet-badge, .location-badge {
          background: rgba(255, 255, 255, 0.2);
          padding: 5px 10px;
          border-radius: 15px;
          font-size: 0.9rem;
        }
        
        .heroic-meta {
          display: flex;
          flex-direction: column;
          gap: 8px;
          min-width: 200px;
        }
        
        .meta-item {
          font-size: 0.95rem;
        }
        
        .heroic-nav {
          background: white;
          border-radius: 10px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          margin-bottom: 20px;
        }
        
        .nav-tabs {
          display: flex;
          overflow-x: auto;
        }
        
        .nav-tab {
          background: none;
          border: none;
          padding: 15px 20px;
          cursor: pointer;
          border-bottom: 3px solid transparent;
          white-space: nowrap;
          transition: all 0.3s ease;
        }
        
        .nav-tab:hover {
          background: #f8f9fa;
        }
        
        .nav-tab.active {
          border-bottom-color: #3498db;
          color: #3498db;
          font-weight: bold;
        }
        
        .heroic-content {
          background: white;
          border-radius: 10px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          padding: 30px;
        }
        
        .tab-content {
          display: none;
        }
        
        .tab-content.active {
          display: block;
        }
        
        .overview-grid {
          display: grid;
          grid-template-columns: 2fr 1fr;
          gap: 30px;
        }
        
        .tier-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 15px;
          margin-top: 15px;
        }
        
        .tier-card {
          border: 2px solid #ddd;
          border-radius: 8px;
          padding: 15px;
          transition: transform 0.2s ease;
        }
        
        .tier-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .tier-card.normal {
          border-color: #27ae60;
        }
        
        .tier-card.hard {
          border-color: #e74c3c;
        }
        
        .quick-stats {
          background: #f8f9fa;
          padding: 20px;
          border-radius: 8px;
        }
        
        .stats-list {
          margin: 0;
        }
        
        .stats-list dt {
          font-weight: bold;
          margin-top: 10px;
        }
        
        .stats-list dd {
          margin: 5px 0 0 0;
          color: #666;
        }
        
        .status.active {
          color: #27ae60;
          font-weight: bold;
        }
        
        .phase-buttons {
          display: flex;
          flex-wrap: wrap;
          gap: 10px;
          margin: 15px 0;
        }
        
        .phase-btn {
          background: #ecf0f1;
          border: 2px solid #bdc3c7;
          padding: 10px 15px;
          border-radius: 5px;
          cursor: pointer;
          transition: all 0.3s ease;
        }
        
        .phase-btn.active {
          background: #3498db;
          color: white;
          border-color: #3498db;
        }
        
        .boss-encounter {
          display: none;
          margin-top: 20px;
        }
        
        .boss-encounter.active {
          display: block;
        }
        
        .boss-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
          padding-bottom: 15px;
          border-bottom: 2px solid #ecf0f1;
        }
        
        .boss-meta {
          display: flex;
          gap: 15px;
        }
        
        .boss-meta span {
          background: #ecf0f1;
          padding: 5px 10px;
          border-radius: 15px;
          font-size: 0.9rem;
        }
        
        .abilities-list {
          list-style: none;
          padding: 0;
        }
        
        .ability-item {
          background: #f8f9fa;
          padding: 10px;
          margin-bottom: 10px;
          border-radius: 5px;
          border-left: 4px solid #3498db;
        }
        
        .damage {
          color: #e74c3c;
          font-weight: bold;
        }
        
        .map-viewer {
          min-height: 400px;
          background: #f8f9fa;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
        }
        
        .map-placeholder {
          text-align: center;
          color: #666;
        }
        
        @media (max-width: 768px) {
          .overview-grid {
            grid-template-columns: 1fr;
          }
          
          .heroic-header-content {
            flex-direction: column;
          }
          
          .nav-tabs {
            flex-direction: column;
          }
          
          .boss-header {
            flex-direction: column;
            align-items: flex-start;
            gap: 10px;
          }
          
          .boss-meta {
            flex-wrap: wrap;
          }
        }
      </style>
    `;
  }
};