/**
 * Error Handling Library for MorningStar SWG
 * Provides error reporting, logging, and Discord integration
 */

// Configuration
const ERROR_CONFIG = {
  // Internal logging
  logToConsole: true,
  logToServer: true,
  logEndpoint: '/api/errors/log',
  
  // Discord integration
  discordWebhook: process.env.DISCORD_ERROR_WEBHOOK || 'https://discord.com/api/webhooks/your-webhook-url',
  discordPingRoles: ['@here', '@everyone'], // Roles to ping for critical errors
  
  // Error categorization
  criticalErrors: [
    'TypeError',
    'ReferenceError',
    'SyntaxError',
    'RangeError',
    'EvalError',
    'URIError'
  ],
  
  // Rate limiting
  maxErrorsPerMinute: 10,
  maxDiscordPingsPerHour: 5,
  
  // Error storage
  maxStoredErrors: 100,
  errorRetentionDays: 7
};

// Error storage
let errorLog = [];
let discordPingCount = 0;
let lastDiscordPing = 0;

/**
 * Main error handling function
 * @param {Object} errorData - Error information
 * @param {Error} errorData.error - The error object
 * @param {Object} errorData.errorInfo - Additional error information
 * @param {string} errorData.errorId - Unique error ID
 * @param {string} errorData.errorBoundaryId - Error boundary ID
 * @param {string} errorData.logLevel - Log level (error, warn, info)
 * @param {boolean} errorData.discordPing - Whether to ping Discord
 */
export function handleError(errorData) {
  const {
    error,
    errorInfo,
    errorId,
    errorBoundaryId,
    logLevel = 'error',
    discordPing = false
  } = errorData;
  
  // Create error entry
  const errorEntry = {
    id: errorId,
    errorBoundaryId: errorBoundaryId,
    timestamp: new Date().toISOString(),
    level: logLevel,
    message: error?.message || 'Unknown error',
    name: error?.name || 'Error',
    stack: error?.stack,
    componentStack: errorInfo?.componentStack,
    url: window.location.href,
    userAgent: navigator.userAgent,
    viewport: {
      width: window.innerWidth,
      height: window.innerHeight
    },
    session: {
      id: getSessionId(),
      duration: getSessionDuration()
    }
  };
  
  // Add to error log
  addToErrorLog(errorEntry);
  
  // Console logging
  if (ERROR_CONFIG.logToConsole) {
    logToConsole(errorEntry);
  }
  
  // Server logging
  if (ERROR_CONFIG.logToServer) {
    logToServer(errorEntry);
  }
  
  // Discord integration
  if (discordPing && shouldPingDiscord(errorEntry)) {
    pingDiscord(errorEntry);
  }
  
  // Analytics tracking
  trackErrorAnalytics(errorEntry);
}

/**
 * Add error to local storage
 */
function addToErrorLog(errorEntry) {
  errorLog.push(errorEntry);
  
  // Limit stored errors
  if (errorLog.length > ERROR_CONFIG.maxStoredErrors) {
    errorLog = errorLog.slice(-ERROR_CONFIG.maxStoredErrors);
  }
  
  // Store in localStorage for persistence
  try {
    localStorage.setItem('ms11_error_log', JSON.stringify(errorLog));
  } catch (e) {
    console.warn('Failed to store error in localStorage:', e);
  }
}

/**
 * Console logging with formatting
 */
function logToConsole(errorEntry) {
  const { level, message, name, stack, componentStack } = errorEntry;
  
  const logMethod = level === 'error' ? 'error' : level === 'warn' ? 'warn' : 'info';
  
  console.group(`🚨 ${name}: ${message}`);
  console.log('Error ID:', errorEntry.id);
  console.log('Timestamp:', errorEntry.timestamp);
  console.log('URL:', errorEntry.url);
  
  if (stack) {
    console.log('Stack trace:', stack);
  }
  
  if (componentStack) {
    console.log('Component stack:', componentStack);
  }
  
  console.groupEnd();
}

/**
 * Send error to server
 */
async function logToServer(errorEntry) {
  try {
    const response = await fetch(ERROR_CONFIG.logEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(errorEntry)
    });
    
    if (!response.ok) {
      console.warn('Failed to log error to server:', response.status);
    }
  } catch (error) {
    console.warn('Failed to send error to server:', error);
  }
}

/**
 * Determine if Discord should be pinged
 */
function shouldPingDiscord(errorEntry) {
  const now = Date.now();
  const oneHour = 60 * 60 * 1000;
  
  // Check rate limiting
  if (discordPingCount >= ERROR_CONFIG.maxDiscordPingsPerHour) {
    if (now - lastDiscordPing < oneHour) {
      return false;
    } else {
      // Reset counter after an hour
      discordPingCount = 0;
    }
  }
  
  // Check if it's a critical error
  const isCritical = ERROR_CONFIG.criticalErrors.includes(errorEntry.name);
  
  return isCritical;
}

