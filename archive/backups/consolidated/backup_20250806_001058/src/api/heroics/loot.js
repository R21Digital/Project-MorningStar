#!/usr/bin/env node
/**
 * Heroics Loot API Endpoint - Phase 1
 * Serves loot data from heroic instances for frontend integration
 */

const express = require('express');
const fs = require('fs');
const path = require('path');
const cors = require('cors');

class HeroicsLootAPI {
    constructor(config = {}) {
        this.config = {
            loot_logs_dir: config.loot_logs_dir || '../data/loot_logs',
            cache_ttl: config.cache_ttl || 300, // 5 minutes
            max_entries_per_request: config.max_entries_per_request || 1000,
            ...config
        };
        
        this.cache = new Map();
        this.app = express();
        this.setupMiddleware();
        this.setupRoutes();
    }
    
    setupMiddleware() {
        this.app.use(cors());
        this.app.use(express.json());
        this.app.use((req, res, next) => {
            res.setHeader('Content-Type', 'application/json');
            next();
        });
    }
    
    setupRoutes() {
        // Main loot endpoint
        this.app.get('/api/heroics/loot', this.getLootData.bind(this));
        
        // Loot by heroic instance
        this.app.get('/api/heroics/loot/:heroic', this.getLootByHeroic.bind(this));
        
        // Loot statistics
        this.app.get('/api/heroics/loot/stats', this.getLootStats.bind(this));
        
        // Recent loot (live feed)
        this.app.get('/api/heroics/loot/recent', this.getRecentLoot.bind(this));
        
        // Loot by player
        this.app.get('/api/heroics/loot/player/:playerName', this.getLootByPlayer.bind(this));
        
        // Health check
        this.app.get('/api/heroics/health', this.healthCheck.bind(this));
    }
    
    async getLootData(req, res) {
        try {
            const {
                heroic,
                rarity,
                type,
                player,
                limit = 100,
                offset = 0,
                sort = 'timestamp',
                order = 'desc'
            } = req.query;
            
            const filters = {
                heroic_instance: heroic,
                rarity: rarity,
                item_type: type,
                player_name: player
            };
            
            const options = {
                limit: Math.min(parseInt(limit), this.config.max_entries_per_request),
                offset: parseInt(offset),
                sort,
                order
            };
            
            const result = await this.fetchLootData(filters, options);
            
            res.json({
                success: true,
                data: result.entries,
                pagination: {
                    total: result.total,
                    limit: options.limit,
                    offset: options.offset,
                    has_more: result.total > (options.offset + options.limit)
                },
                filters: filters,
                timestamp: new Date().toISOString()
            });
            
        } catch (error) {
            console.error('Error in getLootData:', error);
            res.status(500).json({
                success: false,
                error: 'Internal server error',
                message: error.message
            });
        }
    }
    
    async getLootByHeroic(req, res) {
        try {
            const { heroic } = req.params;
            const { limit = 50, rarity, type } = req.query;
            
            const filters = {
                heroic_instance: heroic,
                rarity: rarity,
                item_type: type
            };
            
            const result = await this.fetchLootData(filters, { 
                limit: parseInt(limit),
                sort: 'timestamp',
                order: 'desc'
            });
            
            // Group by boss
            const bosses = {};
            result.entries.forEach(entry => {
                const bossName = entry.boss_name || 'Unknown Boss';
                if (!bosses[bossName]) {
                    bosses[bossName] = {
                        name: bossName,
                        loot_count: 0,
                        items: []
                    };
                }
                bosses[bossName].loot_count++;
                bosses[bossName].items.push({
                    name: entry.item_name,
                    type: entry.item_type,
                    rarity: entry.rarity,
                    quantity: entry.quantity,
                    timestamp: entry.timestamp,
                    player: entry.player_name
                });
            });
            
            res.json({
                success: true,
                heroic_instance: heroic,
                total_drops: result.total,
                bosses: Object.values(bosses),
                timestamp: new Date().toISOString()
            });
            
        } catch (error) {
            console.error('Error in getLootByHeroic:', error);
            res.status(500).json({
                success: false,
                error: 'Internal server error',
                message: error.message
            });
        }
    }
    
    async getLootStats(req, res) {
        try {
            const { heroic, timeframe = '24h' } = req.query;
            
            const hours = this.parseTimeframe(timeframe);
            const cutoffTime = new Date(Date.now() - (hours * 60 * 60 * 1000));
            
            const allEntries = await this.loadAllLootEntries();
            const filteredEntries = allEntries.filter(entry => {
                const entryTime = new Date(entry.timestamp);
                const matchesTime = entryTime >= cutoffTime;
                const matchesHeroic = !heroic || entry.heroic_instance === heroic;
                return matchesTime && matchesHeroic;
            });
            
            const stats = this.calculateStats(filteredEntries);
            
            res.json({
                success: true,
                timeframe: timeframe,
                heroic_filter: heroic || 'all',
                stats: stats,
                timestamp: new Date().toISOString()
            });
            
        } catch (error) {
            console.error('Error in getLootStats:', error);
            res.status(500).json({
                success: false,
                error: 'Internal server error',
                message: error.message
            });
        }
    }
    
