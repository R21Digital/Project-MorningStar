/**
 * Heroic Boss Kill Logging API Endpoint
 * Handles logging of boss kills with validation, rate limiting, and analytics tracking
 */

const fs = require('fs').promises;
const path = require('path');
const crypto = require('crypto');

// Configuration
const BOSS_KILLS_FILE = path.join(__dirname, '../../src/data/heroics/boss_kills.json');
const RATE_LIMIT_WINDOW = 60000; // 1 minute
const MAX_REQUESTS_PER_WINDOW = 10;
const MAX_TEAM_SIZE = 8;
const MIN_KILL_TIME = 30; // seconds
const MAX_KILL_TIME = 3600; // 1 hour

// In-memory rate limiting (in production, use Redis or similar)
const rateLimitStore = new Map();

// Valid boss IDs
const VALID_BOSS_IDS = [
  'exar_kun',
  'ig88', 
  'tusken_king',
  'lord_nyax',
  'axkva_min'
];

// Valid character classes
const VALID_CLASSES = [
  'Jedi',
  'Bounty Hunter',
  'Commando',
  'Rifleman',
  'Marksman',
  'Smuggler',
  'Officer',
  'Medic',
  'Entertainer',
  'Artisan'
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
        return await handleKillLog(req, res);
      case 'GET':
        return await handleGetStats(req, res);
      default:
        return res.status(405).json({ 
          error: 'Method not allowed',
          allowedMethods: ['GET', 'POST']
        });
    }
  } catch (error) {
    console.error('API Error:', error);
    return res.status(500).json({
      error: 'Internal server error',
      message: process.env.NODE_ENV === 'development' ? error.message : 'Something went wrong'
    });
  }
}

/**
 * Handle boss kill logging
 */
async function handleKillLog(req, res) {
  // Rate limiting
  const clientId = getClientId(req);
  if (!checkRateLimit(clientId)) {
    return res.status(429).json({
      error: 'Rate limit exceeded',
      message: 'Too many requests. Please wait before submitting another kill.'
    });
  }

  // Validate request body
  const validation = validateKillData(req.body);
  if (!validation.valid) {
    return res.status(400).json({
      error: 'Validation failed',
      details: validation.errors
    });
  }

  const killData = validation.data;

  try {
    // Load current boss data
    const bossData = await loadBossData();
    
    // Process the kill
    const result = await processKillLog(killData, bossData);
    
    // Save updated data
    await saveBossData(bossData);
    
    // Return success response
    return res.status(201).json({
      success: true,
      message: 'Kill logged successfully',
      killId: result.killId,
      stats: {
        totalKills: result.newTotalKills,
        isFirstKill: result.isFirstKill,
        isFastestKill: result.isFastestKill,
        rank: result.timeRank
      }
    });

  } catch (error) {
    console.error('Kill logging error:', error);
    return res.status(500).json({
      error: 'Failed to log kill',
      message: 'Could not save kill data'
    });
  }
}

/**
 * Handle stats retrieval
 */
async function handleGetStats(req, res) {
  const { boss, season, player, limit } = req.query;

  try {
    const bossData = await loadBossData();
    
    if (boss) {
      // Get specific boss stats
      const bossStats = getBossStats(bossData, boss, season);
      if (!bossStats) {
        return res.status(404).json({ error: 'Boss not found' });
      }
      return res.json(bossStats);
    }

    if (player) {
      // Get player stats
      const playerStats = getPlayerStats(bossData, player, season);
      return res.json(playerStats);
    }

    // Get general stats
    const stats = getGeneralStats(bossData, season, parseInt(limit) || 10);
    return res.json(stats);

  } catch (error) {
    console.error('Stats retrieval error:', error);
    return res.status(500).json({
      error: 'Failed to retrieve stats'
    });
  }
}

/**
 * Validate kill data
 */
