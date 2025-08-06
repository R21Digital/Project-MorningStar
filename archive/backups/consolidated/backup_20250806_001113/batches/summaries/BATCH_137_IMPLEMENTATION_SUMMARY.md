# Batch 137 - MS11 Multi-Character Support (Same Account) Implementation Summary

## Overview

Batch 137 implements comprehensive multi-character support for MS11, enabling the bot to operate 2 characters simultaneously from the same account. The system provides dual-window logic, mode toggles, shared communication, and synchronized questing capabilities.

## Key Features Implemented

### 1. Multi-Character Management System
- **Character Registration**: Register and manage multiple character instances
- **Window Management**: Automatic window arrangement and activation
- **Mode Toggles**: Switch between main and support modes dynamically
- **Session Management**: Individual session tracking for each character

### 2. Dual-Window Logic (SWG Multi-Client Rules)
- **Window Detection**: Find and manage multiple game windows
- **Window Arrangement**: Automatic positioning of windows on screen
- **Window Activation**: Switch between character windows seamlessly
- **Window State Tracking**: Monitor window status and activity

### 3. Character Mode System
- **Main Mode**: Full automation with questing, combat, farming
- **Support Mode**: Stationary support (Medic, Dancer, Entertainer)
- **Dynamic Switching**: Change modes during runtime
- **Role Assignment**: Leader/Follower coordination

### 4. Inter-Character Communication
- **Message Queue**: Shared communication between instances
- **Position Synchronization**: Real-time position updates
- **Quest Synchronization**: Quest progress sharing
- **Command System**: Direct character-to-character commands

### 5. Enhanced Support Modes
- **Stationary Medic**: Healing and buffing in fixed location
- **Stationary Dancer**: Entertainment buffs in fixed location
- **Stationary Entertainer**: Entertainment services
- **Mobile Medic**: Following support with healing capabilities

### 6. Synchronized Questing
- **Quest Progress Sharing**: Main character shares quest updates
- **Support Following**: Support characters follow main to quest locations
- **Location Synchronization**: Real-time location tracking
- **Quest Coordination**: Coordinated quest completion

## Technical Implementation

### Core Components

#### 1. MultiCharacterManager (`core/multi_character_manager.py`)
```python
class MultiCharacterManager:
    """Manages multiple character instances on the same account."""
    
    def register_character(self, character_name: str, window_title: str, 
                          mode: CharacterMode, role: CharacterRole) -> bool
    def activate_character(self, character_name: str) -> bool
    def switch_character_mode(self, character_name: str, new_mode: CharacterMode) -> bool
    def send_message(self, sender: str, message_type: str, data: Dict[str, Any], 
                    priority: str = "normal") -> None
    def sync_quest_progress(self, character_name: str, quest_data: Dict[str, Any]) -> None
    def sync_position(self, character_name: str, position: Tuple[int, int], 
                     planet: str, city: str) -> None
```

#### 2. Enhanced Support Mode (`android_ms11/modes/enhanced_support_mode.py`)
```python
class EnhancedSupportMode:
    """Enhanced support mode with multi-character integration."""
    
    def start_support(self) -> bool
    def stop_support(self) -> bool
    def _support_loop(self) -> None
    def _process_messages(self) -> None
    def _apply_medic_buffs(self) -> None
    def _apply_medic_heals(self) -> None
```

#### 3. Multi-Character CLI (`cli/multi_character_cli.py`)
```python
class MultiCharacterCLI:
    """CLI tool for managing multi-character sessions."""
    
    def start_session(self, main_char: str, support_char: str, 
                     support_type: str = "medic") -> bool
    def stop_session(self) -> bool
    def get_status(self) -> Dict[str, Any]
    def send_command(self, target_char: str, command: str, data: Dict[str, Any] = None) -> bool
    def switch_mode(self, character_name: str, new_mode: str) -> bool
```

### Data Structures

#### CharacterInstance
```python
@dataclass
class CharacterInstance:
    character_name: str
    window_title: str
    mode: CharacterMode
    role: CharacterRole
    session_id: str
    window_handle: Optional[pygetwindow.Window] = None
    is_active: bool = False
    last_activity: datetime = None
    position: Optional[Tuple[int, int]] = None
    current_planet: str = ""
    current_city: str = ""
    status: str = "idle"
```

