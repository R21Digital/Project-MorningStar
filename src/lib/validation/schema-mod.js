/**
 * Mod Validation Schema and Security Framework
 * Comprehensive validation, security scanning, and content filtering for mod submissions
 */

const crypto = require('crypto');
const path = require('path');

class ModValidationSchema {
  constructor() {
    this.version = '2.1.0';
    this.initializeValidationRules();
    this.initializeSecurityScanning();
  }

  initializeValidationRules() {
    this.validationRules = {
      // Basic mod information validation
      basic: {
        title: {
          required: true,
          minLength: 5,
          maxLength: 200,
          pattern: /^[a-zA-Z0-9\s\-_.:()[\]]+$/,
          forbidden: ['hack', 'cheat', 'exploit', 'virus', 'malware']
        },
        description: {
          required: true,
          minLength: 20,
          maxLength: 5000,
          allowMarkdown: true
        },
        version: {
          required: true,
          pattern: /^\d+\.\d+(\.\d+)?(-[a-zA-Z0-9]+)?$/,
          examples: ['1.0.0', '2.1.3', '1.0.0-beta']
        },
        category: {
          required: true,
          allowedValues: [
            'UI Enhancement',
            'Gameplay',
            'Quality of Life',
            'Visual',
            'Audio',
            'Performance',
            'Utility',
            'Bug Fix',
            'Content',
            'Other'
          ]
        }
      },

      // File validation rules
      files: {
        required: true,
        maxFiles: 20,
        maxTotalSize: 100 * 1024 * 1024, // 100MB
        maxFileSize: 50 * 1024 * 1024,   // 50MB per file
        allowedExtensions: [
          // Archive formats
          'zip', 'rar', '7z', 'tar', 'gz',
          // Image formats
          'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp',
          // Text formats
          'txt', 'md', 'readme', 'log',
          // Config/Data formats
          'json', 'xml', 'cfg', 'ini', 'lua'
        ],
        forbiddenExtensions: [
          // Executable formats
          'exe', 'bat', 'cmd', 'com', 'scr', 'pif',
          // Script formats
          'vbs', 'js', 'ps1', 'sh', 'py', 'php',
          // System files
          'sys', 'dll', 'so', 'dylib',
          // Other dangerous formats
          'jar', 'app', 'deb', 'rpm'
        ],
        securityPatterns: [
          // Malicious filename patterns
          /\.(exe|bat|cmd|scr|pif|vbs|js|jar)$/i,
          // Hidden files (security risk)
          /^\./,
          // System directories
          /^(windows|system32|program files)/i,
          // Suspicious names
          /(virus|trojan|malware|hack|crack|keygen|serial)/i
        ]
      },

      // Content validation
      content: {
        instructions: {
          required: true,
          minLength: 50,
          mustInclude: ['installation', 'requirements'],
          recommended: ['screenshots', 'changelog', 'compatibility']
        },
        changelog: {
          required: false,
          format: 'markdown',
          versionTracking: true
        }
      },

      // Author information
      author: {
        name: {
          required: true,
          minLength: 2,
          maxLength: 50,
          pattern: /^[a-zA-Z0-9\s\-_]+$/
        },
        contact: {
          required: true,
          methods: ['discord', 'email'],
          validation: {
            discord: /^.{2,32}#[0-9]{4}$|^@[a-zA-Z0-9_]{2,32}$/,
            email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/
          }
        }
      },

      // Metadata validation
      metadata: {
        gameVersion: {
          required: true,
          allowedValues: ['Pre-CU', 'CU', 'NGE', 'JTL', 'ROTW', 'Legends', 'Custom']
        },
        compatibility: {
          required: false,
          clientVersion: /^\d+\.\d+(\.\d+)?$/,
          serverVersion: /^\d+\.\d+(\.\d+)?$/
        },
        dependencies: {
          maxCount: 10,
          validation: {
            name: { required: true, maxLength: 100 },
            version: { pattern: /^\d+\.\d+(\.\d+)?$/ },
            url: { pattern: /^https?:\/\/.+/ }
          }
        }
      }
    };
  }

