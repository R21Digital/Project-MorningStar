# Navigator System Documentation

## Overview

The Navigator System is a modular waypoint navigation engine that provides coordinate-based movement with safety features and integration with existing movement infrastructure. It enables automated navigation between points of interest using WASD movement controls and includes obstacle detection, timeout handling, and comprehensive logging.

## Features

### Core Functionality
- **Waypoint Management**: Load and manage waypoints from JSON files with planet/zone organization
- **Coordinate Navigation**: Navigate to specific coordinates using WASD movement
- **Heading Logic**: Rotate character to face target before movement
- **Safety Features**: Obstacle detection, timeout handling, and stuck position detection
- **POI Movement**: Simulate movement between multiple points of interest
- **Comprehensive Logging**: JSON-based logging of all navigation events

### Safety Features
- **Obstacle Detection**: Detects when character is stuck and cannot move
- **Timeout Protection**: Prevents infinite movement loops
- **Position Verification**: Validates arrival at target coordinates
- **Error Recovery**: Graceful handling of navigation failures

### Integration
- **Movement Controller**: Integrates with existing `MovementController`
- **Waypoint Verifier**: Uses existing waypoint stability verification
- **Singleton Pattern**: Global navigator instance for consistent state

## Architecture

### Core Classes

#### `Waypoint`
Represents a navigation destination with coordinates and metadata.

```python
@dataclass
class Waypoint:
    x: int                    # X coordinate
    y: int                    # Y coordinate
    name: str                 # Unique waypoint name
    planet: str               # Planet name
    zone: str                 # Zone/city name
    description: Optional[str] # Human-readable description
    safe_zone: Optional[Tuple[int, int, int, int]] # Safe area bounds
```

#### `NavigationState`
Tracks the current navigation state and progress.

```python
@dataclass
class NavigationState:
    current_waypoint: Optional[Waypoint]  # Current location
    target_waypoint: Optional[Waypoint]   # Destination
    status: MovementStatus                 # Current status
    start_time: Optional[float]           # Navigation start time
    attempts: int                         # Attempt counter
    last_position: Optional[Tuple[int, int]] # Last known position
    heading: float                        # Current heading in degrees
```

#### `MovementStatus`
Enumeration of possible navigation states.

```python
class MovementStatus(Enum):
    IDLE = "idle"           # Not moving
    MOVING = "moving"       # Currently navigating
    ARRIVED = "arrived"     # Successfully reached destination
    FAILED = "failed"       # Navigation failed
    TIMEOUT = "timeout"     # Movement timeout
    OBSTACLE = "obstacle"   # Obstacle detected
```

#### `Navigator`
Main navigation engine class.

```python
class Navigator:
    def __init__(self, waypoints_file: Optional[str] = None)
    def navigate_to_waypoint(self, waypoint_name: str) -> bool
    def simulate_movement_between_pois(self, poi_list: List[str]) -> bool
    def get_navigation_status(self) -> Dict[str, Any]
```

## Usage

### Basic Navigation

```python
from core.navigator import get_navigator, navigate_to_waypoint

# Get the global navigator instance
navigator = get_navigator()

# Navigate to a specific waypoint
success = navigate_to_waypoint("mos_eisley_cantina")
if success:
    print("Successfully reached destination")
else:
    print("Navigation failed")
```

### POI Movement

```python
from core.navigator import simulate_poi_movement

# Navigate between multiple points of interest
poi_list = ["mos_eisley_cantina", "anchorhead_center", "bestine_center"]
success = simulate_poi_movement(poi_list)
```

### Status Monitoring

```python
from core.navigator import get_navigation_status

# Get current navigation status
status = get_navigation_status()
print(f"Status: {status['status']}")
print(f"Heading: {status['heading']}°")
print(f"Elapsed time: {status['elapsed_time']:.2f}s")
```

### Direct Navigator Usage

```python
from core.navigator import Navigator

# Create navigator with custom waypoints file
navigator = Navigator(waypoints_file="custom_waypoints.json")

# List waypoints filtered by planet
tatooine_waypoints = navigator.list_waypoints(planet="tatooine")

# Get specific waypoint
waypoint = navigator.get_waypoint("mos_eisley_cantina")
if waypoint:
    print(f"Found waypoint: {waypoint.name} at ({waypoint.x}, {waypoint.y})")
```

## Configuration

### Waypoints File Format

Waypoints are stored in JSON format with the following structure:

```json
[
    {
        "name": "mos_eisley_cantina",
        "x": 3520,
        "y": -4800,
        "planet": "tatooine",
        "zone": "mos_eisley",
        "description": "Cantina in Mos Eisley",
        "safe_zone": [3500, -4850, 40, 100]
    }
]
```

### Navigation Settings

The navigator can be configured with various settings:

