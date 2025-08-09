#!/usr/bin/env python3
"""
Advanced debugging dashboard for MS11 development.
Provides real-time monitoring, log analysis, and debugging tools.
"""

import os
import sys
import time
import json
import asyncio
import threading
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
import logging

# Add project paths
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.syntax import Syntax
    from rich.tree import Tree
    from rich.text import Text
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

try:
    from memory_optimizer import get_memory_stats, optimize_memory
    from cache_manager import get_cache
    from structured_logging import analyze_logs, get_logger
    from enhanced_error_handling import get_error_analytics
    CORE_MODULES_AVAILABLE = True
except ImportError:
    CORE_MODULES_AVAILABLE = False

logger = logging.getLogger(__name__)


class MS11DebugDashboard:
    """Interactive debugging dashboard for MS11."""
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.running = False
        self.update_interval = 2.0  # seconds
        self.stats_history: List[Dict[str, Any]] = []
        self.max_history = 100
        
    def create_system_info_panel(self) -> Panel:
        """Create system information panel."""
        if not RICH_AVAILABLE:
            return "Rich not available"
            
        info_table = Table(show_header=True, header_style="bold magenta")
        info_table.add_column("Metric", style="cyan", no_wrap=True)
        info_table.add_column("Value", style="green")
        
        # System information
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        
        info_table.add_row("Python Version", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        info_table.add_row("Process ID", str(os.getpid()))
        info_table.add_row("Memory RSS", f"{memory_info.rss / 1024 / 1024:.1f} MB")
        info_table.add_row("Memory VMS", f"{memory_info.vms / 1024 / 1024:.1f} MB")
        info_table.add_row("CPU Percent", f"{process.cpu_percent():.1f}%")
        
        # Add module availability
        info_table.add_row("Rich Available", "✓" if RICH_AVAILABLE else "✗")
        info_table.add_row("Core Modules", "✓" if CORE_MODULES_AVAILABLE else "✗")
        
        return Panel(info_table, title="[bold blue]System Information[/bold blue]")
        
    def create_memory_panel(self) -> Panel:
        """Create memory statistics panel."""
        if not RICH_AVAILABLE:
            return "Rich not available"
            
        memory_table = Table(show_header=True, header_style="bold yellow")
        memory_table.add_column("Component", style="cyan")
        memory_table.add_column("Value", style="green")
        memory_table.add_column("Status", justify="center")
        
        if CORE_MODULES_AVAILABLE:
            try:
                stats = get_memory_stats()
                
                memory_table.add_row(
                    "Process Memory",
                    f"{stats['process_memory_mb']:.1f} MB",
                    "🟢" if stats['process_memory_mb'] < 100 else "🟡" if stats['process_memory_mb'] < 200 else "🔴"
                )
                
                memory_table.add_row(
                    "GC Objects",
                    str(stats['gc_objects']),
                    "🟢" if stats['gc_objects'] < 10000 else "🟡" if stats['gc_objects'] < 50000 else "🔴"
                )
                
                if 'cache_stats' in stats:
                    cache_stats = stats['cache_stats']
                    memory_table.add_row(
                        "Cache Memory",
                        f"{cache_stats.get('memory_usage_mb', 0):.1f} MB",
                        "🟢" if cache_stats.get('memory_utilization', 0) < 80 else "🟡"
                    )
                    
            except Exception as e:
                memory_table.add_row("Error", str(e), "🔴")
        else:
            memory_table.add_row("Core modules unavailable", "N/A", "🔴")
            
        return Panel(memory_table, title="[bold yellow]Memory Statistics[/bold yellow]")
        
    def create_cache_panel(self) -> Panel:
        """Create cache statistics panel."""
        if not RICH_AVAILABLE:
            return "Rich not available"
            
        cache_table = Table(show_header=True, header_style="bold green")
        cache_table.add_column("Metric", style="cyan")
        cache_table.add_column("Value", style="green")
        cache_table.add_column("Performance", justify="center")
        
        if CORE_MODULES_AVAILABLE:
            try:
                cache = get_cache()
                stats = cache.get_stats()
                
                cache_table.add_row(
                    "Hit Rate",
                    f"{stats['hit_rate']:.1f}%",
                    "🟢" if stats['hit_rate'] > 80 else "🟡" if stats['hit_rate'] > 60 else "🔴"
                )
                
                cache_table.add_row("Total Requests", str(stats['total_requests']), "📊")
                cache_table.add_row("Cache Hits", str(stats['hits']), "✅")
                cache_table.add_row("Cache Misses", str(stats['misses']), "❌")
                cache_table.add_row("Active Backends", str(stats['backends_count']), "🔧")
                
            except Exception as e:
                cache_table.add_row("Error", str(e), "🔴")
        else:
            cache_table.add_row("Core modules unavailable", "N/A", "🔴")
            
        return Panel(cache_table, title="[bold green]Cache Performance[/bold green]")
        
    def create_error_panel(self) -> Panel:
        """Create error analytics panel."""
        if not RICH_AVAILABLE:
            return "Rich not available"
            
        error_table = Table(show_header=True, header_style="bold red")
        error_table.add_column("Error Type", style="cyan")
        error_table.add_column("Count", style="red")
        error_table.add_column("Recovery Rate", style="yellow")
        
        if CORE_MODULES_AVAILABLE:
            try:
                analytics = get_error_analytics()
                error_stats = analytics.get('error_stats', {})
                
                if error_stats.get('error_types'):
                    for error_type, count in error_stats['error_types'].items():
                        recovery_rate = error_stats.get('recovery_rate', 0)
                        error_table.add_row(
                            error_type,
                            str(count),
                            f"{recovery_rate:.1f}%"
                        )
                else:
                    error_table.add_row("No errors", "0", "N/A")
                    
            except Exception as e:
                error_table.add_row("Error loading analytics", str(e), "N/A")
        else:
            error_table.add_row("Core modules unavailable", "N/A", "N/A")
            
        return Panel(error_table, title="[bold red]Error Analytics[/bold red]")
        
    def create_log_panel(self) -> Panel:
        """Create recent logs panel."""
        if not RICH_AVAILABLE:
            return "Rich not available"
            
        log_text = Text()
        
        if CORE_MODULES_AVAILABLE:
            try:
                log_analysis = analyze_logs(minutes=10)  # Last 10 minutes
                
                log_text.append(f"Recent Activity (10 min):\n", style="bold white")
                log_text.append(f"Errors: {log_analysis.get('error_count', 0)}\n", style="red")
                log_text.append(f"Warnings: {log_analysis.get('warning_count', 0)}\n", style="yellow")
                log_text.append(f"Slow Operations: {log_analysis.get('total_slow_operations', 0)}\n", style="orange1")
                
                alerts = log_analysis.get('alerts', [])
                if alerts:
                    log_text.append("\nRecent Alerts:\n", style="bold red")
                    for alert in alerts[-3:]:  # Show last 3 alerts
                        log_text.append(f"• {alert['message']}\n", style="red")
                        
            except Exception as e:
                log_text.append(f"Error loading logs: {e}", style="red")
        else:
            log_text.append("Core modules unavailable", style="red")
            
        return Panel(log_text, title="[bold magenta]Log Analysis[/bold magenta]")
        
    def create_session_panel(self) -> Panel:
        """Create active sessions panel."""
        if not RICH_AVAILABLE:
            return "Rich not available"
            
        session_table = Table(show_header=True, header_style="bold blue")
        session_table.add_column("Session ID", style="cyan")
        session_table.add_column("Character", style="green")
        session_table.add_column("Mode", style="yellow")
        session_table.add_column("Status", justify="center")
        
        # This would normally connect to actual session data
        # For now, show placeholder data
        session_table.add_row("session_001", "TestChar", "medic", "🟢")
        session_table.add_row("session_002", "DebugChar", "combat", "🟡")
        
        return Panel(session_table, title="[bold blue]Active Sessions[/bold blue]")
        
    def create_layout(self) -> Layout:
        """Create the main dashboard layout."""
        if not RICH_AVAILABLE:
            return "Rich not available"
            
        layout = Layout()
        
        # Split into main areas
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        
        # Header
        layout["header"].update(
            Panel(
                f"[bold blue]MS11 Debug Dashboard[/bold blue] - {datetime.now().strftime('%H:%M:%S')}",
                style="white on blue"
            )
        )
        
        # Main area split
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        # Left column
        layout["left"].split(
            Layout(name="system"),
            Layout(name="memory"),
            Layout(name="cache")
        )
        
        # Right column  
        layout["right"].split(
            Layout(name="errors"),
            Layout(name="logs"),
            Layout(name="sessions")
        )
        
        # Footer
        layout["footer"].update(
            Panel(
                "[bold]Controls:[/bold] [cyan]Ctrl+C[/cyan] to exit, [cyan]Space[/cyan] to refresh, [cyan]m[/cyan] to optimize memory",
                style="white on dark_blue"
            )
        )
        
        return layout
        
    def update_layout(self, layout: Layout):
        """Update all dashboard panels."""
        if not RICH_AVAILABLE:
            return
            
        layout["system"].update(self.create_system_info_panel())
        layout["memory"].update(self.create_memory_panel())
        layout["cache"].update(self.create_cache_panel())
        layout["errors"].update(self.create_error_panel())
        layout["logs"].update(self.create_log_panel())
        layout["sessions"].update(self.create_session_panel())
        
    def run_interactive(self):
        """Run interactive dashboard."""
        if not RICH_AVAILABLE:
            print("Rich library not available. Install with: pip install rich")
            return
            
        self.running = True
        layout = self.create_layout()
        
        try:
            with Live(layout, refresh_per_second=1, screen=True):
                while self.running:
                    self.update_layout(layout)
                    time.sleep(self.update_interval)
                    
        except KeyboardInterrupt:
            self.running = False
            self.console.print("\n[bold red]Dashboard stopped by user[/bold red]")
            
    def show_session_state(self, session_id: str):
        """Show detailed session state."""
        if not RICH_AVAILABLE:
            print(f"Session {session_id} state (Rich not available)")
            return
            
        table = Table(title=f"Session {session_id} State")
        table.add_column("Component", style="cyan", no_wrap=True)
        table.add_column("Status", style="green")
        table.add_column("Memory (MB)", justify="right")
        table.add_column("Details", style="dim")
        
        # Mock session data - would be real in production
        table.add_row("Session Manager", "Active", "2.1", "Managing character state")
        table.add_row("Window Manager", "Connected", "1.5", "SWG client detected")
        table.add_row("Mode Handler", "Running", "0.8", "Medic mode active")
        table.add_row("Movement Agent", "Idle", "0.3", "Waiting for commands")
        
        self.console.print(table)
        
    def show_memory_report(self):
        """Show detailed memory report."""
        if not RICH_AVAILABLE:
            print("Memory report (Rich not available)")
            return
            
        if CORE_MODULES_AVAILABLE:
            stats = get_memory_stats()
            
            tree = Tree("[bold blue]Memory Analysis")
            
            # Process memory
            process_branch = tree.add("[green]Process Memory")
            process_branch.add(f"RSS: {stats['process_memory_mb']:.1f} MB")
            process_branch.add(f"VMS: {stats['virtual_memory_mb']:.1f} MB")
            process_branch.add(f"Objects: {stats['gc_objects']:,}")
            
            # Cache memory
            if 'cache_stats' in stats:
                cache_stats = stats['cache_stats']
                cache_branch = tree.add("[yellow]Cache Memory")
                cache_branch.add(f"Usage: {cache_stats.get('memory_usage_mb', 0):.1f} MB")
                cache_branch.add(f"Utilization: {cache_stats.get('memory_utilization', 0):.1f}%")
                
            # Optimization suggestions
            suggestions = tree.add("[red]Optimization Suggestions")
            if stats['process_memory_mb'] > 100:
                suggestions.add("Consider memory optimization")
            if stats['gc_objects'] > 10000:
                suggestions.add("High object count - consider cleanup")
                
            self.console.print(tree)
        else:
            self.console.print("[red]Core modules not available for memory analysis")
            
    def live_log_viewer(self, log_file: str = "logs/ms11.log"):
        """Live log file viewer."""
        if not RICH_AVAILABLE:
            print("Live log viewer (Rich not available)")
            return
            
        if not Path(log_file).exists():
            self.console.print(f"[red]Log file not found: {log_file}")
            return
            
        self.console.print(f"[green]Watching log file: {log_file}")
        self.console.print("[dim]Press Ctrl+C to stop")
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                # Go to end of file
                f.seek(0, 2)
                
                while True:
                    line = f.readline()
                    if line:
                        try:
                            # Try to parse as JSON log
                            log_entry = json.loads(line.strip())
                            level = log_entry.get('level', 'INFO')
                            message = log_entry.get('message', '')
                            timestamp = log_entry.get('timestamp', '')
                            
                            level_colors = {
                                'DEBUG': 'dim white',
                                'INFO': 'green',
                                'WARNING': 'yellow',
                                'ERROR': 'red',
                                'CRITICAL': 'bold red'
                            }
                            
                            color = level_colors.get(level, 'white')
                            self.console.print(f"[{color}]{timestamp} [{level}] {message}")
                            
                        except json.JSONDecodeError:
                            # Fallback for non-JSON logs
                            self.console.print(line.strip())
                    else:
                        time.sleep(0.1)
                        
        except KeyboardInterrupt:
            self.console.print("\n[bold red]Log viewer stopped")


def main():
    """Main debug dashboard entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MS11 Debug Dashboard")
    parser.add_argument("--session", "-s", help="Show specific session state")
    parser.add_argument("--memory", "-m", action="store_true", help="Show memory report")
    parser.add_argument("--logs", "-l", help="Live log viewer (specify file)")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive dashboard")
    parser.add_argument("--optimize", "-o", action="store_true", help="Run memory optimization")
    
    args = parser.parse_args()
    
    dashboard = MS11DebugDashboard()
    
    if args.session:
        dashboard.show_session_state(args.session)
    elif args.memory:
        dashboard.show_memory_report()
    elif args.logs:
        dashboard.live_log_viewer(args.logs)
    elif args.optimize and CORE_MODULES_AVAILABLE:
        print("Running memory optimization...")
        result = optimize_memory()
        print(f"Optimization complete: {result}")
    elif args.interactive:
        dashboard.run_interactive()
    else:
        # Default: show quick status
        if RICH_AVAILABLE:
            console = Console()
            console.print("[bold blue]MS11 Debug Dashboard[/bold blue]")
            console.print("Use --interactive for full dashboard or --help for options")
            
            # Quick status
            table = Table(title="Quick Status")
            table.add_column("Component", style="cyan")
            table.add_column("Status", justify="center")
            
            table.add_row("Rich Library", "✓" if RICH_AVAILABLE else "✗")
            table.add_row("Core Modules", "✓" if CORE_MODULES_AVAILABLE else "✗")
            table.add_row("Python Version", f"{sys.version_info.major}.{sys.version_info.minor}")
            
            console.print(table)
        else:
            print("MS11 Debug Dashboard - Rich library not available")
            print("Install with: pip install rich")


if __name__ == "__main__":
    main()