/**
 * Send Discord notification
 */
async function pingDiscord(errorEntry) {
  try {
    const embed = {
      title: '🚨 Critical Error Detected',
      color: 0xff0000,
      fields: [
        {
          name: 'Error',
          value: `${errorEntry.name}: ${errorEntry.message}`,
          inline: false
        },
        {
          name: 'Error ID',
          value: errorEntry.id,
          inline: true
        },
        {
          name: 'URL',
          value: errorEntry.url,
          inline: true
        },
        {
          name: 'Timestamp',
          value: new Date(errorEntry.timestamp).toLocaleString(),
          inline: true
        }
      ],
      footer: {
        text: 'MorningStar SWG Error Monitoring'
      },
      timestamp: errorEntry.timestamp
    };
    
    // Add stack trace if available (truncated)
    if (errorEntry.stack) {
      const truncatedStack = errorEntry.stack.split('\n').slice(0, 5).join('\n');
      embed.fields.push({
        name: 'Stack Trace',
        value: `\`\`\`\n${truncatedStack}\n\`\`\``,
        inline: false
      });
    }
    
    const payload = {
      content: ERROR_CONFIG.discordPingRoles.join(' ') + ' Critical error detected!',
      embeds: [embed]
    };
    
    const response = await fetch(ERROR_CONFIG.discordWebhook, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    });
    
    if (response.ok) {
      discordPingCount++;
      lastDiscordPing = Date.now();
      console.log('Discord notification sent successfully');
    } else {
      console.warn('Failed to send Discord notification:', response.status);
    }
  } catch (error) {
    console.warn('Failed to send Discord notification:', error);
  }
}

/**
 * Track error analytics
 */
function trackErrorAnalytics(errorEntry) {
  // Track in analytics if available
  if (typeof gtag !== 'undefined') {
    gtag('event', 'error', {
      error_id: errorEntry.id,
      error_name: errorEntry.name,
      error_message: errorEntry.message,
      page_url: errorEntry.url
    });
  }
  
  // Track in custom analytics
  if (window.ms11Analytics) {
    window.ms11Analytics.track('error', {
      error_id: errorEntry.id,
      error_name: errorEntry.name,
      error_message: errorEntry.message,
      page_url: errorEntry.url,
      user_agent: errorEntry.userAgent
    });
  }
}

/**
 * Get session ID
 */
function getSessionId() {
  let sessionId = sessionStorage.getItem('ms11_session_id');
  if (!sessionId) {
    sessionId = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
    sessionStorage.setItem('ms11_session_id', sessionId);
  }
  return sessionId;
}

/**
 * Get session duration
 */
function getSessionDuration() {
  const sessionStart = sessionStorage.getItem('ms11_session_start');
  if (!sessionStart) {
    const now = Date.now();
    sessionStorage.setItem('ms11_session_start', now.toString());
    return 0;
  }
  return Date.now() - parseInt(sessionStart);
}

/**
 * Get error statistics
 */
export function getErrorStats() {
  const now = Date.now();
  const oneDay = 24 * 60 * 60 * 1000;
  
  const recentErrors = errorLog.filter(error => 
    now - new Date(error.timestamp).getTime() < oneDay
  );
  
  return {
    totalErrors: errorLog.length,
    recentErrors: recentErrors.length,
    criticalErrors: recentErrors.filter(error => 
      ERROR_CONFIG.criticalErrors.includes(error.name)
    ).length,
    discordPings: discordPingCount,
    lastDiscordPing: lastDiscordPing
  };
}

/**
 * Clear error log
 */
export function clearErrorLog() {
  errorLog = [];
  try {
    localStorage.removeItem('ms11_error_log');
  } catch (e) {
    console.warn('Failed to clear error log from localStorage:', e);
  }
}

/**
 * Get error log
 */
export function getErrorLog() {
  return [...errorLog];
}

/**
 * Initialize error handling
 */
export function initializeErrorHandling() {
  // Load stored errors
  try {
    const stored = localStorage.getItem('ms11_error_log');
    if (stored) {
      errorLog = JSON.parse(stored);
    }
  } catch (e) {
    console.warn('Failed to load stored errors:', e);
  }
  
  // Set up global error handlers
  window.addEventListener('error', (event) => {
    handleError({
      error: event.error,
      errorInfo: { componentStack: 'Global error handler' },
      errorId: `global-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      errorBoundaryId: 'global',
      logLevel: 'error',
      discordPing: true
    });
  });
  
  window.addEventListener('unhandledrejection', (event) => {
    handleError({
      error: new Error(event.reason),
      errorInfo: { componentStack: 'Unhandled promise rejection' },
      errorId: `promise-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      errorBoundaryId: 'global',
      logLevel: 'error',
      discordPing: true
    });
  });
  
  console.log('Error handling system initialized');
}

// Auto-initialize if in browser environment
if (typeof window !== 'undefined') {
  initializeErrorHandling();
} 