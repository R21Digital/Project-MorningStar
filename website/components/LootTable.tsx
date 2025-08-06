/**
 * LootTable Component - Phase 2
 * Displays sortable, filterable loot tables for heroic instances
 * Integrates with Batch 171 API endpoints
 */

import React, { useState, useEffect, useMemo } from 'react';

interface LootEntry {
  timestamp: string;
  player_name: string;
  heroic_instance: string;
  boss_name: string;
  item_name: string;
  item_type: string;
  rarity: string;
  quantity: number;
  stats?: Record<string, any>;
  completion_status: string;
  difficulty: string;
  group_size: number;
  session_id?: string;
}

interface LootTableProps {
  heroicInstance?: string;
  apiEndpoint?: string;
  showAllHeroics?: boolean;
  maxEntries?: number;
  refreshInterval?: number;
  className?: string;
}

interface SortConfig {
  key: keyof LootEntry;
  direction: 'asc' | 'desc';
}

interface FilterConfig {
  rarity: string;
  itemType: string;
  boss: string;
  player: string;
  dateRange: string;
}

const RARITY_COLORS = {
  common: '#9d9d9d',
  uncommon: '#1eff00',
  rare: '#0070dd',
  epic: '#a335ee',
  legendary: '#ff8000'
};

const ITEM_TYPE_ICONS = {
  weapon: 'fas fa-sword',
  armor: 'fas fa-shield-alt',
  accessory: 'fas fa-gem',
  material: 'fas fa-hammer',
  consumable: 'fas fa-flask',
  currency: 'fas fa-coins',
  cosmetic: 'fas fa-palette',
  misc: 'fas fa-question'
};

