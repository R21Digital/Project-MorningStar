#!/usr/bin/env python3
"""
Discord Token Validation API
Handles Discord OAuth2 token validation and access control for MS11 dashboard.
"""

import os
import json
import time
import hashlib
import secrets
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple, List
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DiscordTokenValidator:
    """Validates Discord OAuth2 tokens and manages access control."""
    
    def __init__(self, access_registry_path: str = "auth/access_registry.json"):
        self.access_registry_path = Path(access_registry_path)
        self.access_registry = self._load_access_registry()
        self.client_id = os.getenv("DISCORD_CLIENT_ID", "YOUR_DISCORD_CLIENT_ID")
        self.client_secret = os.getenv("DISCORD_CLIENT_SECRET", "YOUR_DISCORD_CLIENT_SECRET")
        self.token_url = "https://discord.com/api/oauth2/token"
        self.user_url = "https://discord.com/api/users/@me"
        
    def _load_access_registry(self) -> Dict[str, Any]:
        """Load access registry from JSON file."""
        try:
            if self.access_registry_path.exists():
                with open(self.access_registry_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning(f"Access registry not found: {self.access_registry_path}")
                return {}
        except Exception as e:
            logger.error(f"Error loading access registry: {e}")
            return {}
    
    def _save_access_registry(self) -> None:
        """Save access registry to JSON file."""
        try:
            with open(self.access_registry_path, 'w', encoding='utf-8') as f:
                json.dump(self.access_registry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving access registry: {e}")
    
    def validate_discord_token(self, access_token: str) -> Dict[str, Any]:
        """Validate Discord OAuth2 token and return user information."""
        if not access_token:
            return {
                "valid": False,
                "error": "No access token provided"
            }
        
        try:
            headers = {
                'Authorization': f"Bearer {access_token}"
            }
            
            response = requests.get(self.user_url, headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                discord_id = user_data['id']
                
                # Check if user has access
                access_info = self._check_user_access(discord_id)
                
                return {
                    "valid": True,
                    "user_id": discord_id,
                    "username": user_data['username'],
                    "email": user_data.get('email'),
                    "discriminator": user_data.get('discriminator'),
                    "avatar": user_data.get('avatar'),
                    "verified": user_data.get('verified', False),
                    "mfa_enabled": user_data.get('mfa_enabled', False),
                    "access_info": access_info
                }
            else:
                return {
                    "valid": False,
                    "error": f"HTTP {response.status_code}",
                    "error_description": response.text
                }
                
        except Exception as e:
            logger.error(f"Error validating Discord token: {e}")
            return {
                "valid": False,
                "error": "Network error",
                "error_description": str(e)
            }
    
    def _check_user_access(self, discord_id: str) -> Dict[str, Any]:
        """Check if user has access to MS11 dashboard."""
        approved_users = self.access_registry.get('approved_users', {})
        pending_requests = self.access_registry.get('pending_requests', {})
        revoked_access = self.access_registry.get('revoked_access', {})
        
        # Check if user is approved
        if discord_id in approved_users:
            user_info = approved_users[discord_id]
            return {
                "has_access": True,
                "access_level": user_info.get('access_level', 'user'),
                "permissions": user_info.get('permissions', []),
                "bot_seats": user_info.get('bot_seats', 0),
                "active_sessions": user_info.get('active_sessions', 0),
                "status": user_info.get('status', 'active'),
                "last_login": user_info.get('last_login'),
                "notes": user_info.get('notes', '')
            }
        
        # Check if user has pending request
        elif discord_id in pending_requests:
            request_info = pending_requests[discord_id]
            return {
                "has_access": False,
                "status": "pending",
                "request_date": request_info.get('request_date'),
                "request_reason": request_info.get('request_reason'),
                "notes": request_info.get('notes', '')
            }
        
        # Check if user is revoked
        elif discord_id in revoked_access:
            revoked_info = revoked_access[discord_id]
            return {
                "has_access": False,
                "status": "revoked",
                "revoked_date": revoked_info.get('revoked_date'),
                "revocation_reason": revoked_info.get('revocation_reason'),
                "notes": revoked_info.get('notes', '')
            }
        
        # User not in system
        else:
            return {
                "has_access": False,
                "status": "not_registered",
                "message": "User not registered in access system"
            }
    
    def request_access(self, discord_id: str, username: str, email: str, reason: str) -> Dict[str, Any]:
        """Request access to MS11 dashboard."""
        try:
            # Check if user already exists
            if discord_id in self.access_registry.get('approved_users', {}):
                return {
                    "success": False,
                    "error": "User already has access"
                }
            
            if discord_id in self.access_registry.get('pending_requests', {}):
                return {
                    "success": False,
                    "error": "Access request already pending"
                }
            
            # Add to pending requests
            if 'pending_requests' not in self.access_registry:
                self.access_registry['pending_requests'] = {}
            
            self.access_registry['pending_requests'][discord_id] = {
                "discord_id": discord_id,
                "username": username,
                "email": email,
                "request_date": datetime.now().isoformat() + "Z",
                "request_reason": reason,
                "status": "pending",
                "reviewed_by": None,
                "review_date": None,
                "notes": "Awaiting admin review"
            }
            
            self._save_access_registry()
            self._log_audit_event("access_requested", discord_id, username)
            
            return {
                "success": True,
                "message": "Access request submitted successfully"
            }
            
        except Exception as e:
            logger.error(f"Error requesting access: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def grant_access(self, discord_id: str, access_level: str, granted_by: str, notes: str = "") -> Dict[str, Any]:
        """Grant access to MS11 dashboard."""
        try:
            # Check if user exists in pending requests
            pending_requests = self.access_registry.get('pending_requests', {})
            if discord_id not in pending_requests:
                return {
                    "success": False,
                    "error": "No pending request found for user"
                }
            
            request_info = pending_requests[discord_id]
            
            # Move to approved users
            if 'approved_users' not in self.access_registry:
                self.access_registry['approved_users'] = {}
            
            access_levels = self.access_registry.get('access_levels', {})
            level_info = access_levels.get(access_level, {})
            
            self.access_registry['approved_users'][discord_id] = {
                "discord_id": discord_id,
                "username": request_info['username'],
                "email": request_info['email'],
                "access_level": access_level,
                "permissions": level_info.get('permissions', []),
                "bot_seats": level_info.get('max_bot_seats', 1),
                "active_sessions": 0,
                "last_login": None,
                "status": "active",
                "notes": notes,
                "granted_by": granted_by,
                "granted_date": datetime.now().isoformat() + "Z"
            }
            
            # Remove from pending requests
            del self.access_registry['pending_requests'][discord_id]
            
            self._save_access_registry()
            self._log_audit_event("access_granted", discord_id, request_info['username'], granted_by)
            
            return {
                "success": True,
                "message": f"Access granted to {request_info['username']} with level {access_level}"
            }
            
        except Exception as e:
            logger.error(f"Error granting access: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def revoke_access(self, discord_id: str, revoked_by: str, reason: str) -> Dict[str, Any]:
        """Revoke access to MS11 dashboard."""
        try:
            approved_users = self.access_registry.get('approved_users', {})
            if discord_id not in approved_users:
                return {
                    "success": False,
                    "error": "User not found in approved users"
                }
            
            user_info = approved_users[discord_id]
            
            # Move to revoked access
            if 'revoked_access' not in self.access_registry:
                self.access_registry['revoked_access'] = {}
            
            self.access_registry['revoked_access'][discord_id] = {
                "discord_id": discord_id,
                "username": user_info['username'],
                "email": user_info['email'],
                "revoked_date": datetime.now().isoformat() + "Z",
                "revoked_by": revoked_by,
                "revocation_reason": reason,
                "status": "revoked",
                "notes": f"Revoked by {revoked_by}"
            }
            
            # Remove from approved users
            del self.access_registry['approved_users'][discord_id]
            
            self._save_access_registry()
            self._log_audit_event("access_revoked", discord_id, user_info['username'], revoked_by)
            
            return {
                "success": True,
                "message": f"Access revoked for {user_info['username']}"
            }
            
        except Exception as e:
            logger.error(f"Error revoking access: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_user_permissions(self, discord_id: str, permissions: List[str], updated_by: str) -> Dict[str, Any]:
        """Update user permissions."""
        try:
            approved_users = self.access_registry.get('approved_users', {})
            if discord_id not in approved_users:
                return {
                    "success": False,
                    "error": "User not found in approved users"
                }
            
            user_info = approved_users[discord_id]
            old_permissions = user_info.get('permissions', [])
            
            user_info['permissions'] = permissions
            user_info['updated_by'] = updated_by
            user_info['updated_date'] = datetime.now().isoformat() + "Z"
            
            self._save_access_registry()
            self._log_audit_event("permission_change", discord_id, user_info['username'], updated_by)
            
            return {
                "success": True,
                "message": f"Permissions updated for {user_info['username']}",
                "old_permissions": old_permissions,
                "new_permissions": permissions
            }
            
        except Exception as e:
            logger.error(f"Error updating permissions: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def assign_bot_seat(self, discord_id: str, seats: int, assigned_by: str) -> Dict[str, Any]:
        """Assign bot seats to user."""
        try:
            approved_users = self.access_registry.get('approved_users', {})
            if discord_id not in approved_users:
                return {
                    "success": False,
                    "error": "User not found in approved users"
                }
            
            user_info = approved_users[discord_id]
            access_level = user_info.get('access_level', 'user')
            access_levels = self.access_registry.get('access_levels', {})
            level_info = access_levels.get(access_level, {})
            max_seats = level_info.get('max_bot_seats', 1)
            
            if seats > max_seats:
                return {
                    "success": False,
                    "error": f"Maximum {max_seats} bot seats allowed for {access_level} level"
                }
            
            old_seats = user_info.get('bot_seats', 0)
            user_info['bot_seats'] = seats
            user_info['seats_assigned_by'] = assigned_by
            user_info['seats_assigned_date'] = datetime.now().isoformat() + "Z"
            
            self._save_access_registry()
            self._log_audit_event("bot_seat_assigned", discord_id, user_info['username'], assigned_by)
            
            return {
                "success": True,
                "message": f"Bot seats updated for {user_info['username']}",
                "old_seats": old_seats,
                "new_seats": seats
            }
            
        except Exception as e:
            logger.error(f"Error assigning bot seats: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def check_permission(self, discord_id: str, permission: str) -> bool:
        """Check if user has specific permission."""
        try:
            approved_users = self.access_registry.get('approved_users', {})
            if discord_id not in approved_users:
                return False
            
            user_info = approved_users[discord_id]
            permissions = user_info.get('permissions', [])
            
            return permission in permissions
            
        except Exception as e:
            logger.error(f"Error checking permission: {e}")
            return False
    
    def get_user_info(self, discord_id: str) -> Optional[Dict[str, Any]]:
        """Get user information from access registry."""
        try:
            approved_users = self.access_registry.get('approved_users', {})
            return approved_users.get(discord_id)
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return None
    
    def get_pending_requests(self) -> List[Dict[str, Any]]:
        """Get all pending access requests."""
        try:
            pending_requests = self.access_registry.get('pending_requests', {})
            return [
                {"discord_id": discord_id, **request_info}
                for discord_id, request_info in pending_requests.items()
            ]
        except Exception as e:
            logger.error(f"Error getting pending requests: {e}")
            return []
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all approved users."""
        try:
            approved_users = self.access_registry.get('approved_users', {})
            return [
                {"discord_id": discord_id, **user_info}
                for discord_id, user_info in approved_users.items()
            ]
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    def _log_audit_event(self, event_type: str, discord_id: str, username: str, actor: str = None) -> None:
        """Log audit event."""
        try:
            if not self.access_registry.get('audit_log', {}).get('enabled', False):
                return
            
            audit_log = self.access_registry.get('audit_log', {})
            events_logged = audit_log.get('events_logged', [])
            
            if event_type in events_logged:
                event = {
                    "timestamp": datetime.now().isoformat() + "Z",
                    "event_type": event_type,
                    "discord_id": discord_id,
                    "username": username,
                    "actor": actor,
                    "ip_address": "127.0.0.1"  # Would be extracted from request
                }
                
                # In a real implementation, this would be stored in a database
                logger.info(f"AUDIT: {event}")
                
        except Exception as e:
            logger.error(f"Error logging audit event: {e}")

class AccessControlAPI:
    """API endpoints for access control management."""
    
    def __init__(self):
        self.validator = DiscordTokenValidator()
    
    def validate_token_endpoint(self, access_token: str) -> Dict[str, Any]:
        """API endpoint for token validation."""
        return self.validator.validate_discord_token(access_token)
    
    def request_access_endpoint(self, discord_id: str, username: str, email: str, reason: str) -> Dict[str, Any]:
        """API endpoint for access requests."""
        return self.validator.request_access(discord_id, username, email, reason)
    
    def grant_access_endpoint(self, discord_id: str, access_level: str, granted_by: str, notes: str = "") -> Dict[str, Any]:
        """API endpoint for granting access."""
        return self.validator.grant_access(discord_id, access_level, granted_by, notes)
    
    def revoke_access_endpoint(self, discord_id: str, revoked_by: str, reason: str) -> Dict[str, Any]:
        """API endpoint for revoking access."""
        return self.validator.revoke_access(discord_id, revoked_by, reason)
    
    def check_permission_endpoint(self, discord_id: str, permission: str) -> Dict[str, Any]:
        """API endpoint for permission checking."""
        has_permission = self.validator.check_permission(discord_id, permission)
        return {
            "has_permission": has_permission,
            "discord_id": discord_id,
            "permission": permission
        }
    
    def get_user_info_endpoint(self, discord_id: str) -> Dict[str, Any]:
        """API endpoint for getting user information."""
        user_info = self.validator.get_user_info(discord_id)
        if user_info:
            return {
                "success": True,
                "user_info": user_info
            }
        else:
            return {
                "success": False,
                "error": "User not found"
            }

def main():
    """Main function for testing the Discord token validator."""
    print("🔐 Discord Token Validation API")
    print("=" * 50)
    
    # Initialize validator
    validator = DiscordTokenValidator()
    
    # Test token validation (with mock token)
    print("\n📋 Testing Token Validation:")
    mock_token = "mock_access_token"
    result = validator.validate_discord_token(mock_token)
    print(f"Validation Result: {result}")
    
    # Test access checking
    print("\n🔍 Testing Access Control:")
    test_discord_id = "123456789012345678"
    access_info = validator._check_user_access(test_discord_id)
    print(f"Access Info: {access_info}")
    
    # Test permission checking
    print("\n🔐 Testing Permission Checking:")
    has_dashboard = validator.check_permission(test_discord_id, "dashboard_access")
    print(f"Has Dashboard Access: {has_dashboard}")
    
    # Test user management
    print("\n👥 Testing User Management:")
    all_users = validator.get_all_users()
    print(f"Total Approved Users: {len(all_users)}")
    
    pending_requests = validator.get_pending_requests()
    print(f"Pending Requests: {len(pending_requests)}")
    
    print("\n✅ Discord Token Validation API test completed!")

if __name__ == "__main__":
    main() 