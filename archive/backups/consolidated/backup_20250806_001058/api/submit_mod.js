/**
 * Mod Submission API Endpoint with Discord Webhook Integration
 * Handles mod submission processing, validation, security scanning, and notifications
 */

const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');

// Configuration
const MOD_SUBMISSIONS_FILE = path.join(__dirname, '../src/data/mods/submissions.json');
const UPLOAD_DIR = path.join(__dirname, '../uploads/mods');
const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB
const MAX_TOTAL_SIZE = 100 * 1024 * 1024; // 100MB total
const RATE_LIMIT_WINDOW = 300000; // 5 minutes
const MAX_REQUESTS_PER_WINDOW = 3;

// In-memory rate limiting (in production, use Redis or similar)
const rateLimitStore = new Map();

// Valid values for validation
const VALID_CATEGORIES = [
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
];

const VALID_GAME_VERSIONS = ['Pre-CU', 'CU', 'NGE', 'JTL', 'ROTW', 'Legends', 'Custom'];
const VALID_STATUSES = ['Submitted', 'Under Review', 'Testing', 'Approved', 'Rejected', 'Published'];
const ALLOWED_FILE_TYPES = [
  'application/zip',
  'application/x-zip-compressed',
  'application/x-rar-compressed',
  'application/x-7z-compressed',
  'image/jpeg',
  'image/png',
  'image/gif',
  'text/plain',
  'text/markdown'
];

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
        return await handleModSubmission(req, res);
      case 'GET':
        return await handleModRetrieval(req, res);
      default:
        return res.status(405).json({ 
          error: 'Method not allowed',
          allowedMethods: ['GET', 'POST']
        });
    }
  } catch (error) {
    console.error('Mod API Error:', error);
    return res.status(500).json({
      error: 'Internal server error',
      message: process.env.NODE_ENV === 'development' ? error.message : 'Something went wrong'
    });
  }
}

/**
 * Handle mod submission
 */
async function handleModSubmission(req, res) {
  // Rate limiting
  const clientId = getClientId(req);
  if (!checkRateLimit(clientId)) {
    return res.status(429).json({
      error: 'Rate limit exceeded',
      message: 'Too many mod submissions. Please wait before submitting another.'
    });
  }

  // Validate request body
  const validation = validateModData(req.body);
  if (!validation.valid) {
    return res.status(400).json({
      error: 'Validation failed',
      details: validation.errors
    });
  }

  const modData = validation.data;

  try {
    // Load current mod submissions
    const modSubmissions = await loadModSubmissions();
    
    // Process the mod submission
    const result = await processModSubmission(modData, modSubmissions);
    
    // Save updated data
    await saveModSubmissions(modSubmissions);
    
    // Send notifications (Discord webhook and others)
    await sendModNotifications(result.submission);
    
    // Return success response
    return res.status(201).json({
      success: true,
      message: 'Mod submitted successfully',
      submissionId: result.submissionId,
      status: result.submission.status,
      estimatedReviewTime: '48-72 hours'
    });

  } catch (error) {
    console.error('Mod submission error:', error);
    return res.status(500).json({
      error: 'Failed to submit mod',
      message: 'Could not save mod submission data'
    });
  }
}

/**
 * Handle mod retrieval
 */
async function handleModRetrieval(req, res) {
  const { id, category, status, author, limit, offset } = req.query;

  try {
    const modSubmissions = await loadModSubmissions();
    
    if (id) {
      // Get specific submission
      const submission = modSubmissions.submissions.find(s => s.id === id);
      if (!submission) {
        return res.status(404).json({ error: 'Mod submission not found' });
      }
      return res.json(submission);
    }

    // Filter submissions based on query parameters
    let filteredSubmissions = modSubmissions.submissions;

    if (category) {
      filteredSubmissions = filteredSubmissions.filter(sub => sub.category === category);
    }

    if (status) {
      filteredSubmissions = filteredSubmissions.filter(sub => sub.status === status);
    }

    if (author) {
      filteredSubmissions = filteredSubmissions.filter(sub => 
        sub.author.name.toLowerCase().includes(author.toLowerCase())
      );
    }

    // Apply pagination
    const limitNum = parseInt(limit) || 50;
    const offsetNum = parseInt(offset) || 0;
    const paginatedSubmissions = filteredSubmissions.slice(offsetNum, offsetNum + limitNum);

    return res.json({
      submissions: paginatedSubmissions,
      total: filteredSubmissions.length,
      limit: limitNum,
      offset: offsetNum,
      metadata: modSubmissions.metadata
    });

  } catch (error) {
    console.error('Mod retrieval error:', error);
    return res.status(500).json({
      error: 'Failed to retrieve mod submissions'
    });
  }
}

