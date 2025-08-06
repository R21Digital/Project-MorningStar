import React, { useState, useEffect } from 'react';
import './BotAccessControl.css';

interface UserInfo {
  discord_id: string;
  username: string;
  email: string;
  access_level: string;
  permissions: string[];
  bot_seats: number;
  active_sessions: number;
  status: string;
  last_login?: string;
  notes?: string;
}

interface AccessRequest {
  discord_id: string;
  username: string;
  email: string;
  request_date: string;
  request_reason: string;
  status: string;
  notes?: string;
}

interface PrivacySettings {
  profile_visibility: 'public' | 'friends' | 'private';
  session_visibility: 'public' | 'friends' | 'private';
  build_visibility: 'public' | 'friends' | 'private';
  stats_visibility: 'public' | 'friends' | 'private';
}

interface BotAccessControlProps {
  currentUser?: UserInfo;
  onAccessChange?: (userInfo: UserInfo) => void;
  onPrivacyChange?: (settings: PrivacySettings) => void;
}

const BotAccessControl: React.FC<BotAccessControlProps> = ({
  currentUser,
  onAccessChange,
  onPrivacyChange
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'requests' | 'privacy' | 'settings'>('overview');
  const [users, setUsers] = useState<UserInfo[]>([]);
  const [pendingRequests, setPendingRequests] = useState<AccessRequest[]>([]);
  const [privacySettings, setPrivacySettings] = useState<PrivacySettings>({
    profile_visibility: 'private',
    session_visibility: 'private',
    build_visibility: 'private',
    stats_visibility: 'private'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedUser, setSelectedUser] = useState<UserInfo | null>(null);
  const [showUserModal, setShowUserModal] = useState(false);
  const [showRequestModal, setShowRequestModal] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState<AccessRequest | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      // Simulate API calls
      const mockUsers: UserInfo[] = [
        {
          discord_id: "123456789012345678",
          username: "AdminUser",
          email: "admin@example.com",
          access_level: "admin",
          permissions: ["dashboard_access", "bot_control", "session_management", "user_management", "admin_panel"],
          bot_seats: 5,
          active_sessions: 2,
          status: "active",
          last_login: "2024-12-19T10:30:00Z",
          notes: "Primary administrator"
        },
        {
          discord_id: "234567890123456789",
          username: "ModeratorUser",
          email: "mod@example.com",
          access_level: "moderator",
          permissions: ["dashboard_access", "bot_control", "session_management", "user_management"],
          bot_seats: 3,
          active_sessions: 1,
          status: "active",
          last_login: "2024-12-19T09:15:00Z",
          notes: "Community moderator"
        },
        {
          discord_id: "345678901234567890",
          username: "RegularUser",
          email: "user@example.com",
          access_level: "user",
          permissions: ["dashboard_access", "bot_control", "session_management"],
          bot_seats: 2,
          active_sessions: 0,
          status: "active",
          last_login: "2024-12-18T14:20:00Z",
          notes: "Regular user"
        }
      ];

      const mockRequests: AccessRequest[] = [
        {
          discord_id: "567890123456789012",
          username: "NewUser",
          email: "new@example.com",
          request_date: "2024-12-19T11:00:00Z",
          request_reason: "Interested in MS11 automation",
          status: "pending",
          notes: "Awaiting admin review"
        }
      ];

      setUsers(mockUsers);
      setPendingRequests(mockRequests);
    } catch (err) {
      setError('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleGrantAccess = async (discordId: string, accessLevel: string) => {
    try {
      setLoading(true);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Update local state
      const updatedUsers = users.map(user => 
        user.discord_id === discordId 
          ? { ...user, access_level: accessLevel, status: 'active' }
          : user
      );
      setUsers(updatedUsers);
      
      // Remove from pending requests
      setPendingRequests(prev => prev.filter(req => req.discord_id !== discordId));
      
      setError(null);
    } catch (err) {
      setError('Failed to grant access');
    } finally {
      setLoading(false);
    }
  };

  const handleRevokeAccess = async (discordId: string, reason: string) => {
    try {
      setLoading(true);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Remove from users
      setUsers(prev => prev.filter(user => user.discord_id !== discordId));
      
      setError(null);
    } catch (err) {
      setError('Failed to revoke access');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateBotSeats = async (discordId: string, seats: number) => {
    try {
      setLoading(true);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Update local state
      const updatedUsers = users.map(user => 
        user.discord_id === discordId 
          ? { ...user, bot_seats: seats }
          : user
      );
      setUsers(updatedUsers);
      
      setError(null);
    } catch (err) {
      setError('Failed to update bot seats');
    } finally {
      setLoading(false);
    }
  };

  const handlePrivacyChange = (setting: keyof PrivacySettings, value: 'public' | 'friends' | 'private') => {
    const newSettings = { ...privacySettings, [setting]: value };
    setPrivacySettings(newSettings);
    onPrivacyChange?.(newSettings);
  };

  const getAccessLevelColor = (level: string) => {
    switch (level) {
      case 'admin': return '#dc3545';
      case 'moderator': return '#fd7e14';
      case 'user': return '#28a745';
      case 'trial': return '#6c757d';
      default: return '#6c757d';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return '#28a745';
      case 'pending': return '#ffc107';
      case 'revoked': return '#dc3545';
      default: return '#6c757d';
    }
  };

  const renderOverview = () => (
    <div className="access-overview">
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Total Users</h3>
          <div className="stat-value">{users.length}</div>
          <div className="stat-label">Approved users</div>
        </div>
        <div className="stat-card">
          <h3>Pending Requests</h3>
          <div className="stat-value">{pendingRequests.length}</div>
          <div className="stat-label">Awaiting review</div>
        </div>
        <div className="stat-card">
          <h3>Active Sessions</h3>
          <div className="stat-value">{users.reduce((sum, user) => sum + user.active_sessions, 0)}</div>
          <div className="stat-label">Currently running</div>
        </div>
        <div className="stat-card">
          <h3>Bot Seats Used</h3>
          <div className="stat-value">{users.reduce((sum, user) => sum + user.bot_seats, 0)}</div>
          <div className="stat-label">Of available seats</div>
        </div>
      </div>

      <div className="recent-activity">
        <h3>Recent Activity</h3>
        <div className="activity-list">
          {users.slice(0, 5).map(user => (
            <div key={user.discord_id} className="activity-item">
              <div className="activity-user">
                <span className="username">{user.username}</span>
                <span className="access-level" style={{ backgroundColor: getAccessLevelColor(user.access_level) }}>
                  {user.access_level}
                </span>
              </div>
              <div className="activity-details">
                <span>Last login: {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}</span>
                <span>Active sessions: {user.active_sessions}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderUsers = () => (
    <div className="users-management">
      <div className="users-header">
        <h3>User Management</h3>
        <button className="btn btn-primary" onClick={() => setShowUserModal(true)}>
          Add User
        </button>
      </div>

      <div className="users-table">
        <table>
          <thead>
            <tr>
              <th>User</th>
              <th>Access Level</th>
              <th>Bot Seats</th>
              <th>Active Sessions</th>
              <th>Status</th>
              <th>Last Login</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map(user => (
              <tr key={user.discord_id}>
                <td>
                  <div className="user-info">
                    <div className="username">{user.username}</div>
                    <div className="email">{user.email}</div>
                  </div>
                </td>
                <td>
                  <span className="access-level" style={{ backgroundColor: getAccessLevelColor(user.access_level) }}>
                    {user.access_level}
                  </span>
                </td>
                <td>
                  <div className="bot-seats">
                    <span>{user.bot_seats}</span>
                    <button 
                      className="btn btn-sm btn-outline"
                      onClick={() => {
                        setSelectedUser(user);
                        setShowUserModal(true);
                      }}
                    >
                      Edit
                    </button>
                  </div>
                </td>
                <td>{user.active_sessions}</td>
                <td>
                  <span className="status" style={{ backgroundColor: getStatusColor(user.status) }}>
                    {user.status}
                  </span>
                </td>
                <td>{user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}</td>
                <td>
                  <div className="actions">
                    <button 
                      className="btn btn-sm btn-outline"
                      onClick={() => {
                        setSelectedUser(user);
                        setShowUserModal(true);
                      }}
                    >
                      Edit
                    </button>
                    <button 
                      className="btn btn-sm btn-danger"
                      onClick={() => handleRevokeAccess(user.discord_id, 'Admin action')}
                    >
                      Revoke
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const renderRequests = () => (
    <div className="requests-management">
      <div className="requests-header">
        <h3>Pending Access Requests</h3>
      </div>

      {pendingRequests.length === 0 ? (
        <div className="no-requests">
          <p>No pending access requests</p>
        </div>
      ) : (
        <div className="requests-list">
          {pendingRequests.map(request => (
            <div key={request.discord_id} className="request-card">
              <div className="request-header">
                <div className="user-info">
                  <div className="username">{request.username}</div>
                  <div className="email">{request.email}</div>
                </div>
                <div className="request-date">
                  {new Date(request.request_date).toLocaleDateString()}
                </div>
              </div>
              <div className="request-reason">
                <strong>Reason:</strong> {request.request_reason}
              </div>
              <div className="request-actions">
                <button 
                  className="btn btn-success"
                  onClick={() => handleGrantAccess(request.discord_id, 'user')}
                >
                  Grant Access
                </button>
                <button 
                  className="btn btn-warning"
                  onClick={() => handleGrantAccess(request.discord_id, 'trial')}
                >
                  Grant Trial
                </button>
                <button 
                  className="btn btn-danger"
                  onClick={() => {
                    setSelectedRequest(request);
                    setShowRequestModal(true);
                  }}
                >
                  Deny
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderPrivacy = () => (
    <div className="privacy-settings">
      <h3>Privacy Settings</h3>
      <p>Control what information is visible to other users on SWGDB</p>

      <div className="privacy-options">
        <div className="privacy-option">
          <label>Profile Visibility</label>
          <select 
            value={privacySettings.profile_visibility}
            onChange={(e) => handlePrivacyChange('profile_visibility', e.target.value as any)}
          >
            <option value="private">Private</option>
            <option value="friends">Friends Only</option>
            <option value="public">Public</option>
          </select>
          <p className="option-description">Who can see your profile information</p>
        </div>

        <div className="privacy-option">
          <label>Session Visibility</label>
          <select 
            value={privacySettings.session_visibility}
            onChange={(e) => handlePrivacyChange('session_visibility', e.target.value as any)}
          >
            <option value="private">Private</option>
            <option value="friends">Friends Only</option>
            <option value="public">Public</option>
          </select>
          <p className="option-description">Who can see your session data</p>
        </div>

        <div className="privacy-option">
          <label>Build Visibility</label>
          <select 
            value={privacySettings.build_visibility}
            onChange={(e) => handlePrivacyChange('build_visibility', e.target.value as any)}
          >
            <option value="private">Private</option>
            <option value="friends">Friends Only</option>
            <option value="public">Public</option>
          </select>
          <p className="option-description">Who can see your character builds</p>
        </div>

        <div className="privacy-option">
          <label>Stats Visibility</label>
          <select 
            value={privacySettings.stats_visibility}
            onChange={(e) => handlePrivacyChange('stats_visibility', e.target.value as any)}
          >
            <option value="private">Private</option>
            <option value="friends">Friends Only</option>
            <option value="public">Public</option>
          </select>
          <p className="option-description">Who can see your statistics</p>
        </div>
      </div>

      <div className="privacy-info">
        <h4>Privacy Information</h4>
        <ul>
          <li><strong>Private:</strong> Only you can see this information</li>
          <li><strong>Friends Only:</strong> Only your approved friends can see this information</li>
          <li><strong>Public:</strong> Anyone can see this information on SWGDB</li>
        </ul>
      </div>
    </div>
  );

  const renderSettings = () => (
    <div className="access-settings">
      <h3>Access Control Settings</h3>

      <div className="settings-section">
        <h4>General Settings</h4>
        <div className="setting-item">
          <label>
            <input type="checkbox" defaultChecked />
            Require Discord OAuth2 login
          </label>
        </div>
        <div className="setting-item">
          <label>
            <input type="checkbox" defaultChecked />
            Enable session timeout
          </label>
        </div>
        <div className="setting-item">
          <label>
            <input type="checkbox" defaultChecked />
            Enable audit logging
          </label>
        </div>
      </div>

      <div className="settings-section">
        <h4>Bot Seat Management</h4>
        <div className="setting-item">
          <label>Total Bot Seats Available:</label>
          <input type="number" defaultValue={100} min={1} />
        </div>
        <div className="setting-item">
          <label>Reserved Seats:</label>
          <input type="number" defaultValue={20} min={0} />
        </div>
        <div className="setting-item">
          <label>Seat Timeout (hours):</label>
          <input type="number" defaultValue={24} min={1} />
        </div>
      </div>

      <div className="settings-section">
        <h4>Security Settings</h4>
        <div className="setting-item">
          <label>Max Failed Login Attempts:</label>
          <input type="number" defaultValue={5} min={1} />
        </div>
        <div className="setting-item">
          <label>Lockout Duration (minutes):</label>
          <input type="number" defaultValue={30} min={1} />
        </div>
        <div className="setting-item">
          <label>Session Timeout (minutes):</label>
          <input type="number" defaultValue={60} min={1} />
        </div>
      </div>

      <div className="settings-actions">
        <button className="btn btn-primary">Save Settings</button>
        <button className="btn btn-outline">Reset to Defaults</button>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="bot-access-control loading">
        <div className="loading-spinner">Loading...</div>
      </div>
    );
  }

  return (
    <div className="bot-access-control">
      {error && (
        <div className="error-message">
          {error}
          <button onClick={() => setError(null)}>×</button>
        </div>
      )}

      <div className="access-header">
        <h2>Bot Access Control</h2>
        <p>Manage user access, bot seats, and privacy settings</p>
      </div>

      <div className="access-tabs">
        <button 
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button 
          className={`tab ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          Users
        </button>
        <button 
          className={`tab ${activeTab === 'requests' ? 'active' : ''}`}
          onClick={() => setActiveTab('requests')}
        >
          Requests
        </button>
        <button 
          className={`tab ${activeTab === 'privacy' ? 'active' : ''}`}
          onClick={() => setActiveTab('privacy')}
        >
          Privacy
        </button>
        <button 
          className={`tab ${activeTab === 'settings' ? 'active' : ''}`}
          onClick={() => setActiveTab('settings')}
        >
          Settings
        </button>
      </div>

      <div className="access-content">
        {activeTab === 'overview' && renderOverview()}
        {activeTab === 'users' && renderUsers()}
        {activeTab === 'requests' && renderRequests()}
        {activeTab === 'privacy' && renderPrivacy()}
        {activeTab === 'settings' && renderSettings()}
      </div>

      {/* User Modal */}
      {showUserModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>{selectedUser ? 'Edit User' : 'Add User'}</h3>
              <button onClick={() => setShowUserModal(false)}>×</button>
            </div>
            <div className="modal-content">
              {/* User form would go here */}
              <p>User management form</p>
            </div>
          </div>
        </div>
      )}

      {/* Request Modal */}
      {showRequestModal && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h3>Review Request</h3>
              <button onClick={() => setShowRequestModal(false)}>×</button>
            </div>
            <div className="modal-content">
              {/* Request review form would go here */}
              <p>Request review form</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BotAccessControl; 