import React, { useState, useEffect } from 'react';
import './GearSuggestions.css';

interface GearRecommendation {
  slot: string;
  current_item: string | null;
  recommended_item: string;
  improvement_score: number;
  stat_gains: Record<string, number>;
  resist_gains: Record<string, number>;
  enhancement_slots: number;
  recommended_enhancements: string[];
  cost: string;
  priority: 'high' | 'medium' | 'low';
  reasoning: string;
}

interface OptimizationResult {
  character_name: string;
  build_id: string;
  optimization_type: string;
  current_stats: Record<string, number>;
  target_stats: Record<string, number>;
  recommendations: GearRecommendation[];
  overall_improvement: number;
  total_cost: string;
  implementation_priority: string[];
  notes: string[];
  timestamp: string;
}

interface GearSuggestionsProps {
  characterName?: string;
  buildId?: string;
  optimizationType?: string;
  budget?: string;
  onOptimizationComplete?: (result: OptimizationResult) => void;
}

const GearSuggestions: React.FC<GearSuggestionsProps> = ({
  characterName = 'TestCharacter',
  buildId = 'rifleman_medic',
  optimizationType = 'balanced',
  budget = 'medium',
  onOptimizationComplete
}) => {
  const [optimizationResult, setOptimizationResult] = useState<OptimizationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedSlot, setSelectedSlot] = useState<string | null>(null);
  const [filterPriority, setFilterPriority] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('priority');

  useEffect(() => {
    if (characterName && buildId) {
      runOptimization();
    }
  }, [characterName, buildId, optimizationType, budget]);

  const runOptimization = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/gear/optimize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          character_name: characterName,
          build_id: buildId,
          optimization_type: optimizationType,
          budget: budget
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setOptimizationResult(result);
      
      if (onOptimizationComplete) {
        onOptimizationComplete(result);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return '#dc3545';
      case 'medium': return '#ffc107';
      case 'low': return '#28a745';
      default: return '#6c757d';
    }
  };

  const getCostColor = (cost: string) => {
    switch (cost) {
      case 'high': return '#dc3545';
      case 'medium': return '#ffc107';
      case 'low': return '#28a745';
      default: return '#6c757d';
    }
  };

  const formatStatGains = (statGains: Record<string, number>) => {
    return Object.entries(statGains)
      .map(([stat, value]) => `+${value} ${stat}`)
      .join(', ');
  };

  const formatResistGains = (resistGains: Record<string, number>) => {
    return Object.entries(resistGains)
      .map(([resist, value]) => `+${value}% ${resist}`)
      .join(', ');
  };

  const filteredRecommendations = optimizationResult?.recommendations.filter(rec => {
    if (filterPriority !== 'all' && rec.priority !== filterPriority) {
      return false;
    }
    return true;
  }) || [];

  const sortedRecommendations = [...filteredRecommendations].sort((a, b) => {
    switch (sortBy) {
      case 'priority':
        const priorityOrder = { high: 3, medium: 2, low: 1 };
        return priorityOrder[b.priority] - priorityOrder[a.priority];
      case 'improvement':
        return b.improvement_score - a.improvement_score;
      case 'cost':
        const costOrder = { high: 3, medium: 2, low: 1 };
        return costOrder[a.cost] - costOrder[b.cost];
      default:
        return 0;
    }
  });

  if (loading) {
    return (
      <div className="gear-suggestions">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Analyzing gear optimization...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="gear-suggestions">
        <div className="error-container">
          <h3>Error</h3>
          <p>{error}</p>
          <button onClick={runOptimization} className="retry-button">
            Retry Optimization
          </button>
        </div>
      </div>
    );
  }

  if (!optimizationResult) {
    return (
      <div className="gear-suggestions">
        <div className="no-data">
          <p>No optimization data available</p>
          <button onClick={runOptimization} className="run-optimization-button">
            Run Gear Optimization
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="gear-suggestions">
      <div className="optimization-header">
        <h2>Gear Optimization Results</h2>
        <div className="optimization-summary">
          <div className="summary-item">
            <span className="label">Character:</span>
            <span className="value">{optimizationResult.character_name}</span>
          </div>
          <div className="summary-item">
            <span className="label">Build:</span>
            <span className="value">{optimizationResult.build_id}</span>
          </div>
          <div className="summary-item">
            <span className="label">Optimization:</span>
            <span className="value">{optimizationResult.optimization_type}</span>
          </div>
          <div className="summary-item">
            <span className="label">Overall Improvement:</span>
            <span className="value improvement-score">
              {optimizationResult.overall_improvement.toFixed(1)}%
            </span>
          </div>
          <div className="summary-item">
            <span className="label">Total Cost:</span>
            <span className="value cost-badge" style={{ backgroundColor: getCostColor(optimizationResult.total_cost) }}>
              {optimizationResult.total_cost}
            </span>
          </div>
        </div>
      </div>

      <div className="controls-section">
        <div className="filters">
          <label>
            Filter by Priority:
            <select value={filterPriority} onChange={(e) => setFilterPriority(e.target.value)}>
              <option value="all">All Priorities</option>
              <option value="high">High Priority</option>
              <option value="medium">Medium Priority</option>
              <option value="low">Low Priority</option>
            </select>
          </label>
        </div>
        <div className="sorting">
          <label>
            Sort by:
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="priority">Priority</option>
              <option value="improvement">Improvement Score</option>
              <option value="cost">Cost</option>
            </select>
          </label>
        </div>
      </div>

      <div className="recommendations-grid">
        {sortedRecommendations.map((recommendation, index) => (
          <div key={index} className="recommendation-card">
            <div className="card-header">
              <h3 className="slot-name">{recommendation.slot}</h3>
              <div className="priority-badge" style={{ backgroundColor: getPriorityColor(recommendation.priority) }}>
                {recommendation.priority}
              </div>
            </div>
            
            <div className="card-content">
              <div className="item-recommendation">
                <div className="current-item">
                  <span className="label">Current:</span>
                  <span className="value">{recommendation.current_item || 'None'}</span>
                </div>
                <div className="recommended-item">
                  <span className="label">Recommended:</span>
                  <span className="value">{recommendation.recommended_item}</span>
                </div>
              </div>

              <div className="improvement-details">
                <div className="improvement-score">
                  <span className="label">Improvement:</span>
                  <span className="value">{recommendation.improvement_score.toFixed(1)}%</span>
                </div>
                
                {Object.keys(recommendation.stat_gains).length > 0 && (
                  <div className="stat-gains">
                    <span className="label">Stats:</span>
                    <span className="value">{formatStatGains(recommendation.stat_gains)}</span>
                  </div>
                )}
                
                {Object.keys(recommendation.resist_gains).length > 0 && (
                  <div className="resist-gains">
                    <span className="label">Resists:</span>
                    <span className="value">{formatResistGains(recommendation.resist_gains)}</span>
                  </div>
                )}
              </div>

              {recommendation.enhancement_slots > 0 && (
                <div className="enhancements">
                  <div className="enhancement-slots">
                    <span className="label">Enhancement Slots:</span>
                    <span className="value">{recommendation.enhancement_slots}</span>
                  </div>
                  {recommendation.recommended_enhancements.length > 0 && (
                    <div className="recommended-enhancements">
                      <span className="label">Recommended:</span>
                      <span className="value">{recommendation.recommended_enhancements.join(', ')}</span>
                    </div>
                  )}
                </div>
              )}

              <div className="cost-info">
                <span className="label">Cost:</span>
                <span className="value cost-badge" style={{ backgroundColor: getCostColor(recommendation.cost) }}>
                  {recommendation.cost}
                </span>
              </div>

              <div className="reasoning">
                <span className="label">Reasoning:</span>
                <p className="value">{recommendation.reasoning}</p>
              </div>
            </div>

            <div className="card-actions">
              <button 
                className="view-details-button"
                onClick={() => setSelectedSlot(selectedSlot === recommendation.slot ? null : recommendation.slot)}
              >
                {selectedSlot === recommendation.slot ? 'Hide Details' : 'View Details'}
              </button>
            </div>

            {selectedSlot === recommendation.slot && (
              <div className="detailed-view">
                <h4>Detailed Analysis</h4>
                <div className="detail-grid">
                  <div className="detail-item">
                    <strong>Current Item:</strong> {recommendation.current_item || 'None'}
                  </div>
                  <div className="detail-item">
                    <strong>Recommended Item:</strong> {recommendation.recommended_item}
                  </div>
                  <div className="detail-item">
                    <strong>Improvement Score:</strong> {recommendation.improvement_score.toFixed(1)}%
                  </div>
                  <div className="detail-item">
                    <strong>Priority:</strong> {recommendation.priority}
                  </div>
                  <div className="detail-item">
                    <strong>Cost:</strong> {recommendation.cost}
                  </div>
                  <div className="detail-item">
                    <strong>Enhancement Slots:</strong> {recommendation.enhancement_slots}
                  </div>
                </div>
                
                <div className="stat-breakdown">
                  <h5>Stat Improvements</h5>
                  <div className="stat-list">
                    {Object.entries(recommendation.stat_gains).map(([stat, value]) => (
                      <div key={stat} className="stat-item">
                        <span className="stat-name">{stat}:</span>
                        <span className="stat-value">+{value}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="resist-breakdown">
                  <h5>Resistance Improvements</h5>
                  <div className="resist-list">
                    {Object.entries(recommendation.resist_gains).map(([resist, value]) => (
                      <div key={resist} className="resist-item">
                        <span className="resist-name">{resist}:</span>
                        <span className="resist-value">+{value}%</span>
                      </div>
                    ))}
                  </div>
                </div>

                {recommendation.recommended_enhancements.length > 0 && (
                  <div className="enhancement-breakdown">
                    <h5>Recommended Enhancements</h5>
                    <div className="enhancement-list">
                      {recommendation.recommended_enhancements.map((enhancement, idx) => (
                        <div key={idx} className="enhancement-item">
                          {enhancement}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>

      {optimizationResult.implementation_priority.length > 0 && (
        <div className="implementation-priority">
          <h3>Implementation Priority</h3>
          <ol className="priority-list">
            {optimizationResult.implementation_priority.map((item, index) => (
              <li key={index} className="priority-item">
                {item}
              </li>
            ))}
          </ol>
        </div>
      )}

      {optimizationResult.notes.length > 0 && (
        <div className="optimization-notes">
          <h3>Optimization Notes</h3>
          <ul className="notes-list">
            {optimizationResult.notes.map((note, index) => (
              <li key={index} className="note-item">
                {note}
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="action-buttons">
        <button onClick={runOptimization} className="refresh-button">
          Refresh Optimization
        </button>
        <button 
          onClick={() => {
            // Save optimization result
            console.log('Saving optimization result:', optimizationResult);
          }} 
          className="save-button"
        >
          Save Results
        </button>
      </div>
    </div>
  );
};

export default GearSuggestions; 