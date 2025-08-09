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
import uuid
import subprocess

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_socketio import SocketIO, emit
import yaml
import platform
from module_registry import get_all_overviews, get_overview
from plugin_manager import list_plugins, set_enabled
from flask import send_from_directory

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

# --- Lightweight Process Manager & Session Store ---
class ManagedProcess:
    def __init__(self, proc: subprocess.Popen, name: str):
        self.proc = proc
        self.name = name


process_table: Dict[str, ManagedProcess] = {}
sessions_store: Dict[str, Dict[str, Any]] = {}
process_table_lock = threading.Lock()
sessions_lock = threading.Lock()


def _stream_pipe(pipe, source_name: str, level: str):
    for raw in iter(pipe.readline, b""):
        try:
            line = raw.decode(errors='ignore').strip()
        except Exception:
            line = str(raw).strip()
        if not line:
            continue
        socketio.emit('log', {
            'type': 'log',
            'level': level,
            'source': source_name,
            'msg': line,
            'ts': datetime.now().isoformat(),
        })


def start_managed_process(pid: str, name: str, cmd: List[str]) -> None:
    with process_table_lock:
        if pid in process_table:
            return
        env = os.environ.copy()
        env.setdefault('PYTHONIOENCODING', 'utf-8')
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                env=env,
                creationflags=(0x08000000 if os.name == 'nt' else 0),  # CREATE_NO_WINDOW on Windows
            )
        except Exception as e:
            logger.error(f"Failed to start process {name}: {e}")
            return

        mp = ManagedProcess(proc=proc, name=name)
        process_table[pid] = mp

        if proc.stdout is not None:
            threading.Thread(target=_stream_pipe, args=(proc.stdout, name, 'info'), daemon=True).start()
        if proc.stderr is not None:
            threading.Thread(target=_stream_pipe, args=(proc.stderr, name, 'error'), daemon=True).start()

        def _waiter():
            code = proc.wait()
            socketio.emit('log', {
                'type': 'log', 'level': 'info' if code == 0 else 'error',
                'source': name, 'msg': f'{name} exited ({code})', 'ts': datetime.now().isoformat()
            })
            with process_table_lock:
                process_table.pop(pid, None)

        threading.Thread(target=_waiter, daemon=True).start()


def stop_managed_process(pid: str) -> None:
    with process_table_lock:
        mp = process_table.pop(pid, None)
    if not mp:
        return
    try:
        mp.proc.terminate()
        try:
            mp.proc.wait(timeout=3)
        except Exception:
            mp.proc.kill()
    except Exception:
        pass

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

# New pages: addons, profiles, shortcuts, updates
@app.route('/addons')
def addons():
    return render_template('addons.html')

@app.route('/profiles')
def profiles_page():
    return render_template('profiles.html')

@app.route('/shortcuts')
def shortcuts_page():
    return render_template('shortcuts.html')

@app.route('/updates')
def updates_page():
    return render_template('updates.html')

@app.route('/ocr')
def ocr_page():
    return render_template('ocr_calibration.html')

# Static dashboard assets (public/)
@app.route('/ms11-dashboard.html')
def serve_ms11_dashboard():
    public_dir = Path(__file__).parents[2] / 'public'
    return send_from_directory(str(public_dir), 'ms11-dashboard.html')


@app.route('/js/<path:filename>')
def serve_public_js(filename: str):
    public_js = Path(__file__).parents[2] / 'public' / 'js'
    return send_from_directory(str(public_js), filename)

# Static images (logos, icons)
@app.route('/img/<path:filename>')
def serve_public_img(filename: str):
    public_img = Path(__file__).parents[2] / 'public' / 'img'
    # Ensure directory exists to avoid 500s when missing. Create lazily.
    try:
        public_img.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    return send_from_directory(str(public_img), filename)

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

@app.route('/api/system/overview')
def api_system_overview():
    """Alias to provide tiles data compatibility if needed by client."""
    try:
        return jsonify({"modules": get_all_overviews()})
    except Exception:
        return jsonify({"modules": []})

# --- Addons API ---
@app.get('/api/addons')
def api_addons_list():
    try:
        return jsonify({"addons": list_plugins()})
    except Exception as e:
        logger.error(f"addons list error: {e}")
        return jsonify({"addons": []})

@app.post('/api/addons/<plugin_id>')
def api_addons_toggle(plugin_id: str):
    payload = request.get_json(silent=True) or {}
    enabled = bool(payload.get('enabled', True))
    ok = set_enabled(plugin_id, enabled)
    return jsonify({"ok": ok})