  initializeSecurityScanning() {
    this.securityConfig = {
      // Virus signature patterns (simplified for demo)
      virusSignatures: [
        // Common malware strings
        'EICAR-STANDARD-ANTIVIRUS-TEST-FILE',
        'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR',
        // Suspicious PowerShell commands
        'powershell.exe -encodedcommand',
        'invoke-expression',
        'downloadstring',
        // Common exploit patterns
        'shell_exec',
        'system(',
        'eval(',
        'exec(',
        // Registry modification patterns
        'HKEY_LOCAL_MACHINE',
        'HKEY_CURRENT_USER'
      ],

      // Suspicious file content patterns
      suspiciousPatterns: [
        // Network operations
        /curl\s+.*\|.*sh/gi,
        /wget\s+.*\|.*sh/gi,
        /nc\s+.*-e/gi,
        // File operations
        /rm\s+-rf\s+\//gi,
        /del\s+\/f\s+\/s\s+\/q/gi,
        // System commands
        /shutdown\s+.*-f/gi,
        /format\s+c:/gi
      ],

      // File size limits for different types
      fileSizeLimits: {
        'txt': 1024 * 1024,      // 1MB
        'md': 1024 * 1024,       // 1MB
        'json': 512 * 1024,      // 512KB
        'xml': 512 * 1024,       // 512KB
        'png': 10 * 1024 * 1024, // 10MB
        'jpg': 10 * 1024 * 1024, // 10MB
        'zip': 50 * 1024 * 1024  // 50MB
      },

      // Quarantine settings
      quarantine: {
        enabled: true,
        directory: '/tmp/mod-quarantine',
        retentionDays: 7,
        logAllActions: true
      }
    };
  }

  /**
   * Validate a complete mod submission
   * @param {Object} modData - The mod submission data
   * @returns {Object} Validation result with success/failure and details
   */
  async validateMod(modData) {
    const validationResult = {
      valid: false,
      errors: [],
      warnings: [],
      securityReport: {},
      metadata: {
        validatedAt: new Date().toISOString(),
        schemaVersion: this.version,
        validationId: this.generateValidationId()
      }
    };

    try {
      // 1. Basic information validation
      const basicValidation = this.validateBasicInfo(modData);
      if (!basicValidation.valid) {
        validationResult.errors.push(...basicValidation.errors);
      }
      validationResult.warnings.push(...basicValidation.warnings);

      // 2. File validation and security scanning
      if (modData.files && modData.files.length > 0) {
        const fileValidation = await this.validateFiles(modData.files);
        if (!fileValidation.valid) {
          validationResult.errors.push(...fileValidation.errors);
        }
        validationResult.warnings.push(...fileValidation.warnings);
        validationResult.securityReport = fileValidation.securityReport;
      } else {
        validationResult.errors.push('At least one file is required for mod submission');
      }

      // 3. Content validation
      const contentValidation = this.validateContent(modData);
      if (!contentValidation.valid) {
        validationResult.errors.push(...contentValidation.errors);
      }
      validationResult.warnings.push(...contentValidation.warnings);

      // 4. Author information validation
      const authorValidation = this.validateAuthor(modData.author);
      if (!authorValidation.valid) {
        validationResult.errors.push(...authorValidation.errors);
      }

      // 5. Metadata validation
      const metadataValidation = this.validateMetadata(modData.metadata);
      if (!metadataValidation.valid) {
        validationResult.errors.push(...metadataValidation.errors);
      }
      validationResult.warnings.push(...metadataValidation.warnings);

      // 6. Cross-validation checks
      const crossValidation = this.performCrossValidation(modData);
      validationResult.warnings.push(...crossValidation.warnings);

      // Final validation status
      validationResult.valid = validationResult.errors.length === 0;

      // Generate validation score
      validationResult.score = this.calculateValidationScore(validationResult);

    } catch (error) {
      validationResult.errors.push(`Validation error: ${error.message}`);
      validationResult.valid = false;
    }

    return validationResult;
  }

