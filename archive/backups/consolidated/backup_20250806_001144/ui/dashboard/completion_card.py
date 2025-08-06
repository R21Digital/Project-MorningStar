"""
Completion Card UI Component

This module provides a visual completion card component for the dashboard that displays
progress tracking, roadmap information, and completion statistics in an attractive format.
"""

import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

try:
    import tkinter as tk
    from tkinter import ttk
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False


class CardType(Enum):
    """Types of completion cards."""
    PLANET_PROGRESS = "planet_progress"
    ROADMAP = "roadmap"
    OBJECTIVE_DETAIL = "objective_detail"
    COMPLETION_SUMMARY = "completion_summary"


class ProgressBarStyle(Enum):
    """Progress bar styling options."""
    LINEAR = "linear"
    CIRCULAR = "circular"
    GRADIENT = "gradient"


@dataclass
class CompletionCardConfig:
    """Configuration for completion cards."""
    width: int = 400
    height: int = 300
    background_color: str = "#2a2a2a"
    text_color: str = "#ffffff"
    accent_color: str = "#4CAF50"
    warning_color: str = "#FF9800"
    error_color: str = "#F44336"
    progress_bar_style: ProgressBarStyle = ProgressBarStyle.LINEAR
    show_percentages: bool = True
    show_estimated_time: bool = True
    show_rewards: bool = True
    auto_refresh_interval: int = 30  # seconds


@dataclass
class PlanetProgressCard:
    """Represents a planet progress card."""
    planet: str
    total_objectives: int
    completed_objectives: int
    completion_percentage: float
    objectives_by_type: Dict[str, int]
    estimated_time_remaining: Optional[int]
    last_updated: datetime
    is_current_planet: bool = False


@dataclass
class RoadmapCard:
    """Represents a roadmap card."""
    current_planet: str
    prioritized_objectives: List[Dict[str, Any]]
    session_completed: int
    session_time: int
    next_objective: Optional[Dict[str, Any]] = None


@dataclass
class ObjectiveDetailCard:
    """Represents an objective detail card."""
    objective_id: str
    name: str
    completion_type: str
    planet: str
    zone: Optional[str]
    status: str
    priority: str
    progress_percentage: float
    estimated_time: Optional[int]
    rewards: List[str]
    description: Optional[str]
    tags: List[str]


