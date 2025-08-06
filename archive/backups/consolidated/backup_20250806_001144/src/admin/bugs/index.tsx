/**
 * Admin Bug Tracker Dashboard - Batch 173
 * Internal-only interface for managing bug reports at /admin/bugs
 */

import React, { useState, useEffect, useMemo } from 'react';
import { BugEntryCard } from '../../components/BugEntryCard';

// Type definitions
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

interface BugData {
  bug_reports: BugReport[];
  metadata: {
    totalBugs: number;
    openBugs: number;
    inProgressBugs: number;
    resolvedBugs: number;
    lastUpdated: string;
    nextBugId: string;
  };
  config: {
    severityLevels: string[];
    statusTypes: string[];
    priorityLevels: string[];
    tagCategories: string[];
    assignableDevs: Array<{id: string, name: string, role: string}>;
  };
}

interface FilterState {
  status: string;
  severity: string;
  priority: string;
  assignee: string;
  tags: string[];
  searchTerm: string;
}

export const AdminBugsDashboard: React.FC = () => {
  const [bugData, setBugData] = useState<BugData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showNewBugForm, setShowNewBugForm] = useState(false);
  const [filters, setFilters] = useState<FilterState>({
    status: 'all',
    severity: 'all',
    priority: 'all',
    assignee: 'all',
    tags: [],
    searchTerm: ''
  });
  const [sortBy, setSortBy] = useState<'date' | 'priority' | 'severity'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Load bug data
  useEffect(() => {
    loadBugData();
  }, []);

  const loadBugData = async () => {
    try {
      setLoading(true);
      // In a real implementation, this would be an API call
      // For now, we'll simulate loading the JSON data
      const response = await fetch('/src/data/bugs.json');
      if (!response.ok) {
        throw new Error('Failed to load bug data');
      }
      const data: BugData = await response.json();
      setBugData(data);
    } catch (err) {
      console.error('Error loading bug data:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
      // Fallback to mock data for demo
      setBugData(mockBugData);
    } finally {
      setLoading(false);
    }
  };

  // Filter and sort bugs
  const filteredAndSortedBugs = useMemo(() => {
    if (!bugData?.bug_reports) return [];

    let filtered = bugData.bug_reports.filter(bug => {
      // Status filter
      if (filters.status !== 'all' && bug.status !== filters.status) return false;
      
      // Severity filter  
      if (filters.severity !== 'all' && bug.severity !== filters.severity) return false;
      
      // Priority filter
      if (filters.priority !== 'all' && bug.priority !== filters.priority) return false;
      
      // Assignee filter
      if (filters.assignee !== 'all') {
        if (filters.assignee === 'unassigned' && bug.assignedTo) return false;
        if (filters.assignee !== 'unassigned' && bug.assignedTo !== filters.assignee) return false;
      }
      
      // Tags filter
      if (filters.tags.length > 0 && !filters.tags.some(tag => bug.tags.includes(tag))) return false;
      
      // Search term filter
      if (filters.searchTerm) {
        const searchTerm = filters.searchTerm.toLowerCase();
        return (
          bug.title.toLowerCase().includes(searchTerm) ||
          bug.description.toLowerCase().includes(searchTerm) ||
          bug.id.toLowerCase().includes(searchTerm) ||
          bug.tags.some(tag => tag.toLowerCase().includes(searchTerm))
        );
      }
      
      return true;
    });

    // Sort bugs
    filtered.sort((a, b) => {
      let comparison = 0;
      
      switch (sortBy) {
        case 'date':
          comparison = new Date(a.lastUpdated).getTime() - new Date(b.lastUpdated).getTime();
          break;
        case 'priority':
          const priorityOrder = ['P0', 'P1', 'P2', 'P3'];
          comparison = priorityOrder.indexOf(a.priority) - priorityOrder.indexOf(b.priority);
          break;
        case 'severity':
          const severityOrder = ['critical', 'high', 'medium', 'low'];
          comparison = severityOrder.indexOf(a.severity) - severityOrder.indexOf(b.severity);
          break;
      }
      
      return sortOrder === 'asc' ? comparison : -comparison;
    });

    return filtered;
  }, [bugData, filters, sortBy, sortOrder]);

  // Handle bug status change
  const handleStatusChange = (bugId: string, newStatus: string) => {
    if (!bugData) return;
    
    const updatedBugs = bugData.bug_reports.map(bug => 
      bug.id === bugId 
        ? { ...bug, status: newStatus as any, lastUpdated: new Date().toISOString() }
        : bug
    );
    
    setBugData({
      ...bugData,
      bug_reports: updatedBugs
    });
  };

  // Handle bug assignment change
  const handleAssignmentChange = (bugId: string, assignee: string | null) => {
    if (!bugData) return;
    
    const updatedBugs = bugData.bug_reports.map(bug =>
      bug.id === bugId 
        ? { ...bug, assignedTo: assignee, lastUpdated: new Date().toISOString() }
        : bug
    );
    
    setBugData({
      ...bugData,
      bug_reports: updatedBugs
    });
  };

  // Handle priority change
  const handlePriorityChange = (bugId: string, priority: string) => {
    if (!bugData) return;
    
    const updatedBugs = bugData.bug_reports.map(bug =>
      bug.id === bugId 
        ? { ...bug, priority: priority as any, lastUpdated: new Date().toISOString() }
        : bug
    );
    
    setBugData({
      ...bugData,
      bug_reports: updatedBugs
    });
  };

  // Handle adding comment
  const handleAddComment = (bugId: string, comment: string) => {
    if (!bugData) return;
    
    const newComment: BugComment = {
      id: `comment-${Date.now()}`,
      author: 'current-user', // In real app, get from auth context
      date: new Date().toISOString(),
      content: comment
    };
    
    const updatedBugs = bugData.bug_reports.map(bug =>
      bug.id === bugId 
        ? { 
            ...bug, 
            comments: [...bug.comments, newComment],
            lastUpdated: new Date().toISOString() 
          }
        : bug
    );
    
    setBugData({
      ...bugData,
      bug_reports: updatedBugs
    });
  };

  // Handle bug edit
  const handleEditBug = (bugId: string) => {
    // In a real implementation, this would open an edit modal
    console.log('Edit bug:', bugId);
  };

  // Handle bug delete
  const handleDeleteBug = (bugId: string) => {
    if (!bugData || !confirm('Are you sure you want to delete this bug report?')) return;
    
    const updatedBugs = bugData.bug_reports.filter(bug => bug.id !== bugId);
    setBugData({
      ...bugData,
      bug_reports: updatedBugs
    });
  };

  // Handle tag filter toggle
  const handleTagToggle = (tag: string) => {
    setFilters(prev => ({
      ...prev,
      tags: prev.tags.includes(tag)
        ? prev.tags.filter(t => t !== tag)
        : [...prev.tags, tag]
    }));
  };

  // Export bugs to JSON
  const handleExportBugs = () => {
    if (!bugData) return;
    
    const exportData = {
      exported_date: new Date().toISOString(),
      total_bugs: filteredAndSortedBugs.length,
      bugs: filteredAndSortedBugs
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { 
      type: 'application/json' 
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `bug-report-export-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    URL.revokeObjectURL(url);
  };

  // Calculate statistics
  const statistics = useMemo(() => {
    if (!bugData) return null;
    
    const bugs = filteredAndSortedBugs;
    return {
      total: bugs.length,
      open: bugs.filter(b => b.status === 'open').length,
      inProgress: bugs.filter(b => b.status === 'in-progress').length,
      resolved: bugs.filter(b => b.status === 'resolved').length,
      critical: bugs.filter(b => b.severity === 'critical').length,
      p0: bugs.filter(b => b.priority === 'P0').length,
      unassigned: bugs.filter(b => !b.assignedTo).length
    };
  }, [filteredAndSortedBugs, bugData]);

  if (loading) {
    return (
      <div className="admin-bugs-dashboard">
        <div className="loading-state">
          <div className="loading-spinner">
            <i className="fas fa-spinner fa-spin"></i>
            <p>Loading bug reports...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="admin-bugs-dashboard">
        <div className="error-state">
          <div className="error-message">
            <i className="fas fa-exclamation-triangle"></i>
            <h3>Error Loading Bug Reports</h3>
            <p>{error}</p>
            <button onClick={loadBugData} className="retry-btn">
              <i className="fas fa-redo"></i> Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-bugs-dashboard">
      <div className="dashboard-header">
        <div className="header-content">
          <h1>
            <i className="fas fa-bug"></i>
            Bug Tracker Dashboard
          </h1>
          <p>Internal bug report management for SWGDB and MS11 systems</p>
        </div>
        <div className="header-actions">
          <button 
            className="btn btn-primary"
            onClick={() => setShowNewBugForm(true)}
          >
            <i className="fas fa-plus"></i>
            New Bug Report
          </button>
          <button 
            className="btn btn-secondary"
            onClick={handleExportBugs}
            disabled={filteredAndSortedBugs.length === 0}
          >
            <i className="fas fa-download"></i>
            Export ({filteredAndSortedBugs.length})
          </button>
        </div>
      </div>

      {/* Statistics Cards */}
      {statistics && (
        <div className="statistics-section">
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">
                <i className="fas fa-list"></i>
              </div>
              <div className="stat-content">
                <div className="stat-number">{statistics.total}</div>
                <div className="stat-label">Total Bugs</div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon open">
                <i className="fas fa-folder-open"></i>
              </div>
              <div className="stat-content">
                <div className="stat-number">{statistics.open}</div>
                <div className="stat-label">Open</div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon in-progress">
                <i className="fas fa-spinner"></i>
              </div>
              <div className="stat-content">
                <div className="stat-number">{statistics.inProgress}</div>
                <div class="stat-label">In Progress</div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon critical">
                <i className="fas fa-exclamation-triangle"></i>
              </div>
              <div className="stat-content">
                <div className="stat-number">{statistics.critical}</div>
                <div className="stat-label">Critical</div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon p0">
                <i className="fas fa-fire"></i>
              </div>
              <div className="stat-content">
                <div className="stat-number">{statistics.p0}</div>
                <div className="stat-label">P0 Priority</div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon unassigned">
                <i className="fas fa-user-slash"></i>
              </div>
              <div className="stat-content">
                <div className="stat-number">{statistics.unassigned}</div>
                <div className="stat-label">Unassigned</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filters and Search */}
      <div className="filters-section">
        <div className="filters-header">
          <h3>
            <i className="fas fa-filter"></i>
            Filters & Search
          </h3>
          <button 
            className="clear-filters-btn"
            onClick={() => setFilters({
              status: 'all',
              severity: 'all', 
              priority: 'all',
              assignee: 'all',
              tags: [],
              searchTerm: ''
            })}
          >
            <i className="fas fa-times"></i>
            Clear All
          </button>
        </div>

        <div className="filters-content">
          <div className="filter-row">
            <div className="filter-group">
              <label>Search:</label>
              <input
                type="text"
                placeholder="Search bugs..."
                value={filters.searchTerm}
                onChange={(e) => setFilters(prev => ({ ...prev, searchTerm: e.target.value }))}
                className="search-input"
              />
            </div>

            <div className="filter-group">
              <label>Status:</label>
              <select
                value={filters.status}
                onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
              >
                <option value="all">All Status</option>
                <option value="open">Open</option>
                <option value="in-progress">In Progress</option>
                <option value="resolved">Resolved</option>
                <option value="closed">Closed</option>
                <option value="wont-fix">Won't Fix</option>
              </select>
            </div>

            <div className="filter-group">
              <label>Severity:</label>
              <select
                value={filters.severity}
                onChange={(e) => setFilters(prev => ({ ...prev, severity: e.target.value }))}
              >
                <option value="all">All Severity</option>
                <option value="critical">Critical</option>
                <option value="high">High</option>
                <option value="medium">Medium</option>
                <option value="low">Low</option>
              </select>
            </div>

            <div className="filter-group">
              <label>Priority:</label>
              <select
                value={filters.priority} 
                onChange={(e) => setFilters(prev => ({ ...prev, priority: e.target.value }))}
              >
                <option value="all">All Priority</option>
                <option value="P0">P0 - Critical</option>
                <option value="P1">P1 - High</option>
                <option value="P2">P2 - Medium</option>
                <option value="P3">P3 - Low</option>
              </select>
            </div>

            <div className="filter-group">
              <label>Assignee:</label>
              <select
                value={filters.assignee}
                onChange={(e) => setFilters(prev => ({ ...prev, assignee: e.target.value }))}
              >
                <option value="all">All Assignees</option>
                <option value="unassigned">Unassigned</option>
                {bugData?.config.assignableDevs.map(dev => (
                  <option key={dev.id} value={dev.id}>{dev.name}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Tag filters */}
          <div className="tag-filters">
            <label>Tags:</label>
            <div className="tag-filter-buttons">
              {bugData?.config.tagCategories.map(tag => (
                <button
                  key={tag}
                  className={`tag-filter-btn ${filters.tags.includes(tag) ? 'active' : ''}`}
                  onClick={() => handleTagToggle(tag)}
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Sort Controls */}
      <div className="sort-section">
        <div className="sort-controls">
          <label>Sort by:</label>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
          >
            <option value="date">Last Updated</option>
            <option value="priority">Priority</option>
            <option value="severity">Severity</option>
          </select>
          
          <button
            className={`sort-order-btn ${sortOrder}`}
            onClick={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')}
            title={`Sort ${sortOrder === 'asc' ? 'Descending' : 'Ascending'}`}
          >
            <i className={`fas fa-sort-amount-${sortOrder === 'desc' ? 'down' : 'up'}`}></i>
            {sortOrder === 'asc' ? 'Ascending' : 'Descending'}
          </button>
        </div>
        
        <div className="results-info">
          Showing {filteredAndSortedBugs.length} of {bugData?.bug_reports.length || 0} bugs
        </div>
      </div>

      {/* Bug List */}
      <div className="bugs-list">
        {filteredAndSortedBugs.length === 0 ? (
          <div className="no-bugs-message">
            <i className="fas fa-search"></i>
            <h3>No bugs found</h3>
            <p>Try adjusting your filters or search terms.</p>
          </div>
        ) : (
          filteredAndSortedBugs.map(bug => (
            <BugEntryCard
              key={bug.id}
              bug={bug}
              onStatusChange={handleStatusChange}
              onAssignmentChange={handleAssignmentChange}
              onPriorityChange={handlePriorityChange}
              onAddComment={handleAddComment}
              onEdit={handleEditBug}
              onDelete={handleDeleteBug}
              assignableDevs={bugData?.config.assignableDevs || []}
            />
          ))
        )}
      </div>

      <style jsx>{`
        .admin-bugs-dashboard {
          max-width: 1400px;
          margin: 0 auto;
          padding: 20px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .loading-state,
        .error-state {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 400px;
        }

        .loading-spinner,
        .error-message {
          text-align: center;
          color: #6c757d;
        }

        .loading-spinner i {
          font-size: 2rem;
          margin-bottom: 15px;
          color: #007bff;
        }

        .error-message i {
          font-size: 3rem;
          margin-bottom: 15px;
          color: #dc3545;
        }

        .retry-btn {
          background: #007bff;
          color: white;
          border: none;
          padding: 10px 20px;
          border-radius: 4px;
          cursor: pointer;
          margin-top: 15px;
        }

        .dashboard-header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          margin-bottom: 30px;
          padding-bottom: 20px;
          border-bottom: 2px solid #e9ecef;
        }

        .header-content h1 {
          color: #212529;
          font-size: 2rem;
          font-weight: 700;
          margin: 0 0 8px 0;
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .header-content h1 i {
          color: #dc3545;
        }

        .header-content p {
          color: #6c757d;
          margin: 0;
          font-size: 1.1rem;
        }

        .header-actions {
          display: flex;
          gap: 12px;
        }

        .btn {
          padding: 10px 20px;
          border-radius: 6px;
          border: none;
          font-weight: 500;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 8px;
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

        .btn-secondary:hover:not(:disabled) {
          background: #545b62;
        }

        .btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .statistics-section {
          margin-bottom: 30px;
        }

        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
          gap: 20px;
        }

        .stat-card {
          background: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          padding: 20px;
          display: flex;
          align-items: center;
          gap: 15px;
        }

        .stat-icon {
          width: 48px;
          height: 48px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 1.5rem;
          color: white;
          background: #6c757d;
        }

        .stat-icon.open { background: #28a745; }
        .stat-icon.in-progress { background: #007bff; }
        .stat-icon.critical { background: #dc3545; }
        .stat-icon.p0 { background: #fd7e14; }
        .stat-icon.unassigned { background: #6c757d; }

        .stat-content {
          flex: 1;
        }

        .stat-number {
          font-size: 1.75rem;
          font-weight: 700;
          color: #212529;
          line-height: 1;
        }

        .stat-label {
          color: #6c757d;
          font-size: 0.9rem;
          margin-top: 4px;
        }

        .filters-section {
          background: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
          padding: 20px;
          margin-bottom: 20px;
        }

        .filters-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
        }

        .filters-header h3 {
          color: #212529;
          font-size: 1.25rem;
          font-weight: 600;
          margin: 0;
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .clear-filters-btn {
          background: #f8f9fa;
          color: #6c757d;
          border: 1px solid #dee2e6;
          padding: 6px 12px;
          border-radius: 4px;
          cursor: pointer;
          font-size: 0.9rem;
          display: flex;
          align-items: center;
          gap: 6px;
        }

        .clear-filters-btn:hover {
          background: #e9ecef;
        }

        .filter-row {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 20px;
          margin-bottom: 20px;
        }

        .filter-group {
          display: flex;
          flex-direction: column;
          gap: 6px;
        }

        .filter-group label {
          font-weight: 500;
          color: #495057;
          font-size: 0.9rem;
        }

        .filter-group select,
        .search-input {
          padding: 8px 12px;
          border: 1px solid #ced4da;
          border-radius: 4px;
          font-size: 0.9rem;
        }

        .filter-group select:focus,
        .search-input:focus {
          outline: none;
          border-color: #007bff;
          box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
        }

        .tag-filters {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .tag-filters label {
          font-weight: 500;
          color: #495057;
          font-size: 0.9rem;
        }

        .tag-filter-buttons {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }

        .tag-filter-btn {
          background: #f8f9fa;
          border: 1px solid #dee2e6;
          color: #495057;
          padding: 6px 12px;
          border-radius: 16px;
          cursor: pointer;
          font-size: 0.85rem;
          transition: all 0.2s ease;
        }

        .tag-filter-btn:hover {
          background: #e9ecef;
        }

        .tag-filter-btn.active {
          background: #007bff;
          color: white;
          border-color: #007bff;
        }

        .sort-section {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
          padding: 15px 20px;
          background: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .sort-controls {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .sort-controls label {
          font-weight: 500;
          color: #495057;
        }

        .sort-controls select {
          padding: 6px 10px;
          border: 1px solid #ced4da;
          border-radius: 4px;
          font-size: 0.9rem;
        }

        .sort-order-btn {
          background: #f8f9fa;
          border: 1px solid #dee2e6;
          color: #495057;
          padding: 6px 12px;
          border-radius: 4px;
          cursor: pointer;
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 0.9rem;
        }

        .sort-order-btn:hover {
          background: #e9ecef;
        }

        .results-info {
          color: #6c757d;
          font-size: 0.9rem;
        }

        .bugs-list {
          margin-top: 20px;
        }

        .no-bugs-message {
          text-align: center;
          padding: 60px 20px;
          color: #6c757d;
        }

        .no-bugs-message i {
          font-size: 3rem;
          margin-bottom: 20px;
          opacity: 0.5;
        }

        .no-bugs-message h3 {
          color: #495057;
          margin-bottom: 10px;
        }

        @media (max-width: 768px) {
          .dashboard-header {
            flex-direction: column;
            gap: 20px;
          }

          .header-actions {
            width: 100%;
            justify-content: stretch;
          }

          .header-actions .btn {
            flex: 1;
            justify-content: center;
          }

          .stats-grid {
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 15px;
          }

          .stat-card {
            flex-direction: column;
            text-align: center;
            gap: 10px;
          }

          .filter-row {
            grid-template-columns: 1fr;
            gap: 15px;
          }

          .sort-section {
            flex-direction: column;
            gap: 15px;
            align-items: stretch;
          }

          .sort-controls {
            justify-content: center;
          }

          .results-info {
            text-align: center;
          }
        }
      `}</style>
    </div>
  );
};

// Mock data for demo purposes when API fails
const mockBugData: BugData = {
  bug_reports: [
    {
      id: "BUG-001",
      title: "MS11 bot fails to detect vendor NPCs in Mos Eisley",
      severity: "high",
      description: "The bot's NPC detection system is not properly identifying vendor NPCs in the Mos Eisley cantina area.",
      screenshot: null,
      status: "open",
      tags: ["Bot", "NPC Detection"],
      assignedTo: "dev-alice",
      priority: "P1",
      reportedBy: "user-john",
      reportedDate: "2025-01-15T10:30:00Z",
      lastUpdated: "2025-01-15T14:22:00Z",
      reproductionSteps: [
        "Navigate MS11 bot to Mos Eisley cantina",
        "Attempt to initiate vendor trading sequence"
      ],
      environment: {
        botVersion: "v2.1.4",
        gameServer: "Restoration III"
      },
      comments: []
    }
  ],
  metadata: {
    totalBugs: 1,
    openBugs: 1,
    inProgressBugs: 0,
    resolvedBugs: 0,
    lastUpdated: "2025-01-15T14:22:00Z",
    nextBugId: "BUG-002"
  },
  config: {
    severityLevels: ["critical", "high", "medium", "low"],
    statusTypes: ["open", "in-progress", "resolved", "closed", "wont-fix"],
    priorityLevels: ["P0", "P1", "P2", "P3"],
    tagCategories: ["Bot", "Website", "Content"],
    assignableDevs: [
      {id: "dev-alice", name: "Alice Johnson", role: "Senior Bot Developer"}
    ]
  }
};

export default AdminBugsDashboard;