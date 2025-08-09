/**
 * Static Builds Viewer
 * Handles the display and interaction of the static builds library
 */
class StaticBuildsViewer {
    constructor() {
        this.builds = [];
        this.filteredBuilds = [];
        this.categories = {};
        this.professions = {};
        this.filters = {
            category: '',
            profession: '',
            difficulty: '',
            specialization: '',
            rating: '',
            search: '',
            sort: 'rating'
        };
        
        this.init();
    }

    async init() {
        try {
            await this.loadBuildsData();
            this.setupEventListeners();
            this.populateFilterOptions();
            this.applyFilters();
            this.updateStats();
            this.hideLoading();
        } catch (error) {
            console.error('Error initializing builds viewer:', error);
            this.showError('Failed to load builds data');
        }
    }

    async loadBuildsData() {
        try {
            const response = await fetch('../data/static_builds_database.json');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            
            this.builds = data.builds || [];
            this.categories = data.categories || {};
            this.professions = data.professions || {};
            
            // Update metadata
            if (data.metadata) {
                data.metadata.total_builds = this.builds.length;
                data.metadata.total_professions = Object.keys(this.professions).length;
            }
            
        } catch (error) {
            console.error('Error loading builds data:', error);
            // Fallback to demo data
            this.builds = this.getDemoData().builds;
            this.categories = this.getDemoData().categories;
            this.professions = this.getDemoData().professions;
        }
    }

    getDemoData() {
        return {
            builds: [
                {
                    id: "rifleman_medic_001",
                    name: "Rifleman/Medic",
                    description: "Versatile combat build combining ranged damage with healing capabilities",
                    category: "combat",
                    difficulty: "medium",
                    specialization: "pve",
                    professions: {
                        primary: "rifleman",
                        secondary: "medic"
                    },
                    skill_trees: {
                        rifleman: [
                            "combat_marksman_novice",
                            "combat_rifleman_novice",
                            "combat_rifleman_marksman",
                            "combat_rifleman_rifleman",
                            "combat_rifleman_sniper",
                            "combat_rifleman_master"
                        ],
                        medic: [
                            "science_medic_novice",
                            "science_medic_healing",
                            "science_medic_medicine",
                            "science_medic_doctor",
                            "science_medic_master"
                        ]
                    },
                    buff_priority: [
                        "accuracy",
                        "damage",
                        "critical",
                        "healing",
                        "defense"
                    ],
                    weapon_type: "rifle",
                    performance: {
                        pve_rating: 8.5,
                        pvp_rating: 6.0,
                        solo_rating: 9.0,
                        group_rating: 8.0,
                        farming_rating: 7.5
                    },
                    rating: {
                        average: 8.2,
                        total_votes: 45,
                        votes: {
                            "5": 20,
                            "4": 15,
                            "3": 8,
                            "2": 2,
                            "1": 0
                        }
                    },
                    attribution: {
                        type: "ai_generated",
                        generated_by: "SWGDB",
                        verified_by: "community",
                        last_verified: "2024-12-15T10:30:00"
                    },
                    skill_calculator_url: "https://swgr.org/calculator/rifleman-medic",
                    created: "2024-01-15T09:00:00",
                    updated: "2024-12-15T10:30:00"
                }
            ],
            categories: {
                combat: {
                    name: "Combat",
                    description: "Combat-focused builds for PvE and PvP",
                    icon: "sword",
                    color: "#dc3545"
                },
                support: {
                    name: "Support",
                    description: "Healing and support builds",
                    icon: "heart",
                    color: "#e83e8c"
                },
                utility: {
                    name: "Utility",
                    description: "Exploration and utility builds",
                    icon: "compass",
                    color: "#6f42c1"
                },
                crafting: {
                    name: "Crafting",
                    description: "Crafting and resource gathering builds",
                    icon: "hammer",
                    color: "#ffc107"
                },
                social: {
                    name: "Social",
                    description: "Social interaction and buff builds",
                    icon: "music",
                    color: "#17a2b8"
                }
            },
            professions: {
                rifleman: {
                    name: "Rifleman",
                    category: "combat",
                    description: "Ranged combat specialist with high accuracy and damage",
                    icon: "crosshairs",
                    color: "#dc3545",
                    primary_weapon: "rifle",
                    secondary_weapon: "carbine"
                },
                medic: {
                    name: "Medic",
                    category: "support",
                    description: "Healing and support specialist",
                    icon: "heart",
                    color: "#e83e8c",
                    primary_weapon: "pistol",
                    secondary_weapon: "carbine"
                }
            }
        };
    }

