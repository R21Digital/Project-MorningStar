"""
Collection Tracker UI Overlay

This module provides a UI overlay for the local dashboard that displays
collection status, nearby items, and progress information.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

from core.collection_tracker import get_collection_tracker, CollectionType, CollectionItem


class CollectionOverlay:
    """UI overlay for collection tracking and management."""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.tracker = get_collection_tracker()
        self.logger = logging.getLogger("collection_overlay")
        self.root = None
        self.is_visible = False
        
        # UI elements
        self.status_frame = None
        self.progress_frame = None
        self.nearby_frame = None
        self.controls_frame = None
        
        # Data
        self.current_status = {}
        self.nearby_items = []
        self.update_interval = 5000  # 5 seconds
        
    def create_overlay(self):
        """Create the collection overlay window."""
        if self.root:
            return
        
        self.root = tk.Toplevel(self.parent) if self.parent else tk.Tk()
        self.root.title("Collection Tracker")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
        # Create main frames
        self._create_header()
        self._create_status_section()
        self._create_progress_section()
        self._create_nearby_section()
        self._create_controls_section()
        
        # Start auto-update
        self._schedule_update()
        
        self.is_visible = True
        self.logger.info("Collection overlay created")
    
    def _create_header(self):
        """Create the header section."""
        header_frame = ttk.Frame(self.root)
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(header_frame, text="Collection Tracker", 
                               font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, sticky="w")
        
        # Last update time
        self.update_time_label = ttk.Label(header_frame, text="Last update: Never")
        self.update_time_label.grid(row=0, column=1, sticky="e")
    
    def _create_status_section(self):
        """Create the status section."""
        self.status_frame = ttk.LabelFrame(self.root, text="Collection Status")
        self.status_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        # Status grid
        status_grid = ttk.Frame(self.status_frame)
        status_grid.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Total collections
        ttk.Label(status_grid, text="Total Collections:").grid(row=0, column=0, sticky="w")
        self.total_label = ttk.Label(status_grid, text="0")
        self.total_label.grid(row=0, column=1, sticky="w", padx=(10, 0))
        
        # Completed collections
        ttk.Label(status_grid, text="Completed:").grid(row=1, column=0, sticky="w")
        self.completed_label = ttk.Label(status_grid, text="0")
        self.completed_label.grid(row=1, column=1, sticky="w", padx=(10, 0))
        
        # Completion percentage
        ttk.Label(status_grid, text="Completion:").grid(row=2, column=0, sticky="w")
        self.percentage_label = ttk.Label(status_grid, text="0%")
        self.percentage_label.grid(row=2, column=1, sticky="w", padx=(10, 0))
        
        # Current target
        ttk.Label(status_grid, text="Current Target:").grid(row=3, column=0, sticky="w")
        self.target_label = ttk.Label(status_grid, text="None")
        self.target_label.grid(row=3, column=1, sticky="w", padx=(10, 0))
    
    def _create_progress_section(self):
        """Create the progress by category section."""
        self.progress_frame = ttk.LabelFrame(self.root, text="Progress by Category")
        self.progress_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.progress_frame.grid_columnconfigure(0, weight=1)
        
        # Progress treeview
        columns = ("Category", "Collected", "Total", "Percentage")
        self.progress_tree = ttk.Treeview(self.progress_frame, columns=columns, 
                                        show="headings", height=5)
        
        for col in columns:
            self.progress_tree.heading(col, text=col)
            self.progress_tree.column(col, width=100)
        
        self.progress_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Scrollbar
        progress_scrollbar = ttk.Scrollbar(self.progress_frame, orient="vertical", 
                                         command=self.progress_tree.yview)
        progress_scrollbar.grid(row=0, column=1, sticky="ns")
        self.progress_tree.configure(yscrollcommand=progress_scrollbar.set)
    
    def _create_nearby_section(self):
        """Create the nearby items section."""
        self.nearby_frame = ttk.LabelFrame(self.root, text="Nearby Collections")
        self.nearby_frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        self.nearby_frame.grid_columnconfigure(0, weight=1)
        
        # Nearby treeview
        columns = ("Name", "Type", "Distance", "Priority")
        self.nearby_tree = ttk.Treeview(self.nearby_frame, columns=columns, 
                                       show="headings", height=4)
        
        for col in columns:
            self.nearby_tree.heading(col, text=col)
            self.nearby_tree.column(col, width=120)
        
        self.nearby_tree.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Scrollbar
        nearby_scrollbar = ttk.Scrollbar(self.nearby_frame, orient="vertical", 
                                        command=self.nearby_tree.yview)
        nearby_scrollbar.grid(row=0, column=1, sticky="ns")
        self.nearby_tree.configure(yscrollcommand=nearby_scrollbar.set)
        
        # Double-click to select
        self.nearby_tree.bind("<Double-1>", self._on_nearby_select)
    
    def _create_controls_section(self):
        """Create the controls section."""
        self.controls_frame = ttk.Frame(self.root)
        self.controls_frame.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
        
        # Buttons
        ttk.Button(self.controls_frame, text="Refresh", 
                  command=self._refresh_data).grid(row=0, column=0, padx=5)
        ttk.Button(self.controls_frame, text="Auto-Complete", 
                  command=self._auto_complete).grid(row=0, column=1, padx=5)
        ttk.Button(self.controls_frame, text="Trigger Goals", 
                  command=self._trigger_goals).grid(row=0, column=2, padx=5)
        ttk.Button(self.controls_frame, text="Export Logs", 
                  command=self._export_logs).grid(row=0, column=3, padx=5)
    
    def _refresh_data(self):
        """Refresh the collection data."""
        try:
            # Get current status
            self.current_status = self.tracker.get_collection_status()
            
            # Update status labels
            self.total_label.config(text=str(self.current_status.get("total_collections", 0)))
            self.completed_label.config(text=str(self.current_status.get("completed_collections", 0)))
            
            completion_pct = self.current_status.get("completion_percentage", 0)
            self.percentage_label.config(text=f"{completion_pct:.1f}%")
            
            current_target = self.current_status.get("current_target")
            if current_target:
                self.target_label.config(text=current_target.get("name", "Unknown"))
            else:
                self.target_label.config(text="None")
            
            # Update progress tree
            self._update_progress_tree()
            
            # Update nearby items
            self._update_nearby_items()
            
            # Update timestamp
            self.update_time_label.config(text=f"Last update: {datetime.now().strftime('%H:%M:%S')}")
            
            self.logger.info("Collection data refreshed")
            
        except Exception as e:
            self.logger.error(f"Error refreshing data: {e}")
            messagebox.showerror("Error", f"Failed to refresh data: {e}")
    
    def _update_progress_tree(self):
        """Update the progress treeview."""
        # Clear existing items
        for item in self.progress_tree.get_children():
            self.progress_tree.delete(item)
        
        # Add progress data
        progress_data = self.current_status.get("progress_by_category", {})
        for category, data in progress_data.items():
            self.progress_tree.insert("", "end", values=(
                category.title(),
                data.get("collected", 0),
                data.get("total", 0),
                f"{data.get('percentage', 0):.1f}%"
            ))
    
    def _update_nearby_items(self):
        """Update the nearby items treeview."""
        # Clear existing items
        for item in self.nearby_tree.get_children():
            self.nearby_tree.delete(item)
        
        try:
            # Get nearby items
            self.nearby_items = self.tracker.trigger_collection_goals()
            
            # Add to treeview
            for item in self.nearby_items:
                distance = self.tracker._calculate_distance((100, 100), item.coordinates)  # Placeholder location
                priority = self.tracker._calculate_priority_score(item, (100, 100))
                
                self.nearby_tree.insert("", "end", values=(
                    item.name,
                    item.collection_type.value.title(),
                    f"{distance:.1f}m",
                    f"{priority:.2f}"
                ))
                
        except Exception as e:
            self.logger.error(f"Error updating nearby items: {e}")
    
    def _on_nearby_select(self, event):
        """Handle nearby item selection."""
        selection = self.nearby_tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        item_data = self.nearby_tree.item(item_id)
        item_name = item_data["values"][0]
        
        # Find the corresponding collection item
        for item in self.nearby_items:
            if item.name == item_name:
                self._show_item_details(item)
                break
    
    def _show_item_details(self, item: CollectionItem):
        """Show details for a collection item."""
        details = f"""
