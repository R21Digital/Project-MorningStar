"""
MS11 Plugin Management API Endpoints
Provides REST API for plugin management and configuration
"""

from flask import Blueprint, request, jsonify, g

from core.structured_logging import StructuredLogger
from core.enhanced_error_handling import handle_exceptions
from core.plugin_system import get_plugin_manager
from api.auth_middleware import require_auth
from api.rest_endpoints import api_response, validate_json, log_api_call

# Initialize logger
logger = StructuredLogger("plugin_endpoints")

# Create plugin management blueprint
plugin_bp = Blueprint('plugins', __name__, url_prefix='/api/plugins')

@plugin_bp.route('/', methods=['GET'])
@log_api_call
@require_auth('config:read')
@handle_exceptions(logger)
def list_plugins():
    """Get list of all plugins with their status"""
    try:
        plugin_manager = get_plugin_manager()
        
        # Get loaded plugins
        loaded_plugins = plugin_manager.get_plugin_info()
        
        # Get discovered but not loaded plugins
        discovered = plugin_manager.discover_plugins()
        
        all_plugins = {}
        
        # Add loaded plugins
        for name, info in loaded_plugins.items():
            all_plugins[name] = info
        
        # Add discovered but not loaded plugins
        for name in discovered:
            if name not in all_plugins:
                config = plugin_manager.get_plugin_config(name, 'enabled', True)
                all_plugins[name] = {
                    'name': name,
                    'loaded': False,
                    'enabled': config,
                    'version': 'unknown',
                    'description': 'Plugin not loaded',
                    'author': 'unknown',
                    'category': 'unknown',
                    'priority': 100,
                    'dependencies': [],
                    'hooks_registered': 0
                }
        
        # Convert to list and sort by name
        plugins_list = list(all_plugins.values())
        plugins_list.sort(key=lambda x: x['name'])
        
        return api_response(True, data={
            'plugins': plugins_list,
            'total_count': len(plugins_list),
            'loaded_count': len(loaded_plugins),
            'enabled_count': len([p for p in plugins_list if p.get('enabled', False)])
        })
        
    except Exception as e:
        logger.error("Failed to list plugins", error=str(e))
        return api_response(False, error="Failed to list plugins", status_code=500)

@plugin_bp.route('/<plugin_name>', methods=['GET'])
@log_api_call
@require_auth('config:read')
@handle_exceptions(logger)
def get_plugin_info(plugin_name: str):
    """Get detailed information about a specific plugin"""
    try:
        plugin_manager = get_plugin_manager()
        
        if plugin_name in plugin_manager.plugins:
            # Plugin is loaded
            plugin = plugin_manager.plugins[plugin_name]
            metadata = plugin.get_metadata()
            
            plugin_info = {
                **metadata.to_dict(),
                'loaded': True,
                'enabled': plugin.enabled,
                'hooks_registered': len(plugin._hooks_registered),
                'registered_hooks': [hook[0] for hook in plugin._hooks_registered],
                'configuration': plugin_manager.plugin_configs.get(plugin_name, {})
            }
            
        else:
            # Plugin is discovered but not loaded
            discovered = plugin_manager.discover_plugins()
            if plugin_name not in discovered:
                return api_response(False, error="Plugin not found", status_code=404)
            
            plugin_info = {
                'name': plugin_name,
                'loaded': False,
                'enabled': plugin_manager.get_plugin_config(plugin_name, 'enabled', True),
                'configuration': plugin_manager.plugin_configs.get(plugin_name, {}),
                'hooks_registered': 0,
                'registered_hooks': []
            }
        
        return api_response(True, data=plugin_info)
        
    except Exception as e:
        logger.error("Failed to get plugin info", plugin=plugin_name, error=str(e))
        return api_response(False, error="Failed to get plugin info", status_code=500)

@plugin_bp.route('/<plugin_name>/load', methods=['POST'])
@log_api_call
@require_auth('config:write')
@handle_exceptions(logger)
def load_plugin(plugin_name: str):
    """Load a specific plugin"""
    try:
        plugin_manager = get_plugin_manager()
        
        if plugin_name in plugin_manager.plugins:
            return api_response(False, error="Plugin is already loaded", status_code=400)
        
        # Load the plugin
        success = plugin_manager.load_plugin(plugin_name)
        
        if success:
            logger.info("Plugin loaded via API", plugin=plugin_name, user=g.current_user.username)
            return api_response(True, message=f"Plugin '{plugin_name}' loaded successfully")
        else:
            return api_response(False, error=f"Failed to load plugin '{plugin_name}'", status_code=500)
        
    except Exception as e:
        logger.error("Failed to load plugin", plugin=plugin_name, error=str(e))
        return api_response(False, error="Failed to load plugin", status_code=500)

