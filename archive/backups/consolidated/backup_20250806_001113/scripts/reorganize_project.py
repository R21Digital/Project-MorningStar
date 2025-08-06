#!/usr/bin/env python3
"""
Project MorningStar - Reorganization Script

This script reorganizes the project structure to improve maintainability and developer experience.
It handles file conflicts and creates a clean, organized structure.
"""

import os
import shutil
import glob
from pathlib import Path
from datetime import datetime

class ProjectReorganizer:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def create_backup(self):
        """Create a backup of the current project structure."""
        print("📦 Creating backup...")
        shutil.copytree(self.project_root, self.backup_dir, ignore=shutil.ignore_patterns(
            '.git', '__pycache__', '*.pyc', 'backup_*', '.claude'
        ))
        print(f"✅ Backup created at: {self.backup_dir}")
    
    def create_directories(self):
        """Create the new directory structure."""
        directories = [
            "batches/summaries",
            "batches/demos", 
            "batches/reports",
            "docs/guides",
            "docs/api",
            "docs/architecture",
            "tests/unit",
            "tests/integration",
            "tests/fixtures",
            "tools/linting",
            "tools/analysis",
            "config/development",
            "config/production", 
            "config/testing",
            "requirements/base",
            "requirements/dev",
            "requirements/test"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"📁 Created: {directory}")
            except FileExistsError:
                print(f"📁 Directory already exists: {directory}")
    
    def move_batch_files(self):
        """Move batch files to their new organized locations."""
        print("\n📋 Moving batch files...")
        
        # Move implementation summaries
        summaries = glob.glob("BATCH_*_IMPLEMENTATION_SUMMARY.md")
        for summary in summaries:
            dest = self.project_root / "batches" / "summaries" / Path(summary).name
            if dest.exists():
                # Add timestamp to avoid conflicts
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name_parts = Path(summary).stem.split('_')
                new_name = f"{name_parts[0]}_{name_parts[1]}_{timestamp}_IMPLEMENTATION_SUMMARY.md"
                dest = self.project_root / "batches" / "summaries" / new_name
            
            shutil.move(summary, dest)
            print(f"  📄 Moved: {summary} → batches/summaries/")
        
        # Move demo files
        demos = glob.glob("demo_batch_*.py")
        for demo in demos:
            dest = self.project_root / "batches" / "demos" / Path(demo).name
            if dest.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name_parts = Path(demo).stem.split('_')
                new_name = f"{name_parts[0]}_{name_parts[1]}_{timestamp}.py"
                dest = self.project_root / "batches" / "demos" / new_name
            
            shutil.move(demo, dest)
            print(f"  🎯 Moved: {demo} → batches/demos/")
        
        # Move test reports
        reports = glob.glob("*_TEST_REPORT_*.json")
        reports.extend(glob.glob("*_VERIFICATION_*.json"))
        for report in reports:
            dest = self.project_root / "batches" / "reports" / Path(report).name
            if dest.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name_parts = Path(report).stem.split('_')
                new_name = f"{name_parts[0]}_{name_parts[1]}_{timestamp}.json"
                dest = self.project_root / "batches" / "reports" / new_name
            
            shutil.move(report, dest)
            print(f"  📊 Moved: {report} → batches/reports/")
    
    def organize_test_files(self):
        """Organize test files into unit and integration tests."""
        print("\n🧪 Organizing test files...")
        
        # Move existing test files to unit tests
        test_files = glob.glob("tests/test_*.py")
        for test_file in test_files:
            if "test_batch_" not in test_file:  # Skip batch tests for now
                dest = self.project_root / "tests" / "unit" / Path(test_file).name
                if dest.exists():
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    name_parts = Path(test_file).stem.split('_')
                    new_name = f"{name_parts[0]}_{name_parts[1]}_{timestamp}.py"
                    dest = self.project_root / "tests" / "unit" / new_name
                
                shutil.move(test_file, dest)
                print(f"  🧪 Moved: {test_file} → tests/unit/")
        
        # Move batch test files to integration tests
        batch_tests = glob.glob("test_batch_*.py")
        for test_file in batch_tests:
            dest = self.project_root / "tests" / "integration" / Path(test_file).name
            if dest.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name_parts = Path(test_file).stem.split('_')
                new_name = f"{name_parts[0]}_{name_parts[1]}_{timestamp}.py"
                dest = self.project_root / "tests" / "integration" / new_name
            
            shutil.move(test_file, dest)
            print(f"  🔗 Moved: {test_file} → tests/integration/")
    
    def organize_config_files(self):
        """Organize configuration files."""
        print("\n⚙️ Organizing configuration files...")
        
        # Move config files to development environment
        config_files = glob.glob("config/*.json")
        for config_file in config_files:
            dest = self.project_root / "config" / "development" / Path(config_file).name
            if dest.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                name_parts = Path(config_file).stem.split('_')
                new_name = f"{name_parts[0]}_{timestamp}.json"
                dest = self.project_root / "config" / "development" / new_name
            
            shutil.move(config_file, dest)
            print(f"  ⚙️ Moved: {config_file} → config/development/")
    
    def create_batch_index(self):
        """Create an index file for easy batch navigation."""
        print("\n📑 Creating batch index...")
        
        index_content = """# Project MorningStar - Batch Implementation Index

This file provides an organized index of all batch implementations in the project.

## 📋 Implementation Summaries

"""
        
        summaries_dir = self.project_root / "batches" / "summaries"
        if summaries_dir.exists():
            summaries = list(summaries_dir.glob("*.md"))
            summaries.sort()
            
            for summary in summaries:
                batch_num = summary.stem.split('_')[1] if '_' in summary.stem else "Unknown"
                index_content += f"- [Batch {batch_num}](summaries/{summary.name})\n"
        
        index_content += """
## 🎯 Demo Scripts

"""
        
        demos_dir = self.project_root / "batches" / "demos"
        if demos_dir.exists():
            demos = list(demos_dir.glob("*.py"))
            demos.sort()
            
            for demo in demos:
                batch_num = demo.stem.split('_')[1] if '_' in demo.stem else "Unknown"
                index_content += f"- [Batch {batch_num} Demo](demos/{demo.name})\n"
        
        index_content += """
## 📊 Test Reports

"""
        
        reports_dir = self.project_root / "batches" / "reports"
        if reports_dir.exists():
            reports = list(reports_dir.glob("*.json"))
            reports.sort()
            
            for report in reports:
                batch_num = report.stem.split('_')[1] if '_' in report.stem else "Unknown"
                index_content += f"- [Batch {batch_num} Report](reports/{report.name})\n"
        
        # Write index file
        index_file = self.project_root / "batches" / "README.md"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(index_content)
        
        print(f"  📑 Created: batches/README.md")
    
    def create_project_structure_doc(self):
        """Create documentation for the new project structure."""
        print("\n📚 Creating project structure documentation...")
        
        structure_doc = """# Project MorningStar - New Structure

## 📁 Directory Organization

### 🧪 Development & Testing
- `tests/unit/` - Unit tests for individual components
- `tests/integration/` - Integration tests for batch implementations
- `tests/fixtures/` - Test data and fixtures
- `tools/linting/` - Code quality tools
- `tools/analysis/` - Code analysis tools

### 📚 Documentation
- `docs/guides/` - User guides and tutorials
- `docs/api/` - API documentation
- `docs/architecture/` - System architecture docs
- `batches/summaries/` - Implementation summaries
- `batches/demos/` - Demo scripts
- `batches/reports/` - Test reports

### 🔧 Configuration
- `config/development/` - Development environment configs
- `config/production/` - Production environment configs
- `config/testing/` - Test environment configs
- `requirements/base/` - Base dependencies
- `requirements/dev/` - Development dependencies
- `requirements/test/` - Test dependencies

### 🌐 Public Components (SWGDB)
- `swgdb_site/` - Main website
- `api/` - Public APIs
- `dashboard/` - Admin dashboard
- `website/` - Site configuration

### 🤖 Private Components (MS11)
- `core/` - Core automation engine
- `src/` - Source code
- `android_ms11/` - Mobile companion
- `auth/` - Authentication

### 📊 Data & Assets
- `data/` - Game data
- `assets/` - Static assets
- `backups/` - Backup data

## 🚀 Benefits

1. **Clear Separation**: Code, docs, tests, and configs are clearly separated
2. **Easy Navigation**: Related files are grouped together
3. **Better Maintainability**: Organized structure makes maintenance easier
4. **Improved Developer Experience**: Clear paths for different types of contributions
5. **Professional Structure**: Follows Python project best practices

## 📋 Migration Summary

- ✅ Batch files organized into summaries, demos, and reports
- ✅ Test files separated into unit and integration tests
- ✅ Configuration files organized by environment
- ✅ Documentation structured for easy navigation
- ✅ Backup created for safety

## 🔄 Next Steps

1. Update import paths in moved files
2. Update documentation references
3. Test the new structure
4. Update CI/CD pipelines if needed
5. Train team on new organization

---
*Reorganized on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
""".format(datetime=datetime)
        
        doc_file = self.project_root / "PROJECT_STRUCTURE.md"
        with open(doc_file, 'w', encoding='utf-8') as f:
            f.write(structure_doc)
        
        print(f"  📚 Created: PROJECT_STRUCTURE.md")
    
    def run(self):
        """Execute the complete reorganization."""
        print("🚀 Starting Project MorningStar Reorganization...")
        print("=" * 60)
        
        try:
            # Step 1: Create backup
            self.create_backup()
            
            # Step 2: Create new directory structure
            self.create_directories()
            
            # Step 3: Move batch files
            self.move_batch_files()
            
            # Step 4: Organize test files
            self.organize_test_files()
            
            # Step 5: Organize config files
            self.organize_config_files()
            
            # Step 6: Create batch index
            self.create_batch_index()
            
            # Step 7: Create project structure documentation
            self.create_project_structure_doc()
            
            print("\n" + "=" * 60)
            print("✅ Project reorganization completed successfully!")
            print(f"📦 Backup available at: {self.backup_dir}")
            print("📚 Check PROJECT_STRUCTURE.md for details")
            print("📑 Check batches/README.md for batch index")
            
        except Exception as e:
            print(f"\n❌ Reorganization failed: {e}")
            print(f"📦 Restore from backup: {self.backup_dir}")
            raise

if __name__ == "__main__":
    reorganizer = ProjectReorganizer()
    reorganizer.run() 