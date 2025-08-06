const fs = require('fs');
const path = require('path');

module.exports = class {
  data() {
    return {
      title: "Heroic Loot Tables",
      description: "Detailed loot tables for heroic encounters",
      layout: "base.njk",
      eleventyComputed: {
        // This will be computed based on the URL parameter
        heroicData: (data) => {
          const heroic = data.page.fileSlug;
          const planet = data.page.filePathStem.split('/')[2]; // Extract planet from path
          
          try {
            // Try to load the specific planet's loot table
            const lootTablePath = path.join(__dirname, '../../../data/loot_tables', `${planet}.json`);
            if (fs.existsSync(lootTablePath)) {
              const lootData = JSON.parse(fs.readFileSync(lootTablePath, 'utf8'));
              return {
                planet: planet,
                heroic: heroic,
                lootData: lootData,
                availableHeroics: Object.keys(lootData.heroics || {})
              };
            }
          } catch (error) {
            console.error('Error loading loot data:', error);
          }
          
          return {
            planet: planet,
            heroic: heroic,
            lootData: {},
            availableHeroics: []
          };
        }
      }
    };
  }

  render(data) {
    const { heroicData } = data;
    const { planet, heroic, lootData, availableHeroics } = heroicData;
    
    // Check if the requested heroic exists
    const heroicExists = availableHeroics.includes(heroic);
    const heroicInfo = lootData.heroics?.[heroic];
    
    if (!heroicExists || !heroicInfo) {
      return `
        <div class="error-container">
          <h1>Heroic Not Found</h1>
          <p>The heroic "${heroic}" was not found for planet "${planet}".</p>
          <div class="available-heroics">
            <h3>Available Heroics for ${planet}:</h3>
            <ul>
              ${availableHeroics.map(h => `
                <li><a href="/heroics/${h}/loot">${h.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</a></li>
              `).join('')}
            </ul>
          </div>
        </div>
      `;
    }

    return `
      <div class="heroic-loot-page">
        <!-- Navigation Breadcrumb -->
        <nav class="breadcrumb-nav">
          <a href="/heroics">Heroics</a> &gt;
          <a href="/heroics/${planet}">${planet.charAt(0).toUpperCase() + planet.slice(1)}</a> &gt;
          <span>${heroicInfo.boss}</span>
        </nav>

        <!-- Heroic Information Header -->
        <div class="heroic-header">
          <div class="heroic-info">
            <h1>${heroicInfo.boss}</h1>
            <div class="heroic-details">
              <div class="detail-item">
                <span class="label">Location:</span>
                <span class="value">${heroicInfo.location}</span>
              </div>
              <div class="detail-item">
                <span class="label">Level:</span>
                <span class="value">${heroicInfo.level}</span>
              </div>
              <div class="detail-item">
                <span class="label">Total Kills:</span>
                <span class="value">${heroicInfo.totalKills || 0}</span>
              </div>
            </div>
          </div>
          
          <div class="heroic-actions">
            <button class="btn btn-primary" onclick="window.print()">
              Print Loot Table
            </button>
            <button class="btn btn-secondary" onclick="exportToMS11()">
              Export for MS11
            </button>
          </div>
        </div>

        <!-- Loot Table Component -->
        <div id="loot-table-container" 
             data-planet="${planet}" 
             data-heroic="${heroic}"
             data-loot-data='${JSON.stringify(lootData)}'>
          <!-- Svelte component will be mounted here -->
        </div>

        <!-- Related Heroics -->
        <div class="related-heroics">
          <h3>Other Heroics on ${planet.charAt(0).toUpperCase() + planet.slice(1)}</h3>
          <div class="heroic-grid">
            ${availableHeroics.filter(h => h !== heroic).map(h => {
              const hInfo = lootData.heroics[h];
              return `
                <div class="heroic-card">
                  <h4>${hInfo.boss}</h4>
                  <p>${hInfo.location}</p>
                  <p>Level: ${hInfo.level}</p>
                  <a href="/heroics/${h}/loot" class="btn btn-outline">View Loot</a>
                </div>
              `;
            }).join('')}
          </div>
        </div>

        <!-- Data Source Information -->
        <div class="data-source-info">
          <h3>Data Sources</h3>
          <div class="source-breakdown">
            <div class="source-item">
              <span class="source-label">SWGDB Generated:</span>
              <span class="source-count">${Object.values(lootData.heroics || {}).reduce((acc, h) => 
                acc + (h.items || []).filter(item => item.source === 'SWGDB Generated').length, 0)}</span>
            </div>
            <div class="source-item">
              <span class="source-label">User Submitted:</span>
              <span class="source-count">${Object.values(lootData.heroics || {}).reduce((acc, h) => 
                acc + (h.items || []).filter(item => item.source === 'User Submitted').length, 0)}</span>
            </div>
            <div class="source-item">
              <span class="source-label">Bot Generated:</span>
              <span class="source-count">${Object.values(lootData.heroics || {}).reduce((acc, h) => 
                acc + (h.items || []).filter(item => item.source === 'Bot Generated').length, 0)}</span>
            </div>
          </div>
          <p class="last-updated">
            Last updated: ${lootData.lastUpdated ? new Date(lootData.lastUpdated).toLocaleDateString() : 'Unknown'}
          </p>
        </div>

        <!-- MS11 Integration Script -->
        <script>
          function exportToMS11() {
            const lootData = ${JSON.stringify(lootData)};
            const exportData = {
              timestamp: new Date().toISOString(),
              source: 'SWGDB Loot Tables',
              planet: '${planet}',
              heroic: '${heroic}',
              data: lootData
            };
            
            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = '${planet}_${heroic}_ms11_export.json';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
          }

          // Initialize Svelte component when page loads
          document.addEventListener('DOMContentLoaded', function() {
            // This would typically initialize the Svelte component
            // For now, we'll just set up the data for the component
            window.lootTableData = {
              planet: '${planet}',
              heroic: '${heroic}',
              lootData: ${JSON.stringify(lootData)}
            };
          });
        </script>

        <style>
          .heroic-loot-page {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
          }

          .breadcrumb-nav {
            margin-bottom: 20px;
            padding: 10px 0;
            border-bottom: 1px solid #e0e0e0;
          }

          .breadcrumb-nav a {
            color: #007bff;
            text-decoration: none;
          }

          .breadcrumb-nav a:hover {
            text-decoration: underline;
          }

          .heroic-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
          }

          .heroic-info h1 {
            margin: 0 0 15px 0;
            color: #333;
          }

          .heroic-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
          }

          .detail-item {
            display: flex;
            justify-content: space-between;
            padding: 8px 12px;
            background: white;
            border-radius: 4px;
            border-left: 4px solid #007bff;
          }

          .detail-item .label {
            font-weight: 600;
            color: #666;
          }

          .detail-item .value {
            font-weight: bold;
            color: #333;
          }

          .heroic-actions {
            display: flex;
            gap: 10px;
          }

          .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            text-decoration: none;
            display: inline-block;
            transition: all 0.2s;
          }

          .btn-primary {
            background: #007bff;
            color: white;
          }

          .btn-primary:hover {
            background: #0056b3;
          }

          .btn-secondary {
            background: #6c757d;
            color: white;
          }

          .btn-secondary:hover {
            background: #545b62;
          }

          .btn-outline {
            background: transparent;
            color: #007bff;
            border: 1px solid #007bff;
          }

          .btn-outline:hover {
            background: #007bff;
            color: white;
          }

          .related-heroics {
            margin-top: 40px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
          }

          .related-heroics h3 {
            margin-bottom: 20px;
            color: #333;
          }

          .heroic-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
          }

          .heroic-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          }

          .heroic-card h4 {
            margin: 0 0 10px 0;
            color: #333;
          }

          .heroic-card p {
            margin: 5px 0;
            color: #666;
          }

          .data-source-info {
            margin-top: 40px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
          }

          .data-source-info h3 {
            margin-bottom: 15px;
            color: #333;
          }

          .source-breakdown {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 15px;
          }

          .source-item {
            display: flex;
            justify-content: space-between;
            padding: 10px;
            background: white;
            border-radius: 4px;
          }

          .source-label {
            font-weight: 600;
            color: #666;
          }

          .source-count {
            font-weight: bold;
            color: #333;
          }

          .last-updated {
            margin: 0;
            color: #666;
            font-style: italic;
          }

          .error-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 40px;
            text-align: center;
          }

          .error-container h1 {
            color: #dc3545;
            margin-bottom: 20px;
          }

          .available-heroics {
            margin-top: 30px;
            text-align: left;
          }

          .available-heroics h3 {
            margin-bottom: 15px;
            color: #333;
          }

          .available-heroics ul {
            list-style: none;
            padding: 0;
          }

          .available-heroics li {
            margin: 10px 0;
          }

          .available-heroics a {
            color: #007bff;
            text-decoration: none;
            padding: 8px 12px;
            background: #f8f9fa;
            border-radius: 4px;
            display: inline-block;
          }

          .available-heroics a:hover {
            background: #e9ecef;
          }

          @media (max-width: 768px) {
            .heroic-header {
              flex-direction: column;
              gap: 20px;
            }

            .heroic-actions {
              align-self: stretch;
            }

            .heroic-grid {
              grid-template-columns: 1fr;
            }
          }
        </style>
      </div>
    `;
  }
}; 