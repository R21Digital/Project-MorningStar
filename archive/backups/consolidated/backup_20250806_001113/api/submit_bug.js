/**
 * Bug Report Submission API Endpoint
 * Handles bug report processing, validation, storage, and notifications
 */

const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');

// Configuration
const BUG_REPORTS_FILE = path.join(__dirname, '../src/data/bugs/bug_reports.json');
const UPLOAD_DIR = path.join(__dirname, '../uploads/bugs');
const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB
const RATE_LIMIT_WINDOW = 300000; // 5 minutes
const MAX_REQUESTS_PER_WINDOW = 5;

// In-memory rate limiting (in production, use Redis or similar)
const rateLimitStore = new Map();

// Valid values for validation
const VALID_MODULES = [
  'MS11-Core',
  'MS11-Combat', 
  'MS11-Heroics',
  'MS11-Discord',
  'SWGDB',
  'Website',
  'API',
  'Database',
  'Infrastructure'
];

const VALID_SEVERITIES = ['Critical', 'High', 'Medium', 'Low'];
const VALID_PRIORITIES = ['Critical', 'High', 'Medium', 'Low'];
const VALID_STATUSES = ['Open', 'In Progress', 'Resolved', 'Closed', 'Duplicate', "Won't Fix"];

/**
 * Main API handler
 */
export default async function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  try {
    switch (req.method) {
      case 'POST':
        return await handleBugSubmission(req, res);
      case 'GET':
        return await handleBugRetrieval(req, res);
      default:
        return res.status(405).json({ 
          error: 'Method not allowed',
          allowedMethods: ['GET', 'POST']
        });
    }
  } catch (error) {
    console.error('Bug API Error:', error);
    return res.status(500).json({
      error: 'Internal server error',
      message: process.env.NODE_ENV === 'development' ? error.message : 'Something went wrong'
    });
  }
}

/**
 * Handle bug report submission
 */
async function handleBugSubmission(req, res) {
  // Rate limiting
  const clientId = getClientId(req);
  if (!checkRateLimit(clientId)) {
    return res.status(429).json({
      error: 'Rate limit exceeded',
      message: 'Too many bug reports submitted. Please wait before submitting another.'
    });
  }

  // Validate request body
  const validation = validateBugData(req.body);
  if (!validation.valid) {
    return res.status(400).json({
      error: 'Validation failed',
      details: validation.errors
    });
  }

  const bugData = validation.data;

  try {
    // Load current bug reports
    const bugReports = await loadBugReports();
    
    // Process the bug submission
    const result = await processBugSubmission(bugData, bugReports);
    
    // Save updated data
    await saveBugReports(bugReports);
    
    // Send notifications (if configured)
    await sendBugNotifications(result.bug);
    
    // Return success response
    return res.status(201).json({
      success: true,
      message: 'Bug report submitted successfully',
      bugId: result.bugId,
      status: result.bug.status,
      assignee: result.bug.assignee
    });

  } catch (error) {
    console.error('Bug submission error:', error);
    return res.status(500).json({
      error: 'Failed to submit bug report',
      message: 'Could not save bug report data'
    });
  }
}

/**
 * Handle bug report retrieval
 */
async function handleBugRetrieval(req, res) {
  const { id, module, severity, status, limit, offset } = req.query;

  try {
    const bugReports = await loadBugReports();
    
    if (id) {
      // Get specific bug
      const bug = bugReports.bugs.find(b => b.id === id);
      if (!bug) {
        return res.status(404).json({ error: 'Bug not found' });
      }
      return res.json(bug);
    }

    // Filter bugs based on query parameters
    let filteredBugs = bugReports.bugs;

    if (module) {
      filteredBugs = filteredBugs.filter(bug => bug.module === module);
    }

    if (severity) {
      filteredBugs = filteredBugs.filter(bug => bug.severity === severity);
    }

    if (status) {
      filteredBugs = filteredBugs.filter(bug => bug.status === status);
    }

    // Apply pagination
    const limitNum = parseInt(limit) || 50;
    const offsetNum = parseInt(offset) || 0;
    const paginatedBugs = filteredBugs.slice(offsetNum, offsetNum + limitNum);

    return res.json({
      bugs: paginatedBugs,
      total: filteredBugs.length,
      limit: limitNum,
      offset: offsetNum,
      metadata: bugReports.metadata
    });

  } catch (error) {
    console.error('Bug retrieval error:', error);
    return res.status(500).json({
      error: 'Failed to retrieve bug reports'
    });
  }
}