#### InterCharacterMessage
```python
@dataclass
class InterCharacterMessage:
    sender: str
    message_type: str  # "quest_update", "position", "status", "command"
    data: Dict[str, Any]
    timestamp: datetime
    priority: str = "normal"  # "high", "normal", "low"
```

### Configuration System

#### Multi-Character Config (`config/multi_character_config.json`)
```json
{
  "max_characters": 2,
  "quest_sync_enabled": true,
  "position_sync_enabled": true,
  "communication_port": 12345,
  "window_spacing": 50,
  "support_modes": ["medic", "dancer", "entertainer"],
  "main_modes": ["quest", "combat", "farming", "profession"],
  "window_management": {
    "auto_arrange": true,
    "spacing": 50,
    "minimize_inactive": false,
    "always_on_top": false
  },
  "synchronization": {
    "quest_sync": {"enabled": true, "sync_interval": 10, "auto_follow": true},
    "position_sync": {"enabled": true, "sync_interval": 5, "max_distance": 100},
    "status_sync": {"enabled": true, "sync_interval": 15}
  }
}
```

## Usage Instructions

### 1. Basic Session Management

#### Start a Multi-Character Session
```bash
# Using CLI tool
python cli/multi_character_cli.py --start MainChar SupportChar medic

# Interactive mode
python cli/multi_character_cli.py --interactive
```

#### Monitor Session Status
```bash
python cli/multi_character_cli.py --status
```

#### Stop Session
```bash
python cli/multi_character_cli.py --stop
```

### 2. Interactive CLI Commands
```
> start MainChar SupportChar medic
> status
> switch MainChar support
> command SupportChar follow
> monitor 3600
> quit
```

### 3. Programmatic Usage

#### Register Characters
```python
from core.multi_character_manager import multi_character_manager, CharacterMode, CharacterRole

# Register main character
multi_character_manager.register_character(
    character_name="MainChar",
    window_title="SWG - MainChar",
    mode=CharacterMode.MAIN,
    role=CharacterRole.LEADER
)

# Register support character
multi_character_manager.register_character(
    character_name="SupportChar",
    window_title="SWG - SupportChar",
    mode=CharacterMode.SUPPORT,
    role=CharacterRole.FOLLOWER
)
```

#### Start Enhanced Support
```python
from android_ms11.modes.enhanced_support_mode import EnhancedSupportMode

support = EnhancedSupportMode("SupportChar", "medic")
support.start_support()
```

#### Send Messages
```python
# Send position update
multi_character_manager.sync_position(
    character_name="MainChar",
    position=(100, 200),
    planet="Naboo",
    city="Theed"
)

# Send quest update
multi_character_manager.sync_quest_progress("MainChar", {
    "quest_name": "Demo Quest",
    "status": "active",
    "location": {"planet": "Naboo", "city": "Theed"}
})
```

### 4. Support Mode Types

#### Stationary Medic
- Buffs every 5 minutes
- Heals every 1 minute
- Stays in fixed location
- Range: 50 for buffs, 30 for heals

#### Stationary Dancer
- Dance buffs every 3 minutes
- No healing capabilities
- Stays in fixed location
- Range: 40 for buffs

#### Stationary Entertainer
- Entertainment buffs every 4 minutes
- No healing capabilities
- Stays in fixed location
- Range: 45 for buffs

#### Mobile Medic
- Same as stationary medic
- Follows main character
- Can move to quest locations

## Integration with Existing Systems

### 1. Session Manager Integration
- Each character has its own SessionManager instance
- Individual session tracking and logging
- Separate action logs and performance metrics

### 2. Window Management Integration
- Uses existing `utils/window_finder.py` functionality
- Extends with multi-window arrangement
- Integrates with `pygetwindow` and `pyautogui`

### 3. Support Mode Integration
- Extends existing support mode functionality
- Integrates with `android_ms11.core` modules
- Uses existing follow, assist, and party managers

### 4. Communication Integration
- Socket-based inter-process communication
- Message queue system for character coordination
- Priority-based message handling

## Demo and Testing

### Run the Demo
```bash
python demo_batch_137_multi_character.py
```

### Demo Features
1. **Multi-Character Registration**: Register main and support characters
2. **Enhanced Support Mode**: Start and manage support functionality
3. **Inter-Character Communication**: Send messages and updates
4. **Mode Switching**: Switch between main and support modes
5. **CLI Functionality**: Test command-line interface
6. **Synchronized Questing**: Demonstrate quest coordination

