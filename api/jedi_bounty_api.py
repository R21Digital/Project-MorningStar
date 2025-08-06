#!/usr/bin/env python3
"""
Batch 139 - Jedi Bounty Hunter API

API endpoints for Jedi bounty hunting kill logs and seasonal tracking.
Provides RESTful endpoints for accessing kill data, leaderboards,
season management, and manual entry system.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from flask import Flask, request, jsonify, send_file
from werkzeug.exceptions import BadRequest, NotFound

from core.jedi_bounty_tracker import get_jedi_bounty_tracker, JediKill, Season
from utils.license_hooks import requires_license
from profession_logic.utils.logger import logger


def register_jedi_bounty_routes(app: Flask) -> None:
    """Register Jedi bounty API routes with Flask app.
    
    Parameters
    ----------
    app : Flask
        Flask application instance
    """
    
    @app.route('/api/jedi-bounty/kills', methods=['GET'])
    def api_jedi_bounty_kills_list():
        """Get list of all Jedi bounty kills.
        
        Query Parameters:
        - limit: Maximum number of kills to return (default: 100)
        - offset: Number of kills to skip (default: 0)
        - target_name: Filter by target name
        - hunter_name: Filter by hunter name
        - planet: Filter by planet
        - kill_method: Filter by kill method
        - season_id: Filter by season ID
        - date_from: Filter kills from date (ISO format)
        - date_to: Filter kills to date (ISO format)
        """
        try:
            tracker = get_jedi_bounty_tracker()
            
            # Parse query parameters
            limit = min(int(request.args.get('limit', 100)), 1000)
            offset = int(request.args.get('offset', 0))
            target_name = request.args.get('target_name')
            hunter_name = request.args.get('hunter_name')
            planet = request.args.get('planet')
            kill_method = request.args.get('kill_method')
            season_id = request.args.get('season_id')
            date_from = request.args.get('date_from')
            date_to = request.args.get('date_to')
            
            # Filter kills
            filtered_kills = []
            for kill in tracker.kills:
                # Apply filters
                if target_name and target_name.lower() not in kill.target_name.lower():
                    continue
                if hunter_name and hunter_name.lower() not in kill.hunter_name.lower():
                    continue
                if planet and planet.lower() not in kill.planet.lower():
                    continue
                if kill_method and kill_method.lower() not in kill.kill_method.lower():
                    continue
                if season_id and kill.season_id != season_id:
                    continue
                
                # Date filtering
                if date_from or date_to:
                    kill_date = datetime.fromisoformat(kill.timestamp.replace('Z', '+00:00'))
                    if date_from:
                        from_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                        if kill_date < from_date:
                            continue
                    if date_to:
                        to_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                        if kill_date > to_date:
                            continue
                
                filtered_kills.append(kill)
            
            # Apply pagination
            total_count = len(filtered_kills)
            paginated_kills = filtered_kills[offset:offset + limit]
            
            # Convert to dict for JSON serialization
            kills_data = []
            for kill in paginated_kills:
                kill_dict = {
                    "kill_id": kill.kill_id,
                    "target_name": kill.target_name,
                    "location": kill.location,
                    "planet": kill.planet,
                    "coordinates": kill.coordinates,
                    "timestamp": kill.timestamp,
                    "reward_earned": kill.reward_earned,
                    "kill_method": kill.kill_method,
                    "season_id": kill.season_id,
                    "hunter_name": kill.hunter_name,
                    "target_level": kill.target_level,
                    "target_species": kill.target_species,
                    "target_faction": kill.target_faction,
                    "screenshot_path": kill.screenshot_path,
                    "notes": kill.notes
                }
                kills_data.append(kill_dict)
            
            return jsonify({
                "success": True,
                "data": kills_data,
                "total_count": total_count,
                "limit": limit,
                "offset": offset
            })
            
        except Exception as e:
            logger.error(f"[JEDI-BOUNTY-API] Error listing kills: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/jedi-bounty/kills', methods=['POST'])
    @requires_license
    def api_jedi_bounty_kills_create():
        """Create a new Jedi bounty kill record.
        
        Required JSON fields:
        - target_name: Name of the Jedi target
        - location: Location where kill occurred
        - planet: Planet where kill occurred
        - reward_earned: Credits earned
        - kill_method: Method used to kill
        - hunter_name: Name of the bounty hunter
        
        Optional fields:
        - coordinates: Tuple of coordinates
        - target_level: Level of target
        - target_species: Species of target
        - target_faction: Faction of target
        - screenshot_path: Path to screenshot
        - notes: Additional notes
        """
        try:
            data = request.get_json()
            if not data:
                raise BadRequest("No JSON data provided")
            
            # Validate required fields
            required_fields = ['target_name', 'location', 'planet', 'reward_earned', 'kill_method', 'hunter_name']
            for field in required_fields:
                if field not in data:
                    raise BadRequest(f"Missing required field: {field}")
            
            tracker = get_jedi_bounty_tracker()
            
            # Record the kill
            kill_id = tracker.record_jedi_kill(
                target_name=data['target_name'],
                location=data['location'],
                planet=data['planet'],
                coordinates=data.get('coordinates'),
                reward_earned=int(data['reward_earned']),
                kill_method=data['kill_method'],
                hunter_name=data['hunter_name'],
                target_level=data.get('target_level'),
                target_species=data.get('target_species'),
                target_faction=data.get('target_faction'),
                screenshot_path=data.get('screenshot_path'),
                notes=data.get('notes')
            )
            
            return jsonify({
                "success": True,
                "kill_id": kill_id,
                "message": f"Jedi bounty kill recorded: {data['target_name']}"
            })
            
        except BadRequest as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 400
        except Exception as e:
            logger.error(f"[JEDI-BOUNTY-API] Error creating kill: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/jedi-bounty/kills/<kill_id>', methods=['GET'])
    def api_jedi_bounty_kills_detail(kill_id: str):
        """Get details of a specific Jedi bounty kill.
        
        Parameters
        ----------
        kill_id : str
            ID of the kill to retrieve
        """
        try:
            tracker = get_jedi_bounty_tracker()
            kill = tracker.get_kill_by_id(kill_id)
            
            if not kill:
                return jsonify({
                    "success": False,
                    "error": "Kill not found"
                }), 404
            
            kill_dict = {
                "kill_id": kill.kill_id,
                "target_name": kill.target_name,
                "location": kill.location,
                "planet": kill.planet,
                "coordinates": kill.coordinates,
                "timestamp": kill.timestamp,
                "reward_earned": kill.reward_earned,
                "kill_method": kill.kill_method,
                "season_id": kill.season_id,
                "hunter_name": kill.hunter_name,
                "target_level": kill.target_level,
                "target_species": kill.target_species,
                "target_faction": kill.target_faction,
                "screenshot_path": kill.screenshot_path,
                "notes": kill.notes
            }
            
            return jsonify({
                "success": True,
                "data": kill_dict
            })
            
        except Exception as e:
            logger.error(f"[JEDI-BOUNTY-API] Error getting kill details: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/jedi-bounty/kills/<kill_id>', methods=['DELETE'])
    @requires_license
    def api_jedi_bounty_kills_delete(kill_id: str):
        """Delete a Jedi bounty kill record.
        
        Parameters
        ----------
        kill_id : str
            ID of the kill to delete
        """
        try:
            tracker = get_jedi_bounty_tracker()
            success = tracker.delete_kill(kill_id)
            
            if not success:
                return jsonify({
                    "success": False,
                    "error": "Kill not found"
                }), 404
            
            return jsonify({
                "success": True,
                "message": f"Kill {kill_id} deleted successfully"
            })
            
        except Exception as e:
            logger.error(f"[JEDI-BOUNTY-API] Error deleting kill: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/jedi-bounty/statistics', methods=['GET'])
    def api_jedi_bounty_statistics():
        """Get overall Jedi bounty hunting statistics."""
        try:
            tracker = get_jedi_bounty_tracker()
            stats = tracker.get_overall_statistics()
            
            return jsonify({
                "success": True,
                "data": stats
            })
            
        except Exception as e:
            logger.error(f"[JEDI-BOUNTY-API] Error getting statistics: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/jedi-bounty/seasons', methods=['GET'])
    def api_jedi_bounty_seasons_list():
        """Get list of all bounty hunting seasons."""
        try:
            tracker = get_jedi_bounty_tracker()
            
            seasons_data = []
            for season in tracker.seasons:
                season_dict = {
                    "season_id": season.season_id,
                    "name": season.name,
                    "start_date": season.start_date,
                    "end_date": season.end_date,
                    "is_active": season.is_active,
                    "description": season.description,
                    "special_rules": season.special_rules
                }
                seasons_data.append(season_dict)
            
            return jsonify({
                "success": True,
                "data": seasons_data
            })
            
        except Exception as e:
            logger.error(f"[JEDI-BOUNTY-API] Error listing seasons: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/jedi-bounty/seasons', methods=['POST'])
    @requires_license
    def api_jedi_bounty_seasons_create():
        """Create a new bounty hunting season.
        
        Required JSON fields:
        - name: Name of the season
        - start_date: Start date in ISO format
        - end_date: End date in ISO format
        
        Optional fields:
        - description: Season description
        - special_rules: Special rules for the season
        """
        try:
            data = request.get_json()
            if not data:
                raise BadRequest("No JSON data provided")
            
            # Validate required fields
            required_fields = ['name', 'start_date', 'end_date']
            for field in required_fields:
                if field not in data:
                    raise BadRequest(f"Missing required field: {field}")
            
            tracker = get_jedi_bounty_tracker()
            
            # Create the season
            season_id = tracker.create_season(
                name=data['name'],
                start_date=data['start_date'],
                end_date=data['end_date'],
                description=data.get('description'),
                special_rules=data.get('special_rules')
            )
            
            return jsonify({
                "success": True,
                "season_id": season_id,
                "message": f"Season created: {data['name']}"
            })
            
        except BadRequest as e:
            return jsonify({
                "success": False,
                "error": str(e)
            }), 400
        except Exception as e:
            logger.error(f"[JEDI-BOUNTY-API] Error creating season: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/jedi-bounty/seasons/<season_id>/activate', methods=['POST'])
    @requires_license
    def api_jedi_bounty_seasons_activate(season_id: str):
        """Activate a bounty hunting season.
        
        Parameters
        ----------
        season_id : str
            ID of the season to activate
        """
        try:
            tracker = get_jedi_bounty_tracker()
            success = tracker.activate_season(season_id)
            
            if not success:
                return jsonify({
                    "success": False,
                    "error": "Season not found"
                }), 404
            
            return jsonify({
                "success": True,
                "message": f"Season {season_id} activated successfully"
            })
            
        except Exception as e:
            logger.error(f"[JEDI-BOUNTY-API] Error activating season: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/jedi-bounty/seasons/<season_id>/leaderboard', methods=['GET'])
    def api_jedi_bounty_seasons_leaderboard(season_id: str):
        """Get leaderboard for a specific season.
        
        Parameters
        ----------
        season_id : str
            ID of the season to get leaderboard for
        """
        try:
            tracker = get_jedi_bounty_tracker()
            leaderboard = tracker.get_season_leaderboard(season_id)
            
            return jsonify({
                "success": True,
                "season_id": season_id,
                "data": leaderboard
            })
            
        except Exception as e:
            logger.error(f"[JEDI-BOUNTY-API] Error getting leaderboard: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/jedi-bounty/active-season', methods=['GET'])
    def api_jedi_bounty_active_season():
        """Get the currently active season."""
        try:
            tracker = get_jedi_bounty_tracker()
            active_season = tracker.get_active_season()
            
            if not active_season:
                return jsonify({
                    "success": False,
                    "error": "No active season found"
                }), 404
            
            season_dict = {
                "season_id": active_season.season_id,
                "name": active_season.name,
                "start_date": active_season.start_date,
                "end_date": active_season.end_date,
                "is_active": active_season.is_active,
                "description": active_season.description,
                "special_rules": active_season.special_rules
            }
            
            return jsonify({
                "success": True,
                "data": season_dict
            })
            
        except Exception as e:
            logger.error(f"[JEDI-BOUNTY-API] Error getting active season: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500
    
    @app.route('/api/jedi-bounty/export/json', methods=['GET'])
    @requires_license
    def api_jedi_bounty_export_json():
        """Export all Jedi bounty data as JSON."""
        try:
            tracker = get_jedi_bounty_tracker()
            
            export_data = {
                "kills": [asdict(kill) for kill in tracker.kills],
                "seasons": [asdict(season) for season in tracker.seasons],
                "statistics": tracker.get_overall_statistics(),
                "export_timestamp": datetime.now().isoformat()
            }
            
            return jsonify({
                "success": True,
                "data": export_data
            })
            
        except Exception as e:
            logger.error(f"[JEDI-BOUNTY-API] Error exporting data: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
            }), 500


# Register routes with Flask app
def init_jedi_bounty_api(app: Flask) -> None:
    """Initialize Jedi bounty API routes.
    
    Parameters
    ----------
    app : Flask
        Flask application instance
    """
    register_jedi_bounty_routes(app)
    logger.info("[JEDI-BOUNTY-API] Jedi bounty API routes registered") 