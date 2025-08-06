/**
 * Discord Webhook Integration for MorningStar
 * Real-time notifications for mod submissions and bug reports with rich embeds
 */

const fs = require('fs');
const path = require('path');
const https = require('https');
const crypto = require('crypto');

class DiscordWebhookManager {
    constructor() {
        this.configPath = path.join(__dirname, '../../config/webhooks.json');
        this.config = this.loadConfiguration();
        this.rateLimits = new Map();
        this.retryQueue = [];
        this.webhookStats = {
            sent: 0,
            failed: 0,
            retries: 0,
            lastSent: null
        };
    }

    /**
     * Load webhook configuration
     */
    loadConfiguration() {
        try {
            if (fs.existsSync(this.configPath)) {
                const configData = fs.readFileSync(this.configPath, 'utf8');
                return JSON.parse(configData);
            }
            
            // Return default configuration if file doesn't exist
            return this.getDefaultConfiguration();
        } catch (error) {
            console.error('Failed to load webhook configuration:', error);
            return this.getDefaultConfiguration();
        }
    }

    /**
     * Get default webhook configuration
     */
    getDefaultConfiguration() {
        return {
            enabled: true,
            webhooks: {
                modSubmissions: {
                    url: process.env.DISCORD_MOD_WEBHOOK_URL || '',
                    name: 'Mod Submissions',
                    avatar: 'https://cdn.discordapp.com/avatars/mod-bot.png',
                    enabled: true,
                    mentions: ['@ModTeam'],
                    channels: ['mod-submissions', 'general']
                },
                bugReports: {
                    url: process.env.DISCORD_BUG_WEBHOOK_URL || '',
                    name: 'Bug Reports',
                    avatar: 'https://cdn.discordapp.com/avatars/bug-bot.png',
                    enabled: true,
                    mentions: ['@BugSquad', '@Developers'],
                    channels: ['bug-reports', 'development']
                },
                general: {
                    url: process.env.DISCORD_GENERAL_WEBHOOK_URL || '',
                    name: 'MorningStar Notifications',
                    avatar: 'https://cdn.discordapp.com/avatars/general-bot.png',
                    enabled: true,
                    mentions: ['@everyone'],
                    channels: ['announcements']
                }
            },
            rateLimiting: {
                maxRequests: 30,
                timeWindow: 60000, // 1 minute
                retryDelay: 5000,   // 5 seconds
                maxRetries: 3
            },
            formatting: {
                embedColor: {
                    modSubmission: 0x9b59b6,   // Purple
                    bugReport: 0xe74c3c,       // Red
                    success: 0x27ae60,         // Green
                    warning: 0xf39c12,         // Orange
                    info: 0x3498db             // Blue
                },
                includeTimestamp: true,
                includeFooter: true,
                maxDescriptionLength: 2048,
                maxFieldLength: 1024
            },
            security: {
                validateUrls: true,
                allowedDomains: ['discord.com', 'discordapp.com'],
                signatureValidation: false,
                logAllRequests: true
            }
        };
    }

    /**
     * Send mod submission notification
     */
    async sendModSubmission(submissionData) {
        try {
            const webhookConfig = this.config.webhooks.modSubmissions;
            
            if (!webhookConfig.enabled || !webhookConfig.url) {
                console.log('Mod submission webhook disabled or URL not configured');
                return { success: false, reason: 'webhook_disabled' };
            }

            const embed = this.createModSubmissionEmbed(submissionData);
            const payload = this.createWebhookPayload(webhookConfig, embed, 'mod');

            const result = await this.sendWebhook(webhookConfig.url, payload);
            
            if (result.success) {
                this.webhookStats.sent++;
                this.webhookStats.lastSent = new Date().toISOString();
                this.logWebhookActivity('mod_submission', 'success', submissionData.submissionId);
            } else {
                this.webhookStats.failed++;
                this.logWebhookActivity('mod_submission', 'failed', submissionData.submissionId, result.error);
            }

            return result;
        } catch (error) {
            console.error('Error sending mod submission webhook:', error);
            this.webhookStats.failed++;
            return { success: false, error: error.message };
        }
    }

