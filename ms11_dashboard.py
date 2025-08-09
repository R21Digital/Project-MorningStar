#!/usr/bin/env python3
"""
MS11 Dashboard - Real-time monitoring and control interface
Provides visual interface for MS11 operations, status, and configuration.
"""

import json
import os
import sys
import subprocess
import threading
import time
import webbrowser
from pathlib import Path
from flask import Flask, render_template, jsonify, request, redirect, url_for
import psutil
import tkinter as tk
from tkinter import ttk, messagebox

class MS11Dashboard:
    def __init__(self):
        self.app = Flask(__name__)
        self.setup_routes()
        self.ms11_process = None
        self.config = {}
        self.load_config()
        
    def setup_routes(self):
        """Setup Flask routes for the dashboard."""
        
        @self.app.route('/')
        def index():
            return render_template('ms11_dashboard.html')
            
        @self.app.route('/api/status')
        def status():
            return jsonify(self.get_system_status())
            
        @self.app.route('/api/config')
        def get_config():
            return jsonify(self.config)
            
        @self.app.route('/api/config', methods=['POST'])
        def update_config():
            try:
                data = request.json
                self.update_config(data)
                return jsonify({"status": "success"})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)})
                
        @self.app.route('/api/launch', methods=['POST'])
        def launch_ms11():
            try:
                data = request.json
                profile = data.get('profile', 'default')
                self.launch_ms11(profile)
                return jsonify({"status": "success"})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)})
                
        @self.app.route('/api/stop', methods=['POST'])
        def stop_ms11():
            try:
                self.stop_ms11()
                return jsonify({"status": "success"})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)})
                
        @self.app.route('/api/restart', methods=['POST'])
        def restart_ms11():
            try:
                self.restart_ms11()
                return jsonify({"status": "success"})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)})
                
        @self.app.route('/api/logs')
        def get_logs():
            try:
                logs = self.get_recent_logs()
                return jsonify({"logs": logs})
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)})
                
        @self.app.route('/api/performance')
        def get_performance():
            try:
                perf = self.get_performance_metrics()
                return jsonify(perf)
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)})
                
    def load_config(self):
        """Load MS11 configuration."""
        try:
            config_path = Path("config/config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = {
                    "character_name": "Not Configured",
                    "default_mode": "medic",
                    "enable_discord_relay": False
                }
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = {}
            
    def update_config(self, new_config):
        """Update configuration and save to file."""
        self.config.update(new_config)
        
        # Save to file
        os.makedirs("config", exist_ok=True)
        with open("config/config.json", 'w') as f:
            json.dump(self.config, f, indent=4)
            
    def get_system_status(self):
        """Get current system status."""
        status = {
            "ms11_running": self.is_ms11_running(),
            "config": self.config,
            "uptime": self.get_uptime(),
            "memory_usage": self.get_memory_usage(),
            "cpu_usage": self.get_cpu_usage(),
            "disk_usage": self.get_disk_usage(),
            "swg_running": self.is_swg_running()
        }
        
        if self.ms11_process:
            status["ms11_pid"] = self.ms11_process.pid
            status["ms11_memory"] = self.ms11_process.memory_info().rss / 1024 / 1024  # MB
            
        return status
        
    def is_ms11_running(self):
        """Check if MS11 is currently running."""
        if self.ms11_process:
            return self.ms11_process.poll() is None
        return False
        
    def is_swg_running(self):
        """Check if Star Wars Galaxies is running."""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'swg' in proc.info['name'].lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
        
    def get_uptime(self):
        """Get system uptime."""
        try:
            uptime = time.time() - psutil.boot_time()
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)
            return f"{hours}h {minutes}m"
        except:
            return "Unknown"
            
    def get_memory_usage(self):
        """Get memory usage information."""
        try:
            memory = psutil.virtual_memory()
            return {
                "total": memory.total / 1024 / 1024 / 1024,  # GB
                "used": memory.used / 1024 / 1024 / 1024,    # GB
                "percent": memory.percent
            }
        except:
            return {"total": 0, "used": 0, "percent": 0}
            
    def get_cpu_usage(self):
        """Get CPU usage information."""
        try:
            return psutil.cpu_percent(interval=1)
        except:
            return 0
            
    def get_disk_usage(self):
        """Get disk usage information."""
        try:
            disk = psutil.disk_usage('/')
            return {
                "total": disk.total / 1024 / 1024 / 1024,  # GB
                "used": disk.used / 1024 / 1024 / 1024,    # GB
                "percent": (disk.used / disk.total) * 100
            }
        except:
            return {"total": 0, "used": 0, "percent": 0}
            
    def launch_ms11(self, profile="default"):
        """Launch MS11 with specified profile."""
        if self.is_ms11_running():
            return False, "MS11 is already running"
            
        try:
            # Check if main.py exists
            if not os.path.exists("src/main.py"):
                return False, "MS11 main.py not found"
                
            # Launch MS11
            cmd = [sys.executable, "src/main.py", "--profile", profile]
            self.ms11_process = subprocess.Popen(
                cmd, 
                cwd=os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            return True, f"MS11 launched with profile: {profile}"
            
        except Exception as e:
            return False, f"Error launching MS11: {e}"
            
    def stop_ms11(self):
        """Stop MS11 if running."""
        if self.ms11_process and self.is_ms11_running():
            try:
                self.ms11_process.terminate()
                self.ms11_process.wait(timeout=5)
                return True, "MS11 stopped successfully"
            except subprocess.TimeoutExpired:
                self.ms11_process.kill()
                return True, "MS11 force-killed"
            except Exception as e:
                return False, f"Error stopping MS11: {e}"
        else:
            return False, "MS11 is not running"
            
    def restart_ms11(self):
        """Restart MS11."""
        success, message = self.stop_ms11()
        if success:
            time.sleep(2)  # Wait a bit before restarting
            success, message = self.launch_ms11()
            return success, f"MS11 restarted: {message}"
        else:
            return False, f"Failed to stop MS11: {message}"
            
    def get_recent_logs(self, lines=50):
        """Get recent log entries."""
        try:
            log_path = Path("logs/ms11.log")
            if log_path.exists():
                with open(log_path, 'r') as f:
                    lines_list = f.readlines()
                    return lines_list[-lines:] if len(lines_list) > lines else lines_list
            else:
                return ["No log file found"]
        except Exception as e:
            return [f"Error reading logs: {e}"]
            
    def get_performance_metrics(self):
        """Get performance metrics."""
        try:
            metrics = {
                "timestamp": time.time(),
                "system": {
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_percent": psutil.disk_usage('/').percent
                }
            }
            
            if self.ms11_process and self.is_ms11_running():
                try:
                    proc = psutil.Process(self.ms11_process.pid)
                    metrics["ms11"] = {
                        "cpu_percent": proc.cpu_percent(),
                        "memory_mb": proc.memory_info().rss / 1024 / 1024,
                        "threads": proc.num_threads()
                    }
                except:
                    metrics["ms11"] = {"error": "Cannot access process info"}
                    
            return metrics
            
        except Exception as e:
            return {"error": str(e)}
            
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Run the dashboard."""
        print(f"🚀 Starting MS11 Dashboard on http://{host}:{port}")
        print("📊 Open your browser to view the dashboard")
        
        # Auto-open browser
        def open_browser():
            time.sleep(1.5)
            webbrowser.open(f"http://{host}:{port}")
            
        threading.Thread(target=open_browser, daemon=True).start()
        
        self.app.run(host=host, port=port, debug=debug)

def create_dashboard_templates():
    """Create dashboard HTML templates."""
    os.makedirs("dashboard/templates", exist_ok=True)
    
    # Main dashboard template
    dashboard_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MS11 Dashboard 🚀</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #333;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            color: white;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0,0,0,0.3);
        }
        
        .card h2 {
            color: #2a5298;
            margin-bottom: 20px;
            font-size: 1.5em;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 10px;
        }
        
        .status-running { background-color: #4CAF50; }
        .status-stopped { background-color: #f44336; }
        .status-unknown { background-color: #ff9800; }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-label {
            font-weight: 500;
            color: #666;
        }
        
        .metric-value {
            font-weight: 600;
            color: #2a5298;
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background-color: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 5px;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #4CAF50, #8BC34A);
            transition: width 0.3s ease;
        }
        
        .control-buttons {
            display: flex;
            gap: 15px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #4CAF50, #45a049);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
        }
        
        .btn-secondary {
            background: linear-gradient(135deg, #2196F3, #1976D2);
            color: white;
        }
        
        .btn-secondary:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(33, 150, 243, 0.4);
        }
        
        .btn-danger {
            background: linear-gradient(135deg, #f44336, #d32f2f);
            color: white;
        }
        
        .btn-danger:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(244, 67, 54, 0.4);
        }
        
        .btn-warning {
            background: linear-gradient(135deg, #ff9800, #f57c00);
            color: white;
        }
        
        .btn-warning:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 152, 0, 0.4);
        }
        
        .logs-container {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-top: 20px;
        }
        
        .logs-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .logs-content {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            max-height: 400px;
            overflow-y: auto;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.4;
        }
        
        .log-entry {
            padding: 2px 0;
            border-bottom: 1px solid #e9ecef;
        }
        
        .log-entry:last-child {
            border-bottom: none;
        }
        
        .refresh-btn {
            background: #6c757d;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 12px;
        }
        
        .refresh-btn:hover {
            background: #5a6268;
        }
        
        @media (max-width: 768px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
            
            .control-buttons {
                flex-direction: column;
            }
            
            .btn {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 MS11 Dashboard</h1>
            <p>Real-time monitoring and control for Star Wars Galaxies automation</p>
        </div>
        
        <div class="dashboard-grid">
            <!-- System Status Card -->
            <div class="card">
                <h2>🖥️ System Status</h2>
                <div class="metric">
                    <span class="metric-label">MS11 Status:</span>
                    <span class="metric-value">
                        <span class="status-indicator" id="ms11-status-indicator"></span>
                        <span id="ms11-status">Checking...</span>
                    </span>
                </div>
                <div class="metric">
                    <span class="metric-label">SWG Status:</span>
                    <span class="metric-value">
                        <span class="status-indicator" id="swg-status-indicator"></span>
                        <span id="swg-status">Checking...</span>
                    </span>
                </div>
                <div class="metric">
                    <span class="metric-label">System Uptime:</span>
                    <span class="metric-value" id="system-uptime">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">CPU Usage:</span>
                    <span class="metric-value" id="cpu-usage">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Memory Usage:</span>
                    <span class="metric-value" id="memory-usage">-</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="memory-progress"></div>
                </div>
            </div>
            
            <!-- MS11 Control Card -->
            <div class="card">
                <h2>🎮 MS11 Control</h2>
                <div class="metric">
                    <span class="metric-label">Character:</span>
                    <span class="metric-value" id="character-name">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Default Mode:</span>
                    <span class="metric-value" id="default-mode">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Profile:</span>
                    <span class="metric-value" id="current-profile">-</span>
                </div>
                <div class="control-buttons">
                    <button class="btn btn-primary" onclick="launchMS11()">🚀 Launch MS11</button>
                    <button class="btn btn-danger" onclick="stopMS11()">⏹️ Stop MS11</button>
                    <button class="btn btn-warning" onclick="restartMS11()">🔄 Restart MS11</button>
                </div>
            </div>
            
            <!-- Performance Card -->
            <div class="card">
                <h2>📊 Performance Metrics</h2>
                <div class="metric">
                    <span class="metric-label">Disk Usage:</span>
                    <span class="metric-value" id="disk-usage">-</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill" id="disk-progress"></div>
                </div>
                <div class="metric">
                    <span class="metric-label">MS11 Memory:</span>
                    <span class="metric-value" id="ms11-memory">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">MS11 CPU:</span>
                    <span class="metric-value" id="ms11-cpu">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Last Update:</span>
                    <span class="metric-value" id="last-update">-</span>
                </div>
            </div>
            
            <!-- Configuration Card -->
            <div class="card">
                <h2>⚙️ Configuration</h2>
                <div class="metric">
                    <span class="metric-label">Discord Integration:</span>
                    <span class="metric-value" id="discord-status">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Health Threshold:</span>
                    <span class="metric-value" id="health-threshold">-</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Fatigue Threshold:</span>
                    <span class="metric-value" id="fatigue-threshold">-</span>
                </div>
                <div class="control-buttons">
                    <button class="btn btn-secondary" onclick="openSetupWizard()">🔧 Setup Wizard</button>
                    <button class="btn btn-secondary" onclick="refreshConfig()">🔄 Refresh</button>
                </div>
            </div>
        </div>
        
        <!-- Logs Section -->
        <div class="logs-container">
            <div class="logs-header">
                <h2>📝 Recent Logs</h2>
                <button class="refresh-btn" onclick="refreshLogs()">Refresh Logs</button>
            </div>
            <div class="logs-content" id="logs-content">
                <div class="log-entry">Loading logs...</div>
            </div>
        </div>
    </div>
    
    <script>
        let updateInterval;
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            updateDashboard();
            updateInterval = setInterval(updateDashboard, 5000); // Update every 5 seconds
        });
        
        // Update dashboard data
        async function updateDashboard() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                updateSystemStatus(data);
                updatePerformanceMetrics(data);
                
                // Update last update time
                document.getElementById('last-update').textContent = new Date().toLocaleTimeString();
                
            } catch (error) {
                console.error('Error updating dashboard:', error);
            }
        }
        
        // Update system status
        function updateSystemStatus(data) {
            // MS11 Status
            const ms11Status = data.ms11_running ? 'Running' : 'Stopped';
            const ms11Indicator = data.ms11_running ? 'status-running' : 'status-stopped';
            
            document.getElementById('ms11-status').textContent = ms11Status;
            document.getElementById('ms11-status-indicator').className = `status-indicator ${ms11Indicator}`;
            
            // SWG Status
            const swgStatus = data.swg_running ? 'Running' : 'Stopped';
            const swgIndicator = data.swg_running ? 'status-running' : 'status-stopped';
            
            document.getElementById('swg-status').textContent = swgStatus;
            document.getElementById('swg-status-indicator').className = `status-indicator ${swgIndicator}`;
            
            // System metrics
            document.getElementById('system-uptime').textContent = data.uptime || '-';
            document.getElementById('cpu-usage').textContent = (data.cpu_usage || 0).toFixed(1) + '%';
            document.getElementById('memory-usage').textContent = (data.memory_usage.percent || 0).toFixed(1) + '%';
            
            // Memory progress bar
            const memoryProgress = data.memory_usage.percent || 0;
            document.getElementById('memory-progress').style.width = memoryProgress + '%';
            
            // Configuration
            if (data.config) {
                document.getElementById('character-name').textContent = data.config.character_name || '-';
                document.getElementById('default-mode').textContent = data.config.default_mode || '-';
                document.getElementById('discord-status').textContent = data.config.enable_discord_relay ? 'Enabled' : 'Disabled';
                
                if (data.config.safety) {
                    document.getElementById('health-threshold').textContent = (data.config.safety.health_threshold || 0) + '%';
                    document.getElementById('fatigue-threshold').textContent = (data.config.safety.fatigue_threshold || 0) + '%';
                }
            }
        }
        
        // Update performance metrics
        function updatePerformanceMetrics(data) {
            // Disk usage
            if (data.disk_usage) {
                document.getElementById('disk-usage').textContent = (data.disk_usage.percent || 0).toFixed(1) + '%';
                document.getElementById('disk-progress').style.width = (data.disk_usage.percent || 0) + '%';
            }
            
            // MS11 metrics
            if (data.ms11_pid) {
                document.getElementById('ms11-memory').textContent = (data.ms11_memory || 0).toFixed(1) + ' MB';
                document.getElementById('ms11-cpu').textContent = 'Active';
            } else {
                document.getElementById('ms11-memory').textContent = 'N/A';
                document.getElementById('ms11-cpu').textContent = 'N/A';
            }
        }
        
        // Control functions
        async function launchMS11() {
            try {
                const response = await fetch('/api/launch', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({profile: 'default'})
                });
                
                const result = await response.json();
                if (result.status === 'success') {
                    alert('MS11 launched successfully!');
                    setTimeout(updateDashboard, 2000);
                } else {
                    alert('Failed to launch MS11: ' + result.message);
                }
            } catch (error) {
                alert('Error launching MS11: ' + error);
            }
        }
        
        async function stopMS11() {
            if (confirm('Are you sure you want to stop MS11?')) {
                try {
                    const response = await fetch('/api/stop', {method: 'POST'});
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        alert('MS11 stopped successfully!');
                        setTimeout(updateDashboard, 1000);
                    } else {
                        alert('Failed to stop MS11: ' + result.message);
                    }
                } catch (error) {
                    alert('Error stopping MS11: ' + error);
                }
            }
        }
        
        async function restartMS11() {
            if (confirm('Are you sure you want to restart MS11?')) {
                try {
                    const response = await fetch('/api/restart', {method: 'POST'});
                    const result = await response.json();
                    
                    if (result.status === 'success') {
                        alert('MS11 restarted successfully!');
                        setTimeout(updateDashboard, 3000);
                    } else {
                        alert('Failed to restart MS11: ' + result.message);
                    }
                } catch (error) {
                    alert('Error restarting MS11: ' + error);
                }
            }
        }
        
        // Utility functions
        function openSetupWizard() {
            window.open('ms11_setup_wizard.py', '_blank');
        }
        
        async function refreshConfig() {
            await updateDashboard();
        }
        
        async function refreshLogs() {
            try {
                const response = await fetch('/api/logs');
                const data = await response.json();
                
                const logsContent = document.getElementById('logs-content');
                logsContent.innerHTML = '';
                
                if (data.logs && data.logs.length > 0) {
                    data.logs.forEach(log => {
                        const logEntry = document.createElement('div');
                        logEntry.className = 'log-entry';
                        logEntry.textContent = log.trim();
                        logsContent.appendChild(logEntry);
                    });
                } else {
                    logsContent.innerHTML = '<div class="log-entry">No logs available</div>';
                }
                
            } catch (error) {
                console.error('Error refreshing logs:', error);
            }
        }
        
        // Initial log load
        setTimeout(refreshLogs, 1000);
    </script>
</body>
</html>'''
    
    with open("dashboard/templates/ms11_dashboard.html", 'w') as f:
        f.write(dashboard_html)
        
    print("✅ Dashboard templates created successfully!")

def main():
    """Main entry point."""
    print("🚀 MS11 Dashboard")
    print("=" * 40)
    
    # Create templates if they don't exist
    if not os.path.exists("dashboard/templates/ms11_dashboard.html"):
        print("📝 Creating dashboard templates...")
        create_dashboard_templates()
    
    # Start dashboard
    dashboard = MS11Dashboard()
    
    try:
        dashboard.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error running dashboard: {e}")

if __name__ == "__main__":
    main()
