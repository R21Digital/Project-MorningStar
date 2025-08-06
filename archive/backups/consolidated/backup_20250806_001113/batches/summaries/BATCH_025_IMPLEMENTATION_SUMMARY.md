# Batch 025 - Passive Learning Hook System

## Overview

Batch 025 implements a passive learning hook system that tracks session data like XP gain, damage dealt, and skill use frequency to inform future learning systems and combat auto-tuning. This system provides the foundation for data-driven combat optimization and build performance analysis.

## Goals

- ✅ Track XP gained per session (via OCR delta)
- ✅ Track which combat skills were used (and how often)
- ✅ Track approximate skill damage (via combat log parsing or XP per kill)
- ✅ Store data in session logs for analysis
- ✅ Lay foundation for combat auto-tuning (Batch 040+)
- ✅ Enable build performance review

## Files Created/Modified

### New Files
- `logs/session_tracker.py` - Main passive learning tracker implementation
- `logs/combat_usage_log.json` - Combat usage log with sample data
- `profiles/learned_combat_insights.json` - Learned combat insights and analysis
- `test_batch_025_passive_learning.py` - Comprehensive test suite

## Implementation Details

### Core Components

#### 1. PassiveLearningTracker Class
The main class that manages session tracking and learning:

**Key Features:**
- Session lifecycle management (start, record, end)
- Skill usage tracking with damage and XP
- Combat statistics (kills, deaths, damage dealt)
- XP monitoring and OCR integration
- Learned insights generation
- File persistence and data analysis

**Main Methods:**
- `start_session(session_id, mode)` - Start new combat session
- `end_session()` - End session and save data
- `record_skill_usage(skill_name, damage, xp_gained, success)` - Track skill usage
- `record_kill(xp_gained)` - Track kills and XP
- `record_death()` - Track deaths
- `update_xp(current_xp)` - Update XP level
- `scan_xp_from_screen()` - OCR XP scanning
- `get_session_status()` - Get current status
- `get_learned_insights()` - Get analyzed insights

#### 2. CombatSession Dataclass
Represents a combat session with comprehensive tracking:

```python
@dataclass
class CombatSession:
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    state: SessionState = SessionState.ACTIVE
    
    # XP tracking
    start_xp: int = 0
    current_xp: int = 0
    total_xp_gained: int = 0
    
    # Skill usage tracking
    skills_used: Dict[str, SkillUsage] = field(default_factory=dict)
    
    # Combat statistics
    total_damage_dealt: int = 0
    total_damage_taken: int = 0
    kills: int = 0
    deaths: int = 0
```

#### 3. SkillUsage Dataclass
Tracks individual skill performance metrics:

```python
@dataclass
class SkillUsage:
    skill_name: str
    usage_count: int = 0
    total_damage: int = 0
    average_damage: float = 0.0
    last_used: Optional[datetime] = None
    success_rate: float = 1.0
    xp_per_use: float = 0.0
```

### Data Storage Format

#### Combat Usage Log (`logs/combat_usage_log.json`)
Stores session data in the format specified in requirements:

```json
{
  "sessions": [
    {
      "session_id": "session_1733012345",
      "start_time": "2025-08-03T21:45:00.000000",
      "end_time": "2025-08-03T22:15:00.000000",
      "duration_minutes": 30.0,
      "state": "completed",
      "total_xp_gained": 12240,
      "total_damage_dealt": 45000,
      "kills": 24,
      "deaths": 0,
      "skills": {
        "headshot": {
          "usage_count": 48,
          "total_damage": 19200,
          "average_damage": 400.0,
          "success_rate": 0.95,
          "xp_per_use": 255.0
        }
      }
    }
  ],
  "total_sessions": 1,
  "total_xp": 12240
}
```

#### Learned Combat Insights (`profiles/learned_combat_insights.json`)
Stores analyzed data for combat optimization:

