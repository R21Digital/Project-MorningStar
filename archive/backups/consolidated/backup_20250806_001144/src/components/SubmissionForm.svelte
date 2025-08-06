<script>
  /**
   * Universal Submission Form Component
   * Handles guide, mod, loot data, and bug report submissions with validation
   */
  
  import { onMount, createEventDispatcher } from 'svelte';
  import { writable } from 'svelte/store';
  
  // Props
  export let submissionType = 'guide'; // 'guide', 'mod', 'loot', 'bug'
  export let submitUrl = '/api/submit';
  export let allowedFileTypes = ['md', 'txt', 'zip', 'rar', '7z', 'png', 'jpg', 'jpeg', 'gif'];
  export let maxFileSize = 50 * 1024 * 1024; // 50MB default
  export let showPreview = true;
  export let enableMarkdown = true;
  
  // Event dispatcher
  const dispatch = createEventDispatcher();
  
  // Form state
  let isSubmitting = false;
  let showSuccess = false;
  let showError = false;
  let errorMessage = '';
  let submissionId = '';
  let markdownPreview = '';
  
  // Form data
  let formData = {
    type: submissionType,
    title: '',
    description: '',
    content: '',
    tags: [],
    category: '',
    difficulty: 'Medium',
    estimatedTime: '',
    version: '',
    author: {
      name: '',
      discordId: '',
      email: '',
      preferredContact: 'discord'
    },
    metadata: {
      gameVersion: 'NGE',
      profession: '',
      location: '',
      requirements: []
    },
    files: [],
    disclaimer: false,
    termsAccepted: false,
    allowUpdates: true,
    featured: false
  };
  
  // Configuration
  const submissionTypes = {
    guide: {
      title: 'Submit a Guide',
      icon: '📚',
      description: 'Share your knowledge with the community',
      categories: ['Profession', 'Combat', 'Crafting', 'Trading', 'PvP', 'Questing', 'General'],
      requiredFields: ['title', 'description', 'content', 'category'],
      maxContentLength: 50000,
      allowFiles: true,
      fileTypes: ['md', 'txt', 'png', 'jpg', 'jpeg', 'gif', 'mp4', 'webm']
    },
    mod: {
      title: 'Upload a Mod',
      icon: '⚙️',
      description: 'Share your modifications with the community',
      categories: ['UI', 'Gameplay', 'Quality of Life', 'Visual', 'Audio', 'Performance', 'Utility'],
      requiredFields: ['title', 'description', 'version', 'files'],
      maxContentLength: 20000,
      allowFiles: true,
      fileTypes: ['zip', 'rar', '7z', 'png', 'jpg', 'jpeg', 'gif', 'txt', 'md']
    },
    loot: {
      title: 'Report Loot Data',
      icon: '💎',
      description: 'Contribute to the loot database',
      categories: ['Creature Loot', 'Quest Rewards', 'Vendor Items', 'Rare Drops', 'Profession Items'],
      requiredFields: ['title', 'description', 'location', 'profession'],
      maxContentLength: 10000,
      allowFiles: true,
      fileTypes: ['png', 'jpg', 'jpeg', 'gif', 'txt', 'csv', 'json']
    },
    bug: {
      title: 'Report a Bug',
      icon: '🐛',
      description: 'Help improve the platform',
      categories: ['Website', 'Database', 'Mod Portal', 'Guides', 'Performance', 'Mobile'],
      requiredFields: ['title', 'description', 'category'],
      maxContentLength: 5000,
      allowFiles: true,
      fileTypes: ['png', 'jpg', 'jpeg', 'gif', 'txt', 'log']
    }
  };
  
  const difficultyLevels = ['Beginner', 'Intermediate', 'Advanced', 'Expert'];
  const gameVersions = ['Pre-CU', 'CU', 'NGE', 'JTL', 'ROTW', 'Legends'];
  const contactMethods = ['discord', 'email', 'both'];
  
  // Reactive variables
  $: currentConfig = submissionTypes[submissionType] || submissionTypes.guide;
  $: isFormValid = validateForm();
  $: characterCount = formData.content.length;
  $: selectedTags = formData.tags;
  $: fileCount = formData.files.length;
  
  onMount(() => {
    formData.type = submissionType;
    setupMarkdownPreview();
    loadDraftFromStorage();
    
    // Auto-save draft periodically
    const saveInterval = setInterval(saveDraftToStorage, 30000);
    
    return () => {
      clearInterval(saveInterval);
    };
  });
  
  // Functions
  function validateForm() {
    const required = currentConfig.requiredFields;
    
    for (const field of required) {
      if (field === 'files') {
        if (formData.files.length === 0) return false;
      } else if (field.includes('.')) {
        const [parent, child] = field.split('.');
        if (!formData[parent] || !formData[parent][child] || formData[parent][child].trim().length === 0) {
          return false;
        }
      } else {
        if (!formData[field] || (typeof formData[field] === 'string' && formData[field].trim().length === 0)) {
          return false;
        }
      }
    }
    
    // Check required checkboxes
    if (submissionType === 'mod' && !formData.disclaimer) return false;
    if (!formData.termsAccepted) return false;
    
    // Content length validation
    if (formData.content && formData.content.length > currentConfig.maxContentLength) return false;
    
    return true;
  }
  
  function setupMarkdownPreview() {
    if (!enableMarkdown) return;
    
    // Simple markdown preview (would use marked.js in production)
    const updatePreview = () => {
      if (!formData.content) {
        markdownPreview = '';
        return;
      }
      
      let html = formData.content
        .replace(/^### (.*$)/gim, '<h3>$1</h3>')
        .replace(/^## (.*$)/gim, '<h2>$1</h2>')
        .replace(/^# (.*$)/gim, '<h1>$1</h1>')
        .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
        .replace(/\*(.*)\*/gim, '<em>$1</em>')
        .replace(/!\[([^\]]*)\]\(([^\)]*)\)/gim, '<img alt="$1" src="$2" style="max-width: 100%; height: auto;">')
        .replace(/\[([^\]]*)\]\(([^\)]*)\)/gim, '<a href="$2" target="_blank">$1</a>')
        .replace(/`([^`]*)`/gim, '<code>$1</code>')
        .replace(/\n\n/gim, '</p><p>')
        .replace(/\n/gim, '<br>');
      
      markdownPreview = '<p>' + html + '</p>';
    };
    
    // Watch for content changes
    $: formData.content, updatePreview();
  }
  
  function addTag(tag) {
    if (tag && !formData.tags.includes(tag)) {
      formData.tags = [...formData.tags, tag.trim()];
    }
  }
  
  function removeTag(index) {
    formData.tags = formData.tags.filter((_, i) => i !== index);
  }
  
  function handleTagInput(event) {
    if (event.key === 'Enter' || event.key === ',') {
      event.preventDefault();
      const tag = event.target.value.trim();
      if (tag) {
        addTag(tag);
        event.target.value = '';
      }
    }
  }
  
  function handleFileUpload(event) {
    const files = Array.from(event.target.files);
    const allowedTypes = currentConfig.fileTypes;
    const maxSize = maxFileSize;
    
    const validFiles = files.filter(file => {
      const extension = file.name.split('.').pop().toLowerCase();
      
      if (!allowedTypes.includes(extension)) {
        showErrorMessage(`File ${file.name} has unsupported format. Allowed: ${allowedTypes.join(', ')}`);
        return false;
      }
      
      if (file.size > maxSize) {
        showErrorMessage(`File ${file.name} is too large. Maximum size is ${formatFileSize(maxSize)}.`);
        return false;
      }
      
      return true;
    });
    
    // Convert to base64 for storage (in production, would upload to server)
    validFiles.forEach(file => {
      const reader = new FileReader();
      reader.onload = (e) => {
        formData.files = [...formData.files, {
          name: file.name,
          type: file.type,
          size: file.size,
          data: e.target.result,
          uploadedAt: new Date().toISOString()
        }];
      };
      reader.readAsDataURL(file);
    });
  }
  
  function removeFile(index) {
    formData.files = formData.files.filter((_, i) => i !== index);
  }
  
  function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
  
  function addRequirement() {
    formData.metadata.requirements = [...formData.metadata.requirements, ''];
  }
  
  function removeRequirement(index) {
    formData.metadata.requirements = formData.metadata.requirements.filter((_, i) => i !== index);
  }
  
  function saveDraftToStorage() {
    if (typeof localStorage !== 'undefined' && formData.title.trim()) {
      localStorage.setItem(`${submissionType}Draft`, JSON.stringify(formData));
    }
  }
  
  function loadDraftFromStorage() {
    if (typeof localStorage !== 'undefined') {
      const draft = localStorage.getItem(`${submissionType}Draft`);
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
      localStorage.removeItem(`${submissionType}Draft`);
    }
  }
  
  function resetForm() {
    formData = {
      type: submissionType,
      title: '',
      description: '',
      content: '',
      tags: [],
      category: '',
      difficulty: 'Medium',
      estimatedTime: '',
      version: '',
      author: {
        name: '',
        discordId: '',
        email: '',
        preferredContact: 'discord'
      },
      metadata: {
        gameVersion: 'NGE',
        profession: '',
        location: '',
        requirements: []
      },
      files: [],
      disclaimer: false,
      termsAccepted: false,
      allowUpdates: true,
      featured: false
    };
    clearDraft();
    markdownPreview = '';
  }
  
  function showErrorMessage(message) {
    errorMessage = message;
    showError = true;
    setTimeout(() => {
      showError = false;
    }, 5000);
  }
  
  function previewSubmission() {
    dispatch('preview', { data: formData, config: currentConfig });
  }
  
  async function submitForm() {
    if (!isFormValid || isSubmitting) return;
    
    isSubmitting = true;
    showError = false;
    
    try {
      // Prepare submission data
      const submissionData = {
        ...formData,
        submittedAt: new Date().toISOString(),
        userAgent: navigator.userAgent,
        formVersion: '2.0'
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
        submissionId = result.submissionId;
        showSuccess = true;
        clearDraft();
        
        dispatch('success', {
          submissionId: result.submissionId,
          data: submissionData,
          type: submissionType
        });
        
        // Analytics tracking
        if (typeof gtag !== 'undefined') {
          gtag('event', 'submission_success', {
            'submission_type': submissionType,
            'submission_id': result.submissionId
          });
        }
      } else {
        throw new Error(result.message || 'Failed to submit');
      }
    } catch (error) {
      console.error('Submission error:', error);
      showErrorMessage(error.message || 'Failed to submit. Please try again.');
      
      dispatch('error', {
        error: error.message,
        data: formData,
        type: submissionType
      });
    } finally {
      isSubmitting = false;
    }
  }
</script>

<div class="submission-form-container">
  <!-- Success Message -->
  {#if showSuccess}
    <div class="success-message">
      <div class="success-icon">{currentConfig.icon}</div>
      <div class="success-content">
        <h3>{currentConfig.title} Submitted Successfully!</h3>
        <p>Your submission has been received with ID: <strong>{submissionId}</strong></p>
        <p>We'll review it and get back to you within 24-48 hours.</p>
        {#if formData.author.preferredContact === 'discord' && formData.author.discordId}
          <p>We'll contact you on Discord: <strong>{formData.author.discordId}</strong></p>
        {:else if formData.author.email}
          <p>We'll email you at: <strong>{formData.author.email}</strong></p>
        {/if}
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
    <form class="submission-form" on:submit|preventDefault={submitForm}>
      <!-- Form Header -->
      <div class="form-header">
        <div class="form-icon">{currentConfig.icon}</div>
        <h2>{currentConfig.title}</h2>
        <p>{currentConfig.description}</p>
      </div>
      
      <!-- Basic Information -->
      <div class="form-section">
        <h3>Basic Information</h3>
        
        <!-- Title -->
        <div class="form-group">
          <label for="title" class="required">Title</label>
          <input 
            type="text" 
            id="title" 
            bind:value={formData.title}
            placeholder="Enter a clear, descriptive title"
            maxlength="200"
            required
          >
          <div class="form-hint">
            {formData.title.length}/200 characters
          </div>
        </div>
        
        <!-- Category and Difficulty -->
        <div class="form-row">
          <div class="form-group">
            <label for="category" class="required">Category</label>
            <select id="category" bind:value={formData.category} required>
              <option value="">Select category...</option>
              {#each currentConfig.categories as category}
                <option value={category}>{category}</option>
              {/each}
            </select>
          </div>
          
          {#if submissionType === 'guide'}
            <div class="form-group">
              <label for="difficulty">Difficulty Level</label>
              <select id="difficulty" bind:value={formData.difficulty}>
                {#each difficultyLevels as level}
                  <option value={level}>{level}</option>
                {/each}
              </select>
            </div>
          {/if}
          
          {#if submissionType === 'mod'}
            <div class="form-group">
              <label for="version" class="required">Version</label>
              <input 
                type="text" 
                id="version" 
                bind:value={formData.version}
                placeholder="e.g., 1.0.0"
                required
              >
            </div>
          {/if}
        </div>
        
        <!-- Description -->
        <div class="form-group">
          <label for="description" class="required">Description</label>
          <textarea 
            id="description" 
            bind:value={formData.description}
            placeholder="Provide a clear description of your {submissionType}"
            rows="4"
            maxlength="1000"
            required
          ></textarea>
          <div class="form-hint">
            {formData.description.length}/1000 characters
          </div>
        </div>
      </div>
      
      <!-- Content Section -->
      {#if submissionType === 'guide' || submissionType === 'mod'}
        <div class="form-section">
          <h3>Content</h3>
          
          <div class="content-editor">
            <div class="editor-tabs">
              <button type="button" class="tab-btn active" data-tab="edit">
                ✏️ Edit
              </button>
              {#if enableMarkdown && showPreview}
                <button type="button" class="tab-btn" data-tab="preview">
                  👁️ Preview
                </button>
              {/if}
            </div>
            
            <div class="tab-content">
              <div class="tab-pane active" id="edit-tab">
                <textarea 
                  id="content" 
                  bind:value={formData.content}
                  placeholder={submissionType === 'guide' ? 'Write your guide content here. Markdown formatting is supported.' : 'Describe your mod, installation instructions, and usage.'}
                  rows="15"
                  maxlength={currentConfig.maxContentLength}
                  class="content-textarea"
                ></textarea>
                <div class="form-hint">
                  {characterCount}/{currentConfig.maxContentLength} characters
                  {#if enableMarkdown}
                    • Markdown formatting supported
                  {/if}
                </div>
              </div>
              
              {#if enableMarkdown && showPreview}
                <div class="tab-pane" id="preview-tab">
                  <div class="markdown-preview">
                    {#if markdownPreview}
                      {@html markdownPreview}
                    {:else}
                      <p class="preview-placeholder">Content preview will appear here...</p>
                    {/if}
                  </div>
                </div>
              {/if}
            </div>
          </div>
        </div>
      {/if}
      
      <!-- Metadata Section -->
      <div class="form-section">
        <h3>Additional Information</h3>
        
        <div class="form-row">
          <div class="form-group">
            <label for="gameVersion">Game Version</label>
            <select id="gameVersion" bind:value={formData.metadata.gameVersion}>
              {#each gameVersions as version}
                <option value={version}>{version}</option>
              {/each}
            </select>
          </div>
          
          {#if submissionType === 'guide' || submissionType === 'loot'}
            <div class="form-group">
              <label for="profession">Related Profession</label>
              <input 
                type="text" 
                id="profession" 
                bind:value={formData.metadata.profession}
                placeholder="e.g., Jedi, Bounty Hunter, Crafter"
              >
            </div>
          {/if}
          
          {#if submissionType === 'loot'}
            <div class="form-group">
              <label for="location" class="required">Location</label>
              <input 
                type="text" 
                id="location" 
                bind:value={formData.metadata.location}
                placeholder="e.g., Tatooine, Krayt Dragon Cave"
                required
              >
            </div>
          {/if}
        </div>
        
        {#if submissionType === 'guide'}
          <div class="form-group">
            <label for="estimatedTime">Estimated Time</label>
            <input 
              type="text" 
              id="estimatedTime" 
              bind:value={formData.estimatedTime}
              placeholder="e.g., 30 minutes, 2 hours"
            >
          </div>
        {/if}
        
        <!-- Requirements -->
        {#if submissionType === 'guide' || submissionType === 'mod'}
          <div class="form-group">
            <label>Requirements/Prerequisites</label>
            <div class="requirements-list">
              {#each formData.metadata.requirements as requirement, index}
                <div class="requirement-input">
                  <input 
                    type="text" 
                    bind:value={formData.metadata.requirements[index]}
                    placeholder="Enter requirement"
                  >
                  <button 
                    type="button" 
                    class="remove-btn"
                    on:click={() => removeRequirement(index)}
                  >
                    ×
                  </button>
                </div>
              {/each}
              <button type="button" class="add-requirement-btn" on:click={addRequirement}>
                + Add Requirement
              </button>
            </div>
          </div>
        {/if}
      </div>
      
      <!-- Tags Section -->
      <div class="form-section">
        <h3>Tags</h3>
        <div class="form-group">
          <label for="tags">Tags (comma-separated)</label>
          <input 
            type="text" 
            id="tagInput"
            placeholder="Type a tag and press Enter or comma"
            on:keydown={handleTagInput}
          >
          <div class="tags-display">
            {#each selectedTags as tag, index}
              <span class="tag">
                {tag}
                <button type="button" class="tag-remove" on:click={() => removeTag(index)}>×</button>
              </span>
            {/each}
          </div>
          <div class="form-hint">
            Popular tags: Guide, Mod, Loot Drop, Bug Report, PvP, PvE, Crafting, Trading
          </div>
        </div>
      </div>
      
      <!-- File Upload -->
      {#if currentConfig.allowFiles}
        <div class="form-section">
          <h3>File Attachments</h3>
          <div class="form-group">
            <label for="files">
              {submissionType === 'mod' ? 'Mod Files (Required)' : 'Supporting Files'}
              {#if currentConfig.requiredFields.includes('files')}
                <span class="required-asterisk">*</span>
              {/if}
            </label>
            <input 
              type="file" 
              id="files" 
              multiple
              accept={currentConfig.fileTypes.map(type => `.${type}`).join(',')}
              on:change={handleFileUpload}
            >
            <div class="form-hint">
              Allowed: {currentConfig.fileTypes.join(', ')} • Max {formatFileSize(maxFileSize)} per file
            </div>
            
            <!-- File Preview -->
            {#if fileCount > 0}
              <div class="files-preview">
                <h4>Uploaded Files ({fileCount})</h4>
                {#each formData.files as file, index}
                  <div class="file-item">
                    <div class="file-info">
                      <span class="file-name">{file.name}</span>
                      <span class="file-size">{formatFileSize(file.size)}</span>
                    </div>
                    <button 
                      type="button" 
                      class="remove-file-btn"
                      on:click={() => removeFile(index)}
                    >
                      ×
                    </button>
                  </div>
                {/each}
              </div>
            {/if}
          </div>
        </div>
      {/if}
      
      <!-- Author Information -->
      <div class="form-section">
        <h3>Contact Information</h3>
        
        <div class="form-row">
          <div class="form-group">
            <label for="authorName">Your Name/Handle</label>
            <input 
              type="text" 
              id="authorName" 
              bind:value={formData.author.name}
              placeholder="How should we credit you?"
            >
          </div>
          
          <div class="form-group">
            <label for="preferredContact">Preferred Contact</label>
            <select id="preferredContact" bind:value={formData.author.preferredContact}>
              {#each contactMethods as method}
                <option value={method}>{method.charAt(0).toUpperCase() + method.slice(1)}</option>
              {/each}
            </select>
          </div>
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label for="discordId">Discord ID (Optional)</label>
            <input 
              type="text" 
              id="discordId" 
              bind:value={formData.author.discordId}
              placeholder="username#1234 or @username"
            >
          </div>
          
          <div class="form-group">
            <label for="email">Email (Optional)</label>
            <input 
              type="email" 
              id="email" 
              bind:value={formData.author.email}
              placeholder="your.email@example.com"
            >
          </div>
        </div>
      </div>
      
      <!-- Agreements and Options -->
      <div class="form-section">
        <h3>Agreements & Options</h3>
        
        {#if submissionType === 'mod'}
          <div class="form-group">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                bind:checked={formData.disclaimer}
                required
              >
              <span class="checkmark"></span>
              I understand that uploaded mods will be scanned for security and may be rejected if they contain malicious code or violate community guidelines.
            </label>
          </div>
        {/if}
        
        <div class="form-group">
          <label class="checkbox-label">
            <input 
              type="checkbox" 
              bind:checked={formData.termsAccepted}
              required
            >
            <span class="checkmark"></span>
            I agree to the <a href="/terms" target="_blank">Terms of Service</a> and <a href="/community-guidelines" target="_blank">Community Guidelines</a>
          </label>
        </div>
        
        <div class="form-group">
          <label class="checkbox-label">
            <input 
              type="checkbox" 
              bind:checked={formData.allowUpdates}
            >
            <span class="checkmark"></span>
            Allow community updates and improvements to my submission
          </label>
        </div>
      </div>
      
      <!-- Form Actions -->
      <div class="form-actions">
        <button type="button" class="btn btn-secondary" on:click={resetForm}>
          🔄 Reset Form
        </button>
        
        <button type="button" class="btn btn-secondary" on:click={previewSubmission}>
          👁️ Preview
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
            {currentConfig.icon} Submit {currentConfig.title.split(' ').pop()}
          {/if}
        </button>
      </div>
      
      <!-- Form Status -->
      <div class="form-status">
        {#if !isFormValid}
          <div class="validation-message">
            Please complete all required fields to submit.
          </div>
        {/if}
      </div>
    </form>
  {/if}
</div>

<style>
  .submission-form-container {
    max-width: 900px;
    margin: 0 auto;
    padding: 20px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  }
  
  .success-message,
  .error-message {
    display: flex;
    align-items: flex-start;
    gap: 15px;
    padding: 25px;
    border-radius: 12px;
    margin-bottom: 30px;
  }
  
  .success-message {
    background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
    border: 1px solid #c3e6cb;
    color: #155724;
  }
  
  .error-message {
    background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
    border: 1px solid #f5c6cb;
    color: #721c24;
  }
  
  .success-icon,
  .error-icon {
    font-size: 2em;
    line-height: 1;
  }
  
  .success-content h3,
  .error-content strong {
    margin: 0 0 10px 0;
    font-size: 1.3em;
  }
  
  .success-content p,
  .error-content p {
    margin: 5px 0;
    line-height: 1.5;
  }
  
  .submission-form {
    background: white;
    border-radius: 16px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.1);
    overflow: hidden;
  }
  
  .form-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 40px;
    text-align: center;
  }
  
  .form-icon {
    font-size: 3em;
    margin-bottom: 15px;
    display: block;
  }
  
  .form-header h2 {
    margin: 0 0 10px 0;
    font-size: 2.2em;
    font-weight: 700;
  }
  
  .form-header p {
    margin: 0;
    opacity: 0.9;
    font-size: 1.1em;
  }
  
  .form-section {
    padding: 30px 40px;
    border-bottom: 1px solid #e9ecef;
  }
  
  .form-section:last-child {
    border-bottom: none;
  }
  
  .form-section h3 {
    margin: 0 0 25px 0;
    color: #333;
    font-size: 1.4em;
    font-weight: 600;
    border-bottom: 2px solid #667eea;
    padding-bottom: 10px;
  }
  
  .form-group {
    margin-bottom: 25px;
  }
  
  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 25px;
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
  
  label.required::after,
  .required-asterisk {
    content: " *";
    color: #e74c3c;
  }
  
  input[type="text"],
  input[type="email"],
  select,
  textarea {
    width: 100%;
    padding: 12px 16px;
    border: 2px solid #e1e8ed;
    border-radius: 8px;
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
  
  .content-editor {
    border: 2px solid #e1e8ed;
    border-radius: 8px;
    overflow: hidden;
  }
  
  .editor-tabs {
    display: flex;
    background: #f8f9fa;
    border-bottom: 1px solid #e1e8ed;
  }
  
  .tab-btn {
    background: none;
    border: none;
    padding: 12px 20px;
    cursor: pointer;
    transition: background-color 0.2s ease;
    font-weight: 500;
  }
  
  .tab-btn.active {
    background: white;
    border-bottom: 2px solid #667eea;
  }
  
  .tab-pane {
    display: none;
    padding: 0;
  }
  
  .tab-pane.active {
    display: block;
  }
  
  .content-textarea {
    border: none;
    resize: vertical;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 13px;
    line-height: 1.5;
  }
  
  .content-textarea:focus {
    box-shadow: none;
  }
  
  .markdown-preview {
    padding: 20px;
    min-height: 300px;
    background: #fafbfc;
    line-height: 1.6;
  }
  
  .preview-placeholder {
    color: #666;
    font-style: italic;
    text-align: center;
    margin-top: 100px;
  }
  
  .form-hint {
    font-size: 0.9em;
    color: #666;
    margin-top: 5px;
  }
  
  .tags-display {
    margin-top: 10px;
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  
  .tag {
    background: #667eea;
    color: white;
    padding: 4px 8px;
    border-radius: 15px;
    font-size: 0.85em;
    display: flex;
    align-items: center;
    gap: 5px;
  }
  
  .tag-remove {
    background: none;
    border: none;
    color: white;
    cursor: pointer;
    font-size: 1.2em;
    line-height: 1;
  }
  
  .requirements-list {
    space-y: 10px;
  }
  
  .requirement-input {
    display: flex;
    gap: 10px;
    align-items: center;
    margin-bottom: 10px;
  }
  
  .requirement-input input {
    flex: 1;
    margin: 0;
  }
  
  .remove-btn {
    background: #e74c3c;
    color: white;
    border: none;
    border-radius: 50%;
    width: 30px;
    height: 30px;
    cursor: pointer;
    font-size: 16px;
  }
  
  .add-requirement-btn {
    background: #667eea;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.9em;
  }
  
  .files-preview {
    margin-top: 15px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
    border: 1px solid #e1e8ed;
  }
  
  .files-preview h4 {
    margin: 0 0 10px 0;
    color: #333;
    font-size: 1em;
  }
  
  .file-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    background: white;
    border-radius: 6px;
    margin-bottom: 8px;
    border: 1px solid #e9ecef;
  }
  
  .file-item:last-child {
    margin-bottom: 0;
  }
  
  .file-info {
    display: flex;
    flex-direction: column;
  }
  
  .file-name {
    font-weight: 500;
    color: #333;
  }
  
  .file-size {
    font-size: 0.85em;
    color: #666;
  }
  
  .remove-file-btn {
    background: #e74c3c;
    color: white;
    border: none;
    border-radius: 50%;
    width: 25px;
    height: 25px;
    cursor: pointer;
    font-size: 14px;
  }
  
  .checkbox-label {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    cursor: pointer;
    line-height: 1.5;
  }
  
  .checkbox-label input[type="checkbox"] {
    width: auto;
    margin: 0;
  }
  
  .form-actions {
    padding: 30px 40px;
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
    border-radius: 8px;
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
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
  }
  
  .btn-primary:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
  }
  
  .btn-primary:disabled {
    background: #a0aec0;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
  
  .btn-secondary {
    background: #e2e8f0;
    color: #4a5568;
    border: 2px solid #e2e8f0;
  }
  
  .btn-secondary:hover {
    background: #cbd5e0;
    border-color: #cbd5e0;
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
    padding: 15px 40px;
    background: #fff3cd;
    border-top: 1px solid #ffeaa7;
  }
  
  .validation-message {
    color: #856404;
    font-size: 0.9em;
    text-align: center;
  }
  
  input[type="file"] {
    padding: 12px;
    border: 2px dashed #e1e8ed;
    background: #f8f9fa;
    border-radius: 8px;
  }
  
  input[type="file"]:focus {
    border-color: #667eea;
    border-style: solid;
  }
</style>