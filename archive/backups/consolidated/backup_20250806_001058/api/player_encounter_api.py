#!/usr/bin/env python3
"""
Batch 138 - Player Encounter API

API endpoints for player encounter data collection and SWGDB integration.
Provides RESTful endpoints for accessing player encounter data, statistics,
and SWGDB upload functionality.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path

from flask import Flask, request, jsonify, send_file
from werkzeug.exceptions import BadRequest, NotFound

from core.player_encounter_scanner import player_scanner
from utils.license_hooks import requires_license
from profession_logic.utils.logger import logger


def register_player_encounter_routes(app: Flask) -> None:
    """Register player encounter API routes with Flask app.
    
    Parameters
    ----------
    app : Flask
        Flask application instance
    """
    
    @app.route('/api/player-encounters', methods=['GET'])
    @requires_license
    def api_player_encounters_list():
        """Get list of all player encounters.
        
        Query Parameters:
        - limit: Maximum number of encounters to return (default: 100)
        - offset: Number of encounters to skip (default: 0)
        - player_name: Filter by specific player name
        - guild: Filter by guild name
        - planet: Filter by planet
        - city: Filter by city
        - species: Filter by species
        - faction: Filter by faction
        - date_from: Filter encounters from date (ISO format)
        - date_to: Filter encounters to date (ISO format)
        """
        try:
            # Parse query parameters
            limit = min(int(request.args.get('limit', 100)), 1000)
            offset = int(request.args.get('offset', 0))
            player_name = request.args.get('player_name')
            guild = request.args.get('guild')
            planet = request.args.get('planet')
            city = request.args.get('city')
            species = request.args.get('species')
            faction = request.args.get('faction')
            date_from = request.args.get('date_from')
            date_to = request.args.get('date_to')
            
            # Filter encounters
            filtered_encounters = []
            for encounter in player_scanner.encounter_history:
                # Apply filters
                if player_name and player_name.lower() not in encounter.player_name.lower():
                    continue
                if guild and (not encounter.guild or guild.lower() not in encounter.guild.lower()):
                    continue
                if planet and planet.lower() not in encounter.planet.lower():
                    continue
                if city and city.lower() not in encounter.city.lower():
                    continue
                if species and (not encounter.species or species.lower() not in encounter.species.lower()):
                    continue
                if faction and (not encounter.faction or faction.lower() not in encounter.faction.lower()):
                    continue
                
                # Date filtering
                if date_from or date_to:
                    encounter_date = datetime.fromisoformat(encounter.timestamp.replace('Z', '+00:00'))
                    if date_from:
                        from_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
                        if encounter_date < from_date:
                            continue
                    if date_to:
                        to_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
                        if encounter_date > to_date:
                            continue
                
                filtered_encounters.append(encounter)
            
            # Apply pagination
            total_count = len(filtered_encounters)
            paginated_encounters = filtered_encounters[offset:offset + limit]
            
            # Convert to dict for JSON serialization
            encounters_data = []
            for encounter in paginated_encounters:
                encounter_dict = {
                    "player_name": encounter.player_name,
                    "guild": encounter.guild,
                    "title": encounter.title,
                    "species": encounter.species,
                    "faction": encounter.faction,
                    "planet": encounter.planet,
                    "city": encounter.city,
                    "coordinates": encounter.coordinates,
                    "timestamp": encounter.timestamp,
                    "encounter_type": encounter.encounter_type,
                    "confidence": encounter.confidence,
                    "screenshot_path": encounter.screenshot_path
                }
                encounters_data.append(encounter_dict)
            
            return jsonify({
                "encounters": encounters_data,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total_count
            })
            
        except Exception as e:
            logger.error(f"[API] Player encounters list error: {e}")
            return jsonify({"error": "Failed to retrieve encounters"}), 500
    
    @app.route('/api/player-encounters/statistics', methods=['GET'])
    @requires_license
    def api_player_encounters_statistics():
        """Get player encounter statistics."""
        try:
            stats = player_scanner.get_player_statistics()
            return jsonify(stats)
        except Exception as e:
            logger.error(f"[API] Player statistics error: {e}")
            return jsonify({"error": "Failed to retrieve statistics"}), 500
    
    @app.route('/api/player-encounters/players', methods=['GET'])
    @requires_license
    def api_player_encounters_players():
        """Get list of all known players.
        
        Query Parameters:
        - limit: Maximum number of players to return (default: 100)
        - offset: Number of players to skip (default: 0)
        - sort_by: Sort field (name, encounter_count, last_seen, first_seen)
        - sort_order: Sort order (asc, desc)
        - guild: Filter by guild name
        - species: Filter by species
        - faction: Filter by faction
        """
        try:
            # Parse query parameters
            limit = min(int(request.args.get('limit', 100)), 1000)
            offset = int(request.args.get('offset', 0))
            sort_by = request.args.get('sort_by', 'name')
            sort_order = request.args.get('sort_order', 'asc')
            guild = request.args.get('guild')
            species = request.args.get('species')
            faction = request.args.get('faction')
            
            # Filter players
            filtered_players = []
            for player_name, player_info in player_scanner.known_players.items():
                # Apply filters
                if guild and (not player_info.guild or guild.lower() not in player_info.guild.lower()):
                    continue
                if species and (not player_info.species or species.lower() not in player_info.species.lower()):
                    continue
                if faction and (not player_info.faction or faction.lower() not in player_info.faction.lower()):
                    continue
                
                filtered_players.append(player_info)
            
            # Sort players
            reverse_sort = sort_order.lower() == 'desc'
            if sort_by == 'encounter_count':
                filtered_players.sort(key=lambda p: p.encounter_count, reverse=reverse_sort)
            elif sort_by == 'last_seen':
                filtered_players.sort(key=lambda p: p.last_seen, reverse=reverse_sort)
            elif sort_by == 'first_seen':
                filtered_players.sort(key=lambda p: p.first_seen, reverse=reverse_sort)
            else:  # sort_by == 'name'
                filtered_players.sort(key=lambda p: p.name.lower(), reverse=reverse_sort)
            
            # Apply pagination
            total_count = len(filtered_players)
            paginated_players = filtered_players[offset:offset + limit]
            
            # Convert to dict for JSON serialization
            players_data = []
            for player_info in paginated_players:
                player_dict = {
                    "name": player_info.name,
                    "guild": player_info.guild,
                    "title": player_info.title,
                    "species": player_info.species,
                    "faction": player_info.faction,
                    "profession": player_info.profession,
                    "level": player_info.level,
                    "encounter_count": player_info.encounter_count,
                    "first_seen": player_info.first_seen,
                    "last_seen": player_info.last_seen,
                    "location": player_info.location
                }
                players_data.append(player_dict)
            
            return jsonify({
                "players": players_data,
                "total_count": total_count,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total_count
            })
            
        except Exception as e:
            logger.error(f"[API] Player list error: {e}")
            return jsonify({"error": "Failed to retrieve players"}), 500
    
    @app.route('/api/player-encounters/players/<player_name>', methods=['GET'])
    @requires_license
    def api_player_encounters_player_detail(player_name):
        """Get detailed information about a specific player.
        
        Parameters
        ----------
        player_name : str
            Name of the player to retrieve
        """
        try:
            if player_name not in player_scanner.known_players:
                return jsonify({"error": "Player not found"}), 404
            
            player_info = player_scanner.known_players[player_name]
            
            # Get encounter history for this player
            player_encounters = [
                encounter for encounter in player_scanner.encounter_history
                if encounter.player_name == player_name
            ]
            
            # Convert to dict
            player_dict = {
                "name": player_info.name,
                "guild": player_info.guild,
                "title": player_info.title,
                "species": player_info.species,
                "faction": player_info.faction,
                "profession": player_info.profession,
                "level": player_info.level,
                "encounter_count": player_info.encounter_count,
                "first_seen": player_info.first_seen,
                "last_seen": player_info.last_seen,
                "location": player_info.location,
                "encounters": [
                    {
                        "planet": e.planet,
                        "city": e.city,
                        "coordinates": e.coordinates,
                        "timestamp": e.timestamp,
                        "encounter_type": e.encounter_type,
                        "confidence": e.confidence,
                        "screenshot_path": e.screenshot_path
                    }
                    for e in player_encounters[-20:]  # Last 20 encounters
                ]
            }
            
            return jsonify(player_dict)
            
        except Exception as e:
            logger.error(f"[API] Player detail error: {e}")
            return jsonify({"error": "Failed to retrieve player details"}), 500
    
    @app.route('/api/player-encounters/export/swgdb', methods=['GET'])
    @requires_license
    def api_player_encounters_export_swgdb():
        """Export player encounter data for SWGDB integration."""
        try:
            export_data = player_scanner.export_for_swgdb()
            return jsonify(export_data)
        except Exception as e:
            logger.error(f"[API] SWGDB export error: {e}")
            return jsonify({"error": "Failed to export data"}), 500
    
    @app.route('/api/player-encounters/export/json', methods=['GET'])
    @requires_license
    def api_player_encounters_export_json():
        """Export all player encounter data as JSON file."""
        try:
            export_data = {
                "known_players": {
                    name: {
                        "name": player_info.name,
                        "guild": player_info.guild,
                        "title": player_info.title,
                        "species": player_info.species,
                        "faction": player_info.faction,
                        "profession": player_info.profession,
                        "level": player_info.level,
                        "encounter_count": player_info.encounter_count,
                        "first_seen": player_info.first_seen,
                        "last_seen": player_info.last_seen,
                        "location": player_info.location
                    }
                    for name, player_info in player_scanner.known_players.items()
                },
                "encounter_history": [
                    {
                        "player_name": encounter.player_name,
                        "guild": encounter.guild,
                        "title": encounter.title,
                        "species": encounter.species,
                        "faction": encounter.faction,
                        "planet": encounter.planet,
                        "city": encounter.city,
                        "coordinates": encounter.coordinates,
                        "timestamp": encounter.timestamp,
                        "encounter_type": encounter.encounter_type,
                        "confidence": encounter.confidence,
                        "screenshot_path": encounter.screenshot_path
                    }
                    for encounter in player_scanner.encounter_history
                ],
                "export_timestamp": datetime.now().isoformat(),
                "scanner_version": "1.0.0"
            }
            
            # Create export file
            export_dir = Path("data/exports")
            export_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = export_dir / f"player_encounters_{timestamp}.json"
            
            with open(export_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            return send_file(
                export_file,
                as_attachment=True,
                download_name=f"player_encounters_{timestamp}.json",
                mimetype='application/json'
            )
            
        except Exception as e:
            logger.error(f"[API] JSON export error: {e}")
            return jsonify({"error": "Failed to export data"}), 500
    
    @app.route('/api/player-encounters/scan', methods=['POST'])
    @requires_license
    def api_player_encounters_scan():
        """Trigger a manual player scan.
        
        Request Body:
        - location: Current location information (optional)
        """
        try:
            data = request.get_json() or {}
            location = data.get('location', {
                "planet": "Unknown",
                "city": "Unknown",
                "coordinates": None
            })
            
            # Perform scan
            encounters = player_scanner.scan_for_players(location)
            
            return jsonify({
                "encounters_found": len(encounters),
                "encounters": [
                    {
                        "player_name": encounter.player_name,
                        "guild": encounter.guild,
                        "title": encounter.title,
                        "species": encounter.species,
                        "faction": encounter.faction,
                        "planet": encounter.planet,
                        "city": encounter.city,
                        "timestamp": encounter.timestamp,
                        "confidence": encounter.confidence
                    }
                    for encounter in encounters
                ],
                "scan_timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"[API] Manual scan error: {e}")
            return jsonify({"error": "Failed to perform scan"}), 500
    
    @app.route('/api/player-encounters/cleanup', methods=['POST'])
    @requires_license
    def api_player_encounters_cleanup():
        """Cleanup player encounter data and save to disk."""
        try:
            player_scanner.cleanup()
            return jsonify({
                "message": "Player encounter data cleaned up successfully",
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"[API] Cleanup error: {e}")
            return jsonify({"error": "Failed to cleanup data"}), 500
    
    @app.route('/api/player-encounters/screenshots/<player_name>', methods=['GET'])
    @requires_license
    def api_player_encounters_screenshots(player_name):
        """Get screenshots for a specific player.
        
        Parameters
        ----------
        player_name : str
            Name of the player
        """
        try:
            # Find screenshots for this player
            safe_name = player_name.replace(' ', '_')
            screenshot_dir = Path("data/player_encounters/screenshots")
            
            if not screenshot_dir.exists():
                return jsonify({"screenshots": []})
            
            screenshots = list(screenshot_dir.glob(f"{safe_name}_*.png"))
            
            screenshot_data = []
            for screenshot_path in screenshots:
                if screenshot_path.exists():
                    screenshot_data.append({
                        "filename": screenshot_path.name,
                        "path": str(screenshot_path),
                        "size": screenshot_path.stat().st_size,
                        "created": datetime.fromtimestamp(screenshot_path.stat().st_mtime).isoformat()
                    })
            
            return jsonify({
                "player_name": player_name,
                "screenshots": screenshot_data,
                "total_count": len(screenshot_data)
            })
            
        except Exception as e:
            logger.error(f"[API] Screenshots error: {e}")
            return jsonify({"error": "Failed to retrieve screenshots"}), 500
    
    @app.route('/api/player-encounters/screenshots/<player_name>/<filename>', methods=['GET'])
    @requires_license
    def api_player_encounters_screenshot_file(player_name, filename):
        """Get a specific screenshot file.
        
        Parameters
        ----------
        player_name : str
            Name of the player
        filename : str
            Screenshot filename
        """
        try:
            screenshot_path = Path("data/player_encounters/screenshots") / filename
            
            if not screenshot_path.exists():
                return jsonify({"error": "Screenshot not found"}), 404
            
            return send_file(
                screenshot_path,
                as_attachment=False,
                mimetype='image/png'
            )
            
        except Exception as e:
            logger.error(f"[API] Screenshot file error: {e}")
            return jsonify({"error": "Failed to retrieve screenshot"}), 500
    
    logger.info("[API] Player encounter routes registered")


# Example usage and testing
if __name__ == "__main__":
    # Create a test Flask app
    app = Flask(__name__)
    register_player_encounter_routes(app)
    
    print("Player Encounter API Routes:")
    print("- GET /api/player-encounters - List encounters")
    print("- GET /api/player-encounters/statistics - Get statistics")
    print("- GET /api/player-encounters/players - List players")
    print("- GET /api/player-encounters/players/<name> - Player details")
    print("- GET /api/player-encounters/export/swgdb - SWGDB export")
    print("- GET /api/player-encounters/export/json - JSON export")
    print("- POST /api/player-encounters/scan - Manual scan")
    print("- POST /api/player-encounters/cleanup - Cleanup data")
    print("- GET /api/player-encounters/screenshots/<name> - Player screenshots") 