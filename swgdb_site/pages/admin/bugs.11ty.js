module.exports = class {
  data() {
    return {
      title: "Bug Tracker - Admin Panel",
      description: "Internal bug tracking system for SWGDB administrators",
      layout: "base.njk",
      tags: ["admin", "bugs", "internal"],
      permalink: "/admin/bugs/"
    };
  }

  async render(data) {
    const bugs = [
      {
        id: "BUG-2024-001",
        title: "Heroics loot table not displaying correctly on mobile",
        severity: "medium",
        status: "open",
        module: "heroics"
      },
      {
        id: "BUG-2024-002", 
        title: "RLS mode not detecting rare loot properly",
        severity: "high",
        status: "in_progress",
        module: "rls"
      },
      {
        id: "BUG-2024-003",
        title: "Build showcase API returning 500 errors", 
        severity: "critical",
        status: "resolved",
        module: "api"
      }
    ];

    return `
    <div style="padding: 40px;">
      <h1>Bug Tracker - Admin Panel</h1>
      <div style="display: grid; gap: 20px; margin-top: 30px;">
        ${bugs.map(bug => `
          <div style="border: 1px solid #e9ecef; border-radius: 8px; padding: 20px; background: white;">
            <h3 style="margin: 0 0 10px 0; color: #333;">${bug.id}: ${bug.title}</h3>
            <div style="display: flex; gap: 10px; margin-bottom: 10px;">
              <span style="padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; 
                background: ${bug.severity === 'critical' ? '#dc3545' : bug.severity === 'high' ? '#fd7e14' : '#28a745'}; 
                color: white;">${bug.severity.toUpperCase()}</span>
              <span style="padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; 
                background: ${bug.status === 'resolved' ? '#28a745' : bug.status === 'in_progress' ? '#ffc107' : '#6c757d'}; 
                color: ${bug.status === 'in_progress' ? '#000' : 'white'};">${bug.status.replace('_', ' ').toUpperCase()}</span>
              <span style="padding: 4px 8px; border-radius: 4px; font-size: 12px; background: #f8f9fa; color: #333;">${bug.module}</span>
            </div>
          </div>
        `).join('')}
      </div>
      
      <div style="margin-top: 40px;">
        <h2>Statistics</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
          <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e9ecef; text-align: center;">
            <div style="font-size: 2rem; font-weight: bold; color: #667eea;">${bugs.length}</div>
            <div style="color: #666; font-size: 0.9rem;">Total Bugs</div>
          </div>
          <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e9ecef; text-align: center;">
            <div style="font-size: 2rem; font-weight: bold; color: #28a745;">${bugs.filter(b => b.status === 'resolved').length}</div>
            <div style="color: #666; font-size: 0.9rem;">Resolved</div>
          </div>
          <div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e9ecef; text-align: center;">
            <div style="font-size: 2rem; font-weight: bold; color: #dc3545;">${bugs.filter(b => b.severity === 'critical').length}</div>
            <div style="color: #666; font-size: 0.9rem;">Critical</div>
          </div>
        </div>
      </div>
    </div>
    `;
  }
};