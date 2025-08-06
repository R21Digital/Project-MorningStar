#!/usr/bin/env python3
"""
Enhanced Feedback API for SWGDB
Integrates with existing Flask dashboard and provides Discord webhooks
"""

from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from components.FeedbackForm import FeedbackForm, feedback_manager
import logging
import os
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def register_feedback_routes(app: Flask):
    """Register feedback routes with the Flask app"""
    
    @app.route('/feedback', methods=['GET', 'POST'])
    def feedback_form():
        """Display and process feedback form"""
        form = FeedbackForm()
        
        if request.method == 'POST':
            if form.validate_on_submit():
                try:
                    # Process form data
                    form_data = {
                        'title': form.title.data,
                        'description': form.description.data,
                        'category': form.category.data,
                        'priority': form.priority.data,
                        'user_agent': form.user_agent.data,
                        'page_url': form.page_url.data,
                        'user_contact': form.user_contact.data,
                        'mod_name': form.mod_name.data,
                    }
                    
                    # Handle screenshot upload
                    screenshot_url = ''
                    if form.screenshot.data:
                        screenshot_url = handle_screenshot_upload(form.screenshot.data)
                        form_data['screenshot_url'] = screenshot_url
                    
                    # Submit feedback
                    success, message, feedback_data = feedback_manager.submit_feedback(form_data)
                    
                    if success:
                        flash(message, 'success')
                        return redirect(url_for('feedback_form'))
                    else:
                        flash(f"Error submitting feedback: {message}", 'error')
                        
                except Exception as e:
                    logger.error(f"Error processing feedback form: {e}")
                    flash("An unexpected error occurred. Please try again.", 'error')
            
            else:
                # Form validation failed
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f"{field}: {error}", 'error')
        
        return render_template('feedback_form.html', form=form)
    
    @app.route('/api/feedback', methods=['POST'])
    def api_submit_feedback():
        """API endpoint for programmatic feedback submission"""
        try:
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Validate required fields
            required_fields = ['title', 'description', 'category', 'priority']
            for field in required_fields:
                if field not in data or not str(data[field]).strip():
                    return jsonify({"error": f"Missing required field: {field}"}), 400
            
            # Submit feedback
            success, message, feedback_data = feedback_manager.submit_feedback(data)
            
            if success:
                return jsonify({
                    "success": True,
                    "message": message,
                    "feedback_id": feedback_data.get('id'),
                    "data": feedback_data
                }), 201
            else:
                return jsonify({"error": message}), 500
                
        except Exception as e:
            logger.error(f"API feedback submission error: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    @app.route('/api/feedback/stats', methods=['GET'])
    def feedback_stats():
        """Get feedback statistics"""
        try:
            # Implement basic authentication check
            api_key = request.headers.get('X-API-Key')
            if not api_key or api_key != os.getenv('SWGDB_API_KEY', 'demo-key'):
                return jsonify({"error": "Unauthorized"}), 401
            
            # Calculate stats from files
            stats = calculate_feedback_stats()
            
            return jsonify({
                "success": True,
                "stats": stats
            })
            
        except Exception as e:
            logger.error(f"Error getting feedback stats: {e}")
            return jsonify({"error": "Internal server error"}), 500
    
    @app.route('/admin/feedback')
    def admin_feedback_dashboard():
        """Admin dashboard for managing feedback"""
        # Add authentication check in production
        api_key = request.args.get('api_key') or request.headers.get('X-API-Key')
        if not api_key or api_key != os.getenv('SWGDB_API_KEY', 'demo-key'):
            return "Unauthorized", 401
        
        try:
            stats = calculate_feedback_stats()
            recent_feedback = get_recent_feedback(limit=10)
            
            return render_template('admin/feedback_dashboard.html', 
                                 stats=stats, 
                                 recent_feedback=recent_feedback)
        except Exception as e:
            logger.error(f"Error loading admin feedback dashboard: {e}")
            return "Internal server error", 500

def handle_screenshot_upload(file) -> str:
    """Handle screenshot file upload"""
    if not file or file.filename == '':
        return ''
    
    # Validate file
    if not allowed_file(file.filename):
        raise ValueError("Invalid file type")
    
    # Create uploads directory
    upload_dir = 'static/uploads/screenshots'
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate secure filename
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_{filename}"
    
    file_path = os.path.join(upload_dir, filename)
    
    try:
        file.save(file_path)
        return f"/static/uploads/screenshots/{filename}"
    except Exception as e:
        logger.error(f"Error saving screenshot: {e}")
        raise

def allowed_file(filename: str) -> bool:
    """Check if uploaded file is allowed"""
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def calculate_feedback_stats() -> dict:
    """Calculate feedback statistics from stored files"""
    from pathlib import Path
    import json
    
    stats = {
        "total": 0,
        "by_category": {},
        "by_priority": {},
        "by_status": {"New": 0, "In Progress": 0, "Resolved": 0, "Closed": 0},
        "recent_submissions": 0
    }
    
    try:
        # Read from legacy JSON file
        json_file = Path("data/feedback_reports.json")
        if json_file.exists():
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                reports = data.get("feedback_reports", [])
                
                stats["total"] = len(reports)
                
                for report in reports:
                    # Count by category
                    category = report.get('category', 'Unknown')
                    stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
                    
                    # Count by priority
                    priority = report.get('priority', 'Unknown')
                    stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
                    
                    # Count by status
                    status = report.get('status', 'New')
                    stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
                    
                    # Count recent (last 7 days)
                    submitted_at = report.get('submitted_at')
                    if submitted_at:
                        try:
                            from datetime import datetime, timedelta
                            submitted_date = datetime.fromisoformat(submitted_at.replace('Z', '+00:00'))
                            if (datetime.now() - submitted_date).days <= 7:
                                stats['recent_submissions'] += 1
                        except:
                            pass
        
        return stats
        
    except Exception as e:
        logger.error(f"Error calculating feedback stats: {e}")
        return stats

def get_recent_feedback(limit: int = 10) -> list:
    """Get recent feedback submissions"""
    from pathlib import Path
    import json
    
    try:
        json_file = Path("data/feedback_reports.json")
        if json_file.exists():
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                reports = data.get("feedback_reports", [])
                
                # Sort by submission date (newest first)
                reports.sort(key=lambda x: x.get('submitted_at', ''), reverse=True)
                
                return reports[:limit]
        
        return []
        
    except Exception as e:
        logger.error(f"Error getting recent feedback: {e}")
        return []