"""
Character Registry API Endpoints

Provides REST API endpoints for managing multiple characters per Discord user,
including character creation, switching, session management, and statistics.
"""

import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS

from core.character_registry import get_registry, CharacterProfile, CharacterSession

# Create Flask blueprint
character_api = Blueprint('character_api', __name__)
CORS(character_api)

# Get the global registry instance
registry = get_registry()


@character_api.route('/api/characters', methods=['GET'])
def get_characters():
    """Get all characters for a Discord user."""
    try:
        discord_user_id = request.args.get('discord_user_id')
        if not discord_user_id:
            return jsonify({'error': 'discord_user_id is required'}), 400
        
        characters = registry.get_characters_by_user(discord_user_id)
        
        # Convert to JSON-serializable format
        character_data = []
        for char in characters:
            char_dict = {
                'character_id': char.character_id,
                'discord_user_id': char.discord_user_id,
                'name': char.name,
                'server': char.server,
                'race': char.race,
                'profession': char.profession,
                'level': char.level,
                'faction': char.faction,
                'city': char.city,
                'guild': char.guild,
                'guild_tag': char.guild_tag,
                'planet': char.planet,
                'location': char.location,
                'coordinates': char.coordinates,
                'status': char.status,
                'role': char.role,
                'is_main_character': char.is_main_character,
                'auto_launch_enabled': char.auto_launch_enabled,
                'created_at': char.created_at,
                'updated_at': char.updated_at,
                'last_session_at': char.last_session_at,
                'total_playtime_hours': char.total_playtime_hours,
                'total_sessions': char.total_sessions,
                'total_xp_gained': char.total_xp_gained,
                'total_credits_earned': char.total_credits_earned,
                'notes': char.notes,
                'build_profile': char.build_profile,
                'combat_profile': char.combat_profile,
                'session_config': char.session_config
            }
            character_data.append(char_dict)
        
        return jsonify({
            'characters': character_data,
            'total_characters': len(character_data),
            'active_characters': len([c for c in characters if c.status == 'active']),
            'main_characters': len([c for c in characters if c.is_main_character])
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@character_api.route('/api/characters', methods=['POST'])
def create_character():
    """Create a new character for a Discord user."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        required_fields = ['discord_user_id', 'name', 'server', 'race', 'profession', 'level', 'faction', 'city']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create the character
        character = registry.create_character(
            discord_user_id=data['discord_user_id'],
            name=data['name'],
            server=data['server'],
            race=data['race'],
            profession=data['profession'],
            level=data['level'],
            faction=data['faction'],
            city=data['city'],
            guild=data.get('guild', ''),
            guild_tag=data.get('guild_tag', ''),
            planet=data.get('planet', ''),
            location=data.get('location', ''),
            coordinates=data.get('coordinates', (0.0, 0.0)),
            role=data.get('role', 'alt'),
            is_main_character=data.get('is_main_character', False),
            auto_launch_enabled=data.get('auto_launch_enabled', False),
            notes=data.get('notes', '')
        )
        
        # Return the created character
        char_dict = {
            'character_id': character.character_id,
            'discord_user_id': character.discord_user_id,
            'name': character.name,
            'server': character.server,
            'race': character.race,
            'profession': character.profession,
            'level': character.level,
            'faction': character.faction,
            'city': character.city,
            'guild': character.guild,
            'guild_tag': character.guild_tag,
            'planet': character.planet,
            'location': character.location,
            'coordinates': character.coordinates,
            'status': character.status,
            'role': character.role,
            'is_main_character': character.is_main_character,
            'auto_launch_enabled': character.auto_launch_enabled,
            'created_at': character.created_at,
            'updated_at': character.updated_at,
            'last_session_at': character.last_session_at,
            'total_playtime_hours': character.total_playtime_hours,
            'total_sessions': character.total_sessions,
            'total_xp_gained': character.total_xp_gained,
            'total_credits_earned': character.total_credits_earned,
            'notes': character.notes,
            'build_profile': character.build_profile,
            'combat_profile': character.combat_profile,
            'session_config': character.session_config
        }
        
        return jsonify(char_dict), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@character_api.route('/api/characters/<character_id>', methods=['GET'])
def get_character(character_id):
    """Get a specific character by ID."""
    try:
        character = registry.get_character_by_id(character_id)
        if not character:
            return jsonify({'error': 'Character not found'}), 404
        
        char_dict = {
            'character_id': character.character_id,
            'discord_user_id': character.discord_user_id,
            'name': character.name,
            'server': character.server,
            'race': character.race,
            'profession': character.profession,
            'level': character.level,
            'faction': character.faction,
            'city': character.city,
            'guild': character.guild,
            'guild_tag': character.guild_tag,
            'planet': character.planet,
            'location': character.location,
            'coordinates': character.coordinates,
            'status': character.status,
            'role': character.role,
            'is_main_character': character.is_main_character,
            'auto_launch_enabled': character.auto_launch_enabled,
            'created_at': character.created_at,
            'updated_at': character.updated_at,
            'last_session_at': character.last_session_at,
            'total_playtime_hours': character.total_playtime_hours,
            'total_sessions': character.total_sessions,
            'total_xp_gained': character.total_xp_gained,
            'total_credits_earned': character.total_credits_earned,
            'notes': character.notes,
            'build_profile': character.build_profile,
            'combat_profile': character.combat_profile,
            'session_config': character.session_config
        }
        
        return jsonify(char_dict)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@character_api.route('/api/characters/<character_id>', methods=['PUT'])
def update_character(character_id):
    """Update a character's information."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Update the character
        character = registry.update_character(character_id, **data)
        if not character:
            return jsonify({'error': 'Character not found'}), 404
        
        char_dict = {
            'character_id': character.character_id,
            'discord_user_id': character.discord_user_id,
            'name': character.name,
            'server': character.server,
            'race': character.race,
            'profession': character.profession,
            'level': character.level,
            'faction': character.faction,
            'city': character.city,
            'guild': character.guild,
            'guild_tag': character.guild_tag,
            'planet': character.planet,
            'location': character.location,
            'coordinates': character.coordinates,
            'status': character.status,
            'role': character.role,
            'is_main_character': character.is_main_character,
            'auto_launch_enabled': character.auto_launch_enabled,
            'created_at': character.created_at,
            'updated_at': character.updated_at,
            'last_session_at': character.last_session_at,
            'total_playtime_hours': character.total_playtime_hours,
            'total_sessions': character.total_sessions,
            'total_xp_gained': character.total_xp_gained,
            'total_credits_earned': character.total_credits_earned,
            'notes': character.notes,
            'build_profile': character.build_profile,
            'combat_profile': character.combat_profile,
            'session_config': character.session_config
        }
        
        return jsonify(char_dict)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@character_api.route('/api/characters/<character_id>', methods=['DELETE'])
def delete_character(character_id):
    """Delete a character (soft delete)."""
    try:
        success = registry.delete_character(character_id)
        if not success:
            return jsonify({'error': 'Character not found'}), 404
        
        return jsonify({'message': 'Character deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@character_api.route('/api/characters/switch', methods=['POST'])
def switch_character():
    """Switch to a different character for a user."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        discord_user_id = data.get('discord_user_id')
        character_name = data.get('character_name')
        
        if not discord_user_id or not character_name:
            return jsonify({'error': 'discord_user_id and character_name are required'}), 400
        
        character = registry.switch_character(discord_user_id, character_name)
        if not character:
            return jsonify({'error': 'Character not found'}), 404
        
        char_dict = {
            'character_id': character.character_id,
            'discord_user_id': character.discord_user_id,
            'name': character.name,
            'server': character.server,
            'race': character.race,
            'profession': character.profession,
            'level': character.level,
            'faction': character.faction,
            'city': character.city,
            'guild': character.guild,
            'guild_tag': character.guild_tag,
            'planet': character.planet,
            'location': character.location,
            'coordinates': character.coordinates,
            'status': character.status,
            'role': character.role,
            'is_main_character': character.is_main_character,
            'auto_launch_enabled': character.auto_launch_enabled,
            'created_at': character.created_at,
            'updated_at': character.updated_at,
            'last_session_at': character.last_session_at,
            'total_playtime_hours': character.total_playtime_hours,
            'total_sessions': character.total_sessions,
            'total_xp_gained': character.total_xp_gained,
            'total_credits_earned': character.total_credits_earned,
            'notes': character.notes,
            'build_profile': character.build_profile,
            'combat_profile': character.combat_profile,
            'session_config': character.session_config
        }
        
        return jsonify(char_dict)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@character_api.route('/api/characters/<character_id>/auto-launch', methods=['POST'])
def toggle_auto_launch(character_id):
    """Toggle auto-launch setting for a character."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        enabled = data.get('enabled')
        if enabled is None:
            return jsonify({'error': 'enabled field is required'}), 400
        
        # Update the character's auto-launch setting
        character = registry.update_character(character_id, auto_launch_enabled=enabled)
        if not character:
            return jsonify({'error': 'Character not found'}), 404
        
        return jsonify({
            'character_id': character_id,
            'auto_launch_enabled': character.auto_launch_enabled
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@character_api.route('/api/characters/<character_id>/sessions', methods=['GET'])
def get_character_sessions(character_id):
    """Get sessions for a character."""
    try:
        days = request.args.get('days', type=int)
        sessions = registry.get_character_sessions(character_id, days)
        
        session_data = []
        for session in sessions:
            session_dict = {
                'session_id': session.session_id,
                'character_id': session.character_id,
                'start_time': session.start_time,
                'end_time': session.end_time,
                'mode': session.mode,
                'xp_gained': session.xp_gained,
                'credits_gained': session.credits_gained,
                'playtime_minutes': session.playtime_minutes,
                'actions_completed': session.actions_completed,
                'notes': session.notes
            }
            session_data.append(session_dict)
        
        return jsonify({
            'sessions': session_data,
            'total_sessions': len(session_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@character_api.route('/api/characters/<character_id>/sessions', methods=['POST'])
def start_session(character_id):
    """Start a new session for a character."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        mode = data.get('mode', 'general')
        session_config = data.get('session_config')
        
        session = registry.start_session(character_id, mode, session_config)
        if not session:
            return jsonify({'error': 'Character not found'}), 404
        
        session_dict = {
            'session_id': session.session_id,
            'character_id': session.character_id,
            'start_time': session.start_time,
            'end_time': session.end_time,
            'mode': session.mode,
            'xp_gained': session.xp_gained,
            'credits_gained': session.credits_gained,
            'playtime_minutes': session.playtime_minutes,
            'actions_completed': session.actions_completed,
            'notes': session.notes
        }
        
        return jsonify(session_dict), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@character_api.route('/api/characters/<character_id>/sessions/<session_id>', methods=['PUT'])
def end_session(character_id, session_id):
    """End a character session."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        xp_gained = data.get('xp_gained', 0)
        credits_gained = data.get('credits_gained', 0)
        playtime_minutes = data.get('playtime_minutes', 0.0)
        actions_completed = data.get('actions_completed', [])
        notes = data.get('notes', '')
        
        session = registry.end_session(
            character_id,
            session_id,
            xp_gained=xp_gained,
            credits_gained=credits_gained,
            playtime_minutes=playtime_minutes,
            actions_completed=actions_completed,
            notes=notes
        )
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        session_dict = {
            'session_id': session.session_id,
            'character_id': session.character_id,
            'start_time': session.start_time,
            'end_time': session.end_time,
            'mode': session.mode,
            'xp_gained': session.xp_gained,
            'credits_gained': session.credits_gained,
            'playtime_minutes': session.playtime_minutes,
            'actions_completed': session.actions_completed,
            'notes': session.notes
        }
        
        return jsonify(session_dict)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@character_api.route('/api/users/<discord_user_id>/statistics', methods=['GET'])
def get_user_statistics(discord_user_id):
    """Get comprehensive statistics for a Discord user."""
    try:
        stats = registry.get_user_statistics(discord_user_id)
        
        # Convert characters to JSON-serializable format
        characters_data = []
        for char in stats['characters']:
            char_dict = {
                'character_id': char.character_id,
                'discord_user_id': char.discord_user_id,
                'name': char.name,
                'server': char.server,
                'race': char.race,
                'profession': char.profession,
                'level': char.level,
                'faction': char.faction,
                'city': char.city,
                'guild': char.guild,
                'guild_tag': char.guild_tag,
                'planet': char.planet,
                'location': char.location,
                'coordinates': char.coordinates,
                'status': char.status,
                'role': char.role,
                'is_main_character': char.is_main_character,
                'auto_launch_enabled': char.auto_launch_enabled,
                'created_at': char.created_at,
                'updated_at': char.updated_at,
                'last_session_at': char.last_session_at,
                'total_playtime_hours': char.total_playtime_hours,
                'total_sessions': char.total_sessions,
                'total_xp_gained': char.total_xp_gained,
                'total_credits_earned': char.total_credits_earned,
                'notes': char.notes,
                'build_profile': char.build_profile,
                'combat_profile': char.combat_profile,
                'session_config': char.session_config
            }
            characters_data.append(char_dict)
        
        # Convert sessions to JSON-serializable format
        sessions_data = []
        for session in stats['recent_sessions']:
            session_dict = {
                'session_id': session.session_id,
                'character_id': session.character_id,
                'start_time': session.start_time,
                'end_time': session.end_time,
                'mode': session.mode,
                'xp_gained': session.xp_gained,
                'credits_gained': session.credits_gained,
                'playtime_minutes': session.playtime_minutes,
                'actions_completed': session.actions_completed,
                'notes': session.notes
            }
            sessions_data.append(session_dict)
        
        # Convert main character if exists
        main_character = None
        if stats['main_character']:
            main_char = stats['main_character']
            main_character = {
                'character_id': main_char.character_id,
                'discord_user_id': main_char.discord_user_id,
                'name': main_char.name,
                'server': main_char.server,
                'race': main_char.race,
                'profession': main_char.profession,
                'level': main_char.level,
                'faction': main_char.faction,
                'city': main_char.city,
                'guild': main_char.guild,
                'guild_tag': main_char.guild_tag,
                'planet': main_char.planet,
                'location': main_char.location,
                'coordinates': main_char.coordinates,
                'status': main_char.status,
                'role': main_char.role,
                'is_main_character': main_char.is_main_character,
                'auto_launch_enabled': main_char.auto_launch_enabled,
                'created_at': main_char.created_at,
                'updated_at': main_char.updated_at,
                'last_session_at': main_char.last_session_at,
                'total_playtime_hours': main_char.total_playtime_hours,
                'total_sessions': main_char.total_sessions,
                'total_xp_gained': main_char.total_xp_gained,
                'total_credits_earned': main_char.total_credits_earned,
                'notes': main_char.notes,
                'build_profile': main_char.build_profile,
                'combat_profile': main_char.combat_profile,
                'session_config': main_char.session_config
            }
        
        return jsonify({
            'total_characters': stats['total_characters'],
            'active_characters': stats['active_characters'],
            'main_character': main_character,
            'total_playtime_hours': stats['total_playtime_hours'],
            'total_xp_gained': stats['total_xp_gained'],
            'total_credits_earned': stats['total_credits_earned'],
            'total_sessions': stats['total_sessions'],
            'recent_sessions': sessions_data,
            'characters': characters_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@character_api.route('/api/users/<discord_user_id>/auto-launch', methods=['GET'])
def get_auto_launch_characters(discord_user_id):
    """Get all characters with auto-launch enabled for a user."""
    try:
        characters = registry.get_auto_launch_characters(discord_user_id)
        
        character_data = []
        for char in characters:
            char_dict = {
                'character_id': char.character_id,
                'discord_user_id': char.discord_user_id,
                'name': char.name,
                'server': char.server,
                'race': char.race,
                'profession': char.profession,
                'level': char.level,
                'faction': char.faction,
                'city': char.city,
                'guild': char.guild,
                'guild_tag': char.guild_tag,
                'planet': char.planet,
                'location': char.location,
                'coordinates': char.coordinates,
                'status': char.status,
                'role': char.role,
                'is_main_character': char.is_main_character,
                'auto_launch_enabled': char.auto_launch_enabled,
                'created_at': char.created_at,
                'updated_at': char.updated_at,
                'last_session_at': char.last_session_at,
                'total_playtime_hours': char.total_playtime_hours,
                'total_sessions': char.total_sessions,
                'total_xp_gained': char.total_xp_gained,
                'total_credits_earned': char.total_credits_earned,
                'notes': char.notes,
                'build_profile': char.build_profile,
                'combat_profile': char.combat_profile,
                'session_config': char.session_config
            }
            character_data.append(char_dict)
        
        return jsonify({
            'characters': character_data,
            'total_auto_launch': len(character_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@character_api.route('/api/characters/<character_id>/export', methods=['GET'])
def export_character_data(character_id):
    """Export complete character data including sessions."""
    try:
        data = registry.export_character_data(character_id)
        if not data:
            return jsonify({'error': 'Character not found'}), 404
        
        return jsonify(data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@character_api.route('/api/characters/import', methods=['POST'])
def import_character_data():
    """Import character data from external source."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        discord_user_id = data.get('discord_user_id')
        if not discord_user_id:
            return jsonify({'error': 'discord_user_id is required'}), 400
        
        character = registry.import_character_data(data, discord_user_id)
        if not character:
            return jsonify({'error': 'Failed to import character data'}), 400
        
        char_dict = {
            'character_id': character.character_id,
            'discord_user_id': character.discord_user_id,
            'name': character.name,
            'server': character.server,
            'race': character.race,
            'profession': character.profession,
            'level': character.level,
            'faction': character.faction,
            'city': character.city,
            'guild': character.guild,
            'guild_tag': character.guild_tag,
            'planet': character.planet,
            'location': character.location,
            'coordinates': character.coordinates,
            'status': character.status,
            'role': character.role,
            'is_main_character': character.is_main_character,
            'auto_launch_enabled': character.auto_launch_enabled,
            'created_at': character.created_at,
            'updated_at': character.updated_at,
            'last_session_at': character.last_session_at,
            'total_playtime_hours': character.total_playtime_hours,
            'total_sessions': character.total_sessions,
            'total_xp_gained': character.total_xp_gained,
            'total_credits_earned': character.total_credits_earned,
            'notes': character.notes,
            'build_profile': character.build_profile,
            'combat_profile': character.combat_profile,
            'session_config': character.session_config
        }
        
        return jsonify(char_dict), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Health check endpoint
@character_api.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'character_registry_api',
        'timestamp': datetime.now().isoformat()
    })


def register_character_api(app: Flask):
    """Register the character API blueprint with the Flask app."""
    app.register_blueprint(character_api)
    return app 