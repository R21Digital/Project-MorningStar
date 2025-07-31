"""Enhanced dialogue execution with OCR-based detection."""

from core.dialogue_detector import detect_dialogue, DialogueDetector
from core.logging_config import configure_logger
from src.automation.training import train_with_npc

logger = configure_logger("dialogue_execution")


def execute_dialogue(step: dict) -> bool:
    """Execute a dialogue step with advanced OCR-based detection.
    
    Parameters
    ----------
    step : dict
        Dialogue step containing target NPC and optional dialogue type.
        
    Returns
    -------
    bool
        True if dialogue was successfully handled, False otherwise.
    """
    target = step.get("target", "")
    dialogue_type = step.get("dialogue_type", "")
    region = step.get("region", "dialogue_box")
    
    logger.info(f"Executing dialogue step with target: {target}")
    
    try:
        # Use dialogue detector for automatic handling
        detector = DialogueDetector()
        detection = detector.detect_and_handle_dialogue(
            auto_respond=True, 
            region=region
        )
        
        if detection:
            logger.info(
                f"Dialogue detected and handled: {detection.dialogue_type} "
                f"with target '{target}' (confidence: {detection.confidence:.2f})"
            )
            
            # Special handling for trainer dialogues
            if detection.dialogue_type == "trainer_dialogue" and target.lower() == "trainer":
                logger.info("Initiating trainer-specific actions")
                train_with_npc(target)
                
            return True
            
        else:
            logger.warning(f"No dialogue detected for target '{target}', attempting fallback")
            
            # Fallback: use simple dialogue handling based on target type
            return _fallback_dialogue_handling(target, dialogue_type)
            
    except Exception as e:
        logger.error(f"Error in dialogue execution: {e}")
        return _fallback_dialogue_handling(target, dialogue_type)


def _fallback_dialogue_handling(target: str, dialogue_type: str = "") -> bool:
    """Fallback dialogue handling for when OCR detection fails.
    
    Parameters
    ----------
    target : str
        The target NPC or dialogue type.
    dialogue_type : str, optional
        Specific dialogue type if known.
        
    Returns
    -------
    bool
        True if fallback handling completed, False otherwise.
    """
    import time
    import random
    import pyautogui
    
    logger.info(f"Using fallback dialogue handling for target: {target}")
    
    try:
        # Determine appropriate action based on target or dialogue type
        if target.lower() == "trainer" or dialogue_type == "trainer":
            logger.info("Executing trainer fallback")
            time.sleep(random.uniform(0.8, 1.2))
            pyautogui.press("1")  # Train option
            time.sleep(random.uniform(0.5, 1.0))
            train_with_npc(target)
            
        elif dialogue_type in ["quest", "quest_offer", "quest_acceptance"]:
            logger.info("Executing quest fallback")
            time.sleep(random.uniform(0.8, 1.2))
            pyautogui.press("1")  # Accept quest
            time.sleep(random.uniform(0.5, 1.0))
            pyautogui.press("enter")  # Confirm
            
        elif dialogue_type == "vendor":
            logger.info("Executing vendor fallback")
            time.sleep(random.uniform(0.8, 1.2))
            pyautogui.press("1")  # Browse items
            time.sleep(random.uniform(0.5, 1.0))
            
        else:
            # Generic dialogue handling
            logger.info("Executing generic dialogue fallback")
            time.sleep(random.uniform(0.8, 1.2))
            pyautogui.press("1")  # First option
            time.sleep(random.uniform(0.5, 1.0))
            pyautogui.press("enter")  # Confirm/Continue
            
        logger.info("Fallback dialogue handling completed")
        return True
        
    except Exception as e:
        logger.error(f"Error in fallback dialogue handling: {e}")
        return False


def scan_and_handle_dialogues(duration: float = 10.0, interval: float = 2.0) -> list:
    """Scan for and automatically handle any dialogues for a specified duration.
    
    This function is useful for situations where dialogues might appear
    unpredictably and need to be handled automatically.
    
    Parameters
    ----------
    duration : float, default 10.0
        How long to scan for dialogues in seconds.
    interval : float, default 2.0
        How often to check for dialogues in seconds.
        
    Returns
    -------
    list
        List of DialogueDetection objects for all handled dialogues.
    """
    logger.info(f"Starting dialogue scan for {duration}s (interval: {interval}s)")
    
    try:
        detector = DialogueDetector()
        detections = detector.scan_for_dialogues(
            duration=duration,
            interval=interval,
            auto_respond=True
        )
        
        logger.info(f"Dialogue scan completed. Found and handled {len(detections)} dialogues")
        return detections
        
    except Exception as e:
        logger.error(f"Error during dialogue scan: {e}")
        return []


def wait_for_dialogue(timeout: float = 30.0, expected_type: str = None) -> bool:
    """Wait for a specific dialogue to appear and handle it.
    
    Parameters
    ----------
    timeout : float, default 30.0
        Maximum time to wait for dialogue in seconds.
    expected_type : str, optional
        Expected dialogue type to wait for (e.g., "quest_offer").
        
    Returns
    -------
    bool
        True if expected dialogue was detected and handled, False otherwise.
    """
    import time
    
    logger.info(f"Waiting for dialogue (timeout: {timeout}s, expected: {expected_type})")
    
    start_time = time.time()
    detector = DialogueDetector()
    
    while time.time() - start_time < timeout:
        try:
            detection = detector.detect_and_handle_dialogue(auto_respond=True)
            
            if detection:
                if expected_type is None or detection.dialogue_type == expected_type:
                    logger.info(
                        f"Expected dialogue detected: {detection.dialogue_type} "
                        f"(confidence: {detection.confidence:.2f})"
                    )
                    return True
                else:
                    logger.info(
                        f"Dialogue detected but not expected type: {detection.dialogue_type} "
                        f"(expected: {expected_type})"
                    )
                    
            time.sleep(1.0)  # Wait before next check
            
        except Exception as e:
            logger.error(f"Error while waiting for dialogue: {e}")
            time.sleep(1.0)
    
    logger.warning(f"Timeout waiting for dialogue (expected: {expected_type})")
    return False


def get_dialogue_history(limit: int = 20) -> list:
    """Retrieve recent dialogue history.
    
    Parameters
    ----------
    limit : int, default 20
        Maximum number of recent dialogues to retrieve.
        
    Returns
    -------
    list
        List of recent dialogue events.
    """
    try:
        detector = DialogueDetector()
        return detector.get_dialogue_history(limit=limit)
    except Exception as e:
        logger.error(f"Error retrieving dialogue history: {e}")
        return []


# Legacy function for backward compatibility
def execute_dialogue_step(step: dict) -> bool:
    """Legacy function name for backward compatibility."""
    return execute_dialogue(step)