```json
{
  "skill_performance": {
    "headshot": {
      "total_uses": 48,
      "total_damage": 19200,
      "average_damage": 400.0,
      "success_rate": 0.95,
      "xp_efficiency": 255.0,
      "damage_per_second": 800.0,
      "xp_per_minute": 510.0
    }
  },
  "xp_efficiency": {
    "xp_per_minute": 408.0,
    "best_xp_skill": "burst_fire",
    "best_damage_skill": "headshot",
    "most_reliable_skill": "rifle_shot"
  },
  "combat_patterns": {
    "most_used_skill": "rifle_shot",
    "highest_damage_skill": "headshot",
    "most_efficient_skill": "burst_fire",
    "preferred_rotation": ["headshot", "burst_fire", "rifle_shot"]
  },
  "build_recommendations": {
    "primary_damage_skill": "headshot",
    "secondary_damage_skill": "burst_fire",
    "filler_skill": "rifle_shot",
    "recommended_rotation": ["headshot", "burst_fire", "rifle_shot"],
    "skill_priorities": {
      "headshot": "high",
      "burst_fire": "medium",
      "rifle_shot": "low"
    }
  }
}
```

### Key Features

#### 1. Session Management
- **Session Lifecycle**: Start, record, end with automatic data persistence
- **Session States**: Active, paused, completed, error states
- **Session Metadata**: Duration, location, mode, notes
- **Session Summary**: Comprehensive statistics and analysis

#### 2. Skill Usage Tracking
- **Usage Count**: Number of times each skill was used
- **Damage Tracking**: Total and average damage per skill
- **Success Rate**: Percentage of successful skill uses
- **XP Efficiency**: XP gained per skill usage
- **Performance Metrics**: Damage per second, XP per minute

#### 3. Combat Statistics
- **Damage Tracking**: Total damage dealt and taken
- **Kill/Death Tracking**: Combat outcome statistics
- **XP Monitoring**: XP gained from skills and kills
- **Session Duration**: Time-based performance metrics

#### 4. XP Monitoring
- **Manual Updates**: Direct XP level updates
- **OCR Integration**: Automatic XP scanning from screen
- **XP Patterns**: Multiple regex patterns for XP detection
- **XP Calculation**: Delta tracking for session XP gain

#### 5. Learned Insights
- **Skill Performance**: Comprehensive skill analysis
- **XP Efficiency**: Best skills for XP gain
- **Combat Patterns**: Usage patterns and preferences
- **Build Recommendations**: Optimized skill rotations
- **Performance Metrics**: Historical performance data

#### 6. Data Persistence
- **Combat Usage Log**: Session data storage
- **Learned Insights**: Analyzed performance data
- **Automatic Updates**: Real-time data analysis
- **File Management**: Robust file handling with error recovery

### Global Functions

For easy integration:

```python
# Start a new session
session_id = start_session("combat_session_001")

# Record skill usage
record_skill_usage("headshot", damage=400, xp_gained=255, success=True)

# Record combat events
record_kill(xp_gained=100)
record_death()

# Update XP
update_xp(1500)

# Get status and insights
status = get_session_status()
insights = get_learned_insights()

# End session
summary = end_session()
```

## Testing Results

All 11 tests pass successfully:

1. ✅ **Session Tracker Initialization** - Tracker loads and configures correctly
2. ✅ **Session Lifecycle** - Start, record, end workflow works
3. ✅ **Skill Usage Tracking** - Detailed skill statistics calculated correctly
4. ✅ **XP Tracking** - XP monitoring and calculation working
5. ✅ **Session Status** - Real-time status reporting functional
6. ✅ **Learned Insights** - Data analysis and insights generation working
7. ✅ **Skill Performance Analysis** - Individual skill analysis functional
8. ✅ **Global Functions** - Global API working correctly
9. ✅ **File Operations** - Data persistence and file management working
10. ✅ **Error Handling** - Graceful error handling and recovery
11. ✅ **Data Structures** - Dataclass functionality working correctly

## Usage Examples

### Basic Session Tracking

```python
from logs.session_tracker import start_session, record_skill_usage, end_session

# Start session
session_id = start_session("combat_session_001")

# Record combat activity
record_skill_usage("headshot", damage=400, xp_gained=255, success=True)
record_skill_usage("burst_fire", damage=400, xp_gained=382, success=True)
record_kill(xp_gained=100)

# End session and get summary
summary = end_session()
print(f"Session completed: {summary['total_xp_gained']} XP gained")
```

