#!/usr/bin/env python3
"""
Batch 116 Tests - Local Installer + Auth Gateway
Comprehensive tests for MS11 installer and Discord authentication.
"""

import os
import sys
import json
import time
import tempfile
import shutil
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from auth.discord_auth import DiscordAuthGateway, DiscordAuthManager, DiscordAuthServer
from auth.validate_token import TokenValidator, AuthFileValidator, TokenSecurityChecker


class TestDiscordAuthGateway(unittest.TestCase):
    """Test Discord OAuth2 authentication gateway."""
    
    def setUp(self):
        """Set up test environment."""
        self.gateway = DiscordAuthGateway()
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_auth_"))
        
    def tearDown(self):
        """Clean up test environment."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            
    def test_init(self):
        """Test gateway initialization."""
        self.assertIsNotNone(self.gateway.client_id)
        self.assertIsNotNone(self.gateway.client_secret)
        self.assertEqual(self.gateway.redirect_uri, "http://localhost:8080/callback")
        self.assertEqual(self.gateway.scope, "identify email")
        self.assertIsNotNone(self.gateway.state)
        
    def test_get_auth_url(self):
        """Test authorization URL generation."""
        auth_url = self.gateway.get_auth_url()
        
        self.assertIn("discord.com/api/oauth2/authorize", auth_url)
        self.assertIn("client_id=", auth_url)
        self.assertIn("redirect_uri=", auth_url)
        self.assertIn("response_type=code", auth_url)
        self.assertIn("scope=", auth_url)
        self.assertIn("state=", auth_url)
        
    @patch('auth.discord_auth.requests.post')
    def test_exchange_code_for_token_success(self, mock_post):
        """Test successful token exchange."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token',
            'expires_in': 604800,
            'token_type': 'Bearer',
            'scope': 'identify email'
        }
        mock_post.return_value = mock_response
        
        # Mock user info response
        with patch('auth.discord_auth.DiscordAuthGateway.get_user_info') as mock_user_info:
            mock_user_info.return_value = {
                'id': '123456789',
                'username': 'TestUser',
                'email': 'test@example.com'
            }
            
            token_data = self.gateway.exchange_code_for_token("test_code")
            
            self.assertEqual(token_data['access_token'], 'test_access_token')
            self.assertEqual(token_data['refresh_token'], 'test_refresh_token')
            self.assertEqual(token_data['user_id'], '123456789')
            self.assertEqual(token_data['username'], 'TestUser')
            
    @patch('auth.discord_auth.requests.post')
    def test_exchange_code_for_token_failure(self, mock_post):
        """Test failed token exchange."""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            'error': 'invalid_grant',
            'error_description': 'Invalid authorization code'
        }
        mock_post.return_value = mock_response
        
        with self.assertRaises(Exception) as context:
            self.gateway.exchange_code_for_token("invalid_code")
            
        self.assertIn("Token exchange failed", str(context.exception))
        
    @patch('auth.discord_auth.requests.get')
    def test_get_user_info_success(self, mock_get):
        """Test successful user info retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': '123456789',
            'username': 'TestUser',
            'email': 'test@example.com',
            'verified': True,
            'mfa_enabled': False
        }
        mock_get.return_value = mock_response
        
        user_info = self.gateway.get_user_info("test_token")
        
        self.assertEqual(user_info['id'], '123456789')
        self.assertEqual(user_info['username'], 'TestUser')
        self.assertEqual(user_info['email'], 'test@example.com')
        
    @patch('auth.discord_auth.requests.get')
    def test_get_user_info_failure(self, mock_get):
        """Test failed user info retrieval."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        with self.assertRaises(Exception) as context:
            self.gateway.get_user_info("invalid_token")
            
        self.assertIn("Failed to get user information", str(context.exception))
        
    @patch('auth.discord_auth.requests.post')
    def test_refresh_token_success(self, mock_post):
        """Test successful token refresh."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'new_access_token',
            'refresh_token': 'new_refresh_token',
            'expires_in': 604800,
            'token_type': 'Bearer'
        }
        mock_post.return_value = mock_response
        
        with patch('auth.discord_auth.DiscordAuthGateway.get_user_info') as mock_user_info:
            mock_user_info.return_value = {
                'id': '123456789',
                'username': 'TestUser',
                'email': 'test@example.com'
            }
            
            token_data = self.gateway.refresh_token("test_refresh_token")
            
            self.assertEqual(token_data['access_token'], 'new_access_token')
            self.assertEqual(token_data['refresh_token'], 'new_refresh_token')
            
    @patch('auth.discord_auth.requests.get')
    def test_validate_token_success(self, mock_get):
        """Test successful token validation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': '123456789'}
        mock_get.return_value = mock_response
        
        is_valid = self.gateway.validate_token("valid_token")
        self.assertTrue(is_valid)
        
    @patch('auth.discord_auth.requests.get')
    def test_validate_token_failure(self, mock_get):
        """Test failed token validation."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        is_valid = self.gateway.validate_token("invalid_token")
        self.assertFalse(is_valid)
        
    @patch('auth.discord_auth.requests.post')
    def test_revoke_token_success(self, mock_post):
        """Test successful token revocation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        success = self.gateway.revoke_token("test_token")
        self.assertTrue(success)
        
    @patch('auth.discord_auth.requests.post')
    def test_revoke_token_failure(self, mock_post):
        """Test failed token revocation."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        success = self.gateway.revoke_token("invalid_token")
        self.assertFalse(success)


class TestDiscordAuthManager(unittest.TestCase):
    """Test Discord authentication manager."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_manager_"))
        self.auth_file = self.temp_dir / "discord_auth.json"
        self.auth_manager = DiscordAuthManager(str(self.auth_file))
        
    def tearDown(self):
        """Clean up test environment."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            
    def test_init(self):
        """Test manager initialization."""
        self.assertEqual(self.auth_manager.auth_file, self.auth_file)
        self.assertIsNotNone(self.auth_manager.gateway)
        
    def test_save_and_load_auth_data(self):
        """Test saving and loading auth data."""
        auth_data = {
            'access_token': 'test_token',
            'refresh_token': 'test_refresh',
            'expires_at': time.time() + 3600,
            'user_id': '123456789',
            'username': 'TestUser',
            'scope': 'identify email',
            'token_type': 'Bearer'
        }
        
        # Save auth data
        self.auth_manager.save_auth_data(auth_data)
        
        # Load auth data
        loaded_data = self.auth_manager.load_auth_data()
        
        self.assertIsNotNone(loaded_data)
        self.assertEqual(loaded_data['access_token'], 'test_token')
        self.assertEqual(loaded_data['user_id'], '123456789')
        self.assertEqual(loaded_data['username'], 'TestUser')
        
    def test_load_auth_data_nonexistent(self):
        """Test loading auth data from nonexistent file."""
        # Remove auth file if it exists
        if self.auth_file.exists():
            self.auth_file.unlink()
            
        loaded_data = self.auth_manager.load_auth_data()
        self.assertIsNone(loaded_data)
        
    @patch('auth.discord_auth.DiscordAuthGateway.validate_token')
    @patch('auth.discord_auth.DiscordAuthGateway.refresh_token')
    def test_is_authenticated_valid_token(self, mock_refresh, mock_validate):
        """Test authentication check with valid token."""
        # Setup auth data
        auth_data = {
            'access_token': 'test_token',
            'refresh_token': 'test_refresh',
            'expires_at': time.time() + 3600,
            'user_id': '123456789',
            'username': 'TestUser'
        }
        self.auth_manager.save_auth_data(auth_data)
        
        # Mock valid token
        mock_validate.return_value = True
        
        is_authenticated = self.auth_manager.is_authenticated()
        self.assertTrue(is_authenticated)
        
    @patch('auth.discord_auth.DiscordAuthGateway.validate_token')
    @patch('auth.discord_auth.DiscordAuthGateway.refresh_token')
    def test_is_authenticated_expired_token_refresh_success(self, mock_refresh, mock_validate):
        """Test authentication check with expired token that refreshes successfully."""
        # Setup auth data with expired token
        auth_data = {
            'access_token': 'test_token',
            'refresh_token': 'test_refresh',
            'expires_at': time.time() - 3600,  # Expired
            'user_id': '123456789',
            'username': 'TestUser'
        }
        self.auth_manager.save_auth_data(auth_data)
        
        # Mock invalid token but successful refresh
        mock_validate.return_value = False
        mock_refresh.return_value = {
            'access_token': 'new_token',
            'refresh_token': 'new_refresh',
            'expires_in': 604800,
            'user_id': '123456789',
            'username': 'TestUser'
        }
        
        is_authenticated = self.auth_manager.is_authenticated()
        self.assertTrue(is_authenticated)
        
        # Verify auth data was updated
        updated_data = self.auth_manager.load_auth_data()
        self.assertEqual(updated_data['access_token'], 'new_token')
        
    @patch('auth.discord_auth.DiscordAuthGateway.get_user_info')
    def test_get_user_info_success(self, mock_user_info):
        """Test successful user info retrieval."""
        # Setup auth data
        auth_data = {
            'access_token': 'test_token',
            'user_id': '123456789',
            'username': 'TestUser'
        }
        self.auth_manager.save_auth_data(auth_data)
        
        # Mock user info response
        mock_user_info.return_value = {
            'id': '123456789',
            'username': 'TestUser',
            'email': 'test@example.com'
        }
        
        user_info = self.auth_manager.get_user_info()
        
        self.assertIsNotNone(user_info)
        self.assertEqual(user_info['id'], '123456789')
        self.assertEqual(user_info['username'], 'TestUser')
        
    @patch('auth.discord_auth.DiscordAuthGateway.revoke_token')
    def test_logout_success(self, mock_revoke):
        """Test successful logout."""
        # Setup auth data
        auth_data = {
            'access_token': 'test_token',
            'user_id': '123456789',
            'username': 'TestUser'
        }
        self.auth_manager.save_auth_data(auth_data)
        
        # Mock successful token revocation
        mock_revoke.return_value = True
        
        success = self.auth_manager.logout()
        self.assertTrue(success)
        
        # Verify auth file was removed
        self.assertFalse(self.auth_file.exists())


class TestTokenValidator(unittest.TestCase):
    """Test token validation functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.validator = TokenValidator()
        
    def test_init(self):
        """Test validator initialization."""
        self.assertIsNotNone(self.validator.client_id)
        self.assertIsNotNone(self.validator.client_secret)
        self.assertEqual(self.validator.token_url, "https://discord.com/api/oauth2/token")
        self.assertEqual(self.validator.user_url, "https://discord.com/api/users/@me")
        
    def test_validate_token_empty(self):
        """Test token validation with empty token."""
        is_valid = self.validator.validate_token("")
        self.assertFalse(is_valid)
        
    def test_validate_token_none(self):
        """Test token validation with None token."""
        is_valid = self.validator.validate_token(None)
        self.assertFalse(is_valid)
        
    @patch('auth.validate_token.requests.get')
    def test_validate_token_success(self, mock_get):
        """Test successful token validation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        is_valid = self.validator.validate_token("valid_token")
        self.assertTrue(is_valid)
        
    @patch('auth.validate_token.requests.get')
    def test_validate_token_failure(self, mock_get):
        """Test failed token validation."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        is_valid = self.validator.validate_token("invalid_token")
        self.assertFalse(is_valid)
        
    @patch('auth.validate_token.requests.get')
    def test_get_token_info_success(self, mock_get):
        """Test successful token info retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': '123456789',
            'username': 'TestUser',
            'email': 'test@example.com',
            'discriminator': '1234',
            'avatar': 'test_avatar',
            'verified': True,
            'mfa_enabled': False
        }
        mock_get.return_value = mock_response
        
        token_info = self.validator.get_token_info("valid_token")
        
        self.assertIsNotNone(token_info)
        self.assertTrue(token_info['valid'])
        self.assertEqual(token_info['user_id'], '123456789')
        self.assertEqual(token_info['username'], 'TestUser')
        self.assertEqual(token_info['email'], 'test@example.com')
        self.assertTrue(token_info['verified'])
        self.assertFalse(token_info['mfa_enabled'])
        
    @patch('auth.validate_token.requests.get')
    def test_get_token_info_failure(self, mock_get):
        """Test failed token info retrieval."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_get.return_value = mock_response
        
        token_info = self.validator.get_token_info("invalid_token")
        
        self.assertIsNotNone(token_info)
        self.assertFalse(token_info['valid'])
        self.assertIn('error', token_info)
        self.assertIn('error_description', token_info)
        
    @patch('auth.validate_token.requests.post')
    def test_refresh_token_success(self, mock_post):
        """Test successful token refresh."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'access_token': 'new_access_token',
            'refresh_token': 'new_refresh_token',
            'expires_in': 604800,
            'token_type': 'Bearer'
        }
        mock_post.return_value = mock_response
        
        with patch('auth.validate_token.TokenValidator.get_user_info') as mock_user_info:
            mock_user_info.return_value = {
                'id': '123456789',
                'username': 'TestUser',
                'email': 'test@example.com'
            }
            
            token_data = self.validator.refresh_token("test_refresh_token")
            
            self.assertIsNotNone(token_data)
            self.assertEqual(token_data['access_token'], 'new_access_token')
            self.assertEqual(token_data['refresh_token'], 'new_refresh_token')
            self.assertEqual(token_data['user_id'], '123456789')
            self.assertEqual(token_data['username'], 'TestUser')
            
    @patch('auth.validate_token.requests.post')
    def test_refresh_token_failure(self, mock_post):
        """Test failed token refresh."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            'error': 'invalid_grant',
            'error_description': 'Invalid refresh token'
        }
        mock_post.return_value = mock_response
        
        token_data = self.validator.refresh_token("invalid_refresh_token")
        
        self.assertIsNotNone(token_data)
        self.assertIn('error', token_data)
        self.assertEqual(token_data['error'], 'Token refresh failed')
        
    @patch('auth.validate_token.requests.get')
    def test_get_user_info_success(self, mock_get):
        """Test successful user info retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': '123456789',
            'username': 'TestUser',
            'email': 'test@example.com'
        }
        mock_get.return_value = mock_response
        
        user_info = self.validator.get_user_info("valid_token")
        
        self.assertIsNotNone(user_info)
        self.assertEqual(user_info['id'], '123456789')
        self.assertEqual(user_info['username'], 'TestUser')
        self.assertEqual(user_info['email'], 'test@example.com')
        
    @patch('auth.validate_token.requests.get')
    def test_get_user_info_failure(self, mock_get):
        """Test failed user info retrieval."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response
        
        user_info = self.validator.get_user_info("invalid_token")
        
        self.assertIsNone(user_info)
        
    @patch('auth.validate_token.requests.post')
    def test_revoke_token_success(self, mock_post):
        """Test successful token revocation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        success = self.validator.revoke_token("valid_token")
        self.assertTrue(success)
        
    @patch('auth.validate_token.requests.post')
    def test_revoke_token_failure(self, mock_post):
        """Test failed token revocation."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        success = self.validator.revoke_token("invalid_token")
        self.assertFalse(success)