## Safety and Monitoring

### 1. Safety Features
- **Maximum Session Duration**: Configurable timeout (default: 2 hours)
- **AFK Detection**: Automatic detection of inactivity
- **Emergency Stop**: Quick shutdown capability
- **Auto Cleanup**: Automatic resource cleanup

### 2. Monitoring
- **Real-time Status**: Live character status monitoring
- **Performance Metrics**: Track buffs, heals, and activity
- **Communication Logs**: Message queue monitoring
- **Window State Tracking**: Window status and activity

### 3. Error Handling
- **Graceful Degradation**: Continue operation on partial failures
- **Error Recovery**: Automatic retry mechanisms
- **Resource Cleanup**: Proper cleanup on errors
- **Logging**: Comprehensive error logging

## Configuration Options

### Character Profiles
```json
{
  "character_profiles": {
    "main_character": {
      "name": "MainChar",
      "window_title": "SWG - MainChar",
      "mode": "main",
      "role": "leader",
      "default_mode": "quest"
    },
    "support_character": {
      "name": "SupportChar",
      "window_title": "SWG - SupportChar",
      "mode": "support",
      "role": "follower",
      "default_mode": "medic"
    }
  }
}
```

### Support Configurations
```json
{
  "support_configs": {
    "medic": {
      "buff_interval": 300,
      "heal_interval": 60,
      "buff_range": 50,
      "heal_range": 30,
      "buffs": ["heal_health", "heal_action", "heal_mind"],
      "stationary": true,
      "follow_leader": false
    }
  }
}
```

## Key Benefits

### 1. Efficiency
- **Dual Automation**: Run two characters simultaneously
- **Coordinated Activities**: Synchronized questing and combat
- **Reduced Manual Work**: Automated support functions

### 2. Flexibility
- **Mode Switching**: Change roles dynamically
- **Configurable Support**: Multiple support types available
- **Adaptive Behavior**: Support follows main character

### 3. Safety
- **Comprehensive Monitoring**: Real-time status tracking
- **Error Recovery**: Robust error handling
- **Resource Management**: Proper cleanup and resource management

### 4. Integration
- **Existing Systems**: Seamless integration with current MS11
- **Extensible Design**: Easy to add new support types
- **Modular Architecture**: Clean separation of concerns

## Future Enhancements

### 1. Advanced Support Types
- **Combat Support**: Specialized combat assistance
- **Crafting Support**: Resource gathering and crafting
- **Trading Support**: Automated trading and market operations

### 2. Enhanced Coordination
- **Group Formation**: Automatic group management
- **Role Rotation**: Dynamic role switching
- **Advanced AI**: Machine learning for better coordination

### 3. Monitoring and Analytics
- **Performance Dashboard**: Web-based monitoring interface
- **Analytics**: Detailed performance analysis
- **Alerting**: Automated alerts for issues

### 4. Configuration Management
- **Web Interface**: Browser-based configuration
- **Profile Management**: Save and load character profiles
- **Template System**: Pre-configured setups

## Troubleshooting

### Common Issues

#### 1. Window Not Found
- Ensure game windows are open and visible
- Check window titles match configuration
- Verify SWG client is running

#### 2. Communication Errors
- Check if port 12345 is available
- Ensure firewall allows local connections
- Verify network configuration

#### 3. Support Mode Not Starting
- Check character registration
- Verify support type configuration
- Ensure window activation

#### 4. Mode Switching Fails
- Verify character exists in manager
- Check mode configuration
- Ensure proper role assignment

### Debug Commands
```bash
# Check status
python cli/multi_character_cli.py --status

# Monitor session
python cli/multi_character_cli.py --monitor 300

# Interactive debugging
python cli/multi_character_cli.py --interactive
```

## Conclusion

Batch 137 successfully implements comprehensive multi-character support for MS11, providing:

- **Dual-window logic** following SWG multi-client rules
- **Flexible mode toggles** between main and support modes
- **Robust communication** between character instances
- **Synchronized questing** with support following main character
- **Enhanced support modes** for various character types
- **Comprehensive CLI tools** for session management
- **Safety and monitoring** features for reliable operation

The system is designed for extensibility and can be easily enhanced with additional support types, coordination features, and monitoring capabilities. The modular architecture ensures clean integration with existing MS11 systems while providing powerful new multi-character capabilities. 