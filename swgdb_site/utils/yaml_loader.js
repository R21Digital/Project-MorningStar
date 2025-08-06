const yaml = require('js-yaml');
const fs = require('fs');
const path = require('path');

class YamlLoader {
    constructor() {
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
    }

    /**
     * Load and parse a YAML file
     * @param {string} filePath - Path to the YAML file
     * @param {boolean} useCache - Whether to use caching (default: true)
     * @returns {object} Parsed YAML data
     */
    loadYaml(filePath, useCache = true) {
        const absolutePath = path.resolve(filePath);
        
        // Check cache first
        if (useCache && this.cache.has(absolutePath)) {
            const cached = this.cache.get(absolutePath);
            if (Date.now() - cached.timestamp < this.cacheTimeout) {
                return cached.data;
            }
        }

        try {
            // Check if file exists
            if (!fs.existsSync(absolutePath)) {
                throw new Error(`File not found: ${absolutePath}`);
            }

            // Read and parse file
            const fileContents = fs.readFileSync(absolutePath, 'utf8');
            const data = yaml.load(fileContents);

            // Cache the result
            if (useCache) {
                this.cache.set(absolutePath, {
                    data: data,
                    timestamp: Date.now()
                });
            }

            return data;
        } catch (error) {
            console.error(`Error loading YAML file ${absolutePath}:`, error);
            throw error;
        }
    }

    /**
     * Load heroics loot data
     * @returns {object} Heroics loot data
     */
    loadHeroicsLoot() {
        const lootDataPath = path.join(__dirname, '../data/loot/heroics.yml');
        return this.loadYaml(lootDataPath);
    }

    /**
     * Get specific section from heroics loot data
     * @param {string} section - Section name (heroics, rarity_levels, etc.)
     * @returns {object} Section data
     */
    getHeroicsSection(section) {
        const data = this.loadHeroicsLoot();
        return data[section] || {};
    }

    /**
     * Get all heroics data
     * @returns {object} All heroics data
     */
    getAllHeroics() {
        return this.getHeroicsSection('heroics');
    }

    /**
     * Get rarity levels
     * @returns {object} Rarity levels data
     */
    getRarityLevels() {
        return this.getHeroicsSection('rarity_levels');
    }

    /**
     * Get loot types
     * @returns {object} Loot types data
     */
    getLootTypes() {
        return this.getHeroicsSection('loot_types');
    }

    /**
     * Get profession relevance
     * @returns {object} Profession relevance data
     */
    getProfessionRelevance() {
        return this.getHeroicsSection('profession_relevance');
    }

    /**
     * Get source information
     * @returns {object} Source information
     */
    getSourceInfo() {
        return this.getHeroicsSection('source_info');
    }

    /**
     * Get metadata
     * @returns {object} Metadata
     */
    getMetadata() {
        return this.getHeroicsSection('metadata');
    }

    /**
     * Clear cache
     */
    clearCache() {
        this.cache.clear();
    }

    /**
     * Get cache statistics
     * @returns {object} Cache statistics
     */
    getCacheStats() {
        return {
            size: this.cache.size,
            entries: Array.from(this.cache.keys())
        };
    }

    /**
     * Validate heroics data structure
     * @param {object} data - Data to validate
     * @returns {object} Validation result
     */
    validateHeroicsData(data) {
        const errors = [];
        const warnings = [];

        // Check required sections
        const requiredSections = ['heroics', 'rarity_levels', 'loot_types'];
        requiredSections.forEach(section => {
            if (!data[section]) {
                errors.push(`Missing required section: ${section}`);
            }
        });

        // Validate heroics structure
        if (data.heroics) {
            Object.keys(data.heroics).forEach(heroicId => {
                const heroic = data.heroics[heroicId];
                
                if (!heroic.name) {
                    errors.push(`Heroic ${heroicId} missing name`);
                }
                
                if (!heroic.planet) {
                    errors.push(`Heroic ${heroicId} missing planet`);
                }
                
                if (!heroic.bosses || !Array.isArray(heroic.bosses)) {
                    errors.push(`Heroic ${heroicId} missing or invalid bosses array`);
                } else {
                    heroic.bosses.forEach((boss, index) => {
                        if (!boss.name) {
                            errors.push(`Boss ${index} in heroic ${heroicId} missing name`);
                        }
                        
                        if (!boss.loot || !Array.isArray(boss.loot)) {
                            errors.push(`Boss ${boss.name} missing or invalid loot array`);
                        } else {
                            boss.loot.forEach((item, itemIndex) => {
                                if (!item.name) {
                                    errors.push(`Loot item ${itemIndex} in boss ${boss.name} missing name`);
                                }
                                
                                if (!item.rarity) {
                                    warnings.push(`Loot item ${item.name} missing rarity`);
                                }
                                
                                if (!item.type) {
                                    warnings.push(`Loot item ${item.name} missing type`);
                                }
                                
                                if (!item.drop_chance) {
                                    warnings.push(`Loot item ${item.name} missing drop chance`);
                                }
                            });
                        }
                    });
                }
            });
        }

        return {
            isValid: errors.length === 0,
            errors: errors,
            warnings: warnings
        };
    }

    /**
     * Get filtered heroics data
     * @param {object} filters - Filter criteria
     * @returns {object} Filtered data
     */
    getFilteredHeroics(filters = {}) {
        const allHeroics = this.getAllHeroics();
        const filtered = {};

        Object.keys(allHeroics).forEach(heroicId => {
            const heroic = allHeroics[heroicId];
            
            // Apply heroic filter
            if (filters.heroic && filters.heroic !== 'all' && filters.heroic !== heroicId) {
                return;
            }

            // Apply planet filter
            if (filters.planet && filters.planet !== 'all' && filters.planet !== heroic.planet) {
                return;
            }

            // Filter bosses and their loot
            const filteredBosses = heroic.bosses.filter(boss => {
                const filteredLoot = boss.loot.filter(item => {
                    // Rarity filter
                    if (filters.rarity && filters.rarity !== 'all' && item.rarity !== filters.rarity) {
                        return false;
                    }

                    // Type filter
                    if (filters.type && filters.type !== 'all' && item.type !== filters.type) {
                        return false;
                    }

                    // Profession filter
                    if (filters.profession && filters.profession !== 'all') {
                        const professionRelevance = this.getProfessionRelevance();
                        const relevantItems = professionRelevance[filters.profession] || [];
                        if (!relevantItems.includes(item.name)) {
                            return false;
                        }
                    }

                    return true;
                });

                return filteredLoot.length > 0;
            });

            if (filteredBosses.length > 0) {
                filtered[heroicId] = {
                    ...heroic,
                    bosses: filteredBosses
                };
            }
        });

        return filtered;
    }
}

module.exports = YamlLoader; 