### Advanced Analytics

```python
from logs.session_tracker import get_learned_insights, get_skill_performance

# Get overall insights
insights = get_learned_insights()
print(f"Best XP skill: {insights['xp_efficiency']['best_xp_skill']}")
print(f"Most used skill: {insights['combat_patterns']['most_used_skill']}")

# Get specific skill performance
headshot_perf = get_skill_performance("headshot")
if headshot_perf:
    print(f"Headshot average damage: {headshot_perf['average_damage']}")
    print(f"Headshot success rate: {headshot_perf['success_rate']:.2%}")
```

### XP Monitoring

```python
from logs.session_tracker import update_xp, scan_xp_from_screen

# Manual XP update
update_xp(1500)

# Automatic XP scanning (requires OCR)
xp_value = scan_xp_from_screen()
if xp_value:
    print(f"Current XP: {xp_value}")
```

### Session Status Monitoring

```python
from logs.session_tracker import get_session_status

# Get real-time status
status = get_session_status()
if status["status"] != "no_active_session":
    print(f"Session: {status['session_id']}")
    print(f"Duration: {status['duration_minutes']:.1f} minutes")
    print(f"XP Gained: {status['total_xp_gained']}")
    print(f"Skills Used: {status['skills_used']}")
    print(f"Kills: {status['kills']}, Deaths: {status['deaths']}")
```

## Technical Implementation

### Data Flow
1. **Session Start** → Initialize tracking structures
2. **Combat Activity** → Record skill usage, kills, deaths
3. **XP Updates** → Track XP changes and gains
4. **Session End** → Calculate statistics and save data
5. **Insights Generation** → Analyze performance and update insights

### Performance Optimizations
- **Efficient Calculations**: Running averages and statistics
- **Minimal File I/O**: Batch updates and smart caching
- **Memory Management**: Clean session lifecycle
- **Error Recovery**: Graceful handling of file operations

### OCR Integration
- **Optional Dependency**: Works without Tesseract
- **Multiple Patterns**: Various XP display formats
- **Error Handling**: Graceful fallback when OCR fails
- **Screen Regions**: Configurable scanning areas

### File Management
- **Automatic Creation**: Directories and files created as needed
- **JSON Format**: Human-readable data storage
- **Error Recovery**: Robust file handling
- **Data Validation**: Type checking and validation

## Integration Points

### With Existing Systems
- **Combat Engine**: Integrates with rotation engine for skill tracking
- **Movement Systems**: Can track location-based performance
- **Mount Management**: Session context for travel efficiency
- **Quest Systems**: Session metadata for quest tracking

### Future Extensions (Batch 040+)
- **Combat Auto-tuning**: Use insights to optimize rotations
- **Build Performance Review**: Analyze build effectiveness
- **Skill Recommendations**: Suggest optimal skill usage
- **Performance Alerts**: Notify when performance drops
- **Trend Analysis**: Long-term performance tracking

## Foundation for Future Features

### Combat Auto-tuning
The learned insights provide the data foundation for:
- **Skill Priority Optimization**: Use success rates and damage data
- **Rotation Refinement**: Analyze usage patterns
- **Build Optimization**: Performance-based skill selection
- **Real-time Adaptation**: Dynamic combat adjustments

### Build Performance Review
Session data enables:
- **Build Comparison**: Performance across different builds
- **Skill Effectiveness**: Damage and XP efficiency analysis
- **Session Analysis**: Detailed performance breakdowns
- **Trend Tracking**: Long-term performance monitoring

## Conclusion

Batch 025 successfully implements a comprehensive passive learning hook system that provides:

- **Comprehensive Tracking**: XP, damage, skill usage, combat statistics
- **Data Persistence**: Robust file-based storage system
- **Real-time Analysis**: Live session monitoring and status
- **Learned Insights**: Automated performance analysis
- **Future Foundation**: Data foundation for combat auto-tuning
- **Extensible Design**: Clean API for future enhancements

The system is ready for production use and provides the essential data collection and analysis capabilities needed for advanced combat automation and build optimization features. 