<script>
  /**
   * Interactive Boss Statistics Card Component
   * Displays detailed boss statistics with real-time updates and interactive features
   */
  
  import { onMount, createEventDispatcher } from 'svelte';
  import { writable } from 'svelte/store';
  
  // Props
  export let boss = {};
  export let showDetails = false;
  export let enableRealTime = true;
  export let showFirstKill = true;
  export let showRecentKills = true;
  export let maxRecentKills = 3;
  export let refreshInterval = 30000; // 30 seconds
  
  // Event dispatcher
  const dispatch = createEventDispatcher();
  
  // Reactive variables
  let isExpanded = false;
  let isLoading = false;
  let lastUpdated = new Date();
  let refreshTimer;
  
  // Stores for reactive data
  const bossStats = writable(boss.stats || {});
  const recentKills = writable(boss.stats?.recentKills || []);
  const topKillers = writable(boss.stats?.topKillers || []);
  
  // Computed values
  $: difficultyClass = boss.difficulty?.toLowerCase() || 'medium';
  $: difficultyColor = getDifficultyColor(boss.difficulty);
  $: killsToday = getKillsToday($recentKills);
  $: averageTeamSize = $bossStats.averageTeamSize || 0;
  $: successRate = calculateSuccessRate($bossStats);
  $: popularityRank = getPopularityRank(boss.id);
  
  onMount(() => {
    if (enableRealTime) {
      startRealTimeUpdates();
    }
    
    return () => {
      if (refreshTimer) {
        clearInterval(refreshTimer);
      }
    };
  });
  
  // Functions
  function toggleExpanded() {
    isExpanded = !isExpanded;
    dispatch('toggle', { bossId: boss.id, expanded: isExpanded });
  }
  
  function startRealTimeUpdates() {
    refreshTimer = setInterval(async () => {
      await refreshBossData();
    }, refreshInterval);
  }
  
  async function refreshBossData() {
    if (isLoading) return;
    
    isLoading = true;
    try {
      // In a real implementation, this would fetch from an API
      const response = await fetch(`/api/heroics/boss/${boss.id}/stats`);
      if (response.ok) {
        const data = await response.json();
        updateBossData(data);
        lastUpdated = new Date();
        dispatch('dataUpdated', { bossId: boss.id, data });
      }
    } catch (error) {
      console.error('Failed to refresh boss data:', error);
      dispatch('error', { bossId: boss.id, error });
    } finally {
      isLoading = false;
    }
  }
  
  function updateBossData(newData) {
    bossStats.set(newData.stats || {});
    recentKills.set(newData.stats?.recentKills || []);
    topKillers.set(newData.stats?.topKillers || []);
  }
  
  function getDifficultyColor(difficulty) {
    const colors = {
      'legendary': '#ff6b35',
      'hard': '#f39c12',
      'medium': '#27ae60',
      'easy': '#3498db'
    };
    return colors[difficulty?.toLowerCase()] || colors.medium;
  }
  
  function getKillsToday(kills) {
    const today = new Date().toDateString();
    return kills.filter(kill => 
      new Date(kill.timestamp).toDateString() === today
    ).length;
  }
  
  function calculateSuccessRate(stats) {
    // Estimate success rate based on total kills vs attempts
    const totalKills = stats.totalKills || 0;
    const estimatedAttempts = Math.floor(totalKills * 1.3); // Rough estimate
    return totalKills > 0 ? Math.round((totalKills / estimatedAttempts) * 100) : 0;
  }
  
  function getPopularityRank(bossId) {
    // This would normally come from analytics data
    const ranks = {
      'tusken_king': 1,
      'ig88': 2,
      'exar_kun': 3,
      'axkva_min': 4,
      'lord_nyax': 5
    };
    return ranks[bossId] || 0;
  }
  
  function formatTime(seconds) {
    if (!seconds) return '0:00';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  }
  
  function formatNumber(num) {
    return new Intl.NumberFormat().format(num || 0);
  }
  
  function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
  
  function getTimeAgo(dateString) {
    const diff = Date.now() - new Date(dateString).getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    if (minutes > 0) return `${minutes}m ago`;
    return 'Just now';
  }
  
  function handleKillClick(kill) {
    dispatch('killSelected', { boss: boss.id, kill });
  }
  
  function handlePlayerClick(player) {
    dispatch('playerSelected', { player: player.alias });
  }
