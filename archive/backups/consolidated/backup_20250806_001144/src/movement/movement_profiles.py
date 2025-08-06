"""Strategy functions for common movement behaviors."""

from .agent_mover import MovementAgent
from .waypoints import get_waypoint_route
import time
import random
import pyautogui
from typing import Tuple, Optional
import cv2
import numpy as np


def travel_to_city(agent: MovementAgent, destination: str) -> None:
    """Move the agent directly to the given destination."""
    agent.destination = destination
    agent.move_to()


def patrol_route(agent: MovementAgent, route_name: str) -> None:
    """Patrol through the stops in the named waypoint route."""
    route = get_waypoint_route(route_name)
    if not route:
        agent.session.add_action(f"Route '{route_name}' not found.")
        return

    for stop in route:
        agent.destination = stop
        agent.move_to()

        # Simulate human-like pause between moves
        wait_time = random.uniform(5.0, 15.0)
        agent.session.add_action(
            f"Waiting {wait_time:.1f} seconds before next move."
        )
        time.sleep(wait_time)


def idle(agent: MovementAgent) -> None:
    """Perform no movement."""
    agent.session.add_action("Staying idle, no movement performed.")


def detect_screen_region(image: np.ndarray, template_path: str) -> Optional[Tuple[int, int, int, int]]:
    """Detect a region on screen using template matching.
    
    Parameters
    ----------
    image : np.ndarray
        Screenshot to search in
    template_path : str
        Path to template image to find
        
    Returns
    -------
    tuple or None
        (x, y, width, height) of detected region, or None if not found
    """
    try:
        template = cv2.imread(template_path)
        if template is None:
            return None
            
        result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val > 0.8:  # Confidence threshold
            h, w = template.shape[:2]
            return (max_loc[0], max_loc[1], w, h)
        return None
    except Exception as e:
        print(f"[MOVEMENT] Template matching failed: {e}")
        return None


def walk_to_coords(agent: MovementAgent, x: int, y: int) -> None:
    """Walk the agent to the specified ``x`` and ``y`` coordinates."""

    print(f"[Movement] Walking to coordinates: ({x}, {y})...")

    # Get current screen dimensions
    screen_width, screen_height = pyautogui.size()
    
    # Calculate relative movement
    current_x, current_y = pyautogui.position()
    delta_x = x - current_x
    delta_y = y - current_y
    
    # Implement WASD-style movement
    if abs(delta_x) > 10 or abs(delta_y) > 10:
        # Calculate movement direction
        if delta_x > 0:
            pyautogui.keyDown('d')  # Move right
            time.sleep(0.1)
            pyautogui.keyUp('d')
        elif delta_x < 0:
            pyautogui.keyDown('a')  # Move left
            time.sleep(0.1)
            pyautogui.keyUp('a')
            
        if delta_y > 0:
            pyautogui.keyDown('s')  # Move down
            time.sleep(0.1)
            pyautogui.keyUp('s')
        elif delta_y < 0:
            pyautogui.keyDown('w')  # Move up
            time.sleep(0.1)
            pyautogui.keyUp('w')
        
        # Small delay for movement animation
        time.sleep(0.5)
        
        # Log the movement
        agent.session.add_action(f"Moved to coordinates ({x}, {y})")
        print("[Movement] Movement completed.")
    else:
        print("[Movement] Already at destination.")


def navigate_to_waypoint(agent: MovementAgent, waypoint_name: str) -> bool:
    """Navigate to a specific waypoint using screen recognition.
    
    Parameters
    ----------
    agent : MovementAgent
        The movement agent
    waypoint_name : str
        Name of the waypoint to navigate to
        
    Returns
    -------
    bool
        True if navigation was successful, False otherwise
    """
    print(f"[Movement] Navigating to waypoint: {waypoint_name}")
    
    # Capture screen for waypoint detection
    screenshot = pyautogui.screenshot()
    image = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    
    # Try to find waypoint on screen
    waypoint_region = detect_screen_region(image, f"data/waypoints/{waypoint_name}.png")
    
    if waypoint_region:
        x, y, w, h = waypoint_region
        center_x = x + w // 2
        center_y = y + h // 2
        
        # Click on waypoint
        pyautogui.click(center_x, center_y)
        agent.session.add_action(f"Clicked waypoint: {waypoint_name}")
        print(f"[Movement] Waypoint {waypoint_name} found and clicked.")
        return True
    else:
        print(f"[Movement] Waypoint {waypoint_name} not found on screen.")
        return False


def auto_walk_to_destination(agent: MovementAgent, destination: str) -> bool:
    """Automatically walk to a destination using available navigation methods.
    
    Parameters
    ----------
    agent : MovementAgent
        The movement agent
    destination : str
        Destination to walk to
        
    Returns
    -------
    bool
        True if navigation was successful, False otherwise
    """
    print(f"[Movement] Auto-walking to: {destination}")
    
    # Try waypoint navigation first
    if navigate_to_waypoint(agent, destination):
        return True
    
    # Fallback to coordinate-based movement
    # This would require a coordinate database
    coords = get_coordinates_for_destination(destination)
    if coords:
        x, y = coords
        walk_to_coords(agent, x, y)
        return True
    
    print(f"[Movement] Could not find navigation method for: {destination}")
    return False


def get_coordinates_for_destination(destination: str) -> Optional[Tuple[int, int]]:
    """Get coordinates for a destination from the coordinate database.
    
    Parameters
    ----------
    destination : str
        Name of the destination
        
    Returns
    -------
    tuple or None
        (x, y) coordinates, or None if not found
    """
    # This would typically load from a JSON file
    coordinate_db = {
        "Theed": (500, 300),
        "Coronet": (600, 400),
        "Mos Eisley": (400, 500),
        "Bestine": (700, 200),
    }
    
    return coordinate_db.get(destination)


def smart_movement(agent: MovementAgent, target: str, movement_type: str = "auto") -> bool:
    """Smart movement that chooses the best method based on target type.
    
    Parameters
    ----------
    agent : MovementAgent
        The movement agent
    target : str
        Target to move to
    movement_type : str
        Type of movement: "auto", "waypoint", "coordinates", "walk"
        
    Returns
    -------
    bool
        True if movement was successful, False otherwise
    """
    print(f"[Movement] Smart movement to: {target} (type: {movement_type})")
    
    if movement_type == "waypoint":
        return navigate_to_waypoint(agent, target)
    elif movement_type == "coordinates":
        coords = get_coordinates_for_destination(target)
        if coords:
            walk_to_coords(agent, coords[0], coords[1])
            return True
        return False
    elif movement_type == "walk":
        return auto_walk_to_destination(agent, target)
    else:  # auto
        # Try waypoint first, then coordinates, then walk
        if navigate_to_waypoint(agent, target):
            return True
        elif auto_walk_to_destination(agent, target):
            return True
        else:
            print(f"[Movement] All navigation methods failed for: {target}")
            return False
