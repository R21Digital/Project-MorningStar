"""
MS11 Authentication Endpoints
Provides user authentication, registration, and profile management
"""

import time
from datetime import datetime
from typing import Dict, Any
from flask import Blueprint, request, jsonify, g

from core.structured_logging import StructuredLogger
from core.enhanced_error_handling import handle_exceptions
from api.auth_middleware import auth_manager, require_auth, optional_auth, User
from api.rest_endpoints import api_response, validate_json, log_api_call

# Initialize logger
logger = StructuredLogger("auth_endpoints")

# Create auth blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/login', methods=['POST'])
@log_api_call
@validate_json('username', 'password')
@handle_exceptions(logger)
def login():
    """Authenticate user and return JWT tokens"""
    try:
        data = g.request_data
        username = data['username'].strip()
        password = data['password']
        
        # Authenticate user
        user = auth_manager.authenticate_user(username, password)
        if not user:
            return api_response(
                False, 
                error="Invalid username or password",
                status_code=401
            )
        
        # Generate tokens
        access_token = auth_manager.generate_token(user, 'access')
        refresh_token = auth_manager.generate_token(user, 'refresh')
        
        response_data = {
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'permissions': user.permissions,
                'preferences': user.preferences,
                'last_login_at': user.last_login_at
            },
            'tokens': {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': 'Bearer',
                'expires_in': int(auth_manager.token_expiry.total_seconds())
            }
        }
        
        logger.info("User login successful", username=username, user_id=user.id)
        
        return api_response(
            True, 
            data=response_data,
            message=f"Welcome back, {user.username}!"
        )
        
    except Exception as e:
        logger.error("Login failed", error=str(e))
        return api_response(False, error="Login failed", status_code=500)

@auth_bp.route('/refresh', methods=['POST'])
@log_api_call
@validate_json('refresh_token')
@handle_exceptions(logger)
def refresh_token():
    """Refresh access token using refresh token"""
    try:
        data = g.request_data
        refresh_token = data['refresh_token']
        
        # Generate new access token
        new_access_token = auth_manager.refresh_access_token(refresh_token)
        if not new_access_token:
            return api_response(
                False, 
                error="Invalid or expired refresh token",
                status_code=401
            )
        
        response_data = {
            'access_token': new_access_token,
            'token_type': 'Bearer',
            'expires_in': int(auth_manager.token_expiry.total_seconds())
        }
        
        return api_response(True, data=response_data, message="Token refreshed successfully")
        
    except Exception as e:
        logger.error("Token refresh failed", error=str(e))
        return api_response(False, error="Token refresh failed", status_code=500)

@auth_bp.route('/logout', methods=['POST'])
@log_api_call
@require_auth()
@handle_exceptions(logger)
def logout():
    """Logout user and revoke refresh tokens"""
    try:
        user = g.current_user
        
        # In a full implementation, you'd track and revoke all user tokens
        # For now, we'll just log the logout
        logger.info("User logout", username=user.username, user_id=user.id)
        
        return api_response(True, message="Logged out successfully")
        
    except Exception as e:
        logger.error("Logout failed", error=str(e))
        return api_response(False, error="Logout failed", status_code=500)

@auth_bp.route('/verify', methods=['GET'])
@log_api_call
@require_auth()
@handle_exceptions(logger)
def verify_token():
    """Verify current token and return user info"""
    try:
        user = g.current_user
        token_payload = g.token_payload
        
        response_data = {
            'user': user.to_dict(),
            'token_info': {
                'issued_at': datetime.fromtimestamp(token_payload['iat']).isoformat(),
                'expires_at': datetime.fromtimestamp(token_payload['exp']).isoformat(),
                'token_id': token_payload['jti']
            }
        }
        
        return api_response(True, data=response_data, message="Token is valid")
        
    except Exception as e:
        logger.error("Token verification failed", error=str(e))
        return api_response(False, error="Token verification failed", status_code=500)

@auth_bp.route('/profile', methods=['GET'])
@log_api_call
@require_auth()
@handle_exceptions(logger)
def get_profile():
    """Get current user profile"""
    try:
        user = g.current_user
        
        return api_response(True, data=user.to_dict())
        
    except Exception as e:
        logger.error("Failed to get profile", error=str(e))
        return api_response(False, error="Failed to get profile", status_code=500)

@auth_bp.route('/profile', methods=['PUT'])
@log_api_call
@require_auth()
@validate_json()
@handle_exceptions(logger)
def update_profile():
    """Update current user profile"""
    try:
        user = g.current_user
        data = g.request_data
        
        # Update allowed fields
        updated_fields = []
        
        if 'email' in data and data['email'] != user.email:
            user.email = data['email']
            updated_fields.append('email')
        
        # Note: Role changes require admin permission
        if 'preferences' in data:
            user.preferences.update(data['preferences'])
            updated_fields.append('preferences')
        
        logger.info("Profile updated", user_id=user.id, fields=updated_fields)
        
        return api_response(
            True, 
            data=user.to_dict(),
            message="Profile updated successfully"
        )
        
    except Exception as e:
        logger.error("Failed to update profile", error=str(e))
        return api_response(False, error="Failed to update profile", status_code=500)

