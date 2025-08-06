/**
 * Mod Submission Portal - Specialized Page
 * Dedicated interface for mod uploads with enhanced validation and guidelines
 */

const fs = require('fs');
const path = require('path');

class ModSubmissionGenerator {
  data() {
    return {
      title: "Submit a Mod - MorningStar Mod Portal",
      description: "Upload and share your Star Wars Galaxies modifications with the community. Secure validation and community testing included.",
      layout: "base.njk",
      permalink: "/mods/submit/",
      tags: ["mods", "submit", "upload"],
      eleventyNavigation: {
        key: "Submit Mod",
        parent: "Mods",
        order: 1
      }
    };
  }

  async render(data) {
    // Load mod categories and guidelines
    const modConfig = await this.loadModConfiguration();
    
    return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${data.title}</title>
    <meta name="description" content="${data.description}">
    
    <!-- Schema.org markup for mod submission -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "WebPage",
      "name": "${data.title}",
      "description": "${data.description}",
      "url": "https://morningstar.ms11.com/mods/submit/"
    }
    </script>
    
    <!-- Styles -->
    <style>
        .mod-submission-page {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .page-header {
            background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);
            color: white;
            padding: 50px 40px;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 40px;
            box-shadow: 0 10px 30px rgba(155, 89, 182, 0.3);
        }
        
        .page-header h1 {
            margin: 0 0 15px 0;
            font-size: 2.8em;
            font-weight: 700;
        }
        
        .page-header .subtitle {
            font-size: 1.2em;
            opacity: 0.95;
            max-width: 700px;
            margin: 0 auto;
            line-height: 1.6;
        }
        
        .content-grid {
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: 40px;
            margin-bottom: 40px;
        }
        
        @media (max-width: 1024px) {
            .content-grid {
                grid-template-columns: 1fr;
                gap: 30px;
            }
        }
        
        .main-content {
            background: white;
            border-radius: 16px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .sidebar {
            display: flex;
            flex-direction: column;
            gap: 25px;
        }
        
        .sidebar-card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .sidebar-card h3 {
            margin: 0 0 15px 0;
            color: #333;
            font-size: 1.3em;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .guidelines-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        
        .guidelines-list li {
            padding: 12px 0;
            border-bottom: 1px solid #f0f0f0;
            position: relative;
            padding-left: 30px;
            line-height: 1.5;
        }
        
        .guidelines-list li:before {
            content: "✓";
            position: absolute;
            left: 0;
            color: #27ae60;
            font-weight: bold;
            font-size: 1.1em;
        }
        
        .guidelines-list li:last-child {
            border-bottom: none;
        }
        
        .security-notice {
            background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
            border: 1px solid #ffeaa7;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 25px;
        }
        
        .security-notice .notice-header {
            display: flex;
            align-items: center;
            gap: 10px;
            font-weight: 600;
            color: #856404;
            margin-bottom: 10px;
        }
        
        .security-notice .notice-text {
            color: #856404;
            line-height: 1.5;
        }
        
        .popular-categories {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
        }
        
        .category-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-top: 15px;
        }
        
        .category-item {
            background: white;
            padding: 12px 15px;
            border-radius: 6px;
            text-align: center;
            font-size: 0.9em;
            color: #666;
            border: 1px solid #e9ecef;
            transition: all 0.2s ease;
        }
        
        .category-item:hover {
            background: #9b59b6;
            color: white;
            border-color: #9b59b6;
            transform: translateY(-1px);
        }
        
        .upload-requirements {
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border: 1px solid #bbdefb;
            border-radius: 12px;
            padding: 20px;
        }
        
        .requirements-grid {
            display: grid;
            gap: 15px;
            margin-top: 15px;
        }
        
        .requirement-item {
            display: flex;
            align-items: center;
            gap: 10px;
            color: #1565c0;
        }
        
        .requirement-icon {
            background: #1976d2;
            color: white;
            border-radius: 50%;
            width: 25px;
            height: 25px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8em;
            font-weight: bold;
        }
        
        .testing-info {
            background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
            border: 1px solid #e1bee7;
            border-radius: 12px;
            padding: 20px;
        }
        
        .testing-steps {
            margin-top: 15px;
        }
        
        .testing-step {
            display: flex;
            align-items: flex-start;
            gap: 12px;
            margin-bottom: 12px;
        }
        
        .step-number {
            background: #9c27b0;
            color: white;
            border-radius: 50%;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8em;
            font-weight: bold;
            flex-shrink: 0;
        }
        
        .step-text {
            color: #4a148c;
            line-height: 1.5;
            flex: 1;
        }
        
        .mod-form-container {
            padding: 0;
        }
        
        .form-progress {
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
        }
        
        .progress-steps {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 600px;
            margin: 0 auto;
        }
        
        .progress-step {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
            flex: 1;
            position: relative;
        }
        
        .progress-step:not(:last-child)::after {
            content: '';
            position: absolute;
            top: 15px;
            right: -50%;
            width: 100%;
            height: 2px;
            background: #e9ecef;
            z-index: 1;
        }
        
        .progress-step.active:not(:last-child)::after {
            background: #9b59b6;
        }
        
        .step-circle {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            background: #e9ecef;
            color: #666;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            z-index: 2;
            position: relative;
        }
        
        .progress-step.active .step-circle {
            background: #9b59b6;
            color: white;
        }
        
        .progress-step.completed .step-circle {
            background: #27ae60;
            color: white;
        }
        
        .step-label {
            font-size: 0.85em;
            color: #666;
            text-align: center;
        }
        
        .progress-step.active .step-label {
            color: #9b59b6;
            font-weight: 600;
        }
        
        .featured-mods {
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            margin-top: 40px;
        }
        
        .featured-mods h2 {
            margin: 0 0 20px 0;
            color: #333;
            font-size: 1.8em;
            text-align: center;
        }
        
        .featured-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin-top: 25px;
        }
        
