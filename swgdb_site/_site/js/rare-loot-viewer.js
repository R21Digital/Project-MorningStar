/**
 * Rare Loot Drop Table Viewer
 * Comprehensive loot lookup tool with filtering and search capabilities
 */

class RareLootViewer {
    constructor() {
        this.lootData = null;
        this.filteredItems = [];
        this.currentFilters = {
            category: '',
            rarity: '',
            planet: '',
            enemyType: '',
            source: '',
            valueRange: '',
            search: '',
            sortBy: 'name'
        };
        
        this.init();
    }

    async init() {
        try {
            await this.loadLootData();
            this.setupEventListeners();
            this.populateFilterOptions();
            this.updateStats();
            this.renderItems();
        } catch (error) {
            console.error('Failed to initialize rare loot viewer:', error);
            this.showError('Failed to load loot data');
        }
    }

    async loadLootData() {
        try {
            const response = await fetch('/data/rare_loot_database.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            this.lootData = await response.json();
            this.filteredItems = [...this.lootData.items];
        } catch (error) {
            console.error('Error loading loot data:', error);
            // Fallback to demo data if fetch fails
            this.lootData = this.getDemoData();
            this.filteredItems = [...this.lootData.items];
        }
    }

    getDemoData() {
        return {
            metadata: {
                version: "1.0",
                last_updated: "2025-01-04T12:00:00",
                data_sources: ["community_submissions", "ms11_scanning", "rls_wiki", "loot_tables"],
                total_items: 10,
                total_sources: 4
            },
            categories: {
                weapons: { name: "Weapons", description: "Rare weapons and weapon components", icon: "sword", color: "#dc3545" },
                armor: { name: "Armor", description: "Rare armor pieces and components", icon: "shield", color: "#28a745" },
                jewelry: { name: "Jewelry", description: "Rings, necklaces, and other jewelry", icon: "gem", color: "#ffc107" },
                resources: { name: "Resources", description: "Rare crafting materials and resources", icon: "cog", color: "#17a2b8" },
                collectibles: { name: "Collectibles", description: "Rare collectible items", icon: "star", color: "#6f42c1" },
                consumables: { name: "Consumables", description: "Rare consumable items", icon: "flask", color: "#fd7e14" }
            },
            locations: {
                tatooine: { name: "Tatooine", zones: ["Krayt Dragon Valley", "Jundland Wastes", "Dune Sea"] },
                lok: { name: "Lok", zones: ["Kimogila Territory", "Imperial Research Facility", "Lok Jungle"] },
                kashyyyk: { name: "Kashyyyk", zones: ["Mouf Territory", "Wookiee Village", "Kashyyyk Jungle"] },
                dantooine: { name: "Dantooine", zones: ["Force Crystal Cave", "Dantooine Plains", "Abandoned Jedi Temple"] }
            },
            enemy_types: {
                boss: { name: "Boss", description: "Major boss enemies", difficulty: "high", color: "#dc3545" },
                elite: { name: "Elite", description: "Elite enemy types", difficulty: "medium", color: "#fd7e14" },
                rare: { name: "Rare", description: "Rare spawn enemies", difficulty: "medium", color: "#6f42c1" },
                common: { name: "Common", description: "Common enemies", difficulty: "low", color: "#6c757d" }
            },
            items: [
                {
                    id: "krayt_pearl_001",
                    name: "Krayt Dragon Pearl",
                    category: "jewelry",
                    rarity: "legendary",
                    description: "A rare pearl from the heart of a Krayt Dragon",
                    locations: [{
                        planet: "tatooine",
                        zone: "Krayt Dragon Valley",
                        enemy_type: "boss",
                        enemy_name: "Greater Krayt Dragon",
                        drop_rate: 0.02,
                        confirmed_drops: 3,
                        last_seen: "2024-01-15T09:45:30"
                    }],
                    stats: { value: 50000, weight: 0.1, attributes: ["rare", "collectible", "valuable"] },
                    sources: ["ms11_scanning", "community_submissions"],
                    image_url: "/images/loot/krayt_pearl.jpg",
                    wiki_url: "https://swgr.org/wiki/rls/krayt-dragon-pearl"
                },
                {
                    id: "kimogila_scale_001",
                    name: "Kimogila Scale",
                    category: "resources",
                    rarity: "epic",
                    description: "A tough scale from a Kimogila matriarch",
                    locations: [{
                        planet: "lok",
                        zone: "Kimogila Territory",
                        enemy_type: "boss",
                        enemy_name: "Kimogila Matriarch",
                        drop_rate: 0.15,
                        confirmed_drops: 12,
                        last_seen: "2024-01-10T14:22:15"
                    }],
                    stats: { value: 15000, weight: 2.0, attributes: ["crafting_material", "armor_component"] },
                    sources: ["ms11_scanning", "rls_wiki"],
                    image_url: "/images/loot/kimogila_scale.jpg",
                    wiki_url: "https://swgr.org/wiki/rls/kimogila-scale"
                }
            ],
            boss_profiles: {
                greater_krayt_dragon: {
                    name: "Greater Krayt Dragon",
                    planet: "tatooine",
                    zone: "Krayt Dragon Valley",
                    level: 90,
                    type: "boss",
                    description: "The most powerful Krayt Dragon variant",
                    known_drops: ["krayt_pearl_001", "ancient_artifact_001"],
                    spawn_conditions: "Rare spawn in Krayt Dragon Valley",
                    difficulty: "extreme",
                    image_url: "/images/bosses/greater_krayt_dragon.jpg",
                    wiki_url: "https://swgr.org/wiki/bosses/greater-krayt-dragon"
                }
            }
        };
    }

    setupEventListeners() {
        // Filter change events
        document.getElementById('categoryFilter').addEventListener('change', (e) => {
            this.currentFilters.category = e.target.value;
            this.applyFilters();
        });

        document.getElementById('rarityFilter').addEventListener('change', (e) => {
            this.currentFilters.rarity = e.target.value;
            this.applyFilters();
        });

        document.getElementById('planetFilter').addEventListener('change', (e) => {
            this.currentFilters.planet = e.target.value;
            this.applyFilters();
        });

        document.getElementById('enemyTypeFilter').addEventListener('change', (e) => {
            this.currentFilters.enemyType = e.target.value;
            this.applyFilters();
        });

        document.getElementById('sourceFilter').addEventListener('change', (e) => {
            this.currentFilters.source = e.target.value;
            this.applyFilters();
        });

        document.getElementById('valueFilter').addEventListener('change', (e) => {
            this.currentFilters.valueRange = e.target.value;
            this.applyFilters();
        });

        document.getElementById('sortFilter').addEventListener('change', (e) => {
            this.currentFilters.sortBy = e.target.value;
            this.applyFilters();
        });

        // Search box
        document.getElementById('searchBox').addEventListener('input', (e) => {
            this.currentFilters.search = e.target.value;
            this.applyFilters();
        });

        // Quick filter buttons
        document.getElementById('quickFilters').addEventListener('click', (e) => {
            if (e.target.classList.contains('filter-btn')) {
                // Remove active class from all buttons
                document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
                // Add active class to clicked button
                e.target.classList.add('active');
                
                const filter = e.target.dataset.filter;
                this.applyQuickFilter(filter);
            }
        });
    }

    populateFilterOptions() {
        // Populate category filter
        const categoryFilter = document.getElementById('categoryFilter');
        Object.entries(this.lootData.categories).forEach(([key, category]) => {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = category.name;
            categoryFilter.appendChild(option);
        });

        // Populate rarity filter
        const rarityFilter = document.getElementById('rarityFilter');
        const rarities = ['common', 'uncommon', 'rare', 'epic', 'legendary'];
        rarities.forEach(rarity => {
            const option = document.createElement('option');
            option.value = rarity;
            option.textContent = rarity.charAt(0).toUpperCase() + rarity.slice(1);
            rarityFilter.appendChild(option);
        });

        // Populate planet filter
        const planetFilter = document.getElementById('planetFilter');
        Object.entries(this.lootData.locations).forEach(([key, location]) => {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = location.name;
            planetFilter.appendChild(option);
        });

        // Populate enemy type filter
        const enemyTypeFilter = document.getElementById('enemyTypeFilter');
        Object.entries(this.lootData.enemy_types).forEach(([key, enemyType]) => {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = enemyType.name;
            enemyTypeFilter.appendChild(option);
        });

        // Populate source filter
        const sourceFilter = document.getElementById('sourceFilter');
        const sources = [
            { value: 'community_submissions', label: 'Community Submissions' },
            { value: 'ms11_scanning', label: 'MS11 Scanning' },
            { value: 'rls_wiki', label: 'RLS Wiki' },
            { value: 'loot_tables', label: 'Loot Tables' }
        ];
        sources.forEach(source => {
            const option = document.createElement('option');
            option.value = source.value;
            option.textContent = source.label;
            sourceFilter.appendChild(option);
        });
    }

    applyQuickFilter(filter) {
        // Reset all filters
        this.currentFilters = {
            category: '',
            rarity: '',
            planet: '',
            enemyType: '',
            source: '',
            valueRange: '',
            search: '',
            sortBy: 'name'
        };

        // Apply quick filter
        switch (filter) {
            case 'legendary':
                this.currentFilters.rarity = 'legendary';
                break;
            case 'epic':
                this.currentFilters.rarity = 'epic';
                break;
            case 'rare':
                this.currentFilters.rarity = 'rare';
                break;
            case 'boss':
                this.currentFilters.enemyType = 'boss';
                break;
            case 'recent':
                this.currentFilters.sortBy = 'recent';
                break;
        }

        // Update filter UI
        this.updateFilterUI();
        this.applyFilters();
    }

    updateFilterUI() {
        document.getElementById('categoryFilter').value = this.currentFilters.category;
        document.getElementById('rarityFilter').value = this.currentFilters.rarity;
        document.getElementById('planetFilter').value = this.currentFilters.planet;
        document.getElementById('enemyTypeFilter').value = this.currentFilters.enemyType;
        document.getElementById('sourceFilter').value = this.currentFilters.source;
        document.getElementById('valueFilter').value = this.currentFilters.valueRange;
        document.getElementById('sortFilter').value = this.currentFilters.sortBy;
        document.getElementById('searchBox').value = this.currentFilters.search;
    }

    applyFilters() {
        this.filteredItems = this.lootData.items.filter(item => {
            // Category filter
            if (this.currentFilters.category && item.category !== this.currentFilters.category) {
                return false;
            }

            // Rarity filter
            if (this.currentFilters.rarity && item.rarity !== this.currentFilters.rarity) {
                return false;
            }

            // Planet filter
            if (this.currentFilters.planet) {
                const hasPlanet = item.locations.some(loc => loc.planet === this.currentFilters.planet);
                if (!hasPlanet) return false;
            }

            // Enemy type filter
            if (this.currentFilters.enemyType) {
                const hasEnemyType = item.locations.some(loc => loc.enemy_type === this.currentFilters.enemyType);
                if (!hasEnemyType) return false;
            }

            // Source filter
            if (this.currentFilters.source) {
                const hasSource = item.sources.includes(this.currentFilters.source);
                if (!hasSource) return false;
            }

            // Value range filter
            if (this.currentFilters.valueRange) {
                const value = item.stats.value;
                switch (this.currentFilters.valueRange) {
                    case '0-1000':
                        if (value > 1000) return false;
                        break;
                    case '1000-10000':
                        if (value < 1000 || value > 10000) return false;
                        break;
                    case '10000-50000':
                        if (value < 10000 || value > 50000) return false;
                        break;
                    case '50000+':
                        if (value < 50000) return false;
                        break;
                }
            }

            // Search filter
            if (this.currentFilters.search) {
                const searchTerm = this.currentFilters.search.toLowerCase();
                const searchableText = [
                    item.name,
                    item.description,
                    ...item.locations.map(loc => loc.enemy_name),
                    ...item.locations.map(loc => loc.zone),
                    ...item.stats.attributes
                ].join(' ').toLowerCase();
                
                if (!searchableText.includes(searchTerm)) {
                    return false;
                }
            }

            return true;
        });

        // Sort items
        this.sortItems();
        this.renderItems();
    }

    sortItems() {
        this.filteredItems.sort((a, b) => {
            switch (this.currentFilters.sortBy) {
                case 'name':
                    return a.name.localeCompare(b.name);
                case 'rarity':
                    const rarityOrder = { 'legendary': 5, 'epic': 4, 'rare': 3, 'uncommon': 2, 'common': 1 };
                    return rarityOrder[b.rarity] - rarityOrder[a.rarity];
                case 'value':
                    return b.stats.value - a.stats.value;
                case 'drop_rate':
                    const maxDropRateA = Math.max(...a.locations.map(loc => loc.drop_rate));
                    const maxDropRateB = Math.max(...b.locations.map(loc => loc.drop_rate));
                    return maxDropRateB - maxDropRateA;
                case 'recent':
                    const latestA = Math.max(...a.locations.map(loc => new Date(loc.last_seen).getTime()));
                    const latestB = Math.max(...b.locations.map(loc => new Date(loc.last_seen).getTime()));
                    return latestB - latestA;
                default:
                    return 0;
            }
        });
    }

    renderItems() {
        const container = document.getElementById('resultsContainer');
        
        if (this.filteredItems.length === 0) {
            container.innerHTML = `
                <div class="no-results">
                    <i class="fas fa-search"></i>
                    <h3>No items found</h3>
                    <p>Try adjusting your filters or search terms</p>
                </div>
            `;
            return;
        }

        const itemsHtml = this.filteredItems.map(item => this.renderItemCard(item)).join('');
        container.innerHTML = `
            <div class="loot-grid">
                ${itemsHtml}
            </div>
        `;
    }

    renderItemCard(item) {
        const category = this.lootData.categories[item.category];
        const rarityClass = `rarity-${item.rarity}`;
        
        const locationsHtml = item.locations.map(location => {
            const planet = this.lootData.locations[location.planet];
            const enemyType = this.lootData.enemy_types[location.enemy_type];
            const dropRatePercent = (location.drop_rate * 100).toFixed(1);
            
            return `
                <div class="location-item">
                    <div class="location-header">
                        <div class="location-name">${planet.name} - ${location.zone}</div>
                        <div class="drop-rate">${dropRatePercent}%</div>
                    </div>
                    <div class="enemy-info">
                        <i class="fas fa-skull"></i> ${location.enemy_name} (${enemyType.name})
                    </div>
                    <div class="enemy-info">
                        <i class="fas fa-calendar"></i> Last seen: ${new Date(location.last_seen).toLocaleDateString()}
                    </div>
                </div>
            `;
        }).join('');

        const sourcesHtml = item.sources.map(source => {
            const sourceClass = `source-${source.replace('_', '')}`;
            const sourceLabel = source.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
            return `<span class="source-badge ${sourceClass}">${sourceLabel}</span>`;
        }).join('');

        return `
            <div class="loot-card" data-item-id="${item.id}">
                <div class="loot-header">
                    <h3 class="loot-title">${item.name}</h3>
                    <span class="rarity-badge ${rarityClass}">${item.rarity}</span>
                </div>
                
                <div class="loot-info">
                    <div class="loot-description">${item.description}</div>
                    
                    <div class="loot-stats">
                        <div class="stat-item">
                            <i class="fas fa-coins"></i>
                            <span>${item.stats.value.toLocaleString()} credits</span>
                        </div>
                        <div class="stat-item">
                            <i class="fas fa-weight-hanging"></i>
                            <span>${item.stats.weight} kg</span>
                        </div>
                        <div class="stat-item">
                            <i class="fas fa-${category.icon}"></i>
                            <span>${category.name}</span>
                        </div>
                    </div>
                    
                    <div class="source-badges">
                        ${sourcesHtml}
                    </div>
                </div>
                
                <div class="drop-locations">
                    <h4><i class="fas fa-map-marker-alt"></i> Drop Locations</h4>
                    ${locationsHtml}
                </div>
                
                <button class="view-details-btn" onclick="viewItemDetails('${item.id}')">
                    <i class="fas fa-external-link-alt"></i> View Details
                </button>
            </div>
        `;
    }

    updateStats() {
        const stats = {
            totalItems: this.lootData.items.length,
            totalLocations: Object.keys(this.lootData.locations).length,
            totalBosses: Object.keys(this.lootData.boss_profiles).length,
            dataSources: this.lootData.metadata.data_sources.length
        };

        document.getElementById('totalItems').textContent = stats.totalItems;
        document.getElementById('totalLocations').textContent = stats.totalLocations;
        document.getElementById('totalBosses').textContent = stats.totalBosses;
        document.getElementById('dataSources').textContent = stats.dataSources;
    }

    showError(message) {
        const container = document.getElementById('resultsContainer');
        container.innerHTML = `
            <div class="no-results">
                <i class="fas fa-exclamation-triangle"></i>
                <h3>Error</h3>
                <p>${message}</p>
            </div>
        `;
    }
}

// Global function for item details
function viewItemDetails(itemId) {
    // This would open a modal or navigate to a detailed view
    console.log('Viewing details for item:', itemId);
    // For now, just show an alert
    alert(`Viewing details for item: ${itemId}\n\nThis would open a detailed view with:\n- Full item information\n- Boss profile links\n- Community comments\n- Drop history`);
}

// Initialize the viewer when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new RareLootViewer();
}); 