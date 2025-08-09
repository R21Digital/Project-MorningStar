#!/usr/bin/env python3
"""
MS11 Visual Interface (GUI)
Provides a clickable interface for MS11 instead of command line.
"""

import os
import sys
import json
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MS11GUI:
    """Visual interface for MS11."""
    
    def __init__(self):
        """Initialize the GUI."""
        self.root = tk.Tk()
        self.root.title("MS11 Control Center")
        self.root.geometry("800x600")
        self.root.configure(bg='#2b2b2b')
        
        # Variables
        self.selected_profile = tk.StringVar()
        self.selected_mode = tk.StringVar()
        self.session_active = tk.BooleanVar()
        self.auto_detect = tk.BooleanVar()
        
        # Available profiles and modes
        self.profiles = self.load_profiles()
        self.modes = [
            "quest", "combat", "medic", "crafting", "bounty", 
            "entertainer", "rls", "special-goals", "whisper", 
            "support", "follow", "dancer", "profession"
        ]
        
        self.setup_ui()
        
    def load_profiles(self) -> list:
        """Load available profiles."""
        profiles_dir = Path("profiles/runtime")
        if profiles_dir.exists():
            return [f.stem for f in profiles_dir.glob("*.json")]
        return ["default"]
    
    def setup_ui(self):
        """Setup the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="🚀 MS11 Control Center", 
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="System Status", padding="10")
        status_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status indicators
        self.status_label = ttk.Label(status_frame, text="🟢 System Ready")
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        self.session_label = ttk.Label(status_frame, text="🔴 No Active Session")
        self.session_label.grid(row=1, column=0, sticky=tk.W)
        
        # Profile selection
        profile_frame = ttk.LabelFrame(main_frame, text="Profile Management", padding="10")
        profile_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(profile_frame, text="Select Profile:").grid(row=0, column=0, sticky=tk.W)
        
        profile_combo = ttk.Combobox(
            profile_frame, 
            textvariable=self.selected_profile,
            values=self.profiles,
            state="readonly"
        )
        profile_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        profile_combo.set(self.profiles[0] if self.profiles else "default")
        
        # Mode selection
        mode_frame = ttk.LabelFrame(main_frame, text="Mode Control", padding="10")
        mode_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(mode_frame, text="Select Mode:").grid(row=0, column=0, sticky=tk.W)
        
        mode_combo = ttk.Combobox(
            mode_frame,
            textvariable=self.selected_mode,
            values=self.modes,
            state="readonly"
        )
        mode_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        mode_combo.set("quest")
        
        # Auto-detect checkbox
        auto_frame = ttk.Frame(mode_frame)
        auto_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        auto_check = ttk.Checkbutton(
            auto_frame,
            text="Auto-detect game state",
            variable=self.auto_detect
        )
        auto_check.grid(row=0, column=0, sticky=tk.W)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(20, 10))
        
        # Start button
        self.start_button = ttk.Button(
            button_frame,
            text="🚀 Start Session",
            command=self.start_session,
            style="Accent.TButton"
        )
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        # Stop button
        self.stop_button = ttk.Button(
            button_frame,
            text="⏹️ Stop Session",
            command=self.stop_session,
            state="disabled"
        )
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        # Auto-detect button
        auto_button = ttk.Button(
            button_frame,
            text="🔍 Auto Detect",
            command=self.auto_detect_session
        )
        auto_button.grid(row=0, column=2, padx=(0, 10))
        
        # Quick test button
        test_button = ttk.Button(
            button_frame,
            text="🧪 Quick Test",
            command=self.quick_test
        )
        test_button.grid(row=0, column=3)
        
        # Log output
        log_frame = ttk.LabelFrame(main_frame, text="Session Log", padding="10")
        log_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=10,
            width=80,
            bg='#1e1e1e',
            fg='#ffffff',
            font=("Consolas", 9)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure main frame grid weights
        main_frame.rowconfigure(5, weight=1)
        
        # Menu bar
        self.setup_menu()
        
        # Process tracking
        self.current_process = None
        
    def setup_menu(self):
        """Setup menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="System Check", command=self.system_check)
        tools_menu.add_command(label="Web Dashboard", command=self.open_web_dashboard)
        tools_menu.add_command(label="Profile Editor", command=self.open_profile_editor)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
    
    def log_message(self, message: str):
        """Add message to log."""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def start_session(self):
        """Start MS11 session."""
        profile = self.selected_profile.get()
        mode = self.selected_mode.get()
        
        if not profile or not mode:
            messagebox.showerror("Error", "Please select both profile and mode")
            return
        
        self.log_message(f"🚀 Starting session: {mode} mode with {profile} profile")
        
        # Disable start button, enable stop button
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.session_active.set(True)
        
        # Update status
        self.session_label.config(text="🟢 Session Active")
        
        # Start MS11 in background thread
        thread = threading.Thread(
            target=self.run_ms11_session,
            args=(profile, mode),
            daemon=True
        )
        thread.start()
    
    def run_ms11_session(self, profile: str, mode: str):
        """Run MS11 session in background thread."""
        try:
            # Set environment
            env = os.environ.copy()
            env['PYTHONPATH'] = f".;{env.get('PYTHONPATH', '')}"
            
            # Build command
            cmd = [
                sys.executable, "src/main.py",
                "--mode", mode,
                "--profile", profile
            ]
            
            self.log_message(f"Running: {' '.join(cmd)}")
            
            # Start process
            self.current_process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Monitor output
            while self.current_process.poll() is None:
                output = self.current_process.stdout.readline()
                if output:
                    self.log_message(output.strip())
                
                if not self.session_active.get():
                    self.current_process.terminate()
                    break
            
            # Get final output
            stdout, stderr = self.current_process.communicate()
            if stdout:
                self.log_message(stdout)
            if stderr:
                self.log_message(f"ERROR: {stderr}")
            
            self.log_message("Session ended")
            
        except Exception as e:
            self.log_message(f"Error: {e}")
        finally:
            # Re-enable start button
            self.root.after(0, self.session_ended)
    
    def session_ended(self):
        """Called when session ends."""
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.session_active.set(False)
        self.session_label.config(text="🔴 No Active Session")
        self.current_process = None
    
    def stop_session(self):
        """Stop current session."""
        if self.current_process:
            self.current_process.terminate()
            self.log_message("⏹️ Session stopped by user")
            self.session_active.set(False)
    
    def auto_detect_session(self):
        """Run auto-detection."""
        self.log_message("🔍 Running auto-detection...")
        
        try:
            # Run auto-detection script
            env = os.environ.copy()
            env['PYTHONPATH'] = f".;{env.get('PYTHONPATH', '')}"
            
            result = subprocess.run(
                [sys.executable, "scripts/auto_session_detector.py"],
                env=env,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log_message("✅ Auto-detection successful")
                # Update profile and mode based on detection
                # This would parse the output and update the UI
            else:
                self.log_message(f"❌ Auto-detection failed: {result.stderr}")
                
        except Exception as e:
            self.log_message(f"❌ Auto-detection error: {e}")
    
    def quick_test(self):
        """Run quick system test."""
        self.log_message("🧪 Running quick test...")
        
        try:
            result = subprocess.run(
                [sys.executable, "scripts/quick_test_ms11.py"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.log_message("✅ Quick test passed")
            else:
                self.log_message(f"❌ Quick test failed: {result.stderr}")
                
        except Exception as e:
            self.log_message(f"❌ Quick test error: {e}")
    
    def system_check(self):
        """Run system check."""
        self.log_message("🔧 Running system check...")
        # Implementation for system check
    
    def open_web_dashboard(self):
        """Open web dashboard."""
        self.log_message("🌐 Opening web dashboard...")
        
        try:
            env = os.environ.copy()
            env['PYTHONPATH'] = f".;{env.get('PYTHONPATH', '')}"
            
            subprocess.Popen(
                [sys.executable, "dashboard/app.py"],
                env=env
            )
            
            self.log_message("✅ Web dashboard started at http://localhost:5000/ms11")
            
        except Exception as e:
            self.log_message(f"❌ Error starting web dashboard: {e}")
    
    def open_profile_editor(self):
        """Open profile editor."""
        self.log_message("📝 Opening profile editor...")
        # Implementation for profile editor
    
    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About MS11",
            "MS11 Control Center\n\n"
            "A visual interface for MS11 automation.\n"
            "Version: 1.0.0\n"
            "Author: MS11 Team"
        )
    
    def show_documentation(self):
        """Show documentation."""
        self.log_message("📚 Opening documentation...")
        # Implementation for documentation
    
    def run(self):
        """Run the GUI."""
        self.log_message("🚀 MS11 Control Center started")
        self.log_message("Select a profile and mode, then click Start Session")
        
        self.root.mainloop()


def main():
    """Main entry point."""
    app = MS11GUI()
    app.run()


if __name__ == "__main__":
    main()
