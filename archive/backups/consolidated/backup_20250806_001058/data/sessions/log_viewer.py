#!/usr/bin/env python3
"""
Internal Log Viewer for Session Data

This module provides a comprehensive log viewer for debugging session data
before uploading to SWGDB. It includes filtering, searching, and analysis tools.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import argparse
from collections import defaultdict, Counter


class SessionLogViewer:
    """Internal log viewer for session data debugging."""
    
    def __init__(self, sessions_dir: str = "data/sessions"):
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        self.session_files: List[Path] = []
        self.loaded_sessions: Dict[str, Dict[str, Any]] = {}
    
    def find_session_files(self) -> List[Path]:
        """Find all session files in the sessions directory."""
        if not self.sessions_dir.exists():
            return []
        
        session_files = []
        for file_path in self.sessions_dir.glob("*.json"):
            if file_path.is_file():
                session_files.append(file_path)
        
        # Sort by modification time (newest first)
        session_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        return session_files
    
    def load_session(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Load a single session file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Add file metadata
            data['_file_path'] = str(file_path)
            data['_file_name'] = file_path.name
            data['_file_size'] = file_path.stat().st_size
            data['_modified_time'] = file_path.stat().st_mtime
            
            return data
        except Exception as e:
            print(f"Error loading session {file_path}: {e}")
            return None
    
    def load_all_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Load all session files."""
        session_files = self.find_session_files()
        sessions = {}
        
        print(f"Loading {len(session_files)} session files...")
        
        for file_path in session_files:
            session_data = self.load_session(file_path)
            if session_data:
                session_id = session_data.get('session_id', file_path.stem)
                sessions[session_id] = session_data
        
        self.loaded_sessions = sessions
        print(f"Loaded {len(sessions)} sessions")
        return sessions
    
    def list_sessions(self, limit: int = 10) -> None:
        """List recent sessions with basic information."""
        sessions = self.load_all_sessions()
        
        if not sessions:
            print("No sessions found")
            return
        
        print(f"\n{'Session ID':<20} {'Start Time':<20} {'Duration':<10} {'XP':<8} {'Credits':<10} {'Quests':<8}")
        print("-" * 80)
        
        count = 0
        for session_id, session_data in sessions.items():
            if count >= limit:
                break
            
            start_time = session_data.get('start_time', 'Unknown')
            if start_time != 'Unknown':
                try:
                    dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    start_time = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    pass
            
            duration = session_data.get('duration_minutes', 0)
            duration_str = f"{duration:.1f}m" if duration > 0 else "Unknown"
            
            xp_gained = session_data.get('xp', {}).get('gained', 0)
            credits_gained = session_data.get('credits', {}).get('gained', 0)
            quests_completed = len(session_data.get('quests_completed', []))
            
            print(f"{session_id:<20} {start_time:<20} {duration_str:<10} {xp_gained:<8} {credits_gained:<10} {quests_completed:<8}")
            count += 1
    
    def view_session(self, session_id: str) -> None:
        """View detailed information about a specific session."""
        sessions = self.load_all_sessions()
        
        if session_id not in sessions:
            print(f"Session {session_id} not found")
            return
        
        session_data = sessions[session_id]
        
        print(f"\n=== Session Details: {session_id} ===")
        print(f"File: {session_data.get('_file_name', 'Unknown')}")
        print(f"Start Time: {session_data.get('start_time', 'Unknown')}")
        print(f"End Time: {session_data.get('end_time', 'Unknown')}")
        print(f"Duration: {session_data.get('duration_minutes', 0):.1f} minutes")
        print(f"Mode: {session_data.get('mode', 'Unknown')}")
        
        # XP Information
        xp_info = session_data.get('xp', {})
        print(f"\n--- XP Information ---")
        print(f"Total XP Gained: {xp_info.get('gained', 0):,}")
        print(f"XP per Hour: {xp_info.get('gained', 0) / max(session_data.get('duration_minutes', 1) / 60, 1):.0f}")
        
        # Credit Information
        credit_info = session_data.get('credits', {})
        print(f"\n--- Credit Information ---")
        print(f"Total Credits Gained: {credit_info.get('gained', 0):,}")
        print(f"Credits per Hour: {credit_info.get('gained', 0) / max(session_data.get('duration_minutes', 1) / 60, 1):.0f}")
        
        # Quest Information
        quests = session_data.get('quests_completed', [])
        print(f"\n--- Quest Information ---")
        print(f"Quests Completed: {len(quests)}")
        if quests:
            print("Quest List:")
            for quest in quests[:10]:  # Show first 10
                if isinstance(quest, str):
                    print(f"  - {quest}")
                else:
                    print(f"  - {quest.get('name', 'Unknown Quest')}")
            if len(quests) > 10:
                print(f"  ... and {len(quests) - 10} more")
        
        # Location Information
        locations = session_data.get('locations_visited', [])
        print(f"\n--- Location Information ---")
        print(f"Locations Visited: {len(locations)}")
        if locations:
            unique_planets = set()
            unique_cities = set()
            for location in locations:
                if isinstance(location, dict):
                    unique_planets.add(location.get('planet', 'Unknown'))
                    unique_cities.add(location.get('city', 'Unknown'))
            
            print(f"Unique Planets: {', '.join(unique_planets)}")
            print(f"Unique Cities: {', '.join(unique_cities)}")
        
        # Performance Metrics
        metrics = session_data.get('performance_metrics', {})
        if metrics:
            print(f"\n--- Performance Metrics ---")
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    print(f"{key}: {value}")
        
        # Actions Log (last 10)
        actions = session_data.get('actions', [])
        if actions:
            print(f"\n--- Recent Actions (last 10) ---")
            for action in actions[-10:]:
                print(f"  {action.get('time', 'Unknown')}: {action.get('action', 'Unknown')}")
    
    def search_sessions(self, query: str, field: str = "all") -> List[Tuple[str, Dict[str, Any]]]:
        """Search sessions for specific content."""
        sessions = self.load_all_sessions()
        results = []
        
        query_lower = query.lower()
        
        for session_id, session_data in sessions.items():
            if field == "all":
                # Search in all text fields
                searchable_text = json.dumps(session_data, default=str).lower()
                if query_lower in searchable_text:
                    results.append((session_id, session_data))
            elif field == "actions":
                # Search in actions
                actions = session_data.get('actions', [])
                for action in actions:
                    if query_lower in action.get('action', '').lower():
                        results.append((session_id, session_data))
                        break
            elif field == "quests":
                # Search in quests
                quests = session_data.get('quests_completed', [])
                for quest in quests:
                    quest_name = quest if isinstance(quest, str) else quest.get('name', '')
                    if query_lower in quest_name.lower():
                        results.append((session_id, session_data))
                        break
            elif field in session_data:
                # Search in specific field
                field_data = str(session_data[field]).lower()
                if query_lower in field_data:
                    results.append((session_id, session_data))
        
        return results
    
    def analyze_sessions(self) -> Dict[str, Any]:
        """Analyze all sessions for patterns and statistics."""
        sessions = self.load_all_sessions()
        
        if not sessions:
            return {"error": "No sessions found"}
        
        analysis = {
            "total_sessions": len(sessions),
            "total_duration_hours": 0,
            "total_xp_gained": 0,
            "total_credits_gained": 0,
            "total_quests_completed": 0,
            "average_session_duration": 0,
            "average_xp_per_session": 0,
            "average_credits_per_session": 0,
            "most_common_quests": [],
            "most_visited_planets": [],
            "session_modes": {},
            "xp_sources": {},
            "quest_types": {}
        }
        
        # Collect data
        all_quests = []
        all_planets = []
        all_xp_sources = []
        all_quest_types = []
        
        for session_data in sessions.values():
            # Duration
            duration = session_data.get('duration_minutes', 0)
            analysis["total_duration_hours"] += duration / 60
            
            # XP
            xp_gained = session_data.get('xp', {}).get('gained', 0)
            analysis["total_xp_gained"] += xp_gained
            
            # Credits
            credits_gained = session_data.get('credits', {}).get('gained', 0)
            analysis["total_credits_gained"] += credits_gained
            
            # Quests
            quests = session_data.get('quests_completed', [])
            analysis["total_quests_completed"] += len(quests)
            all_quests.extend([q if isinstance(q, str) else q.get('name', '') for q in quests])
            
            # Locations
            locations = session_data.get('locations_visited', [])
            for location in locations:
                if isinstance(location, dict):
                    all_planets.append(location.get('planet', 'Unknown'))
            
            # XP Sources
            xp_events = session_data.get('xp_events', [])
            for event in xp_events:
                if isinstance(event, dict):
                    all_xp_sources.append(event.get('source', 'unknown'))
            
            # Quest Types
            for quest in quests:
                if isinstance(quest, dict):
                    all_quest_types.append(quest.get('type', 'unknown'))
            
            # Session Modes
            mode = session_data.get('mode', 'unknown')
            analysis["session_modes"][mode] = analysis["session_modes"].get(mode, 0) + 1
        
        # Calculate averages
        if analysis["total_sessions"] > 0:
            analysis["average_session_duration"] = analysis["total_duration_hours"] / analysis["total_sessions"]
            analysis["average_xp_per_session"] = analysis["total_xp_gained"] / analysis["total_sessions"]
            analysis["average_credits_per_session"] = analysis["total_credits_gained"] / analysis["total_sessions"]
        
        # Most common quests
        quest_counter = Counter(all_quests)
        analysis["most_common_quests"] = quest_counter.most_common(10)
        
        # Most visited planets
        planet_counter = Counter(all_planets)
        analysis["most_visited_planets"] = planet_counter.most_common(10)
        
        # XP sources
        xp_source_counter = Counter(all_xp_sources)
        analysis["xp_sources"] = dict(xp_source_counter.most_common(10))
        
        # Quest types
        quest_type_counter = Counter(all_quest_types)
        analysis["quest_types"] = dict(quest_type_counter.most_common(10))
        
        return analysis
    
    def export_session(self, session_id: str, output_file: str) -> bool:
        """Export a session to a file."""
        sessions = self.load_all_sessions()
        
        if session_id not in sessions:
            print(f"Session {session_id} not found")
            return False
        
        session_data = sessions[session_id]
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
            
            print(f"Session exported to {output_file}")
            return True
        except Exception as e:
            print(f"Error exporting session: {e}")
            return False
    
    def compare_sessions(self, session_ids: List[str]) -> Dict[str, Any]:
        """Compare multiple sessions."""
        sessions = self.load_all_sessions()
        
        # Filter to requested sessions
        selected_sessions = {sid: sessions[sid] for sid in session_ids if sid in sessions}
        
        if not selected_sessions:
            return {"error": "No valid sessions found"}
        
        comparison = {
            "sessions_compared": list(selected_sessions.keys()),
            "comparison_data": {}
        }
        
        for session_id, session_data in selected_sessions.items():
            comparison["comparison_data"][session_id] = {
                "duration_minutes": session_data.get('duration_minutes', 0),
                "xp_gained": session_data.get('xp', {}).get('gained', 0),
                "credits_gained": session_data.get('credits', {}).get('gained', 0),
                "quests_completed": len(session_data.get('quests_completed', [])),
                "locations_visited": len(session_data.get('locations_visited', [])),
                "mode": session_data.get('mode', 'unknown'),
                "start_time": session_data.get('start_time', ''),
                "end_time": session_data.get('end_time', '')
            }
        
        return comparison
    
    def interactive_mode(self) -> None:
        """Run the log viewer in interactive mode."""
        print("=== MS11 Session Log Viewer ===")
        print("Commands: list, view <id>, search <query>, analyze, export <id> <file>, compare <id1> <id2>..., quit")
        
        while True:
            try:
                command = input("\n> ").strip().split()
                if not command:
                    continue
                
                cmd = command[0].lower()
                
                if cmd == "quit" or cmd == "exit":
                    break
                elif cmd == "list":
                    limit = int(command[1]) if len(command) > 1 else 10
                    self.list_sessions(limit)
                elif cmd == "view" and len(command) > 1:
                    self.view_session(command[1])
                elif cmd == "search" and len(command) > 1:
                    query = " ".join(command[1:])
                    results = self.search_sessions(query)
                    print(f"Found {len(results)} sessions matching '{query}':")
                    for session_id, _ in results:
                        print(f"  - {session_id}")
                elif cmd == "analyze":
                    analysis = self.analyze_sessions()
                    if "error" not in analysis:
                        print("\n=== Session Analysis ===")
                        print(f"Total Sessions: {analysis['total_sessions']}")
                        print(f"Total Duration: {analysis['total_duration_hours']:.1f} hours")
                        print(f"Total XP Gained: {analysis['total_xp_gained']:,}")
                        print(f"Total Credits Gained: {analysis['total_credits_gained']:,}")
                        print(f"Total Quests Completed: {analysis['total_quests_completed']}")
                        print(f"Average Session Duration: {analysis['average_session_duration']:.1f} hours")
                        print(f"Average XP per Session: {analysis['average_xp_per_session']:,.0f}")
                        print(f"Average Credits per Session: {analysis['average_credits_per_session']:,.0f}")
                        
                        if analysis['most_common_quests']:
                            print("\nMost Common Quests:")
                            for quest, count in analysis['most_common_quests'][:5]:
                                print(f"  {quest}: {count}")
                        
                        if analysis['most_visited_planets']:
                            print("\nMost Visited Planets:")
                            for planet, count in analysis['most_visited_planets'][:5]:
                                print(f"  {planet}: {count}")
                    else:
                        print(f"Analysis error: {analysis['error']}")
                elif cmd == "export" and len(command) > 2:
                    session_id = command[1]
                    output_file = command[2]
                    self.export_session(session_id, output_file)
                elif cmd == "compare" and len(command) > 1:
                    session_ids = command[1:]
                    comparison = self.compare_sessions(session_ids)
                    if "error" not in comparison:
                        print("\n=== Session Comparison ===")
                        for session_id, data in comparison["comparison_data"].items():
                            print(f"\n{session_id}:")
                            print(f"  Duration: {data['duration_minutes']:.1f} minutes")
                            print(f"  XP Gained: {data['xp_gained']:,}")
                            print(f"  Credits Gained: {data['credits_gained']:,}")
                            print(f"  Quests Completed: {data['quests_completed']}")
                            print(f"  Mode: {data['mode']}")
                    else:
                        print(f"Comparison error: {comparison['error']}")
                else:
                    print("Unknown command. Use: list, view <id>, search <query>, analyze, export <id> <file>, compare <id1> <id2>..., quit")
            
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")


