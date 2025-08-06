import React, { useState } from 'react';
import './OptimizerResult.css';

interface AttributeBreakpoint {
  attribute: string;
  current_value: number;
  target_value: number;
  breakpoint_value: number;
  improvement_potential: number;
  priority: 'critical' | 'high' | 'medium' | 'low';
  reasoning: string;
}

interface ArmorRecommendation {
  slot: string;
  current_item: string | null;
  recommended_item: string;
  resist_gains: Record<string, number>;
  stat_gains: Record<string, number>;
  cost: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  reasoning: string;
}

interface EnhancementRecommendation {
  type: string;
  name: string;
  effect: Record<string, number>;
  duration: string | null;
  cost: string;
  priority: 'critical' | 'high' | 'medium' | 'low';
  reasoning: string;
}

interface GCWOptimization {
  role: string;
  current_rank: number;
  target_rank: number;
  required_attributes: Record<string, number>;
  recommended_gear: string[];
  strategy_notes: string[];
}

interface OptimizationResult {
  character_name: string;
  selected_role: string;
  gcw_role: string | null;
  current_stats: Record<string, number>;
  target_stats: Record<string, number>;
  attribute_breakpoints: AttributeBreakpoint[];
  armor_recommendations: ArmorRecommendation[];
  enhancement_recommendations: EnhancementRecommendation[];
  gcw_optimization: GCWOptimization | null;
  overall_improvement: number;
  total_cost: string;
  implementation_priority: string[];
  tradeoffs: string[];
  links: Record<string, string>;
  timestamp: string;
}

interface OptimizerResultProps {
  result: OptimizationResult;
  onClose?: () => void;
  onSave?: (result: OptimizationResult) => void;
  onExport?: (result: OptimizationResult) => void;
}

