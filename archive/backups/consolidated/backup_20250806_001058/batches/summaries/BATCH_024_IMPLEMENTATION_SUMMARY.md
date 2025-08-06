# Batch 024 - Lightweight Combat Profile Dispatcher

## Overview

Batch 024 implements a lightweight combat rotation engine that executes combat logic based on weapon and profession profiles loaded from JSON files. The system provides a simple, configurable way to manage combat rotations with cooldown tracking, emergency skills, and fallback mechanisms.

## Goals

- ✅ Allow simple combat rotation logic to execute based on weapon and profession profile
- ✅ Include weapon type (ranged/melee) support
- ✅ Implement heal/self-buff thresholds
- ✅ Use cooldown memory to avoid spamming
- ✅ Match available skills based on Toolbar OCR and Action log response
- ✅ Add helper method `is_skill_ready(skill)` for cooldown checking

## Files Created/Modified

### New Files
- `combat/rotation_engine.py` - Main rotation engine implementation
- `test_batch_024_rotation_engine.py` - Comprehensive test suite

### Modified Files
- `profiles/combat/rifleman_medic.json` - Updated to new format

## Implementation Details

### Core Components

#### 1. RotationEngine Class
The main class that manages combat rotations:

**Key Features:**
- Profile loading from JSON files
- Skill cooldown tracking
- Rotation execution with fallback
- Emergency skill handling
- OCR integration for skill detection
- Test mode for faster execution

**Main Methods:**
- `load_profile(profile_name)` - Load combat profile from JSON
- `execute_rotation()` - Execute current rotation
- `execute_skill(skill_name)` - Execute individual skill
- `is_skill_ready(skill_name)` - Check if skill is off cooldown
- `get_rotation_status()` - Get current status information

#### 2. CombatProfile Dataclass
Represents a lightweight combat profile:

```python
@dataclass
class CombatProfile:
    name: str
    weapon_type: WeaponType
    stance: StanceType
    rotation: List[str]
    heal_threshold: int = 50
    fallback: str = ""
    skills: Dict[str, SkillInfo] = field(default_factory=dict)
    emergency_skills: Dict[str, str] = field(default_factory=dict)
    buff_threshold: int = 80
    max_range: int = 50
```

#### 3. SkillInfo Dataclass
Tracks individual skill state and cooldowns:

```python
@dataclass
class SkillInfo:
    name: str
    cooldown: float
    last_used: float = 0.0
    is_ready: bool = True
    
    def is_skill_ready(self) -> bool:
        # Smart cooldown checking with execution lock
```

### Profile Format

The new JSON profile format includes:

```json
{
  "name": "rifleman_medic",
  "description": "Rifleman with medic abilities for sustained combat and healing",
  "weapon_type": "ranged",
  "stance": "kneeling",
  "rotation": [
    "aim",
    "headshot",
    "burst_fire"
  ],
  "heal_threshold": 50,
  "fallback": "rifle_shot",
  "cooldowns": {
    "aim": 0,
    "headshot": 5,
    "burst_fire": 15,
    "rifle_shot": 0,
    "heal_self": 30,
    "stim_pack": 120
  },
  "emergency_abilities": {
    "critical_heal": "heal_self",
    "defensive": "stim_pack"
  },
  "buff_threshold": 80,
  "max_range": 50
}
```

### Key Features

#### 1. Weapon Type Support
- **Ranged**: Long-range combat with accuracy bonuses
- **Melee**: Close combat with damage bonuses
- **Hybrid**: Mixed combat styles

#### 2. Stance System
- **Standing**: Default stance
- **Kneeling**: Improved accuracy for ranged
- **Prone**: Maximum accuracy, reduced mobility
- **Cover**: Defensive stance

#### 3. Cooldown Management
- Smart cooldown tracking with execution locks
- Skills with 0 cooldown get 100ms execution lock
- Automatic cooldown expiration detection
- Prevents skill spamming

#### 4. Rotation Logic
- Execute skills in order until one succeeds
- Emergency skills take priority
- Fallback to basic attack when rotation skills unavailable
- Only execute one skill per rotation cycle

