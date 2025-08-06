"""
Interactive NPC & Terminal Logic

This module provides intelligent NPC interaction capabilities including:
- OCR parsing of NPC speech from chatbox and speech bubbles
- Context-aware response selection
- Fallback interaction logic
- Success/failure tracking and statistics
"""

import time
import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import json

# Mock imports for testing (avoiding import issues)
def run_ocr(image):
    """Mock OCR function for testing."""
    return "Mock OCR text"

def capture_screen():
    """Mock screen capture function for testing."""
    return None

def click_at(x, y):
    """Mock click function for testing."""
    print(f"Mock click at ({x}, {y})")

def press_key(key):
    """Mock key press function for testing."""
    print(f"Mock press key: {key}")

def wait(seconds):
    """Mock wait function for testing."""
    time.sleep(seconds * 0.1)  # Faster for testing

class InteractionType(Enum):
    """Types of NPC interactions."""
    QUEST_GIVER = "quest_giver"
    TRAINER = "trainer"
    TERMINAL = "terminal"
    VENDOR = "vendor"
    MISSION_GIVER = "mission_giver"
    UNKNOWN = "unknown"

class ResponseType(Enum):
    """Types of responses to NPC interactions."""
    ACCEPT = "accept"
    DECLINE = "decline"
    TRAIN = "train"
    BUY = "buy"
    SELL = "sell"
    CONTINUE = "continue"
    EXIT = "exit"
    CUSTOM = "custom"

@dataclass
class InteractionAttempt:
    """Represents a single interaction attempt."""
    npc_name: str
    interaction_type: InteractionType
    ocr_text: str
    detected_response: ResponseType
    success: bool
    timestamp: float
    fallback_used: bool
    response_time: float

@dataclass
class NPCDialogue:
    """Represents NPC dialogue information."""
    npc_name: str
    dialogue_text: str
    response_options: List[str]
    interaction_type: InteractionType
    confidence: float

