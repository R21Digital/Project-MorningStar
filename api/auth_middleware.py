"""
MS11 Authentication Middleware
Provides JWT-based authentication with role-based access control
"""

import os
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from functools import wraps

import jwt
import bcrypt
from flask import request, jsonify, g, current_app

from core.structured_logging import StructuredLogger
from core.enhanced_error_handling import handle_exceptions

# Initialize logger
logger = StructuredLogger("auth_middleware")

@dataclass
class User:
    """User data class"""
    id: str
    username: str
    email: Optional[str] = None
    role: str = "user"  # admin, user, viewer
    permissions: List[str] = None
    created_at: str = ""
    last_login_at: str = ""
    preferences: Dict[str, Any] = None
    is_active: bool = True
    
    def __post_init__(self):
        if self.permissions is None:
            self.permissions = self._get_default_permissions()
        if self.preferences is None:
            self.preferences = self._get_default_preferences()
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
    
    def _get_default_permissions(self) -> List[str]:
        """Get default permissions based on role"""
        role_permissions = {
            'admin': [
                'dashboard:read', 'dashboard:write',
                'sessions:read', 'sessions:write', 'sessions:delete',
                'commands:execute', 'commands:history',
                'config:read', 'config:write',
                'users:read', 'users:write', 'users:delete',
                'metrics:read', 'health:read'
            ],
            'user': [
                'dashboard:read',
                'sessions:read', 'sessions:write',
                'commands:execute', 'commands:history',
                'metrics:read', 'health:read'
            ],
            'viewer': [
                'dashboard:read',
                'sessions:read',
                'commands:history',
                'metrics:read', 'health:read'
            ]
        }
        return role_permissions.get(self.role, [])
    
    def _get_default_preferences(self) -> Dict[str, Any]:
        """Get default user preferences"""
        return {
            'theme': 'dark',
            'notifications': True,
            'auto_refresh': True,
            'refresh_interval': 30,
            'dashboard_layout': {}
        }
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has specific permission"""
        if self.role == 'admin':  # Admin has all permissions
            return True
        return permission in self.permissions
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (excluding sensitive data)"""
        return asdict(self)

