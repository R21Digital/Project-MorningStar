/**
 * BugEntryCard Component - Batch 173
 * Displays individual bug reports in card format with actions
 */

import React, { useState } from 'react';

interface BugComment {
  id: string;
  author: string;
  date: string;
  content: string;
}

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

interface BugReport {
  id: string;
  title: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  description: string;
  screenshot?: string | null;
  status: 'open' | 'in-progress' | 'resolved' | 'closed' | 'wont-fix';
  tags: string[];
  assignedTo?: string | null;
  priority: 'P0' | 'P1' | 'P2' | 'P3';
  reportedBy: string;
  reportedDate: string;
  lastUpdated: string;
  reproductionSteps: string[];
  environment: BugEnvironment;
  comments: BugComment[];
}

interface BugEntryCardProps {
  bug: BugReport;
  onStatusChange: (bugId: string, newStatus: string) => void;
  onAssignmentChange: (bugId: string, assignee: string | null) => void;
  onPriorityChange: (bugId: string, priority: string) => void;
  onAddComment: (bugId: string, comment: string) => void;
  onEdit: (bugId: string) => void;
  onDelete: (bugId: string) => void;
  assignableDevs: Array<{id: string, name: string, role: string}>;
  className?: string;
}

const SEVERITY_COLORS = {
  critical: '#dc3545',
  high: '#fd7e14', 
  medium: '#ffc107',
  low: '#28a745'
};

const STATUS_COLORS = {
  open: '#6c757d',
  'in-progress': '#007bff',
  resolved: '#28a745',
  closed: '#6c757d',
  'wont-fix': '#dc3545'
};

const PRIORITY_COLORS = {
  P0: '#dc3545',
  P1: '#fd7e14',
  P2: '#ffc107', 
  P3: '#28a745'
};

