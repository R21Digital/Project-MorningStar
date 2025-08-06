<script>
  import { onMount, onDestroy } from 'svelte';
  import { handleError } from '../lib/handle-error.js';
  
  export let fallback = null; // Custom fallback component
  export let showDetails = false; // Show error details to users
  export let autoReport = true; // Auto-report errors
  export let discordPing = false; // Ping Discord for critical errors
  export let logLevel = 'error'; // error, warn, info
  
  let error = null;
  let errorInfo = null;
  let hasError = false;
  let errorId = null;
  let componentStack = [];
  let errorBoundaryId = null;
  
  // Generate unique error boundary ID
  onMount(() => {
    errorBoundaryId = `error-boundary-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  });
  
  // Handle errors from child components
  function handleComponentError(event) {
    const { error: childError, errorInfo: childErrorInfo } = event.detail;
    
    error = childError;
    errorInfo = childErrorInfo;
    hasError = true;
    errorId = `error-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    // Extract component stack if available
    if (childErrorInfo && childErrorInfo.componentStack) {
      componentStack = childErrorInfo.componentStack.split('\n').filter(line => line.trim());
    }
    
    // Report error
    if (autoReport) {
      handleError({
        error: childError,
        errorInfo: childErrorInfo,
        errorId: errorId,
        errorBoundaryId: errorBoundaryId,
        logLevel: logLevel,
        discordPing: discordPing
      });
    }
  }
  
  // Reset error state
  function resetError() {
    error = null;
    errorInfo = null;
    hasError = false;
    errorId = null;
    componentStack = [];
  }
  
  // Copy error details to clipboard
  function copyErrorDetails() {
    const errorDetails = {
      errorId: errorId,
      errorBoundaryId: errorBoundaryId,
      message: error?.message,
      stack: error?.stack,
      componentStack: componentStack,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent
    };
    
    navigator.clipboard.writeText(JSON.stringify(errorDetails, null, 2))
      .then(() => {
        // Show success message
        const copyBtn = document.querySelector('.copy-error-btn');
        if (copyBtn) {
          const originalText = copyBtn.textContent;
          copyBtn.textContent = 'Copied!';
          copyBtn.classList.add('copied');
          setTimeout(() => {
            copyBtn.textContent = originalText;
            copyBtn.classList.remove('copied');
          }, 2000);
        }
      })
      .catch(err => {
        console.error('Failed to copy error details:', err);
      });
  }
  
  // Reload page
  function reloadPage() {
    window.location.reload();
  }
  
  // Go back to previous page
  function goBack() {
    window.history.back();
  }
  
  // Go to home page
  function goHome() {
    window.location.href = '/';
  }
</script>

<svelte:window on:error={handleComponentError} />

{#if hasError}
  <div class="error-boundary" data-error-id={errorId}>
    {#if fallback}
      <svelte:component this={fallback} {error} {errorInfo} {errorId} />
    {:else}
      <div class="error-fallback">
        <div class="error-header">
          <div class="error-icon">⚠️</div>
          <h2>Something went wrong</h2>
          <p class="error-message">
            We encountered an unexpected error. Our team has been notified.
          </p>
        </div>
        
        <div class="error-actions">
          <button class="btn btn-primary" on:click={reloadPage}>
            🔄 Reload Page
          </button>
          <button class="btn btn-secondary" on:click={goBack}>
            ← Go Back
          </button>
          <button class="btn btn-secondary" on:click={goHome}>
            🏠 Go Home
          </button>
        </div>
        
        {#if showDetails}
          <div class="error-details">
            <details>
              <summary>Error Details</summary>
              <div class="error-info">
                <div class="error-id">
                  <strong>Error ID:</strong> {errorId}
                </div>
                <div class="error-message">
                  <strong>Message:</strong> {error?.message || 'Unknown error'}
                </div>
                {#if componentStack.length > 0}
                  <div class="component-stack">
                    <strong>Component Stack:</strong>
                    <ul>
                      {#each componentStack as stack}
                        <li>{stack}</li>
                      {/each}
                    </ul>
                  </div>
                {/if}
                <button class="copy-error-btn" on:click={copyErrorDetails}>
                  📋 Copy Error Details
                </button>
              </div>
            </details>
          </div>
        {/if}
        
        <div class="error-footer">
          <p>
            If this problem persists, please contact support with Error ID: <code>{errorId}</code>
          </p>
        </div>
      </div>
    {/if}
  </div>
{:else}
  <slot />
{/if}

<style>
  .error-boundary {
    padding: 2rem;
    max-width: 600px;
    margin: 0 auto;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }
  
  .error-fallback {
    background: #f8f9fa;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    padding: 2rem;
    text-align: center;
  }
  
  .error-header {
    margin-bottom: 2rem;
  }
  
  .error-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
  }
  
  .error-header h2 {
    color: #dc3545;
    margin: 0 0 0.5rem 0;
    font-size: 1.5rem;
  }
  
  .error-message {
    color: #6c757d;
    margin: 0;
    font-size: 1rem;
  }
  
  .error-actions {
    display: flex;
    gap: 1rem;
    justify-content: center;
    margin-bottom: 2rem;
    flex-wrap: wrap;
  }
  
  .btn {
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 6px;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
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
  
  .error-details {
    margin-top: 2rem;
    text-align: left;
  }
  
  .error-details summary {
    cursor: pointer;
    color: #007bff;
    font-weight: 500;
    margin-bottom: 1rem;
  }
  
  .error-details summary:hover {
    color: #0056b3;
  }
  
  .error-info {
    background: white;
    border: 1px solid #dee2e6;
    border-radius: 6px;
    padding: 1rem;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.85rem;
  }
  
  .error-id {
    margin-bottom: 0.5rem;
  }
  
  .error-message {
    margin-bottom: 0.5rem;
  }
  
  .component-stack {
    margin-bottom: 1rem;
  }
  
  .component-stack ul {
    margin: 0.5rem 0;
    padding-left: 1.5rem;
  }
  
  .component-stack li {
    margin-bottom: 0.25rem;
  }
  
  .copy-error-btn {
    background: #28a745;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.8rem;
    transition: background-color 0.2s ease;
  }
  
  .copy-error-btn:hover {
    background: #218838;
  }
  
  .copy-error-btn.copied {
    background: #6c757d;
  }
  
  .error-footer {
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #dee2e6;
  }
  
  .error-footer p {
    color: #6c757d;
    font-size: 0.9rem;
    margin: 0;
  }
  
  .error-footer code {
    background: #e9ecef;
    padding: 0.2rem 0.4rem;
    border-radius: 3px;
    font-size: 0.8rem;
  }
  
  /* Dark mode support */
  @media (prefers-color-scheme: dark) {
    .error-fallback {
      background: #2d3748;
      border-color: #4a5568;
    }
    
    .error-header h2 {
      color: #f56565;
    }
    
    .error-message {
      color: #a0aec0;
    }
    
    .error-info {
      background: #1a202c;
      border-color: #4a5568;
      color: #e2e8f0;
    }
    
    .error-footer p {
      color: #a0aec0;
    }
    
    .error-footer code {
      background: #4a5568;
      color: #e2e8f0;
    }
  }
  
  /* Mobile responsiveness */
  @media (max-width: 768px) {
    .error-boundary {
      padding: 1rem;
    }
    
    .error-fallback {
      padding: 1.5rem;
    }
    
    .error-actions {
      flex-direction: column;
      align-items: center;
    }
    
    .btn {
      width: 100%;
      max-width: 200px;
      justify-content: center;
    }
  }
</style> 