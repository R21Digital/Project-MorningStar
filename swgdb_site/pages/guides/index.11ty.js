module.exports = class {
  data() {
    return {
      title: "Guides - SWGDB",
      description: "Comprehensive guides for Star Wars Galaxies Restoration - builds, PvP tactics, farming strategies, and more",
      layout: "base.njk",
      permalink: "/guides/"
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
    <style>
        :root {
            --primary-color: #667eea;
            --secondary-color: #764ba2;
            --accent-color: #28a745;
            --dark-color: #333;
            --light-color: #f8f9fa;
        }

        .guides-hero {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 60px 0;
            text-align: center;
        }

        .guides-hero h1 {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 20px;
        }

        .guides-hero p {
            font-size: 1.2rem;
            opacity: 0.9;
            max-width: 600px;
            margin: 0 auto;
        }

        .guides-section {
            padding: 60px 0;
        }

        .category-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            margin-top: 40px;
        }

        .category-card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            padding: 30px;
            text-align: center;
            transition: all 0.3s ease;
            border: 2px solid transparent;
        }

        .category-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
            border-color: var(--primary-color);
        }

        .category-icon {
            font-size: 3rem;
            color: var(--primary-color);
            margin-bottom: 20px;
        }

        .category-title {
            font-size: 1.4rem;
            font-weight: 600;
            color: var(--dark-color);
            margin-bottom: 15px;
        }

        .category-description {
            color: #666;
            margin-bottom: 25px;
            line-height: 1.6;
        }

        .category-link {
            background: var(--primary-color);
            color: white;
            padding: 12px 25px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.3s ease;
            display: inline-block;
        }

        .category-link:hover {
            background: var(--secondary-color);
            color: white;
            transform: scale(1.05);
        }

        .stats-section {
            background: var(--light-color);
            padding: 40px 0;
            text-align: center;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }

        .stat-item {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }

        .stat-number {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--primary-color);
        }

        .stat-label {
            color: #666;
            font-size: 0.9rem;
            margin-top: 5px;
        }

        @media (max-width: 768px) {
            .guides-hero h1 {
                font-size: 2rem;
            }
            
            .guides-hero p {
                font-size: 1rem;
            }
            
            .category-grid {
                grid-template-columns: 1fr;
                gap: 20px;
            }
        }
    </style>
