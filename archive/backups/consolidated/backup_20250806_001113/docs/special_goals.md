# Special Goals & Unlock Paths System

## Overview

The Special Goals & Unlock Paths System provides comprehensive tracking and automation for long-term character development goals in the game. This system focuses on unlockable content such as character slots, key quests, token loops, and reputation-based unlocks.

## Features

### Core Functionality
- **Goal Tracking**: Monitor progress on special goals with detailed requirement checking
- **Priority Management**: Automatic goal prioritization based on importance and requirements
- **Navigation Integration**: Seamless integration with the navigation and travel systems
- **Progress Logging**: Comprehensive JSON-based logging for goal events and completions
- **Requirement Validation**: Real-time checking of level, reputation, quest, skill, and collection requirements

### Goal Types
- **Character Slots**: Unlock additional character slots through reputation and quest completion
- **Key Quests**: Complete critical quests to unlock new areas and content
- **Token Loops**: Establish sustainable token farming loops for Galactic Fortitude
- **Reputation Grinds**: Build reputation to unlock exclusive areas and guilds
- **Skill Mastery**: Achieve skill milestones for character progression
- **Collection Complete**: Complete collection sets for rewards and unlocks
- **Unlock Paths**: Access exclusive areas and content through various requirements

### Priority Levels
- **Critical**: Mustafar key quest, fourth character slot unlock
- **High**: Third character slot unlock, Jedi knowledge access
- **Medium**: Token loops, merchant guild access
- **Low**: Basic unlock paths and reputation grinds

## Architecture

### Core Classes

#### SpecialGoals
The main class that manages the special goals system.

**Key Methods**:
```python
def load_goals(self) -> None
def check_goal_requirements(self, goal_name: str) -> Dict[str, Any]
def start_goal(self, goal_name: str) -> bool
def work_on_current_goal(self) -> bool
def get_available_goals(self, priority: Optional[GoalPriority] = None) -> List[SpecialGoal]
def get_goal_status(self) -> Dict[str, Any]
```

#### Data Structures

**SpecialGoal**:
```python
@dataclass
class SpecialGoal:
    name: str
    goal_type: GoalType
    description: str
    priority: GoalPriority
    planet: str
    zone: str
    coordinates: Tuple[int, int]
    requirements: List[GoalRequirement]
    rewards: List[str]
    estimated_time_hours: Optional[float] = None
    unlock_conditions: Optional[Dict[str, Any]] = None
    quest_chain: Optional[List[str]] = None
    collection_targets: Optional[List[str]] = None
```

**GoalRequirement**:
```python
@dataclass
class GoalRequirement:
    type: str  # "level", "reputation", "quest", "skill", "collection", "unlock"
    target: str  # Specific target (e.g., "level_50", "tatooine_1000")
    description: str
    current_progress: Optional[Union[int, float, str]] = None
    required_progress: Optional[Union[int, float, str]] = None
```

**GoalProgress**:
```python
@dataclass
class GoalProgress:
    goal_name: str
    status: GoalStatus
    current_step: Optional[str] = None
    steps_completed: int = 0
    total_steps: int = 0
    start_time: Optional[datetime] = None
    completion_time: Optional[datetime] = None
    last_updated: Optional[datetime] = None
```

### Enums

**GoalType**:
```python
class GoalType(Enum):
    CHARACTER_SLOT = "character_slot"
    KEY_QUEST = "key_quest"
    TOKEN_LOOP = "token_loop"
    REPUTATION_GRIND = "reputation_grind"
    SKILL_MASTERY = "skill_mastery"
    COLLECTION_COMPLETE = "collection_complete"
    UNLOCK_PATH = "unlock_path"
```

**GoalStatus**:
```python
class GoalStatus(Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    LOCKED = "locked"
```

**GoalPriority**:
```python
class GoalPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
```

## Configuration

### Goals Configuration File
**Location**: `data/goals.json`

