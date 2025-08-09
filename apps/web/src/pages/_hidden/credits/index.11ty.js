const fs = require('fs');
const path = require('path');

module.exports = class {
  data() {
    return {
      title: "Contributors & Credits",
      description: "Acknowledge contributors, modders, guide writers, and community helpers",
      layout: "base.11ty.js",
      eleventyComputed: {
        contributors: () => {
          try {
            const contributorsPath = path.join(__dirname, '../data/contributors.json');
            const fileContents = fs.readFileSync(contributorsPath, 'utf8');
            return JSON.parse(fileContents);
          } catch (error) {
            console.error('Error loading contributors:', error);
            return { contributors: [] };
          }
        }
      }
    };
  }

  render(data) {
    const { contributors } = data;
    
    return `
      <div class="credits-container">
        <header class="credits-header">
          <h1>Contributors & Credits</h1>
          <p class="credits-subtitle">Acknowledging the amazing community that makes MorningStar SWG possible</p>
          <div class="last-updated">
            <small>Last updated: ${new Date().toLocaleDateString()}</small>
          </div>
        </header>

        <nav class="credits-nav">
          <ul>
            <li><a href="#guide-authors">Guide Authors</a></li>
            <li><a href="#modders">Modders</a></li>
            <li><a href="#bug-hunters">Bug Hunters</a></li>
            <li><a href="#testers">Testers</a></li>
            <li><a href="#community-helpers">Community Helpers</a></li>
            <li><a href="#special-thanks">Special Thanks</a></li>
          </ul>
        </nav>

        <main class="credits-content">
          <div class="contributors-grid">
            ${this.renderContributorsByCategory(contributors)}
          </div>

          <aside class="credits-sidebar">
            <div class="badge-info">
              <h3>Badge Tiers</h3>
              <div class="badge-tier">
                <span class="badge guide-author">Guide Author</span>
                <p>Created comprehensive guides and documentation</p>
              </div>
              <div class="badge-tier">
                <span class="badge modder">Modder</span>
                <p>Developed mods and tools for the community</p>
              </div>
              <div class="badge-tier">
                <span class="badge bug-hunter">Bug Hunter</span>
                <p>Found and reported critical bugs and issues</p>
              </div>
              <div class="badge-tier">
                <span class="badge tester">Tester</span>
                <p>Provided extensive testing and feedback</p>
              </div>
            </div>

            <div class="stats-summary">
              <h3>Community Stats</h3>
              <div class="stat-item">
                <span class="stat-label">Total Contributors:</span>
                <span class="stat-value">${contributors.contributors?.length || 0}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Guide Authors:</span>
                <span class="stat-value">${this.countBadgeType(contributors, 'guide-author')}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Modders:</span>
                <span class="stat-value">${this.countBadgeType(contributors, 'modder')}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Bug Hunters:</span>
                <span class="stat-value">${this.countBadgeType(contributors, 'bug-hunter')}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">Testers:</span>
                <span class="stat-value">${this.countBadgeType(contributors, 'tester')}</span>
              </div>
            </div>

            <div class="join-community">
              <h3>Join the Community</h3>
              <p>Want to contribute? Join our Discord!</p>
              <a href="https://discord.gg/morningstar-swg" target="_blank" rel="noopener" class="discord-link">
                <span class="discord-icon">📱</span>
                Join Discord
              </a>
            </div>
          </aside>
        </main>

        <footer class="credits-footer">
          <div class="special-thanks">
            <h2 id="special-thanks">Special Thanks</h2>
            <p>To all the contributors who have made MorningStar SWG what it is today. Your dedication, creativity, and passion for the SWG community is what drives this project forward.</p>
            <p>Whether you've written a single guide, reported one bug, or created dozens of mods, every contribution matters and helps make the SWG experience better for everyone.</p>
          </div>
        </footer>
      </div>

      <style>
        .credits-container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 2rem;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          line-height: 1.6;
        }

        .credits-header {
          text-align: center;
          margin-bottom: 3rem;
          padding-bottom: 2rem;
          border-bottom: 2px solid #e0e0e0;
        }

        .credits-header h1 {
          color: #2c3e50;
          font-size: 2.5rem;
          margin-bottom: 0.5rem;
        }

        .credits-subtitle {
          color: #7f8c8d;
          font-size: 1.1rem;
          margin-bottom: 1rem;
        }

        .last-updated {
          color: #95a5a6;
          font-style: italic;
        }

        .credits-nav {
          background: #f8f9fa;
          padding: 1rem;
          border-radius: 8px;
          margin-bottom: 2rem;
        }

        .credits-nav ul {
          list-style: none;
          padding: 0;
          margin: 0;
          display: flex;
          flex-wrap: wrap;
          gap: 1rem;
          justify-content: center;
        }

        .credits-nav a {
          color: #3498db;
          text-decoration: none;
          padding: 0.5rem 1rem;
          border-radius: 4px;
          transition: background-color 0.2s;
        }

        .credits-nav a:hover {
          background-color: #e3f2fd;
        }

        .credits-content {
          display: grid;
          grid-template-columns: 2fr 1fr;
          gap: 3rem;
        }

        .contributors-grid {
          display: flex;
          flex-direction: column;
          gap: 2rem;
        }

        .contributor-category {
          background: white;
          padding: 2rem;
          border-radius: 8px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .contributor-category h2 {
          color: #2c3e50;
          border-bottom: 2px solid #3498db;
          padding-bottom: 0.5rem;
          margin-bottom: 1.5rem;
        }

        .contributors-list {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 1.5rem;
        }

        .contributor-card {
          background: #f8f9fa;
          padding: 1.5rem;
          border-radius: 8px;
          border-left: 4px solid #3498db;
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .contributor-card:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        }

        .contributor-header {
          display: flex;
          align-items: center;
          gap: 1rem;
          margin-bottom: 1rem;
        }

        .contributor-avatar {
          width: 50px;
          height: 50px;
          border-radius: 50%;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          color: white;
          font-weight: bold;
          font-size: 1.2rem;
        }

        .contributor-info h3 {
          margin: 0;
          color: #2c3e50;
          font-size: 1.1rem;
        }

        .contributor-discord {
          color: #7f8c8d;
          font-size: 0.9rem;
          margin-top: 0.25rem;
        }

        .contributor-badges {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          margin-bottom: 1rem;
        }

        .badge {
          padding: 0.25rem 0.75rem;
          border-radius: 20px;
          font-size: 0.8rem;
          font-weight: 500;
          color: white;
        }

        .badge.guide-author {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        .badge.modder {
          background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }

        .badge.bug-hunter {
          background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }

        .badge.tester {
          background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }

        .contributor-contributions {
          font-size: 0.9rem;
          color: #555;
          line-height: 1.4;
        }

        .contributor-contributions ul {
          margin: 0.5rem 0;
          padding-left: 1.5rem;
        }

        .contributor-contributions li {
          margin-bottom: 0.25rem;
        }

        .credits-sidebar {
          display: flex;
          flex-direction: column;
          gap: 2rem;
        }

        .badge-info, .stats-summary, .join-community {
          background: white;
          padding: 1.5rem;
          border-radius: 8px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .badge-info h3, .stats-summary h3, .join-community h3 {
          color: #2c3e50;
          margin-bottom: 1rem;
          font-size: 1.2rem;
        }

        .badge-tier {
          margin-bottom: 1rem;
          padding-bottom: 1rem;
          border-bottom: 1px solid #ecf0f1;
        }

        .badge-tier:last-child {
          border-bottom: none;
          margin-bottom: 0;
        }

        .badge-tier p {
          margin: 0.5rem 0 0 0;
          font-size: 0.9rem;
          color: #7f8c8d;
        }

        .stat-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
          padding: 0.5rem 0;
          border-bottom: 1px solid #ecf0f1;
        }

        .stat-item:last-child {
          border-bottom: none;
        }

        .stat-label {
          font-weight: 500;
          color: #34495e;
        }

        .stat-value {
          color: #3498db;
          font-weight: bold;
        }

        .discord-link {
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
          background: #7289da;
          color: white;
          text-decoration: none;
          padding: 0.75rem 1.5rem;
          border-radius: 6px;
          font-weight: 500;
          transition: background-color 0.2s;
        }

        .discord-link:hover {
          background: #5b6eae;
        }

        .discord-icon {
          font-size: 1.2rem;
        }

        .credits-footer {
          margin-top: 3rem;
          padding-top: 2rem;
          border-top: 2px solid #e0e0e0;
        }

        .special-thanks {
          text-align: center;
          max-width: 800px;
          margin: 0 auto;
        }

        .special-thanks h2 {
          color: #2c3e50;
          margin-bottom: 1rem;
        }

        .special-thanks p {
          color: #555;
          margin-bottom: 1rem;
        }

        @media (max-width: 768px) {
          .credits-content {
            grid-template-columns: 1fr;
            gap: 2rem;
          }

          .credits-nav ul {
            flex-direction: column;
            align-items: center;
          }

          .contributors-list {
            grid-template-columns: 1fr;
          }

          .credits-container {
            padding: 1rem;
          }
        }
      </style>
    `;
  }

  renderContributorsByCategory(contributors) {
    if (!contributors.contributors) return '<p>No contributors data available.</p>';

    const categories = {
      'guide-author': { title: 'Guide Authors', id: 'guide-authors' },
      'modder': { title: 'Modders', id: 'modders' },
      'bug-hunter': { title: 'Bug Hunters', id: 'bug-hunters' },
      'tester': { title: 'Testers', id: 'testers' },
      'community-helper': { title: 'Community Helpers', id: 'community-helpers' }
    };

    let html = '';
    
    for (const [badgeType, category] of Object.entries(categories)) {
      const categoryContributors = contributors.contributors.filter(c => 
        c.badges && c.badges.includes(badgeType)
      );

      if (categoryContributors.length > 0) {
        html += `
          <section class="contributor-category">
            <h2 id="${category.id}">${category.title}</h2>
            <div class="contributors-list">
              ${categoryContributors.map(contributor => this.renderContributorCard(contributor)).join('')}
            </div>
          </section>
        `;
      }
    }

    return html;
  }

  renderContributorCard(contributor) {
    const avatarInitial = contributor.name.charAt(0).toUpperCase();
    const discordHandle = contributor.discord ? `@${contributor.discord}` : '';
    
    return `
      <div class="contributor-card">
        <div class="contributor-header">
          <div class="contributor-avatar">${avatarInitial}</div>
          <div class="contributor-info">
            <h3>${contributor.name}</h3>
            ${discordHandle ? `<div class="contributor-discord">${discordHandle}</div>` : ''}
          </div>
        </div>
        
        <div class="contributor-badges">
          ${contributor.badges.map(badge => `<span class="badge ${badge}">${this.getBadgeLabel(badge)}</span>`).join('')}
        </div>
        
        <div class="contributor-contributions">
          ${contributor.contributions ? contributor.contributions : 'Valuable contributions to the community'}
          ${contributor.links ? `
            <ul>
              ${contributor.links.map(link => `<li><a href="${link.url}" target="_blank" rel="noopener">${link.text}</a></li>`).join('')}
            </ul>
          ` : ''}
        </div>
      </div>
    `;
  }

  getBadgeLabel(badgeType) {
    const labels = {
      'guide-author': 'Guide Author',
      'modder': 'Modder',
      'bug-hunter': 'Bug Hunter',
      'tester': 'Tester',
      'community-helper': 'Community Helper'
    };
    return labels[badgeType] || badgeType;
  }

  countBadgeType(contributors, badgeType) {
    if (!contributors.contributors) return 0;
    return contributors.contributors.filter(c => 
      c.badges && c.badges.includes(badgeType)
    ).length;
  }
}; 