function validateKillData(data) {
  const errors = [];

  // Required fields
  if (!data.bossId || !VALID_BOSS_IDS.includes(data.bossId)) {
    errors.push('Invalid or missing boss ID');
  }

  if (!data.killTime || typeof data.killTime !== 'number') {
    errors.push('Invalid or missing kill time');
  } else if (data.killTime < MIN_KILL_TIME || data.killTime > MAX_KILL_TIME) {
    errors.push(`Kill time must be between ${MIN_KILL_TIME} and ${MAX_KILL_TIME} seconds`);
  }

  if (!data.team || !Array.isArray(data.team) || data.team.length === 0) {
    errors.push('Team data is required');
  } else if (data.team.length > MAX_TEAM_SIZE) {
    errors.push(`Team size cannot exceed ${MAX_TEAM_SIZE} players`);
  }

  // Validate team members
  if (data.team) {
    data.team.forEach((member, index) => {
      if (!member.alias || typeof member.alias !== 'string' || member.alias.length < 2) {
        errors.push(`Team member ${index + 1}: Invalid alias`);
      }

      if (!member.class || !VALID_CLASSES.includes(member.class)) {
        errors.push(`Team member ${index + 1}: Invalid character class`);
      }

      if (!member.level || typeof member.level !== 'number' || member.level < 1 || member.level > 90) {
        errors.push(`Team member ${index + 1}: Invalid level (1-90)`);
      }

      // Generate discord hash if not provided
      if (!member.discordHash) {
        member.discordHash = generateDiscordHash(member.alias);
      }
    });
  }

  // Optional fields validation
  if (data.serverPop && (typeof data.serverPop !== 'number' || data.serverPop < 0)) {
    errors.push('Invalid server population');
  }

  if (data.screenshot && typeof data.screenshot !== 'string') {
    errors.push('Invalid screenshot URL');
  }

  return {
    valid: errors.length === 0,
    errors,
    data: errors.length === 0 ? {
      ...data,
      timestamp: new Date().toISOString(),
      killId: generateKillId(),
      serverPop: data.serverPop || null,
      screenshot: data.screenshot || null
    } : null
  };
}

/**
 * Process kill log and update boss data
 */
async function processKillLog(killData, bossData) {
  const { bossId, killTime, team, timestamp, killId } = killData;
  
  // Get or initialize boss stats
  if (!bossData.bosses[bossId]) {
    return { error: 'Boss not found in database' };
  }

  const boss = bossData.bosses[bossId];
  const stats = boss.stats;

  // Check if this is the first kill this season
  const currentSeason = bossData.metadata.currentSeason;
  const isFirstKill = !stats.firstKillThisSeason;

  // Check if this is the fastest kill
  const isFastestKill = !stats.fastestKill || killTime < stats.fastestKill;

  // Update boss statistics
  stats.totalKills = (stats.totalKills || 0) + 1;
  stats.averageTeamSize = calculateNewAverage(
    stats.averageTeamSize || 0,
    stats.totalKills - 1,
    team.length
  );

  if (isFastestKill) {
    stats.fastestKill = killTime;
  }

  stats.averageKillTime = calculateNewAverage(
    stats.averageKillTime || 0,
    stats.totalKills - 1,
    killTime
  );

  // Update unique killers count
  const existingKillers = new Set();
  stats.topKillers?.forEach(killer => existingKillers.add(killer.alias));
  stats.recentKills?.forEach(kill => {
    kill.team?.forEach(member => existingKillers.add(member.alias));
  });
  
  team.forEach(member => existingKillers.add(member.alias));
  stats.uniqueKillers = existingKillers.size;

  // Set first kill if this is the first
  if (isFirstKill) {
    stats.firstKillThisSeason = {
      timestamp,
      team,
      killTime,
      serverPop: killData.serverPop,
      screenshot: killData.screenshot
    };
  }

  // Add to recent kills (keep last 10)
  if (!stats.recentKills) stats.recentKills = [];
  stats.recentKills.unshift({
    timestamp,
    team,
    killTime,
    serverPop: killData.serverPop,
    killId
  });
  stats.recentKills = stats.recentKills.slice(0, 10);

  // Update top killers
  updateTopKillers(stats, team, killTime);

  // Update global metadata
  bossData.metadata.totalKills = (bossData.metadata.totalKills || 0) + 1;
  bossData.metadata.lastUpdated = timestamp;
  bossData.metadata.averageTeamSize = calculateNewAverage(
    bossData.metadata.averageTeamSize || 0,
    bossData.metadata.totalKills - 1,
    team.length
  );

  // Update leaderboards
  updateLeaderboards(bossData, team, killTime, bossId);

  // Calculate time rank
  const allKillTimes = stats.recentKills?.map(k => k.killTime) || [];
  allKillTimes.push(killTime);
  allKillTimes.sort((a, b) => a - b);
  const timeRank = allKillTimes.indexOf(killTime) + 1;

  return {
    killId,
    newTotalKills: stats.totalKills,
    isFirstKill,
    isFastestKill,
    timeRank
  };
}

