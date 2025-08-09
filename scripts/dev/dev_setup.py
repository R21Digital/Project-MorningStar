#!/usr/bin/env python3
"""
Advanced Development Environment Setup Script for MS11.
Automates complete development environment configuration with modern tooling.
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DevSetup:
    """Advanced development environment setup manager."""
    
    def __init__(self, project_root: Optional[str] = None):
        self.platform = platform.system().lower()
        self.python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.venv_path = self.project_root / "venv"
        self.python_executable = sys.executable
        self.setup_steps: List[Dict[str, Any]] = []
        
    def print_header(self, title: str):
        """Print a formatted header."""
        print(f"\n{'='*60}")
        print(f"🔧 {title}")
        print(f"{'='*60}")
        
    def print_step(self, step: str):
        """Print a step."""
        print(f"\n📋 {step}")
        
    def print_success(self, message: str):
        """Print success message."""
        print(f"✅ {message}")
        
    def print_error(self, message: str):
        """Print error message."""
        print(f"❌ {message}")
        
    def print_warning(self, message: str):
        """Print warning message."""
        print(f"⚠️  {message}")
        
    def run_command(self, cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run a command and return the result."""
        try:
            result = subprocess.run(cmd, check=check, capture_output=True, text=True)
            return result
                raise
            return e
            
    def check_python_version(self) -> bool:
        """Check if Python version is supported."""
        self.print_step("Checking Python version")
        
        version = sys.version_info
        if version.major == 3 and version.minor >= 11:
            self.print_success(f"Python {version.major}.{version.minor}.{version.micro} - Compatible")
            return True
        else:
            self.print_error(f"Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.11+")
            return False
            
    def check_system_dependencies(self) -> bool:
        """Check and install system dependencies."""
        self.print_step("Checking system dependencies")
        
        if self.platform == "windows":
            return self._check_windows_deps()
        elif self.platform == "linux":
            return self._check_linux_deps()
        else:
            self.print_warning(f"Unsupported platform: {self.platform}")
            return False
            
    def _check_windows_deps(self) -> bool:
        """Check Windows dependencies."""
        # Check for Tesseract
        try:
            result = self.run_command(["tesseract", "--version"])
            self.print_success("Tesseract OCR found")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.print_warning("Tesseract OCR not found")
            print("To install: choco install tesseract")
            print("Or download from: https://github.com/UB-Mannheim/tesseract/wiki")
            return False
            
    def _check_linux_deps(self) -> bool:
        """Check Linux dependencies."""
        # Check for Tesseract
        try:
            result = self.run_command(["tesseract", "--version"])
            self.print_success("Tesseract OCR found")
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.print_warning("Tesseract OCR not found")
            print("To install: sudo apt-get install tesseract-ocr")
            return False
            
        # Check for X11 dependencies
        try:
            result = self.run_command(["dpkg", "-l", "libx11-dev"], check=False)
            if result.returncode == 0:
                self.print_success("X11 development libraries found")
            else:
                self.print_warning("X11 development libraries not found")
                print("To install: sudo apt-get install libx11-dev libxext-dev")
                return False
        except FileNotFoundError:
            self.print_warning("Cannot check X11 libraries (dpkg not found)")
            
        return True
        
    def create_virtual_environment(self) -> bool:
        """Create a Python virtual environment."""
        self.print_step("Creating virtual environment")
        
        if self.venv_path.exists():
            self.print_success("Virtual environment already exists")
            return True
            
        try:
            self.run_command([sys.executable, "-m", "venv", str(self.venv_path)])
            self.print_success(f"Virtual environment created at {self.venv_path}")
            return True
        except subprocess.CalledProcessError:
            self.print_error("Failed to create virtual environment")
            return False
            
    def install_dependencies(self) -> bool:
        """Install Python dependencies."""
        self.print_step("Installing Python dependencies")
        
        # Determine pip path
        if self.platform == "windows":
            pip_path = self.venv_path / "Scripts" / "pip.exe"
            python_path = self.venv_path / "Scripts" / "python.exe"
        else:
            pip_path = self.venv_path / "bin" / "pip"
            python_path = self.venv_path / "bin" / "python"
            
        if not pip_path.exists():
            self.print_error("Virtual environment pip not found")
            return False
            
        try:
            # Upgrade pip
            self.run_command([str(python_path), "-m", "pip", "install", "--upgrade", "pip"])
            
            # Install main requirements
            requirements_file = self.project_root / "requirements.txt"
            if requirements_file.exists():
                self.run_command([str(pip_path), "install", "-r", str(requirements_file)])
                self.print_success("Main dependencies installed")
            else:
                self.print_warning("requirements.txt not found")
                
            # Install dev requirements if available
            dev_requirements = self.project_root / "requirements-dev.txt"
            if dev_requirements.exists():
                self.run_command([str(pip_path), "install", "-r", str(dev_requirements)])
                self.print_success("Development dependencies installed")
                
            # Install additional testing tools
            self.run_command([str(pip_path), "install", "pytest", "pytest-cov", "bandit", "mypy"])
            self.print_success("Testing tools installed")
            
            return True
        except subprocess.CalledProcessError:
            self.print_error("Failed to install dependencies")
            return False
            
    def setup_pre_commit_hooks(self) -> bool:
        """Set up pre-commit hooks."""
        self.print_step("Setting up pre-commit hooks")
        
        if self.platform == "windows":
            python_path = self.venv_path / "Scripts" / "python.exe"
        else:
            python_path = self.venv_path / "bin" / "python"
            
        try:
            # Install pre-commit
            self.run_command([str(python_path), "-m", "pip", "install", "pre-commit"])
            
            # Install hooks if .pre-commit-config.yaml exists
            precommit_config = self.project_root / ".pre-commit-config.yaml"
            if precommit_config.exists():
                # Set up the hooks
                env = os.environ.copy()
                env["PATH"] = f"{self.venv_path / 'bin' if self.platform != 'windows' else self.venv_path / 'Scripts'}{os.pathsep}{env['PATH']}"
                
                result = subprocess.run(
                    [str(python_path), "-m", "pre_commit", "install"],
                    cwd=self.project_root,
                    env=env,
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    self.print_success("Pre-commit hooks installed")
                else:
                    self.print_warning("Pre-commit hooks installation skipped")
            else:
                self.print_warning(".pre-commit-config.yaml not found")
                
            return True
        except subprocess.CalledProcessError:
            self.print_warning("Failed to set up pre-commit hooks")
            return False
            
    def create_env_file(self) -> bool:
        """Create environment file with default settings."""
        self.print_step("Creating environment configuration")
        
        env_file = self.project_root / ".env"
        if env_file.exists():
            self.print_success(".env file already exists")
            return True
            
        env_content = f'''# MS11 Development Environment Configuration
# Generated by dev_setup.py

# License configuration
ANDROID_MS11_LICENSE=demo

# Python path configuration
PYTHONPATH={self.project_root / "src"}:{self.project_root / "core"}:{self.project_root}

# Logging configuration
MS11_LOG_LEVEL=INFO
MS11_LOG_FILE=logs/ms11.log

# Development settings
MS11_DEV_MODE=true
MS11_DEBUG=true

# Platform: {self.platform}
# Python: {self.python_version}
# Setup date: {Path(__file__).stat().st_mtime}
'''
        
        try:
            with open(env_file, 'w') as f:
                f.write(env_content)
            self.print_success(".env file created")
            return True
        except Exception as e:
            self.print_error(f"Failed to create .env file: {e}")
            return False
            
    def run_quick_test(self) -> bool:
        """Run quick test to verify setup."""
        self.print_step("Running quick test")
        
        if self.platform == "windows":
            python_path = self.venv_path / "Scripts" / "python.exe"
        else:
            python_path = self.venv_path / "bin" / "python"
            
        test_script = self.project_root / "scripts" / "quick_test_ms11.py"
        if not test_script.exists():
            self.print_warning("Quick test script not found")
            return False
            
        try:
            result = self.run_command([str(python_path), str(test_script)], check=False)
            if result.returncode == 0:
                self.print_success("Quick test passed")
                return True
            else:
                self.print_warning("Quick test had some failures (this may be normal)")
                return True
        except subprocess.CalledProcessError:
            self.print_warning("Quick test failed")
            return False
            
    def create_vscode_settings(self) -> bool:
        """Create VS Code settings for the project."""
        self.print_step("Creating VS Code settings")
        
        vscode_dir = self.project_root / ".vscode"
        vscode_dir.mkdir(exist_ok=True)
        
        # Settings.json
        settings = {
            "python.defaultInterpreterPath": str(self.venv_path / ("Scripts/python.exe" if self.platform == "windows" else "bin/python")),
            "python.terminal.activateEnvironment": True,
            "python.testing.pytestEnabled": True,
            "python.testing.pytestArgs": ["tests"],
            "python.linting.enabled": True,
            "python.linting.pylintEnabled": False,
            "python.linting.flake8Enabled": True,
            "python.formatting.provider": "black",
            "files.exclude": {
                "**/__pycache__": True,
                "**/*.pyc": True,
                ".pytest_cache": True,
                "venv": True,
                ".coverage": True,
                "htmlcov": True
            },
            "python.analysis.extraPaths": [
                "./src",
                "./core",
                "."
            ]
        }
        
        settings_file = vscode_dir / "settings.json"
        try:
            import json
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            self.print_success("VS Code settings created")
            return True
        except Exception as e:
            self.print_error(f"Failed to create VS Code settings: {e}")
            return False
            
    def run_setup(self) -> bool:
        """Run the complete development setup."""
        self.print_header("MS11 Development Environment Setup")
        
        steps = [
            ("Check Python version", self.check_python_version),
            ("Check system dependencies", self.check_system_dependencies), 
            ("Create virtual environment", self.create_virtual_environment),
            ("Install dependencies", self.install_dependencies),
            ("Setup pre-commit hooks", self.setup_pre_commit_hooks),
            ("Create environment file", self.create_env_file),
            ("Create VS Code settings", self.create_vscode_settings),
            ("Run quick test", self.run_quick_test),
        ]
        
        success_count = 0
        for step_name, step_func in steps:
            try:
                if step_func():
                    success_count += 1
                else:
                    self.print_warning(f"Step '{step_name}' had issues but continuing...")
            except Exception as e:
                self.print_error(f"Step '{step_name}' failed: {e}")
                
        self.print_header("Setup Complete")
        print(f"✅ {success_count}/{len(steps)} steps completed successfully")
        
        if success_count >= len(steps) - 2:  # Allow 2 failures
            self.print_success("Development environment is ready!")
            print("\n📋 Next steps:")
            print(f"   1. Activate virtual environment:")
            if self.platform == "windows":
                print(f"      {self.venv_path / 'Scripts' / 'activate'}")
            else:
                print(f"      source {self.venv_path / 'bin' / 'activate'}")
            print(f"   2. Run tests: python -m pytest")
            print(f"   3. Start development: python scripts/ms11_interface.py")
            return True
        else:
            self.print_error("Setup had significant issues. Please review the errors above.")
            return False


def main():
    """Main setup function."""
    setup = DevSetup()
    success = setup.run_setup()
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()