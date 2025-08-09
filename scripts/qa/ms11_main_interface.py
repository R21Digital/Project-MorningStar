# Simple diagnostics runner and 24h backup scheduler
diagnostics_history: list[dict] = []

def run_diagnostics() -> dict:
    """Collect system diagnostics and append to history."""
    result = {
        "timestamp": datetime.now().isoformat(),
        "platform": platform.platform(),
        "python": sys.version.split()[0],
        "modules_active": len([m for m in ms11_modules.values() if m["status"] == "active"]),
        "metrics": ms11_state.get("performance_metrics", {}),
    }
    diagnostics_history.append(result)
    # keep only last 50
    if len(diagnostics_history) > 50:
        del diagnostics_history[:-50]
    return result


def scheduled_backups_loop():
    """Run a configuration backup every 24 hours."""
    while True:
        try:
            # Only back up if config directory exists
            from pathlib import Path
            cfg_dir = Path('config')
            backups_dir = cfg_dir / 'backups'
            backups_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            # Create a tar-like folder copy (simple approach to avoid extra deps)
            dest = backups_dir / f"daily_backup_{timestamp}"
            dest.mkdir(parents=True, exist_ok=True)
            for p in cfg_dir.glob('*.json'):
                try:
                    import shutil
                    shutil.copy2(p, dest / p.name)
                except Exception:
                    continue
        except Exception as e:
            logger.error(f"Scheduled backup failed: {e}")
        # Sleep 24h
        time.sleep(24 * 60 * 60)
#!/usr/bin/env python3
"""
MS11 Main Visual Interface
Comprehensive web-based interface for the entire MS11 system.
Provides a unified dashboard for all MS11 functionality.
"""
import os
import sys
import json
import logging
import threading
import webbrowser
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import time

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_socketio import SocketIO, emit
import yaml
import platform
from module_registry import get_all_overviews, get_overview

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

# Import existing MS11 components
try:
    from configuration_automation import ConfigurationAutomation
    from validate_configurations import ConfigurationValidator
    from deploy_configurations import ConfigurationDeployer
except ImportError:
    # Fallback if modules aren't available
    ConfigurationAutomation = None
    ConfigurationValidator = None
    ConfigurationDeployer = None
# Capability probe
try:
    from capability_probe import get_probe
    PROBE_AVAILABLE = True
except Exception:
    get_probe = None  # type: ignore
    PROBE_AVAILABLE = False

# Mount detection utilities (OCR-aware wrappers have graceful fallbacks)
try:
    from movement.mount_manager import (
        get_mount_manager,
        get_mount_status as mm_get_mount_status,
        detect_mounts as mm_detect_mounts,
        auto_mount_for_travel as mm_auto_mount_for_travel,
    )
    MOUNTS_AVAILABLE = True
except Exception:
    get_mount_manager = None
    mm_get_mount_status = None
    mm_detect_mounts = None
    mm_auto_mount_for_travel = None
    MOUNTS_AVAILABLE = False

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(
    __name__,
    template_folder=str(Path(__file__).parent / "templates"),
)
app.config['SECRET_KEY'] = 'ms11-main-interface-secret-key-2024'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour session
# Ensure template changes reflect without full server restart and reduce caching
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global state
ms11_state = {
    "status": "initializing",
    "version": "1.0.0",
    "last_update": datetime.now().isoformat(),
    "started_at": datetime.now().isoformat(),
    "active_modules": [],
    "system_health": "healthy",
    "performance_metrics": {},
    "active_sessions": 0,
    "total_operations": 0
}

# Initialize MS11 components
if ConfigurationAutomation:
    config_automation = ConfigurationAutomation()
    validator = ConfigurationValidator()
    deployer = ConfigurationDeployer()
else:
    config_automation = None
    validator = None
    deployer = None

# Initialize mount manager lazily
mount_manager = get_mount_manager() if MOUNTS_AVAILABLE else None
probe = get_probe() if PROBE_AVAILABLE else None
connected_clients = set()

# MS11 Module Registry
ms11_modules = {
    "configuration": {
        "name": "Configuration Management",
        "description": "Manage MS11 configuration files and settings",
        "icon": "fas fa-cogs",
        "status": "active" if config_automation else "inactive",
        "route": "/configuration",
        "permissions": ["admin", "config_manager"]
    },
    "combat": {
        "name": "Combat System",
        "description": "Combat profiles, rotations, and battle management",
        "icon": "fas fa-sword",
        "status": "active",
        "route": "/combat",
        "permissions": ["admin", "combat_manager"]
    },
    "movement": {
        "name": "Movement & Travel",
        "description": "Travel automation, pathfinding, and navigation",
        "icon": "fas fa-route",
        "status": "active",
        "route": "/movement",
        "permissions": ["admin", "travel_manager"]
    },
    "professions": {
        "name": "Profession Management",
        "description": "Crafting, harvesting, and profession automation",
        "icon": "fas fa-hammer",
        "status": "active",
        "route": "/professions",
        "permissions": ["admin", "profession_manager"]
    },
    "quests": {
        "name": "Quest System",
        "description": "Quest tracking, automation, and management",
        "icon": "fas fa-scroll",
        "status": "active",
        "route": "/quests",
        "permissions": ["admin", "quest_manager"]
    },
    "analytics": {
        "name": "Analytics & Reports",
        "description": "Performance metrics, statistics, and reporting",
        "icon": "fas fa-chart-line",
        "status": "active",
        "route": "/analytics",
        "permissions": ["admin", "analyst"]
    },
    "discord": {
        "name": "Discord Integration",
        "description": "Discord bot management and relay settings",
        "icon": "fab fa-discord",
        "status": "active",
        "route": "/discord",
        "permissions": ["admin", "discord_manager"]
    },
    "system": {
        "name": "System Monitor",
        "description": "System health, performance, and diagnostics",
        "icon": "fas fa-server",
        "status": "active",
        "route": "/system",
        "permissions": ["admin", "system_admin"]
    }
}