@auth_bp.route('/preferences', methods=['PUT'])
@log_api_call
@require_auth()
@validate_json()
@handle_exceptions(logger)
def update_preferences():
    """Update user preferences"""
    try:
        user = g.current_user
        data = g.request_data
        
        # Update preferences
        success = auth_manager.update_user_preferences(user.id, data)
        if not success:
            return api_response(False, error="Failed to update preferences", status_code=500)
        
        return api_response(
            True,
            data={'preferences': user.preferences},
            message="Preferences updated successfully"
        )
        
    except Exception as e:
        logger.error("Failed to update preferences", error=str(e))
        return api_response(False, error="Failed to update preferences", status_code=500)

# Admin-only endpoints
@auth_bp.route('/users', methods=['GET'])
@log_api_call
@require_auth('users:read')
@handle_exceptions(logger)
def list_users():
    """List all users (admin only)"""
    try:
        users = []
        for user in auth_manager.users.values():
            # Return user data without sensitive info
            user_data = user.to_dict()
            users.append(user_data)
        
        return api_response(True, data={'users': users, 'total': len(users)})
        
    except Exception as e:
        logger.error("Failed to list users", error=str(e))
        return api_response(False, error="Failed to list users", status_code=500)

@auth_bp.route('/users', methods=['POST'])
@log_api_call
@require_auth('users:write')
@validate_json('username', 'email', 'password')
@handle_exceptions(logger)
def create_user():
    """Create new user (admin only)"""
    try:
        data = g.request_data
        
        # Create user
        user = auth_manager.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            role=data.get('role', 'user')
        )
        
        if not user:
            return api_response(False, error="Username already exists", status_code=400)
        
        logger.info("User created by admin", 
                   new_user=user.username, 
                   created_by=g.current_user.username)
        
        return api_response(
            True, 
            data=user.to_dict(),
            message="User created successfully",
            status_code=201
        )
        
    except Exception as e:
        logger.error("Failed to create user", error=str(e))
        return api_response(False, error="Failed to create user", status_code=500)

@auth_bp.route('/users/<user_id>', methods=['PUT'])
@log_api_call
@require_auth('users:write')
@validate_json()
@handle_exceptions(logger)
def update_user(user_id: str):
    """Update user (admin only)"""
    try:
        data = g.request_data
        user = auth_manager.get_user_by_id(user_id)
        
        if not user:
            return api_response(False, error="User not found", status_code=404)
        
        # Update allowed fields
        updated_fields = []
        
        if 'role' in data and data['role'] != user.role:
            user.role = data['role']
            user.permissions = user._get_default_permissions()  # Update permissions based on role
            updated_fields.append('role')
        
        if 'is_active' in data and data['is_active'] != user.is_active:
            user.is_active = data['is_active']
            updated_fields.append('is_active')
        
        if 'email' in data and data['email'] != user.email:
            user.email = data['email']
            updated_fields.append('email')
        
        logger.info("User updated by admin", 
                   updated_user=user.username,
                   fields=updated_fields,
                   updated_by=g.current_user.username)
        
        return api_response(
            True,
            data=user.to_dict(), 
            message="User updated successfully"
        )
        
    except Exception as e:
        logger.error("Failed to update user", user_id=user_id, error=str(e))
        return api_response(False, error="Failed to update user", status_code=500)

@auth_bp.route('/users/<user_id>', methods=['DELETE'])
@log_api_call
@require_auth('users:delete')
@handle_exceptions(logger)
def delete_user(user_id: str):
    """Delete user (admin only)"""
    try:
        user = auth_manager.get_user_by_id(user_id)
        if not user:
            return api_response(False, error="User not found", status_code=404)
        
        # Prevent self-deletion
        if user.id == g.current_user.id:
            return api_response(False, error="Cannot delete your own account", status_code=400)
        
        # Remove user (in production, you might want to soft delete)
        username_to_remove = None
        for username, u in auth_manager.users.items():
            if u.id == user_id:
                username_to_remove = username
                break
        
        if username_to_remove:
            del auth_manager.users[username_to_remove]
            
        logger.info("User deleted by admin", 
                   deleted_user=user.username,
                   deleted_by=g.current_user.username)
        
        return api_response(True, message="User deleted successfully")
        
    except Exception as e:
        logger.error("Failed to delete user", user_id=user_id, error=str(e))
        return api_response(False, error="Failed to delete user", status_code=500)

def register_auth_routes(app):
    """Register authentication routes with Flask app"""
    app.register_blueprint(auth_bp)
    logger.info("Authentication routes registered")