# --- Profiles API (stub: scan data/quest_profiles or similar) ---
@app.get('/api/profiles')
def api_profiles():
    try:
        from pathlib import Path
        profiles_dir = Path('data/quest_profiles')
        items = []
        if profiles_dir.exists():
            for p in sorted(profiles_dir.glob('**/*.json')):
                items.append({"id": p.stem, "name": p.stem.replace('_', ' ').title(), "path": str(p)})
        else:
            # fallback: list quest templates we already have
            profiles_dir = Path('data/quests')
            for p in sorted(profiles_dir.glob('**/*.json')):
                items.append({"id": p.stem, "name": p.stem.replace('_', ' ').title(), "path": str(p)})
        return jsonify({"profiles": items})
    except Exception as e:
        logger.error(f"profiles error: {e}")
        return jsonify({"profiles": []})

# --- Shortcuts API (local JSON storage) ---
SHORTCUTS_FILE = Path('data') / 'shortcuts.json'

def _load_shortcuts():
    try:
        if SHORTCUTS_FILE.exists():
            import json
            return json.loads(SHORTCUTS_FILE.read_text(encoding='utf-8'))
    except Exception:
        pass
    return []

def _save_shortcuts(items):
    try:
        import json
        SHORTCUTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        SHORTCUTS_FILE.write_text(json.dumps(items, indent=2), encoding='utf-8')
    except Exception:
        pass

@app.get('/api/shortcuts')
def api_shortcuts_list():
    return jsonify({"shortcuts": _load_shortcuts()})

@app.post('/api/shortcuts')
def api_shortcuts_add():
    payload = request.get_json(silent=True) or {}
    action = (payload.get('action') or '').strip()
    key = (payload.get('key') or '').strip()
    if not action or not key:
        return jsonify({"ok": False, "error": "invalid"}), 400
    items = _load_shortcuts()
    items = [s for s in items if s.get('action') != action]
    items.append({"action": action, "key": key})
    _save_shortcuts(items)
    return jsonify({"ok": True})

@app.delete('/api/shortcuts/<action_id>')
def api_shortcuts_del(action_id: str):
    items = _load_shortcuts()
    items = [s for s in items if s.get('action') != action_id]
    _save_shortcuts(items)
    return jsonify({"ok": True})

@app.get('/api/shortcuts/export')
def api_shortcuts_export():
    from flask import Response
    data = json.dumps(_load_shortcuts(), indent=2)
    return Response(data, mimetype='application/json', headers={'Content-Disposition': 'attachment; filename=shortcuts.json'})

@app.post('/api/shortcuts/import')
def api_shortcuts_import():
    try:
        payload = request.get_json(force=True)  # expecting full JSON list
        if not isinstance(payload, list):
            return jsonify({"ok": False, "error": "invalid"}), 400
        _save_shortcuts(payload)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 400

# --- Updates API (stubbed) ---
@app.get('/api/updates')
def api_updates_info():
    current = ms11_state.get('version', '1.0.0')
    latest = current  # TODO hook to GitHub release/tag check
    return jsonify({"current": current, "latest": latest, "updateAvailable": latest != current})

@app.post('/api/updates/apply')
def api_updates_apply():
    # Stub: In future, pull latest, install deps, restart services
    return jsonify({"ok": True})

# --- OCR calibration APIs ---
OCR_REGIONS_FILE = Path('data') / 'ocr_regions.json'

def _load_regions():
    try:
        if OCR_REGIONS_FILE.exists():
            return json.loads(OCR_REGIONS_FILE.read_text(encoding='utf-8'))
    except Exception:
        pass
    return {"hotbar": {}, "chat": {}}

def _save_regions(data):
    try:
        OCR_REGIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        OCR_REGIONS_FILE.write_text(json.dumps(data, indent=2), encoding='utf-8')
    except Exception:
        pass

@app.get('/api/ocr/regions')
def api_ocr_regions():
    return jsonify(_load_regions())

@app.post('/api/ocr/regions/<kind>')
def api_ocr_set(kind: str):
    data = _load_regions()
    payload = request.get_json(silent=True) or {}
    if kind not in ('hotbar','chat'):
        return jsonify({"ok": False}), 400
    data[kind] = {"x": int(payload.get('x',0)), "y": int(payload.get('y',0)), "w": int(payload.get('w',0)), "h": int(payload.get('h',0))}
    _save_regions(data)
    return jsonify({"ok": True})

