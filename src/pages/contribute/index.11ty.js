/**
 * Contributor Wiki + Mod Submission Portal - Main Page
 * Public-facing contribution hub for guides, mods, and community submissions
 */

const fs = require('fs');
const path = require('path');

class ContributorPortalGenerator {
  data() {
    return {
      title: "Contribute to MorningStar - Community Portal",
      description: "Join the MorningStar community by contributing guides, mods, loot data, and more. Help fellow players and enhance the gaming experience.",
      layout: "base.njk",
      permalink: "/contribute/",
      tags: ["contribute", "community", "portal"],
      eleventyNavigation: {
        key: "Contribute",
        order: 5
      }
    };
  }

  async render(data) {
    // Load contribution statistics if available
    const statsPath = path.join(__dirname, '../../data/contributions/stats.json');
    let contributionStats = await this.loadContributionStats(statsPath);

    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${data.title}</title>
    <meta name="description" content="${data.description}">
    
    <!-- Open Graph / Social Media -->
    <meta property="og:type" content="website">
    <meta property="og:title" content="${data.title}">
    <meta property="og:description" content="${data.description}">
    <meta property="og:url" content="https://morningstar.ms11.com/contribute/">
    
    <!-- Schema.org markup -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "WebPage",
      "name": "${data.title}",
      "description": "${data.description}",
      "url": "https://morningstar.ms11.com/contribute/"
    }
    </script>
    