**Structure**:
```json
{
  "goals": [
    {
      "name": "Third Character Slot Unlock",
      "type": "character_slot",
      "description": "Unlock the third character slot through reputation and quest completion",
      "priority": "high",
      "planet": "tatooine",
      "zone": "mos_eisley",
      "coordinates": [100, 200],
      "requirements": [
        {
          "type": "reputation",
          "target": "tatooine_2000",
          "description": "Reach 2000 reputation on Tatooine",
          "required_progress": 2000
        },
        {
          "type": "quest",
          "target": "tatooine_artifact_hunt",
          "description": "Complete the Tatooine Artifact Hunt quest",
          "required_progress": "completed"
        },
        {
          "type": "level",
          "target": "level_25",
          "description": "Reach character level 25",
          "required_progress": 25
        }
      ],
      "rewards": ["third_character_slot", "tatooine_cantina_access"],
      "estimated_time_hours": 8.0,
      "quest_chain": ["tatooine_artifact_hunt", "tatooine_reputation_grind"]
    }
  ]
}
```

## Usage Examples

### Basic Usage

```python
from core.special_goals import get_special_goals, start_special_goal, work_on_current_goal

# Get the special goals system
goals_system = get_special_goals()

# Check available goals
available_goals = goals_system.get_available_goals()
print(f"Available goals: {len(available_goals)}")

# Start a goal
if available_goals:
    goal_name = available_goals[0].name
    success = start_special_goal(goal_name)
    if success:
        print(f"Started goal: {goal_name}")

# Work on current goal
progress_made = work_on_current_goal()
if progress_made:
    print("Made progress on current goal")
```

### Goal Status Monitoring

```python
from core.special_goals import get_special_goals_status

# Get current status
status = get_special_goals_status()
print(f"Total goals: {status['total_goals']}")
print(f"Active goals: {status['active_goals']}")
print(f"Completed goals: {status['completed_goals']}")

# Check specific goal progress
if status['current_goal']:
    current_goal = status['current_goal']
    print(f"Current goal: {current_goal['name']}")
    print(f"Progress: {current_goal['steps_completed']}/{current_goal['total_steps']}")
```

### Goal Filtering

```python
from core.special_goals import list_special_goals, GoalType, GoalPriority

# List character slot goals
character_slot_goals = list_special_goals(goal_type=GoalType.CHARACTER_SLOT)
for goal in character_slot_goals:
    print(f"Character slot goal: {goal.name}")

# List high priority goals
high_priority_goals = list_special_goals(priority=GoalPriority.HIGH)
for goal in high_priority_goals:
    print(f"High priority goal: {goal.name}")
```

### Requirement Checking

```python
from core.special_goals import get_special_goals

goals_system = get_special_goals()

# Check if a goal's requirements are met
requirements_check = goals_system.check_goal_requirements("Third Character Slot Unlock")
if requirements_check['all_requirements_met']:
    print("All requirements met for Third Character Slot Unlock")
else:
    print("Requirements not met:")
    for req in requirements_check['requirements']:
        if not req['met']:
            print(f"  - {req['requirement']}")
```

## Integration

### Navigation Integration
The special goals system integrates with the navigation system from Batch 002:

```python
# Travel to goal location
navigator = get_navigator()
waypoint = f"{goal.planet}/{goal.zone}/{goal.coordinates[0]},{goal.coordinates[1]}"
success = navigator.navigate_to_waypoint(waypoint)
```

### Travel Integration
Integration with the travel automation system from Batch 003:

```python
# Travel to unlock location
travel_automation = get_travel_automation()
success = travel_automation.travel_to_unlock(f"{goal.planet}_{goal.zone}_access")
```

### Dialogue Integration
Integration with the dialogue detection system from Batch 001:

```python
# Interact with goal
dialogue_detector = get_dialogue_detector()
dialogue_window = dialogue_detector.wait_for_dialogue(timeout=5.0)
if dialogue_window:
    # Look for goal-related options
    for i, option in enumerate(dialogue_window.options, 1):
        if "accept" in option.lower() or "start" in option.lower():
            dialogue_detector.click_dialogue_option(i)
            break
```

### Collection Integration
Integration with the collection tracker from Batch 004:

