"""Test suite for Batch 096 - Steam + Discord Identity Bridge.

This test suite validates the comprehensive identity bridge system:
- Steam OAuth authentication integration
- Discord OAuth authentication integration
- Profile linking and management
- Identity bridge for cross-platform syncing
- Optional authentication with Discord as primary requirement
"""

import json
import pytest
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any

# Import the identity bridge modules
from core.steam_discord_bridge import (
    identity_bridge, SteamProfile, DiscordProfile, LinkedIdentity, 
    AuthStatus, SteamOAuth, DiscordOAuth, IdentityBridge
)


class TestSteamProfile:
    """Test Steam profile data structure."""
    
    def test_steam_profile_creation(self):
        """Test creating a Steam profile."""
        profile = SteamProfile(
            steam_id="76561198012345678",
            username="TestUser",
            avatar_url="https://example.com/avatar.jpg",
            profile_url="https://steamcommunity.com/id/testuser",
            real_name="John Doe",
            country_code="US",
            time_created=1234567890,
            last_updated=datetime.now().isoformat()
        )
        
        assert profile.steam_id == "76561198012345678"
        assert profile.username == "TestUser"
        assert profile.avatar_url == "https://example.com/avatar.jpg"
        assert profile.profile_url == "https://steamcommunity.com/id/testuser"
        assert profile.real_name == "John Doe"
        assert profile.country_code == "US"
        assert profile.time_created == 1234567890
        assert profile.last_updated is not None
    
    def test_steam_profile_optional_fields(self):
        """Test Steam profile with optional fields."""
        profile = SteamProfile(
            steam_id="76561198012345678",
            username="TestUser",
            avatar_url="https://example.com/avatar.jpg",
            profile_url="https://steamcommunity.com/id/testuser"
        )
        
        assert profile.steam_id == "76561198012345678"
        assert profile.username == "TestUser"
        assert profile.real_name is None
        assert profile.country_code is None
        assert profile.time_created is None


class TestDiscordProfile:
    """Test Discord profile data structure."""
    
    def test_discord_profile_creation(self):
        """Test creating a Discord profile."""
        profile = DiscordProfile(
            discord_id="123456789012345678",
            username="TestUser",
            discriminator="1234",
            avatar_url="https://cdn.discordapp.com/avatars/123456789012345678/avatar.png",
            email="test@example.com",
            verified=True,
            last_updated=datetime.now().isoformat()
        )
        
        assert profile.discord_id == "123456789012345678"
        assert profile.username == "TestUser"
        assert profile.discriminator == "1234"
        assert profile.avatar_url == "https://cdn.discordapp.com/avatars/123456789012345678/avatar.png"
        assert profile.email == "test@example.com"
        assert profile.verified is True
        assert profile.last_updated is not None
    
    def test_discord_profile_optional_fields(self):
        """Test Discord profile with optional fields."""
        profile = DiscordProfile(
            discord_id="123456789012345678",
            username="TestUser",
            discriminator="1234",
            avatar_url="https://cdn.discordapp.com/avatars/123456789012345678/avatar.png"
        )
        
        assert profile.discord_id == "123456789012345678"
        assert profile.username == "TestUser"
        assert profile.email is None
        assert profile.verified is False


class TestLinkedIdentity:
    """Test linked identity data structure."""
    
    def test_linked_identity_creation(self):
        """Test creating a linked identity."""
        steam_profile = SteamProfile(
            steam_id="76561198012345678",
            username="SteamUser",
            avatar_url="https://example.com/steam.jpg",
            profile_url="https://steamcommunity.com/id/steamuser"
        )
        
        discord_profile = DiscordProfile(
            discord_id="123456789012345678",
            username="DiscordUser",
            discriminator="1234",
            avatar_url="https://cdn.discordapp.com/avatars/123456789012345678/avatar.png"
        )
        
        identity = LinkedIdentity(
            discord_id="123456789012345678",
            steam_id="76561198012345678",
            linked=True,
            linked_at=datetime.now().isoformat(),
            steam_profile=steam_profile,
            discord_profile=discord_profile,
            auth_status=AuthStatus.LINKED,
            last_activity=datetime.now().isoformat()
        )
        
        assert identity.discord_id == "123456789012345678"
        assert identity.steam_id == "76561198012345678"
        assert identity.linked is True
        assert identity.linked_at is not None
        assert identity.steam_profile == steam_profile
        assert identity.discord_profile == discord_profile
        assert identity.auth_status == AuthStatus.LINKED
        assert identity.last_activity is not None
    
    def test_linked_identity_discord_only(self):
        """Test creating a Discord-only linked identity."""
        discord_profile = DiscordProfile(
            discord_id="123456789012345678",
            username="DiscordUser",
            discriminator="1234",
            avatar_url="https://cdn.discordapp.com/avatars/123456789012345678/avatar.png"
        )
        
        identity = LinkedIdentity(
            discord_id="123456789012345678",
            steam_id=None,
            linked=False,
            linked_at=None,
            steam_profile=None,
            discord_profile=discord_profile,
            auth_status=AuthStatus.AUTHENTICATED,
            last_activity=datetime.now().isoformat()
        )
        
        assert identity.discord_id == "123456789012345678"
        assert identity.steam_id is None
        assert identity.linked is False
        assert identity.linked_at is None
        assert identity.steam_profile is None
        assert identity.discord_profile == discord_profile
        assert identity.auth_status == AuthStatus.AUTHENTICATED


