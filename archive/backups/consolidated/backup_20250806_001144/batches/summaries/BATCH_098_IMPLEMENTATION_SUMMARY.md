# Batch 098 - Quest Heatmap & Popular Paths Tracker

## Overview

Batch 098 implements a comprehensive quest heatmap and popular paths tracking system that analyzes session logs to visualize quest usage patterns and identify popular areas across all bot sessions. The system provides anonymized data visualization for admin use only, helping to improve route logic and fallback detection.

## Core Features

### 1. Quest Usage Tracking
- **Quest Event Tracking**: Records quest starts, completions, failures, and abandonments
- **Location Mapping**: Tracks planetary coordinates and city locations for each quest
- **Session Anonymization**: Ensures privacy by hashing session identifiers
- **Time-based Analysis**: Filters data by customizable time periods (7, 14, 30 days)

### 2. Popular Paths Detection
- **Travel Route Analysis**: Identifies most common travel paths between locations
- **Method Tracking**: Records travel methods (shuttle, direct, mount)
- **Duration Analysis**: Calculates average travel times for optimization
- **Path Frequency**: Ranks paths by usage frequency

### 3. Danger Zone Identification
- **Stuck Event Detection**: Identifies areas where the bot frequently gets stuck
- **Reason Analysis**: Categorizes stuck events (navigation_failed, quest_blocked, etc.)
- **Duration Tracking**: Records how long the bot remains stuck
- **Attempt Counting**: Tracks retry attempts for stuck situations

### 4. City Visit Heatmap
- **Location Frequency**: Tracks most visited cities and areas
- **Visit Type Analysis**: Categorizes visits (quest, travel, stuck, idle)
- **Duration Tracking**: Records time spent at each location
- **Coordinate Mapping**: Maps all visits to specific coordinates

### 5. Coordinate Heatmap Visualization
- **Planetary Heatmaps**: Visual representation of activity density per planet
- **Intensity Calculation**: Normalizes visit counts for visual scaling
- **Interactive Display**: Hover effects show detailed information
- **Multi-planet Support**: Supports all major SWG planets

## Technical Implementation

### Core Components

#### 1. QuestHeatmapTracker Class
```python
class QuestHeatmapTracker:
    """Tracks quest usage patterns and popular paths across all sessions."""
    
    def __init__(self, logs_dir: str = "logs", data_dir: str = "data/quest_heatmap", anonymize: bool = True)
    def process_session_logs(self)
    def get_quest_heatmap(self, days: int = 7) -> Dict[str, Any]
    def get_city_heatmap(self, days: int = 7) -> Dict[str, Any]
    def get_danger_zones(self, days: int = 7) -> Dict[str, Any]
    def get_popular_paths(self, days: int = 7) -> Dict[str, Any]
    def get_coordinate_heatmap(self, planet: str, days: int = 7) -> List[Dict[str, Any]]
    def get_weekly_stats(self) -> Dict[str, Any]
```

#### 2. Data Structures
```python
@dataclass
class QuestEvent:
    quest_id: str
    quest_name: str
    planet: str
    city: str
    coordinates: Tuple[int, int]
    timestamp: str
    action: str  # start, complete, fail, abandon
    session_hash: str  # anonymized session identifier
    duration_minutes: Optional[int] = None
    xp_gained: Optional[int] = None

@dataclass
class LocationVisit:
    planet: str
    city: str
    zone: str
    coordinates: Tuple[int, int]
    timestamp: str
    session_hash: str
    duration_minutes: int
    visit_type: str  # quest, travel, stuck, idle

@dataclass
class StuckEvent:
    planet: str
    city: str
    zone: str
    coordinates: Tuple[int, int]
    timestamp: str
    session_hash: str
    duration_minutes: int
    attempts: int
    reason: str  # navigation_failed, quest_blocked, etc.

@dataclass
class TravelPath:
    from_planet: str
    from_city: str
    from_coordinates: Tuple[int, int]
    to_planet: str
    to_city: str
    to_coordinates: Tuple[int, int]
    timestamp: str
    session_hash: str
    duration_minutes: int
    method: str  # shuttle, direct, mount
```

### 3. Data Processing Pipeline

#### Session Log Processing
- **File Discovery**: Automatically finds session log files in logs directory
- **JSON Parsing**: Processes session data and navigation events
- **Data Extraction**: Extracts quest events, location visits, and stuck events
- **Anonymization**: Hashes session IDs for privacy protection
- **Coordinate Extraction**: Handles various coordinate formats (dict, list, tuple)