/**
 * Validate mod submission data
 */
function validateModData(data) {
  const errors = [];

  // Required fields
  if (!data.title || typeof data.title !== 'string' || data.title.trim().length < 5) {
    errors.push('Title is required and must be at least 5 characters');
  }

  if (!data.description || typeof data.description !== 'string' || data.description.trim().length < 20) {
    errors.push('Description is required and must be at least 20 characters');
  }

  if (!data.version || typeof data.version !== 'string' || !isValidVersion(data.version)) {
    errors.push('Valid version number is required (e.g., 1.0.0)');
  }

  if (!data.category || !VALID_CATEGORIES.includes(data.category)) {
    errors.push('Valid category selection is required');
  }

  // Author information
  if (!data.author || typeof data.author !== 'object') {
    errors.push('Author information is required');
  } else {
    if (!data.author.name || data.author.name.trim().length < 2) {
      errors.push('Author name is required and must be at least 2 characters');
    }

    // At least one contact method required
    if (!data.author.email && !data.author.discordId) {
      errors.push('At least one contact method (email or Discord ID) is required');
    }

    if (data.author.email && !isValidEmail(data.author.email)) {
      errors.push('Valid email address is required');
    }

    if (data.author.discordId && !isValidDiscordId(data.author.discordId)) {
      errors.push('Valid Discord ID format is required');
    }
  }

  // Files validation
  if (!data.files || !Array.isArray(data.files) || data.files.length === 0) {
    errors.push('At least one file is required for mod submission');
  } else {
    let totalSize = 0;
    
    data.files.forEach((file, index) => {
      if (!file.name || !file.type || !file.data) {
        errors.push(`File ${index + 1}: Missing required fields (name, type, data)`);
      }

      // Check file size
      if (file.size && file.size > MAX_FILE_SIZE) {
        errors.push(`File ${index + 1}: File too large (max ${MAX_FILE_SIZE / 1024 / 1024}MB)`);
      }

      totalSize += file.size || 0;

      // Check file type
      if (file.type && !ALLOWED_FILE_TYPES.includes(file.type)) {
        errors.push(`File ${index + 1}: Unsupported file type (${file.type})`);
      }
    });

    if (totalSize > MAX_TOTAL_SIZE) {
      errors.push(`Total file size too large (max ${MAX_TOTAL_SIZE / 1024 / 1024}MB)`);
    }
  }

  // Optional field validation
  if (data.gameVersion && !VALID_GAME_VERSIONS.includes(data.gameVersion)) {
    errors.push('Invalid game version');
  }

  if (data.tags && !Array.isArray(data.tags)) {
    errors.push('Tags must be an array');
  }

  if (data.dependencies && !Array.isArray(data.dependencies)) {
    errors.push('Dependencies must be an array');
  }

  // Security disclaimer requirement
  if (!data.disclaimer) {
    errors.push('Security disclaimer acceptance is required');
  }

  if (!data.termsAccepted) {
    errors.push('Terms of service acceptance is required');
  }

  return {
    valid: errors.length === 0,
    errors,
    data: errors.length === 0 ? {
      ...data,
      title: data.title.trim(),
      description: data.description.trim(),
      gameVersion: data.gameVersion || 'NGE',
      tags: data.tags || [],
      dependencies: data.dependencies || [],
      timestamp: new Date().toISOString()
    } : null
  };
}

