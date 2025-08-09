const fs = require('fs');
const path = require('path');
const marked = require('marked');

module.exports = class {
  data() {
    return {
      title: "Legal & Compliance Notices",
      description: "Legal notices, disclaimers, and compliance guidelines for MorningStar SWG",
      layout: "base.11ty.js",
      eleventyComputed: {
        legalNotices: () => {
          try {
            const noticesPath = path.join(__dirname, '../data/legal/notices.md');
            const fileContents = fs.readFileSync(noticesPath, 'utf8');
            return marked.parse(fileContents);
          } catch (error) {
            console.error('Error loading legal notices:', error);
            return '<p>Legal notices are currently being updated.</p>';
          }
        }
      }
    };
  }

  render(data) {
    const { legalNotices } = data;
    
    return `
      <div class="legal-container">
        <header class="legal-header">
          <h1>Legal & Compliance Notices</h1>
          <p class="legal-subtitle">Important legal information, disclaimers, and compliance guidelines</p>
          <div class="last-updated">
            <small>Last updated: ${new Date().toLocaleDateString()}</small>
          </div>
        </header>

        <nav class="legal-nav">
          <ul>
            <li><a href="#dmca">DMCA Disclaimer</a></li>
            <li><a href="#swg-restoration">SWG Restoration Rules</a></li>
            <li><a href="#mod-compliance">Mod Compliance Guidelines</a></li>
            <li><a href="#terms-of-use">Terms of Use</a></li>
            <li><a href="#fair-use">Fair Use Policy</a></li>
            <li><a href="#disclaimers">General Disclaimers</a></li>
          </ul>
        </nav>

        <main class="legal-content">
          <div class="legal-notices">
            ${legalNotices}
          </div>

          <aside class="legal-sidebar">
            <div class="legal-contact">
              <h3>Legal Contact</h3>
              <p>For legal inquiries or DMCA notices:</p>
              <ul>
                <li>Email: legal@morningstar.swg.ms11.com</li>
                <li>Response Time: 48-72 hours</li>
              </ul>
            </div>

            <div class="compliance-status">
              <h3>Compliance Status</h3>
              <div class="status-item">
                <span class="status-label">DMCA Compliance:</span>
                <span class="status-value compliant">✅ Compliant</span>
              </div>
              <div class="status-item">
                <span class="status-label">SWG Rules:</span>
                <span class="status-value compliant">✅ Compliant</span>
              </div>
              <div class="status-item">
                <span class="status-label">Mod Guidelines:</span>
                <span class="status-value compliant">✅ Compliant</span>
              </div>
            </div>

            <div class="legal-resources">
              <h3>Legal Resources</h3>
              <ul>
                <li><a href="https://www.law.cornell.edu/uscode/text/17/512" target="_blank" rel="noopener">DMCA Section 512</a></li>
                <li><a href="https://www.swglegends.com/forums/" target="_blank" rel="noopener">SWG Legends Forums</a></li>
                <li><a href="https://www.swgemu.com/forums/" target="_blank" rel="noopener">SWGEmu Forums</a></li>
              </ul>
            </div>
          </aside>
        </main>

        <footer class="legal-footer">
          <div class="legal-disclaimer">
            <p><strong>Important:</strong> This legal information is provided for informational purposes only and does not constitute legal advice. Please consult with a qualified attorney for specific legal guidance.</p>
          </div>
        </footer>
      </div>

      <style>
        .legal-container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 2rem;
          font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
          line-height: 1.6;
        }

        .legal-header {
          text-align: center;
          margin-bottom: 3rem;
          padding-bottom: 2rem;
          border-bottom: 2px solid #e0e0e0;
        }

        .legal-header h1 {
          color: #2c3e50;
          font-size: 2.5rem;
          margin-bottom: 0.5rem;
        }

        .legal-subtitle {
          color: #7f8c8d;
          font-size: 1.1rem;
          margin-bottom: 1rem;
        }

        .last-updated {
          color: #95a5a6;
          font-style: italic;
        }

        .legal-nav {
          background: #f8f9fa;
          padding: 1rem;
          border-radius: 8px;
          margin-bottom: 2rem;
        }

        .legal-nav ul {
          list-style: none;
          padding: 0;
          margin: 0;
          display: flex;
          flex-wrap: wrap;
          gap: 1rem;
          justify-content: center;
        }

        .legal-nav a {
          color: #3498db;
          text-decoration: none;
          padding: 0.5rem 1rem;
          border-radius: 4px;
          transition: background-color 0.2s;
        }

        .legal-nav a:hover {
          background-color: #e3f2fd;
        }

        .legal-content {
          display: grid;
          grid-template-columns: 2fr 1fr;
          gap: 3rem;
        }

        .legal-notices {
          background: white;
          padding: 2rem;
          border-radius: 8px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .legal-notices h2 {
          color: #2c3e50;
          border-bottom: 2px solid #3498db;
          padding-bottom: 0.5rem;
          margin-top: 2rem;
          margin-bottom: 1rem;
        }

        .legal-notices h2:first-child {
          margin-top: 0;
        }

        .legal-notices h3 {
          color: #34495e;
          margin-top: 1.5rem;
          margin-bottom: 0.5rem;
        }

        .legal-notices p {
          margin-bottom: 1rem;
          text-align: justify;
        }

        .legal-notices ul, .legal-notices ol {
          margin-bottom: 1rem;
          padding-left: 2rem;
        }

        .legal-notices li {
          margin-bottom: 0.5rem;
        }

        .legal-notices blockquote {
          border-left: 4px solid #3498db;
          padding-left: 1rem;
          margin: 1rem 0;
          font-style: italic;
          color: #555;
        }

        .legal-notices code {
          background: #f4f4f4;
          padding: 0.2rem 0.4rem;
          border-radius: 3px;
          font-family: 'Courier New', monospace;
        }

        .legal-sidebar {
          display: flex;
          flex-direction: column;
          gap: 2rem;
        }

        .legal-contact, .compliance-status, .legal-resources {
          background: white;
          padding: 1.5rem;
          border-radius: 8px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .legal-contact h3, .compliance-status h3, .legal-resources h3 {
          color: #2c3e50;
          margin-bottom: 1rem;
          font-size: 1.2rem;
        }

        .status-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 0.5rem;
          padding: 0.5rem 0;
          border-bottom: 1px solid #ecf0f1;
        }

        .status-item:last-child {
          border-bottom: none;
        }

        .status-label {
          font-weight: 500;
          color: #34495e;
        }

        .status-value.compliant {
          color: #27ae60;
          font-weight: bold;
        }

        .status-value.non-compliant {
          color: #e74c3c;
          font-weight: bold;
        }

        .legal-resources ul {
          list-style: none;
          padding: 0;
        }

        .legal-resources li {
          margin-bottom: 0.5rem;
        }

        .legal-resources a {
          color: #3498db;
          text-decoration: none;
        }

        .legal-resources a:hover {
          text-decoration: underline;
        }

        .legal-footer {
          margin-top: 3rem;
          padding-top: 2rem;
          border-top: 2px solid #e0e0e0;
          text-align: center;
        }

        .legal-disclaimer {
          background: #fff3cd;
          border: 1px solid #ffeaa7;
          border-radius: 4px;
          padding: 1rem;
          color: #856404;
        }

        @media (max-width: 768px) {
          .legal-content {
            grid-template-columns: 1fr;
            gap: 2rem;
          }

          .legal-nav ul {
            flex-direction: column;
            align-items: center;
          }

          .legal-container {
            padding: 1rem;
          }
        }
      </style>
    `;
  }
}; 