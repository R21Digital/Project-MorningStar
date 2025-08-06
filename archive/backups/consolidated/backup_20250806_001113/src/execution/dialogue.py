import random
import time
import pyautogui
import cv2
import numpy as np
from typing import List, Optional, Dict, Any
from src.vision.ocr import screen_text, capture_screen
from src.automation.training import train_with_npc


def detect_dialogue_window(screen_image: np.ndarray) -> Optional[Dict[str, Any]]:
    """Detect dialogue window on screen using image processing.
    
    Parameters
    ----------
    screen_image : np.ndarray
        Screenshot to analyze
        
    Returns
    -------
    dict or None
        Dialogue window info with coordinates and detected text, or None if not found
    """
    try:
        # Convert to grayscale for processing
        gray = cv2.cvtColor(screen_image, cv2.COLOR_BGR2GRAY)
        
        # Look for dialogue window patterns (bright rectangular areas)
        # This is a simplified approach - in practice you'd use more sophisticated detection
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 10000:  # Minimum dialogue window size
                x, y, w, h = cv2.boundingRect(contour)
                
                # Extract text from the potential dialogue area
                dialogue_region = screen_image[y:y+h, x:x+w]
                text = screen_text(region=(x, y, w, h))
                
                if text and len(text.strip()) > 10:  # Minimum text length
                    return {
                        "x": x, "y": y, "width": w, "height": h,
                        "text": text.strip(),
                        "confidence": 0.8
                    }
        
        return None
    except Exception as e:
        print(f"[DIALOGUE] Window detection failed: {e}")
        return None


def extract_dialogue_options(text: str) -> List[str]:
    """Extract dialogue options from OCR text.
    
    Parameters
    ----------
    text : str
        Raw OCR text from dialogue window
        
    Returns
    -------
    list
        List of dialogue options found
    """
    options = []
    
    # Look for numbered options (1. Option text)
    import re
    option_patterns = [
        r'(\d+)\.\s*([^\n]+)',  # "1. Option text"
        r'(\d+)\)\s*([^\n]+)',  # "1) Option text"
        r'\[(\d+)\]\s*([^\n]+)',  # "[1] Option text"
    ]
    
    for pattern in option_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            option_num, option_text = match
            options.append(option_text.strip())
    
    # If no numbered options found, look for bullet points or other indicators
    if not options:
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) > 5 and not line.startswith('NPC:'):
                options.append(line)
    
    return options


def click_dialogue_option(option_index: int, dialogue_region: Dict[str, Any]) -> bool:
    """Click on a specific dialogue option.
    
    Parameters
    ----------
    option_index : int
        Index of the option to click (0-based)
    dialogue_region : dict
        Dialogue window region information
        
    Returns
    -------
    bool
        True if click was successful, False otherwise
    """
    try:
        x, y, w, h = dialogue_region["x"], dialogue_region["y"], dialogue_region["width"], dialogue_region["height"]
        
        # Calculate click position (assume options are vertically stacked)
        option_height = h // 4  # Rough estimate
        click_y = y + (option_index + 1) * option_height
        click_x = x + w // 2  # Center horizontally
        
        # Click the option
        pyautogui.click(click_x, click_y)
        print(f"[DIALOGUE] Clicked option {option_index + 1}")
        return True
        
    except Exception as e:
        print(f"[DIALOGUE] Failed to click option: {e}")
        return False


def simulate_macro_click(button_text: str) -> bool:
    """Simulate clicking a button by text using macro simulation.
    
    Parameters
    ----------
    button_text : str
        Text of the button to click
        
    Returns
    -------
    bool
        True if click was successful, False otherwise
    """
    try:
        # Capture screen and look for button text
        screenshot = capture_screen()
        text = screen_text()
        
        if button_text.lower() in text.lower():
            # Find the text position and click near it
            # This is a simplified approach - in practice you'd use more precise text detection
            lines = text.split('\n')
            for i, line in enumerate(lines):
                if button_text.lower() in line.lower():
                    # Estimate click position based on line number
                    click_y = 100 + (i * 20)  # Rough estimate
                    click_x = 400  # Center of screen
                    pyautogui.click(click_x, click_y)
                    print(f"[DIALOGUE] Macro clicked: {button_text}")
                    return True
        
        return False
    except Exception as e:
        print(f"[DIALOGUE] Macro click failed: {e}")
        return False