/**
 * Validate bug report data
 */
function validateBugData(data) {
  const errors = [];

  // Required fields
  if (!data.title || typeof data.title !== 'string' || data.title.trim().length < 5) {
    errors.push('Title is required and must be at least 5 characters');
  }

  if (!data.description || typeof data.description !== 'string' || data.description.trim().length < 20) {
    errors.push('Description is required and must be at least 20 characters');
  }

  if (!data.module || !VALID_MODULES.includes(data.module)) {
    errors.push('Valid module selection is required');
  }

  if (!data.severity || !VALID_SEVERITIES.includes(data.severity)) {
    errors.push('Valid severity level is required');
  }

  // Reporter information
  if (!data.reporter || typeof data.reporter !== 'object') {
    errors.push('Reporter information is required');
  } else {
    if (!data.reporter.name || data.reporter.name.trim().length < 2) {
      errors.push('Reporter name is required and must be at least 2 characters');
    }

    if (!data.reporter.email || !isValidEmail(data.reporter.email)) {
      errors.push('Valid reporter email is required');
    }
  }

  // Optional field validation
  if (data.priority && !VALID_PRIORITIES.includes(data.priority)) {
    errors.push('Invalid priority level');
  }

  if (data.stepsToReproduce && !Array.isArray(data.stepsToReproduce)) {
    errors.push('Steps to reproduce must be an array');
  }

  if (data.tags && !Array.isArray(data.tags)) {
    errors.push('Tags must be an array');
  }

  if (data.attachments && !Array.isArray(data.attachments)) {
    errors.push('Attachments must be an array');
  }

  // Validate attachments
  if (data.attachments && data.attachments.length > 0) {
    data.attachments.forEach((attachment, index) => {
      if (!attachment.name || !attachment.type || !attachment.data) {
        errors.push(`Attachment ${index + 1}: Missing required fields (name, type, data)`);
      }

      // Check file size (if size provided)
      if (attachment.size && attachment.size > MAX_FILE_SIZE) {
        errors.push(`Attachment ${index + 1}: File too large (max ${MAX_FILE_SIZE / 1024 / 1024}MB)`);
      }

      // Check file type
      const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'text/plain', 'application/pdf'];
      if (!allowedTypes.includes(attachment.type)) {
        errors.push(`Attachment ${index + 1}: Unsupported file type`);
      }
    });
  }

  return {
    valid: errors.length === 0,
    errors,
    data: errors.length === 0 ? {
      ...data,
      title: data.title.trim(),
      description: data.description.trim(),
      priority: data.priority || 'Medium',
      stepsToReproduce: data.stepsToReproduce || [],
      tags: data.tags || [],
      attachments: data.attachments || [],
      timestamp: new Date().toISOString()
    } : null
  };
}

/**
 * Process bug submission and update data
 */