        .featured-mod {
            border: 1px solid #e9ecef;
            border-radius: 12px;
            padding: 20px;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .featured-mod:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        .mod-title {
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
            font-size: 1.1em;
        }
        
        .mod-author {
            color: #666;
            font-size: 0.9em;
            margin-bottom: 10px;
        }
        
        .mod-description {
            color: #555;
            line-height: 1.5;
            margin-bottom: 15px;
        }
        
        .mod-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.85em;
            color: #666;
        }
        
        .mod-category {
            background: #9b59b6;
            color: white;
            padding: 3px 8px;
            border-radius: 12px;
            font-size: 0.75em;
        }
        
        .quick-tips {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-radius: 16px;
            padding: 30px;
            margin-top: 40px;
        }
        
        .tips-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .tip-card {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .tip-icon {
            font-size: 2em;
            margin-bottom: 10px;
            display: block;
        }
        
        .tip-title {
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
        }
        
        .tip-text {
            color: #666;
            line-height: 1.5;
            font-size: 0.9em;
        }
        
        .community-feedback {
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            margin-top: 40px;
        }
        
        .feedback-item {
            border-left: 4px solid #9b59b6;
            padding: 15px 20px;
            background: #f8f9fa;
            border-radius: 0 8px 8px 0;
            margin-bottom: 15px;
        }
        
        .feedback-text {
            font-style: italic;
            color: #555;
            margin-bottom: 8px;
            line-height: 1.5;
        }
        
        .feedback-author {
            font-weight: 600;
            color: #9b59b6;
            font-size: 0.9em;
        }
        
        .success-stories {
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border-radius: 16px;
            padding: 30px;
            margin-top: 40px;
        }
        
        .success-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-top: 25px;
        }
        
