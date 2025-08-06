"""
Progress Dashboard Module

This module provides a comprehensive UI dashboard for tracking progress,
smart suggestions, and completion analytics for the Smart Todo Tracker system.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

# Import the smart todo tracker
from core.todo_tracker import (
    get_smart_tracker, SmartGoal, GoalStatus, GoalPriority, GoalCategory,
    GoalType, SmartSuggestion, CompletionScore, get_smart_suggestions,
    get_completion_scores, get_statistics
)

logger = logging.getLogger(__name__)


class ProgressDashboard:
    """
    Comprehensive progress dashboard for smart todo tracking.
    
    Features:
    - Visual progress tracking with charts and graphs
    - Smart suggestions display
    - Category completion overview
    - Goal management interface
    - Real-time statistics
    """
    
    def __init__(self, root: Optional[tk.Tk] = None):
        """Initialize the progress dashboard."""
        self.root = root or tk.Tk()
        self.root.title("Smart Todo Progress Dashboard")
        self.root.geometry("1200x800")
        
        # Get the smart tracker
        self.tracker = get_smart_tracker()
        
        # Current location (can be updated)
        self.current_location: Optional[Tuple[str, str]] = None
        
        # Setup UI
        self._setup_ui()
        self._setup_styles()
        
        # Initial data load
        self._refresh_data()
        
        logger.info("Progress Dashboard initialized")
    
    def _setup_ui(self):
        """Setup the main UI components."""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎯 Smart Todo Progress Dashboard", 
                               font=("Arial", 16, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self._create_overview_tab()
        self._create_suggestions_tab()
        self._create_goals_tab()
        self._create_analytics_tab()
        self._create_settings_tab()
    
    def _setup_styles(self):
        """Setup custom styles for the dashboard."""
        style = ttk.Style()
        
        # Configure styles
        style.configure("Title.TLabel", font=("Arial", 12, "bold"))
        style.configure("Subtitle.TLabel", font=("Arial", 10, "bold"))
        style.configure("Success.TLabel", foreground="green")
        style.configure("Warning.TLabel", foreground="orange")
        style.configure("Error.TLabel", foreground="red")
        
        # Progress bar styles
        style.configure("Progress.Horizontal.TProgressbar", 
                       troughcolor="lightgray", background="green")
    
    def _create_overview_tab(self):
        """Create the overview tab."""
        overview_frame = ttk.Frame(self.notebook)
        self.notebook.add(overview_frame, text="📊 Overview")
        
        # Statistics section
        stats_frame = ttk.LabelFrame(overview_frame, text="📈 Overall Statistics", padding=10)
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.stats_labels = {}
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        # Create statistics labels
        stat_names = [
            ("total_goals", "Total Goals"),
            ("completed_goals", "Completed"),
            ("in_progress_goals", "In Progress"),
            ("not_started_goals", "Not Started"),
            ("overall_completion_percentage", "Overall Completion %")
        ]
        
        for i, (key, name) in enumerate(stat_names):
            row = i // 3
            col = i % 3
            
            label = ttk.Label(stats_grid, text=f"{name}:", style="Subtitle.TLabel")
            label.grid(row=row, column=col*2, sticky="w", padx=(0, 5), pady=2)
            
            value_label = ttk.Label(stats_grid, text="0")
            value_label.grid(row=row, column=col*2+1, sticky="w", padx=(0, 20), pady=2)
            self.stats_labels[key] = value_label
        
        # Completion scores section
        scores_frame = ttk.LabelFrame(overview_frame, text="🏆 Category Completion", padding=10)
        scores_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create canvas for completion chart
        self.completion_figure, self.completion_ax = plt.subplots(figsize=(10, 6))
        self.completion_canvas = FigureCanvasTkAgg(self.completion_figure, scores_frame)
        self.completion_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _create_suggestions_tab(self):
        """Create the suggestions tab."""
        suggestions_frame = ttk.Frame(self.notebook)
        self.notebook.add(suggestions_frame, text="💡 Smart Suggestions")
        
        # Location selector
        location_frame = ttk.LabelFrame(suggestions_frame, text="📍 Current Location", padding=10)
        location_frame.pack(fill=tk.X, padx=5, pady=5)
        
        location_grid = ttk.Frame(location_frame)
        location_grid.pack(fill=tk.X)
        
        ttk.Label(location_grid, text="Planet:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.planet_var = tk.StringVar(value="tatooine")
        planet_combo = ttk.Combobox(location_grid, textvariable=self.planet_var, 
                                   values=["tatooine", "naboo", "corellia", "talus", "rori", "lok"])
        planet_combo.grid(row=0, column=1, sticky="w", padx=(0, 20))
        
        ttk.Label(location_grid, text="City:").grid(row=0, column=2, sticky="w", padx=(0, 5))
        self.city_var = tk.StringVar(value="mos_eisley")
        city_combo = ttk.Combobox(location_grid, textvariable=self.city_var, 
                                 values=["mos_eisley", "theed", "coronet", "narmle", "restuss", "nyms_stronghold"])
        city_combo.grid(row=0, column=3, sticky="w", padx=(0, 20))
        
        refresh_btn = ttk.Button(location_grid, text="🔄 Refresh Suggestions", 
                                command=self._refresh_suggestions)
        refresh_btn.grid(row=0, column=4, padx=(20, 0))
        
        # Suggestions list
        suggestions_list_frame = ttk.LabelFrame(suggestions_frame, text="🎯 Smart Suggestions", padding=10)
        suggestions_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview for suggestions
        columns = ("Priority", "Goal", "Reason", "Time", "Location")
        self.suggestions_tree = ttk.Treeview(suggestions_list_frame, columns=columns, show="headings", height=10)
        
        # Configure columns
        for col in columns:
            self.suggestions_tree.heading(col, text=col)
            self.suggestions_tree.column(col, width=150)
        
        # Add scrollbar
        suggestions_scrollbar = ttk.Scrollbar(suggestions_list_frame, orient="vertical", 
                                            command=self.suggestions_tree.yview)
        self.suggestions_tree.configure(yscrollcommand=suggestions_scrollbar.set)
        
        self.suggestions_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        suggestions_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Action buttons
        action_frame = ttk.Frame(suggestions_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(action_frame, text="✅ Start Selected Goal", 
                  command=self._start_selected_goal).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="📋 View Goal Details", 
                  command=self._view_goal_details).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="🗺️ Show Path", 
                  command=self._show_goal_path).pack(side=tk.LEFT)
    
    def _create_goals_tab(self):
        """Create the goals management tab."""
        goals_frame = ttk.Frame(self.notebook)
        self.notebook.add(goals_frame, text="📋 Goals Management")
        
        # Filters
        filters_frame = ttk.LabelFrame(goals_frame, text="🔍 Filters", padding=10)
        filters_frame.pack(fill=tk.X, padx=5, pady=5)
        
        filters_grid = ttk.Frame(filters_frame)
        filters_grid.pack(fill=tk.X)
        
        # Status filter
        ttk.Label(filters_grid, text="Status:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.status_filter_var = tk.StringVar(value="all")
        status_combo = ttk.Combobox(filters_grid, textvariable=self.status_filter_var,
                                   values=["all", "not_started", "in_progress", "completed"])
        status_combo.grid(row=0, column=1, sticky="w", padx=(0, 20))
        
        # Category filter
        ttk.Label(filters_grid, text="Category:").grid(row=0, column=2, sticky="w", padx=(0, 5))
        self.category_filter_var = tk.StringVar(value="all")
        category_combo = ttk.Combobox(filters_grid, textvariable=self.category_filter_var,
                                     values=["all"] + [cat.value for cat in GoalCategory])
        category_combo.grid(row=0, column=3, sticky="w", padx=(0, 20))
        
        # Priority filter
        ttk.Label(filters_grid, text="Priority:").grid(row=0, column=4, sticky="w", padx=(0, 5))
        self.priority_filter_var = tk.StringVar(value="all")
        priority_combo = ttk.Combobox(filters_grid, textvariable=self.priority_filter_var,
                                     values=["all", "low", "medium", "high", "critical"])
        priority_combo.grid(row=0, column=5, sticky="w", padx=(0, 20))
        
        # Search
        ttk.Label(filters_grid, text="Search:").grid(row=0, column=6, sticky="w", padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(filters_grid, textvariable=self.search_var)
        search_entry.grid(row=0, column=7, sticky="w", padx=(0, 20))
        
        # Apply filters button
        ttk.Button(filters_grid, text="🔍 Apply Filters", 
                  command=self._apply_filters).grid(row=0, column=8, padx=(20, 0))
        
        # Goals list
        goals_list_frame = ttk.LabelFrame(goals_frame, text="📋 Goals", padding=10)
        goals_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview for goals
        columns = ("Status", "Priority", "Title", "Category", "Progress", "Location")
        self.goals_tree = ttk.Treeview(goals_list_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        for col in columns:
            self.goals_tree.heading(col, text=col)
            self.goals_tree.column(col, width=120)
        
        # Add scrollbar
        goals_scrollbar = ttk.Scrollbar(goals_list_frame, orient="vertical", 
                                       command=self.goals_tree.yview)
        self.goals_tree.configure(yscrollcommand=goals_scrollbar.set)
        
        self.goals_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        goals_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Action buttons
        action_frame = ttk.Frame(goals_frame)
        action_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(action_frame, text="➕ Add Goal", 
                  command=self._add_goal_dialog).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="✏️ Edit Goal", 
                  command=self._edit_goal_dialog).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="✅ Complete Goal", 
                  command=self._complete_selected_goal).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(action_frame, text="🗑️ Delete Goal", 
                  command=self._delete_selected_goal).pack(side=tk.LEFT)
    
    def _create_analytics_tab(self):
        """Create the analytics tab."""
        analytics_frame = ttk.Frame(self.notebook)
        self.notebook.add(analytics_frame, text="📊 Analytics")
        
        # Charts section
        charts_frame = ttk.LabelFrame(analytics_frame, text="📈 Charts", padding=10)
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create figure with subplots
        self.analytics_figure, ((self.pie_ax, self.bar_ax), (self.timeline_ax, self.radar_ax)) = plt.subplots(2, 2, figsize=(12, 8))
        self.analytics_canvas = FigureCanvasTkAgg(self.analytics_figure, charts_frame)
        self.analytics_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _create_settings_tab(self):
        """Create the settings tab."""
        settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(settings_frame, text="⚙️ Settings")
        
        # Settings content
        settings_content = ttk.Frame(settings_frame)
        settings_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Auto-refresh settings
        refresh_frame = ttk.LabelFrame(settings_content, text="🔄 Auto-Refresh Settings", padding=10)
        refresh_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.auto_refresh_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(refresh_frame, text="Enable auto-refresh", 
                       variable=self.auto_refresh_var).pack(anchor=tk.W)
        
        ttk.Label(refresh_frame, text="Refresh interval (seconds):").pack(anchor=tk.W, pady=(10, 0))
        self.refresh_interval_var = tk.StringVar(value="30")
        ttk.Entry(refresh_frame, textvariable=self.refresh_interval_var, width=10).pack(anchor=tk.W)
        
        # Display settings
        display_frame = ttk.LabelFrame(settings_content, text="📱 Display Settings", padding=10)
        display_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.show_progress_bars_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(display_frame, text="Show progress bars", 
                       variable=self.show_progress_bars_var).pack(anchor=tk.W)
        
        self.show_completion_percentages_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(display_frame, text="Show completion percentages", 
                       variable=self.show_completion_percentages_var).pack(anchor=tk.W)
        
        # Data management
        data_frame = ttk.LabelFrame(settings_content, text="💾 Data Management", padding=10)
        data_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(data_frame, text="📤 Export Data", 
                  command=self._export_data).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(data_frame, text="📥 Import Data", 
                  command=self._import_data).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(data_frame, text="🗑️ Clear All Data", 
                  command=self._clear_data).pack(side=tk.LEFT)
    
    def _refresh_data(self):
        """Refresh all data from the tracker."""
        try:
            # Update statistics
            stats = get_statistics()
            for key, label in self.stats_labels.items():
                value = stats.get(key, 0)
                if key == "overall_completion_percentage":
                    label.config(text=f"{value:.1f}%")
                else:
                    label.config(text=str(value))
            
            # Update completion chart
            self._update_completion_chart()
            
            # Update suggestions
            self._refresh_suggestions()
            
            # Update goals list
            self._refresh_goals_list()
            
            # Update analytics
            self._update_analytics()
            
            logger.info("Dashboard data refreshed")
            
        except Exception as e:
            logger.error(f"Error refreshing data: {e}")
            messagebox.showerror("Error", f"Failed to refresh data: {e}")
    
    def _update_completion_chart(self):
        """Update the completion chart."""
        try:
            self.completion_ax.clear()
            
            scores = get_completion_scores()
            if not scores:
                self.completion_ax.text(0.5, 0.5, "No data available", 
                                      ha='center', va='center', transform=self.completion_ax.transAxes)
                self.completion_canvas.draw()
                return
            
            categories = list(scores.keys())
            percentages = [scores[cat].completion_percentage for cat in categories]
            
            # Create bar chart
            bars = self.completion_ax.bar(categories, percentages, color='skyblue', alpha=0.7)
            
            # Add value labels on bars
            for bar, percentage in zip(bars, percentages):
                height = bar.get_height()
                self.completion_ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                                      f'{percentage:.1f}%', ha='center', va='bottom')
            
            self.completion_ax.set_title("Category Completion Percentages")
            self.completion_ax.set_ylabel("Completion %")
            self.completion_ax.set_ylim(0, 100)
            
            # Rotate x-axis labels for better readability
            plt.setp(self.completion_ax.get_xticklabels(), rotation=45, ha='right')
            
            self.completion_ax.tight_layout()
            self.completion_canvas.draw()
            
        except Exception as e:
            logger.error(f"Error updating completion chart: {e}")
    
    def _refresh_suggestions(self):
        """Refresh the suggestions list."""
        try:
            # Clear existing items
            for item in self.suggestions_tree.get_children():
                self.suggestions_tree.delete(item)
            
            # Update current location
            planet = self.planet_var.get()
            city = self.city_var.get()
            self.current_location = (planet, city) if planet and city else None
            
            # Get suggestions
            suggestions = get_smart_suggestions(self.current_location, max_suggestions=10)
            
            # Add suggestions to treeview
            for suggestion in suggestions:
                goal = self.tracker.goals.get(suggestion.goal_id)
                if goal:
                    priority_icon = {
                        GoalPriority.LOW: "🟢",
                        GoalPriority.MEDIUM: "🟡",
                        GoalPriority.HIGH: "🟠",
                        GoalPriority.CRITICAL: "🔴"
                    }.get(goal.priority, "⚪")
                    
                    location_text = f"{goal.location.planet}/{goal.location.city}" if goal.location else "Unknown"
                    
                    self.suggestions_tree.insert("", "end", values=(
                        f"{priority_icon} {goal.priority.value.title()}",
                        goal.title,
                        suggestion.reason,
                        f"{goal.estimated_time}min" if goal.estimated_time else "Unknown",
                        location_text
                    ))
            
            logger.info(f"Refreshed {len(suggestions)} suggestions")
            
        except Exception as e:
            logger.error(f"Error refreshing suggestions: {e}")
    
    def _refresh_goals_list(self):
        """Refresh the goals list."""
        try:
            # Clear existing items
            for item in self.goals_tree.get_children():
                self.goals_tree.delete(item)
            
            # Get filtered goals
            goals = self._get_filtered_goals()
            
            # Add goals to treeview
            for goal in goals:
                status_icon = {
                    GoalStatus.NOT_STARTED: "⚪",
                    GoalStatus.IN_PROGRESS: "🟡",
                    GoalStatus.COMPLETED: "🟢",
                    GoalStatus.FAILED: "🔴",
                    GoalStatus.ABANDONED: "⚫",
                    GoalStatus.LOCKED: "🔒"
                }.get(goal.status, "❓")
                
                priority_icon = {
                    GoalPriority.LOW: "🟢",
                    GoalPriority.MEDIUM: "🟡",
                    GoalPriority.HIGH: "🟠",
                    GoalPriority.CRITICAL: "🔴"
                }.get(goal.priority, "⚪")
                
                progress_text = f"{goal.progress_current}/{goal.progress_total} ({goal.progress_percentage:.1f}%)"
                location_text = f"{goal.location.planet}/{goal.location.city}" if goal.location else "Unknown"
                
                self.goals_tree.insert("", "end", values=(
                    f"{status_icon} {goal.status.value.replace('_', ' ').title()}",
                    f"{priority_icon} {goal.priority.value.title()}",
                    goal.title,
                    goal.category.value.replace('_', ' ').title(),
                    progress_text,
                    location_text
                ))
            
            logger.info(f"Refreshed {len(goals)} goals")
            
        except Exception as e:
            logger.error(f"Error refreshing goals list: {e}")
    
    def _get_filtered_goals(self) -> List[SmartGoal]:
        """Get goals filtered by current filter settings."""
        goals = list(self.tracker.goals.values())
        
        # Apply status filter
        status_filter = self.status_filter_var.get()
        if status_filter != "all":
            goals = [g for g in goals if g.status.value == status_filter]
        
        # Apply category filter
        category_filter = self.category_filter_var.get()
        if category_filter != "all":
            goals = [g for g in goals if g.category.value == category_filter]
        
        # Apply priority filter
        priority_filter = self.priority_filter_var.get()
        if priority_filter != "all":
            goals = [g for g in goals if g.priority.value == priority_filter]
        
        # Apply search filter
        search_query = self.search_var.get().lower()
        if search_query:
            goals = [g for g in goals if 
                    search_query in g.title.lower() or
                    (g.description and search_query in g.description.lower()) or
                    any(search_query in tag.lower() for tag in g.tags)]
        
        return goals
    
    def _update_analytics(self):
        """Update the analytics charts."""
        try:
            # Clear all subplots
            for ax in [self.pie_ax, self.bar_ax, self.timeline_ax, self.radar_ax]:
                ax.clear()
            
            stats = get_statistics()
            
            # Pie chart - Status distribution
            status_counts = {
                'Completed': stats['completed_goals'],
                'In Progress': stats['in_progress_goals'],
                'Not Started': stats['not_started_goals']
            }
            
            if any(status_counts.values()):
                self.pie_ax.pie(status_counts.values(), labels=status_counts.keys(), autopct='%1.1f%%')
                self.pie_ax.set_title("Goal Status Distribution")
            
            # Bar chart - Category completion
            category_stats = stats.get('category_stats', {})
            if category_stats:
                categories = list(category_stats.keys())
                completed = [category_stats[cat]['completed'] for cat in categories]
                total = [category_stats[cat]['total'] for cat in categories]
                
                x = np.arange(len(categories))
                width = 0.35
                
                self.bar_ax.bar(x - width/2, completed, width, label='Completed', color='green', alpha=0.7)
                self.bar_ax.bar(x + width/2, total, width, label='Total', color='lightblue', alpha=0.7)
                
                self.bar_ax.set_xlabel('Categories')
                self.bar_ax.set_ylabel('Number of Goals')
                self.bar_ax.set_title('Goals by Category')
                self.bar_ax.set_xticks(x)
                self.bar_ax.set_xticklabels([cat.replace('_', ' ').title() for cat in categories], rotation=45)
                self.bar_ax.legend()
            
            # Timeline chart - Recent activity
            recent_goals = [g for g in self.tracker.goals.values() 
                           if g.last_updated > datetime.now() - timedelta(days=7)]
            
            if recent_goals:
                dates = [g.last_updated.date() for g in recent_goals]
                statuses = [g.status.value for g in recent_goals]
                
                # Count goals by date and status
                date_status_counts = {}
                for date, status in zip(dates, statuses):
                    if date not in date_status_counts:
                        date_status_counts[date] = {}
                    date_status_counts[date][status] = date_status_counts[date].get(status, 0) + 1
                
                if date_status_counts:
                    dates_list = sorted(date_status_counts.keys())
                    completed_counts = [date_status_counts[date].get('completed', 0) for date in dates_list]
                    in_progress_counts = [date_status_counts[date].get('in_progress', 0) for date in dates_list]
                    
                    self.timeline_ax.plot(dates_list, completed_counts, 'o-', label='Completed', color='green')
                    self.timeline_ax.plot(dates_list, in_progress_counts, 's-', label='In Progress', color='orange')
                    self.timeline_ax.set_title('Recent Activity (Last 7 Days)')
                    self.timeline_ax.set_xlabel('Date')
                    self.timeline_ax.set_ylabel('Number of Goals')
                    self.timeline_ax.legend()
                    self.timeline_ax.tick_params(axis='x', rotation=45)
            
            # Radar chart - Priority distribution
            priority_stats = stats.get('priority_stats', {})
            if priority_stats:
                priorities = list(priority_stats.keys())
                completed = [priority_stats[pri]['completed'] for pri in priorities]
                total = [priority_stats[pri]['total'] for pri in priorities]
                
                # Calculate completion percentages
                completion_percentages = [(comp/tot*100) if tot > 0 else 0 
                                       for comp, tot in zip(completed, total)]
                
                angles = np.linspace(0, 2 * np.pi, len(priorities), endpoint=False).tolist()
                angles += angles[:1]  # Close the loop
                completion_percentages += completion_percentages[:1]
                
                self.radar_ax.plot(angles, completion_percentages, 'o-', linewidth=2)
                self.radar_ax.fill(angles, completion_percentages, alpha=0.25)
                self.radar_ax.set_xticks(angles[:-1])
                self.radar_ax.set_xticklabels([pri.title() for pri in priorities])
                self.radar_ax.set_ylim(0, 100)
                self.radar_ax.set_title('Completion by Priority')
                self.radar_ax.grid(True)
            
            self.analytics_figure.tight_layout()
            self.analytics_canvas.draw()
            
        except Exception as e:
            logger.error(f"Error updating analytics: {e}")
    
    def _apply_filters(self):
        """Apply the current filters to the goals list."""
        self._refresh_goals_list()
    
    def _start_selected_goal(self):
        """Start the selected goal from suggestions."""
        selection = self.suggestions_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a goal to start.")
            return
        
        # Get the selected item
        item = self.suggestions_tree.item(selection[0])
        goal_title = item['values'][1]  # Title is the second column
        
        # Find the goal
        goal = None
        for g in self.tracker.goals.values():
            if g.title == goal_title:
                goal = g
                break
        
        if goal:
            # Update goal status to in progress
            self.tracker.update_goal_progress(goal.id, 0, goal.progress_total)
            messagebox.showinfo("Goal Started", f"Started goal: {goal.title}")
            self._refresh_data()
        else:
            messagebox.showerror("Error", "Could not find the selected goal.")
    
    def _view_goal_details(self):
        """View details of the selected goal."""
        selection = self.suggestions_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a goal to view details.")
            return
        
        # Get the selected item
        item = self.suggestions_tree.item(selection[0])
        goal_title = item['values'][1]  # Title is the second column
        
        # Find the goal
        goal = None
        for g in self.tracker.goals.values():
            if g.title == goal_title:
                goal = g
                break
        
        if goal:
            self._show_goal_details_dialog(goal)
        else:
            messagebox.showerror("Error", "Could not find the selected goal.")
    
    def _show_goal_details_dialog(self, goal: SmartGoal):
        """Show a dialog with goal details."""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Goal Details: {goal.title}")
        dialog.geometry("600x400")
        
        # Create text widget for details
        text_widget = tk.Text(dialog, wrap=tk.WORD, padx=10, pady=10)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Format goal details
        details = f"""
