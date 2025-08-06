# MS11 Batch 066 - Player Keybind Manager + Validation Reporter

## Overview

Batch 066 implements an enhanced keybind management system for MS11 that provides comprehensive parsing, validation, and reporting of SWG keybind configurations. The system includes automatic detection, manual overrides, Discord alerts for critical issues, and detailed reporting with recommendations.

## Key Features

### ✅ SWG Configuration File Parsing
- Automatically detects and parses `options.cfg` and `inputmap.cfg` files
- Supports multiple keybind line formats (Keybind, input, = assignments)
- Handles encoding issues gracefully with error recovery
- Maps common keybind name variations to standard names

### ✅ Required Keybind Validation
- Validates required keybinds for combat, healing, navigation, and inventory
- Defines critical keybinds: attack, use, inventory, map, chat, target
- Optional keybinds: heal, follow, stop, loot
- Detects key conflicts and missing essential keybinds

### ✅ Editable Override System via CLI/JSON
- JSON-based override files for manual keybind configuration
- Template generation for easy setup
- Integration with automatic detection
- Support for adding, removing, and modifying keybinds

### ✅ Comprehensive Reporting
- Outputs valid keys and missing keys with recommended fixes
- Category-based organization (combat, healing, navigation, inventory, etc.)
- Detailed status reporting (valid, missing, conflicting, unknown)
- Automatic fix script generation

### ✅ Discord Integration
- Optional Discord DM alerts for critical keybind issues
- Configurable webhook integration
- Severity-based alert system (critical, warning, info)
- Real-time notifications for broken core bot functions

## Implementation Details

### Core Components

#### `modules/keybind_manager/keybind_parser.py`
The main parser module containing:
- `KeybindParser` class for SWG configuration file parsing
- `Keybind` and `KeybindParseResult` dataclasses
- `KeybindStatus` and `KeybindCategory` enums
- Automatic SWG directory detection
- Support for multiple keybind line formats

#### `modules/keybind_manager/keybind_validator.py`
Validation module providing:
- `KeybindValidator` class for keybind validation
- `KeybindValidationResult` dataclass
- Conflict detection and missing keybind identification
- Smart recommendations for keybind fixes

#### `modules/keybind_manager/keybind_override.py`
Override system providing:
- `KeybindOverrideManager` class for manual overrides
- `KeybindOverride` dataclass
- JSON-based configuration management
- Template generation and file loading

#### `modules/keybind_manager/discord_keybind_alerts.py`
Discord integration providing:
- `DiscordKeybindAlerts` class for alert management
- `KeybindAlert` dataclass
- Async webhook integration
- Severity-based alert creation

#### `modules/keybind_manager/keybind_reporter.py`
Reporting module providing:
- `KeybindReporter` class for comprehensive reporting
- `KeybindReport` dataclass
- Category-based organization
- Fix script generation

### Data Structures

#### Keybind Categories
```python
class KeybindCategory(Enum):
    COMBAT = "combat"
    HEALING = "healing"
    NAVIGATION = "navigation"
    INVENTORY = "inventory"
    MOVEMENT = "movement"
    CHAT = "chat"
    CAMERA = "camera"
    UTILITY = "utility"
    OTHER = "other"
```

#### Keybind Status
```python
class KeybindStatus(Enum):
    VALID = "valid"
    MISSING = "missing"
    CONFLICT = "conflict"
    UNKNOWN = "unknown"
```

#### Required Keybinds
The system defines these essential keybinds for MS11 compatibility:
- **attack**: Combat action (F1 recommended)
- **use**: Interaction (Enter recommended)
- **inventory**: Inventory access (I recommended)
- **map**: Map access (M recommended)
- **chat**: Chat window (Enter recommended)
- **target**: Target selection (Tab recommended)

Optional keybinds include:
- **heal**: Heal action (H recommended)
- **follow**: Follow target (F recommended)
- **stop**: Stop action (Escape recommended)
- **loot**: Loot corpses (L recommended)

### Configuration File Support

The system supports multiple SWG configuration file formats:

#### options.cfg Format
```
Keybind attack F1
Keybind use Enter
Keybind inventory I
Keybind map M
Keybind chat Enter
Keybind target Tab
```

#### inputmap.cfg Format
```
input map M
input chat Enter
input target Tab
input camera_zoom MouseWheel
```

#### Alternative Formats
```
attack=F1
use Enter
input map M
```

### Keybind Name Mapping

The system automatically maps common keybind name variations:
- `combat` → `attack`
- `interact` → `use`
- `inv` → `inventory`
- `worldmap` → `map`
- `halt` → `stop`
- `cure` → `heal`
- `corpse` → `loot`

### Validation Features

#### Conflict Detection
- Identifies when the same key is bound to multiple actions
- Reports conflicts with affected keybinds
- Provides recommendations for resolution

#### Missing Keybind Detection
- Identifies missing required keybinds
- Suggests appropriate key assignments
- Categorizes by severity (critical vs optional)

#### Status Classification
- **Valid**: Keybind is properly configured
- **Missing**: Keybind is not set
- **Conflict**: Keybind conflicts with another action
- **Unknown**: Keybind is not recognized

### Override System

#### JSON Configuration Format
```json
{
  "attack": {
    "key": "F1",
    "category": "combat",
    "description": "Attack/Combat action",
    "required": true
  },
  "use": {
    "key": "Enter",
    "category": "utility",
    "description": "Use/Interact with objects",
    "required": true
  }
}
```

