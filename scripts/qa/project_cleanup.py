#!/usr/bin/env python3
"""
Project Cleanup Script
Safely removes dead code, duplicate files, and unnecessary archives.
"""

import os
import shutil
import sys
from pathlib import Path
from typing import List, Dict, Set
import json
from datetime import datetime


class ProjectCleaner:
    """Project cleanup manager."""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.project_root = Path(__file__).parent.parent
        self.removed_files = []
        self.removed_dirs = []
        self.preserved_files = []
        self.total_size_removed = 0
        self.skip_confirmation = False
        
    def print_header(self, title: str):
        """Print formatted header."""
        print(f"\n{'='*60}")
        print(f"[CLEANUP] {title}")
        print(f"{'='*60}")
        
    def print_action(self, action: str, path: str, size_mb: float = 0):
        """Print action."""
        if self.dry_run:
            print(f"[DRY RUN] {action}: {path}")
        else:
            print(f"[CLEANED] {action}: {path}")
        if size_mb > 0:
            print(f"  Size: {size_mb:.1f} MB")
            
    def get_dir_size(self, path: Path) -> int:
        """Get directory size in bytes."""
        if not path.exists():
            return 0
        total = 0
        try:
            for entry in path.rglob('*'):
                if entry.is_file():
                    total += entry.stat().st_size
        except (OSError, PermissionError):
            pass
        return total
        
    def identify_cleanup_targets(self) -> Dict[str, List[Path]]:
        """Identify files and directories to clean up."""
        targets = {
            'archive_backups': [],
            'duplicate_files': [],
            'temp_files': [],
            'log_files': [],
            'cache_dirs': []
        }
        
        # Archive backups (large duplicate content)
        archive_path = self.project_root / "archive" / "backups"
        if archive_path.exists():
            for backup_dir in archive_path.rglob("backup_*"):
                if backup_dir.is_dir():
                    targets['archive_backups'].append(backup_dir)
                    
        # Emergency backups (small, recent, likely redundant)
        emergency_path = self.project_root / "archive" / "emergency"
        if emergency_path.exists():
            targets['archive_backups'].extend(emergency_path.glob("*"))
            
        # Temporary and cache files
        for pattern in ['**/__pycache__', '**/*.pyc', '**/*.pyo', '**/.pytest_cache']:
            targets['cache_dirs'].extend(self.project_root.glob(pattern))
            
        # Log files (but preserve recent ones)
        log_patterns = ['**/*.log', '**/logs/*.json', '**/session_logs/*']
        for pattern in log_patterns:
            for log_file in self.project_root.glob(pattern):
                if log_file.is_file():
                    # Preserve recent logs (last 7 days)
                    try:
                        age_days = (datetime.now().timestamp() - log_file.stat().st_mtime) / (24 * 3600)
                        if age_days > 7:
                            targets['log_files'].append(log_file)
                    except OSError:
                        pass
                        
        # Duplicate batch test files
        batch_files = list(self.project_root.glob('tests/batch-legacy/test_batch_*.py'))
        if len(batch_files) > 50:  # Keep some, remove excessive duplicates
            targets['duplicate_files'].extend(batch_files[50:])
            
        return targets
        
    def calculate_cleanup_savings(self, targets: Dict[str, List[Path]]) -> Dict[str, float]:
        """Calculate potential space savings."""
        savings = {}
        
        for category, paths in targets.items():
            total_size = 0
            for path in paths:
                if path.exists():
                    if path.is_file():
                        total_size += path.stat().st_size
                    else:
                        total_size += self.get_dir_size(path)
            savings[category] = total_size / (1024 * 1024)  # Convert to MB
            
        return savings
        
    def clean_category(self, category: str, paths: List[Path]):
        """Clean a specific category of files."""
        self.print_header(f"Cleaning {category.replace('_', ' ').title()}")
        
        if not paths:
            print("[OK] No files to clean in this category")
            return
            
        for path in paths:
            if not path.exists():
                continue
                
            try:
                if path.is_file():
                    size_mb = path.stat().st_size / (1024 * 1024)
                    self.print_action("Remove file", str(path), size_mb)
                    
                    if not self.dry_run:
                        path.unlink()
                        self.removed_files.append(str(path))
                        self.total_size_removed += size_mb
                        
                elif path.is_dir():
                    size_mb = self.get_dir_size(path) / (1024 * 1024)
                    self.print_action("Remove directory", str(path), size_mb)
                    
                    if not self.dry_run:
                        shutil.rmtree(path)
                        self.removed_dirs.append(str(path))
                        self.total_size_removed += size_mb
                        
            except (OSError, PermissionError) as e:
                print(f"[ERROR] Error removing {path}: {e}")
                
    def run_cleanup(self):
        """Run the complete cleanup process."""
        self.print_header("MS11 Project Cleanup")
        
        print(f"[ANALYZE] Analyzing project at: {self.project_root}")
        print(f"[DRY RUN] Dry run mode: {self.dry_run}")
        
        # Identify targets
        targets = self.identify_cleanup_targets()
        savings = self.calculate_cleanup_savings(targets)
        
        # Show cleanup summary
        self.print_header("Cleanup Summary")
        total_savings = sum(savings.values())
        
        for category, mb_saved in savings.items():
            file_count = len(targets[category])
            print(f"[FOLDER] {category.replace('_', ' ').title()}: {file_count} items, {mb_saved:.1f} MB")
            
        print(f"\n[SPACE] Total potential savings: {total_savings:.1f} MB ({total_savings/1024:.2f} GB)")
        
        if total_savings < 1:
            print("[OK] Project is already clean! No significant cleanup needed.")
            return
            
        # Confirm cleanup
        if not self.dry_run and not self.skip_confirmation:
            response = input(f"\n[CONFIRM] Proceed with cleanup? This will free {total_savings:.1f} MB (y/N): ")
            if response.lower() not in ['y', 'yes']:
                print("[CANCEL] Cleanup cancelled")
                return
        
        # Perform cleanup
        for category, paths in targets.items():
            if paths and savings[category] > 0.1:  # Only clean if > 0.1 MB
                self.clean_category(category, paths)
                
        # Final summary
        self.print_header("Cleanup Complete")
        if self.dry_run:
            print(f"[DRY RUN] Dry run completed - no files were actually removed")
            print(f"[SPACE] Would have freed: {total_savings:.1f} MB")
            print(f"[INFO] Run with --execute to perform actual cleanup")
        else:
            print(f"[SUCCESS] Cleanup completed successfully!")
            print(f"[SPACE] Space freed: {self.total_size_removed:.1f} MB")
            print(f"[FILES] Files removed: {len(self.removed_files)}")
            print(f"[DIRS] Directories removed: {len(self.removed_dirs)}")


def main():
    """Main cleanup function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean up MS11 project")
    parser.add_argument('--execute', action='store_true', 
                       help='Execute cleanup (default is dry run)')
    parser.add_argument('--yes', action='store_true',
                       help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    # Run cleanup
    cleaner = ProjectCleaner(dry_run=not args.execute)
    cleaner.skip_confirmation = args.yes
    
    try:
        cleaner.run_cleanup()
        
        if args.execute:
            print("\n[NEXT] Next steps:")
            print("1. Test the project: python scripts/quick_test_ms11.py")
            print("2. Commit changes: git add -A && git commit -m 'Clean up project archives'")
            print("3. Check project still works correctly")
            
    except KeyboardInterrupt:
        print("\n\n[CANCEL] Cleanup cancelled by user")
    except Exception as e:
        print(f"\n[ERROR] Cleanup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()