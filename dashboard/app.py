from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import glob

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash

# Import core modules with fallbacks
try:
    from core.session_tracker import load_session
    from core.session_report_dashboard import session_dashboard
    from core.ms11_license_manager import ms11_license_manager
    from core import progress_tracker
    from core.build_manager import BuildManager
    from core.profile_loader import SESSION_STATE
    from profiles.special_goals import get_dashboard_data as get_special_goals_data
    from core.guide_manager import GuideManager, GuideMetadata
    from core.player_guild_tracker import PlayerGuildTracker
    from core.player_profile_manager import profile_manager
    from core.multi_character_profile_manager import multi_character_manager
    from core.chat_session_manager import chat_session_manager
    from core.blog_engine import blog_manager
    from core.macro_safety import macro_safety_manager
    from core.heroic_support import heroic_support
    from core.vendor_price_scanner import vendor_price_scanner
    from core.vendor_price_alerts import vendor_price_alerts
    from core.steam_discord_bridge import identity_bridge
    from core.quest_heatmap_tracker import quest_heatmap_tracker
    from core.tools_manager import tools_manager, submit_player_tool, get_player_tools, get_tool_by_id, increment_tool_views, get_tool_content, get_tools_stats
    CORE_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] Core modules not available: {e}")
    print("[INFO] Dashboard running in limited mode")
    CORE_MODULES_AVAILABLE = False
    
    # Create fallback implementations
    def load_session(*args, **kwargs):
        return {"status": "unavailable"}
    
    def session_dashboard(*args, **kwargs):
        return {"message": "Session dashboard unavailable"}
        
    class BuildManager:
        def __init__(self, *args, **kwargs):
            pass
        def get_builds(self):
            return []
    
    SESSION_STATE = {"demo": True}
    
    def get_special_goals_data():
        return {"goals": [], "status": "unavailable"}
        
    # Add other fallback implementations as needed
    class GuideManager:
        def get_guides(self):
            return []
    
    class PlayerGuildTracker:
        def __init__(self, *args, **kwargs):
            pass
        def get_guilds(self):
            return []
    
    ms11_license_manager = None
    progress_tracker = None
    profile_manager = None
    multi_character_manager = None
    chat_session_manager = None
    blog_manager = None
    macro_safety_manager = None
    heroic_support = None
    vendor_price_scanner = None
    vendor_price_alerts = None
    identity_bridge = None
    quest_heatmap_tracker = None
    tools_manager = None
    
    # Additional fallback implementations
    def analyze_character_build(*args, **kwargs):
        return {"analysis": "unavailable"}
    
    def get_profession_recommendations(*args, **kwargs):
        return []
    
    def get_equipment_recommendations(*args, **kwargs):
        return []
    
    def cross_character_dashboard(*args, **kwargs):
        return {"message": "Cross-character dashboard unavailable"}
    
    def submit_player_tool(*args, **kwargs):
        return {"status": "unavailable"}
    
    def get_player_tools(*args, **kwargs):
        return []
    
    def get_tool_by_id(*args, **kwargs):
        return None
    
    def increment_tool_views(*args, **kwargs):
        pass
    
    def get_tool_content(*args, **kwargs):
        return ""
    
    def get_tools_stats(*args, **kwargs):
        return {"stats": "unavailable"}

# Additional module imports with fallbacks
try:
    from core.build_optimizer import analyze_character_build, get_profession_recommendations, get_equipment_recommendations
    from core.cross_character_session_dashboard import cross_character_dashboard
    from core.mods_hub_manager import mods_hub_manager, ModCategory, ModType, ModStatus
    from core.quest_tracker import quest_tracker, QuestCategory, QuestDifficulty, QuestStatus, Planet, RewardType
    from core.build_loader import get_build_loader
    from optimizer.gear_advisor import get_gear_advisor, OptimizationType
    EXTENDED_MODULES_AVAILABLE = True
except ImportError as e:
    EXTENDED_MODULES_AVAILABLE = False
    # Use fallback implementations defined above
# Final module imports with fallbacks
try:
    from api.public_build_browser import register_build_routes, get_build_browser
    from api.build_showcase_api import register_build_showcase_routes
    from api.player_encounter_api import register_player_encounter_routes
    from tracking.item_scanner import get_item_scanner
    from core.vendor_history_manager import get_vendor_history_manager, VendorHistoryFilter
    API_MODULES_AVAILABLE = True
except ImportError as e:
    API_MODULES_AVAILABLE = False
    
    # API fallback implementations
    def register_build_routes(app):
        @app.route('/builds')
        def builds():
            return jsonify({"message": "Build browser unavailable"})
    
    def get_build_browser():
        return None
    
    def register_build_showcase_routes(app):
        @app.route('/showcase')
        def showcase():
            return jsonify({"message": "Showcase unavailable"})
    
    def register_player_encounter_routes(app):
        pass
    
    def get_item_scanner():
        return None
    
    def get_vendor_history_manager():
        return None
    
    class VendorHistoryFilter:
        pass

# Runtime session data placeholder
session_state: dict = {}

# Directory containing build definitions
BUILD_DIR = Path(__file__).resolve().parents[1] / "profiles" / "builds"

# Potential locations for session logs
LOG_DIRS = [Path("logs"), Path("logs/sessions"), Path("data") / "session_logs", Path("session_logs"), Path("dashboard") / "sessions"]

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for session management

# Initialize guide manager
guide_manager = GuideManager()

# Initialize player/guild tracker
player_guild_tracker = PlayerGuildTracker()

# Register public build browser routes
register_build_routes(app)

# Register build showcase routes
register_build_showcase_routes(app)

# Register player encounter routes
register_player_encounter_routes(app)


def _latest_session_log() -> Optional[Path]:
    """Return the most recently modified session log file if one exists."""
    candidates = []
    for directory in LOG_DIRS:
        if directory.exists():
            candidates.extend(directory.glob("session_*.json"))
            # include plain JSON names from session_logger
            candidates.extend(directory.glob("*.json"))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def _load_session_logs() -> List[Dict[str, Any]]:
    """Load all available session logs from various directories."""
    sessions = []
    
    for directory in LOG_DIRS:
        if directory.exists():
            # Find all JSON session files
            json_files = list(directory.glob("session_*.json"))
            json_files.extend(directory.glob("*.json"))
            
            for file_path in json_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    # Add file metadata
                    session_data['_file_path'] = str(file_path)
                    session_data['_file_name'] = file_path.name
                    session_data['_file_size'] = file_path.stat().st_size
                    session_data['_modified_time'] = file_path.stat().st_mtime
                    
                    sessions.append(session_data)
                except Exception as e:
                    print(f"Error loading session log {file_path}: {e}")
    
    # Sort by modification time (newest first)
    sessions.sort(key=lambda x: x.get('_modified_time', 0), reverse=True)
    return sessions


