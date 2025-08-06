# Dialogue Detection System

## Overview

The Dialogue Detection System is an OCR-driven NPC dialogue detection and interaction system that enables the bot to automatically read dialogue windows, recognize quest prompts or dialogue options, and trigger key inputs to progress conversations automatically.

## Features

### Core Functionality

- **OCR-based Text Recognition**: Uses Tesseract OCR with multiple preprocessing methods for robust text extraction
- **Dialogue Window Detection**: Automatically detects dialogue windows in predefined screen regions
- **Option Parsing**: Extracts dialogue options from detected text using pattern matching
- **Fuzzy Matching**: Supports partial and fuzzy text matching for dialogue options
- **Automatic Interaction**: Clicks on dialogue options based on context and keywords
- **Comprehensive Logging**: Logs all dialogue events to `logs/dialogue/` directory

### Quest Integration

- **Auto-Accept Quests**: Automatically accepts quests when dialogue appears
- **Auto-Complete Quests**: Automatically completes quests when dialogue appears
- **Quest Decline Support**: Can decline quests when needed
- **Trainer Dialogue**: Handles trainer-specific dialogue for skill training

### Dialogue Types Supported

1. **Quest Dialogues**
   - Quest acceptance
   - Quest completion
   - Quest decline

2. **Trainer Dialogues**
   - Skill training
   - Ability learning
   - Training options

3. **General Dialogues**
   - Continue/Next options
   - Close/Exit options
   - Generic interaction options

## Architecture

### Core Components

#### DialogueWindow
```python
@dataclass
class DialogueWindow:
    x: int                    # X coordinate of dialogue window
    y: int                    # Y coordinate of dialogue window
    width: int                # Width of dialogue window
    height: int               # Height of dialogue window
    text: str                 # Extracted dialogue text
    options: List[str]        # Available dialogue options
    confidence: float         # OCR confidence score
    window_type: str          # Type: "quest", "trainer", "general"
    timestamp: str            # ISO timestamp of detection
```

#### DialogueDetector
Main class that handles all dialogue detection and interaction logic.

### Key Methods

#### Detection Methods
- `detect_dialogue_window()`: Detects dialogue windows on screen
- `wait_for_dialogue(timeout)`: Waits for dialogue to appear
- `_is_dialogue_text(text, window_type)`: Determines if text is dialogue
- `_extract_dialogue_options(text)`: Extracts options from dialogue text

#### Interaction Methods
- `click_dialogue_option(index, dialogue_window)`: Clicks option by index
- `click_dialogue_option_by_text(text, dialogue_window)`: Clicks option by text
- `handle_quest_dialogue(dialogue_type)`: Handles quest-specific dialogue
- `handle_trainer_dialogue()`: Handles trainer dialogue

#### Auto-Action Methods
- `auto_accept_quests()`: Automatically accepts quests
- `auto_complete_quests()`: Automatically completes quests

## Usage

### Basic Usage

```python
from core.dialogue_detector import (
    get_dialogue_detector, detect_dialogue_window,
    handle_quest_dialogue, auto_accept_quests
)

# Get the global dialogue detector
detector = get_dialogue_detector()

# Detect dialogue window
dialogue = detect_dialogue_window()
if dialogue:
    print(f"Found dialogue: {dialogue.text}")
    print(f"Options: {dialogue.options}")

# Auto-accept quests
if auto_accept_quests():
    print("Quest accepted!")
```

### Quest Integration

```python
# Handle quest acceptance
if handle_quest_dialogue("accept"):
    print("Quest accepted successfully")

# Handle quest completion
if handle_quest_dialogue("complete"):
    print("Quest completed successfully")

# Handle quest decline
if handle_quest_dialogue("decline"):
    print("Quest declined successfully")
```

### Trainer Integration

```python
# Handle trainer dialogue
if handle_trainer_dialogue():
    print("Trainer dialogue handled successfully")
```

### Waiting for Dialogue

```python
# Wait for dialogue to appear (timeout in seconds)
dialogue = detector.wait_for_dialogue(timeout=5.0)
if dialogue:
    print(f"Dialogue appeared: {dialogue.window_type}")
```

## Configuration

### Dialogue Regions

The system monitors predefined screen regions for different types of dialogue:

```python
dialogue_regions = {
    "quest": (400, 300, 800, 400),      # Center of screen
    "trainer": (300, 200, 900, 600),    # Larger region for trainers
    "general": (350, 250, 850, 500),    # General dialogue
}
```

