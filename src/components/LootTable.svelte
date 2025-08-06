<script>
  import { onMount } from 'svelte';
  import LootParser from '../lib/loot-parser.js';

  // Props
  export let lootData = {};
  export let planet = '';
  export let heroic = '';

  // Reactive variables
  let filteredItems = [];
  let filters = {
    rarity: '',
    type: '',
    profession: '',
    source: '',
    search: ''
  };
  let stats = {};
  let showStats = false;
  let showMS11Sync = false;
  let ms11ExportData = null;

  // Initialize loot parser
  let lootParser = new LootParser();

  // Available filter options
  $: rarityOptions = ['common', 'uncommon', 'rare', 'epic', 'legendary'];
  $: typeOptions = ['weapon', 'armor', 'material', 'component', 'trophy', 'decoration'];
  $: professionOptions = ['weaponsmith', 'armorsmith', 'artisan', 'tailor', 'chemist', 'architect', 'jeweler'];
  $: sourceOptions = ['SWGDB Generated', 'User Submitted', 'Bot Generated', 'Bot Generated + Manual'];

  // Update filtered items when data or filters change
  $: {
    if (lootData && lootData.heroics && lootData.heroics[heroic]) {
      const items = lootData.heroics[heroic].items || [];
      filteredItems = lootParser.filterItems(items, filters);
      stats = lootParser.generateStats(lootData);
    }
  }

  // Handle filter changes
  function updateFilter(filterType, value) {
    filters[filterType] = value;
    filters = filters; // Trigger reactivity
  }

  // Clear all filters
  function clearFilters() {
    filters = {
      rarity: '',
      type: '',
      profession: '',
      source: '',
      search: ''
    };
  }

  // Toggle statistics panel
  function toggleStats() {
    showStats = !showStats;
  }

  // Generate MS11 export data
  function generateMS11Export() {
    ms11ExportData = lootParser.exportForMS11(lootData);
    showMS11Sync = true;
  }

  // Copy MS11 export to clipboard
  function copyMS11Export() {
    const exportText = JSON.stringify(ms11ExportData, null, 2);
    navigator.clipboard.writeText(exportText).then(() => {
      alert('MS11 export data copied to clipboard!');
    });
  }

  // Download MS11 export as JSON file
  function downloadMS11Export() {
    const exportText = JSON.stringify(ms11ExportData, null, 2);
    const blob = new Blob([exportText], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${planet}_heroics_ms11_export.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }
</script>

<div class="loot-table-container">
  <!-- Header -->
  <div class="loot-header">
    <h2>{planet.charAt(0).toUpperCase() + planet.slice(1)} Heroics - {heroic.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</h2>
    <div class="header-actions">
      <button class="btn btn-secondary" on:click={toggleStats}>
        {showStats ? 'Hide' : 'Show'} Statistics
      </button>
      <button class="btn btn-primary" on:click={generateMS11Export}>
        MS11 Sync
      </button>
    </div>
  </div>

  <!-- Statistics Panel -->
  {#if showStats}
    <div class="stats-panel">
      <div class="stats-grid">
        <div class="stat-item">
          <span class="stat-label">Total Items:</span>
          <span class="stat-value">{stats.totalItems || 0}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Total Runs:</span>
          <span class="stat-value">{stats.totalRuns || 0}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Last Updated:</span>
          <span class="stat-value">{lootData.lastUpdated ? new Date(lootData.lastUpdated).toLocaleDateString() : 'Unknown'}</span>
        </div>
      </div>
      
      {#if Object.keys(stats.rarityBreakdown || {}).length > 0}
        <div class="breakdown-section">
          <h4>Rarity Breakdown</h4>
          <div class="breakdown-grid">
            {#each Object.entries(stats.rarityBreakdown) as [rarity, count]}
              <div class="breakdown-item">
                <span class="breakdown-label" style="color: {lootParser.getRarityColor(rarity)}">
                  {lootParser.formatRarity(rarity)}:
                </span>
                <span class="breakdown-value">{count}</span>
              </div>
            {/each}
          </div>
        </div>
      {/if}
    </div>
  {/if}

  <!-- Filter Controls -->
  <div class="filter-controls">
    <div class="filter-row">
      <div class="filter-group">
        <label for="rarity-filter">Rarity:</label>
        <select id="rarity-filter" bind:value={filters.rarity}>
          <option value="">All Rarities</option>
          {#each rarityOptions as rarity}
            <option value={rarity}>{lootParser.formatRarity(rarity)}</option>
          {/each}
        </select>
      </div>

      <div class="filter-group">
        <label for="type-filter">Type:</label>
        <select id="type-filter" bind:value={filters.type}>
          <option value="">All Types</option>
          {#each typeOptions as type}
            <option value={type}>{type.charAt(0).toUpperCase() + type.slice(1)}</option>
          {/each}
        </select>
      </div>

      <div class="filter-group">
        <label for="profession-filter">Profession:</label>
        <select id="profession-filter" bind:value={filters.profession}>
          <option value="">All Professions</option>
          {#each professionOptions as profession}
            <option value={profession}>{profession.charAt(0).toUpperCase() + profession.slice(1)}</option>
          {/each}
        </select>
      </div>

      <div class="filter-group">
        <label for="source-filter">Source:</label>
        <select id="source-filter" bind:value={filters.source}>
          <option value="">All Sources</option>
          {#each sourceOptions as source}
            <option value={source}>{source}</option>
          {/each}
        </select>
      </div>
    </div>

    <div class="filter-row">
      <div class="filter-group search-group">
        <label for="search-filter">Search:</label>
        <input 
          id="search-filter" 
          type="text" 
          placeholder="Search items..."
          bind:value={filters.search}
        />
      </div>

      <button class="btn btn-outline" on:click={clearFilters}>
        Clear Filters
      </button>
    </div>
  </div>

  <!-- Results Count -->
  <div class="results-count">
    Showing {filteredItems.length} of {lootData.heroics?.[heroic]?.items?.length || 0} items
  </div>

  <!-- Loot Table -->
  <div class="loot-table">
    {#if filteredItems.length > 0}
      <div class="table-header">
        <div class="col-item">Item</div>
        <div class="col-rarity">Rarity</div>
        <div class="col-type">Type</div>
        <div class="col-drop">Drop Rate</div>
        <div class="col-profession">Professions</div>
        <div class="col-source">Source</div>
        <div class="col-actions">Actions</div>
      </div>

      <div class="table-body">
        {#each filteredItems as item}
          <div class="table-row" style="border-left: 4px solid {lootParser.getRarityColor(item.rarity)}">
            <div class="col-item">
              <div class="item-info">
                <div class="item-name">{item.name}</div>
                {#if item.use_case}
                  <div class="item-use-case">{item.use_case}</div>
                {/if}
              </div>
            </div>
            
            <div class="col-rarity">
              <span class="rarity-badge" style="color: {lootParser.getRarityColor(item.rarity)}">
                {lootParser.formatRarity(item.rarity)}
              </span>
            </div>
            
            <div class="col-type">
              <span class="type-badge">{item.type.charAt(0).toUpperCase() + item.type.slice(1)}</span>
            </div>
            
            <div class="col-drop">
              {#if item.drop_chance}
                <span class="drop-chance">{lootParser.formatDropChance(item.drop_chance)}</span>
              {:else if item.dropRate}
                <span class="drop-rate">{item.dropRate}%</span>
              {:else}
                <span class="no-data">Unknown</span>
              {/if}
            </div>
            
            <div class="col-profession">
              {#if item.profession_relevance && item.profession_relevance.length > 0}
                <div class="profession-tags">
                  {#each item.profession_relevance as profession}
                    <span class="profession-tag">{profession}</span>
                  {/each}
                </div>
              {:else}
                <span class="no-data">None</span>
              {/if}
            </div>
            
            <div class="col-source">
              <span class="source-badge {item.source?.toLowerCase().replace(/\s+/g, '-')}">
                {item.source || 'Unknown'}
              </span>
            </div>
            
            <div class="col-actions">
              <button class="btn btn-sm btn-outline" on:click={() => console.log('View details:', item)}>
                Details
              </button>
            </div>
          </div>
        {/each}
      </div>
    {:else}
      <div class="no-results">
        <p>No items found matching the current filters.</p>
        <button class="btn btn-outline" on:click={clearFilters}>
          Clear Filters
        </button>
      </div>
    {/if}
  </div>

  <!-- MS11 Sync Modal -->
  {#if showMS11Sync && ms11ExportData}
    <div class="modal-overlay" on:click={() => showMS11Sync = false}>
      <div class="modal-content" on:click|stopPropagation>
        <div class="modal-header">
          <h3>MS11 Sync Export</h3>
          <button class="modal-close" on:click={() => showMS11Sync = false}>&times;</button>
        </div>
        
        <div class="modal-body">
          <p>Export data for MS11 integration (internal use only):</p>
          <div class="export-actions">
            <button class="btn btn-primary" on:click={copyMS11Export}>
              Copy to Clipboard
            </button>
            <button class="btn btn-secondary" on:click={downloadMS11Export}>
              Download JSON
            </button>
          </div>
          
          <div class="export-preview">
            <h4>Preview:</h4>
            <pre>{JSON.stringify(ms11ExportData, null, 2)}</pre>
          </div>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .loot-table-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
  }

  .loot-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 2px solid #e0e0e0;
  }

  .header-actions {
    display: flex;
    gap: 10px;
  }

  .stats-panel {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin-bottom: 20px;
  }

  .stat-item {
    display: flex;
    justify-content: space-between;
    padding: 10px;
    background: white;
    border-radius: 4px;
    border-left: 4px solid #007bff;
  }

  .stat-label {
    font-weight: 600;
    color: #666;
  }

  .stat-value {
    font-weight: bold;
    color: #333;
  }

  .breakdown-section {
    margin-top: 20px;
  }

  .breakdown-section h4 {
    margin-bottom: 10px;
    color: #333;
  }

  .breakdown-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 10px;
  }

  .breakdown-item {
    display: flex;
    justify-content: space-between;
    padding: 8px;
    background: white;
    border-radius: 4px;
  }

  .filter-controls {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
  }

  .filter-row {
    display: flex;
    gap: 15px;
    align-items: end;
    margin-bottom: 15px;
  }

  .filter-row:last-child {
    margin-bottom: 0;
  }

  .filter-group {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }

  .filter-group label {
    font-weight: 600;
    color: #555;
    font-size: 0.9em;
  }

  .filter-group select,
  .filter-group input {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
  }

  .search-group {
    flex: 1;
  }

  .results-count {
    margin-bottom: 15px;
    color: #666;
    font-style: italic;
  }

  .loot-table {
    background: white;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }

  .table-header {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr 1.5fr 1fr 1fr;
    gap: 15px;
    padding: 15px 20px;
    background: #f8f9fa;
    font-weight: 600;
    color: #555;
    border-bottom: 2px solid #e0e0e0;
  }

  .table-body {
    max-height: 600px;
    overflow-y: auto;
  }

  .table-row {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr 1.5fr 1fr 1fr;
    gap: 15px;
    padding: 15px 20px;
    border-bottom: 1px solid #f0f0f0;
    transition: background-color 0.2s;
  }

  .table-row:hover {
    background-color: #f8f9fa;
  }

  .item-info {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }

  .item-name {
    font-weight: 600;
    color: #333;
  }

  .item-use-case {
    font-size: 0.9em;
    color: #666;
    font-style: italic;
  }

  .rarity-badge {
    font-weight: 600;
    padding: 4px 8px;
    border-radius: 4px;
    background: rgba(0,0,0,0.1);
  }

  .type-badge {
    background: #e9ecef;
    color: #495057;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.9em;
  }

  .drop-chance,
  .drop-rate {
    font-weight: 600;
    color: #28a745;
  }

  .no-data {
    color: #999;
    font-style: italic;
  }

  .profession-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }

  .profession-tag {
    background: #007bff;
    color: white;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 0.8em;
  }

  .source-badge {
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 0.9em;
    font-weight: 500;
  }

  .source-badge.swgdb-generated {
    background: #d4edda;
    color: #155724;
  }

  .source-badge.user-submitted {
    background: #d1ecf1;
    color: #0c5460;
  }

  .source-badge.bot-generated {
    background: #fff3cd;
    color: #856404;
  }

  .source-badge.bot-generated-manual {
    background: #f8d7da;
    color: #721c24;
  }

  .no-results {
    text-align: center;
    padding: 40px;
    color: #666;
  }

  .btn {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.2s;
  }

  .btn-primary {
    background: #007bff;
    color: white;
  }

  .btn-primary:hover {
    background: #0056b3;
  }

  .btn-secondary {
    background: #6c757d;
    color: white;
  }

  .btn-secondary:hover {
    background: #545b62;
  }

  .btn-outline {
    background: transparent;
    color: #007bff;
    border: 1px solid #007bff;
  }

  .btn-outline:hover {
    background: #007bff;
    color: white;
  }

  .btn-sm {
    padding: 4px 8px;
    font-size: 12px;
  }

  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .modal-content {
    background: white;
    border-radius: 8px;
    max-width: 800px;
    width: 90%;
    max-height: 80vh;
    overflow-y: auto;
  }

  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px;
    border-bottom: 1px solid #e0e0e0;
  }

  .modal-close {
    background: none;
    border: none;
    font-size: 24px;
    cursor: pointer;
    color: #666;
  }

  .modal-body {
    padding: 20px;
  }

  .export-actions {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
  }

  .export-preview {
    background: #f8f9fa;
    border-radius: 4px;
    padding: 15px;
  }

  .export-preview pre {
    margin: 0;
    white-space: pre-wrap;
    font-size: 12px;
    color: #333;
  }

  @media (max-width: 768px) {
    .table-header,
    .table-row {
      grid-template-columns: 1fr;
      gap: 10px;
    }

    .filter-row {
      flex-direction: column;
      align-items: stretch;
    }

    .header-actions {
      flex-direction: column;
    }
  }
</style> 