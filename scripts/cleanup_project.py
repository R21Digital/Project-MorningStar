#!/usr/bin/env python3
"""
Project-MorningStar Cleanup Script
Automated reorganization of SWGDB + MS11 project structure
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
import json
import glob

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'cleanup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ProjectCleanup:
    """Handles the automated cleanup and reorganization"""
    
    def __init__(self, dry_run=True):
        self.dry_run = dry_run
        self.root_path = Path(".")
        self.moved_files = []
        self.deleted_files = []
        self.created_dirs = []
        
        logger.info(f"Starting Project Cleanup (DRY_RUN: {dry_run})")
        
    def run_cleanup(self):
        """Execute the full cleanup process"""
        try:
            # Phase 1: Create emergency backup
            self.create_emergency_backup()
            
            # Phase 2: Create new directory structure  
            self.create_directory_structure()
            
            # Phase 3: Move batch files to archive
            self.organize_batch_files()
            
            # Phase 4: Clean up test files
            self.organize_test_files()
            
            # Phase 5: Isolate MS11 components
            self.isolate_ms11_components()
            
            # Phase 6: Clean root directory
            self.clean_root_directory()
            
            # Phase 7: Organize backup directories
            self.consolidate_backups()
            
            # Phase 8: Update configuration files
            self.update_config_files()
            
            # Phase 9: Generate cleanup report
            self.generate_cleanup_report()
            
            logger.info("Project cleanup completed successfully!")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            raise

    def create_emergency_backup(self):
        """Create emergency backup before cleanup"""
        logger.info("Creating emergency backup...")
        
        backup_name = f"emergency-backup-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = Path("archive/emergency") / backup_name
        
        if not self.dry_run:
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Backup critical files only (not full repo due to size)
            critical_files = [
                "README.md", "requirements.txt", "package.json", 
                "pyproject.toml", "Makefile", "LICENSE"
            ]
            
            for file_name in critical_files:
                if Path(file_name).exists():
                    shutil.copy2(file_name, backup_path / file_name)
                    
            logger.info(f"Created emergency backup at: {backup_path}")
        else:
            logger.info(f"[DRY RUN] Would create backup at: {backup_path}")

    def create_directory_structure(self):
        """Create the new organized directory structure"""
        logger.info("Creating new directory structure...")
        
        directories = [
            # Public SWGDB structure
            "SWGDB-PUBLIC/src",
            "SWGDB-PUBLIC/data/heroics",
            "SWGDB-PUBLIC/data/builds", 
            "SWGDB-PUBLIC/data/quests",
            "SWGDB-PUBLIC/data/loot",
            "SWGDB-PUBLIC/assets/css",
            "SWGDB-PUBLIC/assets/js",
            "SWGDB-PUBLIC/assets/images",
            "SWGDB-PUBLIC/api",
            "SWGDB-PUBLIC/docs",
            "SWGDB-PUBLIC/tests/unit",
            "SWGDB-PUBLIC/tests/integration",
            
            # Private MS11 structure  
            "MS11-PRIVATE/core",
            "MS11-PRIVATE/android_ms11",
            "MS11-PRIVATE/modes",
            "MS11-PRIVATE/data",
            "MS11-PRIVATE/auth",
            "MS11-PRIVATE/safety",
            "MS11-PRIVATE/tests",
            "MS11-PRIVATE/profiles",
            
            # Archive structure
            "archive/batches/summaries",
            "archive/batches/implementations", 
            "archive/batches/test-reports",
            "archive/legacy-code/deprecated",
            "archive/legacy-code/experimental",
            "archive/backups/consolidated",
            "archive/emergency",
            
            # Development tools
            "development/scripts",
            "development/tools", 
            "development/playground",
            
            # Tests reorganization
            "tests/unit/combat",
            "tests/unit/questing",
            "tests/unit/api",
            "tests/integration/dashboard", 
            "tests/batch-legacy",
            "tests/fixtures",
            
            # Documentation
            "docs/user-guides",
            "docs/development",
            "docs/api",
            "docs/deployment"
        ]
        
        for directory in directories:
            dir_path = Path(directory)
            if not self.dry_run:
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    self.created_dirs.append(str(dir_path))
                except OSError as e:
                    logger.warning(f"Directory already exists or cannot be created: {dir_path} - {e}")
            else:
                logger.info(f"[DRY RUN] Would create: {dir_path}")

    def organize_batch_files(self):
        """Move all batch files to archive"""
        logger.info("Organizing batch files...")
        
        # Batch summary files
        batch_summaries = list(Path(".").glob("BATCH_*_FINAL_SUMMARY.md"))
        batch_summaries.extend(Path(".").glob("BATCH_*_SUMMARY.md"))
        batch_summaries.extend(Path(".").glob("BATCH_*_STATUS.md"))
        
        for batch_file in batch_summaries:
            dest = Path("archive/batches/summaries") / batch_file.name
            self._move_file(batch_file, dest)
        
        # Other batch documentation
        other_batch_docs = [
            "BATCHES_027_035_IMPLEMENTATION_SUMMARY.md",
            "BATCH_STATUS_UPDATE.md",
            "IMPLEMENTATION_SUMMARY.md",
            "PROJECT_IMPROVEMENTS.md",
            "PROJECT_REORGANIZATION_PLAN.md",
            "PROJECT_REORGANIZATION_STATUS.md", 
            "NPC_VALIDATION_FIX_SUMMARY.md",
            "FINAL_STATUS.md"
        ]
        
        for doc_file in other_batch_docs:
            if Path(doc_file).exists():
                dest = Path("archive/batches/implementations") / doc_file
                self._move_file(Path(doc_file), dest)

    def organize_test_files(self):
        """Organize all test files"""
        logger.info("Organizing test files...")
        
        # Move batch test files to legacy
        batch_tests = list(Path(".").glob("test_batch_*.py"))
        for test_file in batch_tests:
            dest = Path("tests/batch-legacy") / test_file.name
            self._move_file(test_file, dest)
        
        # Move demo files to archive
        demo_files = list(Path(".").glob("demo_*.py"))
        demo_files.extend(Path(".").glob("demo_*.json"))
        demo_files.extend(Path(".").glob("demo_*.log"))
        
        for demo_file in demo_files:
            dest = Path("archive/legacy-code/experimental") / demo_file.name
            self._move_file(demo_file, dest)
        
        # Clean up validation and temp files
        cleanup_patterns = [
            "codex_validation_*.py",
            "validate_*.py", 
            "temp_*.json",
            "*_report_*.json",
            "buff_advisor_report_*.json",
            "combat_feedback_report_*.json"
        ]
        
        for pattern in cleanup_patterns:
            for file_path in Path(".").glob(pattern):
                if file_path.name not in ["validate_batch_192.py"]:  # Keep specific files
                    dest = Path("archive/legacy-code/deprecated") / file_path.name
                    self._move_file(file_path, dest)

    def isolate_ms11_components(self):
        """Move MS11 components to private directory"""
        logger.info("Isolating MS11 components...")
        
        ms11_dirs = [
            "core",
            "android_ms11", 
            "auth",
            "safety"
        ]
        
        for ms11_dir in ms11_dirs:
            if Path(ms11_dir).exists():
                dest = Path("MS11-PRIVATE") / ms11_dir
                self._move_directory(Path(ms11_dir), dest)

    def consolidate_backups(self):
        """Consolidate recent backup directories"""
        logger.info("Consolidating backup directories...")
        
        backup_patterns = ["backup_20250806_*"]
        
        for pattern in backup_patterns:
            for backup_dir in Path(".").glob(pattern):
                if backup_dir.is_dir():
                    dest = Path("archive/backups/consolidated") / backup_dir.name
                    self._move_directory(backup_dir, dest)

    def clean_root_directory(self):
        """Clean up remaining clutter in root directory"""
        logger.info("Cleaning root directory...")
        
        # Files to delete (safe temp files)
        delete_patterns = [
            "*.log",
            "swgtracker_dashboard.*",
            "test_alerts.json",
            "simple_main.py",
            "whisper_monitor.py"
        ]
        
        for pattern in delete_patterns:
            for file_path in Path(".").glob(pattern):
                # Skip important log files
                if file_path.name.startswith("cleanup_"):
                    continue
                self._delete_file(file_path)
        
        # Move miscellaneous development files
        dev_files = [
            "run.py",
            "run_quest.py", 
            "game_bridge.py",
            "discord_relay.py",
            "main.py",
            "main_discord_bot.py",
            "main_state_runner.py"
        ]
        
        for dev_file in dev_files:
            if Path(dev_file).exists():
                dest = Path("development/scripts") / dev_file
                self._move_file(Path(dev_file), dest)

    def update_config_files(self):
        """Update configuration files for new structure"""
        logger.info("Updating configuration files...")
        
        # Update .gitignore
        gitignore_content = self._generate_gitignore()
        if not self.dry_run:
            with open(".gitignore", "w") as f:
                f.write(gitignore_content)
            logger.info("Updated .gitignore")
        else:
            logger.info("[DRY RUN] Would update .gitignore")

    def _generate_gitignore(self):
        """Generate updated .gitignore content"""
        return """# MS11 Private Components - NEVER COMMIT TO PUBLIC
