"""Public Build Browser API for SWG Armory.

This module provides API endpoints for browsing, searching, and ranking player builds
in the SWG Armory system. It handles build publication, retrieval, and community features.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from flask import Flask, request, jsonify, current_app
import yaml


class BuildVisibility(Enum):
    """Enumeration of build visibility levels."""
    PRIVATE = "private"
    PUBLIC = "public"
    FEATURED = "featured"


class BuildRanking(Enum):
    """Enumeration of build ranking categories."""
    TOP_DPS = "top_dps"
    POPULAR_BUFF_BOT = "popular_buff_bot"
    BEST_TANK = "best_tank"
    MOST_VERSATILE = "most_versatile"
    COMMUNITY_CHOICE = "community_choice"


@dataclass
class PlayerBuild:
    """Represents a player's published build."""
    player_name: str
    character_name: str
    server: str
    faction: str
    gcw_rank: int
    professions: Dict[str, str]
    skills: Dict[str, List[str]]
    stats: Dict[str, int]
    armor: Dict[str, Dict[str, Any]]
    tapes: List[Dict[str, Any]]
    resists: Dict[str, float]
    weapons: List[Dict[str, Any]]
    build_summary: str
    performance_metrics: Dict[str, float]
    tags: List[str]
    visibility: BuildVisibility
    rankings: List[BuildRanking]
    created_at: datetime
    updated_at: datetime
    views: int
    likes: int
    comments: List[Dict[str, Any]]