/**
 * Update top killers list
 */
function updateTopKillers(stats, team, killTime) {
  if (!stats.topKillers) stats.topKillers = [];

  team.forEach(member => {
    let killer = stats.topKillers.find(k => k.alias === member.alias);
    
    if (killer) {
      killer.kills += 1;
      if (!killer.fastestKill || killTime < killer.fastestKill) {
        killer.fastestKill = killTime;
      }
      killer.averageKill = calculateNewAverage(killer.averageKill, killer.kills - 1, killTime);
    } else {
      stats.topKillers.push({
        alias: member.alias,
        kills: 1,
        fastestKill: killTime,
        averageKill: killTime
      });
    }
  });

  // Sort and keep top 10
  stats.topKillers.sort((a, b) => b.kills - a.kills);
  stats.topKillers = stats.topKillers.slice(0, 10);
}

/**
 * Update global leaderboards
 */
function updateLeaderboards(bossData, team, killTime, bossId) {
  if (!bossData.leaderboards) {
    bossData.leaderboards = { mostKills: [], fastestKillers: [], teamPlayers: [] };
  }

  team.forEach(member => {
    // Update most kills leaderboard
    updatePlayerInLeaderboard(bossData.leaderboards.mostKills, member.alias, 'totalKills', 1, {
      favoriteBoss: bossId,
      averageKillTime: killTime
    });

    // Update fastest killers leaderboard
    updatePlayerInLeaderboard(bossData.leaderboards.fastestKillers, member.alias, 'fastestKill', killTime, {
      boss: bossId,
      averageKillTime: killTime
    }, true); // Only update if faster

    // Update team players leaderboard
    updatePlayerInLeaderboard(bossData.leaderboards.teamPlayers, member.alias, 'teamsJoined', 1, {
      averageTeamSize: team.length,
      favoriteRole: member.class
    });
  });
}

/**
 * Update player in leaderboard
 */