class TestSteamOAuth:
    """Test Steam OAuth functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.steam_oauth = SteamOAuth(
            api_key="test_api_key",
            redirect_uri="http://localhost:8000/auth/steam/callback"
        )
    
    def test_steam_oauth_initialization(self):
        """Test Steam OAuth initialization."""
        assert self.steam_oauth.api_key == "test_api_key"
        assert self.steam_oauth.redirect_uri == "http://localhost:8000/auth/steam/callback"
        assert self.steam_oauth.steam_openid_url == "https://steamcommunity.com/openid/login"
    
    @patch('core.steam_discord_bridge.secrets.token_urlsafe')
    def test_get_auth_url(self, mock_token):
        """Test generating Steam OAuth URL."""
        mock_token.return_value = "test_state_token"
        
        with patch('core.steam_discord_bridge.request') as mock_request:
            mock_request.host_url = "http://localhost:8000/"
            
            auth_url = self.steam_oauth.get_auth_url()
            
            assert "steamcommunity.com/openid/login" in auth_url
            assert "test_state_token" in auth_url
            assert "http://localhost:8000/auth/steam/callback" in auth_url
    
    def test_verify_response_valid(self):
        """Test verifying valid Steam OAuth response."""
        response_data = {
            'openid.claimed_id': 'https://steamcommunity.com/openid/id/76561198012345678'
        }
        
        steam_id = self.steam_oauth.verify_response(response_data)
        
        assert steam_id == "76561198012345678"
    
    def test_verify_response_invalid(self):
        """Test verifying invalid Steam OAuth response."""
        response_data = {
            'openid.claimed_id': 'invalid_format'
        }
        
        steam_id = self.steam_oauth.verify_response(response_data)
        
        assert steam_id is None
    
    @patch('core.steam_discord_bridge.requests.get')
    def test_get_steam_profile(self, mock_get):
        """Test getting Steam profile."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'response': {
                'players': [{
                    'steamid': '76561198012345678',
                    'personaname': 'TestUser',
                    'avatarfull': 'https://example.com/avatar.jpg',
                    'profileurl': 'https://steamcommunity.com/id/testuser',
                    'realname': 'John Doe',
                    'loccountrycode': 'US',
                    'timecreated': 1234567890
                }]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        profile = self.steam_oauth.get_steam_profile("76561198012345678")
        
        assert profile is not None
        assert profile.steam_id == "76561198012345678"
        assert profile.username == "TestUser"
        assert profile.real_name == "John Doe"
        assert profile.country_code == "US"