export const LootTable: React.FC<LootTableProps> = ({
  heroicInstance,
  apiEndpoint = '/api/heroics/loot',
  showAllHeroics = false,
  maxEntries = 100,
  refreshInterval = 30000, // 30 seconds
  className = ''
}) => {
  const [lootData, setLootData] = useState<LootEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortConfig, setSortConfig] = useState<SortConfig>({ key: 'timestamp', direction: 'desc' });
  const [filters, setFilters] = useState<FilterConfig>({
    rarity: 'all',
    itemType: 'all',
    boss: 'all',
    player: 'all',
    dateRange: '24h'
  });

  // Fetch loot data from API
  const fetchLootData = async () => {
    try {
      setLoading(true);
      setError(null);

      const params = new URLSearchParams({
        limit: maxEntries.toString(),
        sort: sortConfig.key,
        order: sortConfig.direction
      });

      if (heroicInstance && !showAllHeroics) {
        params.append('heroic', heroicInstance);
      }

      if (filters.rarity !== 'all') {
        params.append('rarity', filters.rarity);
      }

      if (filters.itemType !== 'all') {
        params.append('type', filters.itemType);
      }

      if (filters.player !== 'all') {
        params.append('player', filters.player);
      }

      const response = await fetch(`${apiEndpoint}?${params}`);
      
      if (!response.ok) {
        throw new Error(`API request failed: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success && result.data) {
        setLootData(result.data);
      } else {
        throw new Error(result.error || 'Failed to load loot data');
      }
    } catch (err) {
      console.error('Error fetching loot data:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
      setLootData([]);
    } finally {
      setLoading(false);
    }
  };

  // Auto-refresh data
  useEffect(() => {
    fetchLootData();
    
    if (refreshInterval > 0) {
      const interval = setInterval(fetchLootData, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [heroicInstance, sortConfig, filters, maxEntries]);

  // Handle sorting
  const handleSort = (key: keyof LootEntry) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }));
  };

  // Handle filtering
  const handleFilterChange = (filterKey: keyof FilterConfig, value: string) => {
    setFilters(prev => ({ ...prev, [filterKey]: value }));
  };

  // Get unique values for filter dropdowns
  const uniqueValues = useMemo(() => {
    const bosses = [...new Set(lootData.map(entry => entry.boss_name))].filter(Boolean);
    const players = [...new Set(lootData.map(entry => entry.player_name))].filter(Boolean);
    const rarities = [...new Set(lootData.map(entry => entry.rarity))].filter(Boolean);
    const itemTypes = [...new Set(lootData.map(entry => entry.item_type))].filter(Boolean);

    return { bosses, players, rarities, itemTypes };
  }, [lootData]);

  // Format timestamp for display
  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMins / 60);
      const diffDays = Math.floor(diffHours / 24);

      if (diffMins < 1) return 'Just now';
      if (diffMins < 60) return `${diffMins}m ago`;
      if (diffHours < 24) return `${diffHours}h ago`;
      if (diffDays < 7) return `${diffDays}d ago`;
      
      return date.toLocaleDateString();
    } catch {
      return timestamp;
    }
  };

  // Format item name with stats tooltip
  const formatItemName = (entry: LootEntry) => {
    const hasStats = entry.stats && Object.keys(entry.stats).length > 0;
    
    return (
      <div className="item-name-container">
        <span 
          className="item-name"
          style={{ color: RARITY_COLORS[entry.rarity as keyof typeof RARITY_COLORS] || '#000' }}
          title={hasStats ? JSON.stringify(entry.stats, null, 2) : undefined}
        >
          {entry.quantity > 1 ? `${entry.quantity}x ` : ''}
          {entry.item_name}
        </span>
        {hasStats && (
          <i className="fas fa-info-circle stats-icon" title="Has stats"></i>
        )}
      </div>
    );
  };

  // Get sort icon
  const getSortIcon = (column: keyof LootEntry) => {
    if (sortConfig.key !== column) return 'fas fa-sort';
    return sortConfig.direction === 'asc' ? 'fas fa-sort-up' : 'fas fa-sort-down';
  };

  if (loading && lootData.length === 0) {
    return (
      <div className={`loot-table-loading ${className}`}>
        <div className="loading-spinner">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading loot data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`loot-table-error ${className}`}>
        <div className="error-message">
          <i className="fas fa-exclamation-triangle"></i>
          <h3>Failed to Load Loot Data</h3>
          <p>{error}</p>
          <button onClick={fetchLootData} className="retry-btn">
            <i className="fas fa-redo"></i> Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`loot-table-container ${className}`}>
      {/* Header with stats */}
      <div className="loot-table-header">
        <div className="loot-stats">
          <span className="stat-item">
            <i className="fas fa-treasure-chest"></i>
            {lootData.length} items
          </span>
          {!showAllHeroics && heroicInstance && (
            <span className="stat-item">
              <i className="fas fa-shield-alt"></i>
              {heroicInstance.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
            </span>
          )}
          <span className="stat-item">
            <i className="fas fa-clock"></i>
            Last updated: {formatTimestamp(new Date().toISOString())}
          </span>
        </div>
      </div>

      {/* Filters */}
      <div className="loot-filters">
        <div className="filter-group">
          <label>Rarity:</label>
          <select 
            value={filters.rarity} 
            onChange={(e) => handleFilterChange('rarity', e.target.value)}
          >
            <option value="all">All Rarities</option>
            {uniqueValues.rarities.map(rarity => (
              <option key={rarity} value={rarity}>
                {rarity.charAt(0).toUpperCase() + rarity.slice(1)}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Type:</label>
          <select 
            value={filters.itemType} 
            onChange={(e) => handleFilterChange('itemType', e.target.value)}
          >
            <option value="all">All Types</option>
            {uniqueValues.itemTypes.map(type => (
              <option key={type} value={type}>
                {type.charAt(0).toUpperCase() + type.slice(1)}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Boss:</label>
          <select 
            value={filters.boss} 
            onChange={(e) => handleFilterChange('boss', e.target.value)}
          >
            <option value="all">All Bosses</option>
            {uniqueValues.bosses.map(boss => (
              <option key={boss} value={boss}>{boss}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Player:</label>
          <select 
            value={filters.player} 
            onChange={(e) => handleFilterChange('player', e.target.value)}
          >
            <option value="all">All Players</option>
            {uniqueValues.players.slice(0, 10).map(player => (
              <option key={player} value={player}>{player}</option>
            ))}
          </select>
        </div>

        <button onClick={fetchLootData} className="refresh-btn" title="Refresh data">
          <i className={`fas fa-sync-alt ${loading ? 'fa-spin' : ''}`}></i>
        </button>
      </div>

      {/* Loot Table */}
      <div className="loot-table-wrapper">
        <table className="loot-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('timestamp')} className="sortable">
                <i className="fas fa-clock"></i>
                Time
                <i className={getSortIcon('timestamp')}></i>
              </th>
              <th onClick={() => handleSort('item_name')} className="sortable">
                <i className="fas fa-cube"></i>
                Item
                <i className={getSortIcon('item_name')}></i>
              </th>
              <th onClick={() => handleSort('rarity')} className="sortable">
                <i className="fas fa-star"></i>
                Rarity
                <i className={getSortIcon('rarity')}></i>
              </th>
              <th onClick={() => handleSort('boss_name')} className="sortable">
                <i className="fas fa-skull"></i>
                Boss
                <i className={getSortIcon('boss_name')}></i>
              </th>
              <th onClick={() => handleSort('player_name')} className="sortable">
                <i className="fas fa-user"></i>
                Player
                <i className={getSortIcon('player_name')}></i>
              </th>
              {showAllHeroics && (
                <th onClick={() => handleSort('heroic_instance')} className="sortable">
                  <i className="fas fa-shield-alt"></i>
                  Heroic
                  <i className={getSortIcon('heroic_instance')}></i>
                </th>
              )}
              <th>
                <i className="fas fa-info-circle"></i>
                Details
              </th>
            </tr>
          </thead>
          <tbody>
            {lootData.length === 0 ? (
              <tr>
                <td colSpan={showAllHeroics ? 7 : 6} className="no-data">
                  <i className="fas fa-search"></i>
                  No loot data found
                </td>
              </tr>
            ) : (
              lootData.map((entry, index) => (
                <tr key={`${entry.session_id}-${entry.timestamp}-${index}`} className="loot-row">
                  <td className="timestamp-cell">
                    <time title={new Date(entry.timestamp).toLocaleString()}>
                      {formatTimestamp(entry.timestamp)}
                    </time>
                  </td>
                  <td className="item-cell">
                    <div className="item-info">
                      <i className={ITEM_TYPE_ICONS[entry.item_type as keyof typeof ITEM_TYPE_ICONS] || 'fas fa-question'}></i>
                      {formatItemName(entry)}
                    </div>
                  </td>
                  <td className="rarity-cell">
                    <span 
                      className={`rarity-badge rarity-${entry.rarity}`}
                      style={{ 
                        backgroundColor: RARITY_COLORS[entry.rarity as keyof typeof RARITY_COLORS],
                        color: entry.rarity === 'uncommon' ? '#000' : '#fff'
                      }}
                    >
                      {entry.rarity}
                    </span>
                  </td>
                  <td className="boss-cell">
                    {entry.boss_name}
                  </td>
                  <td className="player-cell">
                    <span className="player-name" title={`Group size: ${entry.group_size}`}>
                      {entry.player_name}
                    </span>
                  </td>
                  {showAllHeroics && (
                    <td className="heroic-cell">
                      {entry.heroic_instance.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </td>
                  )}
                  <td className="details-cell">
                    <div className="details-info">
                      <span className="difficulty-badge difficulty-{entry.difficulty}">
                        {entry.difficulty}
                      </span>
                      {entry.completion_status === 'completed' ? (
                        <i className="fas fa-check-circle success" title="Completed"></i>
                      ) : (
                        <i className="fas fa-times-circle warning" title="Incomplete"></i>
                      )}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      <div className="loot-table-footer">
        <div className="footer-info">
          <span>
            <i className="fas fa-database"></i>
            Data from MS11 bot sessions and mod submissions
          </span>
          <span className="attribution">
            <i className="fas fa-external-link-alt"></i>
            Generated by SWGDB
          </span>
        </div>
      </div>
    </div>
  );
};

export default LootTable;