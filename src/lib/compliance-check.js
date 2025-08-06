/**
 * SWGR Compliance Checker
 * Validates mods against Star Wars Galaxies Reborn server rules
 */

class ComplianceChecker {
  constructor() {
    this.swgrRules = {
      // Automation rules
      noAutomation: {
        keywords: ['auto', 'automated', 'automatic', 'bot', 'macro', 'script'],
        description: 'No automation of game actions',
        severity: 'critical'
      },
      noCombatAutomation: {
        keywords: ['auto-target', 'auto-heal', 'auto-attack', 'combat automation'],
        description: 'No automation of combat actions',
        severity: 'critical'
      },
      noMovementAutomation: {
        keywords: ['auto-move', 'auto-navigate', 'pathfinding', 'auto-travel'],
        description: 'No automation of movement',
        severity: 'critical'
      },
      
      // UI/Visual rules
      visualOnly: {
        keywords: ['visual', 'display', 'interface', 'ui', 'hud'],
        description: 'Visual improvements are generally safe',
        severity: 'safe'
      },
      informationOnly: {
        keywords: ['tracking', 'monitoring', 'display', 'show', 'highlight'],
        description: 'Information display is generally safe',
        severity: 'safe'
      },
      
      // MS11 specific rules
      ms11Derived: {
        keywords: ['ms11', 'morningstar', 'internal', 'team'],
        description: 'MS11-derived tools are internal only',
        severity: 'internal'
      },
      
      // File analysis rules
      suspiciousFiles: {
        patterns: ['.exe', '.dll', '.bat', '.cmd', '.vbs', '.js'],
        description: 'Executable files are suspicious',
        severity: 'warning'
      },
      
      // Network rules
      noNetworkAccess: {
        keywords: ['network', 'http', 'https', 'api', 'server', 'remote'],
        description: 'No unauthorized network access',
        severity: 'critical'
      }
    };
    
    this.categories = {
      'UI': { safe: true, description: 'User Interface improvements' },
      'HUD': { safe: true, description: 'Heads Up Display enhancements' },
      'Crafting Helpers': { safe: true, description: 'Crafting assistance tools' },
      'Visual Upgrades': { safe: true, description: 'Visual and aesthetic improvements' },
      'Automation Tools': { safe: false, description: 'Automation and scripting tools' }
    };
  }

  /**
   * Check if a mod is SWGR compliant
   * @param {Object} mod - Mod object to check
   * @returns {Object} Compliance result
   */
  checkCompliance(mod) {
    const result = {
      compliant: true,
      issues: [],
      warnings: [],
      ms11Derived: false,
      category: mod.category || 'Unknown',
      riskLevel: 'low'
    };

    // Check for MS11 derivation
    if (this.isMS11Derived(mod)) {
      result.ms11Derived = true;
      result.compliant = false;
      result.issues.push({
        type: 'ms11_derived',
        message: 'MS11-derived mods are for internal use only',
        severity: 'critical'
      });
    }

    // Check name and description for compliance issues
    const textToCheck = [
      mod.name || '',
      mod.description || '',
      mod.compliance_notes || ''
    ].join(' ').toLowerCase();

    // Check features array
    if (mod.features && Array.isArray(mod.features)) {
      textToCheck += ' ' + mod.features.join(' ').toLowerCase();
    }

    // Apply rule checks
    for (const [ruleName, rule] of Object.entries(this.swgrRules)) {
      const matches = this.checkRule(textToCheck, rule);
      if (matches.length > 0) {
        if (rule.severity === 'critical') {
          result.compliant = false;
          result.issues.push({
            type: ruleName,
            message: rule.description,
            details: matches,
            severity: 'critical'
          });
        } else if (rule.severity === 'warning') {
          result.warnings.push({
            type: ruleName,
            message: rule.description,
            details: matches,
            severity: 'warning'
          });
        }
      }
    }

    // Check category compliance
    const categoryInfo = this.categories[mod.category];
    if (categoryInfo && !categoryInfo.safe) {
      result.compliant = false;
      result.issues.push({
        type: 'category_risk',
        message: `Category "${mod.category}" may contain automation`,
        severity: 'critical'
      });
    }

    // Determine risk level
    result.riskLevel = this.calculateRiskLevel(result);

    return result;
  }

  /**
   * Check if mod is MS11-derived
   * @param {Object} mod - Mod object to check
   * @returns {boolean} True if MS11-derived
   */
  isMS11Derived(mod) {
    const ms11Indicators = [
      'ms11',
      'morningstar',
      'internal',
      'team',
      'ms11-team',
      'ms11_derived'
    ];

    const textToCheck = [
      mod.name || '',
      mod.author || '',
      mod.description || '',
      mod.id || ''
    ].join(' ').toLowerCase();

    return ms11Indicators.some(indicator => 
      textToCheck.includes(indicator.toLowerCase())
    ) || mod.ms11_derived === true;
  }

