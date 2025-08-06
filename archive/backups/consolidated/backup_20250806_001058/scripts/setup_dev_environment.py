#!/usr/bin/env python3
"""
Development Environment Setup Script for Project MorningStar

This script automates the setup of the development environment including:
- Virtual environment creation
- Dependency installation
- Pre-commit hooks setup
- Configuration file creation
- Database initialization
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Any
import json
import platform

class DevEnvironmentSetup:
    """Development environment setup automation."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.venv_path = self.project_root / "venv"
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        
    def run_command(self, command: List[str], cwd: Path = None) -> bool:
        """Run a command and return success status."""
        try:
            result = subprocess.run(
                command,
                cwd=cwd or self.project_root,
                check=True,
                capture_output=True,
                text=True
            )
            print(f"✅ {command[0]} completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ {command[0]} failed: {e.stderr}")
            return False
    
    def check_python_version(self) -> bool:
        """Check if Python version meets requirements."""
        if sys.version_info < (3, 8):
            print(f"❌ Python {self.python_version} detected. Python 3.8+ required.")
            return False
        print(f"✅ Python {self.python_version} detected")
        return True
    
    def create_virtual_environment(self) -> bool:
        """Create virtual environment."""
        if self.venv_path.exists():
            print("✅ Virtual environment already exists")
            return True
        
        print("🔧 Creating virtual environment...")
        return self.run_command([sys.executable, "-m", "venv", str(self.venv_path)])
    
    def get_pip_command(self) -> List[str]:
        """Get the appropriate pip command for the virtual environment."""
        if platform.system() == "Windows":
            return [str(self.venv_path / "Scripts" / "pip.exe")]
        else:
            return [str(self.venv_path / "bin" / "pip")]
    
    def get_python_command(self) -> List[str]:
        """Get the appropriate python command for the virtual environment."""
        if platform.system() == "Windows":
            return [str(self.venv_path / "Scripts" / "python.exe")]
        else:
            return [str(self.venv_path / "bin" / "python")]
    
    def install_dependencies(self) -> bool:
        """Install project dependencies."""
        pip_cmd = self.get_pip_command()
        
        print("📦 Installing base dependencies...")
        if not self.run_command(pip_cmd + ["install", "-r", "requirements.txt"]):
            return False
        
        print("📦 Installing development dependencies...")
        if not self.run_command(pip_cmd + ["install", "-r", "requirements/dev.txt"]):
            return False
        
        return True
    
    def setup_pre_commit(self) -> bool:
        """Setup pre-commit hooks."""
        python_cmd = self.get_python_command()
        
        print("🔧 Installing pre-commit...")
        if not self.run_command(python_cmd + ["-m", "pip", "install", "pre-commit"]):
            return False
        
        print("🔧 Installing pre-commit hooks...")
        return self.run_command(python_cmd + ["-m", "pre_commit", "install"])
    
    def create_config_files(self) -> bool:
        """Create default configuration files."""
        config_dir = self.project_root / "config"
        config_dir.mkdir(exist_ok=True)
        
        # Create MS11 config
        ms11_config = {
            "scanner": {
                "scan_interval": 60,
                "idle_scan_interval": 300,
                "travel_scan_interval": 30,
                "ocr_confidence_threshold": 50.0,
                "privacy_enabled": True,
                "opt_out_keywords": ["private", "no scan", "opt out", "do not track"]
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "logs/ms11.log"
            },
            "database": {
                "type": "sqlite",
                "path": "data/ms11.db"
            }
        }
        
        ms11_config_path = config_dir / "ms11_config.json"
        if not ms11_config_path.exists():
            with open(ms11_config_path, 'w') as f:
                json.dump(ms11_config, f, indent=2)
            print("✅ Created MS11 configuration file")
        
        # Create SWGDB config
        swgdb_config = {
            "site": {
                "title": "SWGDB - Star Wars Galaxies Database",
                "description": "Comprehensive SWG database and tools",
                "url": "https://swgdb.com"
            },
            "api": {
                "rate_limit": 100,
                "cors_origins": ["https://swgdb.com"]
            },
            "database": {
                "type": "sqlite",
                "path": "data/swgdb.db"
            }
        }
        
        swgdb_config_path = config_dir / "swgdb_config.json"
        if not swgdb_config_path.exists():
            with open(swgdb_config_path, 'w') as f:
                json.dump(swgdb_config, f, indent=2)
            print("✅ Created SWGDB configuration file")
        
        return True
    
    def create_directories(self) -> bool:
        """Create necessary directories."""
        directories = [
            "logs",
            "data/cache",
            "data/exports",
            "tests/artifacts",
            "docs/build",
            "batches/completed",
            "batches/in_progress",
            "batches/planned"
        ]
        
        for directory in directories:
            dir_path = self.project_root / directory
            dir_path.mkdir(parents=True, exist_ok=True)
        
        print("✅ Created necessary directories")
        return True
    
    def run_tests(self) -> bool:
        """Run initial test suite."""
        python_cmd = self.get_python_command()
        
        print("🧪 Running test suite...")
        return self.run_command(python_cmd + ["-m", "pytest", "tests/", "-v"])
    
    def create_git_hooks(self) -> bool:
        """Create additional git hooks."""
        git_hooks_dir = self.project_root / ".git" / "hooks"
        
        # Create pre-push hook
        pre_push_hook = """#!/bin/sh
# Pre-push hook to run tests and checks
echo "Running pre-push checks..."
python -m pytest tests/ -q
python -m mypy src/
python -m black --check src/
python -m isort --check-only src/
"""
        
        pre_push_path = git_hooks_dir / "pre-push"
        with open(pre_push_path, 'w') as f:
            f.write(pre_push_hook)
        os.chmod(pre_push_path, 0o755)
        
        print("✅ Created git hooks")
        return True
    
    def print_next_steps(self):
        """Print next steps for the developer."""
        print("\n" + "="*60)
        print("🎉 Development Environment Setup Complete!")
        print("="*60)
        
        print("\n📋 Next Steps:")
        print("1. Activate the virtual environment:")
        if platform.system() == "Windows":
            print("   venv\\Scripts\\activate")
        else:
            print("   source venv/bin/activate")
        
        print("\n2. Run the test suite:")
        print("   pytest tests/ -v")
        
        print("\n3. Start development:")
        print("   # Edit code in src/")
        print("   # Run tests: pytest")
        print("   # Format code: black src/")
        print("   # Type check: mypy src/")
        
        print("\n4. Pre-commit hooks are installed:")
        print("   # They will run automatically on commit")
        print("   # Or run manually: pre-commit run --all-files")
        
        print("\n5. Useful commands:")
        print("   # Install new dependencies: pip install package")
        print("   # Update requirements: pip freeze > requirements.txt")
        print("   # Run coverage: pytest --cov=src tests/")
        print("   # Lint code: ruff check src/")
        
        print("\n📚 Documentation:")
        print("- README.md: Project overview")
        print("- PROJECT_IMPROVEMENTS.md: Improvement roadmap")
        print("- docs/: Detailed documentation")
        
        print("\n🚀 Happy coding!")
    
    def setup(self) -> bool:
        """Run the complete setup process."""
        print("🚀 Setting up Project MorningStar development environment...")
        print("="*60)
        
        steps = [
            ("Checking Python version", self.check_python_version),
            ("Creating virtual environment", self.create_virtual_environment),
            ("Installing dependencies", self.install_dependencies),
            ("Setting up pre-commit hooks", self.setup_pre_commit),
            ("Creating configuration files", self.create_config_files),
            ("Creating directories", self.create_directories),
            ("Creating git hooks", self.create_git_hooks),
            ("Running initial tests", self.run_tests),
        ]
        
        for step_name, step_func in steps:
            print(f"\n🔧 {step_name}...")
            if not step_func():
                print(f"❌ Setup failed at: {step_name}")
                return False
        
        self.print_next_steps()
        return True

def main():
    """Main setup function."""
    setup = DevEnvironmentSetup()
    success = setup.setup()
    
    if success:
        print("\n✅ Setup completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 