#### Navigation Event Processing
- **Real-time Tracking**: Processes navigation_events.json for movement data
- **Path Progression**: Tracks movement between coordinates
- **Stuck Detection**: Identifies when bot gets stuck during navigation
- **Location Mapping**: Maps all navigation events to specific locations

### 4. Dashboard Integration

#### Admin Dashboard Routes
```python
@app.route("/admin/quest-heatmap")
def quest_heatmap_dashboard()

@app.route("/admin/quest-heatmap/process")
def process_quest_heatmap()

@app.route("/api/admin/quest-heatmap/weekly-stats")
def api_quest_heatmap_weekly_stats()

@app.route("/api/admin/quest-heatmap/quest-data")
def api_quest_heatmap_quest_data()

@app.route("/api/admin/quest-heatmap/city-data")
def api_quest_heatmap_city_data()

@app.route("/api/admin/quest-heatmap/danger-zones")
def api_quest_heatmap_danger_zones()

@app.route("/api/admin/quest-heatmap/popular-paths")
def api_quest_heatmap_popular_paths()

@app.route("/api/admin/quest-heatmap/coordinate-heatmap")
def api_quest_heatmap_coordinate_heatmap()

@app.route("/admin/quest-heatmap/clear-data", methods=['POST'])
def clear_quest_heatmap_data()
```

#### Dashboard Features
- **Modern UI**: Responsive design with gradient backgrounds and glass-morphism effects
- **Interactive Charts**: Real-time data visualization with JavaScript
- **Period Selection**: Filter data by 7, 14, or 30 days
- **Planet Selection**: Choose specific planets for coordinate heatmaps
- **Data Tables**: Sortable tables for quests, cities, danger zones, and paths
- **Loading States**: Visual feedback during data processing
- **Error Handling**: Graceful error handling with user-friendly messages

### 5. Data Storage

#### File Structure
```
data/quest_heatmap/
├── quest_events.json      # Quest event data
├── location_visits.json   # Location visit data
├── stuck_events.json      # Stuck event data
└── travel_paths.json      # Travel path data
```

#### Data Persistence
- **JSON Storage**: All data stored in human-readable JSON format
- **Automatic Loading**: Data automatically loaded on tracker initialization
- **Incremental Updates**: New data appended to existing files
- **Data Cleanup**: Automatic cleanup of old data (configurable retention)

## Key Features

### 1. Privacy Protection
- **Session Anonymization**: All session IDs are hashed using MD5
- **Admin-Only Access**: Dashboard restricted to admin users
- **No Personal Data**: Only anonymized usage patterns are tracked
- **Configurable Anonymization**: Can be disabled for debugging

### 2. Real-time Processing
- **Live Session Processing**: Processes session logs as they're created
- **Incremental Updates**: Only processes new data since last run
- **Background Processing**: Non-blocking data processing
- **Error Recovery**: Continues processing even if some files fail

### 3. Advanced Analytics
- **Time-based Filtering**: Analyze data for specific time periods
- **Geographic Analysis**: Track activity patterns across planets
- **Performance Metrics**: Calculate averages and trends
- **Pattern Recognition**: Identify common usage patterns

### 4. Route Optimization
- **Popular Paths**: Identify most efficient travel routes
- **Danger Zones**: Avoid areas where bot gets stuck
- **Travel Methods**: Optimize based on travel method efficiency
- **Duration Analysis**: Find fastest routes between locations

## Usage Instructions

### 1. Initial Setup
```bash
# Process existing session logs
python demo_batch_098_quest_heatmap.py

# Or manually process logs
curl -X GET http://localhost:8000/admin/quest-heatmap/process
```

### 2. Access Dashboard
- Navigate to `/admin/quest-heatmap` in the web dashboard
- Use the "Process Session Logs" button to analyze new data
- Select time periods and planets to filter data
- View interactive heatmaps and data tables

### 3. API Usage
```python
from core.quest_heatmap_tracker import quest_heatmap_tracker

# Get quest heatmap data
quest_data = quest_heatmap_tracker.get_quest_heatmap(days=7)

# Get city visit data
city_data = quest_heatmap_tracker.get_city_heatmap(days=7)

# Get danger zones
danger_data = quest_heatmap_tracker.get_danger_zones(days=7)

# Get popular paths
paths_data = quest_heatmap_tracker.get_popular_paths(days=7)

# Get coordinate heatmap for specific planet
coord_data = quest_heatmap_tracker.get_coordinate_heatmap("Tatooine", days=7)
```

