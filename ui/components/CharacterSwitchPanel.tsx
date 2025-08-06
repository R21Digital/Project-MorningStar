import React, { useState, useEffect } from 'react';
import './CharacterSwitchPanel.css';

interface Character {
  character_id: string;
  name: string;
  server: string;
  race: string;
  profession: string;
  level: number;
  faction: string;
  city: string;
  guild: string;
  guild_tag: string;
  planet: string;
  location: string;
  status: string;
  role: string;
  is_main_character: boolean;
  auto_launch_enabled: boolean;
  last_session_at: string | null;
  total_playtime_hours: number;
  total_sessions: number;
  total_xp_gained: number;
  total_credits_earned: number;
  notes: string;
}

interface CharacterSwitchPanelProps {
  discordUserId: string;
  onCharacterSwitch?: (character: Character) => void;
  onAutoLaunchToggle?: (characterId: string, enabled: boolean) => void;
  className?: string;
}

const CharacterSwitchPanel: React.FC<CharacterSwitchPanelProps> = ({
  discordUserId,
  onCharacterSwitch,
  onAutoLaunchToggle,
  className = ''
}) => {
  const [characters, setCharacters] = useState<Character[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [filterRole, setFilterRole] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('last_session');

  useEffect(() => {
    loadCharacters();
  }, [discordUserId]);

  const loadCharacters = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(`/api/characters?discord_user_id=${discordUserId}`);
      if (!response.ok) {
        throw new Error('Failed to load characters');
      }
      
      const data = await response.json();
      setCharacters(data.characters || []);
      
      // Set main character as default selected
      const mainChar = data.characters?.find((c: Character) => c.is_main_character);
      if (mainChar) {
        setSelectedCharacter(mainChar);
      }
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load characters');
    } finally {
      setLoading(false);
    }
  };

  const handleCharacterSwitch = async (character: Character) => {
    try {
      const response = await fetch('/api/characters/switch', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          discord_user_id: discordUserId,
          character_name: character.name
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to switch character');
      }

      setSelectedCharacter(character);
      onCharacterSwitch?.(character);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to switch character');
    }
  };

  const handleAutoLaunchToggle = async (characterId: string, enabled: boolean) => {
    try {
      const response = await fetch(`/api/characters/${characterId}/auto-launch`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ enabled }),
      });

      if (!response.ok) {
        throw new Error('Failed to toggle auto-launch');
      }

      // Update local state
      setCharacters(prev => prev.map(char => 
        char.character_id === characterId 
          ? { ...char, auto_launch_enabled: enabled }
          : char
      ));

      onAutoLaunchToggle?.(characterId, enabled);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to toggle auto-launch');
    }
  };

  const formatPlaytime = (hours: number): string => {
    if (hours < 1) {
      return `${Math.round(hours * 60)}m`;
    }
    const wholeHours = Math.floor(hours);
    const minutes = Math.round((hours - wholeHours) * 60);
    return `${wholeHours}h ${minutes}m`;
  };

  const formatCredits = (credits: number): string => {
    if (credits >= 1000000) {
      return `${(credits / 1000000).toFixed(1)}M`;
    }
    if (credits >= 1000) {
      return `${(credits / 1000).toFixed(1)}K`;
    }
    return credits.toString();
  };

  const formatLastSession = (timestamp: string | null): string => {
    if (!timestamp) return 'Never';
    
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
    return `${Math.floor(diffDays / 30)} months ago`;
  };

  const getFactionColor = (faction: string): string => {
    switch (faction.toLowerCase()) {
      case 'rebel': return '#ff4444';
      case 'imperial': return '#4444ff';
      case 'neutral': return '#888888';
      default: return '#666666';
    }
  };

  const getRoleIcon = (role: string): string => {
    switch (role.toLowerCase()) {
      case 'main': return '👑';
      case 'alt': return '⚔️';
      case 'boxer': return '🎭';
      default: return '👤';
    }
  };

  const filteredAndSortedCharacters = characters
    .filter(char => char.status === 'active')
    .filter(char => filterRole === 'all' || char.role === filterRole)
    .sort((a, b) => {
      switch (sortBy) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'level':
          return b.level - a.level;
        case 'last_session':
          const aTime = a.last_session_at ? new Date(a.last_session_at).getTime() : 0;
          const bTime = b.last_session_at ? new Date(b.last_session_at).getTime() : 0;
          return bTime - aTime;
        case 'playtime':
          return b.total_playtime_hours - a.total_playtime_hours;
        default:
          return 0;
      }
    });

  if (loading) {
    return (
      <div className={`character-switch-panel ${className}`}>
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading characters...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`character-switch-panel ${className}`}>
        <div className="error-message">
          <i className="fas fa-exclamation-triangle"></i>
          <p>{error}</p>
          <button onClick={loadCharacters} className="retry-button">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`character-switch-panel ${className}`}>
      {/* Header */}
      <div className="panel-header">
        <h2>Character Manager</h2>
        <div className="header-controls">
          <select 
            value={filterRole} 
            onChange={(e) => setFilterRole(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Roles</option>
            <option value="main">Main</option>
            <option value="alt">Alt</option>
            <option value="boxer">Boxer</option>
          </select>
          
          <select 
            value={sortBy} 
            onChange={(e) => setSortBy(e.target.value)}
            className="sort-select"
          >
            <option value="last_session">Last Session</option>
            <option value="name">Name</option>
            <option value="level">Level</option>
            <option value="playtime">Playtime</option>
          </select>
          
          <button 
            onClick={() => setShowCreateForm(true)}
            className="create-button"
          >
            <i className="fas fa-plus"></i>
            Add Character
          </button>
        </div>
      </div>

      {/* Character Grid */}
      <div className="character-grid">
        {filteredAndSortedCharacters.map(character => (
          <div 
            key={character.character_id}
            className={`character-card ${selectedCharacter?.character_id === character.character_id ? 'selected' : ''}`}
            onClick={() => handleCharacterSwitch(character)}
          >
            {/* Character Header */}
            <div className="character-header">
              <div className="character-info">
                <span className="role-icon">{getRoleIcon(character.role)}</span>
                <h3 className="character-name">{character.name}</h3>
                {character.is_main_character && (
                  <span className="main-badge">MAIN</span>
                )}
              </div>
              <div className="character-level">
                <span className="level-badge">Lv.{character.level}</span>
              </div>
            </div>

            {/* Character Details */}
            <div className="character-details">
              <div className="detail-row">
                <span className="detail-label">Profession:</span>
                <span className="detail-value">{character.profession}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Faction:</span>
                <span 
                  className="detail-value faction"
                  style={{ color: getFactionColor(character.faction) }}
                >
                  {character.faction}
                </span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Location:</span>
                <span className="detail-value">{character.city}, {character.planet}</span>
              </div>
            </div>

            {/* Character Stats */}
            <div className="character-stats">
              <div className="stat-item">
                <i className="fas fa-clock"></i>
                <span>{formatPlaytime(character.total_playtime_hours)}</span>
              </div>
              <div className="stat-item">
                <i className="fas fa-trophy"></i>
                <span>{formatCredits(character.total_xp_gained)} XP</span>
              </div>
              <div className="stat-item">
                <i className="fas fa-coins"></i>
                <span>{formatCredits(character.total_credits_earned)}</span>
              </div>
            </div>

            {/* Character Actions */}
            <div className="character-actions">
              <div className="last-session">
                <i className="fas fa-calendar"></i>
                <span>{formatLastSession(character.last_session_at)}</span>
              </div>
              
              <div className="action-buttons">
                <button
                  className={`auto-launch-toggle ${character.auto_launch_enabled ? 'enabled' : ''}`}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleAutoLaunchToggle(character.character_id, !character.auto_launch_enabled);
                  }}
                  title={character.auto_launch_enabled ? 'Disable Auto-Launch' : 'Enable Auto-Launch'}
                >
                  <i className={`fas fa-rocket ${character.auto_launch_enabled ? 'active' : ''}`}></i>
                </button>
                
                <button
                  className="edit-button"
                  onClick={(e) => {
                    e.stopPropagation();
                    // TODO: Implement edit functionality
                  }}
                  title="Edit Character"
                >
                  <i className="fas fa-edit"></i>
                </button>
              </div>
            </div>

            {/* Selection Indicator */}
            {selectedCharacter?.character_id === character.character_id && (
              <div className="selection-indicator">
                <i className="fas fa-check"></i>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Empty State */}
      {filteredAndSortedCharacters.length === 0 && (
        <div className="empty-state">
          <i className="fas fa-users"></i>
          <h3>No Characters Found</h3>
          <p>You haven't created any characters yet.</p>
          <button 
            onClick={() => setShowCreateForm(true)}
            className="create-first-button"
          >
            Create Your First Character
          </button>
        </div>
      )}

      {/* Create Character Modal */}
      {showCreateForm && (
        <CreateCharacterModal
          discordUserId={discordUserId}
          onClose={() => setShowCreateForm(false)}
          onCharacterCreated={(newCharacter) => {
            setCharacters(prev => [...prev, newCharacter]);
            setShowCreateForm(false);
          }}
        />
      )}
    </div>
  );
};

// Create Character Modal Component
interface CreateCharacterModalProps {
  discordUserId: string;
  onClose: () => void;
  onCharacterCreated: (character: Character) => void;
}

const CreateCharacterModal: React.FC<CreateCharacterModalProps> = ({
  discordUserId,
  onClose,
  onCharacterCreated
}) => {
  const [formData, setFormData] = useState({
    name: '',
    server: 'Basilisk',
    race: 'Human',
    profession: 'Marksman',
    level: 1,
    faction: 'Neutral',
    city: '',
    guild: '',
    guild_tag: '',
    planet: '',
    role: 'alt',
    auto_launch_enabled: false,
    notes: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/characters', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          discord_user_id: discordUserId,
          ...formData
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to create character');
      }

      const newCharacter = await response.json();
      onCharacterCreated(newCharacter);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create character');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h3>Create New Character</h3>
          <button onClick={onClose} className="close-button">
            <i className="fas fa-times"></i>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="create-character-form">
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="name">Character Name *</label>
              <input
                id="name"
                type="text"
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                required
                placeholder="Enter character name"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="server">Server</label>
              <select
                id="server"
                value={formData.server}
                onChange={(e) => handleInputChange('server', e.target.value)}
              >
                <option value="Basilisk">Basilisk</option>
                <option value="TestCenter">Test Center</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="race">Race</label>
              <select
                id="race"
                value={formData.race}
                onChange={(e) => handleInputChange('race', e.target.value)}
              >
                <option value="Human">Human</option>
                <option value="Wookiee">Wookiee</option>
                <option value="Mon Calamari">Mon Calamari</option>
                <option value="Rodian">Rodian</option>
                <option value="Trandoshan">Trandoshan</option>
                <option value="Zabrak">Zabrak</option>
                <option value="Bothan">Bothan</option>
                <option value="Twi'lek">Twi'lek</option>
              </select>
            </div>
            
            <div className="form-group">
              <label htmlFor="profession">Profession</label>
              <select
                id="profession"
                value={formData.profession}
                onChange={(e) => handleInputChange('profession', e.target.value)}
              >
                <option value="Marksman">Marksman</option>
                <option value="Medic">Medic</option>
                <option value="Artisan">Artisan</option>
                <option value="Brawler">Brawler</option>
                <option value="Scout">Scout</option>
                <option value="Entertainer">Entertainer</option>
                <option value="Commando">Commando</option>
                <option value="Jedi">Jedi</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="level">Level</label>
              <input
                id="level"
                type="number"
                min="1"
                max="90"
                value={formData.level}
                onChange={(e) => handleInputChange('level', parseInt(e.target.value))}
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="faction">Faction</label>
              <select
                id="faction"
                value={formData.faction}
                onChange={(e) => handleInputChange('faction', e.target.value)}
              >
                <option value="Neutral">Neutral</option>
                <option value="Rebel">Rebel</option>
                <option value="Imperial">Imperial</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="city">City</label>
              <input
                id="city"
                type="text"
                value={formData.city}
                onChange={(e) => handleInputChange('city', e.target.value)}
                placeholder="Enter city name"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="planet">Planet</label>
              <input
                id="planet"
                type="text"
                value={formData.planet}
                onChange={(e) => handleInputChange('planet', e.target.value)}
                placeholder="Enter planet name"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="role">Role</label>
              <select
                id="role"
                value={formData.role}
                onChange={(e) => handleInputChange('role', e.target.value)}
              >
                <option value="alt">Alt Character</option>
                <option value="main">Main Character</option>
                <option value="boxer">Boxing Character</option>
              </select>
            </div>
            
            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={formData.auto_launch_enabled}
                  onChange={(e) => handleInputChange('auto_launch_enabled', e.target.checked)}
                />
                Enable Auto-Launch
              </label>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="notes">Notes</label>
            <textarea
              id="notes"
              value={formData.notes}
              onChange={(e) => handleInputChange('notes', e.target.value)}
              placeholder="Optional notes about this character"
              rows={3}
            />
          </div>

          {error && (
            <div className="error-message">
              <i className="fas fa-exclamation-triangle"></i>
              <span>{error}</span>
            </div>
          )}

          <div className="form-actions">
            <button 
              type="button" 
              onClick={onClose}
              className="cancel-button"
              disabled={loading}
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="create-button"
              disabled={loading || !formData.name}
            >
              {loading ? (
                <>
                  <i className="fas fa-spinner fa-spin"></i>
                  Creating...
                </>
              ) : (
                <>
                  <i className="fas fa-plus"></i>
                  Create Character
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CharacterSwitchPanel; 