Goal Details: {goal.title}
{'='*50}

ID: {goal.id}
Status: {goal.status.value.replace('_', ' ').title()}
Priority: {goal.priority.value.title()}
Category: {goal.category.value.replace('_', ' ').title()}

Description: {goal.description or 'No description'}

Progress: {goal.progress_current}/{goal.progress_total} ({goal.progress_percentage:.1f}%)

Location: {goal.location.planet}/{goal.location.city if goal.location else 'Unknown'}

Estimated Time: {goal.estimated_time} minutes
Difficulty: {goal.difficulty or 'Unknown'}

Rewards:
"""
        
        for reward in goal.rewards:
            details += f"  - {reward.description} ({reward.type})\n"
        
        if goal.prerequisites:
            details += "\nPrerequisites:\n"
            for prereq in goal.prerequisites:
                details += f"  - {prereq.description}\n"
        
        if goal.tags:
            details += f"\nTags: {', '.join(goal.tags)}\n"
        
        if goal.notes:
            details += f"\nNotes: {goal.notes}\n"
        
        text_widget.insert(tk.END, details)
        text_widget.config(state=tk.DISABLED)
    
    def _show_goal_path(self):
        """Show the path to complete the selected goal."""
        selection = self.suggestions_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a goal to show path.")
            return
        
        # Get the selected item
        item = self.suggestions_tree.item(selection[0])
        goal_title = item['values'][1]  # Title is the second column
        
        # Find the goal
        goal = None
        for g in self.tracker.goals.values():
            if g.title == goal_title:
                goal = g
                break
        
        if goal:
            path = self.tracker.get_goal_path(goal.id)
            if path:
                self._show_goal_path_dialog(path)
            else:
                messagebox.showinfo("Path", "No prerequisites found for this goal.")
        else:
            messagebox.showerror("Error", "Could not find the selected goal.")
    
    def _show_goal_path_dialog(self, path: List[SmartGoal]):
        """Show a dialog with the goal completion path."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Goal Completion Path")
        dialog.geometry("500x400")
        
        # Create treeview for path
        columns = ("Order", "Status", "Title", "Priority")
        path_tree = ttk.Treeview(dialog, columns=columns, show="headings", height=15)
        
        # Configure columns
        for col in columns:
            path_tree.heading(col, text=col)
            path_tree.column(col, width=100)
        
        # Add path items
        for i, goal in enumerate(path, 1):
            status_icon = {
                GoalStatus.NOT_STARTED: "⚪",
                GoalStatus.IN_PROGRESS: "🟡",
                GoalStatus.COMPLETED: "🟢",
                GoalStatus.FAILED: "🔴",
                GoalStatus.ABANDONED: "⚫",
                GoalStatus.LOCKED: "🔒"
            }.get(goal.status, "❓")
            
            priority_icon = {
                GoalPriority.LOW: "🟢",
                GoalPriority.MEDIUM: "🟡",
                GoalPriority.HIGH: "🟠",
                GoalPriority.CRITICAL: "🔴"
            }.get(goal.priority, "⚪")
            
            path_tree.insert("", "end", values=(
                i,
                f"{status_icon} {goal.status.value.replace('_', ' ').title()}",
                goal.title,
                f"{priority_icon} {goal.priority.value.title()}"
            ))
        
        path_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def _complete_selected_goal(self):
        """Complete the selected goal."""
        selection = self.goals_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a goal to complete.")
            return
        
        # Get the selected item
        item = self.goals_tree.item(selection[0])
        goal_title = item['values'][2]  # Title is the third column
        
        # Find the goal
        goal = None
        for g in self.tracker.goals.values():
            if g.title == goal_title:
                goal = g
                break
        
        if goal:
            if messagebox.askyesno("Complete Goal", f"Are you sure you want to complete '{goal.title}'?"):
                self.tracker.complete_goal(goal.id)
                messagebox.showinfo("Goal Completed", f"Completed goal: {goal.title}")
                self._refresh_data()
        else:
            messagebox.showerror("Error", "Could not find the selected goal.")
    
    def _add_goal_dialog(self):
        """Show dialog to add a new goal."""
        # This would be a comprehensive dialog for adding goals
        # For now, just show a message
        messagebox.showinfo("Add Goal", "Goal addition dialog would be implemented here.")
    
    def _edit_goal_dialog(self):
        """Show dialog to edit the selected goal."""
        selection = self.goals_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a goal to edit.")
            return
        
        messagebox.showinfo("Edit Goal", "Goal editing dialog would be implemented here.")
    
    def _delete_selected_goal(self):
        """Delete the selected goal."""
        selection = self.goals_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a goal to delete.")
            return
        
        # Get the selected item
        item = self.goals_tree.item(selection[0])
        goal_title = item['values'][2]  # Title is the third column
        
        # Find the goal
        goal = None
        for g in self.tracker.goals.values():
            if g.title == goal_title:
                goal = g
                break
        
        if goal:
            if messagebox.askyesno("Delete Goal", f"Are you sure you want to delete '{goal.title}'?"):
                del self.tracker.goals[goal.id]
                self.tracker._save_goals()
                self.tracker._update_completion_scores()
                messagebox.showinfo("Goal Deleted", f"Deleted goal: {goal.title}")
                self._refresh_data()
        else:
            messagebox.showerror("Error", "Could not find the selected goal.")
    
    def _export_data(self):
        """Export data to JSON file."""
        try:
            filename = f"smart_goals_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            data = {
                'goals': [goal.to_dict() for goal in self.tracker.goals.values()],
                'statistics': get_statistics(),
                'completion_scores': {cat: score.completion_percentage 
                                    for cat, score in get_completion_scores().items()},
                'export_date': datetime.now().isoformat()
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            messagebox.showinfo("Export Successful", f"Data exported to {filename}")
            
        except Exception as e:
            logger.error(f"Error exporting data: {e}")
            messagebox.showerror("Export Error", f"Failed to export data: {e}")
    
    def _import_data(self):
        """Import data from JSON file."""
        try:
            from tkinter import filedialog
            filename = filedialog.askopenfilename(
                title="Select file to import",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if filename:
                with open(filename, 'r') as f:
                    data = json.load(f)
                
                # Import goals
                if 'goals' in data:
                    for goal_data in data['goals']:
                        goal = SmartGoal.from_dict(goal_data)
                        self.tracker.goals[goal.id] = goal
                    
                    self.tracker._save_goals()
                    self.tracker._update_completion_scores()
                    self._refresh_data()
                    
                    messagebox.showinfo("Import Successful", f"Imported {len(data['goals'])} goals")
                
        except Exception as e:
            logger.error(f"Error importing data: {e}")
            messagebox.showerror("Import Error", f"Failed to import data: {e}")
    
    def _clear_data(self):
        """Clear all data."""
        if messagebox.askyesno("Clear Data", "Are you sure you want to clear all data? This cannot be undone."):
            self.tracker.goals.clear()
            self.tracker._save_goals()
            self.tracker._update_completion_scores()
            self._refresh_data()
            messagebox.showinfo("Data Cleared", "All data has been cleared.")
    
    def run(self):
        """Run the dashboard."""
        # Schedule auto-refresh if enabled
        if self.auto_refresh_var.get():
            interval = int(self.refresh_interval_var.get()) * 1000  # Convert to milliseconds
            self.root.after(interval, self._auto_refresh)
        
        self.root.mainloop()
    
    def _auto_refresh(self):
        """Auto-refresh the dashboard data."""
        if self.auto_refresh_var.get():
            self._refresh_data()
            interval = int(self.refresh_interval_var.get()) * 1000
            self.root.after(interval, self._auto_refresh)


def run_dashboard():
    """Run the progress dashboard."""
    dashboard = ProgressDashboard()
    dashboard.run()


if __name__ == "__main__":
    run_dashboard() 