#### 5. Emergency Skills
- Critical heal when health below threshold
- Defensive skills for survival
- Automatic priority over rotation skills

#### 6. OCR Integration
- Toolbar scanning for available skills
- Action log monitoring for skill success
- Optional OCR dependency (works without Tesseract)

### Global Functions

For easy integration:

```python
# Load a combat profile
load_combat_profile("rifleman_medic")

# Execute rotation
executed_skills = execute_rotation()

# Check if skill is ready
ready = is_skill_ready("aim")

# Get current status
status = get_rotation_status()
```

## Testing Results

All 12 tests pass successfully:

1. ✅ **Rotation Engine Initialization** - Engine loads correctly
2. ✅ **Profile Loading** - JSON profiles load and parse correctly
3. ✅ **Skill Ready Check** - Cooldown checking works properly
4. ✅ **Skill Execution** - Skills execute and go on cooldown
5. ✅ **Rotation Execution** - Rotation logic works with fallback
6. ✅ **Emergency Skills** - Emergency skill system functional
7. ✅ **Rotation Status** - Status reporting complete
8. ✅ **Toolbar Scanning** - OCR integration working
9. ✅ **Cooldown Management** - Cooldown system robust
10. ✅ **Global Functions** - Global API working
11. ✅ **Error Handling** - Error cases handled gracefully
12. ✅ **Profile Format** - JSON format validation

## Usage Examples

### Basic Usage

```python
from combat.rotation_engine import get_rotation_engine

# Get engine instance
engine = get_rotation_engine()

# Load profile
engine.load_profile("rifleman_medic")

# Execute rotation
executed = engine.execute_rotation()
print(f"Executed skills: {executed}")

# Check status
status = engine.get_rotation_status()
print(f"Available skills: {status['available_skills']}")
```

### Advanced Usage

```python
# Enable test mode for faster execution
engine.enable_test_mode()

# Check specific skill
if engine.is_skill_ready("headshot"):
    success = engine.execute_skill("headshot")
    print(f"Headshot executed: {success}")

# Get detailed status
status = engine.get_rotation_status()
for skill, cooldown in status["skill_cooldowns"].items():
    print(f"{skill}: {cooldown:.1f}s remaining")
```

### Profile Creation

```json
{
  "name": "custom_build",
  "weapon_type": "melee",
  "stance": "standing",
  "rotation": ["slash", "stab", "finisher"],
  "heal_threshold": 30,
  "fallback": "basic_attack",
  "cooldowns": {
    "slash": 2,
    "stab": 3,
    "finisher": 10,
    "basic_attack": 0
  },
  "emergency_abilities": {
    "critical_heal": "heal_potion"
  }
}
```

## Technical Implementation

### Cooldown System
- Uses `time.time()` for precise timing
- Execution locks prevent immediate re-use
- Automatic cooldown expiration detection
- Supports 0-cooldown skills with brief locks

### OCR Integration
- Optional dependency on Tesseract
- Mock OCR for testing environments
- Screen region scanning for skill detection
- Action log pattern matching

### Error Handling
- Graceful handling of missing profiles
- Invalid skill execution prevention
- OCR failure fallbacks
- Comprehensive logging

### Performance Optimizations
- Test mode for faster execution
- Efficient cooldown checking
- Minimal screen captures
- Smart skill availability caching

## Integration Points

### With Existing Systems
- Compatible with existing combat engine
- Can be used alongside movement systems
- Integrates with mount management
- Works with travel automation

### Future Extensions
- Health monitoring integration
- Target selection system
- Advanced stance management
- Multi-target rotation support

## Conclusion

Batch 024 successfully implements a lightweight, configurable combat rotation system that provides:

- **Simplicity**: Easy-to-understand JSON profiles
- **Flexibility**: Support for various weapon types and stances
- **Reliability**: Robust cooldown and error handling
- **Extensibility**: Clean API for future enhancements
- **Testability**: Comprehensive test coverage

The system is ready for production use and provides a solid foundation for more advanced combat automation features. 