def main():
    """Main function for the log viewer."""
    parser = argparse.ArgumentParser(description="MS11 Session Log Viewer")
    parser.add_argument("--sessions-dir", default="data/sessions", help="Directory containing session files")
    parser.add_argument("--list", action="store_true", help="List recent sessions")
    parser.add_argument("--view", help="View specific session by ID")
    parser.add_argument("--search", help="Search sessions for query")
    parser.add_argument("--analyze", action="store_true", help="Analyze all sessions")
    parser.add_argument("--export", nargs=2, metavar=("SESSION_ID", "OUTPUT_FILE"), help="Export session to file")
    parser.add_argument("--compare", nargs="+", help="Compare multiple sessions")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    viewer = SessionLogViewer(args.sessions_dir)
    
    if args.list:
        viewer.list_sessions()
    elif args.view:
        viewer.view_session(args.view)
    elif args.search:
        results = viewer.search_sessions(args.search)
        print(f"Found {len(results)} sessions matching '{args.search}':")
        for session_id, _ in results:
            print(f"  - {session_id}")
    elif args.analyze:
        analysis = viewer.analyze_sessions()
        if "error" not in analysis:
            print(json.dumps(analysis, indent=2))
        else:
            print(f"Analysis error: {analysis['error']}")
    elif args.export:
        session_id, output_file = args.export
        viewer.export_session(session_id, output_file)
    elif args.compare:
        comparison = viewer.compare_sessions(args.compare)
        if "error" not in comparison:
            print(json.dumps(comparison, indent=2))
        else:
            print(f"Comparison error: {comparison['error']}")
    elif args.interactive:
        viewer.interactive_mode()
    else:
        # Default to interactive mode
        viewer.interactive_mode()


if __name__ == '__main__':
    main() 