    setupEventListeners() {
        // Filter change events
        document.getElementById('categoryFilter').addEventListener('change', (e) => {
            this.filters.category = e.target.value;
            this.applyFilters();
        });

        document.getElementById('professionFilter').addEventListener('change', (e) => {
            this.filters.profession = e.target.value;
            this.applyFilters();
        });

        document.getElementById('difficultyFilter').addEventListener('change', (e) => {
            this.filters.difficulty = e.target.value;
            this.applyFilters();
        });

        document.getElementById('specializationFilter').addEventListener('change', (e) => {
            this.filters.specialization = e.target.value;
            this.applyFilters();
        });

        document.getElementById('ratingFilter').addEventListener('change', (e) => {
            this.filters.rating = e.target.value;
            this.applyFilters();
        });

        document.getElementById('sortFilter').addEventListener('change', (e) => {
            this.filters.sort = e.target.value;
            this.applyFilters();
        });

        // Search input
        document.getElementById('searchBox').addEventListener('input', (e) => {
            this.filters.search = e.target.value.toLowerCase();
            this.applyFilters();
        });

        // Reset filters
        document.getElementById('resetFilters').addEventListener('click', () => {
            this.resetFilters();
        });

        // Quick filter buttons
        this.setupQuickFilters();
    }

    setupQuickFilters() {
        const quickFiltersContainer = document.getElementById('quickFilters');
        const quickFilters = [
            { label: 'Combat', value: 'combat', type: 'category' },
            { label: 'Support', value: 'support', type: 'category' },
            { label: 'Easy', value: 'easy', type: 'difficulty' },
            { label: 'PvE', value: 'pve', type: 'specialization' },
            { label: 'High Rating', value: '8', type: 'rating' }
        ];

        quickFilters.forEach(filter => {
            const button = document.createElement('button');
            button.className = 'quick-filter-btn';
            button.textContent = filter.label;
            button.addEventListener('click', () => {
                this.applyQuickFilter(filter.type, filter.value);
            });
            quickFiltersContainer.appendChild(button);
        });
    }

    applyQuickFilter(type, value) {
        // Clear other filters of the same type
        this.filters[type] = '';
        
        // Set the new filter
        this.filters[type] = value;
        
        // Update UI
        this.updateFilterUI();
        this.applyFilters();
    }

    updateFilterUI() {
        document.getElementById('categoryFilter').value = this.filters.category;
        document.getElementById('professionFilter').value = this.filters.profession;
        document.getElementById('difficultyFilter').value = this.filters.difficulty;
        document.getElementById('specializationFilter').value = this.filters.specialization;
        document.getElementById('ratingFilter').value = this.filters.rating;
        document.getElementById('sortFilter').value = this.filters.sort;
    }

    populateFilterOptions() {
        // Populate category filter
        const categoryFilter = document.getElementById('categoryFilter');
        Object.keys(this.categories).forEach(categoryKey => {
            const category = this.categories[categoryKey];
            const option = document.createElement('option');
            option.value = categoryKey;
            option.textContent = category.name;
            categoryFilter.appendChild(option);
        });

        // Populate profession filter
        const professionFilter = document.getElementById('professionFilter');
        Object.keys(this.professions).forEach(professionKey => {
            const profession = this.professions[professionKey];
            const option = document.createElement('option');
            option.value = professionKey;
            option.textContent = profession.name;
            professionFilter.appendChild(option);
        });
    }