    async getRecentLoot(req, res) {
        try {
            const { minutes = 60, heroic } = req.query;
            
            const cutoffTime = new Date(Date.now() - (parseInt(minutes) * 60 * 1000));
            const filters = {
                heroic_instance: heroic,
                min_timestamp: cutoffTime.toISOString()
            };
            
            const result = await this.fetchLootData(filters, {
                limit: 50,
                sort: 'timestamp',
                order: 'desc'
            });
            
            res.json({
                success: true,
                recent_minutes: parseInt(minutes),
                heroic_filter: heroic || 'all',
                entries: result.entries,
                count: result.entries.length,
                timestamp: new Date().toISOString()
            });
            
        } catch (error) {
            console.error('Error in getRecentLoot:', error);
            res.status(500).json({
                success: false,
                error: 'Internal server error',
                message: error.message
            });
        }
    }
    
    async getLootByPlayer(req, res) {
        try {
            const { playerName } = req.params;
            const { limit = 50, heroic } = req.query;
            
            const filters = {
                player_name: playerName,
                heroic_instance: heroic
            };
            
            const result = await this.fetchLootData(filters, {
                limit: parseInt(limit),
                sort: 'timestamp',
                order: 'desc'
            });
            
            // Calculate player stats
            const playerStats = {
                total_drops: result.total,
                heroics_completed: new Set(result.entries.map(e => e.heroic_instance)).size,
                rarity_breakdown: {},
                favorite_heroic: this.getMostFrequent(result.entries.map(e => e.heroic_instance)),
                recent_activity: result.entries.slice(0, 10)
            };
            
            result.entries.forEach(entry => {
                const rarity = entry.rarity || 'common';
                playerStats.rarity_breakdown[rarity] = (playerStats.rarity_breakdown[rarity] || 0) + 1;
            });
            
            res.json({
                success: true,
                player_name: playerName,
                stats: playerStats,
                recent_loot: result.entries,
                timestamp: new Date().toISOString()
            });
            
        } catch (error) {
            console.error('Error in getLootByPlayer:', error);
            res.status(500).json({
                success: false,
                error: 'Internal server error',
                message: error.message
            });
        }
    }
    
    async healthCheck(req, res) {
        try {
            const lootLogsDir = path.resolve(__dirname, this.config.loot_logs_dir);
            const logsExist = fs.existsSync(lootLogsDir);
            
            let fileCount = 0;
            let lastUpdate = null;
            
            if (logsExist) {
                const files = fs.readdirSync(lootLogsDir).filter(f => f.endsWith('.json'));
                fileCount = files.length;
                
                if (files.length > 0) {
                    const latestFile = files[files.length - 1];
                    const stats = fs.statSync(path.join(lootLogsDir, latestFile));
                    lastUpdate = stats.mtime.toISOString();
                }
            }
            
            res.json({
                success: true,
                status: 'healthy',
                loot_logs_directory: lootLogsDir,
                logs_exist: logsExist,
                log_file_count: fileCount,
                last_update: lastUpdate,
                cache_size: this.cache.size,
                timestamp: new Date().toISOString()
            });
            
        } catch (error) {
            console.error('Error in healthCheck:', error);
            res.status(500).json({
                success: false,
                status: 'unhealthy',
                error: error.message,
                timestamp: new Date().toISOString()
            });
        }
    }
    
    async fetchLootData(filters = {}, options = {}) {
        const cacheKey = JSON.stringify({ filters, options });
        
        // Check cache
        if (this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < this.config.cache_ttl * 1000) {
                return cached.data;
            }
        }
        
        // Load data from files
        const allEntries = await this.loadAllLootEntries();
        
        // Apply filters
        let filteredEntries = allEntries.filter(entry => {
            for (const [key, value] of Object.entries(filters)) {
                if (value && entry[key] !== value) {
                    return false;
                }
                if (key === 'min_timestamp' && value) {
                    if (new Date(entry.timestamp) < new Date(value)) {
                        return false;
                    }
                }
            }
            return true;
        });
        
