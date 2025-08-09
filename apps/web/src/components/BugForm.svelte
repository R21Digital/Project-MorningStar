<script>
  /**
   * Bug Report Submission Form Component
   * Comprehensive form for capturing bug reports with validation and submission
   */
  
  import { onMount, createEventDispatcher } from 'svelte';
  import { writable } from 'svelte/store';
  
  // Props
  export let initialData = {};
  export let submitUrl = '/api/submit_bug';
  export let showAdvanced = false;
  export let embedMode = false;
  export let successRedirect = null;
  
  // Event dispatcher
  const dispatch = createEventDispatcher();
  
  // Form state
  let isSubmitting = false;
  let showSuccess = false;
  let showError = false;
  let errorMessage = '';
  let submittedBugId = '';
  
  // Form data
  let formData = {
    title: '',
    description: '',
    module: '',
    severity: 'Medium',
    priority: 'Medium',
    stepsToReproduce: [''],
    expectedBehavior: '',
    actualBehavior: '',
    environment: {
      browser: '',
      os: '',
      version: ''
    },
    reporter: {
      name: '',
      email: ''
    },
    tags: '',
    attachments: [],
    ...initialData
  };
  
  // Configuration
  const modules = [
    'MS11-Core',
    'MS11-Combat',
    'MS11-Heroics',
    'MS11-Discord',
    'SWGDB',
    'Website',
    'API',
    'Database',
    'Infrastructure'
  ];
  
  const severities = [
    { level: 'Critical', description: 'System down, data loss, security breach', color: '#e74c3c' },
    { level: 'High', description: 'Major functionality broken, significant user impact', color: '#e67e22' },
    { level: 'Medium', description: 'Minor functionality issues, workaround available', color: '#f39c12' },
    { level: 'Low', description: 'Cosmetic issues, nice-to-have improvements', color: '#27ae60' }
  ];
  
  const priorities = ['Critical', 'High', 'Medium', 'Low'];
  
  // Reactive variables
  $: isFormValid = validateForm();
  $: currentSeverity = severities.find(s => s.level === formData.severity);
  $: characterCount = formData.description.length;
  $: titleCount = formData.title.length;
  
  onMount(() => {
    detectEnvironment();
    loadDraftFromStorage();
    
    // Auto-save draft periodically
    const saveInterval = setInterval(saveDraftToStorage, 30000);
    
    return () => {
      clearInterval(saveInterval);
    };
  });
  
  // Functions
  function validateForm() {
    return formData.title.trim().length >= 5 &&
           formData.description.trim().length >= 20 &&
           formData.module &&
           formData.reporter.name.trim().length >= 2 &&
           formData.reporter.email.includes('@');
  }
  
  function detectEnvironment() {
    if (typeof window !== 'undefined') {
      formData.environment.browser = detectBrowser();
      formData.environment.os = detectOS();
      formData.environment.version = 'v2.4.1'; // Default version
    }
  }
  
  function detectBrowser() {
    const userAgent = navigator.userAgent;
    if (userAgent.includes('Chrome')) return 'Chrome ' + userAgent.match(/Chrome\/([0-9.]+)/)?.[1];
    if (userAgent.includes('Firefox')) return 'Firefox ' + userAgent.match(/Firefox\/([0-9.]+)/)?.[1];
    if (userAgent.includes('Safari')) return 'Safari ' + userAgent.match(/Version\/([0-9.]+)/)?.[1];
    if (userAgent.includes('Edge')) return 'Edge ' + userAgent.match(/Edge\/([0-9.]+)/)?.[1];
    return 'Unknown';
  }
  
  function detectOS() {
    const platform = navigator.platform;
    const userAgent = navigator.userAgent;
    
    if (platform.includes('Win')) return 'Windows';
    if (platform.includes('Mac')) return 'macOS';
    if (platform.includes('Linux')) return 'Linux';
    if (userAgent.includes('Android')) return 'Android';
    if (userAgent.includes('iPhone') || userAgent.includes('iPad')) return 'iOS';
    return 'Unknown';
  }
  
  function addReproductionStep() {
    formData.stepsToReproduce = [...formData.stepsToReproduce, ''];
  }
  
  function removeReproductionStep(index) {
    if (formData.stepsToReproduce.length > 1) {
      formData.stepsToReproduce = formData.stepsToReproduce.filter((_, i) => i !== index);
    }
  }
  
  function handleFileUpload(event) {
    const files = Array.from(event.target.files);
    const maxSize = 5 * 1024 * 1024; // 5MB
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'text/plain', 'application/pdf'];
    
    const validFiles = files.filter(file => {
      if (file.size > maxSize) {
        showErrorMessage(`File ${file.name} is too large. Maximum size is 5MB.`);
        return false;
      }
      if (!allowedTypes.includes(file.type)) {
        showErrorMessage(`File ${file.name} has unsupported format.`);
        return false;
      }
      return true;
    });
    
    // Convert to base64 for storage (in real implementation, would upload to server)
    validFiles.forEach(file => {
      const reader = new FileReader();
      reader.onload = (e) => {
        formData.attachments = [...formData.attachments, {
          name: file.name,
          type: file.type,
          size: file.size,
          data: e.target.result
        }];
      };
      reader.readAsDataURL(file);
    });
  }
  
  function removeAttachment(index) {
    formData.attachments = formData.attachments.filter((_, i) => i !== index);
  }
  
  function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
  
  function saveDraftToStorage() {
    if (typeof localStorage !== 'undefined' && formData.title.trim()) {
      localStorage.setItem('bugReportDraft', JSON.stringify(formData));
    }
  }
  
  function loadDraftFromStorage() {
    if (typeof localStorage !== 'undefined') {
      const draft = localStorage.getItem('bugReportDraft');
      if (draft) {
        try {
          const draftData = JSON.parse(draft);
          // Only load if form is empty
          if (!formData.title && !formData.description) {
            formData = { ...formData, ...draftData };
          }
        } catch (e) {
          console.warn('Failed to load draft from storage:', e);
        }
      }
    }
  }
  
  function clearDraft() {
    if (typeof localStorage !== 'undefined') {
      localStorage.removeItem('bugReportDraft');
    }
  }
  
  function resetForm() {
    formData = {
      title: '',
      description: '',
      module: '',
      severity: 'Medium',
      priority: 'Medium',
      stepsToReproduce: [''],
      expectedBehavior: '',
      actualBehavior: '',
      environment: {
        browser: '',
        os: '',
        version: ''
      },
      reporter: {
        name: '',
        email: ''
      },
      tags: '',
      attachments: []
    };
    detectEnvironment();
    clearDraft();
  }
  
  function showErrorMessage(message) {
    errorMessage = message;
    showError = true;
    setTimeout(() => {
      showError = false;
    }, 5000);
  }
  
  async function submitBug() {
    if (!isFormValid || isSubmitting) return;
    
    isSubmitting = true;
    showError = false;
    
    try {
      // Prepare submission data
      const submissionData = {
        ...formData,
        tags: formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag),
        stepsToReproduce: formData.stepsToReproduce.filter(step => step.trim()),
        timestamp: new Date().toISOString()
      };
      
      const response = await fetch(submitUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(submissionData)
      });
      
      const result = await response.json();
      
      if (response.ok) {
        submittedBugId = result.bugId;
        showSuccess = true;
        clearDraft();
        
        dispatch('success', {
          bugId: result.bugId,
          data: submissionData
        });
        
        if (successRedirect) {
          setTimeout(() => {
            window.location.href = successRedirect.replace('{bugId}', result.bugId);
          }, 2000);
        }
      } else {
        throw new Error(result.message || 'Failed to submit bug report');
      }
    } catch (error) {
      console.error('Bug submission error:', error);
      showErrorMessage(error.message || 'Failed to submit bug report. Please try again.');
      
      dispatch('error', {
        error: error.message,
        data: formData
      });
    } finally {
      isSubmitting = false;
    }
  }
  
  function previewSubmission() {
    dispatch('preview', { data: formData });
  }