async function processBugSubmission(bugData, bugReports) {
  // Generate bug ID
  const bugId = generateBugId(bugReports.metadata.nextBugId);
  
  // Create bug object
  const bug = {
    id: bugId,
    title: bugData.title,
    description: bugData.description,
    module: bugData.module,
    severity: bugData.severity,
    priority: bugData.priority,
    status: 'Open',
    reporter: {
      name: bugData.reporter.name.trim(),
      email: bugData.reporter.email.toLowerCase().trim(),
      timestamp: bugData.timestamp
    },
    assignee: determineAssignee(bugData.module, bugData.severity),
    tags: bugData.tags.filter(tag => tag && tag.trim()),
    environment: bugData.environment || {},
    stepsToReproduce: bugData.stepsToReproduce.filter(step => step && step.trim()),
    expectedBehavior: bugData.expectedBehavior || '',
    actualBehavior: bugData.actualBehavior || '',
    adminNotes: '',
    internalLogs: [
      {
        timestamp: bugData.timestamp,
        author: 'System',
        note: 'Bug report submitted via web form',
        type: 'creation'
      }
    ],
    attachments: await processAttachments(bugData.attachments, bugId),
    relatedBugs: [],
    worklog: []
  };

  // Add bug to reports
  bugReports.bugs.unshift(bug); // Add to beginning for newest first

  // Update metadata
  updateMetadata(bugReports);

  // Update analytics
  updateAnalytics(bugReports);

  return {
    bugId,
    bug
  };
}

/**
 * Process and save attachments
 */
async function processAttachments(attachments, bugId) {
  if (!attachments || attachments.length === 0) {
    return [];
  }

  const processedAttachments = [];

  for (const attachment of attachments) {
    try {
      // Create bug-specific upload directory
      const bugUploadDir = path.join(UPLOAD_DIR, bugId);
      await fs.mkdir(bugUploadDir, { recursive: true });

      // Generate safe filename
      const safeFilename = sanitizeFilename(attachment.name);
      const filePath = path.join(bugUploadDir, safeFilename);

      // Save file (convert from base64 if needed)
      if (attachment.data.startsWith('data:')) {
        const base64Data = attachment.data.split(',')[1];
        await fs.writeFile(filePath, base64Data, 'base64');
      } else {
        await fs.writeFile(filePath, attachment.data);
      }

      processedAttachments.push({
        name: attachment.name,
        url: `/uploads/bugs/${bugId}/${safeFilename}`,
        type: attachment.type,
        size: attachment.size || 0
      });

    } catch (error) {
      console.error(`Failed to save attachment ${attachment.name}:`, error);
      // Continue processing other attachments
    }
  }

  return processedAttachments;
}

/**
 * Update metadata statistics
 */
function updateMetadata(bugReports) {
  const bugs = bugReports.bugs;
  
  bugReports.metadata.totalBugs = bugs.length;
  bugReports.metadata.openBugs = bugs.filter(b => b.status === 'Open').length;
  bugReports.metadata.inProgressBugs = bugs.filter(b => b.status === 'In Progress').length;
  bugReports.metadata.resolvedBugs = bugs.filter(b => b.status === 'Resolved').length;
  bugReports.metadata.nextBugId += 1;
  bugReports.metadata.lastUpdated = new Date().toISOString();
}

/**
 * Update analytics data
 */
function updateAnalytics(bugReports) {
  const bugs = bugReports.bugs;
  
  // Update bugs by module
  const moduleCount = {};
  bugs.forEach(bug => {
    moduleCount[bug.module] = (moduleCount[bug.module] || 0) + 1;
  });
  bugReports.analytics.bugsByModule = moduleCount;

  // Update bugs by severity
  const severityCount = {};
  bugs.forEach(bug => {
    severityCount[bug.severity] = (severityCount[bug.severity] || 0) + 1;
  });
  bugReports.analytics.bugsBySeverity = severityCount;

  // Update bugs by status
  const statusCount = {};
  bugs.forEach(bug => {
    statusCount[bug.status] = (statusCount[bug.status] || 0) + 1;
  });
  bugReports.analytics.bugsByStatus = statusCount;

  // Update trends (simplified)
  const today = new Date().toISOString().split('T')[0];
  const todayBugs = bugs.filter(bug => 
    bug.reporter.timestamp.startsWith(today)
  ).length;

  if (!bugReports.analytics.trends) {
    bugReports.analytics.trends = { daily: [] };
  }

  // Update or add today's count
  const existingDay = bugReports.analytics.trends.daily.find(d => d.date === today);
  if (existingDay) {
    existingDay.reported = todayBugs;
  } else {
    bugReports.analytics.trends.daily.push({
      date: today,
      reported: todayBugs,
      resolved: 0
    });
  }

  // Keep only last 30 days
  bugReports.analytics.trends.daily = bugReports.analytics.trends.daily
    .sort((a, b) => new Date(b.date) - new Date(a.date))
    .slice(0, 30);
}

