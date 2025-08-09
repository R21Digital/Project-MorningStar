#!/usr/bin/env python3
"""
MS11 System Launcher
Comprehensive launcher for the entire MS11 system.
Starts all components including main interface, configuration UI, and bot monitor.
"""
import os
import sys
import subprocess
import threading
import time
import webbrowser
import signal
import psutil
from pathlib import Path
from typing import Dict, List, Any, Optional

class MS11SystemLauncher:
    """Launches and manages all MS11 system components."""
    
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.processes = {}
        self.running = False
        self.ports = {
            'main_interface': 5000,
            'config_ui': 5001,
            'control_center': None  # Desktop app, no port
        }
        
        # Component configurations
        self.components = {
            'main_interface': {
                'script': 'ms11_main_interface.py',
                'name': 'MS11 Main Interface',
                'description': 'Comprehensive web interface for the entire MS11 system',
                'type': 'web',
                'auto_start': True
            },
            'config_ui': {
                'script': 'config_ui.py',
                'name': 'Configuration Management UI',
                'description': 'Configuration automation interface',
                'type': 'web',
                'auto_start': True
            },
            'control_center': {
                'script': 'ms11_control_center.py',
                'name': 'MS11 Control Center',
                'description': 'Desktop control center with embedded dashboard and attachment status',
                'type': 'desktop',
                'auto_start': True
            }
        }
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        print(f"\nReceived signal {signum}, shutting down MS11 system...")
        self.stop_all_components()
        sys.exit(0)
    
    def install_requirements(self, component: str) -> bool:
        """Install requirements for a specific component.
        Falls back to known filenames when component-specific file is missing.
        """
        # Primary: requirements_<component>.txt
        candidates = [self.script_dir / f"requirements_{component}.txt"]
        # Fallback mappings
        fallback_map = {
            'main_interface': self.script_dir / 'requirements_main_interface.txt',
            'config_ui': self.script_dir / 'requirements_ui.txt',
            'bot_monitor': self.script_dir / 'requirements_monitor.txt',
            'control_center': self.script_dir / 'requirements_control_center.txt',
        }
        if component in fallback_map:
            candidates.append(fallback_map[component])

        requirements_path: Optional[Path] = None
        for path in candidates:
            if path.exists():
                requirements_path = path
                break
        
        if not requirements_path:
            print(f"Warning: No requirements file found for {component}")
            return True
        
        try:
            print(f"Installing requirements for {component}...")
            env = os.environ.copy()
            # Ensure UTF-8 to avoid Windows codepage issues printing unicode
            env.setdefault('PYTHONIOENCODING', 'utf-8')
            env.setdefault('LC_ALL', 'C.UTF-8')
            env.setdefault('LANG', 'C.UTF-8')

            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', str(requirements_path)
            ], capture_output=True, text=True, cwd=self.script_dir, env=env)
            
            if result.returncode == 0:
                print(f"Requirements installed for {component}")
                return True
            else:
                print(f"Failed to install requirements for {component}")
                print(f"Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error installing requirements for {component}: {e}")
            return False
    
    def start_component(self, component: str) -> bool:
        """Start a specific MS11 component."""
        if component not in self.components:
            print(f"Unknown component: {component}")
            return False
        
        if component in self.processes and self.processes[component].poll() is None:
            print(f"{self.components[component]['name']} is already running")
            return True
        
        comp_config = self.components[component]
        script_path = self.script_dir / comp_config['script']
        
        if not script_path.exists():
            print(f"Script not found: {script_path}")
            return False
        
        try:
            # Install requirements first
            if not self.install_requirements(component):
                return False
            
            # Start the component
            print(f"Starting {comp_config['name']}...")
            
            # Proactively kill any previous stray processes for this component (avoids stale servers serving old UI)
            try:
                self._kill_existing_component_process(script_path)
            except Exception:
                pass

            if comp_config['type'] == 'web':
                # Web components run in background
                process = subprocess.Popen([
                    sys.executable, str(script_path)
                ], cwd=self.script_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                self.processes[component] = process
                
                # Wait a bit for the component to start
                time.sleep(2)
                
                if process.poll() is None:
                    print(f"{comp_config['name']} started successfully")
                    
                    # Open browser for web components
                    if component == 'main_interface':
                        self._open_browser(f"http://localhost:{self.ports['main_interface']}")
                    elif component == 'config_ui':
                        self._open_browser(f"http://localhost:{self.ports['config_ui']}")
                    
                    return True
                else:
                    stdout, stderr = process.communicate()
                    print(f"{comp_config['name']} failed to start")
                    print(f"Error: {stderr.decode()}")
                    return False
                    
            else:
                # Desktop components run in foreground
                process = subprocess.Popen([
                    sys.executable, str(script_path)
                ], cwd=self.script_dir)
                
                self.processes[component] = process
                print(f"{comp_config['name']} started successfully")
                return True
                
        except Exception as e:
            print(f"Error starting {comp_config['name']}: {e}")
            return False

    def _kill_existing_component_process(self, script_path: Path) -> None:
        """Terminate any running python processes executing the given script path."""
        try:
            normalized = str(script_path.resolve()).lower()
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmd = proc.info.get('cmdline') or []
                    joined = ' '.join(cmd).lower()
                    if 'python' in (proc.info.get('name') or '').lower() and normalized in joined:
                        if proc.pid in [p.pid for p in self.processes.values() if p]:
                            continue
                        proc.terminate()
                        proc.wait(timeout=3)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.TimeoutExpired):
                    continue
        except Exception:
            pass
    
    def stop_component(self, component: str) -> bool:
        """Stop a specific MS11 component."""
        if component not in self.processes:
            print(f"Component {component} is not running")
            return True
        
        process = self.processes[component]
        
        try:
            if process.poll() is None:
                print(f"Stopping {self.components[component]['name']}...")
                
                # Try graceful shutdown first
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(f"Force killing {self.components[component]['name']}...")
                    process.kill()
                    process.wait()
                
                print(f"{self.components[component]['name']} stopped")
            else:
                print(f"{self.components[component]['name']} is not running")
            
            del self.processes[component]
            return True
            
        except Exception as e:
            print(f"Error stopping {self.components[component]['name']}: {e}")
            return False
    
    def start_all_components(self) -> bool:
        """Start all MS11 components."""
        print("Starting MS11 System...")
        print("=" * 50)
        
        success_count = 0
        total_components = len(self.components)
        
        for component in self.components:
            if self.components[component]['auto_start']:
                if self.start_component(component):
                    success_count += 1
                else:
                    print(f"Failed to start {component}, continuing with other components...")
        
        print("=" * 50)
        print(f"Started {success_count}/{total_components} components successfully")
        
        if success_count == total_components:
            print("MS11 System is fully operational!")
            return True
        else:
            print("Some components failed to start. Check the logs above.")
            return False
    
    def stop_all_components(self):
        """Stop all running MS11 components."""
        print("\nStopping MS11 System...")
        
        for component in list(self.processes.keys()):
            self.stop_component(component)
        
        print("All components stopped")
    
    def restart_component(self, component: str) -> bool:
        """Restart a specific component."""
        print(f"Restarting {self.components[component]['name']}...")
        
        if self.stop_component(component):
            time.sleep(1)  # Brief pause between stop and start
            return self.start_component(component)
        
        return False
    
    def restart_all_components(self) -> bool:
        """Restart all MS11 components."""
        print("Restarting all MS11 components...")
        
        self.stop_all_components()
        time.sleep(2)  # Brief pause before restarting
        
        return self.start_all_components()
    
    def show_status(self):
        """Show status of all MS11 components."""
        print("\nMS11 System Status")
        print("=" * 50)
        
        for component, config in self.components.items():
            status = "Running" if component in self.processes and self.processes[component].poll() is None else "Stopped"
            
            print(f"{config['name']:<25} {status}")
            
            if component in self.processes:
                process = self.processes[component]
                if process.poll() is None:
                    try:
                        # Get process info
                        proc = psutil.Process(process.pid)
                        memory_mb = proc.memory_info().rss / 1024 / 1024
                        print(f"{'':25} PID: {process.pid}, Memory: {memory_mb:.1f} MB")
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
        
        print("=" * 50)
    
    def _open_browser(self, url: str):
        """Open a URL in the default browser."""
        try:
            webbrowser.open(url)
            print(f"Opened {url} in browser")
        except Exception as e:
            print(f"Could not open browser: {e}")
    
    def run_interactive(self):
        """Run the launcher in interactive mode."""
        self.running = True
        
        print("MS11 System Launcher - Interactive Mode")
        print("Type 'help' for available commands")
        print("Type 'quit' or 'exit' to stop all components and exit")
        
        while self.running:
            try:
                command = input("\nms11> ").strip().lower()
                
                if command in ['quit', 'exit', 'q']:
                    break
                elif command == 'help':
                    self._show_help()
                elif command == 'start':
                    self.start_all_components()
                elif command == 'stop':
                    self.stop_all_components()
                elif command == 'restart':
                    self.restart_all_components()
                elif command == 'status':
                    self.show_status()
                elif command.startswith('start '):
                    component = command.split(' ', 1)[1]
                    self.start_component(component)
                elif command.startswith('stop '):
                    component = command.split(' ', 1)[1]
                    self.stop_component(component)
                elif command.startswith('restart '):
                    component = command.split(' ', 1)[1]
                    self.restart_component(component)
                elif command == '':
                    continue
                else:
                    print(f"Unknown command: {command}")
                    print("Type 'help' for available commands")
                    
            except KeyboardInterrupt:
                break
            except EOFError:
                break
        
        print("\nShutting down MS11 System...")
        self.stop_all_components()
    
    def _show_help(self):
        """Show available commands."""
        print("\nAvailable Commands:")
        print("  start                    - Start all components")
        print("  stop                     - Stop all components")
        print("  restart                  - Restart all components")
        print("  status                   - Show component status")
        print("  start <component>        - Start specific component")
        print("  stop <component>         - Stop specific component")
        print("  restart <component>      - Restart specific component")
        print("  help                     - Show this help")
        print("  quit/exit/q              - Exit launcher")
        print("\nAvailable Components:")
        for component, config in self.components.items():
            print(f"  {component:<15} - {config['description']}")

def main():
    """Main entry point."""
    launcher = MS11SystemLauncher()
    
    if len(sys.argv) > 1:
        # Command line mode
        command = sys.argv[1].lower()
        
        if command == 'start':
            launcher.start_all_components()
        elif command == 'stop':
            launcher.stop_all_components()
        elif command == 'restart':
            launcher.restart_all_components()
        elif command == 'status':
            launcher.show_status()
        elif command == 'interactive':
            launcher.run_interactive()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: start, stop, restart, status, interactive")
            sys.exit(1)
    else:
        # Default: start all components and run interactive
        if launcher.start_all_components():
            print("\nMS11 System started successfully!")
            print("Press Ctrl+C to stop all components and exit")
            
            try:
                # Keep running until interrupted
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
        
        launcher.stop_all_components()

if __name__ == '__main__':
    main()
