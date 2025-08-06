const fs = require('fs');
const path = require('path');

module.exports = class {
  data() {
    return {
      title: "SWGDB Mod Portal",
      description: "Community mods and addons for Star Wars Galaxies with SWGR compliance checking",
      layout: "base.njk",
      eleventyComputed: {
        modsData: () => {
          try {
            const modsPath = path.join(__dirname, '../../data/mods/mod-database.json');
            if (fs.existsSync(modsPath)) {
              const modsData = JSON.parse(fs.readFileSync(modsPath, 'utf8'));
              return modsData;
            }
          } catch (error) {
            console.error('Error loading mods data:', error);
          }
          return { metadata: {}, mods: {} };
        }
      }
    };
  }

  render(data) {
    const { modsData } = data;
    const { metadata, mods } = modsData;
    
    // Convert mods object to array for easier handling
    const modsArray = Object.values(mods || {});
    
    // Generate category list
    const categories = metadata.categories || [];
    
    // Generate statistics
    const stats = {
      total: metadata.total_mods || 0,
      swgrSafe: metadata.swgr_safe_count || 0,
      ms11Derived: metadata.ms11_derived_count || 0,
      categories: categories.length
    };

    return `
      <div class="mods-portal">
        <div class="portal-header">
          <div class="header-content">
            <h1><i class="fas fa-puzzle-piece"></i> SWGDB Mod Portal</h1>
            <p>Community mods and addons for Star Wars Galaxies with SWGR compliance checking</p>
          </div>
          
          <div class="compliance-banner">
            <div class="banner-content">
              <i class="fas fa-shield-alt"></i>
              <div>
                <h3>SWGR Rule Compliance</h3>
                <p>All mods are verified against Star Wars Galaxies Reborn server rules</p>
              </div>
            </div>
          </div>
        </div>

        <div class="portal-content">
          <div class="stats-section">
            <div class="stat-card">
              <i class="fas fa-cube"></i>
              <div class="stat-info">
                <h3>${stats.total}</h3>
                <p>Total Mods</p>
              </div>
            </div>
            
            <div class="stat-card safe">
              <i class="fas fa-check-circle"></i>
              <div class="stat-info">
                <h3>${stats.swgrSafe}</h3>
                <p>SWGR Safe</p>
              </div>
            </div>
            
            <div class="stat-card internal">
              <i class="fas fa-lock"></i>
              <div class="stat-info">
                <h3>${stats.ms11Derived}</h3>
                <p>Internal Only</p>
              </div>
            </div>
            
            <div class="stat-card">
              <i class="fas fa-tags"></i>
              <div class="stat-info">
                <h3>${stats.categories}</h3>
                <p>Categories</p>
              </div>
            </div>
          </div>

          <div class="filters-section">
            <div class="filter-group">
              <h3><i class="fas fa-filter"></i> Filter by Status</h3>
              <div class="filter-buttons">
                <button class="filter-btn active" data-filter="all">All Mods</button>
                <button class="filter-btn" data-filter="swgr-safe">SWGR Safe ✅</button>
                <button class="filter-btn" data-filter="swgr-unsafe">Not SWGR Compliant ❌</button>
                <button class="filter-btn" data-filter="internal">Internal Only 🔒</button>
              </div>
            </div>

            <div class="filter-group">
              <h3><i class="fas fa-tag"></i> Filter by Category</h3>
              <div class="filter-buttons">
                <button class="filter-btn" data-filter="UI">UI</button>
                <button class="filter-btn" data-filter="HUD">HUD</button>
                <button class="filter-btn" data-filter="Crafting Helpers">Crafting Helpers</button>
                <button class="filter-btn" data-filter="Visual Upgrades">Visual Upgrades</button>
                <button class="filter-btn" data-filter="Automation Tools">Automation Tools</button>
              </div>
            </div>

            <div class="search-section">
              <div class="search-box">
                <i class="fas fa-search"></i>
                <input type="text" id="searchInput" placeholder="Search mods by name, author, or description...">
              </div>
            </div>
          </div>

          <div class="mods-container">
            <div id="modsGrid" class="mods-grid">
              <!-- Mod cards will be populated by JavaScript -->
            </div>
            
            <div id="noResults" class="no-results" style="display: none;">
              <i class="fas fa-search"></i>
              <h3>No mods found</h3>
              <p>Try adjusting your filters or search terms</p>
            </div>
          </div>

          <div class="submission-section">
            <div class="submission-content">
              <h3><i class="fas fa-upload"></i> Submit Your Mod</h3>
              <p>Have a mod that follows SWGR rules? Submit it for review and inclusion in our database.</p>
              <button class="submit-btn" onclick="openSubmissionModal()">
                <i class="fas fa-plus"></i> Submit Mod
              </button>
            </div>
          </div>
        </div>

        <script>
          // Mod data passed from Eleventy
          const modsData = ${JSON.stringify(modsArray)};
          let filteredMods = [...modsData];
          let currentFilters = {
            status: 'all',
            category: 'all',
            search: ''
          };

          function updateFilters() {
            filteredMods = modsData.filter(mod => {
              // Status filter
              if (currentFilters.status !== 'all') {
                if (currentFilters.status === 'swgr-safe' && !mod.swgr_compliant) return false;
                if (currentFilters.status === 'swgr-unsafe' && mod.swgr_compliant) return false;
                if (currentFilters.status === 'internal' && !mod.ms11_derived) return false;
              }

              // Category filter
              if (currentFilters.category !== 'all' && mod.category !== currentFilters.category) {
                return false;
              }

              // Search filter
              if (currentFilters.search) {
                const searchTerm = currentFilters.search.toLowerCase();
                const searchText = [
                  mod.name,
                  mod.author,
                  mod.description,
                  ...(mod.features || [])
                ].join(' ').toLowerCase();
                
                if (!searchText.includes(searchTerm)) return false;
              }

              return true;
            });

            displayMods();
          }

          function displayMods() {
            const grid = document.getElementById('modsGrid');
            const noResults = document.getElementById('noResults');

            if (filteredMods.length === 0) {
              grid.style.display = 'none';
              noResults.style.display = 'block';
              return;
            }

            grid.style.display = 'grid';
            noResults.style.display = 'none';

            // In a real implementation, this would render Svelte components
            // For now, we'll create basic HTML cards
            grid.innerHTML = filteredMods.map(mod => createModCard(mod)).join('');
          }

          function createModCard(mod) {
            const complianceClass = mod.ms11_derived ? 'internal' : 
                                 mod.swgr_compliant ? 'safe' : 'unsafe';
            
            const complianceText = mod.ms11_derived ? 'Internal Only 🔒' :
                                 mod.swgr_compliant ? 'SWGR Safe ✅' : 'Not SWGR Compliant ❌';

            return \`
              <div class="mod-card \${complianceClass}">
                <div class="mod-header">
                  <h3>\${mod.name}</h3>
                  <div class="mod-badges">
                    <span class="compliance-badge \${complianceClass}">\${complianceText}</span>
                    <span class="category-badge">\${mod.category}</span>
                  </div>
                </div>
                
                <div class="mod-content">
                  <p class="mod-description">\${mod.description}</p>
                  
                  <div class="mod-meta">
                    <span><i class="fas fa-user"></i> \${mod.author}</span>
                    <span><i class="fas fa-download"></i> \${mod.downloads?.toLocaleString() || 0}</span>
                    <span><i class="fas fa-star"></i> \${mod.rating || 'N/A'}</span>
                  </div>
                  
                  <div class="mod-actions">
                    <button class="btn btn-primary" onclick="viewModDetails('\${mod.id}')">
                      <i class="fas fa-eye"></i> View Details
                    </button>
                    \${!mod.internal_only ? \`
                      <button class="btn btn-secondary" onclick="downloadMod('\${mod.id}')">
                        <i class="fas fa-download"></i> Download
                      </button>
                    \` : \`
                      <button class="btn btn-disabled" disabled>
                        <i class="fas fa-lock"></i> Internal Only
                      </button>
                    \`}
                  </div>
                </div>
              </div>
            \`;
          }

          function viewModDetails(modId) {
            // In a real implementation, this would navigate to a detail page
            alert(\`Viewing details for mod: \${modId}\`);
          }

          function downloadMod(modId) {
            const mod = modsData.find(m => m.id === modId);
            if (mod && mod.download_url) {
              window.open(mod.download_url, '_blank');
            } else {
              alert(\`Downloading \${mod?.name || 'mod'}...\n\nNote: This is a demo. In production, this would trigger an actual download.\`);
            }
          }

          function openSubmissionModal() {
            alert('Mod Submission Modal\\n\\nIn production, this would open a modal with:\\n- File upload\\n- SWGR compliance checklist\\n- Author information\\n- Mod description\\n- Rule agreement checkbox');
          }

          // Event listeners
          document.addEventListener('DOMContentLoaded', function() {
            // Filter button clicks
            document.querySelectorAll('.filter-btn').forEach(btn => {
              btn.addEventListener('click', function() {
                const filterType = this.dataset.filter;
                const filterGroup = this.closest('.filter-group');
                
                // Update active button
                filterGroup.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                
                // Update filters
                if (filterGroup.querySelector('[data-filter="swgr-safe"]')) {
                  currentFilters.status = filterType;
                } else if (filterGroup.querySelector('[data-filter="UI"]')) {
                  currentFilters.category = filterType;
                }
                
                updateFilters();
              });
            });

            // Search input
            document.getElementById('searchInput').addEventListener('input', function() {
              currentFilters.search = this.value;
              updateFilters();
            });

            // Initial display
            displayMods();
          });
        </script>

        <style>
          .mods-portal {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
          }

          .portal-header {
            text-align: center;
            margin-bottom: 40px;
          }

          .header-content h1 {
            font-size: 2.5rem;
            color: #333;
            margin-bottom: 10px;
          }

          .header-content p {
            font-size: 1.1rem;
            color: #666;
            margin-bottom: 20px;
          }

          .compliance-banner {
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 20px;
            border-radius: 12px;
            margin-top: 20px;
          }

          .banner-content {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
          }

          .banner-content i {
            font-size: 2rem;
          }

          .banner-content h3 {
            margin: 0 0 5px 0;
            font-size: 1.3rem;
          }

          .banner-content p {
            margin: 0;
            opacity: 0.9;
          }

          .stats-section {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
          }

          .stat-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: center;
            gap: 15px;
          }

          .stat-card.safe {
            border-left: 4px solid #28a745;
          }

          .stat-card.internal {
            border-left: 4px solid #6c757d;
          }

          .stat-card i {
            font-size: 2rem;
            color: #007bff;
          }

          .stat-card.safe i {
            color: #28a745;
          }

          .stat-card.internal i {
            color: #6c757d;
          }

          .stat-info h3 {
            margin: 0;
            font-size: 1.8rem;
            font-weight: 600;
            color: #333;
          }

          .stat-info p {
            margin: 0;
            color: #666;
            font-size: 0.9rem;
          }

          .filters-section {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 30px;
          }

          .filter-group {
            margin-bottom: 25px;
          }

          .filter-group:last-child {
            margin-bottom: 0;
          }

          .filter-group h3 {
            margin: 0 0 15px 0;
            color: #333;
            font-size: 1.1rem;
            display: flex;
            align-items: center;
            gap: 8px;
          }

          .filter-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
          }

          .filter-btn {
            padding: 8px 16px;
            border: 2px solid #e9ecef;
            background: white;
            color: #495057;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 500;
            transition: all 0.2s ease;
          }

          .filter-btn:hover {
            border-color: #007bff;
            color: #007bff;
          }

          .filter-btn.active {
            background: #007bff;
            border-color: #007bff;
            color: white;
          }

          .search-section {
            margin-top: 20px;
          }

          .search-box {
            position: relative;
            max-width: 500px;
          }

          .search-box i {
            position: absolute;
            left: 15px;
            top: 50%;
            transform: translateY(-50%);
            color: #6c757d;
          }

          .search-box input {
            width: 100%;
            padding: 12px 15px 12px 45px;
            border: 2px solid #e9ecef;
            border-radius: 25px;
            font-size: 1rem;
            transition: border-color 0.2s ease;
          }

          .search-box input:focus {
            outline: none;
            border-color: #007bff;
          }

          .mods-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
          }

          .mod-card {
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            padding: 20px;
            transition: all 0.3s ease;
            border: 2px solid transparent;
          }

          .mod-card:hover {
            box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
            transform: translateY(-2px);
          }

          .mod-card.safe {
            border-color: #28a745;
          }

          .mod-card.unsafe {
            border-color: #dc3545;
          }

          .mod-card.internal {
            border-color: #6c757d;
            background: #f8f9fa;
          }

          .mod-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 15px;
          }

          .mod-header h3 {
            margin: 0;
            font-size: 1.3rem;
            color: #333;
          }

          .mod-badges {
            display: flex;
            flex-direction: column;
            gap: 5px;
            align-items: flex-end;
          }

          .compliance-badge {
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: 600;
            color: white;
            text-align: center;
            white-space: nowrap;
          }

          .compliance-badge.safe {
            background: #28a745;
          }

          .compliance-badge.unsafe {
            background: #dc3545;
          }

          .compliance-badge.internal {
            background: #6c757d;
          }

          .category-badge {
            background: #e9ecef;
            color: #495057;
            padding: 2px 6px;
            border-radius: 8px;
            font-size: 0.6rem;
            font-weight: 600;
          }

          .mod-content {
            margin-bottom: 15px;
          }

          .mod-description {
            color: #555;
            line-height: 1.5;
            margin-bottom: 15px;
          }

          .mod-meta {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
            font-size: 0.9rem;
            color: #666;
          }

          .mod-meta span {
            display: flex;
            align-items: center;
            gap: 5px;
          }

          .mod-actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
          }

          .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9rem;
            font-weight: 500;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s ease;
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

          .btn-disabled {
            background: #6c757d;
            color: white;
            opacity: 0.6;
            cursor: not-allowed;
          }

          .no-results {
            text-align: center;
            padding: 60px 20px;
            color: #666;
          }

          .no-results i {
            font-size: 3rem;
            margin-bottom: 20px;
            opacity: 0.5;
          }

          .submission-section {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            text-align: center;
          }

          .submission-content h3 {
            margin: 0 0 10px 0;
            font-size: 1.5rem;
          }

          .submission-content p {
            margin: 0 0 20px 0;
            opacity: 0.9;
          }

          .submit-btn {
            background: white;
            color: #667eea;
            padding: 12px 30px;
            border: none;
            border-radius: 25px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
          }

          .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
          }

          @media (max-width: 768px) {
            .mods-grid {
              grid-template-columns: 1fr;
            }
            
            .filter-buttons {
              justify-content: center;
            }
            
            .mod-header {
              flex-direction: column;
              gap: 10px;
            }
            
            .mod-badges {
              align-items: flex-start;
            }
          }
        </style>
      </div>
    `;
  }
}; 