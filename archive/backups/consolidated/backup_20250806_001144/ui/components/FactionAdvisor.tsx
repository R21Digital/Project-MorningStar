import React, { useState, useEffect } from 'react';
import './FactionAdvisor.css';

interface FactionProfile {
  character_name: string;
  faction: 'rebel' | 'imperial' | 'neutral';
  current_rank: number;
  rank_points: number;
  total_battles: number;
  victories: number;
  defeats: number;
  draws: number;
  win_rate: number;
  favorite_battle_type: string;
  average_battle_duration: number;
  last_battle?: string;
  gear_loadout: Record<string, string>;
  active_strategies: string[];
  notes: string;
}

interface GearRecommendation {
  item_name: string;
  category: string;
  rank_requirement: number;
  faction_requirement?: string;
  stats: Record<string, number>;
  resists: Record<string, number>;
  cost: string;
  priority: string;
  reasoning: string;
}

interface StrategyGuide {
  rank: number;
  faction: string;
  strategy_type: string;
  title: string;
  description: string;
  tactics: string[];
  gear_requirements: string[];
  skill_requirements: string[];
  difficulty: string;
  estimated_success_rate: number;
}

interface RankProgression {
  current_rank: number;
  current_points: number;
  next_rank: number;
  points_needed: number;
  total_battles: number;
  win_rate: number;
  total_points_earned: number;
  points_per_battle: number;
  avg_days_between_battles: number;
  estimated_days_to_next_rank: number;
}

interface GCWBattle {
  battle_id: string;
  battle_type: string;
  location: string;
  faction: string;
  rank_at_time: number;
  outcome: string;
  duration: number;
  participants: number;
  rewards: Record<string, any>;
  timestamp: string;
}

interface FactionAdvisorProps {
  characterName?: string;
  onProfileUpdate?: (profile: FactionProfile) => void;
  onBattleLog?: (battle: GCWBattle) => void;
}

