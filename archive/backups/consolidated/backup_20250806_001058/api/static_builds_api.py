"""
Static Builds API - Public SWGDB section for showcasing viable builds across all professions.

This module provides API endpoints for:
- Listing builds with filtering
- Viewing individual build details
- Searching builds
- Getting build statistics
- User ratings and reviews
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import Blueprint, jsonify, request, render_template, abort
from pathlib import Path

from core.static_builds_library import (
    get_static_builds_library, 
    StaticBuild, 
    BuildCategory, 
    BuildDifficulty, 
    BuildSpecialization,
    BuildSource
)

# Create blueprint
static_builds_bp = Blueprint('static_builds', __name__, url_prefix='/builds')

# Get the library instance
builds_library = get_static_builds_library()


@static_builds_bp.route('/')
def builds_index():
    """Main builds page - list all builds with filtering."""
    # Get query parameters
    category = request.args.get('category')
    difficulty = request.args.get('difficulty')
    specialization = request.args.get('specialization')
    search = request.args.get('search')
    
    # Convert string parameters to enums
    category_enum = None
    if category:
        try:
            category_enum = BuildCategory(category)
        except ValueError:
            pass
    
    difficulty_enum = None
    if difficulty:
        try:
            difficulty_enum = BuildDifficulty(difficulty)
        except ValueError:
            pass
    
    specialization_enum = None
    if specialization:
        try:
            specialization_enum = BuildSpecialization(specialization)
        except ValueError:
            pass
    
    # Get builds with filtering
    if search:
        builds = builds_library.search_builds(search)
    else:
        builds = builds_library.list_builds(
            category=category_enum,
            difficulty=difficulty_enum,
            specialization=specialization_enum
        )
    
    # Get statistics for sidebar
    stats = builds_library.get_statistics()
    
    # Prepare template data
    template_data = {
        'builds': builds,
        'stats': stats,
        'filters': {
            'category': category,
            'difficulty': difficulty,
            'specialization': specialization,
            'search': search
        },
        'categories': [cat.value for cat in BuildCategory],
        'difficulties': [diff.value for diff in BuildDifficulty],
        'specializations': [spec.value for spec in BuildSpecialization]
    }
    
    return render_template('builds/index.html', **template_data)


@static_builds_bp.route('/<build_id>')
def build_detail(build_id: str):
    """Individual build detail page."""
    build = builds_library.get_build(build_id)
    if not build:
        abort(404, description=f"Build '{build_id}' not found")
    
    return render_template('builds/detail.html', build=build)


@static_builds_bp.route('/api/builds')
def api_list_builds():
    """API endpoint to list builds with filtering."""
    # Get query parameters
    category = request.args.get('category')
    difficulty = request.args.get('difficulty')
    specialization = request.args.get('specialization')
    search = request.args.get('search')
    limit = request.args.get('limit', type=int, default=50)
    offset = request.args.get('offset', type=int, default=0)
    
    # Convert string parameters to enums
    category_enum = None
    if category:
        try:
            category_enum = BuildCategory(category)
        except ValueError:
            pass
    
    difficulty_enum = None
    if difficulty:
        try:
            difficulty_enum = BuildDifficulty(difficulty)
        except ValueError:
            pass
    
    specialization_enum = None
    if specialization:
        try:
            specialization_enum = BuildSpecialization(specialization)
        except ValueError:
            pass
    
    # Get builds with filtering
    if search:
        builds = builds_library.search_builds(search)
    else:
        builds = builds_library.list_builds(
            category=category_enum,
            difficulty=difficulty_enum,
            specialization=specialization_enum
        )
    
    # Apply pagination
    total = len(builds)
    builds = builds[offset:offset + limit]
    
    # Convert builds to JSON-serializable format
    builds_data = []
    for build in builds:
        build_dict = _build_to_api_dict(build)
        builds_data.append(build_dict)
    
    return jsonify({
        'builds': builds_data,
        'pagination': {
            'total': total,
            'limit': limit,
            'offset': offset,
            'has_more': offset + limit < total
        },
        'filters': {
            'category': category,
            'difficulty': difficulty,
            'specialization': specialization,
            'search': search
        }
    })


@static_builds_bp.route('/api/builds/<build_id>')
def api_build_detail(build_id: str):
    """API endpoint to get individual build details."""
    build = builds_library.get_build(build_id)
    if not build:
        return jsonify({'error': f"Build '{build_id}' not found"}), 404
    
    build_dict = _build_to_api_dict(build, include_details=True)
    return jsonify(build_dict)


@static_builds_bp.route('/api/builds/<build_id>/rate', methods=['POST'])
def api_rate_build(build_id: str):
    """API endpoint to rate a build."""
    build = builds_library.get_build(build_id)
    if not build:
        return jsonify({'error': f"Build '{build_id}' not found"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    rating = data.get('rating')
    review = data.get('review', '')
    user_name = data.get('user_name', 'Anonymous')
    
    if not rating or not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
        return jsonify({'error': 'Invalid rating (must be 1-5)'}), 400
    
    # Add the rating (simplified - in practice would need user authentication)
    build.ratings.total_votes += 1
    
    # Update average rating
    current_total = build.ratings.average_rating * (build.ratings.total_votes - 1)
    new_total = current_total + rating
    build.ratings.average_rating = new_total / build.ratings.total_votes
    
    # Update rating breakdown
    rating_key = str(int(rating))
    build.ratings.rating_breakdown[rating_key] = build.ratings.rating_breakdown.get(rating_key, 0) + 1
    
    # Add review if provided
    if review:
        review_data = {
            'user_name': user_name,
            'rating': rating,
            'review': review,
            'timestamp': datetime.now().isoformat()
        }
        build.ratings.user_reviews.append(review_data)
    
    # Save the updated build
    builds_library._save_builds_database()
    
    return jsonify({
        'success': True,
        'new_average': build.ratings.average_rating,
        'total_votes': build.ratings.total_votes
    })


@static_builds_bp.route('/api/stats')
def api_builds_stats():
    """API endpoint to get build library statistics."""
    stats = builds_library.get_statistics()
    return jsonify(stats)


@static_builds_bp.route('/api/search')
def api_search_builds():
    """API endpoint to search builds."""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'builds': [], 'query': query})
    
    builds = builds_library.search_builds(query)
    builds_data = [_build_to_api_dict(build) for build in builds]
    
    return jsonify({
        'builds': builds_data,
        'query': query,
        'total_results': len(builds_data)
    })


def _build_to_api_dict(build: StaticBuild, include_details: bool = False) -> Dict[str, Any]:
    """Convert a StaticBuild to API dictionary format."""
    base_data = {
        'id': build.metadata.id,
        'name': build.metadata.name,
        'description': build.metadata.description,
        'category': build.metadata.category.value,
        'difficulty': build.metadata.difficulty.value,
        'specialization': build.metadata.specialization.value,
        'weapon_type': build.weapon_type,
        'author': build.metadata.author,
        'source': build.metadata.source.value,
        'tags': build.metadata.tags,
        'created_at': build.metadata.created_at,
        'updated_at': build.metadata.updated_at,
        'performance': {
            'pve_rating': build.performance.pve_rating,
            'pvp_rating': build.performance.pvp_rating,
            'solo_rating': build.performance.solo_rating,
            'group_rating': build.performance.group_rating,
            'farming_rating': build.performance.farming_rating
        },
        'ratings': {
            'total_votes': build.ratings.total_votes,
            'average_rating': build.ratings.average_rating
        }
    }
    
    if include_details:
        # Add detailed information
        base_data.update({
            'professions': build.professions,
            'skill_trees': {
                prof: {
                    'skills': tree.skills,
                    'xp_costs': tree.xp_costs,
                    'prerequisites': tree.prerequisites
                }
                for prof, tree in build.skill_trees.items()
            },
            'buff_priority': build.buff_priority,
            'equipment': {
                'weapons': build.equipment.weapons,
                'armor': build.equipment.armor,
                'tapes': build.equipment.tapes,
                'resists': build.equipment.resists,
                'buffs': build.equipment.buffs
            },
            'combat_style': build.combat_style,
            'stat_priority': build.stat_priority,
            'recommended_stats': build.recommended_stats,
            'notes': build.notes,
            'links': build.links,
            'ratings': {
                'total_votes': build.ratings.total_votes,
                'average_rating': build.ratings.average_rating,
                'rating_breakdown': build.ratings.rating_breakdown,
                'user_reviews': build.ratings.user_reviews
            }
        })
    
    return base_data


def register_static_builds_routes(app):
    """Register static builds routes with the Flask app."""
    app.register_blueprint(static_builds_bp)
    
    # Add route for the main builds page
    @app.route('/builds')
    def builds_redirect():
        """Redirect /builds to /builds/ for consistency."""
        return redirect('/builds/') 