  /**
   * Check text against a specific rule
   * @param {string} text - Text to check
   * @param {Object} rule - Rule object
   * @returns {Array} Array of matches found
   */
  checkRule(text, rule) {
    const matches = [];
    
    if (rule.keywords) {
      for (const keyword of rule.keywords) {
        if (text.includes(keyword.toLowerCase())) {
          matches.push(keyword);
        }
      }
    }
    
    if (rule.patterns) {
      for (const pattern of rule.patterns) {
        if (text.includes(pattern.toLowerCase())) {
          matches.push(pattern);
        }
      }
    }
    
    return matches;
  }

  /**
   * Calculate risk level based on compliance result
   * @param {Object} result - Compliance result
   * @returns {string} Risk level (low, medium, high, critical)
   */
  calculateRiskLevel(result) {
    if (result.ms11Derived) return 'critical';
    
    const criticalIssues = result.issues.filter(issue => issue.severity === 'critical');
    const warnings = result.warnings.length;
    
    if (criticalIssues.length > 0) return 'high';
    if (warnings > 2) return 'medium';
    if (warnings > 0) return 'low';
    
    return 'low';
  }

  /**
   * Get compliance status badge
   * @param {Object} complianceResult - Compliance check result
   * @returns {Object} Badge information
   */
  getComplianceBadge(complianceResult) {
    if (complianceResult.ms11Derived) {
      return {
        text: 'Internal Use Only',
        class: 'badge-internal',
        icon: '🔒',
        color: '#6c757d'
      };
    }
    
    if (complianceResult.compliant) {
      return {
        text: 'SWGR Safe',
        class: 'badge-safe',
        icon: '✅',
        color: '#28a745'
      };
    } else {
      return {
        text: 'Not SWGR Compliant',
        class: 'badge-unsafe',
        icon: '❌',
        color: '#dc3545'
      };
    }
  }

  /**
   * Get category information
   * @param {string} category - Category name
   * @returns {Object} Category information
   */
  getCategoryInfo(category) {
    return this.categories[category] || {
      safe: false,
      description: 'Unknown category'
    };
  }

  /**
   * Validate mod submission
   * @param {Object} modData - Submitted mod data
   * @returns {Object} Validation result
   */
  validateSubmission(modData) {
    const result = {
      valid: true,
      errors: [],
      warnings: []
    };

    // Required fields
    const requiredFields = ['name', 'author', 'description', 'category'];
    for (const field of requiredFields) {
      if (!modData[field] || modData[field].trim() === '') {
        result.valid = false;
        result.errors.push(`Missing required field: ${field}`);
      }
    }

    // Category validation
    if (modData.category && !this.categories[modData.category]) {
      result.warnings.push(`Unknown category: ${modData.category}`);
    }

    // Description length
    if (modData.description && modData.description.length < 10) {
      result.warnings.push('Description is very short');
    }

    // Version format
    if (modData.version && !/^\d+\.\d+\.\d+$/.test(modData.version)) {
      result.warnings.push('Version should follow semantic versioning (x.y.z)');
    }

    return result;
  }

  /**
   * Generate compliance report
   * @param {Array} mods - Array of mods to analyze
   * @returns {Object} Compliance report
   */
  generateComplianceReport(mods) {
    const report = {
      total: mods.length,
      compliant: 0,
      nonCompliant: 0,
      ms11Derived: 0,
      byCategory: {},
      byRiskLevel: {
        low: 0,
        medium: 0,
        high: 0,
        critical: 0
      },
      issues: []
    };

    for (const mod of mods) {
      const compliance = this.checkCompliance(mod);
      
      if (compliance.ms11Derived) {
        report.ms11Derived++;
      } else if (compliance.compliant) {
        report.compliant++;
      } else {
        report.nonCompliant++;
      }

      // Category breakdown
      const category = mod.category || 'Unknown';
      if (!report.byCategory[category]) {
        report.byCategory[category] = { total: 0, compliant: 0, nonCompliant: 0 };
      }
      report.byCategory[category].total++;
      if (compliance.compliant) {
        report.byCategory[category].compliant++;
      } else {
        report.byCategory[category].nonCompliant++;
      }

      // Risk level breakdown
      report.byRiskLevel[compliance.riskLevel]++;

      // Collect issues
      report.issues.push(...compliance.issues);
    }

    return report;
  }
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = ComplianceChecker;
}

// Export for browser
if (typeof window !== 'undefined') {
  window.ComplianceChecker = ComplianceChecker;
} 