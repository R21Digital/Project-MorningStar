import React, { useState, useEffect } from 'react';
import './PublicProfileHeader.css';

interface SocialLinks {
  discord_tag: string;
  twitch_channel: string;
  steam_profile: string;
  youtube_channel: string;
  twitter_handle: string;
  reddit_username: string;
  website: string;
  guild_website: string;
}

interface UserProfile {
  discord_user_id: string;
  username: string;
  display_name: string;
  about_me: string;
  playstyle: string;
  favorite_activities: string[];
  social_links: SocialLinks;
  badges: string[];
  profile_visibility: string;
  created_at: string;
  updated_at: string;
  last_active: string;
}

interface PublicProfileHeaderProps {
  discordUserId: string;
  onEdit?: () => void;
  isEditable?: boolean;
}

const PublicProfileHeader: React.FC<PublicProfileHeaderProps> = ({
  discordUserId,
  onEdit,
  isEditable = false
}) => {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProfile();
  }, [discordUserId]);

  const loadProfile = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`/api/social/profiles/${discordUserId}`);
      const data = await response.json();

      if (data.success) {
        setProfile(data.profile);
      } else {
        setError(data.error || 'Failed to load profile');
      }
    } catch (err) {
      setError('Failed to load profile');
      console.error('Error loading profile:', err);
    } finally {
      setLoading(false);
    }
  };

  const getBadgeIcon = (badge: string): string => {
    const badgeIcons: Record<string, string> = {
      session_master: '🎯',
      xp_champion: '⭐',
      credit_magnate: '💰',
      playtime_legend: '⏰',
      profession_master: '🎓',
      crafter_extraordinaire: '🔨',
      combat_veteran: '⚔️',
      entertainer_star: '🎭',
      explorer: '🗺️',
      quest_master: '📜',
      collector: '📦',
      heroic_champion: '🏆',
      guild_leader: '👑',
      team_player: '🤝',
      mentor: '📚',
      community_pillar: '🏛️'
    };
    return badgeIcons[badge] || '🏅';
  };

  const getBadgeName = (badge: string): string => {
    const badgeNames: Record<string, string> = {
      session_master: 'Session Master',
      xp_champion: 'XP Champion',
      credit_magnate: 'Credit Magnate',
      playtime_legend: 'Playtime Legend',
      profession_master: 'Profession Master',
      crafter_extraordinaire: 'Crafter Extraordinaire',
      combat_veteran: 'Combat Veteran',
      entertainer_star: 'Entertainer Star',
      explorer: 'Explorer',
      quest_master: 'Quest Master',
      collector: 'Collector',
      heroic_champion: 'Heroic Champion',
      guild_leader: 'Guild Leader',
      team_player: 'Team Player',
      mentor: 'Mentor',
      community_pillar: 'Community Pillar'
    };
    return badgeNames[badge] || badge;
  };

  const getSocialIcon = (platform: string): string => {
    const icons: Record<string, string> = {
      discord: '💬',
      twitch: '📺',
      steam: '🎮',
      youtube: '📹',
      twitter: '🐦',
      reddit: '🤖',
      website: '🌐',
      guild_website: '🏰'
    };
    return icons[platform] || '🔗';
  };

  const formatDate = (dateString: string): string => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getTimeAgo = (dateString: string): string => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diffInMs = now.getTime() - date.getTime();
    const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));

    if (diffInDays === 0) return 'Today';
    if (diffInDays === 1) return 'Yesterday';
    if (diffInDays < 7) return `${diffInDays} days ago`;
    if (diffInDays < 30) return `${Math.floor(diffInDays / 7)} weeks ago`;
    if (diffInDays < 365) return `${Math.floor(diffInDays / 30)} months ago`;
    return `${Math.floor(diffInDays / 365)} years ago`;
  };

  if (loading) {
    return (
      <div className="public-profile-header loading">
        <div className="profile-skeleton">
          <div className="avatar-skeleton"></div>
          <div className="info-skeleton">
            <div className="name-skeleton"></div>
            <div className="playstyle-skeleton"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="public-profile-header error">
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          <span>{error || 'Profile not found'}</span>
        </div>
      </div>
    );
  }

  const hasSocialLinks = Object.values(profile.social_links).some(link => link.trim() !== '');

  return (
    <div className="public-profile-header">
      <div className="profile-main">
        <div className="profile-avatar">
          <div className="avatar-placeholder">
            {profile.display_name.charAt(0).toUpperCase()}
          </div>
        </div>

        <div className="profile-info">
          <div className="profile-name">
            <h2>{profile.display_name}</h2>
            {isEditable && (
              <button className="edit-button" onClick={onEdit}>
                ✏️ Edit
              </button>
            )}
          </div>

          {profile.playstyle && (
            <div className="profile-playstyle">
              <span className="playstyle-label">Playstyle:</span>
              <span className="playstyle-value">{profile.playstyle}</span>
            </div>
          )}

          {profile.about_me && (
            <div className="profile-about">
              <p>{profile.about_me}</p>
            </div>
          )}

          {profile.favorite_activities.length > 0 && (
            <div className="profile-activities">
              <span className="activities-label">Favorite Activities:</span>
              <div className="activities-list">
                {profile.favorite_activities.map((activity, index) => (
                  <span key={index} className="activity-tag">
                    {activity}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="profile-details">
        <div className="profile-badges">
          <h3>Badges</h3>
          {profile.badges.length > 0 ? (
            <div className="badges-grid">
              {profile.badges.map((badge, index) => (
                <div key={index} className="badge-item" title={getBadgeName(badge)}>
                  <span className="badge-icon">{getBadgeIcon(badge)}</span>
                  <span className="badge-name">{getBadgeName(badge)}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="no-badges">No badges earned yet</p>
          )}
        </div>

        {hasSocialLinks && (
          <div className="profile-social">
            <h3>Social Links</h3>
            <div className="social-links">
              {profile.social_links.discord_tag && (
                <a
                  href={`https://discord.com/users/${profile.social_links.discord_tag}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="social-link discord"
                  title="Discord"
                >
                  <span className="social-icon">{getSocialIcon('discord')}</span>
                  <span className="social-text">{profile.social_links.discord_tag}</span>
                </a>
              )}

              {profile.social_links.twitch_channel && (
                <a
                  href={`https://twitch.tv/${profile.social_links.twitch_channel}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="social-link twitch"
                  title="Twitch"
                >
                  <span className="social-icon">{getSocialIcon('twitch')}</span>
                  <span className="social-text">{profile.social_links.twitch_channel}</span>
                </a>
              )}

              {profile.social_links.steam_profile && (
                <a
                  href={profile.social_links.steam_profile}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="social-link steam"
                  title="Steam"
                >
                  <span className="social-icon">{getSocialIcon('steam')}</span>
                  <span className="social-text">Steam Profile</span>
                </a>
              )}

              {profile.social_links.youtube_channel && (
                <a
                  href={`https://youtube.com/${profile.social_links.youtube_channel}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="social-link youtube"
                  title="YouTube"
                >
                  <span className="social-icon">{getSocialIcon('youtube')}</span>
                  <span className="social-text">{profile.social_links.youtube_channel}</span>
                </a>
              )}

              {profile.social_links.twitter_handle && (
                <a
                  href={`https://twitter.com/${profile.social_links.twitter_handle}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="social-link twitter"
                  title="Twitter"
                >
                  <span className="social-icon">{getSocialIcon('twitter')}</span>
                  <span className="social-text">@{profile.social_links.twitter_handle}</span>
                </a>
              )}

              {profile.social_links.reddit_username && (
                <a
                  href={`https://reddit.com/user/${profile.social_links.reddit_username}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="social-link reddit"
                  title="Reddit"
                >
                  <span className="social-icon">{getSocialIcon('reddit')}</span>
                  <span className="social-text">u/{profile.social_links.reddit_username}</span>
                </a>
              )}

              {profile.social_links.website && (
                <a
                  href={profile.social_links.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="social-link website"
                  title="Website"
                >
                  <span className="social-icon">{getSocialIcon('website')}</span>
                  <span className="social-text">Website</span>
                </a>
              )}

              {profile.social_links.guild_website && (
                <a
                  href={profile.social_links.guild_website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="social-link guild-website"
                  title="Guild Website"
                >
                  <span className="social-icon">{getSocialIcon('guild_website')}</span>
                  <span className="social-text">Guild Website</span>
                </a>
              )}
            </div>
          </div>
        )}

        <div className="profile-meta">
          <div className="meta-item">
            <span className="meta-label">Member since:</span>
            <span className="meta-value">{formatDate(profile.created_at)}</span>
          </div>
          <div className="meta-item">
            <span className="meta-label">Last active:</span>
            <span className="meta-value">{getTimeAgo(profile.last_active)}</span>
          </div>
          <div className="meta-item">
            <span className="meta-label">Profile visibility:</span>
            <span className="meta-value visibility-{profile.profile_visibility}">
              {profile.profile_visibility.charAt(0).toUpperCase() + profile.profile_visibility.slice(1)}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PublicProfileHeader; 