"""
MS11 REST API Endpoints for Dashboard Integration
Provides HTTP API endpoints for health checks, metrics, sessions, and commands
"""

import time
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from flask import Blueprint, request, jsonify, g
from functools import wraps

from core.structured_logging import StructuredLogger
from core.enhanced_error_handling import handle_exceptions
from api.websocket_server import get_websocket_manager

# Initialize logger
logger = StructuredLogger("rest_api")

# Create API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

@dataclass
class ApiResponse:
    """Standard API response format"""
    success: bool
    data: Any = None
    message: str = ""
    error: str = ""
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

def api_response(success: bool = True, data: Any = None, message: str = "", 
                error: str = "", status_code: int = 200) -> tuple:
    """Create standardized API response"""
    response = ApiResponse(
        success=success,
        data=data,
        message=message,
        error=error
    )
    return jsonify(response.to_dict()), status_code

def validate_json(*required_fields):
    """Decorator to validate JSON request body"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not request.is_json:
                return api_response(False, error="Content-Type must be application/json", status_code=400)
            
            data = request.get_json()
            if not data:
                return api_response(False, error="Request body must contain valid JSON", status_code=400)
            
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return api_response(False, error=f"Missing required fields: {missing_fields}", status_code=400)
            
            g.request_data = data
            return f(*args, **kwargs)
        return wrapper
    return decorator

def log_api_call(f):
    """Decorator to log API calls"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        endpoint = request.endpoint
        method = request.method
        
        logger.info("API call started", endpoint=endpoint, method=method,
                   remote_addr=request.remote_addr)
        
        try:
            result = f(*args, **kwargs)
            duration = time.time() - start_time
            logger.info("API call completed", endpoint=endpoint, method=method,
                       duration_ms=round(duration * 1000, 2))
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error("API call failed", endpoint=endpoint, method=method,
                        duration_ms=round(duration * 1000, 2), error=str(e))
            raise
    return wrapper

# Configuration Management Endpoints

@api_bp.route('/config/scan', methods=['GET'])
@log_api_call
@handle_exceptions
def scan_configurations():
    """Scan and return available configuration files"""
    try:
        import os
        from pathlib import Path
        
        config_dir = Path("config")
        template_dir = Path("scripts/qa/templates")
        
        configs = []
        templates = []
        
        # Scan config files
        if config_dir.exists():
            for file_path in config_dir.rglob("*.json"):
                configs.append({
                    "name": file_path.stem,
                    "path": str(file_path),
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    "size": file_path.stat().st_size
                })
        
        # Scan template files  
        if template_dir.exists():
            for file_path in template_dir.rglob("*.html"):
                templates.append({
                    "name": file_path.stem,
                    "path": str(file_path),
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    "size": file_path.stat().st_size
                })
        
        return api_response(True, {
            "configs": configs,
            "templates": templates,
            "scan_time": datetime.now().isoformat()
        }, "Configuration scan completed")
        
    except Exception as e:
        logger.error("Configuration scan failed", error=str(e))
        return api_response(False, error=f"Scan failed: {str(e)}", status_code=500)

@api_bp.route('/config/validate', methods=['POST'])
@log_api_call
@handle_exceptions
def validate_configuration():
    """Validate configuration files"""
    try:
        import json
        from pathlib import Path
        
        validation_results = []
        config_dir = Path("config")
        
        if not config_dir.exists():
            return api_response(False, error="Config directory not found", status_code=404)
        
        # Validate JSON files
        for config_file in config_dir.rglob("*.json"):
            try:
                with open(config_file, 'r') as f:
                    json.load(f)
                validation_results.append({
                    "file": str(config_file),
                    "status": "valid",
                    "message": "JSON syntax is valid"
                })
            except json.JSONDecodeError as e:
                validation_results.append({
                    "file": str(config_file),
                    "status": "error", 
                    "message": f"JSON syntax error: {str(e)}"
                })
            except Exception as e:
                validation_results.append({
                    "file": str(config_file),
                    "status": "error",
                    "message": f"Validation error: {str(e)}"
                })
        
        # Check if all validations passed
        all_valid = all(result["status"] == "valid" for result in validation_results)
        
        return api_response(all_valid, {
            "validation_results": validation_results,
            "total_files": len(validation_results),
            "valid_files": sum(1 for r in validation_results if r["status"] == "valid"),
            "validation_time": datetime.now().isoformat()
        }, "Validation completed" if all_valid else "Validation found errors")
        
    except Exception as e:
        logger.error("Configuration validation failed", error=str(e))
        return api_response(False, error=f"Validation failed: {str(e)}", status_code=500)