class PublicBuildBrowser:
    """Manages public build browsing and ranking functionality."""
    
    def __init__(self, builds_dir: str = "data/player_builds"):
        """Initialize the public build browser.
        
        Args:
            builds_dir: Directory containing player build files
        """
        self.builds_dir = Path(builds_dir)
        self.builds_dir.mkdir(parents=True, exist_ok=True)
        self.builds: Dict[str, PlayerBuild] = {}
        self._load_all_builds()
    
    def _load_all_builds(self) -> None:
        """Load all published builds from the builds directory."""
        if not self.builds_dir.exists():
            return
        
        for build_file in self.builds_dir.glob("*.json"):
            try:
                with open(build_file, 'r', encoding='utf-8') as f:
                    build_data = json.load(f)
                
                # Convert datetime strings back to datetime objects
                build_data['created_at'] = datetime.fromisoformat(build_data['created_at'])
                build_data['updated_at'] = datetime.fromisoformat(build_data['updated_at'])
                
                # Convert enums
                build_data['visibility'] = BuildVisibility(build_data['visibility'])
                build_data['rankings'] = [BuildRanking(r) for r in build_data['rankings']]
                
                build = PlayerBuild(**build_data)
                build_id = f"{build.player_name}_{build.character_name}"
                self.builds[build_id] = build
                
            except Exception as e:
                print(f"Error loading build {build_file}: {e}")
    
    def publish_build(self, build_data: Dict[str, Any]) -> str:
        """Publish a new build to the public directory.
        
        Args:
            build_data: Build data to publish
            
        Returns:
            Build ID of the published build
        """
        # Generate build ID
        player_name = build_data['player_name']
        character_name = build_data['character_name']
        build_id = f"{player_name}_{character_name}"
        
        # Create PlayerBuild object
        build = PlayerBuild(
            player_name=player_name,
            character_name=character_name,
            server=build_data['server'],
            faction=build_data['faction'],
            gcw_rank=build_data.get('gcw_rank', 0),
            professions=build_data['professions'],
            skills=build_data['skills'],
            stats=build_data['stats'],
            armor=build_data['armor'],
            tapes=build_data['tapes'],
            resists=build_data['resists'],
            weapons=build_data['weapons'],
            build_summary=build_data['build_summary'],
            performance_metrics=build_data.get('performance_metrics', {}),
            tags=build_data.get('tags', []),
            visibility=BuildVisibility(build_data.get('visibility', 'public')),
            rankings=[],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            views=0,
            likes=0,
            comments=[]
        )
        
        # Save to file
        self._save_build(build)
        
        # Add to memory cache
        self.builds[build_id] = build
        
        return build_id
    
    def _save_build(self, build: PlayerBuild) -> None:
        """Save a build to the file system.
        
        Args:
            build: The build to save
        """
        build_id = f"{build.player_name}_{build.character_name}"
        build_file = self.builds_dir / f"{build_id}.json"
        
        # Convert to JSON-serializable format
        build_dict = asdict(build)
        build_dict['created_at'] = build.created_at.isoformat()
        build_dict['updated_at'] = build.updated_at.isoformat()
        build_dict['visibility'] = build.visibility.value
        build_dict['rankings'] = [r.value for r in build.rankings]
        
        with open(build_file, 'w', encoding='utf-8') as f:
            json.dump(build_dict, f, indent=2, ensure_ascii=False)
    
    def get_build(self, build_id: str) -> Optional[PlayerBuild]:
        """Get a specific build by ID.
        
        Args:
            build_id: The ID of the build to retrieve
            
        Returns:
            PlayerBuild object if found, None otherwise
        """
        return self.builds.get(build_id)
    
    def get_all_builds(self, visibility: Optional[BuildVisibility] = None) -> List[PlayerBuild]:
        """Get all builds, optionally filtered by visibility.
        
        Args:
            visibility: Optional visibility filter
            
        Returns:
            List of matching builds
        """
        builds = list(self.builds.values())
        
        if visibility:
            builds = [b for b in builds if b.visibility == visibility]
        
        return builds
    
    def search_builds(self, 
                     query: Optional[str] = None,
                     profession: Optional[str] = None,
                     damage_type: Optional[str] = None,
                     faction: Optional[str] = None,
                     pve_pvp: Optional[str] = None,
                     min_gcw_rank: Optional[int] = None,
                     tags: Optional[List[str]] = None) -> List[PlayerBuild]:
        """Search builds based on various criteria.
        
        Args:
            query: Text search in build summary and tags
            profession: Filter by profession
            damage_type: Filter by damage type (kinetic, energy, etc.)
            faction: Filter by faction (rebel, imperial, neutral)
            pve_pvp: Filter by PvE or PvP focus
            min_gcw_rank: Minimum GCW rank
            tags: Filter by tags
            
        Returns:
            List of matching builds
        """
        results = []
        
        for build in self.builds.values():
            # Apply filters
            if query and query.lower() not in build.build_summary.lower():
                continue
            
            if profession and profession.lower() not in [p.lower() for p in build.professions.values()]:
                continue
            
            if faction and build.faction.lower() != faction.lower():
                continue
            
            if min_gcw_rank and build.gcw_rank < min_gcw_rank:
                continue
            
            if tags:
                if not any(tag.lower() in [t.lower() for t in build.tags] for tag in tags):
                    continue
            
            # Check damage type in weapons
            if damage_type:
                weapon_damage_types = []
                for weapon in build.weapons:
                    weapon_damage_types.append(weapon.get('damage_type', '').lower())
                if damage_type.lower() not in weapon_damage_types:
                    continue
            
            # Check PvE/PvP focus in tags or performance metrics
            if pve_pvp:
                pve_pvp_lower = pve_pvp.lower()
                if pve_pvp_lower not in [tag.lower() for tag in build.tags]:
                    # Check performance metrics
                    if pve_pvp_lower == 'pve' and 'pve_rating' in build.performance_metrics:
                        if build.performance_metrics['pve_rating'] < 5.0:
                            continue
                    elif pve_pvp_lower == 'pvp' and 'pvp_rating' in build.performance_metrics:
                        if build.performance_metrics['pvp_rating'] < 5.0:
                            continue
            
            results.append(build)
        
        return results
    
    def get_top_builds(self, ranking_type: BuildRanking, limit: int = 10) -> List[PlayerBuild]:
        """Get top builds by ranking type.
        
        Args:
            ranking_type: The type of ranking to use
            limit: Maximum number of builds to return
            
        Returns:
            List of top builds sorted by ranking
        """
        # Filter builds that have this ranking
        ranked_builds = [b for b in self.builds.values() if ranking_type in b.rankings]
        
        # Sort by views and likes (simple ranking algorithm)
        ranked_builds.sort(key=lambda b: (b.views + b.likes * 2), reverse=True)
        
        return ranked_builds[:limit]
    
    def increment_views(self, build_id: str) -> None:
        """Increment the view count for a build.
        
        Args:
            build_id: The ID of the build to update
        """
        build = self.get_build(build_id)
        if build:
            build.views += 1
            build.updated_at = datetime.now()
            self._save_build(build)
    
    def like_build(self, build_id: str) -> None:
        """Like a build.
        
        Args:
            build_id: The ID of the build to like
        """
        build = self.get_build(build_id)
        if build:
            build.likes += 1
            build.updated_at = datetime.now()
            self._save_build(build)
    
    def add_comment(self, build_id: str, commenter: str, comment: str) -> None:
        """Add a comment to a build.
        
        Args:
            build_id: The ID of the build
            commenter: Name of the commenter
            comment: Comment text
        """
        build = self.get_build(build_id)
        if build:
            new_comment = {
                'commenter': commenter,
                'comment': comment,
                'timestamp': datetime.now().isoformat()
            }
            build.comments.append(new_comment)
            build.updated_at = datetime.now()
            self._save_build(build)
    
    def update_build_rankings(self, build_id: str, rankings: List[BuildRanking]) -> None:
        """Update the rankings for a build.
        
        Args:
            build_id: The ID of the build to update
            rankings: New rankings to assign
        """
        build = self.get_build(build_id)
        if build:
            build.rankings = rankings
            build.updated_at = datetime.now()
            self._save_build(build)
    
    def get_build_statistics(self) -> Dict[str, Any]:
        """Get overall statistics about published builds.
        
        Returns:
            Dictionary containing build statistics
        """
        total_builds = len(self.builds)
        public_builds = len([b for b in self.builds.values() if b.visibility == BuildVisibility.PUBLIC])
        featured_builds = len([b for b in self.builds.values() if b.visibility == BuildVisibility.FEATURED])
        
        # Count builds by faction
        faction_counts = {}
        for build in self.builds.values():
            faction = build.faction.lower()
            faction_counts[faction] = faction_counts.get(faction, 0) + 1
        
        # Count builds by profession
        profession_counts = {}
        for build in self.builds.values():
            for profession in build.professions.values():
                profession_counts[profession] = profession_counts.get(profession, 0) + 1
        
        # Most viewed builds
        most_viewed = sorted(self.builds.values(), key=lambda b: b.views, reverse=True)[:5]
        
        # Most liked builds
        most_liked = sorted(self.builds.values(), key=lambda b: b.likes, reverse=True)[:5]
        
        return {
            'total_builds': total_builds,
            'public_builds': public_builds,
            'featured_builds': featured_builds,
            'faction_distribution': faction_counts,
            'profession_distribution': profession_counts,
            'most_viewed': [{'id': f"{b.player_name}_{b.character_name}", 'name': f"{b.player_name} - {b.character_name}", 'views': b.views} for b in most_viewed],
            'most_liked': [{'id': f"{b.player_name}_{b.character_name}", 'name': f"{b.player_name} - {b.character_name}", 'likes': b.likes} for b in most_liked]
        }