</script>

<div class="boss-stats-card {difficultyClass}" class:expanded={isExpanded}>
  <!-- Card Header -->
  <div class="card-header" on:click={toggleExpanded}>
    <div class="boss-info">
      <div class="boss-name">{boss.displayName || boss.name}</div>
      <div class="boss-location">{boss.location}</div>
      <div class="boss-type">{boss.heroicType} • Level {boss.minLevel}+</div>
    </div>
    
    <div class="header-stats">
      <div class="difficulty-badge" style="background-color: {difficultyColor}">
        {boss.difficulty}
      </div>
      <div class="popularity-rank" title="Popularity Rank">
        #{popularityRank}
      </div>
    </div>
    
    <div class="expand-icon" class:rotated={isExpanded}>
      <svg width="20" height="20" viewBox="0 0 20 20">
        <path d="M5 7l5 5 5-5" stroke="currentColor" stroke-width="2" fill="none"/>
      </svg>
    </div>
  </div>
  
  <!-- Quick Stats -->
  <div class="quick-stats">
    <div class="stat-item">
      <div class="stat-value">{formatNumber($bossStats.totalKills)}</div>
      <div class="stat-label">Total Kills</div>
    </div>
    <div class="stat-item">
      <div class="stat-value">{$bossStats.uniqueKillers || 0}</div>
      <div class="stat-label">Hunters</div>
    </div>
    <div class="stat-item">
      <div class="stat-value">{formatTime($bossStats.fastestKill)}</div>
      <div class="stat-label">Best Time</div>
    </div>
    <div class="stat-item">
      <div class="stat-value">{killsToday}</div>
      <div class="stat-label">Today</div>
    </div>
  </div>
  
  <!-- Expanded Content -->
  {#if isExpanded}
    <div class="expanded-content">
      <!-- Detailed Statistics -->
      <div class="detailed-stats">
        <div class="stats-grid">
          <div class="detailed-stat">
            <div class="stat-icon">⚡</div>
            <div class="stat-info">
              <div class="stat-title">Average Kill Time</div>
              <div class="stat-number">{formatTime($bossStats.averageKillTime)}</div>
            </div>
          </div>
          
          <div class="detailed-stat">
            <div class="stat-icon">👥</div>
            <div class="stat-info">
              <div class="stat-title">Avg Team Size</div>
              <div class="stat-number">{averageTeamSize.toFixed(1)}</div>
            </div>
          </div>
          
          <div class="detailed-stat">
            <div class="stat-icon">📈</div>
            <div class="stat-info">
              <div class="stat-title">Success Rate</div>
              <div class="stat-number">{successRate}%</div>
            </div>
          </div>
          
          <div class="detailed-stat">
            <div class="stat-icon">🎯</div>
            <div class="stat-info">
              <div class="stat-title">Recommended Team</div>
              <div class="stat-number">{boss.recommendedTeamSize}</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- First Kill This Season -->
      {#if showFirstKill && $bossStats.firstKillThisSeason}
        <div class="first-kill-section">
          <h4>🥇 First Kill This Season</h4>
          <div class="first-kill-info">
            <div class="first-kill-team">
              {#each $bossStats.firstKillThisSeason.team || [] as member}
                <span class="team-member" on:click={() => handlePlayerClick(member)}>
                  {member.alias}
                  <span class="member-class">({member.class})</span>
                </span>
              {/each}
            </div>
            <div class="first-kill-details">
              <span class="kill-time">Time: {formatTime($bossStats.firstKillThisSeason.killTime)}</span>
              <span class="kill-date">{formatDate($bossStats.firstKillThisSeason.timestamp)}</span>
            </div>
          </div>
        </div>
      {/if}
      
      <!-- Recent Kills -->
      {#if showRecentKills && $recentKills.length > 0}
        <div class="recent-kills-section">
          <h4>🕒 Recent Kills</h4>
          <div class="recent-kills-list">
            {#each $recentKills.slice(0, maxRecentKills) as kill}
              <div class="recent-kill" on:click={() => handleKillClick(kill)}>
                <div class="kill-header">
                  <span class="kill-time-badge">{formatTime(kill.killTime)}</span>
                  <span class="time-ago">{getTimeAgo(kill.timestamp)}</span>
                </div>
                <div class="kill-team">
                  {#each kill.team || [] as member, i}
                    <span class="team-member-mini">
                      {member.alias}{i < kill.team.length - 1 ? ', ' : ''}
                    </span>
                  {/each}
                </div>
                <div class="kill-meta">
                  Server Pop: {kill.serverPop || 'Unknown'}
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/if}
      
      <!-- Top Killers -->
      {#if $topKillers.length > 0}
        <div class="top-killers-section">
          <h4>👑 Top Killers</h4>
          <div class="top-killers-list">
            {#each $topKillers.slice(0, 5) as killer, index}
              <div class="top-killer" on:click={() => handlePlayerClick(killer)}>
                <div class="killer-rank">#{index + 1}</div>
                <div class="killer-info">
                  <div class="killer-name">{killer.alias}</div>
                  <div class="killer-stats">
                    {killer.kills} kills • Best: {formatTime(killer.fastestKill)}
                  </div>
                </div>
              </div>
            {/each}
          </div>
        </div>
      {/if}
      
      <!-- Boss Description -->
      {#if boss.description}
        <div class="description-section">
          <h4>📖 About {boss.displayName}</h4>
          <p class="boss-description">{boss.description}</p>
          {#if boss.rewards && boss.rewards.length > 0}
            <div class="rewards">
              <strong>Rewards:</strong>
              {#each boss.rewards as reward, i}
                <span class="reward-item">{reward}{i < boss.rewards.length - 1 ? ', ' : ''}</span>
              {/each}
            </div>
          {/if}
        </div>
      {/if}
    </div>
  {/if}
  
  <!-- Loading Indicator -->
  {#if isLoading}
    <div class="loading-indicator">
      <div class="spinner"></div>
      <span>Updating...</span>
    </div>
  {/if}
  
  <!-- Last Updated -->
  {#if enableRealTime}
    <div class="last-updated">
      Last updated: {formatDate(lastUpdated)}
    </div>
  {/if}
</div>

<style>
  .boss-stats-card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    border-top: 4px solid var(--difficulty-color, #27ae60);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
  }
  
  .boss-stats-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
  }
  
  .boss-stats-card.legendary {
    border-top-color: #ff6b35;
  }
  
  .boss-stats-card.hard {
    border-top-color: #f39c12;
  }
  
  .boss-stats-card.medium {
    border-top-color: #27ae60;
  }
  
  .boss-stats-card.easy {
    border-top-color: #3498db;
  }
  
  .card-header {
    padding: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    cursor: pointer;
    border-bottom: 1px solid #f0f0f0;
  }
  
  .boss-info {
    flex: 1;
  }
  
  .boss-name {
    font-size: 1.4em;
    font-weight: 700;
    color: #333;
    margin-bottom: 4px;
  }
  
  .boss-location {
    color: #666;
    font-size: 0.9em;
    margin-bottom: 2px;
  }
  
  .boss-type {
    color: #888;
    font-size: 0.8em;
  }
  
  .header-stats {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
  }
  
  .difficulty-badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8em;
    font-weight: 600;
    color: white;
    text-transform: uppercase;
  }
  
  .popularity-rank {
    background: #f8f9fa;
    padding: 4px 8px;
    border-radius: 10px;
    font-size: 0.8em;
    font-weight: 600;
    color: #666;
  }
  
  .expand-icon {
    transition: transform 0.3s ease;
    color: #666;
  }
  
  .expand-icon.rotated {
    transform: rotate(180deg);
  }
  
  .quick-stats {
    padding: 15px 20px;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 15px;
    background: #f8f9fa;
  }
  
  .stat-item {
    text-align: center;
  }
  
  .stat-value {
    font-size: 1.3em;
    font-weight: bold;
    color: #007bff;
    margin-bottom: 4px;
  }
  
  .stat-label {
    font-size: 0.8em;
    color: #666;
    text-transform: uppercase;
    font-weight: 500;
  }
  
  .expanded-content {
    padding: 20px;
    animation: expandIn 0.3s ease;
  }
  
  @keyframes expandIn {
    from {
      opacity: 0;
      max-height: 0;
    }
    to {
      opacity: 1;
      max-height: 1000px;
    }
  }
  
  .detailed-stats {
    margin-bottom: 25px;
  }
  
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
  }
  
  .detailed-stat {
    display: flex;
    align-items: center;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
  }
  
  .stat-icon {
    font-size: 1.5em;
    margin-right: 12px;
  }
  
  .stat-title {
    font-size: 0.9em;
    color: #666;
    margin-bottom: 4px;
  }
  
  .stat-number {
    font-size: 1.2em;
    font-weight: bold;
    color: #333;
  }
  
  .first-kill-section,
  .recent-kills-section,
  .top-killers-section,
  .description-section {
    margin-bottom: 25px;
  }
  
  .first-kill-section h4,
  .recent-kills-section h4,
  .top-killers-section h4,
  .description-section h4 {
    margin: 0 0 15px 0;
    font-size: 1.1em;
    color: #333;
    border-bottom: 2px solid #007bff;
    padding-bottom: 5px;
  }
  
  .first-kill-info {
    background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
    padding: 15px;
    border-radius: 8px;
    border-left: 4px solid #f39c12;
  }
  
  .first-kill-team {
    margin-bottom: 10px;
  }
  
  .team-member {
    display: inline-block;
    margin-right: 10px;
    padding: 4px 8px;
    background: rgba(255,255,255,0.8);
    border-radius: 4px;
    font-weight: 500;
    cursor: pointer;
    transition: background 0.2s ease;
  }
  
  .team-member:hover {
    background: white;
  }
  
  .member-class {
    font-size: 0.8em;
    color: #666;
  }
  
  .first-kill-details {
    display: flex;
    gap: 15px;
    font-size: 0.9em;
  }
  
  .recent-kills-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  
  .recent-kill {
    padding: 12px;
    background: #f8f9fa;
    border-radius: 6px;
    cursor: pointer;
    transition: background 0.2s ease;
  }
  
  .recent-kill:hover {
    background: #e9ecef;
  }
  
  .kill-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
  }
  
  .kill-time-badge {
    background: #007bff;
    color: white;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.8em;
    font-weight: 600;
  }
  
  .time-ago {
    font-size: 0.8em;
    color: #666;
  }
  
  .kill-team {
    font-size: 0.9em;
    margin-bottom: 4px;
  }
  
  .team-member-mini {
    color: #333;
  }
  
  .kill-meta {
    font-size: 0.8em;
    color: #888;
  }
  
  .top-killers-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .top-killer {
    display: flex;
    align-items: center;
    padding: 10px;
    background: #f8f9fa;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .top-killer:hover {
    background: #e9ecef;
    transform: translateX(2px);
  }
  
  .killer-rank {
    font-weight: bold;
    color: #007bff;
    margin-right: 12px;
    min-width: 30px;
  }
  
  .killer-name {
    font-weight: 600;
    color: #333;
    margin-bottom: 2px;
  }
  
  .killer-stats {
    font-size: 0.8em;
    color: #666;
  }
  
  .boss-description {
    color: #555;
    line-height: 1.6;
    margin-bottom: 15px;
  }
  
  .rewards {
    font-size: 0.9em;
    color: #666;
  }
  
  .reward-item {
    color: #007bff;
    font-weight: 500;
  }
  
  .loading-indicator {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(255,255,255,0.95);
    padding: 10px 20px;
    border-radius: 20px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  }
  
  .spinner {
    width: 20px;
    height: 20px;
    border: 2px solid #f3f3f3;
    border-top: 2px solid #007bff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
  
  .last-updated {
    padding: 10px 20px;
    background: #f8f9fa;
    border-top: 1px solid #e9ecef;
    font-size: 0.8em;
    color: #666;
    text-align: center;
  }
  
  @media (max-width: 768px) {
    .quick-stats {
      grid-template-columns: repeat(2, 1fr);
    }
    
    .stats-grid {
      grid-template-columns: 1fr;
    }
    
    .card-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 15px;
    }
    
    .header-stats {
      flex-direction: row;
      align-self: flex-end;
    }
  }
</style>