/**
 * Process mod submission and update data
 */
async function processModSubmission(modData, modSubmissions) {
  // Generate submission ID
  const submissionId = generateSubmissionId(modSubmissions.metadata.nextSubmissionId);
  
  // Create submission object
  const submission = {
    id: submissionId,
    title: modData.title,
    description: modData.description,
    version: modData.version,
    category: modData.category,
    gameVersion: modData.gameVersion,
    status: 'Submitted',
    author: {
      name: modData.author.name.trim(),
      email: modData.author.email ? modData.author.email.toLowerCase().trim() : null,
      discordId: modData.author.discordId ? modData.author.discordId.trim() : null,
      timestamp: modData.timestamp
    },
    tags: modData.tags.filter(tag => tag && tag.trim()),
    dependencies: modData.dependencies || [],
    installationInstructions: modData.installationInstructions || '',
    changelog: modData.changelog || '',
    compatibility: modData.compatibility || {},
    files: await processFiles(modData.files, submissionId),
    securityScan: {
      status: 'Pending',
      scannedAt: null,
      results: {}
    },
    review: {
      assignee: determineReviewer(modData.category),
      startedAt: null,
      completedAt: null,
      notes: []
    },
    testing: {
      status: 'Pending',
      testers: [],
      results: []
    },
    adminNotes: '',
    internalLogs: [
      {
        timestamp: modData.timestamp,
        author: 'System',
        note: 'Mod submission received via web form',
        type: 'creation'
      }
    ],
    downloads: 0,
    rating: 0,
    reviews: []
  };

  // Add submission to array
  modSubmissions.submissions.unshift(submission); // Add to beginning for newest first

  // Update metadata
  updateMetadata(modSubmissions);

  // Update analytics
  updateAnalytics(modSubmissions);

  return {
    submissionId,
    submission
  };
}

/**
 * Process and save mod files
 */
async function processFiles(files, submissionId) {
  if (!files || files.length === 0) {
    return [];
  }

  const processedFiles = [];

  for (const file of files) {
    try {
      // Create submission-specific upload directory
      const submissionUploadDir = path.join(UPLOAD_DIR, submissionId);
      await fs.mkdir(submissionUploadDir, { recursive: true });

      // Generate safe filename
      const safeFilename = sanitizeFilename(file.name);
      const filePath = path.join(submissionUploadDir, safeFilename);

      // Save file (convert from base64 if needed)
      if (file.data.startsWith('data:')) {
        const base64Data = file.data.split(',')[1];
        await fs.writeFile(filePath, base64Data, 'base64');
      } else {
        await fs.writeFile(filePath, file.data);
      }

      processedFiles.push({
        name: file.name,
        url: `/uploads/mods/${submissionId}/${safeFilename}`,
        type: file.type,
        size: file.size || 0,
        uploadedAt: new Date().toISOString()
      });

    } catch (error) {
      console.error(`Failed to save file ${file.name}:`, error);
      // Continue processing other files
    }
  }

  return processedFiles;
}

/**
 * Send notifications for new mod submission
 */
async function sendModNotifications(submission) {
  try {
    // Discord notification (primary)
    await sendDiscordNotification(submission);
    
    // Email notification to reviewers (if configured)
    await sendEmailNotification(submission);
    
    // Slack notification (if configured)
    await sendSlackNotification(submission);
    
  } catch (error) {
    console.error('Failed to send notifications:', error);
    // Don't fail the submission if notifications fail
  }
}

/**
 * Send Discord notification with webhook integration
 */
