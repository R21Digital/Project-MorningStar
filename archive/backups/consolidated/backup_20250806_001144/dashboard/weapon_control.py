"""Weapon Control Dashboard

This module provides a web-based dashboard for manual weapon control,
status monitoring, and loadout management.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from flask import Flask, render_template, request, jsonify, redirect, url_for

from modules.weapon_swap_system import WeaponSwapSystem
from android_ms11.utils.logging_utils import log_event

logger = logging.getLogger(__name__)

app = Flask(__name__)
weapon_system = None


def initialize_weapon_dashboard(config_path: str = "config/weapon_config.json"):
    """Initialize the weapon control dashboard.
    
    Parameters
    ----------
    config_path : str
        Path to weapon configuration file
    """
    global weapon_system
    weapon_system = WeaponSwapSystem(config_path)
    log_event("[WEAPON_DASHBOARD] Weapon control dashboard initialized")


@app.route('/')
def index():
    """Main dashboard page."""
    if not weapon_system:
        return "Weapon system not initialized", 500
    
    return render_template('weapon_dashboard.html', 
                         current_weapon=weapon_system.current_weapon,
                         current_loadout=weapon_system.current_loadout,
                         available_loadouts=list(weapon_system.loadouts.keys()))


@app.route('/api/status')
def get_status():
    """Get current weapon system status."""
    if not weapon_system:
        return jsonify({"error": "Weapon system not initialized"}), 500
    
    status = {
        "current_weapon": weapon_system.current_weapon,
        "current_loadout": weapon_system.current_loadout,
        "available_weapons": weapon_system.get_available_weapons(),
        "combat_context": weapon_system.combat_context,
        "weapon_stats": {}
    }
    
    # Add weapon statistics
    for weapon_name in weapon_system.get_available_weapons():
        weapon_stats = weapon_system.get_weapon_stats(weapon_name)
        if weapon_stats:
            status["weapon_stats"][weapon_name] = {
                "damage_type": weapon_stats.damage_type.value,
                "range": weapon_stats.range,
                "current_ammo": weapon_stats.current_ammo,
                "max_ammo": weapon_stats.ammo_capacity,
                "condition": weapon_stats.condition,
                "accuracy": weapon_stats.accuracy,
                "fire_rate": weapon_stats.fire_rate
            }
    
    return jsonify(status)


@app.route('/api/loadout/<loadout_name>', methods=['POST'])
def load_loadout(loadout_name):
    """Load a specific weapon loadout."""
    if not weapon_system:
        return jsonify({"error": "Weapon system not initialized"}), 500
    
    success = weapon_system.load_loadout(loadout_name)
    
    if success:
        log_event(f"[WEAPON_DASHBOARD] Loaded loadout: {loadout_name}")
        return jsonify({"success": True, "loadout": loadout_name})
    else:
        return jsonify({"error": f"Failed to load loadout: {loadout_name}"}), 400


@app.route('/api/weapon/<weapon_name>/swap', methods=['POST'])
def swap_weapon(weapon_name):
    """Manually swap to a specific weapon."""
    if not weapon_system:
        return jsonify({"error": "Weapon system not initialized"}), 500
    
    success = weapon_system.swap_weapon(weapon_name, "manual_dashboard")
    
    if success:
        log_event(f"[WEAPON_DASHBOARD] Manual weapon swap: {weapon_name}")
        return jsonify({"success": True, "weapon": weapon_name})
    else:
        return jsonify({"error": f"Failed to swap to weapon: {weapon_name}"}), 400


@app.route('/api/weapon/<weapon_name>/ammo', methods=['POST'])
def update_ammo(weapon_name):
    """Update weapon ammo count."""
    if not weapon_system:
        return jsonify({"error": "Weapon system not initialized"}), 500
    
    try:
        ammo_count = int(request.json.get("ammo", 0))
        weapon_system.update_weapon_ammo(weapon_name, ammo_count)
        
        log_event(f"[WEAPON_DASHBOARD] Updated {weapon_name} ammo: {ammo_count}")
        return jsonify({"success": True, "weapon": weapon_name, "ammo": ammo_count})
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid ammo count"}), 400


@app.route('/api/weapon/<weapon_name>/condition', methods=['POST'])
def update_condition(weapon_name):
    """Update weapon condition."""
    if not weapon_system:
        return jsonify({"error": "Weapon system not initialized"}), 500
    
    try:
        condition = float(request.json.get("condition", 100.0))
        weapon_system.update_weapon_condition(weapon_name, condition)
        
        log_event(f"[WEAPON_DASHBOARD] Updated {weapon_name} condition: {condition}%")
        return jsonify({"success": True, "weapon": weapon_name, "condition": condition})
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid condition value"}), 400


@app.route('/api/context', methods=['POST'])
def update_context():
    """Update combat context."""
    if not weapon_system:
        return jsonify({"error": "Weapon system not initialized"}), 500
    
    try:
        data = request.json
        weapon_system.set_combat_context(
            enemy_type=data.get("enemy_type"),
            distance=data.get("distance"),
            enemy_health=data.get("enemy_health"),
            player_health=data.get("player_health"),
            ammo_status=data.get("ammo_status", {}),
            weapon_conditions=data.get("weapon_conditions", {})
        )
        
        log_event(f"[WEAPON_DASHBOARD] Updated combat context")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": f"Failed to update context: {str(e)}"}), 400


@app.route('/api/recommendation')
def get_recommendation():
    """Get weapon recommendation for current context."""
    if not weapon_system:
        return jsonify({"error": "Weapon system not initialized"}), 500
    
    enemy_type = request.args.get("enemy_type", "unknown")
    distance = float(request.args.get("distance", 50.0))
    
    recommendation = weapon_system.get_best_weapon(enemy_type, distance)
    effectiveness = weapon_system.calculate_weapon_effectiveness(recommendation, enemy_type, distance) if recommendation else 0.0
    
    return jsonify({
        "recommended_weapon": recommendation,
        "effectiveness": effectiveness,
        "enemy_type": enemy_type,
        "distance": distance
    })


@app.route('/api/effectiveness')
def get_effectiveness():
    """Get weapon effectiveness for all weapons against current enemy."""
    if not weapon_system:
        return jsonify({"error": "Weapon system not initialized"}), 500
    
    enemy_type = request.args.get("enemy_type", "unknown")
    distance = float(request.args.get("distance", 50.0))
    
    effectiveness_data = {}
    for weapon_name in weapon_system.get_available_weapons():
        effectiveness = weapon_system.calculate_weapon_effectiveness(weapon_name, enemy_type, distance)
        effectiveness_data[weapon_name] = effectiveness
    
    return jsonify({
        "effectiveness": effectiveness_data,
        "enemy_type": enemy_type,
        "distance": distance
    })


@app.route('/api/history')
def get_history():
    """Get weapon swap history."""
    if not weapon_system:
        return jsonify({"error": "Weapon system not initialized"}), 500
    
    limit = int(request.args.get("limit", 10))
    history = weapon_system.get_weapon_history(limit)
    
    history_data = []
    for event in history:
        history_data.append({
            "timestamp": event.timestamp,
            "from_weapon": event.from_weapon,
            "to_weapon": event.to_weapon,
            "reason": event.reason,
            "effectiveness_score": event.effectiveness_score
        })
    
    return jsonify({"history": history_data})


@app.route('/api/analytics')
def get_analytics():
    """Get weapon system analytics."""
    if not weapon_system:
        return jsonify({"error": "Weapon system not initialized"}), 500
    
    analytics = {
        "total_weapons": len(weapon_system.weapons),
        "total_loadouts": len(weapon_system.loadouts),
        "current_weapon": weapon_system.current_weapon,
        "current_loadout": weapon_system.current_loadout,
        "available_weapons": len(weapon_system.get_available_weapons()),
        "total_swaps": len(weapon_system.weapon_history),
        "effectiveness_stats": weapon_system.get_weapon_effectiveness_stats()
    }
    
    return jsonify(analytics)


@app.route('/api/export')
def export_data():
    """Export weapon data to JSON file."""
    if not weapon_system:
        return jsonify({"error": "Weapon system not initialized"}), 500
    
    try:
        export_path = weapon_system.export_weapon_data()
        return jsonify({"success": True, "export_path": export_path})
    except Exception as e:
        return jsonify({"error": f"Failed to export data: {str(e)}"}), 500


@app.route('/api/auto_swap/<loadout_name>', methods=['POST'])
def toggle_auto_swap(loadout_name):
    """Toggle auto-swap for a loadout."""
    if not weapon_system:
        return jsonify({"error": "Weapon system not initialized"}), 500
    
    if loadout_name not in weapon_system.loadouts:
        return jsonify({"error": f"Loadout not found: {loadout_name}"}), 404
    
    enabled = request.json.get("enabled", True)
    weapon_system.loadouts[loadout_name].auto_swap_enabled = enabled
    
    log_event(f"[WEAPON_DASHBOARD] Auto-swap {'enabled' if enabled else 'disabled'} for {loadout_name}")
    return jsonify({"success": True, "loadout": loadout_name, "auto_swap_enabled": enabled})


if __name__ == '__main__':
    initialize_weapon_dashboard()
    app.run(debug=True, host='0.0.0.0', port=5001) 