    /**
     * Send bug report notification
     */
    async sendBugReport(bugData) {
        try {
            const webhookConfig = this.config.webhooks.bugReports;
            
            if (!webhookConfig.enabled || !webhookConfig.url) {
                console.log('Bug report webhook disabled or URL not configured');
                return { success: false, reason: 'webhook_disabled' };
            }

            const embed = this.createBugReportEmbed(bugData);
            const payload = this.createWebhookPayload(webhookConfig, embed, 'bug');

            const result = await this.sendWebhook(webhookConfig.url, payload);
            
            if (result.success) {
                this.webhookStats.sent++;
                this.webhookStats.lastSent = new Date().toISOString();
                this.logWebhookActivity('bug_report', 'success', bugData.bugId);
            } else {
                this.webhookStats.failed++;
                this.logWebhookActivity('bug_report', 'failed', bugData.bugId, result.error);
            }

            return result;
        } catch (error) {
            console.error('Error sending bug report webhook:', error);
            this.webhookStats.failed++;
            return { success: false, error: error.message };
        }
    }

    /**
     * Create mod submission embed
     */
    createModSubmissionEmbed(submissionData) {
        const config = this.config.formatting;
        
        return {
            title: `🔧 New Mod Submission: ${this.truncateText(submissionData.title, 256)}`,
            description: this.truncateText(submissionData.description, config.maxDescriptionLength),
            color: config.embedColor.modSubmission,
            timestamp: config.includeTimestamp ? new Date().toISOString() : undefined,
            author: {
                name: `${submissionData.author.name || 'Anonymous'}`,
                icon_url: submissionData.author.avatar || 'https://cdn.discordapp.com/embed/avatars/0.png'
            },
            fields: [
                {
                    name: '📦 Mod Details',
                    value: [
                        `**Version:** ${submissionData.version || 'Unknown'}`,
                        `**Category:** ${submissionData.category || 'Uncategorized'}`,
                        `**Submission ID:** \`${submissionData.submissionId}\``
                    ].join('\n'),
                    inline: true
                },
                {
                    name: '👤 Author Info',
                    value: [
                        `**Name:** ${submissionData.author.name || 'Anonymous'}`,
                        `**Contact:** ${this.formatContactInfo(submissionData.author)}`,
                        `**Submitted:** <t:${Math.floor(Date.now() / 1000)}:R>`
                    ].join('\n'),
                    inline: true
                },
                {
                    name: '📋 Submission Status',
                    value: [
                        `**Status:** 🔍 Under Review`,
                        `**Priority:** ${this.determinePriority(submissionData)}`,
                        `**Files:** ${submissionData.files?.length || 0} file(s)`
                    ].join('\n'),
                    inline: false
                }
            ],
            footer: config.includeFooter ? {
                text: 'MorningStar Mod Portal',
                icon_url: 'https://cdn.discordapp.com/icons/server-icon.png'
            } : undefined,
            thumbnail: {
                url: submissionData.thumbnail || 'https://cdn.discordapp.com/attachments/mod-icon.png'
            }
        };
    }