class TestAuthFileValidator(unittest.TestCase):
    """Test authentication file validator."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_file_validator_"))
        self.auth_file = self.temp_dir / "discord_auth.json"
        self.validator = AuthFileValidator(str(self.auth_file))
        
    def tearDown(self):
        """Clean up test environment."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            
    def test_init(self):
        """Test validator initialization."""
        self.assertEqual(self.validator.auth_file, self.auth_file)
        self.assertIsNotNone(self.validator.validator)
        
    def test_load_and_validate_auth_nonexistent(self):
        """Test loading auth from nonexistent file."""
        is_valid, auth_data = self.validator.load_and_validate_auth()
        
        self.assertFalse(is_valid)
        self.assertIsNone(auth_data)
        
    def test_load_and_validate_auth_invalid_json(self):
        """Test loading auth from invalid JSON file."""
        # Create invalid JSON file
        with open(self.auth_file, 'w', encoding='utf-8') as f:
            f.write("invalid json content")
            
        is_valid, auth_data = self.validator.load_and_validate_auth()
        
        self.assertFalse(is_valid)
        self.assertIsNone(auth_data)
        
    def test_load_and_validate_auth_missing_fields(self):
        """Test loading auth with missing required fields."""
        # Create auth file with missing access_token
        auth_data = {
            'refresh_token': 'test_refresh',
            'user_id': '123456789'
        }
        
        with open(self.auth_file, 'w', encoding='utf-8') as f:
            json.dump(auth_data, f)
            
        is_valid, loaded_data = self.validator.load_and_validate_auth()
        
        self.assertFalse(is_valid)
        self.assertIsNone(loaded_data)
        
    @patch('auth.validate_token.TokenValidator.validate_token')
    def test_load_and_validate_auth_valid_token(self, mock_validate):
        """Test loading auth with valid token."""
        # Create auth file with valid data
        auth_data = {
            'access_token': 'test_token',
            'refresh_token': 'test_refresh',
            'expires_at': time.time() + 3600,
            'user_id': '123456789',
            'username': 'TestUser'
        }
        
        with open(self.auth_file, 'w', encoding='utf-8') as f:
            json.dump(auth_data, f)
            
        # Mock valid token
        mock_validate.return_value = True
        
        is_valid, loaded_data = self.validator.load_and_validate_auth()
        
        self.assertTrue(is_valid)
        self.assertIsNotNone(loaded_data)
        self.assertEqual(loaded_data['access_token'], 'test_token')
        self.assertEqual(loaded_data['user_id'], '123456789')
        
    @patch('auth.validate_token.TokenValidator.validate_token')
    @patch('auth.validate_token.TokenValidator.refresh_token')
    def test_load_and_validate_auth_expired_token_refresh_success(self, mock_refresh, mock_validate):
        """Test loading auth with expired token that refreshes successfully."""
        # Create auth file with expired token
        auth_data = {
            'access_token': 'test_token',
            'refresh_token': 'test_refresh',
            'expires_at': time.time() - 3600,  # Expired
            'user_id': '123456789',
            'username': 'TestUser'
        }
        
        with open(self.auth_file, 'w', encoding='utf-8') as f:
            json.dump(auth_data, f)
            
        # Mock invalid token but successful refresh
        mock_validate.return_value = False
        mock_refresh.return_value = {
            'access_token': 'new_token',
            'refresh_token': 'new_refresh',
            'expires_in': 604800,
            'user_id': '123456789',
            'username': 'TestUser'
        }
        
        is_valid, loaded_data = self.validator.load_and_validate_auth()
        
        self.assertTrue(is_valid)
        self.assertIsNotNone(loaded_data)
        self.assertEqual(loaded_data['access_token'], 'new_token')
        
        # Verify auth file was updated
        with open(self.auth_file, 'r', encoding='utf-8') as f:
            updated_data = json.load(f)
            self.assertEqual(updated_data['access_token'], 'new_token')
            
    def test_save_auth_data(self):
        """Test saving auth data."""
        auth_data = {
            'access_token': 'test_token',
            'user_id': '123456789',
            'username': 'TestUser'
        }
        
        self.validator.save_auth_data(auth_data)
        
        # Verify file was created
        self.assertTrue(self.auth_file.exists())
        
        # Verify data was saved correctly
        with open(self.auth_file, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            self.assertEqual(saved_data['access_token'], 'test_token')
            self.assertEqual(saved_data['user_id'], '123456789')
            
    @patch('auth.validate_token.TokenValidator.get_user_info')
    def test_get_user_info_success(self, mock_user_info):
        """Test successful user info retrieval."""
        # Setup auth data
        auth_data = {
            'access_token': 'test_token',
            'user_id': '123456789',
            'username': 'TestUser'
        }
        
        with open(self.auth_file, 'w', encoding='utf-8') as f:
            json.dump(auth_data, f)
            
        # Mock user info response
        mock_user_info.return_value = {
            'id': '123456789',
            'username': 'TestUser',
            'email': 'test@example.com'
        }
        
        user_info = self.validator.get_user_info()
        
        self.assertIsNotNone(user_info)
        self.assertEqual(user_info['id'], '123456789')
        self.assertEqual(user_info['username'], 'TestUser')
        
    @patch('auth.validate_token.TokenValidator.revoke_token')
    def test_logout_success(self, mock_revoke):
        """Test successful logout."""
        # Setup auth data
        auth_data = {
            'access_token': 'test_token',
            'user_id': '123456789',
            'username': 'TestUser'
        }
        
        with open(self.auth_file, 'w', encoding='utf-8') as f:
            json.dump(auth_data, f)
            
        # Mock successful token revocation
        mock_revoke.return_value = True
        
        success = self.validator.logout()
        self.assertTrue(success)
        
        # Verify auth file was removed
        self.assertFalse(self.auth_file.exists())


class TestTokenSecurityChecker(unittest.TestCase):
    """Test token security checker."""
    
    def setUp(self):
        """Set up test environment."""
        self.checker = TokenSecurityChecker()
        
    def test_init(self):
        """Test checker initialization."""
        self.assertIsNotNone(self.checker.validator)
        
    def test_check_token_permissions_empty_token(self):
        """Test permission check with empty token."""
        permissions = self.checker.check_token_permissions("")
        
        self.assertFalse(permissions['valid'])
        self.assertIn('error', permissions)
        self.assertEqual(permissions['error'], 'No token provided')
        
    @patch('auth.validate_token.requests.get')
    def test_check_token_permissions_success(self, mock_get):
        """Test successful permission check."""
        # Mock user info response
        user_response = Mock()
        user_response.status_code = 200
        user_response.json.return_value = {
            'id': '123456789',
            'username': 'TestUser',
            'email': 'test@example.com',
            'verified': True,
            'mfa_enabled': False
        }
        
        # Mock guilds response
        guilds_response = Mock()
        guilds_response.status_code = 200
        guilds_response.json.return_value = [
            {'id': '1', 'name': 'Test Server 1'},
            {'id': '2', 'name': 'Test Server 2'}
        ]
        
        # Setup mock to return different responses for different URLs
        def mock_get_side_effect(url, headers=None):
            if 'users/@me' in url:
                return user_response
            elif 'guilds' in url:
                return guilds_response
            else:
                return Mock(status_code=404)
                
        mock_get.side_effect = mock_get_side_effect
        
        permissions = self.checker.check_token_permissions("valid_token")
        
        self.assertTrue(permissions['valid'])
        self.assertEqual(permissions['user_id'], '123456789')
        self.assertEqual(permissions['username'], 'TestUser')
        self.assertEqual(permissions['email'], 'test@example.com')
        self.assertTrue(permissions['verified'])
        self.assertFalse(permissions['mfa_enabled'])
        self.assertEqual(permissions['guild_count'], 2)
        self.assertEqual(len(permissions['guilds']), 2)
        self.assertTrue(permissions['permissions']['can_read_user_info'])
        self.assertTrue(permissions['permissions']['can_read_guilds'])
        self.assertTrue(permissions['permissions']['has_email'])
        self.assertTrue(permissions['permissions']['is_verified'])
        
    @patch('auth.validate_token.requests.get')
    def test_check_token_permissions_user_info_failure(self, mock_get):
        """Test permission check with user info failure."""
        # Mock failed user info response
        user_response = Mock()
        user_response.status_code = 401
        mock_get.return_value = user_response
        
        permissions = self.checker.check_token_permissions("invalid_token")
        
        self.assertFalse(permissions['valid'])
        self.assertIn('error', permissions)
        self.assertIn('User info failed', permissions['error'])


class TestInstallerIntegration(unittest.TestCase):
    """Integration tests for installer functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="test_installer_"))
        self.install_dir = self.temp_dir / "MS11"
        
    def tearDown(self):
        """Clean up test environment."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            
    def test_installer_directory_creation(self):
        """Test installer directory creation."""
        directories = [
            self.install_dir,
            self.install_dir / "config",
            self.install_dir / "data",
            self.install_dir / "auth",
            self.install_dir / "logs",
            self.install_dir / "screenshots",
            self.install_dir / "session_logs",
            self.install_dir / "backups",
            self.install_dir / "temp"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.assertTrue(directory.exists())
            self.assertTrue(directory.is_dir())
            
    def test_configuration_file_creation(self):
        """Test configuration file creation."""
        config_dir = self.install_dir / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create user config
        user_config = {
            "installation": {
                "installation_path": str(self.install_dir),
                "version": "1.0.0",
                "install_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "first_run": True,
                "auto_update": True
            },
            "authentication": {
                "discord_auth_required": True,
                "auth_file_path": str(self.install_dir / "auth" / "discord_auth.json"),
                "auto_refresh_tokens": True,
                "session_timeout": 3600
            },
            "logging": {
                "log_level": "INFO",
                "log_file": str(self.install_dir / "logs" / "ms11.log"),
                "max_log_size": "10MB",
                "log_retention_days": 30,
                "console_output": True
            }
        }
        
        config_file = config_dir / "user_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(user_config, f, indent=2)
            
        self.assertTrue(config_file.exists())
        
        # Verify config can be loaded
        with open(config_file, 'r', encoding='utf-8') as f:
            loaded_config = json.load(f)
            
        self.assertEqual(loaded_config['installation']['installation_path'], str(self.install_dir))
        self.assertTrue(loaded_config['authentication']['discord_auth_required'])
        self.assertEqual(loaded_config['logging']['log_level'], "INFO")
        
    def test_auth_file_creation(self):
        """Test authentication file creation."""
        auth_dir = self.install_dir / "auth"
        auth_dir.mkdir(parents=True, exist_ok=True)
        
        auth_file = auth_dir / "discord_auth.json"
        
        # Create sample auth data
        auth_data = {
            'access_token': 'test_access_token',
            'refresh_token': 'test_refresh_token',
            'expires_at': time.time() + 3600,
            'user_id': '123456789',
            'username': 'TestUser',
            'email': 'test@example.com',
            'scope': 'identify email',
            'token_type': 'Bearer'
        }
        
        with open(auth_file, 'w', encoding='utf-8') as f:
            json.dump(auth_data, f, indent=2)
            
        self.assertTrue(auth_file.exists())
        
        # Verify auth data can be loaded
        with open(auth_file, 'r', encoding='utf-8') as f:
            loaded_auth = json.load(f)
            
        self.assertEqual(loaded_auth['access_token'], 'test_access_token')
        self.assertEqual(loaded_auth['user_id'], '123456789')
        self.assertEqual(loaded_auth['username'], 'TestUser')


def main():
    """Run all tests."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestDiscordAuthGateway,
        TestDiscordAuthManager,
        TestTokenValidator,
        TestAuthFileValidator,
        TestTokenSecurityChecker,
        TestInstallerIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
        
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "="*50)
    print("BATCH 116 TEST SUMMARY")
    print("="*50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  {test}: {traceback}")
            
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  {test}: {traceback}")
            
    return result.wasSuccessful()


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 