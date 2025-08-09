const yaml = require('js-yaml');
const fs = require('fs');
const path = require('path');

/**
 * YAML Loader Utility
 * Provides functions to load and parse YAML files with error handling
 */

class YamlLoader {
  /**
   * Load a YAML file from the given path
   * @param {string} filePath - Path to the YAML file
   * @returns {object} Parsed YAML data or empty object on error
   */
  static loadFile(filePath) {
    try {
      const absolutePath = path.resolve(filePath);
      const fileContents = fs.readFileSync(absolutePath, 'utf8');
      return yaml.load(fileContents);
    } catch (error) {
      console.error(`Error loading YAML file ${filePath}:`, error.message);
      return {};
    }
  }

  /**
   * Load heroics loot data from the default location
   * @returns {object} Heroics loot data
   */
  static loadHeroicsData() {
    const heroicsPath = path.join(__dirname, '../data/loot/heroics.yml');
    return this.loadFile(heroicsPath);
  }

  /**
   * Get all available planets from heroics data
   * @returns {string[]} Array of planet names
   */
  static getPlanets() {
    const data = this.loadHeroicsData();
    return Object.keys(data.heroics || {});
  }

  /**
   * Get all bosses for a specific planet
   * @param {string} planet - Planet name
   * @returns {object[]} Array of boss objects
   */
  static getBossesForPlanet(planet) {
    const data = this.loadHeroicsData();
    return data.heroics?.[planet] || [];
  }

  /**
   * Get all loot items for a specific boss
   * @param {string} planet - Planet name
   * @param {string} bossName - Boss name
   * @returns {object[]} Array of loot items
   */
  static getLootForBoss(planet, bossName) {
    const bosses = this.getBossesForPlanet(planet);
    const boss = bosses.find(b => b.boss.toLowerCase() === bossName.toLowerCase());
    return boss?.loot || [];
  }

  /**
   * Get all loot types available
   * @returns {string[]} Array of loot types
   */
  static getLootTypes() {
    const data = this.loadHeroicsData();
    return data.loot_types || [];
  }

  /**
   * Get all rarity levels available
   * @returns {string[]} Array of rarity levels
   */
  static getRarityLevels() {
    const data = this.loadHeroicsData();
    return data.rarity_levels || [];
  }

  /**
   * Get all professions available
   * @returns {string[]} Array of professions
   */
  static getProfessions() {
    const data = this.loadHeroicsData();
    return data.professions || [];
  }

  /**
   * Filter loot items by criteria
   * @param {object} filters - Filter criteria
   * @returns {object[]} Filtered loot items
   */
  static filterLoot(filters = {}) {
    const data = this.loadHeroicsData();
    const allLoot = [];

    // Collect all loot items from all planets and bosses
    Object.values(data.heroics || {}).forEach(planetBosses => {
      planetBosses.forEach(boss => {
        boss.loot.forEach(item => {
          allLoot.push({
            ...item,
            boss: boss.boss,
            planet: boss.location.split(' - ')[0].toLowerCase(),
            location: boss.location,
            level: boss.level
          });
        });
      });
    });

    // Apply filters
    return allLoot.filter(item => {
      if (filters.planet && item.planet !== filters.planet.toLowerCase()) return false;
      if (filters.boss && item.boss.toLowerCase() !== filters.boss.toLowerCase()) return false;
      if (filters.type && item.type !== filters.type) return false;
      if (filters.rarity && item.rarity !== filters.rarity) return false;
      if (filters.profession && !item.profession_relevance.includes(filters.profession)) return false;
      if (filters.minDropChance && item.drop_chance < filters.minDropChance) return false;
      if (filters.maxDropChance && item.drop_chance > filters.maxDropChance) return false;
      return true;
    });
  }

  /**
   * Get statistics about the loot data
   * @returns {object} Statistics object
   */
  static getLootStats() {
    const data = this.loadHeroicsData();
    const stats = {
      totalPlanets: 0,
      totalBosses: 0,
      totalLootItems: 0,
      rarityBreakdown: {},
      typeBreakdown: {},
      professionBreakdown: {},
      averageDropRate: 0
    };

    let totalDropRate = 0;
    let dropRateCount = 0;

    Object.values(data.heroics || {}).forEach(planetBosses => {
      stats.totalPlanets++;
      planetBosses.forEach(boss => {
        stats.totalBosses++;
        boss.loot.forEach(item => {
          stats.totalLootItems++;
          
          // Rarity breakdown
          stats.rarityBreakdown[item.rarity] = (stats.rarityBreakdown[item.rarity] || 0) + 1;
          
          // Type breakdown
          stats.typeBreakdown[item.type] = (stats.typeBreakdown[item.type] || 0) + 1;
          
          // Profession breakdown
          item.profession_relevance.forEach(profession => {
            stats.professionBreakdown[profession] = (stats.professionBreakdown[profession] || 0) + 1;
          });
          
          // Drop rate calculation
          totalDropRate += item.drop_chance;
          dropRateCount++;
        });
      });
    });

    stats.averageDropRate = dropRateCount > 0 ? totalDropRate / dropRateCount : 0;

    return stats;
  }

  /**
   * Validate the structure of heroics data
   * @returns {object} Validation result
   */
  static validateHeroicsData() {
    const data = this.loadHeroicsData();
    const errors = [];
    const warnings = [];

    // Check required top-level keys
    if (!data.heroics) {
      errors.push('Missing required "heroics" key');
    }

    if (!data.loot_types) {
      warnings.push('Missing "loot_types" definition');
    }

    if (!data.rarity_levels) {
      warnings.push('Missing "rarity_levels" definition');
    }

    if (!data.professions) {
      warnings.push('Missing "professions" definition');
    }

    // Validate planet structure
    Object.entries(data.heroics || {}).forEach(([planet, bosses]) => {
      if (!Array.isArray(bosses)) {
        errors.push(`Planet "${planet}" has invalid structure - expected array`);
        return;
      }

      bosses.forEach((boss, index) => {
        if (!boss.boss) {
          errors.push(`Boss at index ${index} in planet "${planet}" missing "boss" field`);
        }

        if (!boss.location) {
          warnings.push(`Boss "${boss.boss}" in planet "${planet}" missing "location" field`);
        }

        if (!boss.level) {
          warnings.push(`Boss "${boss.boss}" in planet "${planet}" missing "level" field`);
        }

        if (!Array.isArray(boss.loot)) {
          errors.push(`Boss "${boss.boss}" in planet "${planet}" missing or invalid "loot" array`);
          return;
        }

        boss.loot.forEach((item, itemIndex) => {
          if (!item.name) {
            errors.push(`Loot item at index ${itemIndex} for boss "${boss.boss}" missing "name" field`);
          }

          if (!item.type) {
            warnings.push(`Loot item "${item.name}" missing "type" field`);
          }

          if (!item.rarity) {
            warnings.push(`Loot item "${item.name}" missing "rarity" field`);
          }

          if (!item.use_case) {
            warnings.push(`Loot item "${item.name}" missing "use_case" field`);
          }

          if (typeof item.drop_chance !== 'number') {
            warnings.push(`Loot item "${item.name}" has invalid "drop_chance" value`);
          }

          if (!Array.isArray(item.profession_relevance)) {
            warnings.push(`Loot item "${item.name}" missing or invalid "profession_relevance" array`);
          }
        });
      });
    });

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }
}

module.exports = YamlLoader; 