# Routes
@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('main_dashboard.html', 
                         modules=ms11_modules, 
                         state=ms11_state)

@app.route('/configuration')
def configuration():
    """Configuration management page."""
    from pathlib import Path
    try:
        configs: list[str] = []
        templates: list[str] = []
        # Scan config files
        config_dir = Path('config')
        if config_dir.exists():
            configs = [str(p.name) for p in sorted(config_dir.glob('*.json'))]
            configs += [str(p.name) for p in sorted(config_dir.glob('*.yml'))]
            configs += [str(p.name) for p in sorted(config_dir.glob('*.yaml'))]
        # Scan template files
        templates_dir = config_dir / 'templates'
        if templates_dir.exists():
            templates = [str(p.name) for p in sorted(templates_dir.glob('*.yml'))]
            templates += [str(p.name) for p in sorted(templates_dir.glob('*.yaml'))]
        return render_template('configuration.html', configs=configs, templates=templates)
    except Exception as e:
        logger.error(f"Error loading configuration page: {e}")
        flash("Error loading configurations", "error")
        return render_template('configuration.html', configs=[], templates=[])

@app.route('/combat')
def combat():
    """Combat system page."""
    return render_template('combat.html')

@app.route('/movement')
def movement():
    """Movement and travel page."""
    return render_template('movement.html')

@app.route('/professions')
def professions():
    """Profession management page."""
    return render_template('professions.html')

@app.route('/quests')
def quests():
    """Quest system page."""
    return render_template('quests.html')

@app.route('/analytics')
def analytics():
    """Analytics and reports page."""
    return render_template('analytics.html')

@app.route('/discord')
def discord():
    """Discord integration page."""
    return render_template('discord.html')

@app.route('/system')
def system():
    """System monitor page."""
    return render_template('system.html')

@app.route('/details')
def details():
    """Unified details page with navigation and live data."""
    return render_template('details.html')

# Disable caching of HTML to avoid stale UI after edits
@app.after_request
def add_no_cache_headers(response):
    try:
        if response.mimetype == 'text/html':
            response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
    except Exception:
        pass
    return response

# --- Mounts API ---
@app.route('/api/mounts', methods=['GET'])
def api_mounts_status():
    if not MOUNTS_AVAILABLE:
        return jsonify({"success": False, "error": "Mount system unavailable"}), 400
    status = mm_get_mount_status()
    # Provide a convenience best mount suggestion
    try:
        best = mount_manager.get_best_mount()
    except Exception:
        best = None
    return jsonify({"success": True, "data": {"status": status, "suggested_best": best}})


@app.route('/api/mounts/detect', methods=['POST'])
def api_mounts_detect():
    if not MOUNTS_AVAILABLE:
        return jsonify({"success": False, "error": "Mount system unavailable"}), 400
    detected = mm_detect_mounts()
    emit_payload = {"mounts_found": detected}
    try:
        socketio.emit('mounts_update', emit_payload)
    except Exception:
        pass
    return jsonify({"success": True, "data": emit_payload})


@app.route('/api/mounts/auto', methods=['POST'])
def api_mounts_auto():
    if not MOUNTS_AVAILABLE:
        return jsonify({"success": False, "error": "Mount system unavailable"}), 400
    payload = request.get_json(silent=True) or {}
    distance = float(payload.get('distance', 150))
    zone = payload.get('zone')
    ok = mm_auto_mount_for_travel(distance, zone)
    return jsonify({"success": ok})


# --- Capabilities API ---
@app.route('/api/capabilities', methods=['GET'])
def api_capabilities():
    if not PROBE_AVAILABLE:
        return jsonify({"success": False, "error": "Probe unavailable"}), 400
    return jsonify({"success": True, "data": probe.to_dict()})


@app.route('/api/capabilities/refresh', methods=['POST'])
def api_capabilities_refresh():
    if not PROBE_AVAILABLE:
        return jsonify({"success": False, "error": "Probe unavailable"}), 400
    payload = request.get_json(silent=True) or {}
    background = bool(payload.get('background', True))
    probe.refresh_all(background=background)
    return jsonify({"success": True})