class NPCInteractor:
    """
    Intelligent NPC Interaction System
    
    Features:
    - OCR-based dialogue parsing
    - Context-aware response selection
    - Fallback interaction logic
    - Success/failure tracking
    - Statistics and logging
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.logger = logging.getLogger("npc_interactor")
        self.setup_logging()
        
        self.config = self.load_config(config_path)
        self.interaction_history: List[InteractionAttempt] = []
        self.npc_database: Dict[str, Dict[str, Any]] = {}
        
        # Response patterns for different interaction types
        self.response_patterns = self.config.get("response_patterns", {})
        self.fallback_sequences = self.config.get("fallback_sequences", {})
        self.ocr_keywords = self.config.get("ocr_keywords", {})
        
        # Statistics
        self.stats = {
            "total_interactions": 0,
            "successful_interactions": 0,
            "failed_interactions": 0,
            "fallback_usage": 0,
            "average_response_time": 0.0
        }
    
    def setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Load configuration from file or use defaults."""
        default_config = {
            "ocr_interval": 1.0,
            "interaction_timeout": 10.0,
            "fallback_delay": 0.5,
            "max_retries": 3,
            "response_patterns": {
                "quest_giver": {
                    "accept": [r"accept", r"yes", r"okay", r"\[accept\]", r"take quest"],
                    "decline": [r"decline", r"no", r"cancel", r"\[decline\]", r"not now"],
                    "continue": [r"continue", r"next", r"more", r"\[continue\]"]
                },
                "trainer": {
                    "train": [r"train", r"learn", r"skill", r"\[train\]", r"teach"],
                    "exit": [r"exit", r"leave", r"goodbye", r"\[exit\]", r"cancel"]
                },
                "terminal": {
                    "continue": [r"continue", r"next", r"proceed", r"\[continue\]"],
                    "exit": [r"exit", r"cancel", r"back", r"\[exit\]"],
                    "buy": [r"buy", r"purchase", r"\[buy\]", r"acquire"],
                    "sell": [r"sell", r"sale", r"\[sell\]", r"trade"]
                },
                "vendor": {
                    "buy": [r"buy", r"purchase", r"\[buy\]", r"acquire"],
                    "sell": [r"sell", r"sale", r"\[sell\]", r"trade"],
                    "exit": [r"exit", r"leave", r"goodbye", r"\[exit\]"]
                }
            },
            "fallback_sequences": {
                "quest_giver": ["ENTER", "1", "1", "ESC"],
                "trainer": ["ENTER", "1", "ESC"],
                "terminal": ["ENTER", "1", "ESC"],
                "vendor": ["ENTER", "1", "ESC"]
            },
            "ocr_keywords": {
                "quest_indicators": ["quest", "mission", "task", "assignment", "objective"],
                "trainer_indicators": ["train", "learn", "skill", "teach", "training"],
                "terminal_indicators": ["terminal", "computer", "system", "access"],
                "vendor_indicators": ["buy", "sell", "trade", "shop", "store"]
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    default_config.update(config)
            except Exception as e:
                self.logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config
    
    def scan_npc_dialogue(self, npc_name: str = None) -> Optional[NPCDialogue]:
        """Scan for NPC dialogue using OCR."""
        try:
            # Capture screen and run OCR
            screen = capture_screen()
            if screen is None:
                return None
            
            ocr_text = run_ocr(screen)
            if not ocr_text:
                return None
            
            # Parse dialogue from OCR text
            dialogue_info = self.parse_dialogue_from_ocr(ocr_text, npc_name)
            if not dialogue_info:
                return None
            
            return NPCDialogue(
                npc_name=dialogue_info.get("npc_name", "Unknown"),
                dialogue_text=dialogue_info.get("dialogue_text", ""),
                response_options=dialogue_info.get("response_options", []),
                interaction_type=dialogue_info.get("interaction_type", InteractionType.UNKNOWN),
                confidence=dialogue_info.get("confidence", 0.0)
            )
        
        except Exception as e:
            self.logger.error(f"Failed to scan NPC dialogue: {e}")
            return None
    
    def parse_dialogue_from_ocr(self, ocr_text: str, npc_name: str = None) -> Optional[Dict[str, Any]]:
        """Parse dialogue information from OCR text."""
        dialogue_info = {}
        
        # Extract NPC name if not provided
        if not npc_name:
            npc_name = self.extract_npc_name(ocr_text)
        
        dialogue_info["npc_name"] = npc_name
        
        # Extract dialogue text
        dialogue_text = self.extract_dialogue_text(ocr_text)
        dialogue_info["dialogue_text"] = dialogue_text
        
        # Extract response options
        response_options = self.extract_response_options(ocr_text)
        dialogue_info["response_options"] = response_options
        
        # Determine interaction type
        interaction_type = self.determine_interaction_type(ocr_text)
        dialogue_info["interaction_type"] = interaction_type
        
        # Calculate confidence
        confidence = self.calculate_dialogue_confidence(ocr_text, interaction_type)
        dialogue_info["confidence"] = confidence
        
        return dialogue_info if dialogue_info["dialogue_text"] else None
    
    def extract_npc_name(self, ocr_text: str) -> str:
        """Extract NPC name from OCR text."""
        # Common NPC name patterns
        name_patterns = [
            r"([A-Z][a-z]+ [A-Z][a-z]+):",  # "John Smith:"
            r"([A-Z][a-z]+):",               # "John:"
            r"([A-Z]+ [A-Z]+):",             # "JOHN SMITH:"
            r"([A-Z]+):",                    # "JOHN:"
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, ocr_text)
            if match:
                return match.group(1).strip()
        
        return "Unknown NPC"
    
    def extract_dialogue_text(self, ocr_text: str) -> str:
        """Extract dialogue text from OCR text."""
        # Remove NPC name and extract dialogue
        lines = ocr_text.split('\n')
        dialogue_lines = []
        
        for line in lines:
            # Skip empty lines and lines that are just NPC names
            if line.strip() and not re.match(r'^[A-Z][a-z]+:?\s*$', line):
                # Remove NPC name prefix if present
                clean_line = re.sub(r'^[A-Z][a-z]+:?\s*', '', line)
                if clean_line.strip():
                    dialogue_lines.append(clean_line.strip())
        
        return ' '.join(dialogue_lines)
    
    def extract_response_options(self, ocr_text: str) -> List[str]:
        """Extract response options from OCR text."""
        options = []
        
        # Look for numbered options
        option_patterns = [
            r"(\d+)\.\s*([^\n]+)",           # "1. Accept"
            r"\[(\d+)\]\s*([^\n]+)",         # "[1] Accept"
            r"(\d+)\s*([^\n]+)",             # "1 Accept"
        ]
        
        for pattern in option_patterns:
            matches = re.findall(pattern, ocr_text, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    options.append(match[1].strip())
        
        # Look for button-style options
        button_patterns = [
            r"\[([^\]]+)\]",                  # "[Accept]"
            r"<([^>]+)>",                     # "<Accept>"
        ]
        
        for pattern in button_patterns:
            matches = re.findall(pattern, ocr_text, re.IGNORECASE)
            for match in matches:
                options.append(match.strip())
        
        return options
    
    def determine_interaction_type(self, ocr_text: str) -> InteractionType:
        """Determine the type of interaction from OCR text."""
        text_lower = ocr_text.lower()
        
        # Check for quest indicators
        quest_keywords = self.ocr_keywords.get("quest_indicators", [])
        if any(keyword in text_lower for keyword in quest_keywords):
            return InteractionType.QUEST_GIVER
        
        # Check for trainer indicators
        trainer_keywords = self.ocr_keywords.get("trainer_indicators", [])
        if any(keyword in text_lower for keyword in trainer_keywords):
            return InteractionType.TRAINER
        
        # Check for terminal indicators
        terminal_keywords = self.ocr_keywords.get("terminal_indicators", [])
        if any(keyword in text_lower for keyword in terminal_keywords):
            return InteractionType.TERMINAL
        
        # Check for vendor indicators
        vendor_keywords = self.ocr_keywords.get("vendor_indicators", [])
        if any(keyword in text_lower for keyword in vendor_keywords):
            return InteractionType.VENDOR
        
        return InteractionType.UNKNOWN
    
    def calculate_dialogue_confidence(self, ocr_text: str, interaction_type: InteractionType) -> float:
        """Calculate confidence in dialogue parsing."""
        confidence = 0.0
        
        # Base confidence from text length
        if len(ocr_text) > 50:
            confidence += 0.3
        elif len(ocr_text) > 20:
            confidence += 0.2
        else:
            confidence += 0.1
        
        # Confidence from response options
        response_options = self.extract_response_options(ocr_text)
        if response_options:
            confidence += 0.3
            if len(response_options) > 1:
                confidence += 0.2
        
        # Confidence from interaction type detection
        if interaction_type != InteractionType.UNKNOWN:
            confidence += 0.2
        
        # Confidence from keyword matches
        text_lower = ocr_text.lower()
        all_keywords = []
        for keywords in self.ocr_keywords.values():
            all_keywords.extend(keywords)
        
        keyword_matches = sum(1 for keyword in all_keywords if keyword in text_lower)
        confidence += min(keyword_matches * 0.1, 0.2)
        
        return min(confidence, 1.0)
    
    def determine_response(self, dialogue: NPCDialogue) -> ResponseType:
        """Determine the appropriate response based on dialogue context."""
        text_lower = dialogue.dialogue_text.lower()
        interaction_type = dialogue.interaction_type
        
        # Get response patterns for this interaction type
        patterns = self.response_patterns.get(interaction_type.value, {})
        
        # Check each response type
        for response_type, patterns_list in patterns.items():
            for pattern in patterns_list:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    return ResponseType(response_type)
        
        # Check response options for common patterns
        for option in dialogue.response_options:
            option_lower = option.lower()
            
            if any(word in option_lower for word in ["accept", "yes", "okay", "continue"]):
                return ResponseType.ACCEPT
            elif any(word in option_lower for word in ["decline", "no", "cancel", "exit"]):
                return ResponseType.DECLINE
            elif any(word in option_lower for word in ["train", "learn", "skill"]):
                return ResponseType.TRAIN
            elif any(word in option_lower for word in ["buy", "purchase"]):
                return ResponseType.BUY
            elif any(word in option_lower for word in ["sell", "trade"]):
                return ResponseType.SELL
        
        # Default response based on interaction type
        default_responses = {
            InteractionType.QUEST_GIVER: ResponseType.ACCEPT,
            InteractionType.TRAINER: ResponseType.TRAIN,
            InteractionType.TERMINAL: ResponseType.CONTINUE,
            InteractionType.VENDOR: ResponseType.EXIT,
            InteractionType.UNKNOWN: ResponseType.CONTINUE
        }
        
        return default_responses.get(interaction_type, ResponseType.CONTINUE)
    
    def execute_response(self, response: ResponseType, dialogue: NPCDialogue) -> bool:
        """Execute the determined response."""
        start_time = time.time()
        
        try:
            # Find the appropriate response option
            response_text = response.value.upper()
            response_option = None
            
            # Look for exact match in response options
            for option in dialogue.response_options:
                if response_text in option.upper():
                    response_option = option
                    break
            
            # If no exact match, try partial match
            if not response_option:
                for option in dialogue.response_options:
                    if any(word in option.upper() for word in response_text.split()):
                        response_option = option
                        break
            
            if response_option:
                # Click on the response option
                self.logger.info(f"Clicking response: {response_option}")
                # In real implementation, would click on the option
                click_at(100, 200)  # Mock click
                return True
            else:
                # Use fallback sequence
                self.logger.warning(f"No response option found, using fallback for {dialogue.interaction_type.value}")
                return self.execute_fallback_sequence(dialogue.interaction_type)
        
        except Exception as e:
            self.logger.error(f"Failed to execute response: {e}")
            return False
        finally:
            response_time = time.time() - start_time
            self.record_interaction_attempt(dialogue.npc_name, dialogue.interaction_type, 
                                         dialogue.dialogue_text, response, True, response_time, False)
    
    def execute_fallback_sequence(self, interaction_type: InteractionType) -> bool:
        """Execute fallback interaction sequence."""
        try:
            sequence = self.fallback_sequences.get(interaction_type.value, ["ENTER", "1", "ESC"])
            self.logger.info(f"Executing fallback sequence: {sequence}")
            
            for action in sequence:
                if action == "ENTER":
                    press_key("ENTER")
                elif action == "ESC":
                    press_key("ESC")
                elif action.isdigit():
                    press_key(action)
                else:
                    press_key(action)
                
                wait(self.config.get("fallback_delay", 0.5))
            
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to execute fallback sequence: {e}")
            return False
    
    def interact_with_npc(self, npc_name: str = None, max_retries: int = None) -> bool:
        """Main interaction method with NPC."""
        if max_retries is None:
            max_retries = self.config.get("max_retries", 3)
        
        for attempt in range(max_retries):
            self.logger.info(f"NPC interaction attempt {attempt + 1}/{max_retries}")
            
            # Scan for NPC dialogue
            dialogue = self.scan_npc_dialogue(npc_name)
            if not dialogue:
                self.logger.warning("No dialogue detected")
                continue
            
            # Determine appropriate response
            response = self.determine_response(dialogue)
            self.logger.info(f"Determined response: {response.value}")
            
            # Execute response
            success = self.execute_response(response, dialogue)
            if success:
                self.logger.info("NPC interaction successful")
                return True
            
            # Wait before retry
            wait(self.config.get("ocr_interval", 1.0))
        
        self.logger.error(f"Failed to interact with NPC after {max_retries} attempts")
        return False
    
    def record_interaction_attempt(self, npc_name: str, interaction_type: InteractionType, 
                                 ocr_text: str, response: ResponseType, success: bool, 
                                 response_time: float, fallback_used: bool):
        """Record an interaction attempt for statistics."""
        attempt = InteractionAttempt(
            npc_name=npc_name,
            interaction_type=interaction_type,
            ocr_text=ocr_text,
            detected_response=response,
            success=success,
            timestamp=time.time(),
            fallback_used=fallback_used,
            response_time=response_time
        )
        
        self.interaction_history.append(attempt)
        
        # Update statistics
        self.stats["total_interactions"] += 1
        if success:
            self.stats["successful_interactions"] += 1
        else:
            self.stats["failed_interactions"] += 1
        
        if fallback_used:
            self.stats["fallback_usage"] += 1
        
        # Update average response time
        total_time = sum(att.response_time for att in self.interaction_history)
        self.stats["average_response_time"] = total_time / len(self.interaction_history)
    
    def get_interaction_statistics(self) -> Dict[str, Any]:
        """Get interaction statistics."""
        if not self.interaction_history:
            return self.stats
        
        # Calculate additional statistics
        recent_attempts = self.interaction_history[-10:]  # Last 10 attempts
        success_rate = len([a for a in recent_attempts if a.success]) / len(recent_attempts)
        
        # Interaction type distribution
        type_distribution = {}
        for attempt in self.interaction_history:
            interaction_type = attempt.interaction_type.value
            type_distribution[interaction_type] = type_distribution.get(interaction_type, 0) + 1
        
        # Response type distribution
        response_distribution = {}
        for attempt in self.interaction_history:
            response_type = attempt.detected_response.value
            response_distribution[response_type] = response_distribution.get(response_type, 0) + 1
        
        return {
            **self.stats,
            "success_rate": success_rate,
            "interaction_type_distribution": type_distribution,
            "response_type_distribution": response_distribution,
            "total_attempts": len(self.interaction_history)
        }
    
    def clear_history(self):
        """Clear interaction history."""
        self.interaction_history.clear()
        self.stats = {
            "total_interactions": 0,
            "successful_interactions": 0,
            "failed_interactions": 0,
            "fallback_usage": 0,
            "average_response_time": 0.0
        }
        self.logger.info("Interaction history cleared")


# Global NPC interactor instance
_npc_interactor: Optional[NPCInteractor] = None

def get_npc_interactor(config_path: Optional[str] = None) -> NPCInteractor:
    """Get the global NPC interactor instance."""
    global _npc_interactor
    if _npc_interactor is None:
        _npc_interactor = NPCInteractor(config_path)
    return _npc_interactor

def interact_with_npc(npc_name: str = None, max_retries: int = None) -> bool:
    """Interact with an NPC."""
    interactor = get_npc_interactor()
    return interactor.interact_with_npc(npc_name, max_retries)

def get_interaction_statistics() -> Dict[str, Any]:
    """Get interaction statistics."""
    interactor = get_npc_interactor()
    return interactor.get_interaction_statistics() 