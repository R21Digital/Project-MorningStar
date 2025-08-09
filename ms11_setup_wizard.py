#!/usr/bin/env python3
"""
MS11 Setup Wizard - Interactive Configuration Interface
Automatically configures MS11 for new users with minimal manual input.
"""

import json
import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import webbrowser
import threading
import time

class MS11SetupWizard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MS11 Setup Wizard 🚀")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Configuration data
        self.config = {}
        self.character_profile = {}
        
        # Setup UI
        self.setup_ui()
        self.load_existing_config()
        
    def setup_ui(self):
        """Setup the main UI components."""
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="🎮 MS11 Setup Wizard", 
                               font=('Arial', 24, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        subtitle = ttk.Label(main_frame, text="Configure MS11 for Star Wars Galaxies", 
                            font=('Arial', 12))
        subtitle.grid(row=1, column=0, columnspan=2, pady=(0, 30))
        
        # Progress indicator
        self.progress_var = tk.StringVar(value="Step 1: Character Setup")
        progress_label = ttk.Label(main_frame, textvariable=self.progress_var, 
                                 font=('Arial', 10, 'bold'))
        progress_label.grid(row=2, column=0, columnspan=2, pady=(0, 20))
        
        # Character setup section
        self.create_character_section(main_frame, 3)
        
        # Game detection section
        self.create_game_detection_section(main_frame, 8)
        
        # MS11 settings section
        self.create_ms11_settings_section(main_frame, 13)
        
        # Action buttons
        self.create_action_buttons(main_frame, 20)
        
        # Status display
        self.status_text = tk.Text(main_frame, height=8, width=70)
        self.status_text.grid(row=21, column=0, columnspan=2, pady=(20, 0))
        
        # Scrollbar for status
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.status_text.yview)
        scrollbar.grid(row=21, column=2, sticky=(tk.N, tk.S))
        self.status_text.configure(yscrollcommand=scrollbar.set)
        
    def create_character_section(self, parent, row):
        """Create character setup section."""
        # Section header
        char_header = ttk.Label(parent, text="👤 Character Configuration", 
                               font=('Arial', 14, 'bold'))
        char_header.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Character name
        ttk.Label(parent, text="Character Name:").grid(row=row+1, column=0, sticky=tk.W)
        self.char_name_var = tk.StringVar()
        char_name_entry = ttk.Entry(parent, textvariable=self.char_name_var, width=30)
        char_name_entry.grid(row=row+1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Character class/build
        ttk.Label(parent, text="Character Build:").grid(row=row+2, column=0, sticky=tk.W)
        self.build_var = tk.StringVar(value="rifleman_medic")
        build_combo = ttk.Combobox(parent, textvariable=self.build_var, 
                                  values=["rifleman_medic", "pistoleer_combat", "marksman_rifleman", "medic_support"])
        build_combo.grid(row=row+2, column=1, sticky=tk.W, padx=(10, 0))
        
        # Starting location
        ttk.Label(parent, text="Starting Planet:").grid(row=row+3, column=0, sticky=tk.W)
        self.planet_var = tk.StringVar(value="Tatooine")
        planet_combo = ttk.Combobox(parent, textvariable=self.planet_var,
                                   values=["Tatooine", "Naboo", "Corellia", "Coruscant", "Lok", "Rori", "Dantooine", "Yavin IV"])
        planet_combo.grid(row=row+3, column=1, sticky=tk.W, padx=(10, 0))
        
        # Starting city
        ttk.Label(parent, text="Starting City:").grid(row=row+4, column=0, sticky=tk.W)
        self.city_var = tk.StringVar(value="Mos Eisley")
        city_entry = ttk.Entry(parent, textvariable=self.city_var, width=30)
        city_entry.grid(row=row+4, column=1, sticky=tk.W, padx=(10, 0))
        
    def create_game_detection_section(self, parent, row):
        """Create game detection section."""
        # Section header
        game_header = ttk.Label(parent, text="🎮 Game Detection", 
                               font=('Arial', 14, 'bold'))
        game_header.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(20, 10))
        
        # SWG installation path
        ttk.Label(parent, text="SWG Installation:").grid(row=row+1, column=0, sticky=tk.W)
        self.swg_path_var = tk.StringVar()
        swg_path_entry = ttk.Entry(parent, textvariable=self.swg_path_var, width=50)
        swg_path_entry.grid(row=row+1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Browse button
        browse_btn = ttk.Button(parent, text="Browse", command=self.browse_swg_path)
        browse_btn.grid(row=row+1, column=2, padx=(5, 0))
        
        # Auto-detect button
        detect_btn = ttk.Button(parent, text="Auto-Detect", command=self.auto_detect_swg)
        detect_btn.grid(row=row+2, column=1, sticky=tk.W, padx=(10, 0))
        
    def create_ms11_settings_section(self, parent, row):
        """Create MS11 settings section."""
        # Section header
        ms11_header = ttk.Label(parent, text="⚙️ MS11 Settings", 
                               font=('Arial', 14, 'bold'))
        ms11_header.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=(20, 10))
        
        # Default mode
        ttk.Label(parent, text="Default Mode:").grid(row=row+1, column=0, sticky=tk.W)
        self.mode_var = tk.StringVar(value="medic")
        mode_combo = ttk.Combobox(parent, textvariable=self.mode_var,
                                 values=["medic", "quest", "combat", "crafting", "grinding"])
        mode_combo.grid(row=row+1, column=1, sticky=tk.W, padx=(10, 0))
        
        # Safety settings
        ttk.Label(parent, text="Health Threshold (%):").grid(row=row+2, column=0, sticky=tk.W)
        self.health_threshold_var = tk.StringVar(value="50")
        health_entry = ttk.Entry(parent, textvariable=self.health_threshold_var, width=10)
        health_entry.grid(row=row+2, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(parent, text="Fatigue Threshold (%):").grid(row=row+3, column=0, sticky=tk.W)
        self.fatigue_threshold_var = tk.StringVar(value="75")
        fatigue_entry = ttk.Entry(parent, textvariable=self.fatigue_threshold_var, width=10)
        fatigue_entry.grid(row=row+3, column=1, sticky=tk.W, padx=(10, 0))
        
        # Discord integration
        self.discord_var = tk.BooleanVar(value=False)
        discord_check = ttk.Checkbutton(parent, text="Enable Discord Integration", 
                                       variable=self.discord_var)
        discord_check.grid(row=row+4, column=0, columnspan=2, sticky=tk.W, pady=(10, 0))
        
    def create_action_buttons(self, parent, row):
        """Create action buttons."""
        button_frame = ttk.Frame(parent)
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        # Test configuration
        test_btn = ttk.Button(button_frame, text="🧪 Test Configuration", 
                             command=self.test_configuration)
        test_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Save configuration
        save_btn = ttk.Button(button_frame, text="💾 Save Configuration", 
                             command=self.save_configuration)
        save_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Launch MS11
        launch_btn = ttk.Button(button_frame, text="🚀 Launch MS11", 
                               command=self.launch_ms11)
        launch_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Open dashboard
        dashboard_btn = ttk.Button(button_frame, text="📊 Open Dashboard", 
                                  command=self.open_dashboard)
        dashboard_btn.pack(side=tk.LEFT, padx=(0, 10))
        
    def browse_swg_path(self):
        """Browse for SWG installation directory."""
        path = filedialog.askdirectory(title="Select SWG Installation Directory")
        if path:
            self.swg_path_var.set(path)
            self.log_status(f"Selected SWG path: {path}")
            
    def auto_detect_swg(self):
        """Auto-detect SWG installation."""
        self.log_status("🔍 Auto-detecting SWG installation...")
        
        # Common SWG installation paths
        common_paths = [
            "C:\\Program Files (x86)\\Sony\\Star Wars Galaxies",
            "C:\\Program Files\\Sony\\Star Wars Galaxies",
            "C:\\SWG",
            "D:\\SWG",
            "C:\\Games\\SWG"
        ]
        
        for path in common_paths:
            if os.path.exists(path) and os.path.exists(os.path.join(path, "swg.exe")):
                self.swg_path_var.set(path)
                self.log_status(f"✅ Auto-detected SWG at: {path}")
                return
                
        self.log_status("❌ Could not auto-detect SWG. Please browse manually.")
        
    def load_existing_config(self):
        """Load existing configuration if available."""
        config_path = Path("config/config.json")
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    self.config = json.load(f)
                    
                # Populate UI with existing values
                if 'character_name' in self.config:
                    self.char_name_var.set(self.config['character_name'])
                if 'default_mode' in self.config:
                    self.mode_var.set(self.config['default_mode'])
                if 'safety' in self.config:
                    if 'health_threshold' in self.config['safety']:
                        self.health_threshold_var.set(str(self.config['safety']['health_threshold']))
                    if 'fatigue_threshold' in self.config['safety']:
                        self.fatigue_threshold_var.set(str(self.config['safety']['fatigue_threshold']))
                        
                self.log_status("✅ Loaded existing configuration")
            except Exception as e:
                self.log_status(f"❌ Error loading config: {e}")
                
    def test_configuration(self):
        """Test the current configuration."""
        self.log_status("🧪 Testing configuration...")
        
        # Validate character name
        if not self.char_name_var.get().strip():
            messagebox.showerror("Error", "Please enter a character name")
            return
            
        # Validate SWG path
        if not self.swg_path_var.get().strip():
            messagebox.showerror("Error", "Please select SWG installation path")
            return
            
        # Test SWG executable
        swg_exe = os.path.join(self.swg_path_var.get(), "swg.exe")
        if not os.path.exists(swg_exe):
            messagebox.showerror("Error", f"SWG executable not found at: {swg_exe}")
            return
            
        self.log_status("✅ Configuration validation passed!")
        messagebox.showinfo("Success", "Configuration is valid! You can now save and launch MS11.")
        
    def save_configuration(self):
        """Save the configuration to files."""
        self.log_status("💾 Saving configuration...")
        
        try:
            # Create config directory if it doesn't exist
            os.makedirs("config", exist_ok=True)
            os.makedirs("profiles/runtime", exist_ok=True)
            
            # Save main config
            config_data = {
                "character_name": self.char_name_var.get().strip(),
                "default_mode": self.mode_var.get(),
                "enable_discord_relay": self.discord_var.get(),
                "swg_installation_path": self.swg_path_var.get().strip(),
                "session": {
                    "idle_timeout": 300,
                    "max_duration": 14400,
                    "auto_resume": True
                },
                "logging": {
                    "level": "INFO",
                    "file": "logs/ms11.log"
                },
                "safety": {
                    "fatigue_threshold": int(self.fatigue_threshold_var.get()),
                    "health_threshold": int(self.health_threshold_var.get()),
                    "action_threshold": 25
                }
            }
            
            with open("config/config.json", 'w') as f:
                json.dump(config_data, f, indent=4)
                
            # Save character profile
            profile_data = {
                "name": self.char_name_var.get().strip(),
                "character_name": self.char_name_var.get().strip(),
                "default_mode": self.mode_var.get(),
                "skip_modes": [],
                "farming_targets": ["auto"],
                "skill_build": self.build_var.get(),
                "support_target": "auto",
                "preferred_trainers": {
                    "combat": "auto",
                    "crafting": "auto",
                    "entertainer": "auto"
                },
                "description": f"Auto-configured profile for {self.char_name_var.get().strip()}",
                "version": "1.0.0",
                "settings": {
                    "scan_interval": 60,
                    "idle_scan_interval": 300,
                    "travel_scan_interval": 30,
                    "ocr_confidence_threshold": 50.0,
                    "privacy_enabled": True
                },
                "modes": {
                    "quest": {
                        "enabled": True,
                        "priority": 1,
                        "settings": {
                            "auto_accept": True,
                            "auto_complete": True,
                            "quest_types": ["story", "daily", "repeatable"]
                        }
                    },
                    "combat": {
                        "enabled": True,
                        "priority": 2,
                        "settings": {
                            "combat_style": "defensive",
                            "health_threshold": int(self.health_threshold_var.get()),
                            "action_threshold": 25
                        }
                    },
                    "medic": {
                        "enabled": True,
                        "priority": 3,
                        "settings": {
                            "heal_threshold": int(self.fatigue_threshold_var.get()),
                            "buff_interval": 300
                        }
                    }
                },
                "paths": {
                    "logs": "logs/ms11.log",
                    "data": "data/ms11.db",
                    "cache": "data/cache"
                }
            }
            
            profile_filename = f"profiles/runtime/{self.char_name_var.get().strip().lower()}.json"
            with open(profile_filename, 'w') as f:
                json.dump(profile_data, f, indent=4)
                
            self.log_status(f"✅ Configuration saved successfully!")
            self.log_status(f"   - Main config: config/config.json")
            self.log_status(f"   - Character profile: {profile_filename}")
            
            messagebox.showinfo("Success", "Configuration saved successfully! You can now launch MS11.")
            
        except Exception as e:
            self.log_status(f"❌ Error saving configuration: {e}")
            messagebox.showerror("Error", f"Failed to save configuration: {e}")
            
    def launch_ms11(self):
        """Launch MS11 with the current configuration."""
        if not os.path.exists("config/config.json"):
            messagebox.showerror("Error", "Please save configuration first")
            return
            
        self.log_status("🚀 Launching MS11...")
        
        try:
            # Launch MS11 in a separate thread
            def run_ms11():
                try:
                    # Check if main.py exists
                    if os.path.exists("src/main.py"):
                        cmd = [sys.executable, "src/main.py", "--profile", self.char_name_var.get().strip().lower()]
                        subprocess.run(cmd, cwd=os.getcwd())
                    else:
                        self.log_status("❌ MS11 main.py not found. Please ensure MS11 is properly installed.")
                except Exception as e:
                    self.log_status(f"❌ Error launching MS11: {e}")
                    
            thread = threading.Thread(target=run_ms11, daemon=True)
            thread.start()
            
            self.log_status("✅ MS11 launched in background")
            
        except Exception as e:
            self.log_status(f"❌ Error launching MS11: {e}")
            
    def open_dashboard(self):
        """Open the MS11 dashboard."""
        self.log_status("📊 Opening MS11 dashboard...")
        
        try:
            # Check if dashboard exists
            if os.path.exists("dashboard/app.py"):
                # Launch dashboard in browser
                webbrowser.open("http://localhost:5000")
                
                # Start dashboard in background
                def start_dashboard():
                    try:
                        subprocess.run([sys.executable, "dashboard/app.py"], cwd=os.getcwd())
                    except Exception as e:
                        self.log_status(f"❌ Error starting dashboard: {e}")
                        
                thread = threading.Thread(target=start_dashboard, daemon=True)
                thread.start()
                
                self.log_status("✅ Dashboard opened in browser")
            else:
                self.log_status("❌ Dashboard not found. Creating basic MS11 dashboard...")
                self.create_basic_dashboard()
                
        except Exception as e:
            self.log_status(f"❌ Error opening dashboard: {e}")
            
    def create_basic_dashboard(self):
        """Create a basic MS11 dashboard if none exists."""
        try:
            os.makedirs("dashboard", exist_ok=True)
            os.makedirs("dashboard/templates", exist_ok=True)
            
            # Create basic dashboard app
            dashboard_code = '''from flask import Flask, render_template, jsonify
import json
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('ms11_dashboard.html')

@app.route('/api/status')
def status():
    try:
        with open('config/config.json', 'r') as f:
            config = json.load(f)
        return jsonify({"status": "running", "config": config})
    except:
        return jsonify({"status": "error", "message": "Configuration not found"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
'''
            
            with open("dashboard/app.py", 'w') as f:
                f.write(dashboard_code)
                
            # Create dashboard template
            template_code = '''<!DOCTYPE html>
<html>
<head>
    <title>MS11 Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .status { padding: 20px; background: #f0f0f0; border-radius: 5px; }
        .config { background: white; padding: 15px; margin: 10px 0; border: 1px solid #ddd; }
    </style>
</head>
<body>
    <h1>🎮 MS11 Dashboard</h1>
    <div class="status">
        <h2>System Status</h2>
        <div id="status">Loading...</div>
    </div>
    <div class="config">
        <h2>Configuration</h2>
        <div id="config">Loading...</div>
    </div>
    
    <script>
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                document.getElementById('status').innerHTML = 
                    '<p><strong>Status:</strong> ' + data.status + '</p>';
                if (data.config) {
                    document.getElementById('config').innerHTML = 
                        '<pre>' + JSON.stringify(data.config, null, 2) + '</pre>';
                }
            });
    </script>
</body>
</html>
'''
            
            with open("dashboard/templates/ms11_dashboard.html", 'w') as f:
                f.write(template_code)
                
            self.log_status("✅ Basic MS11 dashboard created")
            self.open_dashboard()
            
        except Exception as e:
            self.log_status(f"❌ Error creating dashboard: {e}")
            
    def log_status(self, message):
        """Log a status message to the status display."""
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.root.update_idletasks()
        
    def run(self):
        """Run the setup wizard."""
        self.root.mainloop()

def main():
    """Main entry point."""
    print("🚀 Starting MS11 Setup Wizard...")
    
    try:
        wizard = MS11SetupWizard()
        wizard.run()
    except Exception as e:
        print(f"❌ Error starting wizard: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
