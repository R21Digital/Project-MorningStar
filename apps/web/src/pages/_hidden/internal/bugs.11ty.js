/**
 * Internal Bug Tracker UI - Eleventy Generator
 * Authentication-gated internal dashboard for bug report management
 */

const fs = require('fs');
const path = require('path');

class InternalBugTrackerGenerator {
  data() {
    return {
      title: "Internal Bug Tracker - MorningStar",
      description: "Internal dashboard for managing bug reports across MS11 and SWGDB systems",
      layout: "base.11ty.js",
      permalink: "/internal/bugs/",
      tags: ["internal", "bugs", "admin"],
      eleventyNavigation: {
        key: "Bug Tracker",
        parent: "Internal",
        order: 1
      },
      authRequired: true,
      roles: ["admin", "developer", "qa"]
    };
  }

  async render(data) {
    // Load bug reports data
    const bugReportsPath = path.join(__dirname, '../../data/bugs/bug_reports.json');
    let bugData = {};
    
    try {
      const rawData = fs.readFileSync(bugReportsPath, 'utf8');
      bugData = JSON.parse(rawData);
    } catch (error) {
      console.warn('Could not load bug reports data:', error.message);
      bugData = this.getDefaultBugData();
    }

    const { metadata, bugs, categories, analytics } = bugData;

    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${data.title}</title>
    <meta name="description" content="${data.description}">
    
    <!-- Authentication Check -->
    <script>
        // Check authentication status on page load
        window.addEventListener('DOMContentLoaded', function() {
            if (!checkAuthentication()) {
                window.location.href = '/auth/login?redirect=/internal/bugs/';
                return;
            }
            
            // Initialize page if authenticated
            initializeBugTracker();
        });
        
        function checkAuthentication() {
            // Check for authentication token/session
            const authToken = localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
            const userRole = localStorage.getItem('userRole');
            
            if (!authToken) {
                return false;
            }
            
            // Check if user has required role
            const requiredRoles = ${JSON.stringify(data.roles)};
            if (!requiredRoles.includes(userRole)) {
                alert('Insufficient permissions to access this page');
                return false;
            }
            
            return true;
        }
    </script>
    
    <!-- Internal Styles -->
    <style>
        .bug-tracker {
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .auth-required {
            display: none;
        }
        
        .authenticated .auth-required {
            display: block;
        }
        
        .tracker-header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        .tracker-header h1 {
            margin: 0 0 10px 0;
            font-size: 2.5em;
            font-weight: 700;
        }
        
        .tracker-header .subtitle {
            font-size: 1.1em;
            opacity: 0.9;
            margin-bottom: 20px;
        }
        
        .stats-overview {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border-left: 4px solid;
            transition: transform 0.2s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-3px);
        }
        
        .stat-card.total { border-left-color: #3498db; }
        .stat-card.open { border-left-color: #e74c3c; }
        .stat-card.progress { border-left-color: #f39c12; }
        .stat-card.resolved { border-left-color: #27ae60; }
        
        .stat-card .number {
            font-size: 2.2em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .stat-card.total .number { color: #3498db; }
        .stat-card.open .number { color: #e74c3c; }
        .stat-card.progress .number { color: #f39c12; }
        .stat-card.resolved .number { color: #27ae60; }
        
        .stat-card .label {
            color: #666;
            font-size: 1.1em;
            font-weight: 500;
        }
        
        .controls-section {
            background: white;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .controls-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            align-items: end;
        }
        
        .filter-group {
            display: flex;
            flex-direction: column;
        }
        
        .filter-group label {
            font-weight: 600;
            margin-bottom: 8px;
            color: #333;
        }
        
        .filter-group select,
        .filter-group input {
            padding: 10px 12px;
            border: 2px solid #e1e8ed;
            border-radius: 6px;
            font-size: 14px;
            transition: border-color 0.2s ease;
        }
        
        .filter-group select:focus,
        .filter-group input:focus {
            outline: none;
            border-color: #3498db;
        }
        
        .action-buttons {
            display: flex;
            gap: 10px;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        
        .btn-primary {
            background: #3498db;
            color: white;
        }
        
        .btn-primary:hover {
            background: #2980b9;
        }
        
        .btn-secondary {
            background: #95a5a6;
            color: white;
        }
        
        .btn-secondary:hover {
            background: #7f8c8d;
        }
        
        .bugs-table-container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .table-header {
            background: #f8f9fa;
            padding: 20px 25px;
            border-bottom: 1px solid #e9ecef;
        }
        
        .table-header h2 {
            margin: 0;
            color: #333;
            font-size: 1.5em;
        }
        
        .bugs-table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .bugs-table th {
            background: #f8f9fa;
            padding: 15px 12px;
            text-align: left;
            font-weight: 600;
            color: #555;
            border-bottom: 2px solid #dee2e6;
            font-size: 0.9em;
            text-transform: uppercase;
        }
        
        .bugs-table td {
            padding: 15px 12px;
            border-bottom: 1px solid #e9ecef;
            vertical-align: top;
        }
        
        .bugs-table tr:hover {
            background: #f8f9fa;
        }
        
        .bug-id {
            font-family: monospace;
            font-weight: bold;
            color: #3498db;
            font-size: 0.9em;
        }
        
        .bug-title {
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        }
        
        .bug-description {
            color: #666;
            font-size: 0.9em;
            line-height: 1.4;
            max-width: 300px;
        }
        
        .bug-module {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: 600;
            background: #ecf0f1;
            color: #2c3e50;
        }
        
        .severity-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: 600;
            text-transform: uppercase;
        }
        
        .severity-critical {
            background: #e74c3c;
            color: white;
        }
        
        .severity-high {
            background: #e67e22;
            color: white;
        }
        
        .severity-medium {
            background: #f39c12;
            color: white;
        }
        
        .severity-low {
            background: #27ae60;
            color: white;
        }
        
        .status-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.8em;
            font-weight: 600;
        }
        
        .status-open {
            background: #ff6b35;
            color: white;
        }
        
        .status-progress {
            background: #f39c12;
            color: white;
        }
        
        .status-resolved {
            background: #27ae60;
            color: white;
        }
        
        .bug-actions {
            display: flex;
            gap: 8px;
        }
        
        .action-btn {
            padding: 6px 12px;
            border: none;
            border-radius: 4px;
            font-size: 0.8em;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .action-view {
            background: #3498db;
            color: white;
        }
        
        .action-edit {
            background: #f39c12;
            color: white;
        }
        
        .action-delete {
            background: #e74c3c;
            color: white;
        }
        
        .pagination {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
            padding: 20px;
            background: #f8f9fa;
        }
        
        .pagination button {
            padding: 8px 12px;
            border: 1px solid #dee2e6;
            background: white;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        
        .pagination button:hover:not(:disabled) {
            background: #3498db;
            color: white;
            border-color: #3498db;
        }
        
        .pagination button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        
        .pagination .current-page {
            background: #3498db;
            color: white;
            border-color: #3498db;
        }
        
        .analytics-section {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        @media (max-width: 768px) {
            .analytics-section {
                grid-template-columns: 1fr;
            }
            
            .controls-grid {
                grid-template-columns: 1fr;
            }
            
            .action-buttons {
                flex-direction: column;
            }
        }
        
        .chart-container {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .chart-title {
            font-size: 1.3em;
            font-weight: 600;
            margin-bottom: 20px;
            color: #333;
        }
        
        .chart-placeholder {
            height: 200px;
            background: #f8f9fa;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #666;
            font-style: italic;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 40px;
            color: #666;
        }
        
        .error-message {
            background: #e74c3c;
            color: white;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            display: none;
        }
        
        .success-message {
            background: #27ae60;
            color: white;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            display: none;
        }
        
        .quick-actions {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        .quick-actions h3 {
            margin: 0 0 15px 0;
            color: #333;
        }
        
        .quick-actions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }
        
        .admin-note {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 6px;
            padding: 15px;
            margin: 15px 0;
            color: #856404;
        }
        
        .admin-note strong {
            color: #533f03;
        }
    </style>
</head>
<body>
    <div class="bug-tracker">
        <!-- Authentication Required Message -->
        <div class="auth-required" style="display: none;">
            <div class="error-message" style="display: block;">
                🔒 Authentication required. You must be logged in with admin, developer, or QA privileges to access this page.
            </div>
        </div>
        
        <!-- Main Content (Hidden until authenticated) -->
        <div id="tracker-content" style="display: none;">
            <!-- Header -->
            <div class="tracker-header">
                <h1>🐛 Internal Bug Tracker</h1>
                <div class="subtitle">Comprehensive bug report management for MS11 and SWGDB systems</div>
                <div class="admin-note">
                    <strong>Admin Dashboard:</strong> This internal interface provides full access to bug reports, 
                    analytics, and management tools. All actions are logged for audit purposes.
                </div>
            </div>
            
            <!-- Statistics Overview -->
            <div class="stats-overview">
                <div class="stat-card total">
                    <div class="number">${metadata?.totalBugs || 0}</div>
                    <div class="label">Total Bugs</div>
                </div>
                <div class="stat-card open">
                    <div class="number">${metadata?.openBugs || 0}</div>
                    <div class="label">Open</div>
                </div>
                <div class="stat-card progress">
                    <div class="number">${metadata?.inProgressBugs || 0}</div>
                    <div class="label">In Progress</div>
                </div>
                <div class="stat-card resolved">
                    <div class="number">${metadata?.resolvedBugs || 0}</div>
                    <div class="label">Resolved</div>
                </div>
            </div>
            
            <!-- Quick Actions -->
            <div class="quick-actions">
                <h3>Quick Actions</h3>
                <div class="quick-actions-grid">
                    <button class="btn btn-primary" onclick="createNewBug()">
                        ➕ New Bug Report
                    </button>
                    <button class="btn btn-secondary" onclick="exportBugs()">
                        📊 Export Data
                    </button>
                    <button class="btn btn-secondary" onclick="viewAnalytics()">
                        📈 View Analytics
                    </button>
                    <button class="btn btn-secondary" onclick="refreshData()">
                        🔄 Refresh Data
                    </button>
                </div>
            </div>
            
            <!-- Filters and Controls -->
            <div class="controls-section">
                <div class="controls-grid">
                    <div class="filter-group">
                        <label for="moduleFilter">Module</label>
                        <select id="moduleFilter" onchange="applyFilters()">
                            <option value="">All Modules</option>
                            ${this.renderModuleOptions(categories?.modules || [])}
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <label for="severityFilter">Severity</label>
                        <select id="severityFilter" onchange="applyFilters()">
                            <option value="">All Severities</option>
                            ${this.renderSeverityOptions(categories?.severities || [])}
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <label for="statusFilter">Status</label>
                        <select id="statusFilter" onchange="applyFilters()">
                            <option value="">All Statuses</option>
                            ${this.renderStatusOptions(categories?.statuses || [])}
                        </select>
                    </div>
                    
                    <div class="filter-group">
                        <label for="searchFilter">Search</label>
                        <input type="text" id="searchFilter" placeholder="Search bugs..." onkeyup="applyFilters()">
                    </div>
                </div>
            </div>
            
            <!-- Analytics Section -->
            <div class="analytics-section">
                <div class="chart-container">
                    <div class="chart-title">Bugs by Module</div>
                    <div class="chart-placeholder">
                        ${this.renderModuleChart(analytics?.bugsByModule || {})}
                    </div>
                </div>
                
                <div class="chart-container">
                    <div class="chart-title">Bugs by Status</div>
                    <div class="chart-placeholder">
                        ${this.renderStatusChart(analytics?.bugsByStatus || {})}
                    </div>
                </div>
            </div>
            
            <!-- Bug Reports Table -->
            <div class="bugs-table-container">
                <div class="table-header">
                    <h2>Bug Reports</h2>
                </div>
                
                <div class="loading" id="tableLoading">
                    Loading bug reports...
                </div>
                
                <table class="bugs-table" id="bugsTable">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Title & Description</th>
                            <th>Module</th>
                            <th>Severity</th>
                            <th>Status</th>
                            <th>Reporter</th>
                            <th>Assigned</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="bugsTableBody">
                        ${this.renderBugRows(bugs || [])}
                    </tbody>
                </table>
                
                <div class="pagination" id="pagination">
                    <button onclick="previousPage()" id="prevBtn">← Previous</button>
                    <span id="pageInfo">Page 1 of 1</span>
                    <button onclick="nextPage()" id="nextBtn">Next →</button>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Bug Details Modal (would be implemented separately) -->
    <div id="bugModal" style="display: none;">
        <!-- Modal content for viewing/editing bug details -->
    </div>
    
    <!-- JavaScript for Functionality -->
    <script>
        // Global variables
        let allBugs = ${JSON.stringify(bugs || [])};
        let filteredBugs = [...allBugs];
        let currentPage = 1;
        const bugsPerPage = 10;
        
        function initializeBugTracker() {
            document.body.classList.add('authenticated');
            document.getElementById('tracker-content').style.display = 'block';
            renderBugsTable();
            updatePagination();
        }
        
        function applyFilters() {
            const moduleFilter = document.getElementById('moduleFilter').value;
            const severityFilter = document.getElementById('severityFilter').value;
            const statusFilter = document.getElementById('statusFilter').value;
            const searchFilter = document.getElementById('searchFilter').value.toLowerCase();
            
            filteredBugs = allBugs.filter(bug => {
                const matchesModule = !moduleFilter || bug.module === moduleFilter;
                const matchesSeverity = !severityFilter || bug.severity === severityFilter;
                const matchesStatus = !statusFilter || bug.status === statusFilter;
                const matchesSearch = !searchFilter || 
                    bug.title.toLowerCase().includes(searchFilter) ||
                    bug.description.toLowerCase().includes(searchFilter) ||
                    bug.id.toLowerCase().includes(searchFilter);
                
                return matchesModule && matchesSeverity && matchesStatus && matchesSearch;
            });
            
            currentPage = 1;
            renderBugsTable();
            updatePagination();
        }
        
        function renderBugsTable() {
            const startIndex = (currentPage - 1) * bugsPerPage;
            const endIndex = startIndex + bugsPerPage;
            const pageBugs = filteredBugs.slice(startIndex, endIndex);
            
            const tbody = document.getElementById('bugsTableBody');
            tbody.innerHTML = pageBugs.map(bug => \`
                <tr>
                    <td>
                        <div class="bug-id">\${bug.id}</div>
                    </td>
                    <td>
                        <div class="bug-title">\${bug.title}</div>
                        <div class="bug-description">\${bug.description.substring(0, 100)}...</div>
                    </td>
                    <td>
                        <span class="bug-module">\${bug.module}</span>
                    </td>
                    <td>
                        <span class="severity-badge severity-\${bug.severity.toLowerCase()}">\${bug.severity}</span>
                    </td>
                    <td>
                        <span class="status-badge status-\${bug.status.toLowerCase().replace(' ', '-')}">\${bug.status}</span>
                    </td>
                    <td>\${bug.reporter.name}</td>
                    <td>\${bug.assignee}</td>
                    <td>
                        <div class="bug-actions">
                            <button class="action-btn action-view" onclick="viewBug('\${bug.id}')">View</button>
                            <button class="action-btn action-edit" onclick="editBug('\${bug.id}')">Edit</button>
                        </div>
                    </td>
                </tr>
            \`).join('');
        }
        
        function updatePagination() {
            const totalPages = Math.ceil(filteredBugs.length / bugsPerPage);
            document.getElementById('pageInfo').textContent = \`Page \${currentPage} of \${totalPages}\`;
            document.getElementById('prevBtn').disabled = currentPage === 1;
            document.getElementById('nextBtn').disabled = currentPage === totalPages;
        }
        
        function previousPage() {
            if (currentPage > 1) {
                currentPage--;
                renderBugsTable();
                updatePagination();
            }
        }
        
        function nextPage() {
            const totalPages = Math.ceil(filteredBugs.length / bugsPerPage);
            if (currentPage < totalPages) {
                currentPage++;
                renderBugsTable();
                updatePagination();
            }
        }
        
        // Action handlers
        function createNewBug() {
            window.location.href = '/internal/bugs/new';
        }
        
        function viewBug(bugId) {
            window.location.href = \`/internal/bugs/\${bugId}\`;
        }
        
        function editBug(bugId) {
            window.location.href = \`/internal/bugs/\${bugId}/edit\`;
        }
        
        function exportBugs() {
            // Generate CSV export
            const csv = generateCSV(filteredBugs);
            downloadCSV(csv, 'bug_reports_export.csv');
        }
        
        function generateCSV(bugs) {
            const headers = ['ID', 'Title', 'Module', 'Severity', 'Status', 'Reporter', 'Created', 'Description'];
            const rows = bugs.map(bug => [
                bug.id,
                bug.title,
                bug.module,
                bug.severity,
                bug.status,
                bug.reporter.name,
                new Date(bug.reporter.timestamp).toLocaleDateString(),
                bug.description.replace(/"/g, '""')
            ]);
            
            return [headers, ...rows].map(row => 
                row.map(field => \`"\${field}"\`).join(',')
            ).join('\\n');
        }
        
        function downloadCSV(csv, filename) {
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
            window.URL.revokeObjectURL(url);
        }
        
        function refreshData() {
            location.reload();
        }
        
        function viewAnalytics() {
            window.location.href = '/internal/bugs/analytics';
        }
        
        // Initialize page
        document.addEventListener('DOMContentLoaded', function() {
            // Authentication is checked in the head section
        });
    </script>
</body>
</html>`;
  }

  renderModuleOptions(modules) {
    return modules.map(module => 
      `<option value="${module}">${module}</option>`
    ).join('');
  }

  renderSeverityOptions(severities) {
    return severities.map(severity => 
      `<option value="${severity.level}">${severity.level}</option>`
    ).join('');
  }

  renderStatusOptions(statuses) {
    return statuses.map(status => 
      `<option value="${status.name}">${status.name}</option>`
    ).join('');
  }

  renderBugRows(bugs) {
    return bugs.slice(0, 10).map(bug => `
      <tr>
        <td>
          <div class="bug-id">${bug.id}</div>
        </td>
        <td>
          <div class="bug-title">${bug.title}</div>
          <div class="bug-description">${bug.description.substring(0, 100)}...</div>
        </td>
        <td>
          <span class="bug-module">${bug.module}</span>
        </td>
        <td>
          <span class="severity-badge severity-${bug.severity.toLowerCase()}">${bug.severity}</span>
        </td>
        <td>
          <span class="status-badge status-${bug.status.toLowerCase().replace(' ', '-')}">${bug.status}</span>
        </td>
        <td>${bug.reporter.name}</td>
        <td>${bug.assignee}</td>
        <td>
          <div class="bug-actions">
            <button class="action-btn action-view" onclick="viewBug('${bug.id}')">View</button>
            <button class="action-btn action-edit" onclick="editBug('${bug.id}')">Edit</button>
          </div>
        </td>
      </tr>
    `).join('');
  }

  renderModuleChart(moduleData) {
    const total = Object.values(moduleData).reduce((sum, count) => sum + count, 0);
    return Object.entries(moduleData).map(([module, count]) => {
      const percentage = ((count / total) * 100).toFixed(1);
      return `<div style="margin-bottom: 8px;">
        <strong>${module}:</strong> ${count} bugs (${percentage}%)
      </div>`;
    }).join('');
  }

  renderStatusChart(statusData) {
    const total = Object.values(statusData).reduce((sum, count) => sum + count, 0);
    return Object.entries(statusData).map(([status, count]) => {
      const percentage = ((count / total) * 100).toFixed(1);
      return `<div style="margin-bottom: 8px;">
        <strong>${status}:</strong> ${count} bugs (${percentage}%)
      </div>`;
    }).join('');
  }

  getDefaultBugData() {
    return {
      metadata: {
        totalBugs: 0,
        openBugs: 0,
        inProgressBugs: 0,
        resolvedBugs: 0
      },
      bugs: [],
      categories: {
        modules: ["MS11-Core", "SWGDB"],
        severities: [
          { level: "High", description: "Major issues" },
          { level: "Medium", description: "Minor issues" },
          { level: "Low", description: "Cosmetic issues" }
        ],
        statuses: [
          { name: "Open", description: "New bug" },
          { name: "In Progress", description: "Being worked on" },
          { name: "Resolved", description: "Fixed" }
        ]
      },
      analytics: {
        bugsByModule: {},
        bugsByStatus: {}
      }
    };
  }
}

module.exports = InternalBugTrackerGenerator;