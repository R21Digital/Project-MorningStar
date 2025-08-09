module.exports = class {
  data() {
    return {
      title: "Build Calculator - SWGDB Tools",
      description: "Browse and analyze pre-made character builds for Star Wars Galaxies Restoration",
      layout: "base.11ty.js",
      permalink: "/tools/build-calculator/"
    };
  }

  render(data) {
    return `
    <style>
        .builds-hero {
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(30, 41, 59, 0.8) 100%);
            color: white;
            padding: 60px 0;
            text-align: center;
            border-radius: 12px;
            margin-bottom: 40px;
        }

        .builds-hero h1 {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 20px;
            color: #06b6d4;
            text-shadow: 0 0 20px rgba(6, 182, 212, 0.5);
        }

        .builds-hero p {
            font-size: 1.2rem;
            opacity: 0.9;
            max-width: 600px;
            margin: 0 auto;
            color: #e2e8f0;
        }

        .filters-section {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(6, 182, 212, 0.5);
            padding: 30px;
            margin-bottom: 30px;
            border-radius: 12px;
            box-shadow: 0 0 20px rgba(6, 182, 212, 0.3);
            backdrop-filter: blur(10px);
        }

        .filter-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }

        .filter-group {
            display: flex;
            flex-direction: column;
        }

        .filter-group label {
            font-weight: 600;
            margin-bottom: 5px;
            color: #06b6d4;
        }

        .filter-control {
            padding: 12px 16px;
            background: rgba(15, 23, 42, 0.8);
            border: 1px solid rgba(6, 182, 212, 0.5);
            border-radius: 8px;
            font-size: 14px;
            color: #e2e8f0;
            transition: all 0.3s ease;
        }

        .filter-control:focus {
            outline: none;
            border-color: #06b6d4;
            box-shadow: 0 0 10px rgba(6, 182, 212, 0.3);
        }

        .stats-bar {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(6, 182, 212, 0.5);
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 0 20px rgba(6, 182, 212, 0.3);
            margin-bottom: 30px;
            backdrop-filter: blur(10px);
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            text-align: center;
        }

        .stat-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 15px;
            background: rgba(15, 23, 42, 0.6);
            border-radius: 8px;
            border: 1px solid rgba(6, 182, 212, 0.3);
            transition: all 0.3s ease;
        }

        .stat-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(6, 182, 212, 0.3);
        }

        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            color: #06b6d4;
            margin-bottom: 5px;
        }

        .stat-label {
            font-size: 0.9rem;
            color: #e2e8f0;
            opacity: 0.8;
        }

        .build-card {
            background: rgba(30, 41, 59, 0.8);
            border: 1px solid rgba(6, 182, 212, 0.5);
            border-radius: 12px;
            box-shadow: 0 0 20px rgba(6, 182, 212, 0.3);
            margin-bottom: 25px;
            overflow: hidden;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }

        .build-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(6, 182, 212, 0.4);
        }

        .build-header {
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.2) 0%, rgba(30, 41, 59, 0.9) 100%);
            color: white;
            padding: 25px;
            border-bottom: 1px solid rgba(6, 182, 212, 0.3);
        }

        .build-title {
            font-size: 1.5rem;
            font-weight: 600;
            color: #06b6d4;
            margin-bottom: 8px;
        }

        .build-subtitle {
            color: #e2e8f0;
            font-size: 0.9rem;
            opacity: 0.8;
        }

        .build-content {
            padding: 25px;
        }

        .build-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }

        .build-stat {
            text-align: center;
            padding: 12px;
            background: rgba(15, 23, 42, 0.6);
            border-radius: 8px;
            border: 1px solid rgba(6, 182, 212, 0.2);
        }

        .build-stat-value {
            font-size: 1.2rem;
            font-weight: bold;
            color: #06b6d4;
        }

        .build-stat-label {
            font-size: 0.8rem;
            color: #e2e8f0;
            opacity: 0.8;
        }

        .build-description {
            color: #e2e8f0;
            line-height: 1.6;
            margin-bottom: 20px;
        }

        .build-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 20px;
        }

        .build-tag {
            background: rgba(6, 182, 212, 0.2);
            color: #06b6d4;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.8rem;
            border: 1px solid rgba(6, 182, 212, 0.3);
        }

        .build-actions {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }

        .action-btn {
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            position: relative;
            overflow: hidden;
        }

        .action-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s;
        }

        .action-btn:hover::before {
            left: 100%;
        }

        .btn-primary {
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.9) 0%, rgba(8, 145, 178, 0.9) 100%);
            color: white;
            border: 1px solid rgba(6, 182, 212, 0.6);
        }

        .btn-primary:hover {
            background: linear-gradient(135deg, rgba(8, 145, 178, 0.9) 0%, rgba(6, 182, 212, 0.9) 100%);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(6, 182, 212, 0.4);
        }

        .btn-secondary {
            background: linear-gradient(135deg, rgba(51, 65, 85, 0.9) 0%, rgba(30, 41, 59, 0.9) 100%);
            color: #e2e8f0;
            border: 1px solid rgba(6, 182, 212, 0.3);
        }

        .btn-secondary:hover {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(51, 65, 85, 0.9) 100%);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(6, 182, 212, 0.3);
        }

        .loading-spinner {
            text-align: center;
            padding: 60px;
            color: #06b6d4;
        }

        .loading-spinner i {
            font-size: 3rem;
            animation: spin 2s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>

    <section class="py-12 px-6 max-w-6xl mx-auto text-white relative z-10">
        <!-- Hero Section -->
        <div class="builds-hero">
            <h1><i class="fas fa-user-cog mr-4"></i>Build Calculator</h1>
            <p>Browse and analyze pre-made character builds for optimal performance</p>
        </div>

        <!-- Filters Section -->
        <div class="filters-section">
            <h3 class="text-xl font-bold text-swg-cyan mb-4">Build Filters</h3>
            <div class="filter-row">
                <div class="filter-group">
                    <label for="profession-filter">Profession</label>
                    <select id="profession-filter" class="filter-control">
                        <option value="">All Professions</option>
                        <option value="rifleman">Rifleman</option>
                        <option value="pistoleer">Pistoleer</option>
                        <option value="swordsman">Swordsman</option>
                        <option value="medic">Combat Medic</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label for="role-filter">Role</label>
                    <select id="role-filter" class="filter-control">
                        <option value="">All Roles</option>
                        <option value="dps">DPS</option>
                        <option value="tank">Tank</option>
                        <option value="support">Support</option>
                        <option value="hybrid">Hybrid</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label for="difficulty-filter">Difficulty</label>
                    <select id="difficulty-filter" class="filter-control">
                        <option value="">All Difficulties</option>
                        <option value="easy">Easy</option>
                        <option value="medium">Medium</option>
                        <option value="hard">Hard</option>
                    </select>
                </div>
            </div>
        </div>

        <!-- Stats Overview -->
        <div class="stats-bar">
            <h3 class="text-xl font-bold text-swg-cyan mb-4">Build Statistics</h3>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-value" id="total-builds">0</div>
                    <div class="stat-label">Total Builds</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="avg-rating">0.0</div>
                    <div class="stat-label">Avg Rating</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="top-builds">0</div>
                    <div class="stat-label">Top Rated</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="recent-builds">0</div>
                    <div class="stat-label">Recent</div>
                </div>
            </div>
        </div>

        <!-- Builds Grid -->
        <div id="builds-container">
            <div class="loading-spinner">
                <i class="fas fa-spinner"></i>
                <p style="margin-top: 20px;">Loading builds...</p>
            </div>
        </div>
    </section>

    <script>
        let builds = [];
        let filteredBuilds = [];

        // Sample build data
        const sampleBuilds = [
            {
                id: 1,
                title: "Elite Rifleman",
                subtitle: "High DPS, Long Range",
                profession: "rifleman",
                role: "dps",
                difficulty: "medium",
                rating: 4.8,
                description: "A high-damage rifleman build focused on long-range combat and accuracy. Perfect for PvE content and group play.",
                stats: {
                    damage: 95,
                    accuracy: 90,
                    defense: 60,
                    utility: 70
                },
                tags: ["PvE", "Group", "Long Range", "High DPS"]
            },
            {
                id: 2,
                title: "Tank Medic",
                subtitle: "Support & Survival",
                profession: "medic",
                role: "support",
                difficulty: "hard",
                rating: 4.6,
                description: "A hybrid medic build that combines healing abilities with tank-like survivability. Excellent for group content and solo play.",
                stats: {
                    damage: 40,
                    accuracy: 75,
                    defense: 95,
                    utility: 90
                },
                tags: ["Support", "Tank", "Group", "Solo"]
            },
            {
                id: 3,
                title: "Pistol Master",
                subtitle: "Fast & Furious",
                profession: "pistoleer",
                role: "dps",
                difficulty: "easy",
                rating: 4.4,
                description: "A fast-paced pistoleer build focused on rapid fire and mobility. Great for PvP and solo content.",
                stats: {
                    damage: 85,
                    accuracy: 80,
                    defense: 50,
                    utility: 65
                },
                tags: ["PvP", "Solo", "Fast", "Mobile"]
            }
        ];

        function loadBuilds() {
            builds = [...sampleBuilds];
            filteredBuilds = [...builds];
            renderBuilds();
            updateStats();
        }

        function renderBuilds() {
            const container = document.getElementById('builds-container');
            
            if (filteredBuilds.length === 0) {
                container.innerHTML = '<div class="text-center text-white py-12"><i class="fas fa-search fa-3x mb-4 text-swg-cyan"></i><p>No builds found matching your criteria.</p></div>';
                return;
            }

            container.innerHTML = filteredBuilds.map(build => 
                '<div class="build-card">' +
                    '<div class="build-header">' +
                        '<div class="build-title">' + build.title + '</div>' +
                        '<div class="build-subtitle">' + build.subtitle + '</div>' +
                    '</div>' +
                    '<div class="build-content">' +
                        '<div class="build-stats">' +
                            '<div class="build-stat">' +
                                '<div class="build-stat-value">' + build.stats.damage + '</div>' +
                                '<div class="build-stat-label">Damage</div>' +
                            '</div>' +
                            '<div class="build-stat">' +
                                '<div class="build-stat-value">' + build.stats.accuracy + '</div>' +
                                '<div class="build-stat-label">Accuracy</div>' +
                            '</div>' +
                            '<div class="build-stat">' +
                                '<div class="build-stat-value">' + build.stats.defense + '</div>' +
                                '<div class="build-stat-label">Defense</div>' +
                            '</div>' +
                            '<div class="build-stat">' +
                                '<div class="build-stat-value">' + build.stats.utility + '</div>' +
                                '<div class="build-stat-label">Utility</div>' +
                            '</div>' +
                        '</div>' +
                        '<div class="build-description">' + build.description + '</div>' +
                        '<div class="build-tags">' +
                            build.tags.map(tag => '<span class="build-tag">' + tag + '</span>').join('') +
                        '</div>' +
                        '<div class="build-actions">' +
                            '<button class="action-btn btn-primary" onclick="viewBuild(' + build.id + ')">' +
                                '<i class="fas fa-eye"></i>View Details' +
                            '</button>' +
                            '<button class="action-btn btn-secondary" onclick="exportBuild(' + build.id + ')">' +
                                '<i class="fas fa-download"></i>Export' +
                            '</button>' +
                        '</div>' +
                    '</div>' +
                '</div>'
            ).join('');
        }

        function updateStats() {
            document.getElementById('total-builds').textContent = builds.length;
            document.getElementById('avg-rating').textContent = (builds.reduce((sum, build) => sum + build.rating, 0) / builds.length).toFixed(1);
            document.getElementById('top-builds').textContent = builds.filter(build => build.rating >= 4.5).length;
            document.getElementById('recent-builds').textContent = builds.filter(build => build.id > builds.length - 3).length;
        }

        function filterBuilds() {
            const profession = document.getElementById('profession-filter').value;
            const role = document.getElementById('role-filter').value;
            const difficulty = document.getElementById('difficulty-filter').value;

            filteredBuilds = builds.filter(build => {
                return (!profession || build.profession === profession) &&
                       (!role || build.role === role) &&
                       (!difficulty || build.difficulty === difficulty);
            });

            renderBuilds();
        }

        function viewBuild(buildId) {
            const build = builds.find(b => b.id === buildId);
            if (build) {
                alert('Viewing build: ' + build.title + '\n\nThis would open a detailed view of the build.');
            }
        }

        function exportBuild(buildId) {
            const build = builds.find(b => b.id === buildId);
            if (build) {
                const dataStr = JSON.stringify(build, null, 2);
                const dataBlob = new Blob([dataStr], {type: 'application/json'});
                const url = URL.createObjectURL(dataBlob);
                const link = document.createElement('a');
                link.href = url;
                link.download = 'swg-build-' + build.title.toLowerCase().replace(/\s+/g, '-') + '.json';
                link.click();
            }
        }

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            loadBuilds();
            
            // Add event listeners for filters
            document.getElementById('profession-filter').addEventListener('change', filterBuilds);
            document.getElementById('role-filter').addEventListener('change', filterBuilds);
            document.getElementById('difficulty-filter').addEventListener('change', filterBuilds);
        });
    </script>
    `;
  }
};