    applyFilters() {
        this.filteredBuilds = this.builds.filter(build => {
            // Category filter
            if (this.filters.category && build.category !== this.filters.category) {
                return false;
            }

            // Profession filter
            if (this.filters.profession) {
                const hasProfession = build.professions.primary === this.filters.profession || 
                                   build.professions.secondary === this.filters.profession;
                if (!hasProfession) {
                    return false;
                }
            }

            // Difficulty filter
            if (this.filters.difficulty && build.difficulty !== this.filters.difficulty) {
                return false;
            }

            // Specialization filter
            if (this.filters.specialization && build.specialization !== this.filters.specialization) {
                return false;
            }

            // Rating filter
            if (this.filters.rating && build.rating.average < parseFloat(this.filters.rating)) {
                return false;
            }

            // Search filter
            if (this.filters.search) {
                const searchText = this.filters.search.toLowerCase();
                const searchableText = [
                    build.name,
                    build.description,
                    ...Object.values(build.skill_trees).flat(),
                    ...build.buff_priority
                ].join(' ').toLowerCase();
                
                if (!searchableText.includes(searchText)) {
                    return false;
                }
            }

            return true;
        });

        this.sortBuilds();
        this.renderBuilds();
        this.updateResultsCount();
    }

    sortBuilds() {
        const sortBy = this.filters.sort;
        
        this.filteredBuilds.sort((a, b) => {
            switch (sortBy) {
                case 'rating':
                    return b.rating.average - a.rating.average;
                case 'name':
                    return a.name.localeCompare(b.name);
                case 'difficulty':
                    const difficultyOrder = { 'easy': 1, 'medium': 2, 'hard': 3 };
                    return difficultyOrder[a.difficulty] - difficultyOrder[b.difficulty];
                case 'recent':
                    return new Date(b.updated) - new Date(a.updated);
                default:
                    return 0;
            }
        });
    }

    renderBuilds() {
        const container = document.getElementById('buildsContainer');
        container.innerHTML = '';

        if (this.filteredBuilds.length === 0) {
            document.getElementById('noResultsMessage').style.display = 'block';
            return;
        }

        document.getElementById('noResultsMessage').style.display = 'none';

        this.filteredBuilds.forEach(build => {
            const buildCard = this.createBuildCard(build);
            container.appendChild(buildCard);
        });
    }

    createBuildCard(build) {
        const card = document.createElement('div');
        card.className = 'build-card';

        const primaryProfession = this.professions[build.professions.primary];
        const secondaryProfession = this.professions[build.professions.secondary];

        card.innerHTML = `
            <div class="build-header">
                <div class="build-title">${build.name}</div>
                <div class="build-description">${build.description}</div>
                <div class="build-meta">
                    <span class="build-tag tag-${build.category}">${this.categories[build.category]?.name || build.category}</span>
                    <span class="build-tag tag-${build.difficulty}">${build.difficulty}</span>
                    <span class="build-tag tag-${build.specialization}">${build.specialization}</span>
                    <span class="attribution-badge badge-${build.attribution.type === 'ai_generated' ? 'ai' : 'player'}">
                        <i class="fas fa-${build.attribution.type === 'ai_generated' ? 'robot' : 'user'}"></i>
                        ${build.attribution.type === 'ai_generated' ? 'AI Generated' : 'Player Submitted'}
                    </span>
                </div>
            </div>
            <div class="build-body">
                <div class="profession-info">
                    <div class="profession-icon" style="background-color: ${primaryProfession?.color || '#007bff'}">
                        <i class="fas fa-${primaryProfession?.icon || 'user'}"></i>
                    </div>
                    <div class="profession-details">
                        <h4>${primaryProfession?.name || build.professions.primary}</h4>
                        <p>${primaryProfession?.description || ''}</p>
                    </div>
                </div>
                
                <div class="build-stats">
                    <div class="stat-group">
                        <h5>Performance</h5>
                        <ul class="stat-list">
                            <li>PvE Rating <span class="stat-value">${build.performance.pve_rating}/10</span></li>
                            <li>PvP Rating <span class="stat-value">${build.performance.pvp_rating}/10</span></li>
                            <li>Solo Rating <span class="stat-value">${build.performance.solo_rating}/10</span></li>
                            <li>Group Rating <span class="stat-value">${build.performance.group_rating}/10</span></li>
                        </ul>
                    </div>
                    <div class="stat-group">
                        <h5>Combat</h5>
                        <ul class="stat-list">
                            <li>Weapon Type <span class="stat-value">${build.weapon_type}</span></li>
                            <li>Style <span class="stat-value">${build.combat?.style || 'N/A'}</span></li>
                            <li>Max Range <span class="stat-value">${build.combat?.max_range || 'N/A'}</span></li>
                            <li>Heal Threshold <span class="stat-value">${build.combat?.heal_threshold || 'N/A'}%</span></li>
                        </ul>
                    </div>
                </div>
                
                <div class="build-rating">
                    <div class="rating-stars">
                        ${this.generateStars(build.rating.average)}
                    </div>
                    <div class="rating-text">
                        ${build.rating.average.toFixed(1)} (${build.rating.total_votes} votes)
                    </div>
                </div>
                
                <div class="build-actions">
                    <a href="${build.skill_calculator_url}" class="btn btn-primary" target="_blank">
                        <i class="fas fa-calculator"></i> Skill Calculator
                    </a>
                    <button class="btn btn-outline" onclick="viewBuildDetails('${build.id}')">
                        <i class="fas fa-eye"></i> View Details
                    </button>
                </div>
            </div>
        `;

        return card;
    }