/**
 * Send notifications for new bug
 */
async function sendBugNotifications(bug) {
  try {
    // Email notification to assignee (if configured)
    await sendEmailNotification(bug);
    
    // Discord notification (if configured)
    await sendDiscordNotification(bug);
    
    // Slack notification (if configured)
    await sendSlackNotification(bug);
    
  } catch (error) {
    console.error('Failed to send notifications:', error);
    // Don't fail the bug submission if notifications fail
  }
}

/**
 * Send email notification
 */
async function sendEmailNotification(bug) {
  // Placeholder for email notification
  // In production, integrate with email service (SendGrid, AWS SES, etc.)
  console.log(`Email notification sent for bug ${bug.id} to ${bug.assignee}`);
}

/**
 * Send Discord notification
 */
async function sendDiscordNotification(bug) {
  try {
    // Import Discord webhook manager
    const { sendBugReport } = require('./hooks/discord-webhook.js');
    
    // Prepare bug data for Discord
    const webhookData = {
      bugId: bug.id,
      title: bug.title,
      description: bug.description,
      severity: bug.severity,
      module: bug.module,
      reporter: {
        name: bug.reporter.name,
        email: bug.reporter.email,
        contact: formatContactInfo(bug.reporter)
      },
      environment: bug.environment,
      status: bug.status,
      assignee: bug.assignee,
      tags: bug.tags,
      timestamp: bug.reporter.timestamp,
      url: `${process.env.BASE_URL || 'https://morningstar.ms11.com'}/internal/bugs/${bug.id}`
    };
    
    // Send to Discord webhook
    const result = await sendBugReport(webhookData);
    
    if (result.success) {
      console.log(`Discord notification sent successfully for bug ${bug.id}`);
      
      // Add internal log entry
      bug.internalLogs.push({
        timestamp: new Date().toISOString(),
        author: 'System',
        note: 'Discord notification sent successfully',
        type: 'notification'
      });
    } else {
      console.error(`Discord notification failed for bug ${bug.id}:`, result.error);
      
      // Add internal log entry for failure
      bug.internalLogs.push({
        timestamp: new Date().toISOString(),
        author: 'System',
        note: `Discord notification failed: ${result.error || result.reason}`,
        type: 'notification_failed'
      });
    }
    
    return result;
    
  } catch (error) {
    console.error('Discord webhook integration error:', error);
    
    // Add internal log entry for error
    if (bug.internalLogs) {
      bug.internalLogs.push({
        timestamp: new Date().toISOString(),
        author: 'System',
        note: `Discord notification error: ${error.message}`,
        type: 'notification_error'
      });
    }
    
    return { success: false, error: error.message };
  }
}

/**
 * Format contact information for display
 */
function formatContactInfo(reporter) {
  const contact = [];
  
  if (reporter.email) {
    // Mask email for privacy
    const emailParts = reporter.email.split('@');
    const maskedEmail = emailParts[0].substring(0, 2) + '***@' + emailParts[1];
    contact.push(`Email: ${maskedEmail}`);
  }
  
  if (reporter.discordId) {
    contact.push(`Discord: ${reporter.discordId}`);
  }
  
  return contact.length > 0 ? contact.join('\n') : 'Not provided';
}

/**
 * Send Slack notification
 */
async function sendSlackNotification(bug) {
  // Placeholder for Slack webhook
  // In production, send to configured Slack webhook
  console.log(`Slack notification sent for bug ${bug.id}`);
}

/**
 * Utility functions
 */
function getClientId(req) {
  return req.headers['x-forwarded-for'] || req.connection.remoteAddress || 'unknown';
}