@app.get('/api/ocr/test/<kind>')
def api_ocr_test(kind: str):
    try:
        from ms11lib.ocr import grab_text
        r = _load_regions().get(kind) or {}
        region = None
        if r and all(k in r for k in ('x','y','w','h')):
            region = (int(r['x']), int(r['y']), int(r['x'])+int(r['w']), int(r['y'])+int(r['h']))
        text = grab_text(region)
        return jsonify({"text": text})
    except Exception as e:
        return jsonify({"text": "", "error": str(e)})

# --- Backup API (on-demand)
def run_backup_once() -> tuple[bool, str]:
    try:
        from pathlib import Path
        import shutil
        cfg_dir = Path('config')
        if not cfg_dir.exists():
            return False, 'No config directory'
        dest_root = cfg_dir / 'backups'
        dest_root.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest = dest_root / f"manual_{timestamp}"
        dest.mkdir(parents=True, exist_ok=True)
        for p in cfg_dir.glob('*.*'):
            if p.is_file() and p.suffix.lower() in {'.json', '.yaml', '.yml'}:
                shutil.copy2(p, dest / p.name)
        return True, f'Backup saved to {dest}'
    except Exception as e:
        return False, f'Backup failed: {e}'

@app.post('/api/backup/run')
def api_backup_run():
    ok, msg = run_backup_once()
    return jsonify({"ok": ok, "message": msg})

# --- Active character for probe
ACTIVE_CHAR_FILE = Path('data') / 'active_character.json'

def _save_active_character(name: str) -> None:
    try:
        ACTIVE_CHAR_FILE.parent.mkdir(parents=True, exist_ok=True)
        ACTIVE_CHAR_FILE.write_text(json.dumps({"character": name, "ts": datetime.now().isoformat()}), encoding='utf-8')
    except Exception:
        pass

def _load_active_character() -> str | None:
    try:
        if ACTIVE_CHAR_FILE.exists():
            d = json.loads(ACTIVE_CHAR_FILE.read_text(encoding='utf-8'))
            return d.get('character')
    except Exception:
        pass
    return None

@app.get('/api/character/active')
def api_get_active_character():
    return jsonify({"character": _load_active_character()})

@app.post('/api/character/active')
def api_set_active_character():
    payload = request.get_json(silent=True) or {}
    name = (payload.get('character') or '').strip()
    if not name:
        return jsonify({"ok": False, "error": "invalid"}), 400
    _save_active_character(name)
    return jsonify({"ok": True})

# --- Module log tails
@app.get('/api/modules/<module_id>/logs')
def api_module_logs(module_id: str):
    try:
        base = Path('logs')
        candidates = [base / f"{module_id}.log", base / f"{module_id}.txt"]
        path = next((p for p in candidates if p.exists()), None)
        if not path:
            return jsonify({"lines": []})
        # return last 50 lines
        lines = path.read_text(encoding='utf-8', errors='ignore').splitlines()[-50:]
        return jsonify({"lines": lines})
    except Exception:
        return jsonify({"lines": []})

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

# --- System info endpoint to match scaffold ---
@app.route('/api/system/info')
def api_system_info():
    try:
        import psutil
        cpu_pct = psutil.cpu_percent(interval=None)
        vm = psutil.virtual_memory()
        free = vm.available
        total = vm.total
        mem_used_pct = round(((total - free) / total) * 100)
        uptime = int(time.time() - datetime.fromisoformat(ms11_state.get("started_at")).timestamp())
    except Exception:
        cpu_pct = None
        mem_used_pct = None
        uptime = None
    return jsonify({
        "cpu": cpu_pct,
        "memUsedPct": mem_used_pct,
        "uptime": uptime,
    })

