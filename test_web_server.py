#!/usr/bin/env python3
"""
MS11 Web Server Test
Simple test server to verify all the web pages are connected properly
"""

import sys
import os
from flask import Flask
from flask_cors import CORS

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_minimal_stubs():
    """Create minimal stubs for missing modules"""
    
    # Create minimal StructuredLogger
    if not os.path.exists('core/structured_logging.py'):
        os.makedirs('core', exist_ok=True)
        with open('core/structured_logging.py', 'w') as f:
            f.write("""
import logging

class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def info(self, msg, **kwargs):
        self.logger.info(f"{msg} {kwargs if kwargs else ''}")
    
    def warning(self, msg, **kwargs):
        self.logger.warning(f"{msg} {kwargs if kwargs else ''}")
    
    def error(self, msg, **kwargs):
        self.logger.error(f"{msg} {kwargs if kwargs else ''}")
    
    def debug(self, msg, **kwargs):
        self.logger.debug(f"{msg} {kwargs if kwargs else ''}")
""")

    # Create minimal enhanced_error_handling
    if not os.path.exists('core/enhanced_error_handling.py'):
        with open('core/enhanced_error_handling.py', 'w') as f:
            f.write("""
from functools import wraps

def handle_exceptions(logger):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                logger.error(f"Exception in {f.__name__}: {str(e)}")
                raise
        return wrapper
    return decorator
""")

def create_test_app():
    """Create Flask test application"""
    
    # Create minimal stubs
    create_minimal_stubs()
    
    app = Flask(__name__)
    CORS(app)
    
    # Configure Flask
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Set static folders
    app.static_folder = 'public'
    app.static_url_path = '/static'
    
    try:
        # Import and register routes
        from api.rest_endpoints import register_api_routes
        register_api_routes(app)
        
        print("[OK] API routes registered successfully")
        
    except ImportError as e:
        print(f"[WARN] Could not import API routes: {e}")
        print("Creating basic routes...")
        
        # Create basic routes manually
        @app.route('/')
        def home():
            try:
                return app.send_static_file('index.html')
            except:
                return """
                <html>
                <head><title>MS11 MorningStar</title></head>
                <body style="font-family: Arial; background: #0a0a0a; color: #fff; padding: 2rem;">
                <h1>MS11 MorningStar Control Center</h1>
                <p>Test server is running successfully!</p>
                <div style="margin: 2rem 0;">
                <h3>Available Pages:</h3>
                <ul>
                <li><a href="/dashboard" style="color: #8b5cf6;">Dashboard</a></li>
                <li><a href="/control-center" style="color: #8b5cf6;">Control Center</a></li>
                <li><a href="/config" style="color: #8b5cf6;">Configuration</a></li>
                <li><a href="/api/health" style="color: #8b5cf6;">API Health Check</a></li>
                </ul>
                </div>
                </body>
                </html>
                """
        
        @app.route('/api/health')
        def health():
            return {"success": True, "status": "ok", "message": "Test server running"}
        
        @app.route('/dashboard')
        def dashboard():
            try:
                with open('public/ms11-dashboard.html') as f:
                    return f.read()
            except:
                return "<h1>Dashboard - File not found</h1><a href='/'>Back to Home</a>"
        
        @app.route('/control-center')
        def control_center():
            try:
                with open('scripts/qa/templates/main_dashboard.html') as f:
                    return f.read()
            except:
                return "<h1>Control Center - File not found</h1><a href='/'>Back to Home</a>"
        
        @app.route('/config')
        def config():
            try:
                with open('scripts/qa/templates/configuration.html') as f:
                    return f.read()
            except:
                return "<h1>Configuration - File not found</h1><a href='/'>Back to Home</a>"
    
    return app

def test_pages():
    """Test that all expected pages exist"""
    
    pages = [
        ('public/index.html', 'Landing Page'),
        ('public/ms11-dashboard.html', 'System Dashboard'),
        ('scripts/qa/templates/main_dashboard.html', 'Control Center'),
        ('scripts/qa/templates/configuration.html', 'Configuration'),
    ]
    
    print("\n" + "="*50)
    print("Testing Page Availability")
    print("="*50)
    
    for file_path, name in pages:
        if os.path.exists(file_path):
            with open(file_path) as f:
                content = f.read()
                size_kb = len(content) / 1024
                print(f"[OK] {name:<20} - {file_path} ({size_kb:.1f}KB)")
        else:
            print(f"[MISSING] {name:<20} - {file_path}")

def main():
    """Run the test server"""
    
    print("MS11 Web Server Test")
    print("=" * 30)
    
    # Test page availability
    test_pages()
    
    # Create and run test app
    app = create_test_app()
    
    print("\n" + "="*50)
    print("Starting Test Server")
    print("="*50)
    print("Server will be available at: http://localhost:5000")
    print("Dashboard: http://localhost:5000/dashboard")
    print("Control Center: http://localhost:5000/control-center")
    print("Configuration: http://localhost:5000/config")
    print("API Health: http://localhost:5000/api/health")
    print("\nPress Ctrl+C to stop the server")
    print("="*50)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\nServer stopped. Thanks for testing!")

if __name__ == "__main__":
    main()