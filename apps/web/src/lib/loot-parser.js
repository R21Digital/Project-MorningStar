/**
 * Loot Parser - Helper library for loot formatting and filtering
 * Supports both manual and bot-generated loot data
 */

class LootParser {
  constructor() {
    this.rarityColors = {
      common: '#9d9d9d',
      uncommon: '#1eff00',
      rare: '#0070dd',
      epic: '#a335ee',
      legendary: '#ff8000'
    };

    this.rarityOrder = ['common', 'uncommon', 'rare', 'epic', 'legendary'];
    this.itemTypes = ['weapon', 'armor', 'material', 'component', 'trophy', 'decoration'];
  }

  /**
   * Format rarity for display
   */
  formatRarity(rarity) {
    return rarity.charAt(0).toUpperCase() + rarity.slice(1);
  }

  /**
   * Get rarity color for styling
   */
  getRarityColor(rarity) {
    return this.rarityColors[rarity] || '#9d9d9d';
  }

  /**
   * Sort items by rarity
   */
  sortByRarity(items) {
    return items.sort((a, b) => {
      const aIndex = this.rarityOrder.indexOf(a.rarity);
      const bIndex = this.rarityOrder.indexOf(b.rarity);
      return bIndex - aIndex; // Legendary first
    });
  }

  /**
   * Filter items by multiple criteria
   */
  filterItems(items, filters = {}) {
    return items.filter(item => {
      // Rarity filter
      if (filters.rarity && item.rarity !== filters.rarity) {
        return false;
      }

      // Type filter
      if (filters.type && item.type !== filters.type) {
        return false;
      }

      // Profession filter
      if (filters.profession && item.profession_relevance) {
        if (!item.profession_relevance.includes(filters.profession)) {
          return false;
        }
      }

      // Source filter
      if (filters.source && item.source !== filters.source) {
        return false;
      }

      // Search filter
      if (filters.search) {
        const searchTerm = filters.search.toLowerCase();
        const itemName = item.name.toLowerCase();
        const itemUseCase = (item.use_case || '').toLowerCase();
        
        if (!itemName.includes(searchTerm) && !itemUseCase.includes(searchTerm)) {
          return false;
        }
      }

      return true;
    });
  }

  /**
   * Calculate drop rate percentage
   */
  calculateDropRate(totalDrops, totalKills) {
    if (totalKills === 0) return 0;
    return ((totalDrops / totalKills) * 100).toFixed(1);
  }

  /**
   * Format drop chance for display
   */
  formatDropChance(dropChance) {
    if (dropChance >= 1) {
      return `${dropChance.toFixed(1)}%`;
    } else {
      return `${(dropChance * 100).toFixed(2)}%`;
    }
  }

  /**
   * Parse loot data from JSON files
   */
  parseLootData(data) {
    const parsed = {
      planet: data.planet,
      sourceType: data.source_type,
      totalRuns: data.total_runs || 0,
      totalLoot: data.total_loot || 0,
      lastUpdated: data.last_updated,
      heroics: {}
    };

    if (data.heroics) {
      Object.keys(data.heroics).forEach(heroicKey => {
        const heroic = data.heroics[heroicKey];
        parsed.heroics[heroicKey] = {
          boss: heroic.boss,
          location: heroic.location,
          level: heroic.level,
          totalKills: heroic.total_kills || 0,
          items: []
        };

        // Convert items object to array for easier filtering
        if (heroic.items) {
          Object.keys(heroic.items).forEach(itemKey => {
            const item = heroic.items[itemKey];
            parsed.heroics[heroicKey].items.push({
              id: itemKey,
              ...item,
              dropRate: this.calculateDropRate(item.total_drops || 0, heroic.total_kills || 1)
            });
          });
        }

        // Sort items by rarity
        parsed.heroics[heroicKey].items = this.sortByRarity(parsed.heroics[heroicKey].items);
      });
    }

    return parsed;
  }

  /**
   * Merge bot-generated data with manual data
   */
  mergeLootData(manualData, botData) {
    const merged = { ...manualData };

    if (botData && botData.items) {
      Object.keys(botData.items).forEach(itemKey => {
        const botItem = botData.items[itemKey];
        
        // Find matching item in manual data
        const existingItem = merged.heroics[botData.heroic]?.items.find(
          item => item.name.toLowerCase() === botItem.name.toLowerCase()
        );

        if (existingItem) {
          // Update with bot data
          existingItem.total_drops = (existingItem.total_drops || 0) + botItem.total_drops;
          existingItem.total_quantity = (existingItem.total_quantity || 0) + botItem.total_quantity;
          existingItem.first_seen = existingItem.first_seen || botItem.first_seen;
          existingItem.last_seen = botItem.last_seen || existingItem.last_seen;
          existingItem.source = 'Bot Generated + Manual';
        } else {
          // Add new item from bot data
          if (!merged.heroics[botData.heroic]) {
            merged.heroics[botData.heroic] = {
              boss: botData.boss || 'Unknown',
              location: botData.location || 'Unknown',
              level: botData.level || 0,
              totalKills: botData.total_kills || 0,
              items: []
            };
          }
          
          merged.heroics[botData.heroic].items.push({
            id: itemKey,
            ...botItem,
            source: 'Bot Generated',
            dropRate: this.calculateDropRate(botItem.total_drops, botData.total_kills || 1)
          });
        }
      });
    }

    return merged;
  }

  /**
   * Generate statistics for loot table
   */
  generateStats(lootData) {
    const stats = {
      totalItems: 0,
      totalRuns: lootData.totalRuns || 0,
      rarityBreakdown: {},
      typeBreakdown: {},
      professionBreakdown: {},
      sourceBreakdown: {}
    };

    Object.values(lootData.heroics).forEach(heroic => {
      heroic.items.forEach(item => {
        stats.totalItems++;
        
        // Rarity breakdown
        stats.rarityBreakdown[item.rarity] = (stats.rarityBreakdown[item.rarity] || 0) + 1;
        
        // Type breakdown
        stats.typeBreakdown[item.type] = (stats.typeBreakdown[item.type] || 0) + 1;
        
        // Source breakdown
        stats.sourceBreakdown[item.source] = (stats.sourceBreakdown[item.source] || 0) + 1;
        
        // Profession breakdown
        if (item.profession_relevance) {
          item.profession_relevance.forEach(profession => {
            stats.professionBreakdown[profession] = (stats.professionBreakdown[profession] || 0) + 1;
          });
        }
      });
    });

    return stats;
  }

  /**
   * Export loot data for MS11 sync
   */
  exportForMS11(lootData) {
    const exportData = {
      timestamp: new Date().toISOString(),
      source: 'SWGDB Loot Tables',
      heroics: {}
    };

    Object.keys(lootData.heroics).forEach(heroicKey => {
      const heroic = lootData.heroics[heroicKey];
      exportData.heroics[heroicKey] = {
        boss: heroic.boss,
        location: heroic.location,
        level: heroic.level,
        items: heroic.items.map(item => ({
          name: item.name,
          type: item.type,
          rarity: item.rarity,
          drop_chance: item.drop_chance,
          profession_relevance: item.profession_relevance,
          use_case: item.use_case
        }))
      };
    });

    return exportData;
  }
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = LootParser;
}

// Export for browser
if (typeof window !== 'undefined') {
  window.LootParser = LootParser;
} 