    /**
     * Create bug report embed
     */
    createBugReportEmbed(bugData) {
        const config = this.config.formatting;
        
        return {
            title: `🐛 New Bug Report: ${this.truncateText(bugData.title, 256)}`,
            description: this.truncateText(bugData.description, config.maxDescriptionLength),
            color: config.embedColor.bugReport,
            timestamp: config.includeTimestamp ? new Date().toISOString() : undefined,
            author: {
                name: `${bugData.reporter.name || 'Anonymous Reporter'}`,
                icon_url: bugData.reporter.avatar || 'https://cdn.discordapp.com/embed/avatars/1.png'
            },
            fields: [
                {
                    name: '🔍 Bug Details',
                    value: [
                        `**Severity:** ${this.formatSeverity(bugData.severity)}`,
                        `**Module:** ${bugData.module || 'Unknown'}`,
                        `**Bug ID:** \`${bugData.bugId}\``
                    ].join('\n'),
                    inline: true
                },
                {
                    name: '👤 Reporter Info',
                    value: [
                        `**Name:** ${bugData.reporter.name || 'Anonymous'}`,
                        `**Contact:** ${this.formatContactInfo(bugData.reporter)}`,
                        `**Reported:** <t:${Math.floor(Date.now() / 1000)}:R>`
                    ].join('\n'),
                    inline: true
                },
                {
                    name: '🖥️ Environment',
                    value: [
                        `**Browser:** ${bugData.environment?.browser || 'Unknown'}`,
                        `**OS:** ${bugData.environment?.os || 'Unknown'}`,
                        `**Version:** ${bugData.environment?.version || 'Unknown'}`
                    ].join('\n'),
                    inline: false
                }
            ],
            footer: config.includeFooter ? {
                text: 'MorningStar Bug Tracker',
                icon_url: 'https://cdn.discordapp.com/icons/bug-icon.png'
            } : undefined
        };
    }

    /**
     * Create webhook payload
     */
    createWebhookPayload(webhookConfig, embed, type) {
        const mentions = this.formatMentions(webhookConfig.mentions);
        
        return {
            username: webhookConfig.name || 'MorningStar Bot',
            avatar_url: webhookConfig.avatar,
            content: mentions ? `${mentions}` : undefined,
            embeds: [embed],
            allowed_mentions: {
                parse: ['roles', 'users', 'everyone']
            }
        };
    }