@api_bp.route('/config/deploy', methods=['POST']) 
@log_api_call
@handle_exceptions
def deploy_configuration():
    """Deploy configuration changes"""
    try:
        # In a real implementation, this would:
        # 1. Backup current configs
        # 2. Apply new configurations
        # 3. Restart affected services
        # 4. Verify deployment success
        
        logger.info("Configuration deployment requested")
        
        # Simulate deployment process
        deployment_steps = [
            {"step": "backup_configs", "status": "completed", "timestamp": datetime.now().isoformat()},
            {"step": "validate_configs", "status": "completed", "timestamp": datetime.now().isoformat()},
            {"step": "apply_configs", "status": "completed", "timestamp": datetime.now().isoformat()},
            {"step": "restart_services", "status": "completed", "timestamp": datetime.now().isoformat()},
            {"step": "verify_deployment", "status": "completed", "timestamp": datetime.now().isoformat()}
        ]
        
        # Emit deployment progress via WebSocket
        ws_manager = get_websocket_manager()
        if ws_manager:
            for step in deployment_steps:
                ws_manager.emit('deployment_progress', step)
                time.sleep(0.1)  # Small delay for demo
        
        return api_response(True, {
            "deployment_id": str(uuid.uuid4()),
            "steps": deployment_steps,
            "deployment_time": datetime.now().isoformat()
        }, "Configuration deployed successfully")
        
    except Exception as e:
        logger.error("Configuration deployment failed", error=str(e))
        return api_response(False, error=f"Deployment failed: {str(e)}", status_code=500)

# Health Check Endpoints

@api_bp.route('/health', methods=['GET'])
@log_api_call
@handle_exceptions(logger)
def get_health():
    """Get comprehensive system health status"""
    try:
        # Get WebSocket manager for connection info
        ws_manager = get_websocket_manager()
        
        # Simulate health checks for different components
        components = {
            'database': {
                'status': 'healthy',
                'latency': 12.5,
                'last_check': datetime.now().isoformat(),
                'details': {'connection_pool': 'optimal', 'queries_per_second': 45}
            },
            'cache': {
                'status': 'healthy',
                'latency': 2.1,
                'last_check': datetime.now().isoformat(),
                'details': {'hit_rate': 0.89, 'memory_usage': '245MB'}
            },
            'ocr': {
                'status': 'healthy',
                'latency': 156.3,
                'last_check': datetime.now().isoformat(),
                'details': {'tesseract_version': '5.3.0', 'processing_queue': 2}
            },
            'websocket': {
                'status': 'healthy' if ws_manager and len(ws_manager.connected_clients) >= 0 else 'degraded',
                'latency': 8.7,
                'last_check': datetime.now().isoformat(),
                'details': {
                    'connected_clients': len(ws_manager.connected_clients) if ws_manager else 0,
                    'broadcasting': ws_manager.broadcasting if ws_manager else False
                }
            }
        }
        
        # Determine overall status
        all_healthy = all(comp['status'] == 'healthy' for comp in components.values())
        any_degraded = any(comp['status'] == 'degraded' for comp in components.values())
        
        overall_status = 'healthy' if all_healthy else ('degraded' if any_degraded else 'unhealthy')
        
        health_data = {
            'status': overall_status,
            'uptime': time.time() - getattr(get_health, 'start_time', time.time()),
            'timestamp': datetime.now().isoformat(),
            'components': components,
            'metrics': {
                'cpu_usage': 23.4,  # Would get from actual system monitoring
                'memory_usage': 67.8,
                'disk_usage': 45.2,
                'active_sessions': 3,
                'total_commands': 1247,
                'commands_per_minute': 12.3
            }
        }
        
        status_code = 200 if overall_status == 'healthy' else (503 if overall_status == 'unhealthy' else 200)
        return api_response(True, data=health_data, status_code=status_code)
        
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return api_response(False, error="Health check failed", status_code=500)