def execute_dialogue(step: dict) -> None:
    """Handle dialogue steps with enhanced UI interaction and OCR.

    This enhanced version uses OCR to detect dialogue windows and options,
    then performs appropriate UI interactions or macro simulations.
    """

    npc = step.get("npc", "Unknown NPC")
    options = step.get("options", [])
    selected_index = step.get("selected_index")

    print(f"\U0001F5E8\uFE0F [Dialogue] Interacting with {npc}")

    if step.get("npc") == "Trainer":
        train_with_npc(step)
    else:
        print(f"[DIALOGUE] Talking to {step.get('npc', 'Unknown')}")

    # Capture screen and detect dialogue window
    screen_image = capture_screen()
    dialogue_info = detect_dialogue_window(screen_image)
    
    if dialogue_info:
        print(f"[DIALOGUE] Detected dialogue window: {dialogue_info['text'][:100]}...")
        
        # Extract options from OCR text
        ocr_options = extract_dialogue_options(dialogue_info['text'])
        if ocr_options:
            print("\U0001F4AC Detected Dialogue Options:")
            for i, opt in enumerate(ocr_options, 1):
                print(f"  {i}. {opt}")
            
            # Simulate delay for reading
            time.sleep(0.5)
            
            # Select option
            if selected_index is None:
                selected_index = random.randint(0, len(ocr_options) - 1)
            
            if 0 <= selected_index < len(ocr_options):
                selected_option = ocr_options[selected_index]
                print(f"\n\u27A1 Selected: '{selected_option}'")
                
                # Click the option
                if click_dialogue_option(selected_index, dialogue_info):
                    print("[DIALOGUE] Option clicked successfully")
                else:
                    # Fallback to macro simulation
                    if simulate_macro_click(selected_option):
                        print("[DIALOGUE] Macro simulation successful")
                    else:
                        print("[DIALOGUE] Failed to interact with dialogue option")
            else:
                print(f"[DIALOGUE] Invalid option index: {selected_index}")
        else:
            print("[DIALOGUE] No dialogue options detected in OCR text")
            
            # Fallback to provided options
            if options:
                print("\U0001F4AC Using provided options:")
                for i, opt in enumerate(options, 1):
                    print(f"  {i}. {opt}")
                
                time.sleep(0.5)
                
                if selected_index is None:
                    selected_index = random.randint(0, len(options) - 1)
                
                selected_option = options[selected_index]
                print(f"\n\u27A1 Selected: '{selected_option}'")
                
                # Try macro simulation for provided options
                if simulate_macro_click(selected_option):
                    print("[DIALOGUE] Macro simulation successful")
                else:
                    print("[DIALOGUE] Failed to interact with dialogue")
    else:
        print("[DIALOGUE] No dialogue window detected")
        
        # Fallback to original behavior
        if options:
            print("\U0001F4AC Dialogue Options:")
            for i, opt in enumerate(options, 1):
                print(f"  {i}. {opt}")

            time.sleep(0.5)

            if selected_index is None:
                selected_index = random.randint(0, len(options) - 1)

            selected_option = options[selected_index]
            print(f"\n\u27A1 You selected: '{selected_option}'")
        else:
            print("\U0001F4AC No dialogue options provided.")


def handle_quest_dialogue(quest_step: dict) -> bool:
    """Handle quest-specific dialogue interactions.
    
    Parameters
    ----------
    quest_step : dict
        Quest step containing dialogue information
        
    Returns
    -------
    bool
        True if dialogue was handled successfully, False otherwise
    """
    npc = quest_step.get("npc", "")
    dialogue_type = quest_step.get("dialogue_type", "general")
    
    print(f"[DIALOGUE] Handling {dialogue_type} dialogue with {npc}")
    
    # Capture screen for analysis
    screen_image = capture_screen()
    dialogue_info = detect_dialogue_window(screen_image)
    
    if not dialogue_info:
        print("[DIALOGUE] No dialogue window found")
        return False
    
    # Handle different dialogue types
    if dialogue_type == "quest_accept":
        # Look for "Accept" or "Yes" buttons
        for accept_text in ["Accept", "Yes", "I'll help", "Take quest"]:
            if simulate_macro_click(accept_text):
                print(f"[DIALOGUE] Accepted quest from {npc}")
                return True
                
    elif dialogue_type == "quest_complete":
        # Look for "Complete" or "Turn in" buttons
        for complete_text in ["Complete", "Turn in", "Finish", "Done"]:
            if simulate_macro_click(complete_text):
                print(f"[DIALOGUE] Completed quest with {npc}")
                return True
                
    elif dialogue_type == "training":
        # Handle trainer dialogue
        return train_with_npc(quest_step)
    
    # Default: try to click the first option
    if click_dialogue_option(0, dialogue_info):
        print(f"[DIALOGUE] Selected first option with {npc}")
        return True
    
    return False