### Dialogue Patterns

The system recognizes dialogue patterns for different contexts:

```python
dialogue_patterns = {
    "quest_accept": ["Accept", "Yes", "I'll help", "Take quest", ...],
    "quest_complete": ["Complete", "Turn in", "Finish", "Done", ...],
    "quest_decline": ["Decline", "No", "Not now", "Later", ...],
    "training": ["Train", "Learn", "Skill", "Ability", ...],
    "general": ["Continue", "Next", "Okay", "Close", ...],
}
```

## Logging

### Log Structure

All dialogue events are logged to `logs/dialogue/dialogue_YYYYMMDD.json`:

```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "event_type": "detection",
  "action": "window_detected",
  "success": true,
  "details": {},
  "dialogue": {
    "x": 400,
    "y": 300,
    "width": 800,
    "height": 400,
    "text": "Would you like to accept this quest?",
    "options": ["Accept", "Decline"],
    "confidence": 85.5,
    "window_type": "quest",
    "timestamp": "2024-01-15T10:30:45.123456"
  }
}
```

### Event Types

- `detection`: Dialogue window detected
- `interaction`: User interaction with dialogue
- `error`: Error occurred during processing

## OCR Configuration

### Multiple Preprocessing Methods

The system uses multiple OCR preprocessing methods for better accuracy:

1. **Standard**: Basic preprocessing for normal text
2. **Aggressive**: Enhanced preprocessing for difficult text
3. **Conservative**: Minimal preprocessing for clear text

### Confidence Thresholds

- **Detection threshold**: 40% confidence required for dialogue detection
- **Multiple attempts**: Tries all preprocessing methods and uses best result
- **Fallback logic**: Graceful handling of OCR failures

## Testing

### Unit Tests

Run the comprehensive test suite:

```bash
pytest tests/test_dialogue_detector.py -v
```

### Integration Test

Run the integration test script:

```bash
python scripts/test_dialogue_detection.py
```

## Integration with Quest System

### Quest Manager Integration

The dialogue detector integrates with the existing quest system:

```python
# Auto-accept quests when they appear
if auto_accept_quests():
    # Quest was automatically accepted
    pass

# Auto-complete quests when ready
if auto_complete_quests():
    # Quest was automatically completed
    pass
```

### Fallback Logic

If dialogue detection fails, the system provides fallback options:

1. **First option**: For accept/complete actions
2. **Last option**: For decline actions
3. **Error logging**: All failures are logged for debugging

## Performance Considerations

### Optimization Features

- **Singleton pattern**: Single detector instance for efficiency
- **Cached OCR engine**: Reuses OCR engine across calls
- **Timeout handling**: Prevents infinite waiting
- **Error recovery**: Continues operation after OCR failures

### Memory Management

- **Automatic cleanup**: Log files are managed by date
- **Efficient logging**: JSON format for easy parsing
- **Minimal state**: Stateless design for reliability

## Troubleshooting

### Common Issues

1. **No dialogue detected**
   - Check screen resolution and region coordinates
   - Verify OCR is working correctly
   - Check if dialogue text is clear enough

2. **Wrong options selected**
   - Review dialogue patterns and keywords
   - Check OCR text extraction accuracy
   - Verify click coordinates

3. **OCR failures**
   - Ensure Tesseract is installed
   - Check image quality and preprocessing
   - Review confidence thresholds

### Debug Mode

Enable debug logging by setting environment variable:

```bash
export DIALOGUE_DEBUG=1
```

## Future Enhancements

### Planned Features

1. **Machine Learning**: Train models for better text recognition
2. **Dynamic Regions**: Auto-detect dialogue window positions
3. **Multi-language**: Support for different game languages
4. **Voice Integration**: Combine with voice recognition
5. **Advanced Patterns**: More sophisticated dialogue pattern matching

### API Extensions

- Custom dialogue handlers
- Plugin system for new dialogue types
- Webhook integration for external systems
- Real-time monitoring dashboard

## Contributing

### Adding New Dialogue Types

1. Add new region coordinates to `dialogue_regions`
2. Define patterns in `dialogue_patterns`
3. Create handler method in `DialogueDetector`
4. Add unit tests for new functionality
5. Update documentation

### Testing Guidelines

- Test with various screen resolutions
- Verify OCR accuracy with different text styles
- Test error handling and recovery
- Validate logging functionality

## License

This dialogue detection system is part of the Project MorningStar automation framework and follows the same licensing terms. 