def _filter_sessions(sessions: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Filter sessions based on provided criteria."""
    filtered = sessions
    
    # Date range filter
    if filters.get('date_from'):
        try:
            date_from = datetime.fromisoformat(filters['date_from'].replace('Z', '+00:00'))
            filtered = [s for s in filtered if s.get('start_time') and 
                       datetime.fromisoformat(s['start_time'].replace('Z', '+00:00')) >= date_from]
        except:
            pass
    
    if filters.get('date_to'):
        try:
            date_to = datetime.fromisoformat(filters['date_to'].replace('Z', '+00:00'))
            filtered = [s for s in filtered if s.get('start_time') and 
                       datetime.fromisoformat(s['start_time'].replace('Z', '+00:00')) <= date_to]
        except:
            pass
    
    # Character filter
    if filters.get('character'):
        character_lower = filters['character'].lower()
        filtered = [s for s in filtered if s.get('character_name', '').lower().find(character_lower) != -1]
    
    # Location filter
    if filters.get('location'):
        location_lower = filters['location'].lower()
        filtered = [s for s in filtered if s.get('location', '').lower().find(location_lower) != -1]
    
    # Event type filters
    if filters.get('has_deaths'):
        filtered = [s for s in filtered if s.get('total_deaths', 0) > 0]
    
    if filters.get('has_quests'):
        filtered = [s for s in filtered if s.get('total_quests_completed', 0) > 0]
    
    if filters.get('has_whispers'):
        # Look for whisper events in the events array
        filtered = [s for s in filtered if any(
            event.get('event_type') == 'whisper' 
            for event in s.get('events', [])
        )]
    
    return filtered


def _calculate_session_stats(session: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate additional statistics for a session."""
    stats = {
        'duration_minutes': 0,
        'xp_per_minute': 0,
        'credits_per_minute': 0,
        'quests_per_hour': 0,
        'combat_efficiency': 0,
    }
    
    # Calculate duration
    if session.get('start_time') and session.get('end_time'):
        try:
            start = datetime.fromisoformat(session['start_time'].replace('Z', '+00:00'))
            end = datetime.fromisoformat(session['end_time'].replace('Z', '+00:00'))
            duration = (end - start).total_seconds() / 60
            stats['duration_minutes'] = round(duration, 2)
        except:
            pass
    
    # Calculate rates
    if stats['duration_minutes'] > 0:
        xp_gained = session.get('total_xp_gained', 0)
        credits_gained = session.get('total_credits_gained', 0)
        quests_completed = session.get('total_quests_completed', 0)
        
        stats['xp_per_minute'] = round(xp_gained / stats['duration_minutes'], 2)
        stats['credits_per_minute'] = round(credits_gained / stats['duration_minutes'], 2)
        stats['quests_per_hour'] = round((quests_completed / stats['duration_minutes']) * 60, 2)
    
    # Calculate combat efficiency
    combat_actions = session.get('total_combat_actions', 0)
    deaths = session.get('total_deaths', 0)
    if combat_actions > 0:
        stats['combat_efficiency'] = round((combat_actions - deaths) / combat_actions * 100, 1)
    
    return stats


def _get_progress(build_name: str | None) -> dict:
    """Return progress details for ``build_name`` using the tracker."""
    progress_data = progress_tracker.load_session(SESSION_STATE)
    completed = progress_data.get("completed_skills", [])

    info = {"completed_skills": completed, "next_skill": None, "percent": 0}

    if not build_name:
        return info

    try:
        bm = BuildManager(build_name)
    except Exception:
        return info

    total = len(bm.skills)
    done = bm.get_completed_skills()
    next_skill = bm.get_next_skill(done)

    percent = (len(done) / total * 100) if total else 0

    info.update(
        {
            "completed_skills": done,
            "next_skill": next_skill,
            "percent": round(percent, 2),
            "total_skills": total,
        }
    )
    return info


@app.route("/")
def index():
    """Display basic session details."""
    session = load_session()
    build = session.get("current_build", "Unknown")
    progress = len(session.get("skills_completed", []))
    return render_template("index.html", build=build, progress=progress)


@app.route("/builds")
def list_builds():
    builds = []
    if BUILD_DIR.exists():
        builds.extend(p.stem for p in BUILD_DIR.glob("*.json"))
        builds.extend(p.stem for p in BUILD_DIR.glob("*.txt"))
    return render_template("builds.html", builds=sorted(set(builds)))


@app.route("/community-builds")
def community_builds():
    """Display the community builds page with the React component."""
    return render_template("community_builds.html")

@app.route("/build-showcase")
def build_showcase():
    """Display the build showcase page."""
    return render_template("build_showcase.html")

@app.route("/build-showcase/<build_id>")
def build_showcase_detail(build_id):
    """Display individual build detail page."""
    return render_template("build_showcase_detail.html")

@app.route("/build-showcase-admin")
def build_showcase_admin():
    """Display the build showcase admin page."""
    return render_template("build_showcase_admin.html")


@app.route("/player-encounters")
def player_encounters():
    """Display the player encounters page."""
    return render_template("player_encounters.html")


@app.route("/api/builds")
def api_builds():
    """API endpoint for community builds data."""
    try:
        build_loader = get_build_loader()
        all_builds = build_loader.get_all_builds()
        
        builds_summary = []
        for build_id, build in all_builds.items():
            summary = build_loader.get_build_summary(build_id)
            builds_summary.append(summary)
        
        return jsonify({
            'builds': builds_summary,
            'total_count': len(builds_summary)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/api/builds/<build_id>")
def api_build_detail(build_id):
    """API endpoint for individual build details."""
    try:
        build_loader = get_build_loader()
        build = build_loader.get_build(build_id)
        
        if not build:
            return jsonify({'error': 'Build not found'}), 404
        
        # Get detailed build information
        build_data = {
            'id': build_id,
            'name': build.name,
            'description': build.description,
            'category': build.category.value,
            'specialization': build.specialization.value,
            'difficulty': build.difficulty.value,
            'professions': list(build.professions.values()),
            'skills': build.skills,
            'equipment': build.equipment,
            'performance': build.performance,
            'combat': build.combat,
            'cooldowns': build.cooldowns,
            'emergency_abilities': build.emergency_abilities,
            'notes': build.notes
        }
        
        return jsonify(build_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/api/builds/<build_id>/select", methods=['POST'])
def api_select_build(build_id):
    """API endpoint to select and apply a build."""
    try:
        build_loader = get_build_loader()
        build = build_loader.get_build(build_id)
        
        if not build:
            return jsonify({'error': 'Build not found'}), 404
        
        # Validate the build
        is_valid, errors = build_loader.validate_build(build_id)
        if not is_valid:
            return jsonify({'error': 'Build validation failed', 'errors': errors}), 400
        
        # Export build to JSON for compatibility with existing systems
        output_path = f"profiles/builds/{build_id}.json"
        success = build_loader.export_build_to_json(build_id, output_path)
        
        if not success:
            return jsonify({'error': 'Failed to export build'}), 500
        
        # Update session state with selected build
        session_state['selected_build'] = build_id
        session_state['build_data'] = {
            'name': build.name,
            'description': build.description,
            'category': build.category.value,
            'specialization': build.specialization.value,
            'difficulty': build.difficulty.value
        }
        
        return jsonify({
            'success': True,
            'message': f'Build "{build.name}" selected successfully',
            'build_id': build_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/api/builds/search")
def api_search_builds_main():
    """API endpoint to search builds with filters."""
    try:
        build_loader = get_build_loader()
        
        # Get filter parameters
        category = request.args.get('category')
        specialization = request.args.get('specialization')
        difficulty = request.args.get('difficulty')
        min_rating = request.args.get('min_rating', type=float)
        
        # Apply filters
        from core.build_loader import BuildCategory, BuildSpecialization, BuildDifficulty
        
        category_enum = None
        if category and category != 'all':
            category_enum = BuildCategory(category)
        
        specialization_enum = None
        if specialization and specialization != 'all':
            specialization_enum = BuildSpecialization(specialization)
        
        difficulty_enum = None
        if difficulty and difficulty != 'all':
            difficulty_enum = BuildDifficulty(difficulty)
        
        # Search builds
        filtered_builds = build_loader.search_builds(
            category=category_enum,
            specialization=specialization_enum,
            difficulty=difficulty_enum,
            min_rating=min_rating
        )
        
        # Convert to summary format
        builds_summary = []
        for build_id, build in filtered_builds.items():
            summary = build_loader.get_build_summary(build_id)
            builds_summary.append(summary)
        
        return jsonify({
            'builds': builds_summary,
            'total_count': len(builds_summary),
            'filters': {
                'category': category,
                'specialization': specialization,
                'difficulty': difficulty,
                'min_rating': min_rating
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/api/builds/top-performing")
def api_top_performing_builds():
    """API endpoint to get top performing builds by category."""
    try:
        build_loader = get_build_loader()
        performance_type = request.args.get('type', 'pve_rating')
        limit = request.args.get('limit', 5, type=int)
        
        top_builds = build_loader.get_top_performing_builds(performance_type, limit)
        
        builds_data = []
        for build_id, rating in top_builds:
            build = build_loader.get_build(build_id)
            if build:
                builds_data.append({
                    'id': build_id,
                    'name': build.name,
                    'rating': rating,
                    'category': build.category.value,
                    'specialization': build.specialization.value
                })
        
        return jsonify({
            'builds': builds_data,
            'performance_type': performance_type,
            'limit': limit
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/status")
def status():
    log_path = _latest_session_log()
    data = None
    if log_path and log_path.exists():
        try:
            with open(log_path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
        except Exception:
            data = None
    profile = session_state.get("profile", {})
    build_name = profile.get("skill_build")
    progress = _get_progress(build_name)
    
    # Get special goals data
    special_goals_data = get_special_goals_data()
    
    return render_template(
        "status.html", 
        log=data, 
        build=build_name, 
        progress=progress,
        special_goals=special_goals_data
    )


@app.route("/special-goals")
def special_goals():
    """Display special goals dashboard."""
    special_goals_data = get_special_goals_data()
    return render_template("special_goals.html", special_goals=special_goals_data)


@app.route("/sessions")
def sessions():
    """Display enhanced session reports."""
    # Get filter parameters
    filters = {
        'date_from': request.args.get('date_from'),
        'date_to': request.args.get('date_to'),
        'mode': request.args.get('mode'),
        'min_duration': request.args.get('min_duration', type=float),
        'max_duration': request.args.get('max_duration', type=float),
        'min_credits': request.args.get('min_credits', type=int),
        'min_xp': request.args.get('min_xp', type=int),
    }
    
    # Load sessions using the new dashboard system
    all_sessions = session_dashboard.load_all_sessions()
    filtered_sessions = session_dashboard.filter_sessions(all_sessions, filters)
    
    # Calculate aggregate stats
    aggregate_stats = session_dashboard.calculate_aggregate_stats(filtered_sessions)
    
    # Get recent sessions for quick stats
    recent_sessions = session_dashboard.get_recent_sessions(hours=24)
    recent_stats = session_dashboard.calculate_aggregate_stats(recent_sessions)
    
    return render_template("sessions.html", 
                         sessions=filtered_sessions, 
                         filters=filters,
                         aggregate_stats=aggregate_stats,
                         recent_stats=recent_stats)


@app.route("/api/sessions")
def api_sessions():
    """API endpoint for session data."""
    filters = {
        'date_from': request.args.get('date_from'),
        'date_to': request.args.get('date_to'),
        'mode': request.args.get('mode'),
        'min_duration': request.args.get('min_duration', type=float),
        'max_duration': request.args.get('max_duration', type=float),
        'min_credits': request.args.get('min_credits', type=int),
        'min_xp': request.args.get('min_xp', type=int),
    }
    
    all_sessions = session_dashboard.load_all_sessions()
    filtered_sessions = session_dashboard.filter_sessions(all_sessions, filters)
    aggregate_stats = session_dashboard.calculate_aggregate_stats(filtered_sessions)
    
    return jsonify({
        'sessions': filtered_sessions,
        'total_count': len(filtered_sessions),
        'filters': filters,
        'aggregate_stats': aggregate_stats
    })


@app.route("/api/session/<session_id>")
def api_session_detail(session_id):
    """API endpoint for detailed session information."""
    session_data = session_dashboard.get_session_details(session_id)
    
    if not session_data:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify(session_data)


@app.route("/api/session/<session_id>/export")
def api_session_export(session_id):
    """API endpoint for exporting session data."""
    format_type = request.args.get('format', 'json')
    export_data = session_dashboard.export_session_report(session_id, format_type)
    
    if not export_data:
        return jsonify({'error': 'Session not found or export failed'}), 404
    
    return jsonify({
        'session_id': session_id,
        'format': format_type,
        'data': export_data
    })


@app.route("/api/session/<session_id>/discord-summary")
def api_session_discord_summary(session_id):
    """API endpoint for Discord-friendly session summary."""
    summary = session_dashboard.generate_discord_summary(session_id)
    
    if not summary:
        return jsonify({'error': 'Session not found'}), 404
    
    return jsonify({
        'session_id': session_id,
        'summary': summary
    })


@app.route("/api/sessions/recent")
def api_recent_sessions():
    """API endpoint for recent sessions."""
    hours = request.args.get('hours', 24, type=int)
    sessions = session_dashboard.get_recent_sessions(hours=hours)
    stats = session_dashboard.calculate_aggregate_stats(sessions)
    
    return jsonify({
        'sessions': sessions,
        'stats': stats,
        'hours': hours
    })


@app.route("/api/sessions/stats")
def api_sessions_stats():
    """API endpoint for aggregate session statistics."""
    filters = {
        'date_from': request.args.get('date_from'),
        'date_to': request.args.get('date_to'),
        'mode': request.args.get('mode'),
    }
    
    all_sessions = session_dashboard.load_all_sessions()
    filtered_sessions = session_dashboard.filter_sessions(all_sessions, filters)
    stats = session_dashboard.calculate_aggregate_stats(filtered_sessions)
    
    return jsonify(stats)


# Cross-Character Session Dashboard Routes
@app.route("/my-dashboard/sessions")
def my_dashboard_sessions():
    """Cross-character session dashboard page."""
    # Check if user is authenticated via Discord
    discord_id = session.get('discord_id')
    if not discord_id:
        flash("Please link your Discord account to access cross-character session data", "warning")
        return redirect(url_for('identity_bridge_page'))
    
    # Check if session sync is enabled
    if not cross_character_dashboard.check_session_sync_enabled(discord_id):
        flash("Please enable session sync to view cross-character data", "warning")
        return redirect(url_for('identity_bridge_page'))
    
    # Get cross-character summary
    summary = cross_character_dashboard.get_cross_character_summary(discord_id)
    if not summary:
        flash("No session data available or authentication failed", "error")
        return redirect(url_for('sessions'))
    
    return render_template("my_dashboard_sessions.html", summary=summary)


@app.route("/api/my-dashboard/sessions")
def api_my_dashboard_sessions():
    """API endpoint for cross-character session data."""
    discord_id = session.get('discord_id')
    if not discord_id:
        return jsonify({'error': 'Discord authentication required'}), 401
    
    if not cross_character_dashboard.check_session_sync_enabled(discord_id):
        return jsonify({'error': 'Session sync not enabled'}), 403
    
    summary = cross_character_dashboard.get_cross_character_summary(discord_id)
    if not summary:
        return jsonify({'error': 'No data available'}), 404
    
    return jsonify(summary.__dict__)


@app.route("/api/my-dashboard/sessions/export")
def api_my_dashboard_sessions_export():
    """API endpoint for exporting cross-character session data."""
    discord_id = session.get('discord_id')
    if not discord_id:
        return jsonify({'error': 'Discord authentication required'}), 401
    
    format_type = request.args.get('format', 'json')
    export_data = cross_character_dashboard.export_summary(discord_id, format_type)
    
    if not export_data:
        return jsonify({'error': 'Export failed or no data available'}), 404
    
    return jsonify({
        'discord_id': discord_id,
        'format': format_type,
        'data': export_data
    })


@app.route("/api/my-dashboard/sessions/sync/enable", methods=['POST'])
def api_enable_session_sync():
    """API endpoint to enable session sync."""
    discord_id = session.get('discord_id')
    if not discord_id:
        return jsonify({'error': 'Discord authentication required'}), 401
    
    success = cross_character_dashboard.enable_session_sync(discord_id)
    if success:
        return jsonify({'message': 'Session sync enabled successfully'})
    else:
        return jsonify({'error': 'Failed to enable session sync'}), 500


@app.route("/api/my-dashboard/sessions/sync/disable", methods=['POST'])
def api_disable_session_sync():
    """API endpoint to disable session sync."""
    discord_id = session.get('discord_id')
    if not discord_id:
        return jsonify({'error': 'Discord authentication required'}), 401
    
    success = cross_character_dashboard.disable_session_sync(discord_id)
    if success:
        return jsonify({'message': 'Session sync disabled successfully'})
    else:
        return jsonify({'error': 'Failed to disable session sync'}), 500


@app.route("/api/my-dashboard/sessions/sync/status")
def api_session_sync_status():
    """API endpoint to check session sync status."""
    discord_id = session.get('discord_id')
    if not discord_id:
        return jsonify({'error': 'Discord authentication required'}), 401
    
    auth_status = cross_character_dashboard.check_discord_auth(discord_id)
    sync_enabled = cross_character_dashboard.check_session_sync_enabled(discord_id)
    
    return jsonify({
        'discord_id': discord_id,
        'authenticated': auth_status,
        'sync_enabled': sync_enabled
    })


# Guide System Routes
@app.route("/guides")
def guides():
    """Display guides list."""
    status_filter = request.args.get('status', 'published')
    category_filter = request.args.get('category')
    search_query = request.args.get('search')
    
    if search_query:
        guides_list = guide_manager.search_guides(search_query)
    else:
        guides_list = guide_manager.list_guides(
            status=status_filter,
            category=category_filter
        )
    
    categories = guide_manager.get_categories()
    stats = guide_manager.get_stats()
    
    return render_template("guides.html", 
                         guides=guides_list,
                         categories=categories,
                         stats=stats,
                         current_status=status_filter,
                         current_category=category_filter,
                         search_query=search_query)


@app.route("/guides/<guide_id>")
def guide_detail(guide_id):
    """Display guide detail page."""
    guide = guide_manager.get_guide(guide_id)
    if not guide:
        flash("Guide not found", "error")
        return redirect(url_for('guides'))
    
    return render_template("guide_detail.html", guide=guide)


@app.route("/guides/new", methods=['GET', 'POST'])
def create_guide():
    """Create a new guide."""
    if request.method == 'POST':
        # Check admin authentication
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not guide_manager.authenticate_admin(username, password):
            flash("Invalid admin credentials", "error")
            return render_template("guide_editor.html", 
                                guide=None, 
                                categories=guide_manager.get_categories(),
                                error="Invalid credentials")
        
        # Create guide metadata
        metadata = GuideMetadata(
            title=request.form.get('title'),
            description=request.form.get('description'),
            keywords=request.form.get('keywords', '').split(','),
            author=username,
            created_date='',  # Will be set by guide manager
            modified_date='',  # Will be set by guide manager
            category=request.form.get('category'),
            tags=request.form.get('tags', '').split(','),
            status='draft',
            difficulty=request.form.get('difficulty', 'beginner'),
            estimated_read_time=int(request.form.get('estimated_read_time', 5))
        )
        
        content = request.form.get('content', '')
        
        # Create guide
        guide_id = guide_manager.create_guide(metadata, content, username)
        
        flash(f"Guide '{metadata.title}' created successfully", "success")
        return redirect(url_for('guide_detail', guide_id=guide_id))
    
    return render_template("guide_editor.html", 
                         guide=None, 
                         categories=guide_manager.get_categories())


@app.route("/guides/<guide_id>/edit", methods=['GET', 'POST'])
def edit_guide(guide_id):
    """Edit an existing guide."""
    guide = guide_manager.get_guide(guide_id)
    if not guide:
        flash("Guide not found", "error")
        return redirect(url_for('guides'))
    
    if request.method == 'POST':
        # Check admin authentication
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not guide_manager.authenticate_admin(username, password):
            flash("Invalid admin credentials", "error")
            return render_template("guide_editor.html", 
                                guide=guide, 
                                categories=guide_manager.get_categories(),
                                error="Invalid credentials")
        
        # Update guide metadata
        metadata = GuideMetadata(
            title=request.form.get('title'),
            description=request.form.get('description'),
            keywords=request.form.get('keywords', '').split(','),
            author=username,
            created_date=guide.metadata.created_date,
            modified_date='',  # Will be set by guide manager
            category=request.form.get('category'),
            tags=request.form.get('tags', '').split(','),
            status=request.form.get('status', guide.metadata.status),
            difficulty=request.form.get('difficulty', guide.metadata.difficulty),
            estimated_read_time=int(request.form.get('estimated_read_time', guide.metadata.estimated_read_time))
        )
        
        content = request.form.get('content', '')
        
        # Update guide
        if guide_manager.update_guide(guide_id, metadata, content, username):
            flash(f"Guide '{metadata.title}' updated successfully", "success")
            return redirect(url_for('guide_detail', guide_id=guide_id))
        else:
            flash("Failed to update guide", "error")
    
    return render_template("guide_editor.html", 
                         guide=guide, 
                         categories=guide_manager.get_categories())


@app.route("/guides/<guide_id>/delete", methods=['POST'])
def delete_guide(guide_id):
    """Delete a guide."""
    # Check admin authentication
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not guide_manager.authenticate_admin(username, password):
        return jsonify({'error': 'Invalid admin credentials'}), 401
    
    if guide_manager.delete_guide(guide_id):
        return jsonify({'success': True, 'message': 'Guide deleted successfully'})
    else:
        return jsonify({'error': 'Failed to delete guide'}), 404


@app.route("/guides/<guide_id>/publish", methods=['POST'])
def publish_guide(guide_id):
    """Publish a draft guide."""
    # Check admin authentication
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not guide_manager.authenticate_admin(username, password):
        return jsonify({'error': 'Invalid admin credentials'}), 401
    
    if guide_manager.publish_guide(guide_id):
        return jsonify({'success': True, 'message': 'Guide published successfully'})
    else:
        return jsonify({'error': 'Failed to publish guide'}), 400


@app.route("/api/guides")
def api_guides():
    """API endpoint for guide data."""
    status_filter = request.args.get('status')
    category_filter = request.args.get('category')
    search_query = request.args.get('search')
    
    if search_query:
        guides_list = guide_manager.search_guides(search_query)
    else:
        guides_list = guide_manager.list_guides(
            status=status_filter,
            category=category_filter
        )
    
    return jsonify({
        'guides': guides_list,
        'total_count': len(guides_list),
        'filters': {
            'status': status_filter,
            'category': category_filter,
            'search': search_query
        }
    })


@app.route("/api/guides/<guide_id>")
def api_guide_detail(guide_id):
    """API endpoint for detailed guide information."""
    guide = guide_manager.get_guide(guide_id)
    if not guide:
        return jsonify({'error': 'Guide not found'}), 404
    
    return jsonify(asdict(guide))


# Player and Guild Tracker Routes

@app.route("/players")
def players():
    """Player lookup and search page."""
    return render_template("players.html")


@app.route("/players/<player_name>")
def player_detail(player_name):
    """Player detail page."""
    try:
        player = player_guild_tracker.get_player(player_name)
        if player:
            return render_template("player_detail.html", player=player)
        else:
            return render_template("player_not_found.html", player_name=player_name)
    except Exception as e:
        return render_template("error.html", error=str(e))


@app.route("/guilds")
def guilds():
    """Guild lookup and search page."""
    return render_template("guilds.html")


@app.route("/guilds/<guild_tag>")
def guild_detail(guild_tag):
    """Guild detail page."""
    try:
        guild = player_guild_tracker.get_guild(guild_tag)
        if guild:
            return render_template("guild_detail.html", guild=guild)
        else:
            return render_template("guild_not_found.html", guild_tag=guild_tag)
    except Exception as e:
        return render_template("error.html", error=str(e))


@app.route("/api/players")
def api_players():
    """API endpoint for player search."""
    try:
        query = request.args.get('q', '')
        profession = request.args.get('profession', '')
        planet = request.args.get('planet', '')
        guild = request.args.get('guild', '')
        
        filters = {}
        if profession:
            filters['profession'] = profession
        if planet:
            filters['planet'] = planet
        if guild:
            filters['guild'] = guild
        
        results = player_guild_tracker.search_players(query, filters)
        
        return jsonify({
            'success': True,
            'results': [
                {
                    'player': asdict(result.player),
                    'relevance_score': result.relevance_score,
                    'match_reasons': result.match_reasons
                }
                for result in results
            ]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/guilds")
def api_guilds():
    """API endpoint for guild search."""
    try:
        query = request.args.get('q', '')
        faction = request.args.get('faction', '')
        planet = request.args.get('planet', '')
        
        filters = {}
        if faction:
            filters['faction'] = faction
        if planet:
            filters['planet'] = planet
        
        results = player_guild_tracker.search_guilds(query, filters)
        
        return jsonify({
            'success': True,
            'results': [
                {
                    'guild': asdict(result.guild),
                    'match_reasons': result.match_reasons
                }
                for result in results
            ]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/online-players")
def api_online_players():
    """API endpoint for online players."""
    try:
        online_players = player_guild_tracker.get_online_players()
        return jsonify({
            'success': True,
            'players': [asdict(player) for player in online_players]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/guild-members/<guild_tag>")
def api_guild_members(guild_tag):
    """API endpoint for guild members."""
    try:
        members = player_guild_tracker.get_guild_members(guild_tag)
        return jsonify({
            'success': True,
            'members': [asdict(member) for member in members]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/player-guild-stats")
def api_player_guild_stats():
    """API endpoint for player and guild statistics."""
    try:
        stats = player_guild_tracker.get_statistics()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Batch 090 - Public Player Profile Routes
@app.route("/profile/create", methods=['GET', 'POST'])
def create_profile():
    """Create a new public player profile."""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            server = request.form.get('server', '').strip()
            race = request.form.get('race', '').strip()
            profession = request.form.get('profession', '').strip()
            upload_type = request.form.get('upload_type', 'manual_entry')
            
            # Validate required fields
            if not all([name, server, race, profession]):
                flash('All required fields must be filled out.', 'error')
                return render_template("create_profile.html", 
                                    servers=profile_manager.get_supported_servers(),
                                    races=profile_manager.get_supported_races(),
                                    professions=profile_manager.get_supported_professions())
            
            # Handle file upload
            file = request.files.get('profile_file')
            json_data = None
            
            if upload_type == 'json_data' and file:
                # Validate file
                if file.filename == '':
                    flash('No file selected.', 'error')
                    return render_template("create_profile.html",
                                        servers=profile_manager.get_supported_servers(),
                                        races=profile_manager.get_supported_races(),
                                        professions=profile_manager.get_supported_professions())
                
                # Check file extension
                if not file.filename.lower().endswith('.json'):
                    flash('Only JSON files are allowed for data upload.', 'error')
                    return render_template("create_profile.html",
                                        servers=profile_manager.get_supported_servers(),
                                        races=profile_manager.get_supported_races(),
                                        professions=profile_manager.get_supported_professions())
            
            elif upload_type == 'screenshot' and file:
                # Validate screenshot file
                if file.filename == '':
                    flash('No file selected.', 'error')
                    return render_template("create_profile.html",
                                        servers=profile_manager.get_supported_servers(),
                                        races=profile_manager.get_supported_races(),
                                        professions=profile_manager.get_supported_professions())
                
                # Check file extension
                allowed_extensions = {'.png', '.jpg', '.jpeg', '.gif'}
                file_ext = '.' + file.filename.rsplit('.', 1)[1].lower()
                if file_ext not in allowed_extensions:
                    flash('Only image files (PNG, JPG, JPEG, GIF) are allowed for screenshots.', 'error')
                    return render_template("create_profile.html",
                                        servers=profile_manager.get_supported_servers(),
                                        races=profile_manager.get_supported_races(),
                                        professions=profile_manager.get_supported_professions())
            
            elif upload_type == 'manual_entry':
                # Extract additional data from form
                json_data = {}
                for key in ['level', 'city', 'guild', 'guild_tag', 'faction', 'planet', 
                           'location', 'playtime_hours', 'kills', 'sessions', 'notes']:
                    value = request.form.get(key, '').strip()
                    if value:
                        json_data[key] = value
                
                # Handle arrays
                macros = request.form.get('macros_used', '').strip()
                if macros:
                    json_data['macros_used'] = [m.strip() for m in macros.split(',') if m.strip()]
                
                achievements = request.form.get('achievements', '').strip()
                if achievements:
                    json_data['achievements'] = [a.strip() for a in achievements.split(',') if a.strip()]
            
            # Create profile
            if upload_type in ['json_data', 'screenshot'] and file:
                upload = profile_manager.upload_profile_data(
                    profile_name=name,
                    server=server,
                    upload_type=upload_type,
                    file=file
                )
                
                if upload.error_message:
                    flash(f'Upload failed: {upload.error_message}', 'error')
                    return render_template("create_profile.html",
                                        servers=profile_manager.get_supported_servers(),
                                        races=profile_manager.get_supported_races(),
                                        professions=profile_manager.get_supported_professions())
                
                # Create profile from upload
                profile = profile_manager.create_profile(
                    name=name,
                    server=server,
                    race=race,
                    profession=profession,
                    upload_type=upload_type,
                    upload_data=upload.json_data
                )
            else:
                # Create profile with manual data
                profile = profile_manager.create_profile(
                    name=name,
                    server=server,
                    race=race,
                    profession=profession,
                    **json_data
                )
            
            flash(f'Profile created successfully for {name} on {server}!', 'success')
            return redirect(url_for('player_detail', player_name=name))
            
        except ValueError as e:
            flash(f'Validation error: {str(e)}', 'error')
        except Exception as e:
            flash(f'Error creating profile: {str(e)}', 'error')
    
    return render_template("create_profile.html",
                         servers=profile_manager.get_supported_servers(),
                         races=profile_manager.get_supported_races(),
                         professions=profile_manager.get_supported_professions())


@app.route("/public/players/<player_name>")
def public_player_detail(player_name):
    """Public player detail page."""
    try:
        # First check public profiles
        public_profiles = profile_manager.list_profiles()
        public_profile = None
        
        for profile in public_profiles:
            if profile.name.lower() == player_name.lower():
                public_profile = profile
                break
        
        if public_profile:
            return render_template("public_player_detail.html", profile=public_profile)
        
        # Fall back to existing player lookup
        player = player_guild_tracker.get_player(player_name)
        if player:
            return render_template("player_detail.html", player=player)
        else:
            return render_template("player_not_found.html", player_name=player_name)
    except Exception as e:
        return render_template("error.html", error=str(e))


@app.route("/api/profiles")
def api_profiles():
    """API endpoint for public profiles."""
    try:
        server = request.args.get('server')
        status = request.args.get('status')
        
        profiles = profile_manager.list_profiles(server=server, status=status)
        
        return jsonify({
            'success': True,
            'profiles': [asdict(profile) for profile in profiles]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/profile/<player_name>/<server>")
def api_profile_detail(player_name, server):
    """API endpoint for specific profile."""
    try:
        profile = profile_manager.get_profile(player_name, server)
        if profile:
            return jsonify({
                'success': True,
                'profile': asdict(profile)
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/profile/<player_name>/<server>/verify", methods=['POST'])
def api_verify_profile(player_name, server):
    """API endpoint to verify a profile."""
    try:
        success = profile_manager.verify_profile(player_name, server)
        if success:
            return jsonify({
                'success': True,
                'message': 'Profile verified successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Profile not found or already verified'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Batch 097 - Multi-Character Profile Routes

@app.route("/multi-character")
def multi_character_home():
    """Multi-character profile management home page."""
    return render_template("multi_character_home.html")


@app.route("/multi-character/account/create", methods=['GET', 'POST'])
def create_multi_character_account():
    """Create a new multi-character account."""
    if request.method == 'POST':
        try:
            account_name = request.form.get('account_name')
            email = request.form.get('email')
            discord_id = request.form.get('discord_id')
            steam_id = request.form.get('steam_id')
            
            account = multi_character_manager.create_account(
                account_name=account_name,
                email=email,
                discord_id=discord_id,
                steam_id=steam_id
            )
            
            flash(f'Account "{account_name}" created successfully!', 'success')
            return redirect(url_for('multi_character_account_detail', account_id=account.account_id))
        except Exception as e:
            flash(f'Error creating account: {str(e)}', 'error')
    
    return render_template("create_multi_character_account.html")


@app.route("/multi-character/account/<account_id>")
def multi_character_account_detail(account_id):
    """View account details with all characters."""
    try:
        account = multi_character_manager.get_account(account_id)
        if not account:
            return render_template("error.html", error="Account not found")
        
        characters = multi_character_manager.get_account_characters(account_id)
        account_stats = multi_character_manager.calculate_account_stats(account_id)
        
        return render_template("multi_character_account_detail.html", 
                             account=account, 
                             characters=characters,
                             account_stats=account_stats)
    except Exception as e:
        return render_template("error.html", error=str(e))


@app.route("/multi-character/character/create", methods=['GET', 'POST'])
def create_multi_character():
    """Create a new character under an account."""
    if request.method == 'POST':
        try:
            account_id = request.form.get('account_id')
            name = request.form.get('name')
            server = request.form.get('server')
            race = request.form.get('race')
            profession = request.form.get('profession')
            
            character = multi_character_manager.create_character(
                account_id=account_id,
                name=name,
                server=server,
                race=race,
                profession=profession
            )
            
            flash(f'Character "{name}" created successfully!', 'success')
            return redirect(url_for('multi_character_account_detail', account_id=account_id))
        except Exception as e:
            flash(f'Error creating character: {str(e)}', 'error')
    
    accounts = list(multi_character_manager.accounts.values())
    return render_template("create_multi_character.html", accounts=accounts)


@app.route("/multi-character/character/<character_id>")
def multi_character_detail(character_id):
    """View individual character details."""
    try:
        character = multi_character_manager.get_character(character_id)
        if not character:
            return render_template("error.html", error="Character not found")
        
        account = multi_character_manager.get_account(character.account_id)
        sessions = multi_character_manager.get_character_sessions(character_id)
        
        return render_template("multi_character_detail.html", 
                             character=character,
                             account=account,
                             sessions=sessions)
    except Exception as e:
        return render_template("error.html", error=str(e))


@app.route("/multi-character/character/<character_id>/edit", methods=['GET', 'POST'])
def edit_multi_character(character_id):
    """Edit character details."""
    character = multi_character_manager.get_character(character_id)
    if not character:
        return render_template("error.html", error="Character not found")
    
    if request.method == 'POST':
        try:
            # Update character data
            updates = {}
            for field in ['name', 'server', 'race', 'profession', 'level', 'city', 
                         'guild', 'guild_tag', 'faction', 'planet', 'location',
                         'playtime_hours', 'kills', 'sessions', 'notes', 'visibility']:
                if field in request.form:
                    updates[field] = request.form[field]
            
            # Handle lists and dicts
            if 'macros_used' in request.form:
                updates['macros_used'] = request.form.getlist('macros_used')
            if 'achievements' in request.form:
                updates['achievements'] = request.form.getlist('achievements')
            
            updated_character = multi_character_manager.update_character(character_id, **updates)
            
            flash(f'Character "{updated_character.name}" updated successfully!', 'success')
            return redirect(url_for('multi_character_detail', character_id=character_id))
        except Exception as e:
            flash(f'Error updating character: {str(e)}', 'error')
    
    return render_template("edit_multi_character.html", character=character)


@app.route("/api/multi-character/accounts")
def api_multi_character_accounts():
    """API endpoint for multi-character account search."""
    try:
        query = request.args.get('q', '')
        server = request.args.get('server')
        
        accounts = multi_character_manager.search_accounts(query=query, server=server)
        
        return jsonify({
            'success': True,
            'accounts': [asdict(account) for account in accounts]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/multi-character/characters")
def api_multi_character_characters():
    """API endpoint for multi-character search."""
    try:
        query = request.args.get('q', '')
        server = request.args.get('server')
        profession = request.args.get('profession')
        visibility = request.args.get('visibility')
        
        characters = multi_character_manager.search_characters(
            query=query, 
            server=server, 
            profession=profession, 
            visibility=visibility
        )
        
        return jsonify({
            'success': True,
            'characters': [asdict(character) for character in characters]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/multi-character/account/<account_id>")
def api_multi_character_account_detail(account_id):
    """API endpoint for specific account details."""
    try:
        account = multi_character_manager.get_account(account_id)
        if not account:
            return jsonify({
                'success': False,
                'error': 'Account not found'
            }), 404
        
        characters = multi_character_manager.get_account_characters(account_id)
        account_stats = multi_character_manager.calculate_account_stats(account_id)
        
        return jsonify({
            'success': True,
            'account': asdict(account),
            'characters': [asdict(character) for character in characters],
            'account_stats': account_stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/multi-character/character/<character_id>")
def api_multi_character_character_detail(character_id):
    """API endpoint for specific character details."""
    try:
        character = multi_character_manager.get_character(character_id)
        if not character:
            return jsonify({
                'success': False,
                'error': 'Character not found'
            }), 404
        
        account = multi_character_manager.get_account(character.account_id)
        sessions = multi_character_manager.get_character_sessions(character_id)
        
        return jsonify({
            'success': True,
            'character': asdict(character),
            'account': asdict(account) if account else None,
            'sessions': [asdict(session) for session in sessions]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/multi-character/character/<character_id>/set-main", methods=['POST'])
def api_set_main_character(character_id):
    """API endpoint to set a character as main."""
    try:
        success = multi_character_manager.set_main_character(character_id)
        if success:
            return jsonify({
                'success': True,
                'message': 'Main character updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Character not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/multi-character/character/<character_id>/visibility", methods=['POST'])
def api_set_character_visibility(character_id):
    """API endpoint to set character visibility."""
    try:
        visibility = request.json.get('visibility')
        if not visibility:
            return jsonify({
                'success': False,
                'error': 'Visibility parameter required'
            }), 400
        
        success = multi_character_manager.set_character_visibility(character_id, visibility)
        if success:
            return jsonify({
                'success': True,
                'message': 'Character visibility updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Character not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/multi-character/session/add", methods=['POST'])
def api_add_session_history():
    """API endpoint to add session history."""
    try:
        data = request.json
        character_id = data.get('character_id')
        start_time = data.get('start_time')
        
        if not character_id or not start_time:
            return jsonify({
                'success': False,
                'error': 'Character ID and start time required'
            }), 400
        
        session = multi_character_manager.add_session_history(
            character_id=character_id,
            start_time=start_time,
            **{k: v for k, v in data.items() if k not in ['character_id', 'start_time']}
        )
        
        return jsonify({
            'success': True,
            'session': asdict(session)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Batch 091 - AI Assistant Routes
@app.route("/ai-chat")
def ai_chat():
    """AI Chat interface page."""
    return render_template("ai_chat.html")


@app.route("/api/ai-chat/session", methods=['POST'])
def api_create_chat_session():
    """Create a new AI chat session."""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'anonymous')
        mode = data.get('mode', 'general')
        
        session_id = chat_session_manager.create_session(user_id, mode)
        
        return jsonify({
            'success': True,
            'session_id': session_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/ai-chat/session/<session_id>/message", methods=['POST'])
def api_send_message(session_id):
    """Send a message to the AI assistant."""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'Message is required'
            }), 400
        
        response = chat_session_manager.process_user_message(session_id, message)
        
        return jsonify({
            'success': True,
            'response': response
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/ai-chat/session/<session_id>/history")
def api_get_chat_history(session_id):
    """Get chat history for a session."""
    try:
        history = chat_session_manager.get_session_history(session_id)
        
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/ai-chat/sessions")
def api_list_chat_sessions():
    """List all chat sessions."""
    try:
        user_id = request.args.get('user_id')
        limit = int(request.args.get('limit', 50))
        
        sessions = chat_session_manager.list_sessions(user_id, limit)
        
        return jsonify({
            'success': True,
            'sessions': sessions
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/ai-chat/session/<session_id>", methods=['DELETE'])
def api_delete_chat_session(session_id):
    """Delete a chat session."""
    try:
        success = chat_session_manager.delete_session(session_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Session deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/ai-chat/stats")
def api_chat_stats():
    """Get AI chat statistics."""
    try:
        stats = chat_session_manager.get_session_stats()

        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Batch 092 - Blog Routes
@app.route("/blog")
def blog():
    """Blog listing page."""
    return render_template("blog.html")


@app.route("/blog/<post_id>")
def blog_post(post_id):
    """Individual blog post page."""
    try:
        post = blog_manager.get_post(post_id)
        if post:
            return render_template("blog_post.html", post=post)
        else:
            return render_template("error.html", error="Blog post not found"), 404
    except Exception as e:
        return render_template("error.html", error=str(e))


@app.route("/blog/new", methods=['GET', 'POST'])
def create_blog_post():
    """Create a new blog post."""
    if request.method == 'POST':
        try:
            # Get form data
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            excerpt = request.form.get('excerpt', '').strip()
            category = request.form.get('category', 'general')
            tags = request.form.get('tags', '').strip()
            
            if not title or not content:
                flash('Title and content are required.', 'error')
                return render_template("blog_editor.html")

            # Parse tags
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]

            # Create post
            post = blog_manager.post_generator.data_ingestion.BlogPost(
                post_id=f"manual_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                title=title,
                content=content,
                excerpt=excerpt,
                category=category,
                tags=tag_list,
                status="draft"
            )

            success = blog_manager.create_post(post)
            if success:
                flash('Blog post created successfully!', 'success')
                return redirect(url_for('blog_post', post_id=post.post_id))
            else:
                flash('Failed to create blog post.', 'error')

        except Exception as e:
            flash(f'Error creating blog post: {str(e)}', 'error')

    return render_template("blog_editor.html")


@app.route("/blog/<post_id>/edit", methods=['GET', 'POST'])
def edit_blog_post(post_id):
    """Edit a blog post."""
    post = blog_manager.get_post(post_id)
    if not post:
        return render_template("error.html", error="Blog post not found"), 404

    if request.method == 'POST':
        try:
            # Get form data
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            excerpt = request.form.get('excerpt', '').strip()
            category = request.form.get('category', 'general')
            tags = request.form.get('tags', '').strip()
            
            if not title or not content:
                flash('Title and content are required.', 'error')
                return render_template("blog_editor.html", post=post)

            # Parse tags
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]

            # Update post
            success = blog_manager.update_post(
                post_id,
                title=title,
                content=content,
                excerpt=excerpt,
                category=category,
                tags=tag_list
            )

            if success:
                flash('Blog post updated successfully!', 'success')
                return redirect(url_for('blog_post', post_id=post_id))
            else:
                flash('Failed to update blog post.', 'error')

        except Exception as e:
            flash(f'Error updating blog post: {str(e)}', 'error')

    return render_template("blog_editor.html", post=post)


# Blog API Endpoints
@app.route("/api/blog/posts")
def api_blog_posts():
    """API endpoint for blog posts."""
    try:
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))

        posts = blog_manager.list_posts(status=status, limit=limit)
        
        # Convert posts to dictionaries
        posts_data = []
        for post in posts:
            post_dict = {
                'post_id': post.post_id,
                'title': post.title,
                'excerpt': post.excerpt,
                'author': post.author,
                'category': post.category,
                'tags': post.tags,
                'status': post.status,
                'created_at': post.created_at,
                'published_at': post.published_at,
                'updated_at': post.updated_at,
                'word_count': post.word_count,
                'read_time_minutes': post.read_time_minutes,
                'view_count': post.view_count,
                'share_count': post.share_count
            }
            posts_data.append(post_dict)

        return jsonify({
            'success': True,
            'posts': posts_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/blog/posts/<post_id>")
def api_blog_post_detail(post_id):
    """API endpoint for specific blog post."""
    try:
        post = blog_manager.get_post(post_id)
        if post:
            return jsonify({
                'success': True,
                'post': {
                    'post_id': post.post_id,
                    'title': post.title,
                    'content': post.content,
                    'excerpt': post.excerpt,
                    'author': post.author,
                    'category': post.category,
                    'tags': post.tags,
                    'status': post.status,
                    'created_at': post.created_at,
                    'published_at': post.published_at,
                    'updated_at': post.updated_at,
                    'seo_title': post.seo_title,
                    'seo_description': post.seo_description,
                    'seo_keywords': post.seo_keywords,
                    'word_count': post.word_count,
                    'read_time_minutes': post.read_time_minutes,
                    'view_count': post.view_count,
                    'share_count': post.share_count
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Post not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/blog/posts/<post_id>", methods=['DELETE'])
def api_delete_blog_post(post_id):
    """API endpoint to delete a blog post."""
    try:
        success = blog_manager.delete_post(post_id)
        if success:
            return jsonify({
                'success': True,
                'message': 'Post deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Post not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/blog/posts/<post_id>/publish", methods=['POST'])
def api_publish_blog_post(post_id):
    """API endpoint to publish a blog post."""
    try:
        success = blog_manager.publish_post(post_id)
        if success:
            return jsonify({
                'success': True,
                'message': 'Post published successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Post not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/blog/posts/<post_id>/view", methods=['POST'])
def api_increment_view_count(post_id):
    """API endpoint to increment view count."""
    try:
        post = blog_manager.get_post(post_id)
        if post:
            post.view_count += 1
            success = blog_manager.create_post(post)  # Save updated post
            if success:
                return jsonify({
                    'success': True,
                    'view_count': post.view_count
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to update view count'
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': 'Post not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/blog/generate", methods=['POST'])
def api_generate_daily_post():
    """API endpoint to generate a daily blog post."""
    try:
        post = blog_manager.generate_daily_post()
        if post:
            return jsonify({
                'success': True,
                'post': {
                    'post_id': post.post_id,
                    'title': post.title,
                    'excerpt': post.excerpt,
                    'category': post.category,
                    'status': post.status
                }
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to generate daily post'
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/blog/stats")
def api_blog_stats():
    """API endpoint for blog statistics."""
    try:
        stats = blog_manager.get_blog_stats()

        return jsonify({
            'success': True,
            'stats': {
                'total_posts': stats.total_posts,
                'published_posts': stats.published_posts,
                'draft_posts': stats.draft_posts,
                'total_views': stats.total_views,
                'total_shares': stats.total_shares,
                'average_read_time': stats.average_read_time,
                'most_popular_category': stats.most_popular_category,
                'most_popular_tags': stats.most_popular_tags,
                'last_post_date': stats.last_post_date,
                'next_scheduled_post': stats.next_scheduled_post
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Batch 093 - Macro Safety Routes
@app.route("/macro-safety")
def macro_safety():
    """Macro safety dashboard page."""
    return render_template("macro_safety.html")


# Macro Safety API Endpoints
@app.route("/api/macro-safety/performance")
def api_macro_safety_performance():
    """API endpoint for performance metrics."""
    try:
        metrics = macro_safety_manager.performance_monitor.get_current_metrics()
        
        return jsonify({
            'success': True,
            'metrics': {
                'cpu_usage': metrics.cpu_usage,
                'memory_usage': metrics.memory_usage,
                'fps': metrics.fps,
                'latency': metrics.latency,
                'response_time': metrics.response_time
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/macro-safety/status")
def api_macro_safety_status():
    """API endpoint for safety status."""
    try:
        report = macro_safety_manager.get_safety_report()
        
        return jsonify({
            'success': True,
            'status': {
                'monitoring_active': macro_safety_manager.performance_monitor.monitoring,
                'active_macros': report['active_macros'],
                'total_cancellations': report['total_cancellations'],
                'last_check': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/macro-safety/active-macros")
def api_macro_safety_active_macros():
    """API endpoint for active macros."""
    try:
        report = macro_safety_manager.get_safety_report()
        
        return jsonify({
            'success': True,
            'macros': report['active_macro_details']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/macro-safety/cancellations")
def api_macro_safety_cancellations():
    """API endpoint for recent cancellations."""
    try:
        report = macro_safety_manager.get_safety_report()
        
        return jsonify({
            'success': True,
            'cancellations': report['recent_cancellations']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/macro-safety/start", methods=['POST'])
def api_macro_safety_start():
    """API endpoint to start monitoring a macro."""
    try:
        data = request.get_json()
        macro_id = data.get('macro_id')
        macro_name = data.get('macro_name', macro_id)
        safety_level = data.get('safety_level', 'risky')
        
        if not macro_id:
            return jsonify({
                'success': False,
                'error': 'Macro ID is required'
            }), 400
        
        success = macro_safety_manager.start_macro(macro_id, macro_name)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Started monitoring macro: {macro_id}'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Failed to start macro: {macro_id}'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/macro-safety/stop/<macro_id>", methods=['POST'])
def api_macro_safety_stop(macro_id):
    """API endpoint to stop monitoring a macro."""
    try:
        success = macro_safety_manager.stop_macro(macro_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Stopped monitoring macro: {macro_id}'
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Macro {macro_id} not found or already stopped'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/macro-safety/stop-all", methods=['POST'])
def api_macro_safety_stop_all():
    """API endpoint to stop all active macros."""
    try:
        active_macros = list(macro_safety_manager.active_macros.keys())
        stopped_count = 0
        
        for macro_id in active_macros:
            if macro_safety_manager.stop_macro(macro_id):
                stopped_count += 1
        
        return jsonify({
            'success': True,
            'message': f'Stopped {stopped_count} active macros',
            'stopped_count': stopped_count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/macro-safety/check", methods=['POST'])
def api_macro_safety_check():
    """API endpoint to manually trigger safety check."""
    try:
        cancellations = macro_safety_manager.check_macro_safety()
        
        return jsonify({
            'success': True,
            'cancellations': len(cancellations),
            'cancellation_details': [
                {
                    'macro_id': c.macro_id,
                    'macro_name': c.macro_name,
                    'reason': c.cancellation_reason,
                    'timestamp': c.timestamp.isoformat()
                }
                for c in cancellations
            ]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/macro-safety/report")
def api_macro_safety_report():
    """API endpoint to get comprehensive safety report."""
    try:
        report = macro_safety_manager.get_safety_report()
        
        return jsonify({
            'success': True,
            'report': report
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/macro-safety/log", methods=['POST'])
def api_macro_safety_save_log():
    """API endpoint to save cancellation log."""
    try:
        log_path = macro_safety_manager.save_cancellation_log()
        
        return jsonify({
            'success': True,
            'log_path': log_path,
            'message': 'Cancellation log saved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Helper function for date formatting
def format_date(date_string):
    """Format date string for display."""
    try:
        date = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return date.strftime('%B %d, %Y')
    except:
        return date_string


# Batch 094 - Heroic Support Routes
@app.route("/heroic-support")
def heroic_support_page():
    """Heroic support dashboard page."""
    return render_template("heroic_support.html")


# Heroic Support API Endpoints
@app.route("/api/heroic-support/status")
def api_heroic_support_status():
    """API endpoint for heroic support status."""
    try:
        status = heroic_support.update_state()
        
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/heroic-support/group-info")
def api_heroic_support_group_info():
    """API endpoint for group information."""
    try:
        group_info = heroic_support.group_coordinator.get_group_info()
        
        return jsonify({
            'success': True,
            'group_info': group_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/heroic-support/heroic-list")
def api_heroic_support_heroic_list():
    """API endpoint for available heroics."""
    try:
        # Placeholder character level - would be dynamic in real implementation
        character_level = 80
        heroics = heroic_support.get_available_heroics(character_level)
        
        return jsonify({
            'success': True,
            'heroics': heroics
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/heroic-support/config")
def api_heroic_support_config():
    """API endpoint for heroic support configuration."""
    try:
        config = heroic_support.config.get("heroic_mode", {})
        group_config = heroic_support.config.get("group_behavior", {})
        
        return jsonify({
            'success': True,
            'config': {
                'auto_follow_leader': config.get("auto_follow_leader", True),
                'wait_for_group': config.get("wait_for_group", True),
                'group_timeout': config.get("group_timeout", 300),
                'follow_distance': group_config.get("follow_distance", 10)
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/heroic-support/enable", methods=['POST'])
def api_heroic_support_enable():
    """API endpoint to enable heroic mode."""
    try:
        success = heroic_support.enable_heroic_mode()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Heroic mode enabled successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to enable heroic mode'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/heroic-support/disable", methods=['POST'])
def api_heroic_support_disable():
    """API endpoint to disable heroic mode."""
    try:
        success = heroic_support.disable_heroic_mode()
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Heroic mode disabled successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to disable heroic mode'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/heroic-support/wait-group", methods=['POST'])
def api_heroic_support_wait_group():
    """API endpoint to wait for group."""
    try:
        success = heroic_support.wait_for_group_ready()
        
        return jsonify({
            'success': True,
            'group_ready': success,
            'message': 'Group ready' if success else 'Group wait timeout'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/heroic-support/heroic/<heroic_id>")
def api_heroic_support_heroic_detail(heroic_id):
    """API endpoint for heroic instance details."""
    try:
        heroic_info = heroic_support.get_heroic_info(heroic_id)
        
        if "error" in heroic_info:
            return jsonify({
                'success': False,
                'error': heroic_info["error"]
            }), 404
        
        return jsonify({
            'success': True,
            'heroic': heroic_info
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Batch 095 - Vendor Price Scanner Routes
@app.route("/vendor-price-scanner")
def vendor_price_scanner_page():
    """Vendor price scanner dashboard page."""
    return render_template("vendor_price_scanner.html")

# Batch 100 - Vendor Transaction Ledger Routes
@app.route("/market-insights/vendor-history")
def vendor_transaction_ledger_page():
    """Vendor transaction ledger dashboard page."""
    return render_template("market_insights_vendor_history.html")


# Vendor Price Scanner API Endpoints
@app.route("/api/vendor-scanner/statistics")
def api_vendor_scanner_statistics():
    """API endpoint for vendor scanner statistics."""
    try:
        scanner_stats = vendor_price_scanner.get_statistics()
        alert_stats = vendor_price_alerts.get_alert_statistics()
        
        # Combine statistics
        combined_stats = {
            **scanner_stats,
            "recent_alerts_24h": alert_stats.get("recent_alerts_24h", 0)
        }
        
        return jsonify({
            'success': True,
            'statistics': combined_stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/vendor-scanner/alert-settings")
def api_vendor_scanner_alert_settings():
    """API endpoint for alert settings."""
    try:
        alert_stats = vendor_price_alerts.get_alert_statistics()
        
        return jsonify({
            'success': True,
            'settings': alert_stats.get("alert_preferences", {})
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/vendor-scanner/recent-alerts")
def api_vendor_scanner_recent_alerts():
    """API endpoint for recent alerts."""
    try:
        alert_stats = vendor_price_alerts.get_alert_statistics()
        
        # Get recent alerts from history
        recent_alerts = []
        if vendor_price_alerts.alert_history:
            # Get last 10 alerts
            recent_alerts = vendor_price_alerts.alert_history[-10:]
        
        return jsonify({
            'success': True,
            'alerts': recent_alerts
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/vendor-scanner/start-scan", methods=['POST'])
def api_vendor_scanner_start_scan():
    """API endpoint to start vendor scanning."""
    try:
        data = request.get_json()
        vendor_name = data.get('vendor_name', 'Unknown')
        location = data.get('location', 'Unknown')
        interval = data.get('interval', 30)
        
        # For now, just perform a single scan
        scanned_prices = vendor_price_scanner.scan_vendor_window(vendor_name, location)
        
        if scanned_prices:
            # Save to price history
            vendor_price_scanner.save_price_history(scanned_prices)
            
            # Analyze for alerts
            alerts = vendor_price_scanner.analyze_prices(scanned_prices)
            
            # Send alerts for underpriced items
            for alert in alerts:
                if alert.alert_type == "underpriced":
                    vendor_price_alerts.send_price_alert(
                        alert.item_name,
                        alert.current_price,
                        alert.average_price,
                        alert.discount_percentage,
                        alert.vendor_name,
                        alert.location
                    )
        
        return jsonify({
            'success': True,
            'scanned_prices': len(scanned_prices),
            'alerts_found': len(alerts) if 'alerts' in locals() else 0
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/vendor-scanner/stop-scan", methods=['POST'])
def api_vendor_scanner_stop_scan():
    """API endpoint to stop vendor scanning."""
    try:
        # For now, just return success
        return jsonify({
            'success': True,
            'message': 'Scanner stopped successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/vendor-scanner/perform-scan", methods=['POST'])
def api_vendor_scanner_perform_scan():
    """API endpoint to perform a single vendor scan."""
    try:
        data = request.get_json()
        vendor_name = data.get('vendor_name', 'Unknown')
        location = data.get('location', 'Unknown')
        
        # Perform scan
        scanned_prices = vendor_price_scanner.scan_vendor_window(vendor_name, location)
        
        if scanned_prices:
            # Save to price history
            vendor_price_scanner.save_price_history(scanned_prices)
            
            # Analyze for alerts
            alerts = vendor_price_scanner.analyze_prices(scanned_prices)
            
            # Send alerts for underpriced items
            for alert in alerts:
                if alert.alert_type == "underpriced":
                    vendor_price_alerts.send_price_alert(
                        alert.item_name,
                        alert.current_price,
                        alert.average_price,
                        alert.discount_percentage,
                        alert.vendor_name,
                        alert.location
                    )
        
        return jsonify({
            'success': True,
            'scanned_prices': len(scanned_prices),
            'alerts_found': len(alerts) if 'alerts' in locals() else 0
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/vendor-scanner/update-alert-settings", methods=['POST'])
def api_vendor_scanner_update_alert_settings():
    """API endpoint to update alert settings."""
    try:
        data = request.get_json()
        
        # Update alert preferences
        vendor_price_alerts.update_preferences(
            min_alert_price=data.get('min_alert_price', 1000),
            discount_threshold=data.get('discount_threshold', 0.3),
            enable_discord_alerts=data.get('enable_discord_alerts', True),
            enable_console_alerts=data.get('enable_console_alerts', True)
        )
        
        return jsonify({
            'success': True,
            'message': 'Alert settings updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/vendor-scanner/analyze-prices", methods=['POST'])
def api_vendor_scanner_analyze_prices():
    """API endpoint to analyze current prices."""
    try:
        # For demo purposes, create some sample analysis
        # In real implementation, this would analyze actual scanned prices
        sample_analysis = [
            {
                "item_name": "Durindfire Crystal",
                "current_price": 50000,
                "average_price": 75000,
                "discount_percentage": 0.33,
                "vendor_name": "Test Vendor",
                "alert_type": "underpriced"
            },
            {
                "item_name": "Spice Wine",
                "current_price": 150000,
                "average_price": 120000,
                "discount_percentage": -0.25,
                "vendor_name": "Test Vendor",
                "alert_type": "overpriced"
            }
        ]
        
        return jsonify({
            'success': True,
            'analysis': sample_analysis
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/vendor-scanner/recommendations")
def api_vendor_scanner_recommendations():
    """API endpoint to get price recommendations."""
    try:
        # For demo purposes, create some sample recommendations
        # In real implementation, this would use actual price history
        sample_recommendations = [
            {
                "item_name": "Durindfire Crystal",
                "recommended_price": 70000,
                "confidence": 0.85,
                "reasoning": "Based on 15 price entries. Market trend: stable",
                "market_trend": "stable"
            },
            {
                "item_name": "Spice Wine",
                "recommended_price": 125000,
                "confidence": 0.72,
                "reasoning": "Based on 8 price entries. Market trend: rising",
                "market_trend": "rising"
            }
        ]
        
        return jsonify({
            'success': True,
            'recommendations': sample_recommendations
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Batch 096 - Steam + Discord Identity Bridge Routes
@app.route("/identity-bridge")
def identity_bridge_page():
    """Steam + Discord Identity Bridge dashboard page."""
    return render_template("identity_bridge.html")


# Identity Bridge API Endpoints
@app.route("/api/identity-bridge/discord/auth", methods=['POST'])
def api_identity_bridge_discord_auth():
    """API endpoint to start Discord authentication."""
    try:
        auth_url = identity_bridge.start_discord_auth()
        
        return jsonify({
            'success': True,
            'auth_url': auth_url
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/identity-bridge/steam/auth", methods=['POST'])
def api_identity_bridge_steam_auth():
    """API endpoint to start Steam authentication."""
    try:
        auth_url = identity_bridge.start_steam_auth()
        
        return jsonify({
            'success': True,
            'auth_url': auth_url
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/auth/discord/callback")
def discord_auth_callback():
    """Discord OAuth callback handler."""
    try:
        code = request.args.get('code')
        state = request.args.get('state')
        
        if not code or not state:
            return "Authentication failed: Missing parameters", 400
        
        # Complete Discord authentication
        profile = identity_bridge.complete_discord_auth(code, state)
        
        if profile:
            flash(f"Discord authentication successful! Welcome, {profile.username}", "success")
        else:
            flash("Discord authentication failed", "error")
        
        return redirect(url_for('identity_bridge_page'))
        
    except Exception as e:
        flash(f"Discord authentication error: {str(e)}", "error")
        return redirect(url_for('identity_bridge_page'))


@app.route("/auth/steam/callback")
def steam_auth_callback():
    """Steam OAuth callback handler."""
    try:
        # Steam OpenID response data
        response_data = dict(request.args)
        state = request.args.get('state')
        
        if not state:
            return "Authentication failed: Missing state parameter", 400
        
        # Complete Steam authentication
        profile = identity_bridge.complete_steam_auth(response_data, state)
        
        if profile:
            flash(f"Steam authentication successful! Welcome, {profile.username}", "success")
        else:
            flash("Steam authentication failed", "error")
        
        return redirect(url_for('identity_bridge_page'))
        
    except Exception as e:
        flash(f"Steam authentication error: {str(e)}", "error")
        return redirect(url_for('identity_bridge_page'))


@app.route("/api/identity-bridge/auth-status")
def api_identity_bridge_auth_status():
    """API endpoint to check authentication status."""
    try:
        discord_authenticated = session.get('discord_authenticated', False)
        steam_authenticated = session.get('steam_authenticated', False)
        
        # Check if accounts are linked
        discord_profile = session.get('discord_profile')
        linked = False
        
        if discord_profile and steam_authenticated:
            # Check if there's a linked identity
            discord_id = discord_profile.get('discord_id')
            if discord_id:
                linked_identity = identity_bridge.get_linked_identity(discord_id)
                linked = linked_identity and linked_identity.linked if linked_identity else False
        
        return jsonify({
            'success': True,
            'status': {
                'discord_authenticated': discord_authenticated,
                'steam_authenticated': steam_authenticated,
                'linked': linked
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/identity-bridge/profile")
def api_identity_bridge_profile():
    """API endpoint to get current profile information."""
    try:
        discord_profile = session.get('discord_profile')
        steam_profile = session.get('steam_profile')
        
        # Get linked identity if available
        linked_identity = None
        if discord_profile:
            discord_id = discord_profile.get('discord_id')
            if discord_id:
                linked_identity = identity_bridge.get_linked_identity(discord_id)
        
        # Use linked identity data if available, otherwise use session data
        if linked_identity:
            profile_data = {
                'discord_profile': linked_identity.discord_profile.__dict__ if linked_identity.discord_profile else None,
                'steam_profile': linked_identity.steam_profile.__dict__ if linked_identity.steam_profile else None,
                'linked': linked_identity.linked,
                'linked_at': linked_identity.linked_at,
                'auth_status': linked_identity.auth_status.value
            }
        else:
            profile_data = {
                'discord_profile': discord_profile,
                'steam_profile': steam_profile,
                'linked': False,
                'linked_at': None,
                'auth_status': 'authenticated' if discord_profile else 'pending'
            }
        
        return jsonify({
            'success': True,
            'profile': profile_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/identity-bridge/link", methods=['POST'])
def api_identity_bridge_link():
    """API endpoint to link Discord and Steam accounts."""
    try:
        discord_profile = session.get('discord_profile')
        if not discord_profile:
            return jsonify({
                'success': False,
                'error': 'Discord authentication required'
            }), 400
        
        discord_id = discord_profile.get('discord_id')
        if not discord_id:
            return jsonify({
                'success': False,
                'error': 'Invalid Discord profile'
            }), 400
        
        # Link the identities
        linked_identity = identity_bridge.link_identities(discord_id)
        
        return jsonify({
            'success': True,
            'linked_identity': {
                'discord_id': linked_identity.discord_id,
                'steam_id': linked_identity.steam_id,
                'linked': linked_identity.linked,
                'linked_at': linked_identity.linked_at
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/identity-bridge/unlink", methods=['POST'])
def api_identity_bridge_unlink():
    """API endpoint to unlink Steam account from Discord."""
    try:
        discord_profile = session.get('discord_profile')
        if not discord_profile:
            return jsonify({
                'success': False,
                'error': 'Discord authentication required'
            }), 400
        
        discord_id = discord_profile.get('discord_id')
        if not discord_id:
            return jsonify({
                'success': False,
                'error': 'Invalid Discord profile'
            }), 400
        
        # Unlink Steam account
        success = identity_bridge.unlink_steam(discord_id)
        
        if success:
            # Clear Steam session data
            session.pop('steam_profile', None)
            session.pop('steam_authenticated', None)
        
        return jsonify({
            'success': success
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/identity-bridge/statistics")
def api_identity_bridge_statistics():
    """API endpoint for identity bridge statistics."""
    try:
        stats = identity_bridge.get_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Batch 098 - Quest Heatmap & Popular Paths Tracker Routes
@app.route("/admin/quest-heatmap")
def quest_heatmap_dashboard():
    """Admin dashboard for quest heatmap and popular paths."""
    return render_template("admin/quest_heatmap_dashboard.html")

@app.route("/admin/quest-heatmap/process")
def process_quest_heatmap():
    """Process session logs for heatmap data."""
    try:
        quest_heatmap_tracker.process_session_logs()
        flash("Session logs processed successfully for heatmap data.", "success")
    except Exception as e:
        flash(f"Error processing session logs: {e}", "error")
    
    return redirect(url_for("quest_heatmap_dashboard"))

@app.route("/api/admin/quest-heatmap/weekly-stats")
def api_quest_heatmap_weekly_stats():
    """Get weekly quest heatmap statistics."""
    try:
        stats = quest_heatmap_tracker.get_weekly_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/quest-heatmap/quest-data")
def api_quest_heatmap_quest_data():
    """Get quest heatmap data."""
    try:
        days = request.args.get('days', 7, type=int)
        data = quest_heatmap_tracker.get_quest_heatmap(days)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/quest-heatmap/city-data")
def api_quest_heatmap_city_data():
    """Get city heatmap data."""
    try:
        days = request.args.get('days', 7, type=int)
        data = quest_heatmap_tracker.get_city_heatmap(days)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/quest-heatmap/danger-zones")
def api_quest_heatmap_danger_zones():
    """Get danger zones data."""
    try:
        days = request.args.get('days', 7, type=int)
        data = quest_heatmap_tracker.get_danger_zones(days)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/quest-heatmap/popular-paths")
def api_quest_heatmap_popular_paths():
    """Get popular paths data."""
    try:
        days = request.args.get('days', 7, type=int)
        data = quest_heatmap_tracker.get_popular_paths(days)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/admin/quest-heatmap/coordinate-heatmap")
def api_quest_heatmap_coordinate_heatmap():
    """Get coordinate heatmap for a specific planet."""
    try:
        planet = request.args.get('planet', 'Tatooine')
        days = request.args.get('days', 7, type=int)
        data = quest_heatmap_tracker.get_coordinate_heatmap(planet, days)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/quest-heatmap/clear-data", methods=['POST'])
def clear_quest_heatmap_data():
    """Clear old heatmap data."""
    try:
        days = request.form.get('days', 30, type=int)
        quest_heatmap_tracker.clear_old_data(days)
        flash(f"Cleared heatmap data older than {days} days.", "success")
    except Exception as e:
        flash(f"Error clearing data: {e}", "error")
    
    return redirect(url_for("quest_heatmap_dashboard"))


# Batch 100 - Vendor Transaction Ledger API Endpoints
@app.route("/api/vendor-ledger/statistics")
def api_vendor_ledger_statistics():
    """API endpoint for vendor ledger statistics."""
    try:
        from core.vendor_transaction_ledger import vendor_ledger
        statistics = vendor_ledger.get_statistics()
        
        return jsonify({
            'success': True,
            'statistics': statistics
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/vendor-ledger/transactions")
def api_vendor_ledger_transactions():
    """API endpoint for vendor ledger transactions."""
    try:
        from core.vendor_transaction_ledger import vendor_ledger
        
        # Get filter parameters
        item_name = request.args.get('item_name')
        seller = request.args.get('seller')
        location = request.args.get('location')
        transaction_type = request.args.get('transaction_type')
        item_category = request.args.get('item_category')
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Convert parameters
        if min_price:
            min_price = int(min_price)
        if max_price:
            max_price = int(max_price)
        if start_date:
            start_date = datetime.fromisoformat(start_date)
        if end_date:
            end_date = datetime.fromisoformat(end_date)
        
        transactions = vendor_ledger.get_transactions(
            item_name=item_name,
            seller=seller,
            location=location,
            transaction_type=transaction_type,
            item_category=item_category,
            min_price=min_price,
            max_price=max_price,
            start_date=start_date,
            end_date=end_date
        )
        
        # Convert to dict for JSON serialization
        transaction_dicts = []
        for tx in transactions:
            tx_dict = {
                'item_name': tx.item_name,
                'price': tx.price,
                'location': tx.location,
                'seller': tx.seller,
                'timestamp': tx.timestamp,
                'transaction_type': tx.transaction_type.value,
                'item_category': tx.item_category.value,
                'quantity': tx.quantity,
                'notes': tx.notes,
                'confidence': tx.confidence,
                'raw_text': tx.raw_text
            }
            
            # Add price analysis if available
            if tx.item_name in vendor_ledger.price_analyses:
                analysis = vendor_ledger.price_analyses[tx.item_name]
                tx_dict['price_analysis'] = {
                    'average_price': analysis.average_price,
                    'median_price': analysis.median_price,
                    'min_price': analysis.min_price,
                    'max_price': analysis.max_price,
                    'price_count': analysis.price_count,
                    'price_trend': analysis.price_trend,
                    'underpriced': tx.price <= analysis.underpriced_threshold,
                    'overpriced': tx.price >= analysis.overpriced_threshold
                }
            
            transaction_dicts.append(tx_dict)
        
        return jsonify({
            'success': True,
            'transactions': transaction_dicts
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/vendor-ledger/underpriced")
def api_vendor_ledger_underpriced():
    """API endpoint for underpriced items."""
    try:
        from core.vendor_transaction_ledger import vendor_ledger
        underpriced = vendor_ledger.get_underpriced_items()
        
        # Convert to dict for JSON serialization
        transaction_dicts = []
        for tx, analysis in underpriced:
            tx_dict = {
                'item_name': tx.item_name,
                'price': tx.price,
                'location': tx.location,
                'seller': tx.seller,
                'timestamp': tx.timestamp,
                'transaction_type': tx.transaction_type.value,
                'item_category': tx.item_category.value,
                'quantity': tx.quantity,
                'notes': tx.notes,
                'confidence': tx.confidence,
                'raw_text': tx.raw_text,
                'price_analysis': {
                    'average_price': analysis.average_price,
                    'median_price': analysis.median_price,
                    'min_price': analysis.min_price,
                    'max_price': analysis.max_price,
                    'price_count': analysis.price_count,
                    'price_trend': analysis.price_trend,
                    'underpriced': True,
                    'overpriced': False
                }
            }
            transaction_dicts.append(tx_dict)
        
        return jsonify({
            'success': True,
            'transactions': transaction_dicts
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/vendor-ledger/overpriced")
def api_vendor_ledger_overpriced():
    """API endpoint for overpriced items."""
    try:
        from core.vendor_transaction_ledger import vendor_ledger
        overpriced = vendor_ledger.get_overpriced_items()
        
        # Convert to dict for JSON serialization
        transaction_dicts = []
        for tx, analysis in overpriced:
            tx_dict = {
                'item_name': tx.item_name,
                'price': tx.price,
                'location': tx.location,
                'seller': tx.seller,
                'timestamp': tx.timestamp,
                'transaction_type': tx.transaction_type.value,
                'item_category': tx.item_category.value,
                'quantity': tx.quantity,
                'notes': tx.notes,
                'confidence': tx.confidence,
                'raw_text': tx.raw_text,
                'price_analysis': {
                    'average_price': analysis.average_price,
                    'median_price': analysis.median_price,
                    'min_price': analysis.min_price,
                    'max_price': analysis.max_price,
                    'price_count': analysis.price_count,
                    'price_trend': analysis.price_trend,
                    'underpriced': False,
                    'overpriced': True
                }
            }
            transaction_dicts.append(tx_dict)
        
        return jsonify({
            'success': True,
            'transactions': transaction_dicts
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/vendor-ledger/duplicates")
def api_vendor_ledger_duplicates():
    """API endpoint for duplicate entries."""
    try:
        from core.vendor_transaction_ledger import vendor_ledger
        
        # Get transactions that have duplicates
        duplicate_transactions = []
        for dup in vendor_ledger.duplicate_entries:
            tx_dict = {
                'item_name': dup.duplicate_transaction.item_name,
                'price': dup.duplicate_transaction.price,
                'location': dup.duplicate_transaction.location,
                'seller': dup.duplicate_transaction.seller,
                'timestamp': dup.duplicate_transaction.timestamp,
                'transaction_type': dup.duplicate_transaction.transaction_type.value,
                'item_category': dup.duplicate_transaction.item_category.value,
                'quantity': dup.duplicate_transaction.quantity,
                'notes': dup.duplicate_transaction.notes,
                'confidence': dup.duplicate_transaction.confidence,
                'raw_text': dup.duplicate_transaction.raw_text,
                'duplicate_info': {
                    'similarity_score': dup.similarity_score,
                    'duplicate_type': dup.duplicate_type,
                    'original_timestamp': dup.original_transaction.timestamp
                }
            }
            duplicate_transactions.append(tx_dict)
        
        return jsonify({
            'success': True,
            'transactions': duplicate_transactions
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/vendor-ledger/price-analysis/<item_name>")
def api_vendor_ledger_price_analysis(item_name):
    """API endpoint for price analysis of an item."""
    try:
        from core.vendor_transaction_ledger import vendor_ledger
        analysis = vendor_ledger.get_price_comparison(item_name)
        
        if not analysis:
            return jsonify({
                'success': False,
                'error': f'No price analysis available for {item_name}'
            }), 404
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/vendor-ledger/log-transaction", methods=['POST'])
def api_vendor_ledger_log_transaction():
    """API endpoint to log a new vendor transaction."""
    try:
        from core.vendor_transaction_ledger import vendor_ledger, TransactionType, ItemCategory
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['item_name', 'price', 'location', 'seller']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Log the transaction
        transaction = vendor_ledger.log_transaction(
            item_name=data['item_name'],
            price=int(data['price']),
            location=data['location'],
            seller=data['seller'],
            transaction_type=TransactionType(data.get('transaction_type', 'observed')),
            item_category=ItemCategory(data.get('item_category', 'other')),
            quantity=int(data.get('quantity', 1)),
            notes=data.get('notes', ''),
            confidence=float(data.get('confidence', 1.0)),
            raw_text=data.get('raw_text', '')
        )
        
        return jsonify({
            'success': True,
            'transaction': {
                'item_name': transaction.item_name,
                'price': transaction.price,
                'location': transaction.location,
                'seller': transaction.seller,
                'timestamp': transaction.timestamp,
                'transaction_type': transaction.transaction_type.value,
                'item_category': transaction.item_category.value,
                'quantity': transaction.quantity,
                'notes': transaction.notes,
                'confidence': transaction.confidence,
                'raw_text': transaction.raw_text
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Batch 101 - Attribute Optimizer Routes
@app.route("/tools/attribute-planner")
def attribute_planner_page():
    """Attribute planner dashboard page."""
    return render_template("attribute_planner.html")


@app.route("/api/attribute-optimizer/optimize", methods=['POST'])
def api_attribute_optimizer_optimize():
    """API endpoint to optimize a character build."""
    try:
        from core.attribute_optimizer import attribute_optimizer, WeaponType, CombatRole, ResistanceType
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['build_name', 'weapon_type', 'combat_role']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        # Parse weapon type and combat role
        try:
            weapon_type = WeaponType(data['weapon_type'])
            combat_role = CombatRole(data['combat_role'])
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': f'Invalid weapon type or combat role: {e}'
            }), 400
        
        # Parse resistance focus
        resistance_focus = None
        if data.get('resistance_focus'):
            try:
                resistance_focus = [ResistanceType(res) for res in data['resistance_focus']]
            except ValueError as e:
                return jsonify({
                    'success': False,
                    'error': f'Invalid resistance type: {e}'
                }), 400
        
        # Generate optimization
        optimization = attribute_optimizer.optimize_build(
            build_name=data['build_name'],
            weapon_type=weapon_type,
            combat_role=combat_role,
            resistance_focus=resistance_focus
        )
        
        # Convert to dict for JSON serialization
        optimization_dict = {
            'build_name': optimization.build_name,
            'weapon_type': optimization.weapon_type.value,
            'combat_role': optimization.combat_role.value,
            'primary_attributes': optimization.primary_attributes,
            'armor_recommendation': {
                'build_name': optimization.armor_recommendation.build_name,
                'weapon_type': optimization.armor_recommendation.weapon_type.value,
                'combat_role': optimization.armor_recommendation.combat_role.value,
                'primary_stats': optimization.armor_recommendation.primary_stats,
                'secondary_stats': optimization.armor_recommendation.secondary_stats,
                'resistance_priorities': [r.value for r in optimization.armor_recommendation.resistance_priorities],
                'armor_slots': optimization.armor_recommendation.armor_slots,
                'reasoning': optimization.armor_recommendation.reasoning,
                'effectiveness_score': optimization.armor_recommendation.effectiveness_score
            },
            'buff_recommendations': [
                {
                    'buff_name': buff.buff_name,
                    'buff_type': buff.buff_type,
                    'primary_effect': buff.primary_effect,
                    'secondary_effects': buff.secondary_effects,
                    'duration': buff.duration,
                    'cost_estimate': buff.cost_estimate,
                    'availability': buff.availability,
                    'build_compatibility': buff.build_compatibility
                }
                for buff in optimization.buff_recommendations
            ],
            'food_recommendations': [
                {
                    'buff_name': buff.buff_name,
                    'buff_type': buff.buff_type,
                    'primary_effect': buff.primary_effect,
                    'secondary_effects': buff.secondary_effects,
                    'duration': buff.duration,
                    'cost_estimate': buff.cost_estimate,
                    'availability': buff.availability,
                    'build_compatibility': buff.build_compatibility
                }
                for buff in optimization.food_recommendations
            ],
            'resistance_focus': [r.value for r in optimization.resistance_focus],
            'overall_score': optimization.overall_score,
            'notes': optimization.notes
        }
        
        return jsonify({
            'success': True,
            'optimization': optimization_dict
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/attribute-optimizer/weapon-types")
def api_attribute_optimizer_weapon_types():
    """API endpoint to get available weapon types."""
    try:
        from core.attribute_optimizer import attribute_optimizer
        
        weapon_types = [
            {
                'value': wt.value,
                'name': wt.value.replace('_', ' ').title()
            }
            for wt in attribute_optimizer.get_available_weapon_types()
        ]
        
        return jsonify({
            'success': True,
            'weapon_types': weapon_types
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/attribute-optimizer/combat-roles")
def api_attribute_optimizer_combat_roles():
    """API endpoint to get available combat roles."""
    try:
        from core.attribute_optimizer import attribute_optimizer
        
        combat_roles = [
            {
                'value': cr.value,
                'name': cr.value.upper()
            }
            for cr in attribute_optimizer.get_available_combat_roles()
        ]
        
        return jsonify({
            'success': True,
            'combat_roles': combat_roles
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/attribute-optimizer/resistance-types")
def api_attribute_optimizer_resistance_types():
    """API endpoint to get available resistance types."""
    try:
        from core.attribute_optimizer import attribute_optimizer
        
        resistance_types = [
            {
                'value': rt.value,
                'name': rt.value.title()
            }
            for rt in attribute_optimizer.get_available_resistance_types()
        ]
        
        return jsonify({
            'success': True,
            'resistance_types': resistance_types
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/attribute-optimizer/attribute-effects")
def api_attribute_optimizer_attribute_effects():
    """API endpoint to get attribute effects."""
    try:
        from core.attribute_optimizer import attribute_optimizer
        
        effects = attribute_optimizer.get_attribute_effects()
        effects_dict = {}
        
        for attr, effect in effects.items():
            effects_dict[attr] = {
                'attribute': effect.attribute,
                'weapon_type': effect.weapon_type.value,
                'effect_type': effect.effect_type,
                'effect_value': effect.effect_value,
                'description': effect.description,
                'source_url': effect.source_url,
                'last_updated': effect.last_updated
            }
        
        return jsonify({
            'success': True,
            'attribute_effects': effects_dict
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/attribute-optimizer/weapon-attributes/<weapon_type>")
def api_attribute_optimizer_weapon_attributes(weapon_type):
    """API endpoint to get attributes for a weapon type."""
    try:
        from core.attribute_optimizer import attribute_optimizer, WeaponType
        
        try:
            wt = WeaponType(weapon_type)
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Invalid weapon type: {weapon_type}'
            }), 400
        
        attributes = attribute_optimizer.get_weapon_attributes(wt)
        
        return jsonify({
            'success': True,
            'weapon_type': weapon_type,
            'attributes': attributes
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/attribute-optimizer/role-priorities/<combat_role>")
def api_attribute_optimizer_role_priorities(combat_role):
    """API endpoint to get attribute priorities for a combat role."""
    try:
        from core.attribute_optimizer import attribute_optimizer, CombatRole
        
        try:
            cr = CombatRole(combat_role)
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'Invalid combat role: {combat_role}'
            }), 400
        
        priorities = attribute_optimizer.get_role_priorities(cr)
        
        return jsonify({
            'success': True,
            'combat_role': combat_role,
            'priorities': priorities
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Tools routes
@app.route("/tools")
def tools_page():
    """Player tools page."""
    return render_template("tools.html")


@app.route("/api/tools")
def api_tools():
    """API endpoint to get all tools."""
    try:
        tools = get_player_tools()
        stats = get_tools_stats()
        
        tools_data = []
        for tool in tools:
            tools_data.append({
                'id': tool.id,
                'name': tool.name,
                'category': tool.category.value,
                'description': tool.description,
                'url': tool.url,
                'author': tool.author,
                'tags': tool.tags,
                'notes': tool.notes,
                'views': tool.views,
                'created_at': tool.created_at.isoformat() if tool.created_at else None,
                'updated_at': tool.updated_at.isoformat() if tool.updated_at else None
            })
        
        return jsonify({
            'success': True,
            'tools': tools_data,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/tools/submit", methods=['POST'])
def api_submit_tool():
    """API endpoint to submit a new tool."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        success, message = submit_player_tool(data)
        
        return jsonify({
            'success': success,
            'message': message
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/tools/<tool_id>/view", methods=['POST'])
def api_tool_view(tool_id):
    """API endpoint to increment tool view count."""
    try:
        success = increment_tool_views(tool_id)
        
        return jsonify({
            'success': success
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/tools/<tool_id>/content")
def api_tool_content(tool_id):
    """API endpoint to get tool content (for markdown guides)."""
    try:
        content = get_tool_content(tool_id)
        
        if content is None:
            return jsonify({
                'success': False,
                'error': 'Tool not found or not a guide'
            }), 404
        
        return jsonify({
            'success': True,
            'content': content['content'],
            'type': content['type']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/tools/search")
def api_search_tools():
    """API endpoint to search tools."""
    try:
        query = request.args.get('q', '')
        category = request.args.get('category', '')
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Search query required'
            }), 400
        
        from core.tools_manager import ToolCategory
        search_category = None
        if category:
            try:
                search_category = ToolCategory(category)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': f'Invalid category: {category}'
                }), 400
        
        results = tools_manager.search_tools(query, search_category)
        
        tools_data = []
        for tool in results:
            tools_data.append({
                'id': tool.id,
                'name': tool.name,
                'category': tool.category.value,
                'description': tool.description,
                'url': tool.url,
                'author': tool.author,
                'tags': tool.tags,
                'views': tool.views,
                'created_at': tool.created_at.isoformat() if tool.created_at else None
            })
        
        return jsonify({
            'success': True,
            'tools': tools_data,
            'query': query,
            'category': category,
            'count': len(tools_data)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/tools/popular")
def api_popular_tools():
    """API endpoint to get popular tools."""
    try:
        limit = int(request.args.get('limit', 10))
        popular_tools = tools_manager.get_popular_tools(limit)
        
        tools_data = []
        for tool in popular_tools:
            tools_data.append({
                'id': tool.id,
                'name': tool.name,
                'category': tool.category.value,
                'description': tool.description,
                'url': tool.url,
                'author': tool.author,
                'views': tool.views,
                'created_at': tool.created_at.isoformat() if tool.created_at else None
            })
        
        return jsonify({
            'success': True,
            'tools': tools_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/tools/recent")
def api_recent_tools():
    """API endpoint to get recent tools."""
    try:
        limit = int(request.args.get('limit', 10))
        recent_tools = tools_manager.get_recent_tools(limit)
        
        tools_data = []
        for tool in recent_tools:
            tools_data.append({
                'id': tool.id,
                'name': tool.name,
                'category': tool.category.value,
                'description': tool.description,
                'url': tool.url,
                'author': tool.author,
                'views': tool.views,
                'created_at': tool.created_at.isoformat() if tool.created_at else None
            })
        
        return jsonify({
            'success': True,
            'tools': tools_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Build Optimizer Routes
@app.route("/tools/build-optimizer")
def build_optimizer_page():
    """Render the build optimizer page."""
    return render_template("build_optimizer.html")


@app.route("/api/build-optimizer/analyze", methods=['POST'])
def api_build_optimizer_analyze():
    """Analyze character build and return recommendations."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Convert data to CharacterStats object
        from core.build_optimizer import CharacterStats, CombatRole
        stats = CharacterStats(
            health=data.get('health', 0),
            action=data.get('action', 0),
            mind=data.get('mind', 0),
            strength=data.get('strength', 0),
            constitution=data.get('constitution', 0),
            agility=data.get('agility', 0),
            quickness=data.get('quickness', 0),
            stamina=data.get('stamina', 0),
            presence=data.get('presence', 0),
            focus=data.get('focus', 0),
            willpower=data.get('willpower', 0),
            combat_role=CombatRole(data.get('combat_role', 'dps')),
            level=data.get('level', 1),
            current_profession=data.get('current_profession'),
            respec_available=data.get('respec_available', False)
        )
        
        # Analyze the build
        result = analyze_character_build(stats)
        
        return jsonify(result.to_dict())
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/build-optimizer/professions", methods=['POST'])
def api_build_optimizer_professions():
    """Get profession recommendations for character stats."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Convert data to CharacterStats object
        from core.build_optimizer import CharacterStats, CombatRole
        stats = CharacterStats(
            health=data.get('health', 0),
            action=data.get('action', 0),
            mind=data.get('mind', 0),
            strength=data.get('strength', 0),
            constitution=data.get('constitution', 0),
            agility=data.get('agility', 0),
            quickness=data.get('quickness', 0),
            stamina=data.get('stamina', 0),
            presence=data.get('presence', 0),
            focus=data.get('focus', 0),
            willpower=data.get('willpower', 0),
            combat_role=CombatRole(data.get('combat_role', 'dps')),
            level=data.get('level', 1),
            current_profession=data.get('current_profession'),
            respec_available=data.get('respec_available', False)
        )
        
        # Get profession recommendations
        recommendations = get_profession_recommendations(stats)
        
        return jsonify({
            'success': True,
            'recommendations': [rec.to_dict() for rec in recommendations]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/build-optimizer/equipment", methods=['POST'])
def api_build_optimizer_equipment():
    """Get equipment recommendations for character stats."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Convert data to CharacterStats object
        from core.build_optimizer import CharacterStats, CombatRole
        stats = CharacterStats(
            health=data.get('health', 0),
            action=data.get('action', 0),
            mind=data.get('mind', 0),
            strength=data.get('strength', 0),
            constitution=data.get('constitution', 0),
            agility=data.get('agility', 0),
            quickness=data.get('quickness', 0),
            stamina=data.get('stamina', 0),
            presence=data.get('presence', 0),
            focus=data.get('focus', 0),
            willpower=data.get('willpower', 0),
            combat_role=CombatRole(data.get('combat_role', 'dps')),
            level=data.get('level', 1),
            current_profession=data.get('current_profession'),
            respec_available=data.get('respec_available', False)
        )
        
        # Get equipment recommendations
        recommendations = get_equipment_recommendations(stats)
        
        return jsonify({
            'success': True,
            'recommendations': [rec.to_dict() for rec in recommendations]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Mods Hub Routes
@app.route("/mods")
def mods_hub():
    """Main mods hub page."""
    return render_template("mods_hub.html")


@app.route("/mods/submit", methods=['GET', 'POST'])
def submit_mod():
    """Submit a new mod."""
    if request.method == 'POST':
        try:
            # Get form data
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            category = request.form.get('category', '')
            mod_type = request.form.get('mod_type', '')
            author = request.form.get('author', '').strip()
            author_email = request.form.get('author_email', '').strip()
            version = request.form.get('version', '1.0.0').strip()
            swg_version = request.form.get('swg_version', 'NGE').strip()
            download_url = request.form.get('download_url', '').strip()
            content = request.form.get('content', '').strip()
            tags = request.form.get('tags', '').strip()
            dependencies = request.form.get('dependencies', '').strip()
            installation_notes = request.form.get('installation_notes', '').strip()
            changelog = request.form.get('changelog', '').strip()
            
            # Validate required fields
            if not title or not description or not category or not mod_type or not author:
                flash('Please fill in all required fields.', 'error')
                return render_template("submit_mod.html")
            
            # Process tags and dependencies
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()] if tags else []
            dependency_list = [dep.strip() for dep in dependencies.split(',') if dep.strip()] if dependencies else []
            
            # Handle file upload
            file_path = None
            if 'mod_file' in request.files:
                file = request.files['mod_file']
                if file and file.filename:
                    # Save uploaded file
                    temp_path = os.path.join('/tmp', file.filename)
                    file.save(temp_path)
                    
                    # Validate file
                    is_valid, error_msg = mods_hub_manager.validate_file_upload(temp_path)
                    if not is_valid:
                        os.remove(temp_path)
                        flash(f'File upload error: {error_msg}', 'error')
                        return render_template("submit_mod.html")
                    
                    # Save to mods directory
                    file_path = mods_hub_manager.save_uploaded_file(temp_path, file.filename)
                    os.remove(temp_path)
            
            # Submit mod
            mod_id = mods_hub_manager.submit_mod(
                title=title,
                description=description,
                category=ModCategory(category),
                mod_type=ModType(mod_type),
                author=author,
                author_email=author_email if author_email else None,
                version=version,
                swg_version=swg_version,
                file_path=file_path,
                download_url=download_url if download_url else None,
                content=content if content else None,
                tags=tag_list,
                dependencies=dependency_list,
                installation_notes=installation_notes if installation_notes else None,
                changelog=changelog if changelog else None
            )
            
            flash(f'Mod submitted successfully! Your mod ID is: {mod_id}', 'success')
            return redirect(url_for('mods_hub'))
            
        except Exception as e:
            flash(f'Error submitting mod: {str(e)}', 'error')
            return render_template("submit_mod.html")
    
    return render_template("submit_mod.html")


@app.route("/mods/<mod_id>")
def mod_detail(mod_id):
    """View a specific mod."""
    mod = mods_hub_manager.get_mod(mod_id)
    if not mod:
        flash('Mod not found.', 'error')
        return redirect(url_for('mods_hub'))
    
    # Increment view count
    mods_hub_manager.increment_views(mod_id)
    
    return render_template("mod_detail.html", mod=mod)


@app.route("/mods/<mod_id>/download")
def download_mod(mod_id):
    """Download a mod file."""
    mod = mods_hub_manager.get_mod(mod_id)
    if not mod or not mod.file_path or not os.path.exists(mod.file_path):
        flash('File not found.', 'error')
        return redirect(url_for('mod_detail', mod_id=mod_id))
    
    # Increment download count
    mods_hub_manager.increment_downloads(mod_id)
    
    # Return file for download
    from flask import send_file
    return send_file(mod.file_path, as_attachment=True)


@app.route("/api/mods")
def api_mods():
    """Get mods with filtering."""
    try:
        category = request.args.get('category')
        search = request.args.get('search')
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Get approved mods
        mods = mods_hub_manager.get_approved_mods(
            category=ModCategory(category) if category else None,
            search=search,
            limit=limit,
            offset=offset
        )
        
        # Convert to dict for JSON serialization
        mods_data = []
        for mod in mods:
            mod_dict = {
                'id': mod.id,
                'title': mod.title,
                'description': mod.description,
                'category': mod.category.value,
                'mod_type': mod.mod_type.value,
                'author': mod.author,
                'version': mod.version,
                'swg_version': mod.swg_version,
                'tags': mod.tags,
                'views': mod.views,
                'downloads': mod.downloads,
                'rating': mod.rating,
                'rating_count': mod.rating_count,
                'featured': mod.featured,
                'submitted_at': mod.submitted_at,
                'approved_at': mod.approved_at
            }
            mods_data.append(mod_dict)
        
        return jsonify({
            'success': True,
            'mods': mods_data,
            'total': len(mods_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/mods/categories")
def api_mods_categories():
    """Get mod categories."""
    try:
        categories = mods_hub_manager.get_categories()
        categories_data = {}
        for cat_id, cat_info in categories.items():
            categories_data[cat_id] = {
                'id': cat_info.id,
                'name': cat_info.name,
                'description': cat_info.description,
                'icon': cat_info.icon,
                'color': cat_info.color,
                'mod_count': cat_info.mod_count
            }
        
        return jsonify({
            'success': True,
            'categories': categories_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/mods/popular")
def api_mods_popular():
    """Get popular mods."""
    try:
        limit = request.args.get('limit', 10, type=int)
        mods = mods_hub_manager.get_popular_mods(limit=limit)
        
        mods_data = []
        for mod in mods:
            mod_dict = {
                'id': mod.id,
                'title': mod.title,
                'description': mod.description,
                'category': mod.category.value,
                'author': mod.author,
                'views': mod.views,
                'downloads': mod.downloads,
                'rating': mod.rating
            }
            mods_data.append(mod_dict)
        
        return jsonify({
            'success': True,
            'mods': mods_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/mods/recent")
def api_mods_recent():
    """Get recent mods."""
    try:
        limit = request.args.get('limit', 10, type=int)
        mods = mods_hub_manager.get_recent_mods(limit=limit)
        
        mods_data = []
        for mod in mods:
            mod_dict = {
                'id': mod.id,
                'title': mod.title,
                'description': mod.description,
                'category': mod.category.value,
                'author': mod.author,
                'submitted_at': mod.submitted_at,
                'approved_at': mod.approved_at
            }
            mods_data.append(mod_dict)
        
        return jsonify({
            'success': True,
            'mods': mods_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/mods/featured")
def api_mods_featured():
    """Get featured mods."""
    try:
        mods = mods_hub_manager.get_featured_mods()
        
        mods_data = []
        for mod in mods:
            mod_dict = {
                'id': mod.id,
                'title': mod.title,
                'description': mod.description,
                'category': mod.category.value,
                'author': mod.author,
                'rating': mod.rating
            }
            mods_data.append(mod_dict)
        
        return jsonify({
            'success': True,
            'mods': mods_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/mods/stats")
def api_mods_stats():
    """Get mods hub statistics."""
    try:
        stats = mods_hub_manager.get_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/mods/<mod_id>/rate", methods=['POST'])
def api_rate_mod(mod_id):
    """Rate a mod."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        rating = data.get('rating')
        user_id = data.get('user_id', 'anonymous')
        
        if not rating or not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
            return jsonify({
                'success': False,
                'error': 'Invalid rating. Must be between 1 and 5.'
            }), 400
        
        success = mods_hub_manager.rate_mod(mod_id, float(rating), user_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Rating submitted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to submit rating'
            }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Admin routes for mod approval
@app.route("/admin/mods")
def admin_mods():
    """Admin mods management page."""
    return render_template("admin_mods.html")


@app.route("/api/admin/mods/pending")
def api_admin_pending_mods():
    """Get pending mods for approval."""
    try:
        mods = mods_hub_manager.get_pending_mods()
        
        mods_data = []
        for mod in mods:
            mod_dict = {
                'id': mod.id,
                'title': mod.title,
                'description': mod.description,
                'category': mod.category.value,
                'mod_type': mod.mod_type.value,
                'author': mod.author,
                'author_email': mod.author_email,
                'version': mod.version,
                'swg_version': mod.swg_version,
                'tags': mod.tags,
                'dependencies': mod.dependencies,
                'installation_notes': mod.installation_notes,
                'changelog': mod.changelog,
                'submitted_at': mod.submitted_at,
                'file_size': mod.file_size,
                'download_url': mod.download_url,
                'content': mod.content
            }
            mods_data.append(mod_dict)
        
        return jsonify({
            'success': True,
            'mods': mods_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/admin/mods/<mod_id>/approve", methods=['POST'])
def api_admin_approve_mod(mod_id):
    """Approve a mod."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        approved_by = data.get('approved_by', 'admin')
        rejection_reason = data.get('rejection_reason')
        
        success = mods_hub_manager.approve_mod(mod_id, approved_by, rejection_reason)
        
        if success:
            action = "rejected" if rejection_reason else "approved"
            return jsonify({
                'success': True,
                'message': f'Mod {action} successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to approve/reject mod'
            }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/admin/mods/<mod_id>/feature", methods=['POST'])
def api_admin_feature_mod(mod_id):
    """Feature/unfeature a mod."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        featured = data.get('featured', False)
        
        success = mods_hub_manager.set_featured(mod_id, featured)
        
        if success:
            action = "featured" if featured else "unfeatured"
            return jsonify({
                'success': True,
                'message': f'Mod {action} successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to feature/unfeature mod'
            }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/admin/mods/<mod_id>/delete", methods=['POST'])
def api_admin_delete_mod(mod_id):
    """Delete a mod."""
    try:
        success = mods_hub_manager.delete_mod(mod_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Mod deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to delete mod'
            }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Quest Tracker Routes
@app.route("/tools/quest-tracker")
def quest_tracker_page():
    """Main quest tracker page."""
    return render_template("quest_tracker.html")


@app.route("/tools/quest-tracker/widget")
def quest_tracker_widget():
    """Quest tracker widget for embedding."""
    return render_template("quest_tracker_widget.html")


@app.route("/api/quest-tracker/quests")
def api_quest_tracker_quests():
    """Get quests with filtering."""
    try:
        # Get filter parameters
        categories = request.args.getlist('categories')
        difficulties = request.args.getlist('difficulties')
        planets = request.args.getlist('planets')
        reward_types = request.args.getlist('reward_types')
        level_min = request.args.get('level_min', type=int)
        level_max = request.args.get('level_max', type=int)
        search_term = request.args.get('search', '')
        tags = request.args.getlist('tags')
        
        # Create filter
        quest_filter = QuestFilter()
        if categories:
            quest_filter.categories = [QuestCategory(cat) for cat in categories]
        if difficulties:
            quest_filter.difficulties = [QuestDifficulty(diff) for diff in difficulties]
        if planets:
            quest_filter.planets = [Planet(planet) for planet in planets]
        if reward_types:
            quest_filter.reward_types = [RewardType(rt) for rt in reward_types]
        if level_min is not None and level_max is not None:
            quest_filter.level_range = (level_min, level_max)
        if search_term:
            quest_filter.search_term = search_term
        if tags:
            quest_filter.tags = tags
        
        # Filter quests
        filtered_quests = quest_tracker.filter_quests(quest_filter)
        
        # Convert to JSON-serializable format
        quests_data = []
        for quest in filtered_quests:
            stats = quest_tracker.get_quest_statistics(quest.quest_id)
            quest_data = quest.to_dict()
            quest_data['statistics'] = stats.to_dict() if stats else None
            quests_data.append(quest_data)
        
        return jsonify({
            'success': True,
            'quests': quests_data,
            'total_count': len(quests_data)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/quest-tracker/quest/<quest_id>")
def api_quest_tracker_quest_detail(quest_id):
    """Get detailed information about a specific quest."""
    try:
        quest = quest_tracker.get_quest(quest_id)
        if not quest:
            return jsonify({
                'success': False,
                'error': 'Quest not found'
            }), 404
        
        stats = quest_tracker.get_quest_statistics(quest_id)
        progress_list = quest_tracker.get_quest_progress(quest_id)
        
        quest_data = quest.to_dict()
        quest_data['statistics'] = stats.to_dict() if stats else None
        quest_data['progress'] = [p.to_dict() for p in progress_list]
        
        return jsonify({
            'success': True,
            'quest': quest_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/quest-tracker/progress", methods=['POST'])
def api_quest_tracker_update_progress():
    """Update quest progress for a user."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        user_id = data.get('user_id')
        quest_id = data.get('quest_id')
        status = data.get('status')
        current_step = data.get('current_step', 0)
        steps_completed = data.get('steps_completed', [])
        notes = data.get('notes', '')
        
        if not user_id or not quest_id or not status:
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        # Create progress object
        progress = QuestProgress(
            quest_id=quest_id,
            status=QuestStatus(status),
            current_step=current_step,
            steps_completed=steps_completed,
            notes=notes
        )
        
        # Set timestamps
        if status == QuestStatus.IN_PROGRESS.value:
            progress.start_time = datetime.now()
        elif status == QuestStatus.COMPLETED.value:
            progress.completion_time = datetime.now()
            # Calculate total time if start time exists
            existing_progress = None
            for p in quest_tracker.get_user_progress(user_id):
                if p.quest_id == quest_id:
                    existing_progress = p
                    break
            if existing_progress and existing_progress.start_time:
                total_minutes = (progress.completion_time - existing_progress.start_time).total_seconds() / 60
                progress.total_time = int(total_minutes)
        
        # Update progress
        success = quest_tracker.update_progress(user_id, quest_id, progress)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Progress updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to update progress'
            }), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/quest-tracker/user-progress/<user_id>")
def api_quest_tracker_user_progress(user_id):
    """Get all quest progress for a user."""
    try:
        progress_list = quest_tracker.get_user_progress(user_id)
        
        # Add quest details to progress
        progress_data = []
        for progress in progress_list:
            quest = quest_tracker.get_quest(progress.quest_id)
            progress_item = progress.to_dict()
            progress_item['quest'] = quest.to_dict() if quest else None
            progress_data.append(progress_item)
        
        return jsonify({
            'success': True,
            'progress': progress_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/quest-tracker/popular")
def api_quest_tracker_popular():
    """Get popular quests."""
    try:
        limit = request.args.get('limit', 10, type=int)
        popular_quests = quest_tracker.get_popular_quests(limit)
        
        quests_data = []
        for quest, stats in popular_quests:
            quest_data = quest.to_dict()
            quest_data['statistics'] = stats.to_dict()
            quests_data.append(quest_data)
        
        return jsonify({
            'success': True,
            'quests': quests_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/quest-tracker/recent-activity")
def api_quest_tracker_recent_activity():
    """Get recent quest activity."""
    try:
        hours = request.args.get('hours', 24, type=int)
        recent_activity = quest_tracker.get_recent_activity(hours)
        
        activity_data = []
        for activity in recent_activity:
            activity_item = {
                'user_id': activity['user_id'],
                'quest': activity['quest'].to_dict(),
                'progress': activity['progress'].to_dict(),
                'completion_time': activity['completion_time'].isoformat()
            }
            activity_data.append(activity_item)
        
        return jsonify({
            'success': True,
            'activity': activity_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/quest-tracker/statistics")
def api_quest_tracker_statistics():
    """Get overall quest tracker statistics."""
    try:
        stats = quest_tracker.get_overall_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/quest-tracker/categories")
def api_quest_tracker_categories():
    """Get available quest categories."""
    try:
        categories = [cat.value for cat in QuestCategory]
        difficulties = [diff.value for diff in QuestDifficulty]
        planets = [planet.value for planet in Planet]
        reward_types = [rt.value for rt in RewardType]
        
        return jsonify({
            'success': True,
            'categories': categories,
            'difficulties': difficulties,
            'planets': planets,
            'reward_types': reward_types
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/quest-tracker/widget-data")
def api_quest_tracker_widget_data():
    """Get data for the homepage widget."""
    try:
        # Get popular quests
        popular_quests = quest_tracker.get_popular_quests(5)
        
        # Get recent activity
        recent_activity = quest_tracker.get_recent_activity(6)
        
        # Get overall stats
        stats = quest_tracker.get_overall_statistics()
        
        widget_data = {
            'popular_quests': [],
            'recent_activity': [],
            'statistics': stats
        }
        
        # Format popular quests
        for quest, quest_stats in popular_quests:
            widget_data['popular_quests'].append({
                'id': quest.quest_id,
                'name': quest.name,
                'category': quest.category.value,
                'difficulty': quest.difficulty.value,
                'planet': quest.planet.value,
                'popularity_score': quest_stats.popularity_score,
                'current_players': quest_stats.current_players
            })
        
        # Format recent activity
        for activity in recent_activity[:5]:  # Limit to 5 recent activities
            widget_data['recent_activity'].append({
                'user_id': activity['user_id'],
                'quest_name': activity['quest'].name,
                'category': activity['quest'].category.value,
                'completion_time': activity['completion_time'].isoformat()
            })
        
        return jsonify({
            'success': True,
            'widget_data': widget_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Gear Optimizer API Endpoints
@app.route("/gear-optimizer")
def gear_optimizer_page():
    """Display the gear optimizer page."""
    return render_template("gear_optimizer.html")


@app.route("/api/gear/optimize", methods=['POST'])
def api_gear_optimize():
    """API endpoint for gear optimization."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        character_name = data.get('character_name')
        build_id = data.get('build_id')
        optimization_type = data.get('optimization_type', 'balanced')
        budget = data.get('budget', 'medium')
        
        if not character_name or not build_id:
            return jsonify({
                'success': False,
                'error': 'Character name and build ID are required'
            }), 400
        
        # Get gear advisor
        gear_advisor = get_gear_advisor()
        
        # Get character profile from stat extractor
        from ocr.stat_extractor import get_stat_extractor
        stat_extractor = get_stat_extractor()
        
        # Load or create character profile
        character_profile = stat_extractor.load_character_profile(character_name)
        if not character_profile:
            # Create a default profile for testing
            character_profile = stat_extractor.create_character_profile(character_name, "Rifleman", 50)
        
        # Convert optimization type string to enum
        opt_type_map = {
            'balanced': OptimizationType.BALANCED,
            'dps': OptimizationType.DPS,
            'tank': OptimizationType.TANK,
            'support': OptimizationType.SUPPORT,
            'combat': OptimizationType.COMBAT
        }
        
        optimization_enum = opt_type_map.get(optimization_type, OptimizationType.BALANCED)
        
        # Run optimization
        result = gear_advisor.analyze_gear_optimization(
            character_profile=character_profile,
            build_id=build_id,
            optimization_type=optimization_enum,
            budget=budget
        )
        
        # Convert result to serializable format
        result_dict = {
            "character_name": result.character_name,
            "build_id": result.build_id,
            "optimization_type": result.optimization_type.value,
            "current_stats": result.current_stats,
            "target_stats": result.target_stats,
            "recommendations": [
                {
                    "slot": rec.slot.value,
                    "current_item": rec.current_item,
                    "recommended_item": rec.recommended_item,
                    "improvement_score": rec.improvement_score,
                    "stat_gains": rec.stat_gains,
                    "resist_gains": rec.resist_gains,
                    "enhancement_slots": rec.enhancement_slots,
                    "recommended_enhancements": rec.recommended_enhancements,
                    "cost": rec.cost,
                    "priority": rec.priority,
                    "reasoning": rec.reasoning
                }
                for rec in result.recommendations
            ],
            "overall_improvement": result.overall_improvement,
            "total_cost": result.total_cost,
            "implementation_priority": result.implementation_priority,
            "notes": result.notes,
            "timestamp": result.timestamp.isoformat()
        }
        
        return jsonify(result_dict)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/gear/armor-sets")
def api_gear_armor_sets():
    """Get available armor sets."""
    try:
        gear_advisor = get_gear_advisor()
        
        # Return armor sets data
        armor_sets = {}
        for set_id, set_data in gear_advisor.armor_sets.items():
            armor_sets[set_id] = {
                "name": set_data["name"],
                "type": set_data["type"],
                "profession": set_data["profession"],
                "cost": set_data["cost"],
                "combat_style": set_data["combat_style"],
                "specialization": set_data["specialization"]
            }
        
        return jsonify({
            'success': True,
            'armor_sets': armor_sets
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/gear/enhancements")
def api_gear_enhancements():
    """Get available enhancements."""
    try:
        gear_advisor = get_gear_advisor()
        
        # Return enhancements data
        enhancements = {}
        for enh_id, enh_data in gear_advisor.enhancements.items():
            enhancements[enh_id] = {
                "name": enh_data["name"],
                "type": enh_data["type"],
                "stats": enh_data["stats"],
                "cost": enh_data["cost"]
            }
        
        return jsonify({
            'success': True,
            'enhancements': enhancements
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/gear/builds")
def api_gear_builds():
    """Get available builds for gear optimization."""
    try:
        build_loader = get_build_loader()
        builds = build_loader.get_all_builds()
        
        build_list = []
        for build_id, build_data in builds.items():
            build_list.append({
                "id": build_id,
                "name": build_data.name,
                "category": build_data.category.value,
                "specialization": build_data.specialization.value,
                "difficulty": build_data.difficulty.value
            })
        
        return jsonify({
            'success': True,
            'builds': build_list
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/swg-armory")
def swg_armory():
    """SWG Armory main page."""
    return render_template("swg_armory.html")


@app.route("/swgdb_site/pages/builds/index.html")
def swgdb_builds_index():
    """Serve the SWGDB builds index page."""
    return render_template("swgdb_builds_index.html")


@app.route("/swgdb_site/pages/builds/<build_id>.html")
def swgdb_build_detail(build_id):
    """Serve individual build detail pages."""
    return render_template("swgdb_build_detail.html", build_id=build_id)


@app.route("/api/loot/recent")
def api_loot_recent():
    """Get recent loot items."""
    try:
        item_scanner = get_item_scanner()
        recent_loot = item_scanner.get_recent_loot(limit=20)
        
        # Convert to JSON-serializable format
        loot_data = []
        for item in recent_loot:
            loot_data.append({
                'item_id': item.item_id,
                'item_name': item.item_name,
                'quantity': item.quantity,
                'rarity': item.rarity.value,
                'source_type': item.source_type.value,
                'source_name': item.source_name,
                'location': item.location,
                'coordinates': item.coordinates,
                'timestamp': item.timestamp.isoformat(),
                'session_id': item.session_id,
                'character_name': item.character_name,
                'combat_log_match': item.combat_log_match,
                'ocr_confidence': item.ocr_confidence,
                'macro_detected': item.macro_detected
            })
        
        return jsonify({
            'success': True,
            'items': loot_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route("/api/loot/tables")
def api_loot_tables():
    """Get all loot tables."""
    try:
        item_scanner = get_item_scanner()
        loot_tables = item_scanner.get_all_loot_tables()
        
        # Convert to JSON-serializable format
        tables_data = {}
        for source_name, table in loot_tables.items():
            tables_data[source_name] = {
                'source_name': table.source_name,
                'source_type': table.source_type.value,
                'total_kills': table.total_kills,
                'total_loot': table.total_loot,
                'last_updated': table.last_updated.isoformat(),
                'items': table.items,
                'drop_rates': table.drop_rates,
                'rarity_distribution': table.rarity_distribution
            }
        
        return jsonify({
            'success': True,
            'tables': tables_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route("/api/loot/statistics")
def api_loot_statistics():
    """Get loot statistics."""
    try:
        item_scanner = get_item_scanner()
        stats = item_scanner.get_loot_statistics()
        
        return jsonify({
            'success': True,
            **stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route("/api/loot/search")
def api_loot_search():
    """Search for loot items."""
    try:
        query = request.args.get('q', '')
        source_name = request.args.get('source', None)
        
        item_scanner = get_item_scanner()
        results = item_scanner.search_loot(query, source_name)
        
        # Convert to JSON-serializable format
        loot_data = []
        for item in results:
            loot_data.append({
                'item_id': item.item_id,
                'item_name': item.item_name,
                'quantity': item.quantity,
                'rarity': item.rarity.value,
                'source_type': item.source_type.value,
                'source_name': item.source_name,
                'location': item.location,
                'coordinates': item.coordinates,
                'timestamp': item.timestamp.isoformat(),
                'session_id': item.session_id,
                'character_name': item.character_name,
                'combat_log_match': item.combat_log_match,
                'ocr_confidence': item.ocr_confidence,
                'macro_detected': item.macro_detected
            })
        
        return jsonify({
            'success': True,
            'items': loot_data,
            'query': query,
            'source': source_name
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route("/api/loot/source/<source_name>")
def api_loot_source_statistics(source_name):
    """Get statistics for a specific source."""
    try:
        item_scanner = get_item_scanner()
        stats = item_scanner.get_source_statistics(source_name)
        
        if not stats:
            return jsonify({
                'success': False,
                'error': f'Source "{source_name}" not found'
            }), 404
        
        return jsonify({
            'success': True,
            **stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route("/api/loot/monitoring/start", methods=['POST'])
def api_loot_monitoring_start():
    """Start loot monitoring."""
    try:
        item_scanner = get_item_scanner()
        item_scanner.start_monitoring()
        
        return jsonify({
            'success': True,
            'message': 'Loot monitoring started'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route("/api/loot/monitoring/stop", methods=['POST'])
def api_loot_monitoring_stop():
    """Stop loot monitoring."""
    try:
        item_scanner = get_item_scanner()
        item_scanner.stop_monitoring()
        
        return jsonify({
            'success': True,
            'message': 'Loot monitoring stopped'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route("/api/loot/monitoring/status")
def api_loot_monitoring_status():
    """Get loot monitoring status."""
    try:
        item_scanner = get_item_scanner()
        
        return jsonify({
            'success': True,
            'monitoring': item_scanner.monitoring,
            'active_sessions': len(item_scanner.active_sessions),
            'recent_loot_count': len(item_scanner.recent_loot)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Batch 159 - Vendor History Sync View API Endpoints

@app.route("/dashboard/loot-history/")
def vendor_history_page():
    """Vendor History Dashboard page."""
    return render_template("loot_history.html")


@app.route("/api/vendor-history/data")
def api_vendor_history_data():
    """Get vendor history data with filtering and pagination."""
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 25))
        item_name = request.args.get('item_name', '').strip() or None
        category = request.args.get('category', '').strip() or None
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        seller = request.args.get('seller', '').strip() or None
        location = request.args.get('location', '').strip() or None
        start_date = request.args.get('start_date', '').strip() or None
        end_date = request.args.get('end_date', '').strip() or None
        
        # Parse price filters
        min_price = int(min_price) if min_price and min_price.isdigit() else None
        max_price = int(max_price) if max_price and max_price.isdigit() else None
        
        # Create filter object
        filters = VendorHistoryFilter(
            item_name=item_name,
            category=category,
            min_price=min_price,
            max_price=max_price,
            seller=seller,
            location=location,
            start_date=start_date,
            end_date=end_date
        )
        
        # Get vendor history manager
        vendor_manager = get_vendor_history_manager()
        
        # Get filtered and paginated data
        entries, total_count = vendor_manager.get_vendor_history(filters, page, page_size)
        
        # Convert entries to JSON-serializable format
        data = []
        for entry in entries:
            data.append({
                'item_name': entry.item_name,
                'credits': entry.credits,
                'seller': entry.seller,
                'location': entry.location,
                'timestamp': entry.timestamp,
                'category': entry.category,
                'source': entry.source,
                'quality': entry.quality,
                'notes': entry.notes
            })
        
        return jsonify({
            'success': True,
            'data': data,
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/vendor-history/stats")
def api_vendor_history_stats():
    """Get vendor history statistics."""
    try:
        # Get query parameters for filtering
        item_name = request.args.get('item_name', '').strip() or None
        category = request.args.get('category', '').strip() or None
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        seller = request.args.get('seller', '').strip() or None
        location = request.args.get('location', '').strip() or None
        start_date = request.args.get('start_date', '').strip() or None
        end_date = request.args.get('end_date', '').strip() or None
        
        # Parse price filters
        min_price = int(min_price) if min_price and min_price.isdigit() else None
        max_price = int(max_price) if max_price and max_price.isdigit() else None
        
        # Create filter object
        filters = VendorHistoryFilter(
            item_name=item_name,
            category=category,
            min_price=min_price,
            max_price=max_price,
            seller=seller,
            location=location,
            start_date=start_date,
            end_date=end_date
        )
        
        # Get vendor history manager
        vendor_manager = get_vendor_history_manager()
        
        # Get statistics
        stats = vendor_manager.get_vendor_history_stats(filters)
        
        return jsonify({
            'success': True,
            'stats': {
                'total_items': stats.total_items,
                'total_vendors': stats.total_vendors,
                'total_locations': stats.total_locations,
                'total_categories': stats.total_categories,
                'average_price': round(stats.average_price, 2),
                'min_price': stats.min_price,
                'max_price': stats.max_price,
                'date_range': stats.date_range
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/vendor-history/filters")
def api_vendor_history_filters():
    """Get available filter options for vendor history."""
    try:
        vendor_manager = get_vendor_history_manager()
        
        return jsonify({
            'success': True,
            'categories': vendor_manager.get_categories(),
            'vendors': vendor_manager.get_vendors(),
            'locations': vendor_manager.get_locations()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/vendor-history/export")
def api_vendor_history_export():
    """Export vendor history data."""
    try:
        # Get query parameters for filtering
        item_name = request.args.get('item_name', '').strip() or None
        category = request.args.get('category', '').strip() or None
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')
        seller = request.args.get('seller', '').strip() or None
        location = request.args.get('location', '').strip() or None
        start_date = request.args.get('start_date', '').strip() or None
        end_date = request.args.get('end_date', '').strip() or None
        export_format = request.args.get('format', 'json').lower()
        
        # Parse price filters
        min_price = int(min_price) if min_price and min_price.isdigit() else None
        max_price = int(max_price) if max_price and max_price.isdigit() else None
        
        # Create filter object
        filters = VendorHistoryFilter(
            item_name=item_name,
            category=category,
            min_price=min_price,
            max_price=max_price,
            seller=seller,
            location=location,
            start_date=start_date,
            end_date=end_date
        )
        
        # Get vendor history manager
        vendor_manager = get_vendor_history_manager()
        
        # Export data
        exported_data = vendor_manager.export_vendor_history(filters, export_format)
        
        # Set response headers
        if export_format == 'csv':
            from flask import Response
            return Response(
                exported_data,
                mimetype='text/csv',
                headers={'Content-Disposition': 'attachment; filename=vendor_history.csv'}
            )
        else:
            return jsonify({
                'success': True,
                'data': exported_data
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# Build Optimizer v2 Routes (GCW + Attributes-Aware)
@app.route("/tools/build-optimizer-v2")
def build_optimizer_v2_page():
    """Render the build optimizer v2 page."""
    return render_template("build_optimizer_v2.html")


@app.route("/api/build-optimizer-v2/optimize", methods=['POST'])
def api_build_optimizer_v2_optimize():
    """Optimize character build using GCW calculator & Attributes logic."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Import the new optimizer
        from optimizer.build_optimizer_v2 import (
            get_build_optimizer_v2, OptimizationRole, GCWRole
        )
        
        # Create mock character profile from data
        class MockCharacterProfile:
            def __init__(self, name, stats):
                self.name = name
                self.stats = stats
            
            def get_stat(self, stat_type):
                return self.stats.get(stat_type.value, 0)
            
            def get_health(self):
                return self.stats.get('health', 0)
            
            def get_stamina(self):
                return self.stats.get('stamina', 0)
            
            def get_force_power(self):
                return self.stats.get('force_power', 0)
            
            def get_mental_resistance(self):
                return self.stats.get('mental_resistance', 0)
        
        # Extract character data
        character_name = data.get('character_name', 'Unknown')
        stats = data.get('stats', {})
        selected_role = OptimizationRole(data.get('selected_role', 'dps'))
        gcw_role = GCWRole(data.get('gcw_role')) if data.get('gcw_role') else None
        budget = data.get('budget', 'medium')
        
        # Create character profile
        character_profile = MockCharacterProfile(character_name, stats)
        
        # Get optimizer and perform optimization
        optimizer = get_build_optimizer_v2()
        result = optimizer.optimize_build(
            character_profile, selected_role, gcw_role, budget
        )
        
        # Convert result to JSON-serializable format
        result_dict = {
            'character_name': result.character_name,
            'selected_role': result.selected_role.value,
            'gcw_role': result.gcw_role.value if result.gcw_role else None,
            'current_stats': result.current_stats,
            'target_stats': result.target_stats,
            'attribute_breakpoints': [
                {
                    'attribute': bp.attribute,
                    'current_value': bp.current_value,
                    'target_value': bp.target_value,
                    'breakpoint_value': bp.breakpoint_value,
                    'improvement_potential': bp.improvement_potential,
                    'priority': bp.priority.value,
                    'reasoning': bp.reasoning
                } for bp in result.attribute_breakpoints
            ],
            'armor_recommendations': [
                {
                    'slot': rec.slot,
                    'current_item': rec.current_item,
                    'recommended_item': rec.recommended_item,
                    'resist_gains': rec.resist_gains,
                    'stat_gains': rec.stat_gains,
                    'cost': rec.cost,
                    'priority': rec.priority.value,
                    'reasoning': rec.reasoning
                } for rec in result.armor_recommendations
            ],
            'enhancement_recommendations': [
                {
                    'type': rec.type,
                    'name': rec.name,
                    'effect': rec.effect,
                    'duration': rec.duration,
                    'cost': rec.cost,
                    'priority': rec.priority.value,
                    'reasoning': rec.reasoning
                } for rec in result.enhancement_recommendations
            ],
            'gcw_optimization': {
                'role': result.gcw_optimization.role.value,
                'current_rank': result.gcw_optimization.current_rank,
                'target_rank': result.gcw_optimization.target_rank,
                'required_attributes': result.gcw_optimization.required_attributes,
                'recommended_gear': result.gcw_optimization.recommended_gear,
                'strategy_notes': result.gcw_optimization.strategy_notes
            } if result.gcw_optimization else None,
            'overall_improvement': result.overall_improvement,
            'total_cost': result.total_cost,
            'implementation_priority': result.implementation_priority,
            'tradeoffs': result.tradeoffs,
            'links': result.links,
            'timestamp': result.timestamp.isoformat()
        }
        
        return jsonify({
            'success': True,
            'result': result_dict
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/build-optimizer-v2/roles")
def api_build_optimizer_v2_roles():
    """Get available optimization roles."""
    try:
        from optimizer.build_optimizer_v2 import OptimizationRole, GCWRole
        
        return jsonify({
            'success': True,
            'optimization_roles': [role.value for role in OptimizationRole],
            'gcw_roles': [role.value for role in GCWRole]
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route("/api/build-optimizer-v2/history/<character_name>")
def api_build_optimizer_v2_history(character_name):
    """Get optimization history for a character."""
    try:
        from optimizer.build_optimizer_v2 import get_build_optimizer_v2
        
        optimizer = get_build_optimizer_v2()
        history = optimizer._load_optimization_history(character_name)
        
        return jsonify({
            'success': True,
            'history': history
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# MS11 Dashboard Routes
@app.route("/ms11")
def ms11_dashboard():
    """MS11 Dashboard - requires Discord authentication and license."""
    # Check if user is authenticated via Discord
    discord_profile = session.get('discord_profile')
    if not discord_profile:
        flash("Please login with Discord to access MS11 dashboard", "warning")
        return redirect(url_for('ms11_login'))
    
    # Check if user has MS11 license
    discord_id = discord_profile.get('discord_id')
    if not discord_id or not ms11_license_manager.is_user_authorized(discord_id):
        flash("Access denied. You need an MS11 license to access this dashboard.", "error")
        return redirect(url_for('ms11_license_required'))
    
    # Update license usage
    ms11_license_manager.update_license_usage(discord_id)
    
    # Get user's license info
    license_info = ms11_license_manager.get_user_license(discord_id)
    
    return render_template('ms11/dashboard.html', 
                         user=discord_profile, 
                         license_info=license_info)


@app.route("/ms11/login")
def ms11_login():
    """MS11 login page with Discord authentication."""
    return render_template('ms11/login.html')


@app.route("/ms11/license-required")
def ms11_license_required():
    """Page shown when user doesn't have MS11 license."""
    return render_template('ms11/license_required.html')


@app.route("/ms11/auth/discord")
def ms11_discord_auth():
    """Initiate Discord authentication for MS11."""
    # Load Discord OAuth config
    try:
        with open('config/discord_oauth.json', 'r') as f:
            discord_config = json.load(f)
        
        discord_client_id = discord_config['client_id']
        redirect_uri = discord_config['redirect_uri']
        scope = discord_config['scope']
        
        auth_url = f"https://discord.com/api/oauth2/authorize?client_id={discord_client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scope}"
        return redirect(auth_url)
    except Exception as e:
        flash(f"Discord configuration error: {str(e)}", "error")
        return redirect(url_for('ms11_login'))


@app.route("/ms11/auth/discord/callback")
def ms11_discord_callback():
    """Discord OAuth callback for MS11 authentication."""
    try:
        code = request.args.get('code')
        if not code:
            flash("Discord authentication failed: Missing authorization code", "error")
            return redirect(url_for('ms11_login'))
        
        # Load Discord OAuth config
        with open('config/discord_oauth.json', 'r') as f:
            discord_config = json.load(f)
        
        # Exchange code for access token
        token_data = {
            'client_id': discord_config['client_id'],
            'client_secret': discord_config['client_secret'],
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': discord_config['redirect_uri']
        }
        
        import requests
        
        # Exchange code for access token
        token_response = requests.post(discord_config['token_url'], data=token_data)
        if token_response.status_code != 200:
            flash("Discord authentication failed: Could not exchange code for token", "error")
            return redirect(url_for('ms11_login'))
        
        token_info = token_response.json()
        access_token = token_info.get('access_token')
        
        if not access_token:
            flash("Discord authentication failed: No access token received", "error")
            return redirect(url_for('ms11_login'))
        
        # Get user information from Discord
        headers = {'Authorization': f'Bearer {access_token}'}
        user_response = requests.get(discord_config['user_url'], headers=headers)
        
        if user_response.status_code != 200:
            flash("Discord authentication failed: Could not get user information", "error")
            return redirect(url_for('ms11_login'))
        
        discord_user_data = user_response.json()
        
        # Store in session
        session['discord_profile'] = {
            'discord_id': discord_user_data['id'],
            'username': discord_user_data['username'],
            'avatar': discord_user_data.get('avatar'),
            'discriminator': discord_user_data.get('discriminator', '0')
        }
        session['discord_authenticated'] = True
        
        # Check if user has MS11 license
        if ms11_license_manager.is_user_authorized(discord_user_data['id']):
            flash(f"Welcome back, {discord_user_data['username']}!", "success")
            return redirect(url_for('ms11_dashboard'))
        else:
            flash("Discord authentication successful, but you need an MS11 license to access the dashboard.", "warning")
            return redirect(url_for('ms11_license_required'))
            
    except Exception as e:
        flash(f"Discord authentication error: {str(e)}", "error")
        return redirect(url_for('ms11_login'))


@app.route("/ms11/api/status")
def ms11_api_status():
    """API endpoint to get MS11 system status."""
    try:
        # Check if user is authorized
        discord_profile = session.get('discord_profile')
        if not discord_profile:
            return jsonify({"success": False, "error": "Not authenticated"}), 401
        
        discord_id = discord_profile.get('discord_id')
        if not ms11_license_manager.is_user_authorized(discord_id):
            return jsonify({"success": False, "error": "Not authorized"}), 403
        
        # Get MS11 system status
        status = {
            "system_status": "online",
            "last_updated": datetime.now().isoformat(),
            "active_sessions": 0,  # Replace with actual session count
            "available_modes": ["medic", "quest", "combat", "crafting", "dancer", "whisper", "support", "follow", "bounty", "entertainer", "rls", "special-goals"],
            "license_info": ms11_license_manager.get_user_license(discord_id)
        }
        
        return jsonify({"success": True, "status": status})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/ms11/api/sessions")
def ms11_api_sessions():
    """API endpoint to get MS11 sessions."""
    try:
        # Check if user is authorized
        discord_profile = session.get('discord_profile')
        if not discord_profile:
            return jsonify({"success": False, "error": "Not authenticated"}), 401
        
        discord_id = discord_profile.get('discord_id')
        if not ms11_license_manager.is_user_authorized(discord_id):
            return jsonify({"success": False, "error": "Not authorized"}), 403
        
        # Get MS11 sessions (mock data for now)
        sessions = [
            {
                "id": "session_001",
                "mode": "medic",
                "start_time": "2024-01-15T10:00:00",
                "end_time": "2024-01-15T12:00:00",
                "status": "completed",
                "xp_gained": 1500,
                "quests_completed": 3
            },
            {
                "id": "session_002",
                "mode": "quest",
                "start_time": "2024-01-14T14:00:00",
                "end_time": "2024-01-14T16:00:00",
                "status": "completed",
                "xp_gained": 2000,
                "quests_completed": 5
            }
        ]
        
        return jsonify({"success": True, "sessions": sessions})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/ms11/api/start-session", methods=['POST'])
def ms11_api_start_session():
    """API endpoint to start a new MS11 session."""
    try:
        # Check if user is authorized
        discord_profile = session.get('discord_profile')
        if not discord_profile:
            return jsonify({"success": False, "error": "Not authenticated"}), 401
        
        discord_id = discord_profile.get('discord_id')
        if not ms11_license_manager.is_user_authorized(discord_id):
            return jsonify({"success": False, "error": "Not authorized"}), 403
        
        data = request.get_json()
        mode = data.get('mode', 'medic')
        
        # Here you would actually start the MS11 session
        # For now, we'll return a mock response
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "mode": mode,
            "status": "started",
            "message": f"MS11 session started in {mode} mode"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/ms11/api/stop-session/<session_id>", methods=['POST'])
def ms11_api_stop_session(session_id):
    """API endpoint to stop an MS11 session."""
    try:
        # Check if user is authorized
        discord_profile = session.get('discord_profile')
        if not discord_profile:
            return jsonify({"success": False, "error": "Not authenticated"}), 401
        
        discord_id = discord_profile.get('discord_id')
        if not ms11_license_manager.is_user_authorized(discord_id):
            return jsonify({"success": False, "error": "Not authorized"}), 403
        
        # Here you would actually stop the MS11 session
        # For now, we'll return a mock response
        
        return jsonify({
            "success": True,
            "session_id": session_id,
            "status": "stopped",
            "message": "MS11 session stopped successfully"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/ms11/admin/licenses")
def ms11_admin_licenses():
    """Admin page to manage MS11 licenses."""
    # Check if user is authorized (you might want to add admin role checking)
    discord_profile = session.get('discord_profile')
    if not discord_profile:
        flash("Please login with Discord to access admin panel", "warning")
        return redirect(url_for('ms11_login'))
    
    discord_id = discord_profile.get('discord_id')
    if not discord_id or not ms11_license_manager.is_user_authorized(discord_id):
        flash("Access denied. You need admin privileges to access this page.", "error")
        return redirect(url_for('ms11_license_required'))
    
    licenses = ms11_license_manager.get_all_licenses()
    stats = ms11_license_manager.get_license_stats()
    
    return render_template('ms11/admin/licenses.html', 
                         licenses=licenses, 
                         stats=stats,
                         user=discord_profile)


@app.route("/ms11/admin/licenses/add", methods=['POST'])
def ms11_admin_add_license():
    """Admin endpoint to add a new MS11 license."""
    try:
        # Check if user is authorized
        discord_profile = session.get('discord_profile')
        if not discord_profile:
            return jsonify({"success": False, "error": "Not authenticated"}), 401
        
        discord_id = discord_profile.get('discord_id')
        if not ms11_license_manager.is_user_authorized(discord_id):
            return jsonify({"success": False, "error": "Not authorized"}), 403
        
        data = request.get_json()
        new_discord_id = data.get('discord_id')
        new_username = data.get('discord_username')
        license_type = data.get('license_type', 'standard')
        expires_at = data.get('expires_at')
        
        if not new_discord_id or not new_username:
            return jsonify({"success": False, "error": "Missing required fields"}), 400
        
        success = ms11_license_manager.add_license(new_discord_id, new_username, license_type, expires_at)
        
        if success:
            return jsonify({"success": True, "message": "License added successfully"})
        else:
            return jsonify({"success": False, "error": "Failed to add license. User might already have one or max licenses reached."}), 400
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/ms11/admin/licenses/remove/<discord_id>", methods=['POST'])
def ms11_admin_remove_license(discord_id):
    """Admin endpoint to remove an MS11 license."""
    try:
        # Check if user is authorized
        profile = session.get('discord_profile')
        if not profile:
            return jsonify({"success": False, "error": "Not authenticated"}), 401
        
        user_discord_id = profile.get('discord_id')
        if not ms11_license_manager.is_user_authorized(user_discord_id):
            return jsonify({"success": False, "error": "Not authorized"}), 403
        
        success = ms11_license_manager.remove_license(discord_id)
        
        if success:
            return jsonify({"success": True, "message": "License removed successfully"})
        else:
            return jsonify({"success": False, "error": "License not found"}), 404
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000)