const OptimizerResult: React.FC<OptimizerResultProps> = ({
  result,
  onClose,
  onSave,
  onExport
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'attributes' | 'armor' | 'enhancements' | 'gcw' | 'tradeoffs'>('overview');
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());

  const toggleSection = (sectionId: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId);
    } else {
      newExpanded.add(sectionId);
    }
    setExpandedSections(newExpanded);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return '#ff4444';
      case 'high': return '#ff8800';
      case 'medium': return '#ffaa00';
      case 'low': return '#44aa44';
      default: return '#888888';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'critical': return '🔴';
      case 'high': return '🟠';
      case 'medium': return '🟡';
      case 'low': return '🟢';
      default: return '⚪';
    }
  };

  const formatStatName = (stat: string) => {
    return stat.charAt(0).toUpperCase() + stat.slice(1).replace(/_/g, ' ');
  };

  const formatImprovement = (improvement: number) => {
    return `${(improvement * 100).toFixed(1)}%`;
  };

  const renderOverview = () => (
    <div className="optimizer-overview">
      <div className="overview-header">
        <h2>Build Optimization for {result.character_name}</h2>
        <div className="overview-stats">
          <div className="stat-item">
            <span className="stat-label">Role:</span>
            <span className="stat-value">{result.selected_role.toUpperCase()}</span>
          </div>
          {result.gcw_role && (
            <div className="stat-item">
              <span className="stat-label">GCW Role:</span>
              <span className="stat-value">{result.gcw_role}</span>
            </div>
          )}
          <div className="stat-item">
            <span className="stat-label">Overall Improvement:</span>
            <span className="stat-value improvement">{formatImprovement(result.overall_improvement)}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Total Cost:</span>
            <span className="stat-value cost">{result.total_cost}</span>
          </div>
        </div>
      </div>

      <div className="overview-sections">
        <div className="section-card">
          <h3>Current vs Target Stats</h3>
          <div className="stats-comparison">
            {Object.entries(result.current_stats).map(([stat, value]) => {
              const target = result.target_stats[stat] || value;
              const improvement = target - value;
              return (
                <div key={stat} className="stat-comparison">
                  <span className="stat-name">{formatStatName(stat)}</span>
                  <span className="stat-current">{value}</span>
                  <span className="stat-arrow">→</span>
                  <span className="stat-target">{target}</span>
                  {improvement > 0 && (
                    <span className="stat-improvement">+{improvement}</span>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        <div className="section-card">
          <h3>Implementation Priority</h3>
          <div className="priority-list">
            {result.implementation_priority.map((item, index) => (
              <div key={index} className="priority-item">
                <span className="priority-number">{index + 1}</span>
                <span className="priority-text">{item}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  const renderAttributes = () => (
    <div className="optimizer-attributes">
      <h3>Attribute Breakpoints</h3>
      <div className="breakpoints-grid">
        {result.attribute_breakpoints.map((breakpoint, index) => (
          <div key={index} className="breakpoint-card">
            <div className="breakpoint-header">
              <span className="priority-icon" style={{ color: getPriorityColor(breakpoint.priority) }}>
                {getPriorityIcon(breakpoint.priority)}
              </span>
              <h4>{formatStatName(breakpoint.attribute)}</h4>
              <span className="priority-badge">{breakpoint.priority}</span>
            </div>
            <div className="breakpoint-stats">
              <div className="stat-row">
                <span>Current:</span>
                <span className="stat-value">{breakpoint.current_value}</span>
              </div>
              <div className="stat-row">
                <span>Target:</span>
                <span className="stat-value">{breakpoint.target_value}</span>
              </div>
              <div className="stat-row">
                <span>Breakpoint:</span>
                <span className="stat-value highlight">{breakpoint.breakpoint_value}</span>
              </div>
              <div className="stat-row">
                <span>Improvement:</span>
                <span className="stat-value improvement">{formatImprovement(breakpoint.improvement_potential)}</span>
              </div>
            </div>
            <div className="breakpoint-reasoning">
              <p>{breakpoint.reasoning}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderArmor = () => (
    <div className="optimizer-armor">
      <h3>Armor Recommendations</h3>
      <div className="armor-grid">
        {result.armor_recommendations.map((armor, index) => (
          <div key={index} className="armor-card">
            <div className="armor-header">
              <span className="priority-icon" style={{ color: getPriorityColor(armor.priority) }}>
                {getPriorityIcon(armor.priority)}
              </span>
              <h4>{armor.slot.toUpperCase()}</h4>
              <span className="priority-badge">{armor.priority}</span>
            </div>
            <div className="armor-details">
              <div className="armor-item">
                <span className="label">Current:</span>
                <span className="value">{armor.current_item || 'None'}</span>
              </div>
              <div className="armor-item">
                <span className="label">Recommended:</span>
                <span className="value highlight">{armor.recommended_item}</span>
              </div>
              <div className="armor-item">
                <span className="label">Cost:</span>
                <span className="value cost">{armor.cost}</span>
              </div>
            </div>
            <div className="armor-gains">
              <div className="gains-section">
                <h5>Resist Gains</h5>
                <div className="gains-grid">
                  {Object.entries(armor.resist_gains).map(([resist, value]) => (
                    <div key={resist} className="gain-item">
                      <span className="gain-name">{resist}</span>
                      <span className="gain-value">+{value}</span>
                    </div>
                  ))}
                </div>
              </div>
              <div className="gains-section">
                <h5>Stat Gains</h5>
                <div className="gains-grid">
                  {Object.entries(armor.stat_gains).map(([stat, value]) => (
                    <div key={stat} className="gain-item">
                      <span className="gain-name">{formatStatName(stat)}</span>
                      <span className="gain-value">+{value}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            <div className="armor-reasoning">
              <p>{armor.reasoning}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderEnhancements = () => (
    <div className="optimizer-enhancements">
      <h3>Enhancement Recommendations</h3>
      <div className="enhancements-grid">
        {result.enhancement_recommendations.map((enhancement, index) => (
          <div key={index} className="enhancement-card">
            <div className="enhancement-header">
              <span className="priority-icon" style={{ color: getPriorityColor(enhancement.priority) }}>
                {getPriorityIcon(enhancement.priority)}
              </span>
              <h4>{enhancement.name}</h4>
              <span className="enhancement-type">{enhancement.type}</span>
              <span className="priority-badge">{enhancement.priority}</span>
            </div>
            <div className="enhancement-details">
              <div className="enhancement-item">
                <span className="label">Duration:</span>
                <span className="value">{enhancement.duration || 'Permanent'}</span>
              </div>
              <div className="enhancement-item">
                <span className="label">Cost:</span>
                <span className="value cost">{enhancement.cost}</span>
              </div>
            </div>
            <div className="enhancement-effects">
              <h5>Effects</h5>
              <div className="effects-grid">
                {Object.entries(enhancement.effect).map(([stat, value]) => (
                  <div key={stat} className="effect-item">
                    <span className="effect-name">{formatStatName(stat)}</span>
                    <span className="effect-value">+{value}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="enhancement-reasoning">
              <p>{enhancement.reasoning}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderGCW = () => {
    if (!result.gcw_optimization) {
      return (
        <div className="optimizer-gcw">
          <h3>GCW Optimization</h3>
          <p className="no-gcw">No GCW role selected for this optimization.</p>
        </div>
      );
    }

    return (
      <div className="optimizer-gcw">
        <h3>GCW Optimization</h3>
        <div className="gcw-details">
          <div className="gcw-header">
            <h4>{result.gcw_optimization.role.toUpperCase()}</h4>
            <div className="gcw-rank">
              <span>Rank {result.gcw_optimization.current_rank} → {result.gcw_optimization.target_rank}</span>
            </div>
          </div>
          
          <div className="gcw-requirements">
            <h5>Required Attributes</h5>
            <div className="requirements-grid">
              {Object.entries(result.gcw_optimization.required_attributes).map(([attr, value]) => (
                <div key={attr} className="requirement-item">
                  <span className="requirement-name">{formatStatName(attr)}</span>
                  <span className="requirement-value">{value}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="gcw-gear">
            <h5>Recommended Gear</h5>
            <div className="gear-list">
              {result.gcw_optimization.recommended_gear.map((gear, index) => (
                <div key={index} className="gear-item">
                  <span className="gear-icon">⚔️</span>
                  <span className="gear-name">{gear}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="gcw-strategy">
            <h5>Strategy Notes</h5>
            <div className="strategy-notes">
              {result.gcw_optimization.strategy_notes.map((note, index) => (
                <div key={index} className="strategy-note">
                  <span className="note-bullet">•</span>
                  <span className="note-text">{note}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderTradeoffs = () => (
    <div className="optimizer-tradeoffs">
      <h3>Tradeoffs & Considerations</h3>
      <div className="tradeoffs-list">
        {result.tradeoffs.map((tradeoff, index) => (
          <div key={index} className="tradeoff-item">
            <span className="tradeoff-icon">⚠️</span>
            <span className="tradeoff-text">{tradeoff}</span>
          </div>
        ))}
      </div>
      
      <div className="links-section">
        <h4>Related Resources</h4>
        <div className="links-grid">
          {Object.entries(result.links).map(([name, url]) => (
            <a key={name} href={url} className="resource-link">
              <span className="link-icon">🔗</span>
              <span className="link-name">{name}</span>
            </a>
          ))}
        </div>
      </div>
    </div>
  );

  return (
    <div className="optimizer-result">
      <div className="optimizer-header">
        <div className="header-left">
          <h1>Build Optimizer v2</h1>
          <p className="timestamp">Generated: {new Date(result.timestamp).toLocaleString()}</p>
        </div>
        <div className="header-actions">
          {onSave && (
            <button className="btn btn-secondary" onClick={() => onSave(result)}>
              💾 Save
            </button>
          )}
          {onExport && (
            <button className="btn btn-secondary" onClick={() => onExport(result)}>
              📤 Export
            </button>
          )}
          {onClose && (
            <button className="btn btn-primary" onClick={onClose}>
              ✕ Close
            </button>
          )}
        </div>
      </div>

      <div className="optimizer-tabs">
        <button 
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📊 Overview
        </button>
        <button 
          className={`tab ${activeTab === 'attributes' ? 'active' : ''}`}
          onClick={() => setActiveTab('attributes')}
        >
          ⚡ Attributes
        </button>
        <button 
          className={`tab ${activeTab === 'armor' ? 'active' : ''}`}
          onClick={() => setActiveTab('armor')}
        >
          🛡️ Armor
        </button>
        <button 
          className={`tab ${activeTab === 'enhancements' ? 'active' : ''}`}
          onClick={() => setActiveTab('enhancements')}
        >
          🔧 Enhancements
        </button>
        <button 
          className={`tab ${activeTab === 'gcw' ? 'active' : ''}`}
          onClick={() => setActiveTab('gcw')}
        >
          ⚔️ GCW
        </button>
        <button 
          className={`tab ${activeTab === 'tradeoffs' ? 'active' : ''}`}
          onClick={() => setActiveTab('tradeoffs')}
        >
          ⚖️ Tradeoffs
        </button>
      </div>

      <div className="optimizer-content">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'attributes' && renderAttributes()}
        {activeTab === 'armor' && renderArmor()}
        {activeTab === 'enhancements' && renderEnhancements()}
        {activeTab === 'gcw' && renderGCW()}
        {activeTab === 'tradeoffs' && renderTradeoffs()}
      </div>
    </div>
  );
};

export default OptimizerResult; 