function updatePlayerInLeaderboard(leaderboard, alias, stat, value, extraData, onlyIfBetter = false) {
  let player = leaderboard.find(p => p.alias === alias);
  
  if (player) {
    if (onlyIfBetter) {
      if (!player[stat] || value < player[stat]) {
        player[stat] = value;
        Object.assign(player, extraData);
      }
    } else {
      player[stat] = (player[stat] || 0) + value;
      if (extraData.averageTeamSize) {
        player.averageTeamSize = calculateNewAverage(
          player.averageTeamSize || 0,
          player.teamsJoined - 1,
          extraData.averageTeamSize
        );
      }
      Object.assign(player, extraData);
    }
  } else {
    leaderboard.push({
      alias,
      [stat]: value,
      ...extraData
    });
  }

  // Sort and limit
  if (stat === 'fastestKill') {
    leaderboard.sort((a, b) => a[stat] - b[stat]);
  } else {
    leaderboard.sort((a, b) => b[stat] - a[stat]);
  }
  
  if (leaderboard.length > 50) {
    leaderboard.splice(50);
  }
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

function generateKillId() {
  return crypto.randomBytes(8).toString('hex');
}

function generateDiscordHash(alias) {
  return crypto.createHash('md5').update(alias + Date.now()).digest('hex').substring(0, 8);
}

function calculateNewAverage(currentAvg, count, newValue) {
  return ((currentAvg * count) + newValue) / (count + 1);
}

async function loadBossData() {
  try {
    const data = await fs.readFile(BOSS_KILLS_FILE, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.error('Failed to load boss data:', error);
    throw new Error('Could not load boss data');
  }
}

async function saveBossData(data) {
  try {
    await fs.writeFile(BOSS_KILLS_FILE, JSON.stringify(data, null, 2), 'utf8');
  } catch (error) {
    console.error('Failed to save boss data:', error);
    throw new Error('Could not save boss data');
  }
}

/**
 * Get specific boss statistics
 */
function getBossStats(bossData, bossId, season) {
  const boss = bossData.bosses[bossId];
  if (!boss) return null;

  // If season specified, filter data for that season
  if (season && season !== 'all') {
    // This would filter stats by season - implementation depends on data structure
    return {
      ...boss,
      stats: filterStatsBySeason(boss.stats, season)
    };
  }

  return boss;
}

/**
 * Get player statistics across all bosses
 */
function getPlayerStats(bossData, playerAlias, season) {
  const playerStats = {
    alias: playerAlias,
    totalKills: 0,
    bosses: {},
    fastestKill: null,
    averageKillTime: 0,
    favoriteTeamSize: 0,
    firstKills: 0,
    recentActivity: []
  };

  Object.entries(bossData.bosses).forEach(([bossId, boss]) => {
    const bossPlayerStats = getPlayerBossStats(boss, playerAlias);
    if (bossPlayerStats.kills > 0) {
      playerStats.totalKills += bossPlayerStats.kills;
      playerStats.bosses[bossId] = bossPlayerStats;
      
      if (!playerStats.fastestKill || bossPlayerStats.fastestKill < playerStats.fastestKill) {
        playerStats.fastestKill = bossPlayerStats.fastestKill;
      }
    }
  });

  return playerStats;
}

/**
 * Get player statistics for a specific boss
 */
function getPlayerBossStats(boss, playerAlias) {
  const stats = { kills: 0, fastestKill: null, averageKillTime: 0, totalTime: 0 };
  
  // Check top killers
  const topKiller = boss.stats?.topKillers?.find(k => k.alias === playerAlias);
  if (topKiller) {
    stats.kills = topKiller.kills;
    stats.fastestKill = topKiller.fastestKill;
    stats.averageKillTime = topKiller.averageKill;
  }

  // Check recent kills for additional data
  boss.stats?.recentKills?.forEach(kill => {
    const participant = kill.team?.find(member => member.alias === playerAlias);
    if (participant) {
      if (!topKiller) {
        // Player participated but not in top killers (recent participant)
        stats.kills += 1;
        stats.totalTime += kill.killTime;
        
        if (!stats.fastestKill || kill.killTime < stats.fastestKill) {
          stats.fastestKill = kill.killTime;
        }
      }
    }
  });

  if (stats.kills > 0 && !stats.averageKillTime) {
    stats.averageKillTime = stats.totalTime / stats.kills;
  }

  return stats;
}

/**
 * Get general statistics
 */
function getGeneralStats(bossData, season, limit) {
  return {
    metadata: bossData.metadata,
    leaderboards: {
      mostKills: bossData.leaderboards?.mostKills?.slice(0, limit) || [],
      fastestKillers: bossData.leaderboards?.fastestKillers?.slice(0, limit) || [],
      teamPlayers: bossData.leaderboards?.teamPlayers?.slice(0, limit) || []
    },
    analytics: bossData.analytics,
    totalBosses: Object.keys(bossData.bosses).length
  };
}

/**
 * Filter statistics by season (placeholder)
 */
function filterStatsBySeason(stats, season) {
  // This would implement season-specific filtering
  // For now, return all stats
  return stats;
}