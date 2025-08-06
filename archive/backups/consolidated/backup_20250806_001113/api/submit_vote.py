"""Vote Submission API for SWGDB.

This module provides API endpoints for submitting votes on builds, guides, and profiles
with anti-abuse protection and IP tracking.
"""

from __future__ import annotations

import json
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify, current_app
from flask_cors import CORS

from core.voting_system import (
    get_voting_system,
    ContentType,
    VoteType,
    submit_vote,
    get_vote_summary,
    get_top_content
)


# Initialize Flask Blueprint
vote_api = Flask(__name__)
CORS(vote_api)


def register_vote_api(app: Flask) -> None:
    """Register the vote submission API routes with a Flask app.
    
    Args:
        app: Flask application instance
    """
    app.register_blueprint(vote_api, url_prefix='/api/votes')


def get_client_ip() -> str:
    """Get the client's IP address from the request."""
    # Check for forwarded headers (for proxy setups)
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr


@vote_api.route('/submit', methods=['POST'])
def api_submit_vote():
    """Submit a vote on content.
    
    Request Body:
        content_type: Type of content (build, guide, profile, comment)
        content_id: ID of the content
        vote_type: Type of vote (thumbs_up, thumbs_down, neutral)
        voter_discord_id: Discord ID of the voter (optional)
        reason: Reason for the vote (optional)
        feedback: Additional feedback (optional)
    
    Returns:
        JSON response with vote submission result
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate required fields
        required_fields = ['content_type', 'content_id', 'vote_type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Validate content type
        try:
            content_type = ContentType(data['content_type'])
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Invalid content_type. Valid types: {[ct.value for ct in ContentType]}'
            }), 400
        
        # Validate vote type
        try:
            vote_type = VoteType(data['vote_type'])
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Invalid vote_type. Valid types: {[vt.value for vt in VoteType]}'
            }), 400
        
        # Get client IP
        voter_ip = get_client_ip()
        
        # Extract optional fields
        voter_discord_id = data.get('voter_discord_id')
        reason = data.get('reason', '')
        feedback = data.get('feedback', '')
        
        # Submit vote
        success, message, vote_id = submit_vote(
            content_type=content_type,
            content_id=data['content_id'],
            voter_ip=voter_ip,
            vote_type=vote_type,
            voter_discord_id=voter_discord_id,
            reason=reason,
            feedback=feedback
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'vote_id': vote_id,
                'content_type': content_type.value,
                'content_id': data['content_id'],
                'vote_type': vote_type.value
            })
        else:
            return jsonify({
                'success': False,
                'error': message
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vote_api.route('/summary/<content_type>/<content_id>', methods=['GET'])
def api_get_vote_summary(content_type: str, content_id: str):
    """Get vote summary for content.
    
    Args:
        content_type: Type of content
        content_id: ID of the content
        
    Returns:
        JSON response with vote summary
    """
    try:
        # Validate content type
        try:
            content_type_enum = ContentType(content_type)
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Invalid content_type. Valid types: {[ct.value for ct in ContentType]}'
            }), 400
        
        # Get vote summary
        summary = get_vote_summary(content_type_enum, content_id)
        
        if summary:
            return jsonify({
                'success': True,
                'summary': {
                    'content_type': summary.content_type.value,
                    'content_id': summary.content_id,
                    'total_votes': summary.total_votes,
                    'thumbs_up': summary.thumbs_up,
                    'thumbs_down': summary.thumbs_down,
                    'neutral': summary.neutral,
                    'score': summary.score,
                    'popularity_rank': summary.popularity_rank,
                    'last_updated': summary.last_updated
                }
            })
        else:
            return jsonify({
                'success': True,
                'summary': {
                    'content_type': content_type,
                    'content_id': content_id,
                    'total_votes': 0,
                    'thumbs_up': 0,
                    'thumbs_down': 0,
                    'neutral': 0,
                    'score': 0,
                    'popularity_rank': 0,
                    'last_updated': None
                }
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vote_api.route('/user-vote/<content_type>/<content_id>', methods=['GET'])
def api_get_user_vote(content_type: str, content_id: str):
    """Get the current user's vote on specific content.
    
    Args:
        content_type: Type of content
        content_id: ID of the content
        
    Returns:
        JSON response with user's vote
    """
    try:
        # Validate content type
        try:
            content_type_enum = ContentType(content_type)
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Invalid content_type. Valid types: {[ct.value for ct in ContentType]}'
            }), 400
        
        # Get client IP
        voter_ip = get_client_ip()
        
        # Get user's vote
        voting_system = get_voting_system()
        vote = voting_system.get_user_vote(content_type_enum, content_id, voter_ip)
        
        if vote:
            return jsonify({
                'success': True,
                'vote': {
                    'vote_id': vote.vote_id,
                    'vote_type': vote.vote_type.value,
                    'reason': vote.reason,
                    'feedback': vote.feedback,
                    'created_at': vote.created_at,
                    'updated_at': vote.updated_at
                }
            })
        else:
            return jsonify({
                'success': True,
                'vote': None
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vote_api.route('/top/<content_type>', methods=['GET'])
def api_get_top_content(content_type: str):
    """Get top content by popularity.
    
    Args:
        content_type: Type of content
        
    Query Parameters:
        limit: Maximum number of results (default: 10)
        min_votes: Minimum number of votes required (default: 1)
        
    Returns:
        JSON response with top content
    """
    try:
        # Validate content type
        try:
            content_type_enum = ContentType(content_type)
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Invalid content_type. Valid types: {[ct.value for ct in ContentType]}'
            }), 400
        
        # Get query parameters
        limit = int(request.args.get('limit', 10))
        min_votes = int(request.args.get('min_votes', 1))
        
        # Get top content
        top_content = get_top_content(content_type_enum, limit, min_votes)
        
        # Convert to dict for JSON serialization
        content_data = []
        for summary in top_content:
            content_data.append({
                'content_type': summary.content_type.value,
                'content_id': summary.content_id,
                'total_votes': summary.total_votes,
                'thumbs_up': summary.thumbs_up,
                'thumbs_down': summary.thumbs_down,
                'neutral': summary.neutral,
                'score': summary.score,
                'popularity_rank': summary.popularity_rank,
                'last_updated': summary.last_updated
            })
        
        return jsonify({
            'success': True,
            'content_type': content_type,
            'limit': limit,
            'min_votes': min_votes,
            'top_content': content_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vote_api.route('/statistics', methods=['GET'])
def api_get_vote_statistics():
    """Get overall vote statistics.
    
    Returns:
        JSON response with vote statistics
    """
    try:
        voting_system = get_voting_system()
        stats = voting_system.get_vote_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vote_api.route('/reputation/<discord_id>', methods=['GET'])
def api_get_reputation(discord_id: str):
    """Get reputation score for a Discord user.
    
    Args:
        discord_id: Discord user ID
        
    Returns:
        JSON response with reputation score
    """
    try:
        voting_system = get_voting_system()
        reputation = voting_system.get_reputation_score(discord_id)
        
        if reputation:
            return jsonify({
                'success': True,
                'reputation': {
                    'discord_id': reputation.discord_id,
                    'username': reputation.username,
                    'total_score': reputation.total_score,
                    'positive_votes_given': reputation.positive_votes_given,
                    'negative_votes_given': reputation.negative_votes_given,
                    'positive_votes_received': reputation.positive_votes_received,
                    'negative_votes_received': reputation.negative_votes_received,
                    'reputation_level': reputation.reputation_level,
                    'created_at': reputation.created_at,
                    'updated_at': reputation.updated_at
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Reputation score not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vote_api.route('/delete/<vote_id>', methods=['DELETE'])
def api_delete_vote(vote_id: str):
    """Delete a vote (soft delete).
    
    Args:
        vote_id: ID of the vote to delete
        
    Returns:
        JSON response with deletion result
    """
    try:
        voting_system = get_voting_system()
        success = voting_system.delete_vote(vote_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Vote deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Vote not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vote_api.route('/flag/<vote_id>', methods=['POST'])
def api_flag_vote(vote_id: str):
    """Flag a vote for review.
    
    Args:
        vote_id: ID of the vote to flag
        
    Request Body:
        reason: Reason for flagging the vote
        
    Returns:
        JSON response with flagging result
    """
    try:
        data = request.get_json()
        
        if not data or 'reason' not in data:
            return jsonify({
                'success': False,
                'error': 'Reason required for flagging vote'
            }), 400
        
        voting_system = get_voting_system()
        success = voting_system.flag_vote(vote_id, data['reason'])
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Vote flagged successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Vote not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vote_api.route('/health', methods=['GET'])
def api_health():
    """Health check endpoint.
    
    Returns:
        JSON response with health status
    """
    try:
        voting_system = get_voting_system()
        stats = voting_system.get_vote_statistics()
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'statistics': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500 