        // Apply sorting
        if (options.sort) {
            const sortField = options.sort;
            const sortOrder = options.order === 'asc' ? 1 : -1;
            
            filteredEntries.sort((a, b) => {
                let aVal = a[sortField];
                let bVal = b[sortField];
                
                if (sortField === 'timestamp') {
                    aVal = new Date(aVal);
                    bVal = new Date(bVal);
                }
                
                if (aVal < bVal) return -1 * sortOrder;
                if (aVal > bVal) return 1 * sortOrder;
                return 0;
            });
        }
        
        // Apply pagination
        const total = filteredEntries.length;
        const offset = options.offset || 0;
        const limit = options.limit || 100;
        const paginatedEntries = filteredEntries.slice(offset, offset + limit);
        
        const result = {
            entries: paginatedEntries,
            total: total
        };
        
        // Cache the result
        this.cache.set(cacheKey, {
            data: result,
            timestamp: Date.now()
        });
        
        return result;
    }
    
    async loadAllLootEntries() {
        const lootLogsDir = path.resolve(__dirname, this.config.loot_logs_dir);
        const allEntries = [];
        
        if (!fs.existsSync(lootLogsDir)) {
            console.warn(`Loot logs directory not found: ${lootLogsDir}`);
            return allEntries;
        }
        
        const files = fs.readdirSync(lootLogsDir)
            .filter(file => file.startsWith('heroic_loot_logs_') && file.endsWith('.json'))
            .sort();
        
        for (const file of files) {
            try {
                const filePath = path.join(lootLogsDir, file);
                const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
                
                if (data.loot_entries && Array.isArray(data.loot_entries)) {
                    allEntries.push(...data.loot_entries);
                }
            } catch (error) {
                console.error(`Error loading loot file ${file}:`, error);
            }
        }
        
        return allEntries;
    }
    
    calculateStats(entries) {
        if (!entries.length) {
            return {
                total_entries: 0,
                unique_items: 0,
                heroic_breakdown: {},
                rarity_distribution: {},
                type_distribution: {},
                most_common_items: []
            };
        }
        
        const stats = {
            total_entries: entries.length,
            unique_items: new Set(entries.map(e => e.item_name)).size,
            heroic_breakdown: {},
            rarity_distribution: {},
            type_distribution: {},
            player_count: new Set(entries.map(e => e.player_name)).size,
            date_range: {
                start: Math.min(...entries.map(e => new Date(e.timestamp))),
                end: Math.max(...entries.map(e => new Date(e.timestamp)))
            }
        };
        
        // Count breakdowns
        entries.forEach(entry => {
            // Heroic breakdown
            const heroic = entry.heroic_instance;
            stats.heroic_breakdown[heroic] = (stats.heroic_breakdown[heroic] || 0) + 1;
            
            // Rarity distribution
            const rarity = entry.rarity || 'common';
            stats.rarity_distribution[rarity] = (stats.rarity_distribution[rarity] || 0) + 1;
            
            // Type distribution
            const type = entry.item_type || 'misc';
            stats.type_distribution[type] = (stats.type_distribution[type] || 0) + 1;
        });
        
        // Most common items
        const itemCounts = {};
        entries.forEach(entry => {
            const itemName = entry.item_name;
            itemCounts[itemName] = (itemCounts[itemName] || 0) + 1;
        });
        
        stats.most_common_items = Object.entries(itemCounts)
            .sort(([,a], [,b]) => b - a)
            .slice(0, 10)
            .map(([name, count]) => ({ name, count }));
        
        return stats;
    }
    
    parseTimeframe(timeframe) {
        const match = timeframe.match(/^(\d+)([hdwm])$/);
        if (!match) return 24; // Default to 24 hours
        
        const [, num, unit] = match;
        const multipliers = { h: 1, d: 24, w: 168, m: 720 };
        return parseInt(num) * (multipliers[unit] || 1);
    }
    
    getMostFrequent(array) {
        const counts = {};
        array.forEach(item => {
            counts[item] = (counts[item] || 0) + 1;
        });
        
        return Object.entries(counts)
            .sort(([,a], [,b]) => b - a)[0]?.[0] || null;
    }
    
    start(port = 3000) {
        this.app.listen(port, () => {
            console.log(`Heroics Loot API listening on port ${port}`);
            console.log(`Available endpoints:`);
            console.log(`  GET /api/heroics/loot - Main loot data`);
            console.log(`  GET /api/heroics/loot/:heroic - Loot by heroic instance`);
            console.log(`  GET /api/heroics/loot/stats - Loot statistics`);
            console.log(`  GET /api/heroics/loot/recent - Recent loot feed`);
            console.log(`  GET /api/heroics/loot/player/:playerName - Player loot data`);
            console.log(`  GET /api/heroics/health - Health check`);
        });
    }
}

// CLI usage
if (require.main === module) {
    const port = process.env.PORT || 3000;
    const api = new HeroicsLootAPI();
    api.start(port);
}

module.exports = HeroicsLootAPI;