### 4. Manual Data Addition
```python
# Add travel path
quest_heatmap_tracker.add_travel_path(
    from_location={"planet": "Tatooine", "city": "Mos Eisley", "x": 3600, "y": -4850},
    to_location={"planet": "Naboo", "city": "Theed", "x": 5000, "y": -3000},
    session_hash="session_123",
    duration_minutes=30,
    method="shuttle"
)

# Add stuck event
quest_heatmap_tracker.add_stuck_event(
    location={"planet": "Corellia", "city": "Coronet", "zone": "coronet_city", "x": 4000, "y": -2000},
    session_hash="session_456",
    duration_minutes=15,
    attempts=3,
    reason="quest_blocked"
)
```

## Testing

### 1. Unit Tests
```bash
python test_batch_098_quest_heatmap.py
```

### 2. Demo Script
```bash
python demo_batch_098_quest_heatmap.py
```

### 3. Test Coverage
- **Data Processing**: Tests session log parsing and data extraction
- **Anonymization**: Verifies session ID hashing
- **Heatmap Generation**: Tests all heatmap data generation methods
- **Error Handling**: Tests graceful handling of invalid data
- **Data Persistence**: Tests save/load functionality
- **Integration**: Tests complete workflow from processing to dashboard

## Benefits for Route Logic

### 1. Popular Path Optimization
- **Identify Efficient Routes**: Find most commonly used travel paths
- **Avoid Problem Areas**: Steer clear of frequently stuck locations
- **Method Selection**: Choose optimal travel methods based on success rates
- **Time Optimization**: Use fastest routes based on historical data

### 2. Fallback Detection
- **Stuck Pattern Recognition**: Identify areas where bot frequently gets stuck
- **Reason Analysis**: Understand why bot gets stuck (navigation, quest, etc.)
- **Retry Logic**: Implement smarter retry strategies based on stuck patterns
- **Alternative Routes**: Provide fallback paths when primary routes fail

### 3. Quest Optimization
- **Quest Success Rates**: Track which quests are completed successfully
- **Location Efficiency**: Find optimal quest locations
- **Time Analysis**: Identify quests that take too long
- **Resource Planning**: Optimize quest selection based on historical data

## Future Enhancements

### 1. Advanced Analytics
- **Machine Learning**: Implement ML models for route prediction
- **Real-time Alerts**: Notify when bot gets stuck in new areas
- **Performance Trends**: Track performance improvements over time
- **Predictive Analysis**: Predict optimal quest and route choices

### 2. Enhanced Visualization
- **3D Heatmaps**: Add 3D visualization for complex areas
- **Interactive Maps**: Full SWG world map integration
- **Real-time Updates**: Live dashboard updates during bot operation
- **Export Features**: Export data for external analysis

### 3. Integration Features
- **Discord Integration**: Send alerts to Discord when stuck
- **Email Reports**: Weekly performance reports via email
- **API Extensions**: RESTful API for external tools
- **Database Integration**: Move from JSON to database storage

## Security Considerations

### 1. Data Privacy
- **Session Anonymization**: All session data is anonymized
- **Admin Access Only**: Dashboard restricted to authorized users
- **No Personal Data**: Only usage patterns are tracked
- **Configurable Retention**: Automatic cleanup of old data

### 2. Access Control
- **Admin Dashboard**: Restricted access to quest heatmap
- **API Protection**: Admin-only API endpoints
- **Session Management**: Proper session handling
- **Error Logging**: Secure error logging without sensitive data

## Performance Considerations

### 1. Data Processing
- **Incremental Processing**: Only process new data
- **Background Processing**: Non-blocking data analysis
- **Memory Management**: Efficient data structures
- **File I/O Optimization**: Minimize disk operations

### 2. Dashboard Performance
- **Caching**: Cache frequently accessed data
- **Lazy Loading**: Load data on demand
- **Pagination**: Handle large datasets efficiently
- **Compression**: Compress data for faster loading

## Conclusion

Batch 098 successfully implements a comprehensive quest heatmap and popular paths tracking system that provides valuable insights into bot behavior patterns. The system's anonymized data collection, advanced analytics, and interactive dashboard help optimize route logic and improve fallback detection, ultimately enhancing the bot's performance and reliability.

The implementation includes robust testing, comprehensive documentation, and a user-friendly interface that makes it easy for administrators to analyze bot usage patterns and make data-driven decisions for optimization. 