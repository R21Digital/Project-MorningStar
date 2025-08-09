"""
MS11 Integrated Server
Combines WebSocket real-time communication with REST API endpoints
Provides complete backend integration for the MS11 Dashboard
"""

import os
import sys
import time
import signal
import threading
from datetime import datetime
from typing import Optional

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from flask_cors import CORS

from core.structured_logging import StructuredLogger
from core.session_tracker import SessionTracker
from core.metrics_collector import MS11MetricsCollector
from core.enhanced_error_handling import handle_exceptions
from core.monitoring_system import get_monitor
from core.plugin_system import get_plugin_manager
from api.websocket_server import create_websocket_app, get_websocket_manager
from api.rest_endpoints import register_api_routes
from api.auth_endpoints import register_auth_routes
from api.plugin_endpoints import register_plugin_routes

# Initialize logger
logger = StructuredLogger("ms11_server")

class MS11Server:
    """Main MS11 server class that integrates all components"""
    
    def __init__(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        self.host = host
        self.port = port
        self.debug = debug
        self.app: Optional[Flask] = None
        self.socketio = None
        self.session_tracker: Optional[SessionTracker] = None
        self.metrics_collector: Optional[MS11MetricsCollector] = None
        self.monitor = get_monitor()
        self.plugin_manager = get_plugin_manager()
        self.running = False
        self.start_time = time.time()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, sig, frame):
        """Handle shutdown signals gracefully"""
        logger.info("Received shutdown signal", signal=sig)
        self.shutdown()
    
    def initialize_components(self):
        """Initialize core MS11 components"""
        try:
            logger.info("Initializing MS11 core components")
            
            # Initialize session tracker
            self.session_tracker = SessionTracker()
            logger.info("Session tracker initialized")
            
            # Initialize metrics collector
            self.metrics_collector = MS11MetricsCollector()
            logger.info("Metrics collector initialized")
            
            # Start background services
            self._start_background_services()
            
            # Start monitoring system
            self.monitor.start_monitoring()
            logger.info("Advanced monitoring system started")
            
            # Initialize and load plugins
            self.plugin_manager.execute_hook("ms11.startup")
            self.plugin_manager.load_all_plugins()
            logger.info("Plugin system initialized and plugins loaded")
            
        except Exception as e:
            logger.error("Failed to initialize components", error=str(e))
            raise
    
    def _start_background_services(self):
        """Start background services for session and metrics collection"""
        try:
            # Start session tracking
            if hasattr(self.session_tracker, 'start_tracking'):
                threading.Thread(
                    target=self.session_tracker.start_tracking,
                    daemon=True,
                    name="SessionTracker"
                ).start()
            
            # Start metrics collection
            if hasattr(self.metrics_collector, 'start_collection'):
                threading.Thread(
                    target=self.metrics_collector.start_collection,
                    daemon=True,
                    name="MetricsCollector"
                ).start()
            
            logger.info("Background services started")
            
        except Exception as e:
            logger.error("Failed to start background services", error=str(e))
    
    def create_app(self):
        """Create and configure Flask application"""
        try:
            logger.info("Creating Flask application")
            
            # Create WebSocket-enabled Flask app
            self.app, self.socketio = create_websocket_app(
                self.session_tracker, 
                self.metrics_collector
            )
            
            # Register REST API routes
            register_api_routes(self.app)
            
            # Register authentication routes
            register_auth_routes(self.app)
            
            # Register plugin management routes
            register_plugin_routes(self.app)
            
            # Add additional middleware and configuration
            self._configure_app()
            
            logger.info("Flask application created successfully")
            
        except Exception as e:
            logger.error("Failed to create Flask app", error=str(e))
            raise
    
    def _configure_app(self):
        """Configure Flask app with additional settings"""
        if not self.app:
            return
        
        # Additional CORS configuration
        CORS(self.app, origins=["http://localhost:3000", "http://localhost:3001"])
        
        # Add health check endpoint at root
        @self.app.route('/')
        @handle_exceptions(logger)
        def root():
            return {
                'name': 'MS11 Server',
                'version': '1.0.0',
                'status': 'running',
                'uptime': time.time() - self.start_time,
                'timestamp': datetime.now().isoformat()
            }
        
        # Add server info endpoint
        @self.app.route('/info')
        @handle_exceptions(logger)
        def server_info():
            ws_manager = get_websocket_manager()
            return {
                'server': {
                    'name': 'MS11 Integrated Server',
                    'version': '1.0.0',
                    'started_at': datetime.fromtimestamp(self.start_time).isoformat(),
                    'uptime': time.time() - self.start_time
                },
                'components': {
                    'websocket': {
                        'enabled': True,
                        'connected_clients': len(ws_manager.connected_clients) if ws_manager else 0,
                        'broadcasting': ws_manager.broadcasting if ws_manager else False
                    },
                    'session_tracker': {
                        'enabled': self.session_tracker is not None,
                        'active_sessions': len(getattr(self.session_tracker, 'active_sessions', {})) if self.session_tracker else 0
                    },
                    'metrics_collector': {
                        'enabled': self.metrics_collector is not None,
                        'collecting': getattr(self.metrics_collector, 'collecting', False) if self.metrics_collector else False
                    }
                },
                'endpoints': {
                    'websocket': f'ws://{self.host}:{self.port}',
                    'api': f'http://{self.host}:{self.port}/api',
                    'health': f'http://{self.host}:{self.port}/api/health',
                    'metrics': f'http://{self.host}:{self.port}/api/metrics'
                }
            }
        
        logger.info("Flask app configuration completed")
    
    def run(self):
        """Start the MS11 server"""
        try:
            if not self.app or not self.socketio:
                raise RuntimeError("App not initialized. Call initialize_components() and create_app() first.")
            
            self.running = True
            
            logger.info("Starting MS11 Server", 
                       host=self.host, port=self.port, debug=self.debug)
            
            # Start WebSocket broadcasting
            ws_manager = get_websocket_manager()
            if ws_manager:
                ws_manager.start_broadcasting()
            
            # Print startup information
            self._print_startup_info()
            
            # Run the server
            self.socketio.run(
                self.app,
                host=self.host,
                port=self.port,
                debug=self.debug,
                use_reloader=False  # Disable reloader to prevent issues with threading
            )
            
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error("Server startup failed", error=str(e))
            raise
        finally:
            self.shutdown()
    
    def _print_startup_info(self):
        """Print server startup information"""
        print("\n" + "="*60)
        print("🚀 MS11 Server Started Successfully!")
        print("="*60)
        print(f"📊 Dashboard URL:    http://localhost:3000")
        print(f"🌐 Server URL:       http://{self.host}:{self.port}")
        print(f"🔌 WebSocket URL:    ws://{self.host}:{self.port}")
        print(f"❤️  Health Check:    http://{self.host}:{self.port}/api/health")
        print(f"📈 Metrics:          http://{self.host}:{self.port}/api/metrics")
        print(f"ℹ️  Server Info:     http://{self.host}:{self.port}/info")
        print("-"*60)
        print(f"🕐 Started at:       {datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔧 Debug Mode:       {'Enabled' if self.debug else 'Disabled'}")
        print("="*60)
        print("🎮 Ready for MS11 Dashboard connections!")
        print("Press Ctrl+C to stop the server\n")
    
    def shutdown(self):
        """Gracefully shutdown the server"""
        if not self.running:
            return
        
        logger.info("Shutting down MS11 Server")
        self.running = False
        
        try:
            # Stop WebSocket broadcasting
            ws_manager = get_websocket_manager()
            if ws_manager:
                ws_manager.stop_broadcasting()
            
            # Stop background services
            if hasattr(self.session_tracker, 'stop_tracking'):
                self.session_tracker.stop_tracking()
            
            if hasattr(self.metrics_collector, 'stop_collection'):
                self.metrics_collector.stop_collection()
            
            # Stop monitoring system
            self.monitor.stop_monitoring()
            
            # Shutdown plugin system
            self.plugin_manager.execute_hook("ms11.shutdown")
            self.plugin_manager.shutdown()
            
            logger.info("MS11 Server shutdown completed")
            
        except Exception as e:
            logger.error("Error during shutdown", error=str(e))

def main():
    """Main entry point for the MS11 server"""
    try:
        # Parse command line arguments (basic implementation)
        import argparse
        
        parser = argparse.ArgumentParser(description='MS11 Integrated Server')
        parser.add_argument('--host', default='0.0.0.0', help='Host to bind to (default: 0.0.0.0)')
        parser.add_argument('--port', type=int, default=5000, help='Port to bind to (default: 5000)')
        parser.add_argument('--debug', action='store_true', help='Enable debug mode')
        parser.add_argument('--dev', action='store_true', help='Development mode (enables debug and CORS)')
        
        args = parser.parse_args()
        
        # Override settings for development mode
        if args.dev:
            args.debug = True
            args.host = '127.0.0.1'
        
        # Create and start server
        server = MS11Server(
            host=args.host,
            port=args.port,
            debug=args.debug
        )
        
        # Initialize all components
        server.initialize_components()
        server.create_app()
        
        # Start the server
        server.run()
        
    except Exception as e:
        logger.error("Failed to start MS11 server", error=str(e))
        sys.exit(1)

if __name__ == '__main__':
    main()