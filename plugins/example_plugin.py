"""
Example MS11 Plugin
Demonstrates plugin system capabilities including hooks, events, and configuration
"""

from core.plugin_system import BasePlugin, PluginMetadata
from core.structured_logging import StructuredLogger

class ExamplePlugin(BasePlugin):
    """Example plugin demonstrating various plugin features"""
    
    def get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="example_plugin",
            version="1.0.0", 
            description="Example plugin demonstrating MS11 plugin system features",
            author="MS11 Development Team",
            category="example",
            priority=50,  # Load early
            dependencies=[]
        )
    
    def initialize(self):
        """Initialize the example plugin"""
        self.logger.info("Example plugin initializing")
        
        # Register hooks
        self.register_hook("ms11.startup", self._on_ms11_startup)
        self.register_hook("session.started", self._on_session_started)
        self.register_hook("command.executed", self._on_command_executed)
        self.register_hook("metrics.collected", self._on_metrics_collected)
        
        # Listen for events
        self.listen_for_event("custom.event", self._on_custom_event)
        
        # Load configuration
        self.greeting_message = self.get_config("greeting_message", "Hello from Example Plugin!")
        self.log_commands = self.get_config("log_commands", True)
        self.command_count = 0
        
        self.logger.info("Example plugin initialized successfully",
                        greeting=self.greeting_message,
                        log_commands=self.log_commands)
    
    def cleanup(self):
        """Cleanup plugin resources"""
        self.logger.info("Example plugin cleaning up",
                        commands_processed=self.command_count)
        
        # Save final statistics
        self.set_config("last_command_count", self.command_count)
    
    def _on_ms11_startup(self, *args, **kwargs):
        """Handle MS11 startup"""
        self.logger.info("MS11 is starting up!", message=self.greeting_message)
        
        # Emit a custom event
        self.emit_event("example.startup", {
            "plugin_name": self.get_metadata().name,
            "greeting": self.greeting_message
        })
    
    def _on_session_started(self, session_data=None, *args, **kwargs):
        """Handle session start"""
        if session_data:
            character_name = session_data.get('character_name', 'Unknown')
            self.logger.info("Session started for character", character=character_name)
            
            # You could add custom session handling here
            # For example: send a welcome message, initialize session-specific data, etc.
    
    def _on_command_executed(self, command_data=None, result=None, *args, **kwargs):
        """Handle command execution"""
        if self.log_commands and command_data:
            self.command_count += 1
            command = command_data.get('command', 'unknown')
            success = result.get('success', False) if result else False
            
            self.logger.info("Command executed",
                           command=command,
                           success=success,
                           total_commands=self.command_count)
            
            # You could add custom command processing here
            # For example: command validation, custom responses, statistics tracking, etc.
    
    def _on_metrics_collected(self, metrics_data=None, *args, **kwargs):
        """Handle metrics collection"""
        if metrics_data:
            # You could add custom metrics processing here
            # For example: custom alerts, data aggregation, external reporting, etc.
            
            cpu_usage = metrics_data.get('cpu_usage', 0)
            if cpu_usage > 80:
                self.logger.warning("High CPU usage detected", cpu_usage=cpu_usage)
    
    def _on_custom_event(self, data, source="unknown"):
        """Handle custom events from other plugins"""
        self.logger.info("Received custom event", source=source, data=data)
    
    # Custom plugin methods (can be called by other plugins)
    def get_command_statistics(self):
        """Get command execution statistics"""
        return {
            'total_commands': self.command_count,
            'commands_per_minute': self.command_count / max(1, self._get_uptime() / 60)
        }
    
    def _get_uptime(self):
        """Get plugin uptime in seconds"""
        import time
        return time.time() - getattr(self, '_start_time', time.time())

# Plugin entry point - this is what the plugin manager looks for
def create_plugin(plugin_manager):
    """Create plugin instance (alternative initialization method)"""
    return ExamplePlugin(plugin_manager)