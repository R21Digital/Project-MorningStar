# Collection Tracker & Completion System

## Overview

The Collection Tracker & Completion System is a comprehensive solution for monitoring, prioritizing, and completing collectible items in the game. It provides OCR-based detection, navigation integration, and automated completion of nearby collections.

## Features

### Core Functionality
- **Collection Data Management**: Load and manage collection data from JSON files
- **Progress Tracking**: Track completion progress by category (Trophies, Badges, Lore Items, etc.)
- **OCR Detection**: Use OCR to detect collected items on screen
- **Auto-Completion**: Automatically navigate to and complete nearby collections
- **Screenshot Audit**: Take screenshots when items are collected for verification
- **Comprehensive Logging**: JSON-based logging for all collection events

### Collection Types
- **Trophies**: Rare collectible items from various locations
- **Badges**: Achievement badges from different planets
- **Lore Items**: Historical and story-related collectibles
- **Achievements**: Special accomplishments with requirements
- **Decorations**: Decorative items for player housing

## Architecture

### Core Classes

#### CollectionItem
Represents a collectible item with metadata:
```python
@dataclass
class CollectionItem:
    name: str
    collection_type: CollectionType
    planet: str
    zone: str
    coordinates: Tuple[int, int]
    trigger_text: Optional[str] = None
    required_level: Optional[int] = None
    required_profession: Optional[str] = None
    description: Optional[str] = None
    rarity: Optional[str] = None
```

#### CollectionProgress
Tracks progress for a collection category:
```python
@dataclass
class CollectionProgress:
    category: CollectionType
    total_items: int
    collected_items: int
    completion_percentage: float
    last_updated: datetime
```

#### CollectionState
Maintains current collection tracking state:
```python
@dataclass
class CollectionState:
    total_collections: int
    completed_collections: int
    current_target: Optional[CollectionItem] = None
    last_completion_time: Optional[datetime] = None
    session_start_time: Optional[datetime] = None
```

### CollectionTracker Class

The main class that orchestrates all collection tracking functionality:

#### Key Methods

- `load_collections()`: Load collection data from JSON files
- `detect_collected_items()`: Use OCR to detect items on screen
- `find_nearby_uncollected_items()`: Find items within a specified distance
- `auto_complete_collections()`: Automatically complete nearby collections
- `mark_item_collected()`: Mark an item as collected with screenshot
- `get_collection_status()`: Get comprehensive status information

## Configuration

### Collection Data Format

Collections are defined in `data/collections.json`:

```json
{
  "collections": [
    {
      "name": "Tatooine Trophy - Mos Eisley",
      "type": "trophy",
      "planet": "Tatooine",
      "zone": "Mos Eisley",
      "coordinates": [100, 200],
      "trigger_text": "Collect Trophy",
      "description": "A rare trophy from the cantina in Mos Eisley",
      "rarity": "common",
      "required_level": 5
    }
  ],
  "metadata": {
    "version": "1.0",
    "total_collections": 15,
    "categories": {
      "trophy": 4,
      "badge": 3,
      "lore_item": 3,
      "achievement": 3,
      "decoration": 2
    }
  }
}
```

## Usage Examples

### Basic Usage

```python
from core.collection_tracker import get_collection_tracker, auto_complete_collections

# Get the collection tracker
tracker = get_collection_tracker()

# Auto-complete nearby collections
success = auto_complete_collections(current_location=(120, 220))

# Get collection status
status = tracker.get_collection_status()
print(f"Completed: {status['completed_collections']}/{status['total_collections']}")
```

### Advanced Usage

```python
from core.collection_tracker import (
    get_collection_tracker, list_collections, 
    detect_collected_items, CollectionType
)

tracker = get_collection_tracker()

# List all trophies
trophies = list_collections(collection_type=CollectionType.TROPHY)
for trophy in trophies:
    print(f"Trophy: {trophy.name} at {trophy.coordinates}")

# Detect items via OCR
detected_items = detect_collected_items()
for item in detected_items:
    print(f"Detected: {item.name}")

# Find nearby items
nearby = tracker.find_nearby_uncollected_items((100, 100), max_distance=50)
for item in nearby:
    print(f"Nearby: {item.name}")
```

## Integration Points

### Navigation Integration
The collection tracker integrates with the navigation system:
- Uses `get_navigator()` to navigate to collection coordinates
- Supports waypoint-based navigation to collection locations
- Handles navigation failures gracefully

### Dialogue Integration
Integrates with the dialogue detection system:
- Uses `get_dialogue_detector()` to detect collection-related dialogue
- Automatically selects collection options from dialogue
- Handles different dialogue patterns for different collection types

