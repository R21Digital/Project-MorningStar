"""
Quest Overlay UI System

This module provides a UI overlay for displaying detected quests and NPCs offering quests.
"""

import json
import logging
import time
from datetime import datetime
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


class OverlayPosition(Enum):
    """Overlay position enumeration."""
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    CENTER = "center"


@dataclass
class QuestOverlayItem:
    """Represents a quest item in the overlay."""
    quest_id: str
    name: str
    npc_name: str
    quest_type: str
    difficulty: str
    confidence: float
    distance: float
    detected_at: datetime
    is_highlighted: bool = False


@dataclass
class OverlayConfig:
    """Configuration for the quest overlay."""
    position: OverlayPosition = OverlayPosition.TOP_RIGHT
    width: int = 300
    height: int = 400
    opacity: float = 0.9
    auto_hide: bool = True
    auto_hide_delay: int = 10  # seconds
    max_items: int = 10
    show_confidence: bool = True
    show_distance: bool = True
    highlight_threshold: float = 0.7


class QuestOverlay:
    """
    UI overlay for displaying detected quests.
    """
    
    def __init__(self, config: OverlayConfig = None):
        """
        Initialize the quest overlay.
        
        Parameters
        ----------
        config : OverlayConfig, optional
            Overlay configuration
        """
        self.config = config or OverlayConfig()
        self.logger = self._setup_logging()
        
        # Overlay state
        self.is_visible = False
        self.current_items: List[QuestOverlayItem] = []
        self.last_update = 0.0
        self.auto_hide_timer = 0.0
        
        # UI components
        self.root: Optional[tk.Tk] = None
        self.canvas: Optional[tk.Canvas] = None
        self.frame: Optional[tk.Frame] = None
        
        # Initialize UI if tkinter is available
        if TKINTER_AVAILABLE:
            self._setup_ui()
        else:
            self.logger.warning("Tkinter not available, overlay will be disabled")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the overlay."""
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
            # Create root window
            self.root = tk.Tk()
            self.root.title("Quest Scanner Overlay")
            self.root.geometry(f"{self.config.width}x{self.config.height}")
            
            # Set window properties
            self.root.attributes('-topmost', True)
            self.root.attributes('-alpha', self.config.opacity)
            self.root.overrideredirect(True)  # Remove window decorations
            
            # Position window
            self._position_window()
            
            # Create main frame
            self.frame = tk.Frame(self.root, bg='black', relief='raised', bd=2)
            self.frame.pack(fill='both', expand=True)
            
            # Create title
            title_label = tk.Label(
                self.frame, 
                text="Quest Scanner", 
                bg='black', 
                fg='white',
                font=('Arial', 12, 'bold')
            )
            title_label.pack(pady=5)
            
            # Create canvas for quest items
            self.canvas = tk.Canvas(
                self.frame,
                bg='black',
                highlightthickness=0,
                width=self.config.width - 20,
                height=self.config.height - 60
            )
            self.canvas.pack(padx=10, pady=5)
            
            # Create scrollbar
            scrollbar = tk.Scrollbar(self.frame, orient="vertical", command=self.canvas.yview)
            scrollbar.pack(side="right", fill="y")
            self.canvas.configure(yscrollcommand=scrollbar.set)
            
            # Create scrollable frame
            self.scrollable_frame = tk.Frame(self.canvas, bg='black')
            self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
            
            # Bind events
            self.scrollable_frame.bind(
                "<Configure>",
                lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            )
            
            # Hide initially
            self.root.withdraw()
            
        except Exception as e:
            self.logger.error(f"Failed to setup UI: {e}")
            self.root = None
    
    def _position_window(self):
        """Position the window based on configuration."""
        if not self.root:
            return
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate position
        if self.config.position == OverlayPosition.TOP_LEFT:
            x, y = 0, 0
        elif self.config.position == OverlayPosition.TOP_RIGHT:
            x, y = screen_width - self.config.width, 0
        elif self.config.position == OverlayPosition.BOTTOM_LEFT:
            x, y = 0, screen_height - self.config.height
        elif self.config.position == OverlayPosition.BOTTOM_RIGHT:
            x, y = screen_width - self.config.width, screen_height - self.config.height
        else:  # CENTER
            x = (screen_width - self.config.width) // 2
            y = (screen_height - self.config.height) // 2
        
        self.root.geometry(f"{self.config.width}x{self.config.height}+{x}+{y}")
    
    def update_quests(self, quest_detections: List[Any], current_location: Tuple[int, int] = None):
        """
        Update the overlay with new quest detections.
        
        Parameters
        ----------
        quest_detections : List[Any]
            List of quest detection objects
        current_location : Tuple[int, int], optional
            Current player location for distance calculation
        """
        if not self.root:
            return
        
        self.current_items = []
        
        # Convert detections to overlay items
        for detection in quest_detections[:self.config.max_items]:
            distance = 0.0
            if current_location and hasattr(detection.location, 'coordinates'):
                distance = detection.location.distance_to(current_location)
            
            item = QuestOverlayItem(
                quest_id=detection.quest_id,
                name=detection.location.name,
                npc_name=detection.location.npc_name,
                quest_type=detection.location.quest_type.value,
                difficulty=detection.location.difficulty.value,
                confidence=detection.confidence,
                distance=distance,
                detected_at=detection.detected_at,
                is_highlighted=detection.confidence >= self.config.highlight_threshold
            )
            self.current_items.append(item)
        
        # Update UI
        self._update_ui()
        
        # Show overlay
        self.show()
    
    def _update_ui(self):
        """Update the UI with current quest items."""
        if not self.root or not self.scrollable_frame:
            return
        
        # Clear existing items
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Create quest item widgets
        for item in self.current_items:
            self._create_quest_item_widget(item)
        
        # Update scroll region
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _create_quest_item_widget(self, item: QuestOverlayItem):
        """Create a widget for a quest item."""
        # Create item frame
        item_frame = tk.Frame(self.scrollable_frame, bg='black', relief='solid', bd=1)
        item_frame.pack(fill='x', padx=5, pady=2)
        
        # Set background color based on highlight
        bg_color = '#2a2a2a' if item.is_highlighted else '#1a1a1a'
        item_frame.configure(bg=bg_color)
        
        # Quest name
        name_label = tk.Label(
            item_frame,
            text=item.name,
            bg=bg_color,
            fg='white',
            font=('Arial', 10, 'bold'),
            anchor='w'
        )
        name_label.pack(fill='x', padx=5, pady=2)
        
        # NPC name
        npc_label = tk.Label(
            item_frame,
            text=f"NPC: {item.npc_name}",
            bg=bg_color,
            fg='#cccccc',
            font=('Arial', 8),
            anchor='w'
        )
        npc_label.pack(fill='x', padx=5)
        
        # Quest details
        details_text = f"Type: {item.quest_type} | Difficulty: {item.difficulty}"
        
        if self.config.show_confidence:
            details_text += f" | Confidence: {item.confidence:.2f}"
        
        if self.config.show_distance and item.distance > 0:
            details_text += f" | Distance: {item.distance:.0f}m"
        
        details_label = tk.Label(
            item_frame,
            text=details_text,
            bg=bg_color,
            fg='#888888',
            font=('Arial', 7),
            anchor='w'
        )
        details_label.pack(fill='x', padx=5, pady=2)
    
    def show(self):
        """Show the overlay."""
        if self.root and not self.is_visible:
            self.root.deiconify()
            self.is_visible = True
            self.last_update = time.time()
            self.logger.info("Quest overlay shown")
    
    def hide(self):
        """Hide the overlay."""
        if self.root and self.is_visible:
            self.root.withdraw()
            self.is_visible = False
            self.logger.info("Quest overlay hidden")
    
    def toggle(self):
        """Toggle overlay visibility."""
        if self.is_visible:
            self.hide()
        else:
            self.show()
    
    def update_auto_hide(self):
        """Update auto-hide timer."""
        if self.config.auto_hide and self.is_visible:
            current_time = time.time()
            if current_time - self.last_update > self.config.auto_hide_delay:
                self.hide()
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get overlay status.
        
        Returns
        -------
        Dict[str, Any]
            Overlay status information
        """
        return {
            "visible": self.is_visible,
            "items_count": len(self.current_items),
            "tkinter_available": TKINTER_AVAILABLE,
            "root_available": self.root is not None,
            "last_update": self.last_update,
            "config": {
                "position": self.config.position.value,
                "width": self.config.width,
                "height": self.config.height,
                "opacity": self.config.opacity,
                "auto_hide": self.config.auto_hide,
                "max_items": self.config.max_items
            }
        }


# Global overlay instance
_overlay_instance: Optional[QuestOverlay] = None


def get_quest_overlay() -> QuestOverlay:
    """Get the global quest overlay instance."""
    global _overlay_instance
    if _overlay_instance is None:
        config = OverlayConfig()
        _overlay_instance = QuestOverlay(config)
    return _overlay_instance


def update_quest_overlay(quest_detections: List[Any], current_location: Tuple[int, int] = None):
    """Update the quest overlay with new detections."""
    overlay = get_quest_overlay()
    overlay.update_quests(quest_detections, current_location)


def show_quest_overlay():
    """Show the quest overlay."""
    overlay = get_quest_overlay()
    overlay.show()


def hide_quest_overlay():
    """Hide the quest overlay."""
    overlay = get_quest_overlay()
    overlay.hide()


def toggle_quest_overlay():
    """Toggle the quest overlay."""
    overlay = get_quest_overlay()
    overlay.toggle()


def get_overlay_status() -> Dict[str, Any]:
    """Get overlay status."""
    overlay = get_quest_overlay()
    return overlay.get_status() 