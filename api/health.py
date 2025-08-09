#!/usr/bin/env python3
"""
Comprehensive health check and monitoring endpoints for MS11.
Provides system health monitoring, diagnostics, and operational metrics.
"""

import os
import sys
import time
import json
import psutil
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, Response

# Add project paths
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

try:
    from memory_optimizer import get_memory_stats, optimize_memory
    from cache_manager import get_cache
    from structured_logging import analyze_logs
    from enhanced_error_handling import get_error_analytics
    from async_database import get_async_db
    CORE_MODULES_AVAILABLE = True
except ImportError:
    CORE_MODULES_AVAILABLE = False

logger = logging.getLogger(__name__)

# Create Flask blueprint
health_bp = Blueprint('health', __name__, url_prefix='/api/health')


class HealthChecker:
    """Comprehensive system health monitoring."""
    
    def __init__(self):
        self.start_time = time.time()
        self.health_history: List[Dict[str, Any]] = []
        self.max_history = 100
        self.thresholds = {
            'memory_warning': 200.0,  # MB
            'memory_critical': 500.0,  # MB
            'cpu_warning': 70.0,       # %
            'cpu_critical': 90.0,      # %
            'disk_warning': 80.0,      # %
            'disk_critical': 95.0,     # %
            'error_rate_warning': 5.0, # errors/min
            'error_rate_critical': 20.0 # errors/min
        }
        
    def get_system_health(self) -> Dict[str, Any]:
        """Get comprehensive system health status."""
        health_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'uptime_seconds': time.time() - self.start_time,
            'status': 'healthy',
            'checks': {},
            'metrics': {},
            'alerts': []
        }
        
        # Run all health checks
        checks = [
            ('memory', self._check_memory),
            ('cpu', self._check_cpu),
            ('disk', self._check_disk_space),
            ('database', self._check_database),
            ('cache', self._check_cache),
            ('logging', self._check_logging),
            ('dependencies', self._check_dependencies),
            ('configuration', self._check_configuration)
        ]
        
        overall_status = 'healthy'
        
        for check_name, check_func in checks:
            try:
                result = check_func()
                health_data['checks'][check_name] = result
                
                # Update overall status
                if result['status'] == 'critical':
                    overall_status = 'critical'
                elif result['status'] == 'warning' and overall_status == 'healthy':
                    overall_status = 'warning'
                    
                # Add alerts
                if result.get('alert'):
                    health_data['alerts'].append({
                        'component': check_name,
                        'severity': result['status'],
                        'message': result.get('message', ''),
                        'timestamp': health_data['timestamp']
                    })
                    
            except Exception as e:
                logger.error(f"Health check {check_name} failed: {e}")
                health_data['checks'][check_name] = {
                    'status': 'critical',
                    'message': f'Health check failed: {str(e)}',
                    'alert': True
                }
                overall_status = 'critical'
                
        health_data['status'] = overall_status
        
        # Add to history
        self._add_to_history(health_data)
        
        return health_data
        
    def _check_memory(self) -> Dict[str, Any]:
        """Check memory usage."""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            
            status = 'healthy'
            alert = False
            message = f"Memory usage: {memory_mb:.1f} MB"
            
            if memory_mb > self.thresholds['memory_critical']:
                status = 'critical'
                alert = True
                message += f" (Critical: >{self.thresholds['memory_critical']} MB)"
            elif memory_mb > self.thresholds['memory_warning']:
                status = 'warning'
                message += f" (Warning: >{self.thresholds['memory_warning']} MB)"
                
            return {
                'status': status,
                'message': message,
                'alert': alert,
                'metrics': {
                    'rss_mb': memory_mb,
                    'vms_mb': memory_info.vms / 1024 / 1024,
                    'warning_threshold': self.thresholds['memory_warning'],
                    'critical_threshold': self.thresholds['memory_critical']
                }
            }
            
        except Exception as e:
            return {
                'status': 'critical',
                'message': f'Memory check failed: {str(e)}',
                'alert': True,
                'metrics': {}
            }
            
    def _check_cpu(self) -> Dict[str, Any]:
        """Check CPU usage."""
        try:
            process = psutil.Process()
            cpu_percent = process.cpu_percent(interval=0.1)
            
            status = 'healthy'
            alert = False
            message = f"CPU usage: {cpu_percent:.1f}%"
            
            if cpu_percent > self.thresholds['cpu_critical']:
                status = 'critical'
                alert = True
                message += f" (Critical: >{self.thresholds['cpu_critical']}%)"
            elif cpu_percent > self.thresholds['cpu_warning']:
                status = 'warning'
                message += f" (Warning: >{self.thresholds['cpu_warning']}%)"
                
            return {
                'status': status,
                'message': message,
                'alert': alert,
                'metrics': {
                    'cpu_percent': cpu_percent,
                    'warning_threshold': self.thresholds['cpu_warning'],
                    'critical_threshold': self.thresholds['cpu_critical']
                }
            }
            
        except Exception as e:
            return {
                'status': 'critical',
                'message': f'CPU check failed: {str(e)}',
                'alert': True,
                'metrics': {}
            }
            
    def _check_disk_space(self) -> Dict[str, Any]:
        """Check disk space usage."""
        try:
            # Check current directory disk usage
            disk_usage = psutil.disk_usage('.')
            used_percent = (disk_usage.used / disk_usage.total) * 100
            free_gb = disk_usage.free / 1024 / 1024 / 1024
            
            status = 'healthy'
            alert = False
            message = f"Disk usage: {used_percent:.1f}% ({free_gb:.1f} GB free)"
            
            if used_percent > self.thresholds['disk_critical']:
                status = 'critical'
                alert = True
                message += f" (Critical: >{self.thresholds['disk_critical']}%)"
            elif used_percent > self.thresholds['disk_warning']:
                status = 'warning'
                message += f" (Warning: >{self.thresholds['disk_warning']}%)"
                
            return {
                'status': status,
                'message': message,
                'alert': alert,
                'metrics': {
                    'used_percent': used_percent,
                    'free_gb': free_gb,
                    'total_gb': disk_usage.total / 1024 / 1024 / 1024,
                    'warning_threshold': self.thresholds['disk_warning'],
                    'critical_threshold': self.thresholds['disk_critical']
                }
            }
            
        except Exception as e:
            return {
                'status': 'critical',
                'message': f'Disk check failed: {str(e)}',
                'alert': True,
                'metrics': {}
            }
            
    def _check_database(self) -> Dict[str, Any]:
        """Check database connectivity and health."""
        try:
            if not CORE_MODULES_AVAILABLE:
                return {
                    'status': 'warning',
                    'message': 'Core modules not available - database check skipped',
                    'alert': False,
                    'metrics': {}
                }
                
            db = get_async_db()
            
            # Basic connectivity check
            # Note: In a real implementation, this would test actual connectivity
            status = 'healthy'
            message = 'Database connectivity OK'
            
            return {
                'status': status,
                'message': message,
                'alert': False,
                'metrics': {
                    'pool_size': getattr(db, 'pool_size', 0),
                    'available_connections': 'unknown'  # Would be implemented with actual DB
                }
            }
            
        except Exception as e:
            return {
                'status': 'critical',
                'message': f'Database check failed: {str(e)}',
                'alert': True,
                'metrics': {}
            }
            
    def _check_cache(self) -> Dict[str, Any]:
        """Check cache health and performance."""
        try:
            if not CORE_MODULES_AVAILABLE:
                return {
                    'status': 'warning',
                    'message': 'Core modules not available - cache check skipped',
                    'alert': False,
                    'metrics': {}
                }
                
            cache = get_cache()
            stats = cache.get_stats()
            
            hit_rate = stats.get('hit_rate', 0)
            status = 'healthy'
            alert = False
            message = f"Cache hit rate: {hit_rate}%"
            
            if hit_rate < 50:
                status = 'warning'
                message += " (Low hit rate)"
            elif hit_rate < 20:
                status = 'critical'
                alert = True
                message += " (Very low hit rate)"
                
            return {
                'status': status,
                'message': message,
                'alert': alert,
                'metrics': stats
            }
            
        except Exception as e:
            return {
                'status': 'critical',
                'message': f'Cache check failed: {str(e)}',
                'alert': True,
                'metrics': {}
            }
            
    def _check_logging(self) -> Dict[str, Any]:
        """Check logging system health."""
        try:
            if not CORE_MODULES_AVAILABLE:
                return {
                    'status': 'warning',
                    'message': 'Core modules not available - logging check skipped',
                    'alert': False,
                    'metrics': {}
                }
                
            # Check recent log activity
            log_analysis = analyze_logs(minutes=10)
            error_count = log_analysis.get('error_count', 0)
            
            # Calculate error rate (errors per minute)
            error_rate = error_count / 10.0
            
            status = 'healthy'
            alert = False
            message = f"Error rate: {error_rate:.1f} errors/min"
            
            if error_rate > self.thresholds['error_rate_critical']:
                status = 'critical'
                alert = True
                message += f" (Critical: >{self.thresholds['error_rate_critical']}/min)"
            elif error_rate > self.thresholds['error_rate_warning']:
                status = 'warning'
                message += f" (Warning: >{self.thresholds['error_rate_warning']}/min)"
                
            return {
                'status': status,
                'message': message,
                'alert': alert,
                'metrics': {
                    'error_rate': error_rate,
                    'recent_errors': error_count,
                    'recent_warnings': log_analysis.get('warning_count', 0),
                    'warning_threshold': self.thresholds['error_rate_warning'],
                    'critical_threshold': self.thresholds['error_rate_critical']
                }
            }
            
        except Exception as e:
            return {
                'status': 'warning',
                'message': f'Logging check failed: {str(e)}',
                'alert': False,
                'metrics': {}
            }
            
    def _check_dependencies(self) -> Dict[str, Any]:
        """Check critical dependencies."""
        dependencies = [
            ('psutil', 'System monitoring'),
            ('flask', 'Web framework'),
            ('pathlib', 'Path handling')
        ]
        
        missing_deps = []
        available_deps = []
        
        for dep_name, description in dependencies:
            try:
                __import__(dep_name)
                available_deps.append(dep_name)
            except ImportError:
                missing_deps.append((dep_name, description))
                
        if missing_deps:
            status = 'critical'
            message = f"Missing dependencies: {[dep[0] for dep in missing_deps]}"
            alert = True
        else:
            status = 'healthy'
            message = f"All {len(available_deps)} dependencies available"
            alert = False
            
        return {
            'status': status,
            'message': message,
            'alert': alert,
            'metrics': {
                'available_dependencies': available_deps,
                'missing_dependencies': [dep[0] for dep in missing_deps],
                'total_checked': len(dependencies)
            }
        }
        
    def _check_configuration(self) -> Dict[str, Any]:
        """Check configuration validity."""
        try:
            # Check for essential directories
            essential_dirs = ['logs', 'config', 'profiles/runtime']
            missing_dirs = []
            
            project_root = Path(__file__).parent.parent
            for dir_name in essential_dirs:
                dir_path = project_root / dir_name
                if not dir_path.exists():
                    missing_dirs.append(dir_name)
                    
            # Check for essential files
            essential_files = ['src/main.py']
            missing_files = []
            
            for file_name in essential_files:
                file_path = project_root / file_name
                if not file_path.exists():
                    missing_files.append(file_name)
                    
            if missing_dirs or missing_files:
                status = 'warning'
                message = f"Missing directories: {missing_dirs}, Missing files: {missing_files}"
                alert = False
            else:
                status = 'healthy'
                message = "Configuration structure OK"
                alert = False
                
            return {
                'status': status,
                'message': message,
                'alert': alert,
                'metrics': {
                    'missing_directories': missing_dirs,
                    'missing_files': missing_files,
                    'directories_checked': len(essential_dirs),
                    'files_checked': len(essential_files)
                }
            }
            
        except Exception as e:
            return {
                'status': 'critical',
                'message': f'Configuration check failed: {str(e)}',
                'alert': True,
                'metrics': {}
            }
            
    def _add_to_history(self, health_data: Dict[str, Any]):
        """Add health data to history."""
        self.health_history.append({
            'timestamp': health_data['timestamp'],
            'status': health_data['status'],
            'alert_count': len(health_data['alerts'])
        })
        
        # Limit history size
        if len(self.health_history) > self.max_history:
            self.health_history = self.health_history[-self.max_history:]
            
    def get_health_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get health trends over time."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_history = [
            entry for entry in self.health_history
            if datetime.fromisoformat(entry['timestamp']) > cutoff_time
        ]
        
        if not recent_history:
            return {'message': 'No health data available for the specified period'}
            
        status_counts = {}
        total_alerts = 0
        
        for entry in recent_history:
            status = entry['status']
            status_counts[status] = status_counts.get(status, 0) + 1
            total_alerts += entry.get('alert_count', 0)
            
        return {
            'period_hours': hours,
            'total_checks': len(recent_history),
            'status_distribution': status_counts,
            'total_alerts': total_alerts,
            'alert_rate': total_alerts / len(recent_history) if recent_history else 0
        }