@plugin_bp.route('/<plugin_name>/unload', methods=['POST'])
@log_api_call
@require_auth('config:write')
@handle_exceptions(logger)
def unload_plugin(plugin_name: str):
    """Unload a specific plugin"""
    try:
        plugin_manager = get_plugin_manager()
        
        if plugin_name not in plugin_manager.plugins:
            return api_response(False, error="Plugin is not loaded", status_code=400)
        
        # Unload the plugin
        success = plugin_manager.unload_plugin(plugin_name)
        
        if success:
            logger.info("Plugin unloaded via API", plugin=plugin_name, user=g.current_user.username)
            return api_response(True, message=f"Plugin '{plugin_name}' unloaded successfully")
        else:
            return api_response(False, error=f"Failed to unload plugin '{plugin_name}'", status_code=500)
        
    except Exception as e:
        logger.error("Failed to unload plugin", plugin=plugin_name, error=str(e))
        return api_response(False, error="Failed to unload plugin", status_code=500)

@plugin_bp.route('/<plugin_name>/reload', methods=['POST'])
@log_api_call
@require_auth('config:write')
@handle_exceptions(logger)
def reload_plugin(plugin_name: str):
    """Reload a specific plugin"""
    try:
        plugin_manager = get_plugin_manager()
        
        # Reload the plugin
        success = plugin_manager.reload_plugin(plugin_name)
        
        if success:
            logger.info("Plugin reloaded via API", plugin=plugin_name, user=g.current_user.username)
            return api_response(True, message=f"Plugin '{plugin_name}' reloaded successfully")
        else:
            return api_response(False, error=f"Failed to reload plugin '{plugin_name}'", status_code=500)
        
    except Exception as e:
        logger.error("Failed to reload plugin", plugin=plugin_name, error=str(e))
        return api_response(False, error="Failed to reload plugin", status_code=500)

@plugin_bp.route('/<plugin_name>/enable', methods=['POST'])
@log_api_call
@require_auth('config:write')
@handle_exceptions(logger)
def enable_plugin(plugin_name: str):
    """Enable a specific plugin"""
    try:
        plugin_manager = get_plugin_manager()
        
        plugin_manager.enable_plugin(plugin_name)
        
        logger.info("Plugin enabled via API", plugin=plugin_name, user=g.current_user.username)
        return api_response(True, message=f"Plugin '{plugin_name}' enabled")
        
    except Exception as e:
        logger.error("Failed to enable plugin", plugin=plugin_name, error=str(e))
        return api_response(False, error="Failed to enable plugin", status_code=500)

@plugin_bp.route('/<plugin_name>/disable', methods=['POST'])
@log_api_call
@require_auth('config:write')
@handle_exceptions(logger)
def disable_plugin(plugin_name: str):
    """Disable a specific plugin"""
    try:
        plugin_manager = get_plugin_manager()
        
        plugin_manager.disable_plugin(plugin_name)
        
        logger.info("Plugin disabled via API", plugin=plugin_name, user=g.current_user.username)
        return api_response(True, message=f"Plugin '{plugin_name}' disabled")
        
    except Exception as e:
        logger.error("Failed to disable plugin", plugin=plugin_name, error=str(e))
        return api_response(False, error="Failed to disable plugin", status_code=500)

@plugin_bp.route('/<plugin_name>/config', methods=['GET'])
@log_api_call
@require_auth('config:read')
@handle_exceptions(logger)
def get_plugin_config(plugin_name: str):
    """Get plugin configuration"""
    try:
        plugin_manager = get_plugin_manager()
        
        config = plugin_manager.plugin_configs.get(plugin_name, {})
        
        return api_response(True, data={
            'plugin_name': plugin_name,
            'configuration': config
        })
        
    except Exception as e:
        logger.error("Failed to get plugin config", plugin=plugin_name, error=str(e))
        return api_response(False, error="Failed to get plugin configuration", status_code=500)