const FactionAdvisor: React.FC<FactionAdvisorProps> = ({
  characterName = 'DemoCharacter',
  onProfileUpdate,
  onBattleLog
}) => {
  const [profile, setProfile] = useState<FactionProfile | null>(null);
  const [gearRecommendations, setGearRecommendations] = useState<GearRecommendation[]>([]);
  const [strategyGuides, setStrategyGuides] = useState<StrategyGuide[]>([]);
  const [rankProgression, setRankProgression] = useState<RankProgression | null>(null);
  const [recentBattles, setRecentBattles] = useState<GCWBattle[]>([]);
  const [activeEvents, setActiveEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [selectedGearCategory, setSelectedGearCategory] = useState<string>('all');
  const [selectedStrategyType, setSelectedStrategyType] = useState<string>('all');

  useEffect(() => {
    if (characterName) {
      loadFactionData();
    }
  }, [characterName]);

  const loadFactionData = async () => {
    setLoading(true);
    setError(null);

    try {
      // Load profile
      const profileResponse = await fetch(`/api/gcw/profile/${characterName}`);
      if (profileResponse.ok) {
        const profileData = await profileResponse.json();
        setProfile(profileData);
      }

      // Load gear recommendations
      const gearResponse = await fetch(`/api/gcw/gear/${characterName}`);
      if (gearResponse.ok) {
        const gearData = await gearResponse.json();
        setGearRecommendations(gearData);
      }

      // Load strategy guides
      const strategyResponse = await fetch(`/api/gcw/strategies/${characterName}`);
      if (strategyResponse.ok) {
        const strategyData = await strategyResponse.json();
        setStrategyGuides(strategyData);
      }

      // Load rank progression
      const progressionResponse = await fetch(`/api/gcw/progression/${characterName}`);
      if (progressionResponse.ok) {
        const progressionData = await progressionResponse.json();
        setRankProgression(progressionData);
      }

      // Load recent battles
      const battlesResponse = await fetch(`/api/gcw/battles/${characterName}?limit=10`);
      if (battlesResponse.ok) {
        const battlesData = await battlesResponse.json();
        setRecentBattles(battlesData);
      }

      // Load active events
      const eventsResponse = await fetch(`/api/gcw/events/${characterName}`);
      if (eventsResponse.ok) {
        const eventsData = await eventsResponse.json();
        setActiveEvents(eventsData);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const getFactionColor = (faction: string) => {
    switch (faction) {
      case 'rebel': return '#dc3545';
      case 'imperial': return '#007bff';
      case 'neutral': return '#6c757d';
      default: return '#6c757d';
    }
  };

  const getRankName = (rank: number) => {
    const rankNames = [
      'Neutral', 'Recruit', 'Private', 'Corporal', 'Sergeant',
      'Lieutenant', 'Captain', 'Major', 'Colonel', 'General', 'Marshal'
    ];
    return rankNames[rank] || `Rank ${rank}`;
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

  const formatStatGains = (stats: Record<string, number>) => {
    return Object.entries(stats)
      .map(([stat, value]) => `${stat}: +${value}`)
      .join(', ');
  };

  const formatResistGains = (resists: Record<string, number>) => {
    return Object.entries(resists)
      .map(([resist, value]) => `${resist}: +${value}`)
      .join(', ');
  };

  const logBattle = async (battleData: Partial<GCWBattle>) => {
    try {
      const response = await fetch('/api/gcw/battle/log', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          character_name: characterName,
          ...battleData
        })
      });

      if (response.ok) {
        const battle = await response.json();
        setRecentBattles(prev => [battle, ...prev.slice(0, 9)]);
        if (onBattleLog) {
          onBattleLog(battle);
        }
        loadFactionData(); // Refresh data
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to log battle');
    }
  };

  const filteredGear = gearRecommendations.filter(gear => {
    if (selectedGearCategory !== 'all' && gear.category !== selectedGearCategory) {
      return false;
    }
    return true;
  });

  const filteredStrategies = strategyGuides.filter(strategy => {
    if (selectedStrategyType !== 'all' && strategy.strategy_type !== selectedStrategyType) {
      return false;
    }
    return true;
  });

  if (loading) {
    return (
      <div className="faction-advisor">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading faction data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="faction-advisor">
        <div className="error-message">
          <h3>Error</h3>
          <p>{error}</p>
          <button onClick={loadFactionData}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="faction-advisor">
      <div className="faction-header">
        <h2>Faction Advisor</h2>
        <div className="character-info">
          <span className="character-name">{characterName}</span>
          {profile && (
            <span 
              className="faction-badge"
              style={{ backgroundColor: getFactionColor(profile.faction) }}
            >
              {profile.faction.toUpperCase()}
            </span>
          )}
        </div>
      </div>

      <div className="tab-navigation">
        <button 
          className={`tab-button ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`tab-button ${activeTab === 'gear' ? 'active' : ''}`}
          onClick={() => setActiveTab('gear')}
        >
          Gear Recommendations
        </button>
        <button 
          className={`tab-button ${activeTab === 'strategies' ? 'active' : ''}`}
          onClick={() => setActiveTab('strategies')}
        >
          Strategy Guides
        </button>
        <button 
          className={`tab-button ${activeTab === 'battles' ? 'active' : ''}`}
          onClick={() => setActiveTab('battles')}
        >
          Battle Log
        </button>
        <button 
          className={`tab-button ${activeTab === 'events' ? 'active' : ''}`}
          onClick={() => setActiveTab('events')}
        >
          GCW Events
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
            {profile && (
              <div className="profile-section">
                <h3>Faction Profile</h3>
                <div className="profile-grid">
                  <div className="profile-card">
                    <h4>Rank & Progress</h4>
                    <div className="rank-info">
                      <div className="rank-display">
                        <span className="rank-number">{profile.current_rank}</span>
                        <span className="rank-name">{getRankName(profile.current_rank)}</span>
                      </div>
                      <div className="rank-points">
                        <span>{profile.rank_points} points</span>
                      </div>
                    </div>
                    {rankProgression && (
                      <div className="progression-info">
                        <p>Next Rank: {getRankName(rankProgression.next_rank)}</p>
                        <p>Points Needed: {rankProgression.points_needed}</p>
                        <p>Est. Days to Next Rank: {Math.round(rankProgression.estimated_days_to_next_rank)}</p>
                      </div>
                    )}
                  </div>

                  <div className="profile-card">
                    <h4>Battle Statistics</h4>
                    <div className="battle-stats">
                      <div className="stat-item">
                        <span className="stat-label">Total Battles:</span>
                        <span className="stat-value">{profile.total_battles}</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Win Rate:</span>
                        <span className="stat-value">{(profile.win_rate * 100).toFixed(1)}%</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Victories:</span>
                        <span className="stat-value">{profile.victories}</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Defeats:</span>
                        <span className="stat-value">{profile.defeats}</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Avg Battle Duration:</span>
                        <span className="stat-value">{profile.average_battle_duration.toFixed(1)} min</span>
                      </div>
                    </div>
                  </div>

                  <div className="profile-card">
                    <h4>Current Gear</h4>
                    <div className="gear-loadout">
                      {Object.entries(profile.gear_loadout).map(([slot, item]) => (
                        <div key={slot} className="gear-item">
                          <span className="gear-slot">{slot}:</span>
                          <span className="gear-name">{item}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="profile-card">
                    <h4>Active Strategies</h4>
                    <div className="active-strategies">
                      {profile.active_strategies.map((strategy, index) => (
                        <span key={index} className="strategy-tag">{strategy}</span>
                      ))}
                    </div>
                    {profile.notes && (
                      <div className="profile-notes">
                        <h5>Notes</h5>
                        <p>{profile.notes}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'gear' && (
          <div className="gear-tab">
            <div className="gear-filters">
              <select 
                value={selectedGearCategory} 
                onChange={(e) => setSelectedGearCategory(e.target.value)}
                className="gear-filter"
              >
                <option value="all">All Categories</option>
                <option value="armor">Armor</option>
                <option value="weapons">Weapons</option>
                <option value="buffs">Buffs</option>
                <option value="consumables">Consumables</option>
                <option value="utilities">Utilities</option>
              </select>
            </div>

            <div className="gear-recommendations">
              {filteredGear.map((gear, index) => (
                <div key={index} className="gear-card">
                  <div className="gear-header">
                    <h4>{gear.item_name}</h4>
                    <div className="gear-meta">
                      <span 
                        className="priority-badge"
                        style={{ backgroundColor: getPriorityColor(gear.priority) }}
                      >
                        {gear.priority.toUpperCase()}
                      </span>
                      <span 
                        className="cost-badge"
                        style={{ backgroundColor: getCostColor(gear.cost) }}
                      >
                        {gear.cost.toUpperCase()}
                      </span>
                    </div>
                  </div>
                  
                  <div className="gear-details">
                    <div className="gear-category">
                      <strong>Category:</strong> {gear.category}
                    </div>
                    <div className="gear-rank">
                      <strong>Rank Requirement:</strong> {gear.rank_requirement}
                    </div>
                    {gear.faction_requirement && (
                      <div className="gear-faction">
                        <strong>Faction:</strong> {gear.faction_requirement}
                      </div>
                    )}
                    
                    {Object.keys(gear.stats).length > 0 && (
                      <div className="gear-stats">
                        <strong>Stats:</strong> {formatStatGains(gear.stats)}
                      </div>
                    )}
                    
                    {Object.keys(gear.resists).length > 0 && (
                      <div className="gear-resists">
                        <strong>Resists:</strong> {formatResistGains(gear.resists)}
                      </div>
                    )}
                    
                    <div className="gear-reasoning">
                      <strong>Reasoning:</strong> {gear.reasoning}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'strategies' && (
          <div className="strategies-tab">
            <div className="strategy-filters">
              <select 
                value={selectedStrategyType} 
                onChange={(e) => setSelectedStrategyType(e.target.value)}
                className="strategy-filter"
              >
                <option value="all">All Strategies</option>
                <option value="offensive">Offensive</option>
                <option value="defensive">Defensive</option>
                <option value="support">Support</option>
                <option value="stealth">Stealth</option>
                <option value="tank">Tank</option>
              </select>
            </div>

            <div className="strategy-guides">
              {filteredStrategies.map((strategy, index) => (
                <div key={index} className="strategy-card">
                  <div className="strategy-header">
                    <h4>{strategy.title}</h4>
                    <div className="strategy-meta">
                      <span className="strategy-type">{strategy.strategy_type}</span>
                      <span className="strategy-rank">Rank {strategy.rank}+</span>
                      <span className="strategy-success">
                        {(strategy.estimated_success_rate * 100).toFixed(0)}% Success
                      </span>
                    </div>
                  </div>
                  
                  <div className="strategy-content">
                    <p className="strategy-description">{strategy.description}</p>
                    
                    <div className="strategy-tactics">
                      <h5>Tactics:</h5>
                      <ul>
                        {strategy.tactics.map((tactic, idx) => (
                          <li key={idx}>{tactic}</li>
                        ))}
                      </ul>
                    </div>
                    
                    <div className="strategy-requirements">
                      <div className="gear-requirements">
                        <h5>Gear Requirements:</h5>
                        <ul>
                          {strategy.gear_requirements.map((gear, idx) => (
                            <li key={idx}>{gear}</li>
                          ))}
                        </ul>
                      </div>
                      
                      <div className="skill-requirements">
                        <h5>Skill Requirements:</h5>
                        <ul>
                          {strategy.skill_requirements.map((skill, idx) => (
                            <li key={idx}>{skill}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                    
                    <div className="strategy-difficulty">
                      <strong>Difficulty:</strong> {strategy.difficulty}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'battles' && (
          <div className="battles-tab">
            <div className="battle-log-header">
              <h3>Recent Battles</h3>
              <button 
                className="log-battle-btn"
                onClick={() => {
                  // Quick battle logging interface
                  const battleData = {
                    battle_type: 'pvp',
                    location: 'Unknown',
                    outcome: 'victory',
                    duration: 10,
                    participants: 2
                  };
                  logBattle(battleData);
                }}
              >
                Log Battle
              </button>
            </div>

            <div className="battle-log">
              {recentBattles.map((battle, index) => (
                <div key={index} className="battle-entry">
                  <div className="battle-header">
                    <span className="battle-type">{battle.battle_type.toUpperCase()}</span>
                    <span className={`battle-outcome ${battle.outcome}`}>
                      {battle.outcome.toUpperCase()}
                    </span>
                  </div>
                  
                  <div className="battle-details">
                    <div className="battle-location">
                      <strong>Location:</strong> {battle.location}
                    </div>
                    <div className="battle-duration">
                      <strong>Duration:</strong> {battle.duration} minutes
                    </div>
                    <div className="battle-participants">
                      <strong>Participants:</strong> {battle.participants}
                    </div>
                    <div className="battle-rank">
                      <strong>Rank at Time:</strong> {getRankName(battle.rank_at_time)}
                    </div>
                    <div className="battle-timestamp">
                      <strong>Date:</strong> {new Date(battle.timestamp).toLocaleDateString()}
                    </div>
                  </div>
                  
                  {Object.keys(battle.rewards).length > 0 && (
                    <div className="battle-rewards">
                      <strong>Rewards:</strong>
                      <ul>
                        {Object.entries(battle.rewards).map(([reward, value]) => (
                          <li key={reward}>{reward}: {value}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'events' && (
          <div className="events-tab">
            <h3>Active GCW Events</h3>
            <div className="gcw-events">
              {activeEvents.length > 0 ? (
                activeEvents.map((event, index) => (
                  <div key={index} className="event-card">
                    <div className="event-header">
                      <h4>{event.name}</h4>
                      <span className="event-location">{event.location}</span>
                    </div>
                    
                    <div className="event-content">
                      <p className="event-description">{event.description}</p>
                      
                      <div className="event-details">
                        <div className="event-time">
                          <strong>Duration:</strong> {new Date(event.start_time).toLocaleDateString()} - {new Date(event.end_time).toLocaleDateString()}
                        </div>
                        {event.faction_restriction && (
                          <div className="event-faction">
                            <strong>Faction:</strong> {event.faction_restriction}
                          </div>
                        )}
                        <div className="event-rank">
                          <strong>Rank Requirement:</strong> {event.rank_requirement}
                        </div>
                        <div className="event-participants">
                          <strong>Participants:</strong> {event.participants.length}
                        </div>
                      </div>
                      
                      {Object.keys(event.rewards).length > 0 && (
                        <div className="event-rewards">
                          <strong>Rewards:</strong>
                          <ul>
                            {Object.entries(event.rewards).map(([reward, value]) => (
                              <li key={reward}>{reward}: {value}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="no-events">
                  <p>No active GCW events at this time.</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FactionAdvisor; 