    /**
     * Send webhook to Discord
     */
    async sendWebhook(webhookUrl, payload) {
        return new Promise((resolve) => {
            try {
                // Validate webhook URL
                if (!this.validateWebhookUrl(webhookUrl)) {
                    resolve({ success: false, error: 'Invalid webhook URL' });
                    return;
                }

                // Check rate limiting
                if (!this.checkRateLimit(webhookUrl)) {
                    this.addToRetryQueue(webhookUrl, payload);
                    resolve({ success: false, error: 'Rate limited, queued for retry' });
                    return;
                }

                const url = new URL(webhookUrl);
                const postData = JSON.stringify(payload);

                const options = {
                    hostname: url.hostname,
                    port: url.port || 443,
                    path: url.pathname + url.search,
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Content-Length': Buffer.byteLength(postData),
                        'User-Agent': 'MorningStar-Discord-Webhook/1.0'
                    }
                };

                const req = https.request(options, (res) => {
                    let responseData = '';
                    
                    res.on('data', (chunk) => {
                        responseData += chunk;
                    });
                    
                    res.on('end', () => {
                        if (res.statusCode >= 200 && res.statusCode < 300) {
                            this.updateRateLimit(webhookUrl, res.headers);
                            resolve({ 
                                success: true, 
                                statusCode: res.statusCode,
                                response: responseData
                            });
                        } else {
                            resolve({ 
                                success: false, 
                                error: `HTTP ${res.statusCode}: ${responseData}`,
                                statusCode: res.statusCode
                            });
                        }
                    });
                });

                req.on('error', (error) => {
                    resolve({ success: false, error: error.message });
                });

                req.on('timeout', () => {
                    req.destroy();
                    resolve({ success: false, error: 'Request timeout' });
                });

                req.setTimeout(10000); // 10 second timeout
                req.write(postData);
                req.end();

            } catch (error) {
                resolve({ success: false, error: error.message });
            }
        });
    }

    /**
     * Validate webhook URL
     */
    validateWebhookUrl(url) {
        if (!this.config.security.validateUrls) {
            return true;
        }

        try {
            const urlObj = new URL(url);
            const allowedDomains = this.config.security.allowedDomains;
            
            return allowedDomains.some(domain => 
                urlObj.hostname === domain || urlObj.hostname.endsWith(`.${domain}`)
            );
        } catch {
            return false;
        }
    }

    /**
     * Check rate limiting
     */
    checkRateLimit(webhookUrl) {
        const now = Date.now();
        const rateLimitConfig = this.config.rateLimiting;
        
        if (!this.rateLimits.has(webhookUrl)) {
            this.rateLimits.set(webhookUrl, {
                requests: [],
                lastRequest: now
            });
            return true;
        }

        const rateLimit = this.rateLimits.get(webhookUrl);
        
        // Remove old requests outside the time window
        rateLimit.requests = rateLimit.requests.filter(
            timestamp => now - timestamp < rateLimitConfig.timeWindow
        );

        // Check if we're under the limit
        if (rateLimit.requests.length < rateLimitConfig.maxRequests) {
            rateLimit.requests.push(now);
            rateLimit.lastRequest = now;
            return true;
        }

        return false;
    }

    /**
     * Update rate limit information from response headers
     */
    updateRateLimit(webhookUrl, headers) {
        const remaining = parseInt(headers['x-ratelimit-remaining']) || 0;
        const resetAfter = parseInt(headers['x-ratelimit-reset-after']) || 0;
        
        if (remaining === 0 && resetAfter > 0) {
            // Temporarily block this webhook
            setTimeout(() => {
                if (this.rateLimits.has(webhookUrl)) {
                    this.rateLimits.get(webhookUrl).requests = [];
                }
            }, resetAfter * 1000);
        }
    }

    /**
     * Add to retry queue
     */
    addToRetryQueue(webhookUrl, payload) {
        this.retryQueue.push({
            url: webhookUrl,
            payload: payload,
            attempts: 0,
            nextRetry: Date.now() + this.config.rateLimiting.retryDelay
        });

        this.processRetryQueue();
    }

    /**
     * Process retry queue
     */
    async processRetryQueue() {
        const now = Date.now();
        const maxRetries = this.config.rateLimiting.maxRetries;
        
        for (let i = this.retryQueue.length - 1; i >= 0; i--) {
            const item = this.retryQueue[i];
            
            if (now >= item.nextRetry) {
                if (item.attempts < maxRetries) {
                    item.attempts++;
                    item.nextRetry = now + this.config.rateLimiting.retryDelay * item.attempts;
                    
                    const result = await this.sendWebhook(item.url, item.payload);
                    
                    if (result.success) {
                        this.retryQueue.splice(i, 1);
                        this.webhookStats.retries++;
                    }
                } else {
                    // Max retries exceeded
                    this.retryQueue.splice(i, 1);
                    console.error(`Max retries exceeded for webhook: ${item.url}`);
                }
            }
        }

        // Schedule next retry processing if queue not empty
        if (this.retryQueue.length > 0) {
            setTimeout(() => this.processRetryQueue(), 1000);
        }
    }

    /**
     * Format contact information
     */
    formatContactInfo(author) {
        const contact = [];
        
        if (author.discordId) {
            contact.push(`Discord: ${author.discordId}`);
        }
        
        if (author.email) {
            contact.push(`Email: ${author.email.substring(0, 3)}***@${author.email.split('@')[1]}`);
        }
        
        return contact.length > 0 ? contact.join('\n') : 'Not provided';
    }

    /**
     * Format mentions
     */
    formatMentions(mentions) {
        if (!mentions || mentions.length === 0) {
            return '';
        }
        
        return mentions.map(mention => {
            if (mention.startsWith('@')) {
                return mention;
            }
            return `@${mention}`;
        }).join(' ');
    }

    /**
     * Format severity with emoji
     */
    formatSeverity(severity) {
        const severityMap = {
            'Critical': '🔴 Critical',
            'High': '🟠 High',
            'Medium': '🟡 Medium',
            'Low': '🟢 Low',
            'Info': '🔵 Info'
        };
        
        return severityMap[severity] || `⚪ ${severity || 'Unknown'}`;
    }

    /**
     * Determine submission priority
     */
    determinePriority(submissionData) {
        // Simple priority logic based on submission data
        if (submissionData.category === 'Bug Fix' || submissionData.category === 'Security') {
            return '🔴 High';
        } else if (submissionData.category === 'Performance' || submissionData.category === 'UI Enhancement') {
            return '🟡 Medium';
        } else {
            return '🟢 Normal';
        }
    }

    /**
     * Truncate text to specified length
     */
    truncateText(text, maxLength) {
        if (!text || text.length <= maxLength) {
            return text || '';
        }
        
        return text.substring(0, maxLength - 3) + '...';
    }

    /**
     * Log webhook activity
     */
    logWebhookActivity(type, status, id, error = null) {
        if (!this.config.security.logAllRequests) {
            return;
        }

        const logEntry = {
            timestamp: new Date().toISOString(),
            type: type,
            status: status,
            id: id,
            error: error
        };

        // In production, this would write to a proper log file
        console.log('Webhook Activity:', JSON.stringify(logEntry));
    }

    /**
     * Get webhook statistics
     */
    getStatistics() {
        return {
            ...this.webhookStats,
            queueLength: this.retryQueue.length,
            activeRateLimits: this.rateLimits.size
        };
    }

    /**
     * Test webhook connection
     */
    async testWebhook(type) {
        const testData = this.getTestData(type);
        
        if (type === 'mod') {
            return await this.sendModSubmission(testData);
        } else if (type === 'bug') {
            return await this.sendBugReport(testData);
        }
        
        return { success: false, error: 'Invalid test type' };
    }

    /**
     * Get test data for webhook testing
     */
    getTestData(type) {
        if (type === 'mod') {
            return {
                submissionId: 'TEST-MOD-' + Date.now(),
                title: 'Test Mod Submission',
                description: 'This is a test mod submission to verify webhook functionality.',
                version: '1.0.0',
                category: 'UI Enhancement',
                author: {
                    name: 'Test User',
                    discordId: 'TestUser#1234',
                    email: 'test@example.com'
                },
                files: ['test-mod.zip', 'readme.txt']
            };
        } else if (type === 'bug') {
            return {
                bugId: 'TEST-BUG-' + Date.now(),
                title: 'Test Bug Report',
                description: 'This is a test bug report to verify webhook functionality.',
                severity: 'Medium',
                module: 'Testing',
                reporter: {
                    name: 'Test Reporter',
                    discordId: 'TestReporter#5678',
                    email: 'reporter@example.com'
                },
                environment: {
                    browser: 'Chrome',
                    os: 'Windows 10',
                    version: '1.0.0'
                }
            };
        }
        
        return {};
    }

    /**
     * Send custom notification
     */
    async sendCustomNotification(webhookType, title, description, fields = [], color = null) {
        try {
            const webhookConfig = this.config.webhooks[webhookType];
            
            if (!webhookConfig || !webhookConfig.enabled || !webhookConfig.url) {
                return { success: false, reason: 'webhook_disabled' };
            }

            const embed = {
                title: this.truncateText(title, 256),
                description: this.truncateText(description, this.config.formatting.maxDescriptionLength),
                color: color || this.config.formatting.embedColor.info,
                timestamp: this.config.formatting.includeTimestamp ? new Date().toISOString() : undefined,
                fields: fields.slice(0, 25), // Discord limit
                footer: this.config.formatting.includeFooter ? {
                    text: 'MorningStar Notifications',
                    icon_url: 'https://cdn.discordapp.com/icons/server-icon.png'
                } : undefined
            };

            const payload = this.createWebhookPayload(webhookConfig, embed, 'custom');
            return await this.sendWebhook(webhookConfig.url, payload);
            
        } catch (error) {
            console.error('Error sending custom notification:', error);
            return { success: false, error: error.message };
        }
    }
}

// Export webhook manager and convenience functions
module.exports = {
    DiscordWebhookManager,
    
    // Convenience functions for direct use
    sendModSubmission: async (submissionData) => {
        const webhook = new DiscordWebhookManager();
        return await webhook.sendModSubmission(submissionData);
    },
    
    sendBugReport: async (bugData) => {
        const webhook = new DiscordWebhookManager();
        return await webhook.sendBugReport(bugData);
    },
    
    testWebhook: async (type) => {
        const webhook = new DiscordWebhookManager();
        return await webhook.testWebhook(type);
    },
    
    getStatistics: () => {
        const webhook = new DiscordWebhookManager();
        return webhook.getStatistics();
    }
};