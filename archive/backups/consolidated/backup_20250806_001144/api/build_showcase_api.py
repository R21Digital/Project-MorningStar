"""Build Showcase API for public build browsing and admin management.

This module provides API endpoints for the build showcase system, including
public build browsing, admin management, and user submission features.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from flask import Flask, request, jsonify, current_app
from core.build_showcase_manager import (
    build_showcase_manager, 
    BuildCategory, 
    BuildDifficulty, 
    BuildStatus,
    BuildProfile
)


def register_build_showcase_routes(app: Flask) -> None:
    """Register build showcase API routes with Flask app.
    
    Args:
        app: Flask application instance
    """
    
    @app.route('/api/build-showcase')
    def api_build_showcase_list():
        """Get list of all published builds with optional filtering."""
        try:
            # Get query parameters
            category = request.args.get('category')
            difficulty = request.args.get('difficulty')
            profession = request.args.get('profession')
            tags = request.args.get('tags', '').split(',') if request.args.get('tags') else None
            query = request.args.get('q')
            
            # Convert string parameters to enums
            category_enum = BuildCategory(category) if category else None
            difficulty_enum = BuildDifficulty(difficulty) if difficulty else None
            
            # Get builds with filters
            builds = build_showcase_manager.get_all_builds(
                category=category_enum,
                status=BuildStatus.PUBLISHED,
                difficulty=difficulty_enum
            )
            
            # Apply additional filters
            if profession or tags or query:
                builds = build_showcase_manager.search_builds(
                    query=query,
                    profession=profession,
                    tags=tags
                )
                # Filter to only published builds
                builds = [b for b in builds if b.status == BuildStatus.PUBLISHED]
            
            # Convert to JSON-serializable format
            build_list = []
            for build in builds:
                build_data = {
                    'id': build.id,
                    'name': build.name,
                    'description': build.description,
                    'author': build.author,
                    'category': build.category.value,
                    'difficulty': build.difficulty.value,
                    'professions': build.professions,
                    'tags': build.tags,
                    'views': build.views,
                    'likes': build.likes,
                    'rating': build.rating,
                    'created_at': build.created_at.isoformat(),
                    'updated_at': build.updated_at.isoformat(),
                    'url': build_showcase_manager.generate_build_url(build.id)
                }
                build_list.append(build_data)
            
            return jsonify({
                'success': True,
                'builds': build_list,
                'total': len(build_list)
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/build-showcase/<build_id>')
    def api_build_showcase_detail(build_id):
        """Get detailed information about a specific build."""
        try:
            build = build_showcase_manager.get_build(build_id)
            if not build:
                return jsonify({
                    'success': False,
                    'error': 'Build not found'
                }), 404
            
            # Increment view count
            build_showcase_manager.increment_views(build_id)
            
            # Convert to JSON-serializable format
            build_data = {
                'id': build.id,
                'name': build.name,
                'description': build.description,
                'author': build.author,
                'version': build.version,
                'category': build.category.value,
                'difficulty': build.difficulty.value,
                'status': build.status.value,
                'tags': build.tags,
                'professions': build.professions,
                'profession_tree': build.profession_tree,
                'stat_priority': build.stat_priority,
                'recommended_stats': build.recommended_stats,
                'weapons': build.weapons,
                'armor': build.armor,
                'buffs': build.buffs,
                'tapes': build.tapes,
                'rotation': build.rotation,
                'sample_macro': build.sample_macro,
                'combat_notes': build.combat_notes,
                'performance_metrics': build.performance_metrics,
                'views': build.views,
                'likes': build.likes,
                'downloads': build.downloads,
                'rating': build.rating,
                'comments': build.comments,
                'created_at': build.created_at.isoformat(),
                'updated_at': build.updated_at.isoformat(),
                'url': build_showcase_manager.generate_build_url(build.id)
            }
            
            return jsonify({
                'success': True,
                'build': build_data
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/build-showcase/<build_id>/like', methods=['POST'])
    def api_build_showcase_like(build_id):
        """Like a build."""
        try:
            build_showcase_manager.like_build(build_id)
            return jsonify({
                'success': True,
                'message': 'Build liked successfully'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/build-showcase/<build_id>/comment', methods=['POST'])
    def api_build_showcase_comment(build_id):
        """Add a comment to a build."""
        try:
            data = request.get_json()
            commenter = data.get('commenter', 'Anonymous')
            comment = data.get('comment', '')
            
            if not comment:
                return jsonify({
                    'success': False,
                    'error': 'Comment text is required'
                }), 400
            
            build_showcase_manager.add_comment(build_id, commenter, comment)
            
            return jsonify({
                'success': True,
                'message': 'Comment added successfully'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/build-showcase/<build_id>/export', methods=['GET'])
    def api_build_showcase_export(build_id):
        """Export a build as markdown."""
        try:
            markdown_content = build_showcase_manager.export_build_markdown(build_id)
            
            if not markdown_content:
                return jsonify({
                    'success': False,
                    'error': 'Build not found'
                }), 404
            
            return jsonify({
                'success': True,
                'markdown': markdown_content
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/build-showcase/statistics')
    def api_build_showcase_statistics():
        """Get build showcase statistics."""
        try:
            stats = build_showcase_manager.get_build_statistics()
            return jsonify({
                'success': True,
                'statistics': stats
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # Admin routes (require authentication)
    @app.route('/api/admin/build-showcase', methods=['POST'])
    def api_admin_create_build():
        """Create a new build (admin only)."""
        try:
            data = request.get_json()
            
            # Validate build data
            is_valid, errors = build_showcase_manager.validate_build_data(data)
            if not is_valid:
                return jsonify({
                    'success': False,
                    'errors': errors
                }), 400
            
            # Create build
            build_id = build_showcase_manager.create_build(data)
            
            return jsonify({
                'success': True,
                'build_id': build_id,
                'message': 'Build created successfully'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/admin/build-showcase/<build_id>', methods=['PUT'])
    def api_admin_update_build(build_id):
        """Update a build (admin only)."""
        try:
            data = request.get_json()
            
            # Update build
            success = build_showcase_manager.update_build(build_id, data)
            
            if not success:
                return jsonify({
                    'success': False,
                    'error': 'Build not found'
                }), 404
            
            return jsonify({
                'success': True,
                'message': 'Build updated successfully'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/admin/build-showcase/<build_id>', methods=['DELETE'])
    def api_admin_delete_build(build_id):
        """Delete a build (admin only)."""
        try:
            success = build_showcase_manager.delete_build(build_id)
            
            if not success:
                return jsonify({
                    'success': False,
                    'error': 'Build not found'
                }), 404
            
            return jsonify({
                'success': True,
                'message': 'Build deleted successfully'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/admin/build-showcase/all')
    def api_admin_list_all_builds():
        """Get all builds including unpublished ones (admin only)."""
        try:
            builds = build_showcase_manager.get_all_builds()
            
            # Convert to JSON-serializable format
            build_list = []
            for build in builds:
                build_data = {
                    'id': build.id,
                    'name': build.name,
                    'description': build.description,
                    'author': build.author,
                    'category': build.category.value,
                    'difficulty': build.difficulty.value,
                    'status': build.status.value,
                    'tags': build.tags,
                    'professions': build.professions,
                    'views': build.views,
                    'likes': build.likes,
                    'rating': build.rating,
                    'created_at': build.created_at.isoformat(),
                    'updated_at': build.updated_at.isoformat()
                }
                build_list.append(build_data)
            
            return jsonify({
                'success': True,
                'builds': build_list,
                'total': len(build_list)
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # User submission route
    @app.route('/api/build-showcase/submit', methods=['POST'])
    def api_user_submit_build():
        """Submit a build for review (user submission)."""
        try:
            data = request.get_json()
            
            # Set status to draft for user submissions
            data['status'] = 'draft'
            
            # Validate build data
            is_valid, errors = build_showcase_manager.validate_build_data(data)
            if not is_valid:
                return jsonify({
                    'success': False,
                    'errors': errors
                }), 400
            
            # Create build
            build_id = build_showcase_manager.create_build(data)
            
            return jsonify({
                'success': True,
                'build_id': build_id,
                'message': 'Build submitted for review'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500


def get_build_showcase_api() -> Dict[str, Any]:
    """Get build showcase API information.
    
    Returns:
        Dictionary containing API information
    """
    return {
        'name': 'Build Showcase API',
        'version': '1.0.0',
        'description': 'API for managing and browsing character builds and rotations',
        'endpoints': {
            'public': [
                'GET /api/build-showcase',
                'GET /api/build-showcase/<build_id>',
                'POST /api/build-showcase/<build_id>/like',
                'POST /api/build-showcase/<build_id>/comment',
                'GET /api/build-showcase/<build_id>/export',
                'GET /api/build-showcase/statistics',
                'POST /api/build-showcase/submit'
            ],
            'admin': [
                'POST /api/admin/build-showcase',
                'PUT /api/admin/build-showcase/<build_id>',
                'DELETE /api/admin/build-showcase/<build_id>',
                'GET /api/admin/build-showcase/all'
            ]
        }
    } 