#!/usr/bin/env python3
"""
Session Bridge API for Remote Bot Control

This module provides the API endpoints for controlling and monitoring
bot sessions from the web dashboard on swgdb.com.
"""

import json
import os
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict
from flask import Flask, request, jsonify, session
from flask_cors import CORS

from auth.validate_token import AuthFileValidator, TokenValidator
from core.session_manager import SessionManager
from core.remote_control import RemoteControlManager


@dataclass
class SessionStatus:
    """Represents the current status of a bot session."""
    session_id: str
    status: str  # running, paused, stopped, error
    mode: str
    start_time: str
    uptime_seconds: int
    current_task: str
    stuck_detected: bool
    stuck_duration: Optional[int] = None
    last_activity: str
    performance_metrics: Dict[str, Any]
    error_message: Optional[str] = None


@dataclass
class ControlCommand:
    """Represents a control command sent to the bot."""
    command: str  # start, pause, stop, reset
    session_id: Optional[str] = None
    mode: Optional[str] = None
    parameters: Dict[str, Any]
    timestamp: str
    user_id: str


class SessionBridgeAPI:
    """API for remote bot session control and monitoring."""
    
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = os.getenv('SESSION_BRIDGE_SECRET_KEY', 'your-secret-key-here')
        CORS(self.app)  # Enable CORS for web dashboard
        
        # Initialize components
        self.auth_validator = AuthFileValidator()
        self.token_validator = TokenValidator()
        self.remote_control = RemoteControlManager()
        
        # Session tracking
        self.active_sessions: Dict[str, SessionManager] = {}
        self.session_status_cache: Dict[str, SessionStatus] = {}
        self.control_commands: List[ControlCommand] = []
        
        # Setup routes
        self._setup_routes()
        
        # Start background monitoring
        self._start_background_monitoring()
    
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.app.route('/api/session-bridge/status', methods=['GET'])
        def get_bridge_status():
            """Get overall bridge status."""
            return jsonify({
                'status': 'active',
                'active_sessions': len(self.active_sessions),
                'total_commands': len(self.control_commands),
                'last_heartbeat': datetime.now().isoformat()
            })
        
        @self.app.route('/api/session-bridge/auth/verify', methods=['POST'])
        def verify_user_auth():
            """Verify user authentication token."""
            try:
                data = request.get_json()
                token = data.get('token')
                user_id = data.get('user_id')
                
                if not token or not user_id:
                    return jsonify({'error': 'Missing token or user_id'}), 400
                
                # Validate token
                is_valid, auth_data = self.auth_validator.load_and_validate_auth()
                if not is_valid or auth_data.get('user_id') != user_id:
                    return jsonify({'error': 'Invalid authentication'}), 401
                
                return jsonify({
                    'authenticated': True,
                    'user_id': user_id,
                    'permissions': self._get_user_permissions(user_id)
                })
            
            except Exception as e:
                return jsonify({'error': f'Authentication error: {str(e)}'}), 500
        
        @self.app.route('/api/session-bridge/sessions', methods=['GET'])
        def get_active_sessions():
            """Get list of active sessions."""
            try:
                # Verify authentication
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({'error': 'Missing authentication'}), 401
                
                token = auth_header.split(' ')[1]
                is_valid, auth_data = self.auth_validator.load_and_validate_auth()
                if not is_valid:
                    return jsonify({'error': 'Invalid authentication'}), 401
                
                sessions = []
                for session_id, session_manager in self.active_sessions.items():
                    status = self._get_session_status(session_id)
                    sessions.append(asdict(status))
                
                return jsonify({
                    'sessions': sessions,
                    'total': len(sessions)
                })
            
            except Exception as e:
                return jsonify({'error': f'Error retrieving sessions: {str(e)}'}), 500
        
        @self.app.route('/api/session-bridge/session/<session_id>', methods=['GET'])
        def get_session_detail(session_id):
            """Get detailed status of a specific session."""
            try:
                # Verify authentication
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({'error': 'Missing authentication'}), 401
                
                if session_id not in self.active_sessions:
                    return jsonify({'error': 'Session not found'}), 404
                
                status = self._get_session_status(session_id)
                return jsonify(asdict(status))
            
            except Exception as e:
                return jsonify({'error': f'Error retrieving session: {str(e)}'}), 500
        
        @self.app.route('/api/session-bridge/session/start', methods=['POST'])
        def start_session():
            """Start a new bot session."""
            try:
                # Verify authentication
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({'error': 'Missing authentication'}), 401
                
                data = request.get_json()
                mode = data.get('mode', 'medic')
                parameters = data.get('parameters', {})
                
                # Start session via remote control
                session_id = self.remote_control.start_session(mode, parameters)
                
                if session_id:
                    return jsonify({
                        'success': True,
                        'session_id': session_id,
                        'message': f'Session started in {mode} mode'
                    })
                else:
                    return jsonify({'error': 'Failed to start session'}), 500
            
            except Exception as e:
                return jsonify({'error': f'Error starting session: {str(e)}'}), 500
        
        @self.app.route('/api/session-bridge/session/<session_id>/control', methods=['POST'])
        def control_session(session_id):
            """Control an active session (pause, stop, reset)."""
            try:
                # Verify authentication
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({'error': 'Missing authentication'}), 401
                
                if session_id not in self.active_sessions:
                    return jsonify({'error': 'Session not found'}), 404
                
                data = request.get_json()
                command = data.get('command')
                
                if command not in ['pause', 'stop', 'reset']:
                    return jsonify({'error': 'Invalid command'}), 400
                
                # Execute command via remote control
                success = self.remote_control.control_session(session_id, command)
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': f'Session {command} command executed'
                    })
                else:
                    return jsonify({'error': f'Failed to {command} session'}), 500
            
            except Exception as e:
                return jsonify({'error': f'Error controlling session: {str(e)}'}), 500
        
        @self.app.route('/api/session-bridge/session/<session_id>/status', methods=['GET'])
        def get_session_status_endpoint(session_id):
            """Get real-time status of a session."""
            try:
                # Verify authentication
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({'error': 'Missing authentication'}), 401
                
                if session_id not in self.active_sessions:
                    return jsonify({'error': 'Session not found'}), 404
                
                status = self._get_session_status(session_id)
                return jsonify(asdict(status))
            
            except Exception as e:
                return jsonify({'error': f'Error getting status: {str(e)}'}), 500
        
        @self.app.route('/api/session-bridge/alerts/discord', methods=['POST'])
        def trigger_discord_alert():
            """Trigger Discord alert for session state changes."""
            try:
                # Verify authentication
                auth_header = request.headers.get('Authorization')
                if not auth_header or not auth_header.startswith('Bearer '):
                    return jsonify({'error': 'Missing authentication'}), 401
                
                data = request.get_json()
                alert_type = data.get('type')
                message = data.get('message')
                session_id = data.get('session_id')
                
                if not alert_type or not message:
                    return jsonify({'error': 'Missing alert type or message'}), 400
                
                # Send Discord alert
                success = self._send_discord_alert(alert_type, message, session_id)
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': 'Discord alert sent'
                    })
                else:
                    return jsonify({'error': 'Failed to send Discord alert'}), 500
            
            except Exception as e:
                return jsonify({'error': f'Error sending alert: {str(e)}'}), 500
    
    def _get_session_status(self, session_id: str) -> SessionStatus:
        """Get current status of a session."""
        session_manager = self.active_sessions.get(session_id)
        if not session_manager:
            return SessionStatus(
                session_id=session_id,
                status='not_found',
                mode='unknown',
                start_time='',
                uptime_seconds=0,
                current_task='Session not found',
                stuck_detected=False
            )
        
        # Calculate uptime
        uptime = (datetime.now() - session_manager.start_time).total_seconds()
        
        # Check stuck status
        stuck_detected = session_manager.check_afk_status()
        stuck_duration = None
        if stuck_detected and session_manager.stuck_start_time:
            stuck_duration = (datetime.now() - session_manager.stuck_start_time).total_seconds()
        
        # Get current task from last action
        current_task = 'Idle'
        if session_manager.actions_log:
            current_task = session_manager.actions_log[-1].get('action', 'Idle')
        
        return SessionStatus(
            session_id=session_id,
            status='running' if session_manager.end_time is None else 'stopped',
            mode=session_manager.mode,
            start_time=session_manager.start_time.isoformat(),
            uptime_seconds=int(uptime),
            current_task=current_task,
            stuck_detected=stuck_detected,
            stuck_duration=int(stuck_duration) if stuck_duration else None,
            last_activity=session_manager.last_activity_time.isoformat(),
            performance_metrics=session_manager.performance_metrics,
            error_message=None
        )
    
    def _get_user_permissions(self, user_id: str) -> Dict[str, Any]:
        """Get user permissions for bot control."""
        # This could be expanded based on user roles, etc.
        return {
            'can_start_sessions': True,
            'can_control_sessions': True,
            'can_view_logs': True,
            'can_trigger_alerts': True
        }
    
    def _send_discord_alert(self, alert_type: str, message: str, session_id: Optional[str] = None) -> bool:
        """Send Discord alert for session state changes."""
        try:
            # Import Discord functionality
            from modules.discord_alerts import DiscordAlertManager
            
            alert_manager = DiscordAlertManager()
            
            # Format message
            formatted_message = f"[BOT CONTROL] {alert_type.upper()}: {message}"
            if session_id:
                formatted_message += f" (Session: {session_id})"
            
            # Send alert
            return alert_manager.send_alert(formatted_message)
        
        except Exception as e:
            print(f"Error sending Discord alert: {e}")
            return False
    
    def _start_background_monitoring(self):
        """Start background thread for session monitoring."""
        def monitor_sessions():
            while True:
                try:
                    # Update session status cache
                    for session_id in list(self.active_sessions.keys()):
                        status = self._get_session_status(session_id)
                        self.session_status_cache[session_id] = status
                    
                    # Clean up stopped sessions
                    stopped_sessions = [
                        session_id for session_id, status in self.session_status_cache.items()
                        if status.status == 'stopped'
                    ]
                    for session_id in stopped_sessions:
                        if session_id in self.active_sessions:
                            del self.active_sessions[session_id]
                        if session_id in self.session_status_cache:
                            del self.session_status_cache[session_id]
                    
                    time.sleep(5)  # Check every 5 seconds
                
                except Exception as e:
                    print(f"Error in session monitoring: {e}")
                    time.sleep(10)
        
        monitor_thread = threading.Thread(target=monitor_sessions, daemon=True)
        monitor_thread.start()
    
    def run(self, host: str = '0.0.0.0', port: int = 5001, debug: bool = False):
        """Run the session bridge API server."""
        print(f"Starting Session Bridge API on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


def main():
    """Main entry point for the session bridge API."""
    api = SessionBridgeAPI()
    api.run()


if __name__ == '__main__':
    main() 