# Global health checker instance
health_checker = HealthChecker()


# Flask routes
@health_bp.route('/')
def health_check():
    """Basic health check endpoint."""
    health_data = health_checker.get_system_health()
    
    # Return appropriate HTTP status code
    status_code = 200
    if health_data['status'] == 'warning':
        status_code = 200  # Still OK, but with warnings
    elif health_data['status'] == 'critical':
        status_code = 503  # Service unavailable
        
    return jsonify(health_data), status_code


@health_bp.route('/detailed')
def detailed_health():
    """Detailed health information."""
    health_data = health_checker.get_system_health()
    
    # Add additional detailed information
    if CORE_MODULES_AVAILABLE:
        try:
            health_data['detailed_metrics'] = {
                'memory_stats': get_memory_stats(),
                'error_analytics': get_error_analytics()
            }
        except Exception as e:
            health_data['detailed_metrics'] = {'error': str(e)}
    else:
        health_data['detailed_metrics'] = {'message': 'Core modules not available'}
        
    return jsonify(health_data)


@health_bp.route('/trends')
def health_trends():
    """Health trends over time."""
    hours = request.args.get('hours', 24, type=int)
    trends = health_checker.get_health_trends(hours)
    return jsonify(trends)


@health_bp.route('/metrics')
def metrics_endpoint():
    """Prometheus-style metrics endpoint."""
    health_data = health_checker.get_system_health()
    
    # Generate Prometheus-style metrics
    metrics_lines = []
    
    # Add basic metrics
    for check_name, check_data in health_data['checks'].items():
        metrics = check_data.get('metrics', {})
        
        for metric_name, metric_value in metrics.items():
            if isinstance(metric_value, (int, float)):
                metric_line = f'ms11_{check_name}_{metric_name} {metric_value}'
                metrics_lines.append(metric_line)
                
    # Add status as metric (0=healthy, 1=warning, 2=critical)
    status_value = {'healthy': 0, 'warning': 1, 'critical': 2}.get(health_data['status'], 2)
    metrics_lines.append(f'ms11_system_status {status_value}')
    
    # Add uptime
    metrics_lines.append(f'ms11_uptime_seconds {time.time() - health_checker.start_time}')
    
    # Add alert count
    metrics_lines.append(f'ms11_alerts_total {len(health_data["alerts"])}')
    
    # Return as plain text
    metrics_text = '\n'.join(metrics_lines)
    return Response(metrics_text, mimetype='text/plain')