Collection Item Details:

Name: {item.name}
Type: {item.collection_type.value.title()}
Planet: {item.planet}
Zone: {item.zone}
Coordinates: {item.coordinates}
Rarity: {item.rarity or 'Unknown'}
Required Level: {item.required_level or 'None'}
Required Profession: {item.required_profession or 'None'}
Description: {item.description or 'No description available'}
        """
        
        messagebox.showinfo("Item Details", details)
    
    def _auto_complete(self):
        """Trigger auto-complete for nearby collections."""
        try:
            success = self.tracker.auto_complete_collections()
            if success:
                messagebox.showinfo("Success", "Successfully completed a nearby collection!")
            else:
                messagebox.showinfo("Info", "No nearby collections found or completed.")
            
            # Refresh data
            self._refresh_data()
            
        except Exception as e:
            self.logger.error(f"Error in auto-complete: {e}")
            messagebox.showerror("Error", f"Auto-complete failed: {e}")
    
    def _trigger_goals(self):
        """Trigger collection goals."""
        try:
            goals = self.tracker.trigger_collection_goals()
            if goals:
                messagebox.showinfo("Goals Triggered", 
                                  f"Found {len(goals)} collection goals to prioritize!")
            else:
                messagebox.showinfo("Info", "No collection goals found nearby.")
            
            # Refresh data
            self._refresh_data()
            
        except Exception as e:
            self.logger.error(f"Error triggering goals: {e}")
            messagebox.showerror("Error", f"Failed to trigger goals: {e}")
    
    def _export_logs(self):
        """Export collection logs."""
        try:
            log_dir = Path("logs/collections")
            if not log_dir.exists():
                messagebox.showinfo("Info", "No collection logs found.")
                return
            
            # Find latest log file
            log_files = list(log_dir.glob("*.json"))
            if not log_files:
                messagebox.showinfo("Info", "No collection logs found.")
                return
            
            latest_log = max(log_files, key=lambda f: f.stat().st_mtime)
            
            # Read and format log data
            with open(latest_log, 'r') as f:
                log_data = [json.loads(line) for line in f if line.strip()]
            
            # Create export file
            export_file = Path(f"collection_logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            with open(export_file, 'w') as f:
                json.dump(log_data, f, indent=2)
            
            messagebox.showinfo("Export Complete", 
                              f"Collection logs exported to: {export_file}")
            
        except Exception as e:
            self.logger.error(f"Error exporting logs: {e}")
            messagebox.showerror("Error", f"Failed to export logs: {e}")
    
    def _schedule_update(self):
        """Schedule the next data update."""
        if self.is_visible and self.root:
            self._refresh_data()
            self.root.after(self.update_interval, self._schedule_update)
    
    def show(self):
        """Show the collection overlay."""
        if not self.root:
            self.create_overlay()
        else:
            self.root.deiconify()
            self.root.lift()
        
        self.is_visible = True
        self._refresh_data()
    
    def hide(self):
        """Hide the collection overlay."""
        if self.root:
            self.root.withdraw()
        self.is_visible = False
    
    def destroy(self):
        """Destroy the collection overlay."""
        if self.root:
            self.root.destroy()
            self.root = None
        self.is_visible = False


# Global instance
_collection_overlay = None


def get_collection_overlay(parent=None) -> CollectionOverlay:
    """Get the global collection overlay instance."""
    global _collection_overlay
    if _collection_overlay is None:
        _collection_overlay = CollectionOverlay(parent)
    return _collection_overlay


def show_collection_overlay(parent=None):
    """Show the collection overlay."""
    overlay = get_collection_overlay(parent)
    overlay.show()


def hide_collection_overlay():
    """Hide the collection overlay."""
    if _collection_overlay:
        _collection_overlay.hide()


def destroy_collection_overlay():
    """Destroy the collection overlay."""
    global _collection_overlay
    if _collection_overlay:
        _collection_overlay.destroy()
        _collection_overlay = None 