# Global instance
build_browser = PublicBuildBrowser()


def get_build_browser() -> PublicBuildBrowser:
    """Get the global build browser instance.
    
    Returns:
        The global PublicBuildBrowser instance
    """
    return build_browser


# Flask route handlers
def register_build_routes(app: Flask) -> None:
    """Register build browser routes with Flask app.
    
    Args:
        app: Flask application instance
    """
    
    @app.route('/api/public-builds')
    def api_public_builds():
        """Get all public builds."""
        try:
            visibility = request.args.get('visibility')
            if visibility:
                visibility_enum = BuildVisibility(visibility)
                builds = build_browser.get_all_builds(visibility=visibility_enum)
            else:
                builds = build_browser.get_all_builds()
            
            # Convert to JSON-serializable format
            builds_data = []
            for build in builds:
                build_dict = asdict(build)
                build_dict['created_at'] = build.created_at.isoformat()
                build_dict['updated_at'] = build.updated_at.isoformat()
                build_dict['visibility'] = build.visibility.value
                build_dict['rankings'] = [r.value for r in build.rankings]
                builds_data.append(build_dict)
            
            return jsonify({
                'success': True,
                'builds': builds_data,
                'total': len(builds_data)
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/public-builds/<build_id>')
    def api_public_build_detail(build_id):
        """Get detailed information about a specific build."""
        try:
            build = build_browser.get_build(build_id)
            if not build:
                return jsonify({
                    'success': False,
                    'error': 'Build not found'
                }), 404
            
            # Increment view count
            build_browser.increment_views(build_id)
            
            # Convert to JSON-serializable format
            build_dict = asdict(build)
            build_dict['created_at'] = build.created_at.isoformat()
            build_dict['updated_at'] = build.updated_at.isoformat()
            build_dict['visibility'] = build.visibility.value
            build_dict['rankings'] = [r.value for r in build.rankings]
            
            return jsonify({
                'success': True,
                'build': build_dict
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/public-builds/search')
    def api_search_builds():
        """Search builds based on criteria."""
        try:
            query = request.args.get('query')
            profession = request.args.get('profession')
            damage_type = request.args.get('damage_type')
            faction = request.args.get('faction')
            pve_pvp = request.args.get('pve_pvp')
            min_gcw_rank = request.args.get('min_gcw_rank', type=int)
            tags = request.args.getlist('tags')
            
            builds = build_browser.search_builds(
                query=query,
                profession=profession,
                damage_type=damage_type,
                faction=faction,
                pve_pvp=pve_pvp,
                min_gcw_rank=min_gcw_rank,
                tags=tags
            )
            
            # Convert to JSON-serializable format
            builds_data = []
            for build in builds:
                build_dict = asdict(build)
                build_dict['created_at'] = build.created_at.isoformat()
                build_dict['updated_at'] = build.updated_at.isoformat()
                build_dict['visibility'] = build.visibility.value
                build_dict['rankings'] = [r.value for r in build.rankings]
                builds_data.append(build_dict)
            
            return jsonify({
                'success': True,
                'builds': builds_data,
                'total': len(builds_data)
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/public-builds/top/<ranking_type>')
    def api_top_builds(ranking_type):
        """Get top builds by ranking type."""
        try:
            limit = request.args.get('limit', 10, type=int)
            
            try:
                ranking_enum = BuildRanking(ranking_type)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': f'Invalid ranking type: {ranking_type}'
                }), 400
            
            builds = build_browser.get_top_builds(ranking_enum, limit=limit)
            
            # Convert to JSON-serializable format
            builds_data = []
            for build in builds:
                build_dict = asdict(build)
                build_dict['created_at'] = build.created_at.isoformat()
                build_dict['updated_at'] = build.updated_at.isoformat()
                build_dict['visibility'] = build.visibility.value
                build_dict['rankings'] = [r.value for r in build.rankings]
                builds_data.append(build_dict)
            
            return jsonify({
                'success': True,
                'builds': builds_data,
                'ranking_type': ranking_type,
                'total': len(builds_data)
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/public-builds/<build_id>/like', methods=['POST'])
    def api_like_build(build_id):
        """Like a build."""
        try:
            build_browser.like_build(build_id)
            return jsonify({
                'success': True,
                'message': 'Build liked successfully'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/public-builds/<build_id>/comment', methods=['POST'])
    def api_add_comment(build_id):
        """Add a comment to a build."""
        try:
            data = request.get_json()
            commenter = data.get('commenter')
            comment = data.get('comment')
            
            if not commenter or not comment:
                return jsonify({
                    'success': False,
                    'error': 'Commenter and comment are required'
                }), 400
            
            build_browser.add_comment(build_id, commenter, comment)
            
            return jsonify({
                'success': True,
                'message': 'Comment added successfully'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/public-builds/publish', methods=['POST'])
    def api_publish_build():
        """Publish a new build."""
        try:
            data = request.get_json()
            
            # Validate required fields
            required_fields = ['player_name', 'character_name', 'server', 'faction', 
                             'professions', 'skills', 'stats', 'armor', 'tapes', 
                             'resists', 'weapons', 'build_summary']
            
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }), 400
            
            build_id = build_browser.publish_build(data)
            
            return jsonify({
                'success': True,
                'build_id': build_id,
                'message': 'Build published successfully'
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/public-builds/statistics')
    def api_build_statistics():
        """Get build statistics."""
        try:
            stats = build_browser.get_build_statistics()
            return jsonify({
                'success': True,
                'statistics': stats
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500 