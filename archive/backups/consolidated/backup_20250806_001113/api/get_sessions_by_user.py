#!/usr/bin/env python3
"""
API Endpoint for Getting Sessions by User

This endpoint securely retrieves session data for authenticated users
from the SWGDB database with proper authentication and filtering.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from urllib.parse import parse_qs
import jwt
import sqlite3
from pathlib import Path


class SessionAPI:
    """API handler for session data retrieval."""
    
    def __init__(self):
        self.db_path = Path("data/swgdb_sessions.db")
        self.jwt_secret = os.getenv("SWGDB_JWT_SECRET", "default_secret_key")
        self.init_database()
    
    def init_database(self):
        """Initialize the database with sessions table."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create sessions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    user_hash TEXT NOT NULL,
                    character_name TEXT,
                    start_time TEXT,
                    end_time TEXT,
                    duration_minutes REAL,
                    session_data TEXT,
                    upload_timestamp TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_user_hash 
                ON sessions(user_hash)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_session_id 
                ON sessions(session_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_start_time 
                ON sessions(start_time)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_character_name 
                ON sessions(character_name)
            ''')
            
            conn.commit()
    
    def authenticate_user(self, auth_header: str) -> Optional[str]:
        """Authenticate user from Authorization header."""
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        try:
            token = auth_header.split(' ')[1]
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload.get('user_hash')
        except jwt.InvalidTokenError:
            return None
        except Exception as e:
            print(f"Authentication error: {e}")
            return None
    
    def get_sessions_by_user(self, user_hash: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get sessions for a specific user with optional filtering."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Build query with filters
                query = '''
                    SELECT session_data 
                    FROM sessions 
                    WHERE user_hash = ?
                '''
                params = [user_hash]
                
                # Add date filters
                if filters and filters.get('start_date'):
                    query += ' AND start_time >= ?'
                    params.append(filters['start_date'])
                
                if filters and filters.get('end_date'):
                    query += ' AND start_time <= ?'
                    params.append(filters['end_date'])
                
                # Add character filter
                if filters and filters.get('character'):
                    query += ' AND character_name = ?'
                    params.append(filters['character'])
                
                # Order by start time (newest first)
                query += ' ORDER BY start_time DESC'
                
                # Add limit if specified
                if filters and filters.get('limit'):
                    query += ' LIMIT ?'
                    params.append(filters['limit'])
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                sessions = []
                for row in rows:
                    try:
                        session_data = json.loads(row[0])
                        
                        # Apply post-processing filters
                        if self._should_include_session(session_data, filters):
                            sessions.append(session_data)
                    except json.JSONDecodeError:
                        print(f"Error parsing session data: {row[0][:100]}...")
                        continue
                
                return sessions
                
        except Exception as e:
            print(f"Database error: {e}")
            return []
    
    def _should_include_session(self, session_data: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Apply post-processing filters that require parsing session data."""
        if not filters:
            return True
        
        # Planet filter
        if filters.get('planet'):
            has_planet = False
            for location in session_data.get('location_data', {}).get('location_events', []):
                if location.get('planet') == filters['planet']:
                    has_planet = True
                    break
            if not has_planet:
                return False
        
        # Profession filter
        if filters.get('profession'):
            profession_breakdown = session_data.get('xp_data', {}).get('profession_breakdown', {})
            if filters['profession'] not in profession_breakdown:
                return False
        
        return True
    
    def get_session_by_id(self, user_hash: str, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific session by ID for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT session_data 
                    FROM sessions 
                    WHERE user_hash = ? AND session_id = ?
                ''', [user_hash, session_id])
                
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return None
                
        except Exception as e:
            print(f"Database error: {e}")
            return None
    
    def get_session_statistics(self, user_hash: str, filters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Get aggregated statistics for user sessions."""
        sessions = self.get_sessions_by_user(user_hash, filters)
        
        if not sessions:
            return {
                "total_sessions": 0,
                "total_xp_gained": 0,
                "total_credits_gained": 0,
                "total_quests_completed": 0,
                "total_time_minutes": 0,
                "average_session_duration": 0,
                "average_xp_per_session": 0,
                "average_credits_per_session": 0,
                "total_stuck_events": 0,
                "total_communication_events": 0,
                "characters": [],
                "planets": [],
                "professions": []
            }
        
        stats = {
            "total_sessions": len(sessions),
            "total_xp_gained": 0,
            "total_credits_gained": 0,
            "total_quests_completed": 0,
            "total_time_minutes": 0,
            "total_stuck_events": 0,
            "total_communication_events": 0,
            "characters": set(),
            "planets": set(),
            "professions": set()
        }
        
        for session in sessions:
            # XP
            stats["total_xp_gained"] += session.get("xp_data", {}).get("total_xp_gained", 0)
            
            # Credits
            stats["total_credits_gained"] += session.get("credit_data", {}).get("total_credits_gained", 0)
            
            # Quests
            stats["total_quests_completed"] += session.get("quest_data", {}).get("total_quests_completed", 0)
            
            # Time
            stats["total_time_minutes"] += session.get("duration_minutes", 0)
            
            # Events
            stats["total_stuck_events"] += len(session.get("event_data", {}).get("stuck_events", []))
            stats["total_communication_events"] += len(session.get("event_data", {}).get("communication_events", []))
            
            # Characters
            if session.get("character_name"):
                stats["characters"].add(session["character_name"])
            
            # Planets
            for location in session.get("location_data", {}).get("location_events", []):
                if location.get("planet"):
                    stats["planets"].add(location["planet"])
            
            # Professions
            for profession in session.get("xp_data", {}).get("profession_breakdown", {}).keys():
                stats["professions"].add(profession)
        
        # Calculate averages
        if stats["total_sessions"] > 0:
            stats["average_session_duration"] = stats["total_time_minutes"] / stats["total_sessions"]
            stats["average_xp_per_session"] = stats["total_xp_gained"] / stats["total_sessions"]
            stats["average_credits_per_session"] = stats["total_credits_gained"] / stats["total_sessions"]
        
        # Convert sets to lists for JSON serialization
        stats["characters"] = list(stats["characters"])
        stats["planets"] = list(stats["planets"])
        stats["professions"] = list(stats["professions"])
        
        return stats
    
    def insert_session(self, user_hash: str, session_data: Dict[str, Any]) -> bool:
        """Insert a new session into the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO sessions 
                    (session_id, user_hash, character_name, start_time, end_time, 
                     duration_minutes, session_data, upload_timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', [
                    session_data.get("session_id"),
                    user_hash,
                    session_data.get("character_name"),
                    session_data.get("start_time"),
                    session_data.get("end_time"),
                    session_data.get("duration_minutes"),
                    json.dumps(session_data),
                    datetime.now().isoformat()
                ])
                
                conn.commit()
                return True
                
        except Exception as e:
            print(f"Error inserting session: {e}")
            return False
    
    def delete_session(self, user_hash: str, session_id: str) -> bool:
        """Delete a session for a user."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM sessions 
                    WHERE user_hash = ? AND session_id = ?
                ''', [user_hash, session_id])
                
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False


def handle_request(environ, start_response):
    """Handle HTTP request for session API."""
    api = SessionAPI()
    
    # Get request method and path
    method = environ.get('REQUEST_METHOD', 'GET')
    path = environ.get('PATH_INFO', '')
    
    # Get request body
    content_length = int(environ.get('CONTENT_LENGTH', 0))
    body = environ.get('wsgi.input').read(content_length).decode('utf-8')
    
    # Get query parameters
    query_string = environ.get('QUERY_STRING', '')
    query_params = parse_qs(query_string)
    
    # Get headers
    headers = {}
    for key, value in environ.items():
        if key.startswith('HTTP_'):
            header_name = key[5:].lower().replace('_', '-')
            headers[header_name] = value
    
    # Authenticate user
    auth_header = headers.get('authorization', '')
    user_hash = api.authenticate_user(auth_header)
    
    if not user_hash:
        start_response('401 Unauthorized', [
            ('Content-Type', 'application/json'),
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        ])
        return [json.dumps({"error": "Authentication required"})]
    
    # Handle CORS preflight
    if method == 'OPTIONS':
        start_response('200 OK', [
            ('Content-Type', 'application/json'),
            ('Access-Control-Allow-Origin', '*'),
            ('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS'),
            ('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        ])
        return ['']
    
    try:
        if method == 'GET':
            # Parse filters from query parameters
            filters = {}
            
            if query_params.get('start_date'):
                filters['start_date'] = query_params['start_date'][0]
            
            if query_params.get('end_date'):
                filters['end_date'] = query_params['end_date'][0]
            
            if query_params.get('character'):
                filters['character'] = query_params['character'][0]
            
            if query_params.get('planet'):
                filters['planet'] = query_params['planet'][0]
            
            if query_params.get('profession'):
                filters['profession'] = query_params['profession'][0]
            
            if query_params.get('limit'):
                filters['limit'] = int(query_params['limit'][0])
            
            # Check if requesting statistics
            if '/statistics' in path:
                stats = api.get_session_statistics(user_hash, filters)
                response_data = {"statistics": stats}
            # Check if requesting specific session
            elif '/session/' in path:
                session_id = path.split('/session/')[-1]
                session = api.get_session_by_id(user_hash, session_id)
                
                if session:
                    response_data = {"session": session}
                else:
                    start_response('404 Not Found', [
                        ('Content-Type', 'application/json'),
                        ('Access-Control-Allow-Origin', '*')
                    ])
                    return [json.dumps({"error": "Session not found"})]
            else:
                # Get sessions with filters
                sessions = api.get_sessions_by_user(user_hash, filters)
                response_data = {"sessions": sessions}
            
            start_response('200 OK', [
                ('Content-Type', 'application/json'),
                ('Access-Control-Allow-Origin', '*')
            ])
            return [json.dumps(response_data)]
        
        elif method == 'POST':
            # Insert new session
            try:
                session_data = json.loads(body)
                success = api.insert_session(user_hash, session_data)
                
                if success:
                    response_data = {"message": "Session inserted successfully"}
                else:
                    response_data = {"error": "Failed to insert session"}
                
                start_response('200 OK', [
                    ('Content-Type', 'application/json'),
                    ('Access-Control-Allow-Origin', '*')
                ])
                return [json.dumps(response_data)]
                
            except json.JSONDecodeError:
                start_response('400 Bad Request', [
                    ('Content-Type', 'application/json'),
                    ('Access-Control-Allow-Origin', '*')
                ])
                return [json.dumps({"error": "Invalid JSON"})]
        
        elif method == 'DELETE':
            # Delete session
            if '/session/' in path:
                session_id = path.split('/session/')[-1]
                success = api.delete_session(user_hash, session_id)
                
                if success:
                    response_data = {"message": "Session deleted successfully"}
                else:
                    response_data = {"error": "Session not found or could not be deleted"}
                
                start_response('200 OK', [
                    ('Content-Type', 'application/json'),
                    ('Access-Control-Allow-Origin', '*')
                ])
                return [json.dumps(response_data)]
            else:
                start_response('400 Bad Request', [
                    ('Content-Type', 'application/json'),
                    ('Access-Control-Allow-Origin', '*')
                ])
                return [json.dumps({"error": "Session ID required for deletion"})]
        
        else:
            start_response('405 Method Not Allowed', [
                ('Content-Type', 'application/json'),
                ('Access-Control-Allow-Origin', '*')
            ])
            return [json.dumps({"error": "Method not allowed"})]
    
    except Exception as e:
        print(f"API error: {e}")
        start_response('500 Internal Server Error', [
            ('Content-Type', 'application/json'),
            ('Access-Control-Allow-Origin', '*')
        ])
        return [json.dumps({"error": "Internal server error"})]


def main():
    """Main function for testing the API."""
    # Simulate environment for testing
    environ = {
        'REQUEST_METHOD': 'GET',
        'PATH_INFO': '/',
        'QUERY_STRING': '',
        'CONTENT_LENGTH': '0',
        'wsgi.input': type('MockInput', (), {'read': lambda x: b''})(),
        'HTTP_AUTHORIZATION': 'Bearer test_token'
    }
    
    def start_response(status, headers):
        print(f"Status: {status}")
        print(f"Headers: {headers}")
    
    # Test the API
    print("Testing Session API...")
    result = handle_request(environ, start_response)
    print(f"Response: {result}")


if __name__ == '__main__':
    main() 