```python
navigator = Navigator()
navigator.max_attempts = 3                    # Max navigation attempts
navigator.timeout_seconds = 30.0              # Movement timeout
navigator.obstacle_detection_threshold = 5    # Pixels for stuck detection
navigator.heading_tolerance = 15.0            # Degrees for rotation
```

### Default Waypoints

If no waypoints file is provided, the system creates default waypoints:

- **Tatooine**: Mos Eisley Cantina, Anchorhead Center, Bestine Center
- **Naboo**: Theed Palace, Moenia Center  
- **Dantooine**: Mining Cave

## Logging

### Navigation Events

All navigation events are logged to `logs/navigation/navigation_YYYYMMDD.json`:

```json
{
    "timestamp": 1703123456.789,
    "event_type": "navigation_start",
    "details": {
        "waypoint_name": "mos_eisley_cantina",
        "coordinates": [3520, -4800],
        "planet": "tatooine",
        "zone": "mos_eisley"
    }
}
```

### Event Types

- `navigation_start`: Navigation initiated
- `navigation_success`: Successfully reached destination
- `navigation_failed`: Navigation failed
- `navigation_error`: Error during navigation
- `obstacle_detected`: Obstacle or stuck position detected
- `movement_timeout`: Movement timeout reached

## Testing

### Unit Tests

Comprehensive unit tests are available in `tests/test_navigator.py`:

```bash
python -m pytest tests/test_navigator.py -v
```

### Test Coverage

- Waypoint creation and validation
- Navigation state management
- Movement and rotation logic
- Obstacle detection and timeout handling
- POI movement simulation
- Global function integration
- JSON serialization

### Integration Testing

The system integrates with existing components:

- **Movement Controller**: Uses existing WASD movement infrastructure
- **Waypoint Verifier**: Leverages existing position verification
- **Screenshot System**: Integrates with screen capture for position detection

## Safety Features

### Obstacle Detection

The system monitors movement progress and detects when the character is stuck:

```python
# Check if position has changed significantly
pos_distance = math.sqrt((current_x - last_position[0])**2 + (current_y - last_position[1])**2)
if pos_distance < obstacle_detection_threshold:
    stuck_count += 1
    if stuck_count > 5:
        return False  # Obstacle detected
```

### Timeout Protection

Movement is limited by configurable timeouts:

```python
while time.time() - start_time < self.timeout_seconds:
    # Movement logic
    pass
return False  # Timeout reached
```

### Position Verification

Arrival is verified by checking distance to target:

```python
distance = math.sqrt((target_x - current_x)**2 + (target_y - current_y)**2)
if distance < 10:  # Within 10 pixels
    return True  # Arrived
```

## Future Enhancements

### Planned Features

1. **Minimap Integration**: Use minimap for more accurate navigation
2. **Pathfinding**: Implement A* pathfinding for complex routes
3. **Dynamic Obstacle Avoidance**: Real-time obstacle detection and avoidance
4. **Multi-Planet Travel**: Automated planet-to-planet navigation
5. **Quest Integration**: Automatic navigation for quest objectives

### Performance Optimizations

1. **Position Caching**: Cache position data to reduce OCR calls
2. **Movement Prediction**: Predict movement patterns for smoother navigation
3. **Parallel Processing**: Concurrent navigation and monitoring tasks

## Troubleshooting

### Common Issues

1. **Navigation Fails**: Check if waypoint exists and coordinates are valid
2. **Stuck Detection**: Verify obstacle detection threshold settings
3. **Timeout Errors**: Increase timeout_seconds for longer distances
4. **Rotation Issues**: Adjust heading_tolerance for rotation sensitivity

### Debug Information

Enable debug logging to troubleshoot navigation issues:

```python
import logging
logging.getLogger('core.navigator').setLevel(logging.DEBUG)
```

### Log Analysis

Review navigation logs to identify patterns:

```bash
tail -f logs/navigation/navigation_$(date +%Y%m%d).json
```

## API Reference

### Global Functions

- `get_navigator(waypoints_file=None)`: Get global navigator instance
- `navigate_to_waypoint(waypoint_name)`: Navigate to waypoint
- `simulate_poi_movement(poi_list)`: Navigate between POIs
- `get_navigation_status()`: Get current navigation status

### Navigator Methods

- `navigate_to_waypoint(waypoint_name)`: Navigate to specific waypoint
- `simulate_movement_between_pois(poi_list)`: Navigate between POIs
- `get_waypoint(name)`: Get waypoint by name
- `list_waypoints(planet=None, zone=None)`: List waypoints with filters
- `get_navigation_status()`: Get current status

### Configuration

- `max_attempts`: Maximum navigation attempts
- `timeout_seconds`: Movement timeout in seconds
- `obstacle_detection_threshold`: Pixels for stuck detection
- `heading_tolerance`: Degrees for rotation tolerance
- `position_verification_delay`: Delay for position verification 