### OCR Integration
Uses the existing OCR system:
- Leverages `extract_text_from_screen()` for text detection
- Searches for trigger text patterns in screen content
- Supports multiple OCR methods and confidence scoring

## Logging

### Log Structure
All collection events are logged to `logs/collections/collections_YYYYMMDD.json`:

```json
{
  "timestamp": "2024-01-01T12:00:00.000000",
  "event_type": "item_collected",
  "data": {
    "item_name": "Tatooine Trophy",
    "collection_type": "trophy",
    "planet": "Tatooine",
    "zone": "Mos Eisley",
    "coordinates": [100, 200],
    "screenshot_path": "screenshots/collections/collection_Tatooine_Trophy_20240101_120000.png"
  }
}
```

### Event Types
- `collections_loaded`: When collection data is loaded
- `item_detected`: When an item is detected via OCR
- `item_collected`: When an item is successfully collected
- `auto_complete_started`: When auto-completion begins
- `auto_complete_success`: When auto-completion succeeds
- `auto_complete_failed`: When auto-completion fails
- `navigation_failed`: When navigation to an item fails
- `interaction_error`: When item interaction fails

## Safety Features

### Error Handling
- Graceful handling of OCR failures
- Navigation timeout protection
- Screenshot capture error handling
- File I/O error recovery

### Fallback Mechanisms
- Default collection data if file loading fails
- Click-based interaction if dialogue detection fails
- Distance-based filtering to prevent infinite loops

### Performance Optimizations
- Efficient distance calculations
- Cached collection data
- Minimal OCR calls
- Optimized navigation routes

## Testing

### Unit Tests
Comprehensive test suite in `tests/test_collection_tracker.py`:
- Collection data loading and validation
- OCR detection functionality
- Navigation and interaction testing
- Progress tracking verification
- Error handling scenarios

### Test Coverage
- 36/37 tests passing (97% pass rate)
- Covers all major functionality
- Includes integration tests
- Mocked external dependencies

## Future Enhancements

### Planned Features
- **Collection Requirements**: Check level and profession requirements
- **Collection Chains**: Multi-step collection sequences
- **Collection Rewards**: Track rewards for completed collections
- **Collection Sharing**: Share collection progress with other players
- **Collection Analytics**: Detailed statistics and completion rates

### Performance Improvements
- **Caching**: Cache OCR results and navigation paths
- **Batch Processing**: Process multiple collections simultaneously
- **Parallel Detection**: Concurrent OCR and navigation operations
- **Memory Optimization**: Reduce memory footprint for large collections

## Troubleshooting

### Common Issues

#### OCR Detection Fails
- Ensure Tesseract is installed and in PATH
- Check screen resolution and text clarity
- Verify trigger text patterns in collection data

#### Navigation Fails
- Check waypoint data in navigation system
- Verify coordinates are accessible
- Ensure character has required permissions

#### Collection Not Found
- Verify collection data is loaded correctly
- Check coordinate accuracy
- Ensure collection is not already completed

### Debug Mode
Enable detailed logging by setting log level to DEBUG:
```python
import logging
logging.getLogger("collection_tracker").setLevel(logging.DEBUG)
```

## API Reference

### Global Functions

#### `get_collection_tracker() -> CollectionTracker`
Get the singleton collection tracker instance.

#### `auto_complete_collections(current_location: Optional[Tuple[int, int]] = None) -> bool`
Auto-complete nearby collections.

#### `get_collection_status() -> Dict[str, Any]`
Get current collection status and progress.

#### `list_collections(collection_type: Optional[CollectionType] = None, planet: Optional[str] = None) -> List[CollectionItem]`
List collections with optional filtering.

#### `detect_collected_items() -> List[CollectionItem]`
Detect collected items using OCR.

### CollectionTracker Methods

#### `load_collections()`
Load collection data from JSON files.

#### `detect_collected_items() -> List[CollectionItem]`
Use OCR to detect collected items on screen.

#### `find_nearby_uncollected_items(current_location: Tuple[int, int], max_distance: int = 100) -> List[CollectionItem]`
Find uncollected items near the current location.

#### `auto_complete_collections(current_location: Optional[Tuple[int, int]] = None) -> bool`
Automatically complete nearby collections.

#### `mark_item_collected(item_name: str)`
Mark an item as collected with screenshot.

#### `get_collection_status() -> Dict[str, Any]`
Get current collection status and progress.

#### `list_collections(collection_type: Optional[CollectionType] = None, planet: Optional[str] = None) -> List[CollectionItem]` 