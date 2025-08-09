#!/usr/bin/env python3
"""
Development Tools Script
Common development tasks for MS11 project.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Optional


class DevTools:
    """Development tools manager."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.venv_path = self.project_root / "venv"
        
    def print_header(self, title: str):
        """Print formatted header."""
        print(f"\n{'='*60}")
        print(f"🛠️  {title}")
        print(f"{'='*60}")
        
    def run_command(self, cmd: List[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
        """Run a command."""
        return subprocess.run(cmd, cwd=cwd or self.project_root, check=True)
        
    def get_python_path(self) -> str:
        """Get the Python executable path."""
        if os.name == "nt":  # Windows
            return str(self.venv_path / "Scripts" / "python.exe")
        else:  # Unix-like
            return str(self.venv_path / "bin" / "python")
            
    def test(self, args: argparse.Namespace):
        """Run tests."""
        self.print_header("Running Tests")
        
        cmd = [self.get_python_path(), "-m", "pytest"]
        
        if args.coverage:
            cmd.extend(["--cov=src", "--cov-report=html", "--cov-report=term"])
        
        if args.verbose:
            cmd.append("-v")
            
        if args.file:
            cmd.append(args.file)
        else:
            cmd.append("tests/")
            
        if args.markers:
            cmd.extend(["-m", args.markers])
            
        self.run_command(cmd)
        
    def lint(self, args: argparse.Namespace):
        """Run linting tools."""
        self.print_header("Running Code Quality Checks")
        
        python = self.get_python_path()
        
        # Flake8
        print("\n📋 Running flake8...")
        try:
            self.run_command([python, "-m", "flake8", "src/", "scripts/", "tests/"])
            print("✅ flake8 passed")
        except subprocess.CalledProcessError:
            print("❌ flake8 found issues")
            
        # Bandit security scan
        print("\n📋 Running bandit security scan...")
        try:
            self.run_command([python, "-m", "bandit", "-r", "src/", "-f", "json"])
            print("✅ bandit passed")
        except subprocess.CalledProcessError:
            print("❌ bandit found security issues")
            
        # MyPy type checking
        if args.mypy:
            print("\n📋 Running mypy type checking...")
            try:
                self.run_command([python, "-m", "mypy", "src/"])
                print("✅ mypy passed")
            except subprocess.CalledProcessError:
                print("❌ mypy found type issues")
                
    def format_code(self, args: argparse.Namespace):
        """Format code with black."""
        self.print_header("Formatting Code")
        
        python = self.get_python_path()
        
        cmd = [python, "-m", "black"]
        if args.check:
            cmd.append("--check")
        if args.diff:
            cmd.append("--diff")
            
        cmd.extend(["src/", "scripts/", "tests/"])
        
        self.run_command(cmd)
        
    def clean(self, args: argparse.Namespace):
        """Clean up temporary files."""
        self.print_header("Cleaning Project")
        
        import shutil
        
        patterns = [
            "**/__pycache__",
            "**/*.pyc", 
            "**/*.pyo",
            "**/*.egg-info",
            ".pytest_cache",
            ".coverage",
            "htmlcov",
            "dist",
            "build",
            ".mypy_cache"
        ]
        
        for pattern in patterns:
            for path in self.project_root.glob(pattern):
                if path.is_dir():
                    print(f"🗑️  Removing directory: {path}")
                    shutil.rmtree(path)
                else:
                    print(f"🗑️  Removing file: {path}")
                    path.unlink()
                    
        print("✅ Project cleaned")
        
    def build(self, args: argparse.Namespace):
        """Build the project."""
        self.print_header("Building Project")
        
        python = self.get_python_path()
        
        # Install in development mode
        self.run_command([python, "-m", "pip", "install", "-e", "."])
        print("✅ Project built in development mode")
        
    def quick_test(self, args: argparse.Namespace):
        """Run quick MS11 system test."""
        self.print_header("Quick System Test")
        
        python = self.get_python_path()
        test_script = self.project_root / "scripts" / "quick_test_ms11.py"
        
        self.run_command([python, str(test_script)])
        
    def interface(self, args: argparse.Namespace):
        """Start MS11 interface."""
        self.print_header("Starting MS11 Interface")
        
        python = self.get_python_path()
        interface_script = self.project_root / "scripts" / "ms11_interface.py"
        
        self.run_command([python, str(interface_script)])
        
    def dashboard(self, args: argparse.Namespace):
        """Start web dashboard."""
        self.print_header("Starting Web Dashboard")
        
        python = self.get_python_path()
        dashboard_script = self.project_root / "dashboard" / "app.py"
        
        print("🌐 Starting web dashboard at http://localhost:5000/ms11")
        self.run_command([python, str(dashboard_script)])
        
    def install(self, args: argparse.Namespace):
        """Install/update dependencies."""
        self.print_header("Installing Dependencies")
        
        python = self.get_python_path()
        
        # Update pip
        self.run_command([python, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install requirements
        requirements = self.project_root / "requirements.txt"
        if requirements.exists():
            self.run_command([python, "-m", "pip", "install", "-r", str(requirements)])
            
        # Install dev requirements
        if args.dev:
            dev_requirements = self.project_root / "requirements-dev.txt"
            if dev_requirements.exists():
                self.run_command([python, "-m", "pip", "install", "-r", str(dev_requirements)])
                
        print("✅ Dependencies installed")
        
    def docs(self, args: argparse.Namespace):
        """Generate documentation."""
        self.print_header("Generating Documentation")
        
        python = self.get_python_path()
        
        # Install docs dependencies if needed
        try:
            self.run_command([python, "-c", "import sphinx"])
        except subprocess.CalledProcessError:
            print("📦 Installing sphinx for documentation...")
            self.run_command([python, "-m", "pip", "install", "sphinx", "sphinx-rtd-theme"])
            
        docs_dir = self.project_root / "docs"
        if not docs_dir.exists():
            print("📁 Creating docs directory...")
            docs_dir.mkdir()
            
        print("📚 Documentation generation not yet implemented")
        print("📋 Available documentation:")
        for doc in docs_dir.glob("*.md"):
            print(f"   - {doc.name}")
            
    def profile(self, args: argparse.Namespace):
        """Profile MS11 performance."""
        self.print_header("Profiling MS11")
        
        python = self.get_python_path()
        
        # Install profiling tools
        try:
            self.run_command([python, "-c", "import cProfile, pstats"])
        except subprocess.CalledProcessError:
            print("❌ Profiling tools not available")
            return
            
        # Run profiling
        profile_script = f"""
import cProfile
import sys
sys.path.insert(0, '{self.project_root / "src"}')

def profile_main():
    from main import main
    main()
    
if __name__ == '__main__':
    cProfile.run('profile_main()', 'profile_output.prof')
"""
        
        profile_file = self.project_root / "profile_runner.py"
        with open(profile_file, 'w') as f:
            f.write(profile_script)
            
        try:
            self.run_command([python, str(profile_file)])
            print("✅ Profiling complete - see profile_output.prof")
        finally:
            profile_file.unlink(missing_ok=True)


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(description="MS11 Development Tools")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("--coverage", action="store_true", help="Run with coverage")
    test_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    test_parser.add_argument("--file", help="Specific test file")
    test_parser.add_argument("--markers", "-m", help="Test markers to run")
    
    # Lint command
    lint_parser = subparsers.add_parser("lint", help="Run code quality checks")
    lint_parser.add_argument("--mypy", action="store_true", help="Include mypy type checking")
    
    # Format command
    format_parser = subparsers.add_parser("format", help="Format code with black")
    format_parser.add_argument("--check", action="store_true", help="Check formatting only")
    format_parser.add_argument("--diff", action="store_true", help="Show diff")
    
    # Clean command
    clean_parser = subparsers.add_parser("clean", help="Clean temporary files")
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build project")
    
    # Quick test command
    quick_parser = subparsers.add_parser("quick-test", help="Run quick system test")
    
    # Interface commands
    interface_parser = subparsers.add_parser("interface", help="Start MS11 interface")
    dashboard_parser = subparsers.add_parser("dashboard", help="Start web dashboard")
    
    # Install command
    install_parser = subparsers.add_parser("install", help="Install/update dependencies")
    install_parser.add_argument("--dev", action="store_true", help="Include dev dependencies")
    
    # Docs command
    docs_parser = subparsers.add_parser("docs", help="Generate documentation")
    
    # Profile command
    profile_parser = subparsers.add_parser("profile", help="Profile performance")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    tools = DevTools()
    
    command_map = {
        "test": tools.test,
        "lint": tools.lint,
        "format": tools.format_code,
        "clean": tools.clean,
        "build": tools.build,
        "quick-test": tools.quick_test,
        "interface": tools.interface,
        "dashboard": tools.dashboard,
        "install": tools.install,
        "docs": tools.docs,
        "profile": tools.profile,
    }
    
    try:
        command_map[args.command](args)
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed with exit code {e.returncode}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()