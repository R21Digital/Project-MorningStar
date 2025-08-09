<script>
  import { onMount } from 'svelte';
  import ComplianceChecker from '../lib/compliance-check.js';

  export let mod = {};
  export let showDetails = false;
  export let onDownload = null;
  export let onViewDetails = null;

  let complianceResult = {};
  let badge = {};
  let expanded = false;
  let showComplianceDetails = false;

  let complianceChecker = new ComplianceChecker();

  $: {
    if (mod) {
      complianceResult = complianceChecker.checkCompliance(mod);
      badge = complianceChecker.getComplianceBadge(complianceResult);
    }
  }

  function toggleExpanded() {
    expanded = !expanded;
  }

  function toggleComplianceDetails() {
    showComplianceDetails = !showComplianceDetails;
  }

  function handleDownload() {
    if (mod.internal_only) {
      alert('This mod is for internal use only and cannot be downloaded.');
      return;
    }
    
    if (onDownload) {
      onDownload(mod);
    } else {
      // Default download behavior
      if (mod.download_url) {
        window.open(mod.download_url, '_blank');
      } else {
        alert(`Downloading ${mod.name}...\n\nNote: This is a demo. In production, this would trigger an actual download.`);
      }
    }
  }

  function handleViewDetails() {
    if (onViewDetails) {
      onViewDetails(mod);
    }
  }

  function formatDate(dateString) {
    if (!dateString) return 'Unknown';
    const date = new Date(dateString);
    return date.toLocaleDateString();
  }

  function formatFileSize(size) {
    if (!size) return 'Unknown';
    return size;
  }

  function getRatingStars(rating) {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
    
    return {
      full: fullStars,
      half: hasHalfStar ? 1 : 0,
      empty: emptyStars
    };
  }
</script>

