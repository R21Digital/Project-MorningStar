# Travel Automation System Documentation

## Overview

The Travel Automation System provides comprehensive multi-zone and multi-planet travel automation using shuttleports and zone transitions. It enables automated travel for questing, trainer visits, and unlock progression with integration to the navigator system and existing travel infrastructure.

## Features

### Core Functionality
- **Multi-Planet Travel**: Navigate between different planets using shuttle networks
- **Trainer Travel**: Automated travel to profession trainers across the galaxy
- **Quest Travel**: Travel to quest locations with requirement checking
- **Unlock Travel**: Travel to unlock locations with condition verification
- **Route Planning**: Intelligent route planning using BFS algorithm
- **Shuttle Integration**: Seamless integration with shuttle dialogue detection
- **Comprehensive Logging**: JSON-based travel event logging

### Travel Types
- **SHUTTLE**: Inter-planet travel using shuttle networks
- **WALKING**: Local movement within zones
- **TRAINER**: Travel to profession trainers
- **QUEST**: Travel to quest locations
- **UNLOCK**: Travel to unlock locations

### Integration Features
- **Navigator System**: Integrates with the waypoint navigation engine
- **Dialogue Detection**: Uses dialogue detection for shuttle interactions
- **Waypoint Verification**: Leverages existing waypoint stability verification
- **Singleton Pattern**: Global travel automation instance for consistent state

## Architecture

### Core Classes

#### `TravelDestination`
Represents a travel destination with metadata and requirements.

```python
@dataclass
class TravelDestination:
    name: str                    # Destination name
    planet: str                  # Planet name
    city: str                    # City/zone name
    x: int                       # X coordinate
    y: int                       # Y coordinate
    travel_type: TravelType      # Type of travel
    description: Optional[str]   # Human-readable description
    requirements: Optional[List[str]] # Quest requirements
    unlock_conditions: Optional[Dict[str, Any]] # Unlock conditions
```

#### `TravelRoute`
Represents a planned travel route with stops and metadata.

```python
@dataclass
class TravelRoute:
    start_planet: str            # Starting planet
    start_city: str              # Starting city
    destination: TravelDestination # Final destination
    stops: List[Dict[str, Any]]  # Route stops
    total_distance: float         # Total route distance
    estimated_time: float         # Estimated travel time
    travel_type: TravelType      # Type of travel
```

#### `TravelState`
Tracks the current travel automation state.

```python
@dataclass
class TravelState:
    current_destination: Optional[TravelDestination] # Current destination
    current_route: Optional[TravelRoute]            # Current route
    status: TravelStatus                            # Current status
    start_time: Optional[float]                     # Travel start time
    attempts: int                                   # Attempt counter
    current_stop_index: int                         # Current stop index
    last_position: Optional[Tuple[int, int]]        # Last known position
```

#### `TravelStatus`
Enumeration of possible travel states.

```python
class TravelStatus(Enum):
    IDLE = "idle"           # Not traveling
    PLANNING = "planning"   # Planning route
    TRAVELING = "traveling" # Currently traveling
    ARRIVED = "arrived"     # Successfully arrived
    FAILED = "failed"       # Travel failed
    INTERRUPTED = "interrupted" # Travel interrupted
```

#### `TravelAutomation`
Main travel automation engine class.

```python
class TravelAutomation:
    def __init__(self, config_file: Optional[str] = None)
    def travel_to_trainer(self, profession: str) -> bool
    def travel_to_quest(self, quest_id: str) -> bool
    def travel_to_unlock(self, unlock_id: str) -> bool
    def plan_shuttle_route(self, start_planet: str, start_city: str,
                          dest_planet: str, dest_city: str) -> Optional[TravelRoute]
```

## Usage

### Basic Trainer Travel

```python
from core.travel_automation import travel_to_trainer

# Travel to a profession trainer
success = travel_to_trainer("artisan")
if success:
    print("Successfully reached artisan trainer")
else:
    print("Failed to reach trainer")
```

### Quest Travel

```python
from core.travel_automation import travel_to_quest

# Travel to a quest location
success = travel_to_quest("tatooine_artifact_hunt")
if success:
    print("Successfully reached quest location")
else:
    print("Failed to reach quest location")
```

### Unlock Travel

```python
from core.travel_automation import travel_to_unlock

# Travel to an unlock location
success = travel_to_unlock("tatooine_cantina_access")
if success:
    print("Successfully reached unlock location")
else:
    print("Failed to reach unlock location")
```

### Status Monitoring

```python
from core.travel_automation import get_travel_status

# Get current travel status
status = get_travel_status()
print(f"Status: {status['status']}")
print(f"Current destination: {status['current_destination']}")
print(f"Elapsed time: {status['elapsed_time']:.2f}s")
```

