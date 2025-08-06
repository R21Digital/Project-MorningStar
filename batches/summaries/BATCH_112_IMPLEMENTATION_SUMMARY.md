# Batch 112 - Guild Alert System + Priority Communication

## Overview

Batch 112 implements a comprehensive guild alert system that detects guild member whispers, sends priority Discord notifications, and provides AI-enabled auto-replies. The system integrates seamlessly with the existing Discord relay and session management infrastructure.

## Features Implemented

### 1. Guild Member Detection
- **Guild Roster Management**: Load and manage guild member roster from JSON configuration
- **Role-Based Detection**: Identify guild leaders, officers, and regular members
- **Case-Insensitive Matching**: Handle player names regardless of case
- **Dynamic Roster Updates**: Add/remove guild members at runtime

### 2. Priority Alert System
- **High Priority**: Guild leaders and officers automatically get high priority
- **Medium Priority**: Messages containing urgent keywords (urgent, emergency, help, assist, raid, event)
- **Low Priority**: Regular guild member messages
- **Visual Indicators**: Discord messages show priority with emojis and colors

### 3. Discord Integration
- **Priority Notifications**: Guild messages get special Discord embeds with priority indicators
- **Color-Coded Alerts**: Red for high priority, orange for medium, blue for low
- **Auto-Reply Information**: Discord embeds include auto-reply details
- **Enhanced Relay**: Updated Discord relay to handle guild alerts with priority indicators

### 4. Auto-Reply System
- **Role-Based Templates**: Different auto-replies for leaders, officers, and members
- **Configurable**: Enable/disable auto-replies via configuration
- **Context-Aware**: Templates include sender name for personalization
- **RP-Friendly**: Professional and friendly response templates

### 5. Session Analytics Integration
- **Guild Alert Tracking**: Record all guild alerts in session logs
- **Analytics Dashboard**: Track alerts by type, priority, and auto-replies sent
- **Performance Metrics**: Include guild alert statistics in session performance data
- **Export Functionality**: Export guild alerts to JSON for analysis

## Files Created/Modified

### New Files
- `modules/guild_alert_system.py` - Core guild alert system implementation
- `config/guild_config.json` - Guild configuration with sample members
- `demo_batch_112_guild_alert_system.py` - Comprehensive demo script
- `test_batch_112_guild_alert_system.py` - Complete test suite

### Modified Files
- `discord_relay.py` - Enhanced with guild alert integration
- `core/session_manager.py` - Added guild alert tracking and analytics

## Technical Implementation

### Core Classes

#### GuildAlertSystem
```python
class GuildAlertSystem:
    """Handles guild member detection and priority alert system."""
    
    def __init__(self, config_path: str = "config/guild_config.json")
    def is_guild_member(self, player_name: str) -> bool
    def is_guild_leader(self, player_name: str) -> bool
    def is_guild_officer(self, player_name: str) -> bool
    def get_alert_priority(self, sender: str, message: str) -> str
    def generate_auto_reply(self, sender: str, message: str, member: GuildMember) -> Optional[str]
    def process_guild_whisper(self, sender: str, message: str) -> Optional[GuildAlert]
    def get_session_analytics(self) -> Dict[str, Any]
```

#### Data Classes
```python
@dataclass
class GuildMember:
    name: str
    role: str  # leader, officer, member
    rank: int  # 1=leader, 2=officer, 3=member
    online: bool = False
    last_seen: Optional[str] = None

@dataclass
class GuildAlert:
    timestamp: str
    sender: str
    message: str
    alert_type: str  # guild_whisper, leader_message, officer_message
    priority: str  # high, medium, low
    auto_reply_sent: bool = False
    reply_message: Optional[str] = None
```

### Configuration Structure

```json
{
  "guild_name": "MorningStar Guild",
  "guild_leader": "GuildMaster",
  "guild_officers": ["OfficerOne", "OfficerTwo", "OfficerThree"],
  "members": {
    "GuildMaster": {
      "name": "GuildMaster",
      "role": "leader",
      "rank": 1,
      "online": false,
      "last_seen": null
    }
  },
  "auto_reply_enabled": true,
  "priority_alerts_enabled": true,
  "discord_integration": true
}
```

## Integration Points

### Discord Relay Integration
- Enhanced `DiscordRelay` class to detect guild alerts
- Priority indicators (🚨) for guild messages
- Color-coded Discord embeds based on priority
- Auto-reply information included in Discord notifications

