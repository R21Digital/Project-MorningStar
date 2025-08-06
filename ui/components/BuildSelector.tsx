import React, { useState, useEffect } from 'react';
import './BuildSelector.css';

interface BuildMetadata {
  id: string;
  name: string;
  description: string;
  category: string;
  specialization: string;
  difficulty: string;
  professions: string[];
  total_skills: number;
  avg_performance: number;
  best_performance: number;
  combat_style: string;
  notes: string[];
}

interface BuildSelectorProps {
  onBuildSelect?: (buildId: string) => void;
  selectedBuild?: string;
  showFilters?: boolean;
  showPerformance?: boolean;
}

const BuildSelector: React.FC<BuildSelectorProps> = ({
  onBuildSelect,
  selectedBuild,
  showFilters = true,
  showPerformance = true
}) => {
  const [builds, setBuilds] = useState<BuildMetadata[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filter states
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [specializationFilter, setSpecializationFilter] = useState<string>('all');
  const [difficultyFilter, setDifficultyFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState<string>('name');
  
  // Detail view state
  const [selectedBuildDetails, setSelectedBuildDetails] = useState<BuildMetadata | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    fetchBuilds();
  }, []);

  const fetchBuilds = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/builds');
      if (!response.ok) {
        throw new Error('Failed to fetch builds');
      }
      const data = await response.json();
      setBuilds(data.builds || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load builds');
    } finally {
      setLoading(false);
    }
  };

  const fetchBuildDetails = async (buildId: string) => {
    try {
      const response = await fetch(`/api/builds/${buildId}`);
      if (!response.ok) {
        throw new Error('Failed to fetch build details');
      }
      const data = await response.json();
      setSelectedBuildDetails(data);
      setShowDetails(true);
    } catch (err) {
      console.error('Error fetching build details:', err);
    }
  };

  const filteredBuilds = builds.filter(build => {
    // Category filter
    if (categoryFilter !== 'all' && build.category !== categoryFilter) {
      return false;
    }
    
    // Specialization filter
    if (specializationFilter !== 'all' && build.specialization !== specializationFilter) {
      return false;
    }
    
    // Difficulty filter
    if (difficultyFilter !== 'all' && build.difficulty !== difficultyFilter) {
      return false;
    }
    
    // Search term
    if (searchTerm && !build.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
        !build.description.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }
    
    return true;
  });

  const sortedBuilds = [...filteredBuilds].sort((a, b) => {
    switch (sortBy) {
      case 'name':
        return a.name.localeCompare(b.name);
      case 'performance':
        return b.avg_performance - a.avg_performance;
      case 'difficulty':
        const difficultyOrder = { 'easy': 1, 'medium': 2, 'hard': 3 };
        return difficultyOrder[a.difficulty as keyof typeof difficultyOrder] - 
               difficultyOrder[b.difficulty as keyof typeof difficultyOrder];
      case 'skills':
        return b.total_skills - a.total_skills;
      default:
        return 0;
    }
  });

  const handleBuildSelect = (buildId: string) => {
    onBuildSelect?.(buildId);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return '#4caf50';
      case 'medium': return '#ff9800';
      case 'hard': return '#f44336';
      default: return '#757575';
    }
  };

  const getPerformanceColor = (rating: number) => {
    if (rating >= 8) return '#4caf50';
    if (rating >= 6) return '#ff9800';
    return '#f44336';
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'combat': return '⚔️';
      case 'utility': return '🛠️';
      case 'support': return '🛡️';
      default: return '📋';
    }
  };

  if (loading) {
    return (
      <div className="build-selector">
        <div className="loading">Loading builds...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="build-selector">
        <div className="error">Error: {error}</div>
        <button onClick={fetchBuilds} className="retry-button">Retry</button>
      </div>
    );
  }

  return (
    <div className="build-selector">
      {/* Header */}
      <div className="build-selector-header">
        <h2>Community Builds</h2>
        <p>Select from pre-built combat and utility templates</p>
      </div>

      {/* Filters */}
      {showFilters && (
        <div className="build-filters">
          <div className="filter-row">
            <div className="filter-group">
              <label>Category:</label>
              <select 
                value={categoryFilter} 
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="filter-select"
              >
                <option value="all">All Categories</option>
                <option value="combat">Combat</option>
                <option value="utility">Utility</option>
                <option value="support">Support</option>
              </select>
            </div>

            <div className="filter-group">
              <label>Specialization:</label>
              <select 
                value={specializationFilter} 
                onChange={(e) => setSpecializationFilter(e.target.value)}
                className="filter-select"
              >
                <option value="all">All Specializations</option>
                <option value="pve">PvE</option>
                <option value="pvp">PvP</option>
                <option value="group">Group</option>
                <option value="solo">Solo</option>
                <option value="tank">Tank</option>
                <option value="farming">Farming</option>
              </select>
            </div>

            <div className="filter-group">
              <label>Difficulty:</label>
              <select 
                value={difficultyFilter} 
                onChange={(e) => setDifficultyFilter(e.target.value)}
                className="filter-select"
              >
                <option value="all">All Difficulties</option>
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>

            <div className="filter-group">
              <label>Sort by:</label>
              <select 
                value={sortBy} 
                onChange={(e) => setSortBy(e.target.value)}
                className="filter-select"
              >
                <option value="name">Name</option>
                <option value="performance">Performance</option>
                <option value="difficulty">Difficulty</option>
                <option value="skills">Skills</option>
              </select>
            </div>
          </div>

          <div className="search-group">
            <input
              type="text"
              placeholder="Search builds..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
          </div>
        </div>
      )}

      {/* Build Grid */}
      <div className="build-grid">
        {sortedBuilds.map((build) => (
          <div 
            key={build.id}
            className={`build-card ${selectedBuild === build.id ? 'selected' : ''}`}
            onClick={() => handleBuildSelect(build.id)}
          >
            <div className="build-card-header">
              <div className="build-icon">
                {getCategoryIcon(build.category)}
              </div>
              <div className="build-title">
                <h3>{build.name}</h3>
                <span 
                  className="difficulty-badge"
                  style={{ backgroundColor: getDifficultyColor(build.difficulty) }}
                >
                  {build.difficulty}
                </span>
              </div>
            </div>

            <div className="build-description">
              {build.description}
            </div>

            <div className="build-meta">
              <div className="build-professions">
                <strong>Professions:</strong> {build.professions.join(', ')}
              </div>
              <div className="build-combat">
                <strong>Style:</strong> {build.combat_style}
              </div>
              <div className="build-skills">
                <strong>Skills:</strong> {build.total_skills}
              </div>
            </div>

            {showPerformance && (
              <div className="build-performance">
                <div className="performance-bar">
                  <span>Performance:</span>
                  <div className="performance-fill" style={{ 
                    width: `${(build.avg_performance / 10) * 100}%`,
                    backgroundColor: getPerformanceColor(build.avg_performance)
                  }}></div>
                  <span className="performance-score">{build.avg_performance}/10</span>
                </div>
              </div>
            )}

            <div className="build-actions">
              <button 
                className="view-details-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  fetchBuildDetails(build.id);
                }}
              >
                View Details
              </button>
              <button 
                className="select-build-btn"
                onClick={(e) => {
                  e.stopPropagation();
                  handleBuildSelect(build.id);
                }}
              >
                {selectedBuild === build.id ? 'Selected' : 'Select Build'}
              </button>
            </div>
          </div>
        ))}
      </div>

      {sortedBuilds.length === 0 && (
        <div className="no-builds">
          <p>No builds found matching your criteria.</p>
          <button onClick={() => {
            setCategoryFilter('all');
            setSpecializationFilter('all');
            setDifficultyFilter('all');
            setSearchTerm('');
          }} className="clear-filters-btn">
            Clear Filters
          </button>
        </div>
      )}

      {/* Build Details Modal */}
      {showDetails && selectedBuildDetails && (
        <div className="modal-overlay" onClick={() => setShowDetails(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{selectedBuildDetails.name}</h2>
              <button 
                className="close-btn"
                onClick={() => setShowDetails(false)}
              >
                ×
              </button>
            </div>
            
            <div className="modal-body">
              <div className="build-detail-section">
                <h3>Description</h3>
                <p>{selectedBuildDetails.description}</p>
              </div>

              <div className="build-detail-section">
                <h3>Details</h3>
                <div className="detail-grid">
                  <div className="detail-item">
                    <strong>Category:</strong> {selectedBuildDetails.category}
                  </div>
                  <div className="detail-item">
                    <strong>Specialization:</strong> {selectedBuildDetails.specialization}
                  </div>
                  <div className="detail-item">
                    <strong>Difficulty:</strong> {selectedBuildDetails.difficulty}
                  </div>
                  <div className="detail-item">
                    <strong>Combat Style:</strong> {selectedBuildDetails.combat_style}
                  </div>
                </div>
              </div>

              <div className="build-detail-section">
                <h3>Professions</h3>
                <ul className="profession-list">
                  {selectedBuildDetails.professions.map((profession, index) => (
                    <li key={index}>{profession}</li>
                  ))}
                </ul>
              </div>

              {selectedBuildDetails.notes.length > 0 && (
                <div className="build-detail-section">
                  <h3>Notes</h3>
                  <ul className="notes-list">
                    {selectedBuildDetails.notes.map((note, index) => (
                      <li key={index}>{note}</li>
                    ))}
                  </ul>
                </div>
              )}

              {showPerformance && (
                <div className="build-detail-section">
                  <h3>Performance Ratings</h3>
                  <div className="performance-details">
                    <div className="performance-item">
                      <span>Average:</span>
                      <span className="performance-value">{selectedBuildDetails.avg_performance}/10</span>
                    </div>
                    <div className="performance-item">
                      <span>Best:</span>
                      <span className="performance-value">{selectedBuildDetails.best_performance}/10</span>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button 
                className="select-build-btn"
                onClick={() => {
                  handleBuildSelect(selectedBuildDetails.id);
                  setShowDetails(false);
                }}
              >
                Select This Build
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BuildSelector; 