export const BugEntryCard: React.FC<BugEntryCardProps> = ({
  bug,
  onStatusChange,
  onAssignmentChange,
  onPriorityChange,
  onAddComment,
  onEdit,
  onDelete,
  assignableDevs,
  className = ''
}) => {
  const [showDetails, setShowDetails] = useState(false);
  const [showComments, setShowComments] = useState(false);
  const [newComment, setNewComment] = useState('');
  const [isAddingComment, setIsAddingComment] = useState(false);

  const formatDate = (dateString: string) => {
    try {
      return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return dateString;
    }
  };

  const handleAddComment = () => {
    if (newComment.trim()) {
      onAddComment(bug.id, newComment.trim());
      setNewComment('');
      setIsAddingComment(false);
    }
  };

  const getAssigneeName = (assigneeId: string | null) => {
    if (!assigneeId) return 'Unassigned';
    const dev = assignableDevs.find(d => d.id === assigneeId);
    return dev ? dev.name : assigneeId;
  };

  return (
    <div className={`bug-entry-card ${className}`}>
      <div className="bug-card-header">
        <div className="bug-card-title-section">
          <div className="bug-id-badges">
            <span className="bug-id">{bug.id}</span>
            <span 
              className="severity-badge"
              style={{ backgroundColor: SEVERITY_COLORS[bug.severity] }}
            >
              {bug.severity.toUpperCase()}
            </span>
            <span 
              className="priority-badge"
              style={{ backgroundColor: PRIORITY_COLORS[bug.priority] }}
            >
              {bug.priority}
            </span>
          </div>
          <h3 className="bug-title">{bug.title}</h3>
        </div>
        <div className="bug-card-actions">
          <button 
            className="action-btn details-btn"
            onClick={() => setShowDetails(!showDetails)}
            title="Toggle details"
          >
            <i className={`fas fa-chevron-${showDetails ? 'up' : 'down'}`}></i>
          </button>
          <button 
            className="action-btn edit-btn"
            onClick={() => onEdit(bug.id)}
            title="Edit bug"
          >
            <i className="fas fa-edit"></i>
          </button>
          <button 
            className="action-btn delete-btn"
            onClick={() => onDelete(bug.id)}
            title="Delete bug"
          >
            <i className="fas fa-trash"></i>
          </button>
        </div>
      </div>

      <div className="bug-card-meta">
        <div className="bug-meta-item">
          <i className="fas fa-user"></i>
          <span>Reported by: {bug.reportedBy}</span>
        </div>
        <div className="bug-meta-item">
          <i className="fas fa-calendar"></i>
          <span>Created: {formatDate(bug.reportedDate)}</span>
        </div>
        <div className="bug-meta-item">
          <i className="fas fa-clock"></i>
          <span>Updated: {formatDate(bug.lastUpdated)}</span>
        </div>
      </div>

      <div className="bug-card-status-section">
        <div className="status-controls">
          <div className="control-group">
            <label htmlFor={`status-${bug.id}`}>Status:</label>
            <select
              id={`status-${bug.id}`}
              value={bug.status}
              onChange={(e) => onStatusChange(bug.id, e.target.value)}
              className="status-select"
              style={{ borderColor: STATUS_COLORS[bug.status] }}
            >
              <option value="open">Open</option>
              <option value="in-progress">In Progress</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
              <option value="wont-fix">Won't Fix</option>
            </select>
          </div>

          <div className="control-group">
            <label htmlFor={`assignee-${bug.id}`}>Assignee:</label>
            <select
              id={`assignee-${bug.id}`}
              value={bug.assignedTo || ''}
              onChange={(e) => onAssignmentChange(bug.id, e.target.value || null)}
              className="assignee-select"
            >
              <option value="">Unassigned</option>
              {assignableDevs.map(dev => (
                <option key={dev.id} value={dev.id}>
                  {dev.name} ({dev.role})
                </option>
              ))}
            </select>
          </div>

          <div className="control-group">
            <label htmlFor={`priority-${bug.id}`}>Priority:</label>
            <select
              id={`priority-${bug.id}`}
              value={bug.priority}
              onChange={(e) => onPriorityChange(bug.id, e.target.value)}
              className="priority-select"
              style={{ borderColor: PRIORITY_COLORS[bug.priority] }}
            >
              <option value="P0">P0 - Critical</option>
              <option value="P1">P1 - High</option>
              <option value="P2">P2 - Medium</option>
              <option value="P3">P3 - Low</option>
            </select>
          </div>
        </div>
      </div>

      <div className="bug-tags">
        {bug.tags.map((tag, index) => (
          <span key={index} className={`bug-tag tag-${tag.toLowerCase().replace(/\s+/g, '-')}`}>
            {tag}
          </span>
        ))}
      </div>

      <div className="bug-description">
        <p>{bug.description}</p>
      </div>

      {bug.screenshot && (
        <div className="bug-screenshot">
          <img 
            src={bug.screenshot} 
            alt={`Screenshot for ${bug.title}`}
            className="screenshot-image"
            onError={(e) => {
              const target = e.target as HTMLImageElement;
              target.style.display = 'none';
            }}
          />
        </div>
      )}

      {showDetails && (
        <div className="bug-details">
          <div className="details-section">
            <h4>Reproduction Steps:</h4>
            <ol className="reproduction-steps">
              {bug.reproductionSteps.map((step, index) => (
                <li key={index}>{step}</li>
              ))}
            </ol>
          </div>

          <div className="details-section">
            <h4>Environment:</h4>
            <div className="environment-details">
              {Object.entries(bug.environment).map(([key, value]) => (
                <div key={key} className="env-item">
                  <strong>{key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}:</strong>
                  <span>{value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="bug-comments-section">
        <div className="comments-header">
          <button 
            className="comments-toggle"
            onClick={() => setShowComments(!showComments)}
          >
            <i className={`fas fa-comment${bug.comments.length > 0 ? 's' : ''}`}></i>
            Comments ({bug.comments.length})
            <i className={`fas fa-chevron-${showComments ? 'up' : 'down'}`}></i>
          </button>
          <button 
            className="add-comment-btn"
            onClick={() => setIsAddingComment(!isAddingComment)}
          >
            <i className="fas fa-plus"></i>
            Add Comment
          </button>
        </div>

        {showComments && (
          <div className="comments-list">
            {bug.comments.map((comment) => (
              <div key={comment.id} className="comment-item">
                <div className="comment-header">
                  <strong className="comment-author">{comment.author}</strong>
                  <span className="comment-date">{formatDate(comment.date)}</span>
                </div>
                <div className="comment-content">{comment.content}</div>
              </div>
            ))}
          </div>
        )}

        {isAddingComment && (
          <div className="add-comment-form">
            <textarea
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              placeholder="Add a comment..."
              className="comment-textarea"
              rows={3}
            />
            <div className="comment-form-actions">
              <button 
                className="btn btn-primary"
                onClick={handleAddComment}
                disabled={!newComment.trim()}
              >
                Add Comment
              </button>
              <button 
                className="btn btn-secondary"
                onClick={() => {
                  setIsAddingComment(false);
                  setNewComment('');
                }}
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        .bug-entry-card {
          background: white;
          border-radius: 8px;
          border: 1px solid #dee2e6;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          margin-bottom: 20px;
          padding: 20px;
          transition: box-shadow 0.2s ease;
        }

        .bug-entry-card:hover {
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        .bug-card-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 15px;
        }

        .bug-card-title-section {
          flex: 1;
        }

        .bug-id-badges {
          display: flex;
          gap: 8px;
          margin-bottom: 8px;
          flex-wrap: wrap;
        }

        .bug-id {
          background: #f8f9fa;
          color: #495057;
          padding: 4px 8px;
          border-radius: 4px;
          font-family: 'Courier New', monospace;
          font-size: 0.85rem;
          font-weight: 600;
        }

        .severity-badge,
        .priority-badge {
          color: white;
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 0.75rem;
          font-weight: 600;
          text-transform: uppercase;
        }

        .bug-title {
          color: #212529;
          font-size: 1.25rem;
          font-weight: 600;
          margin: 0;
          line-height: 1.3;
        }

        .bug-card-actions {
          display: flex;
          gap: 8px;
        }

        .action-btn {
          background: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 4px;
          padding: 8px;
          cursor: pointer;
          transition: all 0.2s ease;
          width: 36px;
          height: 36px;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .action-btn:hover {
          background: #e9ecef;
        }

        .details-btn:hover {
          background: #007bff;
          color: white;
          border-color: #007bff;
        }

        .edit-btn:hover {
          background: #28a745;
          color: white;
          border-color: #28a745;
        }

        .delete-btn:hover {
          background: #dc3545;
          color: white;
          border-color: #dc3545;
        }

        .bug-card-meta {
          display: flex;
          gap: 20px;
          margin-bottom: 15px;
          flex-wrap: wrap;
        }

        .bug-meta-item {
          display: flex;
          align-items: center;
          gap: 6px;
          color: #6c757d;
          font-size: 0.9rem;
        }

        .bug-meta-item i {
          width: 16px;
        }

        .bug-card-status-section {
          margin-bottom: 15px;
        }

        .status-controls {
          display: flex;
          gap: 20px;
          flex-wrap: wrap;
        }

        .control-group {
          display: flex;
          flex-direction: column;
          gap: 4px;
          min-width: 150px;
        }

        .control-group label {
          font-size: 0.9rem;
          font-weight: 500;
          color: #495057;
        }

        .status-select,
        .assignee-select,
        .priority-select {
          padding: 6px 10px;
          border: 2px solid #dee2e6;
          border-radius: 4px;
          font-size: 0.9rem;
          background: white;
          cursor: pointer;
        }

        .status-select:focus,
        .assignee-select:focus,
        .priority-select:focus {
          outline: none;
          border-color: #007bff;
          box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
        }

        .bug-tags {
          display: flex;
          gap: 6px;
          margin-bottom: 15px;
          flex-wrap: wrap;
        }

        .bug-tag {
          background: #e9ecef;
          color: #495057;
          padding: 4px 8px;
          border-radius: 12px;
          font-size: 0.8rem;
          font-weight: 500;
        }

        .bug-tag.tag-bot {
          background: #d4edda;
          color: #155724;
        }

        .bug-tag.tag-website {
          background: #d1ecf1;
          color: #0c5460;
        }

        .bug-tag.tag-content {
          background: #fff3cd;
          color: #856404;
        }

        .bug-tag.tag-critical {
          background: #f8d7da;
          color: #721c24;
        }

        .bug-description {
          color: #495057;
          line-height: 1.5;
          margin-bottom: 15px;
        }

        .bug-screenshot {
          margin-bottom: 15px;
        }

        .screenshot-image {
          max-width: 100%;
          height: auto;
          border-radius: 4px;
          border: 1px solid #dee2e6;
          cursor: pointer;
        }

        .bug-details {
          background: #f8f9fa;
          border-radius: 6px;
          padding: 15px;
          margin-bottom: 15px;
        }

        .details-section {
          margin-bottom: 15px;
        }

        .details-section:last-child {
          margin-bottom: 0;
        }

        .details-section h4 {
          color: #495057;
          font-size: 1rem;
          font-weight: 600;
          margin-bottom: 8px;
        }

        .reproduction-steps {
          margin: 0;
          padding-left: 20px;
        }

        .reproduction-steps li {
          margin-bottom: 4px;
          color: #495057;
        }

        .environment-details {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 8px;
        }

        .env-item {
          display: flex;
          gap: 8px;
          font-size: 0.9rem;
        }

        .env-item strong {
          color: #495057;
          min-width: 120px;
        }

        .bug-comments-section {
          border-top: 1px solid #dee2e6;
          padding-top: 15px;
        }

        .comments-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 10px;
        }

        .comments-toggle {
          background: none;
          border: none;
          color: #495057;
          font-weight: 500;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .comments-toggle:hover {
          color: #007bff;
        }

        .add-comment-btn {
          background: #007bff;
          color: white;
          border: none;
          padding: 6px 12px;
          border-radius: 4px;
          font-size: 0.9rem;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 6px;
        }

        .add-comment-btn:hover {
          background: #0056b3;
        }

        .comments-list {
          margin-bottom: 15px;
        }

        .comment-item {
          background: #f8f9fa;
          border-radius: 6px;
          padding: 12px;
          margin-bottom: 10px;
        }

        .comment-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 6px;
        }

        .comment-author {
          color: #007bff;
          font-size: 0.9rem;
        }

        .comment-date {
          color: #6c757d;
          font-size: 0.8rem;
        }

        .comment-content {
          color: #495057;
          line-height: 1.4;
        }

        .add-comment-form {
          background: #f8f9fa;
          border-radius: 6px;
          padding: 15px;
        }

        .comment-textarea {
          width: 100%;
          border: 1px solid #ced4da;
          border-radius: 4px;
          padding: 8px 12px;
          font-family: inherit;
          font-size: 0.9rem;
          resize: vertical;
          margin-bottom: 10px;
        }

        .comment-textarea:focus {
          outline: none;
          border-color: #007bff;
          box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
        }

        .comment-form-actions {
          display: flex;
          gap: 10px;
        }

        .btn {
          padding: 8px 16px;
          border-radius: 4px;
          border: none;
          font-size: 0.9rem;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s ease;
        }

        .btn-primary {
          background: #007bff;
          color: white;
        }

        .btn-primary:hover:not(:disabled) {
          background: #0056b3;
        }

        .btn-primary:disabled {
          background: #6c757d;
          cursor: not-allowed;
        }

        .btn-secondary {
          background: #6c757d;
          color: white;
        }

        .btn-secondary:hover {
          background: #545b62;
        }

        @media (max-width: 768px) {
          .bug-card-header {
            flex-direction: column;
            gap: 10px;
          }

          .bug-card-actions {
            justify-content: flex-end;
          }

          .bug-card-meta {
            flex-direction: column;
            gap: 8px;
          }

          .status-controls {
            flex-direction: column;
            gap: 12px;
          }

          .control-group {
            min-width: auto;
          }

          .comments-header {
            flex-direction: column;
            gap: 10px;
            align-items: stretch;
          }

          .environment-details {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default BugEntryCard;