### Session Manager Integration
- New `GuildAlertEvent` dataclass for session tracking
- `record_guild_alert()` method for logging guild alerts
- Enhanced session analytics including guild alert statistics
- Export functionality for guild alert data

### Whisper Monitor Integration
- Guild alert system processes whispers through existing infrastructure
- Seamless integration with current whisper detection
- No changes required to existing whisper monitoring

## Usage Examples

### Basic Guild Alert Processing
```python
from modules.guild_alert_system import GuildAlertSystem

# Initialize guild system
guild_system = GuildAlertSystem()

# Process a whisper
alert = guild_system.process_guild_whisper("GuildMaster", "We need to discuss strategy")
if alert:
    print(f"Priority: {alert.priority}")
    print(f"Auto-reply: {alert.reply_message}")
```

### Session Integration
```python
from core.session_manager import SessionManager

# Create session manager
session = SessionManager(mode="guild_alert_demo")

# Record guild alert
session.record_guild_alert(
    "GuildMaster", "Hello", "leader_message", "high", 
    True, "I'll be there!"
)

# Get analytics
analytics = session.performance_metrics
print(f"Total guild alerts: {analytics['total_guild_alerts']}")
```

### Discord Integration
```python
# Guild alerts automatically trigger priority Discord notifications
# with enhanced embeds showing:
# - 🚨 Priority indicators
# - Color-coded alerts (red for high priority)
# - Auto-reply information
# - Guild member role details
```

## Testing

### Demo Script
Run the comprehensive demo to test all functionality:
```bash
python demo_batch_112_guild_alert_system.py
```

### Test Suite
Run the complete test suite:
```bash
python test_batch_112_guild_alert_system.py
```

### Test Coverage
- ✅ Guild member detection
- ✅ Priority detection
- ✅ Auto-reply generation
- ✅ Discord integration
- ✅ Session analytics
- ✅ Configuration management
- ✅ Edge case handling

## Configuration

### Setting Up Guild Roster
1. Edit `config/guild_config.json`
2. Add guild members with their roles
3. Set guild leader and officers
4. Configure auto-reply settings

### Discord Integration
1. Ensure Discord bot token is configured in `config/discord_config.json`
2. Guild alerts will automatically send priority notifications
3. Priority indicators and color coding are applied automatically

### Auto-Reply Templates
Customize auto-reply templates in the configuration:
```json
{
  "auto_reply_templates": {
    "guild_leader": "Hello {sender}! I'll make sure to address your message when I'm available.",
    "guild_officer": "Hi {sender}! I've noted your message and will respond when I can.",
    "guild_member": "Thanks for reaching out, {sender}! I'll get back to you shortly."
  }
}
```

## Analytics and Reporting

### Session Analytics
Guild alerts are tracked in session logs with:
- Total guild alerts received
- Breakdown by alert type (leader, officer, member)
- Breakdown by priority (high, medium, low)
- Auto-replies sent count
- Unique guild members contacted

### Export Functionality
Export guild alerts to JSON for analysis:
```python
export_path = guild_system.export_alerts()
# Exports to logs/guild_alerts_YYYYMMDD_HHMMSS.json
```

## Performance Considerations

### Memory Usage
- Guild roster loaded once at startup
- Alert history stored in memory during session
- Configurable export to reduce memory footprint

### Processing Speed
- O(1) guild member lookup using dictionary
- Case-insensitive matching for player names
- Efficient priority detection with keyword matching

### Scalability
- Supports large guild rosters
- Configurable alert limits
- Export functionality for long-term storage

## Future Enhancements

### Potential Improvements
1. **Guild Roster Sync**: Auto-sync with game guild roster
2. **Advanced Keywords**: Machine learning for priority detection
3. **Custom Templates**: User-defined auto-reply templates
4. **Guild Events**: Special handling for guild events/raids
5. **Multi-Guild Support**: Handle multiple guild memberships

### Integration Opportunities
1. **Quest System**: Guild quest coordination
2. **Combat System**: Guild combat alerts
3. **Trading System**: Guild trade notifications
4. **Event Calendar**: Guild event scheduling

## Conclusion

Batch 112 successfully implements a comprehensive guild alert system that:
- ✅ Detects guild member whispers
- ✅ Sends priority Discord notifications
- ✅ Provides AI-enabled auto-replies
- ✅ Tracks guild alerts in session logs
- ✅ Integrates seamlessly with existing systems
- ✅ Includes comprehensive testing and documentation

The system provides immediate value for guild management while maintaining compatibility with the existing codebase architecture. 