import React, { useState, useRef } from 'react';

interface BugReport {
  id: string;
  title: string;
  description: string;
  priority: 'Low' | 'Medium' | 'High';
  category: 'Bot' | 'Website' | 'Mod';
  screenshot_url?: string;
  user_agent: string;
  page_url: string;
  submitted_at: string;
  status: 'New' | 'In Progress' | 'Resolved' | 'Closed';
  assigned_to?: string;
  notes?: string;
}

interface BugReportFormProps {
  onSubmit?: (report: BugReport) => void;
}

const BugReportForm: React.FC<BugReportFormProps> = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'Medium' as const,
    category: 'Website' as const,
  });
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitStatus, setSubmitStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [screenshotFile, setScreenshotFile] = useState<File | null>(null);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type
      if (!file.type.startsWith('image/')) {
        setErrorMessage('Please select an image file (PNG, JPG, GIF)');
        return;
      }
      
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        setErrorMessage('File size must be less than 5MB');
        return;
      }
      
      setScreenshotFile(file);
      setErrorMessage('');
    }
  };

  const generateId = () => {
    return `bug_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.title.trim() || !formData.description.trim()) {
      setErrorMessage('Please fill in all required fields');
      return;
    }

    setIsSubmitting(true);
    setSubmitStatus('idle');
    setErrorMessage('');

    try {
      // Create the bug report object
      const bugReport: BugReport = {
        id: generateId(),
        title: formData.title.trim(),
        description: formData.description.trim(),
        priority: formData.priority,
        category: formData.category,
        user_agent: navigator.userAgent,
        page_url: window.location.href,
        submitted_at: new Date().toISOString(),
        status: 'New',
      };

      // Handle file upload if present
      if (screenshotFile) {
        // In a real implementation, you would upload to a server
        // For now, we'll create a data URL
        const reader = new FileReader();
        reader.onload = (e) => {
          bugReport.screenshot_url = e.target?.result as string;
          submitReport(bugReport);
        };
        reader.readAsDataURL(screenshotFile);
      } else {
        submitReport(bugReport);
      }
    } catch (error) {
      console.error('Error submitting bug report:', error);
      setSubmitStatus('error');
      setErrorMessage('Failed to submit bug report. Please try again.');
      setIsSubmitting(false);
    }
  };

  const submitReport = async (bugReport: BugReport) => {
    try {
      // In a real implementation, this would be an API call
      // For now, we'll simulate the submission
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Call the onSubmit prop if provided
      if (onSubmit) {
        onSubmit(bugReport);
      }
      
      setSubmitStatus('success');
      
      // Reset form
      setFormData({
        title: '',
        description: '',
        priority: 'Medium',
        category: 'Website',
      });
      setScreenshotFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
      
      // Show success message for 3 seconds
      setTimeout(() => {
        setSubmitStatus('idle');
      }, 3000);
      
    } catch (error) {
      console.error('Error submitting report:', error);
      setSubmitStatus('error');
      setErrorMessage('Failed to submit bug report. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      priority: 'Medium',
      category: 'Website',
    });
    setScreenshotFile(null);
    setErrorMessage('');
    setSubmitStatus('idle');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="bug-report-form">
      <div className="card">
        <div className="card-header">
          <h2 className="mb-0">
            <i className="fas fa-bug me-2"></i>
            Report a Bug
          </h2>
          <p className="text-muted mb-0">
            Help us improve SWGDB by reporting bugs and issues you encounter.
          </p>
        </div>
        
        <div className="card-body">
          {submitStatus === 'success' && (
            <div className="alert alert-success alert-dismissible fade show" role="alert">
              <i className="fas fa-check-circle me-2"></i>
              <strong>Thank you!</strong> Your bug report has been submitted successfully.
              <button type="button" className="btn-close" onClick={() => setSubmitStatus('idle')}></button>
            </div>
          )}
          
          {submitStatus === 'error' && (
            <div className="alert alert-danger alert-dismissible fade show" role="alert">
              <i className="fas fa-exclamation-triangle me-2"></i>
              <strong>Error:</strong> {errorMessage}
              <button type="button" className="btn-close" onClick={() => setSubmitStatus('idle')}></button>
            </div>
          )}
          
          {errorMessage && submitStatus === 'idle' && (
            <div className="alert alert-warning alert-dismissible fade show" role="alert">
              <i className="fas fa-exclamation-triangle me-2"></i>
              {errorMessage}
              <button type="button" className="btn-close" onClick={() => setErrorMessage('')}></button>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="row">
              <div className="col-md-8">
                <div className="mb-3">
                  <label htmlFor="title" className="form-label">
                    <i className="fas fa-heading me-2"></i>
                    Bug Title <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    className="form-control"
                    id="title"
                    name="title"
                    value={formData.title}
                    onChange={handleInputChange}
                    placeholder="Brief description of the bug"
                    required
                    maxLength={100}
                  />
                  <div className="form-text">
                    Provide a clear, concise title that describes the issue
                  </div>
                </div>

                <div className="mb-3">
                  <label htmlFor="description" className="form-label">
                    <i className="fas fa-align-left me-2"></i>
                    Description <span className="text-danger">*</span>
                  </label>
                  <textarea
                    className="form-control"
                    id="description"
                    name="description"
                    rows={6}
                    value={formData.description}
                    onChange={handleInputChange}
                    placeholder="Please provide detailed information about the bug:
• What were you trying to do?
• What happened instead?
• Steps to reproduce the issue
• Any error messages you saw"
                    required
                    maxLength={2000}
                  ></textarea>
                  <div className="form-text">
                    Be as detailed as possible to help us understand and fix the issue
                  </div>
                </div>
              </div>

              <div className="col-md-4">
                <div className="mb-3">
                  <label htmlFor="priority" className="form-label">
                    <i className="fas fa-exclamation-triangle me-2"></i>
                    Priority
                  </label>
                  <select
                    className="form-select"
                    id="priority"
                    name="priority"
                    value={formData.priority}
                    onChange={handleInputChange}
                  >
                    <option value="Low">Low - Minor issue</option>
                    <option value="Medium">Medium - Moderate impact</option>
                    <option value="High">High - Critical issue</option>
                  </select>
                </div>

                <div className="mb-3">
                  <label htmlFor="category" className="form-label">
                    <i className="fas fa-tags me-2"></i>
                    Category
                  </label>
                  <select
                    className="form-select"
                    id="category"
                    name="category"
                    value={formData.category}
                    onChange={handleInputChange}
                  >
                    <option value="Website">Website</option>
                    <option value="Bot">Bot</option>
                    <option value="Mod">Mod</option>
                  </select>
                </div>

                <div className="mb-3">
                  <label htmlFor="screenshot" className="form-label">
                    <i className="fas fa-camera me-2"></i>
                    Screenshot (Optional)
                  </label>
                  <input
                    type="file"
                    className="form-control"
                    id="screenshot"
                    name="screenshot"
                    accept="image/*"
                    onChange={handleFileChange}
                    ref={fileInputRef}
                  />
                  <div className="form-text">
                    Upload a screenshot showing the issue (PNG, JPG, GIF, max 5MB)
                  </div>
                  {screenshotFile && (
                    <div className="mt-2">
                      <small className="text-success">
                        <i className="fas fa-check me-1"></i>
                        File selected: {screenshotFile.name}
                      </small>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="row mt-4">
              <div className="col-12">
                <div className="d-flex gap-2">
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                        Submitting...
                      </>
                    ) : (
                      <>
                        <i className="fas fa-paper-plane me-2"></i>
                        Submit Bug Report
                      </>
                    )}
                  </button>
                  
                  <button
                    type="button"
                    className="btn btn-outline-secondary"
                    onClick={resetForm}
                    disabled={isSubmitting}
                  >
                    <i className="fas fa-undo me-2"></i>
                    Reset Form
                  </button>
                </div>
              </div>
            </div>
          </form>
        </div>
      </div>

      <div className="mt-4">
        <div className="card">
          <div className="card-header">
            <h5 className="mb-0">
              <i className="fas fa-info-circle me-2"></i>
              Tips for Better Bug Reports
            </h5>
          </div>
          <div className="card-body">
            <ul className="list-unstyled mb-0">
              <li className="mb-2">
                <i className="fas fa-check text-success me-2"></i>
                <strong>Be specific:</strong> Include exact steps to reproduce the issue
              </li>
              <li className="mb-2">
                <i className="fas fa-check text-success me-2"></i>
                <strong>Include context:</strong> Mention your browser, operating system, and any relevant settings
              </li>
              <li className="mb-2">
                <i className="fas fa-check text-success me-2"></i>
                <strong>Add screenshots:</strong> Visual evidence helps us understand the problem faster
              </li>
              <li className="mb-2">
                <i className="fas fa-check text-success me-2"></i>
                <strong>Check for duplicates:</strong> Search existing reports before submitting
              </li>
              <li>
                <i className="fas fa-check text-success me-2"></i>
                <strong>Follow up:</strong> We may need additional information to resolve the issue
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BugReportForm; 