"""Track in-game credits using OCR and session management."""

import json
import os
import re
from datetime import datetime
from typing import Optional, Dict, Any

from src.vision.ocr import screen_text
from utils.logging_utils import log_event


class CreditTracker:
    """Track credit balance changes using OCR and session logging."""
    
    def __init__(self, session_id: str = None):
        """Initialize the credit tracker.
        
        Parameters
        ----------
        session_id : str, optional
            Session identifier for logging
        """
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.start_credits = 0
        self.current_credits = 0
        self.credit_history = []
        self.last_check = None
        
        # Credit detection patterns
        self.credit_patterns = [
            r'(\d{1,3}(?:,\d{3})*)\s*credits?',  # "1,234 credits"
            r'credits?:\s*(\d{1,3}(?:,\d{3})*)',  # "credits: 1,234"
            r'balance:\s*(\d{1,3}(?:,\d{3})*)',   # "balance: 1,234"
        ]
        
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)
    
    def detect_credits_via_ocr(self, screen_text: str) -> Optional[int]:
        """Extract credit amount from OCR text.
        
        Parameters
        ----------
        screen_text : str
            Raw OCR text from screen capture
            
        Returns
        -------
        int or None
            Detected credit amount, or None if not found
        """
        for pattern in self.credit_patterns:
            match = re.search(pattern, screen_text, re.IGNORECASE)
            if match:
                try:
                    # Remove commas and convert to int
                    credit_str = match.group(1).replace(',', '')
                    return int(credit_str)
                except (ValueError, AttributeError):
                    continue
        return None
    
    def capture_current_credits(self) -> Optional[int]:
        """Capture current credit balance from screen.
        
        Returns
        -------
        int or None
            Current credit balance, or None if detection failed
        """
        try:
            # Capture screen and extract text
            text = screen_text()
            credits = self.detect_credits_via_ocr(text)
            
            if credits is not None:
                self.current_credits = credits
                self.last_check = datetime.now()
                
                # Log the detection
                log_event(f"[CREDITS] Detected: {credits:,} credits")
                
                # Add to history
                self.credit_history.append({
                    "timestamp": self.last_check.isoformat(),
                    "credits": credits,
                    "source": "ocr"
                })
                
                return credits
            else:
                log_event("[CREDITS] No credit amount detected in screen text")
                return None
                
        except Exception as e:
            log_event(f"[CREDITS] Error capturing credits: {e}")
            return None
    
    def set_start_credits(self, credits: int) -> None:
        """Set the starting credit balance.
        
        Parameters
        ----------
        credits : int
            Starting credit amount
        """
        self.start_credits = credits
        self.current_credits = credits
        log_event(f"[CREDITS] Session start: {credits:,} credits")
    
    def get_credits_earned(self) -> int:
        """Calculate total credits earned this session.
        
        Returns
        -------
        int
            Credits earned (current - start)
        """
        return max(0, self.current_credits - self.start_credits)
    
    def save_session_log(self) -> None:
        """Save credit tracking session to log file."""
        log_data = {
            "session_id": self.session_id,
            "start_credits": self.start_credits,
            "end_credits": self.current_credits,
            "credits_earned": self.get_credits_earned(),
            "credit_history": self.credit_history,
            "session_duration": None,  # TODO: Calculate if session manager available
            "created_at": datetime.now().isoformat()
        }
        
        log_path = os.path.join("logs", f"credits_{self.session_id}.json")
        try:
            with open(log_path, "w", encoding="utf-8") as f:
                json.dump(log_data, f, indent=2)
            log_event(f"[CREDITS] Session log saved: {log_path}")
        except Exception as e:
            log_event(f"[CREDITS] Error saving log: {e}")


def track_credits() -> int:
    """Legacy function for backward compatibility.
    
    Returns
    -------
    int
        Current credit balance (0 if detection fails)
    """
    tracker = CreditTracker()
    credits = tracker.capture_current_credits()
    return credits or 0


# Global tracker instance for simple usage
_global_tracker = None


def get_credit_tracker() -> CreditTracker:
    """Get or create the global credit tracker instance.
    
    Returns
    -------
    CreditTracker
        Global tracker instance
    """
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = CreditTracker()
    return _global_tracker


def update_credits() -> Optional[int]:
    """Update and return current credit balance.
    
    Returns
    -------
    int or None
        Current credit balance, or None if detection failed
    """
    tracker = get_credit_tracker()
    return tracker.capture_current_credits()