        .success-card {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .success-number {
            font-size: 2.5em;
            font-weight: bold;
            color: #27ae60;
            margin-bottom: 10px;
            display: block;
        }
        
        .success-label {
            color: #155724;
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .success-description {
            color: #155724;
            font-size: 0.9em;
            line-height: 1.5;
        }
    </style>
</head>
<body>
    <div class="mod-submission-page">
        <!-- Header -->
        <div class="page-header">
            <h1>⚙️ Submit Your Mod</h1>
            <div class="subtitle">
                Share your Star Wars Galaxies modifications with the community. 
                Our secure validation ensures safe downloads while showcasing your creativity.
            </div>
        </div>
        
        <!-- Security Notice -->
        <div class="security-notice">
            <div class="notice-header">
                🔒 Security & Safety First
            </div>
            <div class="notice-text">
                All uploaded mods undergo automated security scanning and community review. 
                We maintain a zero-tolerance policy for malicious code, exploits, or harmful content. 
                Your mod will be tested in a secure environment before approval.
            </div>
        </div>
        
        <!-- Main Content Grid -->
        <div class="content-grid">
            <!-- Main Form Area -->
            <div class="main-content">
                <!-- Progress Indicator -->
                <div class="form-progress">
                    <div class="progress-steps">
                        <div class="progress-step active">
                            <div class="step-circle">1</div>
                            <div class="step-label">Upload</div>
                        </div>
                        <div class="progress-step">
                            <div class="step-circle">2</div>
                            <div class="step-label">Review</div>
                        </div>
                        <div class="progress-step">
                            <div class="step-circle">3</div>
                            <div class="step-label">Test</div>
                        </div>
                        <div class="progress-step">
                            <div class="step-circle">4</div>
                            <div class="step-label">Publish</div>
                        </div>
                    </div>
                </div>
                
                <!-- Mod Submission Form -->
                <div class="mod-form-container">
                    <!-- The SubmissionForm.svelte component would be embedded here -->
                    <div id="mod-submission-form"></div>
                </div>
            </div>
            
            <!-- Sidebar -->
            <div class="sidebar">
                <!-- Submission Guidelines -->
                <div class="sidebar-card">
                    <h3>📋 Submission Guidelines</h3>
                    <ul class="guidelines-list">
                        <li>Original work or proper attribution required</li>
                        <li>No malicious code or exploits</li>
                        <li>Clear installation instructions</li>
                        <li>Compatible with current game version</li>
                        <li>Appropriate content rating</li>
                        <li>Professional description and screenshots</li>
                    </ul>
                </div>
                
                <!-- Popular Categories -->
                <div class="sidebar-card">
                    <h3>🎯 Popular Categories</h3>
                    <div class="popular-categories">
                        <div class="category-grid">
                            ${this.renderCategoryGrid(modConfig.popularCategories)}
                        </div>
                    </div>
                </div>
                
                <!-- Upload Requirements -->
                <div class="sidebar-card">
                    <h3>📦 Upload Requirements</h3>
                    <div class="upload-requirements">
                        <div class="requirements-grid">
                            <div class="requirement-item">
                                <div class="requirement-icon">📁</div>
                                <div>Max 50MB per file</div>
                            </div>
                            <div class="requirement-item">
                                <div class="requirement-icon">🗜️</div>
                                <div>ZIP, RAR, or 7Z format</div>
                            </div>
                            <div class="requirement-item">
                                <div class="requirement-icon">🖼️</div>
                                <div>Screenshots encouraged</div>
                            </div>
                            <div class="requirement-item">
                                <div class="requirement-icon">📄</div>
                                <div>Include README file</div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Testing Process -->
                <div class="sidebar-card">
                    <h3>🧪 Testing Process</h3>
                    <div class="testing-info">
                        <div class="testing-steps">
                            <div class="testing-step">
                                <div class="step-number">1</div>
                                <div class="step-text">Automated security scan</div>
                            </div>
                            <div class="testing-step">
                                <div class="step-number">2</div>
                                <div class="step-text">Community review period</div>
                            </div>
                            <div class="testing-step">
                                <div class="step-number">3</div>
                                <div class="step-text">Compatibility testing</div>
                            </div>
                            <div class="testing-step">
                                <div class="step-number">4</div>
                                <div class="step-text">Publication approval</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Featured Recent Mods -->
        <div class="featured-mods">
            <h2>🌟 Recently Featured Mods</h2>
            <p style="text-align: center; color: #666; margin-bottom: 0;">
                Get inspired by what the community has been creating
            </p>
            
            <div class="featured-grid">
                ${this.renderFeaturedMods(modConfig.recentMods)}
            </div>
        </div>
        
        <!-- Quick Tips -->
        <div class="quick-tips">
            <h2 style="text-align: center; margin-bottom: 10px;">💡 Quick Tips for Success</h2>
            <p style="text-align: center; color: #666;">
                Follow these best practices to improve your mod's approval chances
            </p>
            
            <div class="tips-grid">
                <div class="tip-card">
                    <span class="tip-icon">📸</span>
                    <div class="tip-title">Great Screenshots</div>
                    <div class="tip-text">
                        Include before/after screenshots showing your mod in action. 
                        Visual comparisons help users understand the improvements.
                    </div>
                </div>
                
                <div class="tip-card">
                    <span class="tip-icon">📝</span>
                    <div class="tip-title">Clear Documentation</div>
                    <div class="tip-text">
                        Write detailed installation instructions and include any 
                        dependencies or requirements needed to run your mod.
                    </div>
                </div>
                
                <div class="tip-card">
                    <span class="tip-icon">🔧</span>
                    <div class="tip-title">Version Control</div>
                    <div class="tip-text">
                        Use semantic versioning (1.0.0) and maintain changelog 
                        documentation for updates and bug fixes.
                    </div>
                </div>
                
                <div class="tip-card">
                    <span class="tip-icon">🤝</span>
                    <div class="tip-title">Community Engagement</div>
                    <div class="tip-text">
                        Respond to feedback, fix reported issues, and engage 
                        with users who download and test your modifications.
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Community Feedback -->
        <div class="community-feedback">
            <h2 style="text-align: center; margin-bottom: 20px;">💬 What Modders Say</h2>
            
            <div class="feedback-item">
                <div class="feedback-text">
                    "The submission process was straightforward and the automated testing caught 
                    a compatibility issue I missed. Great system for ensuring quality!"
                </div>
                <div class="feedback-author">— UIModder, Enhanced Inventory Mod</div>
            </div>
            
            <div class="feedback-item">
                <div class="feedback-text">
                    "Love how the community can provide feedback during the review process. 
                    It helped me improve my mod before the final release."
                </div>
                <div class="feedback-author">— CreativeCoder, Visual Enhancement Pack</div>
            </div>
            
            <div class="feedback-item">
                <div class="feedback-text">
                    "The security scanning gave me confidence that my mod wouldn't accidentally 
                    break anything. Professional platform for mod distribution."
                </div>
                <div class="feedback-author">— SafeModder, Performance Optimizer</div>
            </div>
        </div>
        
        <!-- Success Stories -->
        <div class="success-stories">
            <h2 style="text-align: center; color: #155724; margin-bottom: 10px;">🎉 Community Success</h2>
            <p style="text-align: center; color: #155724; margin-bottom: 0;">
                See the impact of community contributions
            </p>
            
            <div class="success-grid">
                <div class="success-card">
                    <span class="success-number">500+</span>
                    <div class="success-label">Mods Available</div>
                    <div class="success-description">
                        A thriving library of community-created modifications 
                        covering everything from UI to gameplay enhancements.
                    </div>
                </div>
                
                <div class="success-card">
                    <span class="success-number">98%</span>
                    <div class="success-label">Approval Rate</div>
                    <div class="success-description">
                        Most submitted mods meet our quality standards and 
                        get approved within the review period.
                    </div>
                </div>
                
                <div class="success-card">
                    <span class="success-number">50K+</span>
                    <div class="success-label">Downloads Monthly</div>
                    <div class="success-description">
                        Active community engagement with thousands of players 
                        downloading and using community modifications.
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- JavaScript -->
    <script type="module">
        // Import and initialize the SubmissionForm component
        // This would normally be handled by a build system
        
        // Mock initialization for demonstration
        document.addEventListener('DOMContentLoaded', function() {
            const formContainer = document.getElementById('mod-submission-form');
            
            // This would be replaced with actual Svelte component mounting
            formContainer.innerHTML = \`
                <div style="padding: 40px; text-align: center; background: #f8f9fa; border-radius: 12px; margin: 20px;">
                    <h3>🚧 SubmissionForm Component Integration Point</h3>
                    <p>The SubmissionForm.svelte component would be mounted here with mod-specific configuration:</p>
                    <pre style="background: white; padding: 15px; border-radius: 8px; text-align: left; margin-top: 15px;">
&lt;SubmissionForm 
  submissionType="mod"
  submitUrl="/api/submit"
  maxFileSize={50 * 1024 * 1024}
  allowedFileTypes={['zip', 'rar', '7z', 'png', 'jpg', 'jpeg', 'gif', 'txt', 'md']}
  showPreview={false}
  enableMarkdown={true}
/&gt;</pre>
                </div>
            \`;
            
            // Progress step activation simulation
            updateProgressSteps();
        });
        
        function updateProgressSteps() {
            const steps = document.querySelectorAll('.progress-step');
            steps.forEach((step, index) => {
                if (index === 0) {
                    step.classList.add('active');
                }
            });
        }
        
        // Category hover effects
        document.querySelectorAll('.category-item').forEach(item => {
            item.addEventListener('click', function() {
                const category = this.textContent.trim();
                if (window.submitForm) {
                    window.submitForm.setCategory(category);
                }
            });
        });
        
        // Analytics tracking
        function trackModSubmissionStart() {
            if (typeof gtag !== 'undefined') {
                gtag('event', 'mod_submission_started', {
                    'page_location': window.location.href
                });
            }
        }
        
        // Track when users interact with the form
        document.addEventListener('click', function(e) {
            if (e.target.closest('#mod-submission-form')) {
                trackModSubmissionStart();
            }
        });
    </script>
</body>
</html>`;
  }

  async loadModConfiguration() {
    // In production, this would load from a configuration file
    return {
      popularCategories: [
        'UI Enhancement',
        'Quality of Life',
        'Visual Overhaul',
        'Performance',
        'Gameplay',
        'Audio',
        'Utility Tools',
        'Bug Fixes'
      ],
      recentMods: [
        {
          title: 'Enhanced Inventory Manager v3.2',
          author: 'UIExpert',
          description: 'Complete overhaul of the inventory system with sorting, filtering, and search capabilities.',
          category: 'UI Enhancement',
          downloads: 2340,
          rating: 4.8
        },
        {
          title: 'Performance Optimizer Pro',
          author: 'SpeedDemon',
          description: 'Comprehensive performance improvements for better frame rates and reduced loading times.',
          category: 'Performance',
          downloads: 1876,
          rating: 4.6
        },
        {
          title: 'Immersive Audio Pack',
          author: 'SoundMaster',
          description: 'High-quality audio replacements and enhancements for a more immersive experience.',
          category: 'Audio',
          downloads: 1543,
          rating: 4.9
        }
      ]
    };
  }

  renderCategoryGrid(categories) {
    return categories.map(category => 
      `<div class="category-item">${category}</div>`
    ).join('');
  }

  renderFeaturedMods(mods) {
    return mods.map(mod => `
      <div class="featured-mod">
        <div class="mod-title">${mod.title}</div>
        <div class="mod-author">by ${mod.author}</div>
        <div class="mod-description">${mod.description}</div>
        <div class="mod-meta">
          <span class="mod-category">${mod.category}</span>
          <span>${mod.downloads.toLocaleString()} downloads</span>
        </div>
      </div>
    `).join('');
  }
}

module.exports = ModSubmissionGenerator;