@plugin_bp.route('/<plugin_name>/config', methods=['PUT'])
@log_api_call
@require_auth('config:write')
@validate_json()
@handle_exceptions(logger)
def update_plugin_config(plugin_name: str):
    """Update plugin configuration"""
    try:
        plugin_manager = get_plugin_manager()
        data = g.request_data
        
        # Update configuration
        for key, value in data.items():
            plugin_manager.set_plugin_config(plugin_name, key, value)
        
        logger.info("Plugin config updated via API", 
                   plugin=plugin_name, 
                   user=g.current_user.username,
                   keys=list(data.keys()))
        
        return api_response(True, message=f"Configuration updated for plugin '{plugin_name}'")
        
    except Exception as e:
        logger.error("Failed to update plugin config", plugin=plugin_name, error=str(e))
        return api_response(False, error="Failed to update plugin configuration", status_code=500)

@plugin_bp.route('/hooks', methods=['GET'])
@log_api_call
@require_auth('config:read')
@handle_exceptions(logger)
def list_hooks():
    """Get list of all available hooks"""
    try:
        plugin_manager = get_plugin_manager()
        
        hooks_info = []
        for hook_name, hook in plugin_manager.hooks.items():
            hooks_info.append({
                'name': hook_name,
                'description': hook.description,
                'enabled': hook.enabled,
                'callback_count': len([ref for ref in hook.callbacks if ref() is not None])
            })
        
        hooks_info.sort(key=lambda x: x['name'])
        
        return api_response(True, data={
            'hooks': hooks_info,
            'total_count': len(hooks_info)
        })
        
    except Exception as e:
        logger.error("Failed to list hooks", error=str(e))
        return api_response(False, error="Failed to list hooks", status_code=500)

@plugin_bp.route('/hooks/<hook_name>/execute', methods=['POST'])
@log_api_call
@require_auth('config:write')
@validate_json()
@handle_exceptions(logger)
def execute_hook(hook_name: str):
    """Manually execute a specific hook (for testing)"""
    try:
        plugin_manager = get_plugin_manager()
        data = g.request_data
        
        if hook_name not in plugin_manager.hooks:
            return api_response(False, error="Hook not found", status_code=404)
        
        # Execute the hook with provided data
        args = data.get('args', [])
        kwargs = data.get('kwargs', {})
        
        results = plugin_manager.execute_hook(hook_name, *args, **kwargs)
        
        logger.info("Hook executed manually via API", 
                   hook=hook_name, 
                   user=g.current_user.username,
                   result_count=len(results))
        
        return api_response(True, data={
            'hook_name': hook_name,
            'results': results,
            'callback_count': len(results)
        }, message=f"Hook '{hook_name}' executed successfully")
        
    except Exception as e:
        logger.error("Failed to execute hook", hook=hook_name, error=str(e))
        return api_response(False, error="Failed to execute hook", status_code=500)

@plugin_bp.route('/discover', methods=['POST'])
@log_api_call
@require_auth('config:write')
@handle_exceptions(logger)
def discover_plugins():
    """Discover new plugins in plugin directories"""
    try:
        plugin_manager = get_plugin_manager()
        
        discovered = plugin_manager.discover_plugins()
        
        logger.info("Plugin discovery completed via API", 
                   user=g.current_user.username,
                   discovered_count=len(discovered))
        
        return api_response(True, data={
            'discovered_plugins': discovered,
            'count': len(discovered)
        }, message=f"Discovered {len(discovered)} plugins")
        
    except Exception as e:
        logger.error("Failed to discover plugins", error=str(e))
        return api_response(False, error="Failed to discover plugins", status_code=500)

@plugin_bp.route('/load-all', methods=['POST'])
@log_api_call
@require_auth('config:write')
@handle_exceptions(logger)
def load_all_plugins():
    """Load all discovered and enabled plugins"""
    try:
        plugin_manager = get_plugin_manager()
        
        # Get current state
        before_count = len(plugin_manager.plugins)
        
        # Load all plugins
        plugin_manager.load_all_plugins()
        
        # Get new state
        after_count = len(plugin_manager.plugins)
        loaded_count = after_count - before_count
        
        logger.info("All plugins loaded via API", 
                   user=g.current_user.username,
                   newly_loaded=loaded_count,
                   total_loaded=after_count)
        
        return api_response(True, data={
            'newly_loaded': loaded_count,
            'total_loaded': after_count,
            'loaded_plugins': list(plugin_manager.plugins.keys())
        }, message=f"Loaded {loaded_count} new plugins")
        
    except Exception as e:
        logger.error("Failed to load all plugins", error=str(e))
        return api_response(False, error="Failed to load all plugins", status_code=500)

def register_plugin_routes(app):
    """Register plugin management routes with Flask app"""
    app.register_blueprint(plugin_bp)
    logger.info("Plugin management routes registered")