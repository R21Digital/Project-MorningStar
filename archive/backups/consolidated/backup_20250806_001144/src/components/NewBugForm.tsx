/**
 * NewBugForm Component - Batch 173
 * Form for creating new bug reports with validation and file upload
 */

import React, { useState, useRef } from 'react';

interface BugEnvironment {
  botVersion?: string;
  gameServer?: string;
  operatingSystem?: string;
  browser?: string;
  device?: string;
  screenResolution?: string;
  contentVersion?: string;
  dataSource?: string;
  memoryUsage?: string;
}

interface NewBugFormData {
  title: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  description: string;
  tags: string[];
  priority: 'P0' | 'P1' | 'P2' | 'P3';
  assignedTo?: string;
  reproductionSteps: string[];
  environment: BugEnvironment;
  screenshot?: File | null;
}

interface NewBugFormProps {
  onSubmit: (bugData: NewBugFormData) => void;
  onCancel: () => void;
  assignableDevs: Array<{id: string, name: string, role: string}>;
  availableTags: string[];
  isVisible: boolean;
}

export const NewBugForm: React.FC<NewBugFormProps> = ({
  onSubmit,
  onCancel,
  assignableDevs,
  availableTags,
  isVisible
}) => {
  const [formData, setFormData] = useState<NewBugFormData>({
    title: '',
    severity: 'medium',
    description: '',
    tags: [],
    priority: 'P2',
    assignedTo: '',
    reproductionSteps: [''],
    environment: {},
    screenshot: null
  });

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Validate form data
  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    } else if (formData.title.length < 10) {
      newErrors.title = 'Title must be at least 10 characters';
    }

    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    } else if (formData.description.length < 20) {
      newErrors.description = 'Description must be at least 20 characters';
    }

    if (formData.tags.length === 0) {
      newErrors.tags = 'At least one tag is required';
    }

    if (formData.reproductionSteps.filter(step => step.trim()).length === 0) {
      newErrors.reproductionSteps = 'At least one reproduction step is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    
    try {
      // Filter out empty reproduction steps
      const cleanedData = {
        ...formData,
        reproductionSteps: formData.reproductionSteps.filter(step => step.trim()),
        assignedTo: formData.assignedTo || undefined
      };
      
      await onSubmit(cleanedData);
      
      // Reset form on successful submission
      setFormData({
        title: '',
        severity: 'medium',
        description: '',
        tags: [],
        priority: 'P2',
        assignedTo: '',
        reproductionSteps: [''],
        environment: {},
        screenshot: null
      });
      
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      
    } catch (error) {
      console.error('Error submitting bug report:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle input changes
  const handleInputChange = (field: keyof NewBugFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  // Handle environment field changes
  const handleEnvironmentChange = (field: keyof BugEnvironment, value: string) => {
    setFormData(prev => ({
      ...prev,
      environment: { ...prev.environment, [field]: value }
    }));
  };

  // Handle reproduction steps
  const handleReproductionStepChange = (index: number, value: string) => {
    const newSteps = [...formData.reproductionSteps];
    newSteps[index] = value;
    setFormData(prev => ({ ...prev, reproductionSteps: newSteps }));
    
    if (errors.reproductionSteps) {
      setErrors(prev => ({ ...prev, reproductionSteps: '' }));
    }
  };

  const addReproductionStep = () => {
    setFormData(prev => ({
      ...prev,
      reproductionSteps: [...prev.reproductionSteps, '']
    }));
  };

  const removeReproductionStep = (index: number) => {
    if (formData.reproductionSteps.length > 1) {
      const newSteps = formData.reproductionSteps.filter((_, i) => i !== index);
      setFormData(prev => ({ ...prev, reproductionSteps: newSteps }));
    }
  };

  // Handle tag toggle
  const handleTagToggle = (tag: string) => {
    const newTags = formData.tags.includes(tag)
      ? formData.tags.filter(t => t !== tag)
      : [...formData.tags, tag];
    
    handleInputChange('tags', newTags);
  };

  // Handle screenshot upload
  const handleScreenshotChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    
    if (file) {
      // Validate file type and size
      const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
      const maxSize = 10 * 1024 * 1024; // 10MB
      
      if (!validTypes.includes(file.type)) {
        alert('Please select a valid image file (JPEG, PNG, GIF, or WebP)');
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
        return;
      }
      
      if (file.size > maxSize) {
        alert('File size must be less than 10MB');
        if (fileInputRef.current) {
          fileInputRef.current.value = '';
        }
        return;
      }
    }
    
    handleInputChange('screenshot', file);
  };

  // Auto-populate environment data
  const handleAutoFillEnvironment = () => {
    const environment: BugEnvironment = {
      browser: navigator.userAgent.includes('Chrome') ? 'Chrome' : 
                navigator.userAgent.includes('Firefox') ? 'Firefox' :
                navigator.userAgent.includes('Safari') ? 'Safari' : 'Unknown',
      operatingSystem: navigator.platform,
      screenResolution: `${screen.width}x${screen.height}`,
      device: /Mobi|Android/i.test(navigator.userAgent) ? 'Mobile' : 'Desktop'
    };
    
    setFormData(prev => ({
      ...prev,
      environment: { ...prev.environment, ...environment }
    }));
  };

  if (!isVisible) return null;

  return (
    <div className="new-bug-form-overlay">
      <div className="new-bug-form-container">
        <div className="form-header">
          <h2>
            <i className="fas fa-bug"></i>
            New Bug Report
          </h2>
          <button className="close-btn" onClick={onCancel}>
            <i className="fas fa-times"></i>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="bug-form">
          {/* Basic Information */}
          <div className="form-section">
            <h3>Basic Information</h3>
            
            <div className="form-group">
              <label htmlFor="title">
                Title <span className="required">*</span>
              </label>
              <input
                id="title"
                type="text"
                value={formData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                placeholder="Brief description of the bug..."
                className={errors.title ? 'error' : ''}
                maxLength={200}
              />
              {errors.title && <div className="error-message">{errors.title}</div>}
              <div className="char-count">{formData.title.length}/200</div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="severity">
                  Severity <span className="required">*</span>
                </label>
                <select
                  id="severity"
                  value={formData.severity}
                  onChange={(e) => handleInputChange('severity', e.target.value)}
                >
                  <option value="low">Low - Minor issue</option>
                  <option value="medium">Medium - Affects functionality</option>
                  <option value="high">High - Major impact</option>
                  <option value="critical">Critical - System down/blocking</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="priority">
                  Priority <span className="required">*</span>
                </label>
                <select
                  id="priority"
                  value={formData.priority}
                  onChange={(e) => handleInputChange('priority', e.target.value)}
                >
                  <option value="P3">P3 - Low priority</option>
                  <option value="P2">P2 - Medium priority</option>
                  <option value="P1">P1 - High priority</option>
                  <option value="P0">P0 - Critical priority</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="assignee">Assign to</label>
                <select
                  id="assignee"
                  value={formData.assignedTo}
                  onChange={(e) => handleInputChange('assignedTo', e.target.value)}
                >
                  <option value="">Unassigned</option>
                  {assignableDevs.map(dev => (
                    <option key={dev.id} value={dev.id}>
                      {dev.name} ({dev.role})
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="form-group">
              <label>
                Tags <span className="required">*</span>
              </label>
              <div className="tag-selector">
                {availableTags.map(tag => (
                  <button
                    key={tag}
                    type="button"
                    className={`tag-btn ${formData.tags.includes(tag) ? 'selected' : ''}`}
                    onClick={() => handleTagToggle(tag)}
                  >
                    {tag}
                  </button>
                ))}
              </div>
              {errors.tags && <div className="error-message">{errors.tags}</div>}
            </div>
          </div>

          {/* Description */}
          <div className="form-section">
            <h3>Description</h3>
            
            <div className="form-group">
              <label htmlFor="description">
                Detailed Description <span className="required">*</span>
              </label>
              <textarea
                id="description"
                value={formData.description}
                onChange={(e) => handleInputChange('description', e.target.value)}
                placeholder="Provide a detailed description of the bug, including what you expected to happen vs. what actually happened..."
                rows={6}
                className={errors.description ? 'error' : ''}
                maxLength={2000}
              />
              {errors.description && <div className="error-message">{errors.description}</div>}
              <div className="char-count">{formData.description.length}/2000</div>
            </div>
          </div>

          {/* Reproduction Steps */}
          <div className="form-section">
            <h3>Reproduction Steps</h3>
            
            <div className="form-group">
              <label>
                Steps to Reproduce <span className="required">*</span>
              </label>
              {formData.reproductionSteps.map((step, index) => (
                <div key={index} className="reproduction-step">
                  <div className="step-number">{index + 1}.</div>
                  <input
                    type="text"
                    value={step}
                    onChange={(e) => handleReproductionStepChange(index, e.target.value)}
                    placeholder="Describe the step..."
                    className="step-input"
                  />
                  {formData.reproductionSteps.length > 1 && (
                    <button
                      type="button"
                      className="remove-step-btn"
                      onClick={() => removeReproductionStep(index)}
                    >
                      <i className="fas fa-trash"></i>
                    </button>
                  )}
                </div>
              ))}
              {errors.reproductionSteps && <div className="error-message">{errors.reproductionSteps}</div>}
              
              <button
                type="button"
                className="add-step-btn"
                onClick={addReproductionStep}
              >
                <i className="fas fa-plus"></i>
                Add Step
              </button>
            </div>
          </div>

          {/* Environment */}
          <div className="form-section">
            <h3>Environment Information</h3>
            
            <div className="auto-fill-section">
              <button
                type="button"
                className="auto-fill-btn"
                onClick={handleAutoFillEnvironment}
              >
                <i className="fas fa-magic"></i>
                Auto-fill Browser Info
              </button>
            </div>

            <div className="environment-grid">
              <div className="form-group">
                <label htmlFor="botVersion">Bot Version</label>
                <input
                  id="botVersion"
                  type="text"
                  value={formData.environment.botVersion || ''}
                  onChange={(e) => handleEnvironmentChange('botVersion', e.target.value)}
                  placeholder="e.g., v2.1.4"
                />
              </div>

              <div className="form-group">
                <label htmlFor="gameServer">Game Server</label>
                <input
                  id="gameServer"
                  type="text"
                  value={formData.environment.gameServer || ''}
                  onChange={(e) => handleEnvironmentChange('gameServer', e.target.value)}
                  placeholder="e.g., Restoration III"
                />
              </div>

              <div className="form-group">
                <label htmlFor="operatingSystem">Operating System</label>
                <input
                  id="operatingSystem"
                  type="text"
                  value={formData.environment.operatingSystem || ''}
                  onChange={(e) => handleEnvironmentChange('operatingSystem', e.target.value)}
                  placeholder="e.g., Windows 11"
                />
              </div>

              <div className="form-group">
                <label htmlFor="browser">Browser</label>
                <input
                  id="browser"
                  type="text"
                  value={formData.environment.browser || ''}
                  onChange={(e) => handleEnvironmentChange('browser', e.target.value)}
                  placeholder="e.g., Chrome 131.0.0.0"
                />
              </div>

              <div className="form-group">
                <label htmlFor="device">Device</label>
                <input
                  id="device"
                  type="text"
                  value={formData.environment.device || ''}
                  onChange={(e) => handleEnvironmentChange('device', e.target.value)}
                  placeholder="e.g., Desktop, iPhone 12"
                />
              </div>

              <div className="form-group">
                <label htmlFor="screenResolution">Screen Resolution</label>
                <input
                  id="screenResolution" 
                  type="text"
                  value={formData.environment.screenResolution || ''}
                  onChange={(e) => handleEnvironmentChange('screenResolution', e.target.value)}
                  placeholder="e.g., 1920x1080"
                />
              </div>
            </div>
          </div>

          {/* Screenshot */}
          <div className="form-section">
            <h3>Screenshot (Optional)</h3>
            
            <div className="form-group">
              <label htmlFor="screenshot">Upload Screenshot</label>
              <input
                id="screenshot"
                type="file"
                ref={fileInputRef}
                accept="image/*"
                onChange={handleScreenshotChange}
                className="file-input"
              />
              <div className="file-info">
                Supported formats: JPEG, PNG, GIF, WebP (max 10MB)
              </div>
              {formData.screenshot && (
                <div className="file-preview">
                  <i className="fas fa-image"></i>
                  <span>{formData.screenshot.name}</span>
                  <button
                    type="button"
                    className="remove-file-btn"
                    onClick={() => {
                      handleInputChange('screenshot', null);
                      if (fileInputRef.current) {
                        fileInputRef.current.value = '';
                      }
                    }}
                  >
                    <i className="fas fa-times"></i>
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Form Actions */}
          <div className="form-actions">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={onCancel}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn btn-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <i className="fas fa-spinner fa-spin"></i>
                  Creating Bug Report...
                </>
              ) : (
                <>
                  <i className="fas fa-plus"></i>
                  Create Bug Report
                </>
              )}
            </button>
          </div>
        </form>

        <style jsx>{`
          .new-bug-form-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.7);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            padding: 20px;
          }

          .new-bug-form-container {
            background: white;
            border-radius: 12px;
            max-width: 800px;
            width: 100%;
            max-height: 90vh;
            overflow-y: auto;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
          }

          .form-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 24px;
            border-bottom: 1px solid #dee2e6;
            position: sticky;
            top: 0;
            background: white;
            z-index: 10;
          }

          .form-header h2 {
            color: #212529;
            font-size: 1.5rem;
            font-weight: 600;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 10px;
          }

          .form-header h2 i {
            color: #dc3545;
          }

          .close-btn {
            background: none;
            border: none;
            font-size: 1.5rem;
            color: #6c757d;
            cursor: pointer;
            padding: 8px;
            border-radius: 4px;
            transition: all 0.2s ease;
          }

          .close-btn:hover {
            background: #f8f9fa;
            color: #495057;
          }

          .bug-form {
            padding: 24px;
          }

          .form-section {
            margin-bottom: 32px;
          }

          .form-section h3 {
            color: #495057;
            font-size: 1.25rem;
            font-weight: 600;
            margin: 0 0 20px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid #e9ecef;
          }

          .form-group {
            margin-bottom: 20px;
          }

          .form-row {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
          }

          .form-group label {
            display: block;
            color: #495057;
            font-weight: 500;
            margin-bottom: 6px;
            font-size: 0.95rem;
          }

          .required {
            color: #dc3545;
          }

          .form-group input,
          .form-group select,
          .form-group textarea {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #ced4da;
            border-radius: 6px;
            font-size: 0.95rem;
            font-family: inherit;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
          }

          .form-group input:focus,
          .form-group select:focus,
          .form-group textarea:focus {
            outline: none;
            border-color: #007bff;
            box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
          }

          .form-group input.error,
          .form-group textarea.error {
            border-color: #dc3545;
          }

          .error-message {
            color: #dc3545;
            font-size: 0.85rem;
            margin-top: 4px;
          }

          .char-count {
            text-align: right;
            font-size: 0.8rem;
            color: #6c757d;
            margin-top: 4px;
          }

          .tag-selector {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 8px;
          }

          .tag-btn {
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            color: #495057;
            padding: 6px 12px;
            border-radius: 16px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: all 0.2s ease;
          }

          .tag-btn:hover {
            background: #e9ecef;
          }

          .tag-btn.selected {
            background: #007bff;
            color: white;
            border-color: #007bff;
          }

          .reproduction-step {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 12px;
          }

          .step-number {
            min-width: 24px;
            height: 24px;
            background: #007bff;
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.8rem;
            font-weight: 600;
          }

          .step-input {
            flex: 1;
            margin: 0 !important;
          }

          .remove-step-btn {
            background: #dc3545;
            color: white;
            border: none;
            width: 32px;
            height: 32px;
            border-radius: 4px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
          }

          .remove-step-btn:hover {
            background: #c82333;
          }

          .add-step-btn {
            background: #28a745;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.9rem;
            transition: all 0.2s ease;
          }

          .add-step-btn:hover {
            background: #218838;
          }

          .auto-fill-section {
            margin-bottom: 20px;
          }

          .auto-fill-btn {
            background: #17a2b8;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.9rem;
            transition: all 0.2s ease;
          }

          .auto-fill-btn:hover {
            background: #138496;
          }

          .environment-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
          }

          .file-input {
            padding: 8px 0 !important;
          }

          .file-info {
            font-size: 0.8rem;
            color: #6c757d;
            margin-top: 4px;
          }

          .file-preview {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 8px;
            padding: 8px 12px;
            background: #f8f9fa;
            border-radius: 4px;
            font-size: 0.9rem;
          }

          .file-preview i {
            color: #007bff;
          }

          .remove-file-btn {
            background: none;
            border: none;
            color: #dc3545;
            cursor: pointer;
            padding: 4px;
            border-radius: 4px;
            margin-left: auto;
          }

          .remove-file-btn:hover {
            background: #f8d7da;
          }

          .form-actions {
            display: flex;
            justify-content: flex-end;
            gap: 12px;
            padding-top: 24px;
            border-top: 1px solid #dee2e6;
            margin-top: 32px;
          }

          .btn {
            padding: 12px 24px;
            border-radius: 6px;
            border: none;
            font-weight: 500;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s ease;
            font-size: 0.95rem;
          }

          .btn-primary {
            background: #007bff;
            color: white;
          }

          .btn-primary:hover:not(:disabled) {
            background: #0056b3;
          }

          .btn-secondary {
            background: #6c757d;
            color: white;
          }

          .btn-secondary:hover:not(:disabled) {
            background: #545b62;
          }

          .btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
          }

          @media (max-width: 768px) {
            .new-bug-form-overlay {
              padding: 10px;
            }

            .form-header {
              padding: 16px;
            }

            .bug-form {
              padding: 16px;
            }

            .form-row {
              grid-template-columns: 1fr;
              gap: 16px;
            }

            .environment-grid {
              grid-template-columns: 1fr;
              gap: 16px;
            }

            .form-actions {
              flex-direction: column-reverse;
            }

            .btn {
              width: 100%;
              justify-content: center;
            }

            .reproduction-step {
              flex-direction: column;
              align-items: stretch;
              gap: 8px;
            }

            .step-number {
              align-self: flex-start;
            }
          }
        `}</style>
      </div>
    </div>
  );
};

export default NewBugForm;