<div class="mod-card" class:expanded={expanded} class:ms11-derived={complianceResult.ms11Derived}>
  <div class="mod-header">
    <div class="mod-info">
      <h3 class="mod-title">{mod.name}</h3>
      <div class="mod-meta">
        <span class="mod-author">by {mod.author}</span>
        <span class="mod-version">v{mod.version}</span>
        <span class="mod-date">Updated {formatDate(mod.last_updated)}</span>
      </div>
    </div>
    
    <div class="mod-badges">
      <div class="compliance-badge {badge.class}" style="background-color: {badge.color}">
        {badge.icon} {badge.text}
      </div>
      
      {#if complianceResult.ms11Derived}
        <div class="ms11-badge">
          🔒 Internal Only
        </div>
      {/if}
      
      <div class="category-badge">
        {mod.category}
      </div>
    </div>
  </div>

  <div class="mod-content">
    <p class="mod-description">{mod.description}</p>
    
    {#if mod.features && mod.features.length > 0}
      <div class="mod-features">
        <h4>Features:</h4>
        <div class="feature-tags">
          {#each mod.features as feature}
            <span class="feature-tag">{feature}</span>
          {/each}
        </div>
      </div>
    {/if}

    <div class="mod-stats">
      <div class="stat">
        <i class="fas fa-download"></i>
        <span>{mod.downloads?.toLocaleString() || 0} downloads</span>
      </div>
      
      {#if mod.rating > 0}
        <div class="stat">
          <i class="fas fa-star"></i>
          <span class="rating">
            {#each Array(getRatingStars(mod.rating).full) as _}
              <i class="fas fa-star filled"></i>
            {/each}
            {#if getRatingStars(mod.rating).half}
              <i class="fas fa-star-half-alt filled"></i>
            {/if}
            {#each Array(getRatingStars(mod.rating).empty) as _}
              <i class="far fa-star"></i>
            {/each}
            <span class="rating-value">({mod.rating})</span>
          </span>
        </div>
      {/if}
      
      <div class="stat">
        <i class="fas fa-file-archive"></i>
        <span>{formatFileSize(mod.file_size)}</span>
      </div>
    </div>

    {#if complianceResult.issues.length > 0 || complianceResult.warnings.length > 0}
      <div class="compliance-section">
        <button class="compliance-toggle" on:click={toggleComplianceDetails}>
          <i class="fas fa-shield-alt"></i>
          Compliance Details
          <i class="fas fa-chevron-{showComplianceDetails ? 'up' : 'down'}"></i>
        </button>
        
        {#if showComplianceDetails}
          <div class="compliance-details">
            {#if complianceResult.issues.length > 0}
              <div class="compliance-issues">
                <h5>Issues:</h5>
                {#each complianceResult.issues as issue}
                  <div class="issue-item critical">
                    <i class="fas fa-exclamation-triangle"></i>
                    <span>{issue.message}</span>
                  </div>
                {/each}
              </div>
            {/if}
            
            {#if complianceResult.warnings.length > 0}
              <div class="compliance-warnings">
                <h5>Warnings:</h5>
                {#each complianceResult.warnings as warning}
                  <div class="issue-item warning">
                    <i class="fas fa-exclamation-circle"></i>
                    <span>{warning.message}</span>
                  </div>
                {/each}
              </div>
            {/if}
          </div>
        {/if}
      </div>
    {/if}
  </div>

  <div class="mod-actions">
    {#if !mod.internal_only}
      <button class="btn btn-primary" on:click={handleViewDetails}>
        <i class="fas fa-eye"></i> View Details
      </button>
      
      <button class="btn btn-secondary" on:click={handleDownload} disabled={!mod.download_url}>
        <i class="fas fa-download"></i> Download
      </button>
    {:else}
      <button class="btn btn-disabled" disabled>
        <i class="fas fa-lock"></i> Internal Only
      </button>
    {/if}
    
    <button class="btn btn-info" on:click={toggleExpanded}>
      <i class="fas fa-{expanded ? 'compress' : 'expand'}"></i>
      {expanded ? 'Less' : 'More'}
    </button>
  </div>

  {#if expanded}
    <div class="mod-details">
      {#if mod.screenshots && mod.screenshots.length > 0}
        <div class="screenshots-section">
          <h4>Screenshots:</h4>
          <div class="screenshots-grid">
            {#each mod.screenshots as screenshot}
              <img src={screenshot} alt="Screenshot" class="screenshot" />
            {/each}
          </div>
        </div>
      {/if}
      
      {#if mod.dependencies && mod.dependencies.length > 0}
        <div class="dependencies-section">
          <h4>Dependencies:</h4>
          <div class="dependency-tags">
            {#each mod.dependencies as dependency}
              <span class="dependency-tag">{dependency}</span>
            {/each}
          </div>
        </div>
      {/if}
      
      {#if mod.source_url}
        <div class="source-section">
          <h4>Source:</h4>
          <a href={mod.source_url} target="_blank" rel="noopener noreferrer" class="source-link">
            <i class="fab fa-github"></i> View Source
          </a>
        </div>
      {/if}
    </div>
  {/if}
</div>

<style>
  .mod-card {
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    padding: 20px;
    margin-bottom: 20px;
    transition: all 0.3s ease;
    border: 2px solid transparent;
  }

  .mod-card:hover {
    box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
  }

  .mod-card.ms11-derived {
    border-color: #6c757d;
    background: #f8f9fa;
  }

  .mod-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 15px;
  }

  .mod-info {
    flex: 1;
  }

  .mod-title {
    font-size: 1.4rem;
    font-weight: 600;
    color: #333;
    margin: 0 0 5px 0;
  }

  .mod-meta {
    display: flex;
    gap: 15px;
    font-size: 0.9rem;
    color: #666;
  }

  .mod-badges {
    display: flex;
    flex-direction: column;
    gap: 8px;
    align-items: flex-end;
  }

  .compliance-badge {
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    color: white;
    text-align: center;
    white-space: nowrap;
  }

  .ms11-badge {
    background: #6c757d;
    color: white;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.7rem;
    font-weight: 600;
  }

  .category-badge {
    background: #e9ecef;
    color: #495057;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.7rem;
    font-weight: 600;
  }

  .mod-content {
    margin-bottom: 20px;
  }

  .mod-description {
    color: #555;
    line-height: 1.6;
    margin-bottom: 15px;
  }

  .mod-features h4 {
    font-size: 1rem;
    margin-bottom: 8px;
    color: #333;
  }

  .feature-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  .feature-tag {
    background: #f8f9fa;
    color: #495057;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.8rem;
    border: 1px solid #dee2e6;
  }

  .mod-stats {
    display: flex;
    gap: 20px;
    margin: 15px 0;
    padding: 10px 0;
    border-top: 1px solid #eee;
    border-bottom: 1px solid #eee;
  }

  .stat {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 0.9rem;
    color: #666;
  }

  .rating {
    display: flex;
    align-items: center;
    gap: 2px;
  }

  .rating .filled {
    color: #ffc107;
  }

  .rating-value {
    margin-left: 5px;
    color: #666;
  }

  .compliance-section {
    margin: 15px 0;
  }

  .compliance-toggle {
    background: none;
    border: none;
    color: #007bff;
    cursor: pointer;
    padding: 8px 0;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .compliance-toggle:hover {
    color: #0056b3;
  }

  .compliance-details {
    margin-top: 10px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
    border-left: 4px solid #007bff;
  }

  .compliance-issues h5,
  .compliance-warnings h5 {
    margin: 0 0 10px 0;
    font-size: 0.9rem;
    font-weight: 600;
  }

  .compliance-issues {
    margin-bottom: 15px;
  }

  .issue-item {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 5px;
    font-size: 0.85rem;
  }

  .issue-item.critical {
    color: #dc3545;
  }

  .issue-item.warning {
    color: #ffc107;
  }

  .mod-actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
  }

  .btn {
    padding: 8px 16px;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9rem;
    font-weight: 500;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    transition: all 0.2s ease;
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

  .btn-info {
    background: #17a2b8;
    color: white;
  }

  .btn-info:hover {
    background: #138496;
  }

  .btn-disabled {
    background: #6c757d;
    color: white;
    opacity: 0.6;
    cursor: not-allowed;
  }

  .btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .mod-details {
    margin-top: 20px;
    padding-top: 20px;
    border-top: 1px solid #eee;
  }

  .screenshots-section,
  .dependencies-section,
  .source-section {
    margin-bottom: 20px;
  }

  .screenshots-section h4,
  .dependencies-section h4,
  .source-section h4 {
    font-size: 1rem;
    margin-bottom: 10px;
    color: #333;
  }

  .screenshots-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 10px;
  }

  .screenshot {
    width: 100%;
    height: 150px;
    object-fit: cover;
    border-radius: 8px;
    border: 1px solid #dee2e6;
  }

  .dependency-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  .dependency-tag {
    background: #e3f2fd;
    color: #1976d2;
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 0.8rem;
    border: 1px solid #bbdefb;
  }

  .source-link {
    color: #007bff;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }

  .source-link:hover {
    text-decoration: underline;
  }

  @media (max-width: 768px) {
    .mod-header {
      flex-direction: column;
      gap: 10px;
    }

    .mod-badges {
      align-items: flex-start;
    }

    .mod-stats {
      flex-direction: column;
      gap: 10px;
    }

    .mod-actions {
      justify-content: center;
    }

    .screenshots-grid {
      grid-template-columns: 1fr;
    }
  }
</style> 