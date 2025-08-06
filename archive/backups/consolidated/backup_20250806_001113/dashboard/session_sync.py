#!/usr/bin/env python3
"""
Session Sync Utility for Dashboard

This script syncs session logs from various directories to the dashboard/sessions/
directory for easier access by the web UI.
"""

import json
import shutil
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


class SessionSync:
    """Utility to sync session logs to dashboard directory."""
    
    def __init__(self):
        self.project_root = Path(__file__).resolve().parents[1]
        self.dashboard_sessions_dir = self.project_root / "dashboard" / "sessions"
        self.source_dirs = [
            self.project_root / "logs",
            self.project_root / "data" / "session_logs", 
            self.project_root / "session_logs"
        ]
        
        # Create dashboard sessions directory if it doesn't exist
        self.dashboard_sessions_dir.mkdir(parents=True, exist_ok=True)
    
    def find_session_logs(self) -> List[Path]:
        """Find all session log files in source directories."""
        session_files = []
        
        for source_dir in self.source_dirs:
            if source_dir.exists():
                # Find JSON session files
                json_files = list(source_dir.glob("session_*.json"))
                json_files.extend(source_dir.glob("*.json"))
                
                for file_path in json_files:
                    try:
                        # Validate it's a session log by trying to parse it
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # Check if it has session-like structure
                        if self._is_session_log(data):
                            session_files.append(file_path)
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
        
        return session_files
    
    def _is_session_log(self, data: Dict[str, Any]) -> bool:
        """Check if the JSON data looks like a session log."""
        # Check for common session log fields
        session_indicators = [
            'session_id', 'start_time', 'end_time', 'character_name',
            'total_xp_gained', 'total_credits_gained', 'events'
        ]
        
        return any(indicator in data for indicator in session_indicators)
    
    def sync_sessions(self, force_update: bool = False) -> Dict[str, Any]:
        """Sync session logs to dashboard directory."""
        session_files = self.find_session_logs()
        sync_results = {
            'total_found': len(session_files),
            'copied': 0,
            'skipped': 0,
            'errors': 0,
            'details': []
        }
        
        for source_file in session_files:
            try:
                # Generate destination filename
                dest_filename = source_file.name
                dest_path = self.dashboard_sessions_dir / dest_filename
                
                # Check if we need to copy (if destination doesn't exist or source is newer)
                should_copy = force_update or not dest_path.exists()
                
                if not should_copy and dest_path.exists():
                    source_mtime = source_file.stat().st_mtime
                    dest_mtime = dest_path.stat().st_mtime
                    should_copy = source_mtime > dest_mtime
                
                if should_copy:
                    shutil.copy2(source_file, dest_path)
                    sync_results['copied'] += 1
                    sync_results['details'].append({
                        'file': source_file.name,
                        'action': 'copied',
                        'size': source_file.stat().st_size
                    })
                else:
                    sync_results['skipped'] += 1
                    sync_results['details'].append({
                        'file': source_file.name,
                        'action': 'skipped',
                        'reason': 'up to date'
                    })
                    
            except Exception as e:
                sync_results['errors'] += 1
                sync_results['details'].append({
                    'file': source_file.name,
                    'action': 'error',
                    'error': str(e)
                })
                print(f"Error syncing {source_file}: {e}")
        
        return sync_results
    
    def cleanup_old_sessions(self, max_age_days: int = 30) -> Dict[str, Any]:
        """Remove old session files from dashboard directory."""
        cleanup_results = {
            'total_checked': 0,
            'removed': 0,
            'errors': 0,
            'details': []
        }
        
        cutoff_time = datetime.now().timestamp() - (max_age_days * 24 * 60 * 60)
        
        for file_path in self.dashboard_sessions_dir.glob("*.json"):
            cleanup_results['total_checked'] += 1
            
            try:
                file_mtime = file_path.stat().st_mtime
                
                if file_mtime < cutoff_time:
                    file_path.unlink()
                    cleanup_results['removed'] += 1
                    cleanup_results['details'].append({
                        'file': file_path.name,
                        'action': 'removed',
                        'age_days': (datetime.now().timestamp() - file_mtime) / (24 * 60 * 60)
                    })
                    
            except Exception as e:
                cleanup_results['errors'] += 1
                cleanup_results['details'].append({
                    'file': file_path.name,
                    'action': 'error',
                    'error': str(e)
                })
        
        return cleanup_results
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get status of session sync."""
        source_files = self.find_session_logs()
        dest_files = list(self.dashboard_sessions_dir.glob("*.json"))
        
        # Count files by age
        recent_source = 0
        recent_dest = 0
        cutoff_time = datetime.now().timestamp() - (7 * 24 * 60 * 60)  # 7 days
        
        for file_path in source_files:
            if file_path.stat().st_mtime > cutoff_time:
                recent_source += 1
        
        for file_path in dest_files:
            if file_path.stat().st_mtime > cutoff_time:
                recent_dest += 1
        
        return {
            'source_files': len(source_files),
            'dest_files': len(dest_files),
            'recent_source': recent_source,
            'recent_dest': recent_dest,
            'dashboard_dir': str(self.dashboard_sessions_dir),
            'source_dirs': [str(d) for d in self.source_dirs]
        }


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Sync session logs to dashboard")
    parser.add_argument("--force", action="store_true", help="Force update all files")
    parser.add_argument("--cleanup", action="store_true", help="Clean up old session files")
    parser.add_argument("--max-age", type=int, default=30, help="Max age in days for cleanup")
    parser.add_argument("--status", action="store_true", help="Show sync status")
    
    args = parser.parse_args()
    
    syncer = SessionSync()
    
    if args.status:
        status = syncer.get_sync_status()
        print("Session Sync Status:")
        print(f"  Source files: {status['source_files']}")
        print(f"  Dashboard files: {status['dest_files']}")
        print(f"  Recent source files: {status['recent_source']}")
        print(f"  Recent dashboard files: {status['recent_dest']}")
        print(f"  Dashboard directory: {status['dashboard_dir']}")
        return
    
    if args.cleanup:
        print("Cleaning up old session files...")
        results = syncer.cleanup_old_sessions(args.max_age)
        print(f"Checked {results['total_checked']} files")
        print(f"Removed {results['removed']} old files")
        print(f"Errors: {results['errors']}")
        return
    
    print("Syncing session logs to dashboard...")
    results = syncer.sync_sessions(args.force)
    
    print(f"Found {results['total_found']} session files")
    print(f"Copied {results['copied']} files")
    print(f"Skipped {results['skipped']} files")
    print(f"Errors: {results['errors']}")
    
    if results['details']:
        print("\nDetails:")
        for detail in results['details'][:10]:  # Show first 10
            print(f"  {detail['file']}: {detail['action']}")
        if len(results['details']) > 10:
            print(f"  ... and {len(results['details']) - 10} more")


if __name__ == "__main__":
    main() 