# --- Configuration Management APIs ---
@app.get('/api/config/scan')
def api_config_scan():
    try:
        cfg_dir = Path('config')
        configs: list[str] = []
        templates: list[str] = []
        if cfg_dir.exists():
            configs = [p.name for p in sorted(cfg_dir.glob('*.json'))]
            configs += [p.name for p in sorted(cfg_dir.glob('*.yml'))]
            configs += [p.name for p in sorted(cfg_dir.glob('*.yaml'))]
        tdir = cfg_dir / 'templates'
        if tdir.exists():
            templates = [p.name for p in sorted(tdir.glob('*.yml'))]
            templates += [p.name for p in sorted(tdir.glob('*.yaml'))]
        return jsonify({"ok": True, "configs": configs, "templates": templates})
    except Exception as e:
        logger.error(f"config scan error: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


@app.post('/api/config/validate')
def api_config_validate():
    if not ConfigurationValidator:
        return jsonify({"ok": False, "error": "validator_unavailable"}), 400
    try:
        validator = ConfigurationValidator()
        result = validator.validate_all() if hasattr(validator, 'validate_all') else True
        return jsonify({"ok": bool(result)})
    except Exception as e:
        logger.error(f"config validate error: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


@app.post('/api/config/deploy')
def api_config_deploy():
    if not ConfigurationDeployer:
        return jsonify({"ok": False, "error": "deployer_unavailable"}), 400
    try:
        deployer = ConfigurationDeployer()
        result = deployer.deploy_all() if hasattr(deployer, 'deploy_all') else True
        return jsonify({"ok": bool(result)})
    except Exception as e:
        logger.error(f"config deploy error: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500

# --- Services start/stop (stubbed commands) ---
@app.post('/api/services/startAll')
def api_start_services():
    # Wire real commands or keep stubs for now
    try:
        start_managed_process('svc:combatd', 'combatd', [sys.executable, str(Path(__file__).parent / 'session_runner.py'), '--daemon', 'combat'])
        start_managed_process('svc:questd', 'questd', [sys.executable, str(Path(__file__).parent / 'session_runner.py'), '--daemon', 'quest'])
        return jsonify({"ok": True, "running": list(process_table.keys())})
    except Exception as e:
        logger.error(f"startAll failed: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500


@app.post('/api/services/stopAll')
def api_stop_services():
    try:
        with process_table_lock:
            ids = list(process_table.keys())
        for pid in ids:
            stop_managed_process(pid)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# --- Sessions API ---
@app.get('/api/sessions')
def api_list_sessions():
    with sessions_lock:
        return jsonify({"sessions": list(sessions_store.values())})


@app.post('/api/sessions')
def api_create_session():
    payload = request.get_json(silent=True) or {}
    profile = payload.get('profile') or 'default_profile'
    character = payload.get('character') or 'Player'
    mode = payload.get('mode') or 'quest'
    sid = str(uuid.uuid4())
    spec = {
        'id': sid,
        'profile': profile,
        'character': character,
        'mode': mode,
        'createdAt': datetime.now().isoformat(),
        'status': 'starting',
    }
    with sessions_lock:
        sessions_store[sid] = spec
    socketio.emit('session', {"type": "session", "data": spec})

    # launch runner process bound to this session
    pid = f'session:{sid}'
    start_managed_process(pid, f'session-{profile}', [
        sys.executable, str(Path(__file__).parent / 'session_runner.py'), sid, profile, character, mode
    ])
    spec['status'] = 'running'
    socketio.emit('session', {"type": "session", "data": spec})
    return jsonify({"ok": True, "session": spec})


@app.delete('/api/sessions/<sid>')
def api_stop_session(sid: str):
    stop_managed_process(f'session:{sid}')
    with sessions_lock:
        spec = sessions_store.get(sid)
        if spec:
            spec['status'] = 'stopped'
    if spec:
        socketio.emit('session', {"type": "session", "data": spec})
    return jsonify({"ok": True})

# SocketIO Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info(f"Client connected: {request.sid}")
    connected_clients.add(request.sid)
    ms11_state["active_sessions"] = len(connected_clients)
    emit('status_update', ms11_state)
    # On connect, send a small hello log line for the live console
    socketio.emit('log', {
        'type': 'log', 'level': 'info', 'source': 'ui',
        'msg': 'Client connected to MS11 WS', 'ts': datetime.now().isoformat()
    })

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info(f"Client disconnected: {request.sid}")
    connected_clients.discard(request.sid)
    ms11_state["active_sessions"] = len(connected_clients)
    socketio.emit('log', {
        'type': 'log', 'level': 'info', 'source': 'ui',
        'msg': 'Client disconnected from MS11 WS', 'ts': datetime.now().isoformat()
    })

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
    elif action == 'backup':
        ok, msg = run_backup_once()
        emit('action_response', {"success": ok, "message": msg, "timestamp": datetime.now().isoformat()})
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
            # Also emit a metric event compatible with scaffold
            try:
                perf = ms11_state.get("performance_metrics", {})
                if "cpu_usage" in perf:
                    socketio.emit('metric', {"type": "metric", "key": "cpu", "value": perf["cpu_usage"], "ts": datetime.now().isoformat()})
                if "memory_mb" in perf:
                    socketio.emit('metric', {"type": "metric", "key": "memory_mb", "value": perf["memory_mb"], "ts": datetime.now().isoformat()})
                # Attachment metric using ms11lib.window
                try:
                    from ms11lib.window import find_swg_window
                    attached = 1 if find_swg_window() else 0
                    socketio.emit('metric', {"type": "metric", "key": "attachment", "value": attached, "ts": datetime.now().isoformat()})
                except Exception:
                    pass
            except Exception:
                pass
            
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