  /**
   * Validate basic mod information
   */
  validateBasicInfo(modData) {
    const result = { valid: true, errors: [], warnings: [] };
    const rules = this.validationRules.basic;

    // Title validation
    if (!this.validateField(modData.title, rules.title)) {
      result.errors.push('Title must be 5-200 characters and contain only allowed characters');
      result.valid = false;
    }

    // Check for forbidden words in title
    const titleLower = (modData.title || '').toLowerCase();
    for (const forbidden of rules.title.forbidden) {
      if (titleLower.includes(forbidden)) {
        result.errors.push(`Title contains forbidden word: ${forbidden}`);
        result.valid = false;
      }
    }

    // Description validation
    if (!this.validateField(modData.description, rules.description)) {
      result.errors.push('Description must be 20-5000 characters');
      result.valid = false;
    }

    // Version validation
    if (!this.validateField(modData.version, rules.version)) {
      result.errors.push('Version must follow semantic versioning (e.g., 1.0.0)');
      result.valid = false;
    }

    // Category validation
    if (!rules.category.allowedValues.includes(modData.category)) {
      result.errors.push('Invalid category selected');
      result.valid = false;
    }

    return result;
  }

  /**
   * Validate and scan files for security issues
   */
  async validateFiles(files) {
    const result = { 
      valid: true, 
      errors: [], 
      warnings: [],
      securityReport: {
        scannedFiles: 0,
        suspiciousFiles: [],
        quarantinedFiles: [],
        virusSignatures: [],
        overallRisk: 'low'
      }
    };

    const rules = this.validationRules.files;

    // Check file count
    if (files.length > rules.maxFiles) {
      result.errors.push(`Too many files (max ${rules.maxFiles})`);
      result.valid = false;
    }

    // Check total size
    const totalSize = files.reduce((sum, file) => sum + (file.size || 0), 0);
    if (totalSize > rules.maxTotalSize) {
      result.errors.push(`Total file size exceeds limit (${this.formatBytes(rules.maxTotalSize)})`);
      result.valid = false;
    }

    // Validate each file
    for (const file of files) {
      const fileValidation = await this.validateSingleFile(file, rules);
      if (!fileValidation.valid) {
        result.errors.push(...fileValidation.errors);
        result.valid = false;
      }
      result.warnings.push(...fileValidation.warnings);
      
      // Merge security reports
      if (fileValidation.securityIssues.length > 0) {
        result.securityReport.suspiciousFiles.push({
          filename: file.name,
          issues: fileValidation.securityIssues
        });
      }
      
      result.securityReport.scannedFiles++;
    }

    // Determine overall risk level
    if (result.securityReport.suspiciousFiles.length > 0) {
      result.securityReport.overallRisk = 'medium';
    }
    if (result.securityReport.virusSignatures.length > 0) {
      result.securityReport.overallRisk = 'high';
      result.errors.push('Potential virus signatures detected');
      result.valid = false;
    }

    return result;
  }

  /**
   * Validate a single file
   */
  async validateSingleFile(file, rules) {
    const result = { valid: true, errors: [], warnings: [], securityIssues: [] };

    // File size validation
    if (file.size > rules.maxFileSize) {
      result.errors.push(`File ${file.name} exceeds size limit (${this.formatBytes(rules.maxFileSize)})`);
      result.valid = false;
    }

    // Extension validation
    const extension = this.getFileExtension(file.name).toLowerCase();
    
    if (rules.forbiddenExtensions.includes(extension)) {
      result.errors.push(`File ${file.name} has forbidden extension: ${extension}`);
      result.valid = false;
    }

    if (!rules.allowedExtensions.includes(extension)) {
      result.warnings.push(`File ${file.name} has uncommon extension: ${extension}`);
    }

    // Filename security patterns
    for (const pattern of rules.securityPatterns) {
      if (pattern.test(file.name)) {
        result.securityIssues.push(`Suspicious filename pattern: ${file.name}`);
      }
    }

    // Content scanning (if text-based file)
    if (this.isTextFile(extension) && file.data) {
      const contentScan = await this.scanFileContent(file);
      result.securityIssues.push(...contentScan.securityIssues);
      if (contentScan.hasVirus) {
        result.errors.push(`Potential virus detected in ${file.name}`);
        result.valid = false;
      }
    }

    return result;
  }

