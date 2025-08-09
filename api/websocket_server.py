"""
MS11 WebSocket Server for Real-time Dashboard Communication
Provides real-time updates for sessions, performance metrics, and command execution
"""

import asyncio
import json
import logging
import threading
import time
import weakref
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from flask import Flask
from flask_socketio import SocketIO, emit, join_room, leave_room, disconnect
from flask_cors import CORS
import uuid

from core.session_tracker import SessionTracker
from core.metrics_collector import MS11MetricsCollector
from core.enhanced_error_handling import handle_exceptions
from core.structured_logging import StructuredLogger

# Initialize structured logging
logger = StructuredLogger("websocket_server")

@dataclass
class WebSocketEvent:
    """Represents a WebSocket event to be broadcasted"""
    event_type: str
    data: Dict[str, Any]
    room: Optional[str] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

class WebSocketManager:
    """Manages WebSocket connections and real-time event broadcasting"""
    
    def __init__(self, socketio: SocketIO):
        self.socketio = socketio
        self.connected_clients: Dict[str, Dict[str, Any]] = {}
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.session_tracker: Optional[SessionTracker] = None
        self.metrics_collector: Optional[MS11MetricsCollector] = None
        self.broadcasting = False
        self._weak_callbacks: Dict[str, List[weakref.ref]] = {}
        
    def set_dependencies(self, session_tracker: SessionTracker, metrics_collector: MS11MetricsCollector):
        """Set dependencies for session tracking and metrics collection"""
        self.session_tracker = session_tracker
        self.metrics_collector = metrics_collector
        
        # Register callbacks using weak references
        if hasattr(session_tracker, 'add_callback'):
            callback_ref = weakref.ref(self._on_session_update)
            session_tracker.add_callback('session_update', callback_ref)
            
        if hasattr(metrics_collector, 'add_callback'):
            callback_ref = weakref.ref(self._on_metrics_update)
            metrics_collector.add_callback('metrics_update', callback_ref)
    
    def start_broadcasting(self):
        """Start the background event broadcasting"""
        if not self.broadcasting:
            self.broadcasting = True
            threading.Thread(target=self._broadcast_worker, daemon=True).start()
            logger.info("WebSocket broadcasting started")
    
    def stop_broadcasting(self):
        """Stop the background event broadcasting"""
        self.broadcasting = False
        logger.info("WebSocket broadcasting stopped")
    
    def _broadcast_worker(self):
        """Background worker to process and broadcast events"""
        while self.broadcasting:
            try:
                # Process queued events
                while not self.event_queue.empty():
                    try:
                        event = self.event_queue.get_nowait()
                        self._broadcast_event(event)
                    except asyncio.QueueEmpty:
                        break
                    except Exception as e:
                        logger.error("Failed to process event", error=str(e))
                
                # Send periodic heartbeat
                self._send_heartbeat()
                time.sleep(1)  # 1-second interval
                
            except Exception as e:
                logger.error("Error in broadcast worker", error=str(e))
                time.sleep(5)  # Wait before retrying
    
    def _broadcast_event(self, event: WebSocketEvent):
        """Broadcast an event to connected clients"""
        try:
            payload = {
                'type': event.event_type,
                'data': event.data,
                'timestamp': event.timestamp
            }
            
            if event.room:
                self.socketio.emit(event.event_type, payload, room=event.room)
            else:
                self.socketio.emit(event.event_type, payload)
                
            logger.debug("Broadcasted event", event_type=event.event_type, room=event.room)
            
        except Exception as e:
            logger.error("Failed to broadcast event", 
                        event_type=event.event_type, error=str(e))
    
    def _send_heartbeat(self):
        """Send periodic heartbeat to maintain connections"""
        if self.connected_clients:
            heartbeat_data = {
                'server_time': datetime.now().isoformat(),
                'connected_clients': len(self.connected_clients),
                'uptime': time.time() - getattr(self, 'start_time', time.time())
            }
            
            self.queue_event(WebSocketEvent(
                event_type='heartbeat',
                data=heartbeat_data
            ))
    
    def queue_event(self, event: WebSocketEvent):
        """Queue an event for broadcasting"""
        try:
            self.event_queue.put_nowait(event)
        except asyncio.QueueFull:
            logger.warning("Event queue full, dropping event", event_type=event.event_type)
    
    def add_client(self, session_id: str, client_info: Dict[str, Any]):
        """Add a connected client"""
        self.connected_clients[session_id] = {
            **client_info,
            'connected_at': time.time(),
            'last_seen': time.time()
        }
        
        logger.info("Client connected", session_id=session_id, 
                   total_clients=len(self.connected_clients))
    
    def remove_client(self, session_id: str):
        """Remove a disconnected client"""
        if session_id in self.connected_clients:
            client_info = self.connected_clients.pop(session_id)
            duration = time.time() - client_info['connected_at']
            
            logger.info("Client disconnected", session_id=session_id,
                       duration_seconds=round(duration, 2),
                       remaining_clients=len(self.connected_clients))
    
    def update_client_activity(self, session_id: str):
        """Update client last seen timestamp"""
        if session_id in self.connected_clients:
            self.connected_clients[session_id]['last_seen'] = time.time()
    
    def _on_session_update(self, session_data: Dict[str, Any]):
        """Handle session updates from SessionTracker"""
        self.queue_event(WebSocketEvent(
            event_type='session_update',
            data=session_data
        ))
    
    def _on_metrics_update(self, metrics_data: Dict[str, Any]):
        """Handle metrics updates from MetricsCollector"""
        self.queue_event(WebSocketEvent(
            event_type='performance_metric',
            data=metrics_data
        ))
    
    def broadcast_command_result(self, command: Dict[str, Any], result: Dict[str, Any]):
        """Broadcast command execution result"""
        self.queue_event(WebSocketEvent(
            event_type='command_result',
            data={
                'command': command,
                'result': result,
                'execution_time': result.get('execution_time', 0)
            }
        ))
    
    def broadcast_system_alert(self, level: str, message: str, details: Optional[Dict] = None):
        """Broadcast system alert"""
        self.queue_event(WebSocketEvent(
            event_type='system_alert',
            data={
                'level': level,
                'message': message,
                'details': details or {},
                'timestamp': datetime.now().isoformat()
            }
        ))