</head>
<body>
    <div class="guides-hero">
        <div class="container">
            <h1><i class="fas fa-book-open"></i> SWGDB Guides</h1>
            <p>Master Star Wars Galaxies with our comprehensive collection of builds, strategies, and tutorials</p>
        </div>
    </div>

    <div class="guides-section">
        <div class="container">
            <div class="category-grid">
                <div class="category-card">
                    <div class="category-icon">
                        <i class="fas fa-sword"></i>
                    </div>
                    <h3 class="category-title">Combat Builds</h3>
                    <p class="category-description">Optimized builds for PvP and PvE combat, including weapon specializations and tactical strategies.</p>
                    <a href="/guides/combat-builds/" class="category-link">
                        View Combat Builds <i class="fas fa-arrow-right"></i>
                    </a>
                </div>

                <div class="category-card">
                    <div class="category-icon">
                        <i class="fas fa-hammer"></i>
                    </div>
                    <h3 class="category-title">Crafter Builds</h3>
                    <p class="category-description">Master crafting professions with specialized builds for creating the best gear and items.</p>
                    <a href="/guides/crafter-builds/" class="category-link">
                        View Crafter Builds <i class="fas fa-arrow-right"></i>
                    </a>
                </div>

                <div class="category-card">
                    <div class="category-icon">
                        <i class="fas fa-music"></i>
                    </div>
                    <h3 class="category-title">Entertainer Builds</h3>
                    <p class="category-description">Specialized builds for dancers and musicians to maximize entertainment and buff capabilities.</p>
                    <a href="/guides/entertainer-builds/" class="category-link">
                        View Entertainer Builds <i class="fas fa-arrow-right"></i>
                    </a>
                </div>

                <div class="category-card">
                    <div class="category-icon">
                        <i class="fas fa-hand-sparkles"></i>
                    </div>
                    <h3 class="category-title">Force Sensitive Builds</h3>
                    <p class="category-description">Jedi and Force-sensitive character builds focusing on Force powers and lightsaber combat.</p>
                    <a href="/guides/force-sensitive-builds/" class="category-link">
                        View Force Builds <i class="fas fa-arrow-right"></i>
                    </a>
                </div>

                <div class="category-card">
                    <div class="category-icon">
                        <i class="fas fa-crosshairs"></i>
                    </div>
                    <h3 class="category-title">PvP Fundamentals</h3>
                    <p class="category-description">Essential PvP tactics, positioning, and strategies for player versus player combat.</p>
                    <a href="/guides/pvp-fundamentals/" class="category-link">
                        View PvP Guides <i class="fas fa-arrow-right"></i>
                    </a>
                </div>

                <div class="category-card">
                    <div class="category-icon">
                        <i class="fas fa-users"></i>
                    </div>
                    <h3 class="category-title">Group PvP Tactics</h3>
                    <p class="category-description">Advanced group coordination, roles, and tactics for large-scale PvP battles.</p>
                    <a href="/guides/group-pvp-tactics/" class="category-link">
                        View Group Tactics <i class="fas fa-arrow-right"></i>
                    </a>
                </div>

                <div class="category-card">
                    <div class="category-icon">
                        <i class="fas fa-home"></i>
                    </div>
                    <h3 class="category-title">Base Busting</h3>
                    <p class="category-description">Strategies and builds for attacking and defending player bases and cities.</p>
                    <a href="/guides/base-busting/" class="category-link">
                        View Base Guides <i class="fas fa-arrow-right"></i>
                    </a>
                </div>

                <div class="category-card">
                    <div class="category-icon">
                        <i class="fas fa-coins"></i>
                    </div>
                    <h3 class="category-title">Credit Farming</h3>
                    <p class="category-description">Efficient methods and locations for earning credits through various activities.</p>
                    <a href="/guides/credit-farming/" class="category-link">
                        View Credit Guides <i class="fas fa-arrow-right"></i>
                    </a>
                </div>

                <div class="category-card">
                    <div class="category-icon">
                        <i class="fas fa-gem"></i>
                    </div>
                    <h3 class="category-title">Resource Harvesting</h3>
                    <p class="category-description">Master resource extraction and harvesting for crafting and trading purposes.</p>
                    <a href="/guides/resource-harvesting/" class="category-link">
                        View Resource Guides <i class="fas fa-arrow-right"></i>
                    </a>
                </div>

                <div class="category-card">
                    <div class="category-icon">
                        <i class="fas fa-treasure-chest"></i>
                    </div>
                    <h3 class="category-title">Rare Loot Farming</h3>
                    <p class="category-description">Locations, strategies, and builds for farming rare and valuable loot items.</p>
                    <a href="/guides/rare-loot-farming/" class="category-link">
                        View Loot Guides <i class="fas fa-arrow-right"></i>
                    </a>
                </div>

                <div class="category-card">
                    <div class="category-icon">
                        <i class="fas fa-rocket"></i>
                    </div>
                    <h3 class="category-title">New Player Guides</h3>
                    <p class="category-description">Essential guides for beginners to get started and progress efficiently in SWG.</p>
                    <a href="/guides/new-player-guides/" class="category-link">
                        View Beginner Guides <i class="fas fa-arrow-right"></i>
                    </a>
                </div>

                <div class="category-card">
                    <div class="category-icon">
                        <i class="fas fa-chart-line"></i>
                    </div>
                    <h3 class="category-title">Character Maximization</h3>
                    <p class="category-description">Advanced strategies for optimizing character stats, skills, and overall performance.</p>
                    <a href="/guides/character-maximization/" class="category-link">
                        View Optimization Guides <i class="fas fa-arrow-right"></i>
                    </a>
                </div>

                <div class="category-card">
                    <div class="category-icon">
                        <i class="fas fa-graduation-cap"></i>
                    </div>
                    <h3 class="category-title">Profession Overviews</h3>
                    <p class="category-description">Comprehensive overviews of all professions, their strengths, and typical builds.</p>
                    <a href="/guides/profession-overviews/" class="category-link">
                        View Profession Guides <i class="fas fa-arrow-right"></i>
                    </a>
                </div>
            </div>
        </div>
    </div>

    <div class="stats-section">
        <div class="container">
            <h2>Guide Statistics</h2>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-number">13</div>
                    <div class="stat-label">Guide Categories</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">2</div>
                    <div class="stat-label">Published Guides</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">∞</div>
                    <div class="stat-label">More Coming Soon</div>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
    `;
  }
};