```python
# Check collection requirements
collection_tracker = get_collection_tracker()
if goal.collection_targets:
    for collection_name in goal.collection_targets:
        # Check if collection is complete
        collection_status = collection_tracker.get_collection_status()
        # Process collection completion
```

## Logging

### Log Structure
Special goals events are logged to `logs/special_goals/special_goals_YYYYMMDD.json`:

```json
{
  "timestamp": "2024-01-01T12:00:00",
  "event_type": "goal_started",
  "data": {
    "goal_name": "Third Character Slot Unlock",
    "goal_type": "character_slot",
    "priority": "high",
    "start_time": "2024-01-01T12:00:00"
  }
}
```

### Event Types
- `goals_loaded`: Goals loaded from configuration
- `goal_started`: Goal started successfully
- `goal_work_started`: Started working on a goal
- `goal_progress_made`: Made progress on current goal
- `goal_completed`: Goal completed successfully
- `goal_interaction_success`: Successfully interacted with goal
- `goal_interaction_failed`: Failed to interact with goal
- `goal_navigation_failed`: Failed to navigate to goal location

## Mode Integration

### Special Goals Mode
The system includes a dedicated mode that can be activated with `--mode special-goals`:

```bash
python src/main.py --mode special-goals
```

**Mode Behavior**:
1. Check for current active goal
2. If no active goal, find available goals and start the highest priority one
3. Work on the current goal using navigation and interaction systems
4. Track progress and log events
5. Complete goals when all requirements are met

### Mode Handler
The mode is registered in `src/main.py`:

```python
MODE_HANDLERS = {
    # ... other modes ...
    "special-goals": special_goals_mode.run,
}
```

## Safety Features

### Requirement Validation
- All goals require validation before starting
- Real-time requirement checking during goal execution
- Graceful handling of unmet requirements

### Navigation Safety
- Fallback navigation if travel automation fails
- Timeout protection for navigation attempts
- Error recovery for failed navigation

### Progress Tracking
- Comprehensive progress tracking for each goal
- Automatic completion detection
- State persistence across sessions

## Performance Optimizations

### Caching
- Goal data cached in memory after loading
- Requirement checking results cached
- Progress state maintained in memory

### Efficient Navigation
- Direct navigation to goal coordinates
- Integration with existing travel systems
- Optimized route planning for goal locations

## Testing

### Unit Tests
Comprehensive unit tests in `tests/test_special_goals.py`:

```bash
pytest tests/test_special_goals.py -v
```

**Test Coverage**:
- Goal data structure validation
- Goal loading and configuration
- Requirement checking logic
- Goal starting and progress tracking
- Navigation and interaction integration
- JSON serialization
- Singleton pattern
- Global convenience functions

### Integration Tests
Tests for full goal lifecycle:

```python
def test_full_goal_lifecycle(self):
    """Test a complete goal lifecycle from start to completion."""
    # Start goal
    success = goals.start_goal("Test Goal")
    assert success is True
    
    # Work on goal
    work_success = goals.work_on_current_goal()
    assert work_success is True
    
    # Verify completion
    assert goals.progress["Test Goal"].status == GoalStatus.COMPLETED
```

## Future Enhancements

### Planned Features
- **Goal Chains**: Sequential goal dependencies
- **Dynamic Requirements**: Requirements that change based on game state
- **Goal Templates**: Reusable goal configurations
- **Advanced Analytics**: Detailed goal completion analytics
- **Multi-Character Support**: Goal tracking across multiple characters

### Integration Plans
- **Quest System Integration**: Direct integration with quest completion tracking
- **Reputation System**: Real-time reputation monitoring
- **Skill System**: Integration with skill progression tracking
- **Collection System**: Enhanced collection requirement checking

## Conclusion

The Special Goals & Unlock Paths System provides a comprehensive framework for tracking and automating long-term character development goals. With its modular architecture, extensive integration capabilities, and robust testing, it serves as a foundation for advanced goal-oriented gameplay automation.

The system successfully integrates with all previous batch implementations (dialogue detection, navigation, travel automation, and collection tracking) to provide a complete solution for character progression and unlock management. 