# Global WebSocket manager instance
ws_manager: Optional[WebSocketManager] = None

def create_websocket_app(session_tracker: SessionTracker, metrics_collector: MS11MetricsCollector) -> tuple[Flask, SocketIO]:
    """Create Flask app with SocketIO integration"""
    global ws_manager
    
    # Create Flask app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'ms11-websocket-secret-key'  # Should be from config
    
    # Enable CORS for development
    CORS(app, origins=["http://localhost:3000", "http://localhost:3001"])
    
    # Create SocketIO instance
    socketio = SocketIO(
        app,
        cors_allowed_origins=["http://localhost:3000", "http://localhost:3001"],
        ping_timeout=60,
        ping_interval=25,
        transport=['websocket', 'polling']
    )
    
    # Initialize WebSocket manager
    ws_manager = WebSocketManager(socketio)
    ws_manager.set_dependencies(session_tracker, metrics_collector)
    ws_manager.start_time = time.time()
    
    @socketio.on('connect')
    @handle_exceptions(logger)
    def handle_connect():
        """Handle client connection"""
        session_id = uuid.uuid4().hex
        client_info = {
            'user_agent': '',  # Could extract from headers
            'ip_address': '',  # Could extract from request
        }
        
        ws_manager.add_client(session_id, client_info)
        
        # Send initial data
        emit('connection_established', {
            'session_id': session_id,
            'server_time': datetime.now().isoformat(),
            'status': 'connected'
        })
        
        # Send current system status
        if ws_manager.session_tracker:
            current_sessions = ws_manager.session_tracker.get_all_sessions()
            emit('initial_sessions', current_sessions)
        
        if ws_manager.metrics_collector:
            recent_metrics = ws_manager.metrics_collector.get_recent_metrics(50)
            emit('initial_metrics', recent_metrics)
    
    @socketio.on('disconnect')
    @handle_exceptions(logger)
    def handle_disconnect():
        """Handle client disconnection"""
        # Note: In a real implementation, you'd need to track session_id
        # This is simplified for demonstration
        pass
    
    @socketio.on('ping')
    @handle_exceptions(logger)
    def handle_ping(timestamp):
        """Handle ping for connection monitoring"""
        emit('pong', timestamp)
    
    @socketio.on('ms11_command')
    @handle_exceptions(logger)
    def handle_ms11_command(command_data):
        """Handle MS11 command execution requests"""
        try:
            command_id = str(uuid.uuid4())
            
            logger.info("Received command", command_id=command_id, 
                       command_type=command_data.get('type'))
            
            # Process command based on type
            result = process_ms11_command(command_data)
            
            # Broadcast result
            ws_manager.broadcast_command_result(command_data, {
                'command_id': command_id,
                'status': 'success' if result.get('success') else 'error',
                'data': result,
                'execution_time': result.get('execution_time', 0)
            })
            
        except Exception as e:
            logger.error("Failed to process command", error=str(e))
            emit('command_error', {
                'error': str(e),
                'command': command_data
            })
    
    @socketio.on('subscribe_room')
    @handle_exceptions(logger)
    def handle_subscribe_room(room_data):
        """Handle room subscription for targeted updates"""
        room_name = room_data.get('room')
        if room_name:
            join_room(room_name)
            emit('room_joined', {'room': room_name})
            logger.debug("Client joined room", room=room_name)
    
    @socketio.on('unsubscribe_room')
    @handle_exceptions(logger)  
    def handle_unsubscribe_room(room_data):
        """Handle room unsubscription"""
        room_name = room_data.get('room')
        if room_name:
            leave_room(room_name)
            emit('room_left', {'room': room_name})
            logger.debug("Client left room", room=room_name)
    
    return app, socketio

