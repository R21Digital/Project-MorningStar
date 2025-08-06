#!/usr/bin/env python3
"""
Bug Report API for SWGDB
Handles bug report submissions and saves them to data/bug_reports.json
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
BUG_REPORTS_FILE = "data/bug_reports.json"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def load_bug_reports() -> Dict:
    """Load existing bug reports from JSON file"""
    try:
        if os.path.exists(BUG_REPORTS_FILE):
            with open(BUG_REPORTS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Create initial structure if file doesn't exist
            return {
                "bug_reports": [],
                "metadata": {
                    "created": datetime.now().isoformat(),
                    "version": "1.0",
                    "description": "Bug reports collected from SWGDB website users"
                },
                "schema": {
                    "bug_report": {
                        "id": "string",
                        "title": "string",
                        "description": "string",
                        "priority": "enum: Low, Medium, High",
                        "category": "enum: Bot, Website, Mod",
                        "screenshot_url": "string (optional)",
                        "user_agent": "string",
                        "page_url": "string",
                        "submitted_at": "string (ISO 8601)",
                        "status": "enum: New, In Progress, Resolved, Closed",
                        "assigned_to": "string (optional)",
                        "notes": "string (optional)"
                    }
                }
            }
    except Exception as e:
        logger.error(f"Error loading bug reports: {e}")
        return {"bug_reports": [], "metadata": {}, "schema": {}}

def save_bug_reports(data: Dict) -> bool:
    """Save bug reports to JSON file"""
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(BUG_REPORTS_FILE), exist_ok=True)
        
        with open(BUG_REPORTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Error saving bug reports: {e}")
        return False

def validate_bug_report(data: Dict) -> tuple[bool, str]:
    """Validate bug report data"""
    required_fields = ['title', 'description', 'priority', 'category']
    
    for field in required_fields:
        if field not in data or not data[field].strip():
            return False, f"Missing required field: {field}"
    
    # Validate priority
    if data['priority'] not in ['Low', 'Medium', 'High']:
        return False, "Invalid priority value"
    
    # Validate category
    if data['category'] not in ['Bot', 'Website', 'Mod']:
        return False, "Invalid category value"
    
    # Validate title length
    if len(data['title']) > 100:
        return False, "Title too long (max 100 characters)"
    
    # Validate description length
    if len(data['description']) > 2000:
        return False, "Description too long (max 2000 characters)"
    
    return True, ""

def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/bug-report', methods=['POST'])
def submit_bug_report():
    """Submit a new bug report"""
    try:
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate the data
        is_valid, error_message = validate_bug_report(data)
        if not is_valid:
            return jsonify({"error": error_message}), 400
        
        # Load existing reports
        bug_reports_data = load_bug_reports()
        
        # Create new bug report
        bug_report = {
            "id": data.get('id', f"bug_{datetime.now().timestamp()}_{uuid.uuid4().hex[:8]}"),
            "title": data['title'].strip(),
            "description": data['description'].strip(),
            "priority": data['priority'],
            "category": data['category'],
            "user_agent": data.get('user_agent', request.headers.get('User-Agent', '')),
            "page_url": data.get('page_url', ''),
            "submitted_at": data.get('submitted_at', datetime.now().isoformat()),
            "status": "New",
            "screenshot_url": data.get('screenshot_url', ''),
            "assigned_to": None,
            "notes": ""
        }
        
        # Add to reports
        bug_reports_data['bug_reports'].append(bug_report)
        
        # Save to file
        if save_bug_reports(bug_reports_data):
            logger.info(f"Bug report submitted: {bug_report['id']}")
            return jsonify({
                "success": True,
                "message": "Bug report submitted successfully",
                "bug_id": bug_report['id']
            }), 201
        else:
            return jsonify({"error": "Failed to save bug report"}), 500
            
    except Exception as e:
        logger.error(f"Error submitting bug report: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/bug-reports', methods=['GET'])
def get_bug_reports():
    """Get all bug reports (for admin use)"""
    try:
        # Add basic authentication check (in production, use proper auth)
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.getenv('SWGDB_API_KEY', 'demo-key'):
            return jsonify({"error": "Unauthorized"}), 401
        
        bug_reports_data = load_bug_reports()
        
        # Filter and sort reports
        reports = bug_reports_data.get('bug_reports', [])
        
        # Apply filters if provided
        status_filter = request.args.get('status')
        category_filter = request.args.get('category')
        priority_filter = request.args.get('priority')
        
        if status_filter:
            reports = [r for r in reports if r.get('status') == status_filter]
        if category_filter:
            reports = [r for r in reports if r.get('category') == category_filter]
        if priority_filter:
            reports = [r for r in reports if r.get('priority') == priority_filter]
        
        # Sort by submitted_at (newest first)
        reports.sort(key=lambda x: x.get('submitted_at', ''), reverse=True)
        
        return jsonify({
            "success": True,
            "bug_reports": reports,
            "total": len(reports),
            "metadata": bug_reports_data.get('metadata', {})
        })
        
    except Exception as e:
        logger.error(f"Error getting bug reports: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/bug-report/<bug_id>', methods=['GET'])
def get_bug_report(bug_id: str):
    """Get a specific bug report"""
    try:
        # Add basic authentication check
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.getenv('SWGDB_API_KEY', 'demo-key'):
            return jsonify({"error": "Unauthorized"}), 401
        
        bug_reports_data = load_bug_reports()
        reports = bug_reports_data.get('bug_reports', [])
        
        # Find the specific report
        bug_report = next((r for r in reports if r.get('id') == bug_id), None)
        
        if not bug_report:
            return jsonify({"error": "Bug report not found"}), 404
        
        return jsonify({
            "success": True,
            "bug_report": bug_report
        })
        
    except Exception as e:
        logger.error(f"Error getting bug report {bug_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/bug-report/<bug_id>', methods=['PUT'])
def update_bug_report(bug_id: str):
    """Update a bug report (for admin use)"""
    try:
        # Add basic authentication check
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.getenv('SWGDB_API_KEY', 'demo-key'):
            return jsonify({"error": "Unauthorized"}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        bug_reports_data = load_bug_reports()
        reports = bug_reports_data.get('bug_reports', [])
        
        # Find and update the report
        for i, report in enumerate(reports):
            if report.get('id') == bug_id:
                # Update allowed fields
                allowed_updates = ['status', 'assigned_to', 'notes', 'priority']
                for field in allowed_updates:
                    if field in data:
                        reports[i][field] = data[field]
                
                # Save updated data
                if save_bug_reports(bug_reports_data):
                    logger.info(f"Bug report updated: {bug_id}")
                    return jsonify({
                        "success": True,
                        "message": "Bug report updated successfully"
                    })
                else:
                    return jsonify({"error": "Failed to save updates"}), 500
        
        return jsonify({"error": "Bug report not found"}), 404
        
    except Exception as e:
        logger.error(f"Error updating bug report {bug_id}: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/bug-report/stats', methods=['GET'])
def get_bug_report_stats():
    """Get bug report statistics"""
    try:
        # Add basic authentication check
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.getenv('SWGDB_API_KEY', 'demo-key'):
            return jsonify({"error": "Unauthorized"}), 401
        
        bug_reports_data = load_bug_reports()
        reports = bug_reports_data.get('bug_reports', [])
        
        # Calculate statistics
        stats = {
            "total": len(reports),
            "by_status": {},
            "by_category": {},
            "by_priority": {},
            "recent_submissions": 0
        }
        
        # Count by status, category, priority
        for report in reports:
            status = report.get('status', 'Unknown')
            category = report.get('category', 'Unknown')
            priority = report.get('priority', 'Unknown')
            
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
            stats['by_priority'][priority] = stats['by_priority'].get(priority, 0) + 1
            
            # Count recent submissions (last 7 days)
            submitted_at = report.get('submitted_at')
            if submitted_at:
                try:
                    submitted_date = datetime.fromisoformat(submitted_at.replace('Z', '+00:00'))
                    if (datetime.now() - submitted_date).days <= 7:
                        stats['recent_submissions'] += 1
                except:
                    pass
        
        return jsonify({
            "success": True,
            "stats": stats
        })
        
    except Exception as e:
        logger.error(f"Error getting bug report stats: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "SWGDB Bug Report API",
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Load initial bug reports to ensure file exists
    load_bug_reports()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5001, debug=True) 