#### Template Generation
The system can generate template files with recommended keybinds for easy setup.

### Discord Integration

#### Alert Types
- **Critical Alerts**: For missing required keybinds or key conflicts
- **Warning Alerts**: For significant but non-critical issues
- **Info Alerts**: For minor configuration notes

#### Alert Content
- Affected keybinds list
- Recommendations for fixes
- Severity indicators
- Timestamp information

### Reporting Features

#### Comprehensive Reports
- Summary statistics (total, valid, missing, conflicting keybinds)
- Category-based breakdown
- Detailed keybind listings with status
- Recommendations for fixes

#### Fix Script Generation
```bash
# MS11 Keybind Fix Script
# Generated automatically based on validation report

# Add these lines to your options.cfg file:
Keybind attack F1
Keybind use Enter
Keybind inventory I

# Instructions:
# 1. Open your SWG options.cfg file
# 2. Add the keybind lines above
# 3. Save the file and restart SWG
# 4. Run MS11 keybind validation again
```

#### Category Reports
Organizes keybinds by category for easy review:
- Combat keybinds
- Healing keybinds
- Navigation keybinds
- Inventory keybinds
- Movement keybinds
- Chat keybinds
- Camera keybinds
- Utility keybinds

### Error Handling

#### Robust Parsing
- Handles encoding issues gracefully
- Continues parsing even with malformed lines
- Reports parse errors without stopping execution

#### Graceful Degradation
- Works with missing configuration files
- Handles invalid override files
- Continues operation with partial data

#### Comprehensive Logging
- Detailed error messages
- Parse error reporting
- Validation issue tracking

## Usage Examples

### Basic Validation
```python
from modules.keybind_manager import KeybindParser, KeybindValidator

# Parse SWG configuration files
parser = KeybindParser(swg_directory="/path/to/swg")
parse_result = parser.parse_config_files()

# Validate keybinds
validator = KeybindValidator()
validation_result = validator.validate_keybinds(
    parse_result.keybinds, 
    parse_result.required_keybinds
)

print(f"Valid keybinds: {validation_result.valid_keybinds}")
print(f"Missing keybinds: {validation_result.missing_keybinds}")
print(f"Conflicting keybinds: {validation_result.conflicting_keybinds}")
```

### Manual Overrides
```python
from modules.keybind_manager import KeybindOverrideManager

# Initialize override manager
override_manager = KeybindOverrideManager("data/keybind_overrides.json")

# Add manual override
override_manager.add_override(
    name="custom_action",
    key="X",
    category="utility",
    description="Custom action",
    required=False
)

# Apply overrides to detected keybinds
updated_keybinds = override_manager.apply_overrides_to_keybinds(keybinds)
```

### Discord Alerts
```python
from modules.keybind_manager import DiscordKeybindAlerts

# Initialize Discord alerts
alerts = DiscordKeybindAlerts(webhook_url="https://discord.com/api/webhooks/...")

# Check if alert should be sent
if alerts.should_send_alert(validation_result):
    alert = alerts.create_critical_alert(validation_result)
    success = await alerts.send_keybind_alert(alert)
```

### Comprehensive Reporting
```python
from modules.keybind_manager import KeybindReporter

# Generate comprehensive report
reporter = KeybindReporter()
report = reporter.generate_report(
    keybinds,
    validation_result,
    swg_directory,
    config_files
)

# Print formatted report
reporter.print_report(report, detailed=True)

# Save report to file
reporter.save_report(report, "keybind_report.json")

# Generate fix script
fix_script = reporter.generate_fix_script(report)
reporter.save_fix_script(report, "fix_keybinds.txt")
```

## Testing

### Comprehensive Test Suite
The implementation includes 37 comprehensive tests covering:
- Keybind parsing functionality
- Validation logic
- Override system
- Discord alert creation
- Report generation
- Error handling
- Integration scenarios

### Demo Script
A comprehensive demo script showcases all features:
- Basic keybind parsing
- Validation with conflicts and missing keybinds
- Manual override system
- Discord alert creation
- Comprehensive reporting
- Full integration workflow

## Configuration

### SWG Directory Detection
The system automatically detects common SWG installation paths:
- `C:\Program Files (x86)\Sony\Star Wars Galaxies`
- `C:\Program Files\Sony\Star Wars Galaxies`
- `D:\Star Wars Galaxies`
- `E:\Star Wars Galaxies`
- `~/Star Wars Galaxies`

### Override File Location
Default override file location: `data/keybind_overrides.json`

### Discord Webhook Configuration
Discord alerts require a webhook URL to be configured for sending alerts.

## Future Enhancements

### Potential Improvements
- Support for additional SWG configuration file formats
- Integration with SWG client for real-time keybind detection
- Advanced conflict resolution suggestions
- Keybind profile management
- Integration with other MS11 modules

### Extensibility
The modular design allows for easy extension:
- New keybind categories
- Additional validation rules
- Custom alert formats
- Enhanced reporting features

## Conclusion

Batch 066 provides a comprehensive keybind management solution that ensures MS11 compatibility by:
- Automatically detecting and validating SWG keybind configurations
- Providing manual override capabilities for custom setups
- Alerting users to critical issues via Discord integration
- Generating detailed reports with actionable recommendations
- Supporting multiple configuration file formats and keybind variations

The system is designed to be robust, user-friendly, and extensible, making it an essential component for MS11 users who need to ensure their keybind configurations are optimal for bot operation. 