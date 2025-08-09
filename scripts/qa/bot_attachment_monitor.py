#!/usr/bin/env python3
"""
Bot Attachment Monitor for MS11
Detects when the bot is successfully attached to the game session and provides visual indicators.
"""

import os
import sys
import time
import json
import logging
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import psutil
import win32gui
import win32process
import win32con
import win32api

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BotAttachmentMonitor:
    """Monitors bot attachment status and provides visual indicators."""
    
    def __init__(self):
        self.attached = False
        self.session_detected = False
        self.game_processes = []
        self.bot_processes = []
        self.attachment_status = {
            "status": "disconnected",
            "message": "Bot not attached to game session",
            "timestamp": datetime.now().isoformat(),
            "game_info": {},
            "bot_info": {},
            "session_detected": False,
            "window_title": None,
            "window_hwnd": None
        }
        
        # Game process signatures (restrictive to avoid false positives)
        self.game_signatures = [
            "swg", "star wars", "starwars", "galaxies"
        ]
        
        # Bot process signatures
        self.bot_signatures = [
            "python", "ms11", "morningstar", "bot", "automation",
            "configuration_automation", "main.py"
        ]
        
        # Initialize monitoring
        self.running = False
        self.monitor_thread = None
        
    def start_monitoring(self):
        """Start the attachment monitoring in a background thread."""
        if self.running:
            logger.info("Monitoring already running")
            return
            
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Bot attachment monitoring started")
        
    def stop_monitoring(self):
        """Stop the attachment monitoring."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        logger.info("Bot attachment monitoring stopped")
        
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self.running:
            try:
                self._check_attachment_status()
                time.sleep(2.0)  # Check every 2 seconds
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5.0)  # Wait longer on error
                
    def _check_attachment_status(self):
        """Check if bot is attached to game session."""
        try:
            # Get all running processes
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'exe']):
                try:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cmdline': proc.info['cmdline'],
                        'exe': proc.info['exe']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Find game processes (exclude our own python/ms11 processes)
            game_procs = self._find_game_processes(processes)
            
            # Find bot processes
            bot_procs = self._find_bot_processes(processes)
            
            # Detect an actual game window session (visible, non-minimized, reasonable size)
            hwnd, title = self._detect_game_window(game_procs)
            self.session_detected = hwnd is not None

            # Check for readiness: we only report attached when a valid game window is present
            # AND a bot process is running. This avoids green when the game is closed.
            attached = self._check_attachment(game_procs, bot_procs) and self.session_detected
            
            # Update status
            self._update_attachment_status(attached, game_procs, bot_procs, hwnd, title)
            
        except Exception as e:
            logger.error(f"Error checking attachment status: {e}")
            
    def _find_game_processes(self, processes: List[Dict]) -> List[Dict]:
        """Find game-related processes."""
        game_procs = []
        
        for proc in processes:
            if not proc['name']:
                continue
                
            proc_name = proc['name'].lower()
            proc_cmdline = ' '.join(proc['cmdline'] or []).lower()
            # Exclude python and our own processes
            if 'python' in proc_name or 'python' in proc_cmdline:
                continue
            if 'ms11' in proc_name or 'morningstar' in proc_name or 'project-morningstar' in proc_cmdline:
                continue
            
            # Check if this looks like a game process
            for signature in self.game_signatures:
                if signature in proc_name or signature in proc_cmdline:
                    game_procs.append(proc)
                    break
                    
        return game_procs
        
    def _find_bot_processes(self, processes: List[Dict]) -> List[Dict]:
        """Find bot-related processes."""
        bot_procs = []
        
        for proc in processes:
            if not proc['name']:
                continue
                
            proc_name = proc['name'].lower()
            proc_cmdline = ' '.join(proc['cmdline'] or []).lower()
            
            # Check if this looks like a bot process
            for signature in self.bot_signatures:
                if signature in proc_name or signature in proc_cmdline:
                    bot_procs.append(proc)
                    break
                    
        return bot_procs
        
    def _check_attachment(self, game_procs: List[Dict], bot_procs: List[Dict]) -> bool:
        """Check if bot is attached to game session."""
        if not game_procs or not bot_procs:
            return False
            
        # Check if bot and game processes are running simultaneously
        # and if they share any common characteristics (like working directory, etc.)
        
        # Basic readiness requires distinct PIDs for game and bot
        game_pids = {p.get('pid') for p in game_procs if p.get('pid')}
        bot_pids = {p.get('pid') for p in bot_procs if p.get('pid')}
        if not game_pids.isdisjoint(bot_pids):
            return False
        return True
        
    def _update_attachment_status(self, attached: bool, game_procs: List[Dict], bot_procs: List[Dict], hwnd: Optional[int], title: Optional[str]):
        """Update the attachment status."""
        self.attached = attached
        
        if attached:
            status = "attached"
            message = "Bot successfully attached to game session - Ready to use!"
        else:
            status = "disconnected"
            message = "Bot not attached to game session"
            
        self.attachment_status.update({
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            "game_info": {
                "processes": len(game_procs),
                "details": game_procs[:3]  # Limit to first 3 for display
            },
            "bot_info": {
                "processes": len(bot_procs),
                "details": bot_procs[:3]  # Limit to first 3 for display
            },
            "session_detected": self.session_detected,
            "window_title": title,
            "window_hwnd": hwnd
        })
        
        logger.info(f"Attachment status: {status} - {message}")

    def _detect_game_window(self, game_procs: List[Dict]) -> Tuple[Optional[int], Optional[str]]:
        """Try to locate a visible game window and return (hwnd, title)."""
        if not game_procs:
            return None, None

        target_pids = {p['pid'] for p in game_procs if p.get('pid')}
        found_hwnd: Optional[int] = None
        found_title: Optional[str] = None

        def enum_handler(hwnd, _):
            nonlocal found_hwnd, found_title
            if not win32gui.IsWindowVisible(hwnd):
                return
            # Skip minimized
            try:
                if win32gui.IsIconic(hwnd):
                    return
            except Exception:
                pass
            length = win32gui.GetWindowTextLength(hwnd)
            if length == 0:
                return
            title = win32gui.GetWindowText(hwnd)
            if not title:
                return
            # Check process ownership
            try:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                if pid in target_pids:
                    # Additional title heuristic
                    lower = title.lower()
                    # Require known title hints and a reasonable window size
                    rect = win32gui.GetWindowRect(hwnd)
                    width = max(0, rect[2] - rect[0])
                    height = max(0, rect[3] - rect[1])
                    size_ok = width >= 640 and height >= 480
                    if any(sig in lower for sig in self.game_signatures) and size_ok:
                        found_hwnd = hwnd
                        found_title = title
            except Exception:
                return

        try:
            win32gui.EnumWindows(enum_handler, None)
        except Exception:
            return None, None

        return found_hwnd, found_title
        
    def get_status(self) -> Dict[str, Any]:
        """Get current attachment status."""
        return self.attachment_status.copy()
        
    def is_attached(self) -> bool:
        """Check if bot is currently attached."""
        return self.attached


class BotStatusUI:
    """Tkinter-based UI for displaying bot attachment status."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MS11 Bot Attachment Monitor")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Initialize monitor
        self.monitor = BotAttachmentMonitor()
        
        # Setup UI
        self._setup_ui()
        
        # Start monitoring
        self.monitor.start_monitoring()
        
        # Start UI update timer
        self._update_ui()
        
    def _setup_ui(self):
        """Setup the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="MS11 Bot Attachment Monitor", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status indicator
        self.status_frame = ttk.LabelFrame(main_frame, text="Attachment Status", padding="10")
        self.status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Status label
        self.status_label = ttk.Label(self.status_frame, text="Initializing...", 
                                     font=('Arial', 12))
        self.status_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Status indicator circle
        self.status_canvas = tk.Canvas(self.status_frame, width=20, height=20, 
                                      bg='white', highlightthickness=0)
        self.status_canvas.grid(row=1, column=0, pady=(0, 10))
        
        # Timestamp
        self.timestamp_label = ttk.Label(self.status_frame, text="", font=('Arial', 9))
        self.timestamp_label.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 10))

        # Game session detection indicator
        self.session_label = ttk.Label(self.status_frame, text="Game Session: Unknown", font=('Arial', 10))
        self.session_label.grid(row=2, column=1, sticky=tk.W, padx=(10, 0), pady=(0, 5))
        self.session_canvas = tk.Canvas(self.status_frame, width=14, height=14, bg='white', highlightthickness=0)
        self.session_canvas.grid(row=2, column=0, pady=(0, 5))
        
        # Game info
        game_frame = ttk.LabelFrame(main_frame, text="Game Session Info", padding="10")
        game_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.game_info_text = tk.Text(game_frame, height=8, width=30, wrap=tk.WORD)
        self.game_info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Bot info
        bot_frame = ttk.LabelFrame(main_frame, text="Bot Process Info", padding="10")
        bot_frame.grid(row=2, column=1, sticky=(tk.W, tk.E))
        
        self.bot_info_text = tk.Text(bot_frame, height=8, width=30, wrap=tk.WORD)
        self.bot_info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure frame weights
        game_frame.columnconfigure(0, weight=1)
        game_frame.rowconfigure(0, weight=1)
        bot_frame.columnconfigure(0, weight=1)
        bot_frame.rowconfigure(0, weight=1)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(20, 0))
        
        refresh_btn = ttk.Button(button_frame, text="Refresh Status", 
                                command=self._refresh_status)
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        start_btn = ttk.Button(button_frame, text="Start Monitoring", 
                              command=self._start_monitoring)
        start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        stop_btn = ttk.Button(button_frame, text="Stop Monitoring", 
                             command=self._stop_monitoring)
        stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Menu bar
        self._setup_menu()
        
    def _setup_menu(self):
        """Setup the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Status", command=self._export_status)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self._quit)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        
    def _update_ui(self):
        """Update the UI with current status."""
        try:
            status = self.monitor.get_status()
            
            # Update status label
            self.status_label.config(text=status['message'])
            
            # Update status indicator
            self._update_status_indicator(status['status'])
            
            # Update timestamp
            timestamp = datetime.fromisoformat(status['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            self.timestamp_label.config(text=f"Last updated: {timestamp}")
            
            # Update game info
            self._update_text_widget(self.game_info_text, status['game_info'])
            
            # Update bot info
            self._update_text_widget(self.bot_info_text, status['bot_info'])

            # Update session detection indicator
            if status.get('session_detected'):
                self.session_label.config(text=f"Game Session: Detected ({status.get('window_title') or 'Window'})")
                self._set_canvas_color(self.session_canvas, 'green')
            else:
                self.session_label.config(text="Game Session: Not Detected")
                self._set_canvas_color(self.session_canvas, 'red')
            
        except Exception as e:
            logger.error(f"Error updating UI: {e}")
            
        # Schedule next update
        self.root.after(2000, self._update_ui)
        
    def _update_status_indicator(self, status: str):
        """Update the status indicator circle."""
        self.status_canvas.delete("all")
        
        if status == "attached":
            color = "green"
            text = "✓"
        elif status == "deploying":
            color = "orange"
            text = "⟳"
        else:
            color = "red"
            text = "✗"
            
        # Draw circle
        self.status_canvas.create_oval(2, 2, 18, 18, fill=color, outline="black", width=2)
        
        # Draw text
        self.status_canvas.create_text(10, 10, text=text, fill="white", font=('Arial', 10, 'bold'))

    def _set_canvas_color(self, canvas: tk.Canvas, color: str):
        canvas.delete("all")
        canvas.create_oval(1, 1, 13, 13, fill=color, outline="black", width=1)
        
    def _update_text_widget(self, text_widget: tk.Text, info: Dict):
        """Update a text widget with information."""
        text_widget.delete(1.0, tk.END)
        
        if not info:
            text_widget.insert(tk.END, "No information available")
            return
            
        for key, value in info.items():
            if key == "details" and isinstance(value, list):
                text_widget.insert(tk.END, f"{key}:\n")
                for i, proc in enumerate(value, 1):
                    text_widget.insert(tk.END, f"  {i}. PID: {proc.get('pid', 'N/A')}\n")
                    text_widget.insert(tk.END, f"     Name: {proc.get('name', 'N/A')}\n")
                    if proc.get('cmdline'):
                        cmdline = ' '.join(proc['cmdline'][:3])  # First 3 args
                        text_widget.insert(tk.END, f"     Cmd: {cmdline}...\n")
                    text_widget.insert(tk.END, "\n")
            else:
                text_widget.insert(tk.END, f"{key}: {value}\n")
                
    def _refresh_status(self):
        """Manually refresh the status."""
        self.monitor._check_attachment_status()
        
    def _start_monitoring(self):
        """Start monitoring."""
        self.monitor.start_monitoring()
        
    def _stop_monitoring(self):
        """Stop monitoring."""
        self.monitor.stop_monitoring()
        
    def _export_status(self):
        """Export current status to file."""
        try:
            status = self.monitor.get_status()
            filename = f"bot_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            with open(filename, 'w') as f:
                json.dump(status, f, indent=2)
                
            messagebox.showinfo("Export", f"Status exported to {filename}")
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export status: {e}")
            
    def _show_about(self):
        """Show about dialog."""
        about_text = """MS11 Bot Attachment Monitor
        
Version: 1.0.0
Description: Monitors MS11 bot attachment to game sessions
        
This tool helps players know when the MS11 bot is ready to use."""
        
        messagebox.showinfo("About", about_text)
        
    def _quit(self):
        """Quit the application."""
        self.monitor.stop_monitoring()
        self.root.quit()
        
    def run(self):
        """Run the UI main loop."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("UI interrupted by user")
        finally:
            self.monitor.stop_monitoring()


def main():
    """Main entry point."""
    try:
        print("🚀 Starting MS11 Bot Attachment Monitor...")
        print("📱 Opening status window...")
        
        # Create and run the UI
        ui = BotStatusUI()
        ui.run()
        
    except Exception as e:
        logger.error(f"Failed to start bot attachment monitor: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
