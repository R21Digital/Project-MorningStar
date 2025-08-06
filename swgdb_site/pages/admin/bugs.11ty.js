module.exports = {
  title: "Bug Tracker - Admin Panel",
  description: "Internal bug tracking system for SWGDB administrators",
  layout: "admin",
  tags: ["admin", "bugs", "internal"],
  eleventyComputed: {
    bugs: async function() {
      // In a real implementation, this would load from the JSON file
      // For now, we'll return sample data
      return [
        {
          id: "BUG-2024-001",
          title: "Heroics loot table not displaying correctly on mobile",
          description: "The heroics loot table component is not responsive on mobile devices. Items are overlapping and the filter dropdown is cut off on smaller screens.",
          severity: "medium",
          status: "open",
          module: "heroics",
          reported_by: "user@example.com",
          reported_at: "2024-01-15T10:30:00Z",
          assigned_to: null,
          priority: "normal",
          category: "ui",
          steps_to_reproduce: [
            "Navigate to /heroics/ on mobile device",
            "Try to use the loot type filter",
            "Observe overlapping elements"
          ],
          expected_behavior: "Loot table should be fully responsive and usable on mobile",
          actual_behavior: "Elements overlap and filters are unusable",
          browser: "Chrome Mobile",
          os: "Android 13",
          discord_link: "https://discord.com/channels/123456789/987654321",
          tags: ["mobile", "responsive", "heroics"],
          comments: [
            {
              id: "COM-001",
              author: "admin@swgdb.com",
              content: "Investigating mobile responsiveness issues",
              timestamp: "2024-01-15T11:00:00Z"
            }
          ],
          updated_at: "2024-01-15T11:00:00Z"
        },
        {
          id: "BUG-2024-002",
          title: "RLS mode not detecting rare loot properly",
          description: "The Rare Loot Scan mode is not properly detecting rare loot items in certain areas. False negatives are occurring.",
          severity: "high",
          status: "in_progress",
          module: "rls",
          reported_by: "admin@swgdb.com",
          reported_at: "2024-01-14T14:20:00Z",
          assigned_to: "dev@swgdb.com",
          priority: "high",
          category: "functionality",
          steps_to_reproduce: [
            "Enable RLS mode in MS11",
            "Navigate to Krayt Dragon spawn area",
            "Wait for spawn and engage",
            "Check if rare loot is detected"
          ],
          expected_behavior: "RLS mode should detect all rare loot items",
          actual_behavior: "Some rare items are not being detected",
          browser: "N/A",
          os: "Windows 11",
          discord_link: null,
          tags: ["rls", "loot-detection", "ms11"],
          comments: [
            {
              id: "COM-002",
              author: "dev@swgdb.com",
              content: "Looking into OCR detection thresholds",
              timestamp: "2024-01-14T15:30:00Z"
            },
            {
              id: "COM-003",
              author: "admin@swgdb.com",
              content: "Confirmed issue with Krayt Dragon Pearl detection",
              timestamp: "2024-01-15T09:15:00Z"
            }
          ],
          updated_at: "2024-01-15T09:15:00Z"
        },
        {
          id: "BUG-2024-003",
          title: "Build showcase API returning 500 errors",
          description: "The build showcase API endpoint is intermittently returning 500 internal server errors when fetching build data.",
          severity: "critical",
          status: "resolved",
          module: "api",
          reported_by: "user@example.com",
          reported_at: "2024-01-13T16:45:00Z",
          assigned_to: "dev@swgdb.com",
          priority: "urgent",
          category: "api",
          steps_to_reproduce: [
            "Make GET request to /api/builds/showcase",
            "Observe intermittent 500 errors"
          ],
          expected_behavior: "API should return build data consistently",
          actual_behavior: "Intermittent 500 errors",
          browser: "N/A",
          os: "N/A",
          discord_link: null,
          tags: ["api", "builds", "server-error"],
          comments: [
            {
              id: "COM-004",
              author: "dev@swgdb.com",
              content: "Fixed database connection timeout issue",
              timestamp: "2024-01-14T10:20:00Z"
            }
          ],
          resolved_at: "2024-01-14T10:20:00Z",
          updated_at: "2024-01-14T10:20:00Z"
        }
      ];
    },
    stats: async function() {
      return {
        total_bugs: 3,
        open_bugs: 1,
        in_progress_bugs: 1,
        resolved_bugs: 1,
        critical_bugs: 1,
        high_priority_bugs: 1,
        bugs_by_module: {
          heroics: 1,
          rls: 1,
          api: 1
        },
        bugs_by_severity: {
          low: 0,
          medium: 1,
          high: 1,
          critical: 1
        }
      };
    },
    config: async function() {
      return {
        severity_levels: ["low", "medium", "high", "critical"],
        status_options: ["open", "in_progress", "resolved", "closed", "duplicate"],
        priority_levels: ["low", "normal", "high", "urgent"],
        categories: ["ui", "functionality", "api", "performance", "security", "mobile", "desktop"],
        modules: ["heroics", "rls", "api", "dashboard", "admin", "user-management", "builds", "loot", "general"]
      };
    }
  }
}; 