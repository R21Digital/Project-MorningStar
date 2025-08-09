#!/usr/bin/env python3
"""
Configuration Automation UI for MS11
Provides a web-based interface for managing configuration files without command line usage.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import threading
import webbrowser

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_socketio import SocketIO, emit
import yaml

# Add the parent directory to the path to import our configuration automation
sys.path.append(str(Path(__file__).parent))
from configuration_automation import ConfigurationAutomation
from validate_configurations import ConfigurationValidator
from deploy_configurations import ConfigurationDeployer

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ms11-config-automation-secret-key-2024'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize configuration automation
config_automation = ConfigurationAutomation()
validator = ConfigurationValidator()
deployer = ConfigurationDeployer()

# Global state for real-time updates
deployment_status = {
    "status": "idle",
    "message": "Ready",
    "timestamp": datetime.now().isoformat(),
    "progress": 0
}

@app.route('/')
def index():
    """Main dashboard page."""
    try:
        # Get configuration overview
        config_files = config_automation.list_configurations()
        templates = config_automation.list_templates()
        environments = config_automation.list_environments()
        
        return render_template('dashboard.html', 
                             config_files=config_files,
                             templates=templates,
                             environments=environments,
                             deployment_status=deployment_status)
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return render_template('error.html', error=str(e))

@app.route('/configs')
def configs():
    """Configuration files management page."""
    try:
        config_files = config_automation.list_configurations()
        return render_template('configs.html', config_files=config_files)
    except Exception as e:
        logger.error(f"Error loading configs: {e}")
        return render_template('error.html', error=str(e))

@app.route('/templates')
def templates():
    """Configuration templates page."""
    try:
        templates = config_automation.list_templates()
        return render_template('templates.html', templates=templates)
    except Exception as e:
        logger.error(f"Error loading templates: {e}")
        return render_template('error.html', error=str(e))

@app.route('/deploy')
def deploy():
    """Deployment management page."""
    try:
        environments = config_automation.list_environments()
        deployments = deployer.get_deployment_history()
        return render_template('deploy.html', 
                             environments=environments,
                             deployments=deployments)
    except Exception as e:
        logger.error(f"Error loading deploy page: {e}")
        return render_template('error.html', error=str(e))

@app.route('/api/configs', methods=['GET'])
def api_get_configs():
    """API endpoint to get configuration files."""
    try:
        configs = config_automation.list_configurations()
        return jsonify({"success": True, "data": configs})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/configs/<path:config_path>', methods=['GET'])
def api_get_config(config_path):
    """API endpoint to get a specific configuration file."""
    try:
        config_content = config_automation.read_configuration(config_path)
        return jsonify({"success": True, "data": config_content})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/configs/<path:config_path>', methods=['PUT'])
def api_update_config(config_path):
    """API endpoint to update a configuration file."""
    try:
        data = request.get_json()
        content = data.get('content', '')
        
        # Validate the content first
        validation_result = validator.validate_configuration_content(content, config_path)
        if not validation_result['valid']:
            return jsonify({"success": False, "error": "Validation failed", "details": validation_result['errors']}), 400
        
        # Update the configuration
        config_automation.write_configuration(config_path, content)
        
        socketio.emit('config_updated', {
            'config_path': config_path,
            'timestamp': datetime.now().isoformat()
        })
        
        return jsonify({"success": True, "message": "Configuration updated successfully"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/validate', methods=['POST'])
def api_validate_config():
    """API endpoint to validate a configuration."""
    try:
        data = request.get_json()
        content = data.get('content', '')
        config_path = data.get('config_path', '')
        
        result = validator.validate_configuration_content(content, config_path)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/deploy', methods=['POST'])
def api_deploy_config():
    """API endpoint to deploy configurations."""
    try:
        data = request.get_json()
        environment = data.get('environment', 'development')
        config_files = data.get('config_files', [])
        
        # Start deployment in background thread
        def deploy_background():
            try:
                deployment_status.update({
                    "status": "deploying",
                    "message": f"Deploying to {environment}...",
                    "timestamp": datetime.now().isoformat(),
                    "progress": 0
                })
                socketio.emit('deployment_update', deployment_status)
                
                # Perform deployment
                result = deployer.deploy_to_environment(environment, config_files)
                
                deployment_status.update({
                    "status": "completed" if result['success'] else "failed",
                    "message": result.get('message', 'Deployment completed'),
                    "timestamp": datetime.now().isoformat(),
                    "progress": 100
                })
                socketio.emit('deployment_update', deployment_status)
                
            except Exception as e:
                deployment_status.update({
                    "status": "failed",
                    "message": f"Deployment failed: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                    "progress": 0
                })
                socketio.emit('deployment_update', deployment_status)
        
        thread = threading.Thread(target=deploy_background)
        thread.daemon = True
        thread.start()
        
        return jsonify({"success": True, "message": "Deployment started"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/backup', methods=['POST'])
def api_create_backup():
    """API endpoint to create a backup."""
    try:
        data = request.get_json()
        environment = data.get('environment', 'development')
        
        result = deployer.create_backup(environment)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/rollback', methods=['POST'])
def api_rollback():
    """API endpoint to rollback to a previous version."""
    try:
        data = request.get_json()
        environment = data.get('environment', 'development')
        backup_id = data.get('backup_id')
        
        result = deployer.rollback_to_backup(environment, backup_id)
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    emit('connected', {'message': 'Connected to MS11 Configuration Automation'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info("Client disconnected")

def open_browser():
    """Open the default web browser to the application."""
    webbrowser.open('http://localhost:5001')

def main():
    """Main entry point for the configuration UI."""
    try:
        # Avoid emojis that can break on some Windows codepages
        print("Starting MS11 Configuration Automation UI...")
        print("Opening web browser in 2 seconds...")
        
        # Open browser after a short delay
        threading.Timer(2.0, open_browser).start()
        
        # Start the Flask application
        socketio.run(app, host='0.0.0.0', port=5001, debug=False)
        
    except KeyboardInterrupt:
        print("\n👋 Configuration UI stopped by user")
    except Exception as e:
        logger.error(f"Failed to start configuration UI: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
