"""Social Profile API for SWGDB.

This module provides API endpoints for managing user profiles with social links,
vanity fields, and badges for public profile display.
"""

from __future__ import annotations

import json
from typing import Dict, List, Optional, Any
from datetime import datetime
from flask import Flask, request, jsonify, current_app
from flask_cors import CORS

from core.user_profile import (
    get_profile_manager,
    create_user_profile,
    get_user_profile,
    update_user_profile,
    update_social_links,
    UserProfile,
    SocialLinks,
    BadgeType
)
from core.character_registry import get_registry


# Initialize Flask Blueprint
social_api = Flask(__name__)
CORS(social_api)


def register_social_api(app: Flask) -> None:
    """Register the social profile API routes with a Flask app.
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(social_api, url_prefix='/api/social')


@social_api.route('/profiles', methods=['GET'])
def api_get_profiles():
    """Get all public user profiles with optional filtering.
    
    Query Parameters:
        query: Text search in display_name, about_me, playstyle
        playstyle: Filter by playstyle
        badges: Comma-separated list of badges to filter by
        limit: Maximum number of profiles to return (default: 50)
        offset: Number of profiles to skip (default: 0)
    
    Returns:
        JSON response with profiles and metadata
    """
    try:
        # Get query parameters
        query = request.args.get('query')
        playstyle = request.args.get('playstyle')
        badges_param = request.args.get('badges')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Parse badges filter
        badges = None
        if badges_param:
            badges = [b.strip() for b in badges_param.split(',')]
        
        # Get profile manager
        profile_manager = get_profile_manager()
        
        # Search profiles
        profiles = profile_manager.search_profiles(
            query=query,
            playstyle=playstyle,
            badges=badges
        )
        
        # Apply pagination
        total_count = len(profiles)
        profiles = profiles[offset:offset + limit]
        
        # Convert to dict for JSON serialization
        profile_data = []
        for profile in profiles:
            profile_dict = {
                'discord_user_id': profile.discord_user_id,
                'username': profile.username,
                'display_name': profile.display_name,
                'about_me': profile.about_me,
                'playstyle': profile.playstyle,
                'favorite_activities': profile.favorite_activities,
                'social_links': {
                    'discord_tag': profile.social_links.discord_tag,
                    'twitch_channel': profile.social_links.twitch_channel,
                    'steam_profile': profile.social_links.steam_profile,
                    'youtube_channel': profile.social_links.youtube_channel,
                    'twitter_handle': profile.social_links.twitter_handle,
                    'reddit_username': profile.social_links.reddit_username,
                    'website': profile.social_links.website,
                    'guild_website': profile.social_links.guild_website,
                },
                'badges': profile.badges,
                'profile_visibility': profile.profile_visibility,
                'created_at': profile.created_at,
                'updated_at': profile.updated_at,
                'last_active': profile.last_active,
            }
            profile_data.append(profile_dict)
        
        return jsonify({
            'success': True,
            'profiles': profile_data,
            'metadata': {
                'total_count': total_count,
                'returned_count': len(profile_data),
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@social_api.route('/profiles/<discord_user_id>', methods=['GET'])
def api_get_profile(discord_user_id: str):
    """Get a specific user profile by Discord user ID.
    
    Args:
        discord_user_id: Discord user ID
        
    Returns:
        JSON response with profile data
    """
    try:
        profile = get_user_profile(discord_user_id)
        
        if not profile:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404
        
        # Convert to dict for JSON serialization
        profile_dict = {
            'discord_user_id': profile.discord_user_id,
            'username': profile.username,
            'display_name': profile.display_name,
            'about_me': profile.about_me,
            'playstyle': profile.playstyle,
            'favorite_activities': profile.favorite_activities,
            'social_links': {
                'discord_tag': profile.social_links.discord_tag,
                'twitch_channel': profile.social_links.twitch_channel,
                'steam_profile': profile.social_links.steam_profile,
                'youtube_channel': profile.social_links.youtube_channel,
                'twitter_handle': profile.social_links.twitter_handle,
                'reddit_username': profile.social_links.reddit_username,
                'website': profile.social_links.website,
                'guild_website': profile.social_links.guild_website,
            },
            'badges': profile.badges,
            'profile_visibility': profile.profile_visibility,
            'created_at': profile.created_at,
            'updated_at': profile.updated_at,
            'last_active': profile.last_active,
        }
        
        return jsonify({
            'success': True,
            'profile': profile_dict
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@social_api.route('/profiles', methods=['POST'])
def api_create_profile():
    """Create a new user profile.
    
    Request Body:
        discord_user_id: Discord user ID (required)
        username: Username (required)
        display_name: Display name (required)
        about_me: About me description (optional)
        playstyle: Playstyle description (optional)
        favorite_activities: List of favorite activities (optional)
        social_links: Social media links (optional)
        profile_visibility: Profile visibility setting (optional)
    
    Returns:
        JSON response with created profile
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['discord_user_id', 'username', 'display_name']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Extract social links if provided
        social_links = None
        if 'social_links' in data:
            social_data = data['social_links']
            social_links = SocialLinks(**social_data)
        
        # Create profile
        profile = create_user_profile(
            discord_user_id=data['discord_user_id'],
            username=data['username'],
            display_name=data['display_name'],
            about_me=data.get('about_me', ''),
            playstyle=data.get('playstyle', ''),
            favorite_activities=data.get('favorite_activities', []),
            social_links=social_links,
            profile_visibility=data.get('profile_visibility', 'public')
        )
        
        if not profile:
            return jsonify({
                'success': False,
                'error': 'Failed to create profile'
            }), 500
        
        # Convert to dict for response
        profile_dict = {
            'discord_user_id': profile.discord_user_id,
            'username': profile.username,
            'display_name': profile.display_name,
            'about_me': profile.about_me,
            'playstyle': profile.playstyle,
            'favorite_activities': profile.favorite_activities,
            'social_links': {
                'discord_tag': profile.social_links.discord_tag,
                'twitch_channel': profile.social_links.twitch_channel,
                'steam_profile': profile.social_links.steam_profile,
                'youtube_channel': profile.social_links.youtube_channel,
                'twitter_handle': profile.social_links.twitter_handle,
                'reddit_username': profile.social_links.reddit_username,
                'website': profile.social_links.website,
                'guild_website': profile.social_links.guild_website,
            },
            'badges': profile.badges,
            'profile_visibility': profile.profile_visibility,
            'created_at': profile.created_at,
            'updated_at': profile.updated_at,
            'last_active': profile.last_active,
        }
        
        return jsonify({
            'success': True,
            'profile': profile_dict
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@social_api.route('/profiles/<discord_user_id>', methods=['PUT'])
def api_update_profile(discord_user_id: str):
    """Update a user profile.
    
    Args:
        discord_user_id: Discord user ID
        
    Request Body:
        Any profile fields to update
        
    Returns:
        JSON response with updated profile
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Update profile
        profile = update_user_profile(discord_user_id, **data)
        
        if not profile:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404
        
        # Convert to dict for response
        profile_dict = {
            'discord_user_id': profile.discord_user_id,
            'username': profile.username,
            'display_name': profile.display_name,
            'about_me': profile.about_me,
            'playstyle': profile.playstyle,
            'favorite_activities': profile.favorite_activities,
            'social_links': {
                'discord_tag': profile.social_links.discord_tag,
                'twitch_channel': profile.social_links.twitch_channel,
                'steam_profile': profile.social_links.steam_profile,
                'youtube_channel': profile.social_links.youtube_channel,
                'twitter_handle': profile.social_links.twitter_handle,
                'reddit_username': profile.social_links.reddit_username,
                'website': profile.social_links.website,
                'guild_website': profile.social_links.guild_website,
            },
            'badges': profile.badges,
            'profile_visibility': profile.profile_visibility,
            'created_at': profile.created_at,
            'updated_at': profile.updated_at,
            'last_active': profile.last_active,
        }
        
        return jsonify({
            'success': True,
            'profile': profile_dict
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@social_api.route('/profiles/<discord_user_id>/social-links', methods=['PUT'])
def api_update_social_links(discord_user_id: str):
    """Update social links for a user.
    
    Args:
        discord_user_id: Discord user ID
        
    Request Body:
        Social link fields to update
        
    Returns:
        JSON response with updated profile
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Update social links
        profile = update_social_links(discord_user_id, **data)
        
        if not profile:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404
        
        # Convert to dict for response
        profile_dict = {
            'discord_user_id': profile.discord_user_id,
            'username': profile.username,
            'display_name': profile.display_name,
            'about_me': profile.about_me,
            'playstyle': profile.playstyle,
            'favorite_activities': profile.favorite_activities,
            'social_links': {
                'discord_tag': profile.social_links.discord_tag,
                'twitch_channel': profile.social_links.twitch_channel,
                'steam_profile': profile.social_links.steam_profile,
                'youtube_channel': profile.social_links.youtube_channel,
                'twitter_handle': profile.social_links.twitter_handle,
                'reddit_username': profile.social_links.reddit_username,
                'website': profile.social_links.website,
                'guild_website': profile.social_links.guild_website,
            },
            'badges': profile.badges,
            'profile_visibility': profile.profile_visibility,
            'created_at': profile.created_at,
            'updated_at': profile.updated_at,
            'last_active': profile.last_active,
        }
        
        return jsonify({
            'success': True,
            'profile': profile_dict
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@social_api.route('/profiles/<discord_user_id>/badges', methods=['POST'])
def api_add_badge(discord_user_id: str):
    """Add a badge to a user's profile.
    
    Args:
        discord_user_id: Discord user ID
        
    Request Body:
        badge: Badge to add
        
    Returns:
        JSON response with success status
    """
    try:
        data = request.get_json()
        
        if not data or 'badge' not in data:
            return jsonify({
                'success': False,
                'error': 'Badge field required'
            }), 400
        
        badge = data['badge']
        
        # Validate badge
        valid_badges = [badge.value for badge in BadgeType]
        if badge not in valid_badges:
            return jsonify({
                'success': False,
                'error': f'Invalid badge. Valid badges: {", ".join(valid_badges)}'
            }), 400
        
        # Add badge
        profile_manager = get_profile_manager()
        success = profile_manager.add_badge(discord_user_id, badge)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to add badge'
            }), 500
        
        return jsonify({
            'success': True,
            'message': f'Badge {badge} added successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@social_api.route('/profiles/<discord_user_id>/badges/<badge>', methods=['DELETE'])
def api_remove_badge(discord_user_id: str, badge: str):
    """Remove a badge from a user's profile.
    
    Args:
        discord_user_id: Discord user ID
        badge: Badge to remove
        
    Returns:
        JSON response with success status
    """
    try:
        # Remove badge
        profile_manager = get_profile_manager()
        success = profile_manager.remove_badge(discord_user_id, badge)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to remove badge'
            }), 500
        
        return jsonify({
            'success': True,
            'message': f'Badge {badge} removed successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@social_api.route('/profiles/<discord_user_id>/calculate-badges', methods=['POST'])
def api_calculate_badges(discord_user_id: str):
    """Calculate and add badges based on character and session data.
    
    Args:
        discord_user_id: Discord user ID
        
    Returns:
        JSON response with calculated badges
    """
    try:
        # Get character registry
        registry = get_registry()
        
        # Get character data
        characters = registry.get_characters_by_user(discord_user_id)
        character_data = {
            'characters': [
                {
                    'name': char.name,
                    'profession': char.profession,
                    'level': char.level,
                    'faction': char.faction,
                    'guild': char.guild,
                    'total_playtime_hours': char.total_playtime_hours,
                    'total_sessions': char.total_sessions,
                    'total_xp_gained': char.total_xp_gained,
                    'total_credits_earned': char.total_credits_earned,
                }
                for char in characters
            ]
        }
        
        # Calculate session data
        total_sessions = 0
        total_xp = 0
        total_credits = 0
        total_playtime = 0
        
        for char in characters:
            total_sessions += char.total_sessions
            total_xp += char.total_xp_gained
            total_credits += char.total_credits_earned
            total_playtime += char.total_playtime_hours
        
        session_data = {
            'total_sessions': total_sessions,
            'total_xp_gained': total_xp,
            'total_credits_earned': total_credits,
            'total_playtime_hours': total_playtime,
        }
        
        # Calculate badges
        profile_manager = get_profile_manager()
        earned_badges = profile_manager.calculate_badges(
            discord_user_id, character_data, session_data
        )
        
        # Add earned badges to profile
        added_badges = []
        for badge in earned_badges:
            if profile_manager.add_badge(discord_user_id, badge):
                added_badges.append(badge)
        
        return jsonify({
            'success': True,
            'earned_badges': earned_badges,
            'added_badges': added_badges,
            'character_data': character_data,
            'session_data': session_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@social_api.route('/badges', methods=['GET'])
def api_get_badges():
    """Get all available badge types.
    
    Returns:
        JSON response with badge information
    """
    try:
        badges = []
        for badge_type in BadgeType:
            badges.append({
                'value': badge_type.value,
                'name': badge_type.name,
                'description': badge_type.__doc__ or ''
            })
        
        return jsonify({
            'success': True,
            'badges': badges
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@social_api.route('/health', methods=['GET'])
def api_health():
    """Health check endpoint.
    
    Returns:
        JSON response with health status
    """
    try:
        profile_manager = get_profile_manager()
        profile_count = len(profile_manager.profiles)
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'profile_count': profile_count
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500 