class CompletionCard:
    """
    Base completion card component for the dashboard.
    
    Features:
    - Visual progress tracking
    - Interactive elements
    - Auto-refresh functionality
    - Responsive design
    """
    
    def __init__(self, config: CompletionCardConfig = None):
        """
        Initialize the completion card.
        
        Parameters
        ----------
        config : CompletionCardConfig, optional
            Card configuration
        """
        self.config = config or CompletionCardConfig()
        self.logger = self._setup_logging()
        
        # Card state
        self.is_visible = False
        self.last_update = 0.0
        self.refresh_timer = None
        
        # UI components
        self.frame: Optional[tk.Frame] = None
        self.canvas: Optional[tk.Canvas] = None
        self.title_label: Optional[tk.Label] = None
        self.content_frame: Optional[tk.Frame] = None
        
        # Initialize UI if tkinter is available
        if TKINTER_AVAILABLE:
            self._setup_ui()
        else:
            self.logger.warning("Tkinter not available, card will be disabled")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the completion card."""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger
    
    def _setup_ui(self):
        """Setup the UI components."""
        try:
            # Create main frame
            self.frame = tk.Frame(
                bg=self.config.background_color,
                relief='raised',
                bd=2
            )
            
            # Create title
            self.title_label = tk.Label(
                self.frame,
                text="Completion Tracker",
                bg=self.config.background_color,
                fg=self.config.text_color,
                font=('Arial', 14, 'bold')
            )
            self.title_label.pack(pady=10)
            
            # Create content frame
            self.content_frame = tk.Frame(
                self.frame,
                bg=self.config.background_color
            )
            self.content_frame.pack(fill='both', expand=True, padx=10, pady=5)
            
            # Create canvas for custom drawing
            self.canvas = tk.Canvas(
                self.content_frame,
                bg=self.config.background_color,
                highlightthickness=0,
                width=self.config.width - 40,
                height=self.config.height - 80
            )
            self.canvas.pack(fill='both', expand=True)
            
        except Exception as e:
            self.logger.error(f"Failed to setup UI: {e}")
            self.frame = None
    
    def update_planet_progress(self, planet_progress: PlanetProgressCard):
        """Update the card with planet progress data."""
        if not self.frame:
            return
        
        # Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Update title
        title_text = f"{planet_progress.planet} Progress"
        if planet_progress.is_current_planet:
            title_text += " (Current)"
        self.title_label.config(text=title_text)
        
        # Create progress display
        self._create_progress_display(planet_progress)
        
        # Create objectives breakdown
        self._create_objectives_breakdown(planet_progress)
        
        # Create time estimate
        if self.config.show_estimated_time and planet_progress.estimated_time_remaining:
            self._create_time_estimate(planet_progress)
        
        self.last_update = time.time()
        self.logger.info(f"Updated planet progress card for {planet_progress.planet}")
    
    def update_roadmap(self, roadmap: RoadmapCard):
        """Update the card with roadmap data."""
        if not self.frame:
            return
        
        # Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Update title
        self.title_label.config(text=f"{roadmap.current_planet} Roadmap")
        
        # Create roadmap display
        self._create_roadmap_display(roadmap)
        
        # Create session info
        self._create_session_info(roadmap)
        
        # Create next objective
        if roadmap.next_objective:
            self._create_next_objective(roadmap.next_objective)
        
        self.last_update = time.time()
        self.logger.info(f"Updated roadmap card for {roadmap.current_planet}")
    
    def update_objective_detail(self, objective: ObjectiveDetailCard):
        """Update the card with objective detail data."""
        if not self.frame:
            return
        
        # Clear existing content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Update title
        self.title_label.config(text=f"Objective: {objective.name}")
        
        # Create objective details
        self._create_objective_details(objective)
        
        # Create progress bar
        self._create_progress_bar(objective.progress_percentage)
        
        # Create rewards display
        if self.config.show_rewards and objective.rewards:
            self._create_rewards_display(objective.rewards)
        
        self.last_update = time.time()
        self.logger.info(f"Updated objective detail card for {objective.name}")
    
    def _create_progress_display(self, planet_progress: PlanetProgressCard):
        """Create progress display for planet progress."""
        # Main progress frame
        progress_frame = tk.Frame(self.content_frame, bg=self.config.background_color)
        progress_frame.pack(fill='x', pady=5)
        
        # Progress text
        progress_text = f"{planet_progress.completed_objectives}/{planet_progress.total_objectives}"
        if self.config.show_percentages:
            progress_text += f" ({planet_progress.completion_percentage:.1f}%)"
        
        progress_label = tk.Label(
            progress_frame,
            text=progress_text,
            bg=self.config.background_color,
            fg=self.config.text_color,
            font=('Arial', 16, 'bold')
        )
        progress_label.pack()
        
        # Progress bar
        self._create_progress_bar(planet_progress.completion_percentage)
    
    def _create_objectives_breakdown(self, planet_progress: PlanetProgressCard):
        """Create objectives breakdown display."""
        breakdown_frame = tk.Frame(self.content_frame, bg=self.config.background_color)
        breakdown_frame.pack(fill='x', pady=5)
        
        # Breakdown title
        breakdown_title = tk.Label(
            breakdown_frame,
            text="Objectives by Type:",
            bg=self.config.background_color,
            fg=self.config.text_color,
            font=('Arial', 10, 'bold')
        )
        breakdown_title.pack(anchor='w')
        
        # Create breakdown items
        for obj_type, count in planet_progress.objectives_by_type.items():
            type_frame = tk.Frame(breakdown_frame, bg=self.config.background_color)
            type_frame.pack(fill='x', pady=1)
            
            type_label = tk.Label(
                type_frame,
                text=f"{obj_type.title()}: {count}",
                bg=self.config.background_color,
                fg=self.config.text_color,
                font=('Arial', 9)
            )
            type_label.pack(side='left')
    
    def _create_time_estimate(self, planet_progress: PlanetProgressCard):
        """Create time estimate display."""
        if not planet_progress.estimated_time_remaining:
            return
        
        time_frame = tk.Frame(self.content_frame, bg=self.config.background_color)
        time_frame.pack(fill='x', pady=5)
        
        # Convert minutes to hours and minutes
        hours = planet_progress.estimated_time_remaining // 60
        minutes = planet_progress.estimated_time_remaining % 60
        
        if hours > 0:
            time_text = f"Estimated time remaining: {hours}h {minutes}m"
        else:
            time_text = f"Estimated time remaining: {minutes}m"
        
        time_label = tk.Label(
            time_frame,
            text=time_text,
            bg=self.config.background_color,
            fg=self.config.warning_color,
            font=('Arial', 9)
        )
        time_label.pack()
    
    def _create_roadmap_display(self, roadmap: RoadmapCard):
        """Create roadmap display."""
        roadmap_frame = tk.Frame(self.content_frame, bg=self.config.background_color)
        roadmap_frame.pack(fill='both', expand=True, pady=5)
        
        # Roadmap title
        roadmap_title = tk.Label(
            roadmap_frame,
            text="Prioritized Objectives:",
            bg=self.config.background_color,
            fg=self.config.text_color,
            font=('Arial', 10, 'bold')
        )
        roadmap_title.pack(anchor='w')
        
        # Create scrollable frame for objectives
        canvas = tk.Canvas(roadmap_frame, bg=self.config.background_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(roadmap_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.config.background_color)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add objectives to scrollable frame
        for i, objective in enumerate(roadmap.prioritized_objectives[:5]):  # Show top 5
            obj_frame = tk.Frame(scrollable_frame, bg=self.config.background_color, relief='solid', bd=1)
            obj_frame.pack(fill='x', pady=2, padx=5)
            
            # Objective name
            name_label = tk.Label(
                obj_frame,
                text=f"{i+1}. {objective.get('name', 'Unknown')}",
                bg=self.config.background_color,
                fg=self.config.text_color,
                font=('Arial', 9, 'bold'),
                anchor='w'
            )
            name_label.pack(fill='x', padx=5, pady=2)
            
            # Objective details
            details_text = f"Type: {objective.get('completion_type', 'Unknown')} | Priority: {objective.get('priority', 'Unknown')}"
            details_label = tk.Label(
                obj_frame,
                text=details_text,
                bg=self.config.background_color,
                fg=self.config.text_color,
                font=('Arial', 8),
                anchor='w'
            )
            details_label.pack(fill='x', padx=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _create_session_info(self, roadmap: RoadmapCard):
        """Create session information display."""
        session_frame = tk.Frame(self.content_frame, bg=self.config.background_color)
        session_frame.pack(fill='x', pady=5)
        
        # Session stats
        session_text = f"Session: {roadmap.session_completed} completed | {roadmap.session_time} minutes"
        session_label = tk.Label(
            session_frame,
            text=session_text,
            bg=self.config.background_color,
            fg=self.config.accent_color,
            font=('Arial', 9)
        )
        session_label.pack()
    
    def _create_next_objective(self, next_objective: Dict[str, Any]):
        """Create next objective display."""
        next_frame = tk.Frame(self.content_frame, bg=self.config.background_color)
        next_frame.pack(fill='x', pady=5)
        
        # Next objective title
        next_title = tk.Label(
            next_frame,
            text="Next Objective:",
            bg=self.config.background_color,
            fg=self.config.text_color,
            font=('Arial', 10, 'bold')
        )
        next_title.pack(anchor='w')
        
        # Next objective details
        next_name = tk.Label(
            next_frame,
            text=next_objective.get('name', 'Unknown'),
            bg=self.config.background_color,
            fg=self.config.accent_color,
            font=('Arial', 9, 'bold')
        )
        next_name.pack(anchor='w')
        
        next_details = tk.Label(
            next_frame,
            text=f"Type: {next_objective.get('completion_type', 'Unknown')} | Priority: {next_objective.get('priority', 'Unknown')}",
            bg=self.config.background_color,
            fg=self.config.text_color,
            font=('Arial', 8)
        )
        next_details.pack(anchor='w')
    
    def _create_objective_details(self, objective: ObjectiveDetailCard):
        """Create objective details display."""
        details_frame = tk.Frame(self.content_frame, bg=self.config.background_color)
        details_frame.pack(fill='x', pady=5)
        
        # Basic info
        info_text = f"Planet: {objective.planet}"
        if objective.zone:
            info_text += f" | Zone: {objective.zone}"
        info_text += f" | Type: {objective.completion_type}"
        info_text += f" | Priority: {objective.priority}"
        info_text += f" | Status: {objective.status}"
        
        info_label = tk.Label(
            details_frame,
            text=info_text,
            bg=self.config.background_color,
            fg=self.config.text_color,
            font=('Arial', 9)
        )
        info_label.pack(anchor='w')
        
        # Description
        if objective.description:
            desc_label = tk.Label(
                details_frame,
                text=f"Description: {objective.description}",
                bg=self.config.background_color,
                fg=self.config.text_color,
                font=('Arial', 8),
                wraplength=350
            )
            desc_label.pack(anchor='w', pady=2)
        
        # Tags
        if objective.tags:
            tags_text = f"Tags: {', '.join(objective.tags)}"
            tags_label = tk.Label(
                details_frame,
                text=tags_text,
                bg=self.config.background_color,
                fg=self.config.text_color,
                font=('Arial', 8)
            )
            tags_label.pack(anchor='w')
    
    def _create_progress_bar(self, percentage: float):
        """Create a progress bar."""
        if not self.canvas:
            return
        
        try:
            # Clear canvas
            self.canvas.delete("all")
            
            # Calculate dimensions
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                return
            
            # Progress bar dimensions
            bar_width = canvas_width - 20
            bar_height = 20
            bar_x = 10
            bar_y = (canvas_height - bar_height) // 2
            
            # Background bar
            self.canvas.create_rectangle(
                bar_x, bar_y, bar_x + bar_width, bar_y + bar_height,
                fill="#444444", outline="#666666"
            )
            
            # Progress bar
            progress_width = int((percentage / 100) * bar_width)
            if progress_width > 0:
                color = self.config.accent_color if percentage >= 100 else self.config.warning_color
                self.canvas.create_rectangle(
                    bar_x, bar_y, bar_x + progress_width, bar_y + bar_height,
                    fill=color, outline=color
                )
            
            # Percentage text
            if self.config.show_percentages:
                text_x = bar_x + bar_width // 2
                text_y = bar_y + bar_height // 2
                self.canvas.create_text(
                    text_x, text_y,
                    text=f"{percentage:.1f}%",
                    fill=self.config.text_color,
                    font=('Arial', 10, 'bold')
                )
        except Exception as e:
            # Handle tkinter errors gracefully
            self.logger.debug(f"Could not create progress bar: {e}")
            pass
    
    def _create_rewards_display(self, rewards: List[str]):
        """Create rewards display."""
        rewards_frame = tk.Frame(self.content_frame, bg=self.config.background_color)
        rewards_frame.pack(fill='x', pady=5)
        
        # Rewards title
        rewards_title = tk.Label(
            rewards_frame,
            text="Rewards:",
            bg=self.config.background_color,
            fg=self.config.text_color,
            font=('Arial', 10, 'bold')
        )
        rewards_title.pack(anchor='w')
        
        # Rewards list
        rewards_text = ", ".join(rewards)
        rewards_label = tk.Label(
            rewards_frame,
            text=rewards_text,
            bg=self.config.background_color,
            fg=self.config.accent_color,
            font=('Arial', 9),
            wraplength=350
        )
        rewards_label.pack(anchor='w')
    
    def show(self):
        """Show the completion card."""
        if self.frame:
            self.frame.pack(fill='both', expand=True)
            self.is_visible = True
            self.logger.info("Completion card shown")
    
    def hide(self):
        """Hide the completion card."""
        if self.frame:
            self.frame.pack_forget()
            self.is_visible = False
            self.logger.info("Completion card hidden")
    
    def get_frame(self) -> Optional[tk.Frame]:
        """Get the card frame."""
        return self.frame
    
    def get_status(self) -> Dict[str, Any]:
        """Get card status."""
        return {
            "visible": self.is_visible,
            "tkinter_available": TKINTER_AVAILABLE,
            "frame_available": self.frame is not None,
            "last_update": self.last_update,
            "config": {
                "width": self.config.width,
                "height": self.config.height,
                "show_percentages": self.config.show_percentages,
                "show_estimated_time": self.config.show_estimated_time,
                "show_rewards": self.config.show_rewards
            }
        }


# Global card instances
_planet_progress_card: Optional[CompletionCard] = None
_roadmap_card: Optional[CompletionCard] = None
_objective_detail_card: Optional[CompletionCard] = None


def get_planet_progress_card() -> CompletionCard:
    """Get the planet progress card instance."""
    global _planet_progress_card
    if _planet_progress_card is None:
        config = CompletionCardConfig()
        _planet_progress_card = CompletionCard(config)
    return _planet_progress_card


def get_roadmap_card() -> CompletionCard:
    """Get the roadmap card instance."""
    global _roadmap_card
    if _roadmap_card is None:
        config = CompletionCardConfig()
        _roadmap_card = CompletionCard(config)
    return _roadmap_card


def get_objective_detail_card() -> CompletionCard:
    """Get the objective detail card instance."""
    global _objective_detail_card
    if _objective_detail_card is None:
        config = CompletionCardConfig()
        _objective_detail_card = CompletionCard(config)
    return _objective_detail_card


def update_planet_progress_card(planet_progress: PlanetProgressCard):
    """Update the planet progress card."""
    card = get_planet_progress_card()
    card.update_planet_progress(planet_progress)


def update_roadmap_card(roadmap: RoadmapCard):
    """Update the roadmap card."""
    card = get_roadmap_card()
    card.update_roadmap(roadmap)


def update_objective_detail_card(objective: ObjectiveDetailCard):
    """Update the objective detail card."""
    card = get_objective_detail_card()
    card.update_objective_detail(objective)


def get_card_status() -> Dict[str, Any]:
    """Get status of all cards."""
    return {
        "planet_progress_card": get_planet_progress_card().get_status(),
        "roadmap_card": get_roadmap_card().get_status(),
        "objective_detail_card": get_objective_detail_card().get_status()
    } 