  /**
   * Scan file content for security issues
   */
  async scanFileContent(file) {
    const result = { securityIssues: [], hasVirus: false };

    if (!file.data) return result;

    // Decode base64 content if needed
    let content = file.data;
    if (content.startsWith('data:')) {
      const base64Data = content.split(',')[1];
      content = Buffer.from(base64Data, 'base64').toString('utf8');
    }

    // Virus signature scanning
    for (const signature of this.securityConfig.virusSignatures) {
      if (content.includes(signature)) {
        result.hasVirus = true;
        result.securityIssues.push(`Virus signature detected: ${signature.substring(0, 20)}...`);
      }
    }

    // Suspicious pattern scanning
    for (const pattern of this.securityConfig.suspiciousPatterns) {
      if (pattern.test(content)) {
        result.securityIssues.push(`Suspicious pattern detected: ${pattern.source}`);
      }
    }

    // Check for excessive network requests
    const networkPatterns = [
      /https?:\/\/[^\s]+/gi,
      /ftp:\/\/[^\s]+/gi,
      /telnet:\/\/[^\s]+/gi
    ];

    for (const pattern of networkPatterns) {
      const matches = content.match(pattern);
      if (matches && matches.length > 10) {
        result.securityIssues.push(`Excessive network references found (${matches.length})`);
      }
    }

    return result;
  }

  /**
   * Validate content and instructions
   */
  validateContent(modData) {
    const result = { valid: true, errors: [], warnings: [] };
    const rules = this.validationRules.content;

    // Installation instructions validation
    if (!modData.content || modData.content.length < rules.instructions.minLength) {
      result.errors.push(`Installation instructions must be at least ${rules.instructions.minLength} characters`);
      result.valid = false;
    }

    if (modData.content) {
      const contentLower = modData.content.toLowerCase();
      
      // Check for required keywords
      for (const keyword of rules.instructions.mustInclude) {
        if (!contentLower.includes(keyword)) {
          result.warnings.push(`Instructions should include information about: ${keyword}`);
        }
      }

      // Check for recommended sections
      for (const section of rules.instructions.recommended) {
        if (!contentLower.includes(section)) {
          result.warnings.push(`Consider adding: ${section}`);
        }
      }
    }

    return result;
  }

  /**
   * Validate author information
   */
  validateAuthor(authorData) {
    const result = { valid: true, errors: [] };
    const rules = this.validationRules.author;

    if (!authorData) {
      result.errors.push('Author information is required');
      result.valid = false;
      return result;
    }

    // Name validation
    if (!this.validateField(authorData.name, rules.name)) {
      result.errors.push('Author name must be 2-50 characters, alphanumeric and common symbols only');
      result.valid = false;
    }

    // Contact validation
    let hasValidContact = false;

    if (authorData.discordId && rules.contact.validation.discord.test(authorData.discordId)) {
      hasValidContact = true;
    }

    if (authorData.email && rules.contact.validation.email.test(authorData.email)) {
      hasValidContact = true;
    }

    if (!hasValidContact) {
      result.errors.push('Valid Discord ID or email address is required');
      result.valid = false;
    }

    return result;
  }

  /**
   * Validate metadata information
   */
  validateMetadata(metadataData) {
    const result = { valid: true, errors: [], warnings: [] };
    const rules = this.validationRules.metadata;

    if (!metadataData) {
      result.warnings.push('Metadata information recommended for better compatibility');
      return result;
    }

    // Game version validation
    if (metadataData.gameVersion && !rules.gameVersion.allowedValues.includes(metadataData.gameVersion)) {
      result.errors.push('Invalid game version specified');
      result.valid = false;
    }

    // Dependencies validation
    if (metadataData.dependencies && metadataData.dependencies.length > 0) {
      if (metadataData.dependencies.length > rules.dependencies.maxCount) {
        result.warnings.push(`Many dependencies listed (${metadataData.dependencies.length}). Consider consolidation.`);
      }

      for (const dep of metadataData.dependencies) {
        if (!dep.name || dep.name.length > rules.dependencies.validation.name.maxLength) {
          result.errors.push('Invalid dependency name');
          result.valid = false;
        }
      }
    }

    return result;
  }