### Direct TravelAutomation Usage

```python
from core.travel_automation import get_travel_automation

# Get the global travel automation instance
automation = get_travel_automation()

# Plan a shuttle route
route = automation.plan_shuttle_route(
    "tatooine", "mos_eisley",
    "corellia", "coronet"
)

if route:
    print(f"Route planned: {len(route.stops)} stops")
    print(f"Estimated time: {route.estimated_time:.1f}s")
else:
    print("No route found")
```

## Configuration

### Travel Configuration File

The system uses a JSON configuration file (`data/travel_config.json`) with the following structure:

```json
{
  "shuttles": {
    "tatooine": [
      {
        "city": "mos_eisley",
        "npc": "Shuttle Conductor",
        "x": 3520,
        "y": -4800,
        "destinations": [
          {"planet": "corellia", "city": "coronet"},
          {"planet": "naboo", "city": "theed"}
        ]
      }
    ]
  },
  "trainers": {
    "artisan": {
      "name": "Artisan Trainer",
      "planet": "tatooine",
      "city": "mos_eisley",
      "x": 3432,
      "y": -4795,
      "expected_skill": "Novice Artisan"
    }
  },
  "quests": {
    "tatooine_artifact_hunt": {
      "name": "Tatooine Artifact Hunt",
      "planet": "tatooine",
      "city": "anchorhead",
      "x": -75,
      "y": 225,
      "description": "Search for ancient artifacts",
      "requirements": ["level_5", "scout_novice"]
    }
  },
  "unlocks": {
    "tatooine_cantina_access": {
      "name": "Tatooine Cantina Access",
      "planet": "tatooine",
      "city": "mos_eisley",
      "x": 3500,
      "y": -4850,
      "description": "Gain access to exclusive cantina",
      "unlock_conditions": {
        "reputation": {"tatooine": 1000},
        "quests_completed": ["tatooine_artifact_hunt"]
      }
    }
  },
  "settings": {
    "default_start_planet": "tatooine",
    "default_start_city": "mos_eisley",
    "max_travel_attempts": 3,
    "travel_timeout_seconds": 60.0,
    "verification_delay": 2.0,
    "shuttle_interaction_delay": 1.0
  }
}
```

### Travel Settings

The travel automation system can be configured with various settings:

```python
automation = get_travel_automation()
automation.max_attempts = 3                    # Max travel attempts
automation.timeout_seconds = 60.0              # Travel timeout
automation.verification_delay = 2.0            # Verification delay
automation.shuttle_interaction_delay = 1.0     # Shuttle interaction delay
```

## Logging

### Travel Events

All travel events are logged to `logs/travel/travel_YYYYMMDD.json`:

```json
{
  "timestamp": 1703123456.789,
  "event_type": "travel_start",
  "details": {
    "destination": "Artisan Trainer",
    "route_stops": 2,
    "travel_type": "trainer"
  }
}
```

### Event Types

- `travel_start`: Travel initiated
- `travel_success`: Successfully reached destination
- `travel_failed`: Travel failed
- `shuttle_interaction`: Shuttle interaction event
- `route_planned`: Route planning completed
- `requirement_check`: Requirement verification

## Testing

### Unit Tests

Comprehensive unit tests are available in `tests/test_travel_automation.py`:

```bash
python -m pytest tests/test_travel_automation.py -v
```

### Test Coverage

- Travel destination creation and validation
- Travel route planning and validation
- Travel state management
- Trainer travel functionality
- Quest travel functionality
- Unlock travel functionality
- Shuttle interaction testing
- Global function integration
- JSON serialization

### Integration Testing

The system integrates with existing components:

- **Navigator System**: Uses waypoint navigation for movement
- **Dialogue Detection**: Leverages dialogue detection for shuttle interactions
- **Waypoint Verification**: Uses existing position verification
- **Configuration System**: Loads from JSON configuration files

## Route Planning

### Shuttle Route Algorithm

The system uses a Breadth-First Search (BFS) algorithm to find optimal shuttle routes:

```python
def plan_shuttle_route(self, start_planet: str, start_city: str,
                      dest_planet: str, dest_city: str) -> Optional[TravelRoute]:
    # Build graph of shuttle connections
    graph = {}
    for planet, shuttles in self.shuttle_data.items():
        for shuttle in shuttles:
            node = (planet, shuttle["city"])
            graph[node] = []
            for dest in shuttle.get("destinations", []):
                graph[node].append((dest["planet"], dest["city"]))
    
    # Find shortest path using BFS
    queue = deque([(start, [start])])
    visited = set()
    
    while queue:
        node, path = queue.popleft()
        if node == dest:
            return self._build_route(path)
        # ... BFS logic
```

