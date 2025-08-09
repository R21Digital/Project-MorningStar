"""
MS11 Static Routes for Dashboard Pages
Provides routing for the various dashboard interfaces
"""

import os
from flask import Blueprint, send_from_directory, abort
from functools import wraps

from core.structured_logging import StructuredLogger

# Initialize logger
logger = StructuredLogger("static_routes")

# Create static routes blueprint
static_bp = Blueprint('static_routes', __name__)

def log_static_call(f):
    """Decorator to log static file requests"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        logger.debug("Static file request", endpoint=f.__name__)
        return f(*args, **kwargs)
    return wrapper

@static_bp.route('/')
@log_static_call
def serve_home():
    """Serve main landing page"""
    try:
        return send_from_directory('public', 'index.html')
    except Exception as e:
        logger.error("Error serving home page", error=str(e))
        return "MS11 MorningStar - Service Unavailable", 503

@static_bp.route('/dashboard')
@log_static_call
def serve_dashboard():
    """Serve main dashboard page"""
    try:
        return send_from_directory('public', 'ms11-dashboard.html')
    except Exception as e:
        logger.error("Error serving dashboard", error=str(e))
        return "Dashboard - Service Unavailable", 503

@static_bp.route('/control-center')
@log_static_call
def serve_control_center():
    """Serve control center page"""
    try:
        return send_from_directory('scripts/qa/templates', 'main_dashboard.html')
    except Exception as e:
        logger.error("Error serving control center", error=str(e))
        return "Control Center - Service Unavailable", 503

@static_bp.route('/config')
@log_static_call
def serve_configuration():
    """Serve configuration page"""
    try:
        return send_from_directory('scripts/qa/templates', 'configuration.html')
    except Exception as e:
        logger.error("Error serving configuration", error=str(e))
        return "Configuration - Service Unavailable", 503

@static_bp.route('/analytics')
@log_static_call
def serve_analytics():
    """Serve analytics page"""
    try:
        return send_from_directory('scripts/qa/templates', 'analytics.html')
    except Exception as e:
        logger.error("Error serving analytics", error=str(e))
        return "Analytics - Service Unavailable", 503

@static_bp.route('/combat')
@log_static_call
def serve_combat():
    """Serve combat page"""
    try:
        return send_from_directory('scripts/qa/templates', 'combat.html')
    except Exception as e:
        logger.error("Error serving combat page", error=str(e))
        return "Combat - Service Unavailable", 503

@static_bp.route('/movement')
@log_static_call
def serve_movement():
    """Serve movement page"""
    try:
        return send_from_directory('scripts/qa/templates', 'movement.html')
    except Exception as e:
        logger.error("Error serving movement page", error=str(e))
        return "Movement - Service Unavailable", 503

@static_bp.route('/quests')
@log_static_call
def serve_quests():
    """Serve quests page"""
    try:
        return send_from_directory('scripts/qa/templates', 'quests.html')
    except Exception as e:
        logger.error("Error serving quests page", error=str(e))
        return "Quests - Service Unavailable", 503

@static_bp.route('/system')
@log_static_call
def serve_system():
    """Serve system page"""
    try:
        return send_from_directory('scripts/qa/templates', 'system.html')
    except Exception as e:
        logger.error("Error serving system page", error=str(e))
        return "System - Service Unavailable", 503

# Static file serving for assets
@static_bp.route('/js/<path:filename>')
@log_static_call
def serve_js(filename):
    """Serve JavaScript files"""
    try:
        return send_from_directory('public/js', filename)
    except Exception:
        abort(404)

@static_bp.route('/img/<path:filename>')
@log_static_call
def serve_images(filename):
    """Serve image files"""
    try:
        # Try multiple possible directories for images
        for img_dir in ['public/img', 'assets', 'static/img']:
            if os.path.exists(os.path.join(img_dir, filename)):
                return send_from_directory(img_dir, filename)
        abort(404)
    except Exception:
        abort(404)

def register_static_routes(app):
    """Register static routes with the Flask app"""
    app.register_blueprint(static_bp)
    logger.info("Static routes registered successfully")