class JWTAuthManager:
    """JWT Authentication Manager"""
    
    def __init__(self, secret_key: str = None, algorithm: str = 'HS256'):
        self.secret_key = secret_key or os.getenv('JWT_SECRET_KEY', 'ms11-secret-key-change-in-production')
        self.algorithm = algorithm
        self.token_expiry = timedelta(hours=24)  # 24 hour expiry
        self.refresh_expiry = timedelta(days=7)  # 7 day refresh token expiry
        
        # In-memory user storage (replace with database in production)
        self.users: Dict[str, User] = {}
        self.refresh_tokens: Dict[str, str] = {}  # refresh_token -> user_id
        
        # Initialize with default admin user
        self._create_default_users()
    
    def _create_default_users(self):
        """Create default users for development/demo"""
        # Admin user
        admin_user = User(
            id=str(uuid.uuid4()),
            username='admin',
            email='admin@ms11.local',
            role='admin'
        )
        self.users['admin'] = admin_user
        
        # Regular user
        user = User(
            id=str(uuid.uuid4()),
            username='user',
            email='user@ms11.local', 
            role='user'
        )
        self.users['user'] = user
        
        # Viewer
        viewer = User(
            id=str(uuid.uuid4()),
            username='viewer',
            email='viewer@ms11.local',
            role='viewer'
        )
        self.users['viewer'] = viewer
        
        logger.info("Default users created", 
                   users=['admin', 'user', 'viewer'])
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_token(self, user: User, token_type: str = 'access') -> str:
        """Generate JWT token for user"""
        now = datetime.utcnow()
        
        if token_type == 'access':
            expiry = now + self.token_expiry
        elif token_type == 'refresh':
            expiry = now + self.refresh_expiry
        else:
            raise ValueError(f"Invalid token type: {token_type}")
        
        payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'permissions': user.permissions,
            'token_type': token_type,
            'iat': now,
            'exp': expiry,
            'jti': str(uuid.uuid4())  # Unique token ID
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        # Store refresh token
        if token_type == 'refresh':
            self.refresh_tokens[token] = user.id
        
        return token
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check if user still exists and is active
            user_id = payload.get('user_id')
            user = self.get_user_by_id(user_id)
            
            if not user or not user.is_active:
                logger.warning("Token verification failed: user not found or inactive", 
                              user_id=user_id)
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.info("Token verification failed: token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning("Token verification failed: invalid token", error=str(e))
            return None
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials"""
        # For demo purposes, accept any password for existing users
        # In production, implement proper password verification
        user = self.users.get(username)
        
        if user and user.is_active:
            # Update last login
            user.last_login_at = datetime.now().isoformat()
            
            logger.info("User authenticated", username=username, role=user.role)
            return user
        
        logger.warning("Authentication failed", username=username)
        return None
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        for user in self.users.values():
            if user.id == user_id:
                return user
        return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.users.get(username)
    
    def create_user(self, username: str, email: str, password: str, role: str = 'user') -> Optional[User]:
        """Create new user"""
        if username in self.users:
            logger.warning("User creation failed: username already exists", username=username)
            return None
        
        user = User(
            id=str(uuid.uuid4()),
            username=username,
            email=email,
            role=role
        )
        
        self.users[username] = user
        
        logger.info("User created", username=username, role=role)
        return user
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> bool:
        """Update user preferences"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.preferences.update(preferences)
        logger.info("User preferences updated", user_id=user_id)
        return True
    
    def refresh_access_token(self, refresh_token: str) -> Optional[str]:
        """Generate new access token from refresh token"""
        try:
            payload = self.verify_token(refresh_token)
            if not payload or payload.get('token_type') != 'refresh':
                return None
            
            user = self.get_user_by_id(payload['user_id'])
            if not user:
                return None
            
            # Generate new access token
            return self.generate_token(user, 'access')
            
        except Exception as e:
            logger.error("Token refresh failed", error=str(e))
            return None
    
    def revoke_refresh_token(self, refresh_token: str):
        """Revoke refresh token"""
        self.refresh_tokens.pop(refresh_token, None)

# Global auth manager instance
auth_manager = JWTAuthManager()

def require_auth(permission: str = None):
    """Decorator to require authentication and optionally check permissions"""
    def decorator(f):
        @wraps(f)
        @handle_exceptions(logger)
        def wrapper(*args, **kwargs):
            # Get token from Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({
                    'success': False,
                    'error': 'Authorization header required',
                    'timestamp': datetime.now().isoformat()
                }), 401
            
            try:
                # Extract token from "Bearer <token>"
                token_type, token = auth_header.split(' ', 1)
                if token_type.lower() != 'bearer':
                    raise ValueError("Invalid token type")
                
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': 'Invalid authorization header format',
                    'timestamp': datetime.now().isoformat()
                }), 401
            
            # Verify token
            payload = auth_manager.verify_token(token)
            if not payload:
                return jsonify({
                    'success': False,
                    'error': 'Invalid or expired token',
                    'timestamp': datetime.now().isoformat()
                }), 401
            
            # Get user from payload
            user = auth_manager.get_user_by_id(payload['user_id'])
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'User not found',
                    'timestamp': datetime.now().isoformat()
                }), 401
            
            # Check permissions if required
            if permission and not user.has_permission(permission):
                logger.warning("Access denied: insufficient permissions", 
                              user_id=user.id, permission=permission)
                return jsonify({
                    'success': False,
                    'error': 'Insufficient permissions',
                    'required_permission': permission,
                    'timestamp': datetime.now().isoformat()
                }), 403
            
            # Store user in request context
            g.current_user = user
            g.token_payload = payload
            
            return f(*args, **kwargs)
        
        return wrapper
    return decorator

def optional_auth():
    """Decorator for optional authentication (user info available if authenticated)"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            g.current_user = None
            g.token_payload = None
            
            # Try to get and verify token
            auth_header = request.headers.get('Authorization')
            if auth_header:
                try:
                    token_type, token = auth_header.split(' ', 1)
                    if token_type.lower() == 'bearer':
                        payload = auth_manager.verify_token(token)
                        if payload:
                            user = auth_manager.get_user_by_id(payload['user_id'])
                            if user:
                                g.current_user = user
                                g.token_payload = payload
                except Exception:
                    pass  # Continue without authentication
            
            return f(*args, **kwargs)
        
        return wrapper
    return decorator

def get_auth_manager() -> JWTAuthManager:
    """Get the global authentication manager"""
    return auth_manager