</script>

<div class="bug-form-container" class:embed-mode={embedMode}>
  <!-- Success Message -->
  {#if showSuccess}
    <div class="success-message">
      <div class="success-icon">✅</div>
      <div class="success-content">
        <h3>Bug Report Submitted Successfully!</h3>
        <p>Your bug report has been assigned ID: <strong>{submittedBugId}</strong></p>
        <p>You will receive email updates as the issue is processed.</p>
      </div>
    </div>
  {:else}
    <!-- Error Message -->
    {#if showError}
      <div class="error-message">
        <div class="error-icon">❌</div>
        <div class="error-content">
          <strong>Submission Failed</strong>
          <p>{errorMessage}</p>
        </div>
      </div>
    {/if}
    
    <!-- Form -->
    <form class="bug-form" on:submit|preventDefault={submitBug}>
      <!-- Form Header -->
      <div class="form-header">
        <h2>🐛 Submit Bug Report</h2>
        <p>Help us improve by reporting issues you've encountered. Please provide as much detail as possible.</p>
      </div>
      
      <!-- Basic Information -->
      <div class="form-section">
        <h3>Basic Information</h3>
        
        <!-- Title -->
        <div class="form-group">
          <label for="title" class="required">Bug Title</label>
          <input 
            type="text" 
            id="title" 
            bind:value={formData.title}
            placeholder="Brief, descriptive title of the issue"
            maxlength="200"
            required
          >
          <div class="form-hint">
            {titleCount}/200 characters • Be specific and descriptive
          </div>
        </div>
        
        <!-- Module and Severity -->
        <div class="form-row">
          <div class="form-group">
            <label for="module" class="required">Module/Component</label>
            <select id="module" bind:value={formData.module} required>
              <option value="">Select module...</option>
              {#each modules as module}
                <option value={module}>{module}</option>
              {/each}
            </select>
          </div>
          
          <div class="form-group">
            <label for="severity" class="required">Severity</label>
            <select id="severity" bind:value={formData.severity} required>
              {#each severities as severity}
                <option value={severity.level}>{severity.level}</option>
              {/each}
            </select>
            {#if currentSeverity}
              <div class="severity-description" style="color: {currentSeverity.color}">
                {currentSeverity.description}
              </div>
            {/if}
          </div>
        </div>
        
        <!-- Description -->
        <div class="form-group">
          <label for="description" class="required">Detailed Description</label>
          <textarea 
            id="description" 
            bind:value={formData.description}
            placeholder="Describe the bug in detail. What happened? When did it occur? What were you trying to do?"
            rows="6"
            maxlength="2000"
            required
          ></textarea>
          <div class="form-hint">
            {characterCount}/2000 characters • Include context, frequency, and impact
          </div>
        </div>
      </div>
      
      <!-- Reproduction Steps -->
      <div class="form-section">
        <h3>Reproduction Information</h3>
        
        <!-- Steps to Reproduce -->
        <div class="form-group">
          <label>Steps to Reproduce</label>
          <div class="steps-container">
            {#each formData.stepsToReproduce as step, index}
              <div class="step-input">
                <span class="step-number">{index + 1}.</span>
                <input 
                  type="text" 
                  bind:value={formData.stepsToReproduce[index]}
                  placeholder="Describe step {index + 1}"
                >
                {#if formData.stepsToReproduce.length > 1}
                  <button 
                    type="button" 
                    class="remove-step-btn"
                    on:click={() => removeReproductionStep(index)}
                  >
                    ×
                  </button>
                {/if}
              </div>
            {/each}
            <button type="button" class="add-step-btn" on:click={addReproductionStep}>
              + Add Step
            </button>
          </div>
        </div>
        
        <!-- Expected vs Actual Behavior -->
        <div class="form-row">
          <div class="form-group">
            <label for="expected">Expected Behavior</label>
            <textarea 
              id="expected" 
              bind:value={formData.expectedBehavior}
              placeholder="What should have happened?"
              rows="3"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label for="actual">Actual Behavior</label>
            <textarea 
              id="actual" 
              bind:value={formData.actualBehavior}
              placeholder="What actually happened?"
              rows="3"
            ></textarea>
          </div>
        </div>
      </div>
      
      <!-- Environment Information -->
      <div class="form-section">
        <h3>Environment Information</h3>
        <div class="form-row">
          <div class="form-group">
            <label for="browser">Browser</label>
            <input 
              type="text" 
              id="browser" 
              bind:value={formData.environment.browser}
              placeholder="Chrome 131.0, Firefox 124.0, etc."
            >
          </div>
          
          <div class="form-group">
            <label for="os">Operating System</label>
            <input 
              type="text" 
              id="os" 
              bind:value={formData.environment.os}
              placeholder="Windows 11, macOS 14.2, Ubuntu 22.04, etc."
            >
          </div>
          
          <div class="form-group">
            <label for="version">Application Version</label>
            <input 
              type="text" 
              id="version" 
              bind:value={formData.environment.version}
              placeholder="v2.4.1"
            >
          </div>
        </div>
      </div>
      
      <!-- Reporter Information -->
      <div class="form-section">
        <h3>Contact Information</h3>
        <div class="form-row">
          <div class="form-group">
            <label for="reporterName" class="required">Your Name</label>
            <input 
              type="text" 
              id="reporterName" 
              bind:value={formData.reporter.name}
              placeholder="Full name or username"
              required
            >
          </div>
          
          <div class="form-group">
            <label for="reporterEmail" class="required">Email Address</label>
            <input 
              type="email" 
              id="reporterEmail" 
              bind:value={formData.reporter.email}
              placeholder="your.email@example.com"
              required
            >
            <div class="form-hint">We'll use this to send updates on your bug report</div>
          </div>
        </div>
      </div>
      
      <!-- Advanced Options -->
      {#if showAdvanced}
        <div class="form-section">
          <h3>Additional Information</h3>
          
          <!-- Tags -->
          <div class="form-group">
            <label for="tags">Tags</label>
            <input 
              type="text" 
              id="tags" 
              bind:value={formData.tags}
              placeholder="ui, performance, mobile (comma-separated)"
            >
            <div class="form-hint">Optional tags to help categorize the issue</div>
          </div>
          
          <!-- Priority -->
          <div class="form-group">
            <label for="priority">Priority</label>
            <select id="priority" bind:value={formData.priority}>
              {#each priorities as priority}
                <option value={priority}>{priority}</option>
              {/each}
            </select>
          </div>
        </div>
      {/if}
      
      <!-- File Attachments -->
      <div class="form-section">
        <h3>Attachments</h3>
        <div class="form-group">
          <label for="attachments">Screenshots, Logs, or Files</label>
          <input 
            type="file" 
            id="attachments" 
            multiple
            accept="image/*,.txt,.pdf,.log"
            on:change={handleFileUpload}
          >
          <div class="form-hint">
            Supported: Images (JPEG, PNG, GIF), Text files, PDFs • Max 5MB per file
          </div>
          
          <!-- Attachment Preview -->
          {#if formData.attachments.length > 0}
            <div class="attachments-preview">
              {#each formData.attachments as attachment, index}
                <div class="attachment-item">
                  <div class="attachment-info">
                    <span class="attachment-name">{attachment.name}</span>
                    <span class="attachment-size">{formatFileSize(attachment.size)}</span>
                  </div>
                  <button 
                    type="button" 
                    class="remove-attachment-btn"
                    on:click={() => removeAttachment(index)}
                  >
                    ×
                  </button>
                </div>
              {/each}
            </div>
          {/if}
        </div>
      </div>
      
      <!-- Form Actions -->
      <div class="form-actions">
        <button type="button" class="btn btn-secondary" on:click={resetForm}>
          Reset Form
        </button>
        
        <button type="button" class="btn btn-secondary" on:click={previewSubmission}>
          Preview
        </button>
        
        <button 
          type="submit" 
          class="btn btn-primary"
          disabled={!isFormValid || isSubmitting}
        >
          {#if isSubmitting}
            <span class="spinner"></span>
            Submitting...
          {:else}
            Submit Bug Report
          {/if}
        </button>
      </div>
      
      <!-- Form Status -->
      <div class="form-status">
        {#if !isFormValid}
          <div class="validation-message">
            Please fill in all required fields to submit the bug report.
          </div>
        {/if}
      </div>
    </form>
  {/if}
</div>

<style>
  .bug-form-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }
  
  .embed-mode {
    max-width: 100%;
    padding: 15px;
  }
  
  .success-message,
  .error-message {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
  }
  
  .success-message {
    background: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
  }
  
  .error-message {
    background: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
  }
  
  .success-icon,
  .error-icon {
    font-size: 1.5em;
  }
  
  .success-content h3,
  .error-content strong {
    margin: 0 0 8px 0;
    font-size: 1.1em;
  }
  
  .success-content p,
  .error-content p {
    margin: 0;
  }
  
  .bug-form {
    background: white;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    overflow: hidden;
  }
  
  .form-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 30px;
    text-align: center;
  }
  
  .form-header h2 {
    margin: 0 0 10px 0;
    font-size: 2em;
    font-weight: 700;
  }
  
  .form-header p {
    margin: 0;
    opacity: 0.9;
    font-size: 1.1em;
  }
  
  .form-section {
    padding: 25px 30px;
    border-bottom: 1px solid #e9ecef;
  }
  
  .form-section:last-child {
    border-bottom: none;
  }
  
  .form-section h3 {
    margin: 0 0 20px 0;
    color: #333;
    font-size: 1.3em;
    font-weight: 600;
    border-bottom: 2px solid #667eea;
    padding-bottom: 8px;
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
  }
  
  @media (max-width: 768px) {
    .form-row {
      grid-template-columns: 1fr;
    }
  }
  
  label {
    display: block;
    font-weight: 600;
    margin-bottom: 8px;
    color: #333;
  }
  
  label.required::after {
    content: " *";
    color: #e74c3c;
  }
  
  input[type="text"],
  input[type="email"],
  select,
  textarea {
    width: 100%;
    padding: 12px 15px;
    border: 2px solid #e1e8ed;
    border-radius: 6px;
    font-size: 14px;
    font-family: inherit;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
    box-sizing: border-box;
  }
  
  input[type="text"]:focus,
  input[type="email"]:focus,
  select:focus,
  textarea:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
  
  textarea {
    resize: vertical;
    min-height: 80px;
  }
  
  .form-hint {
    font-size: 0.9em;
    color: #666;
    margin-top: 5px;
  }
  
  .severity-description {
    font-size: 0.9em;
    margin-top: 5px;
    font-style: italic;
  }
  
  .steps-container {
    border: 1px solid #e1e8ed;
    border-radius: 6px;
    padding: 15px;
    background: #f8f9fa;
  }
  
  .step-input {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
  }
  
  .step-input:last-child {
    margin-bottom: 0;
  }
  
  .step-number {
    font-weight: 600;
    color: #667eea;
    min-width: 25px;
  }
  
  .step-input input {
    flex: 1;
    margin: 0;
  }
  
  .remove-step-btn {
    background: #e74c3c;
    color: white;
    border: none;
    border-radius: 50%;
    width: 25px;
    height: 25px;
    font-size: 16px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .add-step-btn {
    background: #667eea;
    color: white;
    border: none;
    padding: 8px 15px;
    border-radius: 4px;
    font-size: 0.9em;
    cursor: pointer;
    margin-top: 10px;
  }
  
  .add-step-btn:hover {
    background: #5a67d8;
  }
  
  .attachments-preview {
    margin-top: 15px;
    border: 1px solid #e1e8ed;
    border-radius: 6px;
    padding: 10px;
    background: #f8f9fa;
  }
  
  .attachment-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px;
    background: white;
    border-radius: 4px;
    margin-bottom: 8px;
  }
  
  .attachment-item:last-child {
    margin-bottom: 0;
  }
  
  .attachment-info {
    display: flex;
    flex-direction: column;
  }
  
  .attachment-name {
    font-weight: 500;
    color: #333;
  }
  
  .attachment-size {
    font-size: 0.8em;
    color: #666;
  }
  
  .remove-attachment-btn {
    background: #e74c3c;
    color: white;
    border: none;
    border-radius: 50%;
    width: 20px;
    height: 20px;
    font-size: 14px;
    cursor: pointer;
  }
  
  .form-actions {
    padding: 25px 30px;
    background: #f8f9fa;
    display: flex;
    gap: 15px;
    justify-content: flex-end;
    border-top: 1px solid #e9ecef;
  }
  
  @media (max-width: 768px) {
    .form-actions {
      flex-direction: column;
    }
  }
  
  .btn {
    padding: 12px 24px;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    font-size: 14px;
  }
  
  .btn-primary {
    background: #667eea;
    color: white;
  }
  
  .btn-primary:hover:not(:disabled) {
    background: #5a67d8;
  }
  
  .btn-primary:disabled {
    background: #a0aec0;
    cursor: not-allowed;
  }
  
  .btn-secondary {
    background: #e2e8f0;
    color: #4a5568;
  }
  
  .btn-secondary:hover {
    background: #cbd5e0;
  }
  
  .spinner {
    width: 16px;
    height: 16px;
    border: 2px solid transparent;
    border-top: 2px solid currentColor;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
  
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
  
  .form-status {
    padding: 15px 30px;
    background: #fff3cd;
    border-top: 1px solid #ffeaa7;
  }
  
  .validation-message {
    color: #856404;
    font-size: 0.9em;
    text-align: center;
  }
  
  input[type="file"] {
    padding: 8px;
    border: 2px dashed #e1e8ed;
    background: #f8f9fa;
  }
  
  input[type="file"]:focus {
    border-color: #667eea;
    border-style: solid;
  }
</style>