@api_bp.route('/health/ready', methods=['GET'])
@log_api_call
@handle_exceptions(logger)
def get_readiness():
    """Kubernetes readiness probe endpoint"""
    # Check if all critical components are ready
    ready = True  # Would check actual component readiness
    
    return api_response(
        success=ready,
        data={'ready': ready, 'timestamp': datetime.now().isoformat()},
        status_code=200 if ready else 503
    )

@api_bp.route('/health/live', methods=['GET'])
@log_api_call
@handle_exceptions(logger)
def get_liveness():
    """Kubernetes liveness probe endpoint"""
    return api_response(
        success=True,
        data={'alive': True, 'timestamp': datetime.now().isoformat()}
    )

# Metrics Endpoints

@api_bp.route('/metrics', methods=['GET'])
@log_api_call
@handle_exceptions(logger)
def get_metrics():
    """Get performance metrics for dashboard"""
    try:
        # Get query parameters
        limit = min(int(request.args.get('limit', 50)), 1000)
        metric_type = request.args.get('type', 'all')
        
        # Generate sample metrics data
        now = datetime.now()
        metrics = []
        
        for i in range(limit):
            timestamp = now - timedelta(seconds=i * 30)  # 30-second intervals
            
            metric = {
                'timestamp': timestamp.timestamp() * 1000,  # JavaScript timestamp
                'cpu_usage': 20 + (i % 40) + (i * 0.1 % 20),
                'memory_usage': 512 + (i % 200) - 100,
                'response_time': 50 + (i % 100) + (i * 0.5 % 50),
                'commands_per_second': max(0, 5 + (i % 20) - 10),
                'error_rate': min(10, max(0, (i % 15) - 12)),
                'active_connections': max(1, 8 + (i % 6) - 3)
            }
            
            metrics.append(metric)
        
        # Filter by metric type if specified
        if metric_type != 'all' and metric_type in ['cpu_usage', 'memory_usage', 'response_time', 'commands_per_second', 'error_rate']:
            filtered_metrics = [
                {'timestamp': m['timestamp'], 'value': m[metric_type]}
                for m in metrics
            ]
            return api_response(True, data=filtered_metrics)
        
        return api_response(True, data=list(reversed(metrics)))  # Reverse for chronological order
        
    except Exception as e:
        logger.error("Failed to get metrics", error=str(e))
        return api_response(False, error="Failed to retrieve metrics", status_code=500)

@api_bp.route('/metrics/prometheus', methods=['GET'])
@log_api_call
@handle_exceptions(logger)
def get_prometheus_metrics():
    """Get metrics in Prometheus format"""
    try:
        # Generate Prometheus-format metrics
        metrics_text = """# HELP ms11_cpu_usage_percent CPU usage percentage
# TYPE ms11_cpu_usage_percent gauge
ms11_cpu_usage_percent 23.4

# HELP ms11_memory_usage_bytes Memory usage in bytes
# TYPE ms11_memory_usage_bytes gauge
ms11_memory_usage_bytes 358400000

# HELP ms11_active_sessions_total Number of active MS11 sessions
# TYPE ms11_active_sessions_total gauge
ms11_active_sessions_total 3

# HELP ms11_commands_executed_total Total number of commands executed
# TYPE ms11_commands_executed_total counter
ms11_commands_executed_total 1247

# HELP ms11_command_execution_duration_seconds Command execution duration
# TYPE ms11_command_execution_duration_seconds histogram
ms11_command_execution_duration_seconds_bucket{le="0.1"} 145
ms11_command_execution_duration_seconds_bucket{le="0.5"} 312
ms11_command_execution_duration_seconds_bucket{le="1.0"} 458
ms11_command_execution_duration_seconds_bucket{le="5.0"} 612
ms11_command_execution_duration_seconds_bucket{le="+Inf"} 645
ms11_command_execution_duration_seconds_sum 234.56
ms11_command_execution_duration_seconds_count 645

# HELP ms11_websocket_connections_active Active WebSocket connections
# TYPE ms11_websocket_connections_active gauge
ms11_websocket_connections_active """ + str(len(get_websocket_manager().connected_clients) if get_websocket_manager() else 0) + """

# HELP ms11_errors_total Total number of errors
# TYPE ms11_errors_total counter
ms11_errors_total 23
"""
        
        return metrics_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}
        
    except Exception as e:
        logger.error("Failed to generate Prometheus metrics", error=str(e))
        return "# Failed to generate metrics\n", 500, {'Content-Type': 'text/plain; charset=utf-8'}

