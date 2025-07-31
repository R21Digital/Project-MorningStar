import pyautogui
import time
import random

from core.dialogue_detector import detect_dialogue, DialogueDetector
from core.logging_config import configure_logger

# Configure logger for handlers
logger = configure_logger("automation_handlers")


def press_continue():
    """Handle continue prompts by pressing Enter."""
    print("[ACTION] Pressing 'Continue'")
    time.sleep(random.uniform(0.5, 1.5))
    pyautogui.press("enter")
    logger.info("Executed continue action")


def click_confirm():
    """Handle confirmation dialogs by clicking center screen."""
    print("[ACTION] Clicking center for confirm")
    time.sleep(random.uniform(0.5, 1.5))
    pyautogui.click(x=960, y=540)  # Adjust if needed
    logger.info("Executed confirm click")


def handle_npc_dialogue():
    """Handle NPC dialogue using advanced dialogue detection system."""
    print("[ACTION] Handling NPC Dialogue with OCR detection")
    
    try:
        # Use the new dialogue detection system
        detection = detect_dialogue(auto_respond=True)
        
        if detection:
            logger.info(
                f"Dialogue detected and handled: {detection.dialogue_type} "
                f"(confidence: {detection.confidence:.2f})"
            )
            return True
        else:
            # Fallback to simple dialogue handling
            print("[FALLBACK] Using simple dialogue handling")
            time.sleep(random.uniform(0.5, 1.5))
            pyautogui.press("1")  # Assume '1' selects dialogue option
            time.sleep(random.uniform(0.5, 1.5))
            pyautogui.press("enter")
            logger.info("Executed fallback dialogue handling")
            return True
            
    except Exception as e:
        logger.error(f"Error in dialogue handling: {e}")
        # Fallback to simple handling on error
        print("[FALLBACK] Error occurred, using simple dialogue handling")
        time.sleep(random.uniform(0.5, 1.5))
        pyautogui.press("1")
        time.sleep(random.uniform(0.5, 1.5))
        pyautogui.press("enter")
        return False


def handle_quest_dialogue():
    """Specialized handler for quest-related dialogues."""
    print("[ACTION] Handling Quest Dialogue")
    
    try:
        # Create detector instance for quest-specific handling
        detector = DialogueDetector()
        
        # Scan for quest-related dialogues
        detection = detector.detect_and_handle_dialogue(auto_respond=True, region="quest_window")
        
        if detection and detection.dialogue_type in ["quest_offer", "quest_acceptance", "quest_completion"]:
            logger.info(f"Quest dialogue handled: {detection.dialogue_type}")
            return True
        else:
            logger.warning("No quest dialogue detected, using fallback")
            # Fallback: accept quest by pressing 1
            time.sleep(random.uniform(0.8, 1.2))
            pyautogui.press("1")
            time.sleep(random.uniform(0.5, 1.0))
            pyautogui.press("enter")
            return True
            
    except Exception as e:
        logger.error(f"Error in quest dialogue handling: {e}")
        return False


def handle_trainer_dialogue():
    """Specialized handler for trainer interactions."""
    print("[ACTION] Handling Trainer Dialogue")
    
    try:
        detector = DialogueDetector()
        detection = detector.detect_and_handle_dialogue(auto_respond=True, region="dialogue_box")
        
        if detection and detection.dialogue_type == "trainer_dialogue":
            logger.info("Trainer dialogue handled successfully")
            return True
        else:
            # Fallback: assume training dialogue
            print("[FALLBACK] Using trainer fallback")
            time.sleep(random.uniform(0.8, 1.2))
            pyautogui.press("1")  # Usually "Train" option
            time.sleep(random.uniform(0.5, 1.0))
            return True
            
    except Exception as e:
        logger.error(f"Error in trainer dialogue handling: {e}")
        return False


def handle_vendor_dialogue():
    """Specialized handler for vendor/merchant interactions."""
    print("[ACTION] Handling Vendor Dialogue")
    
    try:
        detector = DialogueDetector()
        detection = detector.detect_and_handle_dialogue(auto_respond=True)
        
        if detection and detection.dialogue_type == "vendor_dialogue":
            logger.info("Vendor dialogue handled successfully")
            return True
        else:
            # Fallback: browse items
            print("[FALLBACK] Using vendor fallback")
            time.sleep(random.uniform(0.8, 1.2))
            pyautogui.press("1")  # Usually "Browse items" option
            time.sleep(random.uniform(0.5, 1.0))
            return True
            
    except Exception as e:
        logger.error(f"Error in vendor dialogue handling: {e}")
        return False


def scan_for_dialogues(duration: float = 5.0):
    """Actively scan for any dialogues for a specified duration."""
    print(f"[ACTION] Scanning for dialogues for {duration} seconds")
    
    try:
        detector = DialogueDetector()
        detections = detector.scan_for_dialogues(
            duration=duration, 
            interval=1.0, 
            auto_respond=True
        )
        
        logger.info(f"Dialogue scan completed. Found {len(detections)} dialogues")
        
        for detection in detections:
            print(f"  - {detection.dialogue_type} (confidence: {detection.confidence:.2f})")
            
        return detections
        
    except Exception as e:
        logger.error(f"Error during dialogue scan: {e}")
        return []


# Mapping of screen state names to the handler functions that should be
# executed when the state is detected. ``states.handle_state`` will dispatch
# using this dictionary.
STATE_HANDLERS = {
    "continue_prompt": press_continue,
    "npc_dialogue": handle_npc_dialogue,
    "quest_dialogue": handle_quest_dialogue,
    "trainer_dialogue": handle_trainer_dialogue,
    "vendor_dialogue": handle_vendor_dialogue,
    "confirm_dialog": click_confirm,
}

