module.exports = class {
  data() {
    return {
      title: "SWGDB - Star Wars Galaxies Database",
      description: "Complete database and tools for Star Wars Galaxies Restoration including guides, heroics, loot tables, and community tools",
      layout: "base.njk",
      permalink: "/"
    };
  }

  render(data) {
    return `
    <style>
        .hero-section {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 100px 0;
            text-align: center;
            position: relative;
            overflow: hidden;
        }

        .hero-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="stars" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="10" cy="10" r="1" fill="%23ffffff" opacity="0.3"/></pattern></defs><rect width="100" height="100" fill="url(%23stars)"/></svg>') repeat;
            opacity: 0.1;
        }

        .hero-content {
            position: relative;
            z-index: 2;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        .hero-section h1 {
            font-size: 4rem;
            font-weight: 700;
            margin-bottom: 20px;
            text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.5);
            font-family: 'Inter', sans-serif;
        }

        .hero-section .subtitle {
            font-size: 1.4rem;
            opacity: 0.9;
            margin-bottom: 40px;
            max-width: 600px;
            margin-left: auto;
            margin-right: auto;
        }

        .hero-stats {
            display: flex;
            justify-content: center;
            gap: 40px;
            margin-top: 40px;
            flex-wrap: wrap;
        }

        .hero-stat {
            text-align: center;
            background: rgba(255, 255, 255, 0.1);
            padding: 20px;
            border-radius: 12px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .hero-stat-number {
            font-size: 2.5rem;
            font-weight: 700;
            display: block;
            margin-bottom: 5px;
        }

        .hero-stat-label {
            font-size: 0.9rem;
            opacity: 0.8;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .content-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 60px 20px;
        }

        .section-header {
            text-align: center;
            margin-bottom: 50px;
        }

        .section-header h2 {
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--text-color);
            margin-bottom: 15px;
        }

        .section-header p {
            font-size: 1.2rem;
            color: #666;
            max-width: 600px;
            margin: 0 auto;
        }

        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            margin-bottom: 80px;
        }

        .feature-card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            padding: 35px;
            text-decoration: none;
            color: inherit;
            transition: all 0.3s ease;
            border: 1px solid var(--border-color);
            position: relative;
            overflow: hidden;
        }

        .feature-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        }

        .feature-card:hover {
            transform: translateY(-10px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
            text-decoration: none;
            color: inherit;
        }

        .feature-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            border-radius: 12px;
            margin-bottom: 20px;
            font-size: 1.5rem;
            color: white;
        }

        .feature-card h3 {
            font-size: 1.6rem;
            font-weight: 600;
            margin-bottom: 15px;
            color: var(--text-color);
        }

        .feature-card p {
            font-size: 1rem;
            line-height: 1.6;
            color: #666;
            margin-bottom: 20px;
        }

        .feature-highlights {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .feature-highlight {
            background: rgba(102, 126, 234, 0.1);
            color: var(--primary-color);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
        }

        .quick-links {
            background: var(--light-color);
            border-radius: 15px;
            padding: 40px;
            margin: 60px 0;
        }

        .quick-links h3 {
            text-align: center;
            font-size: 2rem;
            margin-bottom: 30px;
            color: var(--text-color);
        }

        .quick-links-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
        }

        .quick-link {
            background: white;
            border-radius: 10px;
            padding: 20px;
            text-decoration: none;
            color: var(--text-color);
            text-align: center;
            transition: all 0.3s ease;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
        }

        .quick-link:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
            text-decoration: none;
            color: var(--text-color);
        }

        .quick-link i {
            font-size: 2rem;
            color: var(--primary-color);
            margin-bottom: 10px;
        }

        .quick-link h4 {
            margin: 0;
            font-size: 1.1rem;
            font-weight: 600;
        }

        .status-banner {
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(40, 167, 69, 0.2);
        }

        .status-banner i {
            margin-right: 8px;
        }

        @media (max-width: 768px) {
            .hero-section h1 {
                font-size: 2.5rem;
            }

            .hero-section .subtitle {
                font-size: 1.1rem;
            }

            .hero-stats {
                gap: 20px;
            }

            .hero-stat {
                padding: 15px;
                min-width: 120px;
            }

            .section-header h2 {
                font-size: 2rem;
            }

            .features-grid {
                grid-template-columns: 1fr;
                gap: 20px;
            }

            .content-container {
                padding: 40px 15px;
            }
        }
    </style>
    <div class="status-banner">
        <i class="fas fa-check-circle"></i>
        All systems operational - Join the community on Discord for live updates and events!
    </div>

    <section class="hero-section">
        <div class="hero-content">
            <h1>SWGDB</h1>
            <p class="subtitle">
                The ultimate Star Wars Galaxies Restoration database and community hub
            </p>
            <div class="hero-stats">
                <div class="hero-stat">
                    <span class="hero-stat-number">50+</span>
                    <span class="hero-stat-label">Interactive Tools</span>
                </div>
                <div class="hero-stat">
                    <span class="hero-stat-number">200+</span>
                    <span class="hero-stat-label">Detailed Guides</span>
                </div>
                <div class="hero-stat">
                    <span class="hero-stat-number">15+</span>
                    <span class="hero-stat-label">Heroic Instances</span>
                </div>
                <div class="hero-stat">
                    <span class="hero-stat-number">∞</span>
                    <span class="hero-stat-label">Community Driven</span>
                </div>
            </div>
        </div>
    </section>

    <div class="content-container">
        <div class="section-header">
            <h2>Everything You Need for SWG</h2>
            <p>From beginner guides to advanced heroic strategies, we've got your galactic adventure covered</p>
        </div>

        <div class="features-grid">
            <a href="/pages/tools/" class="feature-card">
                <div class="feature-icon">
                    <i class="fas fa-tools"></i>
                </div>
                <h3>Interactive Tools</h3>
                <p>Advanced calculators, planners, and utilities to optimize your gameplay experience. From skill calculators to loot trackers, everything you need is here.</p>
                <div class="feature-highlights">
                    <span class="feature-highlight">Skill Calculator</span>
                    <span class="feature-highlight">GCW Simulator</span>
                    <span class="feature-highlight">Loot Tracker</span>
                    <span class="feature-highlight">Build Planner</span>
                </div>
            </a>

            <a href="/pages/guides/" class="feature-card">
                <div class="feature-icon">
                    <i class="fas fa-book"></i>
                </div>
                <h3>Comprehensive Guides</h3>
                <p>Expert-written guides covering every aspect of Star Wars Galaxies. From combat builds to crafting mastery, level up your knowledge.</p>
                <div class="feature-highlights">
                    <span class="feature-highlight">Combat Builds</span>
                    <span class="feature-highlight">PvP Tactics</span>
                    <span class="feature-highlight">Credit Farming</span>
                    <span class="feature-highlight">New Player</span>
                </div>
            </a>

            <a href="/pages/heroics/" class="feature-card">
                <div class="feature-icon">
                    <i class="fas fa-dragon"></i>
                </div>
                <h3>Heroic Instances</h3>
                <p>Complete database of heroic encounters with detailed strategies, boss mechanics, and loot tables. Master the galaxy's toughest challenges.</p>
                <div class="feature-highlights">
                    <span class="feature-highlight">Boss Strategies</span>
                    <span class="feature-highlight">Loot Tables</span>
                    <span class="feature-highlight">Group Comp</span>
                    <span class="feature-highlight">Live Data</span>
                </div>
            </a>

            <a href="/pages/loot/" class="feature-card">
                <div class="feature-icon">
                    <i class="fas fa-gem"></i>
                </div>
                <h3>Loot Database</h3>
                <p>Searchable database of items, drop rates, and locations. Track your collection progress and find exactly what you're looking for.</p>
                <div class="feature-highlights">
                    <span class="feature-highlight">Drop Rates</span>
                    <span class="feature-highlight">Item Search</span>
                    <span class="feature-highlight">Collections</span>
                    <span class="feature-highlight">Rare Items</span>
                </div>
            </a>

            <a href="/pages/leaderboard/" class="feature-card">
                <div class="feature-icon">
                    <i class="fas fa-trophy"></i>
                </div>
                <h3>Community Rankings</h3>
                <p>Competitive leaderboards and player statistics. See how you stack up against the best players in the galaxy.</p>
                <div class="feature-highlights">
                    <span class="feature-highlight">PvP Rankings</span>
                    <span class="feature-highlight">BH Leaderboard</span>
                    <span class="feature-highlight">Guild Stats</span>
                    <span class="feature-highlight">Achievements</span>
                </div>
            </a>

            <a href="/pages/report-bug.html" class="feature-card">
                <div class="feature-icon">
                    <i class="fas fa-users"></i>
                </div>
                <h3>Community Hub</h3>
                <p>Built by players, for players. Join our community to share knowledge, report issues, and help improve SWGDB for everyone.</p>
                <div class="feature-highlights">
                    <span class="feature-highlight">Bug Reports</span>
                    <span class="feature-highlight">Suggestions</span>
                    <span class="feature-highlight">Discord</span>
                    <span class="feature-highlight">Open Source</span>
                </div>
            </a>
        </div>

        <div class="quick-links">
            <h3>Popular Resources</h3>
            <div class="quick-links-grid">
                <a href="/pages/tools/skill-calculator/" class="quick-link">
                    <i class="fas fa-calculator"></i>
                    <h4>Skill Calculator</h4>
                </a>
                <a href="/pages/heroics/axkva-min/" class="quick-link">
                    <i class="fas fa-mask"></i>
                    <h4>Axkva Min Guide</h4>
                </a>
                <a href="/pages/guides/combat-builds/" class="quick-link">
                    <i class="fas fa-sword"></i>
                    <h4>Combat Builds</h4>
                </a>
                <a href="/pages/tools/gcw-calculator/" class="quick-link">
                    <i class="fas fa-globe"></i>
                    <h4>GCW Calculator</h4>
                </a>
                <a href="/pages/tools/loot-tracker.html" class="quick-link">
                    <i class="fas fa-crosshairs"></i>
                    <h4>Loot Tracker</h4>
                </a>
                <a href="/pages/leaderboard/" class="quick-link">
                    <i class="fas fa-trophy"></i>
                    <h4>Rankings</h4>
                </a>
            </div>
        </div>
    </div>

    <script>
        // Add some interactive elements
        document.addEventListener('DOMContentLoaded', function() {
            // Animate hero stats on scroll
            const heroStats = document.querySelectorAll('.hero-stat-number');
            
            const animateNumbers = (entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const target = entry.target;
                        const finalText = target.textContent;
                        
                        if (finalText !== '∞') {
                            const finalNumber = parseInt(finalText.replace('+', ''));
                            let currentNumber = 0;
                            const increment = finalNumber / 20;
                            
                            const timer = setInterval(() => {
                                currentNumber += increment;
                                if (currentNumber >= finalNumber) {
                                    target.textContent = finalText;
                                    clearInterval(timer);
                                } else {
                                    target.textContent = Math.floor(currentNumber) + '+';
                                }
                            }, 50);
                        }
                        
                        observer.unobserve(target);
                    }
                });
            };
            
            const numberObserver = new IntersectionObserver(animateNumbers, {
                threshold: 0.5
            });
            
            heroStats.forEach(stat => {
                numberObserver.observe(stat);
            });

            // Add hover effects to feature cards
            document.querySelectorAll('.feature-card').forEach(card => {
                card.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-10px) scale(1.02)';
                });
                
                card.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0) scale(1)';
                });
            });
        });
    </script>
    `;
  }
};