class TestDiscordOAuth:
    """Test Discord OAuth functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.discord_oauth = DiscordOAuth(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="http://localhost:8000/auth/discord/callback"
        )
    
    def test_discord_oauth_initialization(self):
        """Test Discord OAuth initialization."""
        assert self.discord_oauth.client_id == "test_client_id"
        assert self.discord_oauth.client_secret == "test_client_secret"
        assert self.discord_oauth.redirect_uri == "http://localhost:8000/auth/discord/callback"
        assert self.discord_oauth.discord_auth_url == "https://discord.com/api/oauth2/authorize"
        assert self.discord_oauth.discord_token_url == "https://discord.com/api/oauth2/token"
        assert self.discord_oauth.discord_user_url == "https://discord.com/api/users/@me"
    
    @patch('core.steam_discord_bridge.secrets.token_urlsafe')
    def test_get_auth_url(self, mock_token):
        """Test generating Discord OAuth URL."""
        mock_token.return_value = "test_state_token"
        
        auth_url = self.discord_oauth.get_auth_url()
        
        assert "discord.com/api/oauth2/authorize" in auth_url
        assert "test_state_token" in auth_url
        assert "http://localhost:8000/auth/discord/callback" in auth_url
        assert "identify" in auth_url
        assert "email" in auth_url
    
    @patch('core.steam_discord_bridge.requests.post')
    def test_exchange_code_for_token(self, mock_post):
        """Test exchanging code for token."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'access_token': 'test_access_token'
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        token = self.discord_oauth.exchange_code_for_token("test_code")
        
        assert token == "test_access_token"
    
    @patch('core.steam_discord_bridge.requests.get')
    def test_get_discord_profile(self, mock_get):
        """Test getting Discord profile."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'id': '123456789012345678',
            'username': 'TestUser',
            'discriminator': '1234',
            'avatar': 'test_avatar_hash',
            'email': 'test@example.com',
            'verified': True
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        profile = self.discord_oauth.get_discord_profile("test_access_token")
        
        assert profile is not None
        assert profile.discord_id == "123456789012345678"
        assert profile.username == "TestUser"
        assert profile.discriminator == "1234"
        assert profile.email == "test@example.com"
        assert profile.verified is True


class TestIdentityBridge:
    """Test identity bridge functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "test_config.json"
        
        # Create test configuration
        test_config = {
            "steam": {
                "api_key": "test_steam_key",
                "redirect_uri": "http://localhost:8000/auth/steam/callback"
            },
            "discord": {
                "client_id": "test_discord_client",
                "client_secret": "test_discord_secret",
                "redirect_uri": "http://localhost:8000/auth/discord/callback"
            },
            "security": {
                "session_timeout": 3600,
                "max_session_age": 86400,
                "require_discord": True,
                "optional_steam": True
            },
            "storage": {
                "encrypt_profiles": False,
                "backup_enabled": True,
                "backup_interval": 86400
            }
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(test_config, f)
        
        self.bridge = IdentityBridge(str(self.config_path))
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_identity_bridge_initialization(self):
        """Test identity bridge initialization."""
        assert self.bridge.config is not None
        assert self.bridge.steam_oauth is not None
        assert self.bridge.discord_oauth is not None
        assert self.bridge.identities_dir is not None
        assert self.bridge.active_sessions == {}
    
    def test_load_config(self):
        """Test configuration loading."""
        config = self.bridge._load_config()
        
        assert config["steam"]["api_key"] == "test_steam_key"
        assert config["discord"]["client_id"] == "test_discord_client"
        assert config["security"]["require_discord"] is True
        assert config["security"]["optional_steam"] is True
    
    @patch('core.steam_discord_bridge.secrets.token_urlsafe')
    def test_start_discord_auth(self, mock_token):
        """Test starting Discord authentication."""
        mock_token.return_value = "test_state"
        
        with patch('core.steam_discord_bridge.session') as mock_session:
            auth_url = self.bridge.start_discord_auth()
            
            assert "discord.com/api/oauth2/authorize" in auth_url
            mock_session.__setitem__.assert_called()
    
    @patch('core.steam_discord_bridge.secrets.token_urlsafe')
    def test_start_steam_auth(self, mock_token):
        """Test starting Steam authentication."""
        mock_token.return_value = "test_state"
        
        with patch('core.steam_discord_bridge.session') as mock_session:
            auth_url = self.bridge.start_steam_auth()
            
            assert "steamcommunity.com/openid/login" in auth_url
            mock_session.__setitem__.assert_called()
    
    def test_link_identities(self):
        """Test linking Discord and Steam identities."""
        discord_id = "123456789012345678"
        steam_id = "76561198012345678"
        
        # Mock session data
        with patch('core.steam_discord_bridge.session') as mock_session:
            mock_session.get.side_effect = lambda key, default=None: {
                'discord_profile': {'discord_id': discord_id, 'username': 'TestUser'},
                'steam_profile': {'steam_id': steam_id, 'username': 'SteamUser'}
            }.get(key, default)
            
            linked_identity = self.bridge.link_identities(discord_id, steam_id)
            
            assert linked_identity.discord_id == discord_id
            assert linked_identity.steam_id == steam_id
            assert linked_identity.linked is True
            assert linked_identity.auth_status == AuthStatus.LINKED
    
    def test_save_linked_identity(self):
        """Test saving linked identity."""
        steam_profile = SteamProfile(
            steam_id="76561198012345678",
            username="SteamUser",
            avatar_url="https://example.com/steam.jpg",
            profile_url="https://steamcommunity.com/id/steamuser"
        )
        
        discord_profile = DiscordProfile(
            discord_id="123456789012345678",
            username="DiscordUser",
            discriminator="1234",
            avatar_url="https://cdn.discordapp.com/avatars/123456789012345678/avatar.png"
        )
        
        identity = LinkedIdentity(
            discord_id="123456789012345678",
            steam_id="76561198012345678",
            linked=True,
            linked_at=datetime.now().isoformat(),
            steam_profile=steam_profile,
            discord_profile=discord_profile,
            auth_status=AuthStatus.LINKED,
            last_activity=datetime.now().isoformat()
        )
        
        self.bridge._save_linked_identity(identity)
        
        # Check if file was created
        identity_file = self.bridge.identities_dir / f"{identity.discord_id}.json"
        assert identity_file.exists()
        
        # Load and verify data
        with open(identity_file, 'r') as f:
            data = json.load(f)
        
        assert data['discord_id'] == identity.discord_id
        assert data['steam_id'] == identity.steam_id
        assert data['linked'] == identity.linked
    
    def test_get_linked_identity(self):
        """Test getting linked identity."""
        # Create a test identity file
        discord_id = "123456789012345678"
        identity_data = {
            "discord_id": discord_id,
            "steam_id": "76561198012345678",
            "linked": True,
            "linked_at": datetime.now().isoformat(),
            "auth_status": "linked",
            "last_activity": datetime.now().isoformat(),
            "steam_profile": {
                "steam_id": "76561198012345678",
                "username": "SteamUser",
                "avatar_url": "https://example.com/steam.jpg",
                "profile_url": "https://steamcommunity.com/id/steamuser"
            },
            "discord_profile": {
                "discord_id": discord_id,
                "username": "DiscordUser",
                "discriminator": "1234",
                "avatar_url": "https://cdn.discordapp.com/avatars/123456789012345678/avatar.png"
            }
        }
        
        identity_file = self.bridge.identities_dir / f"{discord_id}.json"
        with open(identity_file, 'w') as f:
            json.dump(identity_data, f)
        
        # Get linked identity
        linked_identity = self.bridge.get_linked_identity(discord_id)
        
        assert linked_identity is not None
        assert linked_identity.discord_id == discord_id
        assert linked_identity.steam_id == "76561198012345678"
        assert linked_identity.linked is True
        assert linked_identity.auth_status == AuthStatus.LINKED
    
    def test_unlink_steam(self):
        """Test unlinking Steam account."""
        # Create a test identity file
        discord_id = "123456789012345678"
        identity_data = {
            "discord_id": discord_id,
            "steam_id": "76561198012345678",
            "linked": True,
            "linked_at": datetime.now().isoformat(),
            "auth_status": "linked",
            "last_activity": datetime.now().isoformat()
        }
        
        identity_file = self.bridge.identities_dir / f"{discord_id}.json"
        with open(identity_file, 'w') as f:
            json.dump(identity_data, f)
        
        # Unlink Steam
        success = self.bridge.unlink_steam(discord_id)
        
        assert success is True
        
        # Check updated identity
        updated_identity = self.bridge.get_linked_identity(discord_id)
        assert updated_identity is not None
        assert updated_identity.steam_id is None
        assert updated_identity.linked is False
        assert updated_identity.auth_status == AuthStatus.AUTHENTICATED
    
    def test_get_statistics(self):
        """Test getting bridge statistics."""
        # Create some test identity files
        test_identities = [
            {"discord_id": "123456789012345678", "linked": True},
            {"discord_id": "234567890123456789", "linked": True},
            {"discord_id": "345678901234567890", "linked": False}
        ]
        
        for identity_data in test_identities:
            identity_file = self.bridge.identities_dir / f"{identity_data['discord_id']}.json"
            with open(identity_file, 'w') as f:
                json.dump(identity_data, f)
        
        stats = self.bridge.get_statistics()
        
        assert stats['total_identities'] == 3
        assert stats['linked_identities'] == 2
        assert stats['discord_only'] == 1
        assert stats['link_rate'] == 2/3


class TestAuthStatus:
    """Test authentication status enumeration."""
    
    def test_auth_status_values(self):
        """Test authentication status values."""
        assert AuthStatus.PENDING.value == "pending"
        assert AuthStatus.AUTHENTICATED.value == "authenticated"
        assert AuthStatus.LINKED.value == "linked"
        assert AuthStatus.EXPIRED.value == "expired"
        assert AuthStatus.FAILED.value == "failed"
    
    def test_auth_status_creation(self):
        """Test creating authentication status."""
        status = AuthStatus.LINKED
        assert status == AuthStatus.LINKED
        assert status.value == "linked"


if __name__ == "__main__":
    pytest.main([__file__]) 