### Route Optimization

- **Shortest Path**: Finds the minimum number of transfers
- **Distance Calculation**: Calculates total route distance
- **Time Estimation**: Estimates travel time based on distance
- **Transfer Detection**: Identifies transfer points in routes

## Safety Features

### Error Handling

- **Route Validation**: Validates route existence before travel
- **Requirement Checking**: Verifies quest requirements before travel
- **Unlock Condition Verification**: Checks unlock conditions
- **Timeout Protection**: Prevents infinite travel loops
- **Exception Recovery**: Graceful handling of travel failures

### Travel Verification

- **Position Verification**: Validates arrival at destinations
- **Shuttle Interaction Verification**: Confirms successful shuttle travel
- **State Management**: Tracks travel progress and state
- **Retry Logic**: Automatic retry on failures

## Performance Optimization

### Caching

- **Route Caching**: Caches planned routes for reuse
- **Location Caching**: Caches current location information
- **Configuration Caching**: Caches loaded configuration data

### Efficiency Features

- **Lazy Loading**: Loads configuration only when needed
- **Singleton Pattern**: Single global instance for efficiency
- **Event Logging**: Efficient JSON-based event logging
- **Memory Management**: Proper cleanup of temporary data

## Future Enhancements

### Planned Features

1. **Advanced Route Planning**: A* pathfinding for complex routes
2. **Dynamic Shuttle Detection**: Real-time shuttle availability detection
3. **Multi-Objective Travel**: Travel to multiple destinations in sequence
4. **Travel Optimization**: AI-powered route optimization
5. **Real-time Updates**: Dynamic route updates based on game state

### Performance Improvements

1. **Parallel Processing**: Concurrent travel planning and execution
2. **Predictive Caching**: Cache frequently used routes
3. **Smart Retry Logic**: Intelligent retry strategies
4. **Performance Monitoring**: Real-time performance metrics

## Troubleshooting

### Common Issues

1. **No Route Found**: Check shuttle configuration and connectivity
2. **Travel Fails**: Verify destination coordinates and requirements
3. **Shuttle Interaction Fails**: Check dialogue detection settings
4. **Timeout Errors**: Increase timeout settings for longer routes

### Debug Information

Enable debug logging to troubleshoot travel issues:

```python
import logging
logging.getLogger('core.travel_automation').setLevel(logging.DEBUG)
```

### Log Analysis

Review travel logs to identify patterns:

```bash
tail -f logs/travel/travel_$(date +%Y%m%d).json
```

## API Reference

### Global Functions

- `get_travel_automation(config_file=None)`: Get global travel automation instance
- `travel_to_trainer(profession)`: Travel to profession trainer
- `travel_to_quest(quest_id)`: Travel to quest location
- `travel_to_unlock(unlock_id)`: Travel to unlock location
- `get_travel_status()`: Get current travel status

### TravelAutomation Methods

- `travel_to_trainer(profession)`: Travel to specific trainer
- `travel_to_quest(quest_id)`: Travel to quest location
- `travel_to_unlock(unlock_id)`: Travel to unlock location
- `plan_shuttle_route(start_planet, start_city, dest_planet, dest_city)`: Plan shuttle route
- `get_travel_status()`: Get current travel status

### Configuration

- `max_attempts`: Maximum travel attempts
- `timeout_seconds`: Travel timeout in seconds
- `verification_delay`: Position verification delay
- `shuttle_interaction_delay`: Shuttle interaction delay

## Integration Examples

### With Navigator System

```python
from core.travel_automation import get_travel_automation
from core.navigator import get_navigator

# Get instances
travel_automation = get_travel_automation()
navigator = get_navigator()

# Travel to trainer then navigate to exact location
success = travel_automation.travel_to_trainer("artisan")
if success:
    # Use navigator for precise positioning
    navigator.navigate_to_waypoint("artisan_trainer_exact")
```

### With Dialogue Detection

```python
from core.travel_automation import get_travel_automation
from core.dialogue_detector import get_dialogue_detector

# Get instances
travel_automation = get_travel_automation()
dialogue_detector = get_dialogue_detector()

# Travel with dialogue interaction
success = travel_automation.travel_to_quest("tatooine_artifact_hunt")
if success:
    # Handle quest dialogue
    dialogue_window = dialogue_detector.detect_dialogue_window()
    if dialogue_window:
        dialogue_detector.click_dialogue_option(1)
```

The travel automation system provides a robust foundation for automated multi-planet travel with comprehensive safety features, detailed logging, and seamless integration with existing systems. 