def process_ms11_command(command_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process incoming MS11 commands"""
    start_time = time.time()
    
    try:
        command_type = command_data.get('type', 'unknown')
        
        if command_type == 'quick_action':
            return handle_quick_action(command_data)
        elif command_type == 'manual_command':
            return handle_manual_command(command_data)
        elif command_type == 'session_control':
            return handle_session_control(command_data)
        else:
            return {
                'success': False,
                'error': f'Unknown command type: {command_type}',
                'execution_time': time.time() - start_time
            }
            
    except Exception as e:
        logger.error("Command processing error", error=str(e), command=command_data)
        return {
            'success': False,
            'error': str(e),
            'execution_time': time.time() - start_time
        }

def handle_quick_action(command_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle quick action commands"""
    action = command_data.get('command', '')
    
    # Simulate command execution
    time.sleep(0.1)  # Simulate processing time
    
    actions = {
        'start_session': 'Session started successfully',
        'pause_session': 'Session paused',
        'stop_session': 'Session stopped',
        'reload_config': 'Configuration reloaded',
        'run_diagnostics': 'Diagnostics completed',
        'emergency_stop': 'Emergency stop activated'
    }
    
    if action in actions:
        return {
            'success': True,
            'message': actions[action],
            'action': action,
            'execution_time': 0.1
        }
    else:
        return {
            'success': False,
            'error': f'Unknown quick action: {action}',
            'execution_time': 0.1
        }

def handle_manual_command(command_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle manual command input"""
    command = command_data.get('command', '').strip()
    
    if not command:
        return {
            'success': False,
            'error': 'Empty command',
            'execution_time': 0.0
        }
    
    # Simulate command processing
    time.sleep(0.2)
    
    # Basic command simulation
    if 'start_mode' in command:
        mode_name = command.split()[-1] if len(command.split()) > 1 else 'default'
        return {
            'success': True,
            'message': f'Started mode: {mode_name}',
            'mode': mode_name,
            'execution_time': 0.2
        }
    elif 'check_health' in command:
        return {
            'success': True,
            'message': 'System health: All components operational',
            'health_status': 'healthy',
            'execution_time': 0.2
        }
    elif 'pause_session' in command:
        return {
            'success': True,
            'message': 'Session paused successfully',
            'execution_time': 0.2
        }
    else:
        return {
            'success': True,
            'message': f'Command executed: {command}',
            'command': command,
            'execution_time': 0.2
        }

def handle_session_control(command_data: Dict[str, Any]) -> Dict[str, Any]:
    """Handle session control commands"""
    action = command_data.get('action', '')
    session_id = command_data.get('session_id')
    
    # Simulate session control
    time.sleep(0.05)
    
    return {
        'success': True,
        'message': f'Session {action} completed',
        'session_id': session_id,
        'action': action,
        'execution_time': 0.05
    }

def get_websocket_manager() -> Optional[WebSocketManager]:
    """Get the global WebSocket manager instance"""
    return ws_manager

if __name__ == '__main__':
    # For testing purposes
    from core.session_tracker import SessionTracker
    from core.metrics_collector import MS11MetricsCollector
    
    # Create mock dependencies
    session_tracker = SessionTracker()
    metrics_collector = MS11MetricsCollector()
    
    # Create and run app
    app, socketio = create_websocket_app(session_tracker, metrics_collector)
    ws_manager.start_broadcasting()
    
    logger.info("Starting WebSocket server on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)