async function sendDiscordNotification(submission) {
  try {
    // Import Discord webhook manager
    const { sendModSubmission } = require('./hooks/discord-webhook.js');
    
    // Prepare submission data for Discord
    const webhookData = {
      submissionId: submission.id,
      title: submission.title,
      description: submission.description,
      version: submission.version,
      category: submission.category,
      gameVersion: submission.gameVersion,
      author: {
        name: submission.author.name,
        email: submission.author.email,
        discordId: submission.author.discordId,
        contact: formatContactInfo(submission.author)
      },
      tags: submission.tags,
      files: submission.files,
      status: submission.status,
      assignee: submission.review.assignee,
      timestamp: submission.author.timestamp,
      url: `${process.env.BASE_URL || 'https://morningstar.ms11.com'}/mods/review/${submission.id}`,
      thumbnail: submission.files.find(f => f.type.startsWith('image/'))?.url
    };
    
    // Send to Discord webhook
    const result = await sendModSubmission(webhookData);
    
    if (result.success) {
      console.log(`Discord notification sent successfully for mod ${submission.id}`);
      
      // Add internal log entry
      submission.internalLogs.push({
        timestamp: new Date().toISOString(),
        author: 'System',
        note: 'Discord notification sent successfully',
        type: 'notification'
      });
    } else {
      console.error(`Discord notification failed for mod ${submission.id}:`, result.error);
      
      // Add internal log entry for failure
      submission.internalLogs.push({
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
    if (submission.internalLogs) {
      submission.internalLogs.push({
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
 * Send email notification
 */
async function sendEmailNotification(submission) {
  // Placeholder for email notification
  // In production, integrate with email service (SendGrid, AWS SES, etc.)
  console.log(`Email notification sent for mod ${submission.id} to ${submission.review.assignee}`);
}

/**
 * Send Slack notification
 */
async function sendSlackNotification(submission) {
  // Placeholder for Slack webhook
  // In production, send to configured Slack webhook
  console.log(`Slack notification sent for mod ${submission.id}`);
}

/**
 * Format contact information for display
 */
function formatContactInfo(author) {
  const contact = [];
  
  if (author.email) {
    // Mask email for privacy
    const emailParts = author.email.split('@');
    const maskedEmail = emailParts[0].substring(0, 2) + '***@' + emailParts[1];
    contact.push(`Email: ${maskedEmail}`);
  }
  
  if (author.discordId) {
    contact.push(`Discord: ${author.discordId}`);
  }
  
  return contact.length > 0 ? contact.join('\n') : 'Not provided';
}

/**
 * Update metadata statistics
 */
function updateMetadata(modSubmissions) {
  const submissions = modSubmissions.submissions;
  
  modSubmissions.metadata.totalSubmissions = submissions.length;
  modSubmissions.metadata.pendingReview = submissions.filter(s => s.status === 'Submitted').length;
  modSubmissions.metadata.underReview = submissions.filter(s => s.status === 'Under Review').length;
  modSubmissions.metadata.approved = submissions.filter(s => s.status === 'Approved').length;
  modSubmissions.metadata.published = submissions.filter(s => s.status === 'Published').length;
  modSubmissions.metadata.nextSubmissionId += 1;
  modSubmissions.metadata.lastUpdated = new Date().toISOString();
}

/**
 * Update analytics data
 */
function updateAnalytics(modSubmissions) {
  const submissions = modSubmissions.submissions;
  
  // Update submissions by category
  const categoryCount = {};
  submissions.forEach(sub => {
    categoryCount[sub.category] = (categoryCount[sub.category] || 0) + 1;
  });
  modSubmissions.analytics.submissionsByCategory = categoryCount;

  // Update submissions by status
  const statusCount = {};
  submissions.forEach(sub => {
    statusCount[sub.status] = (statusCount[sub.status] || 0) + 1;
  });
  modSubmissions.analytics.submissionsByStatus = statusCount;

  // Update submissions by game version
  const versionCount = {};
  submissions.forEach(sub => {
    versionCount[sub.gameVersion] = (versionCount[sub.gameVersion] || 0) + 1;
  });
  modSubmissions.analytics.submissionsByGameVersion = versionCount;

  // Update trends
  const today = new Date().toISOString().split('T')[0];
  const todaySubmissions = submissions.filter(sub => 
    sub.author.timestamp.startsWith(today)
  ).length;

  if (!modSubmissions.analytics.trends) {
    modSubmissions.analytics.trends = { daily: [] };
  }

  // Update or add today's count
  const existingDay = modSubmissions.analytics.trends.daily.find(d => d.date === today);
  if (existingDay) {
    existingDay.submissions = todaySubmissions;
  } else {
    modSubmissions.analytics.trends.daily.push({
      date: today,
      submissions: todaySubmissions,
      approved: 0
    });
  }

  // Keep only last 30 days
  modSubmissions.analytics.trends.daily = modSubmissions.analytics.trends.daily
    .sort((a, b) => new Date(b.date) - new Date(a.date))
    .slice(0, 30);
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

function generateSubmissionId(nextId) {
  return `MOD-${nextId.toString().padStart(4, '0')}`;
}

function determineReviewer(category) {
  // Simple reviewer assignment logic
  const assignments = {
    'UI Enhancement': 'ui-review-team',
    'Gameplay': 'gameplay-team',
    'Quality of Life': 'qol-team',
    'Visual': 'visual-team',
    'Audio': 'audio-team',
    'Performance': 'performance-team',
    'Utility': 'utility-team',
    'Bug Fix': 'bugfix-team',
    'Content': 'content-team',
    'Other': 'general-review-team'
  };

  return assignments[category] || 'general-review-team';
}

function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

function isValidDiscordId(discordId) {
  // Support legacy format (username#1234) and new format (@username)
  const legacyFormat = /^.{2,32}#[0-9]{4}$/;
  const newFormat = /^@[a-zA-Z0-9_]{2,32}$/;
  return legacyFormat.test(discordId) || newFormat.test(discordId);
}

function isValidVersion(version) {
  // Semantic versioning: 1.0.0, 2.1.3-beta, etc.
  const versionRegex = /^\d+\.\d+(\.\d+)?(-[a-zA-Z0-9]+)?$/;
  return versionRegex.test(version);
}

function sanitizeFilename(filename) {
  return filename.replace(/[^a-zA-Z0-9.-]/g, '_');
}

async function loadModSubmissions() {
  try {
    const data = await fs.readFile(MOD_SUBMISSIONS_FILE, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    if (error.code === 'ENOENT') {
      // File doesn't exist, return default structure
      return getDefaultModSubmissions();
    }
    throw error;
  }
}

async function saveModSubmissions(data) {
  // Ensure directory exists
  await fs.mkdir(path.dirname(MOD_SUBMISSIONS_FILE), { recursive: true });
  
  // Create backup before saving
  try {
    const backupPath = MOD_SUBMISSIONS_FILE + '.backup';
    await fs.copyFile(MOD_SUBMISSIONS_FILE, backupPath);
  } catch (error) {
    // Backup failed, but continue with save
    console.warn('Failed to create backup:', error.message);
  }
  
  await fs.writeFile(MOD_SUBMISSIONS_FILE, JSON.stringify(data, null, 2), 'utf8');
}

function getDefaultModSubmissions() {
  return {
    metadata: {
      version: "1.0.0",
      lastUpdated: new Date().toISOString(),
      totalSubmissions: 0,
      pendingReview: 0,
      underReview: 0,
      approved: 0,
      published: 0,
      nextSubmissionId: 1
    },
    submissions: [],
    categories: {
      available: VALID_CATEGORIES,
      gameVersions: VALID_GAME_VERSIONS,
      statuses: [
        { name: "Submitted", description: "Initial submission received", color: "#3498db" },
        { name: "Under Review", description: "Being reviewed by team", color: "#f39c12" },
        { name: "Testing", description: "In community testing phase", color: "#9b59b6" },
        { name: "Approved", description: "Approved for publication", color: "#27ae60" },
        { name: "Rejected", description: "Submission rejected", color: "#e74c3c" },
        { name: "Published", description: "Available for download", color: "#2ecc71" }
      ]
    },
    analytics: {
      submissionsByCategory: {},
      submissionsByStatus: {},
      submissionsByGameVersion: {},
      trends: {
        daily: [],
        weekly: [],
        monthly: []
      },
      averageReviewTime: {
        hours: 0,
        businessDays: 0
      },
      topContributors: []
    }
  };
}