function checkRateLimit(clientId) {
  const now = Date.now();
  const windowStart = now - RATE_LIMIT_WINDOW;
  
  if (!rateLimitStore.has(clientId)) {
    rateLimitStore.set(clientId, []);
  }
  
  const requests = rateLimitStore.get(clientId);
  const recentRequests = requests.filter(time => time > windowStart);
  
  if (recentRequests.length >= MAX_REQUESTS_PER_WINDOW) {
    return false;
  }
  
  recentRequests.push(now);
  rateLimitStore.set(clientId, recentRequests);
  return true;
}

function generateBugId(nextId) {
  return `BUG-${nextId.toString().padStart(3, '0')}`;
}

function determineAssignee(module, severity) {
  // Simple assignee determination logic
  const assignments = {
    'MS11-Core': 'frontend-team',
    'MS11-Combat': 'combat-team',
    'MS11-Heroics': 'heroics-team',
    'MS11-Discord': 'integration-team',
    'SWGDB': 'backend-team',
    'Website': 'ui-team',
    'API': 'backend-team',
    'Database': 'data-team',
    'Infrastructure': 'devops-team'
  };

  const baseAssignee = assignments[module] || 'dev-team';
  
  // Escalate critical and high severity bugs
  if (severity === 'Critical') {
    return 'senior-dev-team';
  }
  
  return baseAssignee;
}

function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

function sanitizeFilename(filename) {
  return filename.replace(/[^a-zA-Z0-9.-]/g, '_');
}

async function loadBugReports() {
  try {
    const data = await fs.readFile(BUG_REPORTS_FILE, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    if (error.code === 'ENOENT') {
      // File doesn't exist, return default structure
      return getDefaultBugReports();
    }
    throw error;
  }
}

async function saveBugReports(data) {
  // Ensure directory exists
  await fs.mkdir(path.dirname(BUG_REPORTS_FILE), { recursive: true });
  
  // Create backup before saving
  try {
    const backupPath = BUG_REPORTS_FILE + '.backup';
    await fs.copyFile(BUG_REPORTS_FILE, backupPath);
  } catch (error) {
    // Backup failed, but continue with save
    console.warn('Failed to create backup:', error.message);
  }
  
  await fs.writeFile(BUG_REPORTS_FILE, JSON.stringify(data, null, 2), 'utf8');
}

function getDefaultBugReports() {
  return {
    metadata: {
      version: "1.0.0",
      lastUpdated: new Date().toISOString(),
      totalBugs: 0,
      openBugs: 0,
      inProgressBugs: 0,
      resolvedBugs: 0,
      nextBugId: 1
    },
    bugs: [],
    categories: {
      modules: VALID_MODULES,
      severities: [
        { level: "Critical", description: "System down, data loss, security breach", color: "#e74c3c" },
        { level: "High", description: "Major functionality broken, significant user impact", color: "#e67e22" },
        { level: "Medium", description: "Minor functionality issues, workaround available", color: "#f39c12" },
        { level: "Low", description: "Cosmetic issues, nice-to-have improvements", color: "#27ae60" }
      ],
      statuses: [
        { name: "Open", description: "Bug reported and confirmed, awaiting assignment", color: "#ff6b35" },
        { name: "In Progress", description: "Bug is being actively worked on", color: "#f39c12" },
        { name: "Resolved", description: "Bug has been fixed and tested", color: "#27ae60" },
        { name: "Closed", description: "Bug resolved and verified by reporter", color: "#95a5a6" },
        { name: "Duplicate", description: "Bug is a duplicate of another report", color: "#9b59b6" },
        { name: "Won't Fix", description: "Bug will not be addressed", color: "#e74c3c" }
      ],
      priorities: VALID_PRIORITIES
    },
    analytics: {
      bugsByModule: {},
      bugsBySeverity: {},
      bugsByStatus: {},
      trends: {
        daily: [],
        weekly: [],
        monthly: []
      },
      averageResolutionTime: {
        hours: 0,
        businessDays: 0
      },
      topReporters: []
    }
  };
}