    <!-- Styles -->
    <style>
        .contributor-portal {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .portal-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 60px 40px;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        .portal-header h1 {
            margin: 0 0 20px 0;
            font-size: 3em;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .portal-header .subtitle {
            font-size: 1.3em;
            opacity: 0.95;
            max-width: 800px;
            margin: 0 auto 30px auto;
            line-height: 1.6;
        }
        
        .contribution-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            background: rgba(255,255,255,0.1);
            padding: 25px;
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }
        
        .stat-item {
            text-align: center;
        }
        
        .stat-number {
            display: block;
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .stat-label {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .contribution-categories {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 30px;
            margin-bottom: 50px;
        }
        
        .category-card {
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            border-left: 5px solid;
        }
        
        .category-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        }
        
        .category-card.guides {
            border-left-color: #3498db;
        }
        
        .category-card.mods {
            border-left-color: #9b59b6;
        }
        
        .category-card.loot {
            border-left-color: #f39c12;
        }
        
        .category-card.bugs {
            border-left-color: #e74c3c;
        }
        
        .category-icon {
            font-size: 3em;
            margin-bottom: 20px;
            display: block;
        }
        
        .category-card.guides .category-icon { color: #3498db; }
        .category-card.mods .category-icon { color: #9b59b6; }
        .category-card.loot .category-icon { color: #f39c12; }
        .category-card.bugs .category-icon { color: #e74c3c; }
        
        .category-title {
            font-size: 1.8em;
            font-weight: 600;
            margin-bottom: 15px;
            color: #333;
        }
        
        .category-description {
            color: #666;
            line-height: 1.6;
            margin-bottom: 25px;
        }
        
        .category-features {
            list-style: none;
            padding: 0;
            margin-bottom: 25px;
        }
        
        .category-features li {
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
            position: relative;
            padding-left: 25px;
        }
        
        .category-features li:before {
            content: "✓";
            position: absolute;
            left: 0;
            color: #27ae60;
            font-weight: bold;
        }
        
        .category-features li:last-child {
            border-bottom: none;
        }
        
        .btn {
            display: inline-flex;
            align-items: center;
            gap: 10px;
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            text-decoration: none;
            cursor: pointer;
            transition: all 0.2s ease;
            font-size: 1em;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        
        .btn-secondary {
            background: #f8f9fa;
            color: #495057;
            border: 2px solid #e9ecef;
        }
        
        .btn-secondary:hover {
            background: #e9ecef;
            border-color: #dee2e6;
        }
        
        .getting-started {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 40px;
            border-radius: 16px;
            margin-bottom: 40px;
        }
        
        .getting-started h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 2.2em;
        }
        
        .steps-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }
        
        .step-card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        }
        
        .step-number {
            background: #667eea;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.2em;
            margin: 0 auto 15px auto;
        }
        
        .step-title {
            font-weight: 600;
            margin-bottom: 10px;
            color: #333;
        }
        
        .step-description {
            color: #666;
            font-size: 0.9em;
            line-height: 1.5;
        }
        
        .community-guidelines {
            background: white;
            padding: 40px;
            border-radius: 16px;
            margin-bottom: 40px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        
        .guidelines-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 30px;
            margin-top: 25px;
        }
        
        .guideline-item {
            padding: 20px;
            border-left: 4px solid #667eea;
            background: #f8f9fa;
            border-radius: 0 8px 8px 0;
        }
        
        .guideline-title {
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }
        
        .guideline-text {
            color: #666;
            line-height: 1.5;
        }
        
        .recent-contributions {
            background: white;
            padding: 40px;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        
        .contribution-item {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 15px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .contribution-item:last-child {
            border-bottom: none;
        }
        
        .contribution-icon {
            width: 40px;
            height: 40px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.2em;
            color: white;
        }
        
        .contribution-icon.guide { background: #3498db; }
        .contribution-icon.mod { background: #9b59b6; }
        .contribution-icon.loot { background: #f39c12; }
        .contribution-icon.bug { background: #e74c3c; }
        
        .contribution-details {
            flex: 1;
        }
        
        .contribution-title {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        
        .contribution-meta {
            color: #666;
            font-size: 0.9em;
        }
        
        .discord-integration {
            background: linear-gradient(135deg, #7289da 0%, #5865f2 100%);
            color: white;
            padding: 30px;
            border-radius: 16px;
            text-align: center;
            margin-top: 40px;
        }
        
        .discord-integration h3 {
            margin-bottom: 15px;
            font-size: 1.5em;
        }
        
        .discord-integration p {
            opacity: 0.9;
            margin-bottom: 20px;
        }
        
        .btn-discord {
            background: rgba(255,255,255,0.2);
            color: white;
            border: 2px solid rgba(255,255,255,0.3);
        }
        
        .btn-discord:hover {
            background: rgba(255,255,255,0.3);
            border-color: rgba(255,255,255,0.5);
        }
        
        @media (max-width: 768px) {
            .portal-header {
                padding: 40px 20px;
            }
            
            .portal-header h1 {
                font-size: 2.2em;
            }
            
            .contribution-categories {
                grid-template-columns: 1fr;
            }
            
            .steps-grid {
                grid-template-columns: 1fr;
            }
        }
        
        .quick-actions {
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 1000;
        }
        
        .quick-action-btn {
            background: #667eea;
            color: white;
            border: none;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            font-size: 1.5em;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
            margin-bottom: 10px;
            display: block;
            transition: all 0.3s ease;
        }
        
        .quick-action-btn:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 25px rgba(102, 126, 234, 0.6);
        }
        
        .announcement-banner {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 15px 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            text-align: center;
            position: relative;
        }
        
        .announcement-banner .close-btn {
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            color: white;
            font-size: 1.2em;
            cursor: pointer;
            opacity: 0.8;
        }
        
        .announcement-banner .close-btn:hover {
            opacity: 1;
        }
    </style>
</head>
<body>
    <div class="contributor-portal">
        <!-- Announcement Banner -->
        <div class="announcement-banner" id="announcementBanner">
            <strong>🎉 New Feature:</strong> Submit your mods directly through our portal! Community validation coming soon.
            <button class="close-btn" onclick="document.getElementById('announcementBanner').style.display='none'">&times;</button>
        </div>
        
        <!-- Header -->
        <div class="portal-header">
            <h1>🌟 Contribute to MorningStar</h1>
            <div class="subtitle">
                Join thousands of players sharing guides, mods, and discoveries. 
                Your contributions help build the ultimate Star Wars Galaxies experience.
            </div>
            
            <!-- Community Stats -->
            <div class="contribution-stats">
                <div class="stat-item">
                    <span class="stat-number">${contributionStats.totalContributions}</span>
                    <span class="stat-label">Total Contributions</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">${contributionStats.activeContributors}</span>
                    <span class="stat-label">Active Contributors</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">${contributionStats.approvedMods}</span>
                    <span class="stat-label">Approved Mods</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">${contributionStats.guidesPublished}</span>
                    <span class="stat-label">Guides Published</span>
                </div>
            </div>
        </div>
        
        <!-- Contribution Categories -->
        <div class="contribution-categories">
            <!-- Guide Submissions -->
            <div class="category-card guides">
                <span class="category-icon">📚</span>
                <h3 class="category-title">Submit a Guide</h3>
                <p class="category-description">
                    Share your knowledge with the community. From profession guides to combat strategies, 
                    help fellow players master the galaxy.
                </p>
                <ul class="category-features">
                    <li>Markdown formatting support</li>
                    <li>Image and video embedding</li>
                    <li>Version control and updates</li>
                    <li>Community feedback and ratings</li>
                    <li>Featured guide opportunities</li>
                </ul>
                <a href="/contribute/guides/submit" class="btn btn-primary">
                    📝 Submit Guide
                </a>
                <a href="/guides/" class="btn btn-secondary">
                    👀 Browse Guides
                </a>
            </div>
            
            <!-- Mod Submissions -->
            <div class="category-card mods">
                <span class="category-icon">⚙️</span>
                <h3 class="category-title">Upload a Mod</h3>
                <p class="category-description">
                    Share your custom modifications with the community. User interfaces, 
                    quality of life improvements, and gameplay enhancements.
                </p>
                <ul class="category-features">
                    <li>Secure file upload system</li>
                    <li>Automatic safety scanning</li>
                    <li>Version management</li>
                    <li>Installation instructions</li>
                    <li>Community testing and feedback</li>
                </ul>
                <a href="/mods/submit" class="btn btn-primary">
                    📦 Upload Mod
                </a>
                <a href="/mods/" class="btn btn-secondary">
                    🔍 Browse Mods
                </a>
            </div>
            
            <!-- Loot Data -->
            <div class="category-card loot">
                <span class="category-icon">💎</span>
                <h3 class="category-title">Report Loot Data</h3>
                <p class="category-description">
                    Help build the most comprehensive loot database. Submit drop rates, 
                    rare items, and discovery locations.
                </p>
                <ul class="category-features">
                    <li>Structured data collection</li>
                    <li>Location and NPC tracking</li>
                    <li>Drop rate calculations</li>
                    <li>Verification system</li>
                    <li>Database integration</li>
                </ul>
                <a href="/contribute/loot/submit" class="btn btn-primary">
                    🎯 Submit Data
                </a>
                <a href="/loot/" class="btn btn-secondary">
                    📊 View Database
                </a>
            </div>
            
            <!-- Bug Reports -->
            <div class="category-card bugs">
                <span class="category-icon">🐛</span>
                <h3 class="category-title">Report Issues</h3>
                <p class="category-description">
                    Found a bug or issue? Help improve the platform by reporting problems 
                    with detailed information and reproduction steps.
                </p>
                <ul class="category-features">
                    <li>Detailed issue tracking</li>
                    <li>Screenshot attachments</li>
                    <li>Developer notifications</li>
                    <li>Status updates</li>
                    <li>Resolution tracking</li>
                </ul>
                <a href="/contribute/bugs/submit" class="btn btn-primary">
                    🚨 Report Bug
                </a>
                <a href="/internal/bugs/" class="btn btn-secondary">
                    📋 View Issues
                </a>
            </div>
        </div>
        
        <!-- Getting Started -->
        <div class="getting-started">
            <h2>🚀 Getting Started</h2>
            <p>New to contributing? Follow these simple steps to get started and make your first contribution to the MorningStar community.</p>
            
            <div class="steps-grid">
                <div class="step-card">
                    <div class="step-number">1</div>
                    <div class="step-title">Choose Your Type</div>
                    <div class="step-description">
                        Select what you'd like to contribute: guides, mods, loot data, or bug reports.
                    </div>
                </div>
                
                <div class="step-card">
                    <div class="step-number">2</div>
                    <div class="step-title">Prepare Content</div>
                    <div class="step-description">
                        Gather your materials, write your content, or prepare your files following our guidelines.
                    </div>
                </div>
                
                <div class="step-card">
                    <div class="step-number">3</div>
                    <div class="step-title">Submit & Review</div>
                    <div class="step-description">
                        Use our submission forms to upload your contribution. Our team will review and provide feedback.
                    </div>
                </div>
                
                <div class="step-card">
                    <div class="step-number">4</div>
                    <div class="step-title">Go Live</div>
                    <div class="step-description">
                        Once approved, your contribution goes live for the community to enjoy and benefit from.
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Community Guidelines -->
        <div class="community-guidelines">
            <h2>📋 Community Guidelines</h2>
            <p>To maintain quality and ensure a positive experience for everyone, please follow these guidelines when contributing.</p>
            
            <div class="guidelines-grid">
                <div class="guideline-item">
                    <div class="guideline-title">🎯 Quality Content</div>
                    <div class="guideline-text">
                        Ensure your contributions are accurate, well-written, and provide value to the community.
                    </div>
                </div>
                
                <div class="guideline-item">
                    <div class="guideline-title">🔒 Safe & Secure</div>
                    <div class="guideline-text">
                        All uploads are scanned for safety. No malicious code, exploits, or harmful content.
                    </div>
                </div>
                
                <div class="guideline-item">
                    <div class="guideline-title">🤝 Respectful Community</div>
                    <div class="guideline-text">
                        Maintain respectful communication and provide constructive feedback to fellow contributors.
                    </div>
                </div>
                
                <div class="guideline-item">
                    <div class="guideline-title">📜 Original Work</div>
                    <div class="guideline-text">
                        Submit only your original work or content you have permission to share.
                    </div>
                </div>
                
                <div class="guideline-item">
                    <div class="guideline-title">🔄 Keep Updated</div>
                    <div class="guideline-text">
                        Maintain your contributions and update them as needed for new game versions.
                    </div>
                </div>
                
                <div class="guideline-item">
                    <div class="guideline-title">💬 Clear Communication</div>
                    <div class="guideline-text">
                        Provide clear descriptions, installation instructions, and contact information.
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Recent Contributions -->
        <div class="recent-contributions">
            <h2>🕒 Recent Community Contributions</h2>
            <p>See what fellow players have been sharing with the community.</p>
            
            <div class="contribution-item">
                <div class="contribution-icon guide">📚</div>
                <div class="contribution-details">
                    <div class="contribution-title">Complete Jedi Guide: From Force Sensitive to Knight</div>
                    <div class="contribution-meta">By CommunityPlayer • 2 hours ago • Guide</div>
                </div>
            </div>
            
            <div class="contribution-item">
                <div class="contribution-icon mod">⚙️</div>
                <div class="contribution-details">
                    <div class="contribution-title">Enhanced Inventory Management UI v2.1</div>
                    <div class="contribution-meta">By ModMaster • 5 hours ago • Mod</div>
                </div>
            </div>
            
            <div class="contribution-item">
                <div class="contribution-icon loot">💎</div>
                <div class="contribution-details">
                    <div class="contribution-title">Krayt Dragon Loot Table Update</div>
                    <div class="contribution-meta">By LootHunter • 1 day ago • Loot Data</div>
                </div>
            </div>
            
            <div class="contribution-item">
                <div class="contribution-icon bug">🐛</div>
                <div class="contribution-details">
                    <div class="contribution-title">Character Sheet Display Issue</div>
                    <div class="contribution-meta">By BugReporter • 2 days ago • Bug Report</div>
                </div>
            </div>
        </div>
        
        <!-- Discord Integration -->
        <div class="discord-integration">
            <h3>💬 Join Our Discord Community</h3>
            <p>Connect with other contributors, get help with submissions, and stay updated on community events.</p>
            <a href="https://discord.gg/morningstar" class="btn btn-discord">
                🎮 Join Discord
            </a>
        </div>
    </div>
    
    <!-- Quick Actions -->
    <div class="quick-actions">
        <button class="quick-action-btn" title="Quick Submit" onclick="showQuickSubmit()">➕</button>
    </div>
    
    <!-- JavaScript -->
    <script>
        // Quick submit modal
        function showQuickSubmit() {
            const options = [
                { text: '📚 Submit Guide', url: '/contribute/guides/submit' },
                { text: '⚙️ Upload Mod', url: '/mods/submit' },
                { text: '💎 Report Loot', url: '/contribute/loot/submit' },
                { text: '🐛 Report Bug', url: '/contribute/bugs/submit' }
            ];
            
            const choice = prompt('Quick Submit:\\n\\n' + 
                options.map((opt, i) => \`\${i+1}. \${opt.text}\`).join('\\n') + 
                '\\n\\nEnter number (1-4):');
            
            if (choice && choice >= 1 && choice <= 4) {
                window.location.href = options[choice - 1].url;
            }
        }
        
        // Analytics tracking
        function trackContribution(type) {
            if (typeof gtag !== 'undefined') {
                gtag('event', 'contribution_start', {
                    'contribution_type': type,
                    'page_location': window.location.href
                });
            }
        }
        
        // Add click tracking to contribution buttons
        document.querySelectorAll('.btn-primary').forEach(btn => {
            btn.addEventListener('click', function(e) {
                const href = this.getAttribute('href');
                if (href && href.includes('submit')) {
                    const type = href.includes('guides') ? 'guide' :
                                href.includes('mods') ? 'mod' :
                                href.includes('loot') ? 'loot' :
                                href.includes('bugs') ? 'bug' : 'unknown';
                    trackContribution(type);
                }
            });
        });
        
        // Smooth scrolling for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
        
        // Initialize tooltips and interactions
        document.addEventListener('DOMContentLoaded', function() {
            // Add hover effects to cards
            document.querySelectorAll('.category-card').forEach(card => {
                card.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-5px)';
                });
                
                card.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0)';
                });
            });
            
            // Auto-hide announcement banner after 10 seconds
            setTimeout(() => {
                const banner = document.getElementById('announcementBanner');
                if (banner && banner.style.display !== 'none') {
                    banner.style.opacity = '0';
                    setTimeout(() => {
                        banner.style.display = 'none';
                    }, 500);
                }
            }, 10000);
        });
    </script>
</body>
</html>`;
  }

  async loadContributionStats(statsPath) {
    try {
      const data = await fs.promises.readFile(statsPath, 'utf8');
      return JSON.parse(data);
    } catch (error) {
      // Return default stats if file doesn't exist
      return {
        totalContributions: 1247,
        activeContributors: 89,
        approvedMods: 156,
        guidesPublished: 342
      };
    }
  }
}

module.exports = ContributorPortalGenerator;