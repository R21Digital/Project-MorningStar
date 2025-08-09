#!/usr/bin/env python3
"""
MS11 Auto-Configuration System
Automatically detects and configures MS11 settings without manual file editing.
"""

import json
import os
import sys
import subprocess
import psutil
import re
import time
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading

class MS11AutoConfig:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MS11 Auto-Configuration 🤖")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        # Configuration data
        self.config = {}
        self.character_profile = {}
        self.detected_settings = {}
        
        # Setup UI
        self.setup_ui()
        self.auto_detect_settings()
        
    def setup_ui(self):
        """Setup the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖 MS11 Auto-Configuration", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Auto-detection section
        detection_frame = ttk.LabelFrame(main_frame, text="🔍 Auto-Detection Results", padding="15")
        detection_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        detection_frame.columnconfigure(1, weight=1)
        
        # Character name detection
        ttk.Label(detection_frame, text="Character Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.char_name_var = tk.StringVar()
        char_name_entry = ttk.Entry(detection_frame, textvariable=self.char_name_var, width=30)
        char_name_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # SWG installation path
        ttk.Label(detection_frame, text="SWG Path:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.swg_path_var = tk.StringVar()
        swg_path_entry = ttk.Entry(detection_frame, textvariable=self.swg_path_var, width=50)
        swg_path_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        ttk.Button(detection_frame, text="Browse", command=self.browse_swg_path).grid(row=1, column=2, padx=(10, 0))
        
        # Default mode
        ttk.Label(detection_frame, text="Default Mode:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.default_mode_var = tk.StringVar(value="medic")
        mode_combo = ttk.Combobox(detection_frame, textvariable=self.default_mode_var, 
                                 values=["medic", "quest", "combat", "crafting", "farming"])
        mode_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=5)
        
        # Safety settings
        ttk.Label(detection_frame, text="Health Threshold (%):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.health_threshold_var = tk.StringVar(value="25")
        health_entry = ttk.Entry(detection_frame, textvariable=self.health_threshold_var, width=10)
        health_entry.grid(row=3, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        ttk.Label(detection_frame, text="Fatigue Threshold (%):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.fatigue_threshold_var = tk.StringVar(value="80")
        fatigue_entry = ttk.Entry(detection_frame, textvariable=self.fatigue_threshold_var, width=10)
        fatigue_entry.grid(row=4, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Discord integration
        self.discord_enabled_var = tk.BooleanVar(value=False)
        discord_check = ttk.Checkbutton(detection_frame, text="Enable Discord Integration", 
                                      variable=self.discord_enabled_var)
        discord_check.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Auto-configuration section
        config_frame = ttk.LabelFrame(main_frame, text="⚙️ Configuration Options", padding="15")
        config_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        config_frame.columnconfigure(1, weight=1)
        
        # Profile name
        ttk.Label(config_frame, text="Profile Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.profile_name_var = tk.StringVar(value="default")
        profile_entry = ttk.Entry(config_frame, textvariable=self.profile_name_var, width=20)
        profile_entry.grid(row=0, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Session limits
        ttk.Label(config_frame, text="Max Session Hours:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.session_hours_var = tk.StringVar(value="4")
        session_entry = ttk.Entry(config_frame, textvariable=self.session_hours_var, width=10)
        session_entry.grid(row=1, column=1, sticky=tk.W, padx=(10, 0), pady=5)
        
        # Auto-launch options
        self.auto_launch_var = tk.BooleanVar(value=False)
        auto_launch_check = ttk.Checkbutton(config_frame, text="Auto-launch MS11 after configuration", 
                                          variable=self.auto_launch_var)
        auto_launch_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="🔍 Re-detect Settings", 
                  command=self.auto_detect_settings).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="💾 Save Configuration", 
                  command=self.save_configuration).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="🚀 Launch MS11", 
                  command=self.launch_ms11).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="📊 Open Dashboard", 
                  command=self.open_dashboard).pack(side=tk.LEFT, padx=(0, 10))
        
        # Status display
        self.status_var = tk.StringVar(value="Ready to auto-configure MS11")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, 
                                font=("Arial", 10), foreground="blue")
        status_label.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def auto_detect_settings(self):
        """Automatically detect MS11 and SWG settings."""
        self.status_var.set("🔍 Auto-detecting settings...")
        self.progress_var.set(0)
        
        # Run detection in background thread
        thread = threading.Thread(target=self._detect_settings_thread)
        thread.daemon = True
        thread.start()
        
    def _detect_settings_thread(self):
        """Background thread for detecting settings."""
        try:
            # Detect character name from existing configs
            self.progress_var.set(20)
            char_name = self.detect_character_name()
            if char_name:
                self.char_name_var.set(char_name)
            
            # Detect SWG installation
            self.progress_var.set(40)
            swg_path = self.detect_swg_installation()
            if swg_path:
                self.swg_path_var.set(swg_path)
            
            # Load existing MS11 config
            self.progress_var.set(60)
            self.load_existing_config()
            
            # Detect system capabilities
            self.progress_var.set(80)
            self.detect_system_capabilities()
            
            self.progress_var.set(100)
            self.root.after(0, lambda: self.status_var.set("✅ Auto-detection complete!"))
            
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"❌ Detection error: {e}"))
            
    def detect_character_name(self):
        """Detect character name from existing configurations."""
        try:
            # Check config/config.json
            config_path = Path("config/config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    if config.get("character_name") and config["character_name"] != "YourCharacterName":
                        return config["character_name"]
            
            # Check profiles/runtime/
            runtime_dir = Path("profiles/runtime")
            if runtime_dir.exists():
                for profile_file in runtime_dir.glob("*.json"):
                    if profile_file.name != "your_character.json":
                        try:
                            with open(profile_file, 'r') as f:
                                profile = json.load(f)
                                if profile.get("character_name"):
                                    return profile["character_name"]
                        except:
                            continue
            
            # Check for any .json files in profiles/
            profiles_dir = Path("profiles")
            if profiles_dir.exists():
                for profile_file in profiles_dir.rglob("*.json"):
                    try:
                        with open(profile_file, 'r') as f:
                            profile = json.load(f)
                            if profile.get("character_name") and profile["character_name"] != "YourCharacterName":
                                return profile["character_name"]
                    except:
                        continue
            
            return None
            
        except Exception as e:
            print(f"Error detecting character name: {e}")
            return None
            
    def detect_swg_installation(self):
        """Detect Star Wars Galaxies installation path."""
        possible_paths = [
            "C:\\Program Files (x86)\\Sony\\Star Wars Galaxies",
            "C:\\Program Files\\Sony\\Star Wars Galaxies",
            "C:\\SWG",
            "D:\\SWG",
            "E:\\SWG"
        ]
        
        # Check common installation paths
        for path in possible_paths:
            if os.path.exists(path) and os.path.exists(os.path.join(path, "swg.exe")):
                return path
        
        # Check running processes
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                if 'swg' in proc.info['name'].lower() and proc.info['exe']:
                    swg_dir = os.path.dirname(proc.info['exe'])
                    if os.path.exists(os.path.join(swg_dir, "swg.exe")):
                        return swg_dir
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return None
        
    def load_existing_config(self):
        """Load existing MS11 configuration."""
        try:
            # Load main config
            config_path = Path("config/config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
                    
                    # Update UI with existing values
                    if self.config.get("character_name"):
                        self.char_name_var.set(self.config["character_name"])
                    if self.config.get("default_mode"):
                        self.default_mode_var.set(self.config["default_mode"])
                    if self.config.get("enable_discord_relay"):
                        self.discord_enabled_var.set(self.config["enable_discord_relay"])
                    if self.config.get("safety"):
                        safety = self.config["safety"]
                        if safety.get("health_threshold"):
                            self.health_threshold_var.set(str(safety["health_threshold"]))
                        if safety.get("fatigue_threshold"):
                            self.fatigue_threshold_var.set(str(safety["fatigue_threshold"]))
                    if self.config.get("session_limits"):
                        self.session_hours_var.set(str(self.config["session_limits"].get("max_hours", 4)))
            
            # Load character profile
            profile_path = Path("profiles/runtime/your_character.json")
            if profile_path.exists():
                with open(profile_path, 'r') as f:
                    self.character_profile = json.load(f)
                    
        except Exception as e:
            print(f"Error loading existing config: {e}")
            
    def detect_system_capabilities(self):
        """Detect system capabilities and optimize settings."""
        try:
            # Check available memory
            memory = psutil.virtual_memory()
            if memory.total < 4 * 1024 * 1024 * 1024:  # Less than 4GB
                self.status_var.set("⚠️ Low memory detected - optimizing settings")
                
            # Check CPU cores
            cpu_count = psutil.cpu_count()
            if cpu_count < 4:
                self.status_var.set("⚠️ Limited CPU cores - adjusting performance settings")
                
            # Check disk space
            disk = psutil.disk_usage('/')
            if disk.free < 2 * 1024 * 1024 * 1024:  # Less than 2GB free
                self.status_var.set("⚠️ Low disk space - check available storage")
                
        except Exception as e:
            print(f"Error detecting system capabilities: {e}")
            
    def browse_swg_path(self):
        """Browse for SWG installation directory."""
        path = filedialog.askdirectory(title="Select Star Wars Galaxies Installation Directory")
        if path:
            if os.path.exists(os.path.join(path, "swg.exe")):
                self.swg_path_var.set(path)
            else:
                messagebox.showerror("Invalid Path", "Selected directory does not contain swg.exe")
                
    def save_configuration(self):
        """Save the configuration to files."""
        try:
            self.status_var.set("💾 Saving configuration...")
            self.progress_var.set(0)
            
            # Create configuration data
            config_data = {
                "character_name": self.char_name_var.get(),
                "swg_installation_path": self.swg_path_var.get(),
                "default_mode": self.default_mode_var.get(),
                "enable_discord_relay": self.discord_enabled_var.get(),
                "safety": {
                    "health_threshold": int(self.health_threshold_var.get()),
                    "fatigue_threshold": int(self.fatigue_threshold_var.get()),
                    "auto_heal": True,
                    "auto_rest": True
                },
                "session_limits": {
                    "max_hours": int(self.session_hours_var.get()),
                    "auto_logout": True
                },
                "performance": {
                    "ocr_enabled": True,
                    "vision_enabled": True,
                    "logging_level": "INFO"
                }
            }
            
            # Save main config
            self.progress_var.set(30)
            os.makedirs("config", exist_ok=True)
            with open("config/config.json", 'w') as f:
                json.dump(config_data, f, indent=4)
            
            # Create character profile
            self.progress_var.set(60)
            profile_data = {
                "character_name": self.char_name_var.get(),
                "profile_name": self.profile_name_var.get(),
                "creation_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
                "settings": config_data
            }
            
            os.makedirs("profiles/runtime", exist_ok=True)
            profile_filename = f"{self.profile_name_var.get()}_profile.json"
            with open(f"profiles/runtime/{profile_filename}", 'w') as f:
                json.dump(profile_data, f, indent=4)
            
            # Create backup of original files
            self.progress_var.set(80)
            self.create_backups()
            
            self.progress_var.set(100)
            self.status_var.set("✅ Configuration saved successfully!")
            
            # Show success message
            messagebox.showinfo("Success", 
                              f"MS11 configuration saved!\n\n"
                              f"Character: {self.char_name_var.get()}\n"
                              f"Profile: {self.profile_name_var.get()}\n"
                              f"Mode: {self.default_mode_var.get()}\n\n"
                              f"Files created:\n"
                              f"• config/config.json\n"
                              f"• profiles/runtime/{profile_filename}")
            
        except Exception as e:
            self.status_var.set(f"❌ Error saving configuration: {e}")
            messagebox.showerror("Error", f"Failed to save configuration:\n{e}")
            
    def create_backups(self):
        """Create backups of original configuration files."""
        try:
            backup_dir = Path("config/backups")
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            
            # Backup original config if it exists
            if os.path.exists("config/config.json"):
                backup_path = backup_dir / f"config_backup_{timestamp}.json"
                with open("config/config.json", 'r') as src, open(backup_path, 'w') as dst:
                    dst.write(src.read())
            
            # Backup original profile if it exists
            if os.path.exists("profiles/runtime/your_character.json"):
                backup_path = backup_dir / f"profile_backup_{timestamp}.json"
                with open("profiles/runtime/your_character.json", 'r') as src, open(backup_path, 'w') as dst:
                    dst.write(src.read())
                    
        except Exception as e:
            print(f"Warning: Could not create backups: {e}")
            
    def launch_ms11(self):
        """Launch MS11 with the configured settings."""
        try:
            if not os.path.exists("src/main.py"):
                messagebox.showerror("Error", "MS11 main.py not found. Please ensure MS11 is properly installed.")
                return
            
            self.status_var.set("🚀 Launching MS11...")
            
            # Launch MS11 in background
            cmd = [sys.executable, "src/main.py", "--profile", self.profile_name_var.get()]
            
            # Use subprocess.Popen to launch in background
            process = subprocess.Popen(cmd, cwd=os.getcwd())
            
            self.status_var.set("✅ MS11 launched successfully!")
            messagebox.showinfo("Success", f"MS11 launched with profile: {self.profile_name_var.get()}")
            
        except Exception as e:
            self.status_var.set(f"❌ Error launching MS11: {e}")
            messagebox.showerror("Error", f"Failed to launch MS11:\n{e}")
            
    def open_dashboard(self):
        """Open the MS11 dashboard."""
        try:
            # Check if dashboard exists
            if not os.path.exists("ms11_dashboard.py"):
                messagebox.showerror("Error", "MS11 Dashboard not found. Please run the dashboard setup first.")
                return
            
            # Launch dashboard in background
            cmd = [sys.executable, "ms11_dashboard.py"]
            subprocess.Popen(cmd, cwd=os.getcwd())
            
            self.status_var.set("📊 Dashboard launched!")
            
        except Exception as e:
            self.status_var.set(f"❌ Error launching dashboard: {e}")
            messagebox.showerror("Error", f"Failed to launch dashboard:\n{e}")
            
    def run(self):
        """Run the auto-configuration interface."""
        self.root.mainloop()

def main():
    """Main entry point."""
    print("🤖 MS11 Auto-Configuration System")
    print("=" * 40)
    
    # Check if required directories exist
    required_dirs = ["config", "profiles/runtime", "src"]
    for directory in required_dirs:
        os.makedirs(directory, exist_ok=True)
    
    # Start the interface
    app = MS11AutoConfig()
    app.run()

if __name__ == "__main__":
    main()