@app.route('/api/capabilities/preflight', methods=['POST'])
def api_capabilities_preflight():
    if not PROBE_AVAILABLE:
        return jsonify({"success": False, "error": "Probe unavailable"}), 400
    payload = request.get_json(silent=True) or {}
    required = payload.get('required', ["mounts"])
    verify = bool(payload.get('verify', True))
    result = probe.ensure_preflight(required=required, verify=verify)
    return jsonify({"success": True, "data": result})

# API Endpoints
@app.route('/api/status')
def api_status():
    """Get current MS11 system status."""
    return jsonify(ms11_state)

@app.route('/api/modules')
def api_modules():
    """Get available MS11 modules."""
    return jsonify(ms11_modules)

@app.route('/api/modules/overview')
def api_modules_overview():
    try:
        return jsonify({"modules": get_all_overviews()})
    except Exception as e:
        logger.error(f"overview error: {e}")
        return jsonify({"modules": []})

@app.route('/api/modules/<module_id>')
def api_module_detail(module_id: str):
    data = get_overview(module_id)
    if not data:
        return jsonify({"error": "not_found"}), 404
    return jsonify(data)

@app.route('/api/health')
def api_health():
    """Get system health information."""
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=None)
        mem = psutil.virtual_memory().used / (1024 * 1024)
    except Exception:
        cpu = None
        mem = None

    try:
        started = datetime.fromisoformat(ms11_state.get("started_at"))
        delta = datetime.now() - started
        uptime = str(delta).split('.')[0]
    except Exception:
        uptime = "unknown"

    health_info = {
        "timestamp": datetime.now().isoformat(),
        "status": ms11_state["system_health"],
        "active_modules": len([m for m in ms11_modules.values() if m["status"] == "active"]),
        "total_modules": len(ms11_modules),
        "uptime": uptime,
        "memory_usage": f"{mem:.1f} MB" if mem is not None else "unknown",
        "cpu_usage": f"{cpu:.0f}%" if cpu is not None else "unknown"
    }
    return jsonify(health_info)

@app.route('/api/performance')
def api_performance():
    """Get performance metrics."""
    return jsonify(ms11_state["performance_metrics"])

# SocketIO Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info(f"Client connected: {request.sid}")
    connected_clients.add(request.sid)
    ms11_state["active_sessions"] = len(connected_clients)
    emit('status_update', ms11_state)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info(f"Client disconnected: {request.sid}")
    connected_clients.discard(request.sid)
    ms11_state["active_sessions"] = len(connected_clients)

@socketio.on('get_status')
def handle_get_status():
    """Handle status request."""
    emit('status_update', ms11_state)

@socketio.on('module_action')
def handle_module_action(data):
    """Handle module action requests."""
    module = data.get('module')
    action = data.get('action')
    
    logger.info(f"Module action: {module} - {action}")
    if action == 'diagnostics':
        result = run_diagnostics()
        socketio.emit('diagnostics_result', result)
        emit('action_response', {"success": True, "message": "Diagnostics completed", "timestamp": datetime.now().isoformat()})
    else:
        emit('action_response', {"success": True, "message": f"Action {action} executed for module {module}", "timestamp": datetime.now().isoformat()})

# Background tasks
def update_system_status():
    """Background task to update system status."""
    while True:
        try:
            # Update system health
            ms11_state["last_update"] = datetime.now().isoformat()
            
            # Basic system monitoring
            try:
                import psutil
                cpu = psutil.cpu_percent(interval=None)
                vm = psutil.virtual_memory()
                mem_used = vm.used / (1024 * 1024)
                ms11_state["performance_metrics"] = {
                    "cpu_usage": cpu,
                    "memory_mb": round(mem_used, 1),
                    "platform": platform.platform(),
                }
            except Exception:
                pass

            ms11_state["system_health"] = "healthy"
            ms11_state["active_sessions"] = len(connected_clients)
            ms11_state["total_operations"] += 1
            
            # Emit status update to all connected clients
            socketio.emit('status_update', ms11_state)
            
            time.sleep(5)  # Update every 5 seconds
            
        except Exception as e:
            logger.error(f"Error updating system status: {e}")
            time.sleep(10)  # Wait longer on error

def main():
    """Main entry point."""
    try:
        # Start background status update thread
        status_thread = threading.Thread(target=update_system_status, daemon=True)
        status_thread.start()
        
        # Update initial state
        ms11_state["status"] = "running"
        ms11_state["active_modules"] = [name for name, module in ms11_modules.items() 
                                       if module["status"] == "active"]
        
        logger.info("MS11 Main Interface starting...")
        logger.info(f"Active modules: {ms11_state['active_modules']}")
        
        # Open browser automatically
        def open_browser():
            time.sleep(1.5)
            webbrowser.open('http://localhost:5000')
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        # Start Flask app
        socketio.run(app, host='0.0.0.0', port=5000, debug=False)
        
    except KeyboardInterrupt:
        logger.info("MS11 Main Interface stopped by user")
    except Exception as e:
        logger.error(f"Error starting MS11 Main Interface: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