  /**
   * Perform cross-validation checks
   */
  performCrossValidation(modData) {
    const result = { warnings: [] };

    // Check if version matches content changes
    if (modData.version === '1.0.0' && modData.content && modData.content.includes('changelog')) {
      result.warnings.push('Version 1.0.0 typically should not include changelog');
    }

    // Check if category matches content
    if (modData.category === 'UI Enhancement' && modData.content) {
      const contentLower = modData.content.toLowerCase();
      if (!contentLower.includes('ui') && !contentLower.includes('interface') && !contentLower.includes('hud')) {
        result.warnings.push('UI Enhancement category but no UI-related content mentioned');
      }
    }

    // Check file types vs category
    if (modData.files) {
      const hasImages = modData.files.some(file => 
        ['png', 'jpg', 'jpeg', 'gif'].includes(this.getFileExtension(file.name).toLowerCase())
      );
      
      if (modData.category === 'Visual' && !hasImages) {
        result.warnings.push('Visual mod category but no image files provided');
      }
    }

    return result;
  }

  /**
   * Calculate validation score (0-100)
   */
  calculateValidationScore(validationResult) {
    let score = 100;

    // Deduct points for errors (major issues)
    score -= validationResult.errors.length * 20;

    // Deduct points for warnings (minor issues)
    score -= validationResult.warnings.length * 5;

    // Deduct points for security issues
    if (validationResult.securityReport.suspiciousFiles) {
      score -= validationResult.securityReport.suspiciousFiles.length * 10;
    }

    // Bonus points for good practices
    if (validationResult.warnings.length === 0) {
      score += 5; // Clean submission
    }

    return Math.max(0, Math.min(100, score));
  }

  /**
   * Helper methods
   */
  validateField(value, rules) {
    if (rules.required && (!value || value.trim().length === 0)) {
      return false;
    }

    if (value) {
      if (rules.minLength && value.length < rules.minLength) return false;
      if (rules.maxLength && value.length > rules.maxLength) return false;
      if (rules.pattern && !rules.pattern.test(value)) return false;
    }

    return true;
  }

  getFileExtension(filename) {
    return path.extname(filename).slice(1);
  }

  isTextFile(extension) {
    const textExtensions = ['txt', 'md', 'json', 'xml', 'cfg', 'ini', 'lua', 'log'];
    return textExtensions.includes(extension.toLowerCase());
  }

  formatBytes(bytes) {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  }

  generateValidationId() {
    return crypto.randomBytes(16).toString('hex');
  }

  /**
   * Generate validation report
   */
  generateValidationReport(validationResult) {
    return {
      summary: {
        valid: validationResult.valid,
        score: validationResult.score,
        riskLevel: validationResult.securityReport.overallRisk,
        timestamp: validationResult.metadata.validatedAt
      },
      details: {
        errors: validationResult.errors,
        warnings: validationResult.warnings,
        filesScanned: validationResult.securityReport.scannedFiles,
        securityIssues: validationResult.securityReport.suspiciousFiles.length
      },
      recommendations: this.generateRecommendations(validationResult),
      nextSteps: validationResult.valid ? 
        ['Submit for community review', 'Await approval notification'] :
        ['Fix validation errors', 'Resubmit for validation']
    };
  }

  generateRecommendations(validationResult) {
    const recommendations = [];

    if (validationResult.warnings.length > 0) {
      recommendations.push('Address warnings to improve mod quality');
    }

    if (validationResult.securityReport.suspiciousFiles.length > 0) {
      recommendations.push('Review flagged files for security concerns');
    }

    if (validationResult.score < 80) {
      recommendations.push('Consider improving documentation and following best practices');
    }

    if (recommendations.length === 0) {
      recommendations.push('Excellent submission! Ready for community review.');
    }

    return recommendations;
  }
}

// Export validation functions
module.exports = {
  ModValidationSchema,
  
  // Convenience functions
  validateMod: async (modData) => {
    const validator = new ModValidationSchema();
    return await validator.validateMod(modData);
  },

  validateBasicInfo: (modData) => {
    const validator = new ModValidationSchema();
    return validator.validateBasicInfo(modData);
  },

  scanFiles: async (files) => {
    const validator = new ModValidationSchema();
    return await validator.validateFiles(files);
  },

  generateReport: (validationResult) => {
    const validator = new ModValidationSchema();
    return validator.generateValidationReport(validationResult);
  }
};