    generateStars(rating) {
        const fullStars = Math.floor(rating);
        const hasHalfStar = rating % 1 >= 0.5;
        const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

        let stars = '';
        
        // Full stars
        for (let i = 0; i < fullStars; i++) {
            stars += '<i class="fas fa-star star"></i>';
        }
        
        // Half star
        if (hasHalfStar) {
            stars += '<i class="fas fa-star-half-alt star"></i>';
        }
        
        // Empty stars
        for (let i = 0; i < emptyStars; i++) {
            stars += '<i class="fas fa-star star empty"></i>';
        }
        
        return stars;
    }

    updateResultsCount() {
        const countElement = document.getElementById('resultsCount');
        countElement.textContent = `Showing ${this.filteredBuilds.length} of ${this.builds.length} builds`;
    }

    updateStats() {
        const totalBuilds = this.builds.length;
        const totalProfessions = Object.keys(this.professions).length;
        
        const avgRating = this.builds.length > 0 
            ? (this.builds.reduce((sum, build) => sum + build.rating.average, 0) / this.builds.length).toFixed(1)
            : '0.0';
        
        const totalVotes = this.builds.reduce((sum, build) => sum + build.rating.total_votes, 0);

        document.getElementById('totalBuilds').textContent = totalBuilds;
        document.getElementById('totalProfessions').textContent = totalProfessions;
        document.getElementById('avgRating').textContent = avgRating;
        document.getElementById('totalVotes').textContent = totalVotes;
    }

    resetFilters() {
        this.filters = {
            category: '',
            profession: '',
            difficulty: '',
            specialization: '',
            rating: '',
            search: '',
            sort: 'rating'
        };

        this.updateFilterUI();
        this.applyFilters();
        
        // Clear search box
        document.getElementById('searchBox').value = '';
    }

    hideLoading() {
        document.getElementById('loadingMessage').style.display = 'none';
    }

    showError(message) {
        const container = document.getElementById('buildsContainer');
        container.innerHTML = `
            <div class="no-results">
                <i class="fas fa-exclamation-triangle"></i>
                <h4>Error</h4>
                <p>${message}</p>
            </div>
        `;
        document.getElementById('loadingMessage').style.display = 'none';
    }
}

// Global function for viewing build details
function viewBuildDetails(buildId) {
    // This would open a detailed view of the build
    // For now, we'll just show an alert
    alert(`Viewing details for build: ${buildId}`);
}

// Initialize the viewer when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new StaticBuildsViewer();
}); 