# Session Management Endpoints

@api_bp.route('/sessions', methods=['GET'])
@log_api_call
@handle_exceptions(logger)
def get_sessions():
    """Get all active MS11 sessions"""
    try:
        # Generate sample session data
        sessions = [
            {
                'id': str(uuid.uuid4()),
                'character_name': 'TestCharacter1',
                'server': 'Basilisk',
                'status': 'running',
                'created_at': (datetime.now() - timedelta(hours=2)).isoformat(),
                'updated_at': datetime.now().isoformat(),
                'current_mode': 'combat_training',
                'stats': {
                    'total_runtime': 7200,
                    'commands_executed': 156,
                    'success_rate': 94.2,
                    'last_activity': (datetime.now() - timedelta(minutes=2)).isoformat()
                }
            },
            {
                'id': str(uuid.uuid4()),
                'character_name': 'TestCharacter2',
                'server': 'Restoration',
                'status': 'paused',
                'created_at': (datetime.now() - timedelta(hours=1)).isoformat(),
                'updated_at': (datetime.now() - timedelta(minutes=15)).isoformat(),
                'current_mode': 'resource_gathering',
                'stats': {
                    'total_runtime': 3600,
                    'commands_executed': 89,
                    'success_rate': 97.8,
                    'last_activity': (datetime.now() - timedelta(minutes=15)).isoformat()
                }
            }
        ]
        
        return api_response(True, data=sessions)
        
    except Exception as e:
        logger.error("Failed to get sessions", error=str(e))
        return api_response(False, error="Failed to retrieve sessions", status_code=500)

@api_bp.route('/sessions', methods=['POST'])
@log_api_call
@validate_json('character_name', 'server')
@handle_exceptions(logger)
def create_session():
    """Create a new MS11 session"""
    try:
        data = g.request_data
        
        new_session = {
            'id': str(uuid.uuid4()),
            'character_name': data['character_name'],
            'server': data['server'],
            'status': 'idle',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'current_mode': None,
            'stats': {
                'total_runtime': 0,
                'commands_executed': 0,
                'success_rate': 0.0,
                'last_activity': None
            }
        }
        
        # Broadcast session creation
        ws_manager = get_websocket_manager()
        if ws_manager:
            ws_manager.queue_event({
                'event_type': 'session_created',
                'data': new_session
            })
        
        logger.info("Session created", session_id=new_session['id'], 
                   character=data['character_name'])
        
        return api_response(True, data=new_session, message="Session created successfully", status_code=201)
        
    except Exception as e:
        logger.error("Failed to create session", error=str(e))
        return api_response(False, error="Failed to create session", status_code=500)

@api_bp.route('/sessions/<session_id>', methods=['PUT'])
@log_api_call
@validate_json()
@handle_exceptions(logger)
def update_session(session_id: str):
    """Update an existing session"""
    try:
        data = g.request_data
        
        # Simulate session update
        updated_session = {
            'id': session_id,
            'status': data.get('status', 'running'),
            'current_mode': data.get('current_mode'),
            'updated_at': datetime.now().isoformat()
        }
        
        # Broadcast session update
        ws_manager = get_websocket_manager()
        if ws_manager:
            ws_manager.queue_event({
                'event_type': 'session_updated',
                'data': updated_session
            })
        
        logger.info("Session updated", session_id=session_id, status=updated_session['status'])
        
        return api_response(True, data=updated_session, message="Session updated successfully")
        
    except Exception as e:
        logger.error("Failed to update session", session_id=session_id, error=str(e))
        return api_response(False, error="Failed to update session", status_code=500)

@api_bp.route('/sessions/<session_id>', methods=['DELETE'])
@log_api_call
@handle_exceptions(logger)
def delete_session(session_id: str):
    """Delete a session"""
    try:
        # Broadcast session deletion
        ws_manager = get_websocket_manager()
        if ws_manager:
            ws_manager.queue_event({
                'event_type': 'session_deleted',
                'data': {'session_id': session_id}
            })
        
        logger.info("Session deleted", session_id=session_id)
        
        return api_response(True, message="Session deleted successfully")
        
    except Exception as e:
        logger.error("Failed to delete session", session_id=session_id, error=str(e))
        return api_response(False, error="Failed to delete session", status_code=500)