MS11-PRIVATE/
*_ms11*
*_private*
*.ms11

# Build artifacts and dependencies
node_modules/
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.env
.venv
pip-log.txt
pip-delete-this-directory.txt

# IDEs and editors
.vscode/
.idea/
*.swp
*.swo
.sublime-workspace
.sublime-project

# OS files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs and temporary files
*.log
logs/
tmp/
temp/
cache/

# Test coverage and reports
htmlcov/
.coverage
.pytest_cache/
.nyc_output/
coverage/

# Build outputs
dist/
build/
*.egg-info/

# Archive directories (optional - include if you want to track)
# archive/
# development/playground/

# Database files
*.db
*.sqlite
*.sqlite3

# Backup files
*.backup
*.bak
*.tmp

# Claude Code specific
.claude/
"""

    def _move_file(self, src: Path, dest: Path):
        """Move a file with logging"""
        if not src.exists():
            return
            
        if not self.dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest))
            self.moved_files.append((str(src), str(dest)))
            logger.info(f"Moved: {src} → {dest}")
        else:
            logger.info(f"[DRY RUN] Would move: {src} → {dest}")

    def _move_directory(self, src: Path, dest: Path):
        """Move a directory with logging"""
        if not src.exists():
            return
            
        if not self.dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest))
            self.moved_files.append((str(src), str(dest)))
            logger.info(f"Moved directory: {src} → {dest}")
        else:
            logger.info(f"[DRY RUN] Would move directory: {src} → {dest}")

    def _delete_file(self, file_path: Path):
        """Delete a file with logging"""
        if not file_path.exists():
            return
            
        if not self.dry_run:
            file_path.unlink()
            self.deleted_files.append(str(file_path))
            logger.info(f"Deleted: {file_path}")
        else:
            logger.info(f"[DRY RUN] Would delete: {file_path}")

    def generate_cleanup_report(self):
        """Generate a detailed cleanup report"""
        logger.info("Generating cleanup report...")
        
        report = {
            "cleanup_date": datetime.now().isoformat(),
            "dry_run": self.dry_run,
            "summary": {
                "directories_created": len(self.created_dirs),
                "files_moved": len(self.moved_files), 
                "files_deleted": len(self.deleted_files)
            },
            "details": {
                "created_directories": self.created_dirs,
                "moved_files": self.moved_files,
                "deleted_files": self.deleted_files
            }
        }
        
        report_file = f"cleanup_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        if not self.dry_run:
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)
            logger.info(f"Generated cleanup report: {report_file}")
        else:
            logger.info(f"[DRY RUN] Would generate report: {report_file}")
            print("\nCleanup Summary:")
            print(f"  Directories to create: {len(self.created_dirs)}")
            print(f"  Files to move: {len(self.moved_files)}")
            print(f"  Files to delete: {len(self.deleted_files)}")

def main():
    """Main function with safety checks"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean up Project-MorningStar repository structure")
    parser.add_argument("--dry-run", action="store_true", default=True,
                       help="Run in dry-run mode (default: True)")
    parser.add_argument("--execute", action="store_true", default=False,
                       help="Actually execute the cleanup (DANGEROUS!)")
    
    args = parser.parse_args()
    
    # Safety check
    if args.execute:
        print("WARNING: This will permanently reorganize your repository!")
        print("Actions that will be performed:")
        print("   - Move 200+ batch files to archive/")
        print("   - Move 200+ test files to organized structure")  
        print("   - Move MS11 components to private directory")
        print("   - Delete temporary and demo files")
        print("   - Reorganize directory structure")
        
        confirm = input("\nType 'CONFIRM' to proceed: ")
        if confirm != "CONFIRM":
            print("Cleanup cancelled")
            return
        
        dry_run = False
    else:
        dry_run = True
        print("Running in DRY-RUN mode (no changes will be made)")
        print("Use --execute to actually perform the cleanup")
    
    # Execute cleanup
    cleanup = ProjectCleanup(dry_run=dry_run)
    cleanup.run_cleanup()

if __name__ == "__main__":
    main()