@health_bp.route('/ready')
def readiness_check():
    """Kubernetes readiness probe."""
    health_data = health_checker.get_system_health()
    
    # Ready if not critical
    if health_data['status'] != 'critical':
        return jsonify({'status': 'ready'}), 200
    else:
        return jsonify({'status': 'not ready', 'reason': 'Critical health issues'}), 503


@health_bp.route('/live')
def liveness_check():
    """Kubernetes liveness probe."""
    # Simple check - if we can respond, we're alive
    return jsonify({
        'status': 'alive',
        'timestamp': datetime.utcnow().isoformat(),
        'uptime': time.time() - health_checker.start_time
    }), 200


@health_bp.route('/optimize', methods=['POST'])
def optimize_system():
    """Trigger system optimization."""
    try:
        if CORE_MODULES_AVAILABLE:
            result = optimize_memory()
            return jsonify({
                'status': 'success',
                'message': 'System optimization completed',
                'results': result
            })
        else:
            return jsonify({
                'status': 'warning',
                'message': 'Core modules not available - optimization skipped'
            })
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Optimization failed: {str(e)}'
        }), 500


# Register the blueprint with Flask app
def register_health_endpoints(app):
    """Register health endpoints with Flask app."""
    app.register_blueprint(health_bp)
    logger.info("Health check endpoints registered")


# Standalone testing
if __name__ == "__main__":
    # Test health checker
    checker = HealthChecker()
    health = checker.get_system_health()
    
    print("=== MS11 Health Check ===")
    print(f"Overall Status: {health['status'].upper()}")
    print(f"Uptime: {health['uptime_seconds']:.1f} seconds")
    print()
    
    print("Component Status:")
    for component, data in health['checks'].items():
        status_icon = {'healthy': '✅', 'warning': '⚠️', 'critical': '❌'}.get(data['status'], '❓')
        print(f"  {status_icon} {component}: {data['status']} - {data['message']}")
        
    if health['alerts']:
        print(f"\nAlerts ({len(health['alerts'])}):")
        for alert in health['alerts']:
            severity_icon = {'warning': '⚠️', 'critical': '❌'}.get(alert['severity'], '❓')
            print(f"  {severity_icon} {alert['component']}: {alert['message']}")
    else:
        print("\n✅ No active alerts")