# Command Execution Endpoints

@api_bp.route('/commands', methods=['POST'])
@log_api_call
@validate_json('command', 'type')
@handle_exceptions(logger)
def execute_command():
    """Execute an MS11 command"""
    try:
        data = g.request_data
        command_id = str(uuid.uuid4())
        
        start_time = time.time()
        
        # Simulate command processing
        result = {
            'command_id': command_id,
            'command': data['command'],
            'type': data['type'],
            'status': 'success',
            'result': f"Command '{data['command']}' executed successfully",
            'execution_time': round((time.time() - start_time) * 1000, 2),
            'timestamp': datetime.now().isoformat()
        }
        
        # Broadcast command result
        ws_manager = get_websocket_manager()
        if ws_manager:
            ws_manager.broadcast_command_result(data, result)
        
        logger.info("Command executed", command_id=command_id, 
                   command=data['command'], execution_time=result['execution_time'])
        
        return api_response(True, data=result, message="Command executed successfully")
        
    except Exception as e:
        logger.error("Command execution failed", error=str(e), command=data.get('command', 'unknown'))
        return api_response(False, error="Command execution failed", status_code=500)

@api_bp.route('/commands/history', methods=['GET'])
@log_api_call
@handle_exceptions(logger)
def get_command_history():
    """Get command execution history"""
    try:
        limit = min(int(request.args.get('limit', 100)), 1000)
        
        # Generate sample command history
        history = []
        for i in range(limit):
            timestamp = datetime.now() - timedelta(minutes=i * 5)
            history.append({
                'command_id': str(uuid.uuid4()),
                'command': f'sample_command_{i}',
                'type': 'manual',
                'status': 'success' if i % 8 != 0 else 'error',
                'execution_time': round(50 + (i % 200), 2),
                'timestamp': timestamp.isoformat(),
                'user': 'system'
            })
        
        return api_response(True, data=history)
        
    except Exception as e:
        logger.error("Failed to get command history", error=str(e))
        return api_response(False, error="Failed to retrieve command history", status_code=500)

# Configuration Endpoints

@api_bp.route('/config', methods=['GET'])
@log_api_call
@handle_exceptions(logger)
def get_config():
    """Get current MS11 configuration"""
    try:
        config = {
            'websocket': {
                'enabled': True,
                'port': 5000,
                'ping_interval': 25,
                'ping_timeout': 60
            },
            'dashboard': {
                'refresh_interval': 30,
                'max_metrics_points': 100,
                'theme': 'dark'
            },
            'ms11': {
                'session_timeout': 3600,
                'max_concurrent_sessions': 10,
                'command_timeout': 30,
                'ocr_enabled': True
            },
            'logging': {
                'level': 'INFO',
                'format': 'json',
                'file_rotation': True
            }
        }
        
        return api_response(True, data=config)
        
    except Exception as e:
        logger.error("Failed to get configuration", error=str(e))
        return api_response(False, error="Failed to retrieve configuration", status_code=500)

@api_bp.route('/config', methods=['PUT'])
@log_api_call
@validate_json()
@handle_exceptions(logger)
def update_config():
    """Update MS11 configuration"""
    try:
        data = g.request_data
        
        # Simulate configuration update
        logger.info("Configuration updated", changes=list(data.keys()))
        
        return api_response(True, message="Configuration updated successfully")
        
    except Exception as e:
        logger.error("Failed to update configuration", error=str(e))
        return api_response(False, error="Failed to update configuration", status_code=500)

# Error handler
@api_bp.errorhandler(404)
def not_found(error):
    return api_response(False, error="Endpoint not found", status_code=404)

@api_bp.errorhandler(500)
def internal_error(error):
    return api_response(False, error="Internal server error", status_code=500)

# Initialize start time for health check uptime
get_health.start_time = time.time()

def register_api_routes